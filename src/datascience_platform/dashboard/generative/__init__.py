"""Generative Dashboard Module

This module provides automatic dashboard generation from ML outputs,
creating TypeScript/React components with dynamic filters and visualizations.
"""

from .generator import DashboardGenerator, DashboardConfig
from .analyzer import DataAnalyzer, VisualizationRecommender
from .components import ComponentGenerator, FilterGenerator
from .optimizer import MLOutputOptimizer, OptimizationStatus

__all__ = [
    'DashboardGenerator',
    'DashboardConfig',
    'DataAnalyzer',
    'VisualizationRecommender',
    'ComponentGenerator',
    'FilterGenerator',
    'MLOutputOptimizer',
    'OptimizationStatus'
]

__version__ = "1.0.0"