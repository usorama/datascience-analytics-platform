"""QVF Financial Metrics Calculator

This module implements financial modeling capabilities for the QVF system,
including NPV (Net Present Value), COPQ (Cost of Poor Quality), ROI
(Return on Investment), and other financial impact calculations.

The financial calculator integrates with QVF criteria to provide
monetary valuations that enhance prioritization decisions with
quantifiable business impact metrics.

Key Features:
- NPV calculations with configurable discount rates
- Cost of Poor Quality (COPQ) modeling
- ROI and payback period analysis
- Cost of delay calculations
- Risk-adjusted financial projections
- Time-value of money considerations
- Sensitivity analysis for financial assumptions

Usage:
    from datascience_platform.qvf.core.financial import FinancialCalculator
    
    calculator = FinancialCalculator(discount_rate=0.10)
    
    # Calculate NPV for a work item
    npv = calculator.calculate_npv(
        initial_investment=50000,
        cash_flows=[10000, 15000, 20000, 25000],
        time_periods=[1, 2, 3, 4]
    )
    
    # Calculate cost of delay
    delay_cost = calculator.calculate_cost_of_delay(
        revenue_per_week=10000,
        delay_weeks=4
    )

Integration:
    The financial calculator works seamlessly with QVF criteria that
    have financial_multiplier or cost_of_delay parameters. Results
    are automatically incorporated into the overall QVF scoring.
"""

import logging
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Union
from pydantic import BaseModel, Field, field_validator
import numpy as np
from dataclasses import dataclass
from enum import Enum

from ...core.exceptions import DataSciencePlatformError

logger = logging.getLogger(__name__)


class FinancialValidationError(DataSciencePlatformError):
    """Exception raised for financial calculation validation errors."""
    pass


class CurrencyType(str, Enum):
    """Supported currency types for financial calculations."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"


class RiskLevel(str, Enum):
    """Risk levels for risk-adjusted calculations."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class NPVCalculation:
    """Result of Net Present Value calculation."""
    npv_value: float
    discount_rate: float
    initial_investment: float
    cash_flows: List[float]
    present_values: List[float]
    time_periods: List[float]
    is_profitable: bool
    profitability_index: float
    
    @property
    def total_present_value(self) -> float:
        """Total present value of cash flows."""
        return sum(self.present_values)
    
    @property
    def roi_percentage(self) -> float:
        """Return on investment as percentage."""
        if self.initial_investment == 0:
            return 0.0
        return (self.npv_value / self.initial_investment) * 100


@dataclass 
class COPQCalculation:
    """Result of Cost of Poor Quality calculation."""
    total_copq: float
    prevention_costs: float
    appraisal_costs: float
    internal_failure_costs: float
    external_failure_costs: float
    quality_improvement_savings: float
    
    @property
    def copq_percentage(self) -> float:
        """COPQ as percentage of total costs."""
        total_costs = (self.prevention_costs + self.appraisal_costs + 
                      self.internal_failure_costs + self.external_failure_costs)
        if total_costs == 0:
            return 0.0
        return (self.total_copq / total_costs) * 100
    
    @property
    def net_savings(self) -> float:
        """Net savings from quality improvements."""
        return self.quality_improvement_savings - self.total_copq


@dataclass
class ROICalculation:
    """Result of Return on Investment calculation."""
    roi_percentage: float
    roi_ratio: float
    investment_amount: float
    return_amount: float
    payback_period_years: float
    break_even_point: Optional[datetime]
    is_positive_roi: bool
    
    @property
    def annual_return_rate(self) -> float:
        """Annualized return rate."""
        if self.payback_period_years <= 0:
            return 0.0
        return (1 + self.roi_ratio) ** (1 / self.payback_period_years) - 1


class FinancialMetrics(BaseModel):
    """Comprehensive financial metrics for a work item.
    
    Encapsulates all financial calculations and projections
    for a work item to support QVF prioritization decisions.
    """
    
    # Basic financial data
    initial_investment: float = Field(0.0, ge=0, description="Initial investment required")
    implementation_cost: float = Field(0.0, ge=0, description="Implementation cost")
    ongoing_costs: List[float] = Field(default_factory=list, description="Ongoing costs per period")
    
    # Revenue and benefits
    expected_revenue: List[float] = Field(default_factory=list, description="Expected revenue per period")
    cost_savings: List[float] = Field(default_factory=list, description="Cost savings per period")
    productivity_gains: List[float] = Field(default_factory=list, description="Productivity gains per period")
    
    # Risk and timing
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Risk level for adjustments")
    implementation_timeline_months: float = Field(1.0, ge=0.1, le=120, description="Implementation timeline")
    benefit_realization_delay_months: float = Field(0.0, ge=0, le=60, description="Delay before benefits start")
    
    # Market and competitive factors
    cost_of_delay_per_month: float = Field(0.0, ge=0, description="Cost of delay per month")
    competitive_advantage_value: float = Field(0.0, description="Value of competitive advantage")
    market_opportunity_size: float = Field(0.0, ge=0, description="Total market opportunity")
    
    # Quality and operational factors
    quality_improvement_factor: float = Field(1.0, ge=0.1, le=10, description="Quality improvement multiplier")
    operational_efficiency_gain: float = Field(0.0, ge=0, le=1, description="Operational efficiency gain (0-1)")
    customer_satisfaction_impact: float = Field(0.0, ge=-1, le=1, description="Customer satisfaction impact (-1 to 1)")
    
    # Financial parameters
    discount_rate: float = Field(0.10, ge=0, le=1, description="Discount rate for NPV calculations")
    currency: CurrencyType = Field(CurrencyType.USD, description="Currency for calculations")
    inflation_rate: float = Field(0.03, ge=0, le=0.20, description="Annual inflation rate")
    
    # Calculated metrics (populated by FinancialCalculator)
    npv_result: Optional[NPVCalculation] = Field(None, description="NPV calculation result")
    copq_result: Optional[COPQCalculation] = Field(None, description="COPQ calculation result")
    roi_result: Optional[ROICalculation] = Field(None, description="ROI calculation result")
    
    total_financial_score: float = Field(0.0, description="Combined financial score")
    confidence_level: float = Field(0.5, ge=0, le=1, description="Confidence in financial projections")
    
    @field_validator('ongoing_costs', 'expected_revenue', 'cost_savings', 'productivity_gains')
    @classmethod
    def validate_cash_flow_lists(cls, v):
        """Ensure cash flow lists have positive values where appropriate."""
        if v and any(x < 0 for x in v if isinstance(x, (int, float))):
            logger.warning("Negative values found in cash flow list")
        return v
    
    def get_total_benefits_per_period(self) -> List[float]:
        """Calculate total benefits per period."""
        max_periods = max(
            len(self.expected_revenue),
            len(self.cost_savings),
            len(self.productivity_gains),
            1
        )
        
        total_benefits = []
        for i in range(max_periods):
            benefit = 0.0
            if i < len(self.expected_revenue):
                benefit += self.expected_revenue[i]
            if i < len(self.cost_savings):
                benefit += self.cost_savings[i]
            if i < len(self.productivity_gains):
                benefit += self.productivity_gains[i]
            total_benefits.append(benefit)
        
        return total_benefits
    
    def get_total_costs_per_period(self) -> List[float]:
        """Calculate total costs per period."""
        costs = [self.initial_investment + self.implementation_cost]
        costs.extend(self.ongoing_costs)
        return costs


class FinancialCalculator:
    """Main financial calculator for QVF financial modeling.
    
    Provides comprehensive financial analysis capabilities including
    NPV, COPQ, ROI calculations, and integration with QVF criteria.
    
    The calculator uses industry-standard financial formulas and
    supports various risk adjustments and sensitivity analysis.
    """
    
    def __init__(
        self,
        default_discount_rate: float = 0.10,
        default_currency: CurrencyType = CurrencyType.USD,
        risk_adjustment_factors: Optional[Dict[RiskLevel, float]] = None
    ):
        """Initialize financial calculator.
        
        Args:
            default_discount_rate: Default discount rate for NPV calculations
            default_currency: Default currency for calculations
            risk_adjustment_factors: Risk adjustment factors by risk level
        """
        self.default_discount_rate = default_discount_rate
        self.default_currency = default_currency
        
        # Default risk adjustment factors
        self.risk_adjustment_factors = risk_adjustment_factors or {
            RiskLevel.VERY_LOW: 0.95,   # 5% discount for very low risk
            RiskLevel.LOW: 0.98,        # 2% discount for low risk
            RiskLevel.MEDIUM: 1.0,      # No adjustment for medium risk
            RiskLevel.HIGH: 1.1,        # 10% premium for high risk
            RiskLevel.VERY_HIGH: 1.25   # 25% premium for very high risk
        }
        
        logger.info(f"Financial calculator initialized with discount rate {default_discount_rate}")
    
    def calculate_npv(
        self,
        initial_investment: float,
        cash_flows: List[float],
        time_periods: Optional[List[float]] = None,
        discount_rate: Optional[float] = None
    ) -> NPVCalculation:
        """Calculate Net Present Value.
        
        Args:
            initial_investment: Initial investment amount
            cash_flows: List of cash flows per period
            time_periods: List of time periods (defaults to 1, 2, 3, ...)
            discount_rate: Discount rate (uses default if None)
            
        Returns:
            NPV calculation result
        """
        if not cash_flows:
            raise FinancialValidationError("Cash flows cannot be empty")
        
        discount_rate = discount_rate or self.default_discount_rate
        time_periods = time_periods or list(range(1, len(cash_flows) + 1))
        
        if len(cash_flows) != len(time_periods):
            raise FinancialValidationError("Cash flows and time periods must have same length")
        
        # Calculate present values
        present_values = []
        for cash_flow, period in zip(cash_flows, time_periods):
            pv = cash_flow / ((1 + discount_rate) ** period)
            present_values.append(pv)
        
        # Calculate NPV
        npv_value = sum(present_values) - initial_investment
        
        # Calculate profitability index
        total_pv = sum(present_values)
        profitability_index = total_pv / initial_investment if initial_investment > 0 else 0
        
        logger.debug(f"NPV calculation: NPV={npv_value:.2f}, PI={profitability_index:.2f}")
        
        return NPVCalculation(
            npv_value=npv_value,
            discount_rate=discount_rate,
            initial_investment=initial_investment,
            cash_flows=cash_flows,
            present_values=present_values,
            time_periods=time_periods,
            is_profitable=npv_value > 0,
            profitability_index=profitability_index
        )
    
    def calculate_copq(
        self,
        prevention_costs: float,
        appraisal_costs: float,
        internal_failure_costs: float,
        external_failure_costs: float,
        quality_improvement_savings: float = 0.0
    ) -> COPQCalculation:
        """Calculate Cost of Poor Quality.
        
        Args:
            prevention_costs: Costs of preventing defects
            appraisal_costs: Costs of detecting defects
            internal_failure_costs: Costs of internal failures
            external_failure_costs: Costs of external failures
            quality_improvement_savings: Expected savings from quality improvements
            
        Returns:
            COPQ calculation result
        """
        if any(cost < 0 for cost in [prevention_costs, appraisal_costs, 
                                    internal_failure_costs, external_failure_costs]):
            raise FinancialValidationError("Cost values cannot be negative")
        
        total_copq = (prevention_costs + appraisal_costs + 
                     internal_failure_costs + external_failure_costs)
        
        logger.debug(f"COPQ calculation: Total COPQ={total_copq:.2f}")
        
        return COPQCalculation(
            total_copq=total_copq,
            prevention_costs=prevention_costs,
            appraisal_costs=appraisal_costs,
            internal_failure_costs=internal_failure_costs,
            external_failure_costs=external_failure_costs,
            quality_improvement_savings=quality_improvement_savings
        )
    
    def calculate_roi(
        self,
        investment_amount: float,
        return_amount: float,
        time_period_years: float = 1.0
    ) -> ROICalculation:
        """Calculate Return on Investment.
        
        Args:
            investment_amount: Initial investment
            return_amount: Total return
            time_period_years: Time period in years
            
        Returns:
            ROI calculation result
        """
        if investment_amount <= 0:
            raise FinancialValidationError("Investment amount must be positive")
        
        if time_period_years <= 0:
            raise FinancialValidationError("Time period must be positive")
        
        # Calculate ROI
        roi_ratio = (return_amount - investment_amount) / investment_amount
        roi_percentage = roi_ratio * 100
        
        # Calculate payback period
        if return_amount > investment_amount:
            payback_period_years = investment_amount / (return_amount / time_period_years)
        else:
            payback_period_years = float('inf')
        
        # Estimate break-even point
        break_even_point = None
        if return_amount > investment_amount:
            days_to_breakeven = payback_period_years * 365
            break_even_point = datetime.now() + timedelta(days=days_to_breakeven)
        
        logger.debug(f"ROI calculation: ROI={roi_percentage:.2f}%, Payback={payback_period_years:.2f} years")
        
        return ROICalculation(
            roi_percentage=roi_percentage,
            roi_ratio=roi_ratio,
            investment_amount=investment_amount,
            return_amount=return_amount,
            payback_period_years=payback_period_years,
            break_even_point=break_even_point,
            is_positive_roi=roi_ratio > 0
        )
    
    def calculate_cost_of_delay(
        self,
        revenue_per_period: float,
        delay_periods: float,
        cost_escalation_factor: float = 1.0
    ) -> float:
        """Calculate cost of delaying a work item.
        
        Args:
            revenue_per_period: Revenue per time period
            delay_periods: Number of periods delayed
            cost_escalation_factor: Factor for escalating costs over time
            
        Returns:
            Total cost of delay
        """
        if revenue_per_period < 0 or delay_periods < 0:
            raise FinancialValidationError("Revenue and delay periods must be non-negative")
        
        # Calculate base cost of delay
        base_cost = revenue_per_period * delay_periods
        
        # Apply escalation factor for longer delays
        escalated_cost = base_cost * (cost_escalation_factor ** delay_periods)
        
        logger.debug(f"Cost of delay calculation: Base={base_cost:.2f}, Escalated={escalated_cost:.2f}")
        return escalated_cost
    
    def calculate_risk_adjusted_value(
        self,
        base_value: float,
        risk_level: RiskLevel,
        confidence_factor: float = 1.0
    ) -> float:
        """Apply risk adjustments to financial values.
        
        Args:
            base_value: Base financial value
            risk_level: Risk level for adjustment
            confidence_factor: Additional confidence adjustment (0-1)
            
        Returns:
            Risk-adjusted value
        """
        risk_factor = self.risk_adjustment_factors.get(risk_level, 1.0)
        adjusted_value = base_value * risk_factor * confidence_factor
        
        logger.debug(f"Risk adjustment: Base={base_value:.2f}, Risk={risk_factor}, Adjusted={adjusted_value:.2f}")
        return adjusted_value
    
    def calculate_comprehensive_financial_metrics(
        self,
        financial_data: FinancialMetrics
    ) -> FinancialMetrics:
        """Calculate comprehensive financial metrics for a work item.
        
        Args:
            financial_data: Input financial data
            
        Returns:
            Enhanced financial metrics with calculations
        """
        logger.info(f"Calculating comprehensive financial metrics")
        
        # Create a copy to avoid modifying the original
        metrics = FinancialMetrics(**financial_data.model_dump())
        
        try:
            # Calculate NPV
            cash_flows = metrics.get_total_benefits_per_period()
            if cash_flows and metrics.initial_investment > 0:
                metrics.npv_result = self.calculate_npv(
                    initial_investment=metrics.initial_investment,
                    cash_flows=cash_flows,
                    discount_rate=metrics.discount_rate
                )
            
            # Calculate ROI if we have sufficient data
            total_benefits = sum(cash_flows) if cash_flows else 0
            total_investment = metrics.initial_investment + metrics.implementation_cost
            
            if total_investment > 0 and total_benefits > 0:
                metrics.roi_result = self.calculate_roi(
                    investment_amount=total_investment,
                    return_amount=total_benefits,
                    time_period_years=metrics.implementation_timeline_months / 12
                )
            
            # Calculate COPQ if quality factors are present
            if metrics.quality_improvement_factor > 1.0:
                # Estimate COPQ based on quality improvement potential
                quality_savings = total_benefits * (metrics.quality_improvement_factor - 1.0)
                prevention_costs = total_investment * 0.1  # Assume 10% prevention
                internal_failures = total_benefits * 0.05   # Assume 5% failure cost
                
                metrics.copq_result = self.calculate_copq(
                    prevention_costs=prevention_costs,
                    appraisal_costs=total_investment * 0.05,
                    internal_failure_costs=internal_failures,
                    external_failure_costs=internal_failures * 0.5,
                    quality_improvement_savings=quality_savings
                )
            
            # Calculate combined financial score
            metrics.total_financial_score = self._calculate_combined_score(metrics)
            
            # Assess confidence based on data completeness
            metrics.confidence_level = self._assess_confidence(metrics)
            
            logger.info(f"Financial metrics calculated. Total score: {metrics.total_financial_score:.3f}")
            
        except Exception as e:
            logger.error(f"Error calculating financial metrics: {e}")
            raise FinancialValidationError(f"Financial calculation failed: {str(e)}")
        
        return metrics
    
    def _calculate_combined_score(self, metrics: FinancialMetrics) -> float:
        """Calculate combined financial score from all metrics.
        
        Args:
            metrics: Financial metrics with calculations
            
        Returns:
            Combined financial score (0-1)
        """
        score_components = []
        weights = []
        
        # NPV component
        if metrics.npv_result:
            npv_score = min(1.0, max(0.0, metrics.npv_result.npv_value / 100000))  # Normalize to 100k
            score_components.append(npv_score)
            weights.append(0.4)  # 40% weight
        
        # ROI component
        if metrics.roi_result:
            roi_score = min(1.0, max(0.0, metrics.roi_result.roi_ratio / 2.0))  # Normalize to 200% ROI
            score_components.append(roi_score)
            weights.append(0.3)  # 30% weight
        
        # COPQ component
        if metrics.copq_result and metrics.copq_result.net_savings > 0:
            copq_score = min(1.0, max(0.0, metrics.copq_result.net_savings / 50000))  # Normalize to 50k
            score_components.append(copq_score)
            weights.append(0.2)  # 20% weight
        
        # Cost of delay component
        if metrics.cost_of_delay_per_month > 0:
            delay_score = min(1.0, metrics.cost_of_delay_per_month / 10000)  # Normalize to 10k/month
            score_components.append(delay_score)
            weights.append(0.1)  # 10% weight
        
        # Calculate weighted average
        if score_components and weights:
            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(score_components, weights)) / total_weight
            
            # Apply risk adjustment
            risk_adjusted_score = self.calculate_risk_adjusted_value(
                weighted_score, metrics.risk_level, metrics.confidence_level
            )
            
            return min(1.0, max(0.0, risk_adjusted_score))
        
        return 0.0
    
    def _assess_confidence(self, metrics: FinancialMetrics) -> float:
        """Assess confidence level based on data completeness.
        
        Args:
            metrics: Financial metrics to assess
            
        Returns:
            Confidence level (0-1)
        """
        confidence_factors = []
        
        # Data completeness factors
        if metrics.initial_investment > 0:
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.3)
        
        if metrics.expected_revenue:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.4)
        
        if len(metrics.expected_revenue) >= 3:  # Multi-period projections
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.5)
        
        # Risk level factor
        risk_confidence = {
            RiskLevel.VERY_LOW: 0.9,
            RiskLevel.LOW: 0.8,
            RiskLevel.MEDIUM: 0.7,
            RiskLevel.HIGH: 0.5,
            RiskLevel.VERY_HIGH: 0.3
        }
        confidence_factors.append(risk_confidence[metrics.risk_level])
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def perform_sensitivity_analysis(
        self,
        base_metrics: FinancialMetrics,
        parameter_variations: Dict[str, List[float]],
        include_monte_carlo: bool = False,
        num_simulations: int = 1000
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on financial metrics.
        
        Args:
            base_metrics: Base financial metrics
            parameter_variations: Parameter variations to test
            include_monte_carlo: Whether to include Monte Carlo simulation
            num_simulations: Number of Monte Carlo simulations
            
        Returns:
            Sensitivity analysis results
        """
        logger.info(f"Performing sensitivity analysis with {len(parameter_variations)} parameters")
        
        results = {
            'base_metrics': self.calculate_comprehensive_financial_metrics(base_metrics),
            'sensitivity_results': {},
            'monte_carlo_results': None
        }
        
        # Parameter sensitivity analysis
        for param_name, variations in parameter_variations.items():
            param_results = []
            
            for variation in variations:
                # Create modified metrics
                modified_metrics = FinancialMetrics(**base_metrics.model_dump())
                
                # Apply variation
                if hasattr(modified_metrics, param_name):
                    setattr(modified_metrics, param_name, variation)
                
                # Calculate metrics
                calculated_metrics = self.calculate_comprehensive_financial_metrics(modified_metrics)
                
                param_results.append({
                    'variation_value': variation,
                    'financial_score': calculated_metrics.total_financial_score,
                    'npv': calculated_metrics.npv_result.npv_value if calculated_metrics.npv_result else 0,
                    'roi': calculated_metrics.roi_result.roi_percentage if calculated_metrics.roi_result else 0
                })
            
            results['sensitivity_results'][param_name] = param_results
        
        # Monte Carlo simulation
        if include_monte_carlo:
            results['monte_carlo_results'] = self._run_monte_carlo_simulation(
                base_metrics, num_simulations
            )
        
        logger.info("Sensitivity analysis completed")
        return results
    
    def _run_monte_carlo_simulation(
        self,
        base_metrics: FinancialMetrics,
        num_simulations: int
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation for financial projections.
        
        Args:
            base_metrics: Base financial metrics
            num_simulations: Number of simulations to run
            
        Returns:
            Monte Carlo simulation results
        """
        logger.info(f"Running Monte Carlo simulation with {num_simulations} iterations")
        
        simulation_results = {
            'financial_scores': [],
            'npv_values': [],
            'roi_percentages': []
        }
        
        for _ in range(num_simulations):
            # Create variation of base metrics with random factors
            varied_metrics = FinancialMetrics(**base_metrics.model_dump())
            
            # Apply random variations with improved distributions
            revenue_factor = np.random.lognormal(0, 0.2)  # Log-normal for revenue (always positive)
            cost_factor = np.random.normal(1.0, 0.15)
            timing_factor = np.random.gamma(2, 0.5)  # Gamma for timing (positive skew)
            risk_factor = np.random.beta(2, 5)  # Beta for risk factors
            
            # Apply variations with bounds
            varied_metrics.expected_revenue = [
                r * max(0.1, min(3.0, revenue_factor)) for r in varied_metrics.expected_revenue
            ]
            varied_metrics.initial_investment *= max(0.5, min(2.0, cost_factor))
            varied_metrics.implementation_timeline_months *= max(0.5, min(3.0, timing_factor))
            
            # Apply risk variation
            if np.random.random() < 0.3:  # 30% chance of risk level change
                risk_levels = list(RiskLevel)
                varied_metrics.risk_level = np.random.choice(risk_levels)
            
            # Calculate metrics for this variation
            try:
                calculated_metrics = self.calculate_comprehensive_financial_metrics(varied_metrics)
                qvf_scores = self.calculate_financial_score_for_qvf(varied_metrics)
                
                simulation_results['financial_scores'].append(calculated_metrics.total_financial_score)
                simulation_results['qvf_scores'].append(qvf_scores['combined_financial_score'])
                
                if calculated_metrics.npv_result:
                    simulation_results['npv_values'].append(calculated_metrics.npv_result.npv_value)
                
                if calculated_metrics.roi_result:
                    simulation_results['roi_percentages'].append(calculated_metrics.roi_result.roi_percentage)
                    
            except Exception as e:
                logger.debug(f"Monte Carlo iteration failed: {e}")
                continue
        
        # Calculate statistics
        stats = {}
        for key, values in simulation_results.items():
            if values:
                stats[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'percentiles': {
                        '5th': np.percentile(values, 5),
                        '25th': np.percentile(values, 25),
                        '50th': np.percentile(values, 50),
                        '75th': np.percentile(values, 75),
                        '95th': np.percentile(values, 95)
                    }
                }
        
        # Calculate enhanced statistics
        stats = {}
        for key, values in simulation_results.items():
            if values:
                values_array = np.array(values)
                stats[key] = {
                    'mean': np.mean(values_array),
                    'std': np.std(values_array),
                    'min': np.min(values_array),
                    'max': np.max(values_array),
                    'skewness': float(np.mean(((values_array - np.mean(values_array)) / np.std(values_array)) ** 3)) if np.std(values_array) > 0 else 0,
                    'kurtosis': float(np.mean(((values_array - np.mean(values_array)) / np.std(values_array)) ** 4)) - 3 if np.std(values_array) > 0 else 0,
                    'percentiles': {
                        '1st': np.percentile(values_array, 1),
                        '5th': np.percentile(values_array, 5),
                        '10th': np.percentile(values_array, 10),
                        '25th': np.percentile(values_array, 25),
                        '50th': np.percentile(values_array, 50),
                        '75th': np.percentile(values_array, 75),
                        '90th': np.percentile(values_array, 90),
                        '95th': np.percentile(values_array, 95),
                        '99th': np.percentile(values_array, 99)
                    },
                    'confidence_intervals': {
                        '90%': (np.percentile(values_array, 5), np.percentile(values_array, 95)),
                        '95%': (np.percentile(values_array, 2.5), np.percentile(values_array, 97.5)),
                        '99%': (np.percentile(values_array, 0.5), np.percentile(values_array, 99.5))
                    }
                }
        
        return {
            'statistics': stats,
            'raw_results': simulation_results,
            'num_successful_simulations': len(simulation_results['financial_scores']),
            'simulation_quality': {
                'success_rate': len(simulation_results['financial_scores']) / num_simulations,
                'convergence_indicator': np.std(simulation_results['financial_scores'][-100:]) if len(simulation_results['financial_scores']) >= 100 else None
            }
        }
    
    def calculate_portfolio_financial_metrics(
        self,
        work_items_metrics: List[FinancialMetrics],
        portfolio_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate portfolio-level financial metrics.
        
        Args:
            work_items_metrics: List of financial metrics for work items
            portfolio_constraints: Optional portfolio constraints
            
        Returns:
            Portfolio financial analysis
        """
        logger.info(f"Calculating portfolio metrics for {len(work_items_metrics)} work items")
        
        # Calculate individual metrics
        enhanced_metrics = []
        for metrics in work_items_metrics:
            enhanced = self.calculate_comprehensive_financial_metrics(metrics)
            enhanced_metrics.append(enhanced)
        
        # Portfolio aggregations
        total_investment = sum(m.initial_investment + m.implementation_cost for m in enhanced_metrics)
        total_npv = sum(m.npv_result.npv_value if m.npv_result else 0 for m in enhanced_metrics)
        
        # Portfolio metrics
        portfolio_roi = (total_npv / total_investment * 100) if total_investment > 0 else 0
        
        # Risk analysis
        financial_scores = [m.total_financial_score for m in enhanced_metrics]
        portfolio_risk = np.std(financial_scores) if financial_scores else 0
        
        # Sharpe ratio calculation (risk-adjusted return)
        risk_free_rate = 0.03  # 3% risk-free rate
        excess_return = (portfolio_roi / 100) - risk_free_rate
        sharpe_ratio = (excess_return / portfolio_risk) if portfolio_risk > 0 else 0
        
        return {
            'portfolio_metrics': {
                'total_investment': total_investment,
                'total_npv': total_npv,
                'portfolio_roi': portfolio_roi,
                'portfolio_risk': portfolio_risk,
                'sharpe_ratio': sharpe_ratio,
                'num_items': len(enhanced_metrics)
            },
            'individual_metrics': enhanced_metrics,
            'risk_analysis': {
                'value_at_risk_5pct': np.percentile(financial_scores, 5) if financial_scores else 0,
                'expected_shortfall': np.mean([s for s in financial_scores if s <= np.percentile(financial_scores, 5)]) if financial_scores else 0,
                'score_volatility': np.std(financial_scores) if financial_scores else 0
            }
        }
    
    def calculate_financial_score_for_qvf(
        self,
        financial_metrics: FinancialMetrics,
        normalization_params: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """Calculate normalized financial score specifically for QVF integration.
        
        Args:
            financial_metrics: Financial metrics to score
            normalization_params: Optional normalization parameters
            
        Returns:
            Normalized financial scores for QVF criteria
        """
        # Calculate comprehensive metrics
        enhanced_metrics = self.calculate_comprehensive_financial_metrics(financial_metrics)
        
        # Default normalization parameters
        if not normalization_params:
            normalization_params = {
                'npv_max': 500000,  # $500K max NPV for normalization
                'roi_max': 3.0,     # 300% max ROI for normalization
                'copq_max': 100000, # $100K max COPQ savings for normalization
                'delay_cost_max': 50000  # $50K max monthly delay cost
            }
        
        scores = {}
        
        # NPV Score (0-1)
        if enhanced_metrics.npv_result:
            npv_score = max(0, min(1, enhanced_metrics.npv_result.npv_value / normalization_params['npv_max']))
            scores['npv_score'] = npv_score
        else:
            scores['npv_score'] = 0.0
        
        # ROI Score (0-1)
        if enhanced_metrics.roi_result:
            roi_score = max(0, min(1, enhanced_metrics.roi_result.roi_ratio / normalization_params['roi_max']))
            scores['roi_score'] = roi_score
        else:
            scores['roi_score'] = 0.0
        
        # COPQ Score (0-1)
        if enhanced_metrics.copq_result and enhanced_metrics.copq_result.net_savings > 0:
            copq_score = max(0, min(1, enhanced_metrics.copq_result.net_savings / normalization_params['copq_max']))
            scores['copq_score'] = copq_score
        else:
            scores['copq_score'] = 0.0
        
        # Cost of Delay Score (0-1)
        if enhanced_metrics.cost_of_delay_per_month > 0:
            delay_score = max(0, min(1, enhanced_metrics.cost_of_delay_per_month / normalization_params['delay_cost_max']))
            scores['delay_urgency_score'] = delay_score
        else:
            scores['delay_urgency_score'] = 0.0
        
        # Combined Financial Score with risk adjustment
        component_scores = [scores['npv_score'], scores['roi_score'], scores['copq_score'], scores['delay_urgency_score']]
        weights = [0.4, 0.3, 0.2, 0.1]  # Weights for NPV, ROI, COPQ, Delay
        
        raw_combined_score = sum(score * weight for score, weight in zip(component_scores, weights))
        
        # Apply risk and confidence adjustments
        risk_adjusted_score = self.calculate_risk_adjusted_value(
            raw_combined_score, enhanced_metrics.risk_level, enhanced_metrics.confidence_level
        )
        
        scores['combined_financial_score'] = min(1.0, max(0.0, risk_adjusted_score))
        scores['confidence_level'] = enhanced_metrics.confidence_level
        scores['risk_adjustment_factor'] = self.risk_adjustment_factors.get(enhanced_metrics.risk_level, 1.0)
        
        logger.debug(f"QVF Financial scoring: Combined={scores['combined_financial_score']:.3f}, NPV={scores['npv_score']:.3f}, ROI={scores['roi_score']:.3f}")
        
        return scores
    
    def calculate_advanced_npv_scenarios(
        self,
        base_investment: float,
        scenarios: List[Dict[str, Any]],
        discount_rate: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculate NPV for multiple scenarios with probability weighting.
        
        Args:
            base_investment: Base investment amount
            scenarios: List of scenario definitions with cash_flows and probability
            discount_rate: Discount rate (uses default if None)
            
        Returns:
            Multi-scenario NPV analysis
        """
        discount_rate = discount_rate or self.default_discount_rate
        scenario_results = []
        
        total_probability = sum(scenario.get('probability', 1.0) for scenario in scenarios)
        if abs(total_probability - 1.0) > 1e-6:
            logger.warning(f"Scenario probabilities sum to {total_probability}, normalizing")
            for scenario in scenarios:
                scenario['probability'] = scenario.get('probability', 1.0) / total_probability
        
        expected_npv = 0.0
        
        for i, scenario in enumerate(scenarios):
            cash_flows = scenario['cash_flows']
            probability = scenario.get('probability', 1.0)
            scenario_name = scenario.get('name', f'Scenario_{i+1}')
            
            npv_result = self.calculate_npv(base_investment, cash_flows, discount_rate=discount_rate)
            expected_npv += npv_result.npv_value * probability
            
            scenario_results.append({
                'name': scenario_name,
                'probability': probability,
                'npv': npv_result.npv_value,
                'is_profitable': npv_result.is_profitable,
                'profitability_index': npv_result.profitability_index,
                'weighted_npv': npv_result.npv_value * probability
            })
        
        # Calculate risk metrics
        npv_values = [r['npv'] for r in scenario_results]
        probabilities = [r['probability'] for r in scenario_results]
        
        variance = sum(prob * (npv - expected_npv) ** 2 for npv, prob in zip(npv_values, probabilities))
        std_deviation = math.sqrt(variance)
        
        return {
            'expected_npv': expected_npv,
            'npv_std_deviation': std_deviation,
            'npv_coefficient_of_variation': std_deviation / abs(expected_npv) if expected_npv != 0 else float('inf'),
            'probability_of_profit': sum(r['probability'] for r in scenario_results if r['is_profitable']),
            'scenarios': scenario_results,
            'risk_metrics': {
                'best_case_npv': max(npv_values),
                'worst_case_npv': min(npv_values),
                'npv_range': max(npv_values) - min(npv_values)
            }
        }


# Enhanced utility functions for common financial calculations
def quick_npv(investment: float, annual_benefits: float, years: int, discount_rate: float = 0.10) -> float:
    """Quick NPV calculation for uniform annual benefits.
    
    Args:
        investment: Initial investment
        annual_benefits: Annual benefits
        years: Number of years
        discount_rate: Discount rate
        
    Returns:
        NPV value
    """
    cash_flows = [annual_benefits] * years
    calculator = FinancialCalculator(default_discount_rate=discount_rate)
    result = calculator.calculate_npv(investment, cash_flows)
    return result.npv_value


def quick_roi(investment: float, returns: float) -> float:
    """Quick ROI calculation.
    
    Args:
        investment: Investment amount
        returns: Return amount
        
    Returns:
        ROI percentage
    """
    if investment <= 0:
        return 0.0
    return ((returns - investment) / investment) * 100


def payback_period(investment: float, annual_cash_flow: float) -> float:
    """Calculate payback period in years.
    
    Args:
        investment: Initial investment
        annual_cash_flow: Annual cash flow
        
    Returns:
        Payback period in years
    """
    if annual_cash_flow <= 0:
        return float('inf')
    return investment / annual_cash_flow