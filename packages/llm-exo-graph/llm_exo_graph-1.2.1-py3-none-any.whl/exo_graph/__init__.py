"""KG Engine v2 - Advanced Knowledge Graph Engine with Semantic Search

Features:
- LLM-powered entity and relationship extraction
- Semantic relationship synonym handling (TEACH_IN ≈ WORKS_AT)
- Vector search with Neo4j and sentence transformers
- Smart duplicate detection and conflict resolution using semantic similarity
- Temporal relationship tracking with date ranges
- Hybrid search combining graph traversal and semantic similarity
- Natural language query understanding and response generation

Public API:
This package exports all classes and types needed for external usage.
"""

# Core Engine
from .core import ExoGraphEngine

# Document Processing (optional - requires langchain dependencies)
try:
    from .document_processor import DocumentProcessor, ProcessingResult
except ImportError:
    # Document processor requires additional dependencies
    DocumentProcessor = None
    ProcessingResult = None

# Data Models and Types
from .models import (
    # Core data structures
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet,
    SearchResult, QueryResponse, ExtractedInfo, ParsedQuery,
    
    # Enums
    RelationshipStatus, SearchType
)

# Configuration
from .config import Neo4jConfig
from .config.neo4j_schema import Neo4jSchemaManager, setup_neo4j_schema

# Storage Layer (for advanced usage)
from .storage import GraphDB

# LLM Interface (for advanced usage)
from .llm import (
    LLMInterface,
    LLMConfig,
    OpenAIConfig,
    OllamaConfig,
    LiteLLMConfig,
    LLMClientFactory
)

# Utilities
from .utils.date_parser import parse_date
from .utils.neo4j_index_manager import Neo4jIndexManager
from .utils.graph_standardizer import GraphStandardizer


__version__ = "1.2.1"

# Core API - Essential classes for basic usage
__core_api__ = [
    "KnowledgeGraphEngineV2",
    "InputItem", 
    "GraphEdge",
    "EdgeMetadata", 
    "GraphTriplet",
    "SearchResult",
    "QueryResponse",
    "RelationshipStatus",
    "SearchType",
    "ExtractedInfo",
    "ParsedQuery",
]

# Add document processor if available
if DocumentProcessor is not None:
    __core_api__.extend(["DocumentProcessor", "ProcessingResult"])

# Configuration API - Setup and configuration
__config_api__ = [
    "Neo4jConfig",
    "Neo4jSchemaManager", 
    "setup_neo4j_schema",
]

# Storage API - Advanced storage operations
__storage_api__ = [
    "GraphDB",
]

# LLM API - Advanced LLM operations
__llm_api__ = [
    "LLMInterface",
    "LLMConfig",
    "OpenAIConfig",
    "OllamaConfig",
    "LiteLLMConfig",
    "LLMClientFactory",
]

# Utilities API - Helper functions and optimizers
__utils_api__ = [
    "parse_date",
    "GraphStandardizer",
]

# Complete public API
__all__ = __core_api__ + __config_api__ + __storage_api__ + __llm_api__ + __utils_api__