"""Comprehensive tests for QVF Work Item Management.

This module provides extensive testing for the WorkItemManager including:
- Work item loading and filtering
- QVF score calculations and updates
- Batch processing capabilities
- Score validation and error handling
- Performance optimization features
- Integration with custom fields manager

Tests use mocked ADO responses to avoid dependencies on live instances.
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

from pydantic import ValidationError

# Internal imports
from datascience_platform.qvf.ado.work_items import (
    WorkItemManager,
    QVFWorkItemScore,
    WorkItemUpdateBatch,
    UpdateResult,
    WorkItemManagementError
)
from datascience_platform.qvf.ado.rest_client import ADOClientConfig, ADOApiError
from datascience_platform.ado.models import WorkItemType, WorkItemState


class TestQVFWorkItemScore:
    """Test QVF work item score data model."""
    
    def test_valid_score_creation(self):
        """Test creating valid QVF work item score."""
        score = QVFWorkItemScore(
            work_item_id=123,
            overall_score=0.85,
            business_value=0.9,
            strategic_alignment=0.8,
            customer_value=0.85,
            complexity=0.7,
            risk_score=0.6,
            configuration_id="qvf_v1",
            confidence=0.95,
            data_quality=0.92
        )
        
        assert score.work_item_id == 123
        assert score.overall_score == 0.85
        assert score.business_value == 0.9
        assert score.configuration_id == "qvf_v1"
        assert score.confidence == 0.95
        assert score.data_quality == 0.92
    
    def test_score_validation_ranges(self):
        """Test score validation for valid ranges."""
        # Test invalid overall_score
        with pytest.raises(ValidationError):
            QVFWorkItemScore(
                work_item_id=123,
                overall_score=1.5,  # Invalid: > 1.0
                configuration_id="test"
            )
        
        with pytest.raises(ValidationError):
            QVFWorkItemScore(
                work_item_id=123,
                overall_score=-0.1,  # Invalid: < 0.0
                configuration_id="test"
            )
    
    def test_score_defaults(self):
        """Test default values for optional fields."""
        score = QVFWorkItemScore(
            work_item_id=123,
            overall_score=0.75,
            configuration_id="test"
        )
        
        assert score.confidence == 1.0
        assert score.data_quality == 1.0
        assert score.criteria_breakdown == {}
        assert score.category_scores == {}
        assert score.missing_data_fields == []
        assert score.data_quality_issues == []
        assert isinstance(score.calculation_timestamp, datetime)
    
    def test_to_field_updates(self):
        """Test conversion to ADO field updates."""
        score = QVFWorkItemScore(
            work_item_id=123,
            overall_score=0.85,
            business_value=0.9,
            strategic_alignment=0.8,
            configuration_id="qvf_v1",
            confidence=0.95,
            data_quality=0.92
        )
        
        field_updates = score.to_field_updates()
        
        assert field_updates["Custom.QVFScore"] == 0.85
        assert field_updates["Custom.QVFBusinessValue"] == 0.9
        assert field_updates["Custom.QVFStrategicAlignment"] == 0.8
        assert field_updates["Custom.QVFConfigurationId"] == "qvf_v1"
        assert field_updates["Custom.QVFConfidence"] == 0.95
        assert field_updates["Custom.QVFDataQuality"] == 0.92
        assert "Custom.QVFLastCalculated" in field_updates
    
    def test_get_score_summary(self):
        """Test human-readable score summary."""
        score = QVFWorkItemScore(
            work_item_id=123,
            overall_score=0.85,
            business_value=0.9,
            strategic_alignment=0.8,
            customer_value=0.85,
            complexity=0.7,
            risk_score=0.6,
            configuration_id="test"
        )
        
        summary = score.get_score_summary()
        
        assert "QVF Score: 0.850" in summary
        assert "Business: 0.900" in summary
        assert "Strategic: 0.800" in summary
        assert "Customer: 0.850" in summary
        assert "Complexity: 0.700" in summary
        assert "Risk: 0.600" in summary
    
    def test_partial_score_updates(self):
        """Test field updates with partial component scores."""
        score = QVFWorkItemScore(
            work_item_id=123,
            overall_score=0.75,
            business_value=0.8,
            # Missing other component scores
            configuration_id="test"
        )
        
        field_updates = score.to_field_updates()
        
        assert field_updates["Custom.QVFScore"] == 0.75
        assert field_updates["Custom.QVFBusinessValue"] == 0.8
        # Should not include None values
        assert "Custom.QVFStrategicAlignment" not in field_updates
        assert "Custom.QVFCustomerValue" not in field_updates


class TestWorkItemUpdateBatch:
    """Test work item update batch processing."""
    
    def create_sample_scores(self) -> Dict[int, QVFWorkItemScore]:
        """Create sample QVF scores for testing."""
        scores = {}
        for i, work_item_id in enumerate([123, 124, 125]):
            scores[work_item_id] = QVFWorkItemScore(
                work_item_id=work_item_id,
                overall_score=0.7 + (i * 0.1),
                configuration_id="test"
            )
        return scores
    
    def test_batch_creation(self):
        """Test batch creation with work item scores."""
        scores = self.create_sample_scores()
        
        batch = WorkItemUpdateBatch(
            batch_id="batch_1",
            project_name="TestProject",
            work_item_scores=scores
        )
        
        assert batch.batch_id == "batch_1"
        assert batch.project_name == "TestProject"
        assert batch.total_items == 3
        assert not batch.is_processed
        assert batch.success_rate == 0.0
    
    def test_batch_processing_lifecycle(self):
        """Test batch processing lifecycle methods."""
        batch = WorkItemUpdateBatch(
            batch_id="batch_1",
            project_name="TestProject",
            work_item_scores=self.create_sample_scores()
        )
        
        # Mark started
        start_time = datetime.now(timezone.utc)
        batch.mark_started()
        assert batch.processing_started is not None
        assert batch.processing_started >= start_time
        
        # Add results
        batch.add_success(123)
        batch.add_failure(124, "Permission denied")
        batch.add_success(125)
        
        assert 123 in batch.successful_updates
        assert 125 in batch.successful_updates
        assert 124 in batch.failed_updates
        assert batch.failed_updates[124] == "Permission denied"
        
        # Mark completed
        end_time = datetime.now(timezone.utc)
        batch.mark_completed()
        assert batch.is_processed
        assert batch.processing_completed is not None
        assert batch.processing_completed >= end_time
        assert batch.processing_duration is not None
        assert batch.processing_duration > 0
    
    def test_batch_success_rate_calculation(self):
        """Test batch success rate calculation."""
        batch = WorkItemUpdateBatch(
            batch_id="batch_1",
            project_name="TestProject",
            work_item_scores=self.create_sample_scores()
        )
        
        # 2 out of 3 successful
        batch.add_success(123)
        batch.add_failure(124, "Error")
        batch.add_success(125)
        
        assert batch.success_rate == (2.0 / 3.0) * 100  # 66.67%


class TestUpdateResult:
    """Test update result aggregation."""
    
    def test_result_creation(self):
        """Test update result creation."""
        result = UpdateResult(
            total_items=100,
            successful_updates=85,
            failed_updates=15,
            processing_time_seconds=45.5
        )
        
        assert result.total_items == 100
        assert result.successful_updates == 85
        assert result.failed_updates == 15
        assert result.success_rate == 85.0
        assert result.items_per_second == 100 / 45.5
    
    def test_batch_result_aggregation(self):
        """Test adding batch results to overall result."""
        result = UpdateResult(
            total_items=6,
            successful_updates=4,
            failed_updates=2,
            processing_time_seconds=30.0
        )
        
        # Create sample batches
        batch1 = WorkItemUpdateBatch(
            batch_id="batch_1",
            project_name="Test",
            work_item_scores={}
        )
        batch1.add_success(123)
        batch1.add_failure(124, "authentication failed")
        
        batch2 = WorkItemUpdateBatch(
            batch_id="batch_2", 
            project_name="Test",
            work_item_scores={}
        )
        batch2.add_success(125)
        batch2.add_failure(126, "rate limit exceeded")
        
        result.add_batch_result(batch1)
        result.add_batch_result(batch2)
        
        assert len(result.batch_results) == 2
        assert result.error_summary["Authentication"] == 1
        assert result.error_summary["Rate Limit"] == 1
    
    def test_result_summary_formatting(self):
        """Test human-readable result summary."""
        result = UpdateResult(
            total_items=1000,
            successful_updates=950,
            failed_updates=50,
            processing_time_seconds=120.0
        )
        
        summary = result.get_summary()
        
        assert "950/1000" in summary
        assert "95.0%" in summary
        assert "120.0s" in summary
        assert "8.3 items/sec" in summary


@pytest.fixture
def mock_rest_client():
    """Create mock REST client for testing."""
    return AsyncMock()


@pytest.fixture
def mock_fields_manager():
    """Create mock custom fields manager for testing."""
    manager = AsyncMock()
    
    # Mock QVF field definitions
    manager.get_qvf_field_definitions.return_value = {
        "QVF.Score": Mock(reference_name="Custom.QVFScore"),
        "QVF.BusinessValue": Mock(reference_name="Custom.QVFBusinessValue"),
        "QVF.Confidence": Mock(reference_name="Custom.QVFConfidence")
    }
    
    return manager


@pytest.fixture
def work_item_manager():
    """Create work item manager for testing."""
    with patch('datascience_platform.qvf.ado.work_items.ADORestClient'):
        with patch('datascience_platform.qvf.ado.work_items.CustomFieldsManager'):
            manager = WorkItemManager(
                organization_url="https://dev.azure.com/testorg",
                personal_access_token="test_pat",
                batch_size=5  # Small batch size for testing
            )
            return manager


class TestWorkItemManager:
    """Test work item manager functionality."""
    
    def test_manager_initialization(self, work_item_manager):
        """Test work item manager initialization."""
        assert work_item_manager.organization_url == "https://dev.azure.com/testorg"
        assert work_item_manager.personal_access_token == "test_pat"
        assert work_item_manager.batch_size == 5
        assert work_item_manager._operation_stats["work_items_loaded"] == 0
        assert work_item_manager._operation_stats["work_items_updated"] == 0
    
    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test async context manager usage."""
        with patch('datascience_platform.qvf.ado.work_items.ADORestClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            
            with patch('datascience_platform.qvf.ado.work_items.CustomFieldsManager'):
                async with WorkItemManager("https://dev.azure.com/test", "pat") as manager:
                    assert manager.rest_client.start_session.called
                
                assert manager.rest_client.close_session.called
    
    @pytest.mark.asyncio
    async def test_load_work_items_for_scoring_basic(self, work_item_manager):
        """Test basic work item loading functionality."""
        project_name = "TestProject"
        
        # Mock WIQL query response
        query_response = {
            "workItems": [
                {"id": 123},
                {"id": 124},
                {"id": 125}
            ]
        }
        
        # Mock batch work items response
        work_items_response = [
            {
                "id": 123,
                "fields": {
                    "System.Id": 123,
                    "System.Title": "Feature A",
                    "System.WorkItemType": "Feature",
                    "System.State": "Active"
                }
            },
            {
                "id": 124,
                "fields": {
                    "System.Id": 124,
                    "System.Title": "Feature B", 
                    "System.WorkItemType": "Feature",
                    "System.State": "Active"
                }
            },
            {
                "id": 125,
                "fields": {
                    "System.Id": 125,
                    "System.Title": "Feature C",
                    "System.WorkItemType": "Feature",
                    "System.State": "Active"
                }
            }
        ]
        
        work_item_manager.rest_client.query_work_items.return_value = query_response
        work_item_manager.rest_client.get_work_items_batch.return_value = work_items_response
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        work_items = await work_item_manager.load_work_items_for_scoring(project_name)
        
        assert len(work_items) == 3
        assert work_items[0]["id"] == 123
        assert work_items[0]["fields"]["System.Title"] == "Feature A"
        
        # Verify WIQL query was constructed correctly
        work_item_manager.rest_client.query_work_items.assert_called_once()
        query_call = work_item_manager.rest_client.query_work_items.call_args
        assert project_name in query_call[0]
        query_str = query_call[0][1]
        assert "FROM WorkItems" in query_str
        assert "[State] NOT IN ('Closed', 'Resolved', 'Removed', 'Cancelled')" in query_str
    
    @pytest.mark.asyncio
    async def test_load_work_items_with_filters(self, work_item_manager):
        """Test work item loading with various filters."""
        project_name = "TestProject"
        
        work_item_manager.rest_client.query_work_items.return_value = {"workItems": []}
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        await work_item_manager.load_work_items_for_scoring(
            project_name,
            work_item_types=[WorkItemType.EPIC, WorkItemType.FEATURE],
            states=[WorkItemState.NEW, WorkItemState.ACTIVE],
            area_path="MyArea",
            iteration_path="Sprint 1",
            max_items=100
        )
        
        # Verify query construction with filters
        query_call = work_item_manager.rest_client.query_work_items.call_args
        query_str = query_call[0][1]
        
        assert "[Work Item Type] IN ('Epic', 'Feature')" in query_str
        assert "[State] IN ('New', 'Active')" in query_str
        assert "[Area Path] UNDER 'MyArea'" in query_str
        assert "[Iteration Path] UNDER 'Sprint 1'" in query_str
        
        # Verify max_items parameter
        assert query_call[1]["max_results"] == 100
    
    @pytest.mark.asyncio
    async def test_load_work_items_empty_result(self, work_item_manager):
        """Test work item loading with empty result."""
        project_name = "TestProject"
        
        work_item_manager.rest_client.query_work_items.return_value = {"workItems": []}
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        work_items = await work_item_manager.load_work_items_for_scoring(project_name)
        
        assert len(work_items) == 0
        
        # Should not call batch get since no work items found
        work_item_manager.rest_client.get_work_items_batch.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_load_work_items_with_qvf_fields(self, work_item_manager):
        """Test work item loading including existing QVF fields."""
        project_name = "TestProject"
        
        work_item_manager.rest_client.query_work_items.return_value = {"workItems": [{"id": 123}]}
        work_item_manager.rest_client.get_work_items_batch.return_value = [
            {"id": 123, "fields": {"System.Title": "Test"}}
        ]
        
        # Mock QVF field definitions
        qvf_fields = {
            "QVF.Score": Mock(reference_name="Custom.QVFScore"),
            "QVF.Confidence": Mock(reference_name="Custom.QVFConfidence")
        }
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = qvf_fields
        
        await work_item_manager.load_work_items_for_scoring(
            project_name,
            include_qvf_fields=True
        )
        
        # Verify QVF fields were included in the query
        query_call = work_item_manager.rest_client.query_work_items.call_args
        query_str = query_call[0][1]
        assert "[Custom.QVFScore]" in query_str
        assert "[Custom.QVFConfidence]" in query_str
    
    @pytest.mark.asyncio
    async def test_load_work_items_batch_processing(self, work_item_manager):
        """Test batch processing during work item loading."""
        project_name = "TestProject"
        
        # Create more work items than batch size (5)
        work_item_ids = list(range(101, 121))  # 20 work items
        query_response = {"workItems": [{"id": wid} for wid in work_item_ids]}
        
        work_item_manager.rest_client.query_work_items.return_value = query_response
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        # Mock batch responses
        def mock_batch_response(project, ids, fields=None):
            return [{"id": wid, "fields": {"System.Title": f"Item {wid}"}} for wid in ids]
        
        work_item_manager.rest_client.get_work_items_batch.side_effect = mock_batch_response
        
        work_items = await work_item_manager.load_work_items_for_scoring(project_name)
        
        assert len(work_items) == 20
        
        # Should have made 4 batch calls (20 items / 5 batch size = 4 batches)
        assert work_item_manager.rest_client.get_work_items_batch.call_count == 4
        
        # Verify batch sizes
        batch_calls = work_item_manager.rest_client.get_work_items_batch.call_args_list
        for i, call in enumerate(batch_calls):
            ids = call[0][1]  # Second argument is the IDs list
            if i < 3:  # First 3 batches should be full
                assert len(ids) == 5
            else:  # Last batch should have remaining items
                assert len(ids) == 5
    
    @pytest.mark.asyncio
    async def test_update_work_item_scores_basic(self, work_item_manager):
        """Test basic work item score updates."""
        project_name = "TestProject"
        
        # Create test scores
        scores = {
            123: QVFWorkItemScore(work_item_id=123, overall_score=0.85, configuration_id="test"),
            124: QVFWorkItemScore(work_item_id=124, overall_score=0.75, configuration_id="test")
        }
        
        # Mock successful field updates
        mock_update_results = {
            123: Mock(is_successful=True, errors=[]),
            124: Mock(is_successful=True, errors=[])
        }
        work_item_manager.fields_manager.update_work_item_scores.return_value = mock_update_results
        
        result = await work_item_manager.update_work_item_scores(project_name, scores)
        
        assert result.total_items == 2
        assert result.successful_updates == 2
        assert result.failed_updates == 0
        assert result.success_rate == 100.0
        
        # Verify field updates were called
        work_item_manager.fields_manager.update_work_item_scores.assert_called_once()
        update_call = work_item_manager.fields_manager.update_work_item_scores.call_args
        assert project_name in update_call[0]
        field_updates = update_call[0][1]
        assert 123 in field_updates
        assert 124 in field_updates
    
    @pytest.mark.asyncio
    async def test_update_work_item_scores_dict_input(self, work_item_manager):
        """Test work item score updates with dictionary input."""
        project_name = "TestProject"
        
        # Create test scores as dictionaries
        scores = {
            123: {"overall_score": 0.85, "business_value": 0.9},
            124: {"overall_score": 0.75, "strategic_alignment": 0.8}
        }
        
        mock_update_results = {
            123: Mock(is_successful=True, errors=[]),
            124: Mock(is_successful=True, errors=[])
        }
        work_item_manager.fields_manager.update_work_item_scores.return_value = mock_update_results
        
        result = await work_item_manager.update_work_item_scores(
            project_name,
            scores,
            configuration_id="test_config"
        )
        
        assert result.total_items == 2
        assert result.successful_updates == 2
        
        # Verify scores were normalized to QVFWorkItemScore objects
        update_call = work_item_manager.fields_manager.update_work_item_scores.call_args
        field_updates = update_call[0][1]
        
        # Should contain configuration_id added to all updates
        for updates in field_updates.values():
            assert "Custom.QVFConfigurationId" in updates
            assert updates["Custom.QVFConfigurationId"] == "test_config"
    
    @pytest.mark.asyncio
    async def test_update_work_item_scores_with_failures(self, work_item_manager):
        """Test work item score updates with some failures."""
        project_name = "TestProject"
        
        scores = {
            123: QVFWorkItemScore(work_item_id=123, overall_score=0.85, configuration_id="test"),
            124: QVFWorkItemScore(work_item_id=124, overall_score=0.75, configuration_id="test"),
            125: QVFWorkItemScore(work_item_id=125, overall_score=0.65, configuration_id="test")
        }
        
        # Mock mixed results
        mock_update_results = {
            123: Mock(is_successful=True, errors=[]),
            124: Mock(is_successful=False, errors=["Permission denied"]),
            125: Mock(is_successful=True, errors=[])
        }
        work_item_manager.fields_manager.update_work_item_scores.return_value = mock_update_results
        
        result = await work_item_manager.update_work_item_scores(project_name, scores)
        
        assert result.total_items == 3
        assert result.successful_updates == 2
        assert result.failed_updates == 1
        assert result.success_rate == (2.0 / 3.0) * 100  # 66.67%
        
        # Check error categorization
        assert "Permission" in result.error_summary
        assert result.error_summary["Permission"] == 1
    
    @pytest.mark.asyncio
    async def test_score_validation(self, work_item_manager):
        """Test score validation functionality."""
        project_name = "TestProject"
        
        # Mix of valid and invalid scores
        scores = {
            123: QVFWorkItemScore(work_item_id=123, overall_score=0.85, configuration_id="test"),
            124: QVFWorkItemScore(work_item_id=124, overall_score=1.5, configuration_id="test"),  # Invalid
            125: QVFWorkItemScore(work_item_id=125, overall_score=-0.1, configuration_id="test")  # Invalid
        }
        
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        work_item_manager.fields_manager.update_work_item_scores.return_value = {}
        
        with patch.object(work_item_manager, '_validate_scores') as mock_validate:
            # Mock validation to return only valid scores
            mock_validate.return_value = {123: scores[123]}  # Only valid score
            
            result = await work_item_manager.update_work_item_scores(
                project_name,
                scores,
                validate_scores=True
            )
            
            mock_validate.assert_called_once()
            # Should only process the valid score
            update_call = work_item_manager.fields_manager.update_work_item_scores.call_args
            field_updates = update_call[0][1]
            assert len(field_updates) == 1
            assert 123 in field_updates
    
    @pytest.mark.asyncio
    async def test_batch_processing_large_update(self, work_item_manager):
        """Test batch processing for large score updates."""
        project_name = "TestProject"
        
        # Create more scores than batch size (5)
        scores = {}
        for i in range(12):  # 12 work items, batch size = 5
            work_item_id = 100 + i
            scores[work_item_id] = QVFWorkItemScore(
                work_item_id=work_item_id,
                overall_score=0.7 + (i * 0.01),
                configuration_id="test"
            )
        
        # Mock successful updates
        mock_update_results = {}
        for work_item_id in scores.keys():
            mock_update_results[work_item_id] = Mock(is_successful=True, errors=[])
        
        work_item_manager.fields_manager.update_work_item_scores.return_value = mock_update_results
        
        result = await work_item_manager.update_work_item_scores(project_name, scores)
        
        assert result.total_items == 12
        assert result.successful_updates == 12
        assert len(result.batch_results) == 3  # 12 items / 5 batch size = 3 batches (rounded up)
        
        # Check batch sizes
        batch_sizes = [batch.total_items for batch in result.batch_results]
        assert batch_sizes == [5, 5, 2]  # First 2 full batches, last batch with 2 items
    
    @pytest.mark.asyncio
    async def test_get_work_item_qvf_history(self, work_item_manager):
        """Test QVF history retrieval for work item."""
        project_name = "TestProject"
        work_item_id = 123
        
        # Mock current work item data
        current_item = {
            "id": 123,
            "fields": {
                "System.Title": "Test Feature",
                "System.WorkItemType": "Feature",
                "System.State": "Active",
                "Custom.QVFScore": 0.85,
                "Custom.QVFLastCalculated": "2025-01-01T10:00:00Z",
                "Custom.QVFConfigurationId": "test_config"
            }
        }
        
        work_item_manager.rest_client.get_work_item.return_value = current_item
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {
            "QVF.Score": Mock(reference_name="Custom.QVFScore"),
            "QVF.LastCalculated": Mock(reference_name="Custom.QVFLastCalculated"),
            "QVF.ConfigurationId": Mock(reference_name="Custom.QVFConfigurationId")
        }
        
        history = await work_item_manager.get_work_item_qvf_history(
            project_name,
            work_item_id,
            include_revisions=True
        )
        
        assert history["work_item_id"] == 123
        assert history["title"] == "Test Feature"
        assert history["work_item_type"] == "Feature"
        assert history["has_qvf_data"] is True
        assert "current_qvf_values" in history
        assert "revision_history" in history
        
        # Check current values
        qvf_values = history["current_qvf_values"]
        assert "QVF.Score" in qvf_values
        assert qvf_values["QVF.Score"] == 0.85
    
    @pytest.mark.asyncio
    async def test_get_work_item_qvf_history_not_found(self, work_item_manager):
        """Test QVF history retrieval for non-existent work item."""
        project_name = "TestProject"
        work_item_id = 999
        
        work_item_manager.rest_client.get_work_item.return_value = None
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        history = await work_item_manager.get_work_item_qvf_history(project_name, work_item_id)
        
        assert "error" in history
        assert "not found" in history["error"].lower()
    
    def test_get_operation_statistics(self, work_item_manager):
        """Test operation statistics retrieval."""
        # Mock statistics from dependencies
        work_item_manager.rest_client.get_performance_stats.return_value = {
            "total_requests": 100,
            "success_rate": 95.0,
            "average_request_time_ms": 250.0
        }
        
        work_item_manager.fields_manager.get_operation_statistics.return_value = {
            "fields_created": 5,
            "fields_updated": 10
        }
        
        # Set some local stats
        work_item_manager._operation_stats["work_items_loaded"] = 500
        work_item_manager._operation_stats["work_items_updated"] = 450
        
        stats = work_item_manager.get_operation_statistics()
        
        assert "work_item_manager" in stats
        assert "rest_client" in stats
        assert "fields_manager" in stats
        assert "combined_metrics" in stats
        
        assert stats["work_item_manager"]["work_items_loaded"] == 500
        assert stats["work_item_manager"]["work_items_updated"] == 450
        assert stats["combined_metrics"]["total_requests"] == 100
    
    @pytest.mark.asyncio
    async def test_validate_qvf_setup(self, work_item_manager):
        """Test QVF setup validation."""
        project_name = "TestProject"
        
        # Mock validation responses
        work_item_manager.fields_manager.validate_project_permissions.return_value = (True, [])
        work_item_manager.fields_manager.check_existing_fields.return_value = ["QVF.Score", "QVF.Confidence"]
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {
            "QVF.Score": Mock(),
            "QVF.Confidence": Mock(),
            "QVF.BusinessValue": Mock()  # This one is missing
        }
        
        # Mock sample work items loading
        with patch.object(work_item_manager, 'load_work_items_for_scoring') as mock_load:
            mock_load.return_value = [
                {"id": 123, "fields": {"System.Title": "Test"}},
                {"id": 124, "fields": {"System.Title": "Test 2"}}
            ]
            
            validation = await work_item_manager.validate_qvf_setup(project_name)
        
        assert validation["project_name"] == project_name
        assert validation["is_valid"] is True
        assert validation["permissions"]["has_required_permissions"] is True
        assert validation["fields"]["total_qvf_fields"] == 3
        assert validation["fields"]["existing_fields"] == 2
        assert len(validation["fields"]["missing_fields"]) == 1
        assert validation["work_items"]["sample_size"] == 2
        assert validation["work_items"]["has_work_items"] is True
    
    @pytest.mark.asyncio
    async def test_validate_qvf_setup_with_issues(self, work_item_manager):
        """Test QVF setup validation with permission and field issues."""
        project_name = "TestProject"
        
        # Mock validation with issues
        work_item_manager.fields_manager.validate_project_permissions.return_value = (
            False, 
            ["Missing 'Edit work items' permission"]
        )
        work_item_manager.fields_manager.check_existing_fields.return_value = []
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {
            "QVF.Score": Mock(),
            "QVF.Confidence": Mock()
        }
        
        # Mock no work items found
        with patch.object(work_item_manager, 'load_work_items_for_scoring') as mock_load:
            mock_load.return_value = []
            
            validation = await work_item_manager.validate_qvf_setup(project_name)
        
        assert validation["is_valid"] is False
        assert len(validation["errors"]) > 0
        assert len(validation["warnings"]) > 0
        assert validation["permissions"]["has_required_permissions"] is False
        assert validation["fields"]["existing_fields"] == 0
        assert validation["work_items"]["has_work_items"] is False
    
    @pytest.mark.asyncio
    async def test_error_handling_in_load_work_items(self, work_item_manager):
        """Test error handling in work item loading."""
        project_name = "TestProject"
        
        # Mock API error
        work_item_manager.rest_client.query_work_items.side_effect = ADOApiError("API Error")
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        with pytest.raises(WorkItemManagementError):
            await work_item_manager.load_work_items_for_scoring(project_name)
    
    @pytest.mark.asyncio
    async def test_error_handling_in_update_scores(self, work_item_manager):
        """Test error handling in score updates."""
        project_name = "TestProject"
        scores = {123: QVFWorkItemScore(work_item_id=123, overall_score=0.85, configuration_id="test")}
        
        # Mock fields manager error
        work_item_manager.fields_manager.update_work_item_scores.side_effect = Exception("Update failed")
        
        with pytest.raises(WorkItemManagementError):
            await work_item_manager.update_work_item_scores(project_name, scores)


class TestWorkItemManagerIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_qvf_scoring_workflow(self, work_item_manager):
        """Test complete QVF scoring workflow from load to update."""
        project_name = "TestProject"
        
        # Step 1: Load work items
        query_response = {"workItems": [{"id": 123}, {"id": 124}]}
        work_items_response = [
            {
                "id": 123,
                "fields": {
                    "System.Title": "Feature A",
                    "System.WorkItemType": "Feature",
                    "Microsoft.VSTS.Common.BusinessValue": 20
                }
            },
            {
                "id": 124,
                "fields": {
                    "System.Title": "Feature B", 
                    "System.WorkItemType": "Feature",
                    "Microsoft.VSTS.Common.BusinessValue": 30
                }
            }
        ]
        
        work_item_manager.rest_client.query_work_items.return_value = query_response
        work_item_manager.rest_client.get_work_items_batch.return_value = work_items_response
        work_item_manager.fields_manager.get_qvf_field_definitions.return_value = {}
        
        # Load work items
        work_items = await work_item_manager.load_work_items_for_scoring(project_name)
        assert len(work_items) == 2
        
        # Step 2: Calculate QVF scores (simulated)
        qvf_scores = {}
        for item in work_items:
            work_item_id = item["id"]
            business_value = item["fields"].get("Microsoft.VSTS.Common.BusinessValue", 0)
            # Simple scoring based on business value (normalized)
            score = min(1.0, business_value / 50.0)
            
            qvf_scores[work_item_id] = QVFWorkItemScore(
                work_item_id=work_item_id,
                overall_score=score,
                business_value=score,
                configuration_id="integration_test_v1"
            )
        
        # Step 3: Update work items with scores
        mock_update_results = {
            wid: Mock(is_successful=True, errors=[]) 
            for wid in qvf_scores.keys()
        }
        work_item_manager.fields_manager.update_work_item_scores.return_value = mock_update_results
        
        update_result = await work_item_manager.update_work_item_scores(project_name, qvf_scores)
        
        assert update_result.total_items == 2
        assert update_result.successful_updates == 2
        assert update_result.success_rate == 100.0
        
        # Verify the complete workflow
        work_item_manager.rest_client.query_work_items.assert_called_once()
        work_item_manager.rest_client.get_work_items_batch.assert_called_once()
        work_item_manager.fields_manager.update_work_item_scores.assert_called_once()
        
        # Check that scores were calculated correctly
        assert qvf_scores[123].overall_score == 20 / 50  # 0.4
        assert qvf_scores[124].overall_score == 30 / 50  # 0.6


if __name__ == "__main__":
    # Run tests with: python -m pytest test_work_items.py -v
    pytest.main([__file__, "-v", "--tb=short"])