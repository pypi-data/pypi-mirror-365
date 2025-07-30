"""
ClassifierMap - Manages edge classifier categories from Neo4j metadata
"""
from typing import Dict, List, Optional, Set, Tuple
import logging
import numpy as np
from ..storage.graph_db import GraphDB
from ..utils.edge_name_utils import to_natural, to_edge_name

logger = logging.getLogger(__name__)


class ClassifierMap:
    """
    Manages classifier categories for edge standardization.
    
    Builds and maintains a map of categories to edge types based on 
    the 'category' field in edge metadata stored in Neo4j.
    
    Structure: Dict[category, List[edge_types]]
    Example: {"location": ["LIVES_IN", "STAY_IN"], "business": ["WORKS_AT", "HIRING"]}
    
    Internally maintains mappings between UPPER_CASE and natural language formats
    for improved embedding and similarity search accuracy.
    """
    
    def __init__(self, graph_db: GraphDB, embedder=None):
        self.graph_db = graph_db
        self.embedder = embedder  # Optional BiEncoder for embedding operations
        self.classifier_map: Dict[str, List[str]] = {}  # category -> [UPPER_CASE edges]
        self.edge_natural_map: Dict[str, str] = {}      # UPPER_CASE -> "natural text"
        self.natural_edge_map: Dict[str, str] = {}      # "natural text" -> UPPER_CASE
        
        # Embedding caches - encapsulated from GraphStandardizer
        self._category_embeddings: Dict[str, np.ndarray] = {}
        self._edge_embeddings: Dict[str, Dict[str, np.ndarray]] = {}
        
        self._load_from_neo4j()
        
        # Build embeddings if bi_encoder is provided
        if self.embedder:
            self._build_embedding_caches()
    
    def _load_from_neo4j(self) -> None:
        """
        Load classifier map from existing edge metadata in Neo4j.
        Builds map from relationships that have category field populated.
        """
        try:
            query = """
            MATCH ()-[r]->() 
            WHERE r.category IS NOT NULL AND r.category <> ''
            RETURN DISTINCT type(r) as edge_type, r.category as category, r.embedding as embedding
            ORDER BY category, edge_type
            """
            
            with self.graph_db.driver.session(database=self.graph_db.config.database) as session:
                results = session.run(query)
                
                # Build classifier map
                for record in results:
                    edge_type = record.get("edge_type")
                    category = record.get("category")
                    
                    if edge_type and category:
                        if category not in self.classifier_map:
                            self.classifier_map[category] = []
                        
                        if edge_type not in self.classifier_map[category]:
                            self.classifier_map[category].append(edge_type)
                            # Build natural language mappings
                            self._build_natural_mappings(edge_type)
            
            logger.info(f"Loaded classifier map with {len(self.classifier_map)} categories")
            logger.debug(f"Classifier map: {self.classifier_map}")
            
        except Exception as e:
            logger.error(f"Failed to load classifier map from Neo4j: {e}")
            self.classifier_map = {}
    
    def get_edges_by_classifier(self, category: str) -> List[str]:
        """
        Get all edge types for a given category in UPPER_CASE format.
        
        Args:
            category: The classifier category (e.g., 'location', 'business')
            
        Returns:
            List of edge type names for the category in UPPER_CASE format
        """
        return self.classifier_map.get(category, [])
    
    def get_natural_edges_by_classifier(self, category: str) -> List[str]:
        """
        Get all edge types for a given category in natural language format.
        
        Args:
            category: The classifier category (e.g., 'location', 'business')
            
        Returns:
            List of edge type names for the category in natural language format
        """
        upper_case_edges = self.classifier_map.get(category, [])
        return [self.get_natural_name(edge) for edge in upper_case_edges]
    
    def get_all_categories(self) -> List[str]:
        """Get all available category names."""
        return list(self.classifier_map.keys())

    def get_category_for_edge(self, edge_type: str) -> Optional[str]:
        """
        Find which category an edge type belongs to.
        
        Args:
            edge_type: The relationship type (e.g., 'LIVES_IN')
            
        Returns:
            Category name if found, None otherwise
        """
        for category, edges in self.classifier_map.items():
            if edge_type in edges:
                return category
        return None
    
    def has_category(self, category: str) -> bool:
        """Check if a category exists in the map."""
        return category in self.classifier_map
    
    def has_edge_in_category(self, category: str, edge_type: str) -> bool:
        """Check if an edge type exists in a specific category."""
        return edge_type in self.classifier_map.get(category, [])
    
    def get_or_create_edge(self, category: str, edge_name: str) -> str:
        """
        Add edge to category, creating category if needed.
        This updates the in-memory map and embeddings but doesn't persist to Neo4j.
        The category will be persisted when the edge is actually created in Neo4j.
        
        Args:
            category: The classifier category
            edge_name: The edge type name
            
        Returns:
            The edge name (for consistency)
        """
        # Normalize edge name to uppercase convention
        edge_name = edge_name.upper()
        
        # Create category if it doesn't exist
        if category not in self.classifier_map:
            self.classifier_map[category] = []
            logger.debug(f"Created new category: {category}")
            
            # Add category embedding if bi_encoder is available
            if self.embedder:
                self.add_category_embedding(category)
        
        # Add edge if not already present
        if edge_name not in self.classifier_map[category]:
            self.classifier_map[category].append(edge_name)
            # Build natural language mappings
            self._build_natural_mappings(edge_name)
            logger.debug(f"Added edge '{edge_name}' to category '{category}'")
            
            # Add edge embedding if bi_encoder is available
            if self.embedder:
                self.add_edge_embedding(category, edge_name)
        
        return edge_name
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about the classifier map."""
        total_edges = sum(len(edges) for edges in self.classifier_map.values())
        return {
            "total_categories": len(self.classifier_map),
            "total_edges": total_edges,
            "average_edges_per_category": total_edges / len(self.classifier_map) if self.classifier_map else 0
        }
    
    def __str__(self) -> str:
        """String representation of the classifier map."""
        lines = [f"ClassifierMap ({len(self.classifier_map)} categories):"]
        for category, edges in self.classifier_map.items():
            lines.append(f"  {category}: {edges}")
        return "\n".join(lines)
    
    
    def _build_natural_mappings(self, edge_type: str) -> None:
        """
        Build bidirectional mappings between UPPER_CASE and natural formats.
        
        Args:
            edge_type: Edge type in UPPER_CASE format
        """
        natural = to_natural(edge_type)
        self.edge_natural_map[edge_type] = natural
        self.natural_edge_map[natural] = edge_type
    
    def get_natural_name(self, edge_type: str) -> str:
        """
        Get natural language version of an edge type, using cache if available.
        
        Args:
            edge_type: Edge type in UPPER_CASE format
            
        Returns:
            Natural language version
        """
        if edge_type in self.edge_natural_map:
            return self.edge_natural_map[edge_type]
        
        natural = to_natural(edge_type)
        self.edge_natural_map[edge_type] = natural
        self.natural_edge_map[natural] = edge_type
        return natural
    
    def get_edge_name(self, natural_name: str) -> str:
        """
        Get UPPER_CASE version of a natural language edge name, using cache if available.
        
        Args:
            natural_name: Edge name in natural language format
            
        Returns:
            UPPER_CASE version
        """
        if natural_name in self.natural_edge_map:
            return self.natural_edge_map[natural_name]
        
        upper_case = to_edge_name(natural_name)
        self.edge_natural_map[upper_case] = natural_name
        self.natural_edge_map[natural_name] = upper_case
        return upper_case
    
    # ============= EMBEDDING MANAGEMENT METHODS =============
    
    def _build_embedding_caches(self) -> None:
        """Build embedding caches for all categories and edges."""
        if not self.embedder:
            logger.warning("No bi_encoder provided - skipping embedding cache build")
            return
            
        logger.debug("Building embedding caches...")
        
        # Build category embeddings
        self._build_category_embeddings()
        
        # Build edge embeddings by category
        self._build_edge_embeddings()
        
        logger.debug(f"Built embedding caches: {len(self._category_embeddings)} categories, "
                    f"{sum(len(edges) for edges in self._edge_embeddings.values())} edges")
    
    def _build_category_embeddings(self) -> None:
        """Create embeddings for category names."""
        categories = self.get_all_categories()
        
        if not categories:
            logger.debug("No categories found for embedding")
            return
            
        try:
            embeddings_dict = self.embedder.build_embeddings_dict(categories)
            self._category_embeddings.update(embeddings_dict)
            logger.debug(f"Created {len(embeddings_dict)} category embeddings")
        except Exception as e:
            logger.error(f"Failed to build category embeddings: {e}")
    
    def _build_edge_embeddings(self) -> None:
        """Create embeddings for edge names by category."""
        for category in self.get_all_categories():
            self._edge_embeddings[category] = {}
            
            # Get edges in natural language format
            natural_edges = self.get_natural_edges_by_classifier(category)
            
            if not natural_edges:
                continue
                
            try:
                # Build embeddings for this category
                embeddings_dict = self.embedder.build_embeddings_dict(natural_edges)
                self._edge_embeddings[category].update(embeddings_dict)
                logger.debug(f"Created {len(embeddings_dict)} edge embeddings for category '{category}'")
            except Exception as e:
                logger.error(f"Failed to build edge embeddings for category '{category}': {e}")
    
    def get_category_embeddings(self) -> Dict[str, np.ndarray]:
        """Get category embeddings dictionary."""
        return self._category_embeddings.copy()
    
    def get_edge_embeddings(self, category: str) -> Dict[str, np.ndarray]:
        """Get edge embeddings for a specific category."""
        return self._edge_embeddings.get(category, {}).copy()
    
    def get_all_edge_embeddings(self) -> Dict[str, Dict[str, np.ndarray]]:
        """Get all edge embeddings by category."""
        return {cat: edges.copy() for cat, edges in self._edge_embeddings.items()}
    
    def get_category_embedding(self, category: str) -> Optional[np.ndarray]:
        """Get embedding for a specific category."""
        return self._category_embeddings.get(category)
    
    def get_edge_embedding(self, category: str, edge_name: str) -> Optional[np.ndarray]:
        """Get embedding for a specific edge in a category."""
        category_edges = self._edge_embeddings.get(category, {})
        return category_edges.get(edge_name)
    
    def add_category_embedding(self, category: str) -> bool:
        """Add embedding for a new category."""
        if not self.embedder:
            logger.warning("No bi_encoder available for embedding generation")
            return False
            
        if category in self._category_embeddings:
            logger.debug(f"Category '{category}' already has embedding")
            return True
            
        try:
            embedding = self.embedder.encode_single(category)
            self._category_embeddings[category] = embedding
            
            # Initialize empty edge embeddings for this category
            if category not in self._edge_embeddings:
                self._edge_embeddings[category] = {}
                
            logger.debug(f"Added embedding for category '{category}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create embedding for category '{category}': {e}")
            return False
    
    def add_edge_embedding(self, category: str, edge_name: str) -> bool:
        """Add embedding for a new edge in a category."""
        if not self.embedder:
            logger.warning("No bi_encoder available for embedding generation")
            return False
            
        # Ensure category exists
        if category not in self._edge_embeddings:
            self._edge_embeddings[category] = {}
            
        # Get natural edge name for embedding
        natural_edge = self.get_natural_name(edge_name)
        
        if natural_edge in self._edge_embeddings[category]:
            logger.debug(f"Edge '{edge_name}' already has embedding in category '{category}'")
            return True
            
        try:
            embedding = self.embedder.encode_single(natural_edge)
            self._edge_embeddings[category][natural_edge] = embedding
            logger.debug(f"Added embedding for edge '{edge_name}' -> '{natural_edge}' in category '{category}'")
            return True
        except Exception as e:
            logger.error(f"Failed to create embedding for edge '{edge_name}' in category '{category}': {e}")
            return False
    
    def search_similar_categories(self, query_text: str, k: int = 10, 
                                exclude_categories: List[str] = None) -> List[Tuple[str, float]]:
        """Search for similar categories using embeddings."""
        if not self.embedder:
            logger.warning("No embedder available for category search")
            return []
            
        exclude_categories = exclude_categories or []
        
        try:
            return self.embedder.get_top_k_similar(
                query_text=query_text,
                embeddings_dict=self._category_embeddings,
                k=k,
                exclude_keys=exclude_categories
            )
        except Exception as e:
            logger.error(f"Failed to search similar categories: {e}")
            return []
    
    def search_similar_edges(self, category: str, query_text: str, k: int = 10) -> List[Tuple[str, float]]:
        """Search for similar edges within a category using embeddings."""
        if not self.embedder:
            logger.warning("No bi_encoder available for edge search")
            return []
            
        category_edges = self._edge_embeddings.get(category, {})
        if not category_edges:
            logger.debug(f"No edges found in category '{category}'")
            return []
            
        try:
            return self.embedder.get_top_k_similar(
                query_text=query_text,
                embeddings_dict=category_edges,
                k=k
            )
        except Exception as e:
            logger.error(f"Failed to search similar edges in category '{category}': {e}")
            return []