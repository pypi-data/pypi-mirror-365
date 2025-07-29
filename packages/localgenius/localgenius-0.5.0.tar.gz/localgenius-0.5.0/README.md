# LocalGenius

A personal MCP (Model Context Protocol) server that acts as a RAG (Retrieval-Augmented Generation) source for your LLM. Works with Claude Desktop!

## Features

- 🔍 Semantic search through your local documents
- 🤖 RAG-powered Q&A using OpenAI GPT-4o
- 📁 Local vector store using SQLite + FAISS
- 🖥️ Claude Desktop integration via MCP
- 🎨 Rich CLI interface with onboarding wizard
- ⚡ Fast indexing and retrieval

## Installation

```bash
# Install from PyPI (recommended)
pip install localgenius

# Or install from source
git clone https://github.com/yourusername/localgenius.git
cd localgenius
pip install -e .
```

## Quick Start

```bash
# 1. Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# 2. First run - interactive setup wizard
localgenius init

# 3. Add documents to index
localgenius add-source /path/to/documents --name "My Docs"

# 4. Index the documents
localgenius index

# 5. Test it out
localgenius ask "What are the main topics in my documents?"
```

## Claude Desktop Integration

### Automatic Setup (Recommended)

```bash
# Automatically configure Claude Desktop
localgenius install --claude
```

This command will:
- Create the MCP server launcher script
- Configure Claude Desktop automatically
- Back up existing configuration
- Show you next steps

Then restart Claude Desktop (Cmd+Q) and look for the MCP icon (🧩)!

## CLI Commands

```bash
# Initialize (first-time setup)
localgenius init

# Manage data sources
localgenius add-source /path/to/docs --name "My Docs" --index
localgenius remove-source /path/to/docs
localgenius list-sources

# Install integrations
localgenius install --claude         # Auto-configure Claude Desktop

# Index documents
localgenius index                    # Index all sources
localgenius index --source /path     # Index specific source
localgenius index --force           # Force re-index
localgenius index --show            # Show detailed index statistics

# Search and ask questions
localgenius search "your query"
localgenius ask "your question"
localgenius ask "question" --model gpt-4o --stream

# Run servers
localgenius serve         # MCP server for Claude Desktop (default)
localgenius serve --admin # Web admin interface on http://localhost:3000
localgenius serve --mcp   # MCP server explicitly

# Check status
localgenius status
```

## Usage in Claude Desktop

Once configured, you can ask Claude to use your documents:

- "Search my documents for information about X"
- "What do my files say about Y?"
- "Show me the LocalGenius status"
- "Based on my indexed documents, explain Z"

## Web Admin Interface

LocalGenius includes a modern React-based admin interface for managing your RAG system:

```bash
# Start the admin interface
localgenius serve --admin

# Opens:
# - Admin interface: http://localhost:3000
# - API backend: http://localhost:8765 (proxied through Next.js)
```

### Admin Features:
- 📊 **Dashboard** - View system status and statistics
- 📁 **Data Sources** - Add, remove, and manage document sources
- 🔍 **Search & Test** - Test semantic search and RAG queries
- ⚙️ **Settings** - Configure embedding, chunking, and MCP settings
- 📈 **Index Management** - View detailed index statistics and trigger re-indexing

## Available MCP Tools

LocalGenius provides three tools to Claude Desktop:

1. **search** - Semantic search through documents
   - Find relevant content based on similarity
   - Adjustable similarity threshold and result count

2. **ask** - RAG-powered Q&A using GPT-4o
   - Get AI-generated answers based on your documents
   - Includes source citations

3. **status** - Get index statistics
   - View total documents, sources, and file types

## Requirements

- Python 3.8+
- OpenAI API key (for embeddings and RAG)

## Troubleshooting

### "Command not found: localgenius"
```bash
pip install -e .
```

### "OpenAI API key not configured"
```bash
export OPENAI_API_KEY="sk-..."
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

### Claude Desktop doesn't show LocalGenius
1. Run `localgenius install --claude` to auto-configure
2. Make sure to completely restart Claude Desktop (Cmd+Q)
3. Check Console.app for error messages

### "No documents indexed"
```bash
localgenius status        # Check what's configured
localgenius index         # Run indexing
```