"""
S3 resource driver for AWS Session TX
"""

import logging
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

from ...utils.aws import get_s3_client
from ...models import HydratedResource, ResourceType
from .base import ResourceDriver

logger = logging.getLogger(__name__)


class S3Driver(ResourceDriver):
    """Driver for S3 bucket deletion"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        super().__init__(profile=profile, region=region)
        self.s3 = get_s3_client(profile=profile, region=region)
    
    def delete(self, resource: HydratedResource) -> bool:
        """Delete S3 bucket by first emptying it"""
        try:
            bucket_name = resource.resource.id
            self._log_deletion_start(resource)
            
            empty_success = self._empty_bucket(bucket_name)
            
            if not empty_success:
                logger.warning(f"Could not empty bucket {bucket_name}, attempting deletion anyway")
            logger.info(f"Deleting S3 bucket: {bucket_name}")
            self.s3.delete_bucket(Bucket=bucket_name)
            
            self._log_deletion_success(resource)
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchBucket':
                logger.info(f"Bucket {resource.resource.id} already deleted")
                return True
            
            if error_code == 'BucketNotEmpty':
                logger.error(f"Bucket {resource.resource.id} is not empty and cannot be deleted")
                return False
            
            if error_code == 'AccessDenied':
                logger.error(f"Access denied when deleting bucket {resource.resource.id}: {e}")
                return False
            
            self._log_deletion_failure(resource, str(e))
            raise
        
        except Exception as e:
            self._log_deletion_failure(resource, str(e))
            raise
    
    def is_gone(self, resource: HydratedResource) -> bool:
        """Check if S3 bucket has been deleted"""
        try:
            bucket_name = resource.resource.id
            self.s3.head_bucket(Bucket=bucket_name)
            return False
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ['NoSuchBucket', '404']:
                return True
            elif error_code == 'AccessDenied':
                logger.warning(f"Access denied checking bucket {resource.resource.id}, assuming it might be gone")
                return True
            else:
                logger.warning(f"Unexpected error checking bucket {resource.resource.id}: {e}")
                return False 
        except Exception as e:
            logger.warning(f"Error checking if bucket {resource.resource.id} is gone: {e}")
            return False
    
    def _empty_bucket(self, bucket_name: str) -> bool:
        """Empty an S3 bucket by deleting all objects and versions"""
        try:
            logger.info(f"Emptying S3 bucket: {bucket_name}")
            
            try:
                versions = self.s3.list_object_versions(Bucket=bucket_name)
                
                if 'Versions' in versions:
                    for version in versions['Versions']:
                        try:
                            self.s3.delete_object(
                                Bucket=bucket_name,
                                Key=version['Key'],
                                VersionId=version['VersionId']
                            )
                        except ClientError as e:
                            if e.response['Error']['Code'] == 'AccessDenied':
                                logger.warning(f"Access denied deleting version {version['Key']} from {bucket_name}")
                                continue
                            else:
                                raise
                
                if 'DeleteMarkers' in versions:
                    for marker in versions['DeleteMarkers']:
                        try:
                            self.s3.delete_object(
                                Bucket=bucket_name,
                                Key=marker['Key'],
                                VersionId=marker['VersionId']
                            )
                        except ClientError as e:
                            if e.response['Error']['Code'] == 'AccessDenied':
                                logger.warning(f"Access denied deleting delete marker {marker['Key']} from {bucket_name}")
                                continue
                            else:
                                raise
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.warning(f"Access denied listing versions for bucket {bucket_name}")
                else:
                    raise
            
            try:
                objects = self.s3.list_objects_v2(Bucket=bucket_name)
                if 'Contents' in objects:
                    for obj in objects['Contents']:
                        try:
                            self.s3.delete_object(
                                Bucket=bucket_name,
                                Key=obj['Key']
                            )
                        except ClientError as e:
                            if e.response['Error']['Code'] == 'AccessDenied':
                                logger.warning(f"Access denied deleting object {obj['Key']} from {bucket_name}")
                                continue
                            else:
                                raise
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    logger.warning(f"Access denied listing objects for bucket {bucket_name}")
                    return False
                else:
                    raise
            
            logger.info(f"Successfully emptied bucket: {bucket_name}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchBucket':
                logger.info(f"Bucket {bucket_name} already deleted")
                return True
            
            if error_code == 'AccessDenied':
                logger.warning(f"Access denied emptying bucket {bucket_name}: {e}")
                return False
            
            logger.error(f"Failed to empty bucket {bucket_name}: {e}")
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error emptying bucket {bucket_name}: {e}")
            return False
    
    def _delete_objects_batch(self, bucket_name: str, objects: list) -> bool:
        """Delete a batch of objects from S3 bucket"""
        if not objects:
            return True
        
        try:
            delete_objects = []
            for obj in objects:
                delete_objects.append({
                    'Key': obj['Key']
                })
                if 'VersionId' in obj:
                    delete_objects[-1]['VersionId'] = obj['VersionId']
            
            response = self.s3.delete_objects(
                Bucket=bucket_name,
                Delete={
                    'Objects': delete_objects,
                    'Quiet': True
                }
            )
            
            if 'Errors' in response:
                for error in response['Errors']:
                    logger.warning(f"Failed to delete object {error['Key']}: {error['Message']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete objects batch from {bucket_name}: {e}")
            return False 