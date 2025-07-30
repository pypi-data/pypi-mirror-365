# Knowledge Graph Visualization Guide

This guide explains how to visualize your knowledge graph data using the provided visualization tools.

## Overview

The `visualize_graph.py` script generates comprehensive visualizations of your Neo4j knowledge graph, creating multiple output formats for different use cases.

## Prerequisites

- Python 3.10+
- Active Neo4j database with graph data
- Required Python packages:
  ```bash
  pip install matplotlib plotly networkx
  ```

## Usage

### Basic Usage

Simply run the visualization script from the project root:

```bash
python visualize_graph.py
```

### Output Files

All outputs are saved to the `/output` directory:

1. **`knowledge_graph_relationships.txt`** - Human-readable text format
2. **`knowledge_graph_static.png`** - High-resolution static image
3. **`knowledge_graph_interactive.html`** - Interactive web visualization

### Configuration

The script uses your existing Neo4j configuration from environment variables:
- `NEO4J_URI` - Database connection URI
- `NEO4J_USERNAME` - Authentication username  
- `NEO4J_PASSWORD` - Authentication password
- `NEO4J_DATABASE` - Database name (optional)

## Output Formats

### 1. Text Output (`knowledge_graph_relationships.txt`)

Structured text file with relationships grouped by type:

```
================================================================================
KNOWLEDGE GRAPH RELATIONSHIPS
================================================================================
Total Entities: 154
Total Relationships: 140
Relationship Types: 17
================================================================================

### CREATED_THE (5 relationships)
--------------------------------------------------------------------------------
God -> CREATED_THE -> heavens (In the beginning, God created the heavens) [conf: 0.95]
God -> CREATED_THE -> earth (In the beginning, God created the earth) [conf: 0.95]
God -> CREATED_THE -> light (God said, "Let there be light," and there was light) [conf: 0.90]
...
```

Features:
- Relationships grouped by type with counts
- Format: `subject -> RELATIONSHIP -> object (summary) [conf: X.XX]`
- Confidence scores for each relationship
- Summaries truncated to 100 characters for readability

### 2. Static Visualization (`knowledge_graph_static.png`)

High-resolution PNG image suitable for:
- Presentations and reports
- Documentation
- Printing
- Quick visual overview

Features:
- **Color-coded edges** by relationship type
- **Node sizing** based on connection count (degree)
- **Spring layout** for optimal node positioning
- **Legend** showing all relationship types
- **Statistics** in the title (entities, relationships, types)

### 3. Interactive Visualization (`knowledge_graph_interactive.html`)

HTML file with interactive features:
- **Zoom and pan** to explore large graphs
- **Hover tooltips** showing:
  - Node name
  - Incoming relationships with summaries
  - Outgoing relationships with summaries
- **Draggable nodes** for manual layout adjustments
- **Responsive design** for different screen sizes

## Customization

### Engine Configuration

The visualization script works with any ExoGraphEngine configuration:

```python
# In your visualization script, you can specify custom encoder models
config = {
    "encoder_model": "all-mpnet-base-v2",
    "cross_encoder_model": "cross-encoder/ms-marco-MiniLM-L-12-v2"
}

engine = ExoGraphEngine(config=config)
# This affects the quality of entity standardization in the graph
```

### Modifying Visual Appearance

Edit `visualize_graph.py` to customize:

```python
# Change figure size
plt.figure(figsize=(20, 16))  # Width, Height in inches

# Adjust node sizes
node_sizes = [300 + 100 * G.degree(node) for node in G.nodes()]
# Base size: 300, increment: 100 per connection

# Modify layout algorithm
pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
# k: Node spacing, iterations: Layout refinement
```

### Filtering Data

Add filters to the Cypher query:

```python
query = """
MATCH (s:Entity)-[r]->(o:Entity)
WHERE r.obsolete = false
  AND r.confidence > 0.5  # Filter by confidence
  AND r.created_at > date('2024-01-01')  # Filter by date
RETURN s.name as subject, 
       type(r) as relationship, 
       o.name as object,
       r.confidence as confidence,
       r.summary as summary
ORDER BY r.confidence DESC
LIMIT 1000  # Limit results for large graphs
"""
```

## Performance Considerations

### Large Graphs

For graphs with thousands of nodes:

1. **Use filtering** to reduce data volume
2. **Increase figure size** for static images
3. **Consider clustering** similar nodes
4. **Use sampling** for initial exploration

### Memory Usage

- Static visualization: ~100MB for 1000 nodes
- Interactive visualization: Scales better with large graphs
- Text output: Minimal memory usage

## Troubleshooting

### Common Issues

1. **"No graph data found"**
   - Ensure Neo4j is running
   - Check database contains data
   - Verify connection credentials

2. **Memory errors with large graphs**
   - Add LIMIT clause to queries
   - Increase system memory
   - Use text output only

3. **Slow visualization generation**
   - Reduce spring layout iterations
   - Filter unnecessary relationships
   - Use cached layouts

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Usage

### Batch Processing

Process multiple databases:

```bash
for db in db1 db2 db3; do
    NEO4J_DATABASE=$db python visualize_graph.py
    mv output/* output_$db/
done
```

### Automated Reports

Schedule regular visualizations:

```bash
# Add to crontab
0 9 * * 1 cd /path/to/project && python visualize_graph.py
```

### Integration with Analysis

Combine with graph analysis:

```python
# After creating NetworkX graph
print(f"Graph density: {nx.density(G):.3f}")
print(f"Average clustering: {nx.average_clustering(G):.3f}")
print(f"Connected components: {nx.number_connected_components(G.to_undirected())}")

# Find important nodes
centrality = nx.degree_centrality(G)
top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
print("Most connected entities:", [node for node, _ in top_nodes])
```

## See Also

- [Architecture Overview](../architecture/overview.md)
- [Neo4j Configuration](../environment-variables.md)
- [API Documentation](../api/README.md)