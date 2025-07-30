#!/usr/bin/env python3
"""
AWS Session TX CLI - Main entry point (Improved Version)
"""

import typer
import json
from typing import Optional, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich import box

from .sessions import SessionManager
from .planner.graph import DependencyGraph
from .planner.resolve import ResourceResolver
from .models import SessionStatus
from .utils.aws import get_sts_client
from .utils.output import (
    print_success, print_error, print_warning, print_info, print_header,
    format_session_table, format_resources_table, format_deletion_plan,
    print_session_status, print_deletion_plan, print_rollback_results,
    print_json_output, create_progress_tracker
)
from .utils.rollback import execute_rollback_with_recovery, get_rollback_status
from .config import get_config, reload_config

app = typer.Typer(
    name="aws-tx",
    help="AWS Session TX - Per-session resource management for AWS sandboxes",
    add_completion=False,
)

console = Console()

@app.command()
def begin(
    session: str = typer.Argument(..., help="Session identifier"),
    ttl: str = typer.Option("24h", help="Session TTL (e.g., 24h, 7d)"),
    principal: Optional[str] = typer.Option(None, help="Principal ARN to filter resources"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    tag_key: Optional[str] = typer.Option(None, help="Tag key for resource filtering"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Start a new session and begin tracking resource creation."""
    try:
        session_mgr = SessionManager(profile=profile, region=region)
        ttl_seconds = _parse_ttl(ttl)
        session_data = session_mgr.create_session(
            session_id=session,
            ttl_seconds=ttl_seconds,
            principal_arn=principal,
            tag_key=tag_key,
            region=region
        )
        
        if json_output:
            print_json_output(session_data.model_dump())
        else:
            print_success(f"Session '{session}' started successfully")
            print_info(f"TTL: {ttl}")
            print_info(f"Region: {region}")
            if principal:
                print_info(f"Principal: {principal}")
            if tag_key:
                print_info(f"Tag Key: {tag_key}")
                
    except Exception as e:
        if debug:
            raise
        print_error(f"Failed to start session: {e}")
        raise typer.Exit(1)

@app.command()
def status(
    session: str = typer.Argument(..., help="Session identifier"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Show session status and tracked resources."""
    try:
        session_mgr = SessionManager(profile=profile, region=region)
        
        session_info = session_mgr.get_session(session)
        if not session_info:
            print_error(f"Session '{session}' not found")
            raise typer.Exit(1)
        
        resources = session_mgr.get_session_resources(session)
        rollback_status = get_rollback_status(session)
        
        if json_output:
            output = {
                "session": session_info.model_dump(),
                "resources": [r.model_dump() for r in resources],
                "count": len(resources),
                "rollback_status": rollback_status
            }
            print_json_output(output)
        else:
            print_session_status(session_info, resources)
            
            if rollback_status and rollback_status['has_incomplete_rollback']:
                print_warning("Incomplete rollback detected!")
                print_info(f"Progress: {rollback_status['progress']['completed']}/{rollback_status['progress']['total_steps']} completed")
                print_info("Use 'aws-tx rollback --resume' to continue")
                
    except Exception as e:
        if debug:
            raise
        print_error(f"Failed to get session status: {e}")
        raise typer.Exit(1)

@app.command()
def plan(
    session: str = typer.Argument(..., help="Session identifier"),
    out: Optional[str] = typer.Option(None, help="Output plan to file"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Generate a deletion plan for session resources."""
    try:
        session_mgr = SessionManager(profile=profile, region=region)
        
        session_info = session_mgr.get_session(session)
        if not session_info:
            print_error(f"Session '{session}' not found")
            raise typer.Exit(1)
        
        resources = session_mgr.get_session_resources(session)
        if not resources:
            print_warning("No resources to plan deletion for")
            return
        
        print_info("Generating deletion plan...")
        resolver = ResourceResolver(profile=profile, region=region)
        graph = DependencyGraph()
        
        for resource in resources:
            hydrated = resolver.hydrate_resource(resource)
            graph.add_resource(hydrated)
        
        plan = graph.generate_deletion_plan()
        
        if json_output:
            print_json_output(plan.model_dump())
        else:
            print_deletion_plan(plan)
        
        if out:
            with open(out, 'w') as f:
                json.dump(plan.model_dump(), f, indent=2, default=str)
            print_success(f"Plan saved to {out}")
                
    except Exception as e:
        if debug:
            raise
        print_error(f"Failed to generate plan: {e}")
        raise typer.Exit(1)

@app.command()
def rollback(
    session: str = typer.Argument(..., help="Session identifier"),
    approve: bool = typer.Option(False, "--approve", help="Skip confirmation prompt"),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompt (alias for --approve)"),
    resume: bool = typer.Option(False, "--resume", help="Resume from previous rollback state"),
    continue_on_failure: bool = typer.Option(False, "--continue-on-failure", help="Continue on individual step failures"),
    force: bool = typer.Option(False, "--force", help="Force deletion (skip verification)"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Execute the deletion plan for session resources with recovery capabilities."""
    try:
        session_mgr = SessionManager(profile=profile, region=region)
        
        rollback_status = get_rollback_status(session)
        if rollback_status and rollback_status['has_incomplete_rollback']:
            print_warning(f"Found incomplete rollback for session '{session}'")
            print_info(f"Progress: {rollback_status['progress']['completed']}/{rollback_status['progress']['total_steps']} completed")
            
            if not resume and not typer.confirm("Do you want to resume the previous rollback?"):
                print_info("Use --resume flag to continue from where it left off")
                return
        
        session_info = session_mgr.get_session(session)
        if not session_info:
            print_error(f"Session '{session}' not found")
            raise typer.Exit(1)
        if not resume:
            resources = session_mgr.get_session_resources(session)
            if not resources:
                print_warning("No resources to delete")
                return
            
            print_info("Generating deletion plan...")
            resolver = ResourceResolver(profile=profile, region=region)
            hydrated_resources = []
            graph = DependencyGraph()
            
            for resource in resources:
                hydrated = resolver.hydrate_resource(resource)
                hydrated_resources.append(hydrated)
                graph.add_resource(hydrated)
            
            plan = graph.generate_deletion_plan()
            
            print_deletion_plan(plan, json_output=json_output)
            
            if not (approve or yes):
                if not typer.confirm("Are you sure you want to delete all session resources?"):
                    print_info("Rollback cancelled")
                    return
        else:
            plan = None
            resources = session_mgr.get_session_resources(session)
            resolver = ResourceResolver(profile=profile, region=region)
            hydrated_resources = [resolver.hydrate_resource(r) for r in resources]
        
        print_header("Executing Rollback")
        
        results = execute_rollback_with_recovery(
            session_id=session,
            plan=plan,
            hydrated_resources=hydrated_resources,
            region=region,
            resume=resume,
            continue_on_failure=continue_on_failure,
            force=force
        )
        
        print_rollback_results(results, json_output=json_output)
        
        if results['success']:
            session_mgr.update_session_status(session, SessionStatus.ROLLED_BACK)
        
        if results['failed'] > 0:
            raise typer.Exit(1)
            
    except Exception as e:
        if debug:
            raise
        print_error(f"Failed to execute rollback: {e}")
        raise typer.Exit(1)

@app.command()
def commit(
    session: str = typer.Argument(..., help="Session identifier"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Commit a session (mark as completed, keep resources)."""
    try:
        session_mgr = SessionManager(profile=profile, region=region)
        
        session_info = session_mgr.get_session(session)
        if not session_info:
            print_error(f"Session '{session}' not found")
            raise typer.Exit(1)
        success = session_mgr.update_session_status(session, SessionStatus.COMMITTED)
        
        if success:
            if json_output:
                print_json_output({"status": "committed", "session_id": session})
            else:
                print_success(f"Session '{session}' committed successfully")
                print_info("Resources will be kept and session tracking will stop")
        else:
            print_error(f"Failed to commit session '{session}'")
            raise typer.Exit(1)
            
    except Exception as e:
        if debug:
            raise
        print_error(f"Failed to commit session: {e}")
        raise typer.Exit(1)


@app.command()
def config(
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    init: bool = typer.Option(False, "--init", help="Initialize configuration file"),
    path: Optional[str] = typer.Option(None, "--path", help="Configuration file path"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """Manage AWS Session TX configuration."""
    try:
        if show:
            config = get_config()
            if json_output:
                print_json_output(config.dict())
            else:
                print_header("Current Configuration")
                from rich.table import Table
                from rich import box
                
                table = Table(box=box.ROUNDED)
                table.add_column("Setting", style="cyan")
                table.add_column("Value", style="green")
                
                for key, value in config.model_dump().items():
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    table.add_row(key, str(value))
                
                console.print(table)
        
        elif init:
            config = get_config()
            config_path = path or str(Path.home() / '.aws-session-tx' / 'config.json')
            
            config.save(config_path)
            print_success(f"Configuration initialized at: {config_path}")
            print_info("Edit this file to customize your settings")
        
        else:
            typer.echo("Use --show to display current configuration or --init to create a config file")
            
    except Exception as e:
        print_error(f"Configuration operation failed: {e}")
        raise typer.Exit(1)


@app.command()
def infra(
    action: str = typer.Argument(..., help="Infrastructure action (deploy, destroy, status, logs)"),
    environment: str = typer.Option("dev", help="Environment name"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Manage AWS Session TX infrastructure (Terraform resources)."""
    try:
        from .utils.infra import InfrastructureManager
        
        infra_mgr = InfrastructureManager(
            environment=environment,
            region=region,
            profile=profile
        )
        
        if action == "deploy":
            print_info("Deploying AWS Session TX infrastructure...")
            result = infra_mgr.deploy()
            if json_output:
                print_json_output(result)
            else:
                print_success("Infrastructure deployed successfully!")
                print_info(f"Environment: {environment}")
                print_info(f"Region: {region}")
                
        elif action == "destroy":
            print_warning("This will destroy ALL AWS Session TX infrastructure!")
            print_warning("This includes DynamoDB tables, Lambda functions, EventBridge rules, and more.")
            
            print_info("Destroying AWS Session TX infrastructure...")
            result = infra_mgr.destroy()
            if json_output:
                print_json_output(result)
            else:
                print_success("Infrastructure destroyed successfully!")
                
        elif action == "status":
            print_info("Checking infrastructure status...")
            status = infra_mgr.get_status()
            if json_output:
                print_json_output(status)
            else:
                print_infrastructure_status(status)
                
        elif action == "logs":
            print_info("Fetching infrastructure logs...")
            logs = infra_mgr.get_logs()
            if json_output:
                print_json_output(logs)
            else:
                print_infrastructure_logs(logs)
                
        else:
            print_error(f"Unknown action: {action}")
            print_info("Available actions: deploy, destroy, status, logs")
            raise typer.Exit(1)
            
    except Exception as e:
        if debug:
            raise
        print_error(f"Infrastructure operation failed: {e}")
        raise typer.Exit(1)


@app.command()
def cleanup(
    what: str = typer.Argument(..., help="What to clean up (sessions, infrastructure, all)"),
    session: Optional[str] = typer.Option(None, help="Specific session to clean up (for sessions cleanup)"),
    environment: str = typer.Option("dev", help="Environment name (for infrastructure cleanup)"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    profile: Optional[str] = typer.Option(None, help="AWS profile to use"),
    approve: bool = typer.Option(False, "--approve", help="Skip confirmation prompt"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging"),
):
    """Comprehensive cleanup of AWS Session TX resources and infrastructure."""
    try:
        if what == "sessions":
            if session:
                print_info(f"Cleaning up session: {session}")
                session_mgr = SessionManager(profile=profile, region=region)
                
                session_info = session_mgr.get_session(session)
                if not session_info:
                    print_error(f"Session '{session}' not found")
                    raise typer.Exit(1)
                
                resources = session_mgr.get_session_resources(session)
                if resources:
                    print_info(f"Found {len(resources)} resources to delete")
                    
                    if not approve:
                        if not typer.confirm(f"Are you sure you want to delete all resources for session '{session}'?"):
                            print_info("Cleanup cancelled")
                            return
                    
                    resolver = ResourceResolver(profile=profile, region=region)
                    graph = DependencyGraph()
                    
                    for resource in resources:
                        hydrated = resolver.hydrate_resource(resource)
                        graph.add_resource(hydrated)
                    
                    plan = graph.generate_deletion_plan()
                    
                    results = execute_rollback_with_recovery(
                        session_id=session,
                        plan=plan,
                        hydrated_resources=[resolver.hydrate_resource(r) for r in resources],
                        region=region,
                        continue_on_failure=True
                    )
                    
                    if json_output:
                        print_json_output(results)
                    else:
                        print_rollback_results(results)
                else:
                    print_info(f"No resources found for session '{session}'")
                
                if session_mgr.delete_session(session):
                    print_success(f"Session '{session}' deleted successfully")
                else:
                    print_error(f"Failed to delete session '{session}'")
                    
            else:
                print_info("Cleaning up all sessions")
                session_mgr = SessionManager(profile=profile, region=region)
                
                active_sessions = session_mgr.list_active_sessions()
                if not active_sessions:
                    print_info("No active sessions found")
                    return
                
                print_info(f"Found {len(active_sessions)} active sessions")
                
                if not approve:
                    if not typer.confirm(f"Are you sure you want to delete all {len(active_sessions)} active sessions?"):
                        print_info("Cleanup cancelled")
                        return
                
                deleted_count = 0
                for session_info in active_sessions:
                    session_id = session_info.session_id
                    print_info(f"Cleaning up session: {session_id}")
                    
                    resources = session_mgr.get_session_resources(session_id)
                    if resources:
                        resolver = ResourceResolver(profile=profile, region=region)
                        graph = DependencyGraph()
                        
                        for resource in resources:
                            hydrated = resolver.hydrate_resource(resource)
                            graph.add_resource(hydrated)
                        
                        plan = graph.generate_deletion_plan()
                        
                        results = execute_rollback_with_recovery(
                            session_id=session_id,
                            plan=plan,
                            hydrated_resources=[resolver.hydrate_resource(r) for r in resources],
                            region=region,
                            continue_on_failure=True
                        )
                        
                        if results['success']:
                            print_success(f"Session {session_id} resources cleaned up")
                        else:
                            print_warning(f"Session {session_id} had some cleanup issues")
                    
                    if session_mgr.delete_session(session_id):
                        deleted_count += 1
                        print_success(f"Session {session_id} deleted")
                    else:
                        print_error(f"Failed to delete session {session_id}")
                
                print_success(f"Cleanup completed: {deleted_count}/{len(active_sessions)} sessions deleted")
                
        elif what == "infrastructure":
            print_info("Cleaning up infrastructure")
            
            if not approve:
                print_warning("This will destroy ALL AWS Session TX infrastructure!")
                print_warning("This includes DynamoDB tables, Lambda functions, EventBridge rules, and more.")
            
            from .utils.infra import InfrastructureManager
            infra_mgr = InfrastructureManager(environment=environment, region=region, profile=profile)
            
            result = infra_mgr.destroy()
            if json_output:
                print_json_output(result)
            else:
                if result['success']:
                    print_success("Infrastructure destroyed successfully")
                else:
                    print_error(f"Infrastructure destruction failed: {result.get('message', 'Unknown error')}")
                    
        elif what == "all":
            print_info("Performing comprehensive cleanup (sessions + infrastructure)")
            
            if not approve:
                print_warning("This will destroy ALL AWS Session TX resources!")
                print_warning("This includes:")
                print_warning("  - All active sessions and their resources")
                print_warning("  - All infrastructure (DynamoDB, Lambda, EventBridge, etc.)")
            
            print_info("Step 1: Cleaning up sessions...")
            session_mgr = SessionManager(profile=profile, region=region)
            active_sessions = session_mgr.list_active_sessions()
            
            if active_sessions:
                print_info(f"Found {len(active_sessions)} active sessions to clean up")
                for session_info in active_sessions:
                    session_id = session_info.session_id
                    print_info(f"Cleaning up session: {session_id}")
                    
                    resources = session_mgr.get_session_resources(session_id)
                    if resources:
                        resolver = ResourceResolver(profile=profile, region=region)
                        graph = DependencyGraph()
                        
                        for resource in resources:
                            hydrated = resolver.hydrate_resource(resource)
                            graph.add_resource(hydrated)
                        
                        plan = graph.generate_deletion_plan()
                        
                        results = execute_rollback_with_recovery(
                            session_id=session_id,
                            plan=plan,
                            hydrated_resources=[resolver.hydrate_resource(r) for r in resources],
                            region=region,
                            continue_on_failure=True
                        )
                        
                        if results['success']:
                            print_success(f"Session {session_id} resources cleaned up")
                        else:
                            print_warning(f"Session {session_id} had some cleanup issues")
                    
                    session_mgr.delete_session(session_id)
                    print_success(f"Session {session_id} deleted")
            else:
                print_info("No active sessions found")
            
            print_info("Step 2: Cleaning up infrastructure...")
            from .utils.infra import InfrastructureManager
            infra_mgr = InfrastructureManager(environment=environment, region=region, profile=profile)
            
            result = infra_mgr.destroy()
            if result['success']:
                print_success("Infrastructure destroyed successfully")
            else:
                print_error(f"Infrastructure destruction failed: {result.get('message', 'Unknown error')}")
            
            print_success("Comprehensive cleanup completed!")
            
        else:
            print_error(f"Unknown cleanup target: {what}")
            print_info("Available targets: sessions, infrastructure, all")
            raise typer.Exit(1)
            
    except Exception as e:
        if debug:
            raise
        print_error(f"Cleanup operation failed: {e}")
        raise typer.Exit(1)


def print_infrastructure_status(status: Dict[str, Any]):
    """Print infrastructure status with rich formatting"""
    print_header("Infrastructure Status")
    
    overall_status = "Healthy" if status.get('healthy', False) else "Unhealthy"
    console.print(Panel(f"Overall Status: {overall_status}", title="Status", border_style="blue"))
    
    table = Table(title="Infrastructure Resources", box=box.ROUNDED)
    table.add_column("Resource", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("ARN/ID", style="yellow")
    
    for resource in status.get('resources', []):
        status_icon = "●" if resource['status'] == 'active' else "○"
        table.add_row(
            resource['type'],
            f"{status_icon} {resource['status']}",
            resource.get('arn', resource.get('id', 'N/A'))
        )
    
    console.print(table)


def print_infrastructure_logs(logs: Dict[str, Any]):
    """Print infrastructure logs with rich formatting"""
    print_header("Infrastructure Logs")
    
    for log_group in logs.get('log_groups', []):
        console.print(Panel(f"Log Group: {log_group['name']}", title="Log Group", border_style="cyan"))
        
        if log_group.get('streams'):
            table = Table(title="Recent Log Streams", box=box.ROUNDED)
            table.add_column("Stream", style="cyan")
            table.add_column("Last Event", style="green")
            table.add_column("Size", style="yellow")
            
            for stream in log_group['streams']:
                last_event = stream.get('last_event_time')
                if last_event:
                    last_event = str(last_event)
                else:
                    last_event = 'N/A'
                
                table.add_row(
                    stream['name'],
                    last_event,
                    f"{stream.get('stored_bytes', 0)} bytes"
                )
            
            console.print(table)
        else:
            console.print("No log streams found")


def _parse_ttl(ttl_str: str) -> int:
    """Parse TTL string into seconds"""
    ttl_str = ttl_str.lower().strip()
    
    if ttl_str.endswith('s'):
        return int(ttl_str[:-1])
    elif ttl_str.endswith('m'):
        return int(ttl_str[:-1]) * 60
    elif ttl_str.endswith('h'):
        return int(ttl_str[:-1]) * 3600
    elif ttl_str.endswith('d'):
        return int(ttl_str[:-1]) * 86400
    else:
        return int(ttl_str) * 3600

if __name__ == "__main__":
    app() 