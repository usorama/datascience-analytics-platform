"""Performance tests for the DataScience Analytics Platform."""

import time
import psutil
import pytest
import pandas as pd
import polars as pl
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
import gc
import resource
from contextlib import contextmanager

from datascience_platform.etl.reader import DataReader, ReadOptions
from datascience_platform.etl.validator import DataValidator, validate_dataframe
from datascience_platform.core.orchestrator import PipelineOrchestrator, PipelineConfig
from datascience_platform.core.config import settings

# Optional ML imports
try:
    from datascience_platform.ml.statistics import StatisticsEngine
    from datascience_platform.ml.insights import InsightGenerator
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

# Optional Dashboard imports
try:
    from datascience_platform.dashboard.generator import DashboardGenerator
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


@contextmanager
def performance_monitor():
    """Context manager to monitor performance metrics."""
    process = psutil.Process()
    
    # Initial measurements
    start_time = time.perf_counter()
    start_memory = process.memory_info().rss / 1024 / 1024  # MB
    start_cpu_times = process.cpu_times()
    
    # Force garbage collection for consistent baseline
    gc.collect()
    
    yield
    
    # Final measurements
    end_time = time.perf_counter()
    end_memory = process.memory_info().rss / 1024 / 1024  # MB
    end_cpu_times = process.cpu_times()
    
    # Calculate metrics
    execution_time = end_time - start_time
    memory_delta = end_memory - start_memory
    cpu_user_time = end_cpu_times.user - start_cpu_times.user
    cpu_system_time = end_cpu_times.system - start_cpu_times.system
    
    return {
        'execution_time': execution_time,
        'memory_delta_mb': memory_delta,
        'peak_memory_mb': end_memory,
        'cpu_user_time': cpu_user_time,
        'cpu_system_time': cpu_system_time,
        'total_cpu_time': cpu_user_time + cpu_system_time
    }


def create_performance_dataset(size: int, temp_dir: Path) -> Path:
    """Create a dataset of specified size for performance testing."""
    np.random.seed(42)  # Reproducible results
    
    data = {
        'id': range(1, size + 1),
        'numeric_1': np.random.normal(100, 15, size),
        'numeric_2': np.random.exponential(2, size),
        'numeric_3': np.random.uniform(0, 1000, size),
        'categorical_1': np.random.choice(['A', 'B', 'C', 'D', 'E'], size),
        'categorical_2': np.random.choice(['X', 'Y', 'Z'], size, p=[0.5, 0.3, 0.2]),
        'text_field': [f'text_value_{i}_{np.random.randint(1000, 9999)}' for i in range(size)],
        'boolean_field': np.random.choice([True, False], size, p=[0.7, 0.3]),
        'timestamp': pd.date_range('2023-01-01', periods=size, freq='1min'),
        'float_precision': np.random.random(size) * 1e6
    }
    
    df = pd.DataFrame(data)
    csv_file = temp_dir / f"performance_dataset_{size}.csv"
    df.to_csv(csv_file, index=False)
    
    return csv_file


@pytest.mark.performance
@pytest.mark.slow
class TestETLPerformance:
    """Performance tests for ETL operations."""
    
    @pytest.mark.parametrize("dataset_size", [1000, 5000, 10000])
    @pytest.mark.parametrize("use_polars", [True, False])
    def test_data_reading_performance(self, dataset_size: int, use_polars: bool, temp_dir: Path):
        """Benchmark data reading performance with different sizes and engines."""
        # Create test dataset
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Configure reader
        options = ReadOptions(use_polars=use_polars)
        reader = DataReader(options)
        
        # Measure performance
        with performance_monitor() as metrics:
            df = reader.read(test_file)
        
        # Verify data was read correctly
        assert len(df) == dataset_size
        
        # Performance assertions
        assert metrics['execution_time'] < 30  # Should complete within 30 seconds
        assert metrics['memory_delta_mb'] < 500  # Should not use excessive memory
        
        # Log performance metrics for analysis
        engine = "Polars" if use_polars else "Pandas"
        print(f"\n{engine} - {dataset_size} rows:")
        print(f"  Execution time: {metrics['execution_time']:.3f}s")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")
        print(f"  Rows per second: {dataset_size / metrics['execution_time']:.0f}")
    
    @pytest.mark.parametrize("chunk_size", [1000, 5000, 10000])
    def test_chunked_reading_performance(self, chunk_size: int, temp_dir: Path):
        """Benchmark chunked reading performance."""
        dataset_size = 20000
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Configure reader for chunked processing
        options = ReadOptions(chunk_size=chunk_size, use_polars=True)
        reader = DataReader(options)
        
        # Measure performance
        with performance_monitor() as metrics:
            chunks = reader.read_chunked(test_file)
            
            # Process chunks to simulate real usage
            total_rows = 0
            for chunk in chunks:
                total_rows += len(chunk)
        
        # Verify all data was processed
        assert total_rows == dataset_size
        
        # Performance assertions
        expected_chunks = (dataset_size + chunk_size - 1) // chunk_size
        assert len(chunks) == expected_chunks
        
        # Log performance metrics
        print(f"\nChunked reading - {chunk_size} chunk size:")
        print(f"  Total chunks: {len(chunks)}")
        print(f"  Execution time: {metrics['execution_time']:.3f}s")
        print(f"  Memory efficiency: {metrics['memory_delta_mb']:.1f}MB")
    
    @pytest.mark.parametrize("dataset_size", [1000, 5000])
    def test_validation_performance(self, dataset_size: int, temp_dir: Path):
        """Benchmark data validation performance."""
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Read data
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(test_file)
        
        # Test different validation modes
        validators = [
            ("Strict", DataValidator(strict_mode=True)),
            ("Lenient", DataValidator(strict_mode=False))
        ]
        
        for mode_name, validator in validators:
            with performance_monitor() as metrics:
                result = validate_dataframe(df, strict_mode=validator.strict_mode)
            
            # Verify validation completed
            assert isinstance(result.is_valid, bool)
            assert result.rows_validated == dataset_size
            
            # Performance assertions
            assert metrics['execution_time'] < 10  # Should complete within 10 seconds
            
            # Log performance metrics
            print(f"\nValidation {mode_name} - {dataset_size} rows:")
            print(f"  Execution time: {metrics['execution_time']:.3f}s")
            print(f"  Validation rate: {dataset_size / metrics['execution_time']:.0f} rows/s")
            print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.skipif(not ML_AVAILABLE, reason="ML components not available")
class TestMLPerformance:
    """Performance tests for ML operations."""
    
    @pytest.mark.parametrize("dataset_size", [500, 1000, 2000])
    def test_statistics_generation_performance(self, dataset_size: int, temp_dir: Path):
        """Benchmark statistics generation performance."""
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Read data
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(test_file)
        
        # Generate statistics
        stats_engine = StatisticsEngine()
        
        with performance_monitor() as metrics:
            stats = stats_engine.generate_statistics(df)
        
        # Verify statistics were generated
        assert isinstance(stats, dict)
        assert 'summary_statistics' in stats
        assert 'column_statistics' in stats
        
        # Performance assertions
        assert metrics['execution_time'] < 30  # Should complete within 30 seconds
        
        # Log performance metrics
        print(f"\nStatistics generation - {dataset_size} rows:")
        print(f"  Execution time: {metrics['execution_time']:.3f}s")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")
        print(f"  Processing rate: {dataset_size / metrics['execution_time']:.0f} rows/s")
    
    @pytest.mark.parametrize("dataset_size", [200, 500])
    def test_insights_generation_performance(self, dataset_size: int, temp_dir: Path):
        """Benchmark ML insights generation performance."""
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Read data
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(test_file)
        
        # Generate insights
        insight_gen = InsightGenerator()
        
        with performance_monitor() as metrics:
            insights = insight_gen.generate_comprehensive_insights(
                df,
                target_column='numeric_1',
                business_context="Performance testing"
            )
        
        # Verify insights were generated
        assert isinstance(insights, dict)
        
        # Performance assertions
        assert metrics['execution_time'] < 60  # Should complete within 1 minute
        
        # Log performance metrics
        print(f"\nInsights generation - {dataset_size} rows:")
        print(f"  Execution time: {metrics['execution_time']:.3f}s")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")


@pytest.mark.performance
@pytest.mark.slow  
@pytest.mark.skipif(not DASHBOARD_AVAILABLE, reason="Dashboard components not available")
class TestDashboardPerformance:
    """Performance tests for dashboard generation."""
    
    @pytest.mark.parametrize("theme", ['light', 'dark'])
    def test_dashboard_initialization_performance(self, theme: str):
        """Benchmark dashboard generator initialization."""
        with performance_monitor() as metrics:
            dashboard_gen = DashboardGenerator(theme=theme)
            
            # Perform basic configuration
            dashboard_gen.config['title'] = "Performance Test Dashboard"
            dashboard_gen.config['description'] = "Testing dashboard performance"
        
        # Verify initialization
        assert dashboard_gen.theme == theme
        assert dashboard_gen.config['title'] == "Performance Test Dashboard"
        
        # Performance assertions
        assert metrics['execution_time'] < 5  # Should initialize quickly
        
        print(f"\nDashboard initialization - {theme} theme:")
        print(f"  Execution time: {metrics['execution_time']:.3f}s")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")


@pytest.mark.performance
@pytest.mark.slow
class TestPipelinePerformance:
    """Performance tests for complete pipeline execution."""
    
    @pytest.mark.parametrize("dataset_size", [500, 1000])
    def test_full_pipeline_performance(self, dataset_size: int, temp_dir: Path):
        """Benchmark complete pipeline execution."""
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # Configure pipeline (disable ML/Dashboard to focus on ETL)
        config = PipelineConfig(
            use_polars=True,
            strict_validation=False,
            generate_insights=False,
            generate_dashboard=False
        )
        
        orchestrator = PipelineOrchestrator(config)
        
        with performance_monitor() as metrics:
            result = orchestrator.execute_pipeline(test_file)
        
        # Verify pipeline success
        assert result.success
        assert result.data is not None
        assert len(result.data) == dataset_size
        
        # Performance assertions
        assert metrics['execution_time'] < 30  # Should complete within 30 seconds
        assert result.execution_time is not None
        assert result.execution_time > 0
        
        # Log performance metrics
        print(f"\nFull pipeline - {dataset_size} rows:")
        print(f"  Total execution time: {metrics['execution_time']:.3f}s")
        print(f"  Pipeline reported time: {result.execution_time:.3f}s")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB")
        print(f"  Throughput: {dataset_size / metrics['execution_time']:.0f} rows/s")
    
    def test_pipeline_stage_performance(self, temp_dir: Path):
        """Benchmark individual pipeline stages."""
        dataset_size = 1000
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        orchestrator = PipelineOrchestrator()
        stage_metrics = {}
        
        # Test extract stage
        with performance_monitor() as metrics:
            extract_result = orchestrator.execute_stage('extract', input_path=test_file)
        
        assert extract_result['success']
        stage_metrics['extract'] = metrics
        data = extract_result['result']
        
        # Test validate stage
        with performance_monitor() as metrics:
            validate_result = orchestrator.execute_stage('validate', data=data)
        
        assert validate_result['success']
        stage_metrics['validate'] = metrics
        
        # Log stage performance
        print(f"\nPipeline stage performance - {dataset_size} rows:")
        for stage, metrics in stage_metrics.items():
            print(f"  {stage.capitalize()}:")
            print(f"    Time: {metrics['execution_time']:.3f}s")
            print(f"    Memory: {metrics['memory_delta_mb']:.1f}MB")


@pytest.mark.performance
class TestMemoryUsage:
    """Tests focused on memory usage patterns."""
    
    def test_memory_efficiency_comparison(self, temp_dir: Path):
        """Compare memory efficiency between Pandas and Polars."""
        dataset_size = 5000
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        memory_results = {}
        
        # Test Pandas
        pandas_reader = DataReader(ReadOptions(use_polars=False))
        with performance_monitor() as metrics:
            df_pandas = pandas_reader.read(test_file)
        
        memory_results['pandas'] = {
            'peak_memory': metrics['peak_memory_mb'],
            'memory_delta': metrics['memory_delta_mb'],
            'execution_time': metrics['execution_time']
        }
        
        # Clear memory
        del df_pandas
        gc.collect()
        
        # Test Polars
        polars_reader = DataReader(ReadOptions(use_polars=True))
        with performance_monitor() as metrics:
            df_polars = polars_reader.read(test_file)
        
        memory_results['polars'] = {
            'peak_memory': metrics['peak_memory_mb'],
            'memory_delta': metrics['memory_delta_mb'],
            'execution_time': metrics['execution_time']
        }
        
        # Log comparison
        print(f"\nMemory efficiency comparison - {dataset_size} rows:")
        for engine, results in memory_results.items():
            print(f"  {engine.capitalize()}:")
            print(f"    Peak memory: {results['peak_memory']:.1f}MB")
            print(f"    Memory delta: {results['memory_delta']:.1f}MB")
            print(f"    Execution time: {results['execution_time']:.3f}s")
        
        # Basic efficiency check
        assert memory_results['pandas']['peak_memory'] > 0
        assert memory_results['polars']['peak_memory'] > 0
    
    def test_memory_growth_with_size(self, temp_dir: Path):
        """Test how memory usage scales with dataset size."""
        sizes = [100, 500, 1000]
        memory_scaling = []
        
        for size in sizes:
            test_file = create_performance_dataset(size, temp_dir)
            reader = DataReader(ReadOptions(use_polars=True))
            
            with performance_monitor() as metrics:
                df = reader.read(test_file)
                # Force some processing to see memory patterns
                result = validate_dataframe(df.to_pandas() if hasattr(df, 'to_pandas') else df)
            
            memory_scaling.append({
                'size': size,
                'memory_delta': metrics['memory_delta_mb'],
                'peak_memory': metrics['peak_memory_mb'],
                'time': metrics['execution_time']
            })
            
            # Cleanup
            del df
            gc.collect()
        
        # Log scaling results
        print(f"\nMemory scaling analysis:")
        for result in memory_scaling:
            print(f"  {result['size']} rows:")
            print(f"    Memory delta: {result['memory_delta']:.1f}MB")
            print(f"    Peak memory: {result['peak_memory']:.1f}MB")
            print(f"    Time: {result['time']:.3f}s")
            if result['size'] > 0:
                print(f"    MB per 1k rows: {result['memory_delta'] / (result['size'] / 1000):.2f}")
        
        # Memory usage should scale somewhat linearly
        if len(memory_scaling) >= 2:
            first_result = memory_scaling[0]
            last_result = memory_scaling[-1]
            
            size_ratio = last_result['size'] / first_result['size']
            memory_ratio = last_result['memory_delta'] / max(first_result['memory_delta'], 0.1)
            
            # Memory growth should not be exponential
            assert memory_ratio < size_ratio * 3, "Memory usage growing too quickly"


@pytest.mark.performance
class TestPerformanceRegression:
    """Tests to detect performance regressions."""
    
    def test_baseline_etl_performance(self, temp_dir: Path):
        """Establish baseline ETL performance metrics."""
        dataset_size = 1000
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        # ETL Pipeline
        reader = DataReader(ReadOptions(use_polars=True, chunk_size=None))
        
        with performance_monitor() as metrics:
            df = reader.read(test_file)
            result = validate_dataframe(df.to_pandas() if hasattr(df, 'to_pandas') else df)
        
        # Performance thresholds (baseline expectations)
        max_time = 10  # seconds
        max_memory = 100  # MB
        min_throughput = 50  # rows per second
        
        throughput = dataset_size / metrics['execution_time']
        
        # Assertions to catch regressions
        assert metrics['execution_time'] < max_time, f"ETL too slow: {metrics['execution_time']:.2f}s > {max_time}s"
        assert metrics['memory_delta_mb'] < max_memory, f"Memory usage too high: {metrics['memory_delta_mb']:.1f}MB > {max_memory}MB"
        assert throughput > min_throughput, f"Throughput too low: {throughput:.0f} < {min_throughput} rows/s"
        
        # Log baseline metrics
        print(f"\nBaseline ETL Performance ({dataset_size} rows):")
        print(f"  Execution time: {metrics['execution_time']:.3f}s (max: {max_time}s)")
        print(f"  Memory usage: {metrics['memory_delta_mb']:.1f}MB (max: {max_memory}MB)")
        print(f"  Throughput: {throughput:.0f} rows/s (min: {min_throughput} rows/s)")
        print(f"  ✅ All performance thresholds met")


@pytest.mark.performance
class TestConcurrencyPerformance:
    """Tests for concurrent processing performance."""
    
    def test_concurrent_processing_overhead(self, temp_dir: Path):
        """Test performance impact of concurrent processing."""
        import threading
        import queue
        
        dataset_size = 500
        test_file = create_performance_dataset(dataset_size, temp_dir)
        
        results_queue = queue.Queue()
        
        def process_data():
            reader = DataReader(ReadOptions(use_polars=True))
            
            start_time = time.perf_counter()
            df = reader.read(test_file)
            result = validate_dataframe(df.to_pandas() if hasattr(df, 'to_pandas') else df)
            end_time = time.perf_counter()
            
            results_queue.put({
                'execution_time': end_time - start_time,
                'success': result.is_valid,
                'rows': len(df)
            })
        
        # Test sequential processing
        with performance_monitor() as sequential_metrics:
            for _ in range(3):
                process_data()
        
        # Test concurrent processing
        with performance_monitor() as concurrent_metrics:
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=process_data)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
        
        # Verify all operations completed successfully
        assert results_queue.qsize() == 6  # 3 sequential + 3 concurrent
        
        # Concurrent processing should not be much slower than sequential
        time_ratio = concurrent_metrics['execution_time'] / sequential_metrics['execution_time']
        
        print(f"\nConcurrency Performance:")
        print(f"  Sequential time: {sequential_metrics['execution_time']:.3f}s")
        print(f"  Concurrent time: {concurrent_metrics['execution_time']:.3f}s")
        print(f"  Time ratio: {time_ratio:.2f}x")
        
        # Should not be more than 2x slower (accounting for overhead)
        assert time_ratio < 2.0, f"Concurrent processing too slow: {time_ratio:.2f}x"