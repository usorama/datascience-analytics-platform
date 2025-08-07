"""MLE-STAR Inspired ML Pipeline Optimization Module

This module implements an ablation-driven, component-focused optimization approach
inspired by Google's MLE-STAR methodology, adapted for automated ML pipeline improvement
without requiring LLMs.
"""

from .ablation import AblationStudyEngine, ComponentImpactAnalyzer
from .optimizer import ComponentOptimizer, RefinementEngine, OptimizationStrategy
from .repository import MLTechniqueRepository, PerformanceBenchmark
from .pipeline import MLPipelineAnalyzer, PipelineComponent, ComponentType

__all__ = [
    'AblationStudyEngine',
    'ComponentImpactAnalyzer',
    'ComponentOptimizer',
    'RefinementEngine',
    'OptimizationStrategy',
    'MLTechniqueRepository',
    'PerformanceBenchmark',
    'MLPipelineAnalyzer',
    'PipelineComponent',
    'ComponentType'
]

__version__ = "1.0.0"