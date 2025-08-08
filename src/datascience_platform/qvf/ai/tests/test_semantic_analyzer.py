"""Tests for QVF Semantic Analyzer

These tests verify the semantic analysis functionality including
AI-powered analysis, fallback behavior, and batch processing.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import time
from typing import List, Dict, Any

from ..semantic import (
    SemanticAnalyzer, 
    SemanticAnalysisResult, 
    BatchAnalysisResult,
    AnalysisPriority
)
from ..ollama_manager import OllamaManager, InferenceResponse
from ..fallback import FallbackEngine
from ..prompt_templates import AnalysisType


class TestSemanticAnalyzer:
    """Test suite for SemanticAnalyzer."""
    
    @pytest.fixture
    def mock_ollama_manager(self):
        """Create mock Ollama manager."""
        mock_manager = Mock(spec=OllamaManager)
        mock_manager.is_available.return_value = True
        return mock_manager
    
    @pytest.fixture
    def mock_ollama_unavailable(self):
        """Create mock unavailable Ollama manager."""
        mock_manager = Mock(spec=OllamaManager)
        mock_manager.is_available.return_value = False
        return mock_manager
    
    @pytest.fixture
    def mock_fallback_engine(self):
        """Create mock fallback engine."""
        mock_engine = Mock(spec=FallbackEngine)
        mock_engine.analyze_work_item.return_value = {
            'score': 0.75,
            'confidence': 0.8,
            'insights': ['Fallback analysis insight'],
            'structured_data': {
                'business_value_score': 8,
                'confidence_level': 8,
                'key_insights': ['Fallback analysis insight']
            }
        }
        return mock_engine
    
    @pytest.fixture
    def analyzer_with_ai(self, mock_ollama_manager, mock_fallback_engine):
        """Create analyzer with AI available."""
        return SemanticAnalyzer(
            ollama_manager=mock_ollama_manager,
            fallback_engine=mock_fallback_engine,
            enable_caching=True,
            max_concurrent=3
        )
    
    @pytest.fixture
    def analyzer_no_ai(self, mock_ollama_unavailable, mock_fallback_engine):
        """Create analyzer with no AI available."""
        return SemanticAnalyzer(
            ollama_manager=mock_ollama_unavailable,
            fallback_engine=mock_fallback_engine,
            enable_caching=True
        )
    
    @pytest.fixture
    def sample_work_item(self):
        """Create sample work item for testing."""
        return {
            'id': 'TEST-001',
            'title': 'Implement customer payment system',
            'description': 'Build secure payment processing system to increase revenue and improve customer experience',
            'acceptance_criteria': 'System must process payments securely and provide real-time feedback'
        }
    
    @pytest.fixture
    def mock_ai_response(self):
        """Create mock AI response."""
        return InferenceResponse(
            model="llama2:7b",
            response=json.dumps({
                "business_value_score": 9,
                "value_drivers": [
                    {"driver": "revenue generation", "impact": "High", "rationale": "Payment system directly impacts revenue"}
                ],
                "customer_impact": {
                    "direct_impact": "Improved payment experience",
                    "indirect_impact": "Increased customer satisfaction",
                    "impact_timeline": "Short-term"
                },
                "revenue_potential": {
                    "revenue_category": "Revenue Generation",
                    "confidence": "High",
                    "rationale": "Direct payment processing impact"
                },
                "competitive_advantage": {
                    "provides_advantage": True,
                    "advantage_type": "Feature Parity",
                    "sustainability": "High"
                },
                "key_insights": [
                    "Strong revenue generation potential",
                    "High customer impact",
                    "Strategic payment capabilities"
                ],
                "confidence_level": 9
            }),
            done=True
        )
    
    def test_analyze_work_item_with_ai(self, analyzer_with_ai, sample_work_item, mock_ai_response, mock_ollama_manager):
        """Test work item analysis with AI available."""
        # Setup AI response
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE],
            priority=AnalysisPriority.HIGH
        )
        
        assert len(results) == 1
        result = results[0]
        
        assert isinstance(result, SemanticAnalysisResult)
        assert result.work_item_id == 'TEST-001'
        assert result.analysis_type == AnalysisType.BUSINESS_VALUE
        assert result.used_ai == True
        assert result.model_used == "llama2:7b"
        assert result.score > 0.0
        assert result.confidence > 0.0
        assert len(result.insights) > 0
        assert result.error_message is None
        
        # Verify AI was called
        mock_ollama_manager.generate.assert_called_once()
    
    def test_analyze_work_item_fallback(self, analyzer_no_ai, sample_work_item, mock_fallback_engine):
        """Test work item analysis with fallback when AI unavailable."""
        results = analyzer_no_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        assert isinstance(result, SemanticAnalysisResult)
        assert result.work_item_id == 'TEST-001'
        assert result.analysis_type == AnalysisType.BUSINESS_VALUE
        assert result.used_ai == False
        assert result.model_used is None
        assert result.score == 0.75  # From mock fallback
        assert result.confidence == 0.8  # From mock fallback
        assert result.insights == ['Fallback analysis insight']
        assert result.error_message is None
        
        # Verify fallback was called
        mock_fallback_engine.analyze_work_item.assert_called_once_with(
            sample_work_item, AnalysisType.BUSINESS_VALUE, None
        )
    
    def test_multiple_analysis_types(self, analyzer_with_ai, sample_work_item, mock_ai_response, mock_ollama_manager):
        """Test analysis with multiple analysis types."""
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        analysis_types = [
            AnalysisType.BUSINESS_VALUE,
            AnalysisType.STRATEGIC_ALIGNMENT,
            AnalysisType.RISK_ASSESSMENT
        ]
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=analysis_types
        )
        
        assert len(results) == 3
        
        # Check each result
        for i, analysis_type in enumerate(analysis_types):
            result = results[i]
            assert result.analysis_type == analysis_type
            assert result.used_ai == True
            assert result.error_message is None
        
        # Should have called AI for each analysis type
        assert mock_ollama_manager.generate.call_count == 3
    
    def test_ai_failure_fallback(self, analyzer_with_ai, sample_work_item, mock_ollama_manager, mock_fallback_engine):
        """Test fallback when AI analysis fails."""
        # Make AI generate return None (failure)
        mock_ollama_manager.generate.return_value = None
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        # Should have fallen back to mathematical analysis
        assert result.used_ai == False
        assert result.score == 0.75  # From mock fallback
        assert result.error_message is None
        
        # Both AI and fallback should have been called
        mock_ollama_manager.generate.assert_called_once()
        mock_fallback_engine.analyze_work_item.assert_called_once()
    
    def test_caching_functionality(self, analyzer_with_ai, sample_work_item, mock_ai_response, mock_ollama_manager):
        """Test result caching."""
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        # First analysis
        results1 = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        # Second identical analysis
        results2 = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results1) == 1
        assert len(results2) == 1
        
        # Results should be similar (from cache)
        assert results1[0].score == results2[0].score
        assert results1[0].confidence == results2[0].confidence
        
        # AI should only be called once due to caching
        assert mock_ollama_manager.generate.call_count == 1
    
    def test_caching_disabled(self, mock_ollama_manager, mock_fallback_engine, sample_work_item, mock_ai_response):
        """Test analysis with caching disabled."""
        analyzer = SemanticAnalyzer(
            ollama_manager=mock_ollama_manager,
            fallback_engine=mock_fallback_engine,
            enable_caching=False
        )
        
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        # Two identical analyses
        results1 = analyzer.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        results2 = analyzer.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        # AI should be called twice (no caching)
        assert mock_ollama_manager.generate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_analyze_work_item_async(self, analyzer_with_ai, sample_work_item, mock_ai_response, mock_ollama_manager):
        """Test async work item analysis."""
        # Mock async generate
        mock_ollama_manager.generate_async = AsyncMock(return_value=mock_ai_response)
        
        results = await analyzer_with_ai.analyze_work_item_async(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        assert result.used_ai == True
        assert result.model_used == "llama2:7b"
        assert result.error_message is None
        
        # Verify async AI was called
        mock_ollama_manager.generate_async.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_analysis_exception_handling(self, analyzer_with_ai, sample_work_item, mock_ollama_manager, mock_fallback_engine):
        """Test async analysis exception handling."""
        # Make async generate raise exception
        mock_ollama_manager.generate_async = AsyncMock(side_effect=Exception("AI Error"))
        
        results = await analyzer_with_ai.analyze_work_item_async(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        # Should have fallen back to mathematical analysis
        assert result.used_ai == False
        assert result.error_message is None  # Fallback should succeed
        
        # Fallback should have been called
        mock_fallback_engine.analyze_work_item.assert_called_once()
    
    def test_batch_analysis(self, analyzer_with_ai, mock_ai_response, mock_ollama_manager):
        """Test batch analysis of multiple work items."""
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        work_items = [
            {'id': 'ITEM-001', 'title': 'First item', 'description': 'First description'},
            {'id': 'ITEM-002', 'title': 'Second item', 'description': 'Second description'},
            {'id': 'ITEM-003', 'title': 'Third item', 'description': 'Third description'}
        ]
        
        batch_result = analyzer_with_ai.analyze_batch(
            work_items=work_items,
            analysis_types=[AnalysisType.BUSINESS_VALUE, AnalysisType.RISK_ASSESSMENT]
        )
        
        assert isinstance(batch_result, BatchAnalysisResult)
        assert batch_result.total_items == 6  # 3 items × 2 analysis types
        assert batch_result.successful_analyses > 0
        assert batch_result.failed_analyses == 0
        assert batch_result.ai_analyses == batch_result.successful_analyses
        assert batch_result.fallback_analyses == 0
        assert len(batch_result.results) == 6
        
        # Check success rate
        assert batch_result.success_rate == 1.0
        assert batch_result.ai_usage_rate == 1.0
        
        # Verify all results are present
        item_ids = set()
        analysis_types = set()
        for result in batch_result.results:
            item_ids.add(result.work_item_id)
            analysis_types.add(result.analysis_type)
        
        assert len(item_ids) == 3
        assert len(analysis_types) == 2
    
    def test_batch_analysis_with_failures(self, analyzer_with_ai, mock_ollama_manager, mock_fallback_engine):
        """Test batch analysis with some failures."""
        # Make AI fail for some calls, succeed for others
        call_count = 0
        def generate_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Fail every second call
                return None
            return mock_ai_response
        
        mock_ollama_manager.generate.side_effect = generate_side_effect
        
        work_items = [
            {'id': 'ITEM-001', 'title': 'First item'},
            {'id': 'ITEM-002', 'title': 'Second item'}
        ]
        
        batch_result = analyzer_with_ai.analyze_batch(
            work_items=work_items,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert batch_result.total_items == 2
        assert batch_result.successful_analyses == 2  # Fallback should succeed
        assert batch_result.failed_analyses == 0
        assert batch_result.ai_analyses == 1  # Only half succeeded with AI
        assert batch_result.fallback_analyses == 1  # Other half used fallback
        
        # Check mixed AI usage rate
        assert batch_result.ai_usage_rate == 0.5
    
    def test_performance_stats_tracking(self, analyzer_with_ai, sample_work_item, mock_ai_response, mock_ollama_manager):
        """Test performance statistics tracking."""
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        # Initial stats
        initial_stats = analyzer_with_ai.get_performance_stats()
        assert initial_stats['total_analyses'] == 0
        assert initial_stats['ai_analyses'] == 0
        assert initial_stats['fallback_analyses'] == 0
        
        # Perform some analyses
        analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE, AnalysisType.RISK_ASSESSMENT]
        )
        
        # Check updated stats
        stats = analyzer_with_ai.get_performance_stats()
        assert stats['total_analyses'] == 2
        assert stats['ai_analyses'] == 2
        assert stats['fallback_analyses'] == 0
        assert stats['ai_usage_rate'] == 1.0
        assert stats['success_rate'] == 1.0
        assert stats['avg_processing_time'] > 0
    
    def test_context_passing(self, analyzer_with_ai, sample_work_item, mock_ollama_manager):
        """Test context passing to analysis methods."""
        mock_ollama_manager.generate.return_value = InferenceResponse(
            model="llama2:7b",
            response='{"strategic_alignment_score": 8, "confidence_level": 8, "key_insights": ["test"]}',
            done=True
        )
        
        context = {
            'pi_objectives': ['Payment improvements'],
            'business_outcomes': ['Revenue growth']
        }
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.STRATEGIC_ALIGNMENT],
            context=context
        )
        
        assert len(results) == 1
        
        # Verify context was passed to AI (check call arguments)
        call_args = mock_ollama_manager.generate.call_args
        # The prompt should include context information
        prompt = call_args[1]['prompt']
        assert 'Payment improvements' in prompt or 'Revenue growth' in prompt
    
    def test_invalid_ai_response_handling(self, analyzer_with_ai, sample_work_item, mock_ollama_manager, mock_fallback_engine):
        """Test handling of invalid AI responses."""
        # Mock invalid JSON response
        mock_ollama_manager.generate.return_value = InferenceResponse(
            model="llama2:7b",
            response="This is not valid JSON",
            done=True
        )
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        # Should have fallen back to mathematical analysis
        assert result.used_ai == False
        assert result.error_message is None
        
        # Both AI and fallback should have been called
        mock_ollama_manager.generate.assert_called_once()
        mock_fallback_engine.analyze_work_item.assert_called_once()
    
    def test_cache_clearing(self, analyzer_with_ai):
        """Test cache clearing functionality."""
        # Add some items to cache (simulate cached results)
        analyzer_with_ai._analysis_cache = {
            'key1': Mock(spec=SemanticAnalysisResult),
            'key2': Mock(spec=SemanticAnalysisResult),
            'key3': Mock(spec=SemanticAnalysisResult)
        }
        
        cleared_count = analyzer_with_ai.clear_cache()
        
        assert cleared_count == 3
        assert len(analyzer_with_ai._analysis_cache) == 0
    
    def test_work_item_id_generation(self, analyzer_with_ai, mock_ai_response, mock_ollama_manager):
        """Test work item ID generation for items without explicit ID."""
        mock_ollama_manager.generate.return_value = mock_ai_response
        
        work_item_no_id = {
            'title': 'No ID item',
            'description': 'This item has no explicit ID'
        }
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=work_item_no_id,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        # Should generate a work item ID
        assert result.work_item_id is not None
        assert len(result.work_item_id) > 0
        assert result.work_item_id != 'None'
    
    def test_error_result_generation(self, analyzer_with_ai, sample_work_item, mock_ollama_manager, mock_fallback_engine):
        """Test error result generation when both AI and fallback fail."""
        # Make both AI and fallback fail
        mock_ollama_manager.generate.side_effect = Exception("AI failed")
        mock_fallback_engine.analyze_work_item.side_effect = Exception("Fallback failed")
        
        results = analyzer_with_ai.analyze_work_item(
            work_item=sample_work_item,
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        assert len(results) == 1
        result = results[0]
        
        # Should create error result
        assert result.error_message is not None
        assert "Fallback failed" in result.error_message
        assert result.score == 0.0
        assert result.confidence == 0.0
        assert result.used_ai == False
        assert len(result.insights) == 0


class AsyncMock(Mock):
    """Helper for mocking async methods."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)