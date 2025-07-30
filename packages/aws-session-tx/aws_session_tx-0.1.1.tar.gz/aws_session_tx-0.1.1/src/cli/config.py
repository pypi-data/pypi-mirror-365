"""
Configuration management for AWS Session TX

Supports configuration from:
1. Default values
2. Configuration file
3. Environment variables
4. Command line arguments (highest priority)
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class AWSSessionTXConfig(BaseModel):
    """Configuration for AWS Session TX"""
    
    region: str = Field(default="us-east-1", description="Default AWS region")
    profile: Optional[str] = Field(default=None, description="AWS profile to use")
    table_name: str = Field(default="session-tx", description="DynamoDB table name")
    table_region: Optional[str] = Field(default=None, description="DynamoDB table region (if different from default)")
    default_ttl: str = Field(default="24h", description="Default session TTL")
    max_ttl: str = Field(default="7d", description="Maximum allowed session TTL")
    rollback_state_dir: str = Field(default="~/.aws-session-tx/rollback-state", description="Directory for rollback state files")
    continue_on_failure: bool = Field(default=False, description="Continue rollback on individual step failures")
    max_retry_attempts: int = Field(default=3, description="Maximum retry attempts for AWS operations")
    retry_base_delay: float = Field(default=1.0, description="Base delay for retry backoff (seconds)")
    retry_max_delay: float = Field(default=60.0, description="Maximum delay for retry backoff (seconds)")
    output_format: str = Field(default="rich", description="Output format: rich, json, plain")
    verbose: bool = Field(default=False, description="Enable verbose output")
    debug: bool = Field(default=False, description="Enable debug logging")
    supported_regions: list = Field(default=["us-east-1"], description="List of supported AWS regions")
    resource_types: list = Field(default=[
        "aws:ec2:instance",
        "aws:ec2:security-group", 
        "aws:ec2:volume",
        "aws:s3:bucket",
        "aws:elasticloadbalancing:loadbalancer",
        "aws:elasticloadbalancing:targetgroup",
        "aws:elasticloadbalancing:listener",
        "aws:logs:log-group"
    ], description="Supported resource types")
    require_confirmation: bool = Field(default=True, description="Require confirmation for destructive operations")
    dry_run_default: bool = Field(default=False, description="Default to dry-run mode")
    
    @validator('rollback_state_dir')
    def expand_rollback_state_dir(cls, v):
        """Expand ~ to user home directory"""
        return os.path.expanduser(v)
    
    @validator('table_region', pre=True)
    def set_table_region_default(cls, v, values):
        """Set table region to default region if not specified"""
        if v is None:
            return values.get('region', 'us-east-1')
        return v
    
    @classmethod
    def from_file(cls, config_path: Optional[str] = None) -> 'AWSSessionTXConfig':
        """Load configuration from file"""
        if config_path is None:
            config_paths = [
                Path.home() / '.aws-session-tx' / 'config.json',
                Path.home() / '.config' / 'aws-session-tx' / 'config.json',
                Path.cwd() / 'aws-session-tx.json',
                Path.cwd() / '.aws-session-tx.json'
            ]
            
            for path in config_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                return cls(**config_data)
            except Exception as e:
                print(f"Warning: Failed to load config from {config_path}: {e}")
        
        return cls()
    
    @classmethod
    def from_env(cls) -> 'AWSSessionTXConfig':
        """Load configuration from environment variables"""
        config_data = {}
        
        env_mapping = {
            'AWS_SESSION_TX_REGION': 'region',
            'AWS_SESSION_TX_PROFILE': 'profile',
            'AWS_SESSION_TX_TABLE_NAME': 'table_name',
            'AWS_SESSION_TX_TABLE_REGION': 'table_region',
            'AWS_SESSION_TX_DEFAULT_TTL': 'default_ttl',
            'AWS_SESSION_TX_MAX_TTL': 'max_ttl',
            'AWS_SESSION_TX_ROLLBACK_STATE_DIR': 'rollback_state_dir',
            'AWS_SESSION_TX_CONTINUE_ON_FAILURE': 'continue_on_failure',
            'AWS_SESSION_TX_MAX_RETRY_ATTEMPTS': 'max_retry_attempts',
            'AWS_SESSION_TX_RETRY_BASE_DELAY': 'retry_base_delay',
            'AWS_SESSION_TX_RETRY_MAX_DELAY': 'retry_max_delay',
            'AWS_SESSION_TX_OUTPUT_FORMAT': 'output_format',
            'AWS_SESSION_TX_VERBOSE': 'verbose',
            'AWS_SESSION_TX_DEBUG': 'debug',
            'AWS_SESSION_TX_REQUIRE_CONFIRMATION': 'require_confirmation',
            'AWS_SESSION_TX_DRY_RUN_DEFAULT': 'dry_run_default'
        }
        
        for env_var, config_field in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if config_field in ['continue_on_failure', 'verbose', 'debug', 'require_confirmation', 'dry_run_default']:
                    config_data[config_field] = value.lower() in ['true', '1', 'yes', 'on']
                elif config_field in ['max_retry_attempts']:
                    config_data[config_field] = int(value)
                elif config_field in ['retry_base_delay', 'retry_max_delay']:
                    config_data[config_field] = float(value)
                else:
                    config_data[config_field] = value
        
        return cls(**config_data)
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'AWSSessionTXConfig':
        """Load configuration with priority: env > file > defaults"""
        config = cls()
        file_config = cls.from_file(config_path)
        config = config.copy(update=file_config.dict(exclude_unset=True))
        env_config = cls.from_env()
        config = config.copy(update=env_config.dict(exclude_unset=True))
        
        return config
    
    def save(self, config_path: str) -> None:
        """Save configuration to file"""
        config_dir = Path(config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.dict(), f, indent=2, default=str)
    
    def get_table_name(self, environment: Optional[str] = None) -> str:
        """Get table name with optional environment suffix"""
        if environment:
            return f"{self.table_name}-{environment}"
        return self.table_name
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration as dictionary"""
        return {
            'max_attempts': self.max_retry_attempts,
            'base_delay': self.retry_base_delay,
            'max_delay': self.retry_max_delay
        }


_config: Optional[AWSSessionTXConfig] = None


def get_config() -> AWSSessionTXConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = AWSSessionTXConfig.load()
    return _config


def set_config(config: AWSSessionTXConfig) -> None:
    """Set global configuration instance"""
    global _config
    _config = config


def reload_config(config_path: Optional[str] = None) -> AWSSessionTXConfig:
    """Reload configuration from file/environment"""
    global _config
    _config = AWSSessionTXConfig.load(config_path)
    return _config 