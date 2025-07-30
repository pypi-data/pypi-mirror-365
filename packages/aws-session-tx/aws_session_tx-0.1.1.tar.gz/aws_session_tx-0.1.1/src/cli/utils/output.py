"""
CLI output utilities for AWS Session TX

Provides rich formatting, colors, progress indicators, and structured output.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

from ..models import Session, Resource, DeletionPlan, DeletionStep, SessionStatus, ResourceType

console = Console()


def print_success(message: str):
    """Print a success message"""
    console.print(f"[SUCCESS] {message}", style="bold green")


def print_error(message: str):
    """Print an error message"""
    console.print(f"[ERROR] {message}", style="bold red")


def print_warning(message: str):
    """Print a warning message"""
    console.print(f"[WARNING] {message}", style="bold yellow")


def print_info(message: str):
    """Print an info message"""
    console.print(f"[INFO] {message}", style="bold blue")


def print_header(title: str):
    """Print a section header"""
    console.print(f"\n[bold cyan]{'='*60}[/bold cyan]")
    console.print(f"[bold cyan]{title.center(60)}[/bold cyan]")
    console.print(f"[bold cyan]{'='*60}[/bold cyan]\n")


def format_session_table(sessions: List[Session]) -> Table:
    table = Table(title="Active Sessions", box=box.ROUNDED)
    
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Region", style="green")
    table.add_column("Started", style="yellow")
    table.add_column("TTL", style="blue")
    table.add_column("Resources", style="white")
    
    for session in sessions:
        status_color = {
            SessionStatus.ACTIVE: "green",
            SessionStatus.COMMITTED: "blue", 
            SessionStatus.ROLLED_BACK: "red"
        }.get(session.status, "white")
        
        table.add_row(
            session.session_id,
            f"[{status_color}]{session.status.value}[/{status_color}]",
            session.region,
            session.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            f"{session.ttl}s",
            str(session.resource_count or 0)
        )
    
    return table


def format_resources_table(resources: List[Resource]) -> Table:
    table = Table(title="Session Resources", box=box.ROUNDED)
    
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("ID", style="green", no_wrap=True)
    table.add_column("Region", style="yellow")
    table.add_column("Created", style="blue")
    table.add_column("ARN", style="white", no_wrap=True)
    
    for resource in resources:
        table.add_row(
            resource.type.value,
            resource.id,
            resource.region,
            resource.created_at.strftime("%Y-%m-%d %H:%M:%S") if resource.created_at else "N/A",
            resource.arn
        )
    
    return table


def format_deletion_plan(plan: DeletionPlan) -> Table:
    table = Table(title="Deletion Plan", box=box.ROUNDED)
    
    table.add_column("Step", style="cyan", justify="right")
    table.add_column("Type", style="magenta")
    table.add_column("Resource ID", style="green", no_wrap=True)
    table.add_column("Estimated Time", style="yellow")
    table.add_column("Dependencies", style="blue")
    
    for i, step in enumerate(plan.steps, 1):
        dependencies = ", ".join(step.dependencies) if step.dependencies else "None"
        table.add_row(
            str(i),
            step.resource_type.value,
            step.resource_id,
            f"{step.estimated_time}s",
            dependencies
        )
    
    return table


def format_rollback_progress(progress: Dict[str, Any]) -> Panel:
    """Create a rich panel for rollback progress"""
    total = progress['total_steps']
    completed = progress['completed']
    failed = progress['failed']
    skipped = progress.get('skipped', 0)
    remaining = progress['remaining']
    percent = progress['progress_percent']
    
    progress_text = f"[green]{'█' * int(percent/5)}[/green][white]{'░' * (20 - int(percent/5))}[/white] {percent:.1f}%"
    
    content = f"""
[bold]Rollback Progress[/bold]

{progress_text}

[bold]Status:[/bold]
• Total Steps: {total}
• Completed: [green]{completed}[/green]
• Failed: [red]{failed}[/red]
• Skipped: [yellow]{skipped}[/yellow]
• Remaining: [yellow]{remaining}[/yellow]

[bold]Timing:[/bold]
• Started: {progress['start_time']}
• Last Update: {progress['last_update']}
"""
    
    return Panel(content, title="Rollback Status", border_style="blue")


def format_error_summary(failed_steps: List[Dict[str, Any]]) -> Panel:
    """Create a rich panel for error summary"""
    if not failed_steps:
        return Panel("No errors occurred", title="Error Summary", border_style="green")
    
    content = f"[bold red]Failed Steps ({len(failed_steps)}):[/bold red]\n\n"
    
    for step in failed_steps:
        content += f"[bold]{step['resource_id']}[/bold] ({step['resource_type']})\n"
        content += f"Error: {step['error']}\n"
        content += f"Time: {step['timestamp']}\n\n"
    
    return Panel(content, title="Error Summary", border_style="red")


def print_json_output(data: Dict[str, Any]):
    """Print data as formatted JSON"""
    console.print(json.dumps(data, indent=2, default=str))


def print_session_status(session: Session, resources: List[Resource], json_output: bool = False):
    if json_output:
        data = {
            'session': session.model_dump(),
            'resources': [r.model_dump() for r in resources],
            'resource_count': len(resources)
        }
        print_json_output(data)
        return
    
    print_header("Session Status")
    
    session_info = f"""
[bold]Session ID:[/bold] {session.session_id}
[bold]Status:[/bold] {session.status.value}
[bold]Region:[/bold] {session.region}
[bold]Started:[/bold] {session.started_at.strftime("%Y-%m-%d %H:%M:%S")}
[bold]TTL:[/bold] {session.ttl} seconds
[bold]Resources Tracked:[/bold] {len(resources)}
"""
    
    console.print(Panel(session_info, title="Session Information", border_style="cyan"))
    
    if resources:
        console.print(format_resources_table(resources))
    else:
        console.print(Panel("No resources tracked in this session", border_style="yellow"))


def print_deletion_plan(plan: DeletionPlan, json_output: bool = False):
    if json_output:
        print_json_output(plan.model_dump())
        return
    
    print_header("Deletion Plan")
    
    summary = f"""
[bold]Plan Summary:[/bold]
• Total Steps: {len(plan.steps)}
• Estimated Time: {plan.estimated_time} seconds
• Resources to Delete: {len(plan.steps)}
"""
    
    console.print(Panel(summary, title="Plan Summary", border_style="blue"))
    
    console.print(format_deletion_plan(plan))


def print_rollback_results(results: Dict[str, Any], json_output: bool = False):
    if json_output:
        print_json_output(results)
        return
    
    print_header("Rollback Results")
    
    if results['success']:
        console.print(Panel("Rollback Completed Successfully!", border_style="green"))
    else:
        console.print(Panel("Rollback Completed with Errors", border_style="red"))
    
    progress_panel = format_rollback_progress({
        'total_steps': results['total'],
        'completed': results['completed'],
        'failed': results['failed'],
        'skipped': results.get('skipped', 0),
        'remaining': results['total'] - results['completed'] - results['failed'] - results.get('skipped', 0),
        'progress_percent': results['progress']['progress_percent'],
        'start_time': results['progress']['start_time'],
        'last_update': results['progress']['last_update']
    })
    console.print(progress_panel)
    
    if results['failed'] > 0:
        error_panel = format_error_summary(results.get('failed_steps', []))
        console.print(error_panel)
    
    if results.get('can_resume', False):
        console.print(Panel(
            "Use --resume flag to continue from where it left off",
            border_style="yellow"
        ))


def create_progress_tracker(total_steps: int, description: str = "Processing"):
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    )
    
    task = progress.add_task(description, total=total_steps)
    return progress, task


def print_resource_type_summary(resources: List[Resource]):
    type_counts = {}
    for resource in resources:
        type_counts[resource.type] = type_counts.get(resource.type, 0) + 1
    
    table = Table(title="Resource Type Summary", box=box.ROUNDED)
    table.add_column("Type", style="cyan")
    table.add_column("Count", style="green", justify="right")
    
    for resource_type, count in sorted(type_counts.items()):
        table.add_row(resource_type.value, str(count))
    
    console.print(table) 