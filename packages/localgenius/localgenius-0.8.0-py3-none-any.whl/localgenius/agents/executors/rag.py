"""RAG executor agent for question answering with retrieved context."""

from typing import List, Dict, Any, Optional
import json

from ..base import BaseAgent, AgentError
from ..models import AgentCapability, TaskMessage, TaskResult, AgentWorkflowContext
from ...core.rag import RAGService


class RAGAgent(BaseAgent):
    """Agent specialized in retrieval-augmented generation for question answering."""
    
    def __init__(self, name: str, settings, rag_service: RAGService):
        super().__init__(name, settings)
        self.rag_service = rag_service
    
    def get_agent_type(self) -> str:
        return "rag"
    
    def get_description(self) -> str:
        return "Generates answers to questions using retrieval-augmented generation"
    
    def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="generate_answer",
                description="Generate answer to a question using RAG",
                parameters={
                    "query": {"type": "string", "required": True},
                    "model": {"type": "string", "default": "gpt-4o"},
                    "context_items": {"type": "integer", "default": 10},
                    "similarity_threshold": {"type": "number", "default": 0.7}
                },
                estimated_duration=10
            ),
            AgentCapability(
                name="generate_with_context",
                description="Generate answer using provided context",
                parameters={
                    "query": {"type": "string", "required": True},
                    "context": {"type": "array", "required": True},
                    "model": {"type": "string", "default": "gpt-4o"}
                },
                estimated_duration=8
            ),
            AgentCapability(
                name="streaming_answer",
                description="Generate streaming answer for real-time responses",
                parameters={
                    "query": {"type": "string", "required": True},
                    "model": {"type": "string", "default": "gpt-4o"},
                    "context_items": {"type": "integer", "default": 10}
                },
                estimated_duration=12
            ),
            AgentCapability(
                name="analyze_context_relevance",
                description="Analyze relevance of context to the query",
                parameters={
                    "query": {"type": "string", "required": True},
                    "context": {"type": "array", "required": True}
                },
                estimated_duration=5
            )
        ]
    
    async def handle_task(self, task_message: TaskMessage, context: AgentWorkflowContext) -> TaskResult:
        """Handle RAG-related tasks."""
        action = task_message.task.action
        parameters = task_message.task.parameters
        
        try:
            if action == "generate_answer":
                return await self._generate_answer(parameters, context)
            elif action == "generate_with_context":
                return await self._generate_with_context(parameters, context)
            elif action == "streaming_answer":
                return await self._streaming_answer(parameters, context)
            elif action == "analyze_context_relevance":
                return await self._analyze_context_relevance(parameters, context)
            else:
                raise AgentError(f"Unknown RAG action: {action}", self.name)
        
        except Exception as e:
            return TaskResult(
                task_id=task_message.task.id,
                status="failed",
                error=str(e)
            )
    
    async def _generate_answer(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Generate answer using standard RAG pipeline."""
        if "query" not in parameters:
            raise AgentError("Missing required parameter: query", self.name)
        
        query = parameters["query"]
        model = parameters.get("model", "gpt-4o")
        max_context_items = parameters.get("context_items", 10)
        similarity_threshold = parameters.get("similarity_threshold", 0.7)
        verbose = context.shared_data.get('_verbose', False)
        
        try:
            # Use the RAG service to generate answer
            result = await self.rag_service.ask(
                query=query,
                model=model,
                max_context_items=max_context_items,
                similarity_threshold=similarity_threshold
            )
            
            # Check if RAG service returned an error
            if "error" in result:
                return TaskResult(
                    task_id="generate_answer",
                    status="failed",
                    error=result["error"]
                )
            
            return TaskResult(
                task_id="generate_answer",
                status="success",
                data={
                    "query": result["query"],
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "model": result["model"],
                    "context_used": result.get("context_used", 0),
                    "tokens_used": result.get("tokens_used"),
                    "generation_metadata": {
                        "max_context_items": max_context_items,
                        "similarity_threshold": similarity_threshold
                    }
                },
                metadata={
                    "rag_type": "standard",
                    "llm_model": model
                }
            )
        
        except Exception as e:
            self.logger.error(f"RAG answer generation failed: {str(e)}")
            raise AgentError(f"Answer generation failed: {str(e)}", self.name)
    
    async def _generate_with_context(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Generate answer using provided context instead of retrieving it."""
        query = parameters["query"]
        provided_context = parameters["context"]
        model = parameters.get("model", "gpt-4o")
        
        # Extract search results from context if they come from search agent
        if isinstance(provided_context, list) and provided_context:
            # Check if context contains search results
            context_text_parts = []
            sources = []
            
            for item in provided_context:
                if isinstance(item, dict):
                    if "content" in item and "metadata" in item:
                        # This looks like a search result
                        source_name = item["metadata"].get("file_name", "Unknown")
                        context_text_parts.append(f"[Source: {source_name}]\n{item['content']}")
                        sources.append({
                            "file": item["metadata"].get("file_path", item.get("source_path", "Unknown")),
                            "chunk": item.get("chunk_index", 0),
                            "similarity": float(item.get("similarity_score", 1.0))
                        })
                    else:
                        # Plain text context
                        context_text_parts.append(str(item))
            
            formatted_context = "\n\n---\n\n".join(context_text_parts)
        else:
            formatted_context = str(provided_context)
            sources = []
        
        # Create prompt using RAG service templates
        system_prompt = self.settings.prompts.system_prompt
        user_content = self.settings.prompts.user_prompt_template.format(
            context=formatted_context,
            query=query
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        verbose = context.shared_data.get('_verbose', False)
        
        try:
            # Generate response using LLM
            answer = await self.call_llm(
                messages=messages,
                model=model,
                temperature=self.settings.prompts.temperature,
                max_tokens=self.settings.prompts.max_tokens,
                verbose=verbose
            )
            
            return TaskResult(
                task_id="generate_with_context",
                status="success",
                data={
                    "query": query,
                    "answer": answer,
                    "sources": sources,
                    "model": model,
                    "context_provided": len(provided_context) if isinstance(provided_context, list) else 1,
                    "context_length": len(formatted_context)
                },
                metadata={
                    "rag_type": "with_context",
                    "llm_model": model
                }
            )
        
        except Exception as e:
            self.logger.error(f"Context-based answer generation failed: {str(e)}")
            raise AgentError(f"Answer generation with context failed: {str(e)}", self.name)
    
    async def _streaming_answer(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Generate streaming answer (collect all chunks for now)."""
        query = parameters["query"]
        model = parameters.get("model", "gpt-4o")
        max_context_items = parameters.get("context_items", 10)
        
        try:
            # Use streaming RAG service
            response_chunks = []
            sources = []
            
            async for chunk in self.rag_service.ask_with_streaming(
                query=query,
                model=model,
                max_context_items=max_context_items
            ):
                if chunk["type"] == "sources":
                    sources = chunk["content"]
                elif chunk["type"] == "content":
                    response_chunks.append(chunk["content"])
                elif chunk["type"] == "error":
                    return TaskResult(
                        task_id="streaming_answer",
                        status="failed",
                        error=chunk["content"]
                    )
            
            full_answer = "".join(response_chunks)
            
            return TaskResult(
                task_id="streaming_answer",
                status="success",
                data={
                    "query": query,
                    "answer": full_answer,
                    "sources": sources,
                    "model": model,
                    "streaming_chunks": len(response_chunks),
                    "generation_metadata": {
                        "max_context_items": max_context_items,
                        "streaming": True
                    }
                },
                metadata={
                    "rag_type": "streaming",
                    "llm_model": model
                }
            )
        
        except Exception as e:
            self.logger.error(f"Streaming answer generation failed: {str(e)}")
            raise AgentError(f"Streaming answer generation failed: {str(e)}", self.name)
    
    async def _analyze_context_relevance(self, parameters: Dict[str, Any], context: AgentWorkflowContext) -> TaskResult:
        """Analyze how relevant the provided context is to the query."""
        query = parameters["query"]
        provided_context = parameters["context"]
        
        # Create analysis prompt
        context_text = json.dumps(provided_context, indent=2)
        
        analysis_prompt = f"""
Analyze the relevance of the provided context to the user's query.

Query: "{query}"

Context:
{context_text}

Provide analysis in JSON format:
{{
    "overall_relevance": "high|medium|low",
    "relevance_score": 0.0-1.0,
    "relevant_pieces": ["list of relevant context pieces"],
    "missing_information": ["what information is missing to fully answer the query"],
    "confidence": 0.0-1.0,
    "reasoning": "explanation of the analysis"
}}
"""
        
        messages = [
            {"role": "system", "content": "You are an expert at analyzing context relevance for question answering."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        try:
            response = await self.call_llm(messages, temperature=0.3)
            
            # Try to parse JSON response
            try:
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback to text response if JSON parsing fails
                analysis = {
                    "overall_relevance": "medium",
                    "relevance_score": 0.5,
                    "reasoning": response,
                    "json_parse_error": True
                }
            
            return TaskResult(
                task_id="analyze_context_relevance",
                status="success",
                data={
                    "query": query,
                    "analysis": analysis,
                    "context_items": len(provided_context) if isinstance(provided_context, list) else 1
                },
                metadata={
                    "analysis_type": "context_relevance"
                }
            )
        
        except Exception as e:
            self.logger.error(f"Context relevance analysis failed: {str(e)}")
            raise AgentError(f"Context analysis failed: {str(e)}", self.name)
    
    async def get_rag_statistics(self) -> Dict[str, Any]:
        """Get statistics about RAG operations."""
        try:
            agent_info = self.get_agent_info()
            
            return {
                "agent_performance": {
                    "tasks_completed": agent_info.metadata["tasks_completed"],
                    "tasks_failed": agent_info.metadata["tasks_failed"],
                    "success_rate": agent_info.metadata["success_rate"],
                    "average_execution_time": agent_info.metadata["average_execution_time"]
                },
                "capabilities": [cap.name for cap in self.get_capabilities()],
                "rag_service_available": self.rag_service is not None,
                "default_model": getattr(self.config, 'model', 'gpt-4o'),
                "settings": {
                    "temperature": self.settings.prompts.temperature,
                    "max_tokens": self.settings.prompts.max_tokens,
                    "system_prompt_length": len(self.settings.prompts.system_prompt)
                }
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get RAG statistics: {str(e)}")
            return {"error": str(e)}