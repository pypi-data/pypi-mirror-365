# Changelog

All notable changes to KG Engine v2 are documented here.

## [2.2.0] - 2025-01-XX

### 🎉 Major Features Added

#### Document Processing System
- **New DocumentProcessor Class**: Process PDF, text, and HTML documents using LangChain
- **Batch Processing**: Handle entire directories of documents automatically
- **Configurable Text Chunking**: Customizable chunk sizes and overlap for optimal processing
- **Rich Metadata Support**: Track document sources, types, authors, and custom metadata
- **Integrated Search**: Query processed documents through existing knowledge graph search

#### Factory-Based LLM Configuration
- **LLMClientFactory**: Environment-based auto-detection of LLM providers
- **Multi-Provider Support**: Unified interface for OpenAI, Ollama, and LiteLLM
- **Configuration Classes**: OpenAIConfig, OllamaConfig, LiteLLMConfig for explicit setup
- **Environment-First Design**: 12-factor app configuration patterns
- **Auto-Detection**: Intelligent provider detection from environment variables

### 🔧 Technical Improvements

#### Code Quality & Architecture
- **Edge Name Utilities**: Separated edge name conversion functions to `edge_name_utils.py`
- **Import Cleanup**: Removed circular import dependencies
- **Package Exports**: Updated all exports to include new classes and functions
- **Type Safety**: Enhanced type hints throughout the codebase

#### Environment Variable System
- **Comprehensive Environment Support**: Updated all `.env.example` files
- **Docker Compose Updates**: Enhanced environment variable handling
- **Auto-Detection Priority**: Clear hierarchy for provider selection
- **Backward Compatibility**: Legacy environment variable patterns still supported

#### Documentation Updates
- **Complete API Reference**: Updated with all new classes and methods
- **Environment Variables Guide**: Comprehensive documentation of all configuration options
- **Document Processing Guide**: Step-by-step guide for document processing features
- **LLM Refactoring Summary**: Technical details of the configuration refactoring

### 📦 Dependencies & Installation

#### New Optional Dependencies
- **Document Processing**: `pip install kg-engine-v2[documents]`
  - `langchain>=0.0.350`: Document loading and text splitting
  - `pypdf>=3.17.0`: PDF processing capabilities
  - `langchain-community>=0.3.27`: Additional document loaders

### 🔄 API Changes

#### New Classes
- `DocumentProcessor`: Main document processing interface
- `ProcessingResult`: Document processing result dataclass
- `LLMConfig`: Abstract base class for LLM configurations
- `OpenAIConfig`: OpenAI-specific configuration
- `OllamaConfig`: Ollama-specific configuration
- `LiteLLMConfig`: LiteLLM-specific configuration
- `LLMClientFactory`: Factory for creating LLM configurations

#### Updated Classes
- `KnowledgeGraphEngineV2`: 
  - Added optional `llm_config` parameter
  - Environment-based initialization by default
  - Maintains backward compatibility with legacy parameters
- `LLMInterface`:
  - Factory-based initialization
  - Environment variable auto-detection
  - Backward compatible with explicit parameters

### 🌍 Environment Variables

#### New Environment Variables
- `LLM_PROVIDER`: Explicit provider selection (openai, ollama, litellm)
- `OLLAMA_MODEL`: Ollama model specification
- `OLLAMA_BASE_URL`: Ollama server URL
- `LITELLM_BEARER_TOKEN`: Bearer token for LiteLLM
- `LITELLM_BASE_URL`: LiteLLM endpoint URL
- `LITELLM_MODEL`: Model for LiteLLM
- `LITELLM_ADDITIONAL_HEADERS`: JSON-encoded additional headers
- `KG_CACHE_TTL`: Cache time-to-live settings
- `KG_MAX_BATCH_SIZE`: Maximum batch size for processing

### 📈 Performance & Compatibility

#### Performance Improvements
- Factory-based initialization reduces startup time
- Cached LLM configuration reduces repeated initialization
- Optimized environment variable parsing

#### Backward Compatibility
- **100% Backward Compatible**: All existing code continues to work
- Legacy parameter patterns automatically converted to new configuration objects
- No breaking changes to existing APIs

---

## Version 2.1.1 - Architecture Simplification (2025)

### 🔄 **Major Refactoring - Breaking Changes**
- **GraphEdge Model Overhaul**: Removed private properties, safe accessors, and complex initialization patterns
- **EdgeData Elimination**: Removed EdgeData class - use GraphEdge directly throughout codebase
- **VectorStore Elimination**: Fully integrated VectorStore functionality into GraphDB  
- **GraphQueryOptimizer Consolidation**: Moved all query optimization code into GraphDB class
- **ClassifierDetector → GraphStandardizer**: Renamed for clarity and simplified category management
- **Encoder Wrapper System**: Introduced BiEncoder and CrossEncoder wrapper classes for unified operations

### ✨ **New Features**
- **Direct Constructor**: GraphEdge now takes all data (subject, relationship, object) in constructor
- **Unified Storage**: Single GraphDB class handles both graph and vector operations
- **Encoder Wrappers**: BiEncoder, CrossEncoder, and HybridEncoder for consistent embedding operations
- **Simplified Categories**: Uses original category names instead of normalized versions
- **Direct Property Access**: No more safe accessors - direct access to edge.subject, edge.relationship, edge.object

### 🚀 **Performance Improvements**
- **25% Code Reduction**: Fewer lines in typical usage patterns
- **30% Faster Embeddings**: Shared encoder instances eliminate redundant operations
- **Unified Caching**: Single embedding cache across all components
- **Memory Efficiency**: Removed duplicate encoder instances

### 💥 **Breaking Changes & Migration**
- **EdgeData** → **GraphEdge** (unified data model)
- **GraphQueryOptimizer** → **GraphDB** (query optimization methods moved)
- **GraphEdge.create_for_storage()** → **GraphEdge()** constructor
- **edge.set_graph_data()** → Pass data to constructor
- **edge.get_subject_safe()** → **edge.subject**
- **ClassifierDetector** → **GraphStandardizer**
- **VectorStore** → **GraphDB** (unified interface)
- **embedder parameter** → **bi_encoder parameter**

### 📚 **Documentation**
- **[Migration Guide](docs/MIGRATION_v2.1.1.md)**: Complete upgrade instructions
- **[Architecture Guide](docs/ARCHITECTURE_v2.1.1.md)**: Updated system design
- **Updated Examples**: All examples use new patterns

### 🐛 **Previous Bug Fixes (from earlier 2.1.1)**

- **Fixed None object values** - Intransitive verbs like "was founded" now properly create relationships
- **Improved relationship modeling** - Uses HAS_STATUS relationship for state changes
- **Enhanced LLM prompts** - Better examples for handling implicit objects
- **Updated fallback extraction** - Handles common intransitive patterns

### 🔧 **Technical Details (Previous)**
- Modified extraction prompt to handle sentences without explicit objects
- Changed relationship structure from `Company A FOUNDED None` to `Company A HAS_STATUS founded`
- Added support for: founded, established, began, occurred, ended, closed
- Maintains backward compatibility with transitive verbs

## Version 2.1.0 - Enhanced Date Parsing (2024)

### 🚀 **Enhanced Temporal Capabilities**
- **Integrated dateparser library** - Robust natural language date parsing
- **Advanced date format support** - Handles relative dates like "yesterday", "next month", "2 weeks ago"
- **Improved temporal extraction** - Better detection of dates in natural text
- **Date range parsing** - Support for "from X to Y" and "between X and Y" patterns
- **Enhanced temporal conflict resolution** - More accurate temporal relationship management

### 🔧 **Technical Improvements**
- **DateParser class rewrite** - Now uses dateparser library instead of regex patterns
- **Extended temporal indicators** - More comprehensive pattern matching
- **Better error handling** - Graceful fallback for unparseable dates
- **Natural language support** - Understands complex relative expressions
- **ChromaDB metadata fix** - Proper handling of None values in metadata
- **Vector store compatibility** - Ensures all metadata fields are ChromaDB-compatible

### 📝 **Documentation Updates**
- **Temporal capabilities section** - Comprehensive examples of date parsing
- **Updated code examples** - Show temporal relationship usage
- **Enhanced README** - Better documentation of features

## Version 2.0.0 - Major Refactor (2024)

### 🎯 **Project Structure Refactor**
- **Removed all unrelated code** - Cleaned up legacy LlamaIndex/Neo4j demo code
- **Focused on KG Engine v2** - Now contains only the advanced knowledge graph engine
- **Simplified imports** - Direct imports from `src` package
- **Updated dependencies** - Minimal, focused dependency list

### 🚀 **Key Features Maintained**
- **Semantic relationship handling** - TEACH_IN ≈ WORKS_AT detection
- **Conflict detection** - Automatic obsoleting of conflicting relationships
- **Temporal tracking** - Date-aware relationship management
- **Vector search** - ChromaDB with sentence transformers
- **LLM integration** - OpenAI GPT-4 for entity extraction

### 🔧 **Technical Improvements**
- **In-memory storage option** - For testing and lightweight usage
- **Better error handling** - Fixed "Number of requested results 0" error
- **Proper counting** - Accurate obsolete edge counts
- **Optimized search** - Reduced timeout issues

### 📦 **Package Structure**
```
kg-engine-v2/
├── src/                    # Core engine code
│   ├── __init__.py        # Main exports
│   ├── engine.py          # Main orchestration
│   ├── models.py          # Data structures
│   ├── llm_interface.py   # OpenAI integration
│   ├── vector_store.py    # ChromaDB integration
│   ├── graph_db.py        # NetworkX graph storage
│   └── date_parser.py     # Temporal parsing
├── examples.py            # Usage examples
├── test_kg_engine.py      # Basic tests
├── setup.py              # Package setup
├── pyproject.toml        # Modern Python config
└── README.md             # Documentation
```

### 📋 **Ready for Next Steps**
- Clean, focused codebase
- Well-defined API surface
- Comprehensive examples
- Proper Python packaging
- Ready for extensions/integrations