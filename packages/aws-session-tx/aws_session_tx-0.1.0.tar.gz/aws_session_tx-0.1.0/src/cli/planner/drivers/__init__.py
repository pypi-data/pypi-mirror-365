"""
Resource drivers for AWS Session TX
"""

from typing import Dict, Type
from .base import ResourceDriver
from .s3 import S3Driver
from .ec2 import EC2Driver
from .alb import ALBDriver
from .logs import LogsDriver

DRIVERS: Dict[str, Type[ResourceDriver]] = {
    "aws:s3:bucket": S3Driver,
    "aws:ec2:instance": EC2Driver,
    "aws:ec2:security-group": EC2Driver,
    "aws:ec2:volume": EC2Driver,
    "aws:elasticloadbalancing:loadbalancer": ALBDriver,
    "aws:elasticloadbalancing:targetgroup": ALBDriver,
    "aws:elasticloadbalancing:listener": ALBDriver,
    "aws:logs:log-group": LogsDriver,
}

def get_driver(resource_type: str) -> Type[ResourceDriver]:
    """Get the appropriate driver for a resource type"""
    return DRIVERS.get(resource_type)

def get_supported_types() -> list:
    """Get list of supported resource types"""
    return list(DRIVERS.keys()) 