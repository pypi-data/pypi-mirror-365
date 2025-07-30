"""
Retry utilities for AWS Session TX

Provides exponential backoff retry logic for AWS API calls that may fail temporarily.
"""

import time
import random
from typing import Callable, Any, Optional, Type, Union, Tuple
from functools import wraps
from botocore.exceptions import ClientError, WaiterError


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_errors: Optional[list] = None
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        
        self.retryable_errors = retryable_errors or [
            'ThrottlingException',
            'RequestLimitExceeded',
            'TooManyRequestsException',
            'InternalServerError',
            'ServiceUnavailable',
            'RequestTimeout',
            'RequestTimeoutException',
            'NetworkingError',
            'ConnectionError',
            'ReadTimeoutError'
        ]


def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable"""
    if isinstance(error, ClientError):
        error_code = error.response['Error']['Code']
        return error_code in [
            'ThrottlingException',
            'RequestLimitExceeded', 
            'TooManyRequestsException',
            'InternalServerError',
            'ServiceUnavailable',
            'RequestTimeout',
            'RequestTimeoutException'
        ]
    elif isinstance(error, WaiterError):
        return True
    else:
        error_name = type(error).__name__
        return any(name in error_name for name in ['Timeout', 'Connection', 'Network'])


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for retry attempt"""
    delay = config.base_delay * (config.exponential_base ** (attempt - 1))
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)
    
    return delay


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        config: Retry configuration
        retryable_exceptions: Tuple of exception types to retry on
    """
    if config is None:
        config = RetryConfig()
    
    if retryable_exceptions is None:
        retryable_exceptions = (ClientError, WaiterError, Exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        raise last_exception
                    
                    if not is_retryable_error(e):
                        raise last_exception
                    
                    delay = calculate_delay(attempt, config)
                    
                    print(f"[WARNING] Attempt {attempt} failed: {type(e).__name__}. Retrying in {delay:.1f}s...")
                    
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


def retry_aws_operation(
    operation_name: str,
    max_attempts: int = 3,
    base_delay: float = 1.0
):
    """
    Decorator specifically for AWS operations with logging
    
    Args:
        operation_name: Name of the AWS operation for logging
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except (ClientError, WaiterError) as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts:
                        print(f"[ERROR] {operation_name} failed after {max_attempts} attempts: {e}")
                        raise last_exception
                    
                    if not is_retryable_error(e):
                        print(f"[ERROR] {operation_name} failed with non-retryable error: {e}")
                        raise last_exception
                    
                    delay = calculate_delay(attempt, config)
                    print(f"[INFO] {operation_name} attempt {attempt} failed, retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
            raise last_exception
        
        return wrapper
    return decorator


@retry_aws_operation("EC2 Describe Instances")
def describe_instances_with_retry(client, **kwargs):
    """Describe EC2 instances with retry logic"""
    return client.describe_instances(**kwargs)


@retry_aws_operation("S3 List Objects")
def list_objects_with_retry(client, **kwargs):
    """List S3 objects with retry logic"""
    return client.list_objects_v2(**kwargs)


@retry_aws_operation("DynamoDB Put Item")
def put_item_with_retry(table, **kwargs):
    """Put DynamoDB item with retry logic"""
    return table.put_item(**kwargs)


@retry_aws_operation("DynamoDB Get Item")
def get_item_with_retry(table, **kwargs):
    """Get DynamoDB item with retry logic"""
    return table.get_item(**kwargs) 