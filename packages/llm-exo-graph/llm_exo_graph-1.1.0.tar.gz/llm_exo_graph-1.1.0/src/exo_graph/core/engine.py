"""
Optimized Knowledge Graph Engine v2 - Streamlined Implementation
"""
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sentence_transformers import SentenceTransformer, CrossEncoder as SentenceTransformerCrossEncoder
import traceback
from ..utils.graph_standardizer import GraphStandardizer
from ..utils.encoders import BiEncoder, CrossEncoder

logger = logging.getLogger(__name__)

from ..models import (
    InputItem, GraphEdge, EdgeMetadata, GraphTriplet,
    SearchResult, QueryResponse, RelationshipStatus, SearchType
)
from ..llm import LLMInterface, LLMConfig
from ..storage import GraphDB
from ..config import Neo4jConfig

DEFAULT_MODEL = "gpt-4o"
DEFAULT_EMBEDDER_MODEL = "all-MiniLM-L6-v2"
DEFAULT_CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class ExoGraphEngine:
    """
    Optimized Knowledge Graph Engine with:
    - LLM-powered entity/relationship extraction
    - Optimized Neo4j operations
    - Advanced conflict detection and temporal analysis
    - Vector search with graph integration
    """

    def __init__(self, 
                 llm_config: Optional[LLMConfig] = None,
                 neo4j_config: Neo4jConfig = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the optimized engine
        
        Args:
            llm_config: LLM configuration object (preferred method)
            neo4j_config: Neo4j configuration
            config: Configuration dictionary with optional parameters:
                - encoder_model: BiEncoder model name (default: DEFAULT_EMBEDDER_MODEL)
                - cross_encoder_model: CrossEncoder model name (default: DEFAULT_CROSS_ENCODER_MODEL)
        """
        # Apply default config and merge with provided config
        self.config = {
            "encoder_model": DEFAULT_EMBEDDER_MODEL,
            "cross_encoder_model": DEFAULT_CROSS_ENCODER_MODEL
        }
        if config:
            self.config.update(config)
        
        # Create embedder and wrapper first so it can be shared across components
        self.embedder = BiEncoder(SentenceTransformer(self.config["encoder_model"]))
        self.cross_encoder = CrossEncoder(SentenceTransformerCrossEncoder(self.config["cross_encoder_model"]))
        # Create graph_db with shared bi_encoder (VectorStore functionality is now integrated)
        self.graph_db = GraphDB(neo4j_config, embedder=self.embedder)
        
        self.graph_standardizer = GraphStandardizer(self.graph_db, self.embedder, self.cross_encoder)

        # Initialize LLM interface with configuration
        self.llm = LLMInterface(llm_config=llm_config)

        # Ensure performance indexes are created once during initialization

        print("🚀 Knowledge Graph Engine v2")
        print(f"   - LLM interface: {self.llm.model} via {self.llm.config.provider}")

    def process_input(self, items: List[InputItem]) -> Dict[str, Any]:
        """
        Process input items using optimized graph operations
        
        Args:
            items: List of InputItem objects to process
            
        Returns:
            Dictionary with processing results and statistics
        """
        start_time = time.time()
        results = {
            "processed_items": 0,
            "new_edges": 0,
            "updated_edges": 0,
            "obsoleted_edges": 0,
            "duplicates_ignored": 0,
            "errors": [],
            "edge_results": []
        }

        for item in items:
            try:
                # Extract entities and relationships using LLM with classifier
                extracted_info = self.llm.extract_entities_relationships(item.description)
                standardized_extracted_info = self.graph_standardizer.process_relationships(extracted_info)
                #
                # if not standardized_extracted_info:
                #     self._add_error(results, f"No relationships extracted from: {item.description}")
                #     continue

                # Process each extracted relationship
                for info in standardized_extracted_info:
                    # Parse dates from extracted info (dates are extracted by LLM)

                    edge_result = self._process_relationship(info, item)
                    
                    # Only add to results if it's not a duplicate (completely skip duplicates)
                    if edge_result.get("action") != "duplicate":
                        edge_result["input_description"] = item.description
                        edge_result["extracted_info"] = {
                            "subject": info.subject,
                            "relationship": info.relationship,
                            "object": info.object,
                            "summary": info.summary,
                            "confidence": info.confidence,
                            "is_negation": info.is_negation,
                            "from_date": info.from_date,
                            "to_date": info.to_date,
                            "category": info.category
                        }
                        
                        results["edge_results"].append(edge_result)
                        self._update_counters(results, edge_result)
                    else:
                        # Just count the duplicate but don't add to results
                        results["duplicates_ignored"] += 1

                results["processed_items"] += 1

            except Exception as e:
                logging.error(f'{e}\r\n{traceback.format_exc()}')
                self._add_error(results, f"Error processing item '{item.description}': {str(e)}", item.description)

        results["processing_time_ms"] = (time.time() - start_time) * 1000
        return results

    def _process_relationship(self, extracted_info, input_item: InputItem) -> Dict[str, Any]:
        """Process a single extracted relationship using optimized operations"""
        try:
            # Create edge metadata with category from classifier
            metadata = EdgeMetadata(
                summary=extracted_info.summary,
                from_date=extracted_info.from_date,
                to_date=extracted_info.to_date,
                confidence=extracted_info.confidence,
                source=input_item.metadata.get("source", "user_input"),
                user_id=input_item.metadata.get("user_id"),
                category=extracted_info.category,
                additional_metadata={k: v for k, v in input_item.metadata.items() 
                                   if k not in ["source", "user_id"]}
            )

            # Handle negations
            if extracted_info.is_negation:
                metadata.obsolete = True
                metadata.status = RelationshipStatus.OBSOLETE
                if not extracted_info.to_date:
                    metadata.to_date = datetime.now()


            # Create edge data
            edge_data = GraphEdge(
                edge_id=None,
                subject=extracted_info.subject,
                relationship=extracted_info.relationship,
                object=extracted_info.object,
                metadata=metadata
            )

            # Check for exact duplicates using optimized method
            duplicates = self.graph_db.find_duplicate_edges(edge_data)
            if duplicates and not extracted_info.is_negation:
                return {"action": "duplicate", "message": f"Duplicate ignored: {extracted_info.summary}"}

            # Handle explicit negations using optimized conflict detection
            if extracted_info.is_negation:
                return self._handle_negation(extracted_info)
            else:
                return self._add_new_edge(edge_data)

        except Exception as e:
            return {"action": "error", "message": str(e)}

    def _handle_negation(self, extracted_info) -> Dict[str, Any]:
        """Handle negations using optimized conflict detection"""
        try:
            # Use optimized conflict detection to find relationships to obsolete
            conflicts = self.graph_db.detect_relationship_conflicts(
                entity_name=extracted_info.subject,
                relationship_type=extracted_info.relationship,
                confidence_threshold=0.3
            )

            obsoleted_count = 0
            obsoleted_relationships = []

            for conflict in conflicts:
                if extracted_info.object.lower() in conflict["conflicting_objects"]:
                    # Obsolete the matching edge
                    edge = conflict["higher_confidence_edge"]
                    edge.metadata.obsolete = True
                    edge.metadata.status = RelationshipStatus.OBSOLETE
                    edge.metadata.to_date = extracted_info.to_date or datetime.now()

                    self.graph_db.update_edge_metadata(edge.edge_id, edge.metadata)
                    
                    # Update vector store
                    triplet = GraphTriplet(edge=edge)
                    self.graph_db.update_triplet(triplet)

                    obsoleted_count += 1
                    subject = edge.subject or "Unknown"
                    relationship = edge.relationship or "Unknown"
                    obj = edge.object or "Unknown"
                    obsoleted_relationships.append(f"{subject} {relationship} {obj}")

            if obsoleted_count > 0:
                return {
                    "action": "obsoleted",
                    "count": obsoleted_count,
                    "obsoleted_relationships": obsoleted_relationships,
                    "message": f"Obsoleted {obsoleted_count} similar relationship(s)"
                }
            else:
                return {"action": "error", "message": f"No existing relationship found to obsolete: {extracted_info.summary}"}

        except Exception as e:
            return {"action": "error", "message": f"Error handling negation: {str(e)}"}

    def _add_new_edge(self, edge_data: GraphEdge) -> Dict[str, Any]:
        """Add new edge using optimized graph operations (single call to avoid duplicates)"""
        try:
            # Only call graph_db.add_edge_data once - the vector store will be updated through Neo4j
            success = self.graph_db.add_edge(edge_data)
            if success:
                return {"action": "created"}
            else:
                return {"action": "error", "message": f"Failed to add edge to graph {edge_data}"}
        except Exception as e:
            return {"action": "error", "message": str(e)}

    def search(self, query: str, search_type: SearchType = SearchType.BOTH, k: int = 10, answer_question: bool = True) -> QueryResponse:
        """
        Search using optimized graph and vector operations
        
        Args:
            query: Natural language query
            search_type: "direct", "semantic", or "both"
            k: Number of results to return
            
        Returns:
            QueryResponse with results and generated answer
        """

        print(f"Search type: {search_type} {query}")
        start_time = time.time()

        try:
            all_results = []

            # Simplified direct graph search with standardization
            if search_type in [SearchType.DIRECT, SearchType.BOTH]:
                print('Parsing query DIRECT with LLM intuition...')
                parsed_query = self.llm.parse_query(query)  # No existing relationships
                print(f"Parsed query: {parsed_query}")
                
                # Standardize relationships from parsed query
                standardized_relationships = self._standardize_relationships(parsed_query.relationships)
                print(f"Standardized relationships: {standardized_relationships}")
                query_relationships = [*parsed_query.relationships, *standardized_relationships]
                graph_results = self._graph_search(parsed_query.entities, query_relationships, k)
                all_results.extend(graph_results)

            # Optimized semantic vector search  
            if search_type in [SearchType.SEMANTIC, SearchType.BOTH]:
                print('Parsing query SEMANTIC...')
                vector_results = self.graph_db.vector_search(query, k=k, filter_obsolete=True)
                all_results.extend(vector_results)

            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            unique_results.sort(key=lambda x: x.score, reverse=True)
            final_results = unique_results[:k]

            # Generate answer using LLM
            answer = None
            if answer_question and final_results:
                result_summaries = []
                for r in final_results[:5]:
                    if r.triplet and r.triplet.edge:
                        result_summaries.append(r.triplet.edge.metadata.summary)
                    else:
                        result_summaries.append(r.explanation)  # Use explanation for path results
                answer = self.llm.generate_answer(query, result_summaries)

            query_time = time.time() - start_time

            return QueryResponse(
                results=final_results,
                total_found=len(unique_results),
                query_time_ms=query_time * 1000,
                answer=answer,
                confidence=self._calculate_confidence(final_results)
            )

        except Exception as e:
            print(f"Error searching: {e} {traceback.format_exc()}")
            query_time = time.time() - start_time
            return QueryResponse(
                results=[],
                total_found=0,
                query_time_ms=query_time * 1000,
                answer=f"Error processing query: {str(e)}",
                confidence=0.0
            )

    def _standardize_relationships(self, relationships: List[str]) -> List[str]:
        """Standardize relationship names using GraphStandardizer"""
        standardized = []
        
        try:
            for relationship_name in relationships:
                if relationship_name:
                    # Use GraphStandardizer to find best category
                    best_category = self.graph_standardizer.standardize_category(
                        predicate=relationship_name
                    )
                    
                    # Use GraphStandardizer to find best edge
                    best_edge = self.graph_standardizer.standardize_edge(
                        category=best_category,
                        proposed_edge=relationship_name
                    )
                    
                    if best_edge:
                        standardized.append(best_edge)
                        logger.info(f"Standardized '{relationship_name}' -> '{best_edge}' (category: {best_category})")
                    else:
                        standardized.append(relationship_name)  # Keep original if no standardization
                
        except Exception as e:
            logger.error(f"Error standardizing relationships: {e}")
            # Return original relationships as fallback
            return relationships
            
        return standardized
    
    def _graph_search(self, entities: List[str], relationships: List[str], k: int) -> List[SearchResult]:
        """Simplified direct graph search using entities and standardized relationships"""
        results = []

        try:
            print(f"Searching with entities: {entities} and relationships: {relationships}")
            
            # Search by entities using optimized method with relationship filtering
            for entity in entities:
                triplets = self.graph_db.get_entity_relationships(
                    entity=entity,
                    filter_obsolete=True,
                    max_depth=1,
                    relationship_types=relationships if relationships else None,
                    limit=k
                )

                for triplet in triplets:
                    # Simple scoring based on relationship match
                    relationship = triplet.edge.relationship
                    score = 1.0 if relationship in relationships else 0.8
                    
                    result = SearchResult(
                        triplet=triplet,
                        score=score,
                        source="graph_direct",
                        explanation=f"Direct graph match for entity '{entity}' with relationship '{relationship}'"
                    )
                    results.append(result)

            # Path finding for multi-entity queries
            if len(entities) >= 2:
                for i, start_entity in enumerate(entities):
                    for end_entity in entities[i+1:]:
                        paths = self.graph_db.find_relationship_paths(
                            start_entity=start_entity,
                            end_entity=end_entity,
                            max_hops=3,
                            limit=5
                        )
                        
                        for path_info in paths:
                            # Simple path scoring
                            path_confidence = path_info.get("path_confidence", 0.5)
                            
                            if path_confidence > 0.3:  # Only include decent paths
                                result = SearchResult(
                                    triplet=None,  # Path results don't have single triplets
                                    score=path_confidence,
                                    source="path_direct",
                                    explanation=f"Path from '{start_entity}' to '{end_entity}' with confidence {path_confidence:.2f}"
                                )
                                results.append(result)

        except Exception as e:
            print(f"Error in direct graph search: {e}")

        return results

    def get_node_relations(self, node_name: str, max_depth: int = 1, 
                          filter_obsolete: bool = True, source: Optional[str] = None) -> List[SearchResult]:
        """
        Get all relations for a node using optimized entity exploration
        
        Args:
            node_name: Name of the node to search relations for
            max_depth: Maximum relationship depth to explore
            filter_obsolete: Whether to filter out obsolete relationships
            source: Optional filter by source metadata
            
        Returns:
            List of SearchResult objects containing all relations
        """
        try:
            triplets = self.graph_db.get_entity_relationships(
                entity=node_name,
                filter_obsolete=filter_obsolete,
                max_depth=max_depth,
                limit=50
            )

            results = []
            for triplet in triplets:
                # Apply source filter if provided
                if source and hasattr(triplet.edge.metadata, 'source'):
                    if triplet.edge.metadata.source != source:
                        continue

                result = SearchResult(
                    triplet=triplet,
                    score=1.0,
                    source="graph",
                    explanation=f"Optimized relation for node '{node_name}'"
                )
                results.append(result)
            
            return results

        except Exception as e:
            print(f"Error getting node relations: {e}")
            return []

    def analyze_conflicts(self, entity_name: Optional[str] = None, 
                         relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze relationship conflicts using optimized detection"""
        try:
            return self.graph_db.detect_relationship_conflicts(
                entity_name=entity_name,
                relationship_type=relationship_type,
                confidence_threshold=0.5
            )
        except Exception as e:
            print(f"Error analyzing conflicts: {e}")
            return []

    def find_paths(self, start_entity: str, end_entity: str, max_hops: int = 4) -> List[Dict[str, Any]]:
        """Find paths between entities using optimized algorithms"""
        try:
            return self.graph_db.find_relationship_paths(
                start_entity=start_entity,
                end_entity=end_entity,
                max_hops=max_hops,
                limit=10
            )
        except Exception as e:
            print(f"Error finding paths: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics including optimization stats"""
        try:
            return {
                "graph_stats": self.graph_db.get_stats(),
                "vector_stats": self.graph_db.get_vector_stats(),
                "relationships": self.graph_db.get_relationships(),
                "entities": len(self.graph_db.get_entities())
            }
        except Exception as e:
            return {"error": str(e)}

    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the entire knowledge graph"""
        return {
            "graph_data": self.graph_db.export_to_dict(),
            "export_timestamp": datetime.now().isoformat(),
            "version": "2.0-optimized"
        }

    def clear_all_data(self) -> bool:
        """Clear all data from both graph and vector stores"""
        try:
            graph_cleared = self.graph_db.clear_graph()
            vector_cleared = self.graph_db.clear_collection()
            return graph_cleared and vector_cleared
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False

    # Helper methods
    def _add_error(self, results: Dict[str, Any], error_msg: str, description: str):
        """Add error to results"""
        results["errors"].append(error_msg)
        results["edge_results"].append({
            "action": "error",
            "message": error_msg,
            "input_description": description
        })

    def _update_counters(self, results: Dict[str, Any], edge_result: Dict[str, Any]):
        """Update result counters based on edge result"""
        action = edge_result.get("action", "unknown")
        if action == "created":
            results["new_edges"] += 1
        elif action == "updated":
            results["updated_edges"] += 1
        elif action == "obsoleted":
            results["obsoleted_edges"] += edge_result.get("count", 1)
        elif action == "duplicate":
            results["duplicates_ignored"] += 1
        elif action == "error":
            # Only append the error message if it's not already in the errors list
            error_msg = edge_result.get("message", "Unknown error")
            if error_msg not in results["errors"]:
                results["errors"].append(error_msg)

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results keeping highest scoring"""
        if not results:
            return []
        
        unique_results = []
        seen_relationships = []
        
        sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
        
        for result in sorted_results:
            # Skip path results that don't have triplets
            if result.triplet is None:
                unique_results.append(result)  # Always include path results
                continue
                
            edge = result.triplet.edge
            # Access graph data directly - handle lists from malformed data
            subject = edge.subject or "unknown"
            if isinstance(subject, list):
                subject = str(subject[0]) if subject else "unknown"
                
            relationship = edge.relationship or "unknown"
            if isinstance(relationship, list):
                relationship = str(relationship[0]) if relationship else "unknown"
                
            obj = edge.object or "unknown"
            if isinstance(obj, list):
                obj = str(obj[0]) if obj else "unknown"
            
            relationship_key = (
                str(subject).lower().strip(),
                str(relationship).upper(),
                str(obj).lower().strip()
            )
            
            if relationship_key not in seen_relationships:
                seen_relationships.append(relationship_key)
                unique_results.append(result)
        
        return unique_results

    def _calculate_confidence(self, results: List[SearchResult]) -> float:
        """Calculate overall confidence in results"""
        if not results:
            return 0.0

        weights = [0.5, 0.3, 0.2]
        total_score = 0.0

        for i, result in enumerate(results[:3]):
            weight = weights[i] if i < len(weights) else 0.1
            total_score += result.score * weight

        return min(total_score, 1.0)

