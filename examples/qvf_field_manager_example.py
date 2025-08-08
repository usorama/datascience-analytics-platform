#!/usr/bin/env python3
"""QVF Field Manager Example

This example demonstrates how to use the QVF Field Manager for enterprise-grade
field lifecycle management in Azure DevOps projects.

The script shows:
1. Field manager initialization
2. Configuration management (loading, saving, templates)
3. Field deployment orchestration
4. Validation and error handling
5. Performance monitoring

Usage:
    python examples/qvf_field_manager_example.py
    
Requirements:
    - Azure DevOps organization and project
    - Personal Access Token with Project Administrator permissions
    - QVF platform installation
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datascience_platform.qvf.ado import (
    QVFFieldManager,
    FieldConfiguration, 
    FieldConfigurationLevel,
    DeploymentStage,
    FieldConflictResolution,
    FieldManagerError
)
from datascience_platform.ado.models import WorkItemType


async def demonstrate_field_manager():
    """Demonstrate QVF Field Manager capabilities."""
    
    print("🚀 QVF Field Manager Demonstration")
    print("=" * 50)
    
    # Configuration (replace with your ADO details)
    organization_url = os.environ.get("ADO_ORG_URL", "https://dev.azure.com/your-org")
    personal_access_token = os.environ.get("ADO_PAT", "your-pat-token")
    project_name = os.environ.get("ADO_PROJECT", "YourProject")
    
    if "your-" in organization_url or "your-" in personal_access_token or "Your" in project_name:
        print("⚠️  Please set environment variables:")
        print("   export ADO_ORG_URL='https://dev.azure.com/your-org'")
        print("   export ADO_PAT='your-personal-access-token'")
        print("   export ADO_PROJECT='YourProjectName'")
        print("\nRunning in demo mode with mock data...")
        await run_demo_mode()
        return
    
    try:
        # Initialize Field Manager
        print("1. Initializing QVF Field Manager...")
        manager = QVFFieldManager(
            organization_url=organization_url,
            personal_access_token=personal_access_token
        )
        print("   ✅ Field Manager initialized")
        
        # Demonstrate configuration management
        await demonstrate_configuration_management(manager)
        
        # Demonstrate deployment orchestration
        await demonstrate_deployment_orchestration(manager, project_name)
        
        # Show performance statistics
        show_performance_statistics(manager)
        
        # Clean up
        await manager.cleanup_workspace()
        print("\n🎉 Demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


async def demonstrate_configuration_management(manager: QVFFieldManager):
    """Demonstrate configuration management features."""
    
    print("\n2. Configuration Management")
    print("-" * 30)
    
    # Show built-in configuration templates
    print("📋 Available configuration levels:")
    for level in FieldConfigurationLevel:
        config = manager.get_default_field_configuration(level)
        print(f"   • {level.value}: {len(config.field_definitions)} fields, "
              f"{len(config.work_item_mappings)} work item types")
    
    # Create and save a custom configuration
    print("\n📄 Creating custom configuration...")
    custom_config = manager.get_default_field_configuration(FieldConfigurationLevel.STAGING)
    custom_config.name = "demo_custom_config"
    custom_config.version = "1.1.0"
    custom_config.description = "Custom configuration for demonstration"
    custom_config.tags = ["demo", "example", "custom"]
    
    manager.configurations["demo_custom"] = custom_config
    
    # Save configuration to file
    config_file = Path("demo_qvf_config.yaml")
    try:
        success = await manager.save_configuration_to_file("demo_custom", str(config_file))
        if success and config_file.exists():
            print(f"   ✅ Configuration saved to {config_file}")
            
            # Load it back to demonstrate loading
            loaded_config = await manager.load_configuration_from_file(
                str(config_file), "demo_loaded"
            )
            print(f"   ✅ Configuration loaded: {loaded_config.name} v{loaded_config.version}")
        else:
            print("   ⚠️  Configuration saving skipped (file system access)")
    except Exception as e:
        print(f"   ⚠️  Configuration file operations skipped: {e}")
    finally:
        # Clean up demo file
        if config_file.exists():
            config_file.unlink()
    
    # List all configurations
    print("\n📊 Loaded configurations:")
    configurations = manager.list_configurations()
    for name, info in configurations.items():
        print(f"   • {name}: v{info['version']} ({info['level']}) - {info['field_count']} fields")


async def demonstrate_deployment_orchestration(manager: QVFFieldManager, project_name: str):
    """Demonstrate deployment orchestration features."""
    
    print(f"\n3. Deployment Orchestration (Project: {project_name})")
    print("-" * 50)
    
    # Demonstrate dry run deployment (validation only)
    print("🔍 Running dry-run deployment (validation only)...")
    try:
        dry_run_deployment = await manager.deploy_to_project(
            project_name=project_name,
            configuration_name="development",  # Use minimal development configuration
            work_item_types=[WorkItemType.USER_STORY],  # Single work item type for demo
            conflict_resolution=FieldConflictResolution.SKIP,
            dry_run=True
        )
        
        # Show deployment results
        summary = dry_run_deployment.get_deployment_summary()
        print(f"   ✅ Dry run completed: {summary['current_stage']}")
        print(f"   📊 Validation results: {len(summary['stage_history'])} stages")
        
        # Show stage history
        print("   📋 Deployment stages:")
        for stage_info in summary['stage_history']:
            stage_name = stage_info['stage'].replace('_', ' ').title()
            print(f"      • {stage_name}: {stage_info.get('note', 'Completed')}")
        
        # Show validation results
        if dry_run_deployment.validation_results:
            validation = dry_run_deployment.validation_results
            if validation.get('is_valid', False):
                print("   ✅ Pre-deployment validation passed")
                checks = validation.get('checks_performed', [])
                print(f"      Performed {len(checks)} validation checks")
            else:
                print("   ⚠️  Pre-deployment validation issues found:")
                for error in validation.get('errors', []):
                    print(f"      • {error}")
        
    except FieldManagerError as e:
        print(f"   ⚠️  Deployment validation completed with issues: {e}")
    except Exception as e:
        print(f"   ℹ️  Deployment demo skipped (requires ADO access): {e}")


async def run_demo_mode():
    """Run demonstration in offline mode without ADO connection."""
    
    print("\n🔧 Running in demo mode (no ADO connection)")
    print("-" * 40)
    
    # Create manager without real credentials
    try:
        manager = QVFFieldManager(
            organization_url="https://dev.azure.com/demo-org",
            personal_access_token="demo-token"
        )
        
        # Demonstrate configuration templates
        print("📋 Configuration Templates:")
        for level in FieldConfigurationLevel:
            config = manager.get_default_field_configuration(level)
            print(f"   • {level.value.title()}: {len(config.field_definitions)} fields")
            
            # Show some sample fields for production level
            if level == FieldConfigurationLevel.PRODUCTION:
                print("     Sample fields:")
                for i, (field_name, field_def) in enumerate(config.field_definitions.items()):
                    if i < 3:  # Show first 3 fields
                        print(f"       - {field_name}: {field_def['description'][:50]}...")
                    elif i == 3:
                        print(f"       ... and {len(config.field_definitions) - 3} more fields")
                        break
        
        # Show work item type mappings
        prod_config = manager.get_default_field_configuration(FieldConfigurationLevel.PRODUCTION)
        print(f"\n📊 Work Item Type Mappings (Production):")
        for wit_type, mapping in prod_config.work_item_mappings.items():
            field_count = len(mapping.get('applicable_fields', []))
            required_count = len(mapping.get('required_fields', []))
            print(f"   • {wit_type}: {field_count} fields ({required_count} required)")
        
        # Show configuration validation
        print(f"\n✅ Configuration Validation:")
        is_valid, errors = prod_config.validate()
        print(f"   • Production config valid: {is_valid}")
        if errors:
            for error in errors:
                print(f"     - Error: {error}")
        
        # Show serialization capability
        print(f"\n💾 Configuration Serialization:")
        config_dict = prod_config.to_dict()
        print(f"   • Serialized size: {len(str(config_dict))} characters")
        print(f"   • Field definitions: {len(config_dict['field_definitions'])}")
        print(f"   • Work item mappings: {len(config_dict['work_item_mappings'])}")
        
        print("\n🎯 Demo completed! To run with real ADO integration:")
        print("   1. Set up Azure DevOps organization and project")
        print("   2. Create Personal Access Token with Project Administrator permissions")
        print("   3. Set environment variables (ADO_ORG_URL, ADO_PAT, ADO_PROJECT)")
        print("   4. Run script again for full demonstration")
        
    except Exception as e:
        print(f"❌ Demo mode error: {e}")


def show_performance_statistics(manager: QVFFieldManager):
    """Show performance statistics and monitoring information."""
    
    print("\n4. Performance Statistics")
    print("-" * 30)
    
    stats = manager.get_operation_statistics()
    
    print("📊 Operation Statistics:")
    print(f"   • Configurations loaded: {stats.get('configurations_loaded', 0)}")
    print(f"   • Deployments completed: {stats.get('deployments_completed', 0)}")
    print(f"   • Active configurations: {stats.get('configurations_active', 0)}")
    print(f"   • Active deployments: {stats.get('deployments_active', 0)}")
    
    if stats.get('total_operation_time', 0) > 0:
        print(f"   • Total operation time: {stats['total_operation_time']:.2f}s")
        print(f"   • Average deployment time: {stats.get('avg_deployment_time', 0):.2f}s")
    
    print(f"   • Workspace directory: {stats.get('workspace_directory', 'Not set')}")
    
    # Show field manager integration stats
    fields_manager_stats = {k: v for k, v in stats.items() if k.startswith('fields_manager_')}
    if fields_manager_stats:
        print("📋 Field Operations:")
        for key, value in fields_manager_stats.items():
            clean_key = key.replace('fields_manager_', '').replace('_', ' ').title()
            print(f"   • {clean_key}: {value}")


def show_usage_examples():
    """Show usage examples for different scenarios."""
    
    print("\n5. Usage Examples")
    print("-" * 20)
    
    examples = [
        {
            "name": "Basic Deployment",
            "code": '''
# Deploy QVF fields to project
manager = QVFFieldManager(org_url, pat_token)
deployment = await manager.deploy_to_project("MyProject", "production")
print(f"Status: {deployment.current_stage}")
'''
        },
        {
            "name": "Custom Configuration",
            "code": '''
# Load and use custom configuration
await manager.load_configuration_from_file("my_config.yaml")
deployment = await manager.deploy_to_project("MyProject", "my_custom_config")
'''
        },
        {
            "name": "Multi-Project Deployment",
            "code": '''
# Deploy to multiple projects
projects = ["ProjectA", "ProjectB", "ProjectC"]
for project in projects:
    deployment = await manager.deploy_to_project(project, "enterprise")
    print(f"{project}: {deployment.current_stage}")
'''
        }
    ]
    
    for example in examples:
        print(f"\n📝 {example['name']}:")
        print(f"```python{example['code']}```")


if __name__ == "__main__":
    print("QVF Field Manager Example")
    print("This example demonstrates enterprise-grade field lifecycle management")
    print("for QVF custom fields in Azure DevOps projects.\n")
    
    # Run the demonstration
    asyncio.run(demonstrate_field_manager())