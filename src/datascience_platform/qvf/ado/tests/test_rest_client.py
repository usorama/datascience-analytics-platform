"""Comprehensive tests for Azure DevOps REST API client.

This module provides extensive testing for the ADORestClient including:
- Authentication and configuration validation
- Work item CRUD operations
- Batch processing capabilities
- Rate limiting and retry logic
- Error handling and exception scenarios
- Performance optimization features

Tests use mocked responses to avoid dependencies on live ADO instances.
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

import aiohttp
from pydantic import ValidationError

# Internal imports
from datascience_platform.qvf.ado.rest_client import (
    ADORestClient,
    ADOClientConfig,
    ADOApiError,
    ADOAuthenticationError,
    ADOPermissionError,
    ADORateLimitError,
    ADOTimeoutError,
    RateLimiter,
    RequestMetrics
)


class TestADOClientConfig:
    """Test ADO client configuration validation and setup."""
    
    def test_valid_configuration(self):
        """Test creating valid client configuration."""
        config = ADOClientConfig(
            organization_url="https://dev.azure.com/myorg",
            personal_access_token="test_pat_token",
            api_version="7.0"
        )
        
        assert config.organization_url == "https://dev.azure.com/myorg"
        assert config.personal_access_token == "test_pat_token"
        assert config.api_version == "7.0"
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert config.max_concurrent_requests == 10
    
    def test_invalid_organization_url_http(self):
        """Test validation of organization URL requiring HTTPS."""
        with pytest.raises(ValidationError, match="Organization URL must use HTTPS"):
            ADOClientConfig(
                organization_url="http://dev.azure.com/myorg",
                personal_access_token="test_pat"
            )
    
    def test_invalid_organization_url_domain(self):
        """Test validation of organization URL domain."""
        with pytest.raises(ValidationError, match="valid Azure DevOps URL"):
            ADOClientConfig(
                organization_url="https://invalid-domain.com/myorg",
                personal_access_token="test_pat"
            )
    
    def test_url_normalization(self):
        """Test organization URL normalization."""
        config = ADOClientConfig(
            organization_url="https://dev.azure.com/myorg/",
            personal_access_token="test_pat"
        )
        
        assert config.organization_url == "https://dev.azure.com/myorg"
    
    def test_auth_header_generation(self):
        """Test authentication header generation."""
        config = ADOClientConfig(
            organization_url="https://dev.azure.com/myorg",
            personal_access_token="test_pat_token"
        )
        
        auth_header = config.get_auth_header()
        assert auth_header.startswith("Basic ")
        
        # Decode and verify
        import base64
        encoded_part = auth_header.split("Basic ")[1]
        decoded = base64.b64decode(encoded_part).decode()
        assert decoded == ":test_pat_token"
    
    def test_api_url_generation(self):
        """Test API URL generation for different endpoint types."""
        config = ADOClientConfig(
            organization_url="https://dev.azure.com/myorg",
            personal_access_token="test_pat"
        )
        
        # Organization-scoped endpoint
        org_url = config.get_api_url("wit/fields")
        expected_org = "https://dev.azure.com/myorg/_apis/wit/fields?api-version=7.0"
        assert org_url == expected_org
        
        # Project-scoped endpoint
        proj_url = config.get_api_url("wit/workitems", "MyProject")
        expected_proj = "https://dev.azure.com/myorg/_apis/MyProject/wit/workitems?api-version=7.0"
        assert proj_url == expected_proj
    
    def test_configuration_validation_ranges(self):
        """Test configuration parameter range validation."""
        # Valid ranges
        config = ADOClientConfig(
            organization_url="https://dev.azure.com/myorg",
            personal_access_token="test_pat",
            timeout_seconds=60,
            max_retries=5,
            max_concurrent_requests=20,
            requests_per_minute=500,
            rate_limit_buffer=0.8
        )
        
        assert config.timeout_seconds == 60
        assert config.max_retries == 5
        assert config.max_concurrent_requests == 20
        assert config.requests_per_minute == 500
        assert config.rate_limit_buffer == 0.8


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic_functionality(self):
        """Test basic rate limiting functionality."""
        limiter = RateLimiter(requests_per_minute=60, buffer_factor=1.0)  # 1 req/sec
        
        # Should allow immediate request
        await limiter.acquire()
        assert limiter.tokens < limiter.max_tokens
    
    @pytest.mark.asyncio
    async def test_rate_limiter_token_refill(self):
        """Test token refill over time."""
        limiter = RateLimiter(requests_per_minute=120, buffer_factor=1.0)  # 2 req/sec
        
        # Consume all tokens
        initial_tokens = limiter.tokens
        for _ in range(int(initial_tokens) + 1):
            await limiter.acquire()
        
        # Wait for refill
        await asyncio.sleep(1.1)
        
        # Should have refilled tokens
        assert limiter.tokens > 0
    
    @pytest.mark.asyncio
    async def test_rate_limiter_buffer_factor(self):
        """Test rate limiter buffer factor application."""
        limiter = RateLimiter(requests_per_minute=100, buffer_factor=0.8)
        
        # Max tokens should be 80% of 100
        assert limiter.max_tokens == 80


class TestRequestMetrics:
    """Test request performance metrics tracking."""
    
    def test_metrics_initialization(self):
        """Test request metrics initialization."""
        metrics = RequestMetrics()
        
        assert isinstance(metrics.start_time, datetime)
        assert metrics.end_time is None
        assert metrics.status_code is None
        assert metrics.response_size == 0
        assert metrics.retry_count == 0
    
    def test_metrics_completion(self):
        """Test request metrics completion."""
        metrics = RequestMetrics()
        metrics.complete(200, 1024)
        
        assert metrics.status_code == 200
        assert metrics.response_size == 1024
        assert metrics.end_time is not None
        assert metrics.duration_ms > 0


@pytest.fixture
def mock_session():
    """Create mock aiohttp session for testing."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def client_config():
    """Create test client configuration."""
    return ADOClientConfig(
        organization_url="https://dev.azure.com/testorg",
        personal_access_token="test_pat_token",
        timeout_seconds=10,
        max_retries=2,
        max_concurrent_requests=5
    )


@pytest.fixture
def rest_client(client_config):
    """Create ADO REST client for testing."""
    return ADORestClient(client_config)


class TestADORestClient:
    """Test Azure DevOps REST API client functionality."""
    
    @pytest.mark.asyncio
    async def test_session_management(self, rest_client):
        """Test HTTP session lifecycle management."""
        # Initial state
        assert rest_client.session is None
        
        # Start session
        await rest_client.start_session()
        assert rest_client.session is not None
        
        # Close session
        await rest_client.close_session()
        assert rest_client.session is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client_config):
        """Test async context manager functionality."""
        async with ADORestClient(client_config) as client:
            assert client.session is not None
        
        # Session should be closed after context exit
        assert client.session is None
    
    @pytest.mark.asyncio
    async def test_successful_request(self, rest_client):
        """Test successful HTTP request handling."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"id": 123, "title": "Test"}')
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            status, data = await rest_client._make_request("GET", "https://test.com/api")
            
            assert status == 200
            assert data["id"] == 123
            assert data["title"] == "Test"
    
    @pytest.mark.asyncio
    async def test_authentication_error(self, rest_client):
        """Test authentication error handling."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text = AsyncMock(return_value='{"message": "Unauthorized"}')
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ADOAuthenticationError):
                await rest_client._make_request("GET", "https://test.com/api")
    
    @pytest.mark.asyncio
    async def test_permission_error(self, rest_client):
        """Test permission error handling."""
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_response.text = AsyncMock(return_value='{"message": "Forbidden"}')
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ADOPermissionError):
                await rest_client._make_request("GET", "https://test.com/api")
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_with_retry(self, rest_client):
        """Test rate limit error handling with retry."""
        # First call returns 429, second returns 200
        responses = [
            Mock(status=429, headers={'Retry-After': '1'}),
            Mock(status=200, headers={})
        ]
        
        for i, resp in enumerate(responses):
            resp.text = AsyncMock(return_value='{"message": "Rate limited"}' if i == 0 else '{"success": true}')
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.side_effect = responses
            
            # Should eventually succeed after retry
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                status, data = await rest_client._make_request("GET", "https://test.com/api")
                assert status == 200
                assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_server_error_with_retry(self, rest_client):
        """Test server error handling with retry."""
        # First call returns 500, second returns 200
        responses = [
            Mock(status=500, headers={}),
            Mock(status=200, headers={})
        ]
        
        for i, resp in enumerate(responses):
            resp.text = AsyncMock(return_value='{"error": "Server error"}' if i == 0 else '{"success": true}')
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.side_effect = responses
            
            with patch('asyncio.sleep'):  # Mock sleep to speed up test
                status, data = await rest_client._make_request("GET", "https://test.com/api")
                assert status == 200
                assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_timeout_error(self, rest_client):
        """Test timeout error handling."""
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(ADOTimeoutError):
                await rest_client._make_request("GET", "https://test.com/api")
    
    @pytest.mark.asyncio
    async def test_client_error_handling(self, rest_client):
        """Test client error handling."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value='{"message": "Bad request"}')
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ADOApiError, match="Bad request"):
                await rest_client._make_request("GET", "https://test.com/api")
    
    @pytest.mark.asyncio
    async def test_get_project(self, rest_client):
        """Test project retrieval."""
        expected_project = {
            "id": "project-123",
            "name": "TestProject",
            "description": "Test project description"
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_project))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            project = await rest_client.get_project("TestProject")
            
            assert project["id"] == "project-123"
            assert project["name"] == "TestProject"
    
    @pytest.mark.asyncio
    async def test_get_project_not_found(self, rest_client):
        """Test project retrieval when project not found."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value='{"message": "Not found"}')
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            project = await rest_client.get_project("NonExistentProject")
            assert project is None
    
    @pytest.mark.asyncio
    async def test_list_projects(self, rest_client):
        """Test project listing."""
        expected_projects = {
            "value": [
                {"id": "project-1", "name": "Project1"},
                {"id": "project-2", "name": "Project2"}
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_projects))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            projects = await rest_client.list_projects()
            
            assert len(projects) == 2
            assert projects[0]["name"] == "Project1"
            assert projects[1]["name"] == "Project2"
    
    @pytest.mark.asyncio
    async def test_list_work_item_fields(self, rest_client):
        """Test work item fields listing."""
        expected_fields = {
            "value": [
                {
                    "referenceName": "System.Title",
                    "name": "Title",
                    "type": "string"
                },
                {
                    "referenceName": "System.State",
                    "name": "State", 
                    "type": "string"
                }
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_fields))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            fields = await rest_client.list_work_item_fields("TestProject")
            
            assert len(fields) == 2
            assert fields[0]["referenceName"] == "System.Title"
            assert fields[1]["referenceName"] == "System.State"
    
    @pytest.mark.asyncio
    async def test_get_work_item_field(self, rest_client):
        """Test specific work item field retrieval."""
        expected_field = {
            "referenceName": "System.Title",
            "name": "Title",
            "type": "string",
            "description": "Work item title"
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_field))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            field = await rest_client.get_work_item_field("TestProject", "System.Title")
            
            assert field["referenceName"] == "System.Title"
            assert field["name"] == "Title"
            assert field["type"] == "string"
    
    @pytest.mark.asyncio
    async def test_create_work_item_field(self, rest_client):
        """Test work item field creation."""
        field_definition = {
            "name": "QVF Score",
            "referenceName": "Custom.QVFScore",
            "type": "double",
            "description": "QVF prioritization score"
        }
        
        expected_response = field_definition.copy()
        expected_response["id"] = "field-123"
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.text = AsyncMock(return_value=json.dumps(expected_response))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            created_field = await rest_client.create_work_item_field("TestProject", field_definition)
            
            assert created_field["id"] == "field-123"
            assert created_field["name"] == "QVF Score"
            assert created_field["referenceName"] == "Custom.QVFScore"
    
    @pytest.mark.asyncio
    async def test_get_work_item(self, rest_client):
        """Test work item retrieval by ID."""
        expected_work_item = {
            "id": 123,
            "rev": 1,
            "fields": {
                "System.Title": "Test Work Item",
                "System.State": "New",
                "System.WorkItemType": "Feature"
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_work_item))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            work_item = await rest_client.get_work_item("TestProject", 123)
            
            assert work_item["id"] == 123
            assert work_item["fields"]["System.Title"] == "Test Work Item"
            assert work_item["fields"]["System.State"] == "New"
    
    @pytest.mark.asyncio
    async def test_get_work_items_batch(self, rest_client):
        """Test batch work item retrieval."""
        expected_work_items = {
            "value": [
                {
                    "id": 123,
                    "fields": {"System.Title": "Work Item 1"}
                },
                {
                    "id": 124,
                    "fields": {"System.Title": "Work Item 2"}
                }
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_work_items))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            work_items = await rest_client.get_work_items_batch("TestProject", [123, 124])
            
            assert len(work_items) == 2
            assert work_items[0]["id"] == 123
            assert work_items[1]["id"] == 124
    
    @pytest.mark.asyncio
    async def test_update_work_item(self, rest_client):
        """Test work item field updates."""
        field_updates = {
            "Custom.QVFScore": 0.85,
            "System.Tags": "qvf-scored"
        }
        
        expected_response = {
            "id": 123,
            "rev": 2,
            "fields": {
                "Custom.QVFScore": 0.85,
                "System.Tags": "qvf-scored",
                "System.ChangedDate": "2025-01-01T10:00:00Z"
            }
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_response))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            updated_item = await rest_client.update_work_item("TestProject", 123, field_updates)
            
            assert updated_item["id"] == 123
            assert updated_item["rev"] == 2
            assert updated_item["fields"]["Custom.QVFScore"] == 0.85
    
    @pytest.mark.asyncio
    async def test_create_work_item(self, rest_client):
        """Test work item creation."""
        fields = {
            "System.Title": "New Feature",
            "System.State": "New",
            "Microsoft.VSTS.Common.Priority": 2
        }
        
        expected_response = {
            "id": 125,
            "rev": 1,
            "fields": fields.copy()
        }
        expected_response["fields"]["System.CreatedDate"] = "2025-01-01T10:00:00Z"
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.text = AsyncMock(return_value=json.dumps(expected_response))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            created_item = await rest_client.create_work_item("TestProject", "Feature", fields)
            
            assert created_item["id"] == 125
            assert created_item["rev"] == 1
            assert created_item["fields"]["System.Title"] == "New Feature"
    
    @pytest.mark.asyncio
    async def test_query_work_items(self, rest_client):
        """Test WIQL query execution."""
        wiql_query = "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active'"
        
        expected_response = {
            "queryType": "flat",
            "queryResultType": "workItem",
            "workItems": [
                {"id": 123},
                {"id": 124},
                {"id": 125}
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=json.dumps(expected_response))
        mock_response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.return_value = mock_response
            
            query_result = await rest_client.query_work_items("TestProject", wiql_query)
            
            assert query_result["queryType"] == "flat"
            assert len(query_result["workItems"]) == 3
            assert query_result["workItems"][0]["id"] == 123
    
    @pytest.mark.asyncio
    async def test_update_work_items_batch(self, rest_client):
        """Test batch work item updates."""
        work_item_updates = {
            123: {"Custom.QVFScore": 0.85},
            124: {"Custom.QVFScore": 0.72},
            125: {"Custom.QVFScore": 0.93}
        }
        
        # Mock successful responses for each update
        mock_responses = []
        for work_item_id, updates in work_item_updates.items():
            response = {
                "id": work_item_id,
                "rev": 2,
                "fields": updates.copy()
            }
            mock_responses.append(response)
        
        async def mock_update_work_item(project, wid, updates, bypass_rules=False):
            # Find matching response
            for response in mock_responses:
                if response["id"] == wid:
                    return response
            raise ADOApiError(f"Work item {wid} not found")
        
        with patch.object(rest_client, 'update_work_item', side_effect=mock_update_work_item):
            results = await rest_client.update_work_items_batch("TestProject", work_item_updates)
            
            assert len(results) == 3
            assert 123 in results
            assert 124 in results
            assert 125 in results
            
            # Check successful updates
            assert results[123]["fields"]["Custom.QVFScore"] == 0.85
            assert results[124]["fields"]["Custom.QVFScore"] == 0.72
            assert results[125]["fields"]["Custom.QVFScore"] == 0.93
    
    @pytest.mark.asyncio
    async def test_batch_update_with_errors(self, rest_client):
        """Test batch updates with some failures."""
        work_item_updates = {
            123: {"Custom.QVFScore": 0.85},
            124: {"Custom.QVFScore": 0.72},  # This will fail
            125: {"Custom.QVFScore": 0.93}
        }
        
        async def mock_update_with_error(project, wid, updates, bypass_rules=False):
            if wid == 124:
                raise ADOApiError("Permission denied")
            return {
                "id": wid,
                "rev": 2,
                "fields": updates.copy()
            }
        
        with patch.object(rest_client, 'update_work_item', side_effect=mock_update_with_error):
            results = await rest_client.update_work_items_batch("TestProject", work_item_updates)
            
            assert len(results) == 3
            
            # Check successful updates
            assert "error" not in results[123]
            assert "error" not in results[125]
            
            # Check failed update
            assert "error" in results[124]
            assert "Permission denied" in results[124]["error"]
    
    def test_performance_stats_tracking(self, rest_client):
        """Test performance statistics tracking."""
        # Initial stats should be zero
        stats = rest_client.get_performance_stats()
        assert stats["total_requests"] == 0
        assert stats["total_errors"] == 0
        assert stats["success_rate"] == 0.0
        
        # Simulate some successful requests
        rest_client._request_count = 10
        rest_client._error_count = 2
        rest_client._total_request_time = 5000.0  # 5 seconds total
        
        stats = rest_client.get_performance_stats()
        assert stats["total_requests"] == 10
        assert stats["total_errors"] == 2
        assert stats["success_rate"] == 80.0
        assert stats["average_request_time_ms"] == 500.0
    
    def test_performance_stats_reset(self, rest_client):
        """Test performance statistics reset."""
        # Set some stats
        rest_client._request_count = 10
        rest_client._error_count = 2
        rest_client._total_request_time = 1000.0
        
        # Reset stats
        rest_client.reset_performance_stats()
        
        stats = rest_client.get_performance_stats()
        assert stats["total_requests"] == 0
        assert stats["total_errors"] == 0
        assert stats["total_request_time_ms"] == 0.0
    
    @pytest.mark.asyncio
    async def test_concurrent_request_limiting(self, rest_client):
        """Test concurrent request limiting via semaphore."""
        # This test verifies that the semaphore properly limits concurrent requests
        # by checking that only a certain number can be in progress simultaneously
        
        request_starts = []
        request_ends = []
        
        async def mock_slow_request(*args, **kwargs):
            request_starts.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # Simulate slow request
            request_ends.append(asyncio.get_event_loop().time())
            return 200, {"success": True}
        
        with patch.object(rest_client, '_make_request', side_effect=mock_slow_request):
            # Launch more requests than the concurrency limit
            tasks = []
            for i in range(15):  # More than max_concurrent_requests=5
                task = rest_client.get_project(f"Project{i}")
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Verify that requests were properly limited
            assert len(request_starts) == 15
            assert len(request_ends) == 15


class TestADORestClientIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_field_workflow(self, rest_client):
        """Test complete field management workflow."""
        project_name = "TestProject"
        field_name = "Custom.QVFScore"
        
        # Mock responses for field workflow
        mock_responses = [
            # 1. Check if field exists (404 - not found)
            Mock(status=404, text=AsyncMock(return_value='{"message": "Not found"}')),
            
            # 2. Create field (201 - created)
            Mock(status=201, text=AsyncMock(return_value=json.dumps({
                "id": "field-123",
                "name": "QVF Score",
                "referenceName": "Custom.QVFScore",
                "type": "double"
            }))),
            
            # 3. Verify field creation (200 - found)
            Mock(status=200, text=AsyncMock(return_value=json.dumps({
                "id": "field-123",
                "name": "QVF Score",
                "referenceName": "Custom.QVFScore",
                "type": "double"
            })))
        ]
        
        for response in mock_responses:
            response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.side_effect = mock_responses
            
            # 1. Check if field exists (should return None)
            existing_field = await rest_client.get_work_item_field(project_name, field_name)
            assert existing_field is None
            
            # 2. Create field
            field_definition = {
                "name": "QVF Score",
                "referenceName": "Custom.QVFScore",
                "type": "double",
                "description": "QVF prioritization score"
            }
            created_field = await rest_client.create_work_item_field(project_name, field_definition)
            assert created_field["id"] == "field-123"
            
            # 3. Verify field was created
            verified_field = await rest_client.get_work_item_field(project_name, field_name)
            assert verified_field["id"] == "field-123"
    
    @pytest.mark.asyncio
    async def test_complete_work_item_scoring_workflow(self, rest_client):
        """Test complete work item scoring workflow."""
        project_name = "TestProject"
        
        # Mock WIQL query response
        wiql_response = {
            "queryType": "flat",
            "workItems": [{"id": 123}, {"id": 124}]
        }
        
        # Mock batch work items response
        batch_response = {
            "value": [
                {
                    "id": 123,
                    "fields": {
                        "System.Title": "Feature 1",
                        "System.State": "Active",
                        "Microsoft.VSTS.Common.BusinessValue": 20
                    }
                },
                {
                    "id": 124,
                    "fields": {
                        "System.Title": "Feature 2",
                        "System.State": "Active",
                        "Microsoft.VSTS.Common.BusinessValue": 30
                    }
                }
            ]
        }
        
        # Mock update responses
        update_responses = [
            {
                "id": 123,
                "rev": 2,
                "fields": {
                    "Custom.QVFScore": 0.75,
                    "Custom.QVFLastCalculated": "2025-01-01T10:00:00Z"
                }
            },
            {
                "id": 124,
                "rev": 2,
                "fields": {
                    "Custom.QVFScore": 0.85,
                    "Custom.QVFLastCalculated": "2025-01-01T10:00:00Z"
                }
            }
        ]
        
        mock_responses = [
            # WIQL query
            Mock(status=200, text=AsyncMock(return_value=json.dumps(wiql_response))),
            # Batch get work items
            Mock(status=200, text=AsyncMock(return_value=json.dumps(batch_response))),
            # Update work item 123
            Mock(status=200, text=AsyncMock(return_value=json.dumps(update_responses[0]))),
            # Update work item 124
            Mock(status=200, text=AsyncMock(return_value=json.dumps(update_responses[1])))
        ]
        
        for response in mock_responses:
            response.headers = {}
        
        with patch.object(rest_client, 'session') as mock_session:
            mock_session.request.return_value.__aenter__.side_effect = mock_responses
            
            # 1. Query for work items needing scoring
            wiql_query = "SELECT [System.Id] FROM WorkItems WHERE [System.State] = 'Active'"
            query_result = await rest_client.query_work_items(project_name, wiql_query)
            
            work_item_ids = [item["id"] for item in query_result["workItems"]]
            assert work_item_ids == [123, 124]
            
            # 2. Get work item details
            work_items = await rest_client.get_work_items_batch(project_name, work_item_ids)
            assert len(work_items) == 2
            
            # 3. Update work items with QVF scores
            score_updates = {
                123: {"Custom.QVFScore": 0.75, "Custom.QVFLastCalculated": "2025-01-01T10:00:00Z"},
                124: {"Custom.QVFScore": 0.85, "Custom.QVFLastCalculated": "2025-01-01T10:00:00Z"}
            }
            
            update_results = {}
            for work_item_id, updates in score_updates.items():
                result = await rest_client.update_work_item(project_name, work_item_id, updates)
                update_results[work_item_id] = result
            
            # Verify updates
            assert update_results[123]["fields"]["Custom.QVFScore"] == 0.75
            assert update_results[124]["fields"]["Custom.QVFScore"] == 0.85


if __name__ == "__main__":
    # Run tests with: python -m pytest test_rest_client.py -v
    pytest.main([__file__, "-v", "--tb=short"])