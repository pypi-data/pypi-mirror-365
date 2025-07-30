# MCP Integration Guide

Model Context Protocol (MCP) integration for Knowledge Graph Engine, designed for AI assistants like Claude, GPT, and other conversational AI systems.

## Overview

The KG MCP Server provides AI assistants with direct access to knowledge graph operations through standardized MCP tools. This enables natural language knowledge management workflows.

## Available Tools

### Knowledge Processing

#### `process_text`
Process natural language text to extract and store knowledge in the graph.

**Parameters:**
- `text` (str): Natural language text containing entity relationships
- `source` (str, optional): Source identifier for data provenance tracking

**Examples:**
```
process_text("Alice works at Google as a software engineer")
process_text("Bob moved to San Francisco last year", source="user_conversation")
```

#### `search`
Search the knowledge graph using natural language queries.

**Parameters:**
- `query` (str): Natural language search query
- `limit` (int): Maximum results to return (1-100, default: 10)
- `search_type` (str): Search method - "direct", "semantic", or "hybrid" (default: "hybrid")

**Examples:**
```
search("Who works at Google?")
search("People who know Alice", limit=5)
search("Software engineers in California", search_type="semantic")
```

### Node Operations

#### `get_node`
Retrieve all relationships connected to a specific entity.

**Parameters:**
- `node_name` (str): Entity name to explore (case-sensitive)
- `depth` (int): Graph traversal depth (1-5, default: 1)

**Examples:**
```
get_node("Alice")
get_node("Google", depth=2)
```

#### `update_node`
Update properties of an existing node.

**Parameters:**
- `node_name` (str): Name of node to update
- `properties` (dict): Properties to set/update

**Examples:**
```
update_node("Alice", {"email": "alice@example.com", "department": "Engineering"})
```

#### `delete_node`
Delete a node from the graph (PERMANENT operation).

**Parameters:**
- `node_name` (str): Name of node to delete
- `cascade` (bool): Delete all relationships (default: false)

#### `merge_nodes`
AI-powered merge of duplicate entities.

**Parameters:**
- `source_node` (str): Node to merge FROM (will be deleted)
- `target_node` (str): Node to merge INTO (will be retained)

### Edge Operations

#### `create_edge`
Create a relationship between entities.

**Parameters:**
- `subject` (str): Source entity name
- `predicate` (str): Relationship type
- `object` (str): Target entity name
- `confidence` (float): Confidence score (0.0-1.0, default: 0.8)

**Examples:**
```
create_edge("Alice", "works_at", "Google")
create_edge("Bob", "knows", "Alice", confidence=0.95)
```

#### `get_edges`
Get all relationships for a node with edge IDs.

**Parameters:**
- `node_name` (str): Node to get edges for
- `relationship_type` (str, optional): Filter by relationship type

#### `update_edge`
Update edge properties like status, dates, description.

**Parameters:**
- `edge_id` (str): Edge ID from get_edges results
- `summary` (str, optional): New description
- `status` (str, optional): "active" or "obsolete"
- `from_date` (str, optional): Start date
- `to_date` (str, optional): End date
- `obsolete` (bool): Shorthand to mark obsolete

#### `delete_edge`
Permanently delete a relationship (CAUTION: Cannot undo).

**Parameters:**
- `edge_id` (str): Edge ID from get_edges results

### System Tools

#### `get_stats`
Get graph statistics for monitoring and health checks.

**Returns:**
- `total_relationships`: All edges including obsolete
- `total_entities`: Unique nodes
- `relationship_types`: Distinct relationship types
- `engine_version`: Current KG Engine version

## Usage Patterns

### Building Knowledge Incrementally

```
# Add individual facts
process_text("Alice works at Google")
process_text("Alice lives in Mountain View")
process_text("Bob is Alice's colleague")

# Search for connections
search("Where does Alice work?")
search("Who are Alice's colleagues?")
```

### Managing Relationships

```
# Get detailed relationship info
get_edges("Alice")

# Update relationship details
update_edge("edge_123", summary="Alice was promoted to Senior Engineer", from_date="2024-01-15")

# Mark relationships as obsolete when they end
update_edge("edge_456", obsolete=true)
```

### Data Cleanup and Merging

```
# Find potential duplicates
search("Alice Smith")
search("A. Smith")

# Merge duplicate entities
merge_nodes("Alice Smith", "A. Smith")
```

### Temporal Tracking

```
# Add historical information
process_text("Alice worked at Facebook from 2020 to 2023")
process_text("Alice joined Google in January 2024")

# The system automatically handles temporal conflicts and maintains history
```

## Best Practices

### 1. Incremental Knowledge Building
- Start with basic facts and add details over time
- Use consistent entity names
- Provide context in natural language

### 2. Search Strategies
- Use "hybrid" search for best results (combines graph + semantic)
- Start with broad queries, then narrow down
- Use different search types for different needs:
  - "direct": Exact graph traversal
  - "semantic": Similarity-based matching
  - "hybrid": Best of both worlds

### 3. Relationship Management
- Use `get_edges` to understand current relationships
- Use `update_edge` instead of `delete_edge` for soft deletes
- Provide meaningful summaries for better searchability

### 4. Data Quality
- Merge duplicate entities using `merge_nodes`
- Use consistent naming conventions
- Add temporal information when available

### 5. Monitoring
- Use `get_stats` to monitor graph growth
- Check relationship counts and types
- Monitor for data quality issues

## Error Handling

All MCP tools return structured responses:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

Or for errors:

```json
{
  "success": false,
  "error": "Descriptive error message",
  "details": { ... }
}
```

## Common Workflows

### Personal Knowledge Management
1. Process meeting notes: `process_text("Discussed project X with Sarah and Tom")`
2. Search for context: `search("What did we discuss about project X?")`
3. Get person details: `get_node("Sarah")`

### Research and Documentation
1. Add paper information: `process_text("Paper by Dr. Smith on AI published in Nature 2024")`
2. Search citations: `search("Dr. Smith AI research")`
3. Link related work: `create_edge("Paper A", "cites", "Paper B")`

### Customer Relationship Management
1. Add customer info: `process_text("John from TechCorp interested in our API")`
2. Track interactions: `process_text("Had demo call with John on Friday")`
3. Search customer history: `search("TechCorp interactions")`

## Configuration

The MCP server requires the same configuration as the core KG Engine:

### Environment Variables
```bash
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# LLM Configuration
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

# Or for Ollama
LLM_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2:3b
```

## Integration Examples

### Claude Desktop
Add to Claude Desktop configuration:

```json
{
  "mcpServers": {
    "kg-engine": {
      "command": "python",
      "args": ["/path/to/kg_mcp_server/server.py"],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password",
        "OPENAI_API_KEY": "your-key"
      }
    }
  }
}
```

### Custom AI Assistant
```python
import asyncio
from mcp_client import MCPClient

async def use_kg_tools():
    client = MCPClient("http://localhost:3000/sse")
    
    # Process knowledge
    result = await client.call_tool("process_text", {
        "text": "Alice works at Google as a senior engineer"
    })
    
    # Search for information
    search_result = await client.call_tool("search", {
        "query": "Who works at Google?",
        "limit": 5
    })
    
    return search_result
```

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify Neo4j is running and accessible
2. **LLM Errors**: Check API keys and model availability
3. **Empty Results**: Try different search types or broader queries
4. **Duplicate Entities**: Use merge_nodes to consolidate

### Debug Information
```
get_stats()  # Check system health
search("test query", search_type="direct")  # Test graph connectivity
```

### Logging
Enable debug logging by setting environment variable:
```bash
PYTHONPATH=/path/to/exo_graph python server.py --log-level=DEBUG
```