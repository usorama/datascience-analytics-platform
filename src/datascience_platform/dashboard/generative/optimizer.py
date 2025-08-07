"""ML Output Optimizer

This module ensures ML optimization is complete before dashboard generation,
integrating with MLE-STAR convergence criteria.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass
import logging
import time

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStatus:
    """Status of ML optimization."""
    is_converged: bool
    iterations_completed: int
    current_performance: float
    improvement_rate: float
    time_elapsed: float
    convergence_criteria_met: Dict[str, bool]
    ready_for_dashboard: bool


class MLOutputOptimizer:
    """Ensures ML outputs are fully optimized before dashboard generation."""
    
    def __init__(
        self,
        convergence_threshold: float = 0.001,
        min_iterations: int = 3,
        max_iterations: int = 100,
        patience: int = 5
    ):
        """
        Initialize ML output optimizer.
        
        Args:
            convergence_threshold: Minimum improvement to continue
            min_iterations: Minimum iterations before checking convergence
            max_iterations: Maximum iterations allowed
            patience: Iterations without improvement before stopping
        """
        self.convergence_threshold = convergence_threshold
        self.min_iterations = min_iterations
        self.max_iterations = max_iterations
        self.patience = patience
        
        self.optimization_history: List[float] = []
        self.start_time: Optional[float] = None
    
    def check_optimization_complete(
        self,
        ml_pipeline: Any,
        refinement_history: Optional[List[Any]] = None
    ) -> OptimizationStatus:
        """
        Check if ML optimization is complete and ready for dashboard.
        
        Args:
            ml_pipeline: The ML pipeline object
            refinement_history: History from MLE-STAR refinement
            
        Returns:
            OptimizationStatus with convergence information
        """
        self.start_time = time.time()
        
        # Check MLE-STAR convergence if available
        if refinement_history:
            return self._check_mle_star_convergence(refinement_history)
        
        # Otherwise use general convergence checking
        return self._check_general_convergence(ml_pipeline)
    
    def _check_mle_star_convergence(
        self,
        refinement_history: List[Any]
    ) -> OptimizationStatus:
        """Check convergence using MLE-STAR refinement history."""
        if not refinement_history:
            return OptimizationStatus(
                is_converged=False,
                iterations_completed=0,
                current_performance=0.0,
                improvement_rate=float('inf'),
                time_elapsed=0.0,
                convergence_criteria_met={},
                ready_for_dashboard=False
            )
        
        iterations_completed = len(refinement_history)
        
        # Extract performance history
        performance_history = [
            iteration.optimization_result.optimized_performance
            for iteration in refinement_history
        ]
        
        current_performance = performance_history[-1] if performance_history else 0.0
        
        # Calculate improvement rate
        if len(performance_history) >= 2:
            recent_improvements = [
                performance_history[i] - performance_history[i-1]
                for i in range(max(1, len(performance_history)-3), len(performance_history))
            ]
            improvement_rate = np.mean(recent_improvements)
        else:
            improvement_rate = float('inf')
        
        # Check convergence criteria
        criteria_met = {
            'min_iterations': iterations_completed >= self.min_iterations,
            'improvement_threshold': abs(improvement_rate) < self.convergence_threshold,
            'max_iterations': iterations_completed < self.max_iterations,
            'performance_stable': self._is_performance_stable(performance_history)
        }
        
        is_converged = (
            criteria_met['min_iterations'] and
            criteria_met['improvement_threshold'] and
            criteria_met['performance_stable']
        )
        
        time_elapsed = time.time() - self.start_time if self.start_time else 0.0
        
        return OptimizationStatus(
            is_converged=is_converged,
            iterations_completed=iterations_completed,
            current_performance=current_performance,
            improvement_rate=improvement_rate,
            time_elapsed=time_elapsed,
            convergence_criteria_met=criteria_met,
            ready_for_dashboard=is_converged
        )
    
    def _check_general_convergence(self, ml_pipeline: Any) -> OptimizationStatus:
        """Check convergence for general ML pipelines."""
        # Try to extract performance metrics
        performance = 0.0
        iterations = 0
        
        # Check common attributes
        if hasattr(ml_pipeline, 'best_score_'):
            performance = ml_pipeline.best_score_
        elif hasattr(ml_pipeline, 'score'):
            try:
                # Assuming we have some validation data
                performance = ml_pipeline.score(X_val, y_val)
            except:
                performance = 0.0
        
        if hasattr(ml_pipeline, 'n_iter_'):
            iterations = ml_pipeline.n_iter_
        
        # Simple convergence check
        is_converged = iterations >= self.min_iterations
        
        return OptimizationStatus(
            is_converged=is_converged,
            iterations_completed=iterations,
            current_performance=performance,
            improvement_rate=0.0,
            time_elapsed=time.time() - self.start_time if self.start_time else 0.0,
            convergence_criteria_met={'basic_check': is_converged},
            ready_for_dashboard=is_converged
        )
    
    def _is_performance_stable(
        self,
        performance_history: List[float],
        window: int = 3
    ) -> bool:
        """Check if performance has stabilized."""
        if len(performance_history) < window:
            return False
        
        recent_values = performance_history[-window:]
        std_dev = np.std(recent_values)
        mean_val = np.mean(recent_values)
        
        # Consider stable if std deviation is less than 1% of mean
        return std_dev < (0.01 * abs(mean_val)) if mean_val != 0 else True
    
    def optimize_for_dashboard(
        self,
        ml_outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Post-process ML outputs for optimal dashboard display.
        
        Args:
            ml_outputs: Raw ML outputs
            
        Returns:
            Optimized outputs ready for visualization
        """
        optimized = ml_outputs.copy()
        
        # Ensure all numeric values are clean
        optimized = self._clean_numeric_values(optimized)
        
        # Add dashboard-specific transformations
        optimized = self._add_dashboard_metadata(optimized)
        
        # Validate data completeness
        optimized = self._validate_completeness(optimized)
        
        # Add interpretability features
        optimized = self._enhance_interpretability(optimized)
        
        return optimized
    
    def _clean_numeric_values(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Clean numeric values for display."""
        cleaned = {}
        
        for key, value in outputs.items():
            if isinstance(value, (int, float)):
                # Handle NaN and infinity
                if pd.isna(value) or np.isinf(value):
                    cleaned[key] = 0.0
                else:
                    # Round to reasonable precision
                    cleaned[key] = round(float(value), 4)
            elif isinstance(value, np.ndarray):
                # Convert numpy arrays to lists
                cleaned[key] = np.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0).tolist()
            elif isinstance(value, pd.DataFrame):
                # Clean dataframes
                cleaned[key] = value.fillna(0).round(4)
            elif isinstance(value, dict):
                # Recursively clean nested dicts
                cleaned[key] = self._clean_numeric_values(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    def _add_dashboard_metadata(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata useful for dashboard generation."""
        outputs['_dashboard_metadata'] = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'optimization_status': 'complete',
            'data_quality_score': self._calculate_data_quality_score(outputs),
            'recommended_refresh_interval': '1 hour'
        }
        
        # Add display hints
        if 'feature_importance' in outputs:
            outputs['_display_hints'] = {
                'feature_importance': {
                    'chart_type': 'horizontal_bar',
                    'top_n': 20,
                    'color_scheme': 'gradient'
                }
            }
        
        return outputs
    
    def _validate_completeness(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data completeness for dashboard."""
        required_fields = ['model_performance', 'predictions']
        missing_fields = []
        
        for field in required_fields:
            if field not in outputs:
                missing_fields.append(field)
        
        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            
            # Add placeholder data
            if 'model_performance' not in outputs:
                outputs['model_performance'] = {
                    'accuracy': 0.0,
                    'status': 'Not available'
                }
            
            if 'predictions' not in outputs:
                outputs['predictions'] = pd.DataFrame()
        
        return outputs
    
    def _enhance_interpretability(self, outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Add interpretability enhancements for dashboard."""
        # Add human-readable labels
        if 'predictions' in outputs and isinstance(outputs['predictions'], pd.DataFrame):
            df = outputs['predictions']
            
            # Add confidence categories
            if 'confidence' in df.columns:
                df['confidence_level'] = pd.cut(
                    df['confidence'],
                    bins=[0, 0.5, 0.8, 1.0],
                    labels=['Low', 'Medium', 'High']
                )
            
            # Add value categories
            if 'value_score' in df.columns:
                df['value_category'] = pd.cut(
                    df['value_score'],
                    bins=[0, 0.3, 0.7, 1.0],
                    labels=['Low Value', 'Medium Value', 'High Value']
                )
        
        # Add explanatory text
        outputs['_explanations'] = {
            'model_type': 'Classification model using Random Forest',
            'optimization_method': 'MLE-STAR ablation-driven optimization',
            'data_preprocessing': 'Robust validation with decimal handling',
            'interpretation_guide': {
                'high_value': 'Items with score > 0.7 are recommended for immediate attention',
                'medium_value': 'Items with score 0.3-0.7 should be reviewed',
                'low_value': 'Items with score < 0.3 can be deprioritized'
            }
        }
        
        return outputs
    
    def _calculate_data_quality_score(self, outputs: Dict[str, Any]) -> float:
        """Calculate a data quality score for the outputs."""
        score = 1.0
        penalties = 0.0
        
        # Check for missing values
        for key, value in outputs.items():
            if isinstance(value, pd.DataFrame):
                missing_ratio = value.isna().sum().sum() / (value.shape[0] * value.shape[1])
                penalties += missing_ratio * 0.2
            elif isinstance(value, (list, np.ndarray)):
                if len(value) == 0:
                    penalties += 0.1
        
        # Check for data consistency
        if 'model_performance' in outputs:
            perf = outputs['model_performance']
            if isinstance(perf, dict):
                for metric, value in perf.items():
                    if isinstance(value, (int, float)):
                        if value < 0 or value > 1:
                            penalties += 0.05
        
        return max(0.0, score - penalties)