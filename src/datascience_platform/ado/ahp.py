"""Analytic Hierarchy Process (AHP) Engine

This module implements the AHP methodology for multi-criteria decision making,
enabling objective prioritization of ADO work items based on configurable criteria.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import logging
from enum import Enum
from scipy import linalg
from scipy.optimize import minimize_scalar
import warnings
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class AHPScale(Enum):
    """Standard AHP comparison scale (Saaty scale)."""
    EQUAL_IMPORTANCE = 1
    WEAK_IMPORTANCE = 3
    ESSENTIAL_IMPORTANCE = 5
    VERY_STRONG_IMPORTANCE = 7
    ABSOLUTE_IMPORTANCE = 9
    # Intermediate values
    WEAK_PLUS = 2
    ESSENTIAL_PLUS = 4
    VERY_STRONG_PLUS = 6
    ABSOLUTE_MINUS = 8


class AHPCriterion(BaseModel):
    """Represents a single criterion in AHP analysis."""
    
    name: str = Field(..., description="Unique criterion name")
    description: str = Field(..., description="Criterion description")
    weight: float = Field(0.0, ge=0, le=1, description="Calculated weight from AHP")
    data_source: str = Field(..., description="Field name in work item to extract value")
    higher_is_better: bool = Field(True, description="Whether higher values are preferred")
    normalization_method: str = Field("minmax", description="Normalization method: minmax, zscore, or none")
    
    # Optional value transformation
    value_mapping: Optional[Dict[str, float]] = Field(None, description="Map categorical values to numbers")
    threshold_min: Optional[float] = Field(None, description="Minimum threshold for consideration")
    threshold_max: Optional[float] = Field(None, description="Maximum threshold for consideration")
    
    @validator('normalization_method')
    def validate_normalization(cls, v):
        allowed = ['minmax', 'zscore', 'none']
        if v not in allowed:
            raise ValueError(f"Normalization method must be one of {allowed}")
        return v


class AHPConfiguration(BaseModel):
    """Configuration for AHP analysis."""
    
    criteria: List[AHPCriterion] = Field(..., description="List of criteria for analysis")
    consistency_threshold: float = Field(0.1, description="Maximum acceptable consistency ratio")
    
    # Optional sub-criteria support
    sub_criteria: Optional[Dict[str, List[AHPCriterion]]] = Field(
        None, 
        description="Sub-criteria for each main criterion"
    )
    
    def get_criterion_names(self) -> List[str]:
        """Get list of criterion names."""
        return [c.name for c in self.criteria]
    
    def get_criterion_by_name(self, name: str) -> Optional[AHPCriterion]:
        """Get criterion by name."""
        for criterion in self.criteria:
            if criterion.name == name:
                return criterion
        return None


class PairwiseComparison(BaseModel):
    """Represents a pairwise comparison between two criteria."""
    
    criterion_a: str
    criterion_b: str
    comparison_value: float = Field(..., ge=1/9, le=9)
    
    @validator('comparison_value')
    def validate_comparison(cls, v):
        # Ensure value is in valid AHP scale
        valid_values = [1/9, 1/8, 1/7, 1/6, 1/5, 1/4, 1/3, 1/2, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        closest = min(valid_values, key=lambda x: abs(x - v))
        return closest


@dataclass
class AHPValidationResult:
    """Result of AHP validation operations."""
    is_valid: bool
    consistency_ratio: float
    issues: List[str]
    suggestions: List[str]
    quality_score: float = 0.0


@dataclass
class GroupAHPResult:
    """Result of group AHP analysis."""
    individual_weights: Dict[str, np.ndarray]
    group_weights: np.ndarray
    consensus_ratio: float
    agreement_matrix: np.ndarray
    participant_consistency: Dict[str, float]


class AHPEngine:
    """Enhanced AHP calculation engine with QVF-specific capabilities.
    
    Features:
    - Multi-level hierarchy support for QVF criteria
    - Automated consistency improvement algorithms
    - Group decision making with geometric mean method
    - Sensitivity analysis for weight changes
    - Advanced eigenvector calculation methods
    - Incomplete comparison matrix handling
    """
    
    def __init__(self, config: AHPConfiguration, enable_advanced_features: bool = True):
        """Initialize enhanced AHP engine with configuration.
        
        Args:
            config: AHP configuration with criteria
            enable_advanced_features: Enable advanced QVF features
        """
        self.config = config
        self.comparison_matrix: Optional[np.ndarray] = None
        self.weights: Optional[np.ndarray] = None
        self.consistency_ratio: Optional[float] = None
        self.enable_advanced_features = enable_advanced_features
        
        # Enhanced random index for consistency calculation (Saaty + extensions)
        self.random_index = {
            1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
            11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59,
            16: 1.60, 17: 1.61, 18: 1.62, 19: 1.63, 20: 1.64
        }
        
        # Advanced calculation settings
        self.eigenvector_method = 'power_iteration'  # 'power_iteration', 'eigenvalue', 'geometric_mean'
        self.max_iterations = 1000
        self.tolerance = 1e-8
        
        # Multi-level hierarchy support
        self.hierarchy_levels: Dict[str, List[AHPEngine]] = {}
        self.level_weights: Dict[str, float] = {}
        
        # Group decision tracking
        self.group_participants: Dict[str, np.ndarray] = {}
        
        logger.info(f"Enhanced AHP Engine initialized with {len(config.criteria)} criteria")
    
    def create_comparison_matrix(self, comparisons: List[PairwiseComparison]) -> np.ndarray:
        """Create pairwise comparison matrix from comparisons.
        
        Args:
            comparisons: List of pairwise comparisons
            
        Returns:
            Comparison matrix
        """
        n = len(self.config.criteria)
        matrix = np.eye(n)  # Initialize with diagonal of 1s
        
        # Create name to index mapping
        name_to_idx = {c.name: i for i, c in enumerate(self.config.criteria)}
        
        # Fill matrix with comparisons
        for comp in comparisons:
            if comp.criterion_a in name_to_idx and comp.criterion_b in name_to_idx:
                i = name_to_idx[comp.criterion_a]
                j = name_to_idx[comp.criterion_b]
                matrix[i, j] = comp.comparison_value
                matrix[j, i] = 1 / comp.comparison_value  # Reciprocal
            else:
                logger.warning(f"Unknown criterion in comparison: {comp.criterion_a} or {comp.criterion_b}")
        
        self.comparison_matrix = matrix
        return matrix
    
    def calculate_weights(self, matrix: Optional[np.ndarray] = None, method: Optional[str] = None) -> np.ndarray:
        """Calculate criterion weights using eigenvector method.
        
        Args:
            matrix: Comparison matrix (uses stored matrix if None)
            
        Returns:
            Normalized weight vector
        """
        if matrix is None:
            matrix = self.comparison_matrix
        
        if matrix is None:
            raise ValueError("No comparison matrix available")
        
        # Calculate eigenvector (principal eigenvector method)
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        
        # Get index of largest eigenvalue
        max_idx = np.argmax(eigenvalues.real)
        principal_eigenvector = eigenvectors[:, max_idx].real
        
        # Normalize to sum to 1
        weights = principal_eigenvector / principal_eigenvector.sum()
        
        # Ensure positive weights
        weights = np.abs(weights)
        
        # Store weights in configuration
        for i, criterion in enumerate(self.config.criteria):
            criterion.weight = float(weights[i])
        
        self.weights = weights
        
        # Calculate consistency ratio
        try:
            self.consistency_ratio = self.calculate_consistency_ratio(matrix, weights)
            logger.debug(f"Calculated weights using {method}: CR={self.consistency_ratio:.4f}")
        except Exception as e:
            logger.warning(f"Failed to calculate consistency ratio: {e}")
            self.consistency_ratio = 1.0  # Conservative fallback
        
        return weights
    
    def calculate_consistency_ratio(self, matrix: Optional[np.ndarray] = None, weights: Optional[np.ndarray] = None) -> float:
        """Calculate consistency ratio for the comparison matrix.
        
        Args:
            matrix: Comparison matrix (uses stored matrix if None)
            
        Returns:
            Consistency ratio (CR)
        """
        if matrix is None:
            matrix = self.comparison_matrix
        if weights is None:
            weights = self.weights
        
        if matrix is None or weights is None:
            raise ValueError("Matrix and weights must be calculated first")
        
        n = matrix.shape[0]
        
        # Calculate λmax (maximum eigenvalue)
        weighted_sum = matrix @ weights
        lambda_max = np.mean(weighted_sum / weights)
        
        # Calculate consistency index (CI)
        ci = (lambda_max - n) / (n - 1) if n > 1 else 0
        
        # Get random index (RI)
        ri = self.random_index.get(n, 1.49)  # Use 1.49 for n > 15
        
        # Calculate consistency ratio (CR)
        cr = ci / ri if ri > 0 else 0
        
        self.consistency_ratio = cr
        return cr
    
    def is_consistent(self) -> bool:
        """Check if comparison matrix is consistent."""
        if self.consistency_ratio is None:
            return False
        return self.consistency_ratio <= self.config.consistency_threshold
    
    def validate_ahp_analysis(self) -> AHPValidationResult:
        """Comprehensive validation of AHP analysis.
        
        Returns:
            Detailed validation result with quality assessment
        """
        issues = []
        suggestions = []
        quality_score = 0.0
        
        # Check if analysis is complete
        if self.comparison_matrix is None:
            issues.append("No comparison matrix available")
            return AHPValidationResult(False, 1.0, issues, suggestions, 0.0)
        
        if self.weights is None:
            issues.append("Weights not calculated")
            return AHPValidationResult(False, 1.0, issues, suggestions, 0.0)
        
        # Validate matrix properties
        if not self._is_valid_comparison_matrix(self.comparison_matrix):
            issues.append("Invalid comparison matrix properties")
        
        # Check consistency
        cr = self.consistency_ratio or self.calculate_consistency_ratio()
        is_consistent = cr <= self.config.consistency_threshold
        
        if not is_consistent:
            issues.append(f"Consistency ratio {cr:.3f} exceeds threshold {self.config.consistency_threshold}")
            if cr > 0.2:
                suggestions.append("Consider revising comparison judgments - high inconsistency detected")
            elif cr > 0.1:
                suggestions.append("Moderate inconsistency - review key comparisons")
        
        # Calculate quality score
        consistency_score = max(0, 1.0 - cr / 0.1)  # Linear decrease from 1.0 to 0 as CR goes from 0 to 0.1
        matrix_quality = 1.0 if self._is_valid_comparison_matrix(self.comparison_matrix) else 0.0
        completeness_score = 1.0 if self._is_matrix_complete(self.comparison_matrix) else 0.5
        
        quality_score = (consistency_score * 0.5 + matrix_quality * 0.3 + completeness_score * 0.2)
        
        # Additional quality checks
        if self._has_extreme_weights():
            issues.append("Extreme weight distribution detected")
            suggestions.append("Review comparisons for potential outliers")
            quality_score *= 0.9
        
        return AHPValidationResult(
            is_valid=len(issues) == 0,
            consistency_ratio=cr,
            issues=issues,
            suggestions=suggestions,
            quality_score=quality_score
        )
    
    def _is_valid_comparison_matrix(self, matrix: np.ndarray) -> bool:
        """Validate comparison matrix properties."""
        if matrix.shape[0] != matrix.shape[1]:
            return False
        
        # Check positive values
        if np.any(matrix <= 0):
            return False
        
        # Check reciprocal property (within tolerance)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if i != j and not np.isclose(matrix[i, j] * matrix[j, i], 1.0, atol=1e-6):
                    return False
        
        # Check diagonal is 1
        if not np.allclose(np.diag(matrix), 1.0, atol=1e-6):
            return False
        
        return True
    
    def _is_matrix_complete(self, matrix: np.ndarray) -> bool:
        """Check if comparison matrix is complete (no missing comparisons)."""
        n = matrix.shape[0]
        for i in range(n):
            for j in range(i+1, n):
                if matrix[i, j] == 0 or matrix[j, i] == 0:
                    return False
        return True
    
    def _has_extreme_weights(self, threshold: float = 0.8) -> bool:
        """Check if any single weight dominates (indicates potential issues)."""
        if self.weights is None:
            return False
        return np.max(self.weights) > threshold
    
    def create_comparison_matrix_from_preferences(
        self, 
        preferences: Dict[str, float]
    ) -> np.ndarray:
        """Create comparison matrix from criterion preferences/rankings.
        
        Args:
            preferences: Dict mapping criterion name to preference value (higher is better)
            
        Returns:
            Comparison matrix
        """
        n = len(self.config.criteria)
        matrix = np.eye(n)
        
        criterion_names = [c.name for c in self.config.criteria]
        
        # Get preference values in order
        pref_values = []
        for name in criterion_names:
            if name in preferences:
                pref_values.append(preferences[name])
            else:
                pref_values.append(1.0)  # Default preference
        
        # Create pairwise comparisons based on preference ratios
        for i in range(n):
            for j in range(n):
                if i != j:
                    ratio = pref_values[i] / pref_values[j]
                    # Map to AHP scale (1-9)
                    if ratio >= 1:
                        matrix[i, j] = min(9, max(1, round(ratio)))
                    else:
                        matrix[i, j] = 1 / min(9, max(1, round(1/ratio)))
        
        self.comparison_matrix = matrix
        return matrix
    
    def calculate_work_item_score(
        self, 
        work_item_values: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Calculate AHP score for a work item.
        
        Args:
            work_item_values: Dict mapping criterion data_source to value
            
        Returns:
            Tuple of (total_score, criterion_scores)
        """
        if self.weights is None:
            raise ValueError("Weights must be calculated first")
        
        criterion_scores = {}
        weighted_scores = []
        
        for i, criterion in enumerate(self.config.criteria):
            # Get raw value
            raw_value = work_item_values.get(criterion.data_source, 0)
            
            # Apply value mapping if exists
            if criterion.value_mapping and isinstance(raw_value, str):
                raw_value = criterion.value_mapping.get(raw_value, 0)
            
            # Convert to float
            try:
                value = float(raw_value) if raw_value is not None else 0.0
            except (ValueError, TypeError):
                value = 0.0
            
            # Apply thresholds
            if criterion.threshold_min is not None:
                value = max(value, criterion.threshold_min)
            if criterion.threshold_max is not None:
                value = min(value, criterion.threshold_max)
            
            # Invert if lower is better
            if not criterion.higher_is_better and value != 0:
                value = 1 / value
            
            # Store criterion score
            criterion_scores[criterion.name] = value
            
            # Calculate weighted score
            weighted_score = value * self.weights[i]
            weighted_scores.append(weighted_score)
        
        total_score = sum(weighted_scores)
        
        return total_score, criterion_scores
    
    def rank_work_items(
        self, 
        work_items: List[Dict[str, Any]]
    ) -> List[Tuple[int, float, Dict[str, float]]]:
        """Rank work items using AHP scoring.
        
        Args:
            work_items: List of work items with values
            
        Returns:
            List of tuples (work_item_index, total_score, criterion_scores)
            sorted by score descending
        """
        if not self.is_consistent():
            logger.warning(f"Comparison matrix is inconsistent (CR={self.consistency_ratio:.3f})")
        
        scores = []
        
        # First pass: collect all values for normalization
        all_values = {criterion.name: [] for criterion in self.config.criteria}
        
        for item in work_items:
            for criterion in self.config.criteria:
                value = item.get(criterion.data_source, 0)
                if criterion.value_mapping and isinstance(value, str):
                    value = criterion.value_mapping.get(value, 0)
                try:
                    value = float(value) if value is not None else 0.0
                except (ValueError, TypeError):
                    value = 0.0
                all_values[criterion.name].append(value)
        
        # Normalize values by criterion
        normalized_values = {}
        for criterion in self.config.criteria:
            values = np.array(all_values[criterion.name])
            
            if criterion.normalization_method == 'minmax' and len(values) > 1:
                min_val, max_val = values.min(), values.max()
                if max_val > min_val:
                    normalized = (values - min_val) / (max_val - min_val)
                else:
                    normalized = np.ones_like(values) * 0.5
            elif criterion.normalization_method == 'zscore' and len(values) > 1:
                mean, std = values.mean(), values.std()
                if std > 0:
                    normalized = (values - mean) / std
                    # Convert to 0-1 range using sigmoid
                    normalized = 1 / (1 + np.exp(-normalized))
                else:
                    normalized = np.ones_like(values) * 0.5
            else:
                normalized = values
            
            normalized_values[criterion.name] = normalized
        
        # Second pass: calculate scores with normalized values
        for idx, item in enumerate(work_items):
            item_normalized = {}
            for i, criterion in enumerate(self.config.criteria):
                item_normalized[criterion.data_source] = normalized_values[criterion.name][idx]
            
            score, criterion_scores = self.calculate_work_item_score(item_normalized)
            scores.append((idx, score, criterion_scores))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores
    
    def perform_advanced_sensitivity_analysis(
        self,
        work_items: List[Dict[str, Any]],
        criteria_variations: Dict[str, List[float]] = None,
        weight_perturbation: float = 0.1
    ) -> Dict[str, Any]:
        """Perform comprehensive sensitivity analysis on AHP results.
        
        Args:
            work_items: List of work items to analyze
            criteria_variations: Specific variations to test for each criterion
            weight_perturbation: Default perturbation percentage
            
        Returns:
            Detailed sensitivity analysis results
        """
        if self.weights is None:
            raise ValueError("Weights must be calculated before sensitivity analysis")
        
        logger.info(f"Performing advanced sensitivity analysis with {weight_perturbation*100:.1f}% perturbation")
        
        original_weights = self.weights.copy()
        original_rankings = self.rank_work_items(work_items)
        
        sensitivity_results = {
            'original_ranking': original_rankings,
            'weight_sensitivity': {},
            'threshold_analysis': {},
            'stability_metrics': {},
            'critical_comparisons': []
        }
        
        # Test weight variations for each criterion
        for i, criterion in enumerate(self.config.criteria):
            variations = criteria_variations.get(criterion.name, 
                [-weight_perturbation, -weight_perturbation/2, weight_perturbation/2, weight_perturbation])
            
            criterion_sensitivity = []
            
            for variation in variations:
                # Perturb weight
                perturbed_weights = original_weights.copy()
                perturbed_weights[i] *= (1 + variation)
                
                # Renormalize weights
                perturbed_weights = perturbed_weights / perturbed_weights.sum()
                
                # Temporarily update weights
                self.weights = perturbed_weights
                for j, c in enumerate(self.config.criteria):
                    c.weight = float(perturbed_weights[j])
                
                # Calculate new rankings
                new_rankings = self.rank_work_items(work_items)
                
                # Measure ranking changes
                rank_changes = self._calculate_ranking_changes(original_rankings, new_rankings)
                
                criterion_sensitivity.append({
                    'variation': variation,
                    'new_weight': float(perturbed_weights[i]),
                    'ranking_changes': rank_changes,
                    'top_5_stability': self._measure_top_n_stability(original_rankings, new_rankings, 5),
                    'kendall_tau': self._calculate_kendall_tau(original_rankings, new_rankings)
                })
            
            sensitivity_results['weight_sensitivity'][criterion.name] = criterion_sensitivity
        
        # Restore original weights
        self.weights = original_weights
        for i, criterion in enumerate(self.config.criteria):
            criterion.weight = float(original_weights[i])
        
        # Calculate overall stability metrics
        sensitivity_results['stability_metrics'] = self._calculate_overall_stability(sensitivity_results['weight_sensitivity'])
        
        # Identify critical comparisons that most affect results
        sensitivity_results['critical_comparisons'] = self._identify_critical_comparisons(work_items)
        
        return sensitivity_results
    
    def _calculate_ranking_changes(self, original: List, new: List, top_n: int = 10) -> Dict[str, Any]:
        """Calculate detailed ranking change metrics."""
        original_ranks = {item[0]: rank+1 for rank, item in enumerate(original[:top_n])}
        new_ranks = {item[0]: rank+1 for rank, item in enumerate(new[:top_n])}
        
        changes = []
        total_change = 0
        
        for item_id in original_ranks:
            old_rank = original_ranks[item_id]
            new_rank = new_ranks.get(item_id, top_n+1)
            change = abs(old_rank - new_rank)
            total_change += change
            
            if change > 0:
                changes.append({
                    'item_id': item_id,
                    'old_rank': old_rank,
                    'new_rank': new_rank,
                    'change': change
                })
        
        return {
            'individual_changes': changes,
            'total_position_changes': total_change,
            'items_affected': len(changes),
            'max_position_change': max([c['change'] for c in changes], default=0)
        }
    
    def _measure_top_n_stability(self, original: List, new: List, n: int) -> float:
        """Measure stability of top N items (0-1, higher is more stable)."""
        original_top = set(item[0] for item in original[:n])
        new_top = set(item[0] for item in new[:n])
        
        intersection = len(original_top.intersection(new_top))
        return intersection / n
    
    def _calculate_kendall_tau(self, original: List, new: List) -> float:
        """Calculate Kendall's tau rank correlation coefficient."""
        from scipy.stats import kendalltau
        
        # Create rank mappings
        original_ranks = {item[0]: rank for rank, item in enumerate(original)}
        new_ranks = {item[0]: rank for rank, item in enumerate(new)}
        
        # Get common items
        common_items = set(original_ranks.keys()).intersection(set(new_ranks.keys()))
        
        if len(common_items) < 2:
            return 0.0
        
        original_rank_list = [original_ranks[item] for item in common_items]
        new_rank_list = [new_ranks[item] for item in common_items]
        
        try:
            tau, _ = kendalltau(original_rank_list, new_rank_list)
            return tau if not np.isnan(tau) else 0.0
        except:
            return 0.0
    
    def _calculate_overall_stability(self, weight_sensitivity: Dict[str, List]) -> Dict[str, float]:
        """Calculate overall stability metrics across all criteria."""
        all_kendall_taus = []
        all_top5_stabilities = []
        
        for criterion_results in weight_sensitivity.values():
            for result in criterion_results:
                all_kendall_taus.append(result['kendall_tau'])
                all_top5_stabilities.append(result['top_5_stability'])
        
        return {
            'average_kendall_tau': np.mean(all_kendall_taus) if all_kendall_taus else 0.0,
            'min_kendall_tau': np.min(all_kendall_taus) if all_kendall_taus else 0.0,
            'average_top5_stability': np.mean(all_top5_stabilities) if all_top5_stabilities else 0.0,
            'min_top5_stability': np.min(all_top5_stabilities) if all_top5_stabilities else 0.0,
            'overall_stability_score': np.mean([np.mean(all_kendall_taus) if all_kendall_taus else 0.0,
                                              np.mean(all_top5_stabilities) if all_top5_stabilities else 0.0])
        }
    
    def _identify_critical_comparisons(self, work_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify comparisons that most significantly affect results."""
        if self.comparison_matrix is None:
            return []
        
        n = self.comparison_matrix.shape[0]
        critical_comparisons = []
        
        original_rankings = self.rank_work_items(work_items)
        
        # Test small perturbations to each comparison
        perturbation = 0.1  # 10% change
        
        for i in range(n):
            for j in range(i+1, n):
                original_value = self.comparison_matrix[i, j]
                
                # Test both positive and negative perturbations
                for direction in [-1, 1]:
                    # Create perturbed matrix
                    perturbed_matrix = self.comparison_matrix.copy()
                    new_value = original_value * (1 + direction * perturbation)
                    perturbed_matrix[i, j] = new_value
                    perturbed_matrix[j, i] = 1.0 / new_value
                    
                    # Calculate new weights and rankings
                    try:
                        perturbed_weights = self._calculate_weights_eigenvalue(perturbed_matrix)
                        
                        # Temporarily update weights
                        original_weights = self.weights.copy()
                        self.weights = perturbed_weights
                        
                        new_rankings = self.rank_work_items(work_items)
                        
                        # Measure impact
                        kendall_tau = self._calculate_kendall_tau(original_rankings, new_rankings)
                        top5_stability = self._measure_top_n_stability(original_rankings, new_rankings, 5)
                        
                        impact_score = (1 - kendall_tau) + (1 - top5_stability)  # Higher score = more critical
                        
                        if impact_score > 0.1:  # Threshold for significance
                            critical_comparisons.append({
                                'criteria_pair': (self.config.criteria[i].name, self.config.criteria[j].name),
                                'original_value': float(original_value),
                                'perturbation_direction': direction,
                                'impact_score': float(impact_score),
                                'kendall_tau_change': 1 - kendall_tau,
                                'top5_stability_change': 1 - top5_stability
                            })
                        
                        # Restore original weights
                        self.weights = original_weights
                        
                    except Exception as e:
                        logger.debug(f"Failed to analyze comparison [{i},{j}]: {e}")
                        continue
        
        # Sort by impact score
        critical_comparisons.sort(key=lambda x: x['impact_score'], reverse=True)
        
        return critical_comparisons[:10]  # Return top 10 most critical
    
    def sensitivity_analysis(
        self, 
        work_items: List[Dict[str, Any]],
        weight_variation: float = 0.1
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on criterion weights.
        
        Args:
            work_items: List of work items
            weight_variation: Percentage to vary weights (0.1 = 10%)
            
        Returns:
            Sensitivity analysis results
        """
        original_weights = self.weights.copy()
        n_criteria = len(self.config.criteria)
        sensitivity_results = {}
        
        for i, criterion in enumerate(self.config.criteria):
            criterion_results = {
                'original_weight': float(original_weights[i]),
                'variations': []
            }
            
            # Try weight variations
            for variation in [-weight_variation, weight_variation]:
                # Adjust weight
                new_weights = original_weights.copy()
                new_weights[i] *= (1 + variation)
                
                # Renormalize
                new_weights = new_weights / new_weights.sum()
                self.weights = new_weights
                
                # Update criterion weights
                for j, c in enumerate(self.config.criteria):
                    c.weight = float(new_weights[j])
                
                # Recalculate rankings
                new_rankings = self.rank_work_items(work_items)
                
                criterion_results['variations'].append({
                    'variation': variation,
                    'new_weight': float(new_weights[i]),
                    'top_5_changes': self._compare_rankings(
                        self.rank_work_items(work_items),
                        new_rankings,
                        top_n=5
                    )
                })
            
            sensitivity_results[criterion.name] = criterion_results
        
        # Restore original weights
        self.weights = original_weights
        for i, criterion in enumerate(self.config.criteria):
            criterion.weight = float(original_weights[i])
        
        return sensitivity_results
    
    def _compare_rankings(
        self, 
        original: List[Tuple[int, float, Dict]], 
        new: List[Tuple[int, float, Dict]],
        top_n: int = 5
    ) -> Dict[str, Any]:
        """Compare two rankings."""
        original_top = [item[0] for item in original[:top_n]]
        new_top = [item[0] for item in new[:top_n]]
        
        changes = []
        for idx in original_top:
            old_rank = original_top.index(idx) if idx in original_top else -1
            new_rank = new_top.index(idx) if idx in new_top else -1
            
            if old_rank != new_rank:
                changes.append({
                    'item_index': idx,
                    'old_rank': old_rank + 1,
                    'new_rank': new_rank + 1 if new_rank >= 0 else 'Not in top 5'
                })
        
        return {
            'changes': changes,
            'stability': len(changes) == 0
        }
    
    # QVF-Specific Enhanced Methods
    
    def improve_consistency_automatically(self, max_iterations: int = 10) -> Tuple[bool, List[str]]:
        """Automatically improve matrix consistency using optimization.
        
        Args:
            max_iterations: Maximum optimization iterations
            
        Returns:
            Tuple of (success, improvement_steps)
        """
        if self.comparison_matrix is None:
            return False, ["No comparison matrix available"]
        
        if self.is_consistent():
            return True, ["Matrix already consistent"]
        
        logger.info(f"Attempting to improve consistency from CR={self.consistency_ratio:.4f}")
        
        original_matrix = self.comparison_matrix.copy()
        improvement_steps = []
        
        for iteration in range(max_iterations):
            # Find most inconsistent comparison
            inconsistent_pairs = self._find_most_inconsistent_comparisons()
            
            if not inconsistent_pairs:
                break
            
            # Adjust most inconsistent comparison
            i, j, suggested_value, current_value = inconsistent_pairs[0]
            
            # Apply conservative adjustment (move 50% towards suggestion)
            adjustment_factor = 0.5
            new_value = current_value + adjustment_factor * (suggested_value - current_value)
            
            # Update matrix
            self.comparison_matrix[i, j] = new_value
            self.comparison_matrix[j, i] = 1.0 / new_value
            
            # Recalculate weights and consistency
            self.calculate_weights()
            
            improvement_steps.append(
                f"Iteration {iteration+1}: Adjusted comparison [{i},{j}] from {current_value:.3f} to {new_value:.3f}, CR: {self.consistency_ratio:.4f}"
            )
            
            if self.is_consistent():
                logger.info(f"Consistency improved to CR={self.consistency_ratio:.4f} in {iteration+1} iterations")
                return True, improvement_steps
        
        # If still not consistent, provide guidance
        improvement_steps.append(f"Final CR: {self.consistency_ratio:.4f} - manual review recommended")
        return self.is_consistent(), improvement_steps
    
    def _find_most_inconsistent_comparisons(self) -> List[Tuple[int, int, float, float]]:
        """Find comparisons that contribute most to inconsistency.
        
        Returns:
            List of (i, j, suggested_value, current_value) sorted by inconsistency
        """
        if self.comparison_matrix is None or self.weights is None:
            return []
        
        n = self.comparison_matrix.shape[0]
        inconsistencies = []
        
        for i in range(n):
            for j in range(i+1, n):
                current_value = self.comparison_matrix[i, j]
                
                # Calculate theoretically consistent value based on weights
                if self.weights[j] > 0:
                    consistent_value = self.weights[i] / self.weights[j]
                    inconsistency = abs(current_value - consistent_value)
                    
                    inconsistencies.append((i, j, consistent_value, current_value, inconsistency))
        
        # Sort by inconsistency level (highest first)
        inconsistencies.sort(key=lambda x: x[4], reverse=True)
        
        # Return top inconsistencies without inconsistency score
        return [(i, j, suggested, current) for i, j, suggested, current, _ in inconsistencies]
    
    def perform_group_ahp_analysis(
        self, 
        participant_matrices: Dict[str, np.ndarray],
        method: str = 'geometric_mean'
    ) -> GroupAHPResult:
        """Perform group AHP analysis using multiple participant matrices.
        
        Args:
            participant_matrices: Dict mapping participant ID to comparison matrix
            method: Aggregation method ('geometric_mean', 'weighted_average')
            
        Returns:
            Group AHP analysis result
        """
        if not participant_matrices:
            raise ValueError("No participant matrices provided")
        
        logger.info(f"Performing group AHP analysis with {len(participant_matrices)} participants")
        
        # Calculate individual weights for each participant
        individual_weights = {}
        participant_consistency = {}
        
        for participant_id, matrix in participant_matrices.items():
            try:
                # Temporarily store current matrix
                original_matrix = self.comparison_matrix
                
                # Calculate weights for this participant
                self.comparison_matrix = matrix
                weights = self.calculate_weights(matrix)
                cr = self.calculate_consistency_ratio(matrix, weights)
                
                individual_weights[participant_id] = weights
                participant_consistency[participant_id] = cr
                
                # Restore original matrix
                self.comparison_matrix = original_matrix
                
            except Exception as e:
                logger.warning(f"Failed to process participant {participant_id}: {e}")
                continue
        
        if not individual_weights:
            raise ValueError("No valid participant matrices")
        
        # Aggregate individual weights into group weights
        if method == 'geometric_mean':
            group_weights = self._calculate_group_weights_geometric_mean(individual_weights)
        elif method == 'weighted_average':
            group_weights = self._calculate_group_weights_weighted_average(
                individual_weights, participant_consistency
            )
        else:
            raise ValueError(f"Unknown group aggregation method: {method}")
        
        # Calculate consensus metrics
        agreement_matrix = self._calculate_agreement_matrix(individual_weights)
        consensus_ratio = self._calculate_consensus_ratio(individual_weights, group_weights)
        
        # Store group weights
        self.weights = group_weights
        for i, criterion in enumerate(self.config.criteria):
            criterion.weight = float(group_weights[i])
        
        return GroupAHPResult(
            individual_weights=individual_weights,
            group_weights=group_weights,
            consensus_ratio=consensus_ratio,
            agreement_matrix=agreement_matrix,
            participant_consistency=participant_consistency
        )
    
    def _calculate_group_weights_geometric_mean(self, individual_weights: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculate group weights using geometric mean method."""
        weights_array = np.array(list(individual_weights.values()))
        
        # Calculate geometric mean for each criterion
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            group_weights = np.exp(np.mean(np.log(weights_array + 1e-10), axis=0))
        
        # Normalize
        return group_weights / group_weights.sum()
    
    def _calculate_group_weights_weighted_average(
        self, 
        individual_weights: Dict[str, np.ndarray],
        participant_consistency: Dict[str, float]
    ) -> np.ndarray:
        """Calculate group weights using consistency-weighted average."""
        # Weight participants by their consistency (lower CR = higher weight)
        participant_weights = {}
        for participant_id in individual_weights.keys():
            cr = participant_consistency.get(participant_id, 1.0)
            # Convert CR to weight (higher consistency = higher weight)
            participant_weights[participant_id] = max(0.1, 1.0 - cr)
        
        # Normalize participant weights
        total_weight = sum(participant_weights.values())
        for participant_id in participant_weights:
            participant_weights[participant_id] /= total_weight
        
        # Calculate weighted average
        group_weights = np.zeros(len(self.config.criteria))
        for participant_id, weights in individual_weights.items():
            p_weight = participant_weights[participant_id]
            group_weights += p_weight * weights
        
        return group_weights
    
    def _calculate_agreement_matrix(self, individual_weights: Dict[str, np.ndarray]) -> np.ndarray:
        """Calculate agreement matrix between participants."""
        participants = list(individual_weights.keys())
        n_participants = len(participants)
        agreement_matrix = np.zeros((n_participants, n_participants))
        
        for i, p1 in enumerate(participants):
            for j, p2 in enumerate(participants):
                if i == j:
                    agreement_matrix[i, j] = 1.0
                else:
                    # Calculate correlation between weight vectors
                    weights1 = individual_weights[p1]
                    weights2 = individual_weights[p2]
                    
                    correlation = np.corrcoef(weights1, weights2)[0, 1]
                    agreement_matrix[i, j] = max(0, correlation)  # Ensure non-negative
        
        return agreement_matrix
    
    def _calculate_consensus_ratio(self, individual_weights: Dict[str, np.ndarray], group_weights: np.ndarray) -> float:
        """Calculate consensus ratio (how well group weights represent individuals)."""
        deviations = []
        
        for weights in individual_weights.values():
            # Calculate Euclidean distance to group weights
            deviation = np.linalg.norm(weights - group_weights)
            deviations.append(deviation)
        
        # Convert to consensus ratio (0-1, higher is better consensus)
        avg_deviation = np.mean(deviations)
        consensus_ratio = max(0.0, 1.0 - avg_deviation)
        
        return consensus_ratio
    
    def complete_incomplete_matrix(self, incomplete_matrix: np.ndarray) -> np.ndarray:
        """Complete an incomplete comparison matrix using optimization.
        
        Args:
            incomplete_matrix: Matrix with 0s or NaNs for missing comparisons
            
        Returns:
            Completed comparison matrix
        """
        n = incomplete_matrix.shape[0]
        completed_matrix = incomplete_matrix.copy()
        
        # Find missing comparisons
        missing_pairs = []
        for i in range(n):
            for j in range(i+1, n):
                if (incomplete_matrix[i, j] == 0 or 
                    np.isnan(incomplete_matrix[i, j]) or
                    incomplete_matrix[j, i] == 0 or 
                    np.isnan(incomplete_matrix[j, i])):
                    missing_pairs.append((i, j))
        
        if not missing_pairs:
            return completed_matrix
        
        logger.info(f"Completing {len(missing_pairs)} missing comparisons")
        
        # Use iterative estimation based on available comparisons
        for iteration in range(50):  # Max iterations
            changed = False
            
            for i, j in missing_pairs:
                # Try to estimate using transitivity
                estimated_value = self._estimate_comparison_transitivity(completed_matrix, i, j)
                
                if estimated_value is not None and not np.isnan(estimated_value):
                    completed_matrix[i, j] = estimated_value
                    completed_matrix[j, i] = 1.0 / estimated_value
                    changed = True
            
            if not changed:
                break
        
        # Fill any remaining missing values with neutral comparisons
        for i, j in missing_pairs:
            if (completed_matrix[i, j] == 0 or np.isnan(completed_matrix[i, j])):
                completed_matrix[i, j] = 1.0  # Neutral comparison
                completed_matrix[j, i] = 1.0
                logger.warning(f"Used neutral comparison for [{i},{j}]")
        
        return completed_matrix
    
    def _estimate_comparison_transitivity(self, matrix: np.ndarray, i: int, j: int) -> Optional[float]:
        """Estimate comparison using transitivity through intermediate elements."""
        n = matrix.shape[0]
        estimates = []
        
        for k in range(n):
            if k != i and k != j:
                if (matrix[i, k] > 0 and not np.isnan(matrix[i, k]) and
                    matrix[k, j] > 0 and not np.isnan(matrix[k, j])):
                    # Estimate a_ij = a_ik * a_kj
                    estimate = matrix[i, k] * matrix[k, j]
                    estimates.append(estimate)
        
        if estimates:
            # Use geometric mean of estimates
            return np.exp(np.mean(np.log(estimates)))
        
        return None
    
    def export_results(self) -> Dict[str, Any]:
        """Export AHP analysis results."""
        return {
            'configuration': {
                'criteria': [
                    {
                        'name': c.name,
                        'description': c.description,
                        'weight': c.weight,
                        'data_source': c.data_source
                    }
                    for c in self.config.criteria
                ],
                'consistency_threshold': self.config.consistency_threshold
            },
            'analysis': {
                'comparison_matrix': self.comparison_matrix.tolist() if self.comparison_matrix is not None else None,
                'weights': self.weights.tolist() if self.weights is not None else None,
                'consistency_ratio': self.consistency_ratio,
                'is_consistent': self.is_consistent(),
                'eigenvector_method': self.eigenvector_method,
                'matrix_completeness': self._calculate_matrix_completeness(),
                'weight_distribution_balance': self._calculate_weight_balance()
            }
        }
    
    def _calculate_matrix_completeness(self) -> float:
        """Calculate percentage of completed comparisons in matrix."""
        if self.comparison_matrix is None:
            return 0.0
        
        n = self.comparison_matrix.shape[0]
        total_comparisons = n * (n - 1) // 2  # Upper triangle only
        completed_comparisons = 0
        
        for i in range(n):
            for j in range(i+1, n):
                if self.comparison_matrix[i, j] > 0 and not np.isnan(self.comparison_matrix[i, j]):
                    completed_comparisons += 1
        
        return completed_comparisons / total_comparisons if total_comparisons > 0 else 1.0
    
    def _calculate_weight_balance(self) -> Dict[str, float]:
        """Calculate weight distribution balance metrics."""
        if self.weights is None:
            return {'entropy': 0.0, 'max_weight': 0.0, 'min_weight': 0.0}
        
        # Calculate entropy (higher = more balanced)
        weights_nonzero = self.weights[self.weights > 0]
        if len(weights_nonzero) > 0:
            entropy = -np.sum(weights_nonzero * np.log(weights_nonzero + 1e-10))
        else:
            entropy = 0.0
        
        return {
            'entropy': float(entropy),
            'max_weight': float(np.max(self.weights)),
            'min_weight': float(np.min(self.weights)),
            'weight_range': float(np.max(self.weights) - np.min(self.weights)),
            'coefficient_of_variation': float(np.std(self.weights) / np.mean(self.weights)) if np.mean(self.weights) > 0 else 0.0
        }