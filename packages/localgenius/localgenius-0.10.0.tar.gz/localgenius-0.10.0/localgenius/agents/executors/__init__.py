"""Executor agents for LocalGenius."""

from .search import SearchAgent
from .rag import RAGAgent

__all__ = ['SearchAgent', 'RAGAgent']