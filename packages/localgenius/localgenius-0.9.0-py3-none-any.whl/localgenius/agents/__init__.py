"""Agent system for LocalGenius."""

from .base import BaseAgent, AgentError
from .registry import AgentRegistry
from .models import (
    AgentMessage, 
    QueryMessage, 
    PlanMessage, 
    TaskMessage, 
    ResultMessage, 
    ErrorMessage,
    MessageType
)

__all__ = [
    'BaseAgent',
    'AgentError', 
    'AgentRegistry',
    'AgentMessage',
    'QueryMessage',
    'PlanMessage', 
    'TaskMessage',
    'ResultMessage',
    'ErrorMessage',
    'MessageType'
]