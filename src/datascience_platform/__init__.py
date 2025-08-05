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