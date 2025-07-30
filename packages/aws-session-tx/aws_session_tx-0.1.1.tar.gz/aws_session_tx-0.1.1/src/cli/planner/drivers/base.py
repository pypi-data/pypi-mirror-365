"""
Base resource driver for AWS Session TX
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError, WaiterError

from ...models import HydratedResource, ResourceType
from ...utils.retry import retry_aws_operation

logger = logging.getLogger(__name__)


class ResourceDriver(ABC):
    """Base class for resource drivers"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        self.profile = profile
        self.region = region
        self.max_retries = 3
        self.retry_delay = 2  
    
    @abstractmethod
    def delete(self, resource: HydratedResource) -> bool:
        """Delete the resource"""
        pass
    
    @abstractmethod
    def is_gone(self, resource: HydratedResource) -> bool:
        """Check if the resource has been deleted"""
        pass
    
    @retry_aws_operation("Resource Deletion", max_attempts=3, base_delay=2.0)
    def delete_with_retry(self, resource: HydratedResource) -> bool:
        """Delete resource with retry logic using the new retry utilities"""
        logger.info(f"Deleting {resource.resource.type}:{resource.resource.id}")
        
        if self.delete(resource):
            if self.wait_for_deletion(resource):
                logger.info(f"Successfully deleted {resource.resource.type}:{resource.resource.id}")
                return True
            else:
                logger.warning(f"Resource {resource.resource.id} may not be fully deleted")
                return True 
        
        return False
    
    def wait_for_deletion(self, resource: HydratedResource, timeout: int = 300) -> bool:
        """Wait for resource to be deleted with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_gone(resource):
                return True
            
            time.sleep(5) 
        
        logger.warning(f"Timeout waiting for {resource.resource.id} to be deleted")
        return False
    
    def _handle_waiter_error(self, e: WaiterError, resource_id: str) -> bool:
        """Handle waiter errors gracefully"""
        if 'ResourceNotFoundException' in str(e):
            logger.info(f"Resource {resource_id} already deleted (waiter confirmed)")
            return True
        
        logger.error(f"Waiter error for {resource_id}: {e}")
        return False
    
    def _log_deletion_start(self, resource: HydratedResource):
        """Log the start of deletion process"""
        logger.info(f"Starting deletion of {resource.resource.type}:{resource.resource.id}")
    
    def _log_deletion_success(self, resource: HydratedResource):
        """Log successful deletion"""
        logger.info(f"Successfully deleted {resource.resource.type}:{resource.resource.id}")
    
    def _log_deletion_failure(self, resource: HydratedResource, error: str):
        """Log deletion failure"""
        logger.error(f"Failed to delete {resource.resource.type}:{resource.resource.id}: {error}")
    
    def _extract_resource_id_from_arn(self, arn: str) -> str:
        """Extract resource ID from ARN"""
        return arn.split('/')[-1]
    
    def _get_account_id_from_arn(self, arn: str) -> str:
        """Extract account ID from ARN"""
        parts = arn.split(':')
        if len(parts) >= 5:
            return parts[4]
        return ""
    
    def _is_resource_in_session(self, resource_arn: str, session_resources: List[HydratedResource]) -> bool:
        """Check if a resource belongs to the current session"""
        session_arns = {r.resource.arn for r in session_resources}
        return resource_arn in session_arns 