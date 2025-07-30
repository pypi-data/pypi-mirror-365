"""Base agent class and common functionality."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import traceback

from openai import AsyncOpenAI

from .models import (
    AgentMessage, TaskMessage, ResultMessage, ErrorMessage, StatusMessage,
    TaskResult, AgentCapability, AgentInfo, AgentWorkflowContext
)
from ..core.config import Settings


logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent-related errors."""
    def __init__(self, message: str, agent_name: str = None, recoverable: bool = True):
        self.agent_name = agent_name
        self.recoverable = recoverable
        super().__init__(message)


class BaseAgent(ABC):
    """Abstract base class for all agents in the system."""
    
    def __init__(self, name: str, settings: Settings):
        self.name = name
        self.settings = settings
        self.logger = logging.getLogger(f"agent.{name}")
        self.status = "available"
        self.created_at = datetime.now()
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if settings.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Agent-specific configuration
        self.config = self._get_agent_config()
        
        # Performance tracking
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_execution_time = 0.0
    
    def _get_agent_config(self) -> Dict[str, Any]:
        """Get agent-specific configuration from settings."""
        agents_config = getattr(self.settings, 'agents', None)
        if not agents_config:
            return {}
        
        agent_type = self.get_agent_type()
        return getattr(agents_config, agent_type, {})
    
    @abstractmethod
    def get_agent_type(self) -> str:
        """Return the type identifier for this agent."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of capabilities this agent provides."""
        pass
    
    @abstractmethod
    async def handle_task(self, task_message: TaskMessage, context: AgentWorkflowContext) -> TaskResult:
        """Handle a specific task assigned to this agent."""
        pass
    
    def get_agent_info(self) -> AgentInfo:
        """Get information about this agent."""
        return AgentInfo(
            name=self.name,
            type=self.get_agent_type(),
            description=self.get_description(),
            capabilities=self.get_capabilities(),
            status=self.status,
            metadata={
                "created_at": self.created_at.isoformat(),
                "tasks_completed": self.tasks_completed,
                "tasks_failed": self.tasks_failed,
                "average_execution_time": (
                    self.total_execution_time / max(self.tasks_completed, 1)
                ),
                "success_rate": (
                    self.tasks_completed / max(self.tasks_completed + self.tasks_failed, 1)
                )
            }
        )
    
    def get_description(self) -> str:
        """Get human-readable description of this agent."""
        return f"{self.get_agent_type().title()} Agent"
    
    async def execute_task(self, task_message: TaskMessage, context: AgentWorkflowContext, verbose: bool = False) -> ResultMessage:
        """Execute a task with error handling and performance tracking."""
        start_time = datetime.now()
        task_id = task_message.task.id
        
        try:
            self.logger.info(f"Starting task {task_id}: {task_message.task.action}")
            self.status = "busy"
            
            # Send status update
            await self._send_status_update("started", task_message, context)
            
            # Execute the actual task (store verbose in context for use in handle_task)
            context.shared_data['_verbose'] = verbose
            result = await self.handle_task(task_message, context)
            
            # Update performance metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            self.total_execution_time += execution_time
            
            if result.status == "success":
                self.tasks_completed += 1
                self.logger.info(f"Task {task_id} completed successfully in {execution_time:.2f}s")
            else:
                self.tasks_failed += 1
                self.logger.warning(f"Task {task_id} failed: {result.error}")
            
            # Send completion status
            await self._send_status_update("completed", task_message, context)
            
            return ResultMessage(
                sender=self.name,
                recipient=task_message.sender,
                correlation_id=task_message.correlation_id,
                result=result
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.tasks_failed += 1
            self.total_execution_time += execution_time
            
            self.logger.error(f"Task {task_id} failed with exception: {str(e)}")
            self.logger.debug(traceback.format_exc())
            
            # Create error result
            error_result = TaskResult(
                task_id=task_id,
                status="failed",
                error=str(e),
                execution_time=execution_time
            )
            
            # Send error status
            await self._send_status_update("failed", task_message, context)
            
            return ResultMessage(
                sender=self.name,
                recipient=task_message.sender,
                correlation_id=task_message.correlation_id,
                result=error_result
            )
        
        finally:
            self.status = "available"
    
    async def _send_status_update(self, status: str, task_message: TaskMessage, context: AgentWorkflowContext):
        """Send a status update message."""
        # In a full implementation, this would send to a message bus
        # For now, we'll just log it
        self.logger.debug(f"Status update: {status} for task {task_message.task.id}")
    
    async def call_llm(self, 
                      messages: List[Dict[str, str]], 
                      model: Optional[str] = None,
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None,
                      verbose: bool = False) -> str:
        """Call OpenAI LLM with the given messages."""
        if not self.openai_client:
            raise AgentError("OpenAI client not initialized (API key missing)", self.name)
        
        if not messages:
            raise AgentError("No messages provided to LLM", self.name)
        
        model = model or getattr(self.config, 'model', 'gpt-4o')
        max_tokens = max_tokens or getattr(self.config, 'max_tokens', 1000)
        
        if verbose:
            self._verbose_print_llm_call(messages, model, temperature, max_tokens)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result = response.choices[0].message.content.strip()
            
            if verbose:
                self._verbose_print_llm_response(result)
            
            return result
            
        except Exception as e:
            raise AgentError(f"LLM call failed: {str(e)}", self.name)
    
    def _verbose_print_llm_call(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int):
        """Print LLM call details in verbose mode."""
        from rich.console import Console
        console = Console()
        
        console.print(f"[dim]🧠 LLM Call ({self.name}):[/dim]")
        console.print(f"[dim]  • Model: {model}[/dim]")
        console.print(f"[dim]  • Temperature: {temperature}, Max tokens: {max_tokens}[/dim]")
        
        for i, msg in enumerate(messages):
            role = msg["role"]
            content = msg["content"]
            
            # Show first 200 chars of each message
            preview = content[:200] + "..." if len(content) > 200 else content
            # Replace newlines with spaces for cleaner display
            preview = preview.replace("\n", " ").replace("\r", "")
            
            console.print(f"[dim]  • {role.title()}: {preview}[/dim]")
    
    def _verbose_print_llm_response(self, response: str):
        """Print LLM response preview in verbose mode."""
        from rich.console import Console
        console = Console()
        
        # Show first 150 chars of response
        preview = response[:150] + "..." if len(response) > 150 else response
        preview = preview.replace("\n", " ").replace("\r", "")
        
        console.print(f"[dim]  → Response: {preview}[/dim]")
    
    async def call_llm_with_tools(self,
                                 messages: List[Dict[str, str]],
                                 tools: List[Dict[str, Any]],
                                 model: Optional[str] = None,
                                 temperature: float = 0.7) -> Dict[str, Any]:
        """Call OpenAI LLM with tool/function calling capability."""
        if not self.openai_client:
            raise AgentError("OpenAI client not initialized (API key missing)", self.name)
        
        model = model or getattr(self.config, 'model', 'gpt-4o')
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls
            }
            
        except Exception as e:
            raise AgentError(f"LLM tool call failed: {str(e)}", self.name)
    
    def validate_task_parameters(self, parameters: Dict[str, Any], required_params: List[str]):
        """Validate that required parameters are present in the parameters dict."""
        missing_params = []
        for param in required_params:
            if param not in parameters:
                missing_params.append(param)
        
        if missing_params:
            raise AgentError(
                f"Missing required parameters: {', '.join(missing_params)}",
                self.name
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on this agent."""
        return {
            "name": self.name,
            "type": self.get_agent_type(),
            "status": self.status,
            "healthy": True,
            "uptime": (datetime.now() - self.created_at).total_seconds(),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "openai_available": self.openai_client is not None
        }