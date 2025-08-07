"""Ablation Study Engine for ML Pipeline Component Analysis

This module implements systematic ablation studies to identify high-impact
components in ML pipelines, following the MLE-STAR methodology.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from scipy import stats
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path

from .pipeline import PipelineComponent, ComponentType

logger = logging.getLogger(__name__)


@dataclass
class AblationResult:
    """Results from ablating a single component."""
    component_id: str
    baseline_performance: float
    ablated_performance: float
    impact_score: float
    relative_impact: float
    confidence_interval: Tuple[float, float]
    p_value: float
    execution_time: float
    error: Optional[str] = None


@dataclass
class ComponentImpact:
    """Detailed impact analysis for a component."""
    component_id: str
    impact_score: float
    statistical_significance: float
    effect_size: float  # Cohen's d
    confidence_level: float
    recommendation: str
    priority: int  # 1-5, where 1 is highest priority


class AblationStudyEngine:
    """Engine for conducting systematic ablation studies on ML pipelines."""
    
    def __init__(
        self,
        performance_metric: str = 'accuracy',
        n_cv_folds: int = 5,
        confidence_level: float = 0.95,
        min_effect_size: float = 0.2,
        parallel_execution: bool = True
    ):
        """
        Initialize ablation study engine.
        
        Args:
            performance_metric: Metric to optimize (accuracy, f1, auc, etc.)
            n_cv_folds: Number of cross-validation folds
            confidence_level: Confidence level for statistical tests
            min_effect_size: Minimum effect size to consider significant
            parallel_execution: Whether to run ablations in parallel
        """
        self.performance_metric = performance_metric
        self.n_cv_folds = n_cv_folds
        self.confidence_level = confidence_level
        self.min_effect_size = min_effect_size
        self.parallel_execution = parallel_execution
        
        self.ablation_results: Dict[str, AblationResult] = {}
        self.baseline_performance: Optional[float] = None
        self.baseline_scores: Optional[np.ndarray] = None
    
    def run_ablation_study(
        self,
        pipeline: Any,
        data: Tuple[pd.DataFrame, pd.Series],
        components: Dict[str, PipelineComponent],
        evaluation_function: Callable
    ) -> Dict[str, AblationResult]:
        """
        Run complete ablation study on all components.
        
        Args:
            pipeline: ML pipeline object with fit/predict methods
            data: Tuple of (X, y) data
            components: Dictionary of pipeline components
            evaluation_function: Function to evaluate pipeline performance
            
        Returns:
            Dictionary of ablation results for each component
        """
        X, y = data
        
        # Get baseline performance
        logger.info("Evaluating baseline pipeline performance...")
        self.baseline_scores = self._evaluate_pipeline(
            pipeline, X, y, evaluation_function
        )
        self.baseline_performance = np.mean(self.baseline_scores)
        logger.info(f"Baseline {self.performance_metric}: {self.baseline_performance:.4f}")
        
        # Run ablation for each component
        if self.parallel_execution:
            self._run_parallel_ablations(
                pipeline, X, y, components, evaluation_function
            )
        else:
            self._run_sequential_ablations(
                pipeline, X, y, components, evaluation_function
            )
        
        return self.ablation_results
    
    def _run_parallel_ablations(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        components: Dict[str, PipelineComponent],
        evaluation_function: Callable
    ):
        """Run ablations in parallel."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_component = {
                executor.submit(
                    self._ablate_component,
                    component_id,
                    component,
                    pipeline,
                    X,
                    y,
                    evaluation_function
                ): component_id
                for component_id, component in components.items()
            }
            
            for future in as_completed(future_to_component):
                component_id = future_to_component[future]
                try:
                    result = future.result()
                    self.ablation_results[component_id] = result
                except Exception as e:
                    logger.error(f"Error ablating {component_id}: {e}")
                    self.ablation_results[component_id] = AblationResult(
                        component_id=component_id,
                        baseline_performance=self.baseline_performance,
                        ablated_performance=self.baseline_performance,
                        impact_score=0.0,
                        relative_impact=0.0,
                        confidence_interval=(0.0, 0.0),
                        p_value=1.0,
                        execution_time=0.0,
                        error=str(e)
                    )
    
    def _run_sequential_ablations(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        components: Dict[str, PipelineComponent],
        evaluation_function: Callable
    ):
        """Run ablations sequentially."""
        for component_id, component in components.items():
            result = self._ablate_component(
                component_id,
                component,
                pipeline,
                X,
                y,
                evaluation_function
            )
            self.ablation_results[component_id] = result
    
    def _ablate_component(
        self,
        component_id: str,
        component: PipelineComponent,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        evaluation_function: Callable
    ) -> AblationResult:
        """Ablate a single component and measure impact."""
        logger.info(f"Ablating component: {component_id}")
        start_time = time.time()
        
        try:
            # Create ablated pipeline (component-specific logic)
            ablated_pipeline = self._create_ablated_pipeline(
                pipeline, component_id, component.component_type
            )
            
            # Evaluate ablated pipeline
            ablated_scores = self._evaluate_pipeline(
                ablated_pipeline, X, y, evaluation_function
            )
            ablated_performance = np.mean(ablated_scores)
            
            # Calculate impact metrics
            impact_score = self.baseline_performance - ablated_performance
            relative_impact = impact_score / self.baseline_performance if self.baseline_performance > 0 else 0
            
            # Statistical significance test
            try:
                t_stat, p_value = stats.ttest_rel(self.baseline_scores, ablated_scores)
            except:
                # If test fails (e.g., constant values), set p_value to 1
                p_value = 1.0
            
            # Confidence interval for impact
            impact_differences = self.baseline_scores - ablated_scores
            ci_lower, ci_upper = self._calculate_confidence_interval(impact_differences)
            
            execution_time = time.time() - start_time
            
            return AblationResult(
                component_id=component_id,
                baseline_performance=self.baseline_performance,
                ablated_performance=ablated_performance,
                impact_score=impact_score,
                relative_impact=relative_impact,
                confidence_interval=(ci_lower, ci_upper),
                p_value=p_value,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Error in ablation: {e}")
            return AblationResult(
                component_id=component_id,
                baseline_performance=self.baseline_performance,
                ablated_performance=self.baseline_performance,
                impact_score=0.0,
                relative_impact=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=1.0,
                execution_time=time.time() - start_time,
                error=str(e)
            )
    
    def _create_ablated_pipeline(
        self,
        pipeline: Any,
        component_id: str,
        component_type: ComponentType
    ) -> Any:
        """
        Create a version of the pipeline with the specified component ablated.
        
        This is a simplified version - in practice, this would need to be
        customized based on the pipeline structure.
        """
        # Deep copy the pipeline
        import copy
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import FunctionTransformer
        
        ablated_pipeline = copy.deepcopy(pipeline)
        
        # Handle sklearn Pipeline
        if isinstance(ablated_pipeline, Pipeline):
            steps = ablated_pipeline.steps
            new_steps = []
            
            for step_name, step_estimator in steps:
                if step_name == component_id:
                    # Replace with pass-through transformer
                    if component_type in [ComponentType.DATA_PREPROCESSING, 
                                         ComponentType.FEATURE_ENGINEERING,
                                         ComponentType.FEATURE_SELECTION]:
                        # Use identity transformer that passes data through
                        new_steps.append((step_name, FunctionTransformer(lambda x: x)))
                    else:
                        # For models, we can't easily ablate, so skip
                        new_steps.append((step_name, step_estimator))
                else:
                    new_steps.append((step_name, step_estimator))
            
            ablated_pipeline = Pipeline(new_steps)
        
        # Component-specific ablation logic for custom pipelines
        elif component_type == ComponentType.FEATURE_ENGINEERING:
            # Remove feature engineering step
            if hasattr(ablated_pipeline, 'feature_engineering'):
                ablated_pipeline.feature_engineering = lambda x: x
        
        elif component_type == ComponentType.FEATURE_SELECTION:
            # Disable feature selection
            if hasattr(ablated_pipeline, 'feature_selection'):
                ablated_pipeline.feature_selection = None
        
        elif component_type == ComponentType.DATA_PREPROCESSING:
            # Use minimal preprocessing
            if hasattr(ablated_pipeline, 'preprocessing'):
                ablated_pipeline.preprocessing = lambda x: x
        
        # Add more component-specific logic as needed
        
        return ablated_pipeline
    
    def _evaluate_pipeline(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        evaluation_function: Callable
    ) -> np.ndarray:
        """Evaluate pipeline performance using cross-validation."""
        from sklearn.model_selection import cross_val_score
        
        # Use the provided evaluation function or default CV
        if evaluation_function:
            scores = evaluation_function(pipeline, X, y, self.n_cv_folds)
        else:
            scores = cross_val_score(
                pipeline, X, y,
                cv=self.n_cv_folds,
                scoring=self.performance_metric
            )
        
        return scores
    
    def _calculate_confidence_interval(
        self,
        data: np.ndarray
    ) -> Tuple[float, float]:
        """Calculate confidence interval for the data."""
        alpha = 1 - self.confidence_level
        n = len(data)
        
        if n < 2:
            return (0.0, 0.0)
        
        mean = np.mean(data)
        sem = stats.sem(data)
        margin = sem * stats.t.ppf((1 + self.confidence_level) / 2, n - 1)
        
        return (mean - margin, mean + margin)
    
    def identify_critical_components(
        self,
        top_n: int = 5
    ) -> List[ComponentImpact]:
        """Identify the most critical components based on ablation results."""
        component_impacts = []
        
        for component_id, result in self.ablation_results.items():
            if result.error:
                continue
            
            # Calculate Cohen's d effect size
            effect_size = self._calculate_effect_size(
                self.baseline_scores,
                result.baseline_performance,
                result.ablated_performance
            )
            
            # Determine priority
            if result.p_value < 0.001 and effect_size > 0.8:
                priority = 1
                recommendation = "Critical component - highest optimization priority"
            elif result.p_value < 0.01 and effect_size > 0.5:
                priority = 2
                recommendation = "Important component - high optimization priority"
            elif result.p_value < 0.05 and effect_size > self.min_effect_size:
                priority = 3
                recommendation = "Significant component - medium optimization priority"
            elif result.relative_impact > 0.05:
                priority = 4
                recommendation = "Minor impact - low optimization priority"
            else:
                priority = 5
                recommendation = "Negligible impact - consider removing"
            
            impact = ComponentImpact(
                component_id=component_id,
                impact_score=result.impact_score,
                statistical_significance=1 - result.p_value,
                effect_size=effect_size,
                confidence_level=self.confidence_level,
                recommendation=recommendation,
                priority=priority
            )
            
            component_impacts.append(impact)
        
        # Sort by priority and impact score
        component_impacts.sort(
            key=lambda x: (x.priority, -x.impact_score)
        )
        
        return component_impacts[:top_n]
    
    def _calculate_effect_size(
        self,
        baseline_scores: np.ndarray,
        baseline_mean: float,
        ablated_mean: float
    ) -> float:
        """Calculate Cohen's d effect size."""
        pooled_std = np.std(baseline_scores)
        if pooled_std == 0:
            return 0.0
        
        return abs(baseline_mean - ablated_mean) / pooled_std
    
    def export_results(self, output_path: Path):
        """Export ablation study results to file."""
        results_data = {
            'metadata': {
                'performance_metric': self.performance_metric,
                'baseline_performance': self.baseline_performance,
                'n_components': len(self.ablation_results),
                'confidence_level': self.confidence_level
            },
            'results': {}
        }
        
        for component_id, result in self.ablation_results.items():
            results_data['results'][component_id] = {
                'baseline_performance': result.baseline_performance,
                'ablated_performance': result.ablated_performance,
                'impact_score': result.impact_score,
                'relative_impact': result.relative_impact,
                'confidence_interval': result.confidence_interval,
                'p_value': result.p_value,
                'execution_time': result.execution_time,
                'error': result.error
            }
        
        with open(output_path, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def generate_report(self) -> pd.DataFrame:
        """Generate a summary report of ablation results."""
        report_data = []
        
        for component_id, result in self.ablation_results.items():
            report_data.append({
                'Component': component_id,
                'Baseline': f"{result.baseline_performance:.4f}",
                'Ablated': f"{result.ablated_performance:.4f}",
                'Impact': f"{result.impact_score:.4f}",
                'Relative Impact': f"{result.relative_impact:.2%}",
                'P-Value': f"{result.p_value:.4f}",
                'CI Lower': f"{result.confidence_interval[0]:.4f}",
                'CI Upper': f"{result.confidence_interval[1]:.4f}",
                'Significant': 'Yes' if result.p_value < 0.05 else 'No',
                'Error': result.error or ''
            })
        
        df = pd.DataFrame(report_data)
        df = df.sort_values('Impact', ascending=False)
        
        return df


class ComponentImpactAnalyzer:
    """Advanced analysis of component impacts from ablation studies."""
    
    def __init__(self, ablation_results: Dict[str, AblationResult]):
        self.ablation_results = ablation_results
    
    def analyze_interaction_effects(
        self,
        component_pairs: List[Tuple[str, str]]
    ) -> Dict[str, float]:
        """
        Analyze interaction effects between component pairs.
        
        This would require additional ablation studies where pairs
        of components are removed together.
        """
        interaction_effects = {}
        
        for comp1, comp2 in component_pairs:
            if comp1 in self.ablation_results and comp2 in self.ablation_results:
                # Simplified interaction calculation
                impact1 = self.ablation_results[comp1].impact_score
                impact2 = self.ablation_results[comp2].impact_score
                
                # Interaction would be measured by ablating both together
                # For now, estimate as non-additive effect
                estimated_interaction = abs(impact1 * impact2) * 0.1
                
                interaction_effects[f"{comp1}_{comp2}"] = estimated_interaction
        
        return interaction_effects
    
    def calculate_cumulative_impact(
        self,
        component_ids: List[str]
    ) -> float:
        """Calculate cumulative impact of multiple components."""
        total_impact = 0.0
        
        for comp_id in component_ids:
            if comp_id in self.ablation_results:
                total_impact += self.ablation_results[comp_id].impact_score
        
        # Account for potential overlap (simplified)
        overlap_factor = 0.9 ** (len(component_ids) - 1)
        
        return total_impact * overlap_factor
    
    def recommend_optimization_strategy(self) -> Dict[str, Any]:
        """Recommend optimization strategy based on ablation results."""
        # Identify high-impact components
        high_impact = []
        medium_impact = []
        low_impact = []
        
        for comp_id, result in self.ablation_results.items():
            if result.relative_impact > 0.1:
                high_impact.append(comp_id)
            elif result.relative_impact > 0.05:
                medium_impact.append(comp_id)
            else:
                low_impact.append(comp_id)
        
        strategy = {
            'immediate_focus': high_impact[:3],
            'secondary_focus': medium_impact[:3],
            'consider_removing': [
                comp for comp in low_impact
                if self.ablation_results[comp].relative_impact < 0.01
            ],
            'estimated_improvement': sum(
                self.ablation_results[comp].impact_score
                for comp in high_impact[:3]
            ),
            'recommendations': [
                f"Focus on optimizing {high_impact[0]} first (impact: {self.ablation_results[high_impact[0]].relative_impact:.1%})"
                if high_impact else "No high-impact components identified",
                f"Consider removing {len(low_impact)} low-impact components to reduce complexity",
                "Run targeted optimization on top 3 components for maximum ROI"
            ]
        }
        
        return strategy