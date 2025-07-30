"""
Session management for AWS Session TX
"""

import boto3
from typing import List, Optional
from datetime import datetime
from botocore.exceptions import ClientError

from .models import Session, Resource, SessionStatus
from .utils.aws import get_dynamodb_client
from .config import get_config


class SessionManager:
    """Manages sessions and resources in DynamoDB"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1", table_name: Optional[str] = None):
        self.dynamodb = get_dynamodb_client(profile=profile, region=region)
        
        if table_name is None:
            config = get_config()
            table_name = config.get_table_name()
        
        self.table = self.dynamodb.Table(table_name)
        
    def create_session(
        self,
        session_id: str,
        ttl_seconds: int,
        principal_arn: Optional[str] = None,
        tag_key: Optional[str] = None,
        region: str = "us-east-1"
    ) -> Session:
        """Create a new session"""
        session = Session(
            session_id=session_id,
            ttl=ttl_seconds,
            region=region,
            principal_arn=principal_arn,
            tag_key=tag_key
        )
        
        try:
            item = {}
            for key, value in session.model_dump().items():
                if value is not None:
                    if hasattr(value, 'value'): 
                        item[key] = value.value
                    elif isinstance(value, datetime):
                        item[key] = value.isoformat()
                    else:
                        item[key] = value
            
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(PK)"
            )
            return session
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise ValueError(f"Session '{session_id}' already exists")
            raise
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        try:
            response = self.table.get_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'SESSION'
                }
            )
            
            if 'Item' not in response:
                return None
            
            item = response['Item']
            session_data = {}
            for key, value in item.items():
                if key in ['PK', 'SK', 'GSI1PK', 'GSI1SK', 'ttl_expiry']:
                    continue
                if key == 'started_at' and isinstance(value, str):
                    session_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    session_data[key] = value
                
            return Session(**session_data)
        except ClientError:
            return None
    
    def update_session_status(self, session_id: str, status: SessionStatus) -> bool:
        """Update session status"""
        try:
            self.table.update_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'SESSION'
                },
                UpdateExpression="SET #status = :status",
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': status
                },
                ConditionExpression="attribute_exists(PK)"
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            raise
    
    def get_session_resources(self, session_id: str) -> List[Resource]:
        """Get all resources for a session"""
        try:
            response = self.table.query(
                KeyConditionExpression="PK = :pk AND begins_with(SK, :sk_prefix)",
                ExpressionAttributeValues={
                    ':pk': f'SESSION#{session_id}',
                    ':sk_prefix': 'RESOURCE#'
                }
            )
            
            resources = []
            for item in response.get('Items', []):
                resource_data = {}
                for key, value in item.items():
                    if key in ['PK', 'SK', 'GSI1PK', 'GSI1SK', 'ttl_expiry']:
                        continue
                    if key == 'created_at' and isinstance(value, str):
                        resource_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        resource_data[key] = value
                
                resources.append(Resource(**resource_data))
            
            return resources
        except ClientError:
            return []
    
    def add_resource(self, resource: Resource) -> bool:
        """Add a resource to a session"""
        try:
            existing = self.table.get_item(
                Key={
                    'PK': resource.PK,
                    'SK': resource.SK
                }
            )
            
            if 'Item' in existing:
                return True
            
            self.table.put_item(
                Item=resource.model_dump()
            )
            return True
        except ClientError:
            return False
    
    def list_active_sessions(self) -> List[Session]:
        """List all active sessions"""
        try:
            response = self.table.scan(
                FilterExpression="SK = :sk AND #status = :status",
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':sk': 'SESSION',
                    ':status': SessionStatus.ACTIVE
                }
            )
            
            sessions = []
            for item in response.get('Items', []):
                sessions.append(Session(**item))
            
            return sessions
        except ClientError:
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its resources"""
        try:
            resources = self.get_session_resources(session_id)
            for resource in resources:
                self.table.delete_item(
                    Key={
                        'PK': resource.PK,
                        'SK': resource.SK
                    }
                )
            
            self.table.delete_item(
                Key={
                    'PK': f'SESSION#{session_id}',
                    'SK': 'SESSION'
                }
            )
            return True
        except ClientError:
            return False 