"""Unit tests for QVF financial calculator system.

Comprehensive tests covering:
- FinancialMetrics model validation and calculations
- NPV, COPQ, and ROI calculations
- FinancialCalculator comprehensive functionality
- Risk adjustments and sensitivity analysis
- Monte Carlo simulations
- Integration with QVF criteria system
- Error handling and edge cases

These tests ensure >90% code coverage and validate all financial calculations.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import patch, MagicMock

from datascience_platform.qvf.core.financial import (
    FinancialMetrics,
    FinancialCalculator,
    NPVCalculation,
    COPQCalculation,
    ROICalculation,
    RiskLevel,
    CurrencyType,
    FinancialValidationError,
    quick_npv,
    quick_roi,
    payback_period
)
from ..test_fixtures import create_test_financial_metrics


class TestFinancialMetrics:
    """Test cases for FinancialMetrics model."""
    
    def test_financial_metrics_creation(self):
        """Test creating financial metrics with valid data."""
        metrics = create_test_financial_metrics()
        
        assert metrics.initial_investment == 100000.0
        assert metrics.implementation_cost == 25000.0
        assert len(metrics.expected_revenue) == 4
        assert metrics.risk_level == RiskLevel.MEDIUM
        assert metrics.currency == CurrencyType.USD
        assert metrics.discount_rate == 0.10
    
    def test_financial_metrics_validation(self):
        """Test validation of financial metrics fields."""
        # Valid metrics
        metrics = FinancialMetrics(
            initial_investment=50000.0,
            implementation_cost=10000.0,
            expected_revenue=[20000.0, 25000.0],
            discount_rate=0.08,
            implementation_timeline_months=6.0
        )
        
        assert metrics.initial_investment == 50000.0
        assert metrics.discount_rate == 0.08
        
        # Test validation constraints
        with pytest.raises(ValueError):
            FinancialMetrics(
                initial_investment=-1000.0  # Negative investment
            )
        
        with pytest.raises(ValueError):
            FinancialMetrics(
                implementation_timeline_months=0.05  # Too short
            )
        
        with pytest.raises(ValueError):
            FinancialMetrics(
                implementation_timeline_months=150.0  # Too long
            )
    
    def test_get_total_benefits_per_period(self):
        """Test calculation of total benefits per period."""
        metrics = FinancialMetrics(
            expected_revenue=[10000.0, 15000.0],
            cost_savings=[2000.0, 3000.0],
            productivity_gains=[1000.0, 1500.0]
        )
        
        benefits = metrics.get_total_benefits_per_period()
        
        assert len(benefits) == 2
        assert benefits[0] == 13000.0  # 10000 + 2000 + 1000
        assert benefits[1] == 19500.0  # 15000 + 3000 + 1500
    
    def test_get_total_benefits_uneven_periods(self):
        """Test benefits calculation with uneven period lengths."""
        metrics = FinancialMetrics(
            expected_revenue=[10000.0, 15000.0, 20000.0],
            cost_savings=[2000.0, 3000.0],  # Only 2 periods
            productivity_gains=[1000.0]     # Only 1 period
        )
        
        benefits = metrics.get_total_benefits_per_period()
        
        assert len(benefits) == 3  # Max of all lists
        assert benefits[0] == 13000.0  # 10000 + 2000 + 1000
        assert benefits[1] == 18000.0  # 15000 + 3000 + 0
        assert benefits[2] == 20000.0  # 20000 + 0 + 0
    
    def test_get_total_costs_per_period(self):
        """Test calculation of total costs per period."""
        metrics = FinancialMetrics(
            initial_investment=50000.0,
            implementation_cost=10000.0,
            ongoing_costs=[5000.0, 6000.0, 7000.0]
        )
        
        costs = metrics.get_total_costs_per_period()
        
        assert len(costs) == 4  # Initial + implementation + 3 ongoing
        assert costs[0] == 60000.0  # 50000 + 10000
        assert costs[1] == 5000.0
        assert costs[2] == 6000.0
        assert costs[3] == 7000.0


class TestNPVCalculation:
    """Test cases for NPV calculation results."""
    
    def test_npv_calculation_properties(self):
        """Test NPV calculation derived properties."""
        npv_calc = NPVCalculation(
            npv_value=25000.0,
            discount_rate=0.10,
            initial_investment=100000.0,
            cash_flows=[50000.0, 40000.0, 35000.0],
            present_values=[45454.55, 33057.85, 26296.03],
            time_periods=[1.0, 2.0, 3.0],
            is_profitable=True,
            profitability_index=1.25
        )
        
        # Test total present value
        expected_total_pv = sum(npv_calc.present_values)
        assert abs(npv_calc.total_present_value - expected_total_pv) < 0.01
        
        # Test ROI percentage
        expected_roi = (npv_calc.npv_value / npv_calc.initial_investment) * 100
        assert abs(npv_calc.roi_percentage - expected_roi) < 0.01
        assert abs(npv_calc.roi_percentage - 25.0) < 0.01


class TestCOPQCalculation:
    """Test cases for COPQ calculation results."""
    
    def test_copq_calculation_properties(self):
        """Test COPQ calculation derived properties."""
        copq_calc = COPQCalculation(
            total_copq=50000.0,
            prevention_costs=10000.0,
            appraisal_costs=8000.0,
            internal_failure_costs=20000.0,
            external_failure_costs=12000.0,
            quality_improvement_savings=75000.0
        )
        
        # Test COPQ percentage
        total_costs = (copq_calc.prevention_costs + copq_calc.appraisal_costs + 
                      copq_calc.internal_failure_costs + copq_calc.external_failure_costs)
        expected_percentage = (copq_calc.total_copq / total_costs) * 100
        assert abs(copq_calc.copq_percentage - expected_percentage) < 0.01
        assert abs(copq_calc.copq_percentage - 100.0) < 0.01  # Should be 100% since total_copq equals sum
        
        # Test net savings
        expected_net_savings = copq_calc.quality_improvement_savings - copq_calc.total_copq
        assert copq_calc.net_savings == expected_net_savings
        assert copq_calc.net_savings == 25000.0


class TestROICalculation:
    """Test cases for ROI calculation results."""
    
    def test_roi_calculation_properties(self):
        """Test ROI calculation derived properties."""
        roi_calc = ROICalculation(
            roi_percentage=150.0,
            roi_ratio=1.5,
            investment_amount=100000.0,
            return_amount=250000.0,
            payback_period_years=2.0,
            break_even_point=datetime(2025, 12, 31),
            is_positive_roi=True
        )
        
        # Test annual return rate calculation
        expected_annual_rate = (1 + roi_calc.roi_ratio) ** (1 / roi_calc.payback_period_years) - 1
        assert abs(roi_calc.annual_return_rate - expected_annual_rate) < 0.001
        
        # Should be approximately 58% annual return for 150% return over 2 years
        assert abs(roi_calc.annual_return_rate - 0.581) < 0.01


class TestFinancialCalculator:
    """Test cases for FinancialCalculator main class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = FinancialCalculator()
        self.test_metrics = create_test_financial_metrics()
    
    def test_calculator_initialization(self):
        """Test calculator initialization with custom parameters."""
        custom_risk_factors = {
            RiskLevel.LOW: 0.95,
            RiskLevel.HIGH: 1.15
        }
        
        calculator = FinancialCalculator(
            default_discount_rate=0.12,
            default_currency=CurrencyType.EUR,
            risk_adjustment_factors=custom_risk_factors
        )
        
        assert calculator.default_discount_rate == 0.12
        assert calculator.default_currency == CurrencyType.EUR
        assert calculator.risk_adjustment_factors[RiskLevel.LOW] == 0.95
        assert calculator.risk_adjustment_factors[RiskLevel.HIGH] == 1.15
    
    def test_calculate_npv_basic(self):
        """Test basic NPV calculation."""
        self.setUp()
        
        npv_result = self.calculator.calculate_npv(
            initial_investment=100000.0,
            cash_flows=[50000.0, 40000.0, 35000.0, 30000.0],
            discount_rate=0.10
        )
        
        assert isinstance(npv_result, NPVCalculation)
        assert npv_result.initial_investment == 100000.0
        assert npv_result.discount_rate == 0.10
        assert len(npv_result.cash_flows) == 4
        assert len(npv_result.present_values) == 4
        assert npv_result.is_profitable == (npv_result.npv_value > 0)
        
        # Manually verify first present value
        expected_pv1 = 50000.0 / (1 + 0.10) ** 1
        assert abs(npv_result.present_values[0] - expected_pv1) < 0.01
        assert abs(npv_result.present_values[0] - 45454.55) < 0.01
    
    def test_calculate_npv_validation(self):
        """Test NPV calculation validation."""
        self.setUp()
        
        # Empty cash flows
        with pytest.raises(FinancialValidationError, match="Cash flows cannot be empty"):
            self.calculator.calculate_npv(
                initial_investment=100000.0,
                cash_flows=[]
            )
        
        # Mismatched cash flows and time periods
        with pytest.raises(FinancialValidationError, match="Cash flows and time periods must have same length"):
            self.calculator.calculate_npv(
                initial_investment=100000.0,
                cash_flows=[10000.0, 20000.0],
                time_periods=[1.0, 2.0, 3.0]  # Different length
            )
    
    def test_calculate_copq(self):
        """Test COPQ calculation."""
        self.setUp()
        
        copq_result = self.calculator.calculate_copq(
            prevention_costs=10000.0,
            appraisal_costs=8000.0,
            internal_failure_costs=15000.0,
            external_failure_costs=12000.0,
            quality_improvement_savings=60000.0
        )
        
        assert isinstance(copq_result, COPQCalculation)
        assert copq_result.total_copq == 45000.0  # Sum of all cost components
        assert copq_result.quality_improvement_savings == 60000.0
        assert copq_result.net_savings == 15000.0  # 60000 - 45000
    
    def test_calculate_copq_validation(self):
        """Test COPQ calculation validation."""
        self.setUp()
        
        with pytest.raises(FinancialValidationError, match="Cost values cannot be negative"):
            self.calculator.calculate_copq(
                prevention_costs=-1000.0,  # Negative cost
                appraisal_costs=5000.0,
                internal_failure_costs=10000.0,
                external_failure_costs=8000.0
            )
    
    def test_calculate_roi(self):
        """Test ROI calculation."""
        self.setUp()
        
        roi_result = self.calculator.calculate_roi(
            investment_amount=100000.0,
            return_amount=180000.0,
            time_period_years=2.0
        )
        
        assert isinstance(roi_result, ROICalculation)
        assert roi_result.investment_amount == 100000.0
        assert roi_result.return_amount == 180000.0
        assert roi_result.roi_percentage == 80.0  # (180000 - 100000) / 100000 * 100
        assert roi_result.roi_ratio == 0.8
        assert roi_result.is_positive_roi is True
        
        # Test payback period calculation
        expected_payback = 100000.0 / (180000.0 / 2.0)  # Investment / annual return
        assert abs(roi_result.payback_period_years - expected_payback) < 0.01
        assert abs(roi_result.payback_period_years - 1.11) < 0.01
    
    def test_calculate_roi_validation(self):
        """Test ROI calculation validation."""
        self.setUp()
        
        with pytest.raises(FinancialValidationError, match="Investment amount must be positive"):
            self.calculator.calculate_roi(
                investment_amount=0.0,  # Zero investment
                return_amount=50000.0
            )
        
        with pytest.raises(FinancialValidationError, match="Time period must be positive"):
            self.calculator.calculate_roi(
                investment_amount=100000.0,
                return_amount=150000.0,
                time_period_years=0.0  # Zero time period
            )
    
    def test_calculate_cost_of_delay(self):
        """Test cost of delay calculation."""
        self.setUp()
        
        # Basic cost of delay
        cost = self.calculator.calculate_cost_of_delay(
            revenue_per_period=10000.0,
            delay_periods=3.0
        )
        assert cost == 30000.0  # 10000 * 3
        
        # With escalation factor
        escalated_cost = self.calculator.calculate_cost_of_delay(
            revenue_per_period=10000.0,
            delay_periods=2.0,
            cost_escalation_factor=1.1
        )
        expected = 10000.0 * 2.0 * (1.1 ** 2.0)  # 20000 * 1.21
        assert abs(escalated_cost - expected) < 0.01
        assert abs(escalated_cost - 24200.0) < 1.0
    
    def test_calculate_risk_adjusted_value(self):
        """Test risk adjustment calculations."""
        self.setUp()
        
        base_value = 100000.0
        
        # Low risk should discount value
        low_risk_value = self.calculator.calculate_risk_adjusted_value(
            base_value, RiskLevel.LOW, confidence_factor=1.0
        )
        assert low_risk_value == base_value * 0.98  # Default low risk factor
        
        # High risk should add premium
        high_risk_value = self.calculator.calculate_risk_adjusted_value(
            base_value, RiskLevel.HIGH, confidence_factor=1.0
        )
        assert high_risk_value == base_value * 1.1  # Default high risk factor
        
        # Test confidence factor
        low_confidence_value = self.calculator.calculate_risk_adjusted_value(
            base_value, RiskLevel.MEDIUM, confidence_factor=0.8
        )
        assert low_confidence_value == base_value * 1.0 * 0.8
    
    def test_calculate_comprehensive_financial_metrics(self):
        """Test comprehensive financial metrics calculation."""
        self.setUp()
        
        # Test with complete financial data
        result_metrics = self.calculator.calculate_comprehensive_financial_metrics(
            self.test_metrics
        )
        
        assert isinstance(result_metrics, FinancialMetrics)
        assert result_metrics.npv_result is not None
        assert result_metrics.roi_result is not None
        assert result_metrics.total_financial_score > 0
        assert 0 <= result_metrics.confidence_level <= 1
        
        # Verify NPV was calculated
        assert isinstance(result_metrics.npv_result, NPVCalculation)
        assert result_metrics.npv_result.initial_investment == self.test_metrics.initial_investment
        
        # Verify ROI was calculated
        assert isinstance(result_metrics.roi_result, ROICalculation)
        assert result_metrics.roi_result.investment_amount > 0
    
    def test_comprehensive_metrics_with_quality_factors(self):
        """Test comprehensive metrics with quality improvement factors."""
        self.setUp()
        
        # Modify test metrics to include quality improvements
        self.test_metrics.quality_improvement_factor = 1.5
        
        result_metrics = self.calculator.calculate_comprehensive_financial_metrics(
            self.test_metrics
        )
        
        # Should include COPQ calculation
        assert result_metrics.copq_result is not None
        assert isinstance(result_metrics.copq_result, COPQCalculation)
    
    def test_perform_sensitivity_analysis(self):
        """Test sensitivity analysis functionality."""
        self.setUp()
        
        parameter_variations = {
            'discount_rate': [0.08, 0.10, 0.12, 0.15],
            'initial_investment': [80000.0, 100000.0, 120000.0],
            'implementation_timeline_months': [9.0, 12.0, 15.0]
        }
        
        results = self.calculator.perform_sensitivity_analysis(
            self.test_metrics,
            parameter_variations,
            include_monte_carlo=False
        )
        
        assert 'base_metrics' in results
        assert 'sensitivity_results' in results
        assert 'monte_carlo_results' in results
        
        # Check sensitivity results structure
        assert len(results['sensitivity_results']) == 3  # Three parameters
        
        for param_name in parameter_variations.keys():
            assert param_name in results['sensitivity_results']
            param_results = results['sensitivity_results'][param_name]
            expected_count = len(parameter_variations[param_name])
            assert len(param_results) == expected_count
            
            # Check each variation result
            for variation_result in param_results:
                assert 'variation_value' in variation_result
                assert 'financial_score' in variation_result
                assert 'npv' in variation_result
                assert 'roi' in variation_result
    
    @patch('numpy.random.normal')
    def test_monte_carlo_simulation(self, mock_random):
        """Test Monte Carlo simulation."""
        self.setUp()
        
        # Mock random number generation for predictable results
        mock_random.side_effect = [1.1, 0.9, 1.0, 1.2, 0.8, 1.1]  # Cycle through values
        
        parameter_variations = {'discount_rate': [0.08, 0.12]}
        
        results = self.calculator.perform_sensitivity_analysis(
            self.test_metrics,
            parameter_variations,
            include_monte_carlo=True,
            num_simulations=10
        )
        
        assert results['monte_carlo_results'] is not None
        monte_carlo = results['monte_carlo_results']
        
        assert 'statistics' in monte_carlo
        assert 'raw_results' in monte_carlo
        assert 'num_successful_simulations' in monte_carlo
        
        # Check statistics structure
        stats = monte_carlo['statistics']
        for key in ['financial_scores', 'npv_values', 'roi_percentages']:
            if key in stats:
                assert 'mean' in stats[key]
                assert 'std' in stats[key]
                assert 'percentiles' in stats[key]


class TestUtilityFunctions:
    """Test utility functions for common financial calculations."""
    
    def test_quick_npv(self):
        """Test quick NPV calculation utility."""
        npv = quick_npv(
            investment=100000.0,
            annual_benefits=30000.0,
            years=5,
            discount_rate=0.10
        )
        
        # Manually calculate expected NPV
        # PV = 30000 * [(1 - (1.1)^-5) / 0.1] = 30000 * 3.7908 = 113,724
        # NPV = 113,724 - 100,000 = 13,724
        assert abs(npv - 13723.60) < 10.0  # Allow small rounding differences
        assert npv > 0  # Should be profitable
    
    def test_quick_roi(self):
        """Test quick ROI calculation utility."""
        roi = quick_roi(investment=50000.0, returns=75000.0)
        assert roi == 50.0  # (75000 - 50000) / 50000 * 100
        
        # Test with loss
        roi_loss = quick_roi(investment=50000.0, returns=40000.0)
        assert roi_loss == -20.0  # (40000 - 50000) / 50000 * 100
        
        # Test with zero investment
        roi_zero = quick_roi(investment=0.0, returns=10000.0)
        assert roi_zero == 0.0
    
    def test_payback_period(self):
        """Test payback period calculation utility."""
        payback = payback_period(investment=100000.0, annual_cash_flow=25000.0)
        assert payback == 4.0  # 100000 / 25000
        
        # Test with zero cash flow
        payback_zero = payback_period(investment=100000.0, annual_cash_flow=0.0)
        assert payback_zero == float('inf')
        
        # Test with negative cash flow
        payback_neg = payback_period(investment=100000.0, annual_cash_flow=-5000.0)
        assert payback_neg == float('inf')


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = FinancialCalculator()
    
    def test_financial_validation_errors(self):
        """Test various financial validation errors."""
        self.setUp()
        
        # Test comprehensive metrics with invalid data
        invalid_metrics = FinancialMetrics(
            initial_investment=0.0,  # Zero investment
            expected_revenue=[]
        )
        
        # Should handle gracefully and return low scores
        result = self.calculator.calculate_comprehensive_financial_metrics(invalid_metrics)
        assert result.total_financial_score >= 0
        assert result.confidence_level < 1.0
    
    def test_edge_case_calculations(self):
        """Test edge cases in calculations."""
        self.setUp()
        
        # NPV with very small cash flows
        npv_result = self.calculator.calculate_npv(
            initial_investment=1.0,
            cash_flows=[0.1, 0.2, 0.3]
        )
        assert npv_result.npv_value < 0  # Should be negative (not profitable)
        
        # ROI with very large returns
        roi_result = self.calculator.calculate_roi(
            investment_amount=1000.0,
            return_amount=1000000.0
        )
        assert roi_result.roi_percentage > 99000  # Should be very high ROI
        assert roi_result.is_positive_roi is True
    
    def test_currency_and_risk_combinations(self):
        """Test various currency and risk level combinations."""
        self.setUp()
        
        # Test all risk levels
        base_value = 50000.0
        
        for risk_level in RiskLevel:
            adjusted_value = self.calculator.calculate_risk_adjusted_value(
                base_value, risk_level, confidence_factor=0.9
            )
            assert adjusted_value > 0  # Should always be positive
            assert isinstance(adjusted_value, float)
        
        # Test all currency types in metrics
        for currency in CurrencyType:
            metrics = FinancialMetrics(
                initial_investment=10000.0,
                expected_revenue=[5000.0, 6000.0],
                currency=currency
            )
            assert metrics.currency == currency
    
    def test_confidence_assessment_edge_cases(self):
        """Test confidence assessment with various data completeness scenarios."""
        self.setUp()
        
        # Minimal data
        minimal_metrics = FinancialMetrics()
        result = self.calculator.calculate_comprehensive_financial_metrics(minimal_metrics)
        assert result.confidence_level < 0.5  # Should be low confidence
        
        # Complete data
        complete_metrics = create_test_financial_metrics()
        complete_metrics.risk_level = RiskLevel.VERY_LOW  # High confidence risk level
        result = self.calculator.calculate_comprehensive_financial_metrics(complete_metrics)
        assert result.confidence_level > 0.7  # Should be high confidence