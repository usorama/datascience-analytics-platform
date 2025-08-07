"""Unit Tests for Enhanced Semantic Embedder

This module contains unit tests specifically for the SemanticEmbedder class.
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from ..core.embedder import SemanticEmbedder, EmbeddingCache, MockSentenceTransformer
    EMBEDDER_AVAILABLE = True
except ImportError:
    EMBEDDER_AVAILABLE = False
    pytest.skip("Embedder module not available", allow_module_level=True)


class TestEmbeddingCache:
    """Test the embedding cache functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def cache(self, temp_dir):
        """Create cache instance for testing."""
        return EmbeddingCache(
            cache_dir=temp_dir / "cache",
            ttl_hours=1,
            max_memory_items=10
        )
    
    def test_cache_initialization(self, cache, temp_dir):
        """Test cache initialization."""
        assert cache.cache_dir.exists()
        assert cache.max_memory_items == 10
        assert len(cache.memory_cache) == 0
    
    def test_cache_set_and_get(self, cache):
        """Test setting and getting cache items."""
        text = "Test text for caching"
        model_name = "test-model"
        embedding = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        
        # Set item
        cache.set(text, model_name, embedding)
        
        # Get item
        retrieved = cache.get(text, model_name)
        
        assert retrieved is not None
        np.testing.assert_array_equal(embedding, retrieved)
    
    def test_cache_miss(self, cache):
        """Test cache miss behavior."""
        result = cache.get("nonexistent text", "test-model")
        assert result is None
    
    def test_cache_statistics(self, cache):
        """Test cache statistics tracking."""
        text1 = "First text"
        text2 = "Second text"
        model_name = "test-model"
        embedding = np.array([0.1, 0.2, 0.3])
        
        # Set one item
        cache.set(text1, model_name, embedding)
        
        # Hit
        cache.get(text1, model_name)
        
        # Miss
        cache.get(text2, model_name)
        
        stats = cache.get_stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5
    
    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            cache = EmbeddingCache(
                cache_dir=temp_dir / "cache",
                max_memory_items=3  # Small cache for testing
            )
            
            model_name = "test-model"
            embedding = np.array([0.1, 0.2, 0.3])
            
            # Fill cache beyond capacity
            for i in range(5):
                cache.set(f"text_{i}", model_name, embedding)
            
            # Check that only recent items are in memory
            assert len(cache.memory_cache) <= 3
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMockSentenceTransformer:
    """Test the mock sentence transformer."""
    
    @pytest.fixture
    def mock_transformer(self):
        """Create mock transformer for testing."""
        return MockSentenceTransformer("test-model")
    
    def test_single_text_encoding(self, mock_transformer):
        """Test encoding a single text."""
        text = "Test text for encoding"
        embedding = mock_transformer.encode(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 2  # Should return 2D array
        assert embedding.shape[0] == 1
        assert embedding.shape[1] == mock_transformer.embedding_dim
        
        # Test consistency
        embedding2 = mock_transformer.encode(text)
        np.testing.assert_array_equal(embedding, embedding2)
    
    def test_batch_text_encoding(self, mock_transformer):
        """Test encoding multiple texts."""
        texts = ["First text", "Second text", "Third text"]
        embeddings = mock_transformer.encode(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] == mock_transformer.embedding_dim
        
        # Test that different texts produce different embeddings
        assert not np.array_equal(embeddings[0], embeddings[1])
    
    def test_keyword_influence(self, mock_transformer):
        """Test that keywords influence embeddings."""
        financial_text = "revenue profit financial budget investment"
        technical_text = "software development programming code architecture"
        
        fin_embedding = mock_transformer.encode(financial_text)
        tech_embedding = mock_transformer.encode(technical_text)
        
        # Should produce different embeddings
        assert not np.array_equal(fin_embedding, tech_embedding)
    
    def test_empty_text_handling(self, mock_transformer):
        """Test handling of empty text."""
        embedding = mock_transformer.encode("")
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (1, mock_transformer.embedding_dim)


class TestSemanticEmbedder:
    """Test the enhanced semantic embedder."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def embedder(self, temp_dir):
        """Create embedder for testing."""
        return SemanticEmbedder(
            model_name="sentence-transformers/all-mpnet-base-v2",
            use_cache=True,
            cache_dir=temp_dir / "embeddings",
            device="cpu"  # Force CPU for testing
        )
    
    def test_embedder_initialization(self, embedder):
        """Test embedder initialization."""
        assert embedder.model_name == "sentence-transformers/all-mpnet-base-v2"
        assert embedder.use_cache == True
        assert embedder.device in ["cpu", "cuda"]
        assert hasattr(embedder, 'model')
    
    def test_single_text_embedding(self, embedder):
        """Test embedding a single text."""
        text = "This is a test document for semantic analysis."
        embedding = embedder.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert embedding.shape[0] > 0
        
        # Test with empty text
        empty_embedding = embedder.embed_text("")
        assert isinstance(empty_embedding, np.ndarray)
        assert empty_embedding.shape[0] > 0
    
    def test_batch_text_embedding(self, embedder):
        """Test embedding multiple texts."""
        texts = [
            "Financial risk assessment document",
            "Technical architecture specification",
            "Security policy and procedures",
            "Customer feedback analysis report"
        ]
        
        embeddings = embedder.embed_texts(texts, batch_size=2)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] > 0
        
        # Test empty input
        empty_embeddings = embedder.embed_texts([])
        assert isinstance(empty_embeddings, np.ndarray)
        assert empty_embeddings.size == 0
    
    def test_similarity_calculation(self, embedder):
        """Test similarity calculation between embeddings."""
        text1 = "Financial budget planning and risk assessment"
        text2 = "Budget risk evaluation and financial planning"
        text3 = "Software development and technical architecture"
        
        emb1 = embedder.embed_text(text1)
        emb2 = embedder.embed_text(text2)
        emb3 = embedder.embed_text(text3)
        
        # Similar texts should have higher similarity
        sim_12 = embedder.calculate_similarity(emb1, emb2)
        sim_13 = embedder.calculate_similarity(emb1, emb3)
        
        assert 0.0 <= sim_12 <= 1.0
        assert 0.0 <= sim_13 <= 1.0
        assert sim_12 > sim_13  # More similar texts should have higher similarity
    
    def test_find_similar_texts(self, embedder):
        """Test finding similar texts."""
        query = "financial risk management"
        candidates = [
            "Financial risk assessment and management strategies",
            "Software development best practices",
            "Risk evaluation in financial planning",
            "Technical architecture patterns",
            "Budget risk management procedures"
        ]
        
        similar = embedder.find_similar_texts(query, candidates, top_k=3, threshold=0.1)
        
        assert len(similar) <= 3
        for idx, text, score in similar:
            assert 0 <= idx < len(candidates)
            assert isinstance(text, str)
            assert 0.0 <= score <= 1.0
        
        # Results should be sorted by similarity (descending)
        if len(similar) > 1:
            for i in range(len(similar) - 1):
                assert similar[i][2] >= similar[i + 1][2]
    
    def test_model_info_and_stats(self, embedder):
        """Test getting model information and statistics."""
        # Get initial info
        info = embedder.get_model_info()
        
        assert isinstance(info, dict)
        assert 'model_name' in info
        assert 'device' in info
        assert 'embedding_dim' in info
        
        # Perform some operations
        texts = ["Test text 1", "Test text 2", "Test text 3"]
        _ = embedder.embed_texts(texts)
        
        # Get stats
        stats = embedder.get_stats()
        
        assert isinstance(stats, dict)
        # Different implementations might have different stat keys
        # Just verify it's a dict with some content
        assert len(stats) > 0
    
    def test_cache_functionality(self, embedder):
        """Test caching behavior."""
        text = "This text should be cached for faster retrieval."
        
        # First embedding (should cache)
        emb1 = embedder.embed_text(text)
        
        # Second embedding (should use cache)
        emb2 = embedder.embed_text(text)
        
        # Should be identical
        np.testing.assert_array_equal(emb1, emb2)
        
        # Clear cache and test
        embedder.clear_cache()
        
        # Should still work after cache clear
        emb3 = embedder.embed_text(text)
        assert isinstance(emb3, np.ndarray)
    
    def test_warm_up(self, embedder):
        """Test model warm-up functionality."""
        # Should complete without error
        embedder.warm_up()
        
        # Test with custom texts
        custom_texts = ["Warm up text 1", "Warm up text 2"]
        embedder.warm_up(custom_texts)
    
    def test_error_handling(self, embedder):
        """Test error handling with invalid inputs."""
        # None input
        try:
            result = embedder.embed_text(None)
            # Should either handle gracefully or raise an exception
            assert isinstance(result, np.ndarray)
        except:
            pass  # Exception is acceptable
        
        # Very long text (should be handled gracefully)
        long_text = "word " * 10000
        embedding = embedder.embed_text(long_text)
        assert isinstance(embedding, np.ndarray)
        
        # Invalid similarity calculation
        emb1 = np.array([1, 2, 3])
        emb2 = np.array([1, 2])  # Different dimensions
        similarity = embedder.calculate_similarity(emb1, emb2)
        assert similarity == 0.0  # Should handle gracefully


class TestSemanticEmbedderWithMocks:
    """Test embedder with mocked dependencies."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('datascience_platform.nlp.core.embedder.SENTENCE_TRANSFORMERS_AVAILABLE', False)
    def test_fallback_to_mock(self, temp_dir):
        """Test fallback to mock transformer when sentence-transformers unavailable."""
        embedder = SemanticEmbedder(cache_dir=temp_dir / "cache")
        
        # Should still work with mock
        text = "Test text with mock transformer"
        embedding = embedder.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape[0] > 0
    
    def test_caching_with_mocked_model(self, temp_dir):
        """Test caching behavior with mocked model."""
        with patch('datascience_platform.nlp.core.embedder.SENTENCE_TRANSFORMERS_AVAILABLE', False):
            embedder = SemanticEmbedder(use_cache=True, cache_dir=temp_dir / "cache")
            
            # Mock the model
            mock_model = Mock()
            mock_embedding = np.array([0.1, 0.2, 0.3])
            mock_model.encode.return_value = mock_embedding
            embedder.model = mock_model
            
            text = "Cached text"
            
            # First call
            emb1 = embedder.embed_text(text)
            assert mock_model.encode.call_count == 1
            
            # Second call (should use cache)
            emb2 = embedder.embed_text(text)
            # Model should not be called again due to caching
            assert mock_model.encode.call_count == 1
            
            np.testing.assert_array_equal(emb1, emb2)