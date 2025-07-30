"""Search executor agent for semantic search operations."""

from typing import List, Dict, Any, Optional, Tuple
import asyncio

from ..base import BaseAgent, AgentError
from ..models import AgentCapability, TaskMessage, TaskResult, AgentWorkflowContext
from ...core.database import Database, Document
from ...core.embeddings import EmbeddingManager


class SearchAgent(BaseAgent):
    """Agent specialized in semantic search operations."""
    
    def __init__(self, name: str, settings, database: Database, embeddings: EmbeddingManager):
        super().__init__(name, settings)
        self.database = database
        self.embeddings = embeddings
    
    def get_agent_type(self) -> str:
        return "search"
    
    def get_description(self) -> str:
        return "Performs semantic search operations on indexed documents"
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="semantic_search",
                description="Perform semantic search using embeddings",
                parameters={
                    "query": {"type": "string", "required": True},
                    "limit": {"type": "integer", "default": 10},
                    "threshold": {"type": "number", "default": 0.7}
                },
                estimated_duration=5
            ),
            AgentCapability(
                name="multi_query_search",
                description="Perform multiple related searches and combine results",
                parameters={
                    "queries": {"type": "array", "required": True},
                    "limit": {"type": "integer", "default": 10},
                    "threshold": {"type": "number", "default": 0.7}
                },
                estimated_duration=15
            ),
            AgentCapability(
                name="contextual_search",
                description="Search with additional context for relevance filtering",
                parameters={
                    "query": {"type": "string", "required": True},
                    "context": {"type": "object", "required": False},
                    "limit": {"type": "integer", "default": 10},
                    "threshold": {"type": "number", "default": 0.7}
                },
                estimated_duration=8
            )
        ]
    
    async def handle_task(self, task_message: TaskMessage, context: AgentWorkflowContext) -> TaskResult:
        """Handle search-related tasks."""
        action = task_message.task.action
        parameters = task_message.task.parameters
        
        try:
            if action == "semantic_search":
                return await self._semantic_search(parameters, context)
            elif action == "multi_query_search":
                return await self._multi_query_search(parameters, context)
            elif action == "contextual_search":
                return await self._contextual_search(parameters, context)
            else:
                raise AgentError(f"Unknown search action: {action}", self.name)
        
        except Exception as e:
            return TaskResult(
                task_id=task_message.task.id,
                status="failed",
                error=str(e)
            )
    
    async def _semantic_search(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Perform basic semantic search."""
        if "query" not in parameters:
            raise AgentError("Missing required parameter: query", self.name)
        
        query = parameters["query"]
        limit = parameters.get("limit", 10)
        threshold = parameters.get("threshold", 0.7)
        
        try:
            # Generate embedding for the query
            query_embedding = await self.embeddings.embed_text(query)
            
            # Perform search
            results = await self.database.search_similar(
                query_embedding, 
                k=limit, 
                threshold=threshold
            )
            
            if not results:
                return TaskResult(
                    task_id="semantic_search",
                    status="success",
                    data={
                        "query": query,
                        "results": [],
                        "total_found": 0,
                        "message": "No matching documents found"
                    }
                )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.content,
                    "metadata": doc.metadata,
                    "source_path": doc.source_path,
                    "chunk_index": doc.chunk_index,
                    "similarity_score": float(round(score, 4))  # Convert to Python float
                })
            
            return TaskResult(
                task_id="semantic_search",
                status="success",
                data={
                    "query": query,
                    "results": formatted_results,
                    "total_found": len(results),
                    "search_parameters": {
                        "limit": limit,
                        "threshold": threshold
                    }
                },
                metadata={
                    "search_type": "semantic",
                    "embedding_model": self.embeddings.config.model
                }
            )
        
        except Exception as e:
            self.logger.error(f"Semantic search failed: {str(e)}")
            raise AgentError(f"Search operation failed: {str(e)}", self.name)
    
    async def _multi_query_search(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Perform multiple searches and combine results."""
        queries = parameters.get("queries", [])
        if not queries:
            raise AgentError("No queries provided for multi-query search", self.name)
        
        limit = parameters.get("limit", 10)
        threshold = parameters.get("threshold", 0.7)
        
        # Perform searches concurrently
        search_tasks = []
        for query in queries:
            search_params = {
                "query": query,
                "limit": limit,
                "threshold": threshold
            }
            search_tasks.append(self._semantic_search(search_params, context))
        
        search_results = await asyncio.gather(*search_tasks)
        
        # Combine and deduplicate results
        all_results = []
        seen_content = set()
        
        for search_result in search_results:
            if search_result.status == "success" and search_result.data:
                for result in search_result.data.get("results", []):
                    content_hash = hash(result["content"])
                    if content_hash not in seen_content:
                        seen_content.add(content_hash)
                        result["source_query"] = search_result.data["query"]
                        # Ensure similarity_score is a regular Python float
                        if "similarity_score" in result:
                            result["similarity_score"] = float(result["similarity_score"])
                        all_results.append(result)
        
        # Sort by similarity score
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Limit results
        final_results = all_results[:limit]
        
        return TaskResult(
            task_id="multi_query_search",
            status="success",
            data={
                "queries": queries,
                "results": final_results,
                "total_found": len(final_results),
                "total_unique_results": len(all_results),
                "search_parameters": {
                    "limit": limit,
                    "threshold": threshold
                }
            },
            metadata={
                "search_type": "multi_query",
                "query_count": len(queries)
            }
        )
    
    async def _contextual_search(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Perform search with additional context filtering."""
        query = parameters["query"]
        search_context = parameters.get("context", {})
        limit = parameters.get("limit", 10)
        threshold = parameters.get("threshold", 0.7)
        
        # First perform regular semantic search with higher limit for filtering
        search_limit = min(limit * 3, 50)  # Get more results for filtering
        
        search_params = {
            "query": query,
            "limit": search_limit,
            "threshold": threshold
        }
        
        search_result = await self._semantic_search(search_params, context)
        
        if search_result.status != "success" or not search_result.data["results"]:
            return search_result
        
        # Apply contextual filtering
        filtered_results = await self._apply_contextual_filter(
            search_result.data["results"],
            search_context,
            query
        )
        
        # Limit to requested number
        final_results = filtered_results[:limit]
        
        return TaskResult(
            task_id="contextual_search",
            status="success",
            data={
                "query": query,
                "context": search_context,
                "results": final_results,
                "total_found": len(final_results),
                "pre_filter_count": len(search_result.data["results"]),
                "search_parameters": {
                    "limit": limit,
                    "threshold": threshold
                }
            },
            metadata={
                "search_type": "contextual",
                "context_applied": bool(search_context)
            }
        )
    
    async def _apply_contextual_filter(self, 
                                     results: List[Dict[str, Any]], 
                                     search_context: Dict[str, Any],
                                     original_query: str) -> List[Dict[str, Any]]:
        """Apply contextual filtering to search results."""
        if not search_context:
            return results
        
        # Simple contextual filtering based on metadata
        filtered_results = []
        
        for result in results:
            include_result = True
            metadata = result.get("metadata", {})
            
            # Filter by file type if specified
            if "file_types" in search_context:
                file_types = search_context["file_types"]
                file_name = metadata.get("file_name", "")
                file_ext = file_name.split(".")[-1].lower() if "." in file_name else ""
                
                if file_ext not in [ft.lower() for ft in file_types]:
                    include_result = False
            
            # Filter by source path if specified
            if "source_paths" in search_context and include_result:
                allowed_paths = search_context["source_paths"]
                source_path = result.get("source_path", "")
                
                if not any(allowed_path in source_path for allowed_path in allowed_paths):
                    include_result = False
            
            # Filter by date range if specified
            if "date_range" in search_context and include_result:
                # This would require timestamp metadata
                # Implementation depends on available metadata
                pass
            
            if include_result:
                filtered_results.append(result)
        
        return filtered_results
    
    async def get_search_statistics(self) -> Dict[str, Any]:
        """Get statistics about search operations."""
        try:
            db_stats = await self.database.get_statistics()
            agent_info = self.get_agent_info()
            
            return {
                "database_stats": db_stats,
                "agent_performance": {
                    "tasks_completed": agent_info.metadata["tasks_completed"],
                    "tasks_failed": agent_info.metadata["tasks_failed"],
                    "success_rate": agent_info.metadata["success_rate"],
                    "average_execution_time": agent_info.metadata["average_execution_time"]
                },
                "capabilities": [cap.name for cap in self.get_capabilities()]
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get search statistics: {str(e)}")
            return {"error": str(e)}