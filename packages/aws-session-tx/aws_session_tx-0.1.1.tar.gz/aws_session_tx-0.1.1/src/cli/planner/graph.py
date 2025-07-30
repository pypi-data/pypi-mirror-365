"""
Dependency graph and deletion planning for AWS Session TX
"""

from typing import Dict, List, Set, Optional
from collections import defaultdict, deque
from ..models import HydratedResource, DeletionPlan, DeletionStep, ResourceType
from ..utils.output import print_warning


class DependencyGraph:
    """Manages resource dependencies and generates deletion plans"""
    
    def __init__(self):
        self.resources: Dict[str, HydratedResource] = {}
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_deps: Dict[str, Set[str]] = defaultdict(set)
    
    def add_resource(self, resource: HydratedResource):
        """Add a resource to the graph"""
        self.resources[resource.resource.arn] = resource
        
        for dep_arn in resource.dependencies:
            if dep_arn in self.resources:
                self.dependencies[resource.resource.arn].add(dep_arn)
                self.reverse_deps[dep_arn].add(resource.resource.arn)
    
    def get_dependencies(self, resource_arn: str) -> Set[str]:
        """Get direct dependencies of a resource"""
        return self.dependencies.get(resource_arn, set())
    
    def get_dependents(self, resource_arn: str) -> Set[str]:
        """Get resources that depend on this resource"""
        return self.reverse_deps.get(resource_arn, set())
    
    def has_cycle(self) -> bool:
        """Check if the graph has cycles using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.resources:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    def topological_sort(self) -> List[str]:
        """Perform topological sort using Kahn's algorithm for deletion order"""
        in_degree = defaultdict(int)
        for resource_arn in self.resources:
            in_degree[resource_arn] = len(self.get_dependents(resource_arn))
        
        queue = deque([arn for arn, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for dependency in self.get_dependencies(current):
                in_degree[dependency] -= 1
                if in_degree[dependency] == 0:
                    queue.append(dependency)
        
        if len(result) != len(self.resources):
            raise ValueError("Graph has cycles, cannot perform topological sort")
        
        return result
    
    def generate_deletion_plan(self) -> DeletionPlan:
        """Generate a deletion plan with proper ordering"""
        if not self.resources:
            return DeletionPlan(session_id="", steps=[], warnings=[], estimated_time=0)
        
        has_cycle = self.has_cycle()
        
        if has_cycle:
            deletion_order = self._break_cycles_and_sort()
        else:
            try:
                deletion_order = self.topological_sort()
            except ValueError as e:
                return DeletionPlan(
                    session_id="",
                    steps=[],
                    warnings=[str(e)],
                    estimated_time=0
                )
        
        steps = []
        warnings = []
        
        for resource_arn in deletion_order:
            resource = self.resources[resource_arn]
            
            if not resource.safe_to_delete:
                warnings.append(
                    f"Resource {resource.resource.type}:{resource.resource.id} "
                    f"may not be safe to delete: {resource.deletion_reason}"
                )
            step = DeletionStep(
                resource_type=resource.resource.type,
                resource_id=resource.resource.id,
                resource_arn=resource.resource.arn,
                safe=resource.safe_to_delete,
                dependencies=list(resource.dependencies),
                reason=resource.deletion_reason,
                estimated_time=self._estimate_deletion_time(resource.resource.type)
            )
            
            steps.append(step)
        
        total_time = sum(step.estimated_time for step in steps)
        
        return DeletionPlan(
            session_id="",
            steps=steps,
            warnings=warnings,
            estimated_time=total_time
        )
    
    def _estimate_deletion_time(self, resource_type: ResourceType) -> int:
        """Estimate deletion time for a resource type in seconds"""
        time_estimates = {
            ResourceType.EC2_INSTANCE: 60,
            ResourceType.EC2_SECURITY_GROUP: 30,
            ResourceType.EC2_VOLUME: 30,
            ResourceType.S3_BUCKET: 120,
            ResourceType.ALB_LOAD_BALANCER: 90,
            ResourceType.ALB_TARGET_GROUP: 30,
            ResourceType.ALB_LISTENER: 30,
            ResourceType.CLOUDWATCH_LOG_GROUP: 15,
        }
        
        return time_estimates.get(resource_type, 30)
    
    def get_resource_by_arn(self, arn: str) -> Optional[HydratedResource]:
        """Get a resource by its ARN"""
        return self.resources.get(arn)
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[HydratedResource]:
        """Get all resources of a specific type"""
        return [
            resource for resource in self.resources.values()
            if resource.resource.type == resource_type
        ]
    
    def _break_cycles_and_sort(self) -> List[str]:
        """Break cycles by prioritizing resource types and return deletion order"""
        priority_order = {
            ResourceType.EC2_INSTANCE: 1,
            ResourceType.EC2_VOLUME: 2,
            ResourceType.ALB_LISTENER: 3,
            ResourceType.ALB_TARGET_GROUP: 4,
            ResourceType.ALB_LOAD_BALANCER: 5,
            ResourceType.EC2_SECURITY_GROUP: 6,
            ResourceType.S3_BUCKET: 7,
            ResourceType.CLOUDWATCH_LOG_GROUP: 8,
        }
        sorted_resources = sorted(
            self.resources.keys(),
            key=lambda arn: priority_order.get(self.resources[arn].resource.type, 999)
        )
        
        return sorted_resources
    
    def validate_dependencies(self) -> List[str]:
        """Validate that all dependencies exist in the graph"""
        missing_deps = []
        
        for resource_arn, deps in self.dependencies.items():
            for dep_arn in deps:
                if dep_arn not in self.resources:
                    missing_deps.append(f"Resource {resource_arn} depends on {dep_arn} which is not in the graph")
        
        return missing_deps 