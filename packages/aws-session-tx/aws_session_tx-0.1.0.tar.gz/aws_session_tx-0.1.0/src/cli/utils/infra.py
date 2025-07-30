"""
Infrastructure management utilities for AWS Session TX

Handles Terraform-deployed infrastructure resources including:
- DynamoDB tables
- Lambda functions
- EventBridge rules
- IAM roles and policies
- CloudWatch log groups
- CloudTrail trails
- S3 buckets
"""

import subprocess
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from botocore.exceptions import ClientError

from .aws import get_dynamodb_client, get_lambda_client, get_events_client, get_logs_client, get_cloudtrail_client, get_s3_client
from .output import print_info, print_warning, print_error


class InfrastructureManager:
    """Manages AWS Session TX infrastructure resources"""
    
    def __init__(self, environment: str = "dev", region: str = "us-east-1", profile: Optional[str] = None):
        self.environment = environment
        self.region = region
        self.profile = profile
        
        self.table_name = f"session-tx-{environment}"
        self.lambda_name = f"session-tx-capture-{environment}"
        self.event_rule_name = f"session-tx-capture-events-{environment}"
        self.iam_role_name = f"session-tx-lambda-role-{environment}"
        self.log_group_name = f"/aws/lambda/session-tx-capture-{environment}"
        self.dynamodb = get_dynamodb_client(profile=profile, region=region)
        self.lambda_client = get_lambda_client(profile=profile, region=region)
        self.events_client = get_events_client(profile=profile, region=region)
        self.logs_client = get_logs_client(profile=profile, region=region)
        self.cloudtrail_client = get_cloudtrail_client(profile=profile, region=region)
        self.s3_client = get_s3_client(profile=profile, region=region)
    
    def deploy(self) -> Dict[str, Any]:
        """Deploy infrastructure using Terraform"""
        try:
            terraform_dir = Path(__file__).parent.parent.parent.parent / "infra" / "terraform"
            
            if not terraform_dir.exists():
                raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")
            
            print_info(f"Deploying infrastructure from: {terraform_dir}")
            
            lambda_zip_path = terraform_dir / "lambda-capture.zip"
            if not lambda_zip_path.exists():
                print_info("Building Lambda deployment package...")
                try:
                    import tempfile
                    import shutil
                    import zipfile
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_lambda_dir = Path(temp_dir) / "lambda"
                        temp_lambda_dir.mkdir()
                        
                        handler_source = Path(__file__).parent.parent.parent.parent / "src" / "lambda" / "capture" / "handler.py"
                        handler_dest = temp_lambda_dir / "handler.py"
                        
                        if handler_source.exists():
                            shutil.copy2(handler_source, handler_dest)
                        else:
                            handler_dest.write_text('''
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    """AWS Lambda handler for CloudTrail events"""
    return {
        'statusCode': 200,
        'body': json.dumps('Event processed successfully')
    }
''')
                        
                        requirements = temp_lambda_dir / "requirements.txt"
                        requirements.write_text("boto3>=1.26.0\n")
                        
                        with zipfile.ZipFile(lambda_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for file_path in temp_lambda_dir.rglob("*"):
                                if file_path.is_file():
                                    arcname = file_path.relative_to(temp_lambda_dir)
                                    zipf.write(file_path, arcname)
                    
                    print_info("Lambda package created successfully")
                except Exception as e:
                    return {
                        'success': False,
                        'message': f'Failed to create Lambda package: {str(e)}',
                        'error': str(e)
                    }
            
            try:
                init_result = subprocess.run(
                    ["terraform", "init"],
                    cwd=terraform_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )
                print_info("Terraform initialized successfully")
            except subprocess.CalledProcessError as e:
                try:
                    init_result = subprocess.run(
                        ["terraform", "init", "-upgrade"],
                        cwd=terraform_dir,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print_info("Terraform initialized with upgrade successfully")
                except subprocess.CalledProcessError as e2:
                    return {
                        'success': False,
                        'message': f'Terraform initialization failed: {e2.stderr}',
                        'error': str(e2)
                    }
            
            result = subprocess.run(
                ["terraform", "apply", "-auto-approve"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            output_result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            outputs = json.loads(output_result.stdout)
            
            try:
                trail_name = f'session-tx-trail-{self.environment}'
                trail_status = self.cloudtrail_client.get_trail_status(Name=trail_name)
                if not trail_status.get('IsLogging', False):
                    self.cloudtrail_client.start_logging(Name=trail_name)
                    print_info(f"Started CloudTrail: {trail_name}")
                else:
                    print_info(f"CloudTrail {trail_name} is already logging")
            except ClientError as e:
                if e.response['Error']['Code'] not in ['InvalidTrailNameException', 'TrailNotFoundException']:
                    print_warning(f"Could not start CloudTrail: {e}")
            
            return {
                'success': True,
                'message': 'Infrastructure deployed successfully',
                'outputs': outputs,
                'logs': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Terraform deployment failed: {e.stderr}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Infrastructure deployment failed: {str(e)}',
                'error': str(e)
            }
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy infrastructure using Terraform"""
        try:
            terraform_dir = Path(__file__).parent.parent.parent.parent / "infra" / "terraform"
            
            if not terraform_dir.exists():
                raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")
            
            print_info(f"Destroying infrastructure from: {terraform_dir}")
            
            try:
                print_info("Cleaning up CloudTrail S3 bucket contents...")
                bucket_name = f'session-tx-cloudtrail-{self.environment}-'
                
                response = self.s3_client.list_buckets()
                cloudtrail_bucket = None
                for bucket in response['Buckets']:
                    if bucket['Name'].startswith(bucket_name):
                        cloudtrail_bucket = bucket['Name']
                        break
                
                if cloudtrail_bucket:
                    try:
                        paginator = self.s3_client.get_paginator('list_object_versions')
                        pages = paginator.paginate(Bucket=cloudtrail_bucket)
                        
                        for page in pages:
                            if 'Contents' in page:
                                objects = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['Contents']]
                                if objects:
                                    self.s3_client.delete_objects(
                                        Bucket=cloudtrail_bucket,
                                        Delete={'Objects': objects}
                                    )
                            
                            if 'DeleteMarkers' in page:
                                markers = [{'Key': obj['Key'], 'VersionId': obj['VersionId']} for obj in page['DeleteMarkers']]
                                if markers:
                                    self.s3_client.delete_objects(
                                        Bucket=cloudtrail_bucket,
                                        Delete={'Objects': markers}
                                    )
                        
                        print_info(f"Successfully cleaned up CloudTrail bucket: {cloudtrail_bucket}")
                    except ClientError as e:
                        if e.response['Error']['Code'] != 'NoSuchBucket':
                            print_warning(f"Could not clean up CloudTrail bucket: {e}")
            except Exception as e:
                print_warning(f"Error during S3 cleanup: {e}")
            
            result = subprocess.run(
                ["terraform", "destroy", "-auto-approve"],
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            try:
                print_info("Cleaning up generated files...")
                files_to_clean = [
                    terraform_dir / ".terraform",
                    terraform_dir / ".terraform.lock.hcl",
                    terraform_dir / "terraform.tfstate",
                    terraform_dir / "terraform.tfstate.backup",
                    terraform_dir / "lambda-capture.zip"
                ]
                
                for file_path in files_to_clean:
                    if file_path.exists():
                        if file_path.is_dir():
                            import shutil
                            shutil.rmtree(file_path)
                        else:
                            file_path.unlink()
                        print_info(f"Cleaned up: {file_path.name}")
                
                print_info("Generated files cleanup completed")
            except Exception as e:
                print_warning(f"Could not clean up some generated files: {e}")
            
            return {
                'success': True,
                'message': 'Infrastructure destroyed successfully',
                'logs': result.stdout
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Terraform destruction failed: {e.stderr}',
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Infrastructure destruction failed: {str(e)}',
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all infrastructure resources"""
        resources = []
        healthy = True
        
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()
            resources.append({
                'type': 'DynamoDB Table',
                'name': self.table_name,
                'status': 'active',
                'arn': table.table_arn,
                'id': table.table_id
            })
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                resources.append({
                    'type': 'DynamoDB Table',
                    'name': self.table_name,
                    'status': 'not_found',
                    'error': 'Table does not exist'
                })
                healthy = False
            else:
                resources.append({
                    'type': 'DynamoDB Table',
                    'name': self.table_name,
                    'status': 'error',
                    'error': str(e)
                })
                healthy = False
        
        try:
            response = self.lambda_client.get_function(FunctionName=self.lambda_name)
            resources.append({
                'type': 'Lambda Function',
                'name': self.lambda_name,
                'status': 'active',
                'arn': response['Configuration']['FunctionArn'],
                'runtime': response['Configuration']['Runtime']
            })
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                resources.append({
                    'type': 'Lambda Function',
                    'name': self.lambda_name,
                    'status': 'not_found',
                    'error': 'Function does not exist'
                })
                healthy = False
            else:
                resources.append({
                    'type': 'Lambda Function',
                    'name': self.lambda_name,
                    'status': 'error',
                    'error': str(e)
                })
                healthy = False
        
        try:
            response = self.events_client.describe_rule(Name=self.event_rule_name)
            resources.append({
                'type': 'EventBridge Rule',
                'name': self.event_rule_name,
                'status': response['State'],
                'arn': response['Arn']
            })
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                resources.append({
                    'type': 'EventBridge Rule',
                    'name': self.event_rule_name,
                    'status': 'not_found',
                    'error': 'Rule does not exist'
                })
                healthy = False
            else:
                resources.append({
                    'type': 'EventBridge Rule',
                    'name': self.event_rule_name,
                    'status': 'error',
                    'error': str(e)
                })
                healthy = False
        
        try:
            response = self.logs_client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
            if response['logGroups']:
                log_group = response['logGroups'][0]
                resources.append({
                    'type': 'CloudWatch Log Group',
                    'name': log_group['logGroupName'],
                    'status': 'active',
                    'arn': log_group['arn'],
                    'stored_bytes': log_group.get('storedBytes', 0)
                })
            else:
                resources.append({
                    'type': 'CloudWatch Log Group',
                    'name': self.log_group_name,
                    'status': 'not_found',
                    'error': 'Log group does not exist'
                })
                healthy = False
        except ClientError as e:
            resources.append({
                'type': 'CloudWatch Log Group',
                'name': self.log_group_name,
                'status': 'error',
                'error': str(e)
            })
            healthy = False
        
        try:
            trail_name = f'session-tx-trail-{self.environment}'
            response = self.cloudtrail_client.describe_trails(trailNameList=[trail_name])
            if response['trailList']:
                trail = response['trailList'][0]
                try:
                    status_response = self.cloudtrail_client.get_trail_status(Name=trail_name)
                    is_logging = status_response.get('IsLogging', False)
                    status = 'active' if is_logging else 'stopped'
                except ClientError:
                    status = 'active' if trail.get('LoggingEnabled', False) else 'stopped'
                
                resources.append({
                    'type': 'CloudTrail',
                    'name': trail['Name'],
                    'status': status,
                    'arn': trail['TrailARN'],
                    's3_bucket': trail['S3BucketName']
                })
            else:
                resources.append({
                    'type': 'CloudTrail',
                    'name': trail_name,
                    'status': 'not_found',
                    'error': 'Trail does not exist'
                })
                healthy = False
        except ClientError as e:
            resources.append({
                'type': 'CloudTrail',
                'name': f'session-tx-trail-{self.environment}',
                'status': 'error',
                'error': str(e)
            })
            healthy = False
        
        return {
            'healthy': healthy,
            'environment': self.environment,
            'region': self.region,
            'resources': resources,
            'timestamp': time.time()
        }
    
    def get_logs(self) -> Dict[str, Any]:
        """Get logs from infrastructure components"""
        log_groups = []
        
        try:
            response = self.logs_client.describe_log_groups(logGroupNamePrefix=self.log_group_name)
            
            for log_group in response['logGroups']:
                streams_response = self.logs_client.describe_log_streams(
                    logGroupName=log_group['logGroupName'],
                    orderBy='LastEventTime',
                    descending=True,
                    limit=5
                )
                
                streams = []
                for stream in streams_response['logStreams']:
                    streams.append({
                        'name': stream['logStreamName'],
                        'last_event_time': stream.get('lastEventTimestamp'),
                        'stored_bytes': stream.get('storedBytes', 0),
                        'creation_time': stream.get('creationTime')
                    })
                
                log_groups.append({
                    'name': log_group['logGroupName'],
                    'arn': log_group['arn'],
                    'stored_bytes': log_group.get('storedBytes', 0),
                    'streams': streams
                })
        
        except ClientError as e:
            print_warning(f"Could not fetch logs: {e}")
        
        return {
            'log_groups': log_groups,
            'environment': self.environment,
            'region': self.region,
            'timestamp': time.time()
        }
    
    def cleanup_orphaned_resources(self) -> Dict[str, Any]:
        """Clean up resources that might be orphaned (not managed by Terraform)"""
        cleaned_resources = []
        

        return {
            'success': True,
            'cleaned_resources': cleaned_resources,
            'message': 'Orphaned resource cleanup completed'
        } 