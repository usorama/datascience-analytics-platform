"""Model Management Utilities

This module provides utilities for managing NLP models, caching, and performance monitoring.
"""

import json
import logging
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import time
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try importing optional libraries
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.debug("psutil not available. Limited system monitoring.")

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.debug("GPUtil not available. No GPU monitoring.")


class ModelMetrics:
    """Track model performance metrics."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics."""
        self.inference_times = []
        self.memory_usage = []
        self.error_count = 0
        self.success_count = 0
        self.total_requests = 0
        self.start_time = datetime.now()
    
    def add_inference_time(self, duration: float):
        """Add an inference time measurement."""
        self.inference_times.append(duration)
    
    def add_memory_usage(self, memory_mb: float):
        """Add a memory usage measurement."""
        self.memory_usage.append(memory_mb)
    
    def record_success(self):
        """Record a successful inference."""
        self.success_count += 1
        self.total_requests += 1
    
    def record_error(self):
        """Record a failed inference."""
        self.error_count += 1
        self.total_requests += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        if not self.inference_times:
            return {
                'total_requests': self.total_requests,
                'success_rate': 0.0,
                'error_rate': 0.0,
                'avg_inference_time': 0.0,
                'throughput_per_second': 0.0,
                'uptime_hours': 0.0
            }
        
        # Calculate statistics
        avg_inference = sum(self.inference_times) / len(self.inference_times)
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        throughput = self.success_count / max(uptime * 3600, 1)  # per second
        
        return {
            'total_requests': self.total_requests,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': self.success_count / max(self.total_requests, 1),
            'error_rate': self.error_count / max(self.total_requests, 1),
            'avg_inference_time': avg_inference,
            'min_inference_time': min(self.inference_times),
            'max_inference_time': max(self.inference_times),
            'throughput_per_second': throughput,
            'uptime_hours': uptime,
            'avg_memory_usage': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        }


class ModelCache:
    """Advanced caching system for models and embeddings."""
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_cache_size_gb: float = 2.0,
        ttl_hours: int = 24
    ):
        """Initialize model cache.
        
        Args:
            cache_dir: Directory for cache storage
            max_cache_size_gb: Maximum cache size in GB
            ttl_hours: Time-to-live for cache entries in hours
        """
        self.cache_dir = cache_dir or Path.home() / ".cache" / "ds_platform_models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_cache_size = max_cache_size_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.ttl = timedelta(hours=ttl_hours)
        
        # In-memory cache for small objects
        self.memory_cache = {}
        self.cache_metadata = {}
        
        # Load existing metadata
        self._load_metadata()
        
        # Statistics
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_size_bytes': 0,
            'cleanup_operations': 0
        }
    
    def _generate_cache_key(self, key_data: Union[str, Dict[str, Any]]) -> str:
        """Generate a unique cache key."""
        if isinstance(key_data, str):
            content = key_data
        else:
            content = json.dumps(key_data, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        cache_key = self._generate_cache_key(key)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            metadata = self.cache_metadata.get(cache_key)
            if metadata and datetime.now() - metadata['created'] < self.ttl:
                self.stats['cache_hits'] += 1
                return self.memory_cache[cache_key]
            else:
                # Expired, remove from memory
                del self.memory_cache[cache_key]
                if cache_key in self.cache_metadata:
                    del self.cache_metadata[cache_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            # Check if expired
            metadata = self.cache_metadata.get(cache_key)
            if metadata and datetime.now() - metadata['created'] < self.ttl:
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    # Add to memory cache if small enough
                    if metadata['size_bytes'] < 100 * 1024 * 1024:  # 100MB threshold
                        self.memory_cache[cache_key] = data
                    
                    self.stats['cache_hits'] += 1
                    return data
                    
                except Exception as e:
                    logger.warning(f"Error loading cache file {cache_file}: {e}")
                    cache_file.unlink(missing_ok=True)
        
        self.stats['cache_misses'] += 1
        return None
    
    def set(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None):
        """Set item in cache."""
        cache_key = self._generate_cache_key(key)
        
        try:
            # Serialize to get size
            serialized_data = pickle.dumps(value)
            size_bytes = len(serialized_data)
            
            # Check cache size limits
            self._cleanup_if_needed(size_bytes)
            
            # Store metadata
            cache_metadata = {
                'created': datetime.now(),
                'size_bytes': size_bytes,
                'key': key,
                **(metadata or {})
            }
            
            self.cache_metadata[cache_key] = cache_metadata
            
            # Store in memory if small enough
            if size_bytes < 100 * 1024 * 1024:  # 100MB threshold
                self.memory_cache[cache_key] = value
            
            # Store on disk
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                f.write(serialized_data)
            
            self.stats['cache_size_bytes'] += size_bytes
            self._save_metadata()
            
        except Exception as e:
            logger.error(f"Error caching item {key}: {e}")
    
    def _cleanup_if_needed(self, new_item_size: int):
        """Clean up cache if size limit would be exceeded."""
        current_size = self._calculate_cache_size()
        
        if current_size + new_item_size > self.max_cache_size:
            logger.info("Cache size limit reached, cleaning up...")
            
            # Sort by access time (oldest first)
            cache_items = list(self.cache_metadata.items())
            cache_items.sort(key=lambda x: x[1]['created'])
            
            bytes_to_free = current_size + new_item_size - self.max_cache_size
            bytes_freed = 0
            
            for cache_key, metadata in cache_items:
                if bytes_freed >= bytes_to_free:
                    break
                
                # Remove from disk
                cache_file = self.cache_dir / f"{cache_key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                    bytes_freed += metadata['size_bytes']
                
                # Remove from memory
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                
                del self.cache_metadata[cache_key]
            
            self.stats['cache_size_bytes'] -= bytes_freed
            self.stats['cleanup_operations'] += 1
            self._save_metadata()
            
            logger.info(f"Freed {bytes_freed / (1024*1024):.1f} MB from cache")
    
    def _calculate_cache_size(self) -> int:
        """Calculate current cache size."""
        return sum(metadata['size_bytes'] for metadata in self.cache_metadata.values())
    
    def _load_metadata(self):
        """Load cache metadata from disk."""
        metadata_file = self.cache_dir / "cache_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                
                # Convert datetime strings back to objects
                for cache_key, metadata in data.items():
                    metadata['created'] = datetime.fromisoformat(metadata['created'])
                    self.cache_metadata[cache_key] = metadata
                
                # Update stats
                self.stats['cache_size_bytes'] = self._calculate_cache_size()
                
            except Exception as e:
                logger.warning(f"Error loading cache metadata: {e}")
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        metadata_file = self.cache_dir / "cache_metadata.json"
        try:
            # Convert datetime objects to strings
            serializable_metadata = {}
            for cache_key, metadata in self.cache_metadata.items():
                serializable_metadata[cache_key] = {
                    **metadata,
                    'created': metadata['created'].isoformat()
                }
            
            with open(metadata_file, 'w') as f:
                json.dump(serializable_metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving cache metadata: {e}")
    
    def clear(self, older_than_hours: Optional[int] = None):
        """Clear cache items."""
        if older_than_hours is None:
            # Clear everything
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            
            self.memory_cache.clear()
            self.cache_metadata.clear()
            self.stats['cache_size_bytes'] = 0
        else:
            # Clear items older than specified hours
            cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
            
            items_to_remove = []
            for cache_key, metadata in self.cache_metadata.items():
                if metadata['created'] < cutoff_time:
                    items_to_remove.append(cache_key)
            
            for cache_key in items_to_remove:
                cache_file = self.cache_dir / f"{cache_key}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
                
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                
                self.stats['cache_size_bytes'] -= self.cache_metadata[cache_key]['size_bytes']
                del self.cache_metadata[cache_key]
        
        self._save_metadata()
        logger.info(f"Cache cleared (older than {older_than_hours} hours)" if older_than_hours else "Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = self.stats['cache_hits'] / max(total_requests, 1)
        
        return {
            **self.stats,
            'hit_rate': hit_rate,
            'cache_items': len(self.cache_metadata),
            'memory_items': len(self.memory_cache),
            'cache_size_mb': self.stats['cache_size_bytes'] / (1024 * 1024)
        }


class SystemMonitor:
    """Monitor system resources during model operations."""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
    
    def start_monitoring(self, interval_seconds: float = 1.0):
        """Start system monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,)
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Started system monitoring")
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Stopped system monitoring")
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                timestamp = datetime.now()
                
                # CPU usage
                if PSUTIL_AVAILABLE:
                    cpu_percent = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    
                    with self.lock:
                        self.metrics['cpu_percent'].append((timestamp, cpu_percent))
                        self.metrics['memory_percent'].append((timestamp, memory.percent))
                        self.metrics['memory_used_gb'].append((timestamp, memory.used / (1024**3)))
                
                # GPU usage
                if GPUTIL_AVAILABLE:
                    try:
                        gpus = GPUtil.getGPUs()
                        for i, gpu in enumerate(gpus):
                            with self.lock:
                                self.metrics[f'gpu_{i}_utilization'].append((timestamp, gpu.load * 100))
                                self.metrics[f'gpu_{i}_memory_percent'].append((timestamp, gpu.memoryUtil * 100))
                    except:
                        pass  # GPU monitoring might fail, ignore
                
                time.sleep(interval)
                
            except Exception as e:
                logger.warning(f"Error in monitoring loop: {e}")
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        stats = {}
        
        if PSUTIL_AVAILABLE:
            stats['cpu_percent'] = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            stats['memory_percent'] = memory.percent
            stats['memory_used_gb'] = memory.used / (1024**3)
            stats['memory_available_gb'] = memory.available / (1024**3)
        
        if GPUTIL_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    stats[f'gpu_{i}_utilization'] = gpu.load * 100
                    stats[f'gpu_{i}_memory_percent'] = gpu.memoryUtil * 100
                    stats[f'gpu_{i}_temperature'] = gpu.temperature
            except:
                pass
        
        return stats
    
    def get_historical_stats(self, minutes: int = 10) -> Dict[str, List[Tuple[datetime, float]]]:
        """Get historical statistics for the last N minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        filtered_metrics = {}
        with self.lock:
            for metric_name, values in self.metrics.items():
                filtered_values = [(ts, val) for ts, val in values if ts >= cutoff_time]
                filtered_metrics[metric_name] = filtered_values
        
        return filtered_metrics
    
    def clear_history(self):
        """Clear historical metrics."""
        with self.lock:
            self.metrics.clear()


class ModelManager:
    """Comprehensive model management system."""
    
    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        max_cache_size_gb: float = 2.0,
        enable_monitoring: bool = True
    ):
        """Initialize model manager.
        
        Args:
            cache_dir: Directory for model caching
            max_cache_size_gb: Maximum cache size
            enable_monitoring: Whether to enable system monitoring
        """
        self.cache = ModelCache(cache_dir, max_cache_size_gb)
        self.monitor = SystemMonitor() if enable_monitoring else None
        
        # Model metrics tracking
        self.model_metrics: Dict[str, ModelMetrics] = defaultdict(ModelMetrics)
        
        # Active models
        self.active_models = {}
        
        if self.monitor:
            self.monitor.start_monitoring()
        
        logger.info("Model manager initialized")
    
    def register_model(self, model_id: str, model: Any, metadata: Optional[Dict[str, Any]] = None):
        """Register a model for management.
        
        Args:
            model_id: Unique model identifier
            model: Model instance
            metadata: Optional model metadata
        """
        self.active_models[model_id] = {
            'model': model,
            'metadata': metadata or {},
            'created': datetime.now()
        }
        
        logger.info(f"Registered model: {model_id}")
    
    def get_model(self, model_id: str) -> Optional[Any]:
        """Get a registered model."""
        if model_id in self.active_models:
            return self.active_models[model_id]['model']
        return None
    
    def time_inference(self, model_id: str):
        """Context manager for timing model inference."""
        return InferenceTimer(self.model_metrics[model_id])
    
    def cache_model_output(self, model_id: str, input_key: str, output: Any):
        """Cache model output."""
        cache_key = f"{model_id}:{input_key}"
        self.cache.set(cache_key, output, {'model_id': model_id})
    
    def get_cached_output(self, model_id: str, input_key: str) -> Optional[Any]:
        """Get cached model output."""
        cache_key = f"{model_id}:{input_key}"
        return self.cache.get(cache_key)
    
    def get_model_stats(self, model_id: str) -> Dict[str, Any]:
        """Get statistics for a specific model."""
        if model_id not in self.model_metrics:
            return {}
        
        metrics = self.model_metrics[model_id].get_summary()
        
        # Add system stats if available
        if self.monitor:
            metrics['current_system_stats'] = self.monitor.get_current_stats()
        
        return metrics
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics."""
        stats = {
            'cache_stats': self.cache.get_stats(),
            'model_count': len(self.active_models),
            'model_stats': {
                model_id: self.get_model_stats(model_id)
                for model_id in self.active_models.keys()
            }
        }
        
        if self.monitor:
            stats['system_stats'] = self.monitor.get_current_stats()
            stats['system_history'] = self.monitor.get_historical_stats()
        
        return stats
    
    def cleanup(self):
        """Clean up resources."""
        if self.monitor:
            self.monitor.stop_monitoring()
        
        logger.info("Model manager cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass


class InferenceTimer:
    """Context manager for timing model inference."""
    
    def __init__(self, metrics: ModelMetrics):
        self.metrics = metrics
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            self.metrics.add_inference_time(duration)
            
            if exc_type is None:
                self.metrics.record_success()
            else:
                self.metrics.record_error()
        
        # Record memory usage if available
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            self.metrics.add_memory_usage(memory.used / (1024**2))  # MB