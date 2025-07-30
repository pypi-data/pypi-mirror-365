"""Configuration management for LocalGenius."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DataSource(BaseModel):
    """Configuration for a data source."""
    path: Path
    name: str
    enabled: bool = True
    file_patterns: List[str] = Field(default_factory=lambda: [
        "*.txt", "*.md", "*.markdown", "*.rst", 
        "*.py", "*.js", "*.ts", "*.jsx", "*.tsx", 
        "*.java", "*.cpp", "*.c", "*.h", "*.hpp",
        "*.json", "*.yaml", "*.yml", "*.xml",
        "*.html", "*.css", "*.scss",
        "*.sh", "*.bash", "*.zsh",
        "*.go", "*.rs", "*.rb", "*.php",
        "*.pdf", "*.docx", "*.pptx", "*.xlsx", "*.epub"
    ])
    recursive: bool = True
    
    @validator("path")
    def validate_path(cls, v):
        path = Path(v) if not isinstance(v, Path) else v
        if not path.exists():
            raise ValueError(f"Path {path} does not exist")
        return path


class EmbeddingConfig(BaseModel):
    """Configuration for embeddings."""
    model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    chunk_separator: str = "\n\n"
    chunk_strategy: str = "size_first"  # "size_first" or "separator_strict"
    batch_size: int = 100


class DatabaseConfig(BaseModel):
    """Configuration for the database."""
    path: Path = Field(
        default=Path.home() / ".localgenius" / "db" / "localgenius.db",
        env="LOCALGENIUS_DB_PATH"
    )
    vector_dimension: int = Field(default=1536, env="LOCALGENIUS_VECTOR_DIMENSION")


class PromptConfig(BaseModel):
    """Configuration for RAG prompts."""
    system_prompt: str = """You are a helpful assistant that answers questions based on the provided context. 
Use the context to provide accurate and relevant answers. If the context doesn't contain enough information 
to fully answer the question, say so. Always cite which source file the information comes from."""
    
    user_prompt_template: str = """Context from indexed documents:

{context}

---

Question: {query}

Please provide a comprehensive answer based on the context above. Cite the source files when referencing specific information."""
    
    temperature: float = 0.7
    max_tokens: int = 1000
    use_for_mcp: bool = False  # Whether to apply prompt processing to MCP server responses


class MCPConfig(BaseModel):
    """Configuration for the MCP server."""
    host: str = Field(default="localhost", env="LOCALGENIUS_MCP_HOST")
    port: int = Field(default=8765, env="LOCALGENIUS_MCP_PORT")
    max_context_items: int = Field(default=10, env="LOCALGENIUS_MAX_CONTEXT_ITEMS")
    similarity_threshold: float = Field(default=0.6, env="LOCALGENIUS_SIMILARITY_THRESHOLD")


class DocumentConversionConfig(BaseModel):
    """Configuration for document conversion."""
    enabled: bool = Field(default=True, env="LOCALGENIUS_CONVERT_ENABLED")
    use_gpu: bool = Field(default=False, env="LOCALGENIUS_CONVERT_GPU")
    max_file_size_mb: int = Field(default=100, env="LOCALGENIUS_CONVERT_MAX_SIZE_MB")
    formats: List[str] = Field(
        default=['pdf', 'docx', 'pptx', 'xlsx', 'epub'],
        env="LOCALGENIUS_CONVERT_FORMATS"
    )


class Settings(BaseSettings):
    """Main settings for LocalGenius."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore',  # Ignore extra fields like openai_api_key from env
    )
    
    # OpenAI API key - always read from environment, never from config file
    openai_api_key_internal: Optional[str] = Field(None, env="OPENAI_API_KEY", exclude=True)
    
    # Configuration file path
    config_path: Path = Path.home() / ".localgenius" / "config.yaml"
    
    # Sub-configurations
    data_sources: List[DataSource] = Field(default_factory=list)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    prompts: PromptConfig = Field(default_factory=PromptConfig)
    document_conversion: DocumentConversionConfig = Field(default_factory=DocumentConversionConfig)
    
    # First run flag
    first_run: bool = True
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Always prioritize environment variable over config file."""
        import os
        return os.getenv("OPENAI_API_KEY") or self.openai_api_key_internal
    
    @classmethod
    def _load_env_files(cls):
        """Load environment variables from .env files in multiple locations."""
        try:
            from dotenv import load_dotenv
            
            # Try to load .env from multiple locations
            env_locations = [
                Path.cwd() / ".env",  # Current working directory
                Path(__file__).parent.parent.parent / ".env",  # Project root
                Path.home() / ".localgenius" / ".env",  # User config directory
            ]
            
            for env_path in env_locations:
                if env_path.exists():
                    load_dotenv(env_path)
                    break
        except ImportError:
            # python-dotenv not installed, skip .env loading
            pass
    
    @classmethod
    def load_from_file(cls, config_path: Optional[Path] = None) -> "Settings":
        """Load settings from a YAML file."""
        # Load .env files from multiple locations
        cls._load_env_files()
        settings = cls()
        
        if config_path:
            settings.config_path = config_path
            
        if settings.config_path.exists():
            with open(settings.config_path, "r") as f:
                config_data = yaml.safe_load(f) or {}
            
            # Remove any API keys from config data for security
            config_data.pop("openai_api_key", None)
                
            # Update settings with file data
            if "data_sources" in config_data:
                # Filter out data sources with non-existent paths
                valid_sources = []
                for ds in config_data["data_sources"]:
                    try:
                        valid_sources.append(DataSource(**ds))
                    except ValueError as e:
                        # Skip data sources with invalid paths
                        print(f"Warning: Skipping data source with invalid path: {e}", file=__import__('sys').stderr)
                        continue
                settings.data_sources = valid_sources
            if "embedding" in config_data:
                settings.embedding = EmbeddingConfig(**config_data["embedding"])
            if "database" in config_data:
                settings.database = DatabaseConfig(**config_data["database"])
            if "mcp" in config_data:
                settings.mcp = MCPConfig(**config_data["mcp"])
            if "prompts" in config_data:
                settings.prompts = PromptConfig(**config_data["prompts"])
            if "document_conversion" in config_data:
                settings.document_conversion = DocumentConversionConfig(**config_data["document_conversion"])
            if "first_run" in config_data:
                settings.first_run = config_data["first_run"]
            if "openai_api_key" in config_data:
                settings.openai_api_key = config_data["openai_api_key"]
                
        return settings
    
    def save_to_file(self) -> None:
        """Save current settings to YAML file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "first_run": self.first_run,
            "data_sources": [
                {
                    "path": str(ds.path),
                    "name": ds.name,
                    "enabled": ds.enabled,
                    "file_patterns": ds.file_patterns,
                    "recursive": ds.recursive,
                }
                for ds in self.data_sources
            ],
            "embedding": self.embedding.model_dump(),
            "database": {
                "path": str(self.database.path),
                "vector_dimension": self.database.vector_dimension,
            },
            "mcp": self.mcp.model_dump(),
            "prompts": self.prompts.model_dump(),
            "document_conversion": self.document_conversion.model_dump(),
        }
        
        # Never save API key to config file - always read from environment
        
        with open(self.config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)
    
    def add_data_source(self, path: Path, name: Optional[str] = None) -> None:
        """Add a new data source."""
        if name is None:
            name = path.name
            
        # Check if already exists
        for ds in self.data_sources:
            if ds.path == path:
                raise ValueError(f"Data source at {path} already exists")
                
        self.data_sources.append(DataSource(path=path, name=name))
        self.save_to_file()
    
    def remove_data_source(self, path: Path) -> None:
        """Remove a data source."""
        self.data_sources = [ds for ds in self.data_sources if ds.path != path]
        self.save_to_file()
    
    def get_active_data_sources(self) -> List[DataSource]:
        """Get all enabled data sources."""
        return [ds for ds in self.data_sources if ds.enabled]