"""Main CLI entry point for LocalGenius."""

# Fix for OpenMP conflict on macOS with FAISS
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich import print as rprint

from .onboarding import check_and_run_onboarding, OnboardingWizard
from ..core.config import Settings
from ..core.database import Database
from ..core.embeddings import EmbeddingManager
from ..core.rag import RAGService
# HTTP server functionality removed - use MCP server instead
from ..utils.indexer import Indexer


console = Console()


@click.group()
@click.pass_context
def cli(ctx):
    """LocalGenius - Personal MCP server for RAG-powered LLM interactions."""
    # Load settings (will be available to all commands)
    ctx.ensure_object(dict)
    ctx.obj['settings'] = Settings.load_from_file()


@cli.command()
@click.option('--force', '-f', is_flag=True, help='Force reinitialization (clear all data)')
@click.pass_context
def init(ctx, force: bool):
    """Initialize LocalGenius (first-run setup)."""
    settings = asyncio.run(_init_localgenius(force))
    ctx.obj['settings'] = settings


@cli.command()
@click.option('--claude', is_flag=True, help='Install MCP server in Claude Desktop')
@click.pass_context
def install(ctx, claude: bool):
    """Install LocalGenius integrations."""
    if claude:
        asyncio.run(_install_claude_mcp(ctx.obj['settings']))
    else:
        console.print("Please specify an integration to install:")
        console.print("  --claude    Install MCP server in Claude Desktop")


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--name', '-n', help='Name for the data source')
@click.option('--index', '-i', is_flag=True, help='Index the data source immediately')
@click.pass_context
def add_source(ctx, path: Path, name: Optional[str], index: bool):
    """Add a new data source."""
    settings: Settings = ctx.obj['settings']
    
    try:
        settings.add_data_source(path.resolve(), name)
        console.print(f"[green]✓[/green] Added data source: {name or path.name} ({path})")
        
        if index:
            console.print("Indexing data source...")
            asyncio.run(_index_source(settings, path.resolve()))
            
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(path_type=Path))
@click.pass_context
def remove_source(ctx, path: Path):
    """Remove a data source."""
    settings: Settings = ctx.obj['settings']
    
    try:
        settings.remove_data_source(path.resolve())
        console.print(f"[green]✓[/green] Removed data source: {path}")
        
        # Also remove from database
        asyncio.run(_remove_source_from_db(settings, path.resolve()))
        
    except ValueError:
        console.print(f"[red]✗[/red] Data source not found: {path}")
        sys.exit(1)


@cli.command()
@click.pass_context
def list_sources(ctx):
    """List all data sources."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.data_sources:
        console.print("[yellow]No data sources configured.[/yellow]")
        console.print("Use [bold]localgenius add-source <path>[/bold] to add one.")
        return
        
    table = Table(title="Data Sources")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Patterns", style="magenta")
    
    for source in settings.data_sources:
        status = "✓ Enabled" if source.enabled else "✗ Disabled"
        patterns = ", ".join(source.file_patterns)
        table.add_row(source.name, str(source.path), status, patterns)
        
    console.print(table)


@cli.command()
@click.option('--source', '-s', type=click.Path(path_type=Path), help='Index specific source')
@click.option('--force', '-f', is_flag=True, help='Force re-indexing')
@click.option('--show', is_flag=True, help='Show detailed index statistics and contents')
@click.pass_context
def index(ctx, source: Optional[Path], force: bool, show: bool):
    """Index data sources or show index contents."""
    settings: Settings = ctx.obj['settings']
    
    if show:
        # Show index statistics and contents
        asyncio.run(_show_index_details(settings))
        return
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        console.print("Set OPENAI_API_KEY environment variable or run [bold]localgenius init[/bold]")
        sys.exit(1)
        
    sources_to_index = []
    
    if source:
        # Find specific source
        source = source.resolve()
        for ds in settings.data_sources:
            if ds.path == source:
                sources_to_index.append(ds)
                break
        else:
            console.print(f"[red]✗[/red] Data source not found: {source}")
            sys.exit(1)
    else:
        # Index all enabled sources
        sources_to_index = settings.get_active_data_sources()
        
    if not sources_to_index:
        console.print("[yellow]No data sources to index.[/yellow]")
        return
        
    console.print(f"Indexing {len(sources_to_index)} data source(s)...")
    asyncio.run(_index_sources(settings, sources_to_index, force))


@cli.command()
@click.option('--mcp', is_flag=True, help='Run as MCP server')
@click.option('--admin', is_flag=True, help='Run with admin web interface')
@click.option('--host', '-h', default='localhost', help='Host to bind to (default: localhost)')
@click.option('--port', '-p', type=int, default=3000, help='Port to bind to (default: 3000)')
@click.pass_context
def serve(ctx, mcp: bool, admin: bool, host: str, port: int):
    """Start the LocalGenius server."""
    settings: Settings = ctx.obj['settings']
    
    # Default to MCP mode if no flags specified
    if not mcp and not admin:
        mcp = True
        
    if mcp and admin:
        console.print("[red]✗[/red] Cannot run both MCP and admin mode simultaneously")
        console.print("Use either [cyan]--mcp[/cyan] or [cyan]--admin[/cyan]")
        sys.exit(1)
        
    if admin:
        # Run admin web interface
        console.print(f"[green]Starting LocalGenius admin interface...[/green]")
        console.print(f"Admin interface: http://{host}:{port}")
        console.print(f"API backend will run on port 8765")
        console.print("[dim]Press Ctrl+C to stop[/dim]")
        
        try:
            asyncio.run(_run_admin_server(settings, host, port))
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped.[/yellow]")
    else:
        # Run MCP server
        # In MCP mode, suppress all console output as it interferes with JSON-RPC protocol
        import os
        import sys
        
        # Redirect stdout to stderr to prevent interfering with MCP protocol
        old_stdout = sys.stdout
        sys.stdout = sys.stderr
        
        try:
            asyncio.run(_run_mcp_server(settings))
        except KeyboardInterrupt:
            pass
        finally:
            sys.stdout = old_stdout


@cli.command()
@click.pass_context
def status(ctx):
    """Show LocalGenius status and statistics."""
    settings: Settings = ctx.obj['settings']
    
    # Configuration status
    config_table = Table(title="Configuration")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    
    config_table.add_row("Config Path", str(settings.config_path))
    config_table.add_row("Database Path", str(settings.database.path))
    config_table.add_row("OpenAI API Key", "✓ Configured" if settings.openai_api_key else "✗ Not configured")
    config_table.add_row("MCP Server", f"{settings.mcp.host}:{settings.mcp.port}")
    
    console.print(config_table)
    console.print()
    
    # Database statistics
    stats = asyncio.run(_get_db_stats(settings))
    
    stats_table = Table(title="Database Statistics")
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Documents", str(stats["total_documents"]))
    stats_table.add_row("Total Embeddings", str(stats["total_embeddings"]))
    stats_table.add_row("Vector Dimension", str(stats["vector_dimension"]))
    
    console.print(stats_table)
    
    if stats["sources"]:
        console.print()
        sources_table = Table(title="Indexed Sources")
        sources_table.add_column("Source", style="cyan")
        sources_table.add_column("Documents", style="green")
        
        for source, count in stats["sources"].items():
            sources_table.add_row(source, str(count))
            
        console.print(sources_table)


@cli.command()
@click.argument('query')
@click.option('--limit', '-l', type=int, default=5, help='Number of results')
@click.option('--threshold', '-t', type=float, default=0.7, help='Similarity threshold (use "config set similarity_threshold X" to change default)')
@click.pass_context
def search(ctx, query: str, limit: int, threshold: float):
    """Search for similar content."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        sys.exit(1)
        
    results = asyncio.run(_search_content(settings, query, limit, threshold))
    
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
        
    for i, (doc, score) in enumerate(results, 1):
        console.print(f"\n[bold cyan]Result {i}[/bold cyan] (similarity: {score:.2f})")
        console.print(f"[green]Source:[/green] {doc.source_path}")
        console.print(f"[green]Chunk:[/green] {doc.chunk_index}")
        console.print(f"[dim]{doc.content[:200]}...[/dim]")


@cli.command()
@click.argument('question')
@click.option('--model', '-m', default='gpt-4o', help='OpenAI model to use')
@click.option('--limit', '-l', type=int, help='Max context items')
@click.option('--threshold', '-t', type=float, help='Similarity threshold (use "config set similarity_threshold X" to change default)')
@click.option('--stream', '-s', is_flag=True, help='Stream the response')
@click.pass_context
def ask(ctx, question: str, model: str, limit: Optional[int], threshold: Optional[float], stream: bool):
    """Ask a question using RAG (Retrieval-Augmented Generation)."""
    settings: Settings = ctx.obj['settings']
    
    if not settings.openai_api_key:
        console.print("[red]✗[/red] OpenAI API key not configured.")
        sys.exit(1)
        
    console.print(f"[cyan]Question:[/cyan] {question}\n")
    
    if stream:
        asyncio.run(_ask_streaming(settings, question, model, limit, threshold))
    else:
        result = asyncio.run(_ask_question(settings, question, model, limit, threshold))
        
        # Display sources
        if result.get("sources"):
            console.print("[bold]Sources used:[/bold]")
            for source in result["sources"]:
                console.print(f"  • {source['file']} (chunk {source['chunk']}, similarity: {source['similarity']})")
            console.print()
        
        # Display answer
        console.print("[bold]Answer:[/bold]")
        console.print(result["answer"])
        
        # Display metadata
        if result.get("tokens_used"):
            console.print(f"\n[dim]Model: {result['model']}, Tokens: {result['tokens_used']}, Context items: {result.get('context_used', 0)}[/dim]")


@cli.group()
@click.pass_context
def config(ctx):
    """Manage LocalGenius configuration settings."""
    pass


@config.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key: str, value: str):
    """Set a configuration value."""
    settings: Settings = ctx.obj['settings']
    
    # Define settable keys and their types/validation
    settable_keys = {
        'similarity_threshold': {'type': float, 'min': 0.0, 'max': 1.0, 'path': 'mcp.similarity_threshold'},
        'max_context_items': {'type': int, 'min': 1, 'max': 50, 'path': 'mcp.max_context_items'},
        'chunk_size': {'type': int, 'min': 100, 'max': 5000, 'path': 'embedding.chunk_size'},
        'chunk_overlap': {'type': int, 'min': 0, 'max': 1000, 'path': 'embedding.chunk_overlap'},
        'embedding_model': {'type': str, 'options': ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002'], 'path': 'embedding.model'},
        'temperature': {'type': float, 'min': 0.0, 'max': 2.0, 'path': 'prompts.temperature'},
        'max_tokens': {'type': int, 'min': 100, 'max': 4000, 'path': 'prompts.max_tokens'},
    }
    
    if key not in settable_keys:
        console.print(f"[red]✗[/red] Unknown setting '{key}'.")
        console.print("\n[bold]Available settings:[/bold]")
        for setting_key in settable_keys.keys():
            console.print(f"  • {setting_key}")
        sys.exit(1)
    
    config_spec = settable_keys[key]
    
    try:
        # Convert value to appropriate type
        if config_spec['type'] == float:
            parsed_value = float(value)
            if 'min' in config_spec and parsed_value < config_spec['min']:
                raise ValueError(f"Value must be >= {config_spec['min']}")
            if 'max' in config_spec and parsed_value > config_spec['max']:
                raise ValueError(f"Value must be <= {config_spec['max']}")
        elif config_spec['type'] == int:
            parsed_value = int(value)
            if 'min' in config_spec and parsed_value < config_spec['min']:
                raise ValueError(f"Value must be >= {config_spec['min']}")
            if 'max' in config_spec and parsed_value > config_spec['max']:
                raise ValueError(f"Value must be <= {config_spec['max']}")
        elif config_spec['type'] == str:
            parsed_value = value
            if 'options' in config_spec and parsed_value not in config_spec['options']:
                raise ValueError(f"Value must be one of: {', '.join(config_spec['options'])}")
        
        # Set the value using the path
        path_parts = config_spec['path'].split('.')
        target_obj = settings
        for part in path_parts[:-1]:
            target_obj = getattr(target_obj, part)
        setattr(target_obj, path_parts[-1], parsed_value)
        
        # Save settings
        settings.save_to_file()
        
        console.print(f"[green]✓[/green] Set {key} = {parsed_value}")
        console.print(f"[dim]Configuration saved to {settings.config_path}[/dim]")
        
    except ValueError as e:
        console.print(f"[red]✗[/red] Invalid value for '{key}': {e}")
        sys.exit(1)


@config.command()
@click.argument('key', required=False)
@click.pass_context
def get(ctx, key: Optional[str]):
    """Get configuration value(s)."""
    settings: Settings = ctx.obj['settings']
    
    # Map display keys to actual setting paths
    config_map = {
        'similarity_threshold': ('mcp.similarity_threshold', settings.mcp.similarity_threshold),
        'max_context_items': ('mcp.max_context_items', settings.mcp.max_context_items),
        'chunk_size': ('embedding.chunk_size', settings.embedding.chunk_size),
        'chunk_overlap': ('embedding.chunk_overlap', settings.embedding.chunk_overlap),
        'embedding_model': ('embedding.model', settings.embedding.model),
        'temperature': ('prompts.temperature', settings.prompts.temperature),
        'max_tokens': ('prompts.max_tokens', settings.prompts.max_tokens),
        'mcp_host': ('mcp.host', settings.mcp.host),
        'mcp_port': ('mcp.port', settings.mcp.port),
        'openai_configured': ('openai_api_key', bool(settings.openai_api_key)),
    }
    
    if key:
        if key in config_map:
            _, value = config_map[key]
            console.print(f"{key} = {value}")
        else:
            console.print(f"[red]✗[/red] Unknown setting '{key}'.")
            console.print("\n[bold]Available settings:[/bold]")
            for setting_key in config_map.keys():
                console.print(f"  • {setting_key}")
            sys.exit(1)
    else:
        # Show all settings
        console.print("[bold]LocalGenius Configuration:[/bold]\n")
        
        console.print("[cyan]🔍 Search & RAG Settings:[/cyan]")
        console.print(f"  similarity_threshold = {settings.mcp.similarity_threshold}")
        console.print(f"  max_context_items = {settings.mcp.max_context_items}")
        console.print(f"  temperature = {settings.prompts.temperature}")
        console.print(f"  max_tokens = {settings.prompts.max_tokens}")
        
        console.print(f"\n[cyan]📝 Text Processing:[/cyan]")
        console.print(f"  embedding_model = {settings.embedding.model}")
        console.print(f"  chunk_size = {settings.embedding.chunk_size}")
        console.print(f"  chunk_overlap = {settings.embedding.chunk_overlap}")
        
        console.print(f"\n[cyan]🌐 Server Settings:[/cyan]")
        console.print(f"  mcp_host = {settings.mcp.host}")
        console.print(f"  mcp_port = {settings.mcp.port}")
        
        console.print(f"\n[cyan]🔑 API Configuration:[/cyan]")
        console.print(f"  openai_configured = {bool(settings.openai_api_key)}")
        
        console.print(f"\n[dim]Config file: {settings.config_path}[/dim]")


@cli.command()
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def reset(ctx, yes: bool):
    """Reset LocalGenius to a fresh state by clearing all data and configuration."""
    settings: Settings = ctx.obj['settings']
    
    console.print("[bold red]⚠️  RESET WARNING ⚠️[/bold red]")
    console.print("\nThis will completely reset LocalGenius by:")
    console.print("• Deleting the entire database and all indexed documents")
    console.print("• Clearing all embeddings and vector data")
    console.print("• Resetting configuration to defaults")
    console.print("• Removing all data sources")
    console.print("\n[red]This action cannot be undone![/red]")
    
    if not yes:
        confirm = click.confirm("\nAre you sure you want to proceed?")
        if not confirm:
            console.print("[yellow]Reset cancelled.[/yellow]")
            return
    
    console.print("\n[yellow]Resetting LocalGenius...[/yellow]")
    
    try:
        # Clear database
        if settings.database.path.exists():
            console.print("🗑️  Removing database...")
            settings.database.path.unlink()
            
            # Also remove the entire db directory if it exists
            db_dir = settings.database.path.parent
            if db_dir.exists() and db_dir.name == "db":
                import shutil
                shutil.rmtree(db_dir)
                
        # Reset configuration to defaults
        console.print("⚙️  Resetting configuration...")
        settings.data_sources = []
        settings.first_run = True
        
        # Reset embedding settings to defaults
        settings.embedding.chunk_size = 1000
        settings.embedding.chunk_overlap = 200
        settings.embedding.chunk_separator = '\n\n'
        settings.embedding.chunk_strategy = 'size_first'
        settings.embedding.batch_size = 100
        
        # Reset MCP settings to defaults
        settings.mcp.host = 'localhost'
        settings.mcp.port = 8765
        settings.mcp.max_context_items = 10
        settings.mcp.similarity_threshold = 0.7
        
        # Reset prompts to defaults
        from ..core.config import PromptConfig
        settings.prompts = PromptConfig()
        
        # Save the reset configuration
        settings.save_to_file()
        
        console.print("✅ Database cleared")
        console.print("✅ Configuration reset to defaults")
        console.print("✅ Data sources cleared")
        
        console.print("\n[bold green]🎉 LocalGenius has been reset successfully![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Run [cyan]localgenius init[/cyan] to set up LocalGenius again")
        console.print("2. Add your data sources with [cyan]localgenius add-source <path>[/cyan]")
        console.print("3. Index your documents with [cyan]localgenius index[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]✗ Reset failed: {str(e)}[/red]")
        sys.exit(1)


# Async helper functions

async def _index_source(settings: Settings, source_path: Path):
    """Index a single data source."""
    from ..utils.indexer import Indexer
    
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
    indexer = Indexer(db, embeddings, settings)
    
    # Find the data source config
    for ds in settings.data_sources:
        if ds.path == source_path:
            await indexer.index_source(ds)
            break
            
    await db.close()


async def _index_sources(settings: Settings, sources, force: bool):
    """Index multiple data sources."""
    from ..utils.indexer import Indexer
    
    try:
        db = Database(settings.database.path, settings.database.vector_dimension)
        await db.initialize()
        
        embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
        indexer = Indexer(db, embeddings, settings)
        
        for source in sources:
            console.print(f"\n[bold]Indexing: {source.name}[/bold]")
            console.print(f"Path: {source.path}")
            
            if force:
                console.print("[yellow]Force mode: removing existing documents...[/yellow]")
                # Remove existing documents
                await db.delete_documents_by_source(str(source.path))
                
            await indexer.index_source(source)
            
        await db.close()
        console.print("\n[green]✓[/green] Indexing complete.")
        
    except Exception as e:
        console.print(f"\n[red]✗ Indexing failed: {str(e)}[/red]")
        if "api_key" in str(e).lower():
            console.print("[yellow]Make sure your OpenAI API key is correctly set.[/yellow]")
        sys.exit(1)


async def _remove_source_from_db(settings: Settings, source_path: Path):
    """Remove source documents from database."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    await db.delete_documents_by_source(str(source_path))
    await db.close()


# HTTP server functionality removed - use MCP server instead


async def _run_mcp_server(settings: Settings):
    """Run the MCP server."""
    # Import and run the FastMCP server directly
    from ..mcp.fastmcp_server import main as run_fastmcp
    
    # FastMCP handles its own event loop, so we need to run it in sync context
    await asyncio.get_event_loop().run_in_executor(None, run_fastmcp)


async def _run_admin_server(settings: Settings, host: str, port: int):
    """Run the admin web interface server."""
    from ..web.server import LocalGeniusWebServer
    
    server = LocalGeniusWebServer(settings)
    await server.run(host, port)


async def _get_db_stats(settings: Settings):
    """Get database statistics."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    stats = await db.get_statistics()
    await db.close()
    return stats


async def _search_content(settings: Settings, query: str, limit: int, threshold: float):
    """Search for similar content."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    embeddings = EmbeddingManager(settings.openai_api_key, settings.embedding)
    query_embedding = await embeddings.embed_text(query)
    
    results = await db.search_similar(query_embedding, limit, threshold)
    
    await db.close()
    return results


async def _ask_question(settings: Settings, question: str, model: str, limit: Optional[int], threshold: Optional[float]):
    """Ask a question using RAG."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    rag = RAGService(settings, db)
    result = await rag.ask(
        query=question,
        model=model,
        max_context_items=limit,
        similarity_threshold=threshold
    )
    
    await db.close()
    return result


async def _ask_streaming(settings: Settings, question: str, model: str, limit: Optional[int], threshold: Optional[float]):
    """Ask a question with streaming response."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    rag = RAGService(settings, db)
    
    sources_shown = False
    console.print("[bold]Answer:[/bold]")
    
    async for chunk in rag.ask_with_streaming(
        query=question,
        model=model,
        max_context_items=limit,
        similarity_threshold=threshold
    ):
        if chunk["type"] == "sources" and not sources_shown:
            console.print("[bold]Sources used:[/bold]")
            for source in chunk["content"]:
                console.print(f"  • {source['file']} (chunk {source['chunk']}, similarity: {source['similarity']})")
            console.print()
            sources_shown = True
        elif chunk["type"] == "content":
            console.print(chunk["content"], end="")
        elif chunk["type"] == "error":
            console.print(f"\n[red]Error: {chunk['content']}[/red]")
    
    console.print()  # New line at the end
    await db.close()


def _detect_python_environment():
    """Detect the current Python environment and return appropriate command."""
    import subprocess
    import shutil
    
    # Check if we're in a virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    
    # Try to find the localgenius command
    localgenius_cmd = shutil.which('localgenius-mcp')
    if localgenius_cmd:
        return localgenius_cmd, "system"
    
    # Check if localgenius is installed in current Python
    try:
        import localgenius
        return sys.executable, "module"
    except ImportError:
        pass
    
    # Check common Python commands
    for python_cmd in ['python3', 'python']:
        if shutil.which(python_cmd):
            try:
                result = subprocess.run([python_cmd, '-c', 'import localgenius'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return python_cmd, "module"
            except:
                continue
    
    return None, None


async def _install_claude_mcp(settings: Settings):
    """Install LocalGenius MCP server in Claude Desktop."""
    import json
    from pathlib import Path
    import shutil
    
    console.print("[bold]Installing LocalGenius MCP server in Claude Desktop[/bold]\n")
    
    # Detect OS and set config path
    if sys.platform == "darwin":  # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    elif sys.platform == "linux":
        config_dir = Path.home() / ".config" / "Claude"
    elif sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", "")) / "Claude"
    else:
        console.print(f"[red]✗[/red] Unsupported platform: {sys.platform}")
        return
        
    config_file = config_dir / "claude_desktop_config.json"
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Detect Python environment and LocalGenius installation
    console.print("[dim]Detecting Python environment...[/dim]")
    python_cmd, install_type = _detect_python_environment()
    
    if not python_cmd:
        console.print("[red]✗[/red] Could not find LocalGenius installation")
        console.print("Please ensure LocalGenius is installed: [cyan]pip install localgenius[/cyan]")
        return
    
    console.print(f"[green]✓[/green] Found LocalGenius ({install_type}): {python_cmd}")
    
    # Prepare the MCP server configuration based on installation type
    if install_type == "system" and python_cmd.endswith('localgenius-mcp'):
        # Direct command available
        mcp_config = {
            "command": python_cmd,
            "args": [],
            "env": {
                "OPENAI_API_KEY": settings.openai_api_key or "${OPENAI_API_KEY}"
            }
        }
    else:
        # Use Python module approach
        mcp_config = {
            "command": python_cmd,
            "args": ["-m", "localgenius.mcp.fastmcp_server"],
            "env": {
                "OPENAI_API_KEY": settings.openai_api_key or "${OPENAI_API_KEY}"
            }
        }
    
    # Load existing config or create new one
    if config_file.exists():
        console.print(f"[green]✓[/green] Found existing Claude config")
        # Backup existing config
        backup_file = config_file.with_suffix(".json.backup")
        shutil.copy2(config_file, backup_file)
        console.print(f"[dim]  Backed up to {backup_file}[/dim]")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        console.print("[yellow]Creating new Claude config[/yellow]")
        config = {}
    
    # Add or update LocalGenius MCP server
    if "mcpServers" not in config:
        config["mcpServers"] = {}
        
    if "localgenius" in config["mcpServers"]:
        console.print("[yellow]⚠ LocalGenius already configured, updating...[/yellow]")
    
    config["mcpServers"]["localgenius"] = mcp_config
    
    # Write updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    console.print(f"[green]✓[/green] Updated Claude config: {config_file}")
    
    # Show summary
    console.print("\n[bold green]Installation complete![/bold green]")
    console.print("\nLocalGenius MCP server has been added to Claude Desktop.")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("1. Make sure you've indexed some documents: [cyan]localgenius index[/cyan]")
    if sys.platform == "darwin":
        console.print("2. Completely quit Claude Desktop (Cmd+Q)")
    elif sys.platform == "win32":
        console.print("2. Completely quit Claude Desktop (Alt+F4 or close from system tray)")
    else:
        console.print("2. Completely quit Claude Desktop")
    console.print("3. Restart Claude Desktop")
    console.print("4. Look for the MCP icon (🧩) in the text input area")
    console.print("\n[bold]You can now ask Claude:[/bold]")
    console.print('  • "Search my documents for X"')
    console.print('  • "What do my files say about Y?"')
    console.print('  • "Show me the LocalGenius status"')


async def _init_localgenius(force: bool = False) -> Settings:
    """Initialize LocalGenius with optional cleanup."""
    import shutil
    from pathlib import Path
    
    # If force flag is set, clean up existing config and database
    if force:
        console.print("[yellow]⚠ Force reinitialization requested[/yellow]")
        
        # Get config directory
        config_dir = Path.home() / ".localgenius"
        
        if config_dir.exists():
            console.print(f"[dim]Removing existing config directory: {config_dir}[/dim]")
            if Confirm.ask("This will delete all your LocalGenius configuration and data. Continue?", default=False):
                shutil.rmtree(config_dir)
                console.print("[green]✓[/green] Cleaned up existing configuration and database")
            else:
                console.print("[yellow]Cancelled initialization[/yellow]")
                return Settings.load_from_file()
        
        console.print()
    
    # Check if we need to run onboarding
    settings = Settings.load_from_file()
    
    # Run onboarding if first run OR if force cleanup was done
    if settings.first_run or force:
        wizard = OnboardingWizard()
        return await wizard.run()
    
    return settings


async def _show_index_details(settings: Settings):
    """Show detailed index statistics and contents."""
    db = Database(settings.database.path, settings.database.vector_dimension)
    await db.initialize()
    
    # Get basic statistics
    stats = await db.get_statistics()
    
    # Display overview
    console.print("[bold]LocalGenius Index Details[/bold]\n")
    
    # Summary table
    summary_table = Table(title="Index Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Documents", str(stats["total_documents"]))
    summary_table.add_row("Total Embeddings", str(stats["total_embeddings"]))
    summary_table.add_row("Vector Dimension", str(stats["vector_dimension"]))
    summary_table.add_row("Database Location", str(settings.database.path))
    summary_table.add_row("Index Size", f"{settings.database.path.stat().st_size / 1024 / 1024:.2f} MB" if settings.database.path.exists() else "N/A")
    
    console.print(summary_table)
    console.print()
    
    # Sources breakdown
    if stats["sources"]:
        sources_table = Table(title="Indexed Sources")
        sources_table.add_column("Source Path", style="cyan")
        sources_table.add_column("Documents", style="green")
        sources_table.add_column("Percentage", style="yellow")
        
        total_docs = stats["total_documents"]
        for source, count in sorted(stats["sources"].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_docs * 100) if total_docs > 0 else 0
            sources_table.add_row(source, str(count), f"{percentage:.1f}%")
            
        console.print(sources_table)
        console.print()
    
    # Sample documents
    console.print("[bold]Sample Indexed Documents:[/bold]")
    
    # Get a few sample documents
    cursor = await db._connection.execute(
        """
        SELECT source_path, content, chunk_index, metadata 
        FROM documents 
        ORDER BY RANDOM() 
        LIMIT 5
        """
    )
    samples = await cursor.fetchall()
    
    for i, (source, content, chunk_idx, metadata_str) in enumerate(samples, 1):
        metadata = json.loads(metadata_str) if metadata_str else {}
        console.print(f"\n[cyan]Sample {i}:[/cyan]")
        console.print(f"  Source: {metadata.get('file_name', 'Unknown')}")
        console.print(f"  Chunk: {chunk_idx}/{metadata.get('total_chunks', '?')}")
        console.print(f"  Preview: [dim]{content[:150]}...[/dim]")
    
    # File type statistics
    console.print("\n[bold]File Types Indexed:[/bold]")
    
    cursor = await db._connection.execute(
        """
        SELECT metadata FROM documents
        """
    )
    all_metadata = await cursor.fetchall()
    
    file_types = {}
    for (metadata_str,) in all_metadata:
        if metadata_str:
            metadata = json.loads(metadata_str)
            file_name = metadata.get('file_name', '')
            if file_name:
                ext = Path(file_name).suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1
    
    if file_types:
        type_table = Table()
        type_table.add_column("File Type", style="cyan")
        type_table.add_column("Count", style="green")
        
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
            type_table.add_row(ext or "(no extension)", str(count))
            
        console.print(type_table)
    
    await db.close()


@cli.command()
@click.pass_context
def sync_env(ctx):
    """Sync configuration with environment variables and remove sensitive data from config files."""
    import os
    from ..core.config import Settings
    
    console.print("[bold]Syncing configuration with environment variables...[/bold]")
    
    # Load current settings (will automatically use env vars where available)
    settings = ctx.obj['settings']
    
    # Check which environment variables are set
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LOCALGENIUS_DB_PATH": os.getenv("LOCALGENIUS_DB_PATH"),
        "LOCALGENIUS_MCP_HOST": os.getenv("LOCALGENIUS_MCP_HOST"),
        "LOCALGENIUS_MCP_PORT": os.getenv("LOCALGENIUS_MCP_PORT"),
        "LOCALGENIUS_MAX_CONTEXT_ITEMS": os.getenv("LOCALGENIUS_MAX_CONTEXT_ITEMS"),
        "LOCALGENIUS_SIMILARITY_THRESHOLD": os.getenv("LOCALGENIUS_SIMILARITY_THRESHOLD"),
        "LOCALGENIUS_CONVERT_ENABLED": os.getenv("LOCALGENIUS_CONVERT_ENABLED"),
        "LOCALGENIUS_CONVERT_GPU": os.getenv("LOCALGENIUS_CONVERT_GPU"),
        "LOCALGENIUS_CONVERT_MAX_SIZE_MB": os.getenv("LOCALGENIUS_CONVERT_MAX_SIZE_MB"),
        "LOCALGENIUS_CONVERT_FORMATS": os.getenv("LOCALGENIUS_CONVERT_FORMATS"),
    }
    
    found_vars = {k: v for k, v in env_vars.items() if v is not None}
    
    if found_vars:
        console.print("\n[green]Found environment variables:[/green]")
        for var, value in found_vars.items():
            if "API_KEY" in var:
                display_value = f"{value[:10]}..." if value else "None"
            else:
                display_value = value
            console.print(f"  {var}: {display_value}")
    else:
        console.print("\n[yellow]No LocalGenius environment variables found.[/yellow]")
    
    # Remove API key from config file if it exists
    config_path = settings.config_path
    if config_path.exists():
        console.print(f"\n[dim]Cleaning sensitive data from {config_path}[/dim]")
        
        # Re-save config (will exclude API key due to our changes)
        settings.save_to_file()
        console.print("[green]✓[/green] Removed sensitive data from config file")
    
    console.print("\n[bold green]Configuration sync complete![/bold green]")
    console.print("\n[dim]Environment variables now take priority over config file settings.[/dim]")


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path), required=False)
@click.option('--clear-cache', is_flag=True, help='Clear conversion cache')
@click.option('--show-stats', is_flag=True, help='Show conversion cache statistics')
@click.pass_context
def convert(ctx, path: Optional[Path], clear_cache: bool, show_stats: bool):
    """Convert documents to markdown format.
    
    Converts PDF, DOCX, PPTX, XLSX, and EPUB files to markdown.
    Requires: pip install localgenius[documents]
    """
    from ..utils.document_converter import DocumentConverter
    
    settings = ctx.obj['settings']
    cache_dir = Path(settings.config_path).parent
    converter_config = settings.document_conversion.model_dump() if hasattr(settings, 'document_conversion') else {}
    converter = DocumentConverter(cache_dir, converter_config)
    
    if clear_cache:
        converter.clear_cache()
        console.print("[green]✓[/green] Conversion cache cleared")
        return
    
    if show_stats:
        stats = converter.get_cache_stats()
        if "error" in stats:
            console.print(f"[red]Error getting cache stats: {stats['error']}[/red]")
            return
            
        console.print("\n[bold]Document Conversion Cache Statistics[/bold]")
        console.print(f"Cache directory: {stats['cache_dir']}")
        console.print(f"Cached files: {stats['cached_files']}")
        console.print(f"Total size: {stats['total_size_mb']:.2f} MB")
        console.print(f"Marker available: {'✓' if stats['marker_available'] else '✗'}")
        return
    
    # Check that path is provided if not using flags
    if not path:
        console.print("[red]Error:[/red] PATH argument required when not using --clear-cache or --show-stats")
        console.print("Usage: localgenius convert PATH")
        return
    
    # Convert files in the specified path
    if not converter.has_marker:
        console.print("[yellow]⚠[/yellow] Marker not available. Install with:")
        console.print("[dim]pip install localgenius[documents][/dim]")
        console.print("Using fallback converters for supported formats.\n")
    
    # Find convertible files
    document_extensions = {'.pdf', '.docx', '.pptx', '.xlsx', '.epub'}
    files_to_convert = []
    
    if path.is_file():
        if path.suffix.lower() in document_extensions:
            files_to_convert.append(path)
    else:
        for ext in document_extensions:
            files_to_convert.extend(path.rglob(f"*{ext}"))
    
    if not files_to_convert:
        console.print(f"[yellow]No convertible documents found in {path}[/yellow]")
        console.print(f"Supported formats: {', '.join(document_extensions)}")
        return
    
    console.print(f"[cyan]Found {len(files_to_convert)} documents to convert[/cyan]")
    
    converted = 0
    failed = 0
    
    for file_path in files_to_convert:
        console.print(f"\n[dim]Converting: {file_path.name}[/dim]")
        try:
            content = converter.convert_to_markdown(file_path)
            if content:
                console.print(f"[green]✓[/green] {file_path.name}")
                converted += 1
            else:
                console.print(f"[red]✗[/red] {file_path.name} (conversion failed)")
                failed += 1
        except Exception as e:
            console.print(f"[red]✗[/red] {file_path.name} (error: {e})")
            failed += 1
    
    console.print(f"\n[bold]Conversion Summary[/bold]")
    console.print(f"Converted: {converted}")
    console.print(f"Failed: {failed}")
    
    if converted > 0:
        console.print(f"\n[dim]Converted documents are cached and will be used during indexing.[/dim]")


if __name__ == "__main__":
    cli()