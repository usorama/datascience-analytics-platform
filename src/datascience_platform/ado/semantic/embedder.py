"""Semantic Embedding Module

This module handles the generation and caching of semantic embeddings
for business text using transformer models.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
from datetime import datetime, timedelta
import logging

# Note: In production, you would use sentence-transformers
# For now, we'll create a mock implementation that demonstrates the concept
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("sentence-transformers not available. Using mock embeddings.")


class EmbeddingCache:
    """Cache for storing and retrieving embeddings."""
    
    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = 24):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ado_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.memory_cache = {}  # In-memory cache for session
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model."""
        content = f"{model_name}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """Retrieve embedding from cache."""
        key = self._get_cache_key(text, model_name)
        
        # Check memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            # Check if not expired
            if datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime) < self.ttl:
                try:
                    with open(cache_file, 'rb') as f:
                        embedding = pickle.load(f)
                    self.memory_cache[key] = embedding
                    return embedding
                except:
                    pass
        
        return None
    
    def set(self, text: str, model_name: str, embedding: np.ndarray):
        """Store embedding in cache."""
        key = self._get_cache_key(text, model_name)
        
        # Store in memory
        self.memory_cache[key] = embedding
        
        # Store on disk
        cache_file = self.cache_dir / f"{key}.pkl"
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
    
    def clear(self):
        """Clear all cached embeddings."""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()


class MockSentenceTransformer:
    """Mock sentence transformer for when the library isn't available."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedding_dim = 768  # Standard BERT dimension
        
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Generate mock embeddings based on text content."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            # Create deterministic pseudo-embedding based on text
            # This maintains consistency for demos
            np.random.seed(hash(text) % (2**32))
            
            # Base embedding
            embedding = np.random.randn(self.embedding_dim) * 0.1
            
            # Add some "semantic" signal based on keywords
            keywords = {
                'customer': 0, 'user': 0, 'revenue': 1, 'growth': 1,
                'efficiency': 2, 'optimize': 2, 'security': 3, 'compliance': 3,
                'innovation': 4, 'transform': 4, 'quality': 5, 'performance': 5
            }
            
            text_lower = text.lower()
            for keyword, idx in keywords.items():
                if keyword in text_lower:
                    # Boost certain dimensions for keywords
                    embedding[idx * 100:(idx + 1) * 100] += 0.5
            
            # Normalize
            embedding = embedding / (np.linalg.norm(embedding) + 1e-9)
            embeddings.append(embedding)
        
        return np.array(embeddings)


class SemanticEmbedder:
    """Generate semantic embeddings for business text."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        use_cache: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """Initialize embedder with specified model.
        
        Args:
            model_name: Name of the sentence transformer model
            use_cache: Whether to use embedding cache
            cache_dir: Directory for cache storage
        """
        self.model_name = model_name
        self.use_cache = use_cache
        
        if use_cache:
            self.cache = EmbeddingCache(cache_dir)
        else:
            self.cache = None
        
        # Load model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.model = SentenceTransformer(model_name)
        else:
            self.model = MockSentenceTransformer(model_name)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        if not text:
            return np.zeros(768)  # Return zero vector for empty text
        
        # Check cache
        if self.cache:
            cached = self.cache.get(text, self.model_name)
            if cached is not None:
                return cached
        
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Store in cache
        if self.cache:
            self.cache.set(text, self.model_name, embedding)
        
        return embedding
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts efficiently."""
        if not texts:
            return np.array([])
        
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache for each text
        if self.cache:
            for i, text in enumerate(texts):
                cached = self.cache.get(text, self.model_name)
                if cached is not None:
                    embeddings.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.model.encode(
                uncached_texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(uncached_texts) > 100
            )
            
            # Cache new embeddings
            if self.cache:
                for text, embedding in zip(uncached_texts, new_embeddings):
                    self.cache.set(text, self.model_name, embedding)
            
            # Combine with cached embeddings
            for idx, embedding in zip(uncached_indices, new_embeddings):
                embeddings.append((idx, embedding))
        
        # Sort by original index and extract embeddings
        embeddings.sort(key=lambda x: x[0])
        return np.array([emb for _, emb in embeddings])
    
    def embed_strategy_document(self, doc: 'StrategyDocument') -> np.ndarray:
        """Generate hierarchical embeddings for strategy document."""
        # Embed full document
        doc_embedding = self.embed_text(doc.full_text)
        
        # Embed sections
        section_embeddings = {}
        for section in doc.sections:
            section_embedding = self.embed_text(section.content)
            section_embeddings[section.section_id] = section_embedding
        
        # Create weighted average based on section importance
        # (In practice, you might use more sophisticated weighting)
        if section_embeddings:
            section_weights = np.array([
                1.5 if section.level == 1 else 1.0
                for section in doc.sections
            ])
            section_weights = section_weights / section_weights.sum()
            
            weighted_embedding = np.average(
                list(section_embeddings.values()),
                axis=0,
                weights=section_weights
            )
            
            # Combine document and section embeddings
            final_embedding = 0.7 * doc_embedding + 0.3 * weighted_embedding
        else:
            final_embedding = doc_embedding
        
        return final_embedding / np.linalg.norm(final_embedding)
    
    def embed_okr(self, okr: 'OKR') -> Tuple[np.ndarray, List[np.ndarray]]:
        """Generate embeddings for OKR and its key results.
        
        Returns:
            Tuple of (objective_embedding, list_of_kr_embeddings)
        """
        # Embed objective
        obj_embedding = self.embed_text(okr.objective_text)
        
        # Embed key results
        kr_embeddings = []
        for kr in okr.key_results:
            kr_embedding = self.embed_text(kr.text)
            kr_embeddings.append(kr_embedding)
        
        # Create combined OKR embedding
        if kr_embeddings:
            # Weight objective more heavily than individual KRs
            all_embeddings = [obj_embedding] + kr_embeddings
            weights = [0.5] + [0.5 / len(kr_embeddings)] * len(kr_embeddings)
            combined_embedding = np.average(all_embeddings, axis=0, weights=weights)
        else:
            combined_embedding = obj_embedding
        
        return combined_embedding, kr_embeddings
    
    def embed_work_item(self, item: 'SemanticWorkItem') -> Dict[str, np.ndarray]:
        """Generate multiple embeddings for work item.
        
        Returns:
            Dictionary with 'title', 'description', and 'combined' embeddings
        """
        embeddings = {}
        
        # Embed title
        embeddings['title'] = self.embed_text(item.title)
        
        # Embed description if available
        if item.full_description:
            embeddings['description'] = self.embed_text(item.full_description)
        else:
            embeddings['description'] = embeddings['title']
        
        # Embed acceptance criteria if available
        if item.acceptance_criteria_text:
            embeddings['acceptance_criteria'] = self.embed_text(item.acceptance_criteria_text)
        
        # Create combined embedding
        all_embeddings = list(embeddings.values())
        embeddings['combined'] = np.mean(all_embeddings, axis=0)
        
        return embeddings
    
    def calculate_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between two embeddings."""
        if embedding1.size == 0 or embedding2.size == 0:
            return 0.0
        
        # Ensure same dimensions
        if embedding1.shape != embedding2.shape:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        
        # Ensure in valid range
        return float(np.clip(similarity, -1.0, 1.0))
    
    def find_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        top_k: int = 10,
        threshold: float = 0.3
    ) -> List[Tuple[int, float]]:
        """Find most similar embeddings from candidates.
        
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        if not candidate_embeddings:
            return []
        
        similarities = []
        for i, candidate in enumerate(candidate_embeddings):
            sim = self.calculate_similarity(query_embedding, candidate)
            if sim >= threshold:
                similarities.append((i, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]