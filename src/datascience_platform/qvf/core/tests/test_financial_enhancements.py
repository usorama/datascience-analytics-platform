"""Unit tests for QVF Financial Enhancements

Tests the enhanced financial calculator methods and QVF-financial integration
capabilities including portfolio analysis, QVF scoring integration, and
advanced Monte Carlo simulations.
"""

import unittest
import numpy as np
from datetime import datetime
from typing import Dict, List

# Import modules under test
from ..financial import (
    FinancialCalculator, FinancialMetrics, RiskLevel, CurrencyType
)

class TestFinancialEnhancements(unittest.TestCase):
    """Test suite for enhanced financial calculator features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = FinancialCalculator(
            default_discount_rate=0.10,
            default_currency=CurrencyType.USD
        )
        
        # Create sample financial metrics
        self.sample_metrics = FinancialMetrics(
            initial_investment=100000,
            implementation_cost=20000,
            expected_revenue=[50000, 60000, 70000],
            cost_savings=[10000, 15000, 20000],
            risk_level=RiskLevel.MEDIUM,
            cost_of_delay_per_month=5000,
            quality_improvement_factor=1.2,
            discount_rate=0.10
        )
        
        # Create multiple metrics for portfolio testing
        self.portfolio_metrics = [
            FinancialMetrics(
                initial_investment=50000,
                expected_revenue=[30000, 35000, 40000],
                risk_level=RiskLevel.LOW
            ),
            FinancialMetrics(
                initial_investment=150000,
                expected_revenue=[80000, 90000, 100000],
                risk_level=RiskLevel.HIGH
            ),
            FinancialMetrics(
                initial_investment=75000,
                expected_revenue=[40000, 45000, 50000],
                risk_level=RiskLevel.MEDIUM
            )
        ]
    
    def test_calculate_financial_score_for_qvf(self):
        """Test QVF financial score calculation."""
        scores = self.calculator.calculate_financial_score_for_qvf(self.sample_metrics)
        
        # Check that all expected score components are present
        self.assertIn('npv_score', scores)
        self.assertIn('roi_score', scores)
        self.assertIn('copq_score', scores)
        self.assertIn('delay_urgency_score', scores)
        self.assertIn('combined_financial_score', scores)
        self.assertIn('confidence_level', scores)
        self.assertIn('risk_adjustment_factor', scores)
        
        # Check score ranges (should be 0-1)
        for score_key, score_value in scores.items():
            if score_key in ['npv_score', 'roi_score', 'copq_score', 'delay_urgency_score', 'combined_financial_score']:
                self.assertGreaterEqual(score_value, 0.0, f"{score_key} should be >= 0")
                self.assertLessEqual(score_value, 1.0, f"{score_key} should be <= 1")
        
        # Combined score should be reasonable
        self.assertGreater(scores['combined_financial_score'], 0.0)
        self.assertLess(scores['combined_financial_score'], 1.0)
    
    def test_calculate_financial_score_with_custom_normalization(self):
        """Test QVF financial score with custom normalization parameters."""
        custom_params = {
            'npv_max': 100000,  # Lower max for higher normalized scores
            'roi_max': 1.0,     # Lower max for higher normalized scores
            'copq_max': 50000,
            'delay_cost_max': 10000
        }
        
        scores = self.calculator.calculate_financial_score_for_qvf(
            self.sample_metrics, 
            normalization_params=custom_params
        )
        
        # With lower normalization maxes, scores should generally be higher
        self.assertIn('combined_financial_score', scores)
        self.assertGreaterEqual(scores['combined_financial_score'], 0.0)
        self.assertLessEqual(scores['combined_financial_score'], 1.0)
    
    def test_calculate_portfolio_financial_metrics(self):
        """Test portfolio-level financial metrics calculation."""
        portfolio_result = self.calculator.calculate_portfolio_financial_metrics(
            self.portfolio_metrics
        )
        
        # Check structure
        self.assertIn('portfolio_metrics', portfolio_result)
        self.assertIn('individual_metrics', portfolio_result)
        self.assertIn('risk_analysis', portfolio_result)
        
        portfolio_metrics = portfolio_result['portfolio_metrics']
        
        # Check portfolio-level calculations
        self.assertIn('total_investment', portfolio_metrics)
        self.assertIn('total_npv', portfolio_metrics)
        self.assertIn('portfolio_roi', portfolio_metrics)
        self.assertIn('portfolio_risk', portfolio_metrics)
        self.assertIn('sharpe_ratio', portfolio_metrics)
        self.assertEqual(portfolio_metrics['num_items'], len(self.portfolio_metrics))
        
        # Check that individual metrics are enhanced
        individual_metrics = portfolio_result['individual_metrics']
        self.assertEqual(len(individual_metrics), len(self.portfolio_metrics))
        
        for enhanced_metric in individual_metrics:
            self.assertIsNotNone(enhanced_metric.total_financial_score)
            self.assertGreaterEqual(enhanced_metric.total_financial_score, 0.0)
            self.assertLessEqual(enhanced_metric.total_financial_score, 1.0)
        
        # Check risk analysis
        risk_analysis = portfolio_result['risk_analysis']
        self.assertIn('value_at_risk_5pct', risk_analysis)
        self.assertIn('expected_shortfall', risk_analysis)
        self.assertIn('score_volatility', risk_analysis)
    
    def test_calculate_portfolio_with_empty_list(self):
        """Test portfolio calculation with empty metrics list."""
        empty_result = self.calculator.calculate_portfolio_financial_metrics([])
        
        self.assertIn('portfolio_metrics', empty_result)
        self.assertEqual(empty_result['portfolio_metrics']['num_items'], 0)
        self.assertEqual(empty_result['portfolio_metrics']['total_investment'], 0)
        self.assertEqual(empty_result['portfolio_metrics']['total_npv'], 0)
    
    def test_enhanced_monte_carlo_simulation(self):
        """Test enhanced Monte Carlo simulation with improved statistics."""
        # Test with smaller number of simulations for faster testing
        sensitivity_result = self.calculator.perform_sensitivity_analysis(
            self.sample_metrics,
            parameter_variations={'discount_rate': [0.08, 0.10, 0.12]},
            include_monte_carlo=True,
            num_simulations=100  # Reduced for testing
        )
        
        self.assertIn('monte_carlo_results', sensitivity_result)
        
        if sensitivity_result['monte_carlo_results']:
            mc_results = sensitivity_result['monte_carlo_results']
            
            # Check enhanced statistics structure
            self.assertIn('statistics', mc_results)
            self.assertIn('simulation_quality', mc_results)
            
            stats = mc_results['statistics']
            
            # Check for enhanced statistical measures
            for metric_name, metric_stats in stats.items():
                if metric_stats:  # Only check non-empty metrics
                    self.assertIn('mean', metric_stats)
                    self.assertIn('std', metric_stats)
                    self.assertIn('skewness', metric_stats)
                    self.assertIn('kurtosis', metric_stats)
                    self.assertIn('confidence_intervals', metric_stats)
                    
                    # Check confidence intervals
                    ci = metric_stats['confidence_intervals']
                    self.assertIn('90%', ci)
                    self.assertIn('95%', ci)
                    self.assertIn('99%', ci)
                    
                    # Check that confidence intervals make sense
                    ci_90 = ci['90%']
                    self.assertLessEqual(ci_90[0], ci_90[1])  # Lower bound <= Upper bound
            
            # Check simulation quality metrics
            quality = mc_results['simulation_quality']
            self.assertIn('success_rate', quality)
            self.assertGreaterEqual(quality['success_rate'], 0.0)
            self.assertLessEqual(quality['success_rate'], 1.0)
    
    def test_calculate_advanced_npv_scenarios(self):
        """Test advanced NPV calculation with multiple scenarios."""
        scenarios = [
            {
                'name': 'Optimistic',
                'cash_flows': [80000, 90000, 100000],
                'probability': 0.3
            },
            {
                'name': 'Base Case',
                'cash_flows': [60000, 70000, 80000],
                'probability': 0.5
            },
            {
                'name': 'Pessimistic',
                'cash_flows': [40000, 50000, 60000],
                'probability': 0.2
            }
        ]
        
        result = self.calculator.calculate_advanced_npv_scenarios(
            base_investment=100000,
            scenarios=scenarios
        )
        
        # Check structure
        self.assertIn('expected_npv', result)
        self.assertIn('npv_std_deviation', result)
        self.assertIn('scenarios', result)
        self.assertIn('risk_metrics', result)
        self.assertIn('probability_of_profit', result)
        
        # Check scenario results
        self.assertEqual(len(result['scenarios']), len(scenarios))
        
        for scenario_result in result['scenarios']:
            self.assertIn('name', scenario_result)
            self.assertIn('probability', scenario_result)
            self.assertIn('npv', scenario_result)
            self.assertIn('is_profitable', scenario_result)
            self.assertIn('weighted_npv', scenario_result)
        
        # Check risk metrics
        risk_metrics = result['risk_metrics']
        self.assertIn('best_case_npv', risk_metrics)
        self.assertIn('worst_case_npv', risk_metrics)
        self.assertIn('npv_range', risk_metrics)
        
        # Verify probabilities sum to 1.0 (approximately)
        total_probability = sum(s['probability'] for s in result['scenarios'])
        self.assertAlmostEqual(total_probability, 1.0, places=6)
    
    def test_risk_level_impact_on_qvf_scores(self):
        """Test that different risk levels appropriately impact QVF scores."""
        base_scores = {}
        
        for risk_level in RiskLevel:
            test_metrics = FinancialMetrics(
                **self.sample_metrics.model_dump(),
                risk_level=risk_level
            )
            
            scores = self.calculator.calculate_financial_score_for_qvf(test_metrics)
            base_scores[risk_level] = scores['combined_financial_score']
        
        # Very low risk should have highest score (least penalty)
        # Very high risk should have lowest score (most penalty)
        self.assertGreaterEqual(
            base_scores[RiskLevel.VERY_LOW],
            base_scores[RiskLevel.HIGH]
        )
        
        self.assertGreaterEqual(
            base_scores[RiskLevel.LOW],
            base_scores[RiskLevel.VERY_HIGH]
        )
    
    def test_zero_financial_data_handling(self):
        """Test handling of work items with minimal financial data."""
        minimal_metrics = FinancialMetrics(
            initial_investment=0,
            expected_revenue=[],
            cost_savings=[]
        )
        
        scores = self.calculator.calculate_financial_score_for_qvf(minimal_metrics)
        
        # Should handle gracefully without errors
        self.assertIn('combined_financial_score', scores)
        self.assertEqual(scores['combined_financial_score'], 0.0)
        self.assertEqual(scores['npv_score'], 0.0)
        self.assertEqual(scores['roi_score'], 0.0)
    
    def test_high_confidence_high_value_scenario(self):
        """Test scoring for high-confidence, high-value scenarios."""
        high_value_metrics = FinancialMetrics(
            initial_investment=100000,
            expected_revenue=[200000, 250000, 300000],  # High returns
            cost_savings=[50000, 60000, 70000],         # High savings
            cost_of_delay_per_month=20000,              # High urgency
            risk_level=RiskLevel.LOW,                   # Low risk
            quality_improvement_factor=1.5,             # Good quality impact
            confidence_factor=0.9                      # High confidence
        )
        
        scores = self.calculator.calculate_financial_score_for_qvf(high_value_metrics)
        
        # Should produce high scores
        self.assertGreater(scores['combined_financial_score'], 0.5)
        self.assertGreater(scores['npv_score'], 0.0)
        self.assertGreater(scores['roi_score'], 0.0)
        self.assertGreater(scores['delay_urgency_score'], 0.0)
        self.assertGreater(scores['confidence_level'], 0.8)


class TestNormalizationParameters(unittest.TestCase):
    """Test suite for normalization parameter handling."""
    
    def setUp(self):
        self.calculator = FinancialCalculator()
        
        self.test_metrics = FinancialMetrics(
            initial_investment=50000,
            expected_revenue=[100000, 120000, 140000],
            cost_of_delay_per_month=10000,
            risk_level=RiskLevel.LOW
        )
    
    def test_default_normalization_parameters(self):
        """Test that default normalization parameters work correctly."""
        scores = self.calculator.calculate_financial_score_for_qvf(self.test_metrics)
        
        # With high revenue and low risk, should get reasonable scores
        self.assertGreater(scores['combined_financial_score'], 0.0)
        self.assertIn('npv_score', scores)
        self.assertIn('roi_score', scores)
    
    def test_custom_normalization_parameters(self):
        """Test custom normalization parameters."""
        # Set very high normalization values - should result in lower scores
        high_norm_params = {
            'npv_max': 10000000,  # $10M
            'roi_max': 10.0,      # 1000%
            'copq_max': 1000000,  # $1M
            'delay_cost_max': 100000  # $100K/month
        }
        
        high_norm_scores = self.calculator.calculate_financial_score_for_qvf(
            self.test_metrics, normalization_params=high_norm_params
        )
        
        # Set low normalization values - should result in higher scores (clamped at 1.0)
        low_norm_params = {
            'npv_max': 10000,    # $10K
            'roi_max': 0.5,      # 50%
            'copq_max': 5000,    # $5K
            'delay_cost_max': 1000   # $1K/month
        }
        
        low_norm_scores = self.calculator.calculate_financial_score_for_qvf(
            self.test_metrics, normalization_params=low_norm_params
        )
        
        # Low normalization should generally result in higher scores
        self.assertGreaterEqual(
            low_norm_scores['combined_financial_score'],
            high_norm_scores['combined_financial_score']
        )


if __name__ == '__main__':
    unittest.main()