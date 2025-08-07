"""Component Optimization and Refinement Engine

This module implements the two-loop refinement architecture from MLE-STAR:
- Outer loop: Ablation-driven component selection
- Inner loop: Focused component optimization
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging
import time
from pathlib import Path
import json

# Optimization libraries
try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False
    
try:
    from skopt import BayesSearchCV
    from skopt.space import Real, Integer, Categorical
    SKOPT_AVAILABLE = True
except ImportError:
    SKOPT_AVAILABLE = False

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

from .pipeline import PipelineComponent, ComponentType
from .ablation import AblationResult, ComponentImpact

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Available optimization strategies."""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    OPTUNA = "optuna"
    EVOLUTIONARY = "evolutionary"


@dataclass
class OptimizationResult:
    """Results from optimizing a component."""
    component_id: str
    original_performance: float
    optimized_performance: float
    improvement: float
    relative_improvement: float
    best_params: Dict[str, Any]
    optimization_history: List[float]
    execution_time: float
    strategy_used: OptimizationStrategy


@dataclass
class RefinementIteration:
    """Single iteration of the refinement process."""
    iteration: int
    target_component: str
    ablation_impact: float
    optimization_result: OptimizationResult
    cumulative_improvement: float


class ComponentOptimizer:
    """Optimizes individual ML pipeline components."""
    
    def __init__(
        self,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BAYESIAN,
        n_iterations: int = 50,
        cv_folds: int = 5,
        random_state: int = 42
    ):
        """
        Initialize component optimizer.
        
        Args:
            optimization_strategy: Strategy to use for optimization
            n_iterations: Number of optimization iterations
            cv_folds: Number of cross-validation folds
            random_state: Random seed for reproducibility
        """
        self.optimization_strategy = optimization_strategy
        self.n_iterations = n_iterations
        self.cv_folds = cv_folds
        self.random_state = random_state
        
        # Check available libraries and adjust strategy
        self._validate_strategy()
    
    def _validate_strategy(self):
        """Validate and adjust optimization strategy based on available libraries."""
        if self.optimization_strategy == OptimizationStrategy.OPTUNA and not OPTUNA_AVAILABLE:
            logger.warning("Optuna not available, falling back to Bayesian search")
            self.optimization_strategy = OptimizationStrategy.BAYESIAN
        
        if self.optimization_strategy == OptimizationStrategy.BAYESIAN and not SKOPT_AVAILABLE:
            logger.warning("Scikit-optimize not available, falling back to random search")
            self.optimization_strategy = OptimizationStrategy.RANDOM_SEARCH
    
    def optimize_component(
        self,
        component: PipelineComponent,
        pipeline: Any,
        data: Tuple[pd.DataFrame, pd.Series],
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> OptimizationResult:
        """
        Optimize a single component.
        
        Args:
            component: Component to optimize
            pipeline: ML pipeline containing the component
            data: Training data (X, y)
            search_space: Parameter search space for the component
            evaluation_function: Function to evaluate performance
            
        Returns:
            OptimizationResult with optimization details
        """
        X, y = data
        start_time = time.time()
        
        # Get baseline performance
        baseline_scores = evaluation_function(pipeline, X, y)
        baseline_performance = np.mean(baseline_scores)
        
        logger.info(f"Optimizing component: {component.component_id}")
        logger.info(f"Baseline performance: {baseline_performance:.4f}")
        
        # Choose optimization method based on component type
        if component.component_type == ComponentType.FEATURE_ENGINEERING:
            result = self._optimize_feature_engineering(
                component, pipeline, X, y, search_space, evaluation_function
            )
        elif component.component_type == ComponentType.MODEL_SELECTION:
            result = self._optimize_model_selection(
                component, pipeline, X, y, search_space, evaluation_function
            )
        elif component.component_type == ComponentType.HYPERPARAMETER_TUNING:
            result = self._optimize_hyperparameters(
                component, pipeline, X, y, search_space, evaluation_function
            )
        else:
            # Generic optimization
            result = self._generic_optimization(
                component, pipeline, X, y, search_space, evaluation_function
            )
        
        # Calculate improvement
        improvement = result['best_score'] - baseline_performance
        relative_improvement = improvement / baseline_performance if baseline_performance > 0 else 0
        
        execution_time = time.time() - start_time
        
        return OptimizationResult(
            component_id=component.component_id,
            original_performance=baseline_performance,
            optimized_performance=result['best_score'],
            improvement=improvement,
            relative_improvement=relative_improvement,
            best_params=result['best_params'],
            optimization_history=result.get('history', []),
            execution_time=execution_time,
            strategy_used=self.optimization_strategy
        )
    
    def _optimize_feature_engineering(
        self,
        component: PipelineComponent,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Optimize feature engineering component."""
        # Feature engineering specific optimization
        fe_search_space = search_space.get('feature_engineering', {
            'polynomial_degree': [1, 2, 3],
            'interaction_only': [True, False],
            'include_bias': [False],
            'scaling_method': ['standard', 'minmax', 'robust', 'none'],
            'encoding_method': ['onehot', 'target', 'ordinal']
        })
        
        if self.optimization_strategy == OptimizationStrategy.BAYESIAN:
            return self._bayesian_search(
                pipeline, X, y, fe_search_space, evaluation_function
            )
        else:
            return self._grid_search(
                pipeline, X, y, fe_search_space, evaluation_function
            )
    
    def _optimize_model_selection(
        self,
        component: PipelineComponent,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Optimize model selection component."""
        # Model selection specific optimization
        model_search_space = search_space.get('models', {
            'model_type': ['rf', 'xgb', 'lgb', 'svm', 'lr'],
            'rf__n_estimators': [50, 100, 200, 300],
            'rf__max_depth': [5, 10, 20, None],
            'xgb__n_estimators': [50, 100, 200],
            'xgb__learning_rate': [0.01, 0.1, 0.3],
            'xgb__max_depth': [3, 5, 7, 9]
        })
        
        if self.optimization_strategy == OptimizationStrategy.OPTUNA:
            return self._optuna_search(
                pipeline, X, y, model_search_space, evaluation_function
            )
        else:
            return self._random_search(
                pipeline, X, y, model_search_space, evaluation_function
            )
    
    def _optimize_hyperparameters(
        self,
        component: PipelineComponent,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Optimize hyperparameters of existing model."""
        # Get current model type and create appropriate search space
        if hasattr(pipeline, 'get_params'):
            current_params = pipeline.get_params()
            # Filter search space to only include relevant parameters
            hp_search_space = {
                k: v for k, v in search_space.items()
                if any(k.startswith(prefix) for prefix in current_params.keys())
            }
        else:
            hp_search_space = search_space
        
        return self._bayesian_search(
            pipeline, X, y, hp_search_space, evaluation_function
        )
    
    def _generic_optimization(
        self,
        component: PipelineComponent,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Generic optimization for any component type."""
        if self.optimization_strategy == OptimizationStrategy.GRID_SEARCH:
            return self._grid_search(pipeline, X, y, search_space, evaluation_function)
        elif self.optimization_strategy == OptimizationStrategy.RANDOM_SEARCH:
            return self._random_search(pipeline, X, y, search_space, evaluation_function)
        elif self.optimization_strategy == OptimizationStrategy.BAYESIAN:
            return self._bayesian_search(pipeline, X, y, search_space, evaluation_function)
        elif self.optimization_strategy == OptimizationStrategy.OPTUNA:
            return self._optuna_search(pipeline, X, y, search_space, evaluation_function)
        else:
            # Fallback to random search
            return self._random_search(pipeline, X, y, search_space, evaluation_function)
    
    def _grid_search(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Perform grid search optimization."""
        grid_search = GridSearchCV(
            pipeline,
            search_space,
            cv=self.cv_folds,
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'history': grid_search.cv_results_['mean_test_score'].tolist()
        }
    
    def _random_search(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Perform random search optimization."""
        random_search = RandomizedSearchCV(
            pipeline,
            search_space,
            n_iter=self.n_iterations,
            cv=self.cv_folds,
            n_jobs=-1,
            random_state=self.random_state,
            verbose=1
        )
        
        random_search.fit(X, y)
        
        return {
            'best_params': random_search.best_params_,
            'best_score': random_search.best_score_,
            'history': random_search.cv_results_['mean_test_score'].tolist()
        }
    
    def _bayesian_search(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Perform Bayesian optimization."""
        if not SKOPT_AVAILABLE:
            logger.warning("Scikit-optimize not available, using random search")
            return self._random_search(pipeline, X, y, search_space, evaluation_function)
        
        # Convert search space to skopt format
        skopt_space = self._convert_to_skopt_space(search_space)
        
        bayes_search = BayesSearchCV(
            pipeline,
            skopt_space,
            n_iter=self.n_iterations,
            cv=self.cv_folds,
            n_jobs=-1,
            random_state=self.random_state,
            verbose=1
        )
        
        bayes_search.fit(X, y)
        
        return {
            'best_params': bayes_search.best_params_,
            'best_score': bayes_search.best_score_,
            'history': [score.mean() for score in bayes_search.cv_results_['split0_test_score']]
        }
    
    def _optuna_search(
        self,
        pipeline: Any,
        X: pd.DataFrame,
        y: pd.Series,
        search_space: Dict[str, Any],
        evaluation_function: Callable
    ) -> Dict[str, Any]:
        """Perform Optuna optimization."""
        if not OPTUNA_AVAILABLE:
            logger.warning("Optuna not available, using random search")
            return self._random_search(pipeline, X, y, search_space, evaluation_function)
        
        import copy
        
        def objective(trial):
            # Sample parameters from search space
            params = {}
            for param_name, param_range in search_space.items():
                if isinstance(param_range, list):
                    if all(isinstance(x, (int, float)) for x in param_range):
                        if all(isinstance(x, int) for x in param_range):
                            params[param_name] = trial.suggest_int(
                                param_name, min(param_range), max(param_range)
                            )
                        else:
                            params[param_name] = trial.suggest_float(
                                param_name, min(param_range), max(param_range)
                            )
                    else:
                        params[param_name] = trial.suggest_categorical(param_name, param_range)
                elif isinstance(param_range, tuple) and len(param_range) == 2:
                    params[param_name] = trial.suggest_float(
                        param_name, param_range[0], param_range[1]
                    )
            
            # Create pipeline with sampled parameters
            trial_pipeline = copy.deepcopy(pipeline)
            trial_pipeline.set_params(**params)
            
            # Evaluate
            scores = evaluation_function(trial_pipeline, X, y)
            return np.mean(scores)
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=self.n_iterations)
        
        return {
            'best_params': study.best_params,
            'best_score': study.best_value,
            'history': [trial.value for trial in study.trials if trial.value is not None]
        }
    
    def _convert_to_skopt_space(self, search_space: Dict[str, Any]) -> Dict[str, Any]:
        """Convert search space to scikit-optimize format."""
        skopt_space = {}
        
        for param_name, param_range in search_space.items():
            if isinstance(param_range, list):
                if all(isinstance(x, (int, float)) for x in param_range):
                    if all(isinstance(x, int) for x in param_range):
                        skopt_space[param_name] = Integer(min(param_range), max(param_range))
                    else:
                        skopt_space[param_name] = Real(min(param_range), max(param_range))
                else:
                    skopt_space[param_name] = Categorical(param_range)
            elif isinstance(param_range, tuple) and len(param_range) == 2:
                skopt_space[param_name] = Real(param_range[0], param_range[1])
        
        return skopt_space


class RefinementEngine:
    """Implements the two-loop refinement architecture from MLE-STAR."""
    
    def __init__(
        self,
        max_outer_iterations: int = 5,
        max_inner_iterations: int = 3,
        convergence_threshold: float = 0.001,
        min_improvement: float = 0.01
    ):
        """
        Initialize refinement engine.
        
        Args:
            max_outer_iterations: Maximum outer loop iterations
            max_inner_iterations: Maximum inner loop iterations per component
            convergence_threshold: Threshold for convergence
            min_improvement: Minimum improvement to continue
        """
        self.max_outer_iterations = max_outer_iterations
        self.max_inner_iterations = max_inner_iterations
        self.convergence_threshold = convergence_threshold
        self.min_improvement = min_improvement
        
        self.refinement_history: List[RefinementIteration] = []
        self.current_performance: Optional[float] = None
        self.cumulative_improvement: float = 0.0
    
    def run_refinement(
        self,
        pipeline: Any,
        data: Tuple[pd.DataFrame, pd.Series],
        components: Dict[str, PipelineComponent],
        ablation_results: Dict[str, AblationResult],
        search_spaces: Dict[str, Dict[str, Any]],
        evaluation_function: Callable,
        component_optimizer: ComponentOptimizer
    ) -> Dict[str, Any]:
        """
        Run the complete two-loop refinement process.
        
        Args:
            pipeline: ML pipeline to optimize
            data: Training data (X, y)
            components: Pipeline components
            ablation_results: Results from ablation study
            search_spaces: Parameter search spaces for each component
            evaluation_function: Performance evaluation function
            component_optimizer: Component optimization engine
            
        Returns:
            Dictionary with refinement results
        """
        X, y = data
        
        # Initialize with baseline performance
        baseline_scores = evaluation_function(pipeline, X, y)
        self.current_performance = np.mean(baseline_scores)
        initial_performance = self.current_performance
        
        logger.info(f"Starting refinement with baseline performance: {self.current_performance:.4f}")
        
        # Outer loop
        for outer_iter in range(self.max_outer_iterations):
            logger.info(f"\n=== Outer Loop Iteration {outer_iter + 1} ===")
            
            # Select target component based on ablation impact
            target_component_id = self._select_target_component(
                ablation_results, self.refinement_history
            )
            
            if not target_component_id:
                logger.info("No suitable target component found")
                break
            
            target_component = components[target_component_id]
            ablation_impact = ablation_results[target_component_id].impact_score
            
            logger.info(f"Target component: {target_component_id} (impact: {ablation_impact:.4f})")
            
            # Inner loop - optimize target component
            inner_improvement = 0.0
            for inner_iter in range(self.max_inner_iterations):
                logger.info(f"  Inner Loop Iteration {inner_iter + 1}")
                
                # Get search space for component
                component_search_space = search_spaces.get(
                    target_component_id,
                    self._get_default_search_space(target_component.component_type)
                )
                
                # Optimize component
                optimization_result = component_optimizer.optimize_component(
                    target_component,
                    pipeline,
                    data,
                    component_search_space,
                    evaluation_function
                )
                
                # Update pipeline with optimized parameters
                if optimization_result.improvement > self.min_improvement:
                    pipeline.set_params(**optimization_result.best_params)
                    self.current_performance = optimization_result.optimized_performance
                    inner_improvement += optimization_result.improvement
                    
                    logger.info(f"    Improvement: {optimization_result.improvement:.4f}")
                else:
                    logger.info("    No significant improvement, ending inner loop")
                    break
            
            # Record refinement iteration
            self.cumulative_improvement = self.current_performance - initial_performance
            
            iteration = RefinementIteration(
                iteration=outer_iter + 1,
                target_component=target_component_id,
                ablation_impact=ablation_impact,
                optimization_result=optimization_result,
                cumulative_improvement=self.cumulative_improvement
            )
            self.refinement_history.append(iteration)
            
            # Check convergence
            if self._check_convergence():
                logger.info("Convergence reached")
                break
        
        # Generate final results
        results = {
            'initial_performance': initial_performance,
            'final_performance': self.current_performance,
            'total_improvement': self.cumulative_improvement,
            'relative_improvement': self.cumulative_improvement / initial_performance,
            'iterations': len(self.refinement_history),
            'optimized_pipeline': pipeline,
            'refinement_history': self.refinement_history
        }
        
        return results
    
    def _select_target_component(
        self,
        ablation_results: Dict[str, AblationResult],
        history: List[RefinementIteration]
    ) -> Optional[str]:
        """Select next component to optimize based on ablation impact."""
        # Get components already optimized
        optimized_components = {iter.target_component for iter in history}
        
        # Sort components by impact, excluding already optimized ones
        candidates = [
            (comp_id, result.impact_score)
            for comp_id, result in ablation_results.items()
            if comp_id not in optimized_components and not result.error
        ]
        
        if not candidates:
            return None
        
        # Sort by impact score
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Return highest impact component
        return candidates[0][0]
    
    def _check_convergence(self) -> bool:
        """Check if refinement has converged."""
        if len(self.refinement_history) < 2:
            return False
        
        # Check recent improvements
        recent_improvements = [
            iter.optimization_result.improvement
            for iter in self.refinement_history[-2:]
        ]
        
        avg_recent_improvement = np.mean(recent_improvements)
        
        return avg_recent_improvement < self.convergence_threshold
    
    def _get_default_search_space(self, component_type: ComponentType) -> Dict[str, Any]:
        """Get default search space for component type."""
        default_spaces = {
            ComponentType.FEATURE_ENGINEERING: {
                'polynomial_degree': [1, 2, 3],
                'scaling_method': ['standard', 'minmax', 'robust']
            },
            ComponentType.MODEL_SELECTION: {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 20, None]
            },
            ComponentType.HYPERPARAMETER_TUNING: {
                'learning_rate': [0.01, 0.1, 0.3],
                'regularization': [0.0, 0.1, 1.0]
            }
        }
        
        return default_spaces.get(component_type, {})
    
    def export_refinement_report(self, output_path: Path):
        """Export detailed refinement report."""
        report = {
            'summary': {
                'initial_performance': self.refinement_history[0].optimization_result.original_performance if self.refinement_history else None,
                'final_performance': self.current_performance,
                'total_improvement': self.cumulative_improvement,
                'iterations': len(self.refinement_history)
            },
            'iterations': []
        }
        
        for iteration in self.refinement_history:
            report['iterations'].append({
                'iteration': iteration.iteration,
                'target_component': iteration.target_component,
                'ablation_impact': iteration.ablation_impact,
                'optimization_improvement': iteration.optimization_result.improvement,
                'cumulative_improvement': iteration.cumulative_improvement,
                'best_params': iteration.optimization_result.best_params
            })
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
    
    def visualize_refinement_progress(self) -> pd.DataFrame:
        """Create DataFrame for visualizing refinement progress."""
        data = []
        
        for iteration in self.refinement_history:
            data.append({
                'Iteration': iteration.iteration,
                'Component': iteration.target_component,
                'Improvement': iteration.optimization_result.improvement,
                'Cumulative': iteration.cumulative_improvement,
                'Performance': iteration.optimization_result.optimized_performance
            })
        
        return pd.DataFrame(data)