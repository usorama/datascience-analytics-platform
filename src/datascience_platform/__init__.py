"""DataScience Analytics Platform.

A comprehensive platform for ETL operations, data validation, and analytics.
"""

__version__ = "0.1.0"
__author__ = "DataScience Platform Team"
__email__ = "team@datascience-platform.com"

# Import core modules (optional - may not be available)
try:
    from datascience_platform.core.config import settings
    from datascience_platform.core.exceptions import (
        DataSciencePlatformError,
        ConfigurationError,
        ValidationError,
        ETLError,
    )
    _CORE_AVAILABLE = True
except ImportError:
    settings = None
    DataSciencePlatformError = Exception
    ConfigurationError = Exception
    ValidationError = Exception
    ETLError = Exception
    _CORE_AVAILABLE = False

# Import dashboard module
try:
    from datascience_platform.dashboard import DashboardGenerator, ChartBuilder
    _DASHBOARD_AVAILABLE = True
except ImportError:
    DashboardGenerator = None
    ChartBuilder = None
    _DASHBOARD_AVAILABLE = False

# Import QVF module
try:
    from datascience_platform.qvf import (
        QVFCriteriaEngine,
        QVFCriteriaConfiguration,
        FinancialCalculator,
        create_enterprise_configuration,
        create_agile_configuration,
        is_ai_available
    )
    _QVF_AVAILABLE = True
except ImportError:
    QVFCriteriaEngine = None
    QVFCriteriaConfiguration = None
    FinancialCalculator = None
    create_enterprise_configuration = None
    create_agile_configuration = None
    is_ai_available = None
    _QVF_AVAILABLE = False

__all__ = [
    "__version__",
    "__author__",
    "__email__",
]

# Add core modules if available
if _CORE_AVAILABLE:
    __all__.extend([
        "settings",
        "DataSciencePlatformError",
        "ConfigurationError",
        "ValidationError",
        "ETLError",
    ])

# Add dashboard modules if available
if _DASHBOARD_AVAILABLE:
    __all__.extend([
        "DashboardGenerator",
        "ChartBuilder",
    ])

# Add QVF modules if available
if _QVF_AVAILABLE:
    __all__.extend([
        "QVFCriteriaEngine",
        "QVFCriteriaConfiguration",
        "FinancialCalculator",
        "create_enterprise_configuration",
        "create_agile_configuration",
        "is_ai_available",
    ])