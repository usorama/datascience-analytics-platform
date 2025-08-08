"""Quantified Value Framework (QVF) for Enterprise Prioritization

This module provides the Quantified Value Framework - an enterprise-grade
prioritization system built on mathematical AHP foundations with optional
AI enhancement. QVF enables objective, measurable prioritization for
Agile Release Trains and PI Planning.

Key Features:
- Mathematical foundation using AHP (Analytic Hierarchy Process)
- Comprehensive criteria framework with 20+ dimensions
- Azure DevOps integration for seamless workflow
- Optional AI enhancement with fallback to mathematical methods
- Real-time scoring for 10,000+ work items
- Executive, Product Owner, and Priority dashboards

Core Components:
- QVFCriteriaEngine: Core criteria configuration and validation
- FinancialCalculator: NPV, COPQ, and ROI calculations
- EnhancedAHPScoring: Advanced AHP with QVF enhancements
- AdminInterface: Configuration and stakeholder management
- QVFOrchestrator: End-to-end workflow automation

Usage:
    from datascience_platform.qvf import QVFCriteriaEngine
    
    criteria_engine = QVFCriteriaEngine()
    criteria_config = criteria_engine.get_default_configuration()
    scores = criteria_engine.score_work_items(work_items, criteria_config)

Architecture:
    QVF leverages the existing AHP engine (80% complete) and extends it
    with enterprise-specific criteria and financial modeling. The system
    is designed for <60 second calculations on large portfolios with
    <2 second failover when AI features are unavailable.
"""

from .core.criteria import (
    QVFCriteriaEngine,
    QVFCriteriaConfiguration,
    QVFCriterion,
    CriteriaCategory,
    CriteriaWeights,
    QVFValidationError,
    create_agile_configuration,
    create_enterprise_configuration,
    create_startup_configuration
)

from .core.financial import (
    FinancialCalculator,
    FinancialMetrics,
    NPVCalculation,
    COPQCalculation,
    ROICalculation
)

# Optional AI Enhancement Module
try:
    from .ai import (
        OllamaManager,
        SemanticAnalyzer,
        FallbackEngine,
        QVFPromptTemplates,
        AnalysisType,
        SemanticAnalysisResult,
        BatchAnalysisResult
    )
    _AI_AVAILABLE = True
except ImportError:
    # AI module dependencies not available
    _AI_AVAILABLE = False
    OllamaManager = None
    SemanticAnalyzer = None
    FallbackEngine = None
    QVFPromptTemplates = None
    AnalysisType = None
    SemanticAnalysisResult = None
    BatchAnalysisResult = None

__version__ = "1.0.0"
__author__ = "DataScience Platform Team"
__description__ = "Quantified Value Framework for Enterprise Prioritization"

# Core exports for external use
# Base exports - always available
_base_exports = [
    # Core criteria system
    "QVFCriteriaEngine",
    "QVFCriteriaConfiguration", 
    "QVFCriterion",
    "CriteriaCategory",
    "CriteriaWeights",
    "QVFValidationError",
    
    # Factory functions
    "create_agile_configuration",
    "create_enterprise_configuration",
    "create_startup_configuration",
    
    # Financial modeling
    "FinancialCalculator",
    "FinancialMetrics",
    "NPVCalculation",
    "COPQCalculation",
    "ROICalculation",
    
    # Module metadata
    "__version__",
    "__author__",
    "__description__",
    "is_ai_available"
]

# AI exports - conditionally available
_ai_exports = [
    "OllamaManager",
    "SemanticAnalyzer",
    "FallbackEngine",
    "QVFPromptTemplates",
    "AnalysisType",
    "SemanticAnalysisResult",
    "BatchAnalysisResult"
]

# Combine exports based on AI availability
__all__ = _base_exports + (_ai_exports if _AI_AVAILABLE else [])

# Module constants
DEFAULT_CONSISTENCY_THRESHOLD = 0.10
MAX_CRITERIA_COUNT = 25
MIN_CRITERIA_COUNT = 3
DEFAULT_CALCULATION_TIMEOUT = 60  # seconds
DEFAULT_FALLBACK_TIMEOUT = 2     # seconds

# AI module configuration
AI_ENABLED = _AI_AVAILABLE
DEFAULT_AI_TIMEOUT = 30          # seconds
DEFAULT_CACHE_TTL = 3600         # seconds
DEFAULT_MAX_CONCURRENT = 5       # concurrent analyses

def is_ai_available() -> bool:
    """Check if AI enhancement module is available.
    
    Returns:
        bool: True if AI module is available and can be used
    """
    return _AI_AVAILABLE

def get_ai_status() -> dict:
    """Get detailed AI module status.
    
    Returns:
        dict: Status information including availability and dependencies
    """
    if not _AI_AVAILABLE:
        return {
            "available": False,
            "reason": "AI module dependencies not installed",
            "ollama_available": False,
            "fallback_available": True
        }
    
    try:
        from .ai import OllamaManager
        manager = OllamaManager()
        health = manager.get_health_status()
        
        return {
            "available": True,
            "ollama_available": manager.is_available(),
            "ollama_status": health["status"],
            "available_models": health["available_models"],
            "fallback_available": True
        }
    except Exception as e:
        return {
            "available": True,
            "ollama_available": False,
            "ollama_error": str(e),
            "fallback_available": True
        }

def create_semantic_analyzer(**kwargs):
    """Create a semantic analyzer instance.
    
    Args:
        **kwargs: Arguments passed to SemanticAnalyzer constructor
        
    Returns:
        SemanticAnalyzer: Configured analyzer instance
        
    Raises:
        ImportError: If AI module is not available
    """
    if not _AI_AVAILABLE:
        raise ImportError(
            "AI enhancement module not available. Install with: "
            "pip install -r requirements-nlp.txt"
        )
    
    from .ai import SemanticAnalyzer
    return SemanticAnalyzer(**kwargs)