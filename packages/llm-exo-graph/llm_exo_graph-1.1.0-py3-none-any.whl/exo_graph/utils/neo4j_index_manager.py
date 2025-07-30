"""Neo4j optimization utilities for vector indexes and graph queries."""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from ..config import Neo4jConfig

logger = logging.getLogger(__name__)


class SimilarityFunction(Enum):
    """Supported similarity functions for vector indexes."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"


@dataclass
class VectorIndexConfig:
    """Configuration for Neo4j vector indexes."""
    index_name: str
    node_label: str
    property_name: str
    dimensions: int
    similarity_function: SimilarityFunction

    def to_cypher_options(self) -> Dict[str, Any]:
        """Convert to Cypher index options."""
        return {
            "indexConfig": {
                "vector.dimensions": self.dimensions,
                "vector.similarity_function": self.similarity_function.value
            }
        }


class Neo4jIndexManager:
    """Optimizer for Neo4j vector indexes and queries."""

    def __init__(self, config: Optional[Neo4jConfig] = None):
        """Initialize Neo4j optimizer.
        
        Args:
            config: Neo4j configuration
        """
        self.config = config or Neo4jConfig()
        # Create indexes if they don't exist
        created_indexes = self.create_indexes()
        if created_indexes:
            logger.info(f"Created {len(created_indexes)} performance indexes: {', '.join(created_indexes)}")


    def _get_existing_indexes(self) -> set:
        """Get all existing index names with a single query.
        
        Returns:
            Set of existing index names
        """
        try:
            driver = self.config.get_driver()
            with driver.session(database=self.config.database) as session:
                result = session.run("SHOW INDEXES YIELD name")
                return {record["name"] for record in result}
        except Exception as e:
            logger.warning(f"Failed to get existing indexes: {e}")
            return set()

    def create_indexes(self) -> List[str]:
        """Create additional indexes for better query performance if they don't exist.
        
        Returns:
            List of newly created index names
        """
        driver = self.config.get_driver()
        created_indexes = []

        # Index definitions for common query patterns
        indexes_to_create = [
            ("triplet_subject_idx", "CREATE INDEX triplet_subject_idx FOR (t:Triplet) ON (t.subject)"),
            ("triplet_object_idx", "CREATE INDEX triplet_object_idx FOR (t:Triplet) ON (t.object)"),
            ("triplet_relationship_idx", "CREATE INDEX triplet_relationship_idx FOR (t:Triplet) ON (t.relationship)"),
            ("triplet_obsolete_idx", "CREATE INDEX triplet_obsolete_idx FOR (t:Triplet) ON (t.obsolete)"),
            ("triplet_confidence_idx", "CREATE INDEX triplet_confidence_idx FOR (t:Triplet) ON (t.confidence)"),
            ("triplet_created_idx", "CREATE INDEX triplet_created_idx FOR (t:Triplet) ON (t.created_at)"),
            ("entity_name_idx", "CREATE INDEX entity_name_idx FOR (e:Entity) ON (e.name)"),
            (
            "relates_to_obsolete_idx", "CREATE INDEX relates_to_obsolete_idx FOR ()-[r:RELATES_TO]-() ON (r.obsolete)"),
            # Additional composite indexes for common query patterns
            ("triplet_subject_obsolete_idx",
             "CREATE INDEX triplet_subject_obsolete_idx FOR (t:Triplet) ON (t.subject, t.obsolete)"),
            ("triplet_object_obsolete_idx",
             "CREATE INDEX triplet_object_obsolete_idx FOR (t:Triplet) ON (t.object, t.obsolete)"),
            ("triplet_relationship_obsolete_idx",
             "CREATE INDEX triplet_relationship_obsolete_idx FOR (t:Triplet) ON (t.relationship, t.obsolete)"),
            # Vector index
        ]

        try:
            # Get all existing indexes with a single query
            existing_indexes = self._get_existing_indexes()
            logger.debug(f"Found {len(existing_indexes)} existing indexes: {existing_indexes}")

            with driver.session(database=self.config.database) as session:
                for index_name, query in indexes_to_create:
                    try:
                        # Check if index already exists using preloaded set
                        if index_name in existing_indexes:
                            logger.debug(f"Index {index_name} already exists, skipping creation")
                            continue

                        # Create the index
                        session.run(query)
                        created_indexes.append(index_name)
                        logger.info(f"Created index: {index_name}")

                    except Exception as e:
                        # Log specific error but continue with other indexes
                        error_msg = str(e).lower()
                        if "equivalent index already exists" in error_msg or "already exists" in error_msg:
                            logger.debug(f"Index {index_name} already exists (from error): {e}")
                        else:
                            logger.warning(f"Failed to create index {index_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to create performance indexes: {e}")

        vector_index_name = "triplet_embedding_index"

        # create vector index if not exist

        if self.create_default_vector_index(vector_index_name):
            created_indexes.append(vector_index_name)

        return created_indexes

    def create_default_vector_index(self, index_name: str, dimensions: int = 384,
                                    similarity_function: SimilarityFunction = SimilarityFunction.COSINE) -> bool:
        """Create the default triplet embedding vector index if it doesn't exist.
        
        Args:
            index_name: name of the index
            dimensions: Vector dimensions (default 384 for all-MiniLM-L6-v2)
            similarity_function: Similarity function to use
            
        Returns:
            True if created or already exists, False if failed
        """
        config = VectorIndexConfig(
            index_name=index_name,
            node_label="Triplet",
            property_name="embedding",
            dimensions=dimensions,
            similarity_function=similarity_function
        )

        driver = self.config.get_driver()

        try:
            with driver.session(database=self.config.database) as session:
                # Check if index already exists using preloaded indexes
                existing_indexes = self._get_existing_indexes()
                if config.index_name in existing_indexes:
                    logger.info(f"Vector index {config.index_name} already exists, skipping creation")
                    return False

                # Create new index with optimized configuration
                cypher_query = f"""
                CREATE VECTOR INDEX {config.index_name}
                FOR (n:{config.node_label}) ON (n.{config.property_name})
                OPTIONS {{
                  indexConfig: {{
                    `vector.dimensions`: {config.dimensions},
                    `vector.similarity_function`: '{config.similarity_function.value}'
                  }}
                }}
                """

                session.run(cypher_query)
                logger.info(f"Created optimized vector index {config.index_name}")

                return True

        except Exception as e:
            logger.error(f"Failed to create optimized vector index: {e}")
            return False

    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics for optimization planning.
        
        Returns:
            Database statistics and metrics
        """
        driver = self.config.get_driver()

        try:
            with driver.session(database=self.config.database) as session:
                # Node counts
                node_stats = {}
                node_result = session.run("""
                    MATCH (n) 
                    RETURN labels(n) as labels, count(n) as count
                """)

                for record in node_result:
                    labels = record["labels"]
                    count = record["count"]
                    label_key = ":".join(sorted(labels)) if labels else "unlabeled"
                    node_stats[label_key] = count

                # Relationship counts
                rel_stats = {}
                rel_result = session.run("""
                    MATCH ()-[r]->()
                    RETURN type(r) as type, count(r) as count
                """)

                for record in rel_result:
                    rel_stats[record["type"]] = record["count"]

                # Index information
                index_result = session.run("SHOW INDEXES")
                indexes = []
                for record in index_result:
                    indexes.append({
                        "name": record["name"],
                        "type": record["type"],
                        "state": record["state"],
                        "population_percent": record["populationPercent"]
                    })

                # Constraint information
                constraint_result = session.run("SHOW CONSTRAINTS")
                constraints = []
                for record in constraint_result:
                    constraints.append({
                        "name": record["name"],
                        "type": record["type"],
                        "description": record["description"]
                    })

                return {
                    "nodes": {
                        "total": sum(node_stats.values()),
                        "by_label": node_stats
                    },
                    "relationships": {
                        "total": sum(rel_stats.values()),
                        "by_type": rel_stats
                    },
                    "indexes": indexes,
                    "constraints": constraints,
                    "timestamp": session.run("RETURN datetime() as now").single()["now"]
                }

        except Exception as e:
            logger.error(f"Failed to get database statistics: {e}")
            return {"error": str(e)}



