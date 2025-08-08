"""Integration Tests for QVF AI Module

These tests verify the complete integration between AI components
and the mathematical fallback system.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any

from ..ollama_manager import OllamaManager
from ..semantic import SemanticAnalyzer
from ..fallback import FallbackEngine
from ..prompt_templates import QVFPromptTemplates, AnalysisType


class TestQVFAIIntegration:
    """Integration test suite for QVF AI module."""
    
    @pytest.fixture
    def real_fallback_engine(self):
        """Create real fallback engine for testing."""
        return FallbackEngine()
    
    @pytest.fixture
    def mock_ollama_healthy(self):
        """Create mock healthy Ollama manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('datascience_platform.qvf.ai.ollama_manager.psutil') as mock_psutil:
                with patch('datascience_platform.qvf.ai.ollama_manager.requests') as mock_requests:
                    # Mock process detection
                    mock_process = Mock()
                    mock_process.name.return_value = "ollama"
                    mock_psutil.process_iter.return_value = [mock_process]
                    
                    # Mock API responses
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "models": [{
                            "name": "llama2:7b",
                            "size": 3800000000,
                            "modified_at": "2024-01-01T10:00:00Z",
                            "details": {
                                "family": "llama",
                                "parameter_size": "7B",
                                "quantization_level": "Q4_0"
                            }
                        }]
                    }
                    mock_requests.get.return_value = mock_response
                    
                    yield OllamaManager(cache_dir=Path(temp_dir))
    
    @pytest.fixture
    def mock_ollama_unhealthy(self):
        """Create mock unhealthy Ollama manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('datascience_platform.qvf.ai.ollama_manager.psutil') as mock_psutil:
                # Mock no process
                mock_psutil.process_iter.return_value = []
                yield OllamaManager(cache_dir=Path(temp_dir))
    
    @pytest.fixture
    def comprehensive_work_items(self):
        """Create comprehensive set of work items for testing."""
        return [
            {
                'id': 'HIGH_VALUE-001',
                'title': 'Revenue Optimization Platform',
                'description': '''
                Build comprehensive revenue optimization platform to increase sales by 25%
                and reduce customer acquisition costs. Platform will use machine learning
                algorithms to analyze customer behavior and optimize pricing strategies.
                Requires integration with payment systems and real-time analytics.
                ''',
                'acceptance_criteria': '''
                - Increase conversion rates by 15%
                - Reduce processing costs by 20%
                - Provide real-time pricing recommendations
                - Integrate with existing payment systems
                '''
            },
            {
                'id': 'COMPLEX-002',
                'title': 'Distributed Microservices Architecture Migration',
                'description': '''
                Migrate monolithic application to distributed microservices architecture
                using Kubernetes orchestration. Requires complex service decomposition,
                data migration, and extensive integration testing. High technical risk
                due to distributed system complexity and performance requirements.
                ''',
                'acceptance_criteria': '''
                - Decompose into 15+ microservices
                - Maintain sub-100ms response times
                - Implement distributed tracing
                - Zero-downtime deployment
                '''
            },
            {
                'id': 'SIMPLE-003',
                'title': 'Update User Interface Colors',
                'description': 'Update the color scheme of the user interface to match new brand guidelines.',
                'acceptance_criteria': 'Apply new color palette to all UI components'
            },
            {
                'id': 'STRATEGIC-004',
                'title': 'Digital Transformation Platform',
                'description': '''
                Build strategic digital transformation platform to enable organizational
                capabilities and support business model evolution. Platform will provide
                foundation for future innovation and competitive advantage. Requires
                architectural alignment with enterprise strategy and stakeholder buy-in.
                ''',
                'acceptance_criteria': '''
                - Support 10x user growth
                - Enable new business models
                - Provide capability foundation
                - Align with strategic objectives
                '''
            },
            {
                'id': 'RISKY-005',
                'title': 'Experimental AI-Powered Feature',
                'description': '''
                Implement experimental artificial intelligence feature using unproven
                neural network architecture. Requires dependency on third-party AI service
                and complex integration with existing systems. High uncertainty around
                technical feasibility and performance requirements.
                ''',
                'acceptance_criteria': '''
                - Implement neural network integration
                - Achieve 85% accuracy threshold
                - Handle real-time inference
                - Graceful fallback mechanisms
                '''
            }
        ]
    
    def test_end_to_end_analysis_with_ai(self, mock_ollama_healthy, real_fallback_engine, comprehensive_work_items):
        """Test complete end-to-end analysis with AI available."""
        # Mock AI responses for different analysis types
        ai_responses = {
            AnalysisType.BUSINESS_VALUE: {
                "business_value_score": 9,
                "value_drivers": [{"driver": "revenue generation", "impact": "High", "rationale": "Direct revenue impact"}],
                "customer_impact": {"direct_impact": "High", "indirect_impact": "Medium", "impact_timeline": "Short-term"},
                "revenue_potential": {"revenue_category": "Revenue Generation", "confidence": "High", "rationale": "Strong indicators"},
                "competitive_advantage": {"provides_advantage": True, "advantage_type": "Innovation", "sustainability": "High"},
                "key_insights": ["Strong revenue potential", "High customer impact"],
                "confidence_level": 9
            },
            AnalysisType.RISK_ASSESSMENT: {
                "overall_risk_score": 7,
                "risk_factors": [{"risk_category": "Technical", "risk_description": "Integration complexity", "probability": "Medium", "impact": "High", "risk_score": 7, "mitigation_strategies": ["Prototype testing"]}],
                "technical_risks": [{"risk": "Technical complexity", "complexity_factor": "High", "skill_availability": "Limited", "technology_maturity": "Emerging"}],
                "business_risks": [{"risk": "Market uncertainty", "market_impact": "Medium", "stakeholder_impact": "High", "timeline_sensitivity": "Critical"}],
                "dependency_risks": [{"dependency": "Third-party services", "dependency_risk": "High", "impact_if_delayed": "High", "mitigation_options": ["Alternative providers"]}],
                "risk_mitigation_plan": {"primary_mitigations": ["Detailed planning"], "contingency_plans": ["Scope reduction"], "monitoring_indicators": ["Progress tracking"]},
                "confidence_level": 8
            }
        }
        
        with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
            def generate_side_effect(*args, **kwargs):
                # Determine analysis type from prompt
                prompt = kwargs.get('prompt', '')
                if 'business value' in prompt.lower():
                    response_data = ai_responses[AnalysisType.BUSINESS_VALUE]
                else:
                    response_data = ai_responses[AnalysisType.RISK_ASSESSMENT]
                
                from ..ollama_manager import InferenceResponse
                return InferenceResponse(
                    model="llama2:7b",
                    response=json.dumps(response_data),
                    done=True
                )
            
            mock_generate.side_effect = generate_side_effect
            
            # Create analyzer
            analyzer = SemanticAnalyzer(
                ollama_manager=mock_ollama_healthy,
                fallback_engine=real_fallback_engine
            )
            
            # Test single work item analysis
            results = analyzer.analyze_work_item(
                work_item=comprehensive_work_items[0],  # High value item
                analysis_types=[AnalysisType.BUSINESS_VALUE, AnalysisType.RISK_ASSESSMENT]
            )
            
            assert len(results) == 2
            
            # Check business value result
            bv_result = next(r for r in results if r.analysis_type == AnalysisType.BUSINESS_VALUE)
            assert bv_result.used_ai == True
            assert bv_result.score > 0.8  # Should be high value
            assert bv_result.confidence > 0.8
            assert len(bv_result.insights) > 0
            assert bv_result.error_message is None
            
            # Check risk assessment result
            risk_result = next(r for r in results if r.analysis_type == AnalysisType.RISK_ASSESSMENT)
            assert risk_result.used_ai == True
            assert risk_result.score > 0.6  # Should have some risk
            assert risk_result.confidence > 0.7
            assert len(risk_result.insights) > 0
            assert risk_result.error_message is None
    
    def test_end_to_end_analysis_fallback_only(self, mock_ollama_unhealthy, real_fallback_engine, comprehensive_work_items):
        """Test complete end-to-end analysis with fallback only."""
        # Create analyzer with unavailable AI
        analyzer = SemanticAnalyzer(
            ollama_manager=mock_ollama_unhealthy,
            fallback_engine=real_fallback_engine
        )
        
        # Test all analysis types on complex work item
        analysis_types = [
            AnalysisType.BUSINESS_VALUE,
            AnalysisType.STRATEGIC_ALIGNMENT,
            AnalysisType.RISK_ASSESSMENT,
            AnalysisType.COMPLEXITY_ANALYSIS,
            AnalysisType.FINANCIAL_IMPACT,
            AnalysisType.STAKEHOLDER_IMPACT
        ]
        
        results = analyzer.analyze_work_item(
            work_item=comprehensive_work_items[1],  # Complex technical item
            analysis_types=analysis_types
        )
        
        assert len(results) == 6
        
        # All results should use fallback
        for result in results:
            assert result.used_ai == False
            assert result.model_used is None
            assert result.score >= 0.0
            assert result.score <= 1.0
            assert result.confidence > 0.0
            assert isinstance(result.insights, list)
            assert result.error_message is None
            assert 'structured_data' in result.__dict__
        
        # Complex item should have high complexity and risk scores
        complexity_result = next(r for r in results if r.analysis_type == AnalysisType.COMPLEXITY_ANALYSIS)
        risk_result = next(r for r in results if r.analysis_type == AnalysisType.RISK_ASSESSMENT)
        
        assert complexity_result.score > 0.6  # Should be complex
        assert risk_result.score > 0.4  # Should have some risk
    
    def test_batch_analysis_mixed_scenarios(self, mock_ollama_healthy, real_fallback_engine, comprehensive_work_items):
        """Test batch analysis with mixed AI success/failure scenarios."""
        # Setup AI to succeed for some items, fail for others
        call_count = 0
        def generate_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count % 3 == 0:  # Fail every third call
                return None
            
            # Return successful response
            from ..ollama_manager import InferenceResponse
            return InferenceResponse(
                model="llama2:7b",
                response=json.dumps({
                    "business_value_score": 7,
                    "key_insights": ["AI analysis insight"],
                    "confidence_level": 8
                }),
                done=True
            )
        
        with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
            mock_generate.side_effect = generate_side_effect
            
            analyzer = SemanticAnalyzer(
                ollama_manager=mock_ollama_healthy,
                fallback_engine=real_fallback_engine
            )
            
            # Analyze all work items
            batch_result = analyzer.analyze_batch(
                work_items=comprehensive_work_items,
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            
            assert batch_result.total_items == 5  # 5 work items × 1 analysis type
            assert batch_result.successful_analyses == 5  # All should succeed (AI or fallback)
            assert batch_result.failed_analyses == 0
            assert batch_result.ai_analyses > 0  # Some AI successes
            assert batch_result.fallback_analyses > 0  # Some fallbacks
            assert batch_result.success_rate == 1.0
            assert 0.0 < batch_result.ai_usage_rate < 1.0  # Mixed usage
    
    def test_comparative_analysis_ai_vs_fallback(self, mock_ollama_healthy, real_fallback_engine, comprehensive_work_items):
        """Test comparative analysis between AI and fallback results."""
        # Setup consistent AI response
        ai_response_data = {
            "business_value_score": 8,
            "key_insights": ["AI detected revenue potential", "Strategic value identified"],
            "confidence_level": 9,
            "value_drivers": [{"driver": "revenue", "impact": "High", "rationale": "AI analysis"}],
            "customer_impact": {"direct_impact": "High", "indirect_impact": "Medium", "impact_timeline": "Short-term"},
            "revenue_potential": {"revenue_category": "Revenue Generation", "confidence": "High", "rationale": "AI analysis"},
            "competitive_advantage": {"provides_advantage": True, "advantage_type": "Innovation", "sustainability": "High"}
        }
        
        with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
            from ..ollama_manager import InferenceResponse
            mock_generate.return_value = InferenceResponse(
                model="llama2:7b",
                response=json.dumps(ai_response_data),
                done=True
            )
            
            # Analyze with AI
            analyzer_ai = SemanticAnalyzer(
                ollama_manager=mock_ollama_healthy,
                fallback_engine=real_fallback_engine
            )
            
            ai_results = analyzer_ai.analyze_work_item(
                work_item=comprehensive_work_items[0],  # Revenue optimization item
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
        
        # Analyze with fallback only
        analyzer_fallback = SemanticAnalyzer(
            ollama_manager=mock_ollama_unhealthy,
            fallback_engine=real_fallback_engine
        )
        
        fallback_results = analyzer_fallback.analyze_work_item(
            work_item=comprehensive_work_items[0],
            analysis_types=[AnalysisType.BUSINESS_VALUE]
        )
        
        ai_result = ai_results[0]
        fallback_result = fallback_results[0]
        
        # Both should produce valid results
        assert ai_result.used_ai == True
        assert fallback_result.used_ai == False
        
        # Both should detect business value (revenue keywords present)
        assert ai_result.score > 0.5
        assert fallback_result.score > 0.5
        
        # AI might have higher confidence due to more sophisticated analysis
        # but fallback should still be reasonably confident for clear cases
        assert ai_result.confidence > 0.8
        assert fallback_result.confidence > 0.4
        
        # Both should have insights
        assert len(ai_result.insights) > 0
        assert len(fallback_result.insights) > 0
    
    def test_prompt_template_integration(self, comprehensive_work_items):
        """Test prompt template generation and validation."""
        work_item = comprehensive_work_items[0]  # Revenue optimization item
        
        # Test all analysis types
        for analysis_type in AnalysisType:
            # Generate prompt
            system_prompt = QVFPromptTemplates.get_system_prompt(analysis_type)
            user_prompt = QVFPromptTemplates.get_analysis_prompt(analysis_type, work_item)
            options = QVFPromptTemplates.get_default_options(analysis_type)
            
            # Verify prompts are generated
            assert len(system_prompt) > 0
            assert len(user_prompt) > 0
            assert isinstance(options, dict)
            assert 'temperature' in options
            
            # Verify work item content is in user prompt
            assert work_item['title'] in user_prompt
            assert work_item['description'] in user_prompt
            
            # Test with context for strategic alignment
            if analysis_type == AnalysisType.STRATEGIC_ALIGNMENT:
                context = {
                    'pi_objectives': ['Revenue growth', 'Platform modernization'],
                    'business_outcomes': ['Increased market share']
                }
                
                context_prompt = QVFPromptTemplates.get_analysis_prompt(
                    analysis_type, work_item, context
                )
                
                # Context should be included
                assert 'Revenue growth' in context_prompt
                assert 'Platform modernization' in context_prompt
    
    def test_performance_under_load(self, mock_ollama_healthy, real_fallback_engine):
        """Test performance with larger dataset."""
        # Generate larger dataset
        large_work_items = []
        for i in range(50):
            large_work_items.append({
                'id': f'PERF-{i:03d}',
                'title': f'Performance test item {i}',
                'description': f'Description for performance testing item number {i}. '
                            f'This item includes revenue optimization and cost reduction features. '
                            f'Complex integration requirements with third-party systems.'
            })
        
        # Mock AI for performance test
        with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
            from ..ollama_manager import InferenceResponse
            mock_generate.return_value = InferenceResponse(
                model="llama2:7b",
                response=json.dumps({
                    "business_value_score": 6,
                    "key_insights": ["Performance test insight"],
                    "confidence_level": 7
                }),
                done=True
            )
            
            analyzer = SemanticAnalyzer(
                ollama_manager=mock_ollama_healthy,
                fallback_engine=real_fallback_engine,
                max_concurrent=5
            )
            
            import time
            start_time = time.time()
            
            batch_result = analyzer.analyze_batch(
                work_items=large_work_items[:10],  # Test with smaller subset for CI
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Performance assertions
            assert batch_result.total_items == 10
            assert batch_result.successful_analyses == 10
            assert processing_time < 30.0  # Should complete within 30 seconds
            
            # Check performance stats
            stats = analyzer.get_performance_stats()
            assert stats['total_analyses'] == 10
            assert stats['avg_processing_time'] > 0
    
    def test_error_recovery_resilience(self, mock_ollama_healthy, real_fallback_engine, comprehensive_work_items):
        """Test system resilience under various error conditions."""
        error_scenarios = [
            Exception("Network error"),
            json.JSONDecodeError("Invalid JSON", "", 0),
            KeyError("Missing key"),
            ValueError("Invalid value"),
            TimeoutError("Request timeout")
        ]
        
        for error in error_scenarios:
            with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
                mock_generate.side_effect = error
                
                analyzer = SemanticAnalyzer(
                    ollama_manager=mock_ollama_healthy,
                    fallback_engine=real_fallback_engine
                )
                
                # Should gracefully fall back to mathematical analysis
                results = analyzer.analyze_work_item(
                    work_item=comprehensive_work_items[0],
                    analysis_types=[AnalysisType.BUSINESS_VALUE]
                )
                
                assert len(results) == 1
                result = results[0]
                
                # Should have fallen back successfully
                assert result.used_ai == False
                assert result.error_message is None  # Fallback should succeed
                assert result.score >= 0.0
                assert result.confidence > 0.0
    
    def test_cache_effectiveness(self, mock_ollama_healthy, real_fallback_engine, comprehensive_work_items):
        """Test caching effectiveness and TTL behavior."""
        with patch.object(mock_ollama_healthy, 'generate') as mock_generate:
            from ..ollama_manager import InferenceResponse
            mock_generate.return_value = InferenceResponse(
                model="llama2:7b",
                response=json.dumps({
                    "business_value_score": 7,
                    "key_insights": ["Cached insight"],
                    "confidence_level": 8
                }),
                done=True
            )
            
            analyzer = SemanticAnalyzer(
                ollama_manager=mock_ollama_healthy,
                fallback_engine=real_fallback_engine,
                enable_caching=True
            )
            
            work_item = comprehensive_work_items[0]
            
            # First analysis - should call AI
            results1 = analyzer.analyze_work_item(
                work_item=work_item,
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            assert mock_generate.call_count == 1
            
            # Second identical analysis - should use cache
            results2 = analyzer.analyze_work_item(
                work_item=work_item,
                analysis_types=[AnalysisType.BUSINESS_VALUE]
            )
            assert mock_generate.call_count == 1  # No additional call
            
            # Results should be equivalent
            assert results1[0].score == results2[0].score
            assert results1[0].confidence == results2[0].confidence
            
            # Check performance stats show cache usage
            stats = analyzer.get_performance_stats()
            assert stats['total_analyses'] == 2
            assert stats['cache_size'] == 1