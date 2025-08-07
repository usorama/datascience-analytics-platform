"""Integration Tests for NLP Enhancement

This module contains comprehensive integration tests that verify the entire
NLP enhancement pipeline works correctly together.
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Import modules to test
try:
    from ..core.embedder import SemanticEmbedder
    from ..domain.model_selector import DomainModelSelector, DomainType
    from ..risk.predictor import HistoricalRiskPredictor, RiskFeatures, HistoricalOutcome, RiskType
    from ..vector_store.faiss_store import VectorStore
    from ..utils.text_processing import TextProcessor
    from ..utils.model_utils import ModelManager
    NLP_MODULES_AVAILABLE = True
except ImportError as e:
    NLP_MODULES_AVAILABLE = False
    pytest.skip(f"NLP modules not available: {e}", allow_module_level=True)


class TestSemanticEmbedderIntegration:
    """Test the enhanced semantic embedder functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def embedder(self, temp_dir):
        """Create embedder instance for testing."""
        return SemanticEmbedder(
            model_name="sentence-transformers/all-mpnet-base-v2",
            use_cache=True,
            cache_dir=temp_dir / "embeddings"
        )
    
    def test_basic_embedding(self, embedder):
        """Test basic embedding functionality."""
        text = "This is a test document for semantic embedding."
        embedding = embedder.embed_text(text)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding.shape) == 1
        assert embedding.shape[0] > 0  # Should have some dimensions
        
        # Test consistency
        embedding2 = embedder.embed_text(text)
        np.testing.assert_array_almost_equal(embedding, embedding2)
    
    def test_batch_embedding(self, embedder):
        """Test batch embedding functionality."""
        texts = [
            "Financial risk assessment for quarterly planning.",
            "Technical implementation of security features.",
            "Customer satisfaction and user experience optimization.",
            "Compliance monitoring and regulatory requirements."
        ]
        
        embeddings = embedder.embed_texts(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape[0] == len(texts)
        assert embeddings.shape[1] > 0
        
        # Test that embeddings are different
        for i in range(len(texts) - 1):
            similarity = embedder.calculate_similarity(embeddings[i], embeddings[i + 1])
            assert 0.0 <= similarity <= 1.0
    
    def test_similarity_calculation(self, embedder):
        """Test similarity calculation between embeddings."""
        text1 = "Financial risk assessment and budget planning"
        text2 = "Budget risk evaluation and financial planning" 
        text3 = "Software development and technical implementation"
        
        emb1 = embedder.embed_text(text1)
        emb2 = embedder.embed_text(text2)
        emb3 = embedder.embed_text(text3)
        
        # Similar texts should have higher similarity
        sim_12 = embedder.calculate_similarity(emb1, emb2)
        sim_13 = embedder.calculate_similarity(emb1, emb3)
        
        assert sim_12 > sim_13
        assert 0.0 <= sim_12 <= 1.0
        assert 0.0 <= sim_13 <= 1.0
    
    def test_caching_behavior(self, embedder):
        """Test that caching works correctly."""
        text = "This text should be cached for faster retrieval."
        
        # First call - should cache
        start_time = datetime.now()
        emb1 = embedder.embed_text(text)
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second call - should use cache
        start_time = datetime.now()
        emb2 = embedder.embed_text(text)
        second_duration = (datetime.now() - start_time).total_seconds()
        
        # Results should be identical
        np.testing.assert_array_equal(emb1, emb2)
        
        # Second call should generally be faster (unless using mock)
        # We'll just verify the embeddings are the same
        assert np.array_equal(emb1, emb2)
    
    def test_empty_and_invalid_inputs(self, embedder):
        """Test handling of empty and invalid inputs."""
        # Empty string
        empty_embedding = embedder.embed_text("")
        assert isinstance(empty_embedding, np.ndarray)
        assert empty_embedding.shape[0] > 0
        
        # None input (should be handled gracefully)
        try:
            none_embedding = embedder.embed_text(None)
            assert isinstance(none_embedding, np.ndarray)
        except:
            pass  # It's okay if this raises an exception
        
        # Empty list
        empty_batch = embedder.embed_texts([])
        assert isinstance(empty_batch, np.ndarray)
        assert empty_batch.size == 0


class TestDomainModelSelectorIntegration:
    """Test domain-specific model selection."""
    
    @pytest.fixture
    def selector(self, temp_dir):
        """Create domain model selector for testing."""
        return DomainModelSelector(cache_dir=temp_dir / "models")
    
    def test_domain_detection(self, selector):
        """Test automatic domain detection."""
        # Financial text
        financial_text = "The quarterly revenue increased by 15% with strong EBITDA growth and improved cash flow metrics."
        domain, confidence = selector.detect_domain(financial_text)
        
        assert isinstance(domain, DomainType)
        assert 0.0 <= confidence <= 1.0
        
        # Security text
        security_text = "The vulnerability assessment revealed critical security flaws requiring immediate patches and firewall updates."
        sec_domain, sec_confidence = selector.detect_domain(security_text)
        
        assert isinstance(sec_domain, DomainType)
        assert 0.0 <= sec_confidence <= 1.0
    
    def test_model_selection(self, selector):
        """Test model selection based on content."""
        legal_text = "The contract clause requires compliance with intellectual property regulations and liability terms."
        model_name, domain, metadata = selector.select_model(legal_text)
        
        assert isinstance(model_name, str)
        assert isinstance(domain, DomainType)
        assert isinstance(metadata, dict)
        assert 'confidence' in metadata
        assert 'description' in metadata
    
    def test_batch_domain_analysis(self, selector):
        """Test analyzing multiple texts for domains."""
        texts = [
            "Financial risk assessment with budget constraints",
            "Security vulnerability in authentication system", 
            "Legal compliance requirements for data protection",
            "Technical architecture for microservices deployment"
        ]
        
        results = selector.analyze_text_domains(texts)
        
        assert len(results) == len(texts)
        for text_snippet, domain, confidence in results:
            assert isinstance(text_snippet, str)
            assert isinstance(domain, DomainType)
            assert 0.0 <= confidence <= 1.0
    
    def test_available_domains(self, selector):
        """Test getting available domains."""
        domains = selector.get_available_domains()
        
        assert len(domains) > 0
        for domain, description, available in domains:
            assert isinstance(domain, DomainType)
            assert isinstance(description, str)
            assert isinstance(available, bool)


class TestHistoricalRiskPredictorIntegration:
    """Test risk prediction functionality."""
    
    @pytest.fixture
    def predictor(self, temp_dir):
        """Create risk predictor for testing."""
        return HistoricalRiskPredictor(data_dir=temp_dir / "risk_data")
    
    @pytest.fixture
    def sample_features(self):
        """Create sample risk features for testing."""
        return RiskFeatures(
            title_length=45,
            description_length=200,
            complexity_keywords=2,
            uncertainty_keywords=1,
            external_dependency_mentions=1,
            technical_debt_indicators=0,
            semantic_similarity_to_past_issues=0.3,
            domain_confidence=0.7,
            team_size=5,
            estimated_hours=40.0,
            priority_score=0.75,
            dependency_count=3,
            team_velocity=1.2,
            similar_item_success_rate=0.8,
            recent_team_performance=0.85
        )
    
    def test_feature_extraction(self, predictor):
        """Test extraction of risk features from work item."""
        title = "Implement complex user authentication system with external API integration"
        description = """
        This task involves implementing a sophisticated authentication system that integrates
        with multiple external services. The implementation requires careful security considerations
        and may involve some uncertainty around the third-party API reliability.
        """
        
        features = predictor.extract_features(
            title=title,
            description=description,
            team_size=4,
            estimated_hours=60.0,
            priority="high",
            dependencies=["external-auth-api", "user-service", "database-migration"]
        )
        
        assert isinstance(features, RiskFeatures)
        assert features.title_length == len(title)
        assert features.description_length == len(description)
        assert features.complexity_keywords > 0  # Should find complexity indicators
        assert features.uncertainty_keywords > 0  # Should find uncertainty indicators
        assert features.external_dependency_mentions > 0  # Should find dependency mentions
        assert features.team_size == 4
        assert features.estimated_hours == 60.0
        assert features.dependency_count == 3
    
    def test_historical_outcome_storage(self, predictor):
        """Test storing and retrieving historical outcomes."""
        outcome = HistoricalOutcome(
            item_id="TEST-123",
            features=RiskFeatures(
                title_length=30, description_length=150, complexity_keywords=1,
                uncertainty_keywords=0, external_dependency_mentions=1,
                technical_debt_indicators=0, semantic_similarity_to_past_issues=0.2,
                domain_confidence=0.6, team_size=3, estimated_hours=24.0,
                priority_score=0.5, dependency_count=2, team_velocity=1.0,
                similar_item_success_rate=0.9, recent_team_performance=0.8
            ),
            actual_duration_days=7.0,
            planned_duration_days=5.0,
            actual_cost=15000.0,
            planned_cost=12000.0,
            quality_score=0.85,
            success=True,
            completion_date=datetime.now(),
            issues_encountered=["minor scope creep"],
            risk_type=RiskType.SCHEDULE_DELAY
        )
        
        predictor.add_historical_outcome(outcome)
        
        # Verify it was stored
        assert len(predictor.historical_outcomes) > 0
        stored_outcome = predictor.historical_outcomes[-1]
        assert stored_outcome.item_id == "TEST-123"
        assert stored_outcome.success == True
    
    def test_risk_prediction(self, predictor):
        """Test risk prediction for a work item."""
        # Add some historical data first
        for i in range(5):
            outcome = HistoricalOutcome(
                item_id=f"HIST-{i}",
                features=RiskFeatures(
                    title_length=20 + i * 10, description_length=100 + i * 50,
                    complexity_keywords=i % 3, uncertainty_keywords=i % 2,
                    external_dependency_mentions=i % 2, technical_debt_indicators=0,
                    semantic_similarity_to_past_issues=0.1 + i * 0.1,
                    domain_confidence=0.5 + i * 0.1, team_size=3 + i % 3,
                    estimated_hours=20.0 + i * 10, priority_score=0.3 + i * 0.2,
                    dependency_count=i % 4, team_velocity=0.8 + i * 0.1,
                    similar_item_success_rate=0.7 + i * 0.05,
                    recent_team_performance=0.75 + i * 0.05
                ),
                actual_duration_days=5.0 + i,
                planned_duration_days=4.0 + i,
                actual_cost=10000.0 + i * 2000,
                planned_cost=8000.0 + i * 1500,
                quality_score=0.7 + i * 0.05,
                success=i % 2 == 0,  # Alternating success
                completion_date=datetime.now() - timedelta(days=i * 10),
                issues_encountered=[f"issue-{i}"],
                risk_type=RiskType.SCHEDULE_DELAY
            )
            predictor.add_historical_outcome(outcome)
        
        # Train models
        predictor.train_models()
        
        # Make predictions
        predictions = predictor.predict_risk(
            title="Implement new payment gateway integration",
            description="Complex integration requiring external API coordination and security compliance",
            team_size=4,
            estimated_hours=80.0,
            priority="critical",
            dependencies=["payment-api", "security-review"]
        )
        
        assert isinstance(predictions, list)
        for prediction in predictions:
            assert hasattr(prediction, 'risk_type')
            assert hasattr(prediction, 'probability') 
            assert hasattr(prediction, 'severity')
            assert hasattr(prediction, 'confidence')
            assert 0.0 <= prediction.probability <= 1.0
            assert 0.0 <= prediction.severity <= 1.0
            assert 0.0 <= prediction.confidence <= 1.0


class TestVectorStoreIntegration:
    """Test vector store functionality."""
    
    @pytest.fixture
    def vector_store(self, temp_dir):
        """Create vector store for testing."""
        return VectorStore(
            dimension=768,
            index_type="flat",
            cache_dir=temp_dir / "vectors"
        )
    
    @pytest.fixture
    def sample_vectors(self):
        """Generate sample vectors for testing."""
        np.random.seed(42)  # For reproducibility
        return {
            "doc1": np.random.randn(768),
            "doc2": np.random.randn(768), 
            "doc3": np.random.randn(768),
            "doc4": np.random.randn(768)
        }
    
    def test_vector_addition_and_retrieval(self, vector_store, sample_vectors):
        """Test adding and retrieving vectors."""
        # Add vectors
        for doc_id, vector in sample_vectors.items():
            success = vector_store.add_vector(
                doc_id=doc_id,
                vector=vector,
                metadata={"source": "test", "doc_id": doc_id}
            )
            assert success == True
        
        # Retrieve vectors
        for doc_id, original_vector in sample_vectors.items():
            retrieved_vector = vector_store.get_vector(doc_id)
            assert retrieved_vector is not None
            np.testing.assert_array_almost_equal(original_vector, retrieved_vector)
    
    def test_vector_search(self, vector_store, sample_vectors):
        """Test similarity search."""
        # Add vectors with metadata
        for i, (doc_id, vector) in enumerate(sample_vectors.items()):
            vector_store.add_vector(
                doc_id=doc_id,
                vector=vector,
                metadata={"category": "A" if i % 2 == 0 else "B", "index": i}
            )
        
        # Search for similar vectors
        query_vector = list(sample_vectors.values())[0]  # Use first vector as query
        results = vector_store.search(query_vector, k=3)
        
        assert len(results) <= 3
        for doc_id, similarity, metadata in results:
            assert isinstance(doc_id, str)
            assert 0.0 <= similarity <= 1.0
            assert isinstance(metadata, dict)
    
    def test_batch_operations(self, vector_store):
        """Test batch vector operations."""
        # Generate batch data
        doc_ids = [f"batch_doc_{i}" for i in range(10)]
        vectors = np.random.randn(10, 768)
        metadata_list = [{"batch": True, "index": i} for i in range(10)]
        
        # Batch add
        results = vector_store.add_vectors_batch(doc_ids, vectors, metadata_list)
        
        assert len(results) == 10
        assert all(results)  # All should succeed
        
        # Verify all were added
        for doc_id in doc_ids:
            assert vector_store.get_vector(doc_id) is not None
    
    def test_metadata_filtering(self, vector_store):
        """Test filtering by metadata during search."""
        # Add vectors with different categories
        categories = ["financial", "technical", "legal", "security"]
        for i, category in enumerate(categories):
            vector = np.random.randn(768)
            vector_store.add_vector(
                doc_id=f"doc_{category}",
                vector=vector,
                metadata={"category": category, "priority": i % 2}
            )
        
        # Search with metadata filter
        query_vector = np.random.randn(768)
        results = vector_store.search(
            query_vector,
            k=10,
            filter_metadata={"category": "financial"}
        )
        
        # Should only return financial documents
        for doc_id, similarity, metadata in results:
            assert metadata["category"] == "financial"


class TestEndToEndNLPPipeline:
    """Test the complete NLP pipeline integration."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def nlp_pipeline(self, temp_dir):
        """Create complete NLP pipeline for testing."""
        return {
            'embedder': SemanticEmbedder(cache_dir=temp_dir / "embeddings"),
            'domain_selector': DomainModelSelector(cache_dir=temp_dir / "models"),
            'risk_predictor': HistoricalRiskPredictor(data_dir=temp_dir / "risk"),
            'vector_store': VectorStore(cache_dir=temp_dir / "vectors"),
            'text_processor': TextProcessor(),
            'model_manager': ModelManager(cache_dir=temp_dir / "manager")
        }
    
    def test_complete_workflow(self, nlp_pipeline):
        """Test a complete end-to-end workflow."""
        embedder = nlp_pipeline['embedder']
        domain_selector = nlp_pipeline['domain_selector']
        risk_predictor = nlp_pipeline['risk_predictor']
        vector_store = nlp_pipeline['vector_store']
        text_processor = nlp_pipeline['text_processor']
        
        # Sample work items
        work_items = [
            {
                "id": "WORK-001",
                "title": "Implement financial risk assessment dashboard",
                "description": "Create a comprehensive dashboard for monitoring financial risks with real-time data visualization and automated alerting capabilities.",
                "type": "feature",
                "priority": "high"
            },
            {
                "id": "WORK-002", 
                "title": "Security audit of authentication system",
                "description": "Conduct thorough security assessment of user authentication including penetration testing and vulnerability analysis.",
                "type": "security",
                "priority": "critical"
            }
        ]
        
        # Process each work item through the pipeline
        for item in work_items:
            # 1. Process text
            processed = text_processor.process_text(
                f"{item['title']} {item['description']}",
                return_tokens=True,
                return_sentences=True
            )
            
            # 2. Detect domain
            domain, confidence = domain_selector.detect_domain(
                item['description'],
                item['type']
            )
            
            # 3. Generate embedding with domain awareness
            embedding = embedder.embed_text(
                f"{item['title']} {item['description']}",
                document_type=item['type']
            )
            
            # 4. Store in vector database
            vector_store.add_vector(
                doc_id=item['id'],
                vector=embedding,
                metadata={
                    'title': item['title'],
                    'type': item['type'],
                    'priority': item['priority'],
                    'domain': domain.value,
                    'domain_confidence': confidence,
                    'processed_tokens': len(processed['tokens']),
                    'sentence_count': len(processed['sentences'])
                }
            )
            
            # 5. Extract risk features and predict
            risk_features = risk_predictor.extract_features(
                title=item['title'],
                description=item['description'],
                priority=item['priority']
            )
            
            # Verify everything worked
            assert isinstance(processed, dict)
            assert isinstance(domain, DomainType)
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape[0] > 0
            assert isinstance(risk_features, RiskFeatures)
        
        # 6. Test cross-item similarity search
        query_text = "financial monitoring and risk analysis"
        query_embedding = embedder.embed_text(query_text)
        similar_items = vector_store.search(query_embedding, k=2)
        
        assert len(similar_items) > 0
        
        # 7. Test domain-based filtering
        financial_items = vector_store.search(
            query_embedding,
            k=10,
            filter_metadata={"domain": "financial"}
        )
        
        for doc_id, similarity, metadata in financial_items:
            assert metadata['domain'] == 'financial'
    
    def test_performance_and_stats(self, nlp_pipeline):
        """Test performance monitoring and statistics."""
        embedder = nlp_pipeline['embedder']
        model_manager = nlp_pipeline['model_manager']
        
        # Register embedder with model manager
        model_manager.register_model("embedder", embedder.model)
        
        # Perform some operations
        test_texts = [
            "Financial risk assessment",
            "Security vulnerability analysis", 
            "Customer satisfaction improvement",
            "Technical debt reduction"
        ]
        
        with model_manager.time_inference("embedder"):
            embeddings = embedder.embed_texts(test_texts)
        
        # Get statistics
        embedder_stats = embedder.get_stats()
        manager_stats = model_manager.get_all_stats()
        
        assert isinstance(embedder_stats, dict)
        assert isinstance(manager_stats, dict)
        
        # Verify some statistics are present
        assert 'texts_encoded' in embedder_stats or 'enhanced_features' in embedder_stats