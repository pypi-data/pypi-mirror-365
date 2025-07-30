"""Planner agent for analyzing queries and creating execution plans."""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
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
    
    async def plan_query_execution(self, query: str, context: Dict[str, Any] = None, verbose: bool = False) -> ExecutionPlan:
        """Main entry point for creating comprehensive execution plans from queries."""
        context = context or {}
        
        # Step 1: Get data source overview (understand what data we have)
        data_overview = await self._analyze_available_data(context)
        
        # Step 2: Analyze the user's question in depth
        question_analysis = await self._deep_question_analysis(query, context)
        
        # Step 3: Create comprehensive plan considering data and question
        comprehensive_plan = await self._create_comprehensive_plan(query, question_analysis, data_overview, context)
        
        # Show planner analysis in verbose mode (most important output)
        if verbose:
            from rich.console import Console
            console = Console()
            console.print(f"\n[bold green]📊 Comprehensive Planner Analysis:[/bold green]")
            console.print("[dim]" + "="*80 + "[/dim]")
            
            console.print(f"[bold cyan]Data Overview:[/bold cyan]")
            for key, value in data_overview.items():
                console.print(f"  [yellow]{key}:[/yellow] {value}")
            
            console.print(f"\n[bold cyan]Question Analysis:[/bold cyan]")
            for key, value in question_analysis.items():
                if isinstance(value, dict):
                    console.print(f"  [yellow]{key}:[/yellow]")
                    for sub_key, sub_value in value.items():
                        console.print(f"    [cyan]{sub_key}:[/cyan] {sub_value}")
                elif isinstance(value, list):
                    console.print(f"  [yellow]{key}:[/yellow] {', '.join(map(str, value))}")
                else:
                    console.print(f"  [yellow]{key}:[/yellow] {value}")
            
            console.print(f"\n[bold cyan]Execution Plan:[/bold cyan]")
            for key, value in comprehensive_plan.items():
                if key == "todo_tasks":
                    console.print(f"  [yellow]{key}:[/yellow]")
                    for i, task in enumerate(value, 1):
                        console.print(f"    {i}. [green]{task}[/green]")
                elif isinstance(value, (dict, list)):
                    console.print(f"  [yellow]{key}:[/yellow] {value}")
                else:
                    console.print(f"  [yellow]{key}:[/yellow] {value}")
            
            console.print("[dim]" + "="*80 + "[/dim]\n")
        
        # Create technical execution plan for agents
        execution_plan = await self._create_execution_plan_from_comprehensive(query, comprehensive_plan, context)
        
        # Optimize the plan
        optimized_plan = await self._optimize_execution_plan(execution_plan)
        
        return optimized_plan
    
    async def _analyze_available_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze available data sources to understand what information we have access to."""
        try:
            # Import here to avoid circular imports
            from .registry import agent_registry
            from ..core.database import Database
            
            # Try to get database statistics
            data_overview = {
                "total_documents": 0,
                "data_sources": [],
                "document_types": [],
                "indexed_content_summary": "No indexed content available",
                "search_capabilities": "Basic semantic search available"
            }
            
            # Check if we have agents available
            available_agents = agent_registry.list_available_agents()
            agent_types = [agent.type for agent in available_agents]
            
            if "search" in agent_types:
                try:
                    # Try to get database instance from search agent to get statistics
                    search_agents = agent_registry.get_agents_by_type("search")
                    if search_agents and hasattr(search_agents[0], 'database'):
                        db = search_agents[0].database
                        stats = await db.get_statistics()
                        
                        data_overview.update({
                            "total_documents": stats.get("total_documents", 0),
                            "data_sources": list(stats.get("sources", {}).keys()),
                            "document_types": stats.get("file_types", []),
                            "indexed_content_summary": f"Has {stats.get('total_documents', 0)} indexed document chunks from {len(stats.get('sources', {}))} sources"
                        })
                        
                        if stats.get("total_documents", 0) > 0:
                            data_overview["search_capabilities"] = "Advanced semantic search with embeddings available"
                            
                except Exception as e:
                    self.logger.warning(f"Could not get database statistics: {e}")
            
            data_overview["available_agents"] = agent_types
            return data_overview
            
        except Exception as e:
            self.logger.error(f"Failed to analyze available data: {e}")
            return {
                "total_documents": 0,
                "data_sources": [],
                "document_types": [],
                "indexed_content_summary": "Unable to analyze available data",
                "search_capabilities": "Unknown",
                "available_agents": []
            }
    
    async def _deep_question_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform deep analysis of the user's question to understand what they really want."""
        
        system_prompt = """You are an expert question analyst. Your job is to deeply understand what the user is really asking and what kind of answer would best serve their needs.

Analyze the user's question from multiple perspectives:
1. Surface-level: What are they literally asking?
2. Intent level: What do they really want to know?
3. Context level: What might be the broader context or use case?
4. Depth level: How comprehensive should the answer be?
5. Format level: How should the information be presented?

Provide a detailed analysis that will help plan the best research approach."""
        
        user_prompt = f"""
User Question: "{query}"
Context: {json.dumps(context) if context else "None provided"}

Analyze this question comprehensively and provide structured analysis in JSON format:
{{
    "literal_question": "What they're literally asking",
    "underlying_intent": "What they really want to understand",
    "question_type": "factual|analytical|comparative|explanatory|procedural|creative",
    "complexity_level": "basic|intermediate|advanced|expert",
    "scope": "narrow|moderate|broad|comprehensive",
    "expected_answer_format": "brief_summary|detailed_explanation|step_by_step|comparison_table|research_report",
    "key_concepts": ["list of main concepts that need to be addressed"],
    "sub_questions": ["list of sub-questions that need to be answered to fully address the main question"],
    "context_requirements": ["what kind of background context would be helpful"],
    "success_criteria": ["how to know if we've answered the question well"],
    "potential_follow_ups": ["likely follow-up questions the user might have"]
}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.3, verbose=False)
            
            # Try to parse JSON response
            if response and response.strip():
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    analysis = json.loads(json_str)
                    return analysis
            
            raise json.JSONDecodeError("No valid JSON found", response, 0)
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to analyze question deeply, using fallback: {e}")
            return self._fallback_question_analysis(query, context)
    
    def _fallback_question_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback question analysis using simple heuristics."""
        query_lower = query.lower()
        
        # Determine question type
        if any(word in query_lower for word in ["what is", "define", "explain"]):
            question_type = "explanatory"
        elif any(word in query_lower for word in ["how to", "how do", "steps"]):
            question_type = "procedural"
        elif any(word in query_lower for word in ["compare", "difference", "vs", "versus"]):
            question_type = "comparative"
        elif any(word in query_lower for word in ["why", "analyze", "impact"]):
            question_type = "analytical"
        else:
            question_type = "factual"
        
        return {
            "literal_question": query,
            "underlying_intent": "Seeking information or understanding",
            "question_type": question_type,
            "complexity_level": "intermediate",
            "scope": "moderate",
            "expected_answer_format": "detailed_explanation",
            "key_concepts": [query],
            "sub_questions": [f"What are the key aspects of {query}?"],
            "context_requirements": ["General background information"],
            "success_criteria": ["Provides clear, accurate information"],
            "potential_follow_ups": ["Related questions about implementation or details"]
        }
    
    async def _create_comprehensive_plan(self, query: str, question_analysis: Dict[str, Any], data_overview: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive plan that combines question understanding with data analysis."""
        
        system_prompt = """You are an expert research planner. Given a deep analysis of the user's question and an overview of available data, create a comprehensive research plan.

Your plan should be like a detailed todo list that other AI agents can follow to thoroughly answer the user's question. Think about this as planning a research project.

Key principles:
1. Use the available data effectively
2. Address all aspects of the user's question
3. Create clear, actionable steps
4. Consider different search strategies
5. Plan for comprehensive analysis and synthesis
6. Anticipate information gaps and how to handle them"""
        
        user_prompt = f"""
USER QUESTION: "{query}"

QUESTION ANALYSIS:
{json.dumps(question_analysis, indent=2)}

AVAILABLE DATA:
{json.dumps(data_overview, indent=2)}

Create a comprehensive research plan in JSON format:
{{
    "research_strategy": "overall approach to answering this question",
    "data_utilization_plan": "how to best use the available indexed data",
    "search_strategy": {{
        "primary_searches": ["list of main search queries to run"],
        "secondary_searches": ["list of follow-up searches based on findings"],
        "search_techniques": ["semantic", "keyword", "contextual", "multi-query"]
    }},
    "todo_tasks": [
        "1. [SEARCH] Run broad search on main topic",
        "2. [ANALYZE] Review search results for key patterns",
        "3. [SEARCH] Conduct targeted searches on specific aspects",
        "4. [SYNTHESIZE] Combine findings into comprehensive answer",
        "5. [VALIDATE] Check completeness against success criteria"
    ],
    "information_gaps": ["potential gaps in available data"],
    "success_metrics": ["how to measure if the research was successful"],
    "estimated_complexity": "low|medium|high|very_high",
    "expected_deliverable": "description of final output format"
}}

Make the todo_tasks very specific and actionable - like a step-by-step research protocol that agents can follow.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.4, verbose=False)
            
            # Try to parse JSON response
            if response and response.strip():
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    plan = json.loads(json_str)
                    return plan
            
            raise json.JSONDecodeError("No valid JSON found", response, 0)
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to create comprehensive plan, using fallback: {e}")
            return self._fallback_comprehensive_plan(query, question_analysis, data_overview)
    
    def _fallback_comprehensive_plan(self, query: str, question_analysis: Dict[str, Any], data_overview: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback comprehensive plan using simple heuristics."""
        
        has_data = data_overview.get("total_documents", 0) > 0
        
        todo_tasks = [
            "1. [SEARCH] Search for information related to the main question",
            "2. [ANALYZE] Review and categorize the found information",
            "3. [SEARCH] Conduct follow-up searches on specific aspects",
            "4. [SYNTHESIZE] Combine all findings into a comprehensive response",
            "5. [VALIDATE] Ensure the response addresses all aspects of the question"
        ]
        
        if has_data:
            search_strategy = {
                "primary_searches": [query],
                "secondary_searches": question_analysis.get("key_concepts", [query]),
                "search_techniques": ["semantic", "contextual"]
            }
        else:
            search_strategy = {
                "primary_searches": [query],
                "secondary_searches": [],
                "search_techniques": ["basic"]
            }
            todo_tasks = [
                "1. [INFO] No indexed data available - using general knowledge",
                "2. [ANALYZE] Break down the question into key components",
                "3. [SYNTHESIZE] Provide comprehensive answer based on available knowledge",
                "4. [VALIDATE] Ensure response addresses the user's needs"
            ]
        
        return {
            "research_strategy": f"Comprehensive analysis of '{query}' using available resources",
            "data_utilization_plan": "Use semantic search to find relevant information" if has_data else "No indexed data available",
            "search_strategy": search_strategy,
            "todo_tasks": todo_tasks,
            "information_gaps": ["May need additional context depending on search results"],
            "success_metrics": ["Addresses all aspects of the question", "Provides actionable information"],
            "estimated_complexity": "medium",
            "expected_deliverable": "Comprehensive written response with analysis and recommendations"
        }
    
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
    
    async def _create_execution_plan_from_comprehensive(self, query: str, comprehensive_plan: Dict[str, Any], context: Dict[str, Any]) -> ExecutionPlan:
        """Convert comprehensive plan into technical execution plan for agents."""
        tasks = []
        parallel_groups = []
        
        search_strategy = comprehensive_plan.get("search_strategy", {})
        primary_searches = search_strategy.get("primary_searches", [query])
        secondary_searches = search_strategy.get("secondary_searches", [])
        search_techniques = search_strategy.get("search_techniques", ["semantic"])
        
        # Use enhanced search parameters
        search_limit = context.get("limit", 50)
        search_threshold = context.get("threshold", 0.6)
        context_items = 30
        
        # Create search tasks based on the comprehensive plan
        search_task_ids = []
        
        # Primary search task
        if "semantic" in search_techniques:
            primary_search_task = SubTask(
                agent_type="search",
                action="semantic_search",
                parameters={
                    "query": primary_searches[0] if primary_searches else query,
                    "limit": search_limit,
                    "threshold": search_threshold
                },
                priority=1
            )
            tasks.append(primary_search_task)
            search_task_ids.append(primary_search_task.id)
        
        # Multi-query search if we have multiple searches
        if len(primary_searches + secondary_searches) > 1 and "multi-query" in search_techniques:
            all_queries = (primary_searches + secondary_searches)[:5]  # Limit to 5
            multi_search_task = SubTask(
                agent_type="search",
                action="multi_query_search",
                parameters={
                    "queries": all_queries,
                    "limit": search_limit,
                    "threshold": search_threshold
                },
                priority=1
            )
            tasks.append(multi_search_task)
            search_task_ids.append(multi_search_task.id)
            
            # Add parallel execution for independent searches
            if len(search_task_ids) > 1:
                parallel_groups.append(search_task_ids[-2:])
        
        # Contextual search if specified
        if "contextual" in search_techniques:
            contextual_search_task = SubTask(
                agent_type="search",
                action="contextual_search",
                parameters={
                    "query": query,
                    "context": {
                        "research_plan": comprehensive_plan,
                        "search_focus": comprehensive_plan.get("research_strategy", "")
                    },
                    "limit": search_limit,
                    "threshold": search_threshold
                },
                dependencies=search_task_ids[:1],  # Depend on first search
                priority=2
            )
            tasks.append(contextual_search_task)
            search_task_ids.append(contextual_search_task.id)
        
        # RAG task for comprehensive answer generation
        rag_task = SubTask(
            agent_type="rag",
            action="generate_answer",
            parameters={
                "query": query,
                "model": context.get("model", "gpt-4o"),
                "context_items": context_items,
                "similarity_threshold": search_threshold,
                "research_context": comprehensive_plan  # Pass the plan for context
            },
            dependencies=search_task_ids,
            priority=3
        )
        tasks.append(rag_task)
        
        # Reporter task with comprehensive synthesis
        reporter_task = SubTask(
            agent_type="reporter",
            action="synthesize_results",
            parameters={
                "original_query": query,
                "format": context.get("output_format", "text"),
                "research_plan": comprehensive_plan,
                "comprehensive_analysis": True
            },
            dependencies=[task.id for task in tasks],
            priority=10
        )
        tasks.append(reporter_task)
        
        # Quality assessment for comprehensive research
        complexity = comprehensive_plan.get("estimated_complexity", "medium")
        if complexity in ["high", "very_high"]:
            quality_task = SubTask(
                agent_type="reporter",
                action="quality_assessment",
                parameters={
                    "results": "workflow_results",
                    "original_query": query,
                    "success_criteria": comprehensive_plan.get("success_metrics", [])
                },
                dependencies=[task.id for task in tasks[:-1]],  # All except reporter
                priority=9
            )
            tasks.append(quality_task)
        
        estimated_duration = 120 if complexity in ["high", "very_high"] else 90
        
        return ExecutionPlan(
            query_id=context.get("query_id", "unknown"),
            tasks=tasks,
            estimated_duration=estimated_duration,
            resource_requirements={
                "requires_search": len(search_task_ids) > 0,
                "requires_llm": True,
                "requires_indexing": False,
                "requires_conversion": False
            },
            parallel_groups=parallel_groups
        )
    
    async def get_raw_planner_response(self, query: str, query_context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Get both raw LLM response and comprehensive analysis for --plan mode."""
        # Get data source overview
        data_overview = await self._analyze_available_data(query_context)
        
        # Get deep question analysis  
        question_analysis = await self._deep_question_analysis(query, query_context)
        
        # Get comprehensive plan with raw response
        comprehensive_plan, raw_plan_response = await self._create_comprehensive_plan_with_raw(query, question_analysis, data_overview, query_context)
        
        # Combine all analysis into a single response
        full_analysis = {
            "data_overview": data_overview,
            "question_analysis": question_analysis,
            "comprehensive_plan": comprehensive_plan
        }
        
        return raw_plan_response, full_analysis
    
    async def _create_comprehensive_plan_with_raw(self, query: str, question_analysis: Dict[str, Any], data_overview: Dict[str, Any], context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Create comprehensive plan and return both parsed plan and raw LLM response."""
        
        system_prompt = """You are an expert research planner. Given a deep analysis of the user's question and an overview of available data, create a comprehensive research plan.

Your plan should be like a detailed todo list that other AI agents can follow to thoroughly answer the user's question. Think about this as planning a research project.

Key principles:
1. Use the available data effectively
2. Address all aspects of the user's question
3. Create clear, actionable steps
4. Consider different search strategies
5. Plan for comprehensive analysis and synthesis
6. Anticipate information gaps and how to handle them"""
        
        user_prompt = f"""
USER QUESTION: "{query}"

QUESTION ANALYSIS:
{json.dumps(question_analysis, indent=2)}

AVAILABLE DATA:
{json.dumps(data_overview, indent=2)}

Create a comprehensive research plan in JSON format:
{{
    "research_strategy": "overall approach to answering this question",
    "data_utilization_plan": "how to best use the available indexed data",
    "search_strategy": {{
        "primary_searches": ["list of main search queries to run"],
        "secondary_searches": ["list of follow-up searches based on findings"],
        "search_techniques": ["semantic", "keyword", "contextual", "multi-query"]
    }},
    "todo_tasks": [
        "1. [SEARCH] Run broad search on main topic",
        "2. [ANALYZE] Review search results for key patterns",
        "3. [SEARCH] Conduct targeted searches on specific aspects",
        "4. [SYNTHESIZE] Combine findings into comprehensive answer",
        "5. [VALIDATE] Check completeness against success criteria"
    ],
    "information_gaps": ["potential gaps in available data"],
    "success_metrics": ["how to measure if the research was successful"],
    "estimated_complexity": "low|medium|high|very_high",
    "expected_deliverable": "description of final output format"
}}

Make the todo_tasks very specific and actionable - like a step-by-step research protocol that agents can follow.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.4, verbose=False)
            
            # Try to parse JSON response
            if response and response.strip():
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    plan = json.loads(json_str)
                    return plan, response
            
            raise json.JSONDecodeError("No valid JSON found", response, 0)
            
        except (json.JSONDecodeError, Exception) as e:
            self.logger.warning(f"Failed to create comprehensive plan, using fallback: {e}")
            fallback_plan = self._fallback_comprehensive_plan(query, question_analysis, data_overview)
            return fallback_plan, "No LLM response (using fallback comprehensive plan)"
    
    async def _analyze_query_intent_with_raw(self, query: str, query_context: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """Analyze query and return both parsed analysis and raw LLM response."""
        
        system_prompt = """You are an expert research planner and query analysis specialist. Your role is to analyze user queries with a focus on comprehensive research and deep analysis requirements.

For research-oriented queries, you should:
1. Identify opportunities for multi-faceted investigation
2. Consider various analytical perspectives and approaches
3. Plan for comprehensive source coverage and evidence gathering
4. Anticipate follow-up questions and related topics
5. Design execution plans that maximize information depth

Analyze the user's query and determine:
1. Primary intent (search, question, analysis, indexing, conversion, research, investigation)
2. Research depth required (surface, moderate, comprehensive, academic)
3. Required capabilities and resources for thorough investigation
4. Expected output format and detail level
5. Complexity level considering research scope (simple, moderate, complex, extensive)
6. Multi-stage approach for comprehensive coverage
7. Potential sub-topics and related areas to explore

Respond with a JSON object containing this enhanced analysis."""
        
        user_prompt = f"""
Query: "{query}"
Context: {json.dumps(query_context) if query_context else "None"}

Analyze this query for comprehensive research potential and provide structured analysis in JSON format:
{{
    "primary_intent": "one of: search, question, analysis, indexing, conversion, management, research, investigation",
    "research_depth": "surface|moderate|comprehensive|academic",
    "secondary_intents": ["list of secondary research angles and related topics"],
    "required_capabilities": ["list of required agent capabilities for thorough investigation"],
    "complexity": "simple|moderate|complex|extensive",
    "expected_output": "detailed description of comprehensive output format",
    "suggested_approach": "multi-stage research approach with specific methodologies",
    "research_scope": {{
        "main_topics": ["primary research areas"],
        "sub_topics": ["related areas to explore"],
        "analytical_perspectives": ["different angles of analysis"],
        "evidence_types": ["types of evidence to gather"]
    }},
    "resource_requirements": {{
        "requires_search": true/false,
        "requires_llm": true/false,
        "requires_indexing": true/false,
        "requires_conversion": true/false,
        "requires_multi_query_search": true/false,
        "requires_contextual_analysis": true/false
    }},
    "execution_stages": ["ordered list of research phases"],
    "estimated_duration": 120
}}

Focus on identifying opportunities for deep, comprehensive research that will provide maximum value and insight.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
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
                            numbers = re.findall(r'\\d+', duration)
                            if numbers:
                                analysis["estimated_duration"] = int(numbers[0])
                            else:
                                analysis["estimated_duration"] = 60  # Default
                        elif not isinstance(duration, int):
                            analysis["estimated_duration"] = 60  # Default
                    
                    return analysis, response
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
            fallback_analysis = self._fallback_query_analysis(query, query_context)
            return fallback_analysis, "No LLM response (using fallback analysis)"

    async def _analyze_query_intent(self, query: str, query_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to understand user intent using LLM."""
        analysis, _ = await self._analyze_query_intent_with_raw(query, query_context)
        return analysis
    
    def _fallback_query_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback query analysis using simple heuristics."""
        query_lower = query.lower()
        
        # Enhanced intent detection with research patterns
        if any(word in query_lower for word in ["research", "investigate", "analyze deeply", "comprehensive", "thorough", "detailed study"]):
            primary_intent = "research"
        elif any(word in query_lower for word in ["search", "find", "look for", "locate"]):
            primary_intent = "search"
        elif any(word in query_lower for word in ["what", "how", "why", "explain", "?", "describe", "tell me", "show me"]):
            primary_intent = "question"
        elif any(word in query_lower for word in ["index", "add", "import", "ingest"]):
            primary_intent = "indexing"
        elif any(word in query_lower for word in ["convert", "transform", "pdf", "docx"]):
            primary_intent = "conversion"
        elif any(word in query_lower for word in ["pattern", "architecture", "structure", "design", "code", "codebase", "analyze", "analysis"]):
            primary_intent = "analysis"
        else:
            primary_intent = "research"  # Default to research for comprehensive coverage
        
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
        
        # Enhanced fallback with research-oriented defaults
        secondary_intents = []
        research_scope = {
            "main_topics": ["primary query topic"],
            "sub_topics": ["related areas"],
            "analytical_perspectives": ["multiple viewpoints"],
            "evidence_types": ["documented evidence"]
        }
        execution_stages = ["initial search", "content analysis", "synthesis"]
        
        # Enhance resource requirements for comprehensive research
        if primary_intent in ["question", "analysis", "research"]:
            resource_requirements["requires_multi_query_search"] = True
            resource_requirements["requires_contextual_analysis"] = True
            secondary_intents = ["contextual_analysis", "source_validation", "comprehensive_synthesis"]
            execution_stages = ["broad search", "targeted search", "context analysis", "synthesis", "validation"]
        
        return {
            "primary_intent": primary_intent,
            "research_depth": "comprehensive" if primary_intent in ["research", "analysis"] else "moderate",
            "secondary_intents": secondary_intents,
            "required_capabilities": required_capabilities,
            "complexity": "complex" if primary_intent in ["research", "analysis"] else "moderate",
            "expected_output": "comprehensive research report with detailed analysis and multiple perspectives",
            "suggested_approach": "multi-stage research approach with extensive source coverage and analytical depth",
            "research_scope": research_scope,
            "resource_requirements": resource_requirements,
            "execution_stages": execution_stages,
            "estimated_duration": 120 if primary_intent in ["research", "analysis"] else 60
        }
    
    async def _create_execution_plan(self, query: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> ExecutionPlan:
        """Create execution plan based on query analysis with focus on comprehensive research."""
        tasks = []
        parallel_groups = []
        
        primary_intent = analysis.get("primary_intent", "question")
        research_depth = analysis.get("research_depth", "moderate")
        resource_reqs = analysis.get("resource_requirements", {})
        research_scope = analysis.get("research_scope", {})
        execution_stages = analysis.get("execution_stages", ["search", "analysis"])
        
        # Use enhanced limits for comprehensive research
        search_limit = context.get("limit", 50 if research_depth in ["comprehensive", "academic"] else 20)
        search_threshold = context.get("threshold", 0.6 if research_depth in ["comprehensive", "academic"] else 0.7)
        context_items = 30 if research_depth in ["comprehensive", "academic"] else 15
        
        # Create tasks based on intent and research depth
        if primary_intent == "search":
            # Even simple searches should be comprehensive
            tasks.append(SubTask(
                agent_type="search",
                action="semantic_search",
                parameters={
                    "query": query,
                    "limit": search_limit,
                    "threshold": search_threshold
                },
                priority=1
            ))
            
        elif primary_intent in ["question", "analysis", "research"]:
            # Multi-stage research approach
            
            # Stage 1: Broad semantic search
            broad_search_task = SubTask(
                agent_type="search",
                action="semantic_search",
                parameters={
                    "query": query,
                    "limit": search_limit,
                    "threshold": search_threshold
                },
                priority=1
            )
            tasks.append(broad_search_task)
            
            # Stage 2: Multi-query search for comprehensive coverage
            if resource_reqs.get("requires_multi_query_search", False):
                # Generate related queries from research scope
                main_topics = research_scope.get("main_topics", [query])
                sub_topics = research_scope.get("sub_topics", [])
                search_queries = [query] + main_topics + sub_topics
                
                multi_search_task = SubTask(
                    agent_type="search",
                    action="multi_query_search",
                    parameters={
                        "queries": search_queries[:5],  # Limit to 5 queries for performance
                        "limit": search_limit,
                        "threshold": search_threshold
                    },
                    priority=1  # Can run in parallel with broad search
                )
                tasks.append(multi_search_task)
                
                # Add to parallel group for concurrent execution
                parallel_groups.append([broad_search_task.id, multi_search_task.id])
            
            # Stage 3: Contextual analysis if required
            if resource_reqs.get("requires_contextual_analysis", False):
                contextual_search_task = SubTask(
                    agent_type="search",
                    action="contextual_search",
                    parameters={
                        "query": query,
                        "context": {
                            "research_scope": research_scope,
                            "analytical_perspectives": research_scope.get("analytical_perspectives", [])
                        },
                        "limit": search_limit,
                        "threshold": search_threshold
                    },
                    dependencies=[broad_search_task.id],
                    priority=2
                )
                tasks.append(contextual_search_task)
            
            # Stage 4: Comprehensive RAG generation
            search_dependencies = [task.id for task in tasks if task.agent_type == "search"]
            
            rag_task = SubTask(
                agent_type="rag",
                action="generate_answer",
                parameters={
                    "query": query,
                    "model": context.get("model", "gpt-4o"),
                    "context_items": context_items,
                    "similarity_threshold": search_threshold
                },
                dependencies=search_dependencies,
                priority=3
            )
            tasks.append(rag_task)
            
            # Stage 5: Context relevance analysis for comprehensive research
            if research_depth in ["comprehensive", "academic"]:
                relevance_task = SubTask(
                    agent_type="rag",
                    action="analyze_context_relevance",
                    parameters={
                        "query": query,
                        "context": "results_from_search_tasks"  # Will be populated at runtime
                    },
                    dependencies=search_dependencies,
                    priority=3  # Can run in parallel with main RAG task
                )
                tasks.append(relevance_task)
            
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
        
        # Always add a comprehensive reporter task at the end to synthesize results
        all_task_dependencies = [task.id for task in tasks]
        
        reporter_task = SubTask(
            agent_type="reporter",
            action="synthesize_results",
            parameters={
                "original_query": query,
                "format": context.get("output_format", "text"),
                "research_depth": research_depth,
                "comprehensive_analysis": research_depth in ["comprehensive", "academic"]
            },
            dependencies=all_task_dependencies,
            priority=10
        )
        tasks.append(reporter_task)
        
        # Add quality assessment for comprehensive research
        if research_depth in ["comprehensive", "academic"]:
            quality_task = SubTask(
                agent_type="reporter",
                action="quality_assessment",
                parameters={
                    "results": "workflow_results",  # Will be populated at runtime
                    "original_query": query
                },
                dependencies=all_task_dependencies,
                priority=9
            )
            tasks.append(quality_task)
        
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
        """Optimize execution plan for better performance and comprehensive research coverage."""
        # Check agent availability
        available_agents = agent_registry.list_available_agents()
        available_types = {agent.type for agent in available_agents}
        
        # Remove tasks for unavailable agent types (or mark for fallback)
        optimized_tasks = []
        skipped_tasks = []
        
        for task in plan.tasks:
            if task.agent_type in available_types:
                optimized_tasks.append(task)
            else:
                skipped_tasks.append(task)
                self.logger.warning(f"Agent type '{task.agent_type}' not available, skipping task")
        
        # Update dependencies for remaining tasks if some were removed
        if skipped_tasks:
            skipped_ids = {task.id for task in skipped_tasks}
            for task in optimized_tasks:
                if task.dependencies:
                    task.dependencies = [dep for dep in task.dependencies if dep not in skipped_ids]
        
        # Optimize parallel groups based on available agents and research depth
        optimized_parallel_groups = []
        for group in plan.parallel_groups:
            available_in_group = [
                task_id for task_id in group
                if any(task.id == task_id and task.agent_type in available_types 
                      for task in optimized_tasks)
            ]
            if len(available_in_group) > 1:
                optimized_parallel_groups.append(available_in_group)
        
        # Add additional parallel opportunities for research workflows
        search_tasks = [task for task in optimized_tasks if task.agent_type == "search"]
        if len(search_tasks) > 1:
            # Multiple search tasks can often run in parallel
            independent_search_tasks = [
                task.id for task in search_tasks 
                if not task.dependencies or not any(dep in [t.id for t in search_tasks] for dep in task.dependencies)
            ]
            if len(independent_search_tasks) > 1 and independent_search_tasks not in optimized_parallel_groups:
                optimized_parallel_groups.append(independent_search_tasks)
        
        # Adjust estimated duration based on parallelization opportunities
        base_duration = plan.estimated_duration
        if optimized_parallel_groups:
            # Estimate time savings from parallel execution (conservative estimate)
            parallel_efficiency = 0.7  # Assume 70% efficiency in parallel execution
            estimated_savings = len(optimized_parallel_groups) * 20 * parallel_efficiency
            optimized_duration = max(base_duration - estimated_savings, base_duration * 0.6)
        else:
            optimized_duration = base_duration
        
        return ExecutionPlan(
            id=plan.id,
            query_id=plan.query_id,
            tasks=optimized_tasks,
            estimated_duration=int(optimized_duration),
            resource_requirements=plan.resource_requirements,
            parallel_groups=optimized_parallel_groups
        )