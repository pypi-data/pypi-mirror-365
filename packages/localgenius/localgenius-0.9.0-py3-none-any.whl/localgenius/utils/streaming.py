"""Streaming utilities for real-time CLI output."""

import asyncio
import sys
from typing import AsyncGenerator, Dict, Any, Optional
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.table import Table
import time

console = Console()


class StreamingOutput:
    """Base class for streaming output functionality."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.start_time = time.time()
        
    async def stream_message(self, message: str, style: str = "white") -> None:
        """Stream a single message."""
        if self.enabled:
            console.print(f"[{style}]{message}[/{style}]")
            await asyncio.sleep(0.01)  # Small delay to allow output to flush
    
    async def stream_progress(self, current: int, total: int, description: str) -> None:
        """Stream progress updates."""
        if self.enabled:
            percentage = (current / total * 100) if total > 0 else 0
            console.print(f"[cyan]{description}[/cyan] [{current}/{total}] {percentage:.1f}%")
            await asyncio.sleep(0.01)
    
    async def stream_error(self, error: str) -> None:
        """Stream error message."""
        if self.enabled:
            console.print(f"[red]✗ {error}[/red]")
            await asyncio.sleep(0.01)
    
    async def stream_success(self, message: str) -> None:
        """Stream success message."""
        if self.enabled:
            console.print(f"[green]✓ {message}[/green]")
            await asyncio.sleep(0.01)
    
    async def stream_warning(self, message: str) -> None:
        """Stream warning message."""
        if self.enabled:
            console.print(f"[yellow]⚠ {message}[/yellow]")
            await asyncio.sleep(0.01)
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since streaming started."""
        return time.time() - self.start_time


class IndexingStreamer(StreamingOutput):
    """Specialized streaming for indexing operations."""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.files_processed = 0
        self.total_files = 0
        self.chunks_generated = 0
        self.embeddings_created = 0
        self.current_file = ""
    
    async def start_indexing(self, total_files: int, source_name: str) -> None:
        """Start indexing stream."""
        self.total_files = total_files
        await self.stream_message(f"🚀 Starting indexing of {source_name}", "bold cyan")
        await self.stream_message(f"📁 Found {total_files} files to process", "dim")
    
    async def start_file(self, file_name: str, file_index: int) -> None:
        """Start processing a file."""
        self.current_file = file_name
        self.files_processed = file_index
        await self.stream_progress(file_index, self.total_files, f"Processing {file_name}")
    
    async def file_read(self, content_length: int) -> None:
        """Stream file read completion."""
        await self.stream_message(f"  📖 Read {content_length:,} characters from {self.current_file}", "dim")
    
    async def chunks_created(self, chunk_count: int) -> None:
        """Stream chunk creation."""
        self.chunks_generated += chunk_count
        await self.stream_message(f"  ✂️ Created {chunk_count} chunks", "dim")
    
    async def embeddings_generated(self, embedding_count: int) -> None:
        """Stream embedding generation."""
        self.embeddings_created += embedding_count
        await self.stream_message(f"  🧠 Generated {embedding_count} embeddings", "dim")
    
    async def file_completed(self) -> None:
        """Stream file completion."""
        await self.stream_success(f"Completed {self.current_file}")
    
    async def file_error(self, error: str) -> None:
        """Stream file error."""
        await self.stream_error(f"Failed to process {self.current_file}: {error}")
    
    async def indexing_completed(self, indexed_count: int, skipped_count: int) -> None:
        """Stream indexing completion."""
        elapsed = self.get_elapsed_time()
        await self.stream_message(f"🎉 Indexing completed in {elapsed:.2f}s", "bold green")
        await self.stream_success(f"Indexed {indexed_count} files")
        if skipped_count > 0:
            await self.stream_warning(f"Skipped {skipped_count} files due to errors")
        await self.stream_message(f"📊 Total chunks: {self.chunks_generated}, embeddings: {self.embeddings_created}", "cyan")


class SearchStreamer(StreamingOutput):
    """Specialized streaming for search operations."""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.results_found = 0
    
    async def start_search(self, query: str, threshold: float) -> None:
        """Start search stream."""
        await self.stream_message(f"🔍 Searching for: '{query}'", "bold cyan")
        await self.stream_message(f"📊 Similarity threshold: {threshold}", "dim")
    
    async def stream_result(self, result_index: int, doc: Any, score: float) -> None:
        """Stream a search result."""
        self.results_found += 1
        await self.stream_message(f"📄 Result {result_index}", "bold yellow")
        await self.stream_message(f"  📂 Source: {doc.source_path}", "green")
        await self.stream_message(f"  🔢 Chunk: {doc.chunk_index}", "green")
        await self.stream_message(f"  🎯 Similarity: {score:.3f}", "green")
        preview = doc.content[:150].replace('\n', ' ')
        await self.stream_message(f"  📝 Preview: {preview}...", "dim")
    
    async def search_completed(self) -> None:
        """Stream search completion."""
        elapsed = self.get_elapsed_time()
        await self.stream_success(f"Search completed in {elapsed:.2f}s - found {self.results_found} results")


class AgentStreamer(StreamingOutput):
    """Specialized streaming for agent operations."""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.tasks_completed = 0
        self.total_tasks = 0
    
    async def start_query(self, query: str) -> None:
        """Start agent query stream."""
        await self.stream_message(f"🤖 Processing query with agent system", "bold cyan")
        await self.stream_message(f"❓ Query: {query}", "dim")
    
    async def service_initialized(self, service_name: str, details: str = "") -> None:
        """Stream service initialization."""
        await self.stream_message(f"  ⚙️ Initialized {service_name}" + (f": {details}" if details else ""), "dim")
    
    async def agents_registered(self, agent_count: int, agent_names: list) -> None:
        """Stream agent registration."""
        await self.stream_message(f"  🤖 Registered {agent_count} agents: {', '.join(agent_names)}", "dim")
    
    async def task_started(self, task_name: str, task_index: int, total_tasks: int) -> None:
        """Stream task start."""
        self.total_tasks = total_tasks
        await self.stream_progress(task_index, total_tasks, f"Starting {task_name}")
    
    async def task_completed(self, task_name: str) -> None:
        """Stream task completion."""
        self.tasks_completed += 1
        await self.stream_success(f"Completed {task_name}")
    
    async def task_error(self, task_name: str, error: str) -> None:
        """Stream task error."""
        await self.stream_error(f"Task {task_name} failed: {error}")
    
    async def query_completed(self, execution_time: float) -> None:
        """Stream query completion."""
        await self.stream_message(f"✨ Query completed in {execution_time:.2f}s", "bold green")
        await self.stream_message(f"📊 Tasks: {self.tasks_completed}/{self.total_tasks} completed", "cyan")


class StatusStreamer(StreamingOutput):
    """Specialized streaming for status operations."""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
    
    async def start_status_check(self) -> None:
        """Start status check stream."""
        await self.stream_message("📊 Gathering LocalGenius status information", "bold cyan")
    
    async def checking_config(self) -> None:
        """Stream config check."""
        await self.stream_message("  ⚙️ Checking configuration", "dim")
    
    async def checking_database(self) -> None:
        """Stream database check."""
        await self.stream_message("  🗄️ Analyzing database", "dim")
    
    async def database_stats(self, stats: Dict[str, Any]) -> None:
        """Stream database statistics."""
        await self.stream_message(f"  📈 Found {stats['total_documents']} documents", "green")
        await self.stream_message(f"  🧠 {stats['total_embeddings']} embeddings stored", "green")
        await self.stream_message(f"  📏 Vector dimension: {stats['vector_dimension']}", "green")
    
    async def status_completed(self) -> None:
        """Stream status completion."""
        elapsed = self.get_elapsed_time()
        await self.stream_success(f"Status check completed in {elapsed:.2f}s")


def create_streamer(command_type: str, enabled: bool = True) -> StreamingOutput:
    """Factory function to create appropriate streamer."""
    streamers = {
        'index': IndexingStreamer,
        'search': SearchStreamer,
        'agent': AgentStreamer,
        'status': StatusStreamer,
    }
    
    streamer_class = streamers.get(command_type, StreamingOutput)
    return streamer_class(enabled)


async def stream_generator(messages: list, delay: float = 0.05) -> AsyncGenerator[str, None]:
    """Async generator for streaming messages with delay."""
    for message in messages:
        yield message
        await asyncio.sleep(delay)