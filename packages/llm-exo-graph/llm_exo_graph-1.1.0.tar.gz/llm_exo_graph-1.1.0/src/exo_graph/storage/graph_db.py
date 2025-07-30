"""
Neo4j graph database implementation for Knowledge Graph Engine v2
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import uuid
import time

from ..models import GraphEdge, GraphTriplet, SearchResult, RelationshipStatus, EdgeMetadata
from ..config import Neo4jConfig
from ..utils.neo4j_index_manager import Neo4jIndexManager
from enum import Enum
from ..utils.encoders import BiEncoder
from ..utils.edge_name_utils import to_natural
from ..utils.date_parser import parse_date

logger = logging.getLogger(__name__)

class GraphDB:
    """Neo4j-based graph database for persistent graph storage"""
    
    def __init__(self, config: Optional[Neo4jConfig] = None, embedder: Optional[BiEncoder] = None):
        self.config = config or Neo4jConfig()
        self.driver = self.config.get_driver()
        self.entity_aliases = {}  # Store entity name variations (could be moved to Neo4j)
        self.embedder = embedder  # Store shared bi_encoder

        # Initialize optimizer
        self.neo4j_optimizer = Neo4jIndexManager(self.config)

    @staticmethod
    def _parse_record_to_edge(record_data: Dict[str, Any]) -> GraphEdge:
        """
        Unified function to parse Neo4j query records to GraphEdge objects.
        
        Args:
            record_data: Dictionary containing all relationship/node properties including
                        subject, relationship, object, edge_id, and metadata
            
        Returns:
            GraphEdge object with all data populated
        """
        # Create metadata
        metadata = EdgeMetadata(
            summary=record_data.get("summary", ""),
            created_at=parse_date(record_data.get("created_at", datetime.now())),
            from_date= parse_date(record_data.get("from_date")),
            to_date= parse_date(record_data.get("to_date")),
            obsolete=record_data.get("obsolete", False),
            status=RelationshipStatus(record_data.get("status", "active")),
            confidence=record_data.get("confidence", 1.0),
            source=record_data.get("source", ""),
            user_id=record_data.get("user_id", ""),
            category=record_data.get("category", "")
        )
        
        # Create edge with all required data from record_data
        edge = GraphEdge(
            edge_id=record_data.get("edge_id", str(uuid.uuid4())),
            metadata=metadata,
            subject=record_data.get("subject", ""),
            relationship=record_data.get("relationship", ""),
            object=record_data.get("object", "")
        )
        
        return edge

    def _triplet_node_to_edge(self, triplet_node) -> GraphEdge:
        """Convert a Triplet node from Neo4j to GraphEdge"""
        node_props = dict(triplet_node)
        return self._parse_record_to_edge(node_props)

    def _create_triplet_node_with_embedding(self, session, edge_data: GraphEdge, edge_id: str):
        """Create a Triplet node with embedding for vector search"""
        try:
            # Create text for embedding
            if edge_data.metadata.summary:
                triplet_text = edge_data.metadata.summary
            else:
                triplet_text = (f"{edge_data.subject} "
                                f"{to_natural(edge_data.relationship)} "
                                f"{edge_data.object}")

            # Generate embedding if bi_encoder is available
            embedding = None
            if self.embedder:
                try:
                    embedding = self.embedder.encode_single(triplet_text).tolist()
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for triplet: {e}")

            # Prepare date values to avoid CASE WHEN in CREATE statement
            from_date_value = None
            if edge_data.metadata.from_date:
                from_date_value = edge_data.metadata.from_date.isoformat()
                
            to_date_value = None
            if edge_data.metadata.to_date:
                to_date_value = edge_data.metadata.to_date.isoformat()
            
            # Create Triplet node with conditional date setting
            if from_date_value or to_date_value:
                # Use WITH to preprocess conditional values and SET to avoid CASE WHEN in CREATE
                session.run(
                    """
                    WITH $from_date AS from_date_str, $to_date AS to_date_str,
                         CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END AS processed_from_date,
                         CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END AS processed_to_date
                    CREATE (t:Triplet {
                        edge_id: $edge_id,
                        subject: $subject,
                        relationship: $relationship,
                        object: $object,
                        summary: $summary,
                        confidence: $confidence,
                        obsolete: $obsolete,
                        status: $status,
                        created_at: datetime($created_at),
                        from_date: processed_from_date,
                        to_date: processed_to_date,
                        source: $source,
                        user_id: $user_id,
                        category: $category,
                        embedding: $embedding
                    })
                    """,
                    edge_id=edge_id,
                    subject=edge_data.subject,
                    relationship=edge_data.relationship,
                    object=edge_data.object,
                    summary=edge_data.metadata.summary,
                    confidence=edge_data.metadata.confidence,
                    obsolete=edge_data.metadata.obsolete,
                    status=edge_data.metadata.status.value,
                    created_at=edge_data.metadata.created_at.isoformat() if edge_data.metadata.created_at else datetime.now().isoformat(),
                    from_date=from_date_value,
                    to_date=to_date_value,
                    source=edge_data.metadata.source or "",
                    user_id=edge_data.metadata.user_id or "",
                    category=edge_data.metadata.category or "",
                    embedding=embedding
                )
            else:
                # Simpler query when no dates need processing
                session.run(
                    """
                    CREATE (t:Triplet {
                        edge_id: $edge_id,
                        subject: $subject,
                        relationship: $relationship,
                        object: $object,
                        summary: $summary,
                        confidence: $confidence,
                        obsolete: $obsolete,
                        status: $status,
                        created_at: datetime($created_at),
                        from_date: null,
                        to_date: null,
                        source: $source,
                        user_id: $user_id,
                        category: $category,
                        embedding: $embedding
                    })
                    """,
                    edge_id=edge_id,
                    subject=edge_data.subject,
                    relationship=edge_data.relationship,
                    object=edge_data.object,
                    summary=edge_data.metadata.summary,
                    confidence=edge_data.metadata.confidence,
                    obsolete=edge_data.metadata.obsolete,
                    status=edge_data.metadata.status.value,
                    created_at=edge_data.metadata.created_at.isoformat() if edge_data.metadata.created_at else datetime.now().isoformat(),
                    source=edge_data.metadata.source or "",
                    user_id=edge_data.metadata.user_id or "",
                    category=edge_data.metadata.category or "",
                    embedding=embedding
                )
            
        except Exception as e:
            logger.error(f"Error creating triplet node with embedding: {e}")
            raise

    def vector_search(
            self,
            query: str,
            k: int = 10,
            index_name: str = "triplet_embedding_index",
            relationship_types: Optional[List[str]] = None,
            confidence_threshold: float = 0.3,
            filter_obsolete: bool = True
    ) -> List[SearchResult]:
        """
        Vector similarity search integrated with graph structure.

        Args:
            query: Query string to create vector from
            k: Number of results to return
            index_name: Name of the vector index to use
            relationship_types: Filter by specific relationship types
            confidence_threshold: Minimum confidence threshold
            filter_obsolete: Whether to filter out obsolete relationships

        Returns:
            List of SearchResult objects with vector scores and graph data
        """
        try:
            # Create vector from query string
            if not self.embedder:
                raise ValueError("Embedder not available for vector creation")
            
            vector = self.embedder.encode_single(query).tolist()
            
            with self.driver.session(database=self.config.database) as session:
                # Build  query based on available  patterns
                cypher_query = """
                CALL db.index.vector.queryNodes($index_name, $k_expanded, $vector) 
                YIELD node AS triplet, score
                WHERE {relationship_filter}
                  triplet.confidence >= $confidence_threshold
                  AND ($filter_obsolete = false OR triplet.obsolete = false)
                WITH triplet, score
                MATCH (subject:Entity {{name: triplet.subject}})
                MATCH (object:Entity {{name: triplet.object}})
                RETURN triplet, subject, object, score
                ORDER BY score DESC
                LIMIT $k
                """

                params = {
                    "index_name": index_name,
                    "k_expanded": k * 2,
                    "k": k,
                    "vector": vector,
                    "confidence_threshold": confidence_threshold,
                    "filter_obsolete": filter_obsolete
                }

                if relationship_types:
                    relationship_filter = "triplet.relationship IN $allowed_relationships AND"
                    params["allowed_relationships"] = relationship_types
                else:
                    relationship_filter = ""

                cypher_query = cypher_query.format(relationship_filter=relationship_filter)

                result = session.run(cypher_query, params)
                search_results = []

                for record in result:
                    try:
                        # Create GraphEdge from triplet node properties
                        triplet_node = record.get("triplet")
                        score = record.get("score", 0.0)

                        if not triplet_node:
                            continue

                        # Convert triplet node to GraphEdge
                        edge = self._triplet_node_to_edge(triplet_node)
                        triplet = GraphTriplet(edge=edge, vector_id=triplet_node.get("vector_id"))

                        search_result = SearchResult(
                            triplet=triplet,
                            score=float(score),
                            source="vector_graph",
                            explanation=f"Vector similarity with graph integration (score: {score:.3f})"
                        )
                        search_results.append(search_result)
                    except Exception as record_error:
                        logger.warning(f"Error processing search result record: {record_error}")
                        continue

                logger.info(f"Vector similarity search returned {len(search_results)} results")
                return search_results

        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            # Return empty results instead of failing completely
            return []

    def add_edge(self, edge_data: GraphEdge) -> bool:
        """Add an edge to the graph using GraphEdge"""
        try:

            edge_id = edge_data.edge_id or str(uuid.uuid4())
                
            with self.driver.session(database=self.config.database) as session:
                # Create or merge entities
                session.run(
                    """
                    MERGE (subject:Entity {name: $subject_name})
                    ON CREATE SET subject.created_at = datetime()
                    
                    MERGE (object:Entity {name: $object_name})
                    ON CREATE SET object.created_at = datetime()
                    """,
                    subject_name=edge_data.subject,
                    object_name=edge_data.object
                )
                
                # Create the edge with dynamic relationship type
                # Prepare date values to avoid CASE WHEN in CREATE statement
                from_date_value = edge_data.metadata.from_date.isoformat() if edge_data.metadata.from_date else None
                to_date_value = edge_data.metadata.to_date.isoformat() if edge_data.metadata.to_date else None
                
                if from_date_value or to_date_value:
                    # Use WITH to preprocess conditional values and avoid CASE WHEN in CREATE
                    query = f"""
                        WITH $from_date AS from_date_str, $to_date AS to_date_str,
                             CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END AS processed_from_date,
                             CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END AS processed_to_date
                        MATCH (subject:Entity {{name: $subject_name}})
                        MATCH (object:Entity {{name: $object_name}})
                        CREATE (subject)-[r:`{edge_data.relationship}` {{
                            edge_id: $edge_id,
                            summary: $summary,
                            obsolete: $obsolete,
                            status: $status,
                            confidence: $confidence,
                            created_at: datetime($created_at),
                            from_date: processed_from_date,
                            to_date: processed_to_date,
                            source: $source,
                            user_id: $user_id,
                            category: $category
                        }}]->(object)
                        RETURN r
                    """
                else:
                    # Simpler query when no dates need processing
                    query = f"""
                        MATCH (subject:Entity {{name: $subject_name}})
                        MATCH (object:Entity {{name: $object_name}})
                        CREATE (subject)-[r:`{edge_data.relationship}` {{
                            edge_id: $edge_id,
                            summary: $summary,
                            obsolete: $obsolete,
                            status: $status,
                            confidence: $confidence,
                            created_at: datetime($created_at),
                            from_date: null,
                            to_date: null,
                            source: $source,
                            user_id: $user_id,
                            category: $category
                        }}]->(object)
                        RETURN r
                    """
                
                result = session.run(
                    query,
                    subject_name=edge_data.subject,
                    object_name=edge_data.object,
                    edge_id=edge_id,
                    summary=edge_data.metadata.summary,
                    obsolete=edge_data.metadata.obsolete,
                    status=edge_data.metadata.status.value,
                    confidence=edge_data.metadata.confidence,
                    created_at=edge_data.metadata.created_at.isoformat() if edge_data.metadata.created_at else datetime.now().isoformat(),
                    from_date=from_date_value,
                    to_date=to_date_value,
                    source=edge_data.metadata.source or "",
                    user_id=edge_data.metadata.user_id or "",
                    category=edge_data.metadata.category or ""
                )
                
                if result.single():
                    # Also create a Triplet node with embedding for vector search
                    try:
                        self._create_triplet_node_with_embedding(session, edge_data, edge_id)
                    except Exception as e:
                        logger.warning(f"Failed to create triplet node with embedding: {e}")
                    
                    logger.info(f"Added edge: {edge_data.subject} -{edge_data.relationship}-> {edge_data.object}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error adding edge to graph: {e}")
            return False

    
    def update_edge_metadata(self, edge_id: str, metadata: EdgeMetadata) -> bool:
        """Update metadata for an existing edge (relationship type agnostic)"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Find edge by ID regardless of relationship type
                result = session.run(
                    """
                    WITH $from_date AS from_date_str, $to_date AS to_date_str,
                         CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END AS processed_from_date,
                         CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END AS processed_to_date
                    MATCH ()-[r {edge_id: $edge_id}]->()
                    SET r.summary = $summary,
                        r.obsolete = $obsolete,
                        r.status = $status,
                        r.confidence = $confidence,
                        r.created_at = datetime($created_at),
                        r.from_date = processed_from_date,
                        r.to_date = processed_to_date,
                        r.source = $source,
                        r.user_id = $user_id,
                        r.category = $category
                    RETURN r
                    """,
                    edge_id=edge_id,
                    summary=metadata.summary,
                    obsolete=metadata.obsolete,
                    status=metadata.status.value,
                    confidence=metadata.confidence,
                    created_at=metadata.created_at.isoformat() if metadata.created_at else datetime.now().isoformat(),
                    from_date=metadata.from_date.isoformat() if metadata.from_date else None,
                    to_date=metadata.to_date.isoformat() if metadata.to_date else None,
                    source=metadata.source or "",
                    user_id=metadata.user_id or "",
                    category=metadata.category or ""
                )
                
                if result.single():
                    # Also update the corresponding Triplet node
                    try:
                        session.run(
                            """
                            WITH $from_date AS from_date_str, $to_date AS to_date_str,
                                 CASE WHEN $from_date IS NOT NULL THEN datetime($from_date) ELSE null END AS processed_from_date,
                                 CASE WHEN $to_date IS NOT NULL THEN datetime($to_date) ELSE null END AS processed_to_date
                            MATCH (t:Triplet {edge_id: $edge_id})
                            SET t.summary = $summary,
                                t.obsolete = $obsolete,
                                t.status = $status,
                                t.confidence = $confidence,
                                t.from_date = processed_from_date,
                                t.to_date = processed_to_date,
                                t.source = $source,
                                t.user_id = $user_id,
                                t.category = $category
                            """,
                            edge_id=edge_id,
                            summary=metadata.summary,
                            obsolete=metadata.obsolete,
                            status=metadata.status.value,
                            confidence=metadata.confidence,
                            from_date=metadata.from_date.isoformat() if metadata.from_date else None,
                            to_date=metadata.to_date.isoformat() if metadata.to_date else None,
                            source=metadata.source or "",
                            user_id=metadata.user_id or "",
                            category=metadata.category or ""
                        )
                    except Exception as e:
                        logger.warning(f"Failed to update triplet node: {e}")
                    
                    logger.info(f"Updated edge metadata: {edge_id}")
                    return True
                else:
                    logger.warning(f"Edge not found: {edge_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating edge: {e}")
            return False
    
    def update_edge(self, edge: GraphEdge) -> bool:
        """Update an existing edge - only updates metadata"""
        return self.update_edge_metadata(edge.edge_id, edge.metadata)
    
    def delete_edge(self, edge_id: str) -> bool:
        """Delete an edge from the graph (relationship type agnostic)"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH ()-[r {edge_id: $edge_id}]->()
                    DELETE r
                    RETURN count(r) as deleted_count
                    """,
                    edge_id=edge_id
                )
                
                deleted_count = result.single()["deleted_count"]
                if deleted_count > 0:
                    # Also delete the corresponding Triplet node
                    try:
                        session.run(
                            """
                            MATCH (t:Triplet {edge_id: $edge_id})
                            DELETE t
                            """,
                            edge_id=edge_id
                        )
                    except Exception as e:
                        logger.warning(f"Failed to delete triplet node: {e}")
                    
                    logger.info(f"Deleted edge: {edge_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting edge: {e}")
            return False
    
    def find_edges(self, subject: str = None, relationship: str = None, 
                   obj: str = None, filter_obsolete: bool = True) -> List[GraphTriplet]:
        """Find edges matching the given criteria"""
        results = []
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build the query dynamically based on provided criteria
                where_clauses = []
                params = {}
                
                if subject:
                    where_clauses.append("s.name = $subject")
                    params["subject"] = subject
                    
                if obj:
                    where_clauses.append("o.name = $object")
                    params["object"] = obj
                    
                if filter_obsolete:
                    where_clauses.append("r.obsolete = false")
                
                # If relationship is specified, match specific type
                if relationship:
                    query_parts = [f"MATCH (s:Entity)-[r:`{relationship}`]->(o:Entity)"]
                else:
                    # Match any relationship type
                    query_parts = ["MATCH (s:Entity)-[r]->(o:Entity)"]
                
                if where_clauses:
                    query_parts.append("WHERE " + " AND ".join(where_clauses))
                
                query_parts.append("RETURN s, r, o, type(r) as rel_type")
                query = "\n".join(query_parts)
                
                result = session.run(query, params)
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"], record["rel_type"])
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                
                return results
                
        except Exception as e:
            logger.error(f"Error finding edges: {e}")
            return []
    
    def find_conflicting_edges(self, edge_data: GraphEdge) -> List[GraphEdge]:
        """Find edges that would conflict with the new edge"""
        conflicts = []
        
        try:
            # Validate edge data before querying
            if not edge_data.subject or not edge_data.relationship or not edge_data.object:
                logger.warning(f"Cannot find conflicts for edge with missing fields: subject={edge_data.subject}, relationship={edge_data.relationship}, object={edge_data.object}")
                return []
            
            with self.driver.session(database=self.config.database) as session:
                # Look for edges with same subject and relationship type but different object
                query = f"""
                    MATCH (s:Entity {{name: $subject}})
                          -[r:`{edge_data.relationship}`]->
                          (o:Entity)
                    WHERE o.name <> $object AND r.obsolete = false
                    RETURN s, r, o, type(r) as rel_type
                """
                
                result = session.run(
                    query,
                    subject=edge_data.subject,
                    object=edge_data.object
                )
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"], record["rel_type"])
                    conflicts.append(edge)
                
                return conflicts
                
        except Exception as e:
            logger.error(f"Error finding conflicts: {e}")
            return []
    
    def detect_relationship_conflicts(
        self,
        entity_name: Optional[str] = None,
        relationship_type: Optional[str] = None,
        confidence_threshold: float = 0.5,
        limit: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Advanced conflict detection
        
        Args:
            entity_name: Specific entity to check for conflicts
            relationship_type: Specific relationship type to check
            confidence_threshold: Minimum confidence for considering conflicts
            limit: Maximum number of conflicts to return
            
        Returns:
            List of conflict information dictionaries
        """
        try:
            # Custom query for relationship-based storage
            with self.driver.session(database=self.config.database) as session:
                # Build dynamic query based on parameters
                entity_filter = ""
                params = {"confidence_threshold": confidence_threshold, "limit": limit}
                
                if entity_name:
                    entity_filter = "AND (startNode(r1).name = $entity_name OR endNode(r1).name = $entity_name)"
                    params["entity_name"] = entity_name
                
                if relationship_type:
                    rel_type_filter = f":{relationship_type}"
                else:
                    rel_type_filter = ""
                
                # Query to find conflicting relationships
                query = f"""
                    MATCH (subject:Entity)
                    MATCH (subject)-[r1{rel_type_filter}]->(obj1:Entity)
                    MATCH (subject)-[r2{rel_type_filter}]->(obj2:Entity)
                    WHERE r1.obsolete = false
                      AND r2.obsolete = false
                      AND r1.confidence >= $confidence_threshold
                      AND r2.confidence >= $confidence_threshold
                      AND obj1 <> obj2
                      AND elementId(r1) < elementId(r2)
                      {entity_filter}
                    RETURN subject.name as conflicted_entity,
                           type(r1) as conflicted_relationship,
                           [obj1.name, obj2.name] as conflicting_objects,
                           abs(r1.confidence - r2.confidence) as confidence_diff,
                           r1, r2, obj1, obj2
                    ORDER BY confidence_diff ASC
                    LIMIT $limit
                """
                
                result = session.run(query, params)
                
                conflicts = []
                for record in result:
                    # Get the subject entity node
                    subject_entity = {"name": record["conflicted_entity"]}
                    
                    # Create edge objects for the conflicting relationships
                    edge1 = self._record_to_edge(
                        subject_entity, record["r1"], record["obj1"], record["conflicted_relationship"]
                    )
                    edge2 = self._record_to_edge(
                        subject_entity, record["r2"], record["obj2"], record["conflicted_relationship"]  
                    )
                    
                    conflict_info = {
                        "conflicted_entity": record["conflicted_entity"],
                        "conflicted_relationship": record["conflicted_relationship"],
                        "conflicting_objects": record["conflicting_objects"],
                        "confidence_diff": record["confidence_diff"],
                        "higher_confidence_edge": edge1 if record["r1"]["confidence"] > record["r2"]["confidence"] else edge2,
                        "lower_confidence_edge": edge1 if record["r1"]["confidence"] <= record["r2"]["confidence"] else edge2
                    }
                    conflicts.append(conflict_info)
                
                logger.info(f"Detected {len(conflicts)} relationship conflicts")
                return conflicts
            
        except Exception as e:
            logger.error(f"Error in conflict detection: {e}")
            return []
    
    def find_relationship_paths(
        self,
        start_entity: str,
        end_entity: str,
        max_hops: int = 4,
        avoid_obsolete: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find relationship paths between two entities.
        
        Args:
            start_entity: Starting entity name
            end_entity: Target entity name
            max_hops: Maximum number of hops
            avoid_obsolete: Whether to avoid obsolete relationships
            limit: Maximum number of paths to return
            
        Returns:
            List of path information dictionaries
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                obsolete_condition = "r.obsolete = false AND" if avoid_obsolete else ""
                
                query = f"""
                MATCH (start:Entity {{name: $start_entity}})
                MATCH (end:Entity {{name: $end_entity}})
                MATCH path = shortestPath((start)-[*1..{max_hops}]-(end))
                WHERE ALL(r IN relationships(path) WHERE {obsolete_condition} r.confidence >= 0.5)
                WITH path, 
                     reduce(conf = 1.0, r IN relationships(path) | conf * r.confidence) as path_confidence,
                     [r IN relationships(path) | type(r)] as relationship_chain
                RETURN path, path_confidence, relationship_chain,
                       length(path) as path_length,
                       nodes(path) as entities_in_path
                ORDER BY path_length ASC, path_confidence DESC
                LIMIT $limit
                """
                
                result = session.run(query, {
                    "start_entity": start_entity,
                    "end_entity": end_entity,
                    "limit": limit
                })
                
                paths_data = []
                for record in result:
                    path_info = {
                        "start_entity": start_entity,
                        "end_entity": end_entity,
                        "path_length": record["path_length"],
                        "path_confidence": record["path_confidence"],
                        "relationship_chain": record["relationship_chain"],
                        "entities_in_path": [node["name"] for node in record["entities_in_path"]],
                        "path": record["path"]
                    }
                    paths_data.append(path_info)
                
                logger.info(f"Found {len(paths_data)} paths from {start_entity} to {end_entity}")
                return paths_data
            
        except Exception as e:
            logger.error(f"Error in path finding: {e}")
            return []
    
    def discover_relationship_patterns(
        self,
        pattern_description: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Discover complex relationship patterns
        
        Args:
            pattern_description: Natural language description of pattern
            limit: Maximum number of results
            
        Returns:
            List of pattern match information
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                query = """
                MATCH (t:Triplet)
                WHERE t.summary CONTAINS $pattern_description
                  AND t.obsolete = false
                MATCH (subject:Entity {name: t.subject})
                MATCH (object:Entity {name: t.object})
                RETURN t, subject, object,
                       t.confidence as confidence
                ORDER BY t.confidence DESC
                LIMIT $limit
                """
                
                result = session.run(query, {
                    "pattern_description": pattern_description, 
                    "limit": limit
                })
                
                patterns_data = []
                for record in result:
                    pattern_info = {
                        "pattern_type": "single_triplet",
                        "triplet": self._triplet_node_to_edge(record["t"]),
                        "subject": record.get("subject"),
                        "object": record.get("object"),
                        "confidence": record["confidence"]
                    }
                    patterns_data.append(pattern_info)
                
                logger.info(f"Discovered {len(patterns_data)} patterns for '{pattern_description}'")
                return patterns_data
            
        except Exception as e:
            logger.error(f"Error in pattern discovery: {e}")
            return []
    
    def find_duplicate_edges(self, edge_data: GraphEdge) -> List[GraphEdge]:
        """Find exact duplicate edges"""
        duplicates = []
        
        try:
            # Validate edge data before querying
            if not edge_data.subject or not edge_data.relationship or not edge_data.object:
                logger.warning(f"Cannot find duplicates for edge with missing fields: subject={edge_data.subject}, relationship={edge_data.relationship}, object={edge_data.object}")
                return []
            
            with self.driver.session(database=self.config.database) as session:
                query = f"""
                    MATCH (s:Entity {{name: $subject}})
                          -[r:`{edge_data.relationship}`]->
                          (o:Entity {{name: $object}})
                    WHERE r.obsolete = false
                    RETURN s, r, o, type(r) as rel_type
                """
                
                result = session.run(
                    query,
                    subject=edge_data.subject,
                    object=edge_data.object
                )
                
                for record in result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"], record["rel_type"])
                    duplicates.append(edge)
                
                return duplicates
                
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []
    
    def get_entity_relationships(
        self, 
        entity: str, 
        filter_obsolete: bool = True,
        max_depth: int = 1,
        relationship_types: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[GraphTriplet]:
        """
        Exploration of entity relationship exploration with depth control.
        
        Args:
            entity: Entity name to explore
            filter_obsolete: Whether to filter obsolete relationships
            max_depth: Maximum relationship depth (1 for direct, 2+ for multi-hop)
            relationship_types: Specific relationship types to include
            limit: Maximum number of results
            
        Returns:
            List of GraphTriplet objects
        """
        with self.driver.session(database=self.config.database) as session:
            rel_filter = ""
            if relationship_types:
                rel_types = "|".join(relationship_types)
                rel_filter = f":{rel_types}"

            obsolete_filter = "WHERE r.obsolete = false" if filter_obsolete else ""

            if max_depth == 1:
                query = f"""
                MATCH (start:Entity {{name: $entity_name}})
                MATCH (start)-[r{rel_filter}]-(connected:Entity)
                {obsolete_filter}
                RETURN start, r, connected, 
                       r.confidence as confidence,
                       type(r) as relationship_type
                ORDER BY r.confidence DESC
                LIMIT $limit
                """
            else:
                obsolete_check = "" if not filter_obsolete else "r.obsolete = false AND"
                rel_check = "true" if not relationship_types else f"type(r) IN {relationship_types}"

                query = f"""
                MATCH (start:Entity {{name: $entity_name}})
                MATCH path = (start)-[*1..{max_depth}]-(connected:Entity)
                WHERE ALL(r IN relationships(path) WHERE {obsolete_check} {rel_check})
                WITH start, connected, path, 
                     reduce(conf = 1.0, r IN relationships(path) | conf * r.confidence) as path_confidence
                RETURN start, connected, path, path_confidence,
                       length(path) as path_length
                ORDER BY path_confidence DESC, path_length ASC
                LIMIT $limit
                """

            result = session.run(query, {"entity_name": entity, "limit": limit})

            results = []
            for record in result:
                if max_depth == 1:
                    edge = self._record_to_edge(
                        record["start"],
                        record["r"],
                        record["connected"],
                        record.get("relationship_type", "RELATES_TO")
                    )
                    triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                    results.append(triplet)
                else:
                    # Multi-hop results
                    path = record["path"]
                    nodes = path.nodes
                    relationships = path.relationships

                    for i, rel in enumerate(relationships):
                        if i < len(nodes) - 1:
                            subject_node = nodes[i]
                            object_node = nodes[i + 1]
                            edge = self._record_to_edge(
                                subject_node, rel, object_node, rel.type
                            )
                            triplet = GraphTriplet(edge=edge, vector_id=edge.edge_id)
                            results.append(triplet)

            logger.info(f"Entity exploration returned {len(results)} results for {entity}")
            return results
            

    def get_entities(self) -> List[str]:
        """Get all entities in the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run("MATCH (e:Entity) RETURN e.name as name")
                return [record["name"] for record in result]
                
        except Exception as e:
            logger.error(f"Error getting entities: {e}")
            return []
    
    def get_relationships(self) -> List[str]:
        """Get all relationship types in the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get all relationship types using CALL db.relationshipTypes()
                result = session.run(
                    """
                    CALL db.relationshipTypes() YIELD relationshipType
                    RETURN relationshipType
                    """
                )
                return [record["relationshipType"] for record in result]
                
        except Exception as e:
            logger.error(f"Error getting relationships: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get entity count
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                
                # Get edge counts (all relationship types)
                edge_stats = session.run(
                    """
                    MATCH ()-[r]->()
                    WHERE r.edge_id IS NOT NULL
                    RETURN count(r) as total,
                           sum(CASE WHEN r.obsolete = false OR r.obsolete IS NULL THEN 1 ELSE 0 END) as active,
                           sum(CASE WHEN r.obsolete = true THEN 1 ELSE 0 END) as obsolete
                    """
                ).single()
                
                # Get relationship types
                relationships = self.get_relationships()
                
                return {
                    "total_entities": entity_count,
                    "total_edges": edge_stats["total"] or 0,
                    "active_edges": edge_stats["active"] or 0,
                    "obsolete_edges": edge_stats["obsolete"] or 0,
                    "relationship_types": len(relationships),
                    "relationships": relationships[:20]  # Show first 20
                }
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    

    def clear_graph(self) -> bool:
        """Clear all data from the graph"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Delete all relationships and nodes
                session.run("MATCH (n) DETACH DELETE n")
                self.entity_aliases.clear()
                logger.info("Cleared all graph data")
                return True
                
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            return False
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export graph data to dictionary for serialization"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Export edges (all relationship types)
                edges_result = session.run(
                    """
                    MATCH (s:Entity)-[r]->(o:Entity)
                    WHERE r.edge_id IS NOT NULL
                    RETURN s, r, o, type(r) as rel_type
                    """
                )
                
                edges = []
                for record in edges_result:
                    edge = self._record_to_edge(record["s"], record["r"], record["o"], record["rel_type"])
                    edge_dict = edge.to_dict()
                    # Include relationship type in export
                    edge_dict['relationship_type'] = record["rel_type"]
                    edges.append(edge_dict)
                
                return {
                    "edges": edges,
                    "aliases": self.entity_aliases,
                    "stats": self.get_stats()
                }
                
        except Exception as e:
            logger.error(f"Error exporting graph: {e}")
            return {"error": str(e)}
    
    def import_from_dict(self, data: Dict[str, Any]) -> bool:
        """Import graph data from dictionary"""
        try:
            # Clear existing data
            self.clear_graph()
            
            # Import aliases
            if "aliases" in data:
                self.entity_aliases = data["aliases"]
            
            # Import edges
            if "edges" in data:
                
                for edge_dict in data["edges"]:
                    # Reconstruct metadata
                    metadata_data = edge_dict["metadata"]
                    
                    metadata = EdgeMetadata(
                        summary=metadata_data["summary"],
                        created_at=datetime.fromisoformat(metadata_data["created_at"]),
                        from_date=datetime.fromisoformat(metadata_data["from_date"]) if metadata_data.get("from_date") else None,
                        to_date=datetime.fromisoformat(metadata_data["to_date"]) if metadata_data.get("to_date") else None,
                        obsolete=metadata_data.get("obsolete", False),
                        result=metadata_data.get("result"),
                        status=RelationshipStatus(metadata_data.get("status", "active")),
                        confidence=metadata_data.get("confidence", 1.0),
                        source=metadata_data.get("source"),
                        user_id=metadata_data.get("user_id")
                    )
                    
                    # Use GraphEdge for import with relationship type
                    rel_type = edge_dict.get("relationship_type") or edge_dict.get("relationship", "RELATES_TO")
                    edge_data = GraphEdge(
                        subject=edge_dict["subject"],
                        relationship=rel_type,
                        object=edge_dict["object"],
                        metadata=metadata,
                        edge_id=edge_dict["edge_id"]
                    )
                    
                    self.add_edge(edge_data)
            
            logger.info(f"Imported {len(data.get('edges', []))} edges")
            return True
            
        except Exception as e:
            logger.error(f"Error importing graph data: {e}")
            return False
    
    def _record_to_edge(self, subject_node, relationship, object_node, rel_type: str) -> GraphEdge:
        """Convert Neo4j record to GraphEdge with dynamic relationship type"""
        # Extract relationship properties and combine with entity names
        record_data = dict(relationship)
        
        # Add subject, object, and relationship type to record_data
        record_data.update({
            "subject": subject_node["name"],
            "relationship": rel_type,
            "object": object_node["name"]
        })
        
        # Use unified parsing function
        return self._parse_record_to_edge(record_data)
    
    # ====== NODE CRUD OPERATIONS ======
    
    def create_node(self, name: str, metadata: Dict[str, Any] = None) -> str:
        """
        Create a new node in the graph.
        
        Args:
            name: Node name/identifier
            metadata: Additional properties for the node
            
        Returns:
            The node name if successful
            
        Raises:
            ValueError: If node already exists
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                # Check if node already exists
                check_query = "MATCH (n:Entity {name: $name}) RETURN n"
                result = session.run(check_query, name=name)
                if result.single():
                    raise ValueError(f"Node '{name}' already exists")
                
                # Create node with metadata
                node_metadata = metadata or {}
                node_metadata.update({
                    "created_at": datetime.now().isoformat()
                })
                
                # Build CREATE query dynamically
                properties = ", ".join([f"{k}: ${k}" for k in node_metadata.keys()])
                create_query = f"CREATE (n:Entity {{name: $name, {properties}}})"
                
                params = {"name": name}
                params.update(node_metadata)
                
                session.run(create_query, params)
                logger.info(f"Created node '{name}'")
                return name
                
        except Exception as e:
            logger.error(f"Error creating node '{name}': {e}")
            raise
    
    def get_node(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a node and its properties.
        
        Args:
            name: Node name to retrieve
            
        Returns:
            Node properties as dictionary, or None if not found
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                query = "MATCH (n:Entity {name: $name}) RETURN n"
                result = session.run(query, name=name)
                record = result.single()
                
                if record:
                    node = record["n"]
                    # Convert Neo4j node to dictionary
                    node_dict = dict(node)
                    return node_dict
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving node '{name}': {e}")
            return None
    
    def update_node(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Update node properties.
        
        Args:
            name: Node name to update
            properties: Properties to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build SET clause dynamically
                set_clauses = [f"n.{k} = ${k}" for k in properties.keys()]
                set_clause = ", ".join(set_clauses)
                
                query = f"MATCH (n:Entity {{name: $name}}) SET {set_clause}, n.updated_at = $updated_at"
                
                params = {"name": name, "updated_at": datetime.now().isoformat()}
                params.update(properties)
                
                result = session.run(query, params)
                summary = result.consume()
                
                if summary.counters.properties_set > 0:
                    logger.info(f"Updated node '{name}' with {len(properties)} properties")
                    return True
                else:
                    logger.warning(f"Node '{name}' not found for update")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating node '{name}': {e}")
            return False
    
    def delete_node(self, name: str, cascade: bool = True) -> bool:
        """
        Delete a node from the graph.
        
        Args:
            name: Node name to delete
            cascade: Whether to delete connected relationships
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                if cascade:
                    # Delete node and all its relationships
                    query = "MATCH (n:Entity {name: $name}) DETACH DELETE n"
                else:
                    # Check if node has relationships
                    check_query = "MATCH (n:Entity {name: $name})-[r]-() RETURN count(r) as rel_count"
                    result = session.run(check_query, name=name)
                    record = result.single()
                    
                    if record and record["rel_count"] > 0:
                        logger.warning(f"Cannot delete node '{name}': has {record['rel_count']} relationships")
                        return False
                    
                    # Delete node only
                    query = "MATCH (n:Entity {name: $name}) DELETE n"
                
                result = session.run(query, name=name)
                summary = result.consume()
                
                if summary.counters.nodes_deleted > 0:
                    logger.info(f"Deleted node '{name}' (cascade={cascade})")
                    return True
                else:
                    logger.warning(f"Node '{name}' not found for deletion")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting node '{name}': {e}")
            return False
    
    # ====== EDGE CRUD OPERATIONS ======
    
    def create_edge(self, subject: str, relationship: str, object_name: str, metadata: EdgeMetadata) -> str:
        """
        Create a new edge/relationship between two nodes.
        
        Args:
            subject: Source node name
            relationship: Relationship type (e.g., "WORKS_AT")
            object_name: Target node name
            metadata: Edge metadata
            
        Returns:
            Edge ID if successful
            
        Raises:
            ValueError: If nodes don't exist
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                # Check if both nodes exist
                check_query = """
                MATCH (s:Entity {name: $subject})
                MATCH (o:Entity {name: $object})
                RETURN s, o
                """
                result = session.run(check_query, subject=subject, object=object_name)
                if not result.single():
                    raise ValueError(f"One or both nodes don't exist: '{subject}', '{object_name}'")
                
                # Create edge with metadata
                edge_id = str(uuid.uuid4())
                
                # Build relationship properties
                rel_props = {
                    "edge_id": edge_id,
                    "summary": metadata.summary or "",
                    "confidence": metadata.confidence,
                    "obsolete": metadata.obsolete,
                    "status": metadata.status.value,
                    "created_at": metadata.created_at.isoformat() if metadata.created_at else datetime.now().isoformat(),
                    "source": metadata.source or ""
                }
                
                # Add optional date fields
                if metadata.from_date:
                    rel_props["from_date"] = metadata.from_date.isoformat()
                if metadata.to_date:
                    rel_props["to_date"] = metadata.to_date.isoformat()
                if metadata.user_id:
                    rel_props["user_id"] = metadata.user_id
                
                # Build properties string for query
                props_str = ", ".join([f"{k}: ${k}" for k in rel_props.keys()])
                
                # Create relationship with dynamic type
                create_query = f"""
                MATCH (s:Entity {{name: $subject}})
                MATCH (o:Entity {{name: $object}})
                CREATE (s)-[r:`{relationship}` {{{props_str}}}]->(o)
                """
                
                params = {"subject": subject, "object": object_name}
                params.update(rel_props)
                
                session.run(create_query, params)
                logger.info(f"Created edge '{subject}' -[{relationship}]-> '{object_name}' with ID {edge_id}")
                return edge_id
                
        except Exception as e:
            logger.error(f"Error creating edge: {e}")
            raise
    
    def get_edge(self, edge_id: str) -> Optional[GraphEdge]:
        """
        Retrieve an edge by its ID.
        
        Args:
            edge_id: Edge ID to retrieve
            
        Returns:
            GraphEdge object or None if not found
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                query = """
                MATCH (s:Entity)-[r]->(o:Entity)
                WHERE r.edge_id = $edge_id
                RETURN s.name as subject, type(r) as relationship, o.name as object, r
                """
                result = session.run(query, edge_id=edge_id)
                record = result.single()
                
                if record:
                    # Extract relationship properties and combine with query data
                    record_data = dict(record["r"])
                    
                    # Add subject, object, relationship type, and edge_id to record_data
                    record_data.update({
                        "subject": record["subject"],
                        "relationship": record["relationship"],
                        "object": record["object"],
                        "edge_id": edge_id
                    })
                    
                    # Use unified parsing function
                    return self._parse_record_to_edge(record_data)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error retrieving edge '{edge_id}': {e}")
            return None
    
    # ====== NODE MERGING HELPER METHODS ======
    
    def _transfer_relationships(self, from_nodes: List[str], to_node: str) -> int:
        """
        Transfer all relationships from source nodes to target node.
        
        Args:
            from_nodes: List of source node names
            to_node: Target node name
            
        Returns:
            Number of relationships transferred
        """
        total_transferred = 0
        
        try:
            with self.driver.session(database=self.config.database) as session:
                for from_node in from_nodes:
                    # Transfer outgoing relationships
                    outgoing_query = """
                    MATCH (from:Entity {name: $from_node})-[r]->(target:Entity)
                    MATCH (to:Entity {name: $to_node})
                    WHERE target.name <> $to_node  // Don't create self-loops
                    WITH from, r, target, to, type(r) as rel_type, properties(r) as props
                    CREATE (to)-[new_r:RELATES_TO]->(target)
                    SET new_r = props, new_r.transferred_from = $from_node
                    DELETE r
                    """
                    
                    result = session.run(outgoing_query, from_node=from_node, to_node=to_node)
                    summary = result.consume()
                    transferred = summary.counters.relationships_created
                    total_transferred += transferred
                    
                    # Transfer incoming relationships
                    incoming_query = """
                    MATCH (source:Entity)-[r]->(from:Entity {name: $from_node})
                    MATCH (to:Entity {name: $to_node})
                    WHERE source.name <> $to_node  // Don't create self-loops
                    WITH source, r, from, to, type(r) as rel_type, properties(r) as props
                    CREATE (source)-[new_r:RELATES_TO]->(to)
                    SET new_r = props, new_r.transferred_from = $from_node
                    DELETE r
                    """
                    
                    result = session.run(incoming_query, from_node=from_node, to_node=to_node)
                    summary = result.consume()
                    transferred = summary.counters.relationships_created
                    total_transferred += transferred
                    
                    logger.info(f"Transferred relationships from '{from_node}' to '{to_node}'")
                    
                return total_transferred
                
        except Exception as e:
            logger.error(f"Error transferring relationships: {e}")
            return total_transferred
    
    def _recalculate_embeddings(self, affected_edges: List[str]) -> bool:
        """
        Recalculate embeddings for affected edges after merge.
        
        Args:
            affected_edges: List of edge IDs that need embedding updates
            
        Returns:
            True if successful
        """
        try:
            # This would integrate with the vector store to update embeddings
            # For now, we'll mark the edges as needing embedding updates
            with self.driver.session(database=self.config.database) as session:
                for edge_id in affected_edges:
                    query = """
                    MATCH ()-[r]->()
                    WHERE r.edge_id = $edge_id
                    SET r.embedding_updated = false, r.needs_reembedding = true
                    """
                    session.run(query, edge_id=edge_id)
                    
                logger.info(f"Marked {len(affected_edges)} edges for embedding recalculation")
                return True
                
        except Exception as e:
            logger.error(f"Error marking edges for embedding recalculation: {e}")
            return False
    
    def _get_node_relationships(self, node_name: str) -> List[str]:
        """
        Get all relationship edge IDs for a node.
        
        Args:
            node_name: Node name
            
        Returns:
            List of edge IDs
        """
        try:
            with self.driver.session(database=self.config.database) as session:
                query = """
                MATCH (n:Entity {name: $node_name})-[r]-()
                WHERE r.edge_id IS NOT NULL
                RETURN r.edge_id as edge_id
                """
                result = session.run(query, node_name=node_name)
                edge_ids = [record["edge_id"] for record in result]
                return edge_ids
                
        except Exception as e:
            logger.error(f"Error getting node relationships: {e}")
            return []
    
    # ====== NODE MERGING OPERATIONS ======
    
    def merge_nodes_auto(self, source_node: str, target_node: str, merge_strategy: str = "intelligent") -> Dict[str, Any]:
        """
        Automatically merge two nodes using LLM to resolve conflicts.
        
        Args:
            source_node: First node name
            target_node: Second node name  
            merge_strategy: Strategy for merging ("intelligent")
            
        Returns:
            Dictionary with merge results and statistics
        """
        start_time = time.time()
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Get both nodes' data
                node1_data = self.get_node(source_node)
                node2_data = self.get_node(target_node)
                
                if not node1_data or not node2_data:
                    return {
                        "success": False,
                        "error": f"One or both nodes not found: '{source_node}', '{target_node}'"
                    }
                
                # Get relationship IDs before merge
                source_edges = self._get_node_relationships(source_node)
                target_edges = self._get_node_relationships(target_node)
                all_affected_edges = source_edges + target_edges
                
                # Use LLM to resolve merge
                from ..llm import LLMInterface, LLMClientFactory
                config = LLMClientFactory.create_from_env()
                llm = LLMInterface(llm_config=config)
                merge_resolution = llm.resolve_node_merge(node1_data, node2_data)
                
                # Create new merged node
                merged_name = merge_resolution["merged_name"]
                merged_metadata = merge_resolution["merged_metadata"]
                
                # Begin transaction
                tx = session.begin_transaction()
                
                try:
                    # Create the new merged node
                    new_node_name = self.create_node(merged_name, metadata=merged_metadata)
                    
                    # Transfer relationships from both nodes to new node
                    transferred_count = self._transfer_relationships([source_node, target_node], new_node_name)
                    
                    # Delete original nodes
                    self.delete_node(source_node, cascade=True)
                    self.delete_node(target_node, cascade=True)
                    
                    # Mark embeddings for recalculation
                    embedding_success = self._recalculate_embeddings(all_affected_edges)
                    
                    tx.commit()
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    result = {
                        "success": True,
                        "new_node_name": new_node_name,
                        "merged_metadata": merged_metadata,
                        "relationships_transferred": transferred_count,
                        "embeddings_updated": len(all_affected_edges) if embedding_success else 0,
                        "original_nodes_deleted": [source_node, target_node],
                        "llm_decisions": merge_resolution,
                        "execution_time_ms": execution_time
                    }
                    
                    logger.info(f"Successfully merged nodes '{source_node}' and '{target_node}' into '{new_node_name}'")
                    return result
                    
                except Exception as e:
                    tx.rollback()
                    raise e
                    
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error in automatic node merge: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time
            }
    
    def merge_nodes_manual(self, source_node: str, target_node: str, new_name: str, new_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manually merge two nodes with user-specified name and metadata.
        
        Args:
            source_node: First node name
            target_node: Second node name
            new_name: Name for the merged node
            new_metadata: Metadata for the merged node
            
        Returns:
            Dictionary with merge results and statistics
        """
        start_time = time.time()
        
        try:
            with self.driver.session(database=self.config.database) as session:
                # Check if trying to merge node with itself
                if source_node == target_node:
                    return {
                        "success": False,
                        "error": "Cannot merge node with itself"
                    }
                
                # Validate that both nodes exist
                node1_data = self.get_node(source_node)
                node2_data = self.get_node(target_node)
                
                if not node1_data or not node2_data:
                    return {
                        "success": False,
                        "error": f"One or both nodes not found: '{source_node}', '{target_node}'"
                    }
                
                # Get relationship IDs before merge
                source_edges = self._get_node_relationships(source_node)
                target_edges = self._get_node_relationships(target_node)
                all_affected_edges = source_edges + target_edges
                
                # Begin transaction
                tx = session.begin_transaction()
                
                try:
                    # Check if new_name matches one of the existing nodes
                    if new_name == source_node:
                        # Update the source node with merged metadata
                        self.update_node(source_node, new_metadata)
                        new_node_name = source_node
                        
                        # Transfer relationships from target node to source
                        transferred_count = self._transfer_relationships([target_node], source_node)
                        
                        # Delete only the target node
                        self.delete_node(target_node, cascade=True)
                        
                    elif new_name == target_node:
                        # Update the target node with merged metadata  
                        self.update_node(target_node, new_metadata)
                        new_node_name = target_node
                        
                        # Transfer relationships from source node to target
                        transferred_count = self._transfer_relationships([source_node], target_node)
                        
                        # Delete only the source node
                        self.delete_node(source_node, cascade=True)
                        
                    else:
                        # Create a new node with the specified name
                        new_node_name = self.create_node(new_name, metadata=new_metadata)
                        
                        # Transfer relationships from both nodes to new node
                        transferred_count = self._transfer_relationships([source_node, target_node], new_node_name)
                        
                        # Delete both original nodes
                        self.delete_node(source_node, cascade=True)
                        self.delete_node(target_node, cascade=True)
                    
                    # Mark embeddings for recalculation
                    embedding_success = self._recalculate_embeddings(all_affected_edges)
                    
                    tx.commit()
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Determine which nodes were deleted
                    if new_name == source_node:
                        deleted_nodes = [target_node]
                    elif new_name == target_node:
                        deleted_nodes = [source_node]
                    else:
                        deleted_nodes = [source_node, target_node]
                    
                    result = {
                        "success": True,
                        "new_node_name": new_node_name,
                        "merged_metadata": new_metadata,
                        "relationships_transferred": transferred_count,
                        "embeddings_updated": len(all_affected_edges) if embedding_success else 0,
                        "original_nodes_deleted": deleted_nodes,
                        "llm_decisions": {
                            "merged_name": new_name,
                            "merged_metadata": new_metadata,
                            "confidence": 1.0,  # Full confidence for manual merge
                            "reasoning": "Manual merge with user-specified parameters",
                            "name_source": "manual",
                            "metadata_conflicts": []
                        },
                        "execution_time_ms": execution_time
                    }
                    
                    logger.info(f"Successfully merged nodes '{source_node}' and '{target_node}' into '{new_node_name}' (manual)")
                    return result
                    
                except Exception as e:
                    tx.rollback()
                    raise e
                    
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Error in manual node merge: {e}")
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time
            }

    # =============================================================================
    # CRUD OPERATIONS FOR API
    # =============================================================================
    
    def get_edge_by_id(self, edge_id: str) -> Optional[GraphEdge]:
        """Get an edge by its ID"""
        with self.driver.session(database=self.config.database) as session:
            result = session.run(
                """
                MATCH (s)-[r {edge_id: $edge_id}]->(o)
                RETURN s.name as subject, type(r) as relationship, o.name as object, r
                """,
                edge_id=edge_id
            )

            record = result.single()
            if not record:
                return None

            # Extract relationship properties and combine with query data
            record_data = dict(record["r"])
            
            # Add subject, object, relationship type, and edge_id to record_data
            record_data.update({
                "subject": record["subject"],
                "relationship": record["relationship"],
                "object": record["object"],
                "edge_id": edge_id
            })
            
            # Use unified parsing function
            return self._parse_record_to_edge(record_data)
                

    
    def list_edges(self, skip: int = 0, limit: int = 50, user_id: str = None, 
                   category: str = None, relationship: str = None, 
                   include_obsolete: bool = False) -> List[GraphEdge]:
        """List edges with pagination and filtering"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build WHERE conditions
                where_conditions = []
                params = {"skip": skip, "limit": limit}
                
                if not include_obsolete:
                    where_conditions.append("r.obsolete = false")
                
                if user_id:
                    where_conditions.append("r.user_id = $user_id")
                    params["user_id"] = user_id
                
                if category:
                    where_conditions.append("r.category = $category")
                    params["category"] = category
                
                if relationship:
                    where_conditions.append(f"type(r) = $relationship")
                    params["relationship"] = relationship
                
                where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                query = f"""
                    MATCH (s)-[r]->(o)
                    {where_clause}
                    RETURN s.name as subject, type(r) as relationship, o.name as object, r
                    ORDER BY coalesce(r.created_at, datetime()) DESC
                    SKIP $skip LIMIT $limit
                """
                
                result = session.run(query, params)
                edges = []
                
                for record in result:
                    # Extract relationship properties and combine with query data
                    record_data = dict(record["r"])
                    edge_id = record_data.get("edge_id", str(uuid.uuid4()))
                    
                    # Add subject, object, relationship type, and edge_id to record_data
                    record_data.update({
                        "subject": record["subject"],
                        "relationship": record["relationship"],
                        "object": record["object"],
                        "edge_id": edge_id
                    })
                    
                    # Use unified parsing function
                    edge = self._parse_record_to_edge(record_data)
                    
                    edges.append(edge)
                
                return edges
                
        except Exception as e:
            logger.error(f"Error listing edges: {e}")
            return []
    
    def get_node_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a node by name with relationship count"""
        try:
            with self.driver.session(database=self.config.database) as session:
                result = session.run(
                    """
                    MATCH (n:Entity {name: $name})
                    OPTIONAL MATCH (n)-[r]-()
                    RETURN n, count(DISTINCT r) as relationships_count
                    """,
                    name=name
                )
                
                record = result.single()
                if not record:
                    return None
                
                node = record["n"]
                node_dict = dict(node)
                node_dict["relationships_count"] = record["relationships_count"]
                
                return node_dict
                
        except Exception as e:
            logger.error(f"Error getting node by name {name}: {e}")
            return None

    def list_nodes(self, skip: int = 0, limit: int = 50, 
                   user_id: str = None, has_relationships: bool = None) -> List[Dict[str, Any]]:
        """List nodes with pagination and filtering"""
        try:
            with self.driver.session(database=self.config.database) as session:
                # Build WHERE conditions
                where_conditions = []
                params = {"skip": skip, "limit": limit}
                
                if user_id:
                    where_conditions.append("n.user_id = $user_id")
                    params["user_id"] = user_id
                
                where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
                
                # Handle has_relationships filter
                relationship_clause = ""
                if has_relationships is not None:
                    if has_relationships:
                        relationship_clause = "AND count(r) > 0"
                    else:
                        relationship_clause = "AND count(r) = 0"
                
                query = f"""
                    MATCH (n:Entity)
                    {where_clause}
                    OPTIONAL MATCH (n)-[r]-()
                    WITH n, count(DISTINCT r) as relationships_count
                    WHERE 1=1 {relationship_clause}
                    RETURN n, relationships_count
                    ORDER BY coalesce(n.created_at, datetime()) DESC
                    SKIP $skip LIMIT $limit
                """
                
                result = session.run(query, params)
                nodes = []
                
                for record in result:
                    node = record["n"]
                    node_dict = dict(node)
                    node_dict["relationships_count"] = record["relationships_count"]
                    nodes.append(node_dict)
                
                return nodes
                
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            return []

    def add_triplets(self, triplets: List[GraphTriplet]) -> List[str]:
        """Add multiple triplets in batch"""
        # GraphDB handles triplets through add_edge_data
        ids = []
        for triplet in triplets:
            # Use GraphEdge directly from triplet
            success = self.add_edge(triplet.edge)
            if success:
                ids.append(triplet.edge.edge_id)
        return ids
    
    def update_triplet(self, triplet: GraphTriplet) -> bool:
        """Update an existing triplet"""
        try:
            return self.update_edge_metadata(triplet.edge.edge_id, triplet.edge.metadata)
        except Exception:
            return False
    
    def delete_triplet(self, vector_id: str) -> bool:
        """Delete a triplet from the vector store"""
        return self.delete_edge(vector_id)
    

    def search_by_entity(self, entity: str, k: int = 10, filter_obsolete: bool = True) -> List[SearchResult]:
        """Search for triplets involving a specific entity"""
        # Use GraphDB's entity relationship exploration
        triplets = self.get_entity_relationships(
            entity=entity,
            filter_obsolete=filter_obsolete,
            max_depth=1,
            limit=k
        )
        
        # Convert to SearchResult format
        search_results = []
        for triplet in triplets:
            search_result = SearchResult(
                triplet=triplet,
                score=1.0,  # Entity matches have perfect score
                source="neo4j_entity",
                explanation=f"Entity match for '{entity}'"
            )
            search_results.append(search_result)
        
        return search_results
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector store statistics (alias for get_stats)"""
        graph_stats = self.get_stats()
        
        # Convert to format expected by existing code
        # GraphDB returns total_edges, active_edges, obsolete_edges
        return {
            "total_triplets": graph_stats.get("total_edges", 0),
            "active_triplets": graph_stats.get("active_edges", 0),
            "obsolete_triplets": graph_stats.get("obsolete_edges", 0),
            "embedder_model": getattr(self.embedder.embedder, 'model_name', 'unknown') if self.embedder else 'none',
        }
    
    def clear_collection(self) -> bool:
        """Clear all data from the collection (alias for clear_graph)"""
        return self.clear_graph()
    
    def get_backend_store(self):
        """Get the underlying backend store instance.
        
        Returns:
            The GraphDB instance (self)
        """
        return self
    
    def __del__(self):
        """Clean up Neo4j driver connection"""
        if hasattr(self, 'driver'):
            self.driver.close()