# LLM Exo-Graph - Project Overview

## 🎯 Project Description

**LLM Exo-Graph** - An advanced knowledge graph engine that externalizes LLM memory into Neo4j, creating a persistent, searchable brain for AI systems. Built entirely on **Neo4j** for persistent graph storage and vector search capabilities, it combines graph database operations with semantic vector search to provide intelligent information storage, retrieval, and reasoning beyond context window limitations.

### Key Features
- **Neo4j-Native**: Complete Neo4j integration for both graph and vector operations
- **Enhanced Semantic Search**: Improved vector search with dynamic thresholds and contextual boosting
- **Smart Query Understanding**: Context-aware search with semantic category matching  
- **Multi-LLM Integration**: OpenAI/Ollama/LiteLLM with factory-based configuration
- **Document Processing**: PDF, text, HTML extraction with LangChain integration
- **Conflict Resolution**: Intelligent handling of contradicting information with temporal tracking
- **Environment-First Configuration**: 12-factor app patterns with auto-detection
- **Modern Architecture**: Clean, modular design with comprehensive error handling
- **Performance Optimizations**: Advanced algorithms and optimized data access
- **Graph Visualization**: Multiple output formats (text, static PNG, interactive HTML) with relationship summaries

### Technology Stack
- **Database**: Neo4j 5.x (graph + vector storage)
- **Language**: Python 3.10+
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: OpenAI/Ollama/LiteLLM with factory-based configuration
- **Document Processing**: LangChain with PDF/text/HTML loaders
- **Query Language**: Cypher
- **Vector Search**: Custom Neo4j vector store implementation

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Interface │    │   Graph Database │    │  Vector Store   │
│                 │    │                  │    │                 │
│ • Entity Extract│    │ • Neo4j Native   │    │ • Neo4j Vectors │
│ • Query Parse   │    │ • Optimizations  │    │ • Semantic      │
│ • Answer Gen.   │    │ • Optimizations  │    │ • Search        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │ LLM Exo-Graph       │
                    │  (Exocortex)        │
                    │                     │
                    │ • Process Input     │
                    │ • Smart Updates     │
                    │ • Hybrid Search     │
                    │ • Persistent Memory │
                    └─────────────────────┘
```

## 📁 Project Structure

```
src/
├── kg_engine/                    # Knowledge Graph Engine
│   ├── core/
│   │   └── engine.py            # Main KG Engine with simplified search
│   ├── models/
│   │   ├── models.py            # Data models (GraphEdge with direct constructor)
│   │   └── classifier_map.py    # Edge classifier management
│   ├── storage/
│   │   └── graph_db.py          # Neo4j unified storage (graph + vector)
│   ├── llm/
│   │   ├── llm_interface.py     # LLM integration with factory pattern
│   │   ├── llm_config.py        # LLM configuration classes
│   │   └── llm_client_factory.py # Factory for LLM client creation
│   ├── utils/
│   │   ├── encoders.py          # BiEncoder and CrossEncoder wrappers
│   │   ├── graph_standardizer.py # Edge and category standardization
│   │   ├── edge_name_utils.py   # Edge name conversion utilities
│   │   └── date_parser.py       # Temporal data parsing
│   ├── config/
│   │   ├── neo4j_config.py      # Neo4j connection configuration
│   │   └── neo4j_schema.py      # Schema management
│   ├── document_processor.py    # Document processing with LangChain
│   └── __init__.py              # Package exports
├── api/
│   └── main.py                  # FastAPI CRUD operations
├── examples/                     # Usage examples
├── tests/                       # Test suite
├── visualize_graph.py           # Graph visualization script
└── output/                      # Visualization outputs (gitignored)

kg_api_server/                   # Separate API server project
├── app/
│   └── main.py                  # FastAPI application
├── tests/                       # API tests
├── requirements.txt             # Dependencies
└── Dockerfile                   # Container config
```

## 🎯 Core Capabilities

### 1. **Intelligent Information Processing**
- Automatic entity and relationship extraction from natural language
- Semantic conflict resolution with temporal tracking
- Duplicate detection and relationship merging
- Negation handling ("Alice no longer works at...")

### 2. **Simplified Direct Search**
- **LLM Intuition-Based**: Query parsing uses pure LLM understanding without existing relationships
- **3-Step Workflow**: Parse → Standardize → Search with clean separation of concerns
- **GraphStandardizer Integration**: Intelligent edge and category standardization using vector similarity
- **List[str] Parameters**: Simple, clean interface for graph search operations
- **Removed Complexity**: Eliminated complex scoring and raw relationship handling

### 3. **Production Features**
- ACID compliance through Neo4j transactions
- Comprehensive error handling and fallback mechanisms
- Performance optimization with query analysis
- Modern Neo4j procedures (no deprecation warnings)
- Optimized queries with 50-74% performance improvements
- Query result deduplication and ranking

## 🆕 Recent Updates (v2.2.0)

### Document Processing System
- **DocumentProcessor Class**: LangChain-based PDF, text, and HTML processing
- **Batch Processing**: Handle entire directories of documents
- **Configurable Chunking**: Customizable text splitting with overlap
- **Metadata Support**: Rich document metadata and source tracking
- **Search Integration**: Query processed documents through existing search API

### Factory-Based LLM Configuration
- **LLMClientFactory**: Environment-based auto-detection of LLM providers
- **Multiple Providers**: OpenAI, Ollama, LiteLLM with unified interface
- **Environment-First**: 12-factor app configuration patterns
- **Backward Compatibility**: Legacy parameters still supported
- **Configuration Classes**: OpenAIConfig, OllamaConfig, LiteLLMConfig

### Architecture Consolidation
- **Unified Storage**: VectorStore functionality fully integrated into GraphDB
- **Encoder Wrappers**: BiEncoder and CrossEncoder classes for reusable embedding operations
- **GraphEdge Simplification**: Direct constructor pattern replacing complex initialization
- **Query Optimization**: GraphQueryOptimizer code integrated into GraphDB for better performance

### Simplified Direct Search
- **LLM Intuition-Based**: Query parsing uses pure LLM understanding without existing relationships
- **Streamlined Workflow**: Extract → Standardize → Search in simple 3-step process
- **List[str] Parameters**: Clean interface with simple string list parameters
- **Removed Complexity**: Eliminated complex scoring and raw relationship handling

### Code Reduction & Quality
- **DRY Principle**: Eliminated duplicate embedding code across components
- **Clean Architecture**: Single responsibility principle applied throughout
### Key Technical Improvements
- **Graph Standardizer**: Enhanced edge and category standardization using vector similarity
- **Embedding Management**: Centralized in ClassifierMap with cached embeddings
- **Direct Search**: Simplified 3-step workflow: Parse → Standardize → Search
- **Method Consolidation**: Removed redundant graph query optimization classes

## 📚 Documentation

Comprehensive documentation available in `/docs`:

- **[Quick Start](docs/user-guide/quick-start.md)**: Get running in 5 minutes
- **[Architecture](docs/architecture/overview.md)**: System design and components
- **[Workflows](docs/architecture/workflows.md)**: Process flows and diagrams
- **[API Reference](docs/api/README.md)**: Complete API documentation
- **[Development Guide](docs/development/migration-v2.md)**: Development setup and guidelines

## 🔧 Development Guidelines

### Code Style & Standards
- **Modular Design**: Single responsibility principle
- **Clean Architecture**: Clear separation of concerns
- **Type Hints**: Full type annotation for all functions
- **Error Handling**: Graceful degradation and comprehensive logging
- **Documentation**: Docstrings for all public methods

### AI tags
It's special snippets that attract attention of user/LLM to some piece of code(problem, uncertainty, etc).
When you get explict command ** process ai tags**, analyze parts where this point and process:
- `# AI-REVIEW` analyze give pros/const and ask to accept. when necessary ask questions, clarify
  - example: `# AI-REVIEW: This code is not very readable. Can you make it better?`
- `# AI-REFACTORING` perform refactoring to that code and all related code
  - example: `# AI-REFACTORING: Remove dublicated code, make separate function`
- `# AI-TASK` do task
  - example: `# AI-TASK: Add unit tests for this function`
When you not fully understand the task add **ai tag** with questions:
- `# AI-QUESTION` not clear how to implement.
  - example: `# AI-QUESTION: what storage is prefered? a) In-memory b) Neo4j`
When you expect or see that some work is out of task scope, add:
  - `# AI-TODO` for tasks that need to be completed later
  - example: `# AI-TODO: Add caching for classifiers`

After **ai tag** is processed - remove it

### Development Rules
- **Follow ai tags** commands: Bi-interact with user using **ai tags**  
- **Neo4j-First**: All graph operations must use Neo4j (no NetworkX, no ChromaDB)
- **Modern Standards**: Use current Neo4j procedures and avoid deprecated features
- **Unified Storage**: GraphDB handles both graph and vector operations
- **Simplified Search**: Use 3-step Parse → Standardize → Search workflow
- **Testing**: Write tests for critical functionality
- **Documentation**: Update docs when changing APIs
- **DRY Principle**: Eliminate code duplication through shared components
- **Minimal code**: Do not add any code unless it is necessary
- **Refactoring**: Do not create fallbacks and backward capabilities unless explict command
- **Maintenance**: Keep tests and examples up to date.
- **try except**: do not place `try: except:` in every function use only on top level abstractions

## 🚀 Getting Started

1. **Prerequisites**: Python 3.10+, Neo4j 5.x
2. **Installation**: `pip install -e .`
3. **Configuration**: Set up `.env` with Neo4j credentials
4. **Quick Test**: `python examples.py`

See [Quick Start Guide](docs/user-guide/quick-start.md) for detailed setup instructions.

## 🔍 Key Use Cases

- **Collaborative Knowledge Management**: Knowledge graph for relationship extraction
- **Customer Relationship Management**: Customer interactions and history
- **Research & Documentation**: Scientific papers, citations, findings
- **Business Intelligence**: Company relationships, market analysis
- **Content Management**: Document relationships, topic modeling

## 🧪 Testing

Comprehensive test suite available:
- `kg_api_server/tests/`: API server tests

Run all tests: `python -m pytest tests/`

## 🔧 Key Implementation Details

---

**Version**: 2.2.0  
**Project**: LLM Exo-Graph - AI Exocortex
**Architecture**: Neo4j-Native Knowledge Graph with Document Processing & Factory-Based LLM Configuration  
**Status**: Production Ready  
**Latest Features**: Document Processing, Factory-Based LLM Configuration, Enhanced Environment Support  
**Last Updated**: January 2025

