"""Ollama Integration Manager for QVF

This module manages the connection to Ollama server for local LLM inference.
It provides robust connection management, health monitoring, and graceful
fallback when the service is unavailable.

Key Features:
- Automatic Ollama server discovery and connection
- Model management and selection
- Health monitoring with automatic reconnection
- Async operations for non-blocking inference
- Response caching to reduce redundant calls
- Graceful degradation when service unavailable

Architecture:
- Local-first: Prioritizes local Ollama installation
- Privacy-preserving: No external API calls
- Resilient: Handles connection failures gracefully
- Performance-optimized: Caching and async operations
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib

import requests
import aiohttp
from pydantic import BaseModel, Field
import psutil

logger = logging.getLogger(__name__)


class OllamaHealth(Enum):
    """Ollama service health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ModelInfo:
    """Information about an Ollama model."""
    name: str
    size: int
    modified: datetime
    family: str
    parameter_size: str
    quantization: str
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass 
class InferenceRequest:
    """Request for LLM inference."""
    model: str
    prompt: str
    system: Optional[str] = None
    context: Optional[List[int]] = None
    options: Optional[Dict[str, Any]] = None
    stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API requests."""
        data = asdict(self)
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class InferenceResponse:
    """Response from LLM inference."""
    model: str
    response: str
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    done: bool = True
    
    @property
    def tokens_per_second(self) -> Optional[float]:
        """Calculate tokens per second if timing available."""
        if self.eval_count and self.eval_duration:
            return (self.eval_count / self.eval_duration) * 1e9
        return None


class OllamaManager:
    """Manages Ollama server connection and model operations.
    
    This class provides a high-level interface for interacting with Ollama,
    including connection management, model selection, health monitoring,
    and caching for performance optimization.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 cache_dir: Optional[Path] = None,
                 cache_ttl: int = 3600):
        """Initialize Ollama manager.
        
        Args:
            base_url: Ollama server URL
            timeout: Request timeout in seconds  
            max_retries: Maximum connection retries
            cache_dir: Directory for response caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        
        # Initialize cache
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "qvf" / "ollama"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Connection state
        self._health_status = OllamaHealth.UNKNOWN
        self._last_health_check = datetime.min
        self._health_check_interval = timedelta(minutes=5)
        self._available_models: List[ModelInfo] = []
        self._preferred_model: Optional[str] = None
        
        # Performance tracking
        self._request_count = 0
        self._cache_hits = 0
        self._total_inference_time = 0.0
        
        # Initialize connection
        self._check_health()
    
    def is_available(self) -> bool:
        """Check if Ollama is available and healthy."""
        if (datetime.now() - self._last_health_check) > self._health_check_interval:
            self._check_health()
        return self._health_status in [OllamaHealth.HEALTHY, OllamaHealth.DEGRADED]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get detailed health status information."""
        self._check_health()
        return {
            "status": self._health_status.value,
            "last_check": self._last_health_check.isoformat(),
            "available_models": len(self._available_models),
            "preferred_model": self._preferred_model,
            "performance_stats": {
                "requests": self._request_count,
                "cache_hits": self._cache_hits,
                "cache_hit_rate": self._cache_hits / max(self._request_count, 1),
                "avg_inference_time": self._total_inference_time / max(self._request_count, 1)
            }
        }
    
    def _check_health(self) -> None:
        """Check Ollama server health and update status."""
        try:
            # Check if Ollama process is running
            ollama_running = any(
                "ollama" in proc.name().lower() 
                for proc in psutil.process_iter(['name'])
            )
            
            if not ollama_running:
                self._health_status = OllamaHealth.UNAVAILABLE
                self._last_health_check = datetime.now()
                logger.warning("Ollama process not detected")
                return
            
            # Test API connection
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5.0
            )
            
            if response.status_code == 200:
                models_data = response.json()
                self._available_models = self._parse_models(models_data.get("models", []))
                self._health_status = OllamaHealth.HEALTHY
                
                # Set preferred model if not already set
                if not self._preferred_model and self._available_models:
                    self._preferred_model = self._select_best_model()
                    
                logger.info(f"Ollama healthy with {len(self._available_models)} models")
            else:
                self._health_status = OllamaHealth.DEGRADED
                logger.warning(f"Ollama API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            self._health_status = OllamaHealth.UNAVAILABLE
            logger.warning(f"Ollama health check failed: {e}")
        except Exception as e:
            self._health_status = OllamaHealth.UNKNOWN
            logger.error(f"Unexpected error in health check: {e}")
        finally:
            self._last_health_check = datetime.now()
    
    def _parse_models(self, models_data: List[Dict]) -> List[ModelInfo]:
        """Parse model information from API response."""
        models = []
        for model_data in models_data:
            try:
                model = ModelInfo(
                    name=model_data.get("name", "unknown"),
                    size=model_data.get("size", 0),
                    modified=datetime.fromisoformat(
                        model_data.get("modified_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
                    ),
                    family=model_data.get("details", {}).get("family", "unknown"),
                    parameter_size=model_data.get("details", {}).get("parameter_size", "unknown"),
                    quantization=model_data.get("details", {}).get("quantization_level", "unknown"),
                    tags=model_data.get("name", "").split(":")
                )
                models.append(model)
            except Exception as e:
                logger.warning(f"Failed to parse model data: {e}")
                continue
        return models
    
    def _select_best_model(self) -> Optional[str]:
        """Select the best available model for QVF tasks."""
        if not self._available_models:
            return None
        
        # Preference order for QVF tasks
        preferred_families = ["llama", "mistral", "gemma", "codellama"]
        preferred_sizes = ["7b", "13b", "3b"]  # Ordered by balance of capability and speed
        
        # Score models based on preferences
        scored_models = []
        for model in self._available_models:
            score = 0
            
            # Family preference (higher is better)
            for i, family in enumerate(preferred_families):
                if family in model.name.lower():
                    score += (len(preferred_families) - i) * 10
                    break
            
            # Size preference (balanced approach)
            for i, size in enumerate(preferred_sizes):
                if size in model.parameter_size.lower():
                    score += (len(preferred_sizes) - i) * 5
                    break
            
            # Recent models preferred
            days_old = (datetime.now() - model.modified).days
            if days_old < 30:
                score += 3
            elif days_old < 90:
                score += 1
            
            scored_models.append((score, model))
        
        # Select highest scoring model
        if scored_models:
            best_model = max(scored_models, key=lambda x: x[0])[1]
            logger.info(f"Selected model: {best_model.name}")
            return best_model.name
        
        return None
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models."""
        self._check_health()
        return self._available_models
    
    def set_preferred_model(self, model_name: str) -> bool:
        """Set the preferred model for inference."""
        available_names = [m.name for m in self._available_models]
        if model_name in available_names:
            self._preferred_model = model_name
            logger.info(f"Set preferred model to: {model_name}")
            return True
        else:
            logger.warning(f"Model {model_name} not available. Available: {available_names}")
            return False
    
    def _get_cache_key(self, request: InferenceRequest) -> str:
        """Generate cache key for request."""
        # Create deterministic hash of request parameters
        request_str = json.dumps(request.to_dict(), sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[InferenceResponse]:
        """Retrieve cached response if valid."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            if cache_file.exists():
                cache_stat = cache_file.stat()
                cache_age = time.time() - cache_stat.st_mtime
                
                if cache_age < self.cache_ttl:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                    return InferenceResponse(**data)
                else:
                    # Cache expired, remove file
                    cache_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to read cache: {e}")
            
        return None
    
    def _cache_response(self, cache_key: str, response: InferenceResponse) -> None:
        """Cache response for future use."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w') as f:
                json.dump(asdict(response), f)
        except Exception as e:
            logger.warning(f"Failed to cache response: {e}")
    
    def generate(self, 
                 prompt: str,
                 model: Optional[str] = None,
                 system: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None,
                 use_cache: bool = True) -> Optional[InferenceResponse]:
        """Generate response using Ollama.
        
        Args:
            prompt: Input prompt
            model: Model name (uses preferred if None)
            system: System message
            options: Model parameters
            use_cache: Whether to use response caching
            
        Returns:
            InferenceResponse if successful, None if unavailable
        """
        if not self.is_available():
            logger.warning("Ollama not available for inference")
            return None
        
        # Use preferred model if not specified
        if model is None:
            model = self._preferred_model
            
        if not model:
            logger.error("No model specified and no preferred model set")
            return None
        
        # Create request
        request = InferenceRequest(
            model=model,
            prompt=prompt,
            system=system,
            options=options or {}
        )
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self._cache_hits += 1
                self._request_count += 1
                logger.debug(f"Cache hit for prompt: {prompt[:50]}...")
                return cached_response
        
        # Make API request
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request.to_dict(),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                inference_response = InferenceResponse(
                    model=result_data.get("model", model),
                    response=result_data.get("response", ""),
                    context=result_data.get("context"),
                    total_duration=result_data.get("total_duration"),
                    load_duration=result_data.get("load_duration"),
                    prompt_eval_count=result_data.get("prompt_eval_count"),
                    prompt_eval_duration=result_data.get("prompt_eval_duration"),
                    eval_count=result_data.get("eval_count"),
                    eval_duration=result_data.get("eval_duration"),
                    done=result_data.get("done", True)
                )
                
                # Update performance metrics
                inference_time = time.time() - start_time
                self._request_count += 1
                self._total_inference_time += inference_time
                
                # Cache successful response
                if use_cache:
                    self._cache_response(cache_key, inference_response)
                
                logger.debug(f"Inference completed in {inference_time:.2f}s")
                return inference_response
                
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timeout after {self.timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in generate: {e}")
            return None
    
    async def generate_async(self,
                           prompt: str,
                           model: Optional[str] = None,
                           system: Optional[str] = None,
                           options: Optional[Dict[str, Any]] = None,
                           use_cache: bool = True) -> Optional[InferenceResponse]:
        """Async version of generate method."""
        if not self.is_available():
            return None
        
        if model is None:
            model = self._preferred_model
            
        if not model:
            return None
        
        request = InferenceRequest(
            model=model,
            prompt=prompt,
            system=system,
            options=options or {}
        )
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self._cache_hits += 1
                self._request_count += 1
                return cached_response
        
        # Make async API request
        start_time = time.time()
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=request.to_dict()
                ) as response:
                    if response.status == 200:
                        result_data = await response.json()
                        
                        inference_response = InferenceResponse(
                            model=result_data.get("model", model),
                            response=result_data.get("response", ""),
                            context=result_data.get("context"),
                            total_duration=result_data.get("total_duration"),
                            load_duration=result_data.get("load_duration"),
                            prompt_eval_count=result_data.get("prompt_eval_count"),
                            prompt_eval_duration=result_data.get("prompt_eval_duration"),
                            eval_count=result_data.get("eval_count"),
                            eval_duration=result_data.get("eval_duration"),
                            done=result_data.get("done", True)
                        )
                        
                        # Update performance metrics
                        inference_time = time.time() - start_time
                        self._request_count += 1
                        self._total_inference_time += inference_time
                        
                        # Cache successful response
                        if use_cache:
                            self._cache_response(cache_key, inference_response)
                        
                        return inference_response
                    else:
                        logger.error(f"Async Ollama API error: {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error(f"Async Ollama request timeout after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"Async request failed: {e}")
            return None
    
    def pull_model(self, model_name: str) -> bool:
        """Pull/download a model from Ollama registry."""
        if not self.is_available():
            logger.error("Cannot pull model: Ollama not available")
            return False
        
        try:
            logger.info(f"Pulling model: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300.0  # Model pulls can take a while
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_name}")
                # Refresh model list
                self._check_health()
                return True
            else:
                logger.error(f"Failed to pull model: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def clear_cache(self) -> int:
        """Clear response cache and return number of files removed."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            for cache_file in cache_files:
                cache_file.unlink()
            logger.info(f"Cleared {len(cache_files)} cache files")
            return len(cache_files)
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return {
            "requests_total": self._request_count,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": self._cache_hits / max(self._request_count, 1),
            "avg_inference_time": self._total_inference_time / max(self._request_count, 1),
            "total_inference_time": self._total_inference_time
        }