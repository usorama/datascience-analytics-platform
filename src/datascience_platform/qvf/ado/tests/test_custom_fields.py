"""Comprehensive tests for QVF Custom Fields Management.

This module provides extensive unit and integration tests for the
QVF custom fields management system including field definitions,
ADO integration, batch operations, and error handling.

Test Coverage:
- QVF field definition validation and creation
- Work item type mapping configuration
- Custom fields manager operations
- ADO API integration mocking
- Batch processing and performance
- Error handling and rollback scenarios
- Field conflict resolution
- Permission validation

Usage:
    python -m pytest src/datascience_platform/qvf/ado/tests/test_custom_fields.py -v
    
    # Run with coverage
    python -m pytest src/datascience_platform/qvf/ado/tests/test_custom_fields.py --cov=src/datascience_platform/qvf/ado/custom_fields

Test Organization:
- TestQVFFieldDefinition: Field definition model tests
- TestWorkItemTypeMapping: Work item type mapping tests  
- TestCustomFieldsManager: Manager class integration tests
- TestBatchOperations: Batch processing and performance tests
- TestErrorHandling: Error scenarios and rollback tests
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any, Optional

# Test imports
from src.datascience_platform.qvf.ado.custom_fields import (
    QVFFieldDefinition,
    QVFCustomField,
    WorkItemTypeFieldMapping,
    CustomFieldsManager,
    FieldOperationResult,
    FieldConflictResolution,
    QVFFieldType,
    QVFFieldScope,
    QVFFieldError
)

from src.datascience_platform.ado.models import WorkItemType
from src.datascience_platform.qvf.core.criteria import CriteriaCategory


class TestQVFFieldDefinition:
    """Test suite for QVF field definition model."""
    
    def test_field_definition_creation(self):
        """Test basic QVF field definition creation."""
        field_def = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score", 
            description="Overall QVF prioritization score",
            field_type=QVFFieldType.DECIMAL,
            min_value=0.0,
            max_value=1.0
        )
        
        assert field_def.name == "QVF.Score"
        assert field_def.field_type == QVFFieldType.DECIMAL
        assert field_def.reference_name == "Custom.QVFScore"
        assert field_def.min_value == 0.0
        assert field_def.max_value == 1.0
    
    def test_reference_name_generation(self):
        """Test automatic reference name generation."""
        # Test with dots and spaces
        field_def = QVFFieldDefinition(
            name="QVF.Business Value",
            display_name="QVF Business Value",
            description="Business value component",
            field_type=QVFFieldType.DECIMAL
        )
        
        assert field_def.reference_name == "Custom.QVFBusinessValue"
        
        # Test with custom reference name
        field_def = QVFFieldDefinition(
            name="QVF.Custom",
            display_name="Custom Field",
            description="Custom field",
            field_type=QVFFieldType.STRING,
            reference_name="Custom.MyCustomField"
        )
        
        assert field_def.reference_name == "Custom.MyCustomField"
    
    def test_ado_field_definition_conversion(self):
        """Test conversion to ADO field definition format."""
        field_def = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score",
            description="Overall QVF score",
            field_type=QVFFieldType.DECIMAL,
            min_value=0.0,
            max_value=1.0,
            default_value=0.0
        )
        
        ado_def = field_def.to_ado_field_definition()
        
        assert ado_def["name"] == "QVF Score"
        assert ado_def["referenceName"] == "Custom.QVFScore"
        assert ado_def["type"] == "double"
        assert ado_def["minValue"] == 0.0
        assert ado_def["maxValue"] == 1.0
        assert ado_def["defaultValue"] == 0.0
        assert ado_def["usage"] == "workItem"
    
    def test_string_field_with_allowed_values(self):
        """Test string field with picklist values."""
        field_def = QVFFieldDefinition(
            name="QVF.Priority",
            display_name="QVF Priority",
            description="Priority level",
            field_type=QVFFieldType.STRING,
            allowed_values=["Critical", "High", "Medium", "Low"],
            max_length=20
        )
        
        ado_def = field_def.to_ado_field_definition()
        
        assert ado_def["type"] == "string"
        assert ado_def["isLimitedToAllowedValues"] == True
        assert ado_def["allowedValues"] == ["Critical", "High", "Medium", "Low"]
        assert ado_def["maxLength"] == 20
    
    def test_value_validation(self):
        """Test field value validation."""
        # Decimal field validation
        decimal_field = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score",
            description="Score field",
            field_type=QVFFieldType.DECIMAL,
            min_value=0.0,
            max_value=1.0
        )
        
        # Valid values
        is_valid, error = decimal_field.validate_value(0.5)
        assert is_valid == True
        assert error is None
        
        is_valid, error = decimal_field.validate_value(0.0)
        assert is_valid == True
        
        is_valid, error = decimal_field.validate_value(1.0)
        assert is_valid == True
        
        # Invalid values
        is_valid, error = decimal_field.validate_value(-0.1)
        assert is_valid == False
        assert "below minimum" in error
        
        is_valid, error = decimal_field.validate_value(1.1)
        assert is_valid == False
        assert "exceeds maximum" in error
        
        is_valid, error = decimal_field.validate_value("not_a_number")
        assert is_valid == False
        assert "not a valid decimal" in error
        
        # String field validation
        string_field = QVFFieldDefinition(
            name="QVF.Category",
            display_name="Category",
            description="Category field",
            field_type=QVFFieldType.STRING,
            allowed_values=["A", "B", "C"],
            max_length=10
        )
        
        is_valid, error = string_field.validate_value("A")
        assert is_valid == True
        
        is_valid, error = string_field.validate_value("D")
        assert is_valid == False
        assert "not in allowed values" in error
        
        is_valid, error = string_field.validate_value("This string is too long")
        assert is_valid == False
        assert "exceeds maximum" in error
    
    def test_required_field_validation(self):
        """Test required field validation."""
        required_field = QVFFieldDefinition(
            name="QVF.Required",
            display_name="Required Field",
            description="Required field",
            field_type=QVFFieldType.STRING,
            is_required=True
        )
        
        # None value for required field
        is_valid, error = required_field.validate_value(None)
        assert is_valid == False
        assert "is required" in error
        
        # Valid value for required field
        is_valid, error = required_field.validate_value("value")
        assert is_valid == True
        
        # Optional field
        optional_field = QVFFieldDefinition(
            name="QVF.Optional",
            display_name="Optional Field",
            description="Optional field",
            field_type=QVFFieldType.STRING,
            is_required=False
        )
        
        is_valid, error = optional_field.validate_value(None)
        assert is_valid == True


class TestQVFCustomField:
    """Test suite for QVF custom field model."""
    
    def test_custom_field_creation(self):
        """Test QVF custom field creation."""
        field_def = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score",
            description="Score field",
            field_type=QVFFieldType.DECIMAL
        )
        
        custom_field = QVFCustomField(
            definition=field_def,
            current_value=0.85
        )
        
        assert custom_field.definition.name == "QVF.Score"
        assert custom_field.current_value == 0.85
        assert custom_field.is_dirty == False
        assert len(custom_field.validation_errors) == 0
    
    def test_set_value_with_validation(self):
        """Test setting field value with validation."""
        field_def = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score",
            description="Score field",
            field_type=QVFFieldType.DECIMAL,
            min_value=0.0,
            max_value=1.0
        )
        
        custom_field = QVFCustomField(definition=field_def)
        
        # Valid value
        success = custom_field.set_value(0.85, "test_user")
        assert success == True
        assert custom_field.current_value == 0.85
        assert custom_field.is_dirty == True
        assert custom_field.updated_by == "test_user"
        assert custom_field.last_updated is not None
        
        # Invalid value
        success = custom_field.set_value(1.5, "test_user")
        assert success == False
        assert custom_field.current_value == 0.85  # Unchanged
        assert len(custom_field.validation_errors) == 1
        assert "exceeds maximum" in custom_field.validation_errors[0]
    
    def test_validate_current_value(self):
        """Test validation of current field value."""
        field_def = QVFFieldDefinition(
            name="QVF.Score",
            display_name="QVF Score",
            description="Score field",
            field_type=QVFFieldType.DECIMAL,
            min_value=0.0,
            max_value=1.0
        )
        
        # Valid current value
        custom_field = QVFCustomField(
            definition=field_def,
            current_value=0.75
        )
        
        is_valid = custom_field.validate_current_value()
        assert is_valid == True
        assert len(custom_field.validation_errors) == 0
        
        # Invalid current value
        custom_field.current_value = 2.0
        is_valid = custom_field.validate_current_value()
        assert is_valid == False
        assert len(custom_field.validation_errors) == 1


class TestWorkItemTypeFieldMapping:
    """Test suite for work item type field mapping."""
    
    def test_default_mappings(self):
        """Test default field mappings for work item types."""
        mappings = WorkItemTypeFieldMapping.get_default_mappings()
        
        # Check that all major work item types are covered
        assert WorkItemType.EPIC in mappings
        assert WorkItemType.FEATURE in mappings
        assert WorkItemType.USER_STORY in mappings
        assert WorkItemType.PIO in mappings
        
        # Check Epic mapping
        epic_mapping = mappings[WorkItemType.EPIC]
        assert "QVF.Score" in epic_mapping.applicable_fields
        assert "QVF.BusinessValue" in epic_mapping.applicable_fields
        assert "QVF.StrategicAlignment" in epic_mapping.applicable_fields
        assert "QVF.Score" in epic_mapping.required_fields or "QVF.BusinessValue" in epic_mapping.required_fields
        
        # Check User Story mapping (should be simplified)
        story_mapping = mappings[WorkItemType.USER_STORY]
        assert "QVF.Score" in story_mapping.applicable_fields
        assert len(story_mapping.applicable_fields) < len(epic_mapping.applicable_fields)
    
    def test_field_applicability(self):
        """Test field applicability checking."""
        mapping = WorkItemTypeFieldMapping(
            work_item_type=WorkItemType.EPIC,
            applicable_fields={"QVF.Score", "QVF.BusinessValue"},
            required_fields={"QVF.Score"}
        )
        
        assert mapping.is_field_applicable("QVF.Score") == True
        assert mapping.is_field_applicable("QVF.BusinessValue") == True
        assert mapping.is_field_applicable("QVF.NotIncluded") == False
        
        assert mapping.is_field_required("QVF.Score") == True
        assert mapping.is_field_required("QVF.BusinessValue") == False
    
    def test_default_values(self):
        """Test default value handling."""
        mapping = WorkItemTypeFieldMapping(
            work_item_type=WorkItemType.FEATURE,
            applicable_fields={"QVF.Score", "QVF.Confidence"},
            default_values={"QVF.Confidence": 0.8}
        )
        
        assert mapping.get_default_value("QVF.Score") is None
        assert mapping.get_default_value("QVF.Confidence") == 0.8
        assert mapping.get_default_value("QVF.NotIncluded") is None


class TestFieldOperationResult:
    """Test suite for field operation result model."""
    
    def test_result_creation(self):
        """Test field operation result creation."""
        result = FieldOperationResult(
            success=True,
            operation="create",
            field_name="QVF.Score",
            field_id="field-123",
            message="Field created successfully"
        )
        
        assert result.success == True
        assert result.operation == "create"
        assert result.field_name == "QVF.Score"
        assert result.field_id == "field-123"
        assert result.is_successful == True
        assert result.has_warnings == False
    
    def test_add_errors_and_warnings(self):
        """Test adding errors and warnings."""
        result = FieldOperationResult(
            success=True,
            operation="create",
            field_name="QVF.Score"
        )
        
        # Add warning
        result.add_warning("This is a warning")
        assert result.has_warnings == True
        assert len(result.warnings) == 1
        assert result.success == True  # Still successful
        
        # Add error
        result.add_error("This is an error")
        assert len(result.errors) == 1
        assert result.success == False  # Now failed
        assert result.is_successful == False
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        result = FieldOperationResult(
            success=True,
            operation="update",
            field_name="QVF.BusinessValue",
            execution_time_seconds=1.5,
            items_processed=100,
            items_succeeded=98,
            items_failed=2
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] == True
        assert result_dict["operation"] == "update"
        assert result_dict["field_name"] == "QVF.BusinessValue"
        assert result_dict["execution_time_seconds"] == 1.5
        assert result_dict["items_processed"] == 100
        assert result_dict["is_successful"] == True
        assert result_dict["has_warnings"] == False
        assert "timestamp" in result_dict


@pytest.mark.asyncio
class TestCustomFieldsManager:
    """Test suite for custom fields manager."""
    
    @pytest.fixture
    def mock_rest_client(self):
        """Mock REST client for testing."""
        mock_client = Mock()
        mock_client.get_project = AsyncMock(return_value={"id": "project-123", "name": "TestProject"})
        mock_client.list_work_item_fields = AsyncMock(return_value=[])
        mock_client.create_work_item_field = AsyncMock(return_value={"id": "field-123", "referenceName": "Custom.QVFScore"})
        mock_client.add_field_to_work_item_type = AsyncMock(return_value=True)
        mock_client.update_work_item = AsyncMock(return_value={"id": 123, "rev": 2})
        return mock_client
    
    @pytest.fixture
    def fields_manager(self, mock_rest_client):
        """Create fields manager with mocked dependencies."""
        with patch('src.datascience_platform.qvf.ado.custom_fields.ADORestClient') as mock_client_class:
            mock_client_class.return_value = mock_rest_client
            
            manager = CustomFieldsManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="fake_token"
            )
            manager.rest_client = mock_rest_client
            return manager
    
    def test_field_definitions_creation(self, fields_manager):
        """Test QVF field definitions creation."""
        field_definitions = fields_manager.get_qvf_field_definitions()
        
        # Check that all required QVF fields are defined
        expected_fields = {
            "QVF.Score", "QVF.BusinessValue", "QVF.StrategicAlignment",
            "QVF.CustomerValue", "QVF.Complexity", "QVF.RiskScore",
            "QVF.LastCalculated", "QVF.ConfigurationId", "QVF.Confidence",
            "QVF.DataQuality"
        }
        
        assert set(field_definitions.keys()) == expected_fields
        
        # Check QVF.Score field specifically
        score_field = field_definitions["QVF.Score"]
        assert score_field.field_type == QVFFieldType.DECIMAL
        assert score_field.min_value == 0.0
        assert score_field.max_value == 1.0
        assert score_field.reference_name == "Custom.QVFScore"
        
        # Check timestamp field
        timestamp_field = field_definitions["QVF.LastCalculated"]
        assert timestamp_field.field_type == QVFFieldType.DATETIME
        
        # Check string field
        config_field = field_definitions["QVF.ConfigurationId"]
        assert config_field.field_type == QVFFieldType.STRING
        assert config_field.max_length == 100
    
    async def test_validate_project_permissions(self, fields_manager, mock_rest_client):
        """Test project permissions validation."""
        # Mock successful permission checks
        mock_rest_client.get_project.return_value = {"id": "project-123"}
        mock_rest_client.list_process_work_item_types.return_value = []
        mock_rest_client.get_work_item_types.return_value = []
        
        has_permissions, missing_perms = await fields_manager.validate_project_permissions("TestProject")
        
        assert has_permissions == True
        assert len(missing_perms) == 0
        
        # Mock permission failure
        from src.datascience_platform.qvf.ado.rest_client import ADOPermissionError
        mock_rest_client.list_process_work_item_types.side_effect = ADOPermissionError("Forbidden", status_code=403)
        
        has_permissions, missing_perms = await fields_manager.validate_project_permissions("TestProject")
        
        assert has_permissions == False
        assert len(missing_perms) > 0
        assert any("Administrator" in perm for perm in missing_perms)
    
    async def test_check_existing_fields(self, fields_manager, mock_rest_client):
        """Test checking existing fields in project."""
        # Mock existing fields response
        mock_existing_fields = [
            {
                "referenceName": "Custom.QVFScore",
                "name": "QVF Score",
                "type": "double",
                "id": "field-123"
            },
            {
                "referenceName": "Custom.QVFBusinessValue",
                "name": "QVF Business Value",
                "type": "double",
                "id": "field-124"
            }
        ]
        
        mock_rest_client.list_work_item_fields.return_value = mock_existing_fields
        
        existing_fields = await fields_manager.check_existing_fields("TestProject")
        
        # Should find existing fields by name mapping
        assert "QVF.Score" in existing_fields
        assert "QVF.BusinessValue" in existing_fields
        assert existing_fields["QVF.Score"]["id"] == "field-123"
        
        mock_rest_client.list_work_item_fields.assert_called_once_with("TestProject")
    
    async def test_create_single_field(self, fields_manager, mock_rest_client):
        """Test creating a single QVF field."""
        # Mock field creation response
        mock_rest_client.create_work_item_field.return_value = {
            "id": "field-123",
            "referenceName": "Custom.QVFScore",
            "name": "QVF Score"
        }
        
        field_def = fields_manager.get_qvf_field_definitions()["QVF.Score"]
        work_item_types = [WorkItemType.EPIC, WorkItemType.FEATURE]
        
        result = await fields_manager._create_single_field(
            "TestProject",
            field_def,
            work_item_types
        )
        
        assert result.success == True
        assert result.field_id == "field-123"
        assert result.operation == "create"
        assert result.field_name == "QVF.Score"
        
        # Verify ADO API calls
        mock_rest_client.create_work_item_field.assert_called_once()
        call_args = mock_rest_client.create_work_item_field.call_args[0]
        assert call_args[0] == "TestProject"
        
        field_definition = call_args[1]
        assert field_definition["referenceName"] == "Custom.QVFScore"
        assert field_definition["type"] == "double"
    
    async def test_create_qvf_fields_batch(self, fields_manager, mock_rest_client):
        """Test batch creation of QVF fields."""
        # Mock permissions validation
        with patch.object(fields_manager, 'validate_project_permissions') as mock_validate:
            mock_validate.return_value = (True, [])
            
            # Mock existing fields check
            with patch.object(fields_manager, 'check_existing_fields') as mock_check:
                mock_check.return_value = {}  # No existing fields
                
                # Mock field creation
                mock_rest_client.create_work_item_field.side_effect = [
                    {"id": f"field-{i}", "referenceName": f"Custom.Field{i}"} 
                    for i in range(10)
                ]
                
                # Create subset of fields
                field_names = ["QVF.Score", "QVF.BusinessValue", "QVF.StrategicAlignment"]
                results = await fields_manager.create_qvf_fields(
                    "TestProject",
                    field_names=field_names,
                    conflict_resolution=FieldConflictResolution.SKIP
                )
                
                assert len(results) == 3
                assert all(result.success for result in results.values())
                
                # Verify all fields were attempted
                for field_name in field_names:
                    assert field_name in results
                    assert results[field_name].operation == "create"
    
    async def test_field_conflict_resolution(self, fields_manager, mock_rest_client):
        """Test field conflict resolution strategies."""
        # Mock existing field
        existing_field = {
            "id": "existing-field-123",
            "referenceName": "Custom.QVFScore",
            "name": "QVF Score"
        }
        
        with patch.object(fields_manager, 'validate_project_permissions') as mock_validate:
            mock_validate.return_value = (True, [])
            
            with patch.object(fields_manager, 'check_existing_fields') as mock_check:
                mock_check.return_value = {"QVF.Score": existing_field}
                
                # Test SKIP strategy
                results = await fields_manager.create_qvf_fields(
                    "TestProject",
                    field_names=["QVF.Score"],
                    conflict_resolution=FieldConflictResolution.SKIP
                )
                
                result = results["QVF.Score"]
                assert result.success == True
                assert result.field_id == "existing-field-123"
                assert len(result.warnings) > 0
                assert "already exists" in result.warnings[0]
                
                # Test ERROR strategy
                results = await fields_manager.create_qvf_fields(
                    "TestProject",
                    field_names=["QVF.Score"],
                    conflict_resolution=FieldConflictResolution.ERROR
                )
                
                result = results["QVF.Score"]
                assert result.success == False
                assert len(result.errors) > 0
                assert "already exists" in result.errors[0]
    
    async def test_update_work_item_scores(self, fields_manager, mock_rest_client):
        """Test updating work item scores."""
        # Mock work item updates
        mock_rest_client.update_work_item.return_value = {
            "id": 123,
            "rev": 2,
            "fields": {"Custom.QVFScore": 0.85}
        }
        
        # Test data
        work_item_scores = {
            123: {"QVF.Score": 0.85, "QVF.BusinessValue": 0.90},
            124: {"QVF.Score": 0.75, "QVF.CustomerValue": 0.80}
        }
        
        results = await fields_manager.update_work_item_scores(
            "TestProject",
            work_item_scores
        )
        
        assert len(results) == 2
        assert 123 in results
        assert 124 in results
        
        # Check that update calls were made
        assert mock_rest_client.update_work_item.call_count == 2
        
        # Verify call arguments
        call_args_list = mock_rest_client.update_work_item.call_args_list
        
        # Check first call (work item 123)
        first_call_args = call_args_list[0][0]
        assert first_call_args[0] == "TestProject"
        assert first_call_args[1] == 123
        
        first_call_updates = first_call_args[2]
        assert "Custom.QVFScore" in first_call_updates
        assert first_call_updates["Custom.QVFScore"] == 0.85
    
    async def test_batch_processing_performance(self, fields_manager, mock_rest_client):
        """Test batch processing with large datasets."""
        # Create large dataset
        work_item_scores = {}
        for i in range(250):  # 250 work items
            work_item_scores[i] = {"QVF.Score": 0.5 + (i % 100) / 200}
        
        # Mock successful updates
        mock_rest_client.update_work_item.return_value = {"id": 1, "rev": 2}
        
        start_time = datetime.now()
        
        results = await fields_manager.update_work_item_scores(
            "TestProject",
            work_item_scores,
            batch_size=50  # Process in batches of 50
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        assert len(results) == 250
        assert all(result.is_successful for result in results.values())
        assert processing_time < 30  # Should complete within 30 seconds
        
        # Verify batch processing (should be 5 batches of 50)
        # Each batch should have slight delays, so total calls should be 250
        assert mock_rest_client.update_work_item.call_count == 250
    
    def test_get_operation_statistics(self, fields_manager):
        """Test operation statistics tracking."""
        # Simulate some operations
        fields_manager._operation_stats["fields_created"] = 10
        fields_manager._operation_stats["work_items_updated"] = 100
        fields_manager._operation_stats["total_operation_time"] = 25.5
        
        stats = fields_manager.get_operation_statistics()
        
        assert stats["fields_created"] == 10
        assert stats["work_items_updated"] == 100
        assert stats["total_operation_time"] == 25.5
        assert "avg_field_creation_time" in stats
        assert "avg_work_item_update_time" in stats
        
        # Check calculated averages
        assert stats["avg_field_creation_time"] == 2.55  # 25.5 / 10
        assert stats["avg_work_item_update_time"] == 0.255  # 25.5 / 100


@pytest.mark.asyncio 
class TestErrorHandling:
    """Test suite for error handling and edge cases."""
    
    @pytest.fixture
    def failing_rest_client(self):
        """Mock REST client that fails for testing error scenarios."""
        mock_client = Mock()
        
        from src.datascience_platform.qvf.ado.rest_client import (
            ADOApiError, ADOAuthenticationError, ADOPermissionError, ADORateLimitError
        )
        
        mock_client.get_project = AsyncMock(side_effect=ADOAuthenticationError("Invalid token", status_code=401))
        mock_client.create_work_item_field = AsyncMock(side_effect=ADOPermissionError("Insufficient permissions", status_code=403))
        mock_client.update_work_item = AsyncMock(side_effect=ADORateLimitError("Rate limit exceeded", status_code=429))
        
        return mock_client
    
    @pytest.fixture
    def error_fields_manager(self, failing_rest_client):
        """Create fields manager with failing client."""
        with patch('src.datascience_platform.qvf.ado.custom_fields.ADORestClient') as mock_client_class:
            mock_client_class.return_value = failing_rest_client
            
            manager = CustomFieldsManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="fake_token"
            )
            manager.rest_client = failing_rest_client
            return manager
    
    async def test_authentication_error_handling(self, error_fields_manager):
        """Test handling of authentication errors."""
        has_permissions, missing_perms = await error_fields_manager.validate_project_permissions("TestProject")
        
        assert has_permissions == False
        assert len(missing_perms) > 0
        assert any("validation failed" in perm for perm in missing_perms)
    
    async def test_permission_error_in_field_creation(self, error_fields_manager):
        """Test handling of permission errors during field creation."""
        # Mock successful permission check but failing field creation
        with patch.object(error_fields_manager, 'validate_project_permissions') as mock_validate:
            mock_validate.return_value = (True, [])
            
            with patch.object(error_fields_manager, 'check_existing_fields') as mock_check:
                mock_check.return_value = {}  # No existing fields
                
                results = await error_fields_manager.create_qvf_fields(
                    "TestProject",
                    field_names=["QVF.Score"]
                )
                
                result = results["QVF.Score"]
                assert result.success == False
                assert len(result.errors) > 0
                assert "permission" in result.errors[0].lower() or "403" in result.errors[0]
    
    async def test_rate_limit_error_handling(self, error_fields_manager, failing_rest_client):
        """Test handling of rate limit errors."""
        work_item_scores = {123: {"QVF.Score": 0.85}}
        
        results = await error_fields_manager.update_work_item_scores(
            "TestProject",
            work_item_scores
        )
        
        result = results[123]
        assert result.success == False
        assert len(result.errors) > 0
        assert "rate limit" in result.errors[0].lower() or "429" in result.errors[0]
    
    async def test_invalid_field_values(self):
        """Test handling of invalid field values."""
        # Create field manager with valid client but test validation
        mock_rest_client = Mock()
        mock_rest_client.update_work_item = AsyncMock(return_value={"id": 123})
        
        with patch('src.datascience_platform.qvf.ado.custom_fields.ADORestClient') as mock_client_class:
            mock_client_class.return_value = mock_rest_client
            
            manager = CustomFieldsManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="fake_token"
            )
            manager.rest_client = mock_rest_client
            
            # Test invalid score values
            work_item_scores = {
                123: {"QVF.Score": 1.5},  # Invalid: > 1.0
                124: {"QVF.Score": -0.1},  # Invalid: < 0.0
                125: {"QVF.Score": "invalid"}  # Invalid: not a number
            }
            
            results = await manager.update_work_item_scores(
                "TestProject",
                work_item_scores
            )
            
            # All should fail validation
            assert len(results) == 3
            for work_item_id, result in results.items():
                assert result.success == False
                assert len(result.errors) > 0
    
    async def test_network_timeout_simulation(self):
        """Test handling of network timeouts."""
        mock_rest_client = Mock()
        mock_rest_client.update_work_item = AsyncMock(side_effect=asyncio.TimeoutError())
        
        with patch('src.datascience_platform.qvf.ado.custom_fields.ADORestClient') as mock_client_class:
            mock_client_class.return_value = mock_rest_client
            
            manager = CustomFieldsManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="fake_token"
            )
            manager.rest_client = mock_rest_client
            
            work_item_scores = {123: {"QVF.Score": 0.85}}
            
            results = await manager.update_work_item_scores(
                "TestProject",
                work_item_scores
            )
            
            result = results[123]
            assert result.success == False
            assert len(result.errors) > 0
    
    def test_field_definition_validation_errors(self):
        """Test field definition validation with invalid configurations."""
        with pytest.raises(ValueError):
            # Invalid field type
            QVFFieldDefinition(
                name="Invalid.Field",
                display_name="Invalid Field",
                description="Field with invalid type",
                field_type="invalid_type"
            )
        
        with pytest.raises(ValueError):
            # Invalid normalization method
            QVFFieldDefinition(
                name="Invalid.Field",
                display_name="Invalid Field", 
                description="Field with invalid normalization",
                field_type=QVFFieldType.DECIMAL,
                normalization_method="invalid_method"
            )
    
    async def test_cleanup_fields_safety(self):
        """Test field cleanup safety mechanisms."""
        mock_rest_client = Mock()
        mock_rest_client.delete_work_item_field = AsyncMock(return_value=True)
        
        with patch('src.datascience_platform.qvf.ado.custom_fields.ADORestClient') as mock_client_class:
            mock_client_class.return_value = mock_rest_client
            
            manager = CustomFieldsManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="fake_token"
            )
            manager.rest_client = mock_rest_client
            
            # Should require explicit confirmation
            with pytest.raises(QVFFieldError) as exc_info:
                await manager.cleanup_qvf_fields(
                    "TestProject",
                    field_names=["QVF.Score"],
                    confirm_deletion=False
                )
            
            assert "explicit confirmation" in str(exc_info.value)
            
            # With confirmation, should proceed
            with patch.object(manager, 'check_existing_fields') as mock_check:
                mock_check.return_value = {
                    "QVF.Score": {"id": "field-123", "referenceName": "Custom.QVFScore"}
                }
                
                results = await manager.cleanup_qvf_fields(
                    "TestProject",
                    field_names=["QVF.Score"],
                    confirm_deletion=True
                )
                
                assert "QVF.Score" in results
                result = results["QVF.Score"]
                assert result.success == True
                assert result.operation == "delete"


if __name__ == "__main__":
    # Run specific test methods for development
    pytest.main([
        __file__ + "::TestQVFFieldDefinition::test_field_definition_creation",
        "-v"
    ])
