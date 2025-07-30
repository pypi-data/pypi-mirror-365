"""
EC2 resource driver for AWS Session TX
"""

import logging
from typing import Optional, List
from botocore.exceptions import ClientError, WaiterError

from ...utils.aws import get_ec2_client
from ...models import HydratedResource, ResourceType
from .base import ResourceDriver

logger = logging.getLogger(__name__)


class EC2Driver(ResourceDriver):
    """Driver for EC2 resource deletion (instances, security groups, volumes)"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        super().__init__(profile=profile, region=region)
        self.ec2 = get_ec2_client(profile=profile, region=region)
    
    def delete(self, resource: HydratedResource) -> bool:
        """Delete EC2 resource based on type"""
        resource_type = resource.resource.type
        
        if resource_type == ResourceType.EC2_INSTANCE:
            return self._delete_instance(resource)
        elif resource_type == ResourceType.EC2_SECURITY_GROUP:
            return self._delete_security_group(resource)
        elif resource_type == ResourceType.EC2_VOLUME:
            return self._delete_volume(resource)
        else:
            logger.error(f"Unsupported EC2 resource type: {resource_type}")
            return False
    
    def is_gone(self, resource: HydratedResource) -> bool:
        """Check if EC2 resource has been deleted"""
        resource_type = resource.resource.type
        
        if resource_type == ResourceType.EC2_INSTANCE:
            return self._is_instance_gone(resource)
        elif resource_type == ResourceType.EC2_SECURITY_GROUP:
            return self._is_security_group_gone(resource)
        elif resource_type == ResourceType.EC2_VOLUME:
            return self._is_volume_gone(resource)
        else:
            return False
    
    def _delete_instance(self, resource: HydratedResource) -> bool:
        """Delete EC2 instance"""
        try:
            instance_id = resource.resource.id
            self._log_deletion_start(resource)
            
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            if not response['Reservations']:
                logger.info(f"Instance {instance_id} already deleted")
                return True
            
            instance = response['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']
            
            if state in ['running', 'pending']:
                logger.info(f"Stopping instance {instance_id}")
                self.ec2.stop_instances(InstanceIds=[instance_id])
                
                try:
                    waiter = self.ec2.get_waiter('instance_stopped')
                    waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 5, 'MaxAttempts': 60})
                except WaiterError as e:
                    logger.warning(f"Timeout waiting for instance {instance_id} to stop: {e}")
            
            logger.info(f"Terminating instance {instance_id}")
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            
            try:
                waiter = self.ec2.get_waiter('instance_terminated')
                waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 5, 'MaxAttempts': 60})
            except WaiterError as e:
                logger.warning(f"Timeout waiting for instance {instance_id} to terminate: {e}")
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'InvalidInstanceID.NotFound':
                logger.info(f"Instance {resource.resource.id} already deleted")
                return True
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _delete_security_group(self, resource: HydratedResource) -> bool:
        """Delete security group"""
        try:
            group_id = resource.resource.id
            self._log_deletion_start(resource)
            
            if not self._is_security_group_detached(group_id):
                logger.error(f"Security group {group_id} is still attached to resources")
                return False
            
            logger.info(f"Deleting security group {group_id}")
            self.ec2.delete_security_group(GroupId=group_id)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'InvalidGroup.NotFound':
                logger.info(f"Security group {resource.resource.id} already deleted")
                return True
            
            if error_code == 'DependencyViolation':
                logger.error(f"Security group {resource.resource.id} has dependencies and cannot be deleted")
                return False
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _delete_volume(self, resource: HydratedResource) -> bool:
        """Delete EBS volume"""
        try:
            volume_id = resource.resource.id
            self._log_deletion_start(resource)
            
            if not self._is_volume_detached(volume_id):
                logger.error(f"Volume {volume_id} is still attached to an instance")
                return False
            
            logger.info(f"Deleting volume {volume_id}")
            self.ec2.delete_volume(VolumeId=volume_id)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'InvalidVolume.NotFound':
                logger.info(f"Volume {resource.resource.id} already deleted")
                return True
            
            if error_code == 'VolumeInUse':
                logger.error(f"Volume {resource.resource.id} is still in use")
                return False
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def _is_instance_gone(self, resource: HydratedResource) -> bool:
        """Check if instance has been deleted"""
        try:
            instance_id = resource.resource.id
            response = self.ec2.describe_instances(InstanceIds=[instance_id])
            return len(response['Reservations']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                return True
            return False
        except Exception:
            return False
    
    def _is_security_group_gone(self, resource: HydratedResource) -> bool:
        """Check if security group has been deleted"""
        try:
            group_id = resource.resource.id
            response = self.ec2.describe_security_groups(GroupIds=[group_id])
            return len(response['SecurityGroups']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
                return True
            return False
        except Exception:
            return False
    
    def _is_volume_gone(self, resource: HydratedResource) -> bool:
        """Check if volume has been deleted"""
        try:
            volume_id = resource.resource.id
            response = self.ec2.describe_volumes(VolumeIds=[volume_id])
            return len(response['Volumes']) == 0
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                return True
            return False
        except Exception:
            return False
    
    def _is_security_group_detached(self, group_id: str) -> bool:
        """Check if security group is detached from all resources"""
        try:
            eni_response = self.ec2.describe_network_interfaces(
                Filters=[{'Name': 'group-id', 'Values': [group_id]}]
            )
            if eni_response['NetworkInterfaces']:
                logger.warning(f"Security group {group_id} is attached to {len(eni_response['NetworkInterfaces'])} network interfaces")
                return False
            
            instance_response = self.ec2.describe_instances(
                Filters=[{'Name': 'instance.group-id', 'Values': [group_id]}]
            )
            for reservation in instance_response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['State']['Name'] not in ['terminated', 'shutting-down']:
                        logger.warning(f"Security group {group_id} is attached to instance {instance['InstanceId']}")
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking if security group {group_id} is detached: {e}")
            return False
    
    def _is_volume_detached(self, volume_id: str) -> bool:
        """Check if volume is detached from all instances"""
        try:
            response = self.ec2.describe_volumes(VolumeIds=[volume_id])
            if not response['Volumes']:
                return True
            
            volume = response['Volumes'][0]
            attachments = volume.get('Attachments', [])
            
            for attachment in attachments:
                if attachment['State'] not in ['detached', 'detaching']:
                    logger.warning(f"Volume {volume_id} is still attached to instance {attachment['InstanceId']}")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking if volume {volume_id} is detached: {e}")
            return False 