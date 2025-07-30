"""Streaming utilities for real-time CLI output."""

import asyncio
import sys
from typing import AsyncGenerator, Dict, Any, Optional, Union
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskID
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
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


class RealTimeResponseStreamer:
    """Streams agent responses in real-time to the terminal."""
    
    def __init__(self, enabled: bool = True, format_type: str = "text"):
        self.enabled = enabled
        self.format_type = format_type
        self.current_content = ""
        self.current_agent = None
        self.response_started = False
        
    async def start_response(self, query: str) -> None:
        """Initialize response streaming."""
        if self.enabled:
            console.print(f"\n[bold blue]🤖 Streaming Response for:[/bold blue] {query}\n")
            console.print("[dim]" + "="*80 + "[/dim]")
            self.response_started = True
    
    async def stream_agent_start(self, agent_name: str, action: str) -> None:
        """Stream when an agent starts working."""
        if self.enabled:
            self.current_agent = agent_name
            console.print(f"\n[bold cyan]🔄 {agent_name.title()} Agent:[/bold cyan] {action}")
    
    async def stream_content_chunk(self, chunk: str, agent_name: str = None) -> None:
        """Stream content chunks in real-time."""
        if not self.enabled:
            return
            
        if agent_name and agent_name != self.current_agent:
            await self.stream_agent_start(agent_name, "generating response")
        
        # Add chunk to current content
        self.current_content += chunk
        
        # Stream the chunk immediately
        if self.format_type == "markdown":
            # For markdown, we can stream raw chunks and let rich handle it
            console.print(chunk, end="", highlight=False)
        else:
            # For text, stream directly
            console.print(chunk, end="", highlight=False)
        
        # Flush output
        sys.stdout.flush()
        await asyncio.sleep(0.001)  # Very small delay for smooth streaming
    
    async def stream_workflow_update(self, step: str, status: str = "in_progress") -> None:
        """Stream workflow step updates."""
        if self.enabled:
            if status == "completed":
                console.print(f"[green]✓[/green] [dim]{step}[/dim]")
            elif status == "in_progress":
                console.print(f"[yellow]⏳[/yellow] [dim]{step}[/dim]")
            elif status == "failed":
                console.print(f"[red]✗[/red] [dim]{step}[/dim]")
    
    async def stream_sources(self, sources: list) -> None:
        """Stream source information."""
        if self.enabled and sources:
            console.print(f"\n[dim]📚 Sources ({len(sources)}):[/dim]")
            for i, source in enumerate(sources[:5], 1):  # Limit to 5 sources
                source_name = source.get('file', 'Unknown')
                similarity = source.get('similarity', 0)
                console.print(f"[dim]  {i}. {source_name} (similarity: {similarity:.2f})[/dim]")
    
    async def stream_final_response(self, response: str, sources: list = None) -> None:
        """Stream the final complete response."""
        if not self.enabled:
            return
        
        if not self.response_started:
            await self.start_response("Query")
        
        console.print("\n")
        
        if self.format_type == "markdown":
            try:
                md = Markdown(response)
                console.print(md)
            except Exception:
                console.print(response)
        else:
            console.print(response)
        
        if sources:
            await self.stream_sources(sources)
        
        console.print(f"\n[dim]" + "="*80 + "[/dim]")
        console.print("[green]✓ Response completed[/green]\n")
    
    async def stream_error(self, error: str, agent_name: str = None) -> None:
        """Stream error messages."""
        if self.enabled:
            agent_info = f" [{agent_name}]" if agent_name else ""
            console.print(f"[red]✗ Error{agent_info}:[/red] {error}")
    
    def get_current_content(self) -> str:
        """Get the current accumulated content."""
        return self.current_content
    
    async def finalize(self) -> None:
        """Finalize the streaming session."""
        if self.enabled and self.response_started:
            console.print(f"\n[dim]📊 Total content streamed: {len(self.current_content)} characters[/dim]")


class WorkflowStreamer(StreamingOutput):
    """Enhanced workflow streaming with real-time updates."""
    
    def __init__(self, enabled: bool = True):
        super().__init__(enabled)
        self.current_step = 0
        self.total_steps = 0
        
    async def start_workflow(self, query: str, total_steps: int) -> None:
        """Start workflow streaming."""
        if self.enabled:
            self.total_steps = total_steps
            console.print(f"[bold blue]🚀 Starting Multi-Agent Workflow[/bold blue]")
            console.print(f"[dim]Query: {query}[/dim]")
            console.print(f"[dim]Total steps: {total_steps}[/dim]\n")
    
    async def update_step(self, step_name: str, status: str = "in_progress", details: str = None) -> None:
        """Update current workflow step."""
        if not self.enabled:
            return
            
        if status == "started":
            self.current_step += 1
            console.print(f"[cyan]🔄 Step {self.current_step}/{self.total_steps}:[/cyan] {step_name}")
            if details:
                console.print(f"[dim]   {details}[/dim]")
        elif status == "completed":
            console.print(f"[green]✓ Completed:[/green] {step_name}")
            if details:
                console.print(f"[dim]   {details}[/dim]")
        elif status == "failed":
            console.print(f"[red]✗ Failed:[/red] {step_name}")
            if details:
                console.print(f"[red]   {details}[/red]")
    
    async def stream_agent_response(self, agent_name: str, content: str, chunk_size: int = 50) -> None:
        """Stream agent response in chunks for real-time effect."""
        if not self.enabled:
            return
            
        console.print(f"[green]📝 {agent_name} Response:[/green]")
        
        # Stream content in chunks
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            console.print(chunk, end="", highlight=False)
            sys.stdout.flush()
            await asyncio.sleep(0.05)  # Adjust speed as needed
        
        console.print("\n")  # End with newline