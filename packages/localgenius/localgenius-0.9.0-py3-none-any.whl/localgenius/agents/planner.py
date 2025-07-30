"""Planner agent for analyzing queries and creating execution plans."""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseAgent, AgentError
from .models import (
    AgentCapability, TaskMessage, TaskResult, SubTask, ExecutionPlan,
    AgentWorkflowContext, QueryMessage, PlanMessage
)
from .registry import agent_registry


class PlannerAgent(BaseAgent):
    """Agent responsible for analyzing queries and creating execution plans."""
    
    def get_agent_type(self) -> str:
        return "planner"
    
    def get_description(self) -> str:
        return "Analyzes user queries and creates structured execution plans for other agents"
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="analyze_query",
                description="Analyze user query to understand intent and requirements",
                parameters={
                    "query": {"type": "string", "required": True},
                    "context": {"type": "object", "required": False}
                }
            ),
            AgentCapability(
                name="create_plan",
                description="Create structured execution plan with sub-tasks",
                parameters={
                    "query": {"type": "string", "required": True},
                    "available_agents": {"type": "array", "required": False}
                }
            ),
            AgentCapability(
                name="optimize_plan",
                description="Optimize execution plan for performance and resources",
                parameters={
                    "plan": {"type": "object", "required": True}
                }
            )
        ]
    
    async def handle_task(self, task_message: TaskMessage, context: AgentWorkflowContext) -> TaskResult:
        """Handle planning tasks."""
        action = task_message.task.action
        parameters = task_message.task.parameters
        
        try:
            if action == "analyze_query":
                return await self._analyze_query(parameters, context)
            elif action == "create_plan":
                return await self._create_plan(parameters, context)
            elif action == "optimize_plan":
                return await self._optimize_plan(parameters, context)
            else:
                raise AgentError(f"Unknown action: {action}", self.name)
        
        except Exception as e:
            return TaskResult(
                task_id=task_message.task.id,
                status="failed",
                error=str(e)
            )
    
    async def plan_query_execution(self, query: str, context: Dict[str, Any] = None) -> ExecutionPlan:
        """Main entry point for creating execution plans from queries."""
        context = context or {}
        
        # Analyze the query first
        analysis = await self._analyze_query_intent(query, context)
        
        # Create execution plan based on analysis
        plan = await self._create_execution_plan(query, analysis, context)
        
        # Optimize the plan
        optimized_plan = await self._optimize_execution_plan(plan)
        
        return optimized_plan
    
    async def _analyze_query(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Analyze user query to understand intent."""
        self.validate_task_parameters(parameters, ["query"])
        query = parameters["query"]
        query_context = parameters.get("context", {})
        
        analysis = await self._analyze_query_intent(query, query_context)
        
        return TaskResult(
            task_id="analyze_query",
            status="success",
            data=analysis
        )
    
    async def _create_plan(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Create execution plan for the query."""
        query = parameters["query"]
        available_agents = parameters.get("available_agents", [])
        query_context = parameters.get("context", {})
        
        # Get query analysis if not provided
        analysis = parameters.get("analysis")
        if not analysis:
            analysis = await self._analyze_query_intent(query, query_context)
        
        plan = await self._create_execution_plan(query, analysis, query_context)
        
        return TaskResult(
            task_id="create_plan",
            status="success",
            data=plan.model_dump()
        )
    
    async def _optimize_plan(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Optimize an existing execution plan."""
        plan_data = parameters["plan"]
        plan = ExecutionPlan(**plan_data)
        
        optimized_plan = await self._optimize_execution_plan(plan)
        
        return TaskResult(
            task_id="optimize_plan",
            status="success",
            data=optimized_plan.model_dump()
        )
    
    async def _analyze_query_intent(self, query: str, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to understand user intent using LLM."""
        
        system_prompt = """You are a query analysis expert. Analyze the user's query and determine:
1. Primary intent (search, question, analysis, indexing, conversion, etc.)
2. Required capabilities and resources
3. Expected output format
4. Complexity level (simple, moderate, complex)
5. Suggested approach

Respond with a JSON object containing this analysis."""
        
        user_prompt = f"""
Query: "{query}"
Context: {json.dumps(query_context) if query_context else "None"}

Analyze this query and provide structured analysis in JSON format with the following structure:
{{
    "primary_intent": "one of: search, question, analysis, indexing, conversion, management",
    "secondary_intents": ["list of secondary intents"],
    "required_capabilities": ["list of required agent capabilities"],
    "complexity": "simple|moderate|complex",
    "expected_output": "description of expected output",
    "suggested_approach": "high-level approach description",
    "resource_requirements": {{
        "requires_search": true/false,
        "requires_llm": true/false,
        "requires_indexing": true/false,
        "requires_conversion": true/false
    }},
    "estimated_duration": 60
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # For the planner, we don't have access to AgentWorkflowContext yet
        # We'll add verbose support here if needed in the future
        verbose = False
        
        try:
            response = await self.call_llm(messages, temperature=0.3, verbose=verbose)
            self.logger.debug(f"LLM response for query analysis: {response}")
            
            # Try to parse JSON response
            if response and response.strip():
                # Try to extract JSON from response if it's wrapped in other text
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    analysis = json.loads(json_str)
                    
                    # Validate and fix the estimated_duration field
                    if "estimated_duration" in analysis:
                        duration = analysis["estimated_duration"]
                        if isinstance(duration, str):
                            # Try to extract a number from string like "300-600 seconds"
                            import re
                            numbers = re.findall(r'\d+', duration)
                            if numbers:
                                analysis["estimated_duration"] = int(numbers[0])
                            else:
                                analysis["estimated_duration"] = 60  # Default
                        elif not isinstance(duration, int):
                            analysis["estimated_duration"] = 60  # Default
                    
                    return analysis
                else:
                    # No JSON found, use fallback
                    self.logger.warning(f"No JSON found in LLM response: {response[:200]}...")
                    raise json.JSONDecodeError("No JSON found in response", response, 0)
            else:
                # Empty response, use fallback
                self.logger.warning("Empty LLM response")
                raise json.JSONDecodeError("Empty response", "", 0)
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to parse LLM analysis, using fallback: {e}")
            return self._fallback_query_analysis(query, query_context)
    
    def _fallback_query_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback query analysis using simple heuristics."""
        query_lower = query.lower()
        
        # Simple intent detection with more patterns
        if any(word in query_lower for word in ["search", "find", "look for", "locate"]):
            primary_intent = "search"
        elif any(word in query_lower for word in ["what", "how", "why", "explain", "?", "describe", "tell me", "show me"]):
            primary_intent = "question"
        elif any(word in query_lower for word in ["index", "add", "import", "ingest"]):
            primary_intent = "indexing"
        elif any(word in query_lower for word in ["convert", "transform", "pdf", "docx"]):
            primary_intent = "conversion"
        elif any(word in query_lower for word in ["pattern", "architecture", "structure", "design", "code", "codebase"]):
            primary_intent = "analysis"  # Code analysis intent
        else:
            primary_intent = "question"  # Default
        
        # Determine required capabilities
        required_capabilities = []
        resource_requirements = {
            "requires_search": False,
            "requires_llm": False,
            "requires_indexing": False,
            "requires_conversion": False
        }
        
        if primary_intent == "search":
            required_capabilities.append("semantic_search")
            resource_requirements["requires_search"] = True
        elif primary_intent in ["question", "analysis"]:
            required_capabilities.extend(["semantic_search", "generate_answer"])
            resource_requirements["requires_search"] = True
            resource_requirements["requires_llm"] = True
        elif primary_intent == "indexing":
            required_capabilities.append("index_documents")
            resource_requirements["requires_indexing"] = True
        elif primary_intent == "conversion":
            required_capabilities.append("convert_document")
            resource_requirements["requires_conversion"] = True
        
        return {
            "primary_intent": primary_intent,
            "secondary_intents": [],
            "required_capabilities": required_capabilities,
            "complexity": "moderate",
            "expected_output": "relevant information or results",
            "suggested_approach": "use appropriate agent based on intent",
            "resource_requirements": resource_requirements,
            "estimated_duration": 30
        }
    
    async def _create_execution_plan(self, query: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> ExecutionPlan:
        """Create execution plan based on query analysis."""
        tasks = []
        parallel_groups = []
        
        primary_intent = analysis.get("primary_intent", "question")
        resource_reqs = analysis.get("resource_requirements", {})
        
        # Create tasks based on intent and requirements
        if primary_intent == "search":
            tasks.append(SubTask(
                agent_type="search",
                action="semantic_search",
                parameters={
                    "query": query,
                    "limit": context.get("limit", 10),
                    "threshold": context.get("threshold", 0.7)
                },
                priority=1
            ))
            
        elif primary_intent in ["question", "analysis"]:
            # For questions and analysis, we typically need search + RAG
            search_task = SubTask(
                agent_type="search",
                action="semantic_search",
                parameters={
                    "query": query,
                    "limit": context.get("limit", 10),
                    "threshold": context.get("threshold", 0.7)
                },
                priority=1
            )
            tasks.append(search_task)
            
            rag_task = SubTask(
                agent_type="rag",
                action="generate_answer",
                parameters={
                    "query": query,
                    "model": context.get("model", "gpt-4o")
                },
                dependencies=[search_task.id],
                priority=2
            )
            tasks.append(rag_task)
            
        elif primary_intent == "indexing":
            tasks.append(SubTask(
                agent_type="indexing",
                action="index_documents",
                parameters={
                    "source_path": context.get("source_path"),
                    "recursive": context.get("recursive", True)
                },
                priority=1
            ))
            
        elif primary_intent == "conversion":
            tasks.append(SubTask(
                agent_type="conversion",
                action="convert_document",
                parameters={
                    "file_path": context.get("file_path"),
                    "output_format": context.get("output_format", "markdown")
                },
                priority=1
            ))
        
        # Always add a reporter task at the end to synthesize results
        reporter_task = SubTask(
            agent_type="reporter",
            action="synthesize_results",
            parameters={
                "original_query": query,
                "format": context.get("output_format", "text")
            },
            dependencies=[task.id for task in tasks],
            priority=10
        )
        tasks.append(reporter_task)
        
        # Identify parallel execution opportunities
        independent_tasks = [task.id for task in tasks if not task.dependencies]
        if len(independent_tasks) > 1:
            parallel_groups.append(independent_tasks)
        
        return ExecutionPlan(
            query_id=context.get("query_id", "unknown"),
            tasks=tasks,
            estimated_duration=int(analysis.get("estimated_duration", 60)),
            resource_requirements=resource_reqs,
            parallel_groups=parallel_groups
        )
    
    async def _optimize_execution_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """Optimize execution plan for better performance."""
        # Check agent availability
        available_agents = agent_registry.list_available_agents()
        available_types = {agent.type for agent in available_agents}
        
        # Remove tasks for unavailable agent types (or mark for fallback)
        optimized_tasks = []
        for task in plan.tasks:
            if task.agent_type in available_types:
                optimized_tasks.append(task)
            else:
                self.logger.warning(f"Agent type '{task.agent_type}' not available, skipping task")
        
        # Update parallel groups based on available agents
        optimized_parallel_groups = []
        for group in plan.parallel_groups:
            available_in_group = [
                task_id for task_id in group
                if any(task.id == task_id and task.agent_type in available_types 
                      for task in optimized_tasks)
            ]
            if len(available_in_group) > 1:
                optimized_parallel_groups.append(available_in_group)
        
        return ExecutionPlan(
            id=plan.id,
            query_id=plan.query_id,
            tasks=optimized_tasks,
            estimated_duration=plan.estimated_duration,
            resource_requirements=plan.resource_requirements,
            parallel_groups=optimized_parallel_groups
        )