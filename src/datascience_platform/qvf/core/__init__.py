"""QVF Core Module

This module contains the core QVF functionality including criteria configuration,
scoring engines, and financial calculations.
"""

# Core QVF components
from .criteria import (
    QVFCriteriaEngine,
    QVFCriteriaConfiguration,
    QVFCriterion,
    CriteriaCategory,
    CriteriaWeights,
    QVFValidationError
)

from .financial import (
    FinancialCalculator,
    FinancialMetrics,
    NPVCalculation,
    COPQCalculation,
    ROICalculation
)

__all__ = [
    # Criteria system
    "QVFCriteriaEngine",
    "QVFCriteriaConfiguration",
    "QVFCriterion", 
    "CriteriaCategory",
    "CriteriaWeights",
    "QVFValidationError",
    
    # Financial modeling
    "FinancialCalculator",
    "FinancialMetrics",
    "NPVCalculation",
    "COPQCalculation",
    "ROICalculation"
]