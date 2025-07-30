"""
AWS utilities for Session TX
"""

import boto3
from typing import Optional, Dict, Any, List
from botocore.config import Config
from botocore.exceptions import ClientError


def get_boto3_session(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get a boto3 session with the specified profile and region"""
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)


def get_dynamodb_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get DynamoDB client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.resource('dynamodb')


def get_ec2_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get EC2 client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('ec2')


def get_elbv2_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get ELBv2 client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('elbv2')


def get_s3_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get S3 client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('s3')


def get_logs_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get CloudWatch Logs client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('logs')


def get_lambda_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get Lambda client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('lambda')


def get_events_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get EventBridge client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('events')


def get_cloudtrail_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get CloudTrail client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('cloudtrail')


def get_sts_client(profile: Optional[str] = None, region: str = "us-east-1"):
    """Get STS client"""
    session = get_boto3_session(profile=profile, region=region)
    return session.client('sts')


def paginate_api_call(client, method_name: str, **kwargs) -> List[Dict[str, Any]]:
    """Generic pagination helper for AWS API calls"""
    paginator = client.get_paginator(method_name)
    results = []
    
    for page in paginator.paginate(**kwargs):
        for key, value in page.items():
            if isinstance(value, list):
                results.extend(value)
                break
    
    return results


def wait_for_resource_deletion(client, waiter_name: str, **kwargs):
    """Wait for a resource to be deleted using AWS waiters"""
    try:
        waiter = client.get_waiter(waiter_name)
        waiter.wait(**kwargs)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return True  
        raise


def get_resource_arn(service: str, resource_id: str, region: str, account_id: Optional[str] = None) -> str:
    """Generate ARN for a resource"""
    if not account_id:
        sts = get_sts_client(region=region)
        account_id = sts.get_caller_identity()['Account']
    
    arn_formats = {
        'ec2': {
            'instance': f'arn:aws:ec2:{region}:{account_id}:instance/{resource_id}',
            'security-group': f'arn:aws:ec2:{region}:{account_id}:security-group/{resource_id}',
            'volume': f'arn:aws:ec2:{region}:{account_id}:volume/{resource_id}'
        },
        's3': {
            'bucket': f'arn:aws:s3:::{resource_id}'
        },
        'elasticloadbalancing': {
            'loadbalancer': f'arn:aws:elasticloadbalancing:{region}:{account_id}:loadbalancer/{resource_id}',
            'targetgroup': f'arn:aws:elasticloadbalancing:{region}:{account_id}:targetgroup/{resource_id}',
            'listener': f'arn:aws:elasticloadbalancing:{region}:{account_id}:listener/{resource_id}'
        },
        'logs': {
            'log-group': f'arn:aws:logs:{region}:{account_id}:log-group:{resource_id}'
        }
    }
    
    if service in arn_formats:
        for resource_type in arn_formats[service]:
            if resource_type in resource_id.lower():
                return arn_formats[service][resource_type]
        
        first_type = list(arn_formats[service].keys())[0]
        return arn_formats[service][first_type].replace(f'/{first_type}/', f'/{resource_id}')
    
    return f'arn:aws:{service}:{region}:{account_id}:{resource_id}'


def extract_resource_info_from_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract resource information from CloudTrail event"""
    detail = event.get('detail', {})
    
    event_name = detail.get('eventName', '')
    service = detail.get('eventSource', '').split('.')[0]
    region = detail.get('awsRegion', 'us-east-1')
    
    resource_id = None
    resource_arn = None
    
    if 'responseElements' in detail:
        response = detail['responseElements']
        
        if event_name == 'RunInstances' and 'instancesSet' in response:
            instances = response['instancesSet']['items']
            if instances:
                resource_id = instances[0]['instanceId']
                resource_arn = instances[0].get('instanceArn')
        
        elif event_name == 'CreateSecurityGroup' and 'groupId' in response:
            resource_id = response['groupId']
            resource_arn = response.get('groupArn')
        
        elif event_name == 'CreateBucket' and 'location' in response:
            request_params = detail.get('requestParameters', {})
            resource_id = request_params.get('bucketName')
            if resource_id:
                resource_arn = f'arn:aws:s3:::{resource_id}'
        
        elif event_name == 'CreateLoadBalancer' and 'loadBalancers' in response:
            lbs = response['loadBalancers']
            if lbs:
                resource_id = lbs[0]['loadBalancerArn'].split('/')[-1]
                resource_arn = lbs[0]['loadBalancerArn']
        
        elif event_name == 'CreateTargetGroup' and 'targetGroups' in response:
            tgs = response['targetGroups']
            if tgs:
                resource_id = tgs[0]['targetGroupArn'].split('/')[-1]
                resource_arn = tgs[0]['targetGroupArn']
        
        elif event_name == 'CreateLogGroup':
            request_params = detail.get('requestParameters', {})
            resource_id = request_params.get('logGroupName')
            if resource_id:
                sts = get_sts_client(region=region)
                account_id = sts.get_caller_identity()['Account']
                resource_arn = f'arn:aws:logs:{region}:{account_id}:log-group:{resource_id}'
    
    return {
        'event_name': event_name,
        'service': service,
        'region': region,
        'resource_id': resource_id,
        'resource_arn': resource_arn,
        'raw_event': detail
    } 