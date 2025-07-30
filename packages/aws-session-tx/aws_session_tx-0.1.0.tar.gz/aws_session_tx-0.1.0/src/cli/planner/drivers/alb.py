"""
Application Load Balancer resource driver for AWS Session TX
"""

import logging
from typing import Optional, List
from botocore.exceptions import ClientError, WaiterError

from ...utils.aws import get_elbv2_client
from ...models import HydratedResource, ResourceType
from .base import ResourceDriver

logger = logging.getLogger(__name__)


class ALBDriver(ResourceDriver):
    """Driver for ALB resource deletion (load balancers, target groups, listeners)"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        super().__init__(profile=profile, region=region)
        self.elbv2 = get_elbv2_client(profile=profile, region=region)
    
    def delete(self, resource: HydratedResource) -> bool:
        """Delete ALB resource based on type"""
        resource_type = resource.resource.type
        
        if resource_type == ResourceType.ALB_LOAD_BALANCER:
            return self._delete_load_balancer(resource)
        elif resource_type == ResourceType.ALB_TARGET_GROUP:
            return self._delete_target_group(resource)
        elif resource_type == ResourceType.ALB_LISTENER:
            return self._delete_listener(resource)
        else:
            logger.error(f"Unsupported ALB resource type: {resource_type}")
            return False
    
    def is_gone(self, resource: HydratedResource) -> bool:
        """Check if ALB resource has been deleted"""
        resource_type = resource.resource.type
        
        if resource_type == ResourceType.ALB_LOAD_BALANCER:
            return self._is_load_balancer_gone(resource)
        elif resource_type == ResourceType.ALB_TARGET_GROUP:
            return self._is_target_group_gone(resource)
        elif resource_type == ResourceType.ALB_LISTENER:
            return self._is_listener_gone(resource)
        else:
            return False
    
    def _delete_load_balancer(self, resource: HydratedResource) -> bool:
        """Delete load balancer"""
        try:
            lb_arn = resource.resource.arn
            self._log_deletion_start(resource)
            
            listeners = self._get_listeners(lb_arn)
            for listener in listeners:
                logger.info(f"Deleting listener {listener['ListenerArn']}")
                self.elbv2.delete_listener(ListenerArn=listener['ListenerArn'])
            
            logger.info(f"Deleting load balancer {resource.resource.id}")
            self.elbv2.delete_load_balancer(LoadBalancerArn=lb_arn)
            
            try:
                waiter = self.elbv2.get_waiter('load_balancers_deleted')
                waiter.wait(LoadBalancerArns=[lb_arn], WaiterConfig={'Delay': 10, 'MaxAttempts': 30})
            except WaiterError as e:
                logger.warning(f"Timeout waiting for load balancer {resource.resource.id} to be deleted: {e}")
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'LoadBalancerNotFound':
                logger.info(f"Load balancer {resource.resource.id} already deleted")
                return True
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _delete_target_group(self, resource: HydratedResource) -> bool:
        """Delete target group"""
        try:
            tg_arn = resource.resource.arn
            self._log_deletion_start(resource)
            
            if not self._is_target_group_detached(tg_arn):
                logger.error(f"Target group {resource.resource.id} is still attached to listeners")
                return False
            
            targets = self._get_targets(tg_arn)
            if targets:
                logger.info(f"Deregistering {len(targets)} targets from target group {resource.resource.id}")
                self.elbv2.deregister_targets(
                    TargetGroupArn=tg_arn,
                    Targets=targets
                )
            
            logger.info(f"Deleting target group {resource.resource.id}")
            self.elbv2.delete_target_group(TargetGroupArn=tg_arn)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'TargetGroupNotFound':
                logger.info(f"Target group {resource.resource.id} already deleted")
                return True
            
            if error_code == 'ResourceInUse':
                logger.error(f"Target group {resource.resource.id} is still in use")
                return False
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _delete_listener(self, resource: HydratedResource) -> bool:
        """Delete listener"""
        try:
            listener_arn = resource.resource.arn
            self._log_deletion_start(resource)
            
            logger.info(f"Deleting listener {resource.resource.id}")
            self.elbv2.delete_listener(ListenerArn=listener_arn)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ListenerNotFound':
                logger.info(f"Listener {resource.resource.id} already deleted")
                return True
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _is_load_balancer_gone(self, resource: HydratedResource) -> bool:
        """Check if load balancer has been deleted"""
        try:
            lb_arn = resource.resource.arn
            response = self.elbv2.describe_load_balancers(LoadBalancerArns=[lb_arn])
            return len(response['LoadBalancers']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                return True
            return False
        except Exception:
            return False
    
    def _is_target_group_gone(self, resource: HydratedResource) -> bool:
        """Check if target group has been deleted"""
        try:
            tg_arn = resource.resource.arn
            response = self.elbv2.describe_target_groups(TargetGroupArns=[tg_arn])
            return len(response['TargetGroups']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'TargetGroupNotFound':
                return True
            return False
        except Exception:
            return False
    
    def _is_listener_gone(self, resource: HydratedResource) -> bool:
        """Check if listener has been deleted"""
        try:
            listener_arn = resource.resource.arn
            response = self.elbv2.describe_listeners(ListenerArns=[listener_arn])
            return len(response['Listeners']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'ListenerNotFound':
                return True
            return False
        except Exception:
            return False
    
    def _get_listeners(self, lb_arn: str) -> List[dict]:
        """Get all listeners for a load balancer"""
        try:
            response = self.elbv2.describe_listeners(LoadBalancerArn=lb_arn)
            return response.get('Listeners', [])
        except Exception as e:
            logger.warning(f"Error getting listeners for load balancer {lb_arn}: {e}")
            return []
    
    def _get_targets(self, tg_arn: str) -> List[dict]:
        """Get all targets for a target group"""
        try:
            response = self.elbv2.describe_target_health(TargetGroupArn=tg_arn)
            targets = []
            for target in response.get('TargetHealthDescriptions', []):
                targets.append({
                    'Id': target['Target']['Id'],
                    'Port': target['Target'].get('Port', 80)
                })
            return targets
        except Exception as e:
            logger.warning(f"Error getting targets for target group {tg_arn}: {e}")
            return []
    
    def _is_target_group_detached(self, tg_arn: str) -> bool:
        """Check if target group is detached from all listeners"""
        try:
            response = self.elbv2.describe_listeners()
            
            for listener in response.get('Listeners', []):
                for action in listener.get('DefaultActions', []):
                    if action.get('Type') == 'forward' and action.get('TargetGroupArn') == tg_arn:
                        logger.warning(f"Target group {tg_arn} is attached to listener {listener['ListenerArn']}")
                        return False
                
                for action in listener.get('Actions', []):
                    if action.get('Type') == 'forward' and action.get('TargetGroupArn') == tg_arn:
                        logger.warning(f"Target group {tg_arn} is attached to listener {listener['ListenerArn']}")
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking if target group {tg_arn} is detached: {e}")
            return False 