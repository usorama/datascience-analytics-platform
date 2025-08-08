"""Unit tests for QVF Scoring Integration

Tests the integration between financial calculations and QVF criteria scoring,
including the QVFScoringEngine and various integration modes.
"""

import unittest
import numpy as np
from datetime import datetime
from typing import Dict, List

# Import modules under test
from ..scoring import (
    QVFScoringEngine, ScoringConfiguration, IntegrationMode, 
    FinancialMappingMode, WorkItemScore, ScoringValidationError
)
from ..financial import FinancialMetrics, RiskLevel
from ..criteria import QVFCriteriaEngine, CriteriaCategory
from ...ado.models import ADOWorkItem, WorkItemType, WorkItemState

class TestQVFScoringEngine(unittest.TestCase):
    """Test suite for QVF scoring engine with financial integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create scoring engine
        self.scoring_engine = QVFScoringEngine()
        
        # Create sample work items
        self.work_items = [
            ADOWorkItem(
                work_item_id=1,
                title="High Value Feature",
                work_item_type=WorkItemType.FEATURE,
                state=WorkItemState.NEW,
                business_value_raw=85,
                story_points=8,
                complexity_score=3,
                risk_score=2
            ),
            ADOWorkItem(
                work_item_id=2,
                title="Technical Debt Fix",
                work_item_type=WorkItemType.BUG,
                state=WorkItemState.NEW,
                business_value_raw=45,
                story_points=13,
                complexity_score=7,
                risk_score=5
            ),
            ADOWorkItem(
                work_item_id=3,
                title="Customer Experience Improvement",
                work_item_type=WorkItemType.FEATURE,
                state=WorkItemState.NEW,
                business_value_raw=75,
                story_points=5,
                complexity_score=2,
                risk_score=1
            )
        ]
        
        # Create financial data for work items
        self.financial_data = {
            1: FinancialMetrics(
                initial_investment=100000,
                expected_revenue=[150000, 180000, 200000],
                cost_savings=[20000, 25000, 30000],
                cost_of_delay_per_month=15000,
                risk_level=RiskLevel.LOW,
                quality_improvement_factor=1.3
            ),
            2: FinancialMetrics(
                initial_investment=80000,
                expected_revenue=[50000, 60000, 70000],
                cost_savings=[40000, 45000, 50000],  # High savings from debt reduction
                cost_of_delay_per_month=5000,
                risk_level=RiskLevel.MEDIUM,
                quality_improvement_factor=1.8  # High quality improvement
            ),
            3: FinancialMetrics(
                initial_investment=60000,
                expected_revenue=[90000, 110000, 130000],
                cost_savings=[15000, 20000, 25000],
                cost_of_delay_per_month=10000,
                risk_level=RiskLevel.LOW,
                quality_improvement_factor=1.2
            )
        }
        
        # Create QVF configuration
        self.qvf_config = self.scoring_engine.criteria_engine.get_default_configuration()
    
    def test_scoring_engine_initialization(self):
        """Test that scoring engine initializes correctly."""
        self.assertIsNotNone(self.scoring_engine.criteria_engine)
        self.assertIsNotNone(self.scoring_engine.financial_calculator)
        self.assertIsNotNone(self.scoring_engine.scoring_config)
        
        # Test with custom components
        custom_engine = QVFScoringEngine(
            scoring_config=ScoringConfiguration(
                integration_mode=IntegrationMode.FINANCIAL_PRIORITY,
                financial_weight=0.8,
                strategic_weight=0.2
            )
        )
        self.assertEqual(custom_engine.scoring_config.integration_mode, IntegrationMode.FINANCIAL_PRIORITY)
        self.assertEqual(custom_engine.scoring_config.financial_weight, 0.8)
    
    def test_score_work_items_with_financials_balanced_mode(self):
        """Test scoring with balanced integration mode."""
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data
        )
        
        # Check result structure
        self.assertIn('configuration', results)
        self.assertIn('work_item_scores', results)
        self.assertIn('portfolio_analytics', results)
        self.assertIn('scoring_quality', results)
        
        # Check work item scores
        work_item_scores = results['work_item_scores']
        self.assertEqual(len(work_item_scores), len(self.work_items))
        
        # Verify score objects
        for score in work_item_scores:
            self.assertIsInstance(score, WorkItemScore)
            self.assertGreaterEqual(score.total_score, 0.0)
            self.assertLessEqual(score.total_score, 1.0)
            self.assertGreater(score.overall_rank, 0)
            self.assertIn('npv_score', score.financial_components)
            self.assertIn('roi_score', score.financial_components)
            self.assertTrue(len(score.criteria_scores) > 0)
        
        # Check that rankings are consistent
        scores_list = [s.total_score for s in work_item_scores]
        ranks_list = [s.overall_rank for s in work_item_scores]
        
        # Higher scores should have lower (better) ranks
        sorted_by_score = sorted(work_item_scores, key=lambda x: x.total_score, reverse=True)
        for i, score_obj in enumerate(sorted_by_score):
            self.assertEqual(score_obj.overall_rank, i + 1)
    
    def test_financial_only_integration_mode(self):
        """Test financial-only integration mode."""
        financial_config = ScoringConfiguration(
            integration_mode=IntegrationMode.FINANCIAL_ONLY,
            financial_weight=1.0,
            strategic_weight=0.0
        )
        
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data,
            custom_scoring_config=financial_config
        )
        
        work_item_scores = results['work_item_scores']
        
        # In financial-only mode, total_score should equal financial_score
        for score in work_item_scores:
            self.assertAlmostEqual(score.total_score, score.financial_score, places=3)
    
    def test_strategic_only_integration_mode(self):
        """Test strategic-only integration mode."""
        strategic_config = ScoringConfiguration(
            integration_mode=IntegrationMode.CRITERIA_ONLY,
            financial_weight=0.0,
            strategic_weight=1.0
        )
        
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data,
            custom_scoring_config=strategic_config
        )
        
        work_item_scores = results['work_item_scores']
        
        # In strategic-only mode, total_score should equal strategic_score
        for score in work_item_scores:
            self.assertAlmostEqual(score.total_score, score.strategic_score, places=3)
    
    def test_financial_priority_mode(self):
        """Test financial priority integration mode."""
        financial_priority_config = ScoringConfiguration(
            integration_mode=IntegrationMode.FINANCIAL_PRIORITY,
            financial_weight=0.8,
            strategic_weight=0.2
        )
        
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data,
            custom_scoring_config=financial_priority_config
        )
        
        work_item_scores = results['work_item_scores']
        
        # Financial scores should have stronger influence on rankings
        # Item 1 has highest financial value, should likely be ranked highly
        item_1_score = next(s for s in work_item_scores if s.work_item_id == 1)
        self.assertGreater(item_1_score.financial_score, 0.1)  # Should have reasonable financial score
    
    def test_portfolio_analytics(self):
        """Test portfolio analytics generation."""
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data
        )
        
        portfolio_analytics = results['portfolio_analytics']
        
        # Check structure
        self.assertIn('score_distributions', portfolio_analytics)
        self.assertIn('portfolio_financial', portfolio_analytics)
        self.assertIn('ranking_insights', portfolio_analytics)
        self.assertIn('optimization_recommendations', portfolio_analytics)
        
        # Check score distributions
        score_dist = portfolio_analytics['score_distributions']
        self.assertIn('total_score', score_dist)
        self.assertIn('financial_score', score_dist)
        self.assertIn('strategic_score', score_dist)
        
        # Check that distributions have required statistics
        total_score_stats = score_dist['total_score']
        self.assertIn('mean', total_score_stats)
        self.assertIn('std', total_score_stats)
        self.assertIn('percentiles', total_score_stats)
        
        # Check financial portfolio analysis
        if portfolio_analytics['portfolio_financial']:
            portfolio_financial = portfolio_analytics['portfolio_financial']
            self.assertIn('portfolio_metrics', portfolio_financial)
            self.assertIn('risk_analysis', portfolio_financial)
    
    def test_scoring_quality_assessment(self):
        """Test scoring quality assessment."""
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data
        )
        
        quality_assessment = results['scoring_quality']
        
        # Check structure
        self.assertIn('overall_quality_score', quality_assessment)
        self.assertIn('financial_coverage', quality_assessment)
        self.assertIn('average_confidence', quality_assessment)
        self.assertIn('quality_assessment', quality_assessment)
        
        # Check values
        self.assertGreaterEqual(quality_assessment['overall_quality_score'], 0.0)
        self.assertLessEqual(quality_assessment['overall_quality_score'], 1.0)
        self.assertEqual(quality_assessment['financial_coverage'], 1.0)  # Full coverage in test
        
        quality_level = quality_assessment['quality_assessment']
        self.assertIn(quality_level, ['excellent', 'good', 'fair', 'poor'])
    
    def test_input_validation(self):
        """Test input validation for scoring."""
        # Test empty work items
        with self.assertRaises(ScoringValidationError):
            self.scoring_engine.score_work_items_with_financials(
                work_items=[],
                qvf_config=self.qvf_config,
                financial_data=self.financial_data
            )
        
        # Test invalid QVF configuration
        invalid_config = self.qvf_config
        invalid_config.criteria = []  # Remove all criteria
        
        with self.assertRaises(ScoringValidationError):
            self.scoring_engine.score_work_items_with_financials(
                work_items=self.work_items,
                qvf_config=invalid_config,
                financial_data=self.financial_data
            )
    
    def test_partial_financial_data(self):
        """Test handling of partial financial data coverage."""
        # Only provide financial data for first item
        partial_financial_data = {1: self.financial_data[1]}
        
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=partial_financial_data
        )
        
        # Should handle gracefully
        work_item_scores = results['work_item_scores']
        self.assertEqual(len(work_item_scores), len(self.work_items))
        
        # Item 1 should have financial score, others should have 0
        item_1_score = next(s for s in work_item_scores if s.work_item_id == 1)
        item_2_score = next(s for s in work_item_scores if s.work_item_id == 2)
        
        self.assertGreater(item_1_score.financial_score, 0.0)
        self.assertEqual(item_2_score.financial_score, 0.0)
    
    def test_analyze_financial_contribution(self):
        """Test financial contribution analysis."""
        results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data
        )
        
        contribution_analysis = self.scoring_engine.analyze_financial_contribution(results)
        
        # Check structure
        self.assertIn('financial_correlation_with_total', contribution_analysis)
        self.assertIn('items_significantly_impacted_by_financials', contribution_analysis)
        self.assertIn('financial_impact_summary', contribution_analysis)
        
        # Check correlation value
        correlation = contribution_analysis['financial_correlation_with_total']
        self.assertGreaterEqual(correlation, -1.0)
        self.assertLessEqual(correlation, 1.0)
        
        # Check impact summary
        impact_summary = contribution_analysis['financial_impact_summary']
        self.assertIn('total_impacted_items', impact_summary)
        self.assertIn('average_rank_change', impact_summary)
    
    def test_risk_adjustment_impact(self):
        """Test that risk adjustment impacts scores appropriately."""
        # Test with risk adjustment enabled
        risk_enabled_config = ScoringConfiguration(
            risk_adjustment_enabled=True,
            max_risk_penalty=0.3
        )
        
        risk_enabled_results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data,
            custom_scoring_config=risk_enabled_config
        )
        
        # Test with risk adjustment disabled
        risk_disabled_config = ScoringConfiguration(
            risk_adjustment_enabled=False
        )
        
        risk_disabled_results = self.scoring_engine.score_work_items_with_financials(
            work_items=self.work_items,
            qvf_config=self.qvf_config,
            financial_data=self.financial_data,
            custom_scoring_config=risk_disabled_config
        )
        
        # Compare results - generally, risk adjustment should lower scores for higher-risk items
        enabled_scores = {s.work_item_id: s.total_score for s in risk_enabled_results['work_item_scores']}
        disabled_scores = {s.work_item_id: s.total_score for s in risk_disabled_results['work_item_scores']}
        
        # At least some scores should be different
        score_differences = [abs(enabled_scores[wid] - disabled_scores[wid]) for wid in enabled_scores.keys()]
        self.assertTrue(any(diff > 0.01 for diff in score_differences))  # At least 1% difference


class TestScoringConfiguration(unittest.TestCase):
    """Test suite for scoring configuration validation."""
    
    def test_valid_configuration(self):
        """Test valid scoring configuration."""
        config = ScoringConfiguration(
            integration_mode=IntegrationMode.BALANCED,
            financial_weight=0.6,
            strategic_weight=0.4,
            normalization_percentile=0.95
        )
        
        issues = config.validate()
        self.assertEqual(len(issues), 0)
    
    def test_invalid_weights(self):
        """Test invalid weight configurations."""
        # Weights don't sum to 1.0
        invalid_config = ScoringConfiguration(
            financial_weight=0.6,
            strategic_weight=0.5  # Should be 0.4 to sum to 1.0
        )
        
        issues = invalid_config.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('sum to 1.0' in issue for issue in issues))
        
        # Negative weights
        negative_config = ScoringConfiguration(
            financial_weight=-0.1,
            strategic_weight=1.1
        )
        
        issues = negative_config.validate()
        self.assertGreater(len(issues), 0)
    
    def test_invalid_percentile(self):
        """Test invalid normalization percentile."""
        invalid_config = ScoringConfiguration(
            normalization_percentile=1.5  # > 1.0
        )
        
        issues = invalid_config.validate()
        self.assertGreater(len(issues), 0)
        self.assertTrue(any('percentile' in issue for issue in issues))
    
    def test_factory_functions(self):
        """Test factory functions for common configurations."""
        from ..scoring import (
            create_balanced_scoring_config,
            create_financial_priority_config,
            create_strategic_priority_config
        )
        
        # Test balanced config
        balanced = create_balanced_scoring_config()
        self.assertEqual(balanced.integration_mode, IntegrationMode.BALANCED)
        self.assertEqual(balanced.financial_weight, 0.5)
        self.assertEqual(balanced.strategic_weight, 0.5)
        self.assertEqual(len(balanced.validate()), 0)
        
        # Test financial priority config
        financial_priority = create_financial_priority_config()
        self.assertEqual(financial_priority.integration_mode, IntegrationMode.FINANCIAL_PRIORITY)
        self.assertGreater(financial_priority.financial_weight, financial_priority.strategic_weight)
        self.assertEqual(len(financial_priority.validate()), 0)
        
        # Test strategic priority config
        strategic_priority = create_strategic_priority_config()
        self.assertEqual(strategic_priority.integration_mode, IntegrationMode.STRATEGIC_PRIORITY)
        self.assertGreater(strategic_priority.strategic_weight, strategic_priority.financial_weight)
        self.assertEqual(len(strategic_priority.validate()), 0)


class TestWorkItemScore(unittest.TestCase):
    """Test suite for WorkItemScore data class."""
    
    def test_work_item_score_creation(self):
        """Test WorkItemScore creation and properties."""
        score = WorkItemScore(
            work_item_id=1,
            title="Test Item",
            work_item_type="Feature",
            total_score=0.75,
            financial_score=0.8,
            strategic_score=0.7,
            overall_rank=1,
            financial_rank=1,
            strategic_rank=2,
            financial_components={'npv_score': 0.6, 'roi_score': 0.9},
            criteria_scores={'criterion_1': 0.8},
            category_scores={'business_value': 0.75},
            confidence_level=0.85,
            risk_level='low',
            risk_adjustment=0.95
        )
        
        self.assertEqual(score.work_item_id, 1)
        self.assertEqual(score.title, "Test Item")
        self.assertEqual(score.total_score, 0.75)
        self.assertIsInstance(score.calculation_timestamp, datetime)
        self.assertEqual(score.data_quality_score, 1.0)  # Default value
        
        # Test that financial components are accessible
        self.assertEqual(score.financial_components['npv_score'], 0.6)
        self.assertEqual(score.financial_components['roi_score'], 0.9)


if __name__ == '__main__':
    unittest.main()