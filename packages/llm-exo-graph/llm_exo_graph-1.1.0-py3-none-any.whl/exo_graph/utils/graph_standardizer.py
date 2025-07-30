"""
Classifier Detection - Maps predicates to categories and standardizes edge names
"""
from typing import List, Dict, Optional, Tuple, Any
import logging
import numpy as np
from dataclasses import replace
from ..models import ExtractedInfo
from ..models.classifier_map import ClassifierMap
from .encoders import BiEncoder, CrossEncoder
from .edge_name_utils import to_edge_name
from ..storage import GraphDB

logger = logging.getLogger(__name__)

BI_ENCODER_THRESHOLD = 0.6
CROSS_ENCODER_THRESHOLD = 0.1
DEFAULT_CATEGORY = "general"


# Removed normalize_category function - using original categories as keys

class GraphStandardizer:
    """
    Detects and assigns classifiers to extracted relationships.
    Maps predicates to categories and standardizes edge names.
    """

    def __init__(self, graph_db: GraphDB, embedder: BiEncoder, cross_encoder: CrossEncoder=None,
                 top_k: int = 10, llm_interface=None):
        if embedder is None:
            raise ValueError("embedder parameter is required and cannot be None")

        # Initialize ClassifierMap with bi_encoder for embedding management
        self.classifier_map = ClassifierMap(graph_db, embedder)

        self.llm_interface = llm_interface  # Optional LLM interface for category estimation
        self.use_cross_encoder = cross_encoder is not None
        self.top_k = top_k  # Number of candidates for cross-encoder reranking

        # Store encoder wrappers
        self.bi_encoder = embedder
        self.cross_encoder = cross_encoder

    def process_relationships(self, extracted_infos: List[ExtractedInfo]) -> List[ExtractedInfo]:
        """
        Process extracted relationships and assign categories.
        
        Args:
            extracted_infos: List of ExtractedInfo from LLM extraction
            
        Returns:
            List of ExtractedInfo with category field populated
        """
        classified_relationships = []

        for info in extracted_infos:
            # Detect category for the predicate (use LLM-provided category if available)
            # Find best standardized edge name
            standardized_edge = self.standardize_edge(
                info.category, info.relationship, info.summary
            )

            # Create new ExtractedInfo with category and standardized edge
            standardized_info = replace(
                info,
                relationship=standardized_edge,
            )

            classified_relationships.append(standardized_info)
            logger.info(f"Standardized: {info.relationship} -> {standardized_edge}")

        return classified_relationships

    def get_category_stats(self) -> Dict[str, int]:
        """Get statistics about categories and their edges."""
        return self.classifier_map.get_stats()

    # Embedding cache methods removed - now handled by ClassifierMap

    def _cross_encoder_best_category(self, candidates: List[Tuple[str, Any]],
                                     predicate: str, summary: str = None) -> str:
        """
        Rerank category candidates using cross-encoder with context prioritization.
        
        Args:
            candidates: List of (category, score) tuples from bi-encoder
            predicate: The predicate being classified
            summary: Optional summary context for better classification
            
        Returns:
            Tuple of (best_category, best_score, best_rank)
        """
        try:
            # Determine context for cross-encoder
            if summary and summary.strip():
                query_context = summary.strip()
                logger.debug(f"Using summary for cross-encoder context: '{query_context}'")
            else:
                query_context = self.classifier_map.get_natural_name(predicate)
                logger.debug(f"Using predicate for cross-encoder context: '{query_context}'")

            # Rerank using cross-encoder wrapper
            reranked = self.cross_encoder.rerank_candidates(
                query_context, candidates,
                text_extractor=lambda x: x.strip(),
                apply_softmax=True
            )

            if reranked:
                best_category, best_score, original_rank = reranked[0]
                logger.debug(f"Cross-encoder reranked categories: best='{best_category}' "
                             f"(rank: {original_rank}, score: {best_score:.3f})")

                return best_category
            else:
                return None

        except Exception as e:
            logger.warning(f"Cross-encoder category reranking failed: {e}")
            return None

    def _cross_encoder_best_edge(self, candidates: List[Tuple[str, Any]],
                                 proposed_edge: str, summary: str = None) -> str:
        """
        Rerank edge candidates using cross-encoder with context prioritization.
        
        Args:
            candidates: List of (edge_upper_case, score) tuples from bi-encoder
            proposed_edge: The proposed edge being matched
            summary: Optional summary context for better classification
            
        Returns:
            Tuple of (best_edge, best_score, best_rank)
        """

        # Determine context for cross-encoder
        normalized_edge = self.classifier_map.get_natural_name(proposed_edge)

        if summary and summary.strip():
            proposed_context = summary.strip()
            logger.debug(f"Using summary for cross-encoder edge context: '{proposed_context}'")
        else:
            proposed_context = normalized_edge
            logger.debug(f"Using proposed edge for cross-encoder context: '{proposed_context}'")

        # Rerank using cross-encoder wrapper
        reranked = self.cross_encoder.rerank_candidates(
            proposed_context, candidates,
            text_extractor=self.classifier_map.get_natural_name,
            apply_softmax=True
        )

        if reranked:
            best_edge, best_score, original_rank = reranked[0]
            logger.debug(f"Cross-encoder reranked edges: best='{best_edge}' "
                         f"(rank: {original_rank}, score: {best_score:.3f})")

            if best_score >= CROSS_ENCODER_THRESHOLD:
                return best_edge
            return None
        else:
            return None

    def standardize_category(self, predicate: str, summary: str = None,
                             llm_category: str = None) -> Optional[str]:
        """
        Hybrid two-stage category detection:
        1. Use bi-encoder to get top-k category candidates
        2. Use cross-encoder to rerank and select best category
        
        Args:
            predicate: The relationship type to classify
            summary: Optional summary context for better classification
            
        Returns:
            Best category name if found above threshold, None otherwise
        """
        existing_category = self.classifier_map.get_category_for_edge(predicate.upper())
        if existing_category:
            logger.debug(f"Found existing category for {predicate}: {existing_category}")
            return existing_category

        best_category = None

        # Stage 1: Get top-k candidates using bi-encoder
        candidates = self._get_top_k_categories_bi_encoder(predicate, k=self.top_k)

        # top category by score
        top_score = candidates[0][1] if len(candidates) > 0 else 0.0

        if top_score > BI_ENCODER_THRESHOLD:
            best_category = candidates[0][0]

            logger.debug(f"bi-encoder score for {predicate} use {best_category}: "
                           f"{top_score} > {BI_ENCODER_THRESHOLD}")

        if self.use_cross_encoder:
            # Stage 2: Rerank with cross-encoder using summary context
            best_category = self._cross_encoder_best_category(candidates, predicate, summary)

        if best_category:
            return best_category

        # no suitable category found, use LLM category if available
        if llm_category:
            self._sync_cache_with_new_category(llm_category)

            return llm_category

        return DEFAULT_CATEGORY

    def standardize_edge(self, category: str, proposed_edge: str, summary: str = None) -> Optional[str]:
        """
        Hybrid two-stage edge matching:
        1. Use bi-encoder to get top-k edge candidates within category
        2. Use cross-encoder to rerank and select best edge
        
        Args:
            category: The category to search in
            proposed_edge: The proposed edge name
            summary: Optional summary context for better edge matching
            
        Returns:
            Best existing edge name if found above threshold, None otherwise
        """
        # Stage 1: Get top-k candidates using bi-encoder
        candidates = self._get_top_k_edges_bi_encoder(category, proposed_edge, k=self.top_k)

        if not candidates:
            return proposed_edge

        best_edge, best_score = candidates[0]

        if self.use_cross_encoder:

            # Stage 2: Rerank with cross-encoder using summary context
            best_edge = self._cross_encoder_best_edge(
                candidates, proposed_edge, summary
            )

        # no suitable edge found from based on encoders
        if not best_edge:
            logger.info(
                f"Cross-encoder edge score {best_score:.3f} < {CROSS_ENCODER_THRESHOLD}, using proposed edge '{proposed_edge}' as-is")

            best_edge = proposed_edge

        # Standardize the proposed edge and add to classifier map
        standardized = to_edge_name(best_edge)

        # Add to classifier map and sync cache
        self.classifier_map.get_or_create_edge(category, standardized)
        self._sync_cache_with_new_edge(category, standardized)

        return standardized

    # Generic bi-encoder method removed - using ClassifierMap methods directly

    def _get_top_k_categories_bi_encoder(self, predicate: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Get top-k category candidates using bi-encoder similarity.
        
        Args:
            predicate: The relationship type
            k: Number of top candidates to return
            
        Returns:
            List of (category, similarity_score) tuples sorted by score
        """
        # Normalize the predicate text
        embedding_text = self.classifier_map.get_natural_name(predicate)

        # Use ClassifierMap's search method
        return self.classifier_map.search_similar_categories(
            query_text=embedding_text,
            k=k,
            exclude_categories=["general"]
        )

    def _get_top_k_edges_bi_encoder(self, category: str, proposed_edge: str, k: int = 10) -> List[Tuple[str, float]]:
        """
        Get top-k edge candidates within a category using bi-encoder similarity.
        
        Args:
            category: The category to search in
            proposed_edge: The proposed edge name
            k: Number of top candidates to return
            
        Returns:
            List of (edge, similarity_score) tuples sorted by score
        """
        # Normalize the proposed edge text
        embedding_text = self.classifier_map.get_natural_name(proposed_edge)

        # Use ClassifierMap's search method
        return self.classifier_map.search_similar_edges(
            category=category,
            query_text=embedding_text,
            k=k
        )

    def _sync_cache_with_new_category(self, category: str) -> None:
        """
        Sync embedding cache with a new LLM-estimated category.
        Ensures the category exists in classifier map and embedding cache.
        
        Args:
            category: The new category name to add to cache
        """
        try:
            # Use ClassifierMap to add category embedding
            if self.classifier_map.add_category_embedding(category):
                logger.info(f"✅ Successfully synced new LLM category '{category}' with embedding cache")
            else:
                logger.warning(f"Failed to sync new category '{category}' with embedding cache")
                
        except Exception as e:
            logger.warning(f"Failed to sync cache with new category '{category}': {e}")

    def _sync_cache_with_new_edge(self, category: str, edge_name: str) -> None:
        """
        Sync embedding cache with a new edge in the given category.
        
        Args:
            category: The category the edge belongs to
            edge_name: The edge name (in UPPER_CASE format)
        """
        try:
            # Use ClassifierMap to add edge embedding
            if self.classifier_map.add_edge_embedding(category, edge_name):
                natural_edge = self.classifier_map.get_natural_name(edge_name)
                logger.debug(f"✅ Successfully synced new edge '{edge_name}' -> '{natural_edge}' in category '{category}' with embedding cache")
            else:
                logger.warning(f"Failed to sync new edge '{edge_name}' in category '{category}' with embedding cache")
                
        except Exception as e:
            logger.warning(f"Failed to sync cache with new edge '{edge_name}' in category '{category}': {e}")
