"""Semantic Embedding Module

This module handles the generation and caching of semantic embeddings
for business text using transformer models. Now uses the enhanced NLP
implementation for production-ready capabilities.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any
import numpy as np
from datetime import datetime, timedelta
import logging

# Import enhanced NLP components
try:
    from ...nlp.core.embedder import SemanticEmbedder as EnhancedSemanticEmbedder
    from ...nlp.domain.model_selector import DomainModelSelector
    ENHANCED_NLP_AVAILABLE = True
except ImportError:
    ENHANCED_NLP_AVAILABLE = False
    logging.getLogger(__name__).warning("Enhanced NLP modules not available, using legacy implementation")

# Fallback imports
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
    """Generate semantic embeddings for business text with enhanced capabilities."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        use_cache: bool = True,
        cache_dir: Optional[Path] = None,
        use_domain_selection: bool = True
    ):
        """Initialize embedder with specified model.
        
        Args:
            model_name: Name of the sentence transformer model
            use_cache: Whether to use embedding cache
            cache_dir: Directory for cache storage
            use_domain_selection: Whether to use domain-specific model selection
        """
        self.model_name = model_name
        self.use_cache = use_cache
        self.use_domain_selection = use_domain_selection
        
        # Initialize enhanced embedder if available
        if ENHANCED_NLP_AVAILABLE:
            self.enhanced_embedder = EnhancedSemanticEmbedder(
                model_name=model_name,
                use_cache=use_cache,
                cache_dir=cache_dir
            )
            
            # Initialize domain model selector if requested
            if use_domain_selection:
                self.domain_selector = DomainModelSelector(cache_dir=cache_dir)
            else:
                self.domain_selector = None
                
            self.model = self.enhanced_embedder.model
        else:
            # Fallback to legacy implementation
            if use_cache:
                self.cache = EmbeddingCache(cache_dir)
            else:
                self.cache = None
            
            # Load model
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.model = SentenceTransformer(model_name)
            else:
                self.model = MockSentenceTransformer(model_name)
            
            self.enhanced_embedder = None
            self.domain_selector = None
    
    def embed_text(self, text: str, document_type: Optional[str] = None) -> np.ndarray:
        """Generate embedding for a single text with optional domain-specific model selection.
        
        Args:
            text: Input text to embed
            document_type: Optional document type for domain model selection
            
        Returns:
            Embedding vector
        """
        if not text:
            return np.zeros(768)  # Return zero vector for empty text
        
        # Use enhanced embedder if available
        if self.enhanced_embedder:
            # Check if we should use domain-specific model selection
            if self.domain_selector and document_type:
                try:
                    model_name, domain, metadata = self.domain_selector.select_model(
                        text, document_type
                    )
                    
                    # If different model selected, use it
                    if model_name != self.model_name:
                        domain_model = self.domain_selector.load_model(model_name, domain)
                        if hasattr(domain_model, 'encode'):
                            embedding = domain_model.encode(text, convert_to_numpy=True)
                            return embedding[0] if len(embedding.shape) > 1 else embedding
                except Exception as e:
                    logging.getLogger(__name__).warning(f"Domain selection failed: {e}, falling back to default model")
            
            return self.enhanced_embedder.embed_text(text)
        else:
            # Legacy implementation
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
        
        # Use enhanced embedder if available
        if self.enhanced_embedder:
            return self.enhanced_embedder.embed_texts(texts, batch_size)
        else:
            # Legacy implementation
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
        # Use enhanced embedder if available
        if self.enhanced_embedder:
            return self.enhanced_embedder.calculate_similarity(embedding1, embedding2)
        else:
            # Legacy implementation
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model and capabilities."""
        if self.enhanced_embedder:
            info = self.enhanced_embedder.get_model_info()
            info['enhanced_features'] = True
            info['domain_selection_available'] = self.domain_selector is not None
        else:
            info = {
                'model_name': self.model_name,
                'enhanced_features': False,
                'domain_selection_available': False,
                'is_mock': isinstance(self.model, MockSentenceTransformer),
                'embedding_dim': 768
            }
        
        return info
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics and performance metrics."""
        if self.enhanced_embedder:
            stats = self.enhanced_embedder.get_stats()
            if self.domain_selector:
                stats['domain_selector_stats'] = self.domain_selector.get_stats()
        else:
            stats = {
                'enhanced_features': False,
                'texts_encoded': 0,
                'cache_hits': 0,
                'model_calls': 0
            }
        
        return stats
    
    def clear_cache(self, older_than_hours: Optional[int] = None):
        """Clear embedding cache."""
        if self.enhanced_embedder:
            self.enhanced_embedder.clear_cache(older_than_hours)
        elif hasattr(self, 'cache') and self.cache:
            self.cache.clear()
    
    def warm_up(self, sample_texts: Optional[List[str]] = None):
        """Warm up the model with sample texts for better initial performance."""
        if self.enhanced_embedder:
            self.enhanced_embedder.warm_up(sample_texts)
        elif sample_texts:
            # Simple warm-up for legacy implementation
            _ = self.embed_texts(sample_texts[:5])  # Just embed first 5 texts