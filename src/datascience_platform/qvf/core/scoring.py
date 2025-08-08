"""QVF Financial Scoring Integration Engine

This module provides the integration layer between QVF criteria scoring
and financial calculations. It combines traditional AHP-based criteria
scoring with comprehensive financial modeling to produce unified
prioritization scores.

The scoring engine supports:
- Financial criteria mapping to QVF categories
- Weighted financial score calculation with risk adjustments
- Score aggregation combining financial and non-financial components
- Real-time normalization and calibration
- Sensitivity analysis for financial assumptions
- Portfolio-level financial optimization

Key Features:
- Seamless integration between financial.py and criteria.py
- Dynamic weight adjustment based on financial confidence
- Multi-objective optimization balancing financial and strategic goals
- Real-time score normalization across portfolios
- Financial risk propagation to QVF scores
- Advanced analytics for decision support

Architecture:
    The scoring engine acts as the coordination layer between:
    - QVFCriteriaEngine (criteria.py) - Strategic and operational criteria
    - FinancialCalculator (financial.py) - Financial modeling
    - AHPEngine (ado/ahp.py) - Mathematical prioritization foundation

Usage:
    from datascience_platform.qvf.core.scoring import QVFScoringEngine
    
    scoring_engine = QVFScoringEngine()
    
    # Score work items with financial integration
    results = scoring_engine.score_work_items_with_financials(
        work_items=work_items,
        qvf_config=config,
        financial_data=financial_metrics,
        integration_mode="balanced"  # balanced, financial_priority, strategic_priority
    )
    
    # Get financial contribution breakdown
    financial_breakdown = scoring_engine.analyze_financial_contribution(results)
"""

import logging
import math
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple
from pydantic import BaseModel, Field, field_validator
import numpy as np
from dataclasses import dataclass

# Import QVF core components
from .criteria import (
    QVFCriteriaEngine, QVFCriteriaConfiguration, QVFCriterion, 
    CriteriaCategory, CriteriaWeights, QVFValidationError
)
from .financial import (
    FinancialCalculator, FinancialMetrics, NPVCalculation, 
    COPQCalculation, ROICalculation, RiskLevel
)

# Import AHP foundation
from ...ado.ahp import AHPEngine, AHPConfiguration
from ...ado.models import ADOWorkItem
from ...core.exceptions import DataSciencePlatformError

logger = logging.getLogger(__name__)


class ScoringValidationError(DataSciencePlatformError):
    """Exception raised for QVF scoring validation errors."""
    pass


class IntegrationMode(str, Enum):
    """Integration modes for financial and criteria scoring."""
    BALANCED = "balanced"                    # Equal weight to financial and strategic
    FINANCIAL_PRIORITY = "financial_priority"  # Higher weight to financial metrics
    STRATEGIC_PRIORITY = "strategic_priority"  # Higher weight to strategic criteria
    FINANCIAL_ONLY = "financial_only"        # Financial metrics only
    CRITERIA_ONLY = "criteria_only"          # Strategic criteria only


class FinancialMappingMode(str, Enum):
    """How to map financial metrics to QVF criteria."""
    DIRECT_CRITERIA = "direct_criteria"      # Map as direct criteria
    WEIGHT_MODIFIER = "weight_modifier"      # Use as criteria weight modifiers
    COMPOSITE_SCORE = "composite_score"      # Create composite financial score
    HYBRID = "hybrid"                        # Combination approach


@dataclass
class ScoringConfiguration:
    """Configuration for QVF scoring with financial integration."""
    
    # Integration settings
    integration_mode: IntegrationMode = IntegrationMode.BALANCED
    financial_mapping_mode: FinancialMappingMode = FinancialMappingMode.HYBRID
    
    # Weight balancing
    financial_weight: float = 0.4  # Weight given to financial metrics (0-1)
    strategic_weight: float = 0.6  # Weight given to strategic criteria (0-1)
    
    # Financial normalization
    enable_dynamic_normalization: bool = True
    normalization_percentile: float = 0.95  # Use 95th percentile for normalization
    confidence_threshold: float = 0.6      # Minimum confidence for financial inclusion
    
    # Risk management
    risk_adjustment_enabled: bool = True
    max_risk_penalty: float = 0.3          # Maximum penalty for high risk (0-1)
    
    # Performance settings
    enable_sensitivity_analysis: bool = True
    monte_carlo_iterations: int = 500
    
    def validate(self) -> List[str]:
        """Validate scoring configuration."""
        issues = []
        
        if not (0 <= self.financial_weight <= 1):
            issues.append("Financial weight must be between 0 and 1")
        
        if not (0 <= self.strategic_weight <= 1):
            issues.append("Strategic weight must be between 0 and 1")
        
        if abs(self.financial_weight + self.strategic_weight - 1.0) > 1e-6:
            issues.append("Financial and strategic weights must sum to 1.0")
        
        if not (0.5 <= self.normalization_percentile <= 0.99):
            issues.append("Normalization percentile must be between 0.5 and 0.99")
        
        if not (0 <= self.confidence_threshold <= 1):
            issues.append("Confidence threshold must be between 0 and 1")
        
        return issues


@dataclass
class WorkItemScore:
    """Comprehensive scoring result for a work item."""
    
    # Basic identification
    work_item_id: int
    title: str
    work_item_type: str
    
    # Composite scores
    total_score: float
    financial_score: float
    strategic_score: float
    
    # Rankings
    overall_rank: int
    financial_rank: int
    strategic_rank: int
    
    # Detailed breakdowns
    financial_components: Dict[str, float]  # NPV, ROI, COPQ, etc.
    criteria_scores: Dict[str, float]       # Individual criteria scores
    category_scores: Dict[str, float]       # QVF category scores
    
    # Confidence and risk
    confidence_level: float
    risk_level: str
    risk_adjustment: float
    
    # Financial details
    npv_value: Optional[float] = None
    roi_percentage: Optional[float] = None
    payback_period: Optional[float] = None
    
    # Metadata
    calculation_timestamp: datetime = None
    data_quality_score: float = 1.0
    
    def __post_init__(self):
        if self.calculation_timestamp is None:
            self.calculation_timestamp = datetime.now()


class QVFScoringEngine:
    """Advanced QVF scoring engine with financial integration.
    
    This engine provides comprehensive prioritization by combining:
    - Strategic and operational criteria from QVF framework
    - Financial modeling and projections
    - Risk assessment and adjustments
    - Portfolio-level optimization
    
    The engine supports multiple integration modes and can adapt
    weights based on data quality and confidence levels.
    """
    
    def __init__(
        self,
        criteria_engine: Optional[QVFCriteriaEngine] = None,
        financial_calculator: Optional[FinancialCalculator] = None,
        scoring_config: Optional[ScoringConfiguration] = None
    ):
        """Initialize QVF scoring engine.
        
        Args:
            criteria_engine: QVF criteria engine (creates default if None)
            financial_calculator: Financial calculator (creates default if None)
            scoring_config: Scoring configuration (creates default if None)
        """
        self.criteria_engine = criteria_engine or QVFCriteriaEngine()
        self.financial_calculator = financial_calculator or FinancialCalculator()
        self.scoring_config = scoring_config or ScoringConfiguration()
        
        # Validate configuration
        config_issues = self.scoring_config.validate()
        if config_issues:
            raise ScoringValidationError(f"Invalid scoring configuration: {config_issues}")
        
        logger.info(f"QVF Scoring Engine initialized with {self.scoring_config.integration_mode.value} mode")
    
    def score_work_items_with_financials(
        self,
        work_items: List[ADOWorkItem],
        qvf_config: QVFCriteriaConfiguration,
        financial_data: Dict[int, FinancialMetrics],  # work_item_id -> financial_metrics
        custom_scoring_config: Optional[ScoringConfiguration] = None
    ) -> Dict[str, Any]:
        """Score work items with integrated financial and criteria analysis.
        
        Args:
            work_items: List of work items to score
            qvf_config: QVF criteria configuration
            financial_data: Financial metrics by work item ID
            custom_scoring_config: Override default scoring configuration
            
        Returns:
            Comprehensive scoring results with rankings and analysis
        """
        config = custom_scoring_config or self.scoring_config
        logger.info(f"Scoring {len(work_items)} work items with financial integration")
        
        # Validate inputs
        self._validate_scoring_inputs(work_items, qvf_config, financial_data)
        
        # Calculate financial scores for all items
        financial_scores = self._calculate_financial_scores(financial_data, work_items)
        
        # Calculate strategic criteria scores
        strategic_results = self._calculate_strategic_scores(work_items, qvf_config)
        
        # Combine scores based on integration mode
        combined_scores = self._combine_scores(
            financial_scores, strategic_results, config, work_items
        )
        
        # Generate rankings
        ranked_scores = self._generate_rankings(combined_scores)
        
        # Calculate portfolio-level analytics
        portfolio_analytics = self._calculate_portfolio_analytics(
            ranked_scores, financial_data, strategic_results
        )
        
        # Build comprehensive results
        results = {
            'configuration': {
                'integration_mode': config.integration_mode.value,
                'financial_weight': config.financial_weight,
                'strategic_weight': config.strategic_weight,
                'total_items_scored': len(ranked_scores)
            },
            'work_item_scores': ranked_scores,
            'portfolio_analytics': portfolio_analytics,
            'scoring_quality': self._assess_scoring_quality(ranked_scores, financial_scores, strategic_results),
            'financial_summary': self._summarize_financial_impact(financial_scores),
            'strategic_summary': self._summarize_strategic_alignment(strategic_results),
            'calculation_metadata': {
                'timestamp': datetime.now(),
                'engine_version': '2.0.0',
                'criteria_count': len(qvf_config.get_active_criteria()),
                'financial_coverage': len(financial_data) / len(work_items)
            }
        }
        
        logger.info(f"Scoring completed. Top item: '{ranked_scores[0].title}' with score {ranked_scores[0].total_score:.3f}")
        return results
    
    def _validate_scoring_inputs(
        self,
        work_items: List[ADOWorkItem],
        qvf_config: QVFCriteriaConfiguration,
        financial_data: Dict[int, FinancialMetrics]
    ) -> None:
        """Validate inputs for scoring operation."""
        if not work_items:
            raise ScoringValidationError("No work items provided for scoring")
        
        if len(work_items) > 10000:
            logger.warning(f"Scoring {len(work_items)} items may impact performance")
        
        # Validate QVF configuration
        config_issues = self.criteria_engine.validate_configuration(qvf_config)
        if config_issues:
            raise ScoringValidationError(f"QVF configuration issues: {config_issues}")
        
        # Check financial data coverage
        work_item_ids = {item.work_item_id for item in work_items}
        financial_coverage = len(set(financial_data.keys()) & work_item_ids) / len(work_items)
        
        if financial_coverage < 0.1:
            raise ScoringValidationError("Less than 10% financial data coverage")
        
        if financial_coverage < 0.5:
            logger.warning(f"Low financial data coverage: {financial_coverage:.1%}")
    
    def _calculate_financial_scores(
        self,
        financial_data: Dict[int, FinancialMetrics],
        work_items: List[ADOWorkItem]
    ) -> Dict[int, Dict[str, float]]:
        """Calculate financial scores for work items."""
        logger.info(f"Calculating financial scores for {len(financial_data)} items")
        
        financial_scores = {}
        all_financial_values = []
        
        # First pass: calculate individual scores and collect values for normalization
        for work_item_id, metrics in financial_data.items():
            scores = self.financial_calculator.calculate_financial_score_for_qvf(metrics)
            financial_scores[work_item_id] = scores
            all_financial_values.append(scores['combined_financial_score'])
        
        # Dynamic normalization if enabled
        if self.scoring_config.enable_dynamic_normalization and all_financial_values:
            normalization_factor = np.percentile(all_financial_values, 
                                                self.scoring_config.normalization_percentile * 100)
            
            if normalization_factor > 0:
                for work_item_id in financial_scores:
                    scores = financial_scores[work_item_id]
                    scores['normalized_combined_score'] = min(1.0, scores['combined_financial_score'] / normalization_factor)
                
                logger.info(f"Applied dynamic normalization with factor {normalization_factor:.3f}")
        
        return financial_scores
    
    def _calculate_strategic_scores(
        self,
        work_items: List[ADOWorkItem],
        qvf_config: QVFCriteriaConfiguration
    ) -> Dict[str, Any]:
        """Calculate strategic criteria scores using QVF engine."""
        logger.info(f"Calculating strategic scores using {len(qvf_config.get_active_criteria())} criteria")
        
        strategic_results = self.criteria_engine.calculate_criteria_scores(
            work_items=work_items,
            config=qvf_config,
            include_breakdown=True
        )
        
        # Convert to dictionary keyed by work item ID for easier lookup
        strategic_by_id = {}
        for score_entry in strategic_results['scores']:
            strategic_by_id[score_entry['work_item_id']] = score_entry
        
        strategic_results['scores_by_id'] = strategic_by_id
        return strategic_results
    
    def _combine_scores(
        self,
        financial_scores: Dict[int, Dict[str, float]],
        strategic_results: Dict[str, Any],
        config: ScoringConfiguration,
        work_items: List[ADOWorkItem]
    ) -> List[WorkItemScore]:
        """Combine financial and strategic scores based on integration mode."""
        logger.info(f"Combining scores using {config.integration_mode.value} integration")
        
        combined_scores = []
        strategic_by_id = strategic_results['scores_by_id']
        
        # Collect all strategic scores for normalization
        all_strategic_scores = [strategic_by_id.get(item.work_item_id, {'total_score': 0.0})['total_score'] 
                               for item in work_items]
        
        # Calculate normalization factor for strategic scores if needed
        max_strategic_score = max(all_strategic_scores) if all_strategic_scores else 1.0
        strategic_normalization_factor = max(1.0, max_strategic_score)  # Ensure we don't amplify scores
        
        if strategic_normalization_factor > 1.0:
            logger.info(f"Normalizing strategic scores with factor {strategic_normalization_factor:.3f}")
        
        for work_item in work_items:
            work_item_id = work_item.work_item_id
            
            # Get financial scores (default to zero if not available)
            financial_data = financial_scores.get(work_item_id, {
                'combined_financial_score': 0.0,
                'npv_score': 0.0,
                'roi_score': 0.0,
                'copq_score': 0.0,
                'delay_urgency_score': 0.0,
                'confidence_level': 0.0,
                'risk_adjustment_factor': 1.0
            })
            
            # Get strategic scores (should always be available)
            strategic_data = strategic_by_id.get(work_item_id, {
                'total_score': 0.0,
                'category_scores': {},
                'criterion_scores': {}
            })
            
            # Normalize strategic score to 0-1 range if it's outside this range
            strategic_score = strategic_data['total_score']
            if strategic_score > 1.0:
                logger.debug(f"Strategic score {strategic_score:.3f} > 1.0 for item {work_item_id}, will normalize")
                # We'll normalize after collecting all strategic scores
            
            # Normalize strategic score
            normalized_strategic_score = strategic_data['total_score'] / strategic_normalization_factor
            
            # Calculate combined score based on integration mode
            if config.integration_mode == IntegrationMode.FINANCIAL_ONLY:
                total_score = financial_data['combined_financial_score']
            elif config.integration_mode == IntegrationMode.CRITERIA_ONLY:
                total_score = normalized_strategic_score
            elif config.integration_mode == IntegrationMode.BALANCED:
                financial_component = financial_data.get('normalized_combined_score', financial_data['combined_financial_score'])
                strategic_component = normalized_strategic_score
                total_score = (config.financial_weight * financial_component + 
                             config.strategic_weight * strategic_component)
            elif config.integration_mode == IntegrationMode.FINANCIAL_PRIORITY:
                # Higher weight to financial, but include strategic as modifier
                financial_component = financial_data.get('normalized_combined_score', financial_data['combined_financial_score'])
                strategic_modifier = 1.0 + (normalized_strategic_score - 0.5) * 0.2  # ±20% modifier
                total_score = financial_component * strategic_modifier
            elif config.integration_mode == IntegrationMode.STRATEGIC_PRIORITY:
                # Higher weight to strategic, but include financial as modifier
                strategic_component = normalized_strategic_score
                financial_modifier = 1.0 + (financial_data['combined_financial_score'] - 0.5) * 0.2  # ±20% modifier
                total_score = strategic_component * financial_modifier
            else:
                # Default to balanced
                total_score = (config.financial_weight * financial_data['combined_financial_score'] + 
                             config.strategic_weight * normalized_strategic_score)
            
            # Apply risk adjustment if enabled
            if config.risk_adjustment_enabled:
                risk_penalty = min(config.max_risk_penalty, 
                                 (2.0 - financial_data['risk_adjustment_factor']) * config.max_risk_penalty)
                total_score = total_score * (1.0 - risk_penalty)
            
            # Create work item score object
            score_obj = WorkItemScore(
                work_item_id=work_item_id,
                title=work_item.title,
                work_item_type=work_item.work_item_type.value,
                total_score=max(0.0, min(1.0, total_score)),  # Clamp to [0,1]
                financial_score=financial_data['combined_financial_score'],
                strategic_score=normalized_strategic_score,
                overall_rank=0,  # Will be set in ranking step
                financial_rank=0,  # Will be set in ranking step
                strategic_rank=0,  # Will be set in ranking step
                financial_components={
                    'npv_score': financial_data.get('npv_score', 0.0),
                    'roi_score': financial_data.get('roi_score', 0.0),
                    'copq_score': financial_data.get('copq_score', 0.0),
                    'delay_urgency_score': financial_data.get('delay_urgency_score', 0.0)
                },
                criteria_scores=strategic_data.get('criterion_scores', {}),
                category_scores=strategic_data.get('category_scores', {}),
                confidence_level=financial_data.get('confidence_level', 0.5),
                risk_level='medium',  # TODO: Extract from financial data
                risk_adjustment=financial_data.get('risk_adjustment_factor', 1.0),
                npv_value=None,  # TODO: Extract from financial calculations
                roi_percentage=None,  # TODO: Extract from financial calculations
                payback_period=None  # TODO: Extract from financial calculations
            )
            
            combined_scores.append(score_obj)
        
        return combined_scores
    
    def _generate_rankings(self, combined_scores: List[WorkItemScore]) -> List[WorkItemScore]:
        """Generate rankings for all score types."""
        # Sort by total score for overall ranking
        combined_scores.sort(key=lambda x: x.total_score, reverse=True)
        for rank, score in enumerate(combined_scores, 1):
            score.overall_rank = rank
        
        # Sort by financial score and set financial ranks
        financial_sorted = sorted(combined_scores, key=lambda x: x.financial_score, reverse=True)
        for rank, score in enumerate(financial_sorted, 1):
            score.financial_rank = rank
        
        # Sort by strategic score and set strategic ranks
        strategic_sorted = sorted(combined_scores, key=lambda x: x.strategic_score, reverse=True)
        for rank, score in enumerate(strategic_sorted, 1):
            score.strategic_rank = rank
        
        # Return in overall ranking order
        return combined_scores
    
    def _calculate_portfolio_analytics(
        self,
        ranked_scores: List[WorkItemScore],
        financial_data: Dict[int, FinancialMetrics],
        strategic_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate portfolio-level analytics and insights."""
        # Score distributions
        total_scores = [s.total_score for s in ranked_scores]
        financial_scores = [s.financial_score for s in ranked_scores]
        strategic_scores = [s.strategic_score for s in ranked_scores]
        
        # Financial portfolio analysis
        portfolio_financial = None
        if financial_data:
            financial_metrics_list = list(financial_data.values())
            portfolio_financial = self.financial_calculator.calculate_portfolio_financial_metrics(
                financial_metrics_list
            )
        
        return {
            'score_distributions': {
                'total_score': {
                    'mean': np.mean(total_scores),
                    'std': np.std(total_scores),
                    'min': np.min(total_scores),
                    'max': np.max(total_scores),
                    'percentiles': {
                        '25th': np.percentile(total_scores, 25),
                        '50th': np.percentile(total_scores, 50),
                        '75th': np.percentile(total_scores, 75),
                        '90th': np.percentile(total_scores, 90)
                    }
                },
                'financial_score': {
                    'mean': np.mean(financial_scores),
                    'std': np.std(financial_scores),
                    'coverage': len([s for s in financial_scores if s > 0]) / len(financial_scores)
                },
                'strategic_score': {
                    'mean': np.mean(strategic_scores),
                    'std': np.std(strategic_scores),
                    'consistency_ratio': strategic_results.get('configuration', {}).get('consistency_ratio', 0.0)
                }
            },
            'portfolio_financial': portfolio_financial,
            'ranking_insights': self._generate_ranking_insights(ranked_scores),
            'optimization_recommendations': self._generate_optimization_recommendations(ranked_scores)
        }
    
    def _generate_ranking_insights(self, ranked_scores: List[WorkItemScore]) -> Dict[str, Any]:
        """Generate insights about ranking patterns."""
        # Find items where financial and strategic rankings differ significantly
        ranking_misalignments = []
        for score in ranked_scores:
            rank_difference = abs(score.financial_rank - score.strategic_rank)
            if rank_difference > len(ranked_scores) * 0.2:  # >20% of total items
                ranking_misalignments.append({
                    'work_item_id': score.work_item_id,
                    'title': score.title,
                    'financial_rank': score.financial_rank,
                    'strategic_rank': score.strategic_rank,
                    'rank_difference': rank_difference
                })
        
        # Top performers in each category
        top_financial = sorted(ranked_scores, key=lambda x: x.financial_score, reverse=True)[:5]
        top_strategic = sorted(ranked_scores, key=lambda x: x.strategic_score, reverse=True)[:5]
        
        return {
            'ranking_misalignments': ranking_misalignments,
            'top_financial_performers': [{'id': s.work_item_id, 'title': s.title, 'score': s.financial_score} for s in top_financial],
            'top_strategic_performers': [{'id': s.work_item_id, 'title': s.title, 'score': s.strategic_score} for s in top_strategic],
            'score_correlation': np.corrcoef([s.financial_score for s in ranked_scores], 
                                           [s.strategic_score for s in ranked_scores])[0,1] if len(ranked_scores) > 1 else 0.0
        }
    
    def _generate_optimization_recommendations(self, ranked_scores: List[WorkItemScore]) -> List[Dict[str, str]]:
        """Generate recommendations for portfolio optimization."""
        recommendations = []
        
        # Check for low-confidence high-ranking items
        high_rank_low_confidence = [s for s in ranked_scores[:10] if s.confidence_level < 0.5]
        if high_rank_low_confidence:
            recommendations.append({
                'type': 'data_quality',
                'priority': 'high',
                'message': f"Top-ranked items have low financial confidence. Consider gathering more financial data for {len(high_rank_low_confidence)} high-priority items."
            })
        
        # Check for high financial value but low strategic alignment
        financial_strategic_mismatch = [s for s in ranked_scores if s.financial_score > 0.7 and s.strategic_score < 0.3]
        if financial_strategic_mismatch:
            recommendations.append({
                'type': 'strategic_alignment',
                'priority': 'medium',
                'message': f"Found {len(financial_strategic_mismatch)} items with high financial value but low strategic alignment. Review strategic criteria weighting."
            })
        
        # Check portfolio balance
        top_quartile = ranked_scores[:len(ranked_scores)//4]
        category_distribution = {}
        for score in top_quartile:
            for category, cat_score in score.category_scores.items():
                if category not in category_distribution:
                    category_distribution[category] = []
                category_distribution[category].append(cat_score)
        
        # Look for category imbalances
        for category, scores in category_distribution.items():
            if len(scores) < len(top_quartile) * 0.2:  # Less than 20% representation
                recommendations.append({
                    'type': 'portfolio_balance',
                    'priority': 'low',
                    'message': f"Category '{category}' is underrepresented in top quartile. Consider reviewing category weights or criteria definitions."
                })
        
        return recommendations
    
    def _assess_scoring_quality(
        self,
        ranked_scores: List[WorkItemScore],
        financial_scores: Dict[int, Dict[str, float]],
        strategic_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess the quality and reliability of scoring results."""
        # Data coverage
        financial_coverage = len(financial_scores) / len(ranked_scores)
        
        # Average confidence levels
        avg_confidence = np.mean([s.confidence_level for s in ranked_scores])
        
        # Consistency with AHP
        ahp_consistency = strategic_results.get('configuration', {}).get('is_consistent', False)
        consistency_ratio = strategic_results.get('configuration', {}).get('consistency_ratio', 1.0)
        
        # Score distribution quality
        total_scores = [s.total_score for s in ranked_scores]
        score_range = np.max(total_scores) - np.min(total_scores)
        score_variance = np.var(total_scores)
        
        quality_score = (
            financial_coverage * 0.3 +
            avg_confidence * 0.3 +
            (1.0 if ahp_consistency else 0.0) * 0.2 +
            min(1.0, score_range) * 0.1 +
            min(1.0, score_variance * 4) * 0.1  # Variance should be reasonable
        )
        
        return {
            'overall_quality_score': quality_score,
            'financial_coverage': financial_coverage,
            'average_confidence': avg_confidence,
            'ahp_consistency': ahp_consistency,
            'consistency_ratio': consistency_ratio,
            'score_distribution_quality': {
                'range': score_range,
                'variance': score_variance,
                'coefficient_of_variation': np.std(total_scores) / np.mean(total_scores) if np.mean(total_scores) > 0 else 0
            },
            'quality_assessment': 'excellent' if quality_score > 0.8 else 'good' if quality_score > 0.6 else 'fair' if quality_score > 0.4 else 'poor'
        }
    
    def _summarize_financial_impact(self, financial_scores: Dict[int, Dict[str, float]]) -> Dict[str, Any]:
        """Summarize financial impact across portfolio."""
        if not financial_scores:
            return {'total_items': 0, 'message': 'No financial data available'}
        
        all_scores = list(financial_scores.values())
        
        return {
            'total_items_with_financial_data': len(all_scores),
            'average_financial_score': np.mean([s['combined_financial_score'] for s in all_scores]),
            'high_financial_value_items': len([s for s in all_scores if s['combined_financial_score'] > 0.7]),
            'average_confidence': np.mean([s.get('confidence_level', 0.5) for s in all_scores]),
            'score_components': {
                'average_npv_score': np.mean([s.get('npv_score', 0) for s in all_scores]),
                'average_roi_score': np.mean([s.get('roi_score', 0) for s in all_scores]),
                'average_copq_score': np.mean([s.get('copq_score', 0) for s in all_scores]),
                'average_delay_urgency': np.mean([s.get('delay_urgency_score', 0) for s in all_scores])
            }
        }
    
    def _summarize_strategic_alignment(self, strategic_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize strategic alignment across portfolio."""
        scores = strategic_results.get('scores', [])
        
        if not scores:
            return {'total_items': 0, 'message': 'No strategic scoring data available'}
        
        # Category performance
        category_performance = {}
        for score_entry in scores:
            for category, cat_score in score_entry.get('category_scores', {}).items():
                if category not in category_performance:
                    category_performance[category] = []
                category_performance[category].append(cat_score)
        
        category_averages = {cat: np.mean(scores) for cat, scores in category_performance.items()}
        
        return {
            'total_items_scored': len(scores),
            'average_strategic_score': np.mean([s['total_score'] for s in scores]),
            'high_strategic_value_items': len([s for s in scores if s['total_score'] > 0.7]),
            'category_performance': category_averages,
            'consistency_metrics': {
                'is_consistent': strategic_results.get('configuration', {}).get('is_consistent', False),
                'consistency_ratio': strategic_results.get('configuration', {}).get('consistency_ratio', 1.0)
            }
        }
    
    def analyze_financial_contribution(self, scoring_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the contribution of financial factors to final rankings."""
        work_item_scores = scoring_results['work_item_scores']
        
        # Correlation between financial scores and final rankings
        financial_scores = [s.financial_score for s in work_item_scores]
        total_scores = [s.total_score for s in work_item_scores]
        
        financial_correlation = np.corrcoef(financial_scores, total_scores)[0,1] if len(financial_scores) > 1 else 0.0
        
        # Items where financial factors significantly impacted ranking
        significant_financial_impact = []
        for score in work_item_scores:
            # Calculate what ranking would be with strategic only
            strategic_only_rank = score.strategic_rank
            actual_rank = score.overall_rank
            
            rank_change = strategic_only_rank - actual_rank
            if abs(rank_change) > len(work_item_scores) * 0.1:  # >10% change
                significant_financial_impact.append({
                    'work_item_id': score.work_item_id,
                    'title': score.title,
                    'strategic_rank': strategic_only_rank,
                    'actual_rank': actual_rank,
                    'rank_change': rank_change,
                    'financial_score': score.financial_score
                })
        
        return {
            'financial_correlation_with_total': financial_correlation,
            'items_significantly_impacted_by_financials': significant_financial_impact,
            'financial_impact_summary': {
                'total_impacted_items': len(significant_financial_impact),
                'average_rank_change': np.mean([item['rank_change'] for item in significant_financial_impact]) if significant_financial_impact else 0,
                'max_positive_impact': max([item['rank_change'] for item in significant_financial_impact], default=0),
                'max_negative_impact': min([item['rank_change'] for item in significant_financial_impact], default=0)
            }
        }
    
    def perform_sensitivity_analysis(
        self,
        work_items: List[ADOWorkItem],
        qvf_config: QVFCriteriaConfiguration,
        financial_data: Dict[int, FinancialMetrics],
        parameter_variations: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on scoring parameters."""
        logger.info(f"Performing sensitivity analysis with {len(parameter_variations)} parameter variations")
        
        base_results = self.score_work_items_with_financials(work_items, qvf_config, financial_data)
        base_rankings = {score.work_item_id: score.overall_rank for score in base_results['work_item_scores']}
        
        sensitivity_results = {}
        
        for param_name, variations in parameter_variations.items():
            param_results = []
            
            for variation_value in variations:
                # Create modified scoring configuration
                modified_config = ScoringConfiguration(
                    **self.scoring_config.__dict__
                )
                
                # Apply parameter variation
                if hasattr(modified_config, param_name):
                    setattr(modified_config, param_name, variation_value)
                
                # Calculate scores with modified configuration
                try:
                    modified_results = self.score_work_items_with_financials(
                        work_items, qvf_config, financial_data, modified_config
                    )
                    
                    # Calculate ranking changes
                    modified_rankings = {score.work_item_id: score.overall_rank for score in modified_results['work_item_scores']}
                    
                    rank_changes = []
                    for work_item_id in base_rankings:
                        base_rank = base_rankings[work_item_id]
                        modified_rank = modified_rankings.get(work_item_id, base_rank)
                        rank_changes.append(abs(base_rank - modified_rank))
                    
                    param_results.append({
                        'parameter_value': variation_value,
                        'average_rank_change': np.mean(rank_changes),
                        'max_rank_change': np.max(rank_changes),
                        'items_with_significant_change': len([r for r in rank_changes if r > len(work_items) * 0.1])
                    })
                    
                except Exception as e:
                    logger.warning(f"Sensitivity analysis failed for {param_name}={variation_value}: {e}")
                    continue
            
            sensitivity_results[param_name] = param_results
        
        return {
            'base_results_summary': {
                'total_items': len(base_rankings),
                'top_item_id': min(base_rankings, key=base_rankings.get)
            },
            'parameter_sensitivity': sensitivity_results,
            'sensitivity_summary': self._summarize_sensitivity_results(sensitivity_results)
        }
    
    def _summarize_sensitivity_results(self, sensitivity_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Summarize sensitivity analysis results."""
        parameter_impacts = {}
        
        for param_name, results in sensitivity_results.items():
            if not results:
                continue
            
            avg_impacts = [r['average_rank_change'] for r in results]
            max_impacts = [r['max_rank_change'] for r in results]
            
            parameter_impacts[param_name] = {
                'sensitivity_level': 'high' if np.mean(avg_impacts) > 5 else 'medium' if np.mean(avg_impacts) > 2 else 'low',
                'average_impact': np.mean(avg_impacts),
                'max_impact_observed': np.max(max_impacts),
                'stability_score': 1.0 / (1.0 + np.mean(avg_impacts))  # Higher score = more stable
            }
        
        # Overall sensitivity assessment
        overall_sensitivity = np.mean([p['average_impact'] for p in parameter_impacts.values()]) if parameter_impacts else 0
        
        return {
            'parameter_impacts': parameter_impacts,
            'overall_sensitivity': overall_sensitivity,
            'most_sensitive_parameter': max(parameter_impacts.keys(), key=lambda k: parameter_impacts[k]['average_impact']) if parameter_impacts else None,
            'most_stable_parameter': max(parameter_impacts.keys(), key=lambda k: parameter_impacts[k]['stability_score']) if parameter_impacts else None,
            'sensitivity_assessment': 'high' if overall_sensitivity > 5 else 'medium' if overall_sensitivity > 2 else 'low'
        }


# Factory functions for common scoring configurations
def create_balanced_scoring_config() -> ScoringConfiguration:
    """Create balanced financial-strategic scoring configuration."""
    return ScoringConfiguration(
        integration_mode=IntegrationMode.BALANCED,
        financial_weight=0.5,
        strategic_weight=0.5,
        enable_dynamic_normalization=True
    )


def create_financial_priority_config() -> ScoringConfiguration:
    """Create financial-priority scoring configuration."""
    return ScoringConfiguration(
        integration_mode=IntegrationMode.FINANCIAL_PRIORITY,
        financial_weight=0.7,
        strategic_weight=0.3,
        confidence_threshold=0.7,
        risk_adjustment_enabled=True
    )


def create_strategic_priority_config() -> ScoringConfiguration:
    """Create strategic-priority scoring configuration."""
    return ScoringConfiguration(
        integration_mode=IntegrationMode.STRATEGIC_PRIORITY,
        financial_weight=0.3,
        strategic_weight=0.7,
        enable_dynamic_normalization=False
    )