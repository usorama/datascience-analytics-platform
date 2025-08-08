"""Comprehensive tests for QVF Field Manager.

This module provides extensive unit and integration tests for the
QVF field lifecycle management system including configuration management,
deployment orchestration, validation, and migration operations.

Test Coverage:
- FieldConfiguration model validation and serialization
- DeploymentPlan lifecycle and state management
- QVFFieldManager initialization and configuration loading
- Multi-project deployment with rollback scenarios
- Configuration template management
- Performance and scalability testing
- Error handling and recovery scenarios
- Integration with CustomFieldsManager

Usage:
    python -m pytest src/datascience_platform/qvf/ado/tests/test_field_manager.py -v
    
    # Run with coverage
    python -m pytest src/datascience_platform/qvf/ado/tests/test_field_manager.py --cov=src/datascience_platform/qvf/ado/field_manager

Test Organization:
- TestFieldConfiguration: Configuration model and validation tests
- TestDeploymentPlan: Deployment plan lifecycle and tracking tests
- TestQVFFieldManager: Main field manager functionality tests
- TestConfigurationManagement: Configuration loading and saving tests
- TestDeploymentOrchestration: End-to-end deployment tests
- TestPerformanceAndScaling: Performance and scalability tests
"""

import pytest
import asyncio
import tempfile
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from typing import Dict, List, Any, Optional

# Test imports
from src.datascience_platform.qvf.ado.field_manager import (
    QVFFieldManager,
    FieldConfiguration,
    DeploymentPlan,
    FieldManagerError,
    FieldConfigurationLevel,
    DeploymentStage,
    MigrationStrategy
)

from src.datascience_platform.qvf.ado.custom_fields import (
    CustomFieldsManager,
    FieldOperationResult,
    FieldConflictResolution,
    QVFFieldType
)

from src.datascience_platform.ado.models import WorkItemType


class TestFieldConfiguration:
    """Test FieldConfiguration model and validation."""
    
    def test_field_configuration_creation(self):
        """Test basic field configuration creation."""
        config = FieldConfiguration(
            name="test_config",
            version="1.0.0",
            description="Test configuration",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={"QVF.Score": {"field_type": "decimal"}},
            work_item_mappings={"User Story": {"applicable_fields": ["QVF.Score"]}}
        )
        
        assert config.name == "test_config"
        assert config.version == "1.0.0"
        assert config.level == FieldConfigurationLevel.DEVELOPMENT
        assert config.created_date is not None
        assert config.last_modified is not None
    
    def test_field_configuration_validation_success(self):
        """Test successful field configuration validation."""
        config = FieldConfiguration(
            name="valid_config",
            version="1.0.0",
            description="Valid test configuration",
            level=FieldConfigurationLevel.PRODUCTION,
            field_definitions={
                "QVF.Score": {
                    "field_type": "decimal",
                    "display_name": "QVF Score"
                }
            },
            work_item_mappings={
                "Epic": {
                    "applicable_fields": ["QVF.Score"]
                }
            }
        )
        
        is_valid, errors = config.validate()
        assert is_valid
        assert len(errors) == 0
    
    def test_field_configuration_validation_failures(self):
        """Test field configuration validation failures."""
        # Missing name
        config1 = FieldConfiguration(
            name="",
            version="1.0.0",
            description="Invalid config",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={},
            work_item_mappings={}
        )
        
        is_valid, errors = config1.validate()
        assert not is_valid
        assert any("Configuration name is required" in str(error) for error in errors)
        assert any("Field definitions are required" in str(error) for error in errors)
        
        # Invalid field definitions
        config2 = FieldConfiguration(
            name="invalid_fields",
            version="1.0.0",
            description="Invalid field definitions",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={
                "QVF.Score": {}  # Missing required fields
            },
            work_item_mappings={
                "Epic": {
                    "applicable_fields": ["QVF.Score", "QVF.NonExistent"]  # References undefined field
                }
            }
        )
        
        is_valid, errors = config2.validate()
        assert not is_valid
        assert any("QVF.Score missing field_type" in str(error) for error in errors)
        assert any("undefined fields" in str(error) for error in errors)
    
    def test_field_configuration_serialization(self):
        """Test field configuration to/from dict conversion."""
        original_config = FieldConfiguration(
            name="serialize_test",
            version="2.1.0",
            description="Serialization test",
            level=FieldConfigurationLevel.STAGING,
            field_definitions={"QVF.Score": {"field_type": "decimal"}},
            work_item_mappings={"Feature": {"applicable_fields": ["QVF.Score"]}},
            tags=["test", "serialization"]
        )
        
        # Convert to dict
        config_dict = original_config.to_dict()
        assert config_dict["name"] == "serialize_test"
        assert config_dict["version"] == "2.1.0"
        assert config_dict["level"] == FieldConfigurationLevel.STAGING
        assert isinstance(config_dict["created_date"], str)
        assert isinstance(config_dict["last_modified"], str)
        
        # Convert back from dict
        restored_config = FieldConfiguration.from_dict(config_dict)
        assert restored_config.name == original_config.name
        assert restored_config.version == original_config.version
        assert restored_config.level == original_config.level
        assert restored_config.tags == original_config.tags
        assert isinstance(restored_config.created_date, datetime)
        assert isinstance(restored_config.last_modified, datetime)


class TestDeploymentPlan:
    """Test DeploymentPlan lifecycle and state management."""
    
    def test_deployment_plan_creation(self):
        """Test deployment plan initialization."""
        config = FieldConfiguration(
            name="test_deploy",
            version="1.0.0",
            description="Test deployment",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={"QVF.Score": {"field_type": "decimal"}},
            work_item_mappings={"User Story": {"applicable_fields": ["QVF.Score"]}}
        )
        
        plan = DeploymentPlan(
            plan_id="test_plan_123",
            project_name="TestProject",
            configuration=config,
            target_work_item_types=[WorkItemType.USER_STORY],
            dry_run=True
        )
        
        assert plan.plan_id == "test_plan_123"
        assert plan.project_name == "TestProject"
        assert plan.current_stage == DeploymentStage.PLANNING
        assert plan.dry_run is True
        assert len(plan.stage_history) == 1  # Initial PLANNING stage
    
    def test_deployment_plan_stage_transitions(self):
        """Test deployment plan stage transitions."""
        config = FieldConfiguration(
            name="stage_test",
            version="1.0.0",
            description="Stage transition test",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={"QVF.Score": {"field_type": "decimal"}},
            work_item_mappings={"User Story": {"applicable_fields": ["QVF.Score"]}}
        )
        
        plan = DeploymentPlan(
            plan_id="stage_test_plan",
            project_name="StageTest",
            configuration=config,
            target_work_item_types=[WorkItemType.USER_STORY]
        )
        
        # Test stage transitions
        plan._record_stage_transition(DeploymentStage.VALIDATION, "Starting validation")
        assert plan.current_stage == DeploymentStage.VALIDATION
        assert len(plan.stage_history) == 2
        
        plan._record_stage_transition(DeploymentStage.DEPLOYMENT, "Starting deployment")
        plan._record_stage_transition(DeploymentStage.COMPLETION, "Deployment completed")
        
        assert plan.current_stage == DeploymentStage.COMPLETION
        assert len(plan.stage_history) == 4
        
        # Verify stage history order
        stages_only = [stage for stage, _, _ in plan.stage_history]
        assert stages_only == [
            DeploymentStage.PLANNING,
            DeploymentStage.VALIDATION,
            DeploymentStage.DEPLOYMENT,
            DeploymentStage.COMPLETION
        ]
    
    def test_deployment_plan_summary(self):
        """Test deployment plan summary generation."""
        config = FieldConfiguration(
            name="summary_test",
            version="1.0.0",
            description="Summary test",
            level=FieldConfigurationLevel.DEVELOPMENT,
            field_definitions={"QVF.Score": {"field_type": "decimal"}},
            work_item_mappings={"User Story": {"applicable_fields": ["QVF.Score"]}}
        )
        
        plan = DeploymentPlan(
            plan_id="summary_test_plan",
            project_name="SummaryTest",
            configuration=config,
            target_work_item_types=[WorkItemType.USER_STORY]
        )
        
        # Add some mock results
        plan.field_results["QVF.Score"] = FieldOperationResult(
            success=True,
            operation="create",
            field_name="QVF.Score",
            message="Field created successfully"
        )
        
        plan.start_time = datetime.now(timezone.utc)
        plan.end_time = plan.start_time
        plan._record_stage_transition(DeploymentStage.COMPLETION, "Completed")
        
        summary = plan.get_deployment_summary()
        
        assert summary["plan_id"] == "summary_test_plan"
        assert summary["project_name"] == "SummaryTest"
        assert summary["configuration_name"] == "summary_test"
        assert summary["configuration_version"] == "1.0.0"
        assert summary["current_stage"] == "completion"
        assert summary["fields_processed"] == 1
        assert summary["fields_successful"] == 1
        assert summary["fields_failed"] == 0
        assert summary["success_rate"] == 1.0
        assert len(summary["stage_history"]) > 0


class TestQVFFieldManager:
    """Test main QVFFieldManager functionality."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_custom_fields_manager(self):
        """Create mock CustomFieldsManager."""
        mock_manager = AsyncMock(spec=CustomFieldsManager)
        mock_manager.validate_project_permissions = AsyncMock(return_value=(True, []))
        mock_manager.check_existing_fields = AsyncMock(return_value={})
        mock_manager.create_qvf_fields = AsyncMock(return_value={})
        mock_manager.get_operation_statistics = Mock(return_value={
            "fields_created": 0,
            "work_items_updated": 0,
            "total_operation_time": 0.0
        })
        
        # Mock REST client
        mock_rest_client = AsyncMock()
        mock_rest_client.get_work_item_types = AsyncMock(return_value=[
            {"name": "Epic"},
            {"name": "Feature"},
            {"name": "User Story"},
            {"name": "PIO"}
        ])
        mock_manager.rest_client = mock_rest_client
        
        return mock_manager
    
    @pytest.mark.asyncio
    async def test_field_manager_initialization(self, temp_workspace):
        """Test field manager initialization."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token",
                workspace_directory=temp_workspace
            )
            
            assert manager.organization_url == "https://dev.azure.com/test"
            assert manager.personal_access_token == "test_token"
            assert manager.workspace_directory == Path(temp_workspace)
            assert len(manager.configurations) == 0
            assert len(manager.active_deployments) == 0
    
    def test_default_field_configuration_generation(self):
        """Test generation of default field configurations."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Test different configuration levels
            dev_config = manager.get_default_field_configuration(FieldConfigurationLevel.DEVELOPMENT)
            assert dev_config.level == FieldConfigurationLevel.DEVELOPMENT
            assert "QVF.Score" in dev_config.field_definitions
            assert len(dev_config.work_item_mappings) == 1  # Only User Story for dev
            
            prod_config = manager.get_default_field_configuration(FieldConfigurationLevel.PRODUCTION)
            assert prod_config.level == FieldConfigurationLevel.PRODUCTION
            assert len(dev_config.field_definitions) == len(prod_config.field_definitions)
            assert len(prod_config.work_item_mappings) == 4  # All work item types for production
            
            # Verify all QVF fields are defined
            expected_fields = [
                "QVF.Score", "QVF.BusinessValue", "QVF.StrategicAlignment",
                "QVF.CustomerValue", "QVF.Complexity", "QVF.RiskScore",
                "QVF.LastCalculated", "QVF.ConfigurationId", 
                "QVF.Confidence", "QVF.DataQuality"
            ]
            for field_name in expected_fields:
                assert field_name in prod_config.field_definitions
    
    @pytest.mark.asyncio
    async def test_configuration_file_operations(self, temp_workspace):
        """Test configuration loading and saving to files."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token",
                workspace_directory=temp_workspace
            )
            
            # Create test configuration
            config = FieldConfiguration(
                name="file_test_config",
                version="1.2.3",
                description="Test configuration for file operations",
                level=FieldConfigurationLevel.STAGING,
                field_definitions={
                    "QVF.Score": {
                        "field_type": "decimal",
                        "display_name": "QVF Score",
                        "min_value": 0.0,
                        "max_value": 1.0
                    }
                },
                work_item_mappings={
                    "Epic": {
                        "applicable_fields": ["QVF.Score"],
                        "required_fields": ["QVF.Score"]
                    }
                },
                tags=["test", "file_operations"]
            )
            
            # Test YAML file operations
            yaml_path = Path(temp_workspace) / "test_config.yaml"
            manager.configurations["file_test_config"] = config
            
            success = await manager.save_configuration_to_file("file_test_config", str(yaml_path))
            assert success
            assert yaml_path.exists()
            
            # Load configuration back from YAML
            loaded_config = await manager.load_configuration_from_file(str(yaml_path), "loaded_yaml_config")
            assert loaded_config.name == "loaded_yaml_config"  # Name should be overridden
            assert loaded_config.version == "1.2.3"
            assert loaded_config.level == FieldConfigurationLevel.STAGING
            assert loaded_config.tags == ["test", "file_operations"]
            
            # Test JSON file operations
            json_path = Path(temp_workspace) / "test_config.json"
            success = await manager.save_configuration_to_file("file_test_config", str(json_path))
            assert success
            assert json_path.exists()
            
            # Load configuration back from JSON
            loaded_json_config = await manager.load_configuration_from_file(str(json_path), "loaded_json_config")
            assert loaded_json_config.version == "1.2.3"
            assert loaded_json_config.level == FieldConfigurationLevel.STAGING
    
    @pytest.mark.asyncio
    async def test_deployment_orchestration(self, mock_custom_fields_manager):
        """Test complete deployment orchestration."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager', return_value=mock_custom_fields_manager):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Setup mock responses
            mock_custom_fields_manager.create_qvf_fields.return_value = {
                "QVF.Score": FieldOperationResult(
                    success=True,
                    operation="create",
                    field_name="QVF.Score",
                    field_id="field_123",
                    message="Field created successfully"
                ),
                "QVF.BusinessValue": FieldOperationResult(
                    success=True,
                    operation="create",
                    field_name="QVF.BusinessValue",
                    field_id="field_456",
                    message="Field created successfully"
                )
            }
            
            # Perform deployment
            deployment_plan = await manager.deploy_to_project(
                project_name="TestProject",
                configuration_name="development",  # Uses default configuration
                work_item_types=[WorkItemType.USER_STORY],
                conflict_resolution=FieldConflictResolution.SKIP,
                dry_run=False
            )
            
            assert deployment_plan is not None
            assert deployment_plan.project_name == "TestProject"
            assert deployment_plan.current_stage == DeploymentStage.COMPLETION
            assert deployment_plan.start_time is not None
            assert deployment_plan.end_time is not None
            assert len(deployment_plan.field_results) == 2  # QVF.Score and QVF.BusinessValue for development level
            
            # Verify manager called the right methods
            mock_custom_fields_manager.validate_project_permissions.assert_called_once_with("TestProject")
            mock_custom_fields_manager.check_existing_fields.assert_called_once()
            mock_custom_fields_manager.create_qvf_fields.assert_called_once()
            
            # Check deployment summary
            summary = deployment_plan.get_deployment_summary()
            assert summary["fields_successful"] == 2
            assert summary["fields_failed"] == 0
            assert summary["success_rate"] == 1.0
    
    @pytest.mark.asyncio
    async def test_dry_run_deployment(self, mock_custom_fields_manager):
        """Test dry run deployment (validation only)."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager', return_value=mock_custom_fields_manager):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Perform dry run deployment
            deployment_plan = await manager.deploy_to_project(
                project_name="DryRunProject",
                configuration_name="staging",
                work_item_types=[WorkItemType.FEATURE],
                dry_run=True
            )
            
            assert deployment_plan.dry_run is True
            assert deployment_plan.current_stage == DeploymentStage.COMPLETION
            
            # Verify that actual field creation was not called in dry run
            mock_custom_fields_manager.create_qvf_fields.assert_not_called()
            
            # But validation should have been performed
            mock_custom_fields_manager.validate_project_permissions.assert_called_once_with("DryRunProject")
    
    @pytest.mark.asyncio
    async def test_deployment_failure_handling(self, mock_custom_fields_manager):
        """Test deployment failure scenarios."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager', return_value=mock_custom_fields_manager):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Setup failure scenario - permission validation fails
            mock_custom_fields_manager.validate_project_permissions.return_value = (False, ["Project Administrator"])
            
            deployment_plan = await manager.deploy_to_project(
                project_name="FailureProject",
                configuration_name="production",
                work_item_types=[WorkItemType.EPIC]
            )
            
            assert deployment_plan.current_stage == DeploymentStage.FAILED
            assert "Missing required permissions" in str(deployment_plan.stage_history[-1][2])
            
            # Test field creation failure
            mock_custom_fields_manager.validate_project_permissions.return_value = (True, [])
            mock_custom_fields_manager.create_qvf_fields.return_value = {
                "QVF.Score": FieldOperationResult(
                    success=False,
                    operation="create",
                    field_name="QVF.Score",
                    message="Field creation failed"
                ),
                "QVF.BusinessValue": FieldOperationResult(
                    success=False,
                    operation="create",
                    field_name="QVF.BusinessValue",
                    message="Field creation failed"
                )
            }
            
            deployment_plan_2 = await manager.deploy_to_project(
                project_name="FieldFailureProject",
                configuration_name="production",
                work_item_types=[WorkItemType.EPIC]
            )
            
            assert deployment_plan_2.current_stage == DeploymentStage.FAILED
            assert "Deployment failed: only 0/" in str(deployment_plan_2.stage_history[-1][2])
    
    def test_configuration_management(self):
        """Test configuration listing and management."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Add test configurations
            config1 = manager.get_default_field_configuration(FieldConfigurationLevel.DEVELOPMENT)
            config2 = manager.get_default_field_configuration(FieldConfigurationLevel.PRODUCTION)
            
            manager.configurations["dev"] = config1
            manager.configurations["prod"] = config2
            
            # Test configuration listing
            config_list = manager.list_configurations()
            assert len(config_list) == 2
            assert "dev" in config_list
            assert "prod" in config_list
            
            # Verify configuration metadata
            dev_info = config_list["dev"]
            assert dev_info["level"] == "development"
            assert dev_info["field_count"] == len(config1.field_definitions)
            assert isinstance(dev_info["work_item_types"], list)
            
            prod_info = config_list["prod"]
            assert prod_info["level"] == "production"
            assert prod_info["field_count"] == len(config2.field_definitions)
    
    def test_deployment_status_tracking(self):
        """Test deployment status tracking and retrieval."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Create a mock deployment plan
            config = manager.get_default_field_configuration(FieldConfigurationLevel.DEVELOPMENT)
            deployment_plan = DeploymentPlan(
                plan_id="status_test_plan",
                project_name="StatusTest",
                configuration=config,
                target_work_item_types=[WorkItemType.USER_STORY]
            )
            
            manager.active_deployments["status_test_plan"] = deployment_plan
            
            # Test status retrieval
            status = manager.get_deployment_status("status_test_plan")
            assert status is not None
            assert status["plan_id"] == "status_test_plan"
            assert status["project_name"] == "StatusTest"
            assert status["current_stage"] == "planning"
            
            # Test non-existent deployment
            status_missing = manager.get_deployment_status("non_existent_plan")
            assert status_missing is None
    
    def test_operation_statistics(self, mock_custom_fields_manager):
        """Test operation statistics collection."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager', return_value=mock_custom_fields_manager):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Add some configurations
            config1 = manager.get_default_field_configuration(FieldConfigurationLevel.DEVELOPMENT)
            config2 = manager.get_default_field_configuration(FieldConfigurationLevel.PRODUCTION)
            manager.configurations["dev"] = config1
            manager.configurations["prod"] = config2
            
            # Get statistics
            stats = manager.get_operation_statistics()
            
            assert "deployments_completed" in stats
            assert "configurations_loaded" in stats
            assert "configurations_active" in stats
            assert "deployments_active" in stats
            assert "workspace_directory" in stats
            assert "avg_deployment_time" in stats
            
            # Verify derived metrics
            assert stats["configurations_active"] == 2
            assert stats["deployments_active"] == 0
            assert isinstance(stats["workspace_directory"], str)
            
            # Verify field manager stats are included
            assert any(key.startswith("fields_manager_") for key in stats.keys())


class TestConfigurationManagement:
    """Test configuration loading, saving, and management."""
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample configuration data for testing."""
        return {
            "name": "test_sample_config",
            "version": "2.1.0",
            "description": "Sample configuration for testing",
            "level": "production",
            "field_definitions": {
                "QVF.Score": {
                    "field_type": "decimal",
                    "display_name": "QVF Score",
                    "description": "Overall QVF score",
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "precision": 4,
                    "is_required": False,
                    "default_value": 0.0
                },
                "QVF.BusinessValue": {
                    "field_type": "decimal",
                    "display_name": "QVF Business Value",
                    "description": "Business value component",
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "precision": 4,
                    "is_required": False,
                    "default_value": 0.0
                }
            },
            "work_item_mappings": {
                "Epic": {
                    "applicable_fields": ["QVF.Score", "QVF.BusinessValue"],
                    "required_fields": ["QVF.Score"],
                    "field_order": ["QVF.Score", "QVF.BusinessValue"]
                },
                "Feature": {
                    "applicable_fields": ["QVF.Score", "QVF.BusinessValue"],
                    "required_fields": ["QVF.Score"],
                    "field_order": ["QVF.Score", "QVF.BusinessValue"]
                }
            },
            "deployment_settings": {
                "batch_size": 100,
                "timeout_seconds": 300,
                "enable_rollback": True
            },
            "validation_rules": {
                "required_coverage": 0.8,
                "validate_permissions": True
            },
            "tags": ["sample", "testing", "configuration"]
        }
    
    @pytest.mark.asyncio
    async def test_yaml_configuration_loading(self, sample_config_data):
        """Test loading configuration from YAML file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
                manager = QVFFieldManager(
                    organization_url="https://dev.azure.com/test",
                    personal_access_token="test_token",
                    workspace_directory=temp_dir
                )
                
                # Create YAML file
                yaml_path = Path(temp_dir) / "test_config.yaml"
                with open(yaml_path, 'w') as f:
                    yaml.safe_dump(sample_config_data, f)
                
                # Load configuration
                config = await manager.load_configuration_from_file(str(yaml_path))
                
                assert config.name == "test_sample_config"
                assert config.version == "2.1.0"
                assert config.level == FieldConfigurationLevel.PRODUCTION
                assert len(config.field_definitions) == 2
                assert len(config.work_item_mappings) == 2
                assert config.tags == ["sample", "testing", "configuration"]
                
                # Verify it's stored in manager
                assert "test_sample_config" in manager.configurations
    
    @pytest.mark.asyncio
    async def test_json_configuration_loading(self, sample_config_data):
        """Test loading configuration from JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
                manager = QVFFieldManager(
                    organization_url="https://dev.azure.com/test",
                    personal_access_token="test_token",
                    workspace_directory=temp_dir
                )
                
                # Create JSON file
                json_path = Path(temp_dir) / "test_config.json"
                with open(json_path, 'w') as f:
                    json.dump(sample_config_data, f)
                
                # Load configuration
                config = await manager.load_configuration_from_file(str(json_path), "custom_name")
                
                assert config.name == "custom_name"  # Override name
                assert config.version == "2.1.0"
                assert config.level == FieldConfigurationLevel.PRODUCTION
                
                # Verify it's stored with custom name
                assert "custom_name" in manager.configurations
    
    @pytest.mark.asyncio
    async def test_configuration_loading_errors(self):
        """Test configuration loading error scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
                manager = QVFFieldManager(
                    organization_url="https://dev.azure.com/test",
                    personal_access_token="test_token",
                    workspace_directory=temp_dir
                )
                
                # Test non-existent file
                with pytest.raises(FieldManagerError, match="Configuration file not found"):
                    await manager.load_configuration_from_file("non_existent.yaml")
                
                # Test invalid YAML
                invalid_yaml_path = Path(temp_dir) / "invalid.yaml"
                with open(invalid_yaml_path, 'w') as f:
                    f.write("invalid: yaml: content: [")
                
                with pytest.raises(FieldManagerError, match="Failed to load configuration"):
                    await manager.load_configuration_from_file(str(invalid_yaml_path))
                
                # Test unsupported file format
                txt_path = Path(temp_dir) / "config.txt"
                with open(txt_path, 'w') as f:
                    f.write("some text content")
                
                with pytest.raises(FieldManagerError, match="Unsupported configuration file format"):
                    await manager.load_configuration_from_file(str(txt_path))


class TestPerformanceAndScaling:
    """Test performance and scalability aspects."""
    
    @pytest.mark.asyncio
    async def test_large_configuration_handling(self):
        """Test handling of large field configurations."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager'):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Create large configuration with many fields
            field_definitions = {}
            work_item_mappings = {}
            
            # Generate 50 fields
            for i in range(50):
                field_name = f"QVF.CustomField{i:02d}"
                field_definitions[field_name] = {
                    "field_type": "decimal",
                    "display_name": f"Custom Field {i}",
                    "description": f"Custom field number {i}",
                    "min_value": 0.0,
                    "max_value": 1.0,
                    "precision": 4,
                    "default_value": 0.5
                }
            
            # Map all fields to all work item types
            for wit_name in ["Epic", "Feature", "User Story", "PIO"]:
                work_item_mappings[wit_name] = {
                    "applicable_fields": list(field_definitions.keys()),
                    "required_fields": [list(field_definitions.keys())[0]],  # Only first field required
                    "field_order": list(field_definitions.keys())
                }
            
            large_config = FieldConfiguration(
                name="large_test_config",
                version="1.0.0",
                description="Large configuration with 50 fields",
                level=FieldConfigurationLevel.PRODUCTION,
                field_definitions=field_definitions,
                work_item_mappings=work_item_mappings
            )
            
            # Validate large configuration
            is_valid, errors = large_config.validate()
            assert is_valid, f"Large configuration validation failed: {errors}"
            
            # Test serialization performance
            import time
            start_time = time.time()
            config_dict = large_config.to_dict()
            serialization_time = time.time() - start_time
            
            assert serialization_time < 1.0, "Serialization took too long"
            assert len(config_dict["field_definitions"]) == 50
            
            # Test deserialization
            start_time = time.time()
            restored_config = FieldConfiguration.from_dict(config_dict)
            deserialization_time = time.time() - start_time
            
            assert deserialization_time < 1.0, "Deserialization took too long"
            assert len(restored_config.field_definitions) == 50
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_deployments(self, mock_custom_fields_manager):
        """Test handling of multiple concurrent deployments."""
        with patch('src.datascience_platform.qvf.ado.field_manager.CustomFieldsManager', return_value=mock_custom_fields_manager):
            manager = QVFFieldManager(
                organization_url="https://dev.azure.com/test",
                personal_access_token="test_token"
            )
            
            # Setup successful deployment mocks
            mock_custom_fields_manager.create_qvf_fields.return_value = {
                "QVF.Score": FieldOperationResult(
                    success=True,
                    operation="create",
                    field_name="QVF.Score",
                    message="Success"
                )
            }
            
            # Start multiple concurrent deployments
            deployment_tasks = []
            project_names = [f"TestProject{i}" for i in range(5)]
            
            for project_name in project_names:
                task = asyncio.create_task(
                    manager.deploy_to_project(
                        project_name=project_name,
                        configuration_name="development",
                        work_item_types=[WorkItemType.USER_STORY],
                        dry_run=True  # Use dry run for faster testing
                    )
                )
                deployment_tasks.append(task)
            
            # Wait for all deployments to complete
            deployment_results = await asyncio.gather(*deployment_tasks)
            
            # Verify all deployments completed successfully
            assert len(deployment_results) == 5
            for i, result in enumerate(deployment_results):
                assert result.project_name == f"TestProject{i}"
                assert result.current_stage == DeploymentStage.COMPLETION
            
            # Verify all deployments are tracked
            assert len(manager.active_deployments) == 5
            
            # Test statistics
            stats = manager.get_operation_statistics()
            assert stats["deployments_active"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])