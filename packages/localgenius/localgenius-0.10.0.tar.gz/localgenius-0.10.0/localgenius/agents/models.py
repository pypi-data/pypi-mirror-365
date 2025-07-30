"""Pydantic models for inter-agent communication."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class MessageType(str, Enum):
    """Types of messages exchanged between agents."""
    QUERY = "query"
    PLAN = "plan"
    TASK = "task"
    RESULT = "result"
    ERROR = "error"
    STATUS = "status"


class AgentMessage(BaseModel):
    """Base message class for all inter-agent communication."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    sender: str
    recipient: Optional[str] = None
    correlation_id: Optional[str] = None  # Links related messages
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryMessage(AgentMessage):
    """Initial query message from user to planner agent."""
    type: MessageType = MessageType.QUERY
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class SubTask(BaseModel):
    """Individual sub-task within an execution plan."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_type: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)  # IDs of prerequisite tasks
    priority: int = 1  # Higher number = higher priority
    timeout: Optional[int] = None  # Timeout in seconds
    retry_count: int = 0


class ExecutionPlan(BaseModel):
    """Complete execution plan created by planner agent."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query_id: str
    tasks: List[SubTask]
    estimated_duration: Optional[int] = None
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    parallel_groups: List[List[str]] = Field(default_factory=list)  # Task IDs that can run in parallel


class PlanMessage(AgentMessage):
    """Message containing execution plan from planner to orchestrator."""
    type: MessageType = MessageType.PLAN
    plan: ExecutionPlan


class TaskMessage(AgentMessage):
    """Message assigning a specific task to an executor agent."""
    type: MessageType = MessageType.TASK
    task: SubTask
    context: Dict[str, Any] = Field(default_factory=dict)
    shared_state: Dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Result from executing a single task."""
    task_id: str
    status: str  # "success", "failed", "partial"
    data: Any = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
    error: Optional[str] = None


class ResultMessage(AgentMessage):
    """Message containing task execution result."""
    type: MessageType = MessageType.RESULT
    result: TaskResult


class ErrorMessage(AgentMessage):
    """Message indicating an error occurred."""
    type: MessageType = MessageType.ERROR
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    recoverable: bool = True


class StatusMessage(AgentMessage):
    """Status update message for workflow tracking."""
    type: MessageType = MessageType.STATUS
    status: str  # "started", "in_progress", "completed", "failed"
    progress: Optional[float] = None  # 0.0 to 1.0
    message: Optional[str] = None


class AgentWorkflowContext(BaseModel):
    """Shared context maintained throughout agent workflow."""
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_query: str
    current_plan: Optional[ExecutionPlan] = None
    completed_tasks: List[TaskResult] = Field(default_factory=list)
    failed_tasks: List[TaskResult] = Field(default_factory=list)
    shared_data: Dict[str, Any] = Field(default_factory=dict)
    start_time: datetime = Field(default_factory=datetime.now)
    settings: Dict[str, Any] = Field(default_factory=dict)


class AgentCapability(BaseModel):
    """Describes what an agent can do."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    estimated_duration: Optional[int] = None


class AgentInfo(BaseModel):
    """Information about a registered agent."""
    name: str
    type: str
    description: str
    capabilities: List[AgentCapability]
    version: str = "1.0.0"
    status: str = "available"  # "available", "busy", "offline"
    metadata: Dict[str, Any] = Field(default_factory=dict)