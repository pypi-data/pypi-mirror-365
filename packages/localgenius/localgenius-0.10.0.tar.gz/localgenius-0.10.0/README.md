# LocalGenius 🧠

> A personal MCP (Model Context Protocol) server that acts as a RAG (Retrieval-Augmented Generation) source for your LLM. Seamlessly integrates with Claude Desktop to give your AI access to your local documents.

[![PyPI version](https://badge.fury.io/py/localgenius.svg)](https://badge.fury.io/py/localgenius)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🔍 **Semantic Search** - Find relevant content using vector similarity
- 🤖 **RAG-Powered Q&A** - AI answers based on your documents using GPT models
- 📁 **Local Vector Store** - Fast SQLite + FAISS storage, all on your machine
- 🖥️ **Claude Desktop Integration** - Native MCP support with automatic setup
- 🎨 **Rich CLI** - Beautiful command-line interface with onboarding wizard
- ⚡ **Fast Indexing** - Efficient document processing and retrieval
- 🌐 **Web Admin Interface** - Modern React dashboard for management
- 🔒 **Security First** - Environment variables, no sensitive data in config files
- 📊 **Multiple File Types** - Support for text, markdown, code, and configuration files

## 🚀 Quick Start

### 1. Installation

```bash
# Basic installation
pip install localgenius

# With document conversion support (PDF, DOCX, PPTX, XLSX, EPUB)
pip install localgenius[documents]

# Verify installation
localgenius --help
```

### 2. Environment Setup

```bash
# Required: Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Optional: Add to your shell profile for persistence
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc  # or ~/.zshrc
```

### 3. Initialize LocalGenius

```bash
# Interactive setup wizard
localgenius init
```

The setup wizard will:
- Create configuration directory (`~/.localgenius/`)
- Set up your first data source
- Configure embedding and MCP settings
- Test your OpenAI API key

### 4. Add Your Documents

```bash
# Add a document directory
localgenius add-source /path/to/documents --name "My Docs"

# Add with automatic indexing
localgenius add-source /path/to/code --name "My Code" --index
```

### 5. Index Your Documents

```bash
# Index all configured sources
localgenius index

# View indexing progress and statistics
localgenius index --show
```

### 6. Test It Out

```bash
# Search your documents
localgenius search "Python examples"

# Ask AI questions about your documents
localgenius ask "What are the main topics in my documents?"

# Check system status
localgenius status
```

## 🖥️ Claude Desktop Integration

### Automatic Setup (Recommended)

```bash
# Automatically configure Claude Desktop
localgenius install --claude
```

This command will:
- ✅ Create MCP server launcher script
- ✅ Configure Claude Desktop automatically
- ✅ Back up existing configuration
- ✅ Show you next steps

**Then restart Claude Desktop completely (Cmd+Q on Mac) and look for the MCP icon (🧩)!**

### Manual Setup

If automatic setup doesn't work, add this to your Claude Desktop config file:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "localgenius": {
      "command": "/path/to/your/python",
      "args": ["-m", "localgenius.mcp.fastmcp_server"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Using LocalGenius in Claude

Once configured, you can ask Claude to use your documents:

- *"Search my documents for information about authentication"*
- *"What do my files say about the API architecture?"*
- *"Show me the LocalGenius status"*
- *"Based on my indexed documents, explain how to deploy this project"*

## 🌐 Web Admin Interface

LocalGenius includes a modern React-based admin interface:

```bash
# Start the admin interface
localgenius serve --admin
```

**Opens at:** http://localhost:3000

### Admin Features

- 📊 **Dashboard** - System status, statistics, and recent activity
- 📁 **Data Sources** - Add, remove, and manage document directories
- 🔍 **Search & Test** - Test semantic search and RAG queries live
- ⚙️ **Settings** - Configure embedding, chunking, and MCP parameters
- 📈 **Index Management** - Detailed statistics and re-indexing controls
- 🎮 **Playground** - Interactive testing environment for prompts and settings

## 📚 CLI Commands Reference

### Core Commands

```bash
# Initialization and setup
localgenius init                    # First-time setup wizard
localgenius install --claude        # Configure Claude Desktop
localgenius sync-env                # Sync with environment variables

# Data source management
localgenius add-source PATH --name "Name" [--index]
localgenius remove-source PATH
localgenius list-sources

# Document indexing
localgenius index                   # Index all sources
localgenius index --source PATH     # Index specific source
localgenius index --force          # Force complete re-index
localgenius index --show           # Show detailed statistics

# Document conversion (requires localgenius[documents])
localgenius convert /path/to/docs   # Convert documents to markdown
localgenius convert --clear-cache   # Clear conversion cache
localgenius convert --show-stats    # Show cache statistics

# Search and Q&A
localgenius search "query" [--limit 5] [--threshold 0.7]
localgenius ask "question" [--model gpt-4] [--stream]

# Server operations
localgenius serve                   # MCP server (default)
localgenius serve --admin          # Web admin interface
localgenius serve --mcp            # MCP server explicitly

# System information
localgenius status                  # Show system status and statistics
```

### Environment Variables

LocalGenius prioritizes environment variables for security:

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional customization
LOCALGENIUS_DB_PATH=/custom/path/db
LOCALGENIUS_MCP_HOST=localhost
LOCALGENIUS_MCP_PORT=8765
LOCALGENIUS_MAX_CONTEXT_ITEMS=10
LOCALGENIUS_SIMILARITY_THRESHOLD=0.6

# Document conversion settings
LOCALGENIUS_CONVERT_ENABLED=true
LOCALGENIUS_CONVERT_GPU=false
LOCALGENIUS_CONVERT_MAX_SIZE_MB=100
LOCALGENIUS_CONVERT_FORMATS=pdf,docx,pptx,xlsx,epub
```

## 🔧 Available MCP Tools

LocalGenius provides these tools to Claude Desktop:

### 1. **search** - Semantic Search
Find relevant content based on similarity:
```
- query: Your search query
- limit: Maximum results (default: 5)  
- threshold: Similarity threshold (default: 0.7)
```

### 2. **ask** - RAG-Powered Q&A
Get AI-generated answers with source citations:
```
- question: Your question
- model: GPT model to use (default: gpt-3.5-turbo)
```

### 3. **status** - System Information
View index statistics and system health:
```
- Returns: Document count, sources, file types, and configuration
```

## 📁 Supported File Types

LocalGenius automatically detects and processes:

**Text & Documentation:**
- `.txt`, `.md`, `.markdown`, `.rst`
- `.log`, `.csv`, `.json`, `.xml`, `.yaml`, `.yml`

**Documents (with `localgenius[documents]`):**
- `.pdf` - PDF documents (using Marker or fallback)
- `.docx` - Word documents
- `.pptx` - PowerPoint presentations
- `.xlsx` - Excel spreadsheets
- `.epub` - eBooks

**Code Files:**
- `.py`, `.js`, `.ts`, `.jsx`, `.tsx`
- `.java`, `.cpp`, `.c`, `.h`, `.hpp`
- `.cs`, `.php`, `.rb`, `.go`, `.rs`
- `.swift`, `.kt`, `.scala`, `.clj`
- `.sh`, `.bat`, `.ps1`

**Web & Markup:**
- `.html`, `.css`, `.scss`

## 🛠️ Configuration

LocalGenius stores configuration in `~/.localgenius/config.yaml`. Key settings:

```yaml
# Embedding configuration
embedding:
  model: text-embedding-3-small
  chunk_size: 1000
  chunk_overlap: 200
  batch_size: 100

# MCP server settings  
mcp:
  host: localhost
  port: 8765
  similarity_threshold: 0.6
  max_context_items: 10

# Database settings
database:
  path: ~/.localgenius/db/localgenius.db
  vector_dimension: 1536
```

## 🔒 Security Features

- **Environment Variable Priority**: API keys read from environment, never stored in config files
- **Local Storage**: All data stays on your machine
- **No Cloud Dependencies**: Works entirely offline after initial setup
- **Config File Safety**: Sensitive data automatically excluded from config files

## 🚨 Troubleshooting

### Installation Issues

**Command not found:**
```bash
pip install --upgrade localgenius
# or for development:
pip install -e .
```

**Permission errors:**
```bash
pip install --user localgenius
```

### API Key Issues

**"Invalid OpenAI API key":**
```bash
# Verify your key is set correctly
echo $OPENAI_API_KEY

# Sync configuration  
localgenius sync-env

# Test with a simple command
localgenius status
```

### Claude Desktop Integration

**LocalGenius not appearing in Claude:**
1. Run `localgenius install --claude` for automatic setup
2. Completely restart Claude Desktop (Cmd+Q, then reopen)
3. Check for the MCP icon (🧩) in Claude's interface
4. Check Console.app for any error messages

**MCP connection issues:**
```bash
# Test MCP server manually
localgenius serve --mcp

# Verify configuration
localgenius status
```

### Indexing Issues

**"No documents found":**
```bash
# Check your data sources
localgenius list-sources

# Verify paths exist and are readable
ls -la /path/to/your/documents

# Check file types are supported
localgenius index --show
```

**Slow indexing:**
- Reduce batch size in settings
- Exclude large binary files
- Use `--source` to index specific directories

### Performance Issues

**Search too slow:**
- Increase similarity threshold
- Reduce max_context_items
- Check database size with `localgenius status`

**Memory usage:**
- Reduce chunk_size and batch_size in configuration
- Consider splitting large document collections

## 📋 Requirements

- **Python**: 3.8 or higher
- **OpenAI API Key**: Required for embeddings and RAG functionality
- **Storage**: ~100MB for typical document collections
- **Memory**: 512MB+ recommended for large document sets

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTE.md](CONTRIBUTE.md) for guidelines on:
- Setting up the development environment
- Code style and testing requirements
- Submitting issues and pull requests
- Feature request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp) for MCP server functionality
- Uses [OpenAI](https://openai.com/) for embeddings and language model capabilities
- Vector search powered by [FAISS](https://github.com/facebookresearch/faiss)
- CLI interface built with [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)

---

**Star ⭐ this repo if LocalGenius helps you organize and search your documents with AI!**