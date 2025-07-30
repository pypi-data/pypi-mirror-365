"""Agent registry and discovery system."""

import logging
from typing import Dict, List, Optional, Type, Any
from collections import defaultdict

from .base import BaseAgent, AgentError
from .models import AgentInfo, AgentCapability


logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing and discovering agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, List[str]] = defaultdict(list)
        self._capabilities: Dict[str, List[str]] = defaultdict(list)
        self.logger = logging.getLogger("agent_registry")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent in the registry."""
        if agent.name in self._agents:
            raise AgentError(f"Agent with name '{agent.name}' already registered")
        
        self._agents[agent.name] = agent
        agent_type = agent.get_agent_type()
        self._agent_types[agent_type].append(agent.name)
        
        # Index capabilities
        for capability in agent.get_capabilities():
            self._capabilities[capability.name].append(agent.name)
        
        self.logger.info(f"Registered agent: {agent.name} (type: {agent_type})")
    
    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent from the registry."""
        if agent_name not in self._agents:
            raise AgentError(f"Agent '{agent_name}' not found in registry")
        
        agent = self._agents[agent_name]
        agent_type = agent.get_agent_type()
        
        # Remove from type index
        if agent_name in self._agent_types[agent_type]:
            self._agent_types[agent_type].remove(agent_name)
        
        # Remove from capability index
        for capability in agent.get_capabilities():
            if agent_name in self._capabilities[capability.name]:
                self._capabilities[capability.name].remove(agent_name)
        
        # Remove from main registry
        del self._agents[agent_name]
        
        self.logger.info(f"Unregistered agent: {agent_name}")
    
    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a specific agent by name."""
        return self._agents.get(agent_name)
    
    def get_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """Get all agents of a specific type."""
        agent_names = self._agent_types.get(agent_type, [])
        return [self._agents[name] for name in agent_names if name in self._agents]
    
    def get_agents_by_capability(self, capability_name: str) -> List[BaseAgent]:
        """Get all agents that have a specific capability."""
        agent_names = self._capabilities.get(capability_name, [])
        return [self._agents[name] for name in agent_names if name in self._agents]
    
    def find_best_agent_for_task(self, 
                                action: str, 
                                parameters: Dict[str, Any] = None,
                                agent_type: Optional[str] = None) -> Optional[BaseAgent]:
        """Find the best agent to handle a specific task."""
        parameters = parameters or {}
        
        # If agent type is specified, limit search to that type
        candidate_agents = []
        if agent_type:
            candidate_agents = self.get_agents_by_type(agent_type)
        else:
            candidate_agents = list(self._agents.values())
        
        # Filter agents that are available and have the required capability
        suitable_agents = []
        for agent in candidate_agents:
            if agent.status != "available":
                continue
            
            # Check if agent has capability for this action
            capabilities = agent.get_capabilities()
            for capability in capabilities:
                if capability.name == action or action in capability.name.lower():
                    suitable_agents.append((agent, capability))
                    break
        
        if not suitable_agents:
            return None
        
        # Simple selection: choose agent with best success rate
        # In a more sophisticated system, this could consider load, performance, etc.
        best_agent = None
        best_score = -1
        
        for agent, capability in suitable_agents:
            info = agent.get_agent_info()
            success_rate = info.metadata.get("success_rate", 0)
            avg_exec_time = info.metadata.get("average_execution_time", float('inf'))
            
            # Score based on success rate and speed (simple heuristic)
            score = success_rate - (avg_exec_time / 100)  # Penalize slow agents slightly
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent
    
    def list_all_agents(self) -> List[AgentInfo]:
        """Get information about all registered agents."""
        return [agent.get_agent_info() for agent in self._agents.values()]
    
    def list_available_agents(self) -> List[AgentInfo]:
        """Get information about all available agents."""
        return [
            agent.get_agent_info() 
            for agent in self._agents.values() 
            if agent.status == "available"
        ]
    
    def get_agent_types(self) -> List[str]:
        """Get list of all registered agent types."""
        return list(self._agent_types.keys())
    
    def get_capabilities(self) -> List[str]:
        """Get list of all available capabilities."""
        return list(self._capabilities.keys())
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all registered agents."""
        results = {}
        healthy_count = 0
        
        for name, agent in self._agents.items():
            try:
                health = await agent.health_check()
                results[name] = health
                if health.get("healthy", False):
                    healthy_count += 1
            except Exception as e:
                results[name] = {
                    "name": name,
                    "healthy": False,
                    "error": str(e)
                }
        
        return {
            "total_agents": len(self._agents),
            "healthy_agents": healthy_count,
            "unhealthy_agents": len(self._agents) - healthy_count,
            "agents": results
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        type_counts = {
            agent_type: len(agent_names)
            for agent_type, agent_names in self._agent_types.items()
        }
        
        status_counts = defaultdict(int)
        for agent in self._agents.values():
            status_counts[agent.status] += 1
        
        total_tasks = sum(agent.tasks_completed + agent.tasks_failed 
                         for agent in self._agents.values())
        total_success = sum(agent.tasks_completed for agent in self._agents.values())
        
        return {
            "total_agents": len(self._agents),
            "agent_types": dict(type_counts),
            "agent_status": dict(status_counts),
            "total_capabilities": len(self._capabilities),
            "total_tasks_processed": total_tasks,
            "overall_success_rate": total_success / max(total_tasks, 1),
            "capabilities": list(self._capabilities.keys())
        }
    
    def clear_registry(self) -> None:
        """Clear all agents from the registry."""
        self._agents.clear()
        self._agent_types.clear()
        self._capabilities.clear()
        self.logger.info("Registry cleared")


# Global registry instance
agent_registry = AgentRegistry()