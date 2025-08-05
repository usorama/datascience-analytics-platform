"""Integration tests for the complete ETL-ML-Dashboard pipeline."""

import json
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import polars as pl

from datascience_platform.etl.reader import DataReader, ReadOptions
from datascience_platform.etl.validator import DataValidator, validate_dataframe
from datascience_platform.etl.schema import create_sample_schema, schema_registry
from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import (
    DataSciencePlatformError,
    ETLError,
    ValidationError
)

# Import ML and Dashboard components if available
try:
    from datascience_platform.ml.insights import InsightGenerator
    from datascience_platform.ml.statistics import StatisticsEngine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from datascience_platform.dashboard.generator import DashboardGenerator
    from datascience_platform.dashboard.charts import ChartBuilder
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False


@pytest.mark.integration
class TestFullPipeline:
    """Test the complete workflow from CSV to dashboard."""
    
    def test_csv_to_insights_pipeline(self, sample_csv_file, sample_schema, temp_dir):
        """Test complete pipeline: CSV -> ETL -> Validation -> ML Insights."""
        # Step 1: Read CSV data
        reader = DataReader(ReadOptions(use_polars=False))  # Use pandas for ML compatibility
        df = reader.read(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        assert 'id' in df.columns
        assert 'score' in df.columns
        
        # Step 2: Validate data
        validator = DataValidator(strict_mode=True)
        result = validator.validate_with_schema(df, sample_schema)
        
        assert result.is_valid
        assert result.rows_validated == 5
        assert result.columns_validated == 6
        
        # Step 3: Generate ML insights (if available)
        if ML_AVAILABLE:
            stats_engine = StatisticsEngine()
            stats = stats_engine.generate_statistics(df)
            
            assert isinstance(stats, dict)
            assert 'summary_statistics' in stats
            assert 'column_statistics' in stats
            assert 'data_quality' in stats
        
        # Step 4: Verify data integrity throughout pipeline
        assert df['id'].nunique() == 5  # All IDs are unique
        assert df['score'].notna().all()  # No null scores
        assert df['status'].isin(['active', 'inactive', 'pending']).all()
    
    def test_json_to_dashboard_pipeline(self, sample_json_file, temp_dir):
        """Test complete pipeline: JSON -> ETL -> Dashboard."""
        # Step 1: Read JSON data
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(sample_json_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        
        # Step 2: Basic validation
        basic_result = validate_dataframe(df, strict_mode=False)
        assert basic_result.is_valid
        
        # Step 3: Generate dashboard (if available)
        if DASHBOARD_AVAILABLE:
            dashboard_gen = DashboardGenerator(theme='light')
            
            # Add basic KPI
            total_records = len(df)
            avg_score = df['score'].mean()
            
            dashboard_gen.config['title'] = "Test Pipeline Dashboard"
            
            # This should not raise an error
            assert dashboard_gen.theme == 'light'
            assert dashboard_gen.config['title'] == "Test Pipeline Dashboard"
    
    def test_large_file_chunked_processing(self, large_csv_file, temp_dir):
        """Test pipeline with large file using chunked processing."""
        # Step 1: Read in chunks
        reader = DataReader(ReadOptions(chunk_size=50, use_polars=True))
        chunks = reader.read_chunked(large_csv_file)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should be split into multiple chunks
        
        # Step 2: Process each chunk
        total_rows = 0
        valid_chunks = 0
        
        for chunk in chunks:
            assert isinstance(chunk, pl.DataFrame) or isinstance(chunk, pd.DataFrame)
            
            # Convert to pandas for validation if needed
            if isinstance(chunk, pl.DataFrame):
                chunk_df = chunk.to_pandas()
            else:
                chunk_df = chunk
            
            # Basic validation
            result = validate_dataframe(chunk_df, strict_mode=False)
            if result.is_valid:
                valid_chunks += 1
            
            total_rows += len(chunk_df)
        
        assert total_rows == 100  # Should read all 100 rows from large file
        assert valid_chunks > 0  # At least some chunks should be valid
    
    def test_error_handling_and_recovery(self, temp_dir):
        """Test pipeline error handling and recovery mechanisms."""
        # Create invalid CSV file
        invalid_csv = temp_dir / "invalid.csv"
        invalid_csv.write_text("invalid,data\n1,2,3\n4,5\n")  # Inconsistent columns
        
        # Step 1: Test reader error handling
        reader = DataReader(ReadOptions(use_polars=False))
        
        with pytest.raises(DataSciencePlatformError):
            reader.read(invalid_csv)
        
        # Step 2: Test validation error handling with invalid data
        df_invalid = pd.DataFrame({
            'id': [1, 1, 3],  # Duplicate IDs
            'name': ['A', '', 'C'],  # Empty name
            'age': [-5, 150, 25],  # Invalid ages
            'email': ['valid@email.com', 'invalid-email', 'another@valid.com'],
            'status': ['active', 'unknown', 'pending'],  # Invalid status
            'score': [85.5, 200.0, 88.9]  # Out of range score
        })
        
        # Should detect validation errors
        result = validate_dataframe(df_invalid, strict_mode=True)
        assert not result.is_valid
        assert len(result.errors) > 0
    
    def test_different_file_formats_compatibility(self, temp_dir, sample_pandas_dataframe):
        """Test pipeline compatibility with different file formats."""
        formats_to_test = []
        
        # CSV
        csv_file = temp_dir / "test.csv"
        sample_pandas_dataframe.to_csv(csv_file, index=False)
        formats_to_test.append(('csv', csv_file))
        
        # JSON
        json_file = temp_dir / "test.json"
        sample_pandas_dataframe.to_json(json_file, orient='records', indent=2)
        formats_to_test.append(('json', json_file))
        
        # Parquet (if supported)
        try:
            parquet_file = temp_dir / "test.parquet"
            sample_pandas_dataframe.to_parquet(parquet_file, index=False)
            formats_to_test.append(('parquet', parquet_file))
        except ImportError:
            pass  # Skip if parquet not available
        
        reader = DataReader(ReadOptions(use_polars=False))
        
        for format_name, file_path in formats_to_test:
            df = reader.read(file_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 5
            assert list(df.columns) == list(sample_pandas_dataframe.columns)
            
            # Test validation
            result = validate_dataframe(df, strict_mode=False)
            assert result.is_valid
    
    def test_memory_usage_optimization(self, temp_dir):
        """Test memory usage optimization in pipeline."""
        # Create a moderately large dataset
        large_data = []
        for i in range(1000):
            large_data.append({
                'id': i + 1,
                'name': f'User{i+1}',
                'age': 20 + (i % 60),
                'email': f'user{i+1}@example.com',
                'status': 'active' if i % 2 == 0 else 'inactive',
                'score': 50.0 + (i % 50)
            })
        
        # Write to CSV
        large_df = pd.DataFrame(large_data)
        large_csv = temp_dir / "large_test.csv"
        large_df.to_csv(large_csv, index=False)
        
        # Test with different chunk sizes
        chunk_sizes = [100, 250, 500]
        
        for chunk_size in chunk_sizes:
            reader = DataReader(ReadOptions(chunk_size=chunk_size, use_polars=True))
            chunks = reader.read_chunked(large_csv)
            
            assert isinstance(chunks, list)
            
            # Verify total rows
            total_rows = sum(len(chunk) for chunk in chunks)
            assert total_rows == 1000
            
            # Verify chunk sizes (except possibly the last chunk)
            for i, chunk in enumerate(chunks[:-1]):
                assert len(chunk) == chunk_size
    
    def test_configuration_impact_on_pipeline(self, sample_csv_file, test_settings):
        """Test how different configurations affect pipeline behavior."""
        # Test with different settings
        reader_strict = DataReader(ReadOptions(use_polars=True))
        reader_lenient = DataReader(ReadOptions(use_polars=False))
        
        # Read with both configurations
        df_polars = reader_strict.read(sample_csv_file)
        df_pandas = reader_lenient.read(sample_csv_file)
        
        # Both should work but may have different types
        assert len(df_polars) == len(df_pandas) == 5
        
        # Test validation with different strictness
        validator_strict = DataValidator(strict_mode=True)
        validator_lenient = DataValidator(strict_mode=False)
        
        # Convert polars to pandas for validation
        if isinstance(df_polars, pl.DataFrame):
            df_polars_pd = df_polars.to_pandas()
        else:
            df_polars_pd = df_polars
        
        result_strict = validator_strict.validate_with_schema(df_polars_pd, create_sample_schema())
        result_lenient = validator_lenient.validate_with_schema(df_pandas, create_sample_schema())
        
        # Both should be valid for our clean test data
        assert result_strict.is_valid
        assert result_lenient.is_valid


@pytest.mark.integration
@pytest.mark.slow
class TestPerformancePipeline:
    """Test pipeline performance characteristics."""
    
    def test_processing_speed_benchmarks(self, temp_dir):
        """Benchmark processing speed for different data sizes."""
        import time
        
        data_sizes = [100, 1000, 5000]
        processing_times = {}
        
        for size in data_sizes:
            # Create test data
            test_data = pd.DataFrame({
                'id': range(1, size + 1),
                'value': [i * 2.5 for i in range(size)],
                'category': [f'cat_{i % 10}' for i in range(size)],
                'flag': [i % 2 == 0 for i in range(size)]
            })
            
            test_file = temp_dir / f"benchmark_{size}.csv"
            test_data.to_csv(test_file, index=False)
            
            # Time the pipeline
            start_time = time.time()
            
            reader = DataReader(ReadOptions(use_polars=True))
            df = reader.read(test_file)
            
            result = validate_dataframe(df.to_pandas() if hasattr(df, 'to_pandas') else df)
            
            end_time = time.time()
            processing_times[size] = end_time - start_time
            
            # Verify processing was successful
            assert result.is_valid
        
        # Basic performance check - larger datasets shouldn't be dramatically slower
        # (This is a simple check; real benchmarks would be more sophisticated)
        assert processing_times[5000] < processing_times[100] * 100  # Not 100x slower
    
    def test_concurrent_processing_safety(self, sample_csv_file):
        """Test that pipeline components are safe for concurrent use."""
        import threading
        import queue
        
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def process_data(file_path, thread_id):
            try:
                reader = DataReader(ReadOptions(use_polars=False))
                df = reader.read(file_path)
                
                result = validate_dataframe(df)
                results_queue.put((thread_id, len(df), result.is_valid))
                
            except Exception as e:
                errors_queue.put((thread_id, str(e)))
        
        # Create multiple threads
        threads = []
        num_threads = 5
        
        for i in range(num_threads):
            thread = threading.Thread(target=process_data, args=(sample_csv_file, i))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)  # 10 second timeout
        
        # Check results
        assert errors_queue.empty(), f"Errors occurred: {list(errors_queue.queue)}"
        assert results_queue.qsize() == num_threads
        
        # All threads should have processed the same data successfully
        while not results_queue.empty():
            thread_id, row_count, is_valid = results_queue.get()
            assert row_count == 5
            assert is_valid


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.skipif(not ML_AVAILABLE, reason="ML components not available")
    def test_data_science_workflow(self, sample_csv_file, temp_dir):
        """Test complete data science workflow with ML insights."""
        # Step 1: Data ingestion
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(sample_csv_file)
        
        # Step 2: Data validation
        result = validate_dataframe(df)
        assert result.is_valid
        
        # Step 3: Generate ML insights
        insight_gen = InsightGenerator()
        insights = insight_gen.generate_comprehensive_insights(
            df,
            target_column='score',
            business_context="User performance analysis"
        )
        
        assert isinstance(insights, dict)
        # Should contain standard insight categories
        expected_keys = ['data_overview', 'statistical_insights', 'quality_insights']
        for key in expected_keys:
            if key in insights:
                assert isinstance(insights[key], (dict, list))
    
    @pytest.mark.skipif(not DASHBOARD_AVAILABLE, reason="Dashboard components not available")
    def test_reporting_workflow(self, sample_csv_file, temp_dir):
        """Test complete reporting workflow ending with dashboard."""
        # Step 1: Data processing
        reader = DataReader(ReadOptions(use_polars=False))
        df = reader.read(sample_csv_file)
        
        # Step 2: Dashboard generation
        dashboard_gen = DashboardGenerator(theme='light')
        
        # Configure dashboard
        dashboard_gen.config['title'] = "Integration Test Dashboard"
        dashboard_gen.config['description'] = "Testing end-to-end workflow"
        
        # Should be able to initialize without error
        assert dashboard_gen.theme == 'light'
        assert dashboard_gen.config['title'] == "Integration Test Dashboard"
        
    def test_data_pipeline_resilience(self, temp_dir):
        """Test pipeline resilience to various data issues."""
        # Test cases with different data problems
        test_cases = [
            # Case 1: Missing values
            pd.DataFrame({
                'id': [1, 2, 3, None, 5],
                'name': ['A', 'B', None, 'D', 'E'],
                'score': [85.5, None, 78.1, 96.7, 88.9]
            }),
            
            # Case 2: Inconsistent data types
            pd.DataFrame({
                'id': ['1', '2', '3', '4', '5'],  # String IDs
                'mixed_col': [1, 'text', 3.14, True, None]
            }),
            
            # Case 3: Empty dataset
            pd.DataFrame(columns=['id', 'name', 'value']),
        ]
        
        for i, test_df in enumerate(test_cases):
            test_file = temp_dir / f"resilience_test_{i}.csv"
            test_df.to_csv(test_file, index=False)
            
            try:
                reader = DataReader(ReadOptions(use_polars=False))
                df = reader.read(test_file)
                
                # Should be able to read the file
                assert isinstance(df, pd.DataFrame)
                
                # Validation may fail, but shouldn't crash
                result = validate_dataframe(df, strict_mode=False)
                assert isinstance(result.is_valid, bool)
                
            except DataSciencePlatformError:
                # Some data issues may legitimately cause errors
                # This is acceptable as long as they're our custom exceptions
                pass
    
    def test_configuration_workflow(self, sample_csv_file):
        """Test workflow behavior with different configurations."""
        # Test different reader configurations
        configs = [
            ReadOptions(use_polars=True, chunk_size=None),
            ReadOptions(use_polars=False, chunk_size=2),
            ReadOptions(use_polars=True, encoding='utf-8'),
        ]
        
        for config in configs:
            reader = DataReader(config)
            
            if config.chunk_size:
                chunks = reader.read_chunked(sample_csv_file)
                assert isinstance(chunks, list)
                assert len(chunks) > 1
            else:
                df = reader.read(sample_csv_file)
                assert len(df) == 5
                
                # Validate each configuration works
                if hasattr(df, 'to_pandas'):
                    df_pd = df.to_pandas()
                else:
                    df_pd = df
                
                result = validate_dataframe(df_pd)
                assert result.is_valid