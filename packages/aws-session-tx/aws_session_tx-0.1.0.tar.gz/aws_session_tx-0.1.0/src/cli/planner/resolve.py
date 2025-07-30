"""
Resource resolution and hydration for AWS Session TX
"""

from typing import Optional, Dict, Any, List
from botocore.exceptions import ClientError

from ..models import Resource, HydratedResource, ResourceType
from ..utils.aws import (
    get_ec2_client, get_elbv2_client, get_s3_client, get_logs_client,
    get_sts_client, paginate_api_call
)


class ResourceResolver:
    """Resolves and hydrates resources with current AWS state"""
    
    def __init__(self, profile: Optional[str] = None, region: str = "us-east-1"):
        self.region = region
        self.profile = profile
        self.ec2 = get_ec2_client(profile=profile, region=region)
        self.elbv2 = get_elbv2_client(profile=profile, region=region)
        self.s3 = get_s3_client(profile=profile, region=region)
        self.logs = get_logs_client(profile=profile, region=region)
        

        try:
            sts = get_sts_client(profile=profile, region=region)
            self.account_id = sts.get_caller_identity()['Account']
        except Exception:
            self.account_id = "000000000000"
    
    def hydrate_resource(self, resource: Resource) -> HydratedResource:
        """Hydrate a resource with current AWS state and dependencies"""
        try:
            if resource.type == ResourceType.EC2_INSTANCE:
                return self._hydrate_ec2_instance(resource)
            elif resource.type == ResourceType.EC2_SECURITY_GROUP:
                return self._hydrate_security_group(resource)
            elif resource.type == ResourceType.S3_BUCKET:
                return self._hydrate_s3_bucket(resource)
            elif resource.type == ResourceType.ALB_LOAD_BALANCER:
                return self._hydrate_load_balancer(resource)
            elif resource.type == ResourceType.ALB_TARGET_GROUP:
                return self._hydrate_target_group(resource)
            elif resource.type == ResourceType.ALB_LISTENER:
                return self._hydrate_listener(resource)
            elif resource.type == ResourceType.CLOUDWATCH_LOG_GROUP:
                return self._hydrate_log_group(resource)
            else:
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Unknown resource type"
                )
        except ClientError as e:
            return HydratedResource(
                resource=resource,
                current_state=None,
                dependencies=[],
                references=[],
                safe_to_delete=False,
                deletion_reason=f"Resource not found: {e}"
            )
    
    def _hydrate_ec2_instance(self, resource: Resource) -> HydratedResource:
        """Hydrate EC2 instance with current state"""
        try:
            response = self.ec2.describe_instances(InstanceIds=[resource.id])
            if not response['Reservations']:
                raise ClientError({'Error': {'Code': 'InvalidInstanceID.NotFound'}}, 'DescribeInstances')
            
            instance = response['Reservations'][0]['Instances'][0]
            state = instance['State']['Name']
            
            safe_to_delete = state in ['stopped', 'terminated']
            deletion_reason = None if safe_to_delete else f"Instance is in {state} state"
            
            dependencies = []
            for sg in instance.get('SecurityGroups', []):
                sg_arn = f"arn:aws:ec2:{self.region}:{self.account_id}:security-group/{sg['GroupId']}"
                dependencies.append(sg_arn)
            
            for block_device in instance.get('BlockDeviceMappings', []):
                if 'Ebs' in block_device:
                    volume_arn = f"arn:aws:ec2:{self.region}:{self.account_id}:volume/{block_device['Ebs']['VolumeId']}"
                    dependencies.append(volume_arn)
            
            return HydratedResource(
                resource=resource,
                current_state=instance,
                dependencies=dependencies,
                references=[],
                safe_to_delete=safe_to_delete,
                deletion_reason=deletion_reason
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidInstanceID.NotFound':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Instance already terminated"
                )
            raise
    
    def _hydrate_security_group(self, resource: Resource) -> HydratedResource:
        """Hydrate security group with current state"""
        try:
            response = self.ec2.describe_security_groups(GroupIds=[resource.id])
            if not response['SecurityGroups']:
                raise ClientError({'Error': {'Code': 'InvalidGroup.NotFound'}}, 'DescribeSecurityGroups')
            
            sg = response['SecurityGroups'][0]
            
            references = []
            
            eni_response = self.ec2.describe_network_interfaces(
                Filters=[{'Name': 'group-id', 'Values': [resource.id]}]
            )
            for eni in eni_response.get('NetworkInterfaces', []):
                references.append(eni['NetworkInterfaceId'])
            
            instance_response = self.ec2.describe_instances(
                Filters=[{'Name': 'instance.group-id', 'Values': [resource.id]}]
            )
            for reservation in instance_response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    references.append(instance['InstanceId'])
            
            safe_to_delete = len(references) == 0
            deletion_reason = None if safe_to_delete else f"Security group is attached to {len(references)} resources"
            
            return HydratedResource(
                resource=resource,
                current_state=sg,
                dependencies=[],
                references=references,
                safe_to_delete=safe_to_delete,
                deletion_reason=deletion_reason
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'InvalidGroup.NotFound':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Security group already deleted"
                )
            raise
    
    def _hydrate_s3_bucket(self, resource: Resource) -> HydratedResource:
        """Hydrate S3 bucket with current state"""
        try:
            response = self.s3.head_bucket(Bucket=resource.id)
            
            objects_response = self.s3.list_objects_v2(Bucket=resource.id, MaxKeys=1)
            is_empty = 'Contents' not in objects_response
            
            safe_to_delete = is_empty
            deletion_reason = None if safe_to_delete else "Bucket is not empty"
            
            return HydratedResource(
                resource=resource,
                current_state={'Location': response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amz-bucket-region')},
                dependencies=[],
                references=[],
                safe_to_delete=safe_to_delete,
                deletion_reason=deletion_reason
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Bucket already deleted"
                )
            raise
    
    def _hydrate_load_balancer(self, resource: Resource) -> HydratedResource:
        """Hydrate load balancer with current state"""
        try:
            response = self.elbv2.describe_load_balancers(LoadBalancerArns=[resource.arn])
            if not response['LoadBalancers']:
                raise ClientError({'Error': {'Code': 'LoadBalancerNotFound'}}, 'DescribeLoadBalancers')
            
            lb = response['LoadBalancers'][0]
            
            listeners_response = self.elbv2.describe_listeners(LoadBalancerArn=resource.arn)
            listeners = listeners_response.get('Listeners', [])
            
            dependencies = [listener['ListenerArn'] for listener in listeners]
            
            return HydratedResource(
                resource=resource,
                current_state=lb,
                dependencies=dependencies,
                references=[],
                safe_to_delete=True,
                deletion_reason=None
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'LoadBalancerNotFound':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Load balancer already deleted"
                )
            raise
    
    def _hydrate_target_group(self, resource: Resource) -> HydratedResource:
        """Hydrate target group with current state"""
        try:
            response = self.elbv2.describe_target_groups(TargetGroupArns=[resource.arn])
            if not response['TargetGroups']:
                raise ClientError({'Error': {'Code': 'TargetGroupNotFound'}}, 'DescribeTargetGroups')
            
            tg = response['TargetGroups'][0]
            
            listeners_response = self.elbv2.describe_listeners()
            references = []
            
            for listener in listeners_response.get('Listeners', []):
                for action in listener.get('DefaultActions', []):
                    if action.get('Type') == 'forward' and action.get('TargetGroupArn') == resource.arn:
                        references.append(listener['ListenerArn'])
            
            safe_to_delete = len(references) == 0
            deletion_reason = None if safe_to_delete else f"Target group is attached to {len(references)} listeners"
            
            return HydratedResource(
                resource=resource,
                current_state=tg,
                dependencies=[],
                references=references,
                safe_to_delete=safe_to_delete,
                deletion_reason=deletion_reason
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'TargetGroupNotFound':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Target group already deleted"
                )
            raise
    
    def _hydrate_listener(self, resource: Resource) -> HydratedResource:
        """Hydrate listener with current state"""
        try:
            response = self.elbv2.describe_listeners(ListenerArns=[resource.arn])
            if not response['Listeners']:
                raise ClientError({'Error': {'Code': 'ListenerNotFound'}}, 'DescribeListeners')
            
            listener = response['Listeners'][0]
            
            return HydratedResource(
                resource=resource,
                current_state=listener,
                dependencies=[],
                references=[],
                safe_to_delete=True,
                deletion_reason=None
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ListenerNotFound':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Listener already deleted"
                )
            raise
    
    def _hydrate_log_group(self, resource: Resource) -> HydratedResource:
        """Hydrate CloudWatch log group with current state"""
        try:
            log_group_name = resource.arn.split(':')[-1]
            
            response = self.logs.describe_log_groups(logGroupNamePrefix=log_group_name)
            
            log_group = None
            for lg in response.get('logGroups', []):
                if lg['logGroupName'] == log_group_name:
                    log_group = lg
                    break
            
            if not log_group:
                raise ClientError({'Error': {'Code': 'ResourceNotFoundException'}}, 'DescribeLogGroups')
            
            return HydratedResource(
                resource=resource,
                current_state=log_group,
                dependencies=[],
                references=[],
                safe_to_delete=True,
                deletion_reason=None
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return HydratedResource(
                    resource=resource,
                    current_state=None,
                    dependencies=[],
                    references=[],
                    safe_to_delete=True,
                    deletion_reason="Log group already deleted"
                )
            raise 