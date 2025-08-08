"""QVF Azure DevOps Integration Module

This module provides comprehensive Azure DevOps integration for the
Quantified Value Framework (QVF), including:

- Custom field management and synchronization
- Field lifecycle management and deployment
- Work item type extensions for QVF scores
- REST API client for ADO operations
- Batch processing for enterprise scale
- Configuration management and templates

Key Components:
- CustomFieldsManager: QVF custom field definitions and management
- QVFFieldManager: Enterprise field lifecycle management
- RestClient: ADO REST API integration
- WorkItemUpdater: Batch work item updates
- FieldMapper: Criteria to ADO field mapping

Enterprise Features:
- Support for 10,000+ work items
- Performance optimized batch operations
- Comprehensive error handling and rollback
- Field conflict resolution
- Permission validation
- Multi-project deployment orchestration
- Configuration templates and versioning

Usage:
    from datascience_platform.qvf.ado import CustomFieldsManager, QVFFieldManager
    
    # Low-level field operations
    manager = CustomFieldsManager(organization_url, pat_token)
    await manager.create_qvf_fields(project_name)
    
    # High-level field lifecycle management
    field_manager = QVFFieldManager(organization_url, pat_token)
    deployment = await field_manager.deploy_to_project(project_name, "production")

Requirements:
- Azure DevOps REST API v7.0+
- Project Administrator permissions for field creation
- Contributor permissions for work item updates
"""

from .custom_fields import (
    CustomFieldsManager,
    QVFCustomField,
    QVFFieldDefinition,
    WorkItemTypeFieldMapping,
    FieldOperationResult,
    FieldConflictResolution,
    QVFFieldType,
    QVFFieldScope
)

from .field_manager import (
    QVFFieldManager,
    FieldConfiguration,
    DeploymentPlan,
    FieldManagerError,
    FieldConfigurationLevel,
    DeploymentStage,
    MigrationStrategy
)

from .rest_client import (
    ADORestClient,
    ADOClientConfig,
    ADOApiError,
    ADOAuthenticationError,
    ADOPermissionError
)

from .work_items import (
    WorkItemManager,
    QVFWorkItemScore,
    WorkItemUpdateBatch,
    UpdateResult,
    WorkItemManagementError
)

__all__ = [
    # Custom Fields
    'CustomFieldsManager',
    'QVFCustomField',
    'QVFFieldDefinition', 
    'WorkItemTypeFieldMapping',
    'FieldOperationResult',
    'FieldConflictResolution',
    'QVFFieldType',
    'QVFFieldScope',
    
    # Field Lifecycle Management
    'QVFFieldManager',
    'FieldConfiguration',
    'DeploymentPlan',
    'FieldManagerError',
    'FieldConfigurationLevel',
    'DeploymentStage',
    'MigrationStrategy',
    
    # REST Client
    'ADORestClient',
    'ADOClientConfig',
    'ADOApiError',
    'ADOAuthenticationError',
    'ADOPermissionError',
    
    # Work Items
    'WorkItemManager',
    'QVFWorkItemScore',
    'WorkItemUpdateBatch',
    'UpdateResult',
    'WorkItemManagementError'
]

# Version and metadata
__version__ = "1.1.0"
__author__ = "DataScience Platform Team"
__description__ = "Azure DevOps integration for Quantified Value Framework with enterprise field lifecycle management"
