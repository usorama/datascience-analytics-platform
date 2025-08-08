"""Tests for Ollama Manager

These tests verify Ollama connection management, model operations,
and graceful degradation when service is unavailable.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from pathlib import Path
import tempfile
import aiohttp
import asyncio
from datetime import datetime

from ..ollama_manager import (
    OllamaManager, 
    OllamaHealth, 
    ModelInfo, 
    InferenceRequest, 
    InferenceResponse
)


class TestOllamaManager:
    """Test suite for OllamaManager."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_requests(self):
        """Mock requests module."""
        with patch('datascience_platform.qvf.ai.ollama_manager.requests') as mock_requests:
            yield mock_requests
    
    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil module."""
        with patch('datascience_platform.qvf.ai.ollama_manager.psutil') as mock_psutil:
            yield mock_psutil
    
    @pytest.fixture
    def manager_healthy(self, temp_cache_dir, mock_requests, mock_psutil):
        """Create OllamaManager with healthy mocked service."""
        # Mock process detection
        mock_process = Mock()
        mock_process.name.return_value = "ollama"
        mock_psutil.process_iter.return_value = [mock_process]
        
        # Mock API responses
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {
                    "name": "llama2:7b",
                    "size": 3800000000,
                    "modified_at": "2024-01-01T10:00:00Z",
                    "details": {
                        "family": "llama",
                        "parameter_size": "7B",
                        "quantization_level": "Q4_0"
                    }
                },
                {
                    "name": "mistral:7b",
                    "size": 4100000000, 
                    "modified_at": "2024-01-02T10:00:00Z",
                    "details": {
                        "family": "mistral",
                        "parameter_size": "7B",
                        "quantization_level": "Q4_0"
                    }
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        
        return OllamaManager(cache_dir=temp_cache_dir, cache_ttl=1)
    
    @pytest.fixture
    def manager_unhealthy(self, temp_cache_dir, mock_requests, mock_psutil):
        """Create OllamaManager with unhealthy mocked service."""
        # Mock no process
        mock_psutil.process_iter.return_value = []
        
        return OllamaManager(cache_dir=temp_cache_dir)
    
    def test_initialization_healthy_service(self, manager_healthy):
        """Test initialization with healthy Ollama service."""
        assert manager_healthy.is_available()
        assert manager_healthy._health_status == OllamaHealth.HEALTHY
        assert len(manager_healthy._available_models) == 2
        assert manager_healthy._preferred_model is not None
        assert "llama2" in manager_healthy._preferred_model or "mistral" in manager_healthy._preferred_model
    
    def test_initialization_unhealthy_service(self, manager_unhealthy):
        """Test initialization with unhealthy Ollama service."""
        assert not manager_unhealthy.is_available()
        assert manager_unhealthy._health_status == OllamaHealth.UNAVAILABLE
        assert len(manager_unhealthy._available_models) == 0
        assert manager_unhealthy._preferred_model is None
    
    def test_health_status_reporting(self, manager_healthy):
        """Test health status reporting."""
        status = manager_healthy.get_health_status()
        
        assert status['status'] == OllamaHealth.HEALTHY.value
        assert 'last_check' in status
        assert status['available_models'] == 2
        assert status['preferred_model'] is not None
        assert 'performance_stats' in status
        
        perf_stats = status['performance_stats']
        assert 'requests' in perf_stats
        assert 'cache_hits' in perf_stats
        assert 'cache_hit_rate' in perf_stats
        assert 'avg_inference_time' in perf_stats
    
    def test_model_selection(self, manager_healthy):
        """Test model selection logic."""
        models = manager_healthy.get_available_models()
        assert len(models) == 2
        
        # Should prefer llama or mistral
        preferred = manager_healthy._preferred_model
        assert preferred is not None
        assert any(family in preferred for family in ['llama', 'mistral'])
        
        # Test manual model selection
        success = manager_healthy.set_preferred_model("mistral:7b")
        assert success
        assert manager_healthy._preferred_model == "mistral:7b"
        
        # Test invalid model selection
        success = manager_healthy.set_preferred_model("nonexistent:model")
        assert not success
        assert manager_healthy._preferred_model == "mistral:7b"  # Should remain unchanged
    
    def test_generate_with_healthy_service(self, manager_healthy, mock_requests):
        """Test text generation with healthy service."""
        # Mock generate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2:7b",
            "response": "This is a test response from the model.",
            "done": True,
            "context": [1, 2, 3, 4, 5],
            "total_duration": 1000000000,
            "load_duration": 100000000,
            "prompt_eval_count": 10,
            "prompt_eval_duration": 200000000,
            "eval_count": 20,
            "eval_duration": 300000000
        }
        mock_requests.post.return_value = mock_response
        
        result = manager_healthy.generate(
            prompt="Test prompt",
            system="You are a helpful assistant",
            options={"temperature": 0.3}
        )
        
        assert result is not None
        assert isinstance(result, InferenceResponse)
        assert result.model == "llama2:7b"
        assert result.response == "This is a test response from the model."
        assert result.done
        assert result.context == [1, 2, 3, 4, 5]
        assert result.tokens_per_second is not None
        
        # Verify API was called correctly
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        assert "api/generate" in call_args[0][0]
        
        request_data = call_args[1]['json']
        assert request_data['prompt'] == "Test prompt"
        assert request_data['system'] == "You are a helpful assistant"
        assert request_data['options']['temperature'] == 0.3
    
    def test_generate_with_unhealthy_service(self, manager_unhealthy):
        """Test generation with unhealthy service returns None."""
        result = manager_unhealthy.generate("Test prompt")
        assert result is None
    
    def test_caching_functionality(self, manager_healthy, mock_requests):
        """Test response caching."""
        # Mock generate API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2:7b",
            "response": "Cached response",
            "done": True
        }
        mock_requests.post.return_value = mock_response
        
        # First request - should hit API
        result1 = manager_healthy.generate("Test prompt", use_cache=True)
        assert result1 is not None
        assert result1.response == "Cached response"
        assert mock_requests.post.call_count == 1
        
        # Second identical request - should use cache
        result2 = manager_healthy.generate("Test prompt", use_cache=True)
        assert result2 is not None
        assert result2.response == "Cached response"
        assert mock_requests.post.call_count == 1  # No additional API call
        
        # Check performance stats
        stats = manager_healthy.get_performance_stats()
        assert stats['requests_total'] == 2
        assert stats['cache_hits'] == 1
        assert stats['cache_hit_rate'] == 0.5
    
    def test_cache_disabled(self, manager_healthy, mock_requests):
        """Test generation with caching disabled."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "llama2:7b",
            "response": "No cache response",
            "done": True
        }
        mock_requests.post.return_value = mock_response
        
        # Two identical requests with caching disabled
        result1 = manager_healthy.generate("Test prompt", use_cache=False)
        result2 = manager_healthy.generate("Test prompt", use_cache=False) 
        
        assert result1 is not None
        assert result2 is not None
        assert mock_requests.post.call_count == 2  # Should call API twice
        
        # No cache hits
        stats = manager_healthy.get_performance_stats()
        assert stats['cache_hits'] == 0
    
    def test_api_error_handling(self, manager_healthy, mock_requests):
        """Test handling of API errors."""
        # Mock API error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_requests.post.return_value = mock_response
        
        result = manager_healthy.generate("Test prompt")
        assert result is None
    
    def test_timeout_handling(self, manager_healthy, mock_requests):
        """Test handling of request timeouts."""
        mock_requests.post.side_effect = requests.exceptions.Timeout()
        
        result = manager_healthy.generate("Test prompt")
        assert result is None
    
    def test_network_error_handling(self, manager_healthy, mock_requests):
        """Test handling of network errors."""
        mock_requests.post.side_effect = requests.exceptions.ConnectionError()
        
        result = manager_healthy.generate("Test prompt")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_async_generate(self, manager_healthy):
        """Test async text generation."""
        # Mock aiohttp response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "model": "llama2:7b", 
            "response": "Async test response",
            "done": True
        })
        
        mock_session = Mock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch('aiohttp.ClientSession') as mock_client_session:
            mock_client_session.return_value.__aenter__.return_value = mock_session
            
            result = await manager_healthy.generate_async("Test async prompt")
            
            assert result is not None
            assert result.response == "Async test response"
    
    @pytest.mark.asyncio
    async def test_async_generate_unhealthy(self, manager_unhealthy):
        """Test async generation with unhealthy service."""
        result = await manager_unhealthy.generate_async("Test prompt")
        assert result is None
    
    def test_model_pulling(self, manager_healthy, mock_requests):
        """Test model pulling functionality."""
        # Mock pull API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        success = manager_healthy.pull_model("codellama:7b")
        assert success
        
        # Should have called pull API
        mock_requests.post.assert_called()
        call_args = mock_requests.post.call_args
        assert "api/pull" in call_args[0][0]
        assert call_args[1]['json']['name'] == "codellama:7b"
    
    def test_model_pull_failure(self, manager_healthy, mock_requests):
        """Test model pull failure handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.post.return_value = mock_response
        
        success = manager_healthy.pull_model("nonexistent:model")
        assert not success
    
    def test_model_pull_unhealthy_service(self, manager_unhealthy):
        """Test model pulling with unhealthy service."""
        success = manager_unhealthy.pull_model("test:model")
        assert not success
    
    def test_cache_management(self, manager_healthy, temp_cache_dir):
        """Test cache file management."""
        # Create some fake cache files
        for i in range(5):
            cache_file = temp_cache_dir / f"cache_{i}.json"
            with open(cache_file, 'w') as f:
                json.dump({"test": f"data_{i}"}, f)
        
        # Clear cache
        cleared_count = manager_healthy.clear_cache()
        assert cleared_count == 5
        
        # Verify files are gone
        remaining_files = list(temp_cache_dir.glob("*.json"))
        assert len(remaining_files) == 0
    
    def test_performance_stats(self, manager_healthy):
        """Test performance statistics tracking."""
        initial_stats = manager_healthy.get_performance_stats()
        assert initial_stats['requests_total'] == 0
        assert initial_stats['cache_hits'] == 0
        assert initial_stats['total_inference_time'] == 0.0
        
        # Simulate some activity by directly updating internal counters
        manager_healthy._request_count = 10
        manager_healthy._cache_hits = 3
        manager_healthy._total_inference_time = 25.5
        
        stats = manager_healthy.get_performance_stats()
        assert stats['requests_total'] == 10
        assert stats['cache_hits'] == 3
        assert stats['cache_hit_rate'] == 0.3
        assert stats['avg_inference_time'] == 2.55
        assert stats['total_inference_time'] == 25.5
    
    def test_inference_request_serialization(self):
        """Test InferenceRequest serialization."""
        request = InferenceRequest(
            model="test:model",
            prompt="Test prompt", 
            system="Test system",
            options={"temperature": 0.5, "top_p": 0.9}
        )
        
        request_dict = request.to_dict()
        assert request_dict['model'] == "test:model"
        assert request_dict['prompt'] == "Test prompt"
        assert request_dict['system'] == "Test system"
        assert request_dict['options']['temperature'] == 0.5
        assert 'context' not in request_dict  # Should exclude None values
    
    def test_inference_response_tokens_per_second(self):
        """Test InferenceResponse tokens per second calculation."""
        response = InferenceResponse(
            model="test:model",
            response="Test response",
            eval_count=100,
            eval_duration=2000000000  # 2 seconds in nanoseconds
        )
        
        tokens_per_sec = response.tokens_per_second
        assert tokens_per_sec is not None
        assert tokens_per_sec == 50.0  # 100 tokens / 2 seconds
        
        # Test with missing data
        response_incomplete = InferenceResponse(
            model="test:model", 
            response="Test response"
        )
        assert response_incomplete.tokens_per_second is None
    
    def test_health_check_interval(self, manager_healthy):
        """Test health check interval behavior."""
        # Initial check should have happened
        initial_check_time = manager_healthy._last_health_check
        
        # Immediate second check should use cached result
        assert manager_healthy.is_available()
        assert manager_healthy._last_health_check == initial_check_time
        
        # Force health check interval to pass
        manager_healthy._health_check_interval = timedelta(seconds=0)
        
        # Now should trigger new health check
        assert manager_healthy.is_available()
        assert manager_healthy._last_health_check > initial_check_time


class AsyncMock(MagicMock):
    """Helper for mocking async methods."""
    
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)