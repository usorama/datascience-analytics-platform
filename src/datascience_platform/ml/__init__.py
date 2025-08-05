"""Machine Learning Insights Generation Engine

This module provides comprehensive ML capabilities for the DataScience Analytics Platform,
including automated statistics, pattern detection, AutoML integration, and model explanations.
"""

from .statistics import StatisticsEngine
from .patterns import PatternDetector
from .automl import AutoMLEngine
from .insights import InsightGenerator
from .explainer import ModelExplainer

__all__ = [
    'StatisticsEngine',
    'PatternDetector', 
    'AutoMLEngine',
    'InsightGenerator',
    'ModelExplainer'
]

__version__ = "1.0.0"