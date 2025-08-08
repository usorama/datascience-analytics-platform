# QVF Field Manager - Enterprise Field Lifecycle Management

The QVF Field Manager provides enterprise-grade field lifecycle management for QVF custom fields in Azure DevOps, offering configuration-driven deployment, validation, and maintenance operations.

## Overview

The Field Manager extends the basic CustomFieldsManager with high-level orchestration capabilities:

- **Configuration Management**: YAML/JSON-based field configuration with versioning
- **Deployment Orchestration**: Multi-stage deployment with rollback capabilities
- **Field Lifecycle Management**: Complete field lifecycle from creation to retirement
- **Enterprise Scale**: Support for multi-project deployments
- **Validation & Compliance**: Comprehensive pre and post-deployment validation

## Architecture

```
QVFFieldManager
├── Configuration Management
│   ├── FieldConfiguration (models field schemas)
│   ├── Configuration Loading/Saving (YAML/JSON)
│   └── Template Generation (dev/staging/production)
├── Deployment Orchestration
│   ├── DeploymentPlan (tracks deployment lifecycle)
│   ├── Multi-stage Deployment (validation → deployment → verification)
│   └── Rollback Capabilities
├── Field Lifecycle Management
│   ├── Field Creation & Updates
│   ├── Migration Strategies
│   └── Retirement Procedures
└── Integration Layer
    ├── CustomFieldsManager (low-level operations)
    ├── ADORestClient (API access)
    └── Performance Monitoring
```

## Quick Start

### 1. Initialize Field Manager

```python
from datascience_platform.qvf.ado import QVFFieldManager

# Initialize with Azure DevOps credentials
manager = QVFFieldManager(
    organization_url="https://dev.azure.com/myorg",
    personal_access_token="your_pat_token"
)
```

### 2. Deploy Using Default Configuration

```python
# Deploy production-ready QVF fields to a project
deployment_plan = await manager.deploy_to_project(
    project_name="MyProject",
    configuration_name="production",  # Uses built-in production template
    work_item_types=[WorkItemType.EPIC, WorkItemType.FEATURE, WorkItemType.USER_STORY]
)

print(f"Deployment Status: {deployment_plan.current_stage}")
print(f"Fields Deployed: {len(deployment_plan.field_results)}")
```

### 3. Use Custom Configuration

```python
# Load custom configuration from file
config = await manager.load_configuration_from_file("my_qvf_config.yaml")

# Deploy with custom configuration
deployment_plan = await manager.deploy_to_project(
    project_name="CustomProject",
    configuration_name="my_custom_config",
    dry_run=False  # Set to True for validation-only
)
```

## Configuration Management

### Configuration Levels

The Field Manager supports multiple configuration levels:

- **Development**: Minimal fields for development and testing
- **Staging**: Extended fields for pre-production validation
- **Production**: Complete field set for production deployment
- **Enterprise**: Full enterprise deployment with all features

### Configuration File Format

```yaml
# QVF Field Configuration
name: "my_qvf_config"
version: "1.0.0"
description: "Custom QVF configuration"
level: "production"

# Field definitions
field_definitions:
  QVF.Score:
    field_type: "decimal"
    display_name: "QVF Score"
    description: "Overall QVF prioritization score"
    min_value: 0.0
    max_value: 1.0
    precision: 4
    is_required: false
    default_value: 0.0

# Work item mappings
work_item_mappings:
  Epic:
    applicable_fields: ["QVF.Score"]
    required_fields: ["QVF.Score"]
    field_order: ["QVF.Score"]

# Deployment settings
deployment_settings:
  batch_size: 100
  timeout_seconds: 300
  enable_rollback: true
```

### Built-in Templates

```python
# Get built-in configuration templates
dev_config = manager.get_default_field_configuration(FieldConfigurationLevel.DEVELOPMENT)
staging_config = manager.get_default_field_configuration(FieldConfigurationLevel.STAGING)
prod_config = manager.get_default_field_configuration(FieldConfigurationLevel.PRODUCTION)

# Save template for customization
await manager.save_configuration_to_file("production", "my_prod_template.yaml")
```

## Deployment Orchestration

### Deployment Stages

Each deployment follows a structured lifecycle:

1. **Planning**: Initialize deployment plan and validate inputs
2. **Validation**: Pre-deployment validation (permissions, conflicts, etc.)
3. **Deployment**: Field creation and work item type configuration
4. **Verification**: Post-deployment validation and integrity checks
5. **Completion**: Finalization and statistics collection

### Deployment Options

```python
# Standard deployment
deployment = await manager.deploy_to_project(
    project_name="MyProject",
    configuration_name="production",
    work_item_types=[WorkItemType.EPIC, WorkItemType.FEATURE],
    conflict_resolution=FieldConflictResolution.SKIP,
    dry_run=False
)

# Dry run (validation only)
validation = await manager.deploy_to_project(
    project_name="MyProject",
    configuration_name="production",
    dry_run=True
)

# Check deployment status
status = manager.get_deployment_status(deployment.plan_id)
print(f"Current stage: {status['current_stage']}")
print(f"Success rate: {status['success_rate']:.1%}")
```

### Deployment Results

```python
# Get deployment summary
summary = deployment_plan.get_deployment_summary()
print(f"Fields processed: {summary['fields_processed']}")
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Duration: {summary['duration_seconds']:.2f}s")

# Check individual field results
for field_name, result in deployment_plan.field_results.items():
    if result.is_successful:
        print(f"✓ {field_name}: {result.message}")
    else:
        print(f"✗ {field_name}: {result.errors}")
```

## Field Definitions

### Complete QVF Field Set

The Field Manager supports all QVF scoring components:

#### Core Scoring Fields
- **QVF.Score**: Overall prioritization score (0.0-1.0)
- **QVF.BusinessValue**: Business value component score
- **QVF.StrategicAlignment**: Strategic alignment component score
- **QVF.CustomerValue**: Customer value component score

#### Complexity and Risk Fields
- **QVF.Complexity**: Implementation complexity score
- **QVF.RiskScore**: Risk assessment score

#### Metadata Fields
- **QVF.LastCalculated**: Calculation timestamp
- **QVF.ConfigurationId**: Configuration identifier
- **QVF.Confidence**: Score confidence level
- **QVF.DataQuality**: Data quality assessment

### Work Item Type Mappings

Fields are mapped to work item types based on their relevance:

| Work Item Type | Core Fields | Extended Fields | Metadata Fields |
|----------------|-------------|-----------------|-----------------|
| Epic | All scoring fields | Risk, Confidence | All metadata |
| Feature | Most scoring fields | Complexity | All metadata |  
| User Story | Basic scoring fields | Customer Value | Basic metadata |
| PIO | Strategic fields | Risk | Basic metadata |

## Advanced Features

### Configuration Management

```python
# List all loaded configurations
configurations = manager.list_configurations()
for name, info in configurations.items():
    print(f"{name}: {info['version']} ({info['level']})")

# Load configuration from different sources
yaml_config = await manager.load_configuration_from_file("config.yaml")
json_config = await manager.load_configuration_from_file("config.json")

# Save configurations in different formats
await manager.save_configuration_to_file("my_config", "output.yaml")
await manager.save_configuration_to_file("my_config", "output.json")
```

### Performance Monitoring

```python
# Get operation statistics
stats = manager.get_operation_statistics()
print(f"Deployments completed: {stats['deployments_completed']}")
print(f"Average deployment time: {stats['avg_deployment_time']:.2f}s")
print(f"Configurations loaded: {stats['configurations_loaded']}")
```

### Error Handling

```python
from datascience_platform.qvf.ado import FieldManagerError

try:
    deployment = await manager.deploy_to_project("MyProject", "production")
    
    if deployment.current_stage == DeploymentStage.FAILED:
        print(f"Deployment failed: {deployment.stage_history[-1][2]}")
        
        # Check individual field errors
        for field_name, result in deployment.field_results.items():
            if not result.is_successful:
                print(f"Field {field_name} errors: {result.errors}")
    
except FieldManagerError as e:
    print(f"Field manager error: {e}")
```

## Migration and Maintenance

### Field Schema Migration

```python
# Future capability - field schema migration
migration_plan = await manager.plan_schema_migration(
    project_name="MyProject",
    from_version="1.0.0",
    to_version="2.0.0"
)

# Execute migration with rollback capability
migration_result = await manager.execute_migration(migration_plan)
```

### Field Retirement

```python
# Clean up deprecated fields (use with caution)
cleanup_results = await manager.custom_fields_manager.cleanup_qvf_fields(
    project_name="MyProject",
    field_names=["QVF.DeprecatedField"],
    confirm_deletion=True
)
```

## Integration Examples

### CI/CD Integration

```python
# Automated deployment in CI/CD pipeline
async def deploy_qvf_fields(project_name: str, environment: str):
    manager = QVFFieldManager(
        organization_url=os.environ["ADO_ORG_URL"],
        personal_access_token=os.environ["ADO_PAT"]
    )
    
    # Load environment-specific configuration
    config_file = f"qvf_config_{environment}.yaml"
    await manager.load_configuration_from_file(config_file)
    
    # Deploy with validation
    deployment = await manager.deploy_to_project(
        project_name=project_name,
        configuration_name=environment,
        dry_run=environment == "production"  # Dry run for production
    )
    
    if not deployment.current_stage == DeploymentStage.COMPLETION:
        raise Exception(f"Deployment failed: {deployment.stage_history[-1][2]}")
    
    return deployment.get_deployment_summary()
```

### Multi-Project Deployment

```python
# Deploy to multiple projects
async def deploy_to_multiple_projects(projects: List[str]):
    manager = QVFFieldManager(org_url, pat_token)
    
    results = {}
    for project in projects:
        try:
            deployment = await manager.deploy_to_project(
                project_name=project,
                configuration_name="enterprise"
            )
            results[project] = deployment.get_deployment_summary()
        except Exception as e:
            results[project] = {"error": str(e)}
    
    return results
```

## Best Practices

### 1. Configuration Management
- Use version control for configuration files
- Test configurations in development environments first
- Use configuration templates for consistency across projects

### 2. Deployment Safety
- Always run dry-run deployments first in production
- Use staging environments for validation
- Monitor deployment results and maintain rollback plans

### 3. Performance Optimization
- Use appropriate batch sizes for large deployments
- Monitor API rate limits and adjust concurrent requests
- Cache configurations to avoid repeated loading

### 4. Error Handling
- Implement comprehensive error handling for all operations
- Log deployment results for audit and troubleshooting
- Use validation results to prevent deployment issues

### 5. Security and Compliance
- Use secure credential management for PAT tokens
- Validate permissions before deployment
- Maintain audit logs for compliance requirements

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Ensure PAT token has Project Administrator permissions
   - Verify organization URL is correct
   - Check project access permissions

2. **Field Creation Failures**
   - Validate field definitions in configuration
   - Check for field name conflicts
   - Verify work item type mappings

3. **Deployment Timeouts**
   - Increase timeout settings in configuration
   - Reduce batch size for large deployments
   - Check Azure DevOps service availability

4. **Configuration Errors**
   - Validate YAML/JSON syntax
   - Check required field definitions
   - Verify work item type names match ADO

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for troubleshooting
manager = QVFFieldManager(org_url, pat_token)
deployment = await manager.deploy_to_project(project, "production", dry_run=True)
```

This comprehensive field management system provides enterprise-grade capabilities for QVF field deployment and maintenance across Azure DevOps projects, ensuring consistency, reliability, and scalability for large-scale implementations.