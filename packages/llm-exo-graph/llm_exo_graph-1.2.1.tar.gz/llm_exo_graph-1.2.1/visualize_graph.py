#!/usr/bin/env python3
"""
Visualize the entire knowledge graph from Neo4j
Shows edge types and summaries as titles
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import logging

# Add the src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# Load environment variables
env_path = project_root / ".env"
load_dotenv(env_path)

from exo_graph.config.neo4j_config import Neo4jConfig
from exo_graph.storage.graph_db import GraphDB

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_graph_as_text(results: List[Dict], stats: Dict[str, int], output_dir: Path, filename: str = "knowledge_graph_relationships.txt"):
    """Save graph relationships as formatted text file"""
    filepath = output_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write header
        f.write("=" * 80 + "\n")
        f.write("KNOWLEDGE GRAPH RELATIONSHIPS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total Entities: {stats['total_entities']}\n")
        f.write(f"Total Relationships: {stats['total_relationships']}\n")
        f.write(f"Relationship Types: {stats['relationship_types']}\n")
        f.write("=" * 80 + "\n\n")
        
        # Group by relationship type
        grouped = {}
        for row in results:
            rel_type = row['relationship']
            if rel_type not in grouped:
                grouped[rel_type] = []
            grouped[rel_type].append(row)
        
        # Write relationships grouped by type
        for rel_type in sorted(grouped.keys()):
            f.write(f"\n### {rel_type} ({len(grouped[rel_type])} relationships)\n")
            f.write("-" * 80 + "\n")
            
            for row in grouped[rel_type]:
                subject = row['subject']
                obj = row['object']
                summary = row.get('summary', 'No summary available')
                confidence = row.get('confidence', 0.0)
                
                # Format: subject -> RELATIONSHIP -> object (summary)
                f.write(f"{subject} -> {rel_type} -> {obj}")
                if summary and summary != 'No summary available':
                    # Truncate long summaries
                    if len(summary) > 100:
                        summary = summary[:97] + "..."
                    f.write(f" ({summary})")
                f.write(f" [conf: {confidence:.2f}]\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("End of Knowledge Graph Relationships\n")
        f.write("=" * 80 + "\n")
    
    logger.info(f"Text output saved as '{filepath}'")


def fetch_graph_data(graph_db: GraphDB) -> Tuple[List[Dict], Dict[str, int]]:
    """Fetch all graph data from Neo4j"""
    query = """
    MATCH (s:Entity)-[r]->(o:Entity)
    WHERE r.obsolete = false
    RETURN s.name as subject, 
           type(r) as relationship, 
           o.name as object,
           r.confidence as confidence,
           r.summary as summary
    ORDER BY r.confidence DESC
    """
    
    results = []
    with graph_db.driver.session(database=graph_db.config.database) as session:
        result = session.run(query)
        results = [dict(record) for record in result]
    
    # Count entities
    entity_query = "MATCH (n:Entity) RETURN count(n) as count"
    with graph_db.driver.session(database=graph_db.config.database) as session:
        result = session.run(entity_query)
        entity_count = result.single()['count']
    
    # Count relationships by type
    rel_query = """
    MATCH ()-[r]->()
    WHERE r.obsolete = false
    RETURN type(r) as rel_type, count(r) as count
    ORDER BY count DESC
    """
    rel_counts = {}
    with graph_db.driver.session(database=graph_db.config.database) as session:
        result = session.run(rel_query)
        rel_counts = {record['rel_type']: record['count'] for record in result}
    
    stats = {
        'total_entities': entity_count,
        'total_relationships': len(results),
        'relationship_types': len(rel_counts)
    }
    
    return results, stats


def create_networkx_graph(results: List[Dict]) -> nx.MultiDiGraph:
    """Create NetworkX graph from query results"""
    G = nx.MultiDiGraph()
    
    for row in results:
        G.add_edge(
            row['subject'], 
            row['object'],
            relationship=row['relationship'],
            confidence=row.get('confidence', 0.5),
            summary=row.get('summary', '')
        )
    
    return G


def visualize_with_matplotlib(G: nx.MultiDiGraph, stats: Dict[str, int], output_dir: Path):
    """Create static visualization with matplotlib"""
    plt.figure(figsize=(20, 16))
    
    # Calculate node sizes based on degree
    node_sizes = [300 + 100 * G.degree(node) for node in G.nodes()]
    
    # Use spring layout for better visualization
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                          node_color='lightblue', alpha=0.7)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    
    # Draw edges with different colors for different relationship types
    edge_colors = plt.cm.tab20(range(len(set(nx.get_edge_attributes(G, 'relationship').values()))))
    rel_types = list(set(nx.get_edge_attributes(G, 'relationship').values()))
    color_map = {rel: edge_colors[i] for i, rel in enumerate(rel_types)}
    
    for (u, v, data) in G.edges(data=True):
        nx.draw_networkx_edges(G, pos, [(u, v)], 
                             edge_color=[color_map[data['relationship']]], 
                             alpha=0.5, arrows=True, 
                             arrowsize=10, width=2)
    
    # Add title and stats
    plt.title(f"Knowledge Graph Visualization\n"
              f"Entities: {stats['total_entities']} | "
              f"Relationships: {stats['total_relationships']} | "
              f"Types: {stats['relationship_types']}", 
              fontsize=16, fontweight='bold')
    
    # Add legend for relationship types
    handles = [plt.Line2D([0], [0], color=color_map[rel], lw=3, label=rel) 
              for rel in sorted(rel_types)]
    plt.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.02, 1))
    
    plt.axis('off')
    plt.tight_layout()
    filepath = output_dir / 'knowledge_graph_static.png'
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    logger.info(f"Static visualization saved as '{filepath}'")
    plt.show()


def visualize_with_plotly(G: nx.MultiDiGraph, stats: Dict[str, int], output_dir: Path):
    """Create interactive visualization with Plotly"""
    # Get position layout
    pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
    
    # Create edge traces
    edge_traces = []
    edge_annotations = []
    
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
        
        # Add edge annotation (relationship type)
        edge_annotations.append(
            dict(
                x=(x0 + x1) / 2,
                y=(y0 + y1) / 2,
                text=edge[2]['relationship'],
                showarrow=False,
                font=dict(size=8, color='red'),
                bgcolor='white',
                opacity=0.8
            )
        )
    
    # Create node trace
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            size=[10 + 5 * G.degree(node) for node in G.nodes()],
            color='lightblue',
            line=dict(width=2, color='darkblue')
        )
    )
    
    # Create hover text with relationship summaries
    hover_texts = []
    for node in G.nodes():
        edges_in = [(e[0], e[2]) for e in G.in_edges(node, data=True)]
        edges_out = [(e[1], e[2]) for e in G.out_edges(node, data=True)]
        
        hover_text = f"<b>{node}</b><br><br>"
        
        if edges_in:
            hover_text += "<b>Incoming:</b><br>"
            for source, data in edges_in[:5]:  # Limit to 5
                summary = data.get('summary', 'No summary')
                hover_text += f"← {source} ({data['relationship']}): {summary[:50]}...<br>"
        
        if edges_out:
            hover_text += "<br><b>Outgoing:</b><br>"
            for target, data in edges_out[:5]:  # Limit to 5
                summary = data.get('summary', 'No summary')
                hover_text += f"→ {target} ({data['relationship']}): {summary[:50]}...<br>"
        
        hover_texts.append(hover_text)
    
    node_trace.hovertext = hover_texts
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    # Update layout
    fig.update_layout(
        title=dict(
            text=f"Interactive Knowledge Graph<br>"
                 f"<sub>Entities: {stats['total_entities']} | "
                 f"Relationships: {stats['total_relationships']} | "
                 f"Types: {stats['relationship_types']}</sub>",
            x=0.5,
            xanchor='center'
        ),
        showlegend=False,
        hovermode='closest',
        annotations=edge_annotations,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white',
        width=1400,
        height=900
    )
    
    # Save and show
    filepath = output_dir / 'knowledge_graph_interactive.html'
    fig.write_html(filepath)
    logger.info(f"Interactive visualization saved as '{filepath}'")
    fig.show()


def main():
    """Main function to visualize the graph"""
    try:
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        logger.info(f"Output directory: {output_dir}")
        
        # Initialize Neo4j configuration
        neo4j_config = Neo4jConfig()
        
        # Verify connectivity
        logger.info("Testing Neo4j connection...")
        if not neo4j_config.verify_connectivity():
            logger.error("Failed to connect to Neo4j")
            return
        
        logger.info("Successfully connected to Neo4j")
        
        # Initialize GraphDB
        graph_db = GraphDB(neo4j_config)
        
        # Fetch graph data
        logger.info("Fetching graph data...")
        results, stats = fetch_graph_data(graph_db)
        
        if not results:
            logger.warning("No graph data found in the database")
            return
        
        logger.info(f"Found {len(results)} relationships")
        logger.info(f"Graph stats: {stats}")
        
        # Create NetworkX graph
        G = create_networkx_graph(results)
        logger.info(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Save text output
        logger.info("Saving text output...")
        save_graph_as_text(results, stats, output_dir)
        
        # Generate visualizations
        logger.info("Creating static visualization...")
        visualize_with_matplotlib(G, stats, output_dir)
        
        logger.info("Creating interactive visualization...")
        visualize_with_plotly(G, stats, output_dir)
        
        logger.info("Visualization complete!")
        
    except Exception as e:
        logger.error(f"Error during visualization: {e}", exc_info=True)
    finally:
        # Clean up Neo4j connection if needed
        if 'graph_db' in locals() and hasattr(graph_db, 'driver'):
            graph_db.driver.close()


if __name__ == "__main__":
    main()