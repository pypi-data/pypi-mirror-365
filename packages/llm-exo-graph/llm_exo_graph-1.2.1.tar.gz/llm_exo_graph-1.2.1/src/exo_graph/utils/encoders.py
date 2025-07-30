"""
High-level encoder wrapper classes for bi-encoder and cross-encoder operations.
Provides clean, reusable interfaces for similarity calculations and ranking.
"""
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.special import softmax
import logging

logger = logging.getLogger(__name__)


class BiEncoder:
    """
    Wrapper for bi-encoder operations.
    Handles embedding generation, similarity calculations, and top-k retrieval.
    """
    
    def __init__(self, embedder):
        """
        Initialize bi-encoder wrapper.
        
        Args:
            embedder: Sentence transformer model for generating embeddings
        """
        if embedder is None:
            raise ValueError("embedder is required for BiEncoderWrapper")
        self.embedder = embedder
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        embeddings = self.embedder.encode(texts)
        
        # Ensure proper numpy array format
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype=np.float32)
        
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to encode
            
        Returns:
            Numpy array embedding
        """

        embeddings = self.encode([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)

        # Calculate cosine similarity
        similarity = cosine_similarity(emb1, emb2)[0][0]

        # Normalize to 0-1 range (cosine similarity is -1 to 1)
        normalized_similarity = (similarity + 1) / 2

        return float(normalized_similarity)
            

    
    def get_top_k_similar(self, query_text: str, embeddings_dict: Dict[str, np.ndarray],
                         k: int = 10, exclude_keys: List[str] = None) -> List[Tuple[str, float]]:
        """
        Find top-k most similar items to a query text.
        
        Args:
            query_text: Text to find similar items for
            embeddings_dict: Dictionary of {name: embedding} to search
            k: Number of top results to return
            exclude_keys: Optional list of keys to exclude
            name_mapping: Optional mapping from normalized to original names
            
        Returns:
            List of (name, similarity_score) tuples sorted by score
        """
        if not embeddings_dict:
            return []
        
        exclude_keys = exclude_keys or []

        try:
            # Generate query embedding
            query_embedding = self.encode_single(query_text)
            
            # Calculate similarities
            similarities = []
            for key, embedding in embeddings_dict.items():
                if key in exclude_keys:
                    continue
                
                similarity = self.cosine_similarity(query_embedding, embedding)
                # Use original name if mapping exists
                similarities.append((key, similarity))
            
            # Sort by similarity and return top-k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            logger.warning(f"Failed to get top-k similar items: {e}")
            return []
    
    def build_embeddings_dict(self, items: List[str]) -> Dict[str, np.ndarray]:
        """
        Build embeddings dictionary for a list of items.
        
        Args:
            items: List of items to embed
            normalizer: Optional function to normalize item names
            
        Returns:
            Tuple of (embeddings_dict, name_mapping)
        """
        embeddings_dict = {}

        for item in items:
            try:

                embeddings_dict[item] = self.encode_single(item)
                
            except Exception as e:
                logger.warning(f"Failed to create embedding for '{item}': {e}")
        
        return embeddings_dict


class CrossEncoder:
    """
    Wrapper for cross-encoder operations.
    Handles pairwise scoring and reranking of candidates.
    """
    
    def __init__(self, cross_encoder):
        """
        Initialize cross-encoder wrapper.
        
        Args:
            cross_encoder: Cross-encoder model for pairwise scoring
        """
        if cross_encoder is None:
            raise ValueError("cross_encoder is required for CrossEncoderWrapper")
        self.cross_encoder = cross_encoder
    
    def score_pairs(self, pairs: List[List[str]], apply_softmax: bool = True) -> np.ndarray:
        """
        Score pairs of texts using cross-encoder.
        
        Args:
            pairs: List of [text1, text2] pairs to score
            apply_softmax: Whether to apply softmax normalization
            
        Returns:
            Array of scores (normalized if apply_softmax=True)
        """
        if not pairs:
            return np.array([])
        
        try:
            # Get raw scores from cross-encoder
            raw_scores = self.cross_encoder.predict(pairs)
            
            # Apply softmax if requested
            if apply_softmax:
                return softmax(raw_scores)
            else:
                return raw_scores
                
        except Exception as e:
            logger.warning(f"Failed to score pairs: {e}")
            return np.array([])
    
    def rerank_candidates(self, query_text: str, candidates: List[Tuple[str, Any]],
                         text_extractor=None, apply_softmax: bool = True) -> List[Tuple[str, float, int]]:
        """
        Rerank candidates using cross-encoder scoring.
        
        Args:
            query_text: Query text to compare against
            candidates: List of (candidate_name, score) tuples to rerank
            text_extractor: Optional function to extract text from candidate name
            apply_softmax: Whether to apply softmax normalization
            
        Returns:
            List of (candidate_name, score, original_rank) tuples sorted by new score
        """
        if not candidates:
            return []
        
        # Prepare pairs for cross-encoder
        pairs = []
        for candidate_name, _ in candidates:
            # Extract text if function provided
            candidate_text = text_extractor(candidate_name) if text_extractor else candidate_name
            pairs.append([query_text, candidate_text])

        # Score all pairs
        scores = self.score_pairs(pairs, apply_softmax=apply_softmax)

        # Combine with candidate names and original ranks
        reranked = []
        for i, (candidate_name, _) in enumerate(candidates):
            reranked.append((candidate_name, float(scores[i]), i + 1))

        # Sort by new scores
        reranked.sort(key=lambda x: x[1], reverse=True)

        return reranked
            

    def find_best_match(self, query_text: str, candidates: List[str],
                       threshold: float = 0.0, text_extractor=None) -> Optional[Tuple[str, float]]:
        """
        Find the best matching candidate for a query text.
        
        Args:
            query_text: Query text to match
            candidates: List of candidate strings
            threshold: Minimum score threshold
            text_extractor: Optional function to extract text from candidates
            
        Returns:
            Tuple of (best_match, score) or None if no match above threshold
        """
        if not candidates:
            return None
        
        # Convert to tuples for reranking
        candidate_tuples = [(c, 0.0) for c in candidates]
        
        # Rerank candidates
        reranked = self.rerank_candidates(query_text, candidate_tuples, 
                                        text_extractor=text_extractor)
        
        if reranked and reranked[0][1] >= threshold:
            best_candidate, best_score, _ = reranked[0]
            return best_candidate, best_score
        
        return None
