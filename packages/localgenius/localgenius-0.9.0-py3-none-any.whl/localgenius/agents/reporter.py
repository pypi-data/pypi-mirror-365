"""Reporter agent for synthesizing and formatting results from multiple agents."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseAgent, AgentError
from .models import (
    AgentCapability, TaskMessage, TaskResult, AgentWorkflowContext,
    ExecutionPlan
)


class ReporterAgent(BaseAgent):
    """Agent responsible for synthesizing results from multiple agents and creating final reports."""
    
    def get_agent_type(self) -> str:
        return "reporter"
    
    def get_description(self) -> str:
        return "Synthesizes results from multiple agents into comprehensive, well-formatted responses"
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="synthesize_results",
                description="Combine results from multiple agents into a coherent response",
                parameters={
                    "original_query": {"type": "string", "required": True},
                    "results": {"type": "array", "required": False},
                    "format": {"type": "string", "default": "text"}
                },
                estimated_duration=8
            ),
            AgentCapability(
                name="format_response",
                description="Format response in specific output format",
                parameters={
                    "content": {"type": "string", "required": True},
                    "format": {"type": "string", "default": "markdown"},
                    "metadata": {"type": "object", "required": False}
                },
                estimated_duration=3
            ),
            AgentCapability(
                name="create_summary",
                description="Create executive summary of workflow results",
                parameters={
                    "workflow_results": {"type": "object", "required": True},
                    "detail_level": {"type": "string", "default": "medium"}
                },
                estimated_duration=5
            ),
            AgentCapability(
                name="quality_assessment",
                description="Assess quality and completeness of results",
                parameters={
                    "results": {"type": "array", "required": True},
                    "original_query": {"type": "string", "required": True}
                },
                estimated_duration=6
            )
        ]
    
    async def handle_task(self, task_message: TaskMessage, context: AgentWorkflowContext) -> TaskResult:
        """Handle reporting and synthesis tasks."""
        action = task_message.task.action
        parameters = task_message.task.parameters
        
        try:
            if action == "synthesize_results":
                return await self._synthesize_results(parameters, context)
            elif action == "format_response":
                return await self._format_response(parameters, context)
            elif action == "create_summary":
                return await self._create_summary(parameters, context)
            elif action == "quality_assessment":
                return await self._quality_assessment(parameters, context)
            else:
                raise AgentError(f"Unknown reporter action: {action}", self.name)
        
        except Exception as e:
            return TaskResult(
                task_id=task_message.task.id,
                status="failed",
                error=str(e)
            )
    
    async def _synthesize_results(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Synthesize results from the workflow context into a final response."""
        original_query = parameters["original_query"]
        output_format = parameters.get("format", "text")
        
        # Get results from context
        completed_tasks = context.completed_tasks
        failed_tasks = context.failed_tasks
        
        if not completed_tasks:
            return TaskResult(
                task_id="synthesize_results",
                status="success",
                data={
                    "query": original_query,
                    "response": "No results were generated from the executed workflow.",
                    "format": output_format,
                    "summary": {
                        "total_tasks": len(failed_tasks),
                        "successful_tasks": 0,
                        "failed_tasks": len(failed_tasks)
                    }
                }
            )
        
        # Analyze and organize results by type
        organized_results = self._organize_results_by_type(completed_tasks)
        
        # Generate synthesis using LLM
        synthesis = await self._generate_synthesis(
            original_query, 
            organized_results, 
            output_format,
            context
        )
        
        # Create metadata
        metadata = {
            "synthesis_timestamp": datetime.now().isoformat(),
            "total_tasks": len(completed_tasks) + len(failed_tasks),
            "successful_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "result_types": list(organized_results.keys()),
            "workflow_duration": (
                datetime.now() - context.start_time
            ).total_seconds()
        }
        
        return TaskResult(
            task_id="synthesize_results",
            status="success",
            data={
                "query": original_query,
                "response": synthesis,
                "format": output_format,
                "summary": metadata,
                "detailed_results": organized_results
            },
            metadata=metadata
        )
    
    def _organize_results_by_type(self, completed_tasks: List[TaskResult]) -> Dict[str, List[Any]]:
        """Organize completed task results by their type/source."""
        organized = {
            "search_results": [],
            "rag_answers": [],
            "analysis_results": [],
            "other_results": []
        }
        
        for task_result in completed_tasks:
            if not task_result.data:
                continue
                
            # Determine result type based on metadata or content structure
            metadata = task_result.metadata or {}
            data = task_result.data
            
            if metadata.get("search_type") or "results" in data and "similarity_score" in str(data):
                organized["search_results"].append(data)
            elif metadata.get("rag_type") or "answer" in data:
                organized["rag_answers"].append(data)
            elif metadata.get("analysis_type"):
                organized["analysis_results"].append(data)
            else:
                organized["other_results"].append(data)
        
        # Remove empty categories
        return {k: v for k, v in organized.items() if v}
    
    async def _generate_synthesis(self, 
                                 original_query: str,
                                 organized_results: Dict[str, List[Any]],
                                 output_format: str,
                                 context: AgentWorkflowContext) -> str:
        """Generate synthesis using LLM."""
        
        # Prepare context for synthesis
        results_summary = []
        
        for result_type, results in organized_results.items():
            if result_type == "search_results":
                total_documents = sum(len(r.get("results", [])) for r in results)
                results_summary.append(f"Found {total_documents} relevant documents from semantic search")
                
            elif result_type == "rag_answers":
                answers = [r.get("answer", "") for r in results if r.get("answer")]
                if answers:
                    results_summary.append(f"Generated {len(answers)} AI-powered answer(s)")
                    
            elif result_type == "analysis_results":
                results_summary.append(f"Completed {len(results)} analysis task(s)")
                
            elif result_type == "other_results":
                results_summary.append(f"Generated {len(results)} additional result(s)")
        
        # Create synthesis prompt
        system_prompt = """You are an expert report synthesizer. Your job is to create a comprehensive, well-structured response that combines results from multiple AI agents.

Key principles:
1. Directly answer the user's original query
2. Integrate information from all available sources coherently
3. Maintain accuracy and cite sources when relevant
4. Use clear, professional language
5. Structure the response logically
6. If there are conflicting results, acknowledge and explain them
7. Be concise but comprehensive"""
        
        user_prompt = f"""
Original Query: "{original_query}"

Available Results:
{json.dumps(organized_results, indent=2)}

Summary of Processing:
{'. '.join(results_summary)}

Output Format: {output_format}

Please synthesize these results into a comprehensive response to the original query. Focus on providing value to the user while maintaining accuracy and proper attribution.
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        verbose = context.shared_data.get('_verbose', False)
        
        try:
            synthesis = await self.call_llm(
                messages=messages,
                model=getattr(self.config, 'model', 'gpt-4o'),
                temperature=getattr(self.config, 'synthesis_temperature', 0.7),
                max_tokens=getattr(self.config, 'max_report_length', 2000),
                verbose=verbose
            )
            
            return synthesis
            
        except Exception as e:
            self.logger.error(f"LLM synthesis failed: {str(e)}")
            # Fallback to simple text concatenation
            return self._fallback_synthesis(original_query, organized_results)
    
    def _fallback_synthesis(self, original_query: str, organized_results: Dict[str, List[Any]]) -> str:
        """Fallback synthesis when LLM is unavailable."""
        response_parts = [f"Results for query: {original_query}\n"]
        
        for result_type, results in organized_results.items():
            response_parts.append(f"\n## {result_type.replace('_', ' ').title()}")
            
            for i, result in enumerate(results, 1):
                if result_type == "rag_answers" and "answer" in result:
                    response_parts.append(f"{i}. {result['answer']}")
                elif result_type == "search_results" and "results" in result:
                    doc_count = len(result["results"])
                    response_parts.append(f"{i}. Found {doc_count} relevant documents")
                else:
                    response_parts.append(f"{i}. {str(result)[:200]}...")
        
        return "\n".join(response_parts)
    
    async def _format_response(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Format response in specific output format."""
        content = parameters["content"]
        output_format = parameters.get("format", "markdown")
        metadata = parameters.get("metadata", {})
        
        if output_format.lower() == "json":
            formatted_content = json.dumps({
                "response": content,
                "metadata": metadata
            }, indent=2)
        elif output_format.lower() == "html":
            formatted_content = self._format_as_html(content, metadata)
        elif output_format.lower() == "markdown":
            formatted_content = self._format_as_markdown(content, metadata)
        else:
            formatted_content = content  # Plain text
        
        return TaskResult(
            task_id="format_response",
            status="success",
            data={
                "content": formatted_content,
                "format": output_format,
                "original_length": len(content),
                "formatted_length": len(formatted_content)
            }
        )
    
    def _format_as_markdown(self, content: str, metadata: Dict[str, Any]) -> str:
        """Format content as markdown."""
        formatted = f"# Response\n\n{content}\n\n"
        
        if metadata:
            formatted += "## Metadata\n\n"
            for key, value in metadata.items():
                formatted += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        return formatted
    
    def _format_as_html(self, content: str, metadata: Dict[str, Any]) -> str:
        """Format content as HTML."""
        html = f"""
<html>
<head><title>LocalGenius Response</title></head>
<body>
<h1>Response</h1>
<div>{content.replace(chr(10), '<br>')}</div>
"""
        
        if metadata:
            html += "<h2>Metadata</h2><ul>"
            for key, value in metadata.items():
                html += f"<li><strong>{key.replace('_', ' ').title()}</strong>: {value}</li>"
            html += "</ul>"
        
        html += "</body></html>"
        return html
    
    async def _create_summary(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Create executive summary of workflow results."""
        workflow_results = parameters["workflow_results"]
        detail_level = parameters.get("detail_level", "medium")
        
        # Extract key metrics
        total_tasks = len(context.completed_tasks) + len(context.failed_tasks)
        success_rate = len(context.completed_tasks) / max(total_tasks, 1)
        duration = (datetime.now() - context.start_time).total_seconds()
        
        summary = {
            "workflow_id": context.workflow_id,
            "original_query": context.original_query,
            "execution_summary": {
                "total_tasks": total_tasks,
                "successful_tasks": len(context.completed_tasks),
                "failed_tasks": len(context.failed_tasks),
                "success_rate": round(success_rate, 2),
                "duration_seconds": round(duration, 2)
            },
            "key_results": []
        }
        
        # Add key results based on detail level
        if detail_level in ["medium", "high"]:
            for task_result in context.completed_tasks:
                if task_result.data:
                    result_summary = self._summarize_task_result(task_result)
                    if result_summary:
                        summary["key_results"].append(result_summary)
        
        return TaskResult(
            task_id="create_summary",
            status="success",
            data=summary
        )
    
    def _summarize_task_result(self, task_result: TaskResult) -> Optional[Dict[str, Any]]:
        """Create a summary of a single task result."""
        if not task_result.data:
            return None
        
        summary = {
            "task_id": task_result.task_id,
            "status": task_result.status,
            "execution_time": task_result.execution_time
        }
        
        data = task_result.data
        
        # Summarize based on data content
        if "answer" in data:
            summary["type"] = "answer"
            summary["preview"] = data["answer"][:100] + "..." if len(data["answer"]) > 100 else data["answer"]
        elif "results" in data:
            summary["type"] = "search"
            summary["results_count"] = len(data["results"])
        elif "analysis" in data:
            summary["type"] = "analysis" 
            summary["analysis_type"] = data.get("analysis", {}).get("type", "unknown")
        else:
            summary["type"] = "other"
            summary["data_keys"] = list(data.keys())
        
        return summary
    
    async def _quality_assessment(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Assess quality and completeness of results."""
        results = parameters["results"]
        original_query = parameters["original_query"]
        
        assessment = {
            "completeness_score": 0.0,
            "quality_score": 0.0,
            "confidence_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        # Simple quality assessment heuristics
        if not results:
            assessment["issues"].append("No results generated")
            assessment["recommendations"].append("Check agent configuration and data sources")
            assessment["completeness_score"] = 0.0
        else:
            # Basic completeness check
            has_answer = any("answer" in str(r) for r in results)
            has_sources = any("sources" in str(r) for r in results) 
            
            completeness = 0.0
            if has_answer:
                completeness += 0.6
            if has_sources:
                completeness += 0.4
                
            assessment["completeness_score"] = completeness
            assessment["quality_score"] = min(completeness + 0.1, 1.0)  # Simple heuristic
            assessment["confidence_score"] = completeness * 0.8  # Conservative confidence
        
        return TaskResult(
            task_id="quality_assessment",
            status="success",
            data=assessment
        )