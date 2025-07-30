"""
CloudWatch Logs resource driver for AWS Session TX
"""

import logging
from typing import Optional
from botocore.exceptions import ClientError

from ...utils.aws import get_logs_client
from ...models import HydratedResource, ResourceType
from .base import ResourceDriver

logger = logging.getLogger(__name__)


class LogsDriver(ResourceDriver):
    """Driver for CloudWatch Logs deletion"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        super().__init__(profile=profile, region=region)
        self.logs = get_logs_client(profile=profile, region=region)
    
    def delete(self, resource: HydratedResource) -> bool:
        """Delete CloudWatch log group"""
        try:
            log_group_name = self._extract_log_group_name(resource.resource.arn)
            self._log_deletion_start(resource)
            
            logger.info(f"Deleting log group: {log_group_name}")
            self.logs.delete_log_group(logGroupName=log_group_name)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                logger.info(f"Log group {resource.resource.id} already deleted")
                return True
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def is_gone(self, resource: HydratedResource) -> bool:
        """Check if log group has been deleted"""
        try:
            log_group_name = self._extract_log_group_name(resource.resource.arn)
            response = self.logs.describe_log_groups(logGroupNamePrefix=log_group_name)
            
            for log_group in response.get('logGroups', []):
                if log_group['logGroupName'] == log_group_name:
                    return False
            
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return True
            return False
        except Exception as e:
            logger.warning(f"Error checking if log group {resource.resource.id} is gone: {e}")
            return False
    
    def _extract_log_group_name(self, arn: str) -> str:
        """Extract log group name from ARN"""
        parts = arn.split(':')
        if len(parts) >= 7:
            return parts[6]  
        return arn.split('/')[-1] 