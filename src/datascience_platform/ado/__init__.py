"""Azure DevOps Analytics Module

This module provides specialized functionality for analyzing ADO work items,
implementing the Quantified Value Framework (QVF) with Analytic Hierarchy Process (AHP),
and generating objective prioritization for Agile planning.
"""

from .models import (
    ADOWorkItem,
    Epic,
    PIO,
    Feature,
    UserStory,
    WorkItemHierarchy,
    WorkItemState,
    WorkItemType
)
from .ahp import (
    AHPEngine,
    AHPConfiguration,
    AHPCriterion,
    PairwiseComparison
)
from .metrics import (
    AgileMetricsCalculator,
    PIMetrics,
    TeamMetrics,
    FlowMetrics
)
from .simulation import ADODataSimulator
from .analyzer import ADOAnalyzer
from .data_validator import (
    RobustDataProcessor,
    FilterableDataProcessor,
    DataValidationError
)

__all__ = [
    'ADOWorkItem',
    'Epic',
    'PIO',
    'Feature',
    'UserStory',
    'WorkItemHierarchy',
    'WorkItemState',
    'WorkItemType',
    'AHPEngine',
    'AHPConfiguration',
    'AHPCriterion',
    'PairwiseComparison',
    'AgileMetricsCalculator',
    'PIMetrics',
    'TeamMetrics',
    'FlowMetrics',
    'ADODataSimulator',
    'ADOAnalyzer',
    'RobustDataProcessor',
    'FilterableDataProcessor',
    'DataValidationError'
]

__version__ = "1.0.0"