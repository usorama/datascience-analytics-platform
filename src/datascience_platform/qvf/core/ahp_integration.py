"""QVF-AHP Integration Engine

This module provides the bridge between QVF criteria system and the enhanced AHP engine.
It handles the conversion of QVF criterion scores into AHP pairwise comparison matrices,
manages multi-level hierarchies for complex QVF structures, and provides advanced
quality assurance for the mathematical consistency of prioritization decisions.

Key Features:
- Automatic pairwise comparison matrix generation from QVF scores
- Multi-level hierarchy support for nested QVF criteria
- Consistency monitoring and automated improvement
- Group decision aggregation using geometric mean method
- Advanced sensitivity analysis for QVF-specific parameters
- Score reconciliation between QVF methods and pure AHP
- Real-time quality assessment and validation

Architecture Integration:
    QVF Criteria (criteria.py) → AHP Integration → Enhanced AHP (ahp.py) → Financial Integration (scoring.py)

The integration engine ensures mathematical rigor while maintaining the business logic
and domain expertise embedded in the QVF framework.

Usage:
    from datascience_platform.qvf.core.ahp_integration import QVFAHPIntegrator
    
    integrator = QVFAHPIntegrator()
    
    # Convert QVF scores to AHP analysis
    ahp_results = integrator.convert_qvf_to_ahp(
        qvf_results=qvf_criteria_results,
        work_items=work_items,
        consistency_threshold=0.10
    )
    
    # Perform integrated analysis
    integrated_results = integrator.perform_integrated_analysis(
        qvf_config=config,
        work_items=work_items,
        stakeholder_inputs=stakeholder_comparisons
    )
"""

import logging
import math
from datetime import datetime
from typing import List, Dict, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.spatial.distance import pdist, squareform
import warnings

# Import QVF core components
from .criteria import (
    QVFCriteriaEngine, QVFCriteriaConfiguration, QVFCriterion, 
    CriteriaCategory, CriteriaWeights
)
from .financial import FinancialCalculator, FinancialMetrics

# Import enhanced AHP engine
from ...ado.ahp import (
    AHPEngine, AHPConfiguration, AHPCriterion, PairwiseComparison,
    AHPValidationResult, GroupAHPResult
)
from ...ado.models import ADOWorkItem
from ...core.exceptions import DataSciencePlatformError

logger = logging.getLogger(__name__)


class QVFAHPIntegrationError(DataSciencePlatformError):
    """Exception raised for QVF-AHP integration errors."""
    pass


class ConversionMethod(str, Enum):
    """Methods for converting QVF scores to AHP comparisons."""
    SCORE_RATIO = "score_ratio"                    # Direct ratio of QVF scores
    LOGARITHMIC_SCALE = "logarithmic_scale"        # Logarithmic mapping to AHP 1-9 scale
    PERCENTILE_MAPPING = "percentile_mapping"      # Map score percentiles to AHP values
    PREFERENCE_ELICITATION = "preference_elicitation"  # Use stakeholder preferences
    HYBRID_APPROACH = "hybrid_approach"            # Combine multiple methods


class HierarchyLevel(str, Enum):
    """Levels in QVF hierarchy for AHP analysis."""
    ROOT = "root"                                  # Overall goal
    CATEGORIES = "categories"                      # QVF categories (e.g., Business Value, Risk)
    CRITERIA = "criteria"                          # Individual criteria within categories
    SUB_CRITERIA = "sub_criteria"                  # Sub-criteria if defined


@dataclass
class IntegrationConfiguration:
    """Configuration for QVF-AHP integration."""
    
    # Conversion settings
    conversion_method: ConversionMethod = ConversionMethod.HYBRID_APPROACH
    consistency_threshold: float = 0.10
    auto_improve_consistency: bool = True
    max_improvement_iterations: int = 10
    
    # Hierarchy settings
    enable_multi_level_hierarchy: bool = True
    category_weight_method: str = "equal"          # "equal", "importance", "ahp"
    
    # Quality assurance
    minimum_score_difference: float = 0.01        # Minimum difference to create meaningful comparison
    extreme_ratio_threshold: float = 7.0          # Maximum AHP ratio before adjustment
    
    # Group decision settings
    enable_group_aggregation: bool = False
    group_method: str = "geometric_mean"           # "geometric_mean", "weighted_average"
    
    # Advanced features
    perform_sensitivity_analysis: bool = True
    monte_carlo_iterations: int = 500
    confidence_level: float = 0.95

    def validate(self) -> List[str]:
        """Validate integration configuration."""
        issues = []
        
        if not (0.01 <= self.consistency_threshold <= 0.30):
            issues.append("Consistency threshold must be between 0.01 and 0.30")
        
        if not (0.001 <= self.minimum_score_difference <= 0.1):
            issues.append("Minimum score difference must be between 0.001 and 0.1")
        
        if not (2.0 <= self.extreme_ratio_threshold <= 9.0):
            issues.append("Extreme ratio threshold must be between 2.0 and 9.0")
        
        if self.monte_carlo_iterations < 100:
            issues.append("Monte Carlo iterations should be at least 100")
        
        return issues


@dataclass
class IntegrationResult:
    """Result of QVF-AHP integration analysis."""
    
    # Integration metadata
    integration_timestamp: datetime
    conversion_method: ConversionMethod
    consistency_achieved: bool
    final_consistency_ratio: float
    
    # Hierarchy results
    ahp_engines: Dict[str, AHPEngine]               # Level -> AHP Engine
    level_weights: Dict[str, np.ndarray]            # Level -> weight vector
    global_weights: np.ndarray                      # Final global weights
    
    # Quality metrics
    integration_quality_score: float
    validation_results: Dict[str, AHPValidationResult]
    score_reconciliation: Dict[str, float]          # QVF vs AHP score comparison
    
    # Work item results  
    work_item_rankings: List[Tuple[int, float, Dict[str, float]]]
    ranking_stability: Dict[str, float]
    
    # Advanced analytics
    sensitivity_analysis: Optional[Dict[str, Any]] = None
    group_results: Optional[GroupAHPResult] = None
    
    def get_top_items(self, n: int = 10) -> List[Tuple[int, float, Dict[str, float]]]:
        """Get top N ranked work items."""
        return self.work_item_rankings[:n]
    
    def get_criterion_global_weight(self, criterion_name: str) -> float:
        """Get global weight for a specific criterion."""
        # Search through hierarchy levels to find the criterion
        for level, engine in self.ahp_engines.items():
            for i, criterion in enumerate(engine.config.criteria):
                if criterion.name == criterion_name:
                    level_weight = self.level_weights.get(level, np.array([1.0]))[0]
                    criterion_weight = engine.weights[i] if engine.weights is not None else 0.0
                    return level_weight * criterion_weight
        return 0.0


class QVFAHPIntegrator:
    """Advanced QVF-AHP integration engine.
    
    This class bridges the QVF criteria framework with the enhanced AHP engine,
    providing mathematically rigorous prioritization that maintains business logic.
    
    Key capabilities:
    - Convert QVF criterion scores to AHP pairwise comparisons
    - Handle multi-level hierarchies (categories → criteria → sub-criteria)
    - Ensure mathematical consistency while preserving domain expertise
    - Aggregate multiple stakeholder inputs using group decision methods
    - Provide comprehensive sensitivity analysis and validation
    """
    
    def __init__(
        self,
        qvf_engine: Optional[QVFCriteriaEngine] = None,
        financial_calculator: Optional[FinancialCalculator] = None,
        integration_config: Optional[IntegrationConfiguration] = None
    ):
        """Initialize QVF-AHP integrator.
        
        Args:
            qvf_engine: QVF criteria engine (creates default if None)
            financial_calculator: Financial calculator for hybrid scoring
            integration_config: Integration configuration (creates default if None)
        """
        self.qvf_engine = qvf_engine or QVFCriteriaEngine()
        self.financial_calculator = financial_calculator or FinancialCalculator()
        self.config = integration_config or IntegrationConfiguration()
        
        # Validate configuration
        config_issues = self.config.validate()
        if config_issues:
            raise QVFAHPIntegrationError(f"Invalid integration configuration: {config_issues}")
        
        # Internal state
        self.hierarchy_engines: Dict[str, AHPEngine] = {}
        self.conversion_cache: Dict[str, np.ndarray] = {}
        self.quality_metrics: Dict[str, float] = {}
        
        logger.info(f"QVF-AHP Integrator initialized with {self.config.conversion_method.value} conversion method")
    
    def convert_qvf_to_ahp(
        self,
        qvf_results: Dict[str, Any],
        work_items: List[ADOWorkItem],
        stakeholder_preferences: Optional[Dict[str, Dict[str, float]]] = None
    ) -> IntegrationResult:
        """Convert QVF results to comprehensive AHP analysis.
        
        Args:
            qvf_results: Results from QVF criteria analysis
            work_items: Work items to prioritize
            stakeholder_preferences: Optional stakeholder preference inputs
            
        Returns:
            Comprehensive integration result with AHP analysis
        """
        logger.info(f"Converting QVF results to AHP for {len(work_items)} work items")
        
        integration_start = datetime.now()
        
        # Extract QVF scores and configuration
        qvf_scores = qvf_results.get('scores', [])
        qvf_config = qvf_results.get('configuration', {})
        
        if not qvf_scores:
            raise QVFAHPIntegrationError("No QVF scores available for conversion")
        
        # Build hierarchy structure
        hierarchy_structure = self._build_hierarchy_structure(qvf_config)
        
        # Create AHP engines for each hierarchy level
        ahp_engines = {}
        level_weights = {}
        validation_results = {}
        
        for level_name, level_config in hierarchy_structure.items():
            logger.info(f"Processing hierarchy level: {level_name}")
            
            # Create AHP configuration for this level
            ahp_config = self._create_ahp_configuration_for_level(level_config)
            
            # Create AHP engine
            ahp_engine = AHPEngine(ahp_config, enable_advanced_features=True)
            
            # Generate comparison matrix using selected method
            comparison_matrix = self._generate_comparison_matrix(
                level_config, qvf_scores, stakeholder_preferences
            )
            
            # Set matrix and calculate weights
            ahp_engine.comparison_matrix = comparison_matrix
            weights = ahp_engine.calculate_weights()
            
            # Validate and improve consistency if needed
            validation = ahp_engine.validate_ahp_analysis()
            
            if not validation.is_valid and self.config.auto_improve_consistency:
                logger.info(f"Improving consistency for level {level_name} (CR={validation.consistency_ratio:.4f})")
                success, steps = ahp_engine.improve_consistency_automatically(
                    self.config.max_improvement_iterations
                )
                if success:
                    validation = ahp_engine.validate_ahp_analysis()
                    logger.info(f"Consistency improved to CR={validation.consistency_ratio:.4f}")
            
            ahp_engines[level_name] = ahp_engine
            level_weights[level_name] = weights
            validation_results[level_name] = validation
        
        # Calculate global weights across hierarchy
        global_weights = self._calculate_global_weights(ahp_engines, hierarchy_structure)
        
        # Rank work items using global weights
        work_item_rankings = self._rank_work_items_with_global_weights(
            work_items, qvf_scores, global_weights, ahp_engines
        )
        
        # Calculate integration quality score
        quality_score = self._calculate_integration_quality(validation_results, global_weights)
        
        # Perform score reconciliation
        score_reconciliation = self._reconcile_qvf_ahp_scores(qvf_scores, work_item_rankings)
        
        # Calculate ranking stability
        ranking_stability = self._calculate_ranking_stability(work_item_rankings, ahp_engines)
        
        # Create integration result
        result = IntegrationResult(
            integration_timestamp=integration_start,
            conversion_method=self.config.conversion_method,
            consistency_achieved=all(v.is_valid for v in validation_results.values()),
            final_consistency_ratio=max(v.consistency_ratio for v in validation_results.values()),
            ahp_engines=ahp_engines,
            level_weights=level_weights,
            global_weights=global_weights,
            integration_quality_score=quality_score,
            validation_results=validation_results,
            score_reconciliation=score_reconciliation,
            work_item_rankings=work_item_rankings,
            ranking_stability=ranking_stability
        )
        
        # Add advanced analytics if enabled
        if self.config.perform_sensitivity_analysis:
            result.sensitivity_analysis = self._perform_integrated_sensitivity_analysis(
                ahp_engines, work_items, qvf_scores
            )
        
        # Add group results if applicable
        if stakeholder_preferences and self.config.enable_group_aggregation:
            result.group_results = self._perform_group_analysis(
                stakeholder_preferences, hierarchy_structure
            )
        
        logger.info(f"QVF-AHP integration completed in {(datetime.now() - integration_start).total_seconds():.2f} seconds")
        logger.info(f"Final consistency ratio: {result.final_consistency_ratio:.4f}, Quality score: {quality_score:.3f}")
        
        return result
    
    def _build_hierarchy_structure(self, qvf_config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Build hierarchical structure from QVF configuration."""
        hierarchy = {}
        
        # Extract active criteria
        active_criteria = qvf_config.get('active_criteria', [])
        
        if not active_criteria:
            raise QVFAHPIntegrationError("No active criteria found in QVF configuration")
        
        if self.config.enable_multi_level_hierarchy:
            # Group criteria by category
            categories = {}
            for criterion in active_criteria:
                category = criterion.get('category', 'default')
                if category not in categories:
                    categories[category] = []
                categories[category].append(criterion)
            
            # Create hierarchy levels
            if len(categories) > 1:
                # Multi-category hierarchy: Root -> Categories -> Criteria
                hierarchy[HierarchyLevel.CATEGORIES.value] = {
                    'type': 'categories',
                    'items': list(categories.keys()),
                    'description': 'QVF Categories'
                }
                
                for category, criteria in categories.items():
                    hierarchy[f"{HierarchyLevel.CRITERIA.value}_{category}"] = {
                        'type': 'criteria',
                        'category': category,
                        'items': criteria,
                        'description': f'Criteria in {category} category'
                    }
            else:
                # Single category: just criteria level
                category = list(categories.keys())[0]
                hierarchy[HierarchyLevel.CRITERIA.value] = {
                    'type': 'criteria',
                    'category': category,
                    'items': categories[category],
                    'description': 'QVF Criteria'
                }
        else:
            # Flat hierarchy: just criteria level
            hierarchy[HierarchyLevel.CRITERIA.value] = {
                'type': 'criteria',
                'category': 'all',
                'items': active_criteria,
                'description': 'All QVF Criteria'
            }
        
        logger.info(f"Built hierarchy with {len(hierarchy)} levels: {list(hierarchy.keys())}")
        return hierarchy
    
    def _create_ahp_configuration_for_level(self, level_config: Dict[str, Any]) -> AHPConfiguration:
        """Create AHP configuration for a specific hierarchy level."""
        level_type = level_config['type']
        items = level_config['items']
        
        # Create AHP criteria
        ahp_criteria = []
        
        if level_type == 'categories':
            # Category-level comparisons
            for category in items:
                criterion = AHPCriterion(
                    name=category,
                    description=f"QVF Category: {category}",
                    weight=0.0,  # Will be calculated
                    data_source=f"category_{category}",
                    higher_is_better=True,
                    normalization_method="none"
                )
                ahp_criteria.append(criterion)
        
        elif level_type == 'criteria':
            # Criteria-level comparisons
            for criterion_config in items:
                if isinstance(criterion_config, dict):
                    name = criterion_config.get('name', 'Unknown')
                    description = criterion_config.get('description', 'QVF Criterion')
                    data_source = criterion_config.get('field_name', name.lower().replace(' ', '_'))
                    
                    criterion = AHPCriterion(
                        name=name,
                        description=description,
                        weight=0.0,  # Will be calculated
                        data_source=data_source,
                        higher_is_better=criterion_config.get('higher_is_better', True),
                        normalization_method=criterion_config.get('normalization_method', 'minmax')
                    )
                    ahp_criteria.append(criterion)
        
        if not ahp_criteria:
            raise QVFAHPIntegrationError(f"No AHP criteria created for level type: {level_type}")
        
        return AHPConfiguration(
            criteria=ahp_criteria,
            consistency_threshold=self.config.consistency_threshold
        )
    
    def _generate_comparison_matrix(
        self,
        level_config: Dict[str, Any],
        qvf_scores: List[Dict[str, Any]],
        stakeholder_preferences: Optional[Dict[str, Dict[str, float]]]
    ) -> np.ndarray:
        """Generate pairwise comparison matrix for hierarchy level."""
        items = level_config['items']
        n = len(items)
        matrix = np.eye(n)
        
        if self.config.conversion_method == ConversionMethod.SCORE_RATIO:
            matrix = self._generate_matrix_score_ratio(level_config, qvf_scores)
        
        elif self.config.conversion_method == ConversionMethod.LOGARITHMIC_SCALE:
            matrix = self._generate_matrix_logarithmic(level_config, qvf_scores)
        
        elif self.config.conversion_method == ConversionMethod.PERCENTILE_MAPPING:
            matrix = self._generate_matrix_percentile(level_config, qvf_scores)
        
        elif self.config.conversion_method == ConversionMethod.PREFERENCE_ELICITATION:
            if stakeholder_preferences:
                matrix = self._generate_matrix_preferences(level_config, stakeholder_preferences)
            else:
                logger.warning("No stakeholder preferences provided, falling back to score ratio")
                matrix = self._generate_matrix_score_ratio(level_config, qvf_scores)
        
        elif self.config.conversion_method == ConversionMethod.HYBRID_APPROACH:
            matrix = self._generate_matrix_hybrid(level_config, qvf_scores, stakeholder_preferences)
        
        # Validate and adjust matrix
        matrix = self._validate_and_adjust_matrix(matrix)
        
        return matrix
    
    def _generate_matrix_score_ratio(self, level_config: Dict[str, Any], qvf_scores: List[Dict[str, Any]]) -> np.ndarray:
        """Generate comparison matrix using direct score ratios."""
        items = level_config['items']
        n = len(items)
        matrix = np.eye(n)
        
        # Calculate average scores for each item
        item_scores = {}
        
        if level_config['type'] == 'categories':
            # Category-level scores
            for i, category in enumerate(items):
                category_score = 0.0
                count = 0
                
                for work_item_score in qvf_scores:
                    category_scores = work_item_score.get('category_scores', {})
                    if category in category_scores:
                        category_score += category_scores[category]
                        count += 1
                
                item_scores[i] = category_score / count if count > 0 else 0.0
        
        elif level_config['type'] == 'criteria':
            # Criteria-level scores
            for i, criterion_config in enumerate(items):
                criterion_name = criterion_config.get('name') if isinstance(criterion_config, dict) else str(criterion_config)
                criterion_score = 0.0
                count = 0
                
                for work_item_score in qvf_scores:
                    criterion_scores = work_item_score.get('criterion_scores', {})
                    if criterion_name in criterion_scores:
                        criterion_score += criterion_scores[criterion_name]
                        count += 1
                
                item_scores[i] = criterion_score / count if count > 0 else 0.0
        
        # Create comparison matrix from score ratios
        for i in range(n):
            for j in range(n):
                if i != j:
                    score_i = item_scores.get(i, 0.0)
                    score_j = item_scores.get(j, 0.0)
                    
                    if score_j > 0:
                        ratio = score_i / score_j
                        # Map to AHP 1-9 scale
                        if ratio > 1:
                            matrix[i, j] = min(9.0, max(1.0, ratio))
                        else:
                            matrix[i, j] = max(1/9.0, min(1.0, ratio))
                    else:
                        matrix[i, j] = 1.0
        
        return matrix
    
    def _generate_matrix_logarithmic(self, level_config: Dict[str, Any], qvf_scores: List[Dict[str, Any]]) -> np.ndarray:
        """Generate comparison matrix using logarithmic scale mapping."""
        # First get score ratios
        matrix = self._generate_matrix_score_ratio(level_config, qvf_scores)
        n = matrix.shape[0]
        
        # Apply logarithmic transformation to map to AHP scale more smoothly
        for i in range(n):
            for j in range(n):
                if i != j:
                    ratio = matrix[i, j]
                    if ratio > 1:
                        # Map ratios > 1 to AHP scale 1-9 using log transformation
                        log_ratio = math.log(ratio)
                        ahp_value = 1 + (8 * log_ratio) / math.log(9)  # Scale to 1-9
                        matrix[i, j] = min(9.0, max(1.0, ahp_value))
                    elif ratio < 1:
                        # Map ratios < 1 to AHP scale 1/9-1
                        log_ratio = math.log(1/ratio)
                        ahp_value = 1 + (8 * log_ratio) / math.log(9)
                        matrix[i, j] = max(1/9.0, min(1.0, 1/ahp_value))
        
        return matrix
    
    def _generate_matrix_percentile(self, level_config: Dict[str, Any], qvf_scores: List[Dict[str, Any]]) -> np.ndarray:
        """Generate comparison matrix using percentile mapping."""
        items = level_config['items']
        n = len(items)
        matrix = np.eye(n)
        
        # Get item scores (same as score ratio method)
        item_scores = {}
        all_scores = []
        
        # Calculate scores similar to score_ratio method
        if level_config['type'] == 'categories':
            for i, category in enumerate(items):
                category_score = 0.0
                count = 0
                for work_item_score in qvf_scores:
                    category_scores = work_item_score.get('category_scores', {})
                    if category in category_scores:
                        category_score += category_scores[category]
                        count += 1
                item_scores[i] = category_score / count if count > 0 else 0.0
                all_scores.append(item_scores[i])
        
        # Convert scores to percentiles
        percentiles = stats.rankdata(all_scores, method='average') / len(all_scores)
        
        # Create matrix based on percentile differences
        for i in range(n):
            for j in range(n):
                if i != j:
                    percentile_i = percentiles[i] if i < len(percentiles) else 0.5
                    percentile_j = percentiles[j] if j < len(percentiles) else 0.5
                    
                    # Map percentile difference to AHP scale
                    diff = percentile_i - percentile_j
                    if diff > 0:
                        # Map positive differences to 1-9 scale
                        ahp_value = 1 + 8 * diff  # Linear mapping
                        matrix[i, j] = min(9.0, max(1.0, ahp_value))
                    else:
                        # Map negative differences to 1/9-1 scale
                        ahp_value = 1 + 8 * abs(diff)
                        matrix[i, j] = max(1/9.0, min(1.0, 1/ahp_value))
        
        return matrix
    
    def _generate_matrix_preferences(
        self, 
        level_config: Dict[str, Any], 
        stakeholder_preferences: Dict[str, Dict[str, float]]
    ) -> np.ndarray:
        """Generate comparison matrix from stakeholder preferences."""
        items = level_config['items']
        n = len(items)
        matrix = np.eye(n)
        
        # Aggregate stakeholder preferences
        aggregated_preferences = {}
        
        # Get item names
        if level_config['type'] == 'categories':
            item_names = items
        else:
            item_names = [item.get('name') if isinstance(item, dict) else str(item) for item in items]
        
        # Aggregate preferences across stakeholders
        for item_name in item_names:
            preferences = []
            for stakeholder_id, prefs in stakeholder_preferences.items():
                if item_name in prefs:
                    preferences.append(prefs[item_name])
            
            if preferences:
                # Use geometric mean for aggregation
                aggregated_preferences[item_name] = np.exp(np.mean(np.log(np.array(preferences) + 1e-10)))
            else:
                aggregated_preferences[item_name] = 1.0
        
        # Create comparison matrix from aggregated preferences
        for i, name_i in enumerate(item_names):
            for j, name_j in enumerate(item_names):
                if i != j:
                    pref_i = aggregated_preferences.get(name_i, 1.0)
                    pref_j = aggregated_preferences.get(name_j, 1.0)
                    
                    if pref_j > 0:
                        ratio = pref_i / pref_j
                        matrix[i, j] = min(9.0, max(1/9.0, ratio))
        
        return matrix
    
    def _generate_matrix_hybrid(
        self, 
        level_config: Dict[str, Any], 
        qvf_scores: List[Dict[str, Any]],
        stakeholder_preferences: Optional[Dict[str, Dict[str, float]]]
    ) -> np.ndarray:
        """Generate comparison matrix using hybrid approach."""
        # Start with score-based matrix
        score_matrix = self._generate_matrix_logarithmic(level_config, qvf_scores)
        
        # If stakeholder preferences available, blend with preference matrix
        if stakeholder_preferences:
            pref_matrix = self._generate_matrix_preferences(level_config, stakeholder_preferences)
            
            # Blend matrices using geometric mean
            n = score_matrix.shape[0]
            hybrid_matrix = np.eye(n)
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        score_value = score_matrix[i, j]
                        pref_value = pref_matrix[i, j]
                        
                        # Geometric mean of the two values
                        hybrid_matrix[i, j] = np.sqrt(score_value * pref_value)
        else:
            hybrid_matrix = score_matrix
        
        return hybrid_matrix
    
    def _validate_and_adjust_matrix(self, matrix: np.ndarray) -> np.ndarray:
        """Validate and adjust comparison matrix for AHP requirements."""
        n = matrix.shape[0]
        adjusted_matrix = matrix.copy()
        
        # Ensure diagonal is 1
        np.fill_diagonal(adjusted_matrix, 1.0)
        
        # Ensure reciprocal property
        for i in range(n):
            for j in range(n):
                if i != j and adjusted_matrix[j, i] != 0:
                    adjusted_matrix[j, i] = 1.0 / adjusted_matrix[i, j]
        
        # Check for extreme ratios and adjust
        for i in range(n):
            for j in range(n):
                if i != j:
                    if adjusted_matrix[i, j] > self.config.extreme_ratio_threshold:
                        adjusted_matrix[i, j] = self.config.extreme_ratio_threshold
                        adjusted_matrix[j, i] = 1.0 / self.config.extreme_ratio_threshold
                    elif adjusted_matrix[i, j] < 1.0 / self.config.extreme_ratio_threshold:
                        adjusted_matrix[i, j] = 1.0 / self.config.extreme_ratio_threshold
                        adjusted_matrix[j, i] = self.config.extreme_ratio_threshold
        
        # Ensure positive values
        adjusted_matrix = np.abs(adjusted_matrix)
        np.fill_diagonal(adjusted_matrix, 1.0)
        
        return adjusted_matrix
    
    def _calculate_global_weights(
        self, 
        ahp_engines: Dict[str, AHPEngine],
        hierarchy_structure: Dict[str, Dict[str, Any]]
    ) -> np.ndarray:
        """Calculate global weights across hierarchy levels."""
        # If only one level, return its weights directly
        if len(ahp_engines) == 1:
            engine = list(ahp_engines.values())[0]
            return engine.weights if engine.weights is not None else np.array([])
        
        # Multi-level hierarchy: combine weights
        global_weights = []
        category_weights = None
        
        # Get category-level weights if available
        if HierarchyLevel.CATEGORIES.value in ahp_engines:
            category_engine = ahp_engines[HierarchyLevel.CATEGORIES.value]
            category_weights = category_engine.weights
            category_names = [c.name for c in category_engine.config.criteria]
        
        # Combine criteria weights from each category
        for level_name, level_config in hierarchy_structure.items():
            if level_config['type'] == 'criteria':
                if level_name in ahp_engines:
                    criteria_engine = ahp_engines[level_name]
                    criteria_weights = criteria_engine.weights
                    
                    if category_weights is not None:
                        # Find category weight for this level
                        category = level_config.get('category', 'default')
                        try:
                            category_idx = category_names.index(category)
                            category_weight = category_weights[category_idx]
                        except (ValueError, IndexError):
                            category_weight = 1.0 / len(category_names)  # Equal weight fallback
                        
                        # Multiply criteria weights by category weight
                        weighted_criteria = criteria_weights * category_weight
                        global_weights.extend(weighted_criteria)
                    else:
                        # No category level, use criteria weights directly
                        global_weights.extend(criteria_weights)
        
        return np.array(global_weights) if global_weights else np.array([])
    
    def _rank_work_items_with_global_weights(
        self,
        work_items: List[ADOWorkItem],
        qvf_scores: List[Dict[str, Any]],
        global_weights: np.ndarray,
        ahp_engines: Dict[str, AHPEngine]
    ) -> List[Tuple[int, float, Dict[str, float]]]:
        """Rank work items using calculated global weights."""
        if len(global_weights) == 0:
            logger.warning("No global weights available for ranking")
            return [(item.work_item_id, 0.0, {}) for item in work_items]
        
        # Create mapping from QVF scores to work item rankings
        work_item_rankings = []
        
        # Get criteria names from AHP engines
        all_criteria = []
        for engine in ahp_engines.values():
            for criterion in engine.config.criteria:
                if criterion.name not in all_criteria:
                    all_criteria.append(criterion.name)
        
        # Ensure we have enough weights for all criteria
        if len(global_weights) < len(all_criteria):
            logger.warning(f"Global weights ({len(global_weights)}) < criteria count ({len(all_criteria)})")
            # Pad with zeros or adjust
            padded_weights = np.zeros(len(all_criteria))
            padded_weights[:len(global_weights)] = global_weights
            global_weights = padded_weights
        
        # Calculate weighted scores for each work item
        for work_item in work_items:
            work_item_id = work_item.work_item_id
            
            # Find QVF scores for this work item
            work_item_qvf = None
            for qvf_entry in qvf_scores:
                if qvf_entry.get('work_item_id') == work_item_id:
                    work_item_qvf = qvf_entry
                    break
            
            if work_item_qvf is None:
                work_item_rankings.append((work_item_id, 0.0, {}))
                continue
            
            # Get criterion scores
            criterion_scores = work_item_qvf.get('criterion_scores', {})
            
            # Calculate weighted total score
            total_score = 0.0
            detailed_scores = {}
            
            for i, criterion_name in enumerate(all_criteria):
                if i < len(global_weights):
                    criterion_score = criterion_scores.get(criterion_name, 0.0)
                    weighted_score = criterion_score * global_weights[i]
                    total_score += weighted_score
                    detailed_scores[criterion_name] = weighted_score
            
            work_item_rankings.append((work_item_id, total_score, detailed_scores))
        
        # Sort by total score descending
        work_item_rankings.sort(key=lambda x: x[1], reverse=True)
        
        return work_item_rankings
    
    def _calculate_integration_quality(
        self, 
        validation_results: Dict[str, AHPValidationResult],
        global_weights: np.ndarray
    ) -> float:
        """Calculate overall integration quality score."""
        quality_components = []
        
        # Average validation quality scores
        if validation_results:
            avg_quality = np.mean([v.quality_score for v in validation_results.values()])
            quality_components.append(avg_quality * 0.4)
        
        # Consistency quality (all matrices should be consistent)
        if validation_results:
            consistency_quality = np.mean([1.0 if v.is_valid else 0.0 for v in validation_results.values()])
            quality_components.append(consistency_quality * 0.3)
        
        # Weight distribution quality
        if len(global_weights) > 0:
            # Prefer balanced but not uniform distributions
            entropy = -np.sum(global_weights * np.log(global_weights + 1e-10))
            max_entropy = np.log(len(global_weights))
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
            
            # Penalty for extremely unbalanced weights
            max_weight = np.max(global_weights)
            balance_penalty = 0.0 if max_weight < 0.8 else (max_weight - 0.8) * 5
            
            weight_quality = max(0.0, normalized_entropy - balance_penalty)
            quality_components.append(weight_quality * 0.3)
        
        # Overall quality score
        return np.mean(quality_components) if quality_components else 0.0
    
    def _reconcile_qvf_ahp_scores(
        self, 
        qvf_scores: List[Dict[str, Any]],
        ahp_rankings: List[Tuple[int, float, Dict[str, float]]]
    ) -> Dict[str, float]:
        """Compare QVF and AHP scoring results for validation."""
        if not qvf_scores or not ahp_rankings:
            return {'correlation': 0.0, 'rank_agreement': 0.0}
        
        # Create mappings
        qvf_score_map = {entry['work_item_id']: entry['total_score'] for entry in qvf_scores}
        ahp_score_map = {entry[0]: entry[1] for entry in ahp_rankings}
        
        # Get common work items
        common_items = set(qvf_score_map.keys()).intersection(set(ahp_score_map.keys()))
        
        if len(common_items) < 2:
            return {'correlation': 0.0, 'rank_agreement': 0.0}
        
        # Calculate score correlation
        qvf_values = [qvf_score_map[item] for item in common_items]
        ahp_values = [ahp_score_map[item] for item in common_items]
        
        try:
            correlation = np.corrcoef(qvf_values, ahp_values)[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
        except:
            correlation = 0.0
        
        # Calculate rank agreement (top 10)
        qvf_sorted = sorted(common_items, key=lambda x: qvf_score_map[x], reverse=True)
        ahp_sorted = sorted(common_items, key=lambda x: ahp_score_map[x], reverse=True)
        
        top_n = min(10, len(common_items))
        qvf_top = set(qvf_sorted[:top_n])
        ahp_top = set(ahp_sorted[:top_n])
        
        rank_agreement = len(qvf_top.intersection(ahp_top)) / top_n
        
        return {
            'correlation': float(correlation),
            'rank_agreement': float(rank_agreement),
            'common_items': len(common_items)
        }
    
    def _calculate_ranking_stability(
        self, 
        rankings: List[Tuple[int, float, Dict[str, float]]],
        ahp_engines: Dict[str, AHPEngine]
    ) -> Dict[str, float]:
        """Calculate ranking stability metrics."""
        stability_metrics = {}
        
        # Score distribution stability
        scores = [r[1] for r in rankings]
        if scores:
            stability_metrics['score_variance'] = float(np.var(scores))
            stability_metrics['score_range'] = float(np.max(scores) - np.min(scores))
            stability_metrics['coefficient_of_variation'] = float(np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0.0
        
        # AHP consistency as stability indicator
        consistency_ratios = [engine.consistency_ratio for engine in ahp_engines.values() if engine.consistency_ratio is not None]
        if consistency_ratios:
            stability_metrics['average_consistency_ratio'] = float(np.mean(consistency_ratios))
            stability_metrics['max_consistency_ratio'] = float(np.max(consistency_ratios))
            stability_metrics['all_consistent'] = all(cr <= 0.10 for cr in consistency_ratios)
        
        return stability_metrics
    
    def _perform_integrated_sensitivity_analysis(
        self,
        ahp_engines: Dict[str, AHPEngine],
        work_items: List[ADOWorkItem],
        qvf_scores: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive sensitivity analysis across the integrated system."""
        sensitivity_results = {}
        
        # Perform sensitivity analysis for each AHP engine
        for level_name, engine in ahp_engines.items():
            if engine.weights is not None and len(engine.weights) > 1:
                try:
                    # Create work items in format expected by AHP engine
                    ahp_work_items = []
                    for work_item in work_items:
                        # Find corresponding QVF scores
                        work_item_qvf = None
                        for qvf_entry in qvf_scores:
                            if qvf_entry.get('work_item_id') == work_item.work_item_id:
                                work_item_qvf = qvf_entry
                                break
                        
                        if work_item_qvf:
                            # Convert to format expected by AHP
                            ahp_item = {}
                            criterion_scores = work_item_qvf.get('criterion_scores', {})
                            
                            for criterion in engine.config.criteria:
                                ahp_item[criterion.data_source] = criterion_scores.get(criterion.name, 0.0)
                            
                            ahp_work_items.append(ahp_item)
                    
                    if ahp_work_items:
                        level_sensitivity = engine.perform_advanced_sensitivity_analysis(
                            ahp_work_items, weight_perturbation=0.1
                        )
                        sensitivity_results[level_name] = level_sensitivity
                        
                except Exception as e:
                    logger.warning(f"Sensitivity analysis failed for level {level_name}: {e}")
                    continue
        
        return sensitivity_results
    
    def _perform_group_analysis(
        self,
        stakeholder_preferences: Dict[str, Dict[str, float]],
        hierarchy_structure: Dict[str, Dict[str, Any]]
    ) -> GroupAHPResult:
        """Perform group AHP analysis using stakeholder inputs."""
        # Create participant matrices for the main criteria level
        participant_matrices = {}
        
        # Find the main criteria level
        criteria_level = None
        for level_name, level_config in hierarchy_structure.items():
            if level_config['type'] == 'criteria':
                criteria_level = level_config
                break
        
        if not criteria_level:
            raise QVFAHPIntegrationError("No criteria level found for group analysis")
        
        # Generate comparison matrix for each stakeholder
        for stakeholder_id, preferences in stakeholder_preferences.items():
            try:
                matrix = self._generate_matrix_preferences(criteria_level, {stakeholder_id: preferences})
                participant_matrices[stakeholder_id] = matrix
            except Exception as e:
                logger.warning(f"Failed to create matrix for stakeholder {stakeholder_id}: {e}")
        
        # Use AHP engine for group analysis
        if participant_matrices:
            # Create temporary AHP engine for group analysis
            ahp_config = self._create_ahp_configuration_for_level(criteria_level)
            group_engine = AHPEngine(ahp_config, enable_advanced_features=True)
            
            return group_engine.perform_group_ahp_analysis(participant_matrices)
        
        raise QVFAHPIntegrationError("No valid participant matrices for group analysis")
    
    def export_integration_results(self, result: IntegrationResult) -> Dict[str, Any]:
        """Export integration results in comprehensive format."""
        export_data = {
            'metadata': {
                'integration_timestamp': result.integration_timestamp.isoformat(),
                'conversion_method': result.conversion_method.value,
                'consistency_achieved': result.consistency_achieved,
                'final_consistency_ratio': result.final_consistency_ratio,
                'integration_quality_score': result.integration_quality_score
            },
            'hierarchy': {
                'levels': list(result.ahp_engines.keys()),
                'level_weights': {level: weights.tolist() for level, weights in result.level_weights.items()},
                'global_weights': result.global_weights.tolist()
            },
            'validation': {
                level: {
                    'is_valid': validation.is_valid,
                    'consistency_ratio': validation.consistency_ratio,
                    'quality_score': validation.quality_score,
                    'issues': validation.issues,
                    'suggestions': validation.suggestions
                } for level, validation in result.validation_results.items()
            },
            'rankings': {
                'work_items': [
                    {
                        'work_item_id': item_id,
                        'score': score,
                        'rank': rank + 1,
                        'detailed_scores': detailed
                    }
                    for rank, (item_id, score, detailed) in enumerate(result.work_item_rankings)
                ],
                'stability_metrics': result.ranking_stability
            },
            'quality_assessment': {
                'score_reconciliation': result.score_reconciliation,
                'integration_quality': result.integration_quality_score
            }
        }
        
        # Add optional advanced results
        if result.sensitivity_analysis:
            export_data['sensitivity_analysis'] = result.sensitivity_analysis
        
        if result.group_results:
            export_data['group_analysis'] = {
                'consensus_ratio': result.group_results.consensus_ratio,
                'participant_consistency': result.group_results.participant_consistency,
                'group_weights': result.group_results.group_weights.tolist()
            }
        
        return export_data


# Factory functions for common integration configurations
def create_balanced_integration_config() -> IntegrationConfiguration:
    """Create balanced configuration for general use."""
    return IntegrationConfiguration(
        conversion_method=ConversionMethod.HYBRID_APPROACH,
        consistency_threshold=0.10,
        auto_improve_consistency=True,
        enable_multi_level_hierarchy=True,
        perform_sensitivity_analysis=True
    )


def create_strict_consistency_config() -> IntegrationConfiguration:
    """Create configuration with strict consistency requirements."""
    return IntegrationConfiguration(
        conversion_method=ConversionMethod.LOGARITHMIC_SCALE,
        consistency_threshold=0.05,
        auto_improve_consistency=True,
        max_improvement_iterations=20,
        enable_multi_level_hierarchy=True,
        perform_sensitivity_analysis=True
    )


def create_stakeholder_focused_config() -> IntegrationConfiguration:
    """Create configuration emphasizing stakeholder preferences."""
    return IntegrationConfiguration(
        conversion_method=ConversionMethod.PREFERENCE_ELICITATION,
        consistency_threshold=0.15,  # More lenient for human judgments
        enable_group_aggregation=True,
        group_method="geometric_mean",
        perform_sensitivity_analysis=True
    )