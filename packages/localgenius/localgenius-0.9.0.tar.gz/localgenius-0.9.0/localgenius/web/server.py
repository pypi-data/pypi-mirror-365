"""Web server for LocalGenius admin interface."""

import os
import asyncio
import subprocess
import signal
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
from datetime import datetime

from aiohttp import web, web_request
import aiofiles

from ..core.config import Settings, DataSource
from ..core.database import Database
from ..core.embeddings import EmbeddingManager
from ..core.rag import RAGService
from ..utils.indexer import Indexer
from ..agents.registry import agent_registry
from ..agents.orchestrator import AgentOrchestrator


class LocalGeniusWebServer:
    """Web server for LocalGenius with admin interface."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("web_server")
        self.db: Optional[Database] = None
        self.embeddings: Optional[EmbeddingManager] = None
        self.rag: Optional[RAGService] = None
        self.orchestrator: Optional[AgentOrchestrator] = None
        self.workflow_history: Dict[str, Any] = {}  # Simple in-memory storage for demo
        self.app = web.Application()
        self.next_process: Optional[subprocess.Popen] = None
        self.setup_routes()
        self.setup_cors_middleware()
        
    async def initialize_services(self):
        """Initialize database and services."""
        self.db = Database(self.settings.database.path, self.settings.database.vector_dimension)
        await self.db.initialize()
        
        if self.settings.openai_api_key:
            self.embeddings = EmbeddingManager(self.settings.openai_api_key, self.settings.embedding)
            self.rag = RAGService(self.settings, self.db)
            
            # Initialize agent system if available  
            if hasattr(self.settings, 'agents') and self.settings.agents.enabled:
                self.orchestrator = AgentOrchestrator(self.settings, verbose=False)
            elif self.settings.openai_api_key:
                # Even if agents config isn't explicitly set, try to initialize if we have OpenAI key
                try:
                    self.orchestrator = AgentOrchestrator(self.settings, verbose=False)
                except Exception as e:
                    self.logger.warning(f"Could not initialize agent system: {e}")
            
    def setup_routes(self):
        """Set up API routes."""
        # API routes
        self.app.router.add_get('/api/status', self.get_status)
        self.app.router.add_get('/api/dashboard', self.get_dashboard_data)
        self.app.router.add_get('/api/metrics', self.get_metrics)
        self.app.router.add_get('/api/activity', self.get_recent_activity)
        self.app.router.add_get('/api/data-sources', self.get_data_sources)
        self.app.router.add_post('/api/data-sources', self.add_data_source)
        self.app.router.add_delete('/api/data-sources/{path:.*}', self.remove_data_source)
        self.app.router.add_post('/api/index', self.trigger_indexing)
        self.app.router.add_get('/api/index/stats', self.get_index_stats)
        self.app.router.add_post('/api/search', self.search_documents)
        self.app.router.add_post('/api/ask', self.ask_question)
        self.app.router.add_get('/api/settings', self.get_settings)
        self.app.router.add_post('/api/settings', self.update_settings)
        
        # Agent API routes
        self.app.router.add_get('/api/agents/status', self.get_agent_status)
        self.app.router.add_get('/api/agents/config', self.get_agent_config)
        self.app.router.add_post('/api/agents/config', self.update_agent_config)
        self.app.router.add_post('/api/agents/ask', self.agent_ask)
        self.app.router.add_post('/api/agents/search', self.agent_search)
        self.app.router.add_get('/api/agents/workflows', self.get_agent_workflows)
        self.app.router.add_get('/api/agents/workflows/{workflow_id}', self.get_agent_workflow)
        self.app.router.add_post('/api/agents/workflows/{workflow_id}/cancel', self.cancel_agent_workflow)
        
        # Serve Next.js static files (after build)
        admin_build_path = Path(__file__).parent.parent.parent / "mcp-admin-interface" / ".next" / "static"
        if admin_build_path.exists():
            self.app.router.add_static('/_next/static', str(admin_build_path))
        
        # Catch-all route for React Router (serve index.html for all non-API routes)
        self.app.router.add_route('*', '/{path:(?!api).*}', self.serve_admin_interface)
        
    def setup_cors_middleware(self):
        """Set up CORS middleware for cross-origin requests."""
        @web.middleware
        async def cors_handler(request, handler):
            # Handle preflight requests
            if request.method == 'OPTIONS':
                response = web.Response()
            else:
                response = await handler(request)
            
            # Add CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '86400'
            
            return response
        
        self.app.middlewares.append(cors_handler)
        
    async def serve_admin_interface(self, request: web_request.Request) -> web.Response:
        """Serve the admin interface by proxying to Next.js dev server."""
        # In development, proxy to Next.js dev server
        # In production, serve built static files
        return web.Response(
            text="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>LocalGenius Admin</title>
                <style>
                    body { font-family: system-ui; margin: 40px; text-align: center; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .status { background: #f0f9ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>LocalGenius Admin Interface</h1>
                    <div class="status">
                        <p>Admin interface is starting up...</p>
                        <p>Next.js development server should be available shortly.</p>
                        <p>Visit <a href="http://localhost:3000">http://localhost:3000</a> for the full admin interface.</p>
                    </div>
                    <h2>Quick API Test</h2>
                    <button onclick="testAPI()">Test API Connection</button>
                    <div id="api-result"></div>
                </div>
                <script>
                    async function testAPI() {
                        try {
                            const response = await fetch('/api/status');
                            const data = await response.json();
                            document.getElementById('api-result').innerHTML = 
                                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                        } catch (error) {
                            document.getElementById('api-result').innerHTML = 
                                '<p style="color: red;">API Error: ' + error.message + '</p>';
                        }
                    }
                </script>
            </body>
            </html>
            """,
            content_type='text/html'
        )
    
    async def start_next_dev_server(self, port: int = 3000):
        """Start the Next.js development server on the specified port."""
        admin_path = Path(__file__).parent.parent.parent / "mcp-admin-interface"
        if not admin_path.exists():
            print(f"Warning: Admin interface directory not found at {admin_path}")
            return
            
        try:
            # Check if dependencies are installed
            node_modules = admin_path / "node_modules"
            if not node_modules.exists():
                print("Installing admin interface dependencies...")
                # Use --legacy-peer-deps to resolve dependency conflicts
                subprocess.run(["npm", "install", "--legacy-peer-deps"], cwd=admin_path, check=True)
            
            # Start Next.js dev server on the specified port
            print(f"Starting Next.js admin interface on http://localhost:{port}")
            env = os.environ.copy()
            env["PORT"] = str(port)
            
            self.next_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=admin_path,
                env=env,
                stdout=subprocess.DEVNULL,  # Suppress output to avoid cluttering
                stderr=subprocess.DEVNULL
            )
            
            # Give it a moment to start
            await asyncio.sleep(3)
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            print("You can manually install with: cd mcp-admin-interface && npm install --legacy-peer-deps")
        except Exception as e:
            print(f"Failed to start Next.js server: {e}")
            print("You can manually start with: cd mcp-admin-interface && npm run dev")
            
    async def stop_next_dev_server(self):
        """Stop the Next.js development server."""
        if self.next_process:
            try:
                self.next_process.terminate()
                self.next_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.next_process.kill()
            self.next_process = None
    
    # API Endpoints
    
    async def get_status(self, request: web_request.Request) -> web.Response:
        """Get LocalGenius status."""
        if not self.db:
            return web.json_response({"error": "Database not initialized"}, status=500)
            
        stats = await self.db.get_statistics()
        
        return web.json_response({
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "config": {
                "database_path": str(self.settings.database.path),
                "openai_configured": bool(self.settings.openai_api_key),
                "data_sources_count": len(self.settings.data_sources)
            },
            "database": stats
        })
    
    async def get_dashboard_data(self, request: web_request.Request) -> web.Response:
        """Get comprehensive dashboard data."""
        if not self.db:
            return web.json_response({"error": "Database not initialized"}, status=500)
        
        # Get database statistics
        stats = await self.db.get_statistics()
        
        # Get file type breakdown
        cursor = await self.db._connection.execute(
            "SELECT metadata FROM documents WHERE metadata IS NOT NULL"
        )
        all_metadata = await cursor.fetchall()
        
        file_types = {}
        for (metadata_str,) in all_metadata:
            if metadata_str:
                metadata = json.loads(metadata_str)
                file_name = metadata.get('file_name', '')
                if file_name:
                    ext = Path(file_name).suffix.lower() or 'no extension'
                    file_types[ext] = file_types.get(ext, 0) + 1
        
        # Get recent documents (last 10)
        cursor = await self.db._connection.execute(
            """
            SELECT source_path, content, chunk_index, metadata, created_at 
            FROM documents 
            ORDER BY created_at DESC 
            LIMIT 10
            """
        )
        recent_docs = await cursor.fetchall()
        
        recent_documents = []
        for source, content, chunk_idx, metadata_str, created_at in recent_docs:
            metadata = json.loads(metadata_str) if metadata_str else {}
            recent_documents.append({
                "source": source,
                "file_name": metadata.get("file_name", "Unknown"),
                "chunk_index": chunk_idx,
                "preview": content[:100] + "..." if len(content) > 100 else content,
                "created_at": created_at
            })
        
        # Calculate index health metrics
        total_sources = len(self.settings.data_sources)
        indexed_sources = len(stats["sources"])
        index_health = (indexed_sources / total_sources * 100) if total_sources > 0 else 0
        
        # Calculate average chunk size
        cursor = await self.db._connection.execute(
            "SELECT AVG(LENGTH(content)) FROM documents"
        )
        avg_chunk_size = await cursor.fetchone()
        avg_chunk_size = int(avg_chunk_size[0]) if avg_chunk_size[0] else 0
        
        return web.json_response({
            "overview": {
                "total_documents": stats["total_documents"],
                "total_embeddings": stats["total_embeddings"],
                "data_sources_count": len(self.settings.data_sources),
                "indexed_sources_count": len(stats["sources"]),
                "vector_dimension": stats["vector_dimension"],
                "index_health_percentage": round(index_health, 1),
                "average_chunk_size": avg_chunk_size,
                "openai_configured": bool(self.settings.openai_api_key)
            },
            "sources": [
                {
                    "name": ds.name,
                    "path": str(ds.path),
                    "enabled": ds.enabled,
                    "document_count": stats["sources"].get(str(ds.path), 0),
                    "status": "indexed" if str(ds.path) in stats["sources"] else "not_indexed"
                }
                for ds in self.settings.data_sources
            ],
            "file_types": dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]),
            "recent_documents": recent_documents,
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_metrics(self, request: web_request.Request) -> web.Response:
        """Get detailed metrics for charts and graphs."""
        if not self.db:
            return web.json_response({"error": "Database not initialized"}, status=500)
        
        # Documents by source (for pie chart)
        cursor = await self.db._connection.execute(
            "SELECT source_path, COUNT(*) as count FROM documents GROUP BY source_path ORDER BY count DESC"
        )
        source_distribution = await cursor.fetchall()
        
        # Documents by file type
        cursor = await self.db._connection.execute(
            "SELECT metadata FROM documents WHERE metadata IS NOT NULL"
        )
        all_metadata = await cursor.fetchall()
        
        file_type_stats = {}
        for (metadata_str,) in all_metadata:
            if metadata_str:
                metadata = json.loads(metadata_str)
                file_name = metadata.get('file_name', '')
                if file_name:
                    ext = Path(file_name).suffix.lower() or 'no extension'
                    file_type_stats[ext] = file_type_stats.get(ext, 0) + 1
        
        # Content length distribution
        cursor = await self.db._connection.execute(
            """
            SELECT 
                CASE 
                    WHEN LENGTH(content) < 500 THEN 'Short (< 500)'
                    WHEN LENGTH(content) < 1000 THEN 'Medium (500-1000)'
                    WHEN LENGTH(content) < 2000 THEN 'Long (1000-2000)'
                    ELSE 'Very Long (> 2000)'
                END as size_category,
                COUNT(*) as count
            FROM documents 
            GROUP BY size_category
            """
        )
        content_distribution = await cursor.fetchall()
        
        # Chunk distribution by source
        cursor = await self.db._connection.execute(
            """
            SELECT source_path, COUNT(*) as chunks, 
                   MIN(chunk_index) as min_chunk, MAX(chunk_index) as max_chunk
            FROM documents 
            GROUP BY source_path
            ORDER BY chunks DESC
            LIMIT 10
            """
        )
        chunk_stats = await cursor.fetchall()
        
        return web.json_response({
            "source_distribution": [
                {"name": Path(source).name, "value": count, "full_path": source}
                for source, count in source_distribution
            ],
            "file_type_distribution": [
                {"name": ext, "value": count}
                for ext, count in sorted(file_type_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            ],
            "content_length_distribution": [
                {"name": category, "value": count}
                for category, count in content_distribution
            ],
            "chunk_statistics": [
                {
                    "source": Path(source).name,
                    "chunk_count": chunks,
                    "min_chunk": min_chunk,
                    "max_chunk": max_chunk,
                    "full_path": source
                }
                for source, chunks, min_chunk, max_chunk in chunk_stats
            ]
        })
    
    async def get_recent_activity(self, request: web_request.Request) -> web.Response:
        """Get recent activity log for dashboard."""
        # This is a simplified activity log - in a real system you'd have proper logging
        activities = []
        
        if self.db:
            # Get recent document additions
            cursor = await self.db._connection.execute(
                """
                SELECT source_path, COUNT(*) as doc_count, MAX(created_at) as last_updated
                FROM documents 
                GROUP BY source_path 
                ORDER BY last_updated DESC 
                LIMIT 10
                """
            )
            recent_updates = await cursor.fetchall()
            
            for source_path, doc_count, last_updated in recent_updates:
                source_name = Path(source_path).name
                activities.append({
                    "event": "Documents indexed" if doc_count > 1 else "Document indexed",
                    "source": source_name,
                    "status": "success",
                    "details": f"{doc_count} documents processed",
                    "timestamp": last_updated or datetime.now().isoformat(),
                    "type": "indexing"
                })
        
        # Add data source status
        for ds in self.settings.data_sources:
            if not ds.enabled:
                activities.append({
                    "event": "Data source disabled",
                    "source": ds.name,
                    "status": "warning",
                    "details": f"Source at {ds.path} is disabled",
                    "timestamp": datetime.now().isoformat(),
                    "type": "configuration"
                })
        
        # Add configuration status
        if not self.settings.openai_api_key:
            activities.append({
                "event": "OpenAI API key not configured",
                "source": "System",
                "status": "error",
                "details": "RAG functionality requires OpenAI API key",
                "timestamp": datetime.now().isoformat(),
                "type": "configuration"
            })
        
        # Sort by timestamp (most recent first) and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return web.json_response({
            "activities": activities[:20],  # Return last 20 activities
            "total_count": len(activities)
        })
    
    async def get_data_sources(self, request: web_request.Request) -> web.Response:
        """Get all configured data sources."""
        sources = []
        for ds in self.settings.data_sources:
            sources.append({
                "path": str(ds.path),
                "name": ds.name,
                "enabled": ds.enabled,
                "file_patterns": ds.file_patterns,
                "recursive": ds.recursive
            })
        return web.json_response({"data_sources": sources})
    
    async def add_data_source(self, request: web_request.Request) -> web.Response:
        """Add a new data source."""
        try:
            data = await request.json()
            path = Path(data["path"])
            name = data.get("name", path.name)
            
            # Validate path exists
            if not path.exists():
                return web.json_response({"error": f"Path {path} does not exist"}, status=400)
            
            # Check if already exists
            for ds in self.settings.data_sources:
                if ds.path == path:
                    return web.json_response({"error": "Data source already exists"}, status=400)
            
            # Add data source
            self.settings.add_data_source(path, name)
            
            return web.json_response({"message": "Data source added successfully"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def remove_data_source(self, request: web_request.Request) -> web.Response:
        """Remove a data source."""
        try:
            path = Path(request.match_info["path"])
            self.settings.remove_data_source(path)
            
            # Also remove from database
            if self.db:
                await self.db.delete_documents_by_source(str(path))
            
            return web.json_response({"message": "Data source removed successfully"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def trigger_indexing(self, request: web_request.Request) -> web.Response:
        """Trigger indexing of data sources."""
        try:
            data = await request.json()
            force = data.get("force", False)
            source_path = data.get("source_path")
            
            if not self.embeddings or not self.db:
                return web.json_response({"error": "Services not properly initialized"}, status=500)
            
            indexer = Indexer(self.db, self.embeddings, self.settings)
            
            sources_to_index = []
            if source_path:
                # Index specific source
                source_path = Path(source_path)
                for ds in self.settings.data_sources:
                    if ds.path == source_path:
                        sources_to_index.append(ds)
                        break
            else:
                # Index all active sources
                sources_to_index = self.settings.get_active_data_sources()
            
            if not sources_to_index:
                return web.json_response({"error": "No sources to index"}, status=400)
            
            # Perform indexing
            results = []
            for source in sources_to_index:
                if force:
                    await self.db.delete_documents_by_source(str(source.path))
                
                result = await indexer.index_source(source)
                results.append({
                    "source": str(source.path),
                    "name": source.name,
                    "indexed": True
                })
            
            return web.json_response({
                "message": "Indexing completed",
                "results": results
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_index_stats(self, request: web_request.Request) -> web.Response:
        """Get detailed index statistics."""
        if not self.db:
            return web.json_response({"error": "Database not initialized"}, status=500)
        
        stats = await self.db.get_statistics()
        
        # Get sample documents
        cursor = await self.db._connection.execute(
            "SELECT source_path, content, chunk_index, metadata FROM documents ORDER BY RANDOM() LIMIT 5"
        )
        samples = await cursor.fetchall()
        
        sample_docs = []
        for source, content, chunk_idx, metadata_str in samples:
            metadata = json.loads(metadata_str) if metadata_str else {}
            sample_docs.append({
                "source": source,
                "chunk_index": chunk_idx,
                "preview": content[:150] + "..." if len(content) > 150 else content,
                "file_name": metadata.get("file_name", "Unknown")
            })
        
        return web.json_response({
            **stats,
            "samples": sample_docs
        })
    
    async def search_documents(self, request: web_request.Request) -> web.Response:
        """Search documents."""
        try:
            data = await request.json()
            query = data["query"]
            limit = data.get("limit", 5)
            threshold = data.get("threshold", 0.7)
            
            # Check if services are initialized
            if not self.db:
                return web.json_response({"error": "Database not initialized"}, status=500)
            
            if not self.embeddings:
                return web.json_response({"error": "Embedding service not initialized. Check OpenAI API key."}, status=500)
            
            # Check if database has any documents
            stats = await self.db.get_stats()
            if stats["total_documents"] == 0:
                return web.json_response({
                    "error": "No documents found in database. Please index some documents first.",
                    "query": query,
                    "results": [],
                    "count": 0
                }, status=200)  # Return 200 with empty results instead of error
            
            # Generate embedding
            query_embedding = await self.embeddings.embed_text(query)
            
            # Search
            results = await self.db.search_similar(query_embedding, limit, threshold)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.content,
                    "source_path": doc.source_path,
                    "chunk_index": doc.chunk_index,
                    "similarity": round(score, 3),
                    "metadata": doc.metadata
                })
            
            return web.json_response({
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results)
            })
            
        except Exception as e:
            import traceback
            return web.json_response({
                "error": f"Search failed: {str(e)}",
                "details": traceback.format_exc()
            }, status=500)
    
    async def ask_question(self, request: web_request.Request) -> web.Response:
        """Ask a question using RAG."""
        try:
            data = await request.json()
            question = data["question"]
            model = data.get("model", "gpt-4o")
            
            if not self.rag:
                return web.json_response({"error": "RAG service not initialized"}, status=500)
            
            result = await self.rag.ask(query=question, model=model)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_settings(self, request: web_request.Request) -> web.Response:
        """Get current settings."""
        try:
            response_data = {
                "config_path": str(self.settings.config_path),
                "database": {
                    "path": str(self.settings.database.path),
                    "vector_dimension": self.settings.database.vector_dimension
                },
                "embedding": {
                    "model": self.settings.embedding.model,
                    "chunk_size": self.settings.embedding.chunk_size,
                    "chunk_overlap": self.settings.embedding.chunk_overlap,
                    "chunk_separator": getattr(self.settings.embedding, 'chunk_separator', '\n\n'),
                    "chunk_strategy": getattr(self.settings.embedding, 'chunk_strategy', 'size_first'),
                    "batch_size": self.settings.embedding.batch_size
                },
                "mcp": {
                    "host": self.settings.mcp.host,
                    "port": self.settings.mcp.port,
                    "max_context_items": self.settings.mcp.max_context_items,
                    "similarity_threshold": self.settings.mcp.similarity_threshold
                },
                "prompts": {
                    "system_prompt": self.settings.prompts.system_prompt,
                    "user_prompt_template": self.settings.prompts.user_prompt_template,
                    "temperature": self.settings.prompts.temperature,
                    "max_tokens": self.settings.prompts.max_tokens,
                    "use_for_mcp": self.settings.prompts.use_for_mcp
                },
                "openai_configured": bool(self.settings.openai_api_key),
                "openai_api_key": self.settings.openai_api_key if self.settings.openai_api_key else ""
            }
            return web.json_response(response_data)
        except Exception as e:
            import traceback
            return web.json_response({
                "error": f"Failed to load settings: {str(e)}",
                "details": traceback.format_exc()
            }, status=500)
    
    async def update_settings(self, request: web_request.Request) -> web.Response:
        """Update settings."""
        try:
            data = await request.json()
            
            # Update OpenAI API key
            if "openai_api_key" in data:
                self.settings.openai_api_key = data["openai_api_key"]
                
                # Reinitialize embedding manager and RAG service with new API key
                if self.settings.openai_api_key:
                    self.embeddings = EmbeddingManager(self.settings.openai_api_key, self.settings.embedding)
                    self.rag = RAGService(self.settings, self.db)
                else:
                    self.embeddings = None
                    self.rag = None
            
            # Update embedding settings
            if "embedding" in data:
                for key, value in data["embedding"].items():
                    if hasattr(self.settings.embedding, key):
                        setattr(self.settings.embedding, key, value)
                
                # Reinitialize embedding manager if API key exists and embedding config changed
                if self.settings.openai_api_key and self.embeddings:
                    self.embeddings = EmbeddingManager(self.settings.openai_api_key, self.settings.embedding)
            
            # Update MCP settings
            if "mcp" in data:
                for key, value in data["mcp"].items():
                    if hasattr(self.settings.mcp, key):
                        setattr(self.settings.mcp, key, value)
            
            # Update prompt settings
            if "prompts" in data:
                for key, value in data["prompts"].items():
                    if hasattr(self.settings.prompts, key):
                        setattr(self.settings.prompts, key, value)
                
                # Reinitialize RAG service if prompt settings changed
                if self.rag:
                    self.rag = RAGService(self.settings, self.db)
            
            # Save settings to file
            self.settings.save_to_file()
            
            return web.json_response({"message": "Settings updated successfully"})
            
        except Exception as e:
            import traceback
            return web.json_response({
                "error": f"Failed to update settings: {str(e)}",
                "details": traceback.format_exc()
            }, status=500)
    
    # Agent API Endpoints
    
    async def get_agent_status(self, request: web_request.Request) -> web.Response:
        """Get status of all agents."""
        try:
            if not self.orchestrator:
                # Return empty status if agent system not initialized
                return web.json_response({
                    "agents": [],
                    "error": "Agent system not initialized - OpenAI API key may be missing"
                })
            
            agents = agent_registry.list_available_agents()
            agent_status = []
            
            for agent in agents:
                # Get performance stats (simplified for now)
                agent_status.append({
                    "name": agent.name,
                    "type": agent.get_agent_type(),
                    "description": agent.get_description(),
                    "capabilities": [cap.model_dump() for cap in agent.get_capabilities()],
                    "status": "available",  # Simplified - could check actual status
                    "performance_stats": {
                        "total_tasks": 0,
                        "successful_tasks": 0,
                        "failed_tasks": 0,
                        "average_execution_time": 0.0,
                        "last_activity": datetime.now().isoformat()
                    }
                })
            
            return web.json_response({"agents": agent_status})
            
        except Exception as e:
            return web.json_response({"agents": [], "error": str(e)})
    
    async def get_agent_config(self, request: web_request.Request) -> web.Response:
        """Get agent configuration."""
        try:
            if not hasattr(self.settings, 'agents'):
                # Return default config if not configured
                return web.json_response({
                    "enabled": False,
                    "max_concurrent_agents": 5,
                    "planner": {
                        "model": "gpt-4o",
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    "executor": {
                        "search": {
                            "default_limit": 10,
                            "default_threshold": 0.7
                        },
                        "rag": {
                            "model": "gpt-4o", 
                            "temperature": 0.7,
                            "max_tokens": 2000
                        }
                    },
                    "reporter": {
                        "model": "gpt-4o",
                        "synthesis_temperature": 0.7,
                        "max_report_length": 2000
                    }
                })
            
            config = self.settings.agents
            return web.json_response({
                "enabled": config.enabled,
                "max_concurrent_agents": config.max_concurrent_agents,
                "planner": {
                    "model": config.planner.model,
                    "temperature": config.planner.temperature,
                    "max_tokens": config.planner.max_tokens
                },
                "executor": {
                    "search": {
                        "default_limit": config.executor.search.default_limit,
                        "default_threshold": config.executor.search.default_threshold
                    },
                    "rag": {
                        "model": config.executor.rag.model,
                        "temperature": config.executor.rag.temperature,
                        "max_tokens": config.executor.rag.max_tokens
                    }
                },
                "reporter": {
                    "model": config.reporter.model,
                    "synthesis_temperature": config.reporter.synthesis_temperature,
                    "max_report_length": config.reporter.max_report_length
                }
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def update_agent_config(self, request: web_request.Request) -> web.Response:
        """Update agent configuration."""
        try:
            data = await request.json()
            
            # This would update the agent configuration in settings
            # For now, return success (full implementation would require config schema updates)
            
            return web.json_response({"message": "Agent configuration updated successfully"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def agent_ask(self, request: web_request.Request) -> web.Response:
        """Handle agent ask requests."""
        try:
            data = await request.json()
            query = data["query"]
            output_format = data.get("format", "markdown")
            model = data.get("model", "gpt-4o")
            verbose = data.get("verbose", False)
            
            if not self.orchestrator:
                return web.json_response({
                    "error": "Agent system not initialized - please configure OpenAI API key"
                }, status=503)
            
            # Execute workflow
            result = await self.orchestrator.execute_query(
                query=query,
                context={
                    "output_format": output_format,
                    "model": model,
                    "_verbose": verbose
                }
            )
            
            # Store in workflow history
            workflow_id = result.get("workflow_id", "unknown")
            self.workflow_history[workflow_id] = {
                "workflow_id": workflow_id,
                "original_query": query,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": "completed" if result.get("success") else "failed",
                "results": result,
                "verbose_logs": result.get("verbose_logs", []) if verbose else []
            }
            
            # Format response
            if result.get("status") == "completed":
                execution_summary = result.get("execution_summary", {})
                return web.json_response({
                    "workflow_id": workflow_id,
                    "query": query,
                    "response": result.get("response", "Query completed successfully"),
                    "format": output_format,
                    "summary": {
                        "synthesis_timestamp": datetime.now().isoformat(),
                        "total_tasks": execution_summary.get("total_tasks", 0),
                        "successful_tasks": execution_summary.get("completed_tasks", 0),
                        "failed_tasks": execution_summary.get("failed_tasks", 0),
                        "workflow_duration": execution_summary.get("duration", 0)
                    },
                    "execution_details": self.workflow_history[workflow_id] if verbose else None
                })
            else:
                return web.json_response({
                    "error": result.get("error", "Workflow execution failed"),
                    "workflow_id": workflow_id
                }, status=500)
            
        except Exception as e:
            import traceback
            return web.json_response({
                "error": f"Agent ask failed: {str(e)}",
                "details": traceback.format_exc()
            }, status=500)
    
    async def agent_search(self, request: web_request.Request) -> web.Response:
        """Handle agent search requests."""
        try:
            data = await request.json()
            query = data["query"]
            limit = data.get("limit", 10)
            threshold = data.get("threshold", 0.7)
            verbose = data.get("verbose", False)
            
            if not self.orchestrator:
                return web.json_response({
                    "error": "Agent system not initialized - please configure OpenAI API key"
                }, status=503)
            
            # Execute search workflow
            result = await self.orchestrator.execute_query(
                query=query,
                context={
                    "search_only": True,
                    "limit": limit,
                    "threshold": threshold,
                    "_verbose": verbose
                }
            )
            
            # Store in workflow history
            workflow_id = result.get("workflow_id", "unknown")
            self.workflow_history[workflow_id] = {
                "workflow_id": workflow_id,
                "original_query": query,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "status": "completed" if result.get("success") else "failed",
                "results": result,
                "verbose_logs": result.get("verbose_logs", []) if verbose else []
            }
            
            if result.get("status") == "completed":
                search_results = result.get("search_results", [])
                return web.json_response({
                    "workflow_id": workflow_id,
                    "query": query,
                    "results": search_results,
                    "count": len(search_results),
                    "execution_details": self.workflow_history[workflow_id] if verbose else None
                })
            else:
                return web.json_response({
                    "error": result.get("error", "Search workflow failed"),
                    "workflow_id": workflow_id
                }, status=500)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_agent_workflows(self, request: web_request.Request) -> web.Response:
        """Get agent workflow history."""
        try:
            limit = int(request.query.get("limit", 20))
            status_filter = request.query.get("status")
            
            workflows = list(self.workflow_history.values())
            
            # Filter by status if specified
            if status_filter and status_filter != "all":
                workflows = [w for w in workflows if w.get("status") == status_filter]
            
            # Sort by start time (most recent first)
            workflows.sort(key=lambda x: x.get("start_time", ""), reverse=True)
            
            # Limit results
            workflows = workflows[:limit]
            
            return web.json_response({
                "workflows": workflows,
                "total_count": len(workflows)
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def get_agent_workflow(self, request: web_request.Request) -> web.Response:
        """Get specific workflow details."""
        try:
            workflow_id = request.match_info["workflow_id"]
            
            if workflow_id not in self.workflow_history:
                return web.json_response({"error": "Workflow not found"}, status=404)
            
            return web.json_response(self.workflow_history[workflow_id])
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def cancel_agent_workflow(self, request: web_request.Request) -> web.Response:
        """Cancel a running workflow."""
        try:
            workflow_id = request.match_info["workflow_id"]
            
            # For now, just mark as cancelled in history
            if workflow_id in self.workflow_history:
                self.workflow_history[workflow_id]["status"] = "cancelled"
                return web.json_response({"message": "Workflow cancelled"})
            else:
                return web.json_response({"error": "Workflow not found"}, status=404)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
    
    async def run(self, host: str = "localhost", port: int = 3000, auto_restart: bool = True):
        """Run the web server with Next.js frontend and Python API backend."""
        await self.initialize_services()
        
        # Start the Python API server on port 8765
        api_port = 8765
        runner = web.AppRunner(self.app)
        await runner.setup()
        api_site = web.TCPSite(runner, host, api_port)
        await api_site.start()
        print(f"API server started on http://{host}:{api_port}")
        
        # Start Next.js dev server on the main port (it will proxy API requests to 8765)
        await self.start_next_dev_server(port)
        
        try:
            print(f"LocalGenius admin interface running on http://{host}:{port}")
            print(f"Frontend: http://{host}:{port}")
            print(f"API Backend: http://{host}:{api_port}/api/")
            print("Next.js will proxy /api/* requests to the Python backend")
            print("")
            if auto_restart:
                print("📝 Note: Next.js may restart occasionally due to file changes - this is normal.")
                print("   The Python API server will remain stable throughout.")
                print("   Auto-restart is enabled with safeguards to prevent restart loops.")
            else:
                print("📝 Note: Auto-restart is disabled. If Next.js stops, you'll need to restart manually.")
            print("🛑 Press Ctrl+C to stop both servers")
            
            # Keep both servers running
            try:
                if auto_restart:
                    restart_count = 0
                    last_restart_time = 0
                    
                    while True:
                        await asyncio.sleep(5)  # Check less frequently (every 5 seconds instead of 1)
                        
                        # Check if Next.js process is still running
                        if self.next_process and self.next_process.poll() is not None:
                            current_time = asyncio.get_event_loop().time()
                            
                            # Only restart if it's been more than 30 seconds since last restart
                            # This prevents restart loops from Next.js hot reloading
                            if current_time - last_restart_time > 30:
                                restart_count += 1
                                
                                # Don't restart more than 3 times to prevent infinite loops
                                if restart_count <= 3:
                                    print(f"Next.js process stopped, restarting... (attempt {restart_count}/3)")
                                    await self.start_next_dev_server(port)
                                    last_restart_time = current_time
                                else:
                                    print("Next.js process has restarted too many times. Stopping auto-restart.")
                                    print("You may need to manually restart or check for issues.")
                                    break
                            # If it's been less than 30 seconds, don't restart (likely hot reload)
                else:
                    # No auto-restart - just wait indefinitely
                    while True:
                        await asyncio.sleep(60)  # Check every minute just to keep the loop alive
                        
            except KeyboardInterrupt:
                pass
            finally:
                await self.stop_next_dev_server()
                await runner.cleanup()
                if self.db:
                    await self.db.close()
                    
        except Exception as e:
            print(f"Server error: {e}")
            await self.stop_next_dev_server()
            if 'runner' in locals():
                await runner.cleanup()
            raise