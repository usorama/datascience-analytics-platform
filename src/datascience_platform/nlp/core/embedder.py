"""Enhanced Semantic Embedding Module

This module provides production-ready semantic embeddings using real transformer models
with proper GPU support, caching, and error handling.
"""

import hashlib
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple, Any
import numpy as np
from datetime import datetime, timedelta
import logging
import warnings
import torch

# Suppress some warnings from transformers
warnings.filterwarnings("ignore", category=FutureWarning)

logger = logging.getLogger(__name__)

# Try importing required libraries with graceful fallback
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    import torch
    TORCH_AVAILABLE = True
    # Check for CUDA or Apple Silicon GPU
    GPU_AVAILABLE = torch.cuda.is_available() or (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
    APPLE_GPU_AVAILABLE = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    GPU_AVAILABLE = False
    APPLE_GPU_AVAILABLE = False
    logger.warning("PyTorch not available. Install with: pip install torch")


class EmbeddingCache:
    """Advanced cache for storing and retrieving embeddings with TTL and compression."""
    
    def __init__(
        self, 
        cache_dir: Optional[Path] = None, 
        ttl_hours: int = 168,  # 1 week default
        max_memory_items: int = 1000,
        compress_disk: bool = True
    ):
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ds_platform_embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.memory_cache = {}
        self.max_memory_items = max_memory_items
        self.compress_disk = compress_disk
        
        # Track cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0
        }
    
    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key from text and model."""
        content = f"{model_name}::{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]  # Shorter keys
    
    def get(self, text: str, model_name: str) -> Optional[np.ndarray]:
        """Retrieve embedding from cache with statistics tracking."""
        if not text:
            return None
            
        key = self._get_cache_key(text, model_name)
        
        # Check memory cache first
        if key in self.memory_cache:
            self.stats['hits'] += 1
            self.stats['memory_hits'] += 1
            return self.memory_cache[key]['embedding']
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                # Check if not expired
                if datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime) < self.ttl:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    embedding = data['embedding']
                    
                    # Add to memory cache if space available
                    if len(self.memory_cache) < self.max_memory_items:
                        self.memory_cache[key] = {
                            'embedding': embedding,
                            'timestamp': datetime.now()
                        }
                    
                    self.stats['hits'] += 1
                    self.stats['disk_hits'] += 1
                    return embedding
                else:
                    # Remove expired file
                    cache_file.unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Error loading cache file {cache_file}: {e}")
                cache_file.unlink(missing_ok=True)
        
        self.stats['misses'] += 1
        return None
    
    def set(self, text: str, model_name: str, embedding: np.ndarray):
        """Store embedding in cache with LRU eviction."""
        if not text:
            return
            
        key = self._get_cache_key(text, model_name)
        
        # Store in memory with LRU eviction
        if len(self.memory_cache) >= self.max_memory_items:
            # Remove oldest item
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['timestamp']
            )
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = {
            'embedding': embedding,
            'timestamp': datetime.now()
        }
        
        # Store on disk
        try:
            cache_file = self.cache_dir / f"{key}.pkl"
            data = {
                'embedding': embedding,
                'model_name': model_name,
                'text_length': len(text),
                'created_at': datetime.now().isoformat()
            }
            
            with open(cache_file, 'wb') as f:
                if self.compress_disk:
                    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    pickle.dump(data, f)
        except Exception as e:
            logger.warning(f"Error saving to cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': hit_rate,
            'memory_items': len(self.memory_cache),
            'cache_size_mb': sum(
                cache_file.stat().st_size 
                for cache_file in self.cache_dir.glob("*.pkl")
            ) / (1024 * 1024)
        }
    
    def clear(self, older_than_hours: Optional[int] = None):
        """Clear cache items, optionally only older items."""
        if older_than_hours is None:
            # Clear everything
            self.memory_cache.clear()
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
        else:
            # Clear items older than specified hours
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            # Clear from memory
            keys_to_remove = [
                key for key, data in self.memory_cache.items()
                if data['timestamp'] < cutoff_time
            ]
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # Clear from disk
            for cache_file in self.cache_dir.glob("*.pkl"):
                if datetime.fromtimestamp(cache_file.stat().st_mtime) < cutoff_time:
                    cache_file.unlink()


class MockSentenceTransformer:
    """Enhanced mock sentence transformer with more realistic embeddings."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.embedding_dim = 768  # Standard BERT dimension
        
        # Create more sophisticated keyword mappings
        self.keyword_vectors = self._create_keyword_vectors()
        
    def _create_keyword_vectors(self) -> Dict[str, np.ndarray]:
        """Create keyword-based semantic vectors."""
        keywords = {
            # Business domains
            'financial': np.array([0.8, 0.2, 0.1, 0.3, 0.6]),
            'technical': np.array([0.1, 0.8, 0.7, 0.2, 0.4]),
            'security': np.array([0.3, 0.6, 0.9, 0.1, 0.2]),
            'compliance': np.array([0.5, 0.3, 0.8, 0.7, 0.1]),
            'customer': np.array([0.7, 0.1, 0.2, 0.8, 0.5]),
            
            # Action words
            'implement': np.array([0.2, 0.9, 0.4, 0.1, 0.6]),
            'analyze': np.array([0.4, 0.3, 0.1, 0.9, 0.2]),
            'optimize': np.array([0.6, 0.7, 0.3, 0.4, 0.8]),
            'monitor': np.array([0.3, 0.4, 0.6, 0.5, 0.7]),
            
            # Risk indicators
            'urgent': np.array([0.9, 0.1, 0.8, 0.2, 0.3]),
            'critical': np.array([0.8, 0.2, 0.9, 0.1, 0.4]),
            'blocked': np.array([0.7, 0.3, 0.7, 0.8, 0.1]),
        }
        
        # Expand to full dimensionality
        expanded = {}
        for word, base_vec in keywords.items():
            # Repeat and add noise
            full_vec = np.tile(base_vec, self.embedding_dim // len(base_vec) + 1)[:self.embedding_dim]
            full_vec += np.random.randn(self.embedding_dim) * 0.05  # Add small amount of noise
            expanded[word] = full_vec / np.linalg.norm(full_vec)
            
        return expanded
        
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Generate enhanced mock embeddings with better semantic properties."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            if not text:
                # Return zero vector for empty text
                embeddings.append(np.zeros(self.embedding_dim))
                continue
                
            # Create deterministic base embedding
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.randn(self.embedding_dim) * 0.1
            
            # Add keyword-based semantic signal
            text_lower = text.lower()
            keyword_influence = 0.0
            
            for keyword, vector in self.keyword_vectors.items():
                if keyword in text_lower:
                    # Weight by keyword frequency
                    count = text_lower.count(keyword)
                    weight = min(count * 0.3, 0.8)  # Cap influence
                    embedding += vector * weight
                    keyword_influence += weight
            
            # Add document length influence (longer docs get slightly different patterns)
            length_factor = min(len(text) / 1000, 2.0)  # Max factor of 2
            embedding[::10] *= (1 + length_factor * 0.1)
            
            # Normalize to unit vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            
            embeddings.append(embedding)
        
        return np.array(embeddings)


class SemanticEmbedder:
    """Production-ready semantic embedder with GPU support and advanced features."""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-mpnet-base-v2",
        use_cache: bool = True,
        cache_dir: Optional[Path] = None,
        device: Optional[str] = None,
        batch_size: int = 32,
        max_seq_length: Optional[int] = None
    ):
        """Initialize embedder with advanced configuration.
        
        Args:
            model_name: Name of the sentence transformer model
            use_cache: Whether to use embedding cache
            cache_dir: Directory for cache storage
            device: Device to use ('cuda', 'cpu', or None for auto)
            batch_size: Default batch size for encoding
            max_seq_length: Maximum sequence length (None for model default)
        """
        self.model_name = model_name
        self.use_cache = use_cache
        self.batch_size = batch_size
        self.max_seq_length = max_seq_length
        
        # Set up device (including Apple Silicon support)
        if device is None:
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif APPLE_GPU_AVAILABLE:
                self.device = 'mps'
                logger.info("Using Apple Silicon GPU (MPS)")
            else:
                self.device = 'cpu'
        else:
            self.device = device
            
        logger.info(f"Initializing SemanticEmbedder with model: {model_name}, device: {self.device}")
        
        # Initialize cache
        if use_cache:
            self.cache = EmbeddingCache(cache_dir)
        else:
            self.cache = None
        
        # Load model
        self.model = self._load_model()
        
        # Track usage statistics
        self.stats = {
            'texts_encoded': 0,
            'cache_hits': 0,
            'model_calls': 0,
            'total_processing_time': 0.0
        }
    
    def _load_model(self) -> Union[SentenceTransformer, MockSentenceTransformer]:
        """Load the sentence transformer model with error handling."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model = SentenceTransformer(self.model_name, device=self.device)
                
                # Set maximum sequence length if specified
                if self.max_seq_length:
                    model.max_seq_length = self.max_seq_length
                
                logger.info(f"Loaded model {self.model_name} on {self.device}")
                return model
                
            except Exception as e:
                logger.error(f"Error loading model {self.model_name}: {e}")
                logger.info("Falling back to mock embedder")
                return MockSentenceTransformer(self.model_name)
        else:
            logger.warning("Using mock embedder. Install sentence-transformers for production use.")
            return MockSentenceTransformer(self.model_name)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text with enhanced error handling."""
        if not text or not text.strip():
            return np.zeros(768 if hasattr(self.model, 'embedding_dim') else 768)
        
        # Clean and truncate text if needed
        text = text.strip()
        if self.max_seq_length and len(text) > self.max_seq_length * 4:  # Rough char estimate
            text = text[:self.max_seq_length * 4]
            logger.debug(f"Truncated text to {len(text)} characters")
        
        # Check cache
        if self.cache:
            cached = self.cache.get(text, self.model_name)
            if cached is not None:
                self.stats['cache_hits'] += 1
                return cached
        
        # Generate embedding
        try:
            import time
            start_time = time.time()
            
            if SENTENCE_TRANSFORMERS_AVAILABLE and isinstance(self.model, SentenceTransformer):
                embedding = self.model.encode(
                    text, 
                    convert_to_numpy=True,
                    device=self.device,
                    batch_size=1
                )
            else:
                embedding = self.model.encode(text)
                if len(embedding.shape) > 1:
                    embedding = embedding[0]
            
            processing_time = time.time() - start_time
            self.stats['total_processing_time'] += processing_time
            self.stats['model_calls'] += 1
            self.stats['texts_encoded'] += 1
            
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            # Return zero vector on error
            embedding = np.zeros(768)
        
        # Store in cache
        if self.cache:
            self.cache.set(text, self.model_name, embedding)
        
        return embedding
    
    def embed_texts(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """Generate embeddings for multiple texts with optimized batching."""
        if not texts:
            return np.array([])
        
        batch_size = batch_size or self.batch_size
        embeddings_list = []
        
        # Filter out empty texts
        valid_texts = [(i, text.strip()) for i, text in enumerate(texts) if text and text.strip()]
        valid_indices = [i for i, _ in valid_texts]
        valid_text_list = [text for _, text in valid_texts]
        
        if not valid_text_list:
            # All texts were empty
            return np.zeros((len(texts), 768))
        
        # Check cache for all texts first
        uncached_texts = []
        uncached_indices = []
        cached_embeddings = {}
        
        if self.cache:
            for idx, text in valid_texts:
                cached = self.cache.get(text, self.model_name)
                if cached is not None:
                    cached_embeddings[idx] = cached
                    self.stats['cache_hits'] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(idx)
        else:
            uncached_texts = valid_text_list
            uncached_indices = valid_indices
        
        # Generate embeddings for uncached texts in batches
        if uncached_texts:
            try:
                import time
                start_time = time.time()
                
                if SENTENCE_TRANSFORMERS_AVAILABLE and isinstance(self.model, SentenceTransformer):
                    new_embeddings = self.model.encode(
                        uncached_texts,
                        batch_size=batch_size,
                        convert_to_numpy=True,
                        device=self.device,
                        show_progress_bar=len(uncached_texts) > 50
                    )
                else:
                    new_embeddings = self.model.encode(uncached_texts)
                
                processing_time = time.time() - start_time
                self.stats['total_processing_time'] += processing_time
                self.stats['model_calls'] += 1
                self.stats['texts_encoded'] += len(uncached_texts)
                
                # Cache new embeddings
                if self.cache:
                    for text, embedding in zip(uncached_texts, new_embeddings):
                        self.cache.set(text, self.model_name, embedding)
                
                # Add to results
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    cached_embeddings[idx] = embedding
                    
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                # Generate zero vectors for failed embeddings
                for idx in uncached_indices:
                    cached_embeddings[idx] = np.zeros(768)
        
        # Reconstruct full embedding array
        full_embeddings = []
        for i in range(len(texts)):
            if i in cached_embeddings:
                full_embeddings.append(cached_embeddings[i])
            else:
                # Empty text
                full_embeddings.append(np.zeros(768))
        
        return np.array(full_embeddings)
    
    def calculate_similarity_batch(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray
    ) -> np.ndarray:
        """Calculate cosine similarity between batches of embeddings efficiently."""
        if embeddings1.size == 0 or embeddings2.size == 0:
            return np.array([])
        
        # Normalize embeddings
        norms1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
        norms2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
        
        # Avoid division by zero
        norms1[norms1 == 0] = 1
        norms2[norms2 == 0] = 1
        
        normalized1 = embeddings1 / norms1
        normalized2 = embeddings2 / norms2
        
        # Calculate similarities
        similarities = np.sum(normalized1 * normalized2, axis=1)
        
        # Ensure valid range
        return np.clip(similarities, -1.0, 1.0)
    
    def find_similar_texts(
        self,
        query_text: str,
        candidate_texts: List[str],
        top_k: int = 10,
        threshold: float = 0.3
    ) -> List[Tuple[int, str, float]]:
        """Find most similar texts with scores."""
        if not candidate_texts:
            return []
        
        # Generate embeddings
        query_embedding = self.embed_text(query_text)
        candidate_embeddings = self.embed_texts(candidate_texts)
        
        # Calculate similarities
        similarities = []
        for i, candidate_embedding in enumerate(candidate_embeddings):
            sim = self.calculate_similarity(query_embedding, candidate_embedding)
            if sim >= threshold:
                similarities.append((i, candidate_texts[i], float(sim)))
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:top_k]
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
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
        return float(np.clip(similarity, -1.0, 1.0))
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        info = {
            'model_name': self.model_name,
            'device': self.device,
            'is_mock': isinstance(self.model, MockSentenceTransformer),
            'batch_size': self.batch_size,
            'max_seq_length': self.max_seq_length
        }
        
        if hasattr(self.model, 'get_sentence_embedding_dimension'):
            info['embedding_dim'] = self.model.get_sentence_embedding_dimension()
        elif hasattr(self.model, 'embedding_dim'):
            info['embedding_dim'] = self.model.embedding_dim
        else:
            info['embedding_dim'] = 768
        
        return info
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        stats = self.stats.copy()
        if self.cache:
            stats['cache_stats'] = self.cache.get_stats()
        
        # Calculate average processing time
        if stats['model_calls'] > 0:
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['model_calls']
        else:
            stats['avg_processing_time'] = 0.0
            
        return stats
    
    def clear_cache(self, older_than_hours: Optional[int] = None):
        """Clear embedding cache."""
        if self.cache:
            self.cache.clear(older_than_hours)
            logger.info(f"Cleared embedding cache (older than {older_than_hours} hours)" if older_than_hours else "Cleared embedding cache")
    
    def warm_up(self, sample_texts: Optional[List[str]] = None):
        """Warm up the model with sample texts."""
        if sample_texts is None:
            sample_texts = [
                "This is a test document for warming up the embedding model.",
                "Financial risk assessment for quarterly planning.",
                "Technical implementation of security features.",
                "Customer satisfaction and user experience optimization."
            ]
        
        logger.info("Warming up embedding model...")
        start_time = time.time()
        _ = self.embed_texts(sample_texts)
        warm_up_time = time.time() - start_time
        logger.info(f"Model warmed up in {warm_up_time:.2f} seconds")