# Core API Reference

API documentation for the Knowledge Graph Engine v2 core package.

## Package Imports

```python
from exo_graph import (
    # Core Engine
    ExoGraphEngine,
    DocumentProcessor, ProcessingResult,

    # Data Models
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet,
    SearchResult, QueryResponse,

    # Enums
    RelationshipStatus, SearchType,

    # Configuration
    Neo4jConfig, setup_neo4j_schema,

    # LLM Configuration
    LLMInterface, LLMConfig, OpenAIConfig, OllamaConfig, LiteLLMConfig,
    LLMClientFactory,

    # Utilities
    parse_date,

    # Version
    __version__
)
```

## Core Classes

### KnowledgeGraphEngineV2

Main engine class for knowledge graph operations.

```python
# Environment-based initialization (recommended)
engine = KnowledgeGraphEngineV2(neo4j_config=Neo4jConfig())

# Or with explicit LLM configuration
from exo_graph import OpenAIConfig, OllamaConfig

openai_config = OpenAIConfig(api_key="your-key", model="gpt-4o-mini")
engine = KnowledgeGraphEngineV2(llm_config=openai_config, neo4j_config=Neo4jConfig())

ollama_config = OllamaConfig(model="phi3:mini", base_url="http://localhost:11434/v1")
engine = KnowledgeGraphEngineV2(llm_config=ollama_config, neo4j_config=Neo4jConfig())
```

**Key Methods:**
- `process_input(items: List[InputItem]) -> Dict[str, Any]`
- `search(query: str, search_type: SearchType, k: int) -> QueryResponse`
- `get_node_relations(node_name: str, max_depth: int) -> List[SearchResult]`
- `analyze_conflicts(entity_name: str) -> List[Dict[str, Any]]`
- `get_stats() -> Dict[str, Any]`

### DocumentProcessor

Processes various document types and extracts knowledge into the graph.

```python
from exo_graph import DocumentProcessor, Neo4jConfig

# Initialize with default settings
processor = DocumentProcessor()

# Or with custom configuration
processor = DocumentProcessor(
    neo4j_config=Neo4jConfig(),
    chunk_size=500,
    chunk_overlap=50
)

# Process different document types
pdf_result = processor.process_pdf("document.pdf")
text_result = processor.process_text_file("notes.txt")
html_result = processor.process_html_file("webpage.html")
content_result = processor.process_text_content("Raw text content...")

# Process entire directories
results = processor.process_directory("./documents/",
                                      file_extensions=['.pdf', '.txt'])
```

**Key Methods:**
- `process_pdf(pdf_path, source_metadata=None) -> ProcessingResult`
- `process_text_file(text_path, source_metadata=None) -> ProcessingResult`
- `process_html_file(html_path, source_metadata=None) -> ProcessingResult`
- `process_text_content(content, source_metadata=None) -> ProcessingResult`
- `process_directory(directory_path, file_extensions=None, recursive=True) -> Dict[str, ProcessingResult]`
- `search(query: str, **kwargs) -> QueryResponse`
- `get_stats() -> Dict[str, Any]`

**Dependencies:**
```bash
pip install kg-engine-v2[documents]
# Includes: langchain, pypdf, unstructured
```

### LLM Configuration

#### LLMClientFactory

Factory for creating LLM configurations from environment variables or parameters.

```python
from exo_graph import LLMClientFactory

# Create from environment variables (auto-detects provider)
config = LLMClientFactory.create_from_env()

# Create from explicit parameters
config = LLMClientFactory.create_from_params(
    api_key="ollama",
    model="phi3:mini",
    base_url="http://localhost:11434/v1"
)
```

#### Configuration Classes

**OpenAIConfig:**
```python
@dataclass
class OpenAIConfig(LLMConfig):
    api_key: str
    model: str = "gpt-4o"
    base_url: Optional[str] = None
    organization: Optional[str] = None
```

**OllamaConfig:**
```python
@dataclass
class OllamaConfig(LLMConfig):
    model: str = "llama3.2:3b"
    base_url: str = "http://localhost:11434/v1"
```

**LiteLLMConfig:**
```python
@dataclass
class LiteLLMConfig(LLMConfig):
    bearer_token: str
    model: str
    base_url: str
    additional_headers: Optional[Dict[str, str]] = None
```

#### LLMInterface

Direct LLM interface for advanced usage.

```python
from exo_graph import LLMInterface, OllamaConfig

# Environment-based (uses LLMClientFactory.create_from_env())
llm = LLMInterface()

# With explicit configuration
config = OllamaConfig(model="phi3:mini")
llm = LLMInterface(llm_config=config)

# Extract entities and relationships
extracted = llm.extract_entities_relationships("Alice works at Google")
```

### Data Models

#### InputItem
```python
@dataclass
class InputItem:
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### GraphEdge
```python
@dataclass  
class GraphEdge:
    edge_id: str
    metadata: EdgeMetadata
    subject: str
    relationship: str
    object: str
```

#### EdgeMetadata
```python
@dataclass
class EdgeMetadata:
    summary: str = ""
    confidence: float = 1.0
    obsolete: bool = False
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    created_at: Optional[datetime] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    source: str = ""
    user_id: str = ""
    category: str = ""
    additional_metadata: Dict[str, Any] = field(default_factory=dict)
```

### Configuration

#### Neo4jConfig
```python
config = Neo4jConfig(
    uri="bolt://localhost:7687",
    username="neo4j", 
    password="password",
    database="neo4j"
)
```

### Utilities

#### Date Parsing

```python
from exo_graph import parse_date

date = parse_date("2024-01-15")  # ISO format
date = parse_date("January 15, 2024")  # Natural language
date = parse_date("last month")  # Relative
```

#### Edge Name Utilities

```python
from exo_graph.utils.edge_name_utils import to_natural, to_edge_name

natural = to_natural("WORKS_AT")  # "works at"
upper = to_edge_name("lives in")  # "LIVES_IN"
```

## GraphDB API

Direct database operations (available via `engine.graph_db`):

### Core Operations
- `add_edge(edge_data: GraphEdge) -> bool`
- `update_edge_metadata(edge_id: str, metadata: EdgeMetadata) -> bool`
- `delete_edge(edge_id: str) -> bool`
- `get_edge_by_id(edge_id: str) -> Optional[GraphEdge]`

### Node Operations  
- `create_node(name: str, metadata: Dict[str, Any]) -> str`
- `update_node(name: str, properties: Dict[str, Any]) -> bool`
- `delete_node(name: str, cascade: bool) -> bool`
- `merge_nodes_auto(source: str, target: str) -> Dict[str, Any]`

### Query Operations
- `vector_search(query: str, k: int) -> List[SearchResult]`
- `get_entity_relationships(entity: str, limit: int) -> List[GraphTriplet]`
- `find_relationship_paths(start: str, end: str, max_hops: int) -> List[Dict]`
- `detect_relationship_conflicts(entity: str) -> List[Dict]`

## Search Types

```python
from exo_graph import SearchType

# Direct graph traversal
response = engine.search("query", SearchType.DIRECT)

# Semantic vector search  
response = engine.search("query", SearchType.SEMANTIC)

# Hybrid approach (recommended)
response = engine.search("query", SearchType.BOTH)
```

## Error Handling

```python
from exo_graph.exceptions import (
    KGEngineError,
    Neo4jConnectionError,
    LLMError,
    ValidationError
)

try:
    result = engine.process_input([item])
except Neo4jConnectionError:
    print("Database connection failed")
except LLMError:
    print("LLM processing failed")
except ValidationError:
    print("Invalid input data")
```

## Advanced Usage

### Custom LLM Configuration
```python
# Ollama local setup
engine = KnowledgeGraphEngineV2(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    model="llama3.2:3b"
)

# Custom OpenAI-compatible endpoint
engine = KnowledgeGraphEngineV2(
    api_key="custom-key",
    base_url="https://api.custom-llm.com/v1",
    model="custom-model"
)
```

### Batch Processing
```python
# Process multiple items efficiently
items = [
    InputItem("Alice works at Google"),
    InputItem("Bob lives in SF"), 
    InputItem("Charlie knows Alice")
]

results = engine.process_input(items)
print(f"Created {results['new_edges']} relationships")
```

### Temporal Relationships
```python
# Add temporal information
item = InputItem(
    description="Alice worked at Facebook",
    metadata={
        "from_date": "2020-01-01",
        "to_date": "2023-12-31",
        "source": "linkedin"
    }
)
```

## Performance Tips

1. **Batch Operations**: Process multiple items together
2. **Connection Reuse**: Use same engine instance  
3. **Query Optimization**: Use appropriate search types
4. **Memory Management**: Clear large result sets when done
5. **Index Usage**: Ensure Neo4j indexes are created

## External Integration

For building applications on top of KG Engine:

- **REST API**: See [`kg_api_server/`](../../kg_api_server/) for FastAPI implementation
- **MCP Integration**: See [`kg_mcp_server/`](../../kg_mcp_server/) for AI assistant integration  
- **Custom Applications**: Use the core package as a dependency

## Version Information

```python
from exo_graph import __version__

print(f"KG Engine version: {__version__}")
```