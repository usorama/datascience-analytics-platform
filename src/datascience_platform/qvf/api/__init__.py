"""QVF API Module

FastAPI endpoints for QVF configuration management and real-time administration.
Provides RESTful APIs for the QVF admin interface.

Endpoints:
- Configuration CRUD operations
- Real-time validation
- Configuration export/import
- Preset management
"""

from .config_api import router as config_router

__all__ = ['config_router']