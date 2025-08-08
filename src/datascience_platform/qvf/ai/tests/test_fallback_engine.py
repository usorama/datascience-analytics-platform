"""Tests for QVF Fallback Engine

These tests verify that the mathematical fallback engine works correctly
and provides consistent analysis results when AI is unavailable.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from ..fallback import FallbackEngine
from ..prompt_templates import AnalysisType


class TestFallbackEngine:
    """Test suite for FallbackEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create fallback engine instance."""
        return FallbackEngine()
    
    @pytest.fixture
    def sample_work_item(self):
        """Create sample work item for testing."""
        return {
            'id': 'TEST-001',
            'title': 'Implement Customer Payment Processing',
            'description': 'Build new payment system to increase revenue and reduce costs through automation. Requires integration with third-party payment providers and complex security requirements.',
            'acceptance_criteria': 'System must process payments securely, handle failures gracefully, and provide real-time reporting.',
            'notes': 'High priority for Q1 revenue targets'
        }
    
    def test_business_value_analysis(self, engine, sample_work_item):
        """Test business value analysis."""
        result = engine.analyze_work_item(sample_work_item, AnalysisType.BUSINESS_VALUE)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        assert result['confidence'] <= 1.0
        assert isinstance(result['insights'], list)
        assert len(result['insights']) > 0
        
        # Check structured data format
        structured_data = result['structured_data']
        assert 'business_value_score' in structured_data
        assert 'value_drivers' in structured_data
        assert 'customer_impact' in structured_data
        assert 'revenue_potential' in structured_data
        assert 'competitive_advantage' in structured_data
        assert 'key_insights' in structured_data
        assert 'confidence_level' in structured_data
        
        # Should detect revenue keywords
        assert result['score'] > 0.5  # Should score well due to revenue/cost keywords
    
    def test_strategic_alignment_analysis(self, engine, sample_work_item):
        """Test strategic alignment analysis."""
        context = {
            'pi_objectives': ['Increase customer satisfaction', 'Improve payment systems'],
            'business_outcomes': ['Revenue growth', 'Cost optimization']
        }
        
        result = engine.analyze_work_item(sample_work_item, AnalysisType.STRATEGIC_ALIGNMENT, context)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        
        # Check structured data
        structured_data = result['structured_data']
        assert 'strategic_alignment_score' in structured_data
        assert 'alignment_factors' in structured_data
        assert 'pi_objective_alignment' in structured_data
        assert 'business_outcome_impact' in structured_data
        
        # Should get context boost due to payment system alignment
        assert result['score'] > 0.4
    
    def test_risk_assessment_analysis(self, engine, sample_work_item):
        """Test risk assessment analysis."""
        result = engine.analyze_work_item(sample_work_item, AnalysisType.RISK_ASSESSMENT)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        
        # Check structured data
        structured_data = result['structured_data']
        assert 'overall_risk_score' in structured_data
        assert 'risk_factors' in structured_data
        assert 'technical_risks' in structured_data
        assert 'business_risks' in structured_data
        assert 'dependency_risks' in structured_data
        assert 'risk_mitigation_plan' in structured_data
        
        # Should detect integration and security risks
        assert result['score'] > 0.3  # Should have some risk due to complexity/integration
    
    def test_complexity_analysis(self, engine, sample_work_item):
        """Test complexity analysis."""
        result = engine.analyze_work_item(sample_work_item, AnalysisType.COMPLEXITY_ANALYSIS)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        
        # Check structured data
        structured_data = result['structured_data']
        assert 'complexity_score' in structured_data
        assert 'complexity_factors' in structured_data
        assert 'technical_complexity' in structured_data
        assert 'skill_requirements' in structured_data
        assert 'effort_estimation' in structured_data
        assert 'implementation_challenges' in structured_data
        assert 'testing_complexity' in structured_data
        
        # Should detect security and integration complexity
        assert result['score'] > 0.4
    
    def test_financial_impact_analysis(self, engine, sample_work_item):
        """Test financial impact analysis."""
        result = engine.analyze_work_item(sample_work_item, AnalysisType.FINANCIAL_IMPACT)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        
        # Check structured data
        structured_data = result['structured_data']
        assert 'financial_impact_score' in structured_data
        assert 'revenue_impact' in structured_data
        assert 'cost_impact' in structured_data
        assert 'roi_indicators' in structured_data
        assert 'investment_requirements' in structured_data
        assert 'financial_risks' in structured_data
        assert 'business_case_strength' in structured_data
        
        # Should score well due to revenue and cost keywords
        assert result['score'] > 0.4
    
    def test_stakeholder_impact_analysis(self, engine, sample_work_item):
        """Test stakeholder impact analysis."""
        result = engine.analyze_work_item(sample_work_item, AnalysisType.STAKEHOLDER_IMPACT)
        
        assert result['score'] > 0.0
        assert result['score'] <= 1.0
        assert result['confidence'] > 0.0
        
        # Check structured data
        structured_data = result['structured_data']
        assert 'stakeholder_impact_score' in structured_data
        assert 'affected_stakeholders' in structured_data
        assert 'customer_impact' in structured_data
        assert 'organizational_impact' in structured_data
        assert 'change_management' in structured_data
        assert 'support_requirements' in structured_data
        assert 'stakeholder_alignment' in structured_data
        
        # Should detect customer impact
        assert result['score'] > 0.2
    
    def test_minimal_work_item(self, engine):
        """Test analysis with minimal work item data."""
        minimal_item = {
            'id': 'MIN-001',
            'title': 'Simple fix',
            'description': 'Fix bug'
        }
        
        result = engine.analyze_work_item(minimal_item, AnalysisType.BUSINESS_VALUE)
        
        # Should still produce valid results
        assert result['score'] >= 0.0
        assert result['confidence'] > 0.0
        assert isinstance(result['insights'], list)
        assert 'structured_data' in result
    
    def test_complex_technical_work_item(self, engine):
        """Test analysis with complex technical work item."""
        complex_item = {
            'id': 'COMP-001',
            'title': 'Implement machine learning recommendation algorithm',
            'description': '''
            Build advanced machine learning recommendation system using neural networks
            and distributed computing. Requires real-time streaming data processing,
            complex optimization algorithms, and integration with multiple data sources.
            Performance requirements include sub-100ms response times and 99.9% availability.
            Security requirements include encryption and authentication.
            ''',
            'acceptance_criteria': '''
            - Algorithm must achieve 95% accuracy
            - System must handle 10k requests per second
            - Must integrate with existing APIs
            - Must include monitoring and alerting
            '''
        }
        
        # Test complexity analysis
        complexity_result = engine.analyze_work_item(complex_item, AnalysisType.COMPLEXITY_ANALYSIS)
        assert complexity_result['score'] > 0.7  # Should be high complexity
        
        # Test risk analysis  
        risk_result = engine.analyze_work_item(complex_item, AnalysisType.RISK_ASSESSMENT)
        assert risk_result['score'] > 0.5  # Should have significant risk
        
        # Test business value
        value_result = engine.analyze_work_item(complex_item, AnalysisType.BUSINESS_VALUE)
        # Innovation should contribute to business value
        assert 'competitive_advantage' in str(value_result['structured_data'])
    
    def test_empty_description_handling(self, engine):
        """Test handling of work items with empty descriptions."""
        empty_item = {
            'id': 'EMPTY-001',
            'title': 'Test item',
            'description': '',
            'acceptance_criteria': None
        }
        
        result = engine.analyze_work_item(empty_item, AnalysisType.RISK_ASSESSMENT)
        
        # Should still work and indicate risk due to lack of detail
        assert result['score'] > 0.0
        assert result['confidence'] > 0.0
        # Should have some risk due to unclear requirements
        assert any('uncertainty' in insight.lower() or 'limited' in insight.lower() 
                  for insight in result['insights'])
    
    def test_keyword_pattern_matching(self, engine):
        """Test keyword pattern matching functionality."""
        # Test revenue-focused item
        revenue_item = {
            'id': 'REV-001',
            'title': 'Subscription billing system',
            'description': 'Implement subscription billing to increase revenue and improve monetization'
        }
        
        result = engine.analyze_work_item(revenue_item, AnalysisType.BUSINESS_VALUE)
        structured_data = result['structured_data']
        
        # Should detect revenue generation category
        revenue_category = structured_data['revenue_potential']['revenue_category']
        assert 'Revenue' in revenue_category
        
        # Should have high business value score
        assert result['score'] > 0.6
    
    def test_all_analysis_types_consistency(self, engine, sample_work_item):
        """Test that all analysis types produce consistent results."""
        results = {}
        
        for analysis_type in AnalysisType:
            result = engine.analyze_work_item(sample_work_item, analysis_type)
            results[analysis_type] = result
            
            # All should produce valid results
            assert result['score'] >= 0.0
            assert result['score'] <= 1.0
            assert result['confidence'] > 0.0
            assert result['confidence'] <= 1.0
            assert isinstance(result['insights'], list)
            assert 'structured_data' in result
        
        # All results should be available
        assert len(results) == len(AnalysisType)
    
    def test_context_impact_on_strategic_alignment(self, engine, sample_work_item):
        """Test that context significantly impacts strategic alignment scoring."""
        # Test without context
        result_no_context = engine.analyze_work_item(
            sample_work_item, 
            AnalysisType.STRATEGIC_ALIGNMENT
        )
        
        # Test with relevant context
        relevant_context = {
            'pi_objectives': ['payment processing improvements', 'revenue optimization'],
            'business_outcomes': ['increase customer payment success rate']
        }
        
        result_with_context = engine.analyze_work_item(
            sample_work_item, 
            AnalysisType.STRATEGIC_ALIGNMENT, 
            relevant_context
        )
        
        # Context should improve score
        assert result_with_context['score'] > result_no_context['score']
        assert result_with_context['confidence'] >= result_no_context['confidence']
    
    def test_pattern_scoring_edge_cases(self, engine):
        """Test edge cases in pattern scoring."""
        # Test with repeated keywords
        repetitive_item = {
            'id': 'REP-001',
            'title': 'Revenue revenue revenue optimization',
            'description': 'Revenue optimization to increase revenue and boost revenue streams'
        }
        
        result = engine.analyze_work_item(repetitive_item, AnalysisType.BUSINESS_VALUE)
        
        # Should handle repeated keywords gracefully
        assert result['score'] > 0.5
        assert result['score'] <= 1.0  # Should not exceed maximum
    
    def test_confidence_scoring(self, engine):
        """Test confidence scoring accuracy."""
        # High-signal item (many relevant keywords)
        high_signal_item = {
            'id': 'HIGH-001',
            'title': 'Customer revenue optimization platform',
            'description': '''
            Build comprehensive revenue optimization platform to increase sales,
            improve customer satisfaction, reduce costs through automation,
            and provide competitive advantage through innovative features.
            '''
        }
        
        # Low-signal item (few relevant keywords)
        low_signal_item = {
            'id': 'LOW-001', 
            'title': 'Update configuration',
            'description': 'Update system configuration file'
        }
        
        high_result = engine.analyze_work_item(high_signal_item, AnalysisType.BUSINESS_VALUE)
        low_result = engine.analyze_work_item(low_signal_item, AnalysisType.BUSINESS_VALUE)
        
        # High-signal item should have higher confidence
        assert high_result['confidence'] > low_result['confidence']
        assert high_result['score'] > low_result['score']
    
    def test_invalid_analysis_type_handling(self, engine, sample_work_item):
        """Test handling of invalid analysis types."""
        with pytest.raises(ValueError, match="Unknown analysis type"):
            # Create mock invalid analysis type
            invalid_type = Mock()
            invalid_type.value = "invalid_type"
            engine.analyze_work_item(sample_work_item, invalid_type)