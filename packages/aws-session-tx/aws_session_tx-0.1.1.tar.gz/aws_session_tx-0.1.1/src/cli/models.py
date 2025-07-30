"""
Data models for AWS Session TX
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"


class ResourceType(str, Enum):
    EC2_INSTANCE = "aws:ec2:instance"
    EC2_SECURITY_GROUP = "aws:ec2:security-group"
    EC2_VOLUME = "aws:ec2:volume"
    S3_BUCKET = "aws:s3:bucket"
    ALB_LOAD_BALANCER = "aws:elasticloadbalancing:loadbalancer"
    ALB_TARGET_GROUP = "aws:elasticloadbalancing:targetgroup"
    ALB_LISTENER = "aws:elasticloadbalancing:listener"
    CLOUDWATCH_LOG_GROUP = "aws:logs:log-group"


class Session(BaseModel):
    """Session model for DynamoDB"""
    session_id: str = Field(..., description="Unique session identifier")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ttl: int = Field(..., description="TTL in seconds")
    region: str = Field(..., description="AWS region")
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    principal_arn: Optional[str] = Field(None, description="Principal ARN filter")
    tag_key: Optional[str] = Field(None, description="Tag key filter")
    
    PK: Optional[str] = Field(None, description="Partition key: SESSION#{session_id}")
    SK: Optional[str] = Field(None, description="Sort key: SESSION")
    ttl_expiry: Optional[int] = Field(None, description="TTL expiry timestamp")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.PK:
            self.PK = f"SESSION#{self.session_id}"
        if not self.SK:
            self.SK = "SESSION"
        if not self.ttl_expiry:
            self.ttl_expiry = int(self.started_at.timestamp()) + (7 * 24 * 3600)


class Resource(BaseModel):
    """Resource model for DynamoDB"""
    session_id: str = Field(..., description="Session this resource belongs to")
    arn: str = Field(..., description="Resource ARN")
    type: ResourceType = Field(..., description="Resource type")
    id: str = Field(..., description="Resource ID")
    region: str = Field(..., description="AWS region")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Principal that created the resource")
    tags: Optional[Dict[str, str]] = Field(None, description="Resource tags")
    raw_event: Optional[Union[Dict[str, Any], str]] = Field(None, description="Original CloudTrail event (dict or JSON string)")
    
    PK: Optional[str] = Field(None, description="Partition key: SESSION#{session_id}")
    SK: Optional[str] = Field(None, description="Sort key: RESOURCE#{timestamp}#{arn}")
    GSI1PK: Optional[str] = Field(None, description="GSI1 partition key: TYPE#{type}")
    GSI1SK: Optional[str] = Field(None, description="GSI1 sort key: {timestamp}")
    ttl_expiry: Optional[int] = Field(None, description="TTL expiry timestamp")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.PK:
            self.PK = f"SESSION#{self.session_id}"
        if not self.SK:
            timestamp = int(self.created_at.timestamp())
            self.SK = f"RESOURCE#{timestamp}#{self.arn}"
        if not self.GSI1PK:
            self.GSI1PK = f"TYPE#{self.type}"
        if not self.GSI1SK:
            timestamp = int(self.created_at.timestamp())
            self.GSI1SK = str(timestamp)
        if not self.ttl_expiry:
            self.ttl_expiry = int(self.created_at.timestamp()) + (7 * 24 * 3600)


class DeletionStep(BaseModel):
    """A step in the deletion plan"""
    resource_type: ResourceType
    resource_id: str
    resource_arn: str
    safe: bool = Field(..., description="Whether this resource is safe to delete")
    dependencies: List[str] = Field(default_factory=list, description="Resource IDs this depends on")
    reason: Optional[str] = Field(None, description="Reason for deletion order or safety status")
    estimated_time: int = Field(default=30, description="Estimated deletion time in seconds")


class DeletionPlan(BaseModel):
    """Complete deletion plan for a session"""
    session_id: str
    steps: List[DeletionStep] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list, description="Warnings about the plan")
    estimated_time: int = Field(default=0, description="Total estimated time in seconds")
    
    def model_post_init(self, __context: Any) -> None:
        """Calculate estimated time after initialization"""
        self.estimated_time = sum(step.estimated_time for step in self.steps)


class HydratedResource(BaseModel):
    """Resource with additional metadata for planning"""
    resource: Resource
    current_state: Optional[Dict[str, Any]] = Field(None, description="Current AWS resource state")
    dependencies: List[str] = Field(default_factory=list, description="Resource ARNs this depends on")
    references: List[str] = Field(default_factory=list, description="Resource ARNs that reference this")
    safe_to_delete: bool = Field(default=True, description="Whether this resource can be safely deleted")
    deletion_reason: Optional[str] = Field(None, description="Reason for deletion safety status") 