"""Agent workflow orchestrator for managing multi-agent workflows."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseAgent, AgentError
from .models import (
    QueryMessage, PlanMessage, TaskMessage, ResultMessage, ExecutionPlan,
    AgentWorkflowContext, TaskResult, SubTask
)
from .registry import agent_registry
from .planner import PlannerAgent
from .reporter import ReporterAgent
from ..core.config import Settings


logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates workflows across multiple agents."""
    
    def __init__(self, settings: Settings, verbose: bool = False):
        self.settings = settings
        self.logger = logging.getLogger("agent_orchestrator")
        self.active_workflows: Dict[str, AgentWorkflowContext] = {}
        self.verbose = verbose
        
        # Configuration
        self.max_concurrent_agents = settings.agents.max_concurrent_agents
        self.workflow_timeout = settings.agents.workflow_timeout
        self.default_timeout = settings.agents.default_timeout
    
    def _verbose_print(self, message: str, style: str = "dim"):
        """Print verbose messages if verbose mode is enabled."""
        if self.verbose:
            from rich.console import Console
            console = Console()
            console.print(f"[{style}]{message}[/{style}]")
    
    async def execute_query(self, 
                           query: str, 
                           context: Dict[str, Any] = None,
                           preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a query using the agent workflow system."""
        context = context or {}
        preferences = preferences or {}
        
        # Create workflow context
        workflow_context = AgentWorkflowContext(
            original_query=query,
            settings=self.settings.model_dump()
        )
        
        self.active_workflows[workflow_context.workflow_id] = workflow_context
        
        try:
            # Step 1: Get planner agent
            self._verbose_print("🤔 Step 1: Looking for planner agent...")
            planner = agent_registry.get_agents_by_type("planner")
            if not planner:
                raise AgentError("No planner agent available")
            
            planner_agent = planner[0]
            self._verbose_print(f"✓ Found planner agent: {planner_agent.name}")
            
            # Step 2: Create execution plan
            self._verbose_print(f"📋 Step 2: Creating execution plan for query: {query[:100]}...")
            self.logger.info(f"Creating execution plan for query: {query[:100]}...")
            plan = await planner_agent.plan_query_execution(query, context)
            workflow_context.current_plan = plan
            
            self._verbose_print(f"✓ Created plan with {len(plan.tasks)} tasks:")
            
            # Show detailed plan information
            self._verbose_print(f"📊 Plan Details:")
            self._verbose_print(f"  • Estimated duration: {plan.estimated_duration}s")
            self._verbose_print(f"  • Resource requirements: {plan.resource_requirements}")
            if plan.parallel_groups:
                self._verbose_print(f"  • Parallel groups: {len(plan.parallel_groups)}")
            
            self._verbose_print(f"📋 Task Breakdown:")
            for i, task in enumerate(plan.tasks, 1):
                self._verbose_print(f"  {i}. [{task.agent_type}] {task.action}")
                self._verbose_print(f"     Task ID: {task.id[:8]}...")
                self._verbose_print(f"     Priority: {task.priority}")
                if task.dependencies:
                    dep_names = [dep_id[:8] + "..." for dep_id in task.dependencies]
                    self._verbose_print(f"     Dependencies: {dep_names}")
                if task.parameters:
                    # Show first few parameters
                    param_preview = {}
                    for k, v in list(task.parameters.items())[:3]:
                        if isinstance(v, str) and len(v) > 50:
                            param_preview[k] = v[:50] + "..."
                        else:
                            param_preview[k] = v
                    self._verbose_print(f"     Parameters: {param_preview}")
                if task.timeout:
                    self._verbose_print(f"     Timeout: {task.timeout}s")
            
            self.logger.info(f"Created plan with {len(plan.tasks)} tasks")
            
            # Step 3: Execute plan
            self._verbose_print("🚀 Step 3: Executing plan...")
            results = await self._execute_plan(plan, workflow_context)
            
            # Step 4: Return final result
            return {
                "workflow_id": workflow_context.workflow_id,
                "query": query,
                "status": "completed",
                "results": results,
                "execution_summary": {
                    "total_tasks": len(plan.tasks),
                    "completed_tasks": len(workflow_context.completed_tasks),
                    "failed_tasks": len(workflow_context.failed_tasks),
                    "duration": (datetime.now() - workflow_context.start_time).total_seconds()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "workflow_id": workflow_context.workflow_id,
                "query": query,
                "status": "failed",
                "error": str(e),
                "partial_results": self._get_partial_results(workflow_context)
            }
        
        finally:
            # Clean up
            if workflow_context.workflow_id in self.active_workflows:
                del self.active_workflows[workflow_context.workflow_id]
    
    async def _execute_plan(self, 
                           plan: ExecutionPlan, 
                           context: AgentWorkflowContext) -> Dict[str, Any]:
        """Execute an execution plan."""
        
        # Build dependency graph
        task_dependencies = self._build_dependency_graph(plan.tasks)
        
        # Track task completion
        completed_tasks = set()
        running_tasks = {}
        
        while len(completed_tasks) < len(plan.tasks):
            # Find tasks that can be executed (dependencies met)
            ready_tasks = []
            for task in plan.tasks:
                if (task.id not in completed_tasks and 
                    task.id not in running_tasks and
                    all(dep_id in completed_tasks for dep_id in task.dependencies)):
                    ready_tasks.append(task)
            
            if ready_tasks:
                self._verbose_print(f"⏳ Ready to execute {len(ready_tasks)} task(s)")
                for task in ready_tasks:
                    self._verbose_print(f"  - {task.agent_type}: {task.action}")
            
            self._verbose_print(f"📊 Status: {len(completed_tasks)}/{len(plan.tasks)} completed, {len(running_tasks)} running")
            
            if not ready_tasks and not running_tasks:
                # No more tasks can be executed and none are running
                self._verbose_print("⚠️ Workflow stalled - no executable tasks remaining", "yellow")
                self.logger.warning("Workflow stalled - no executable tasks remaining")
                break
            
            # Start ready tasks (respecting concurrency limits)
            while (ready_tasks and 
                   len(running_tasks) < self.max_concurrent_agents):
                task = ready_tasks.pop(0)
                
                # Find agent for this task
                self._verbose_print(f"🔍 Looking for agent: {task.agent_type} -> {task.action}")
                agent = agent_registry.find_best_agent_for_task(
                    task.action, 
                    task.parameters,
                    task.agent_type
                )
                
                if not agent:
                    self._verbose_print(f"❌ No agent available for task {task.id} (type: {task.agent_type})", "red")
                    self.logger.error(f"No agent available for task {task.id} (type: {task.agent_type})")
                    # Mark as failed
                    failed_result = TaskResult(
                        task_id=task.id,
                        status="failed",
                        error=f"No agent available for type {task.agent_type}"
                    )
                    context.failed_tasks.append(failed_result)
                    completed_tasks.add(task.id)
                    continue
                
                self._verbose_print(f"✓ Found agent: {agent.name}")
                
                # Create task message
                task_message = TaskMessage(
                    sender="orchestrator",
                    recipient=agent.name,
                    task=task,
                    context=context.shared_data,
                    shared_state=context.shared_data
                )
                
                # Start task execution
                self._verbose_print(f"🚀 Starting task {task.id[:8]}... on agent {agent.name}")
                self.logger.info(f"Starting task {task.id} on agent {agent.name}")
                task_future = asyncio.create_task(
                    self._execute_task_with_timeout(agent, task_message, context, self.verbose)
                )
                running_tasks[task.id] = task_future
            
            # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Process completed tasks
                for future in done:
                    task_id = None
                    for tid, fut in running_tasks.items():
                        if fut == future:
                            task_id = tid
                            break
                    
                    if task_id:
                        try:
                            result_message = await future
                            task_result = result_message.result
                            
                            if task_result.status == "success":
                                context.completed_tasks.append(task_result)
                                exec_time = task_result.execution_time or 0
                                self._verbose_print(f"✅ Task {task_id[:8]}... completed successfully ({exec_time:.1f}s)", "green")
                                self.logger.info(f"Task {task_id} completed successfully")
                                
                                # Update shared data with task results
                                if task_result.data:
                                    context.shared_data[f"task_{task_id}_result"] = task_result.data
                                    data_summary = str(task_result.data)[:100] + "..." if len(str(task_result.data)) > 100 else str(task_result.data)
                                    self._verbose_print(f"  📊 Result data: {data_summary}")
                            else:
                                context.failed_tasks.append(task_result)
                                self._verbose_print(f"❌ Task {task_id[:8]}... failed: {task_result.error}", "red")
                                self.logger.error(f"Task {task_id} failed: {task_result.error}")
                            
                        except Exception as e:
                            # Create error result
                            error_result = TaskResult(
                                task_id=task_id,
                                status="failed",
                                error=str(e)
                            )
                            context.failed_tasks.append(error_result)
                            self._verbose_print(f"💥 Task {task_id[:8]}... execution error: {str(e)}", "red")
                            self.logger.error(f"Task {task_id} execution error: {str(e)}")
                        
                        completed_tasks.add(task_id)
                        del running_tasks[task_id]
        
        # Get final results from reporter agent if available
        self._verbose_print("📝 Step 4: Synthesizing results...")
        reporter_agents = agent_registry.get_agents_by_type("reporter")
        if reporter_agents and context.completed_tasks:
            reporter = reporter_agents[0]
            self._verbose_print(f"✓ Found reporter agent: {reporter.name}")
            
            # Create synthesis task
            synthesis_task = SubTask(
                agent_type="reporter",
                action="synthesize_results",
                parameters={
                    "original_query": context.original_query,
                    "format": "markdown"
                }
            )
            
            synthesis_message = TaskMessage(
                sender="orchestrator",
                recipient=reporter.name,
                task=synthesis_task,
                context=context.shared_data
            )
            
            try:
                self._verbose_print("🔄 Running result synthesis...")
                synthesis_result = await self._execute_task_with_timeout(
                    reporter, synthesis_message, context, self.verbose
                )
                
                if synthesis_result.result.status == "success":
                    self._verbose_print("✅ Result synthesis completed successfully", "green")
                    return synthesis_result.result.data
                else:
                    self._verbose_print(f"❌ Result synthesis failed: {synthesis_result.result.error}", "red")
                
            except Exception as e:
                self._verbose_print(f"💥 Result synthesis error: {str(e)}", "red")
                self.logger.error(f"Result synthesis failed: {str(e)}")
        else:
            if not reporter_agents:
                self._verbose_print("⚠️ No reporter agent available for synthesis", "yellow")
            if not context.completed_tasks:
                self._verbose_print("⚠️ No completed tasks to synthesize", "yellow")
        
        # Fallback: return raw results
        self._verbose_print("📦 Returning raw results (no synthesis)")
        return {
            "completed_tasks": [task.model_dump() for task in context.completed_tasks],
            "failed_tasks": [task.model_dump() for task in context.failed_tasks],
            "message": "Workflow completed without synthesis"
        }
    
    def _build_dependency_graph(self, tasks: List[SubTask]) -> Dict[str, List[str]]:
        """Build a dependency graph from tasks."""
        graph = {}
        for task in tasks:
            graph[task.id] = task.dependencies.copy()
        return graph
    
    async def _execute_task_with_timeout(self, 
                                        agent: BaseAgent, 
                                        task_message: TaskMessage, 
                                        context: AgentWorkflowContext,
                                        verbose: bool = False) -> ResultMessage:
        """Execute a task with timeout."""
        timeout = task_message.task.timeout or self.default_timeout
        
        try:
            return await asyncio.wait_for(
                agent.execute_task(task_message, context, verbose),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            raise AgentError(f"Task {task_message.task.id} timed out after {timeout} seconds")
    
    def _get_partial_results(self, context: AgentWorkflowContext) -> Dict[str, Any]:
        """Get partial results from a failed workflow."""
        return {
            "completed_tasks": [task.model_dump() for task in context.completed_tasks],
            "failed_tasks": [task.model_dump() for task in context.failed_tasks],
            "shared_data": context.shared_data
        }
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active workflow."""
        if workflow_id not in self.active_workflows:
            return None
        
        context = self.active_workflows[workflow_id]
        total_tasks = len(context.current_plan.tasks) if context.current_plan else 0
        completed = len(context.completed_tasks)
        failed = len(context.failed_tasks)
        
        return {
            "workflow_id": workflow_id,
            "query": context.original_query,
            "status": "running",
            "progress": {
                "total_tasks": total_tasks,
                "completed_tasks": completed,
                "failed_tasks": failed,
                "progress_percentage": (completed + failed) / max(total_tasks, 1) * 100
            },
            "duration": (datetime.now() - context.start_time).total_seconds()
        }
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow."""
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]
            self.logger.info(f"Cancelled workflow {workflow_id}")
            return True
        return False
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        workflows = []
        for workflow_id, context in self.active_workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "query": context.original_query,
                "start_time": context.start_time.isoformat(),
                "duration": (datetime.now() - context.start_time).total_seconds()
            })
        return workflows