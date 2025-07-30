"""
Rollback recovery utilities for AWS Session TX

Handles partial rollback failures and provides recovery mechanisms.
"""

import json
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path

from ..models import DeletionPlan, DeletionStep, HydratedResource
from ..planner.drivers import get_driver
from .retry import retry_aws_operation


class RollbackState:
    """Tracks the state of a rollback operation"""
    
    def __init__(self, session_id: str, plan: DeletionPlan):
        self.session_id = session_id
        self.plan = plan
        self.completed_steps: List[str] = []
        self.failed_steps: List[Dict[str, Any]] = []
        self.skipped_steps: List[str] = []
        self.current_step_index = 0
        self.start_time = datetime.now()
        self.last_update = datetime.now()
    
    def mark_step_completed(self, step: DeletionStep):
        """Mark a step as completed"""
        self.completed_steps.append(step.resource_id)
        self.current_step_index += 1
        self.last_update = datetime.now()
    
    def mark_step_failed(self, step: DeletionStep, error: Exception):
        """Mark a step as failed"""
        self.failed_steps.append({
            'resource_id': step.resource_id,
            'resource_type': step.resource_type,
            'error': str(error),
            'error_type': type(error).__name__,
            'timestamp': datetime.now().isoformat()
        })
        self.current_step_index += 1
        self.last_update = datetime.now()
    
    def mark_step_skipped(self, step: DeletionStep, reason: str):
        """Mark a step as skipped"""
        self.skipped_steps.append({
            'resource_id': step.resource_id,
            'resource_type': step.resource_type,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        self.current_step_index += 1
        self.last_update = datetime.now()
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information"""
        total_steps = len(self.plan.steps)
        completed_count = len(self.completed_steps)
        failed_count = len(self.failed_steps)
        skipped_count = len(self.skipped_steps)
        remaining_count = total_steps - completed_count - failed_count - skipped_count
        
        return {
            'total_steps': total_steps,
            'completed': completed_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'remaining': remaining_count,
            'progress_percent': ((completed_count + skipped_count) / total_steps * 100) if total_steps > 0 else 0,
            'start_time': self.start_time.isoformat(),
            'last_update': self.last_update.isoformat()
        }
    
    def can_resume(self) -> bool:
        """Check if rollback can be resumed"""
        return self.current_step_index < len(self.plan.steps)
    
    def get_remaining_steps(self) -> List[DeletionStep]:
        """Get remaining steps to execute"""
        return self.plan.steps[self.current_step_index:]


class RollbackRecovery:
    """Handles rollback recovery and state persistence"""
    
    def __init__(self, session_id: str, state_dir: Optional[str] = None):
        self.session_id = session_id
        self.state_dir = Path(state_dir) if state_dir else Path.home() / '.aws-session-tx' / 'rollback-state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / f'{session_id}-rollback.json'
    
    def save_state(self, state: RollbackState):
        """Save rollback state to disk"""
        state_data = {
            'session_id': state.session_id,
            'plan': state.plan.model_dump(),
            'completed_steps': state.completed_steps,
            'failed_steps': state.failed_steps,
            'skipped_steps': state.skipped_steps,
            'current_step_index': state.current_step_index,
            'start_time': state.start_time.isoformat(),
            'last_update': state.last_update.isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state_data, f, indent=2)
    
    def load_state(self) -> Optional[RollbackState]:
        """Load rollback state from disk"""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                state_data = json.load(f)
            
            plan = DeletionPlan(**state_data['plan'])
            state = RollbackState(state_data['session_id'], plan)
            state.completed_steps = state_data['completed_steps']
            state.failed_steps = state_data['failed_steps']
            state.skipped_steps = state_data.get('skipped_steps', [])
            state.current_step_index = state_data['current_step_index']
            state.start_time = datetime.fromisoformat(state_data['start_time'])
            state.last_update = datetime.fromisoformat(state_data['last_update'])
            
            return state
        except Exception as e:
            print(f"Warning: Failed to load rollback state: {e}")
            return None
    
    def clear_state(self):
        """Clear rollback state"""
        if self.state_file.exists():
            self.state_file.unlink()
    
    def has_incomplete_rollback(self) -> bool:
        """Check if there's an incomplete rollback"""
        return self.state_file.exists()


def is_critical_error(error: Exception) -> bool:
    """Determine if an error is critical and should stop the rollback"""
    if hasattr(error, 'response') and hasattr(error.response, 'get'):
        error_code = error.response.get('Error', {}).get('Code', '')
        
        non_critical_errors = [
            'AccessDenied',
            'NoSuchBucket',
            'NoSuchSecurityGroup',
            'NoSuchLogGroup',
            'ResourceNotFoundException',
            'InvalidGroup.NotFound',
        ]
        
        return error_code not in non_critical_errors
    
    return True


@retry_aws_operation("Resource Deletion", max_attempts=3, base_delay=2.0)
def execute_deletion_step(step: DeletionStep, hydrated_resource: HydratedResource, region: str) -> bool:
    """Execute a single deletion step with retry logic"""
    driver_class = get_driver(step.resource_type)
    if not driver_class:
        raise ValueError(f"No driver found for resource type: {step.resource_type}")
    
    driver = driver_class(region=region)
    
    if hasattr(driver, 'is_gone') and driver.is_gone(hydrated_resource):
        print(f"[INFO] Resource {step.resource_id} already deleted, skipping")
        return True
    
    return driver.delete(hydrated_resource)


def execute_rollback_with_recovery(
    session_id: str,
    plan: DeletionPlan,
    hydrated_resources: List[HydratedResource],
    region: str,
    resume: bool = False,
    continue_on_failure: bool = False,
    force: bool = False
) -> Dict[str, Any]:
    """
    Execute rollback with recovery capabilities
    
    Args:
        session_id: Session ID
        plan: Deletion plan to execute
        hydrated_resources: List of hydrated resources
        region: AWS region
        resume: Whether to resume from previous state
        continue_on_failure: Whether to continue on individual step failures
        force: Whether to force deletion (skip verification)
    
    Returns:
        Dictionary with execution results
    """
    recovery = RollbackRecovery(session_id)
    
    if resume:
        state = recovery.load_state()
        if not state:
            raise ValueError(f"No rollback state found for session {session_id}")
        print(f"[INFO] Resuming rollback for session {session_id}")
    else:
        state = RollbackState(session_id, plan)
        print(f"[INFO] Starting rollback for session {session_id}")
    
    remaining_steps = state.get_remaining_steps()
    if not remaining_steps:
        print("[SUCCESS] No remaining steps to execute")
        return {
            'success': True,
            'completed': len(state.completed_steps),
            'failed': len(state.failed_steps),
            'skipped': len(state.skipped_steps),
            'message': 'Rollback already completed'
        }
    
    print(f"[INFO] Executing {len(remaining_steps)} remaining steps...")
    
    for step in remaining_steps:
        try:
            print(f"[INFO] Deleting {step.resource_type}: {step.resource_id}")
            
            hydrated = next(
                (h for h in hydrated_resources if h.resource.id == step.resource_id),
                None
            )
            
            if not hydrated:
                print(f"[WARNING] No hydrated resource found for {step.resource_id}, skipping")
                state.mark_step_skipped(step, "No hydrated resource found")
                continue
            
            success = execute_deletion_step(step, hydrated, region)
            
            if success:
                state.mark_step_completed(step)
                print(f"[SUCCESS] Successfully deleted {step.resource_id}")
            else:
                raise Exception(f"Deletion returned False for {step.resource_id}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"[ERROR] Failed to delete {step.resource_id}: {error_msg}")
            
            if not is_critical_error(e):
                print(f"[INFO] Non-critical error for {step.resource_id}, marking as skipped")
                state.mark_step_skipped(step, f"Non-critical error: {error_msg}")
            else:
                state.mark_step_failed(step, e)
                
                should_stop = not continue_on_failure and is_critical_error(e)
                
                if should_stop:
                    print("[ERROR] Stopping rollback due to critical failure")
                    break
                else:
                    print("[WARNING] Continuing despite failure...")
        
        recovery.save_state(state)
        time.sleep(1)
    
    progress = state.get_progress()
    result = {
        'success': len(state.failed_steps) == 0,
        'completed': len(state.completed_steps),
        'failed': len(state.failed_steps),
        'skipped': len(state.skipped_steps),
        'total': progress['total_steps'],
        'progress': progress,
        'message': 'Rollback completed successfully' if len(state.failed_steps) == 0 else 'Rollback completed with errors'
    }
    
    if not state.can_resume():
        recovery.clear_state()
        print("[INFO] Rollback state cleared")
    
    return result


def get_rollback_status(session_id: str) -> Optional[Dict[str, Any]]:
    """Get the status of an incomplete rollback"""
    recovery = RollbackRecovery(session_id)
    
    if not recovery.has_incomplete_rollback():
        return None
    
    state = recovery.load_state()
    if not state:
        return None
    
    progress = state.get_progress()
    
    return {
        'has_incomplete_rollback': True,
        'session_id': session_id,
        'progress': progress,
        'can_resume': state.can_resume(),
        'remaining_steps': len(state.get_remaining_steps())
    } 