"""Analytic Hierarchy Process (AHP) Engine

This module implements the AHP methodology for multi-criteria decision making,
enabling objective prioritization of ADO work items based on configurable criteria.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field, validator
import logging
from enum import Enum

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


class AHPEngine:
    """Main AHP calculation engine."""
    
    def __init__(self, config: AHPConfiguration):
        """Initialize AHP engine with configuration.
        
        Args:
            config: AHP configuration with criteria
        """
        self.config = config
        self.comparison_matrix: Optional[np.ndarray] = None
        self.weights: Optional[np.ndarray] = None
        self.consistency_ratio: Optional[float] = None
        
        # Random index for consistency calculation (Saaty)
        self.random_index = {
            1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
            6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
            11: 1.51, 12: 1.48, 13: 1.56, 14: 1.57, 15: 1.59
        }
    
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
    
    def calculate_weights(self, matrix: Optional[np.ndarray] = None) -> np.ndarray:
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
        return weights
    
    def calculate_consistency_ratio(self, matrix: Optional[np.ndarray] = None) -> float:
        """Calculate consistency ratio for the comparison matrix.
        
        Args:
            matrix: Comparison matrix (uses stored matrix if None)
            
        Returns:
            Consistency ratio (CR)
        """
        if matrix is None:
            matrix = self.comparison_matrix
        
        if matrix is None or self.weights is None:
            raise ValueError("Matrix and weights must be calculated first")
        
        n = matrix.shape[0]
        
        # Calculate λmax (maximum eigenvalue)
        weighted_sum = matrix @ self.weights
        lambda_max = np.mean(weighted_sum / self.weights)
        
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
                'is_consistent': self.is_consistent()
            }
        }