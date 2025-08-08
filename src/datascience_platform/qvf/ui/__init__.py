"""QVF User Interface Module

Provides comprehensive user interfaces for QVF configuration and administration.
Includes both admin interfaces and integration utilities.

Components:
- Admin Dashboard: Complete configuration management interface
- Weight Editor: Interactive weight configuration
- API Integration: FastAPI backend integration
- Dashboard Generation: Automated UI generation
"""

from .admin import (
    AdminDashboard,
    ConfigurationManager,
    WeightEditor,
    QVFAdminApp,
    useConfigurations,
    useConfiguration,
    useCreateConfiguration,
    useValidation,
    usePresets,
    useExport
)

from .admin.dashboard_integration import (
    QVFAdminDashboardGenerator,
    QVFAdminConfig,
    generate_qvf_admin_dashboard
)

__all__ = [
    # Main admin components
    'AdminDashboard',
    'ConfigurationManager', 
    'WeightEditor',
    'QVFAdminApp',
    
    # React hooks
    'useConfigurations',
    'useConfiguration',
    'useCreateConfiguration',
    'useValidation',
    'usePresets',
    'useExport',
    
    # Dashboard generation
    'QVFAdminDashboardGenerator',
    'QVFAdminConfig',
    'generate_qvf_admin_dashboard'
]