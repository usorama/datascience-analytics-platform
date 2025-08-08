"""Unit tests for QVF module.

This package contains comprehensive unit tests for the Quantified Value
Framework (QVF) components including criteria configuration, financial
calculations, and scoring engines.
"""

# Test utilities and fixtures
from .test_fixtures import (
    create_test_work_item,
    create_test_criteria_config,
    create_test_financial_metrics
)

__all__ = [
    "create_test_work_item",
    "create_test_criteria_config", 
    "create_test_financial_metrics"
]