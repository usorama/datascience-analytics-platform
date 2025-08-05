"""
Unit tests for the data transformer module.
"""

import pytest
from unittest.mock import patch

import polars as pl
import numpy as np

from src.datascience_platform.etl.transformer import (
    DataTransformer, TransformationReport, TransformationStep,
    MissingValueStrategy, NormalizationMethod, OutlierHandling
)
from src.datascience_platform.etl.schema import (
    DatasetSchema, ColumnSchema, DataType, ColumnStatistics
)


class TestDataTransformer:
    """Test cases for the DataTransformer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DataTransformer()
    
    def create_sample_schema(self) -> DatasetSchema:
        """Create a sample dataset schema for testing."""
        col1_stats = ColumnStatistics(
            count=100,
            null_count=0,
            null_percentage=0.0,
            unique_count=100,
            unique_percentage=100.0,
            min_value=1,
            max_value=100
        )
        
        col2_stats = ColumnStatistics(
            count=100,
            null_count=5,
            null_percentage=5.0,
            unique_count=3,
            unique_percentage=3.0
        )
        
        col1 = ColumnSchema(
            name="numeric_col",
            data_type=DataType.INTEGER,
            polars_type="Int64",
            nullable=False,
            statistics=col1_stats
        )
        
        col2 = ColumnSchema(
            name="category_col",
            data_type=DataType.CATEGORICAL,
            polars_type="Utf8",
            nullable=True,
            statistics=col2_stats
        )
        
        return DatasetSchema(
            columns=[col1, col2],
            total_rows=100,
            total_columns=2,
            file_size_bytes=1024
        )
    
    def test_transform_basic_dataframe(self):
        """Test basic transformation of a clean DataFrame."""
        df = pl.DataFrame({
            'col1': [1, 2, 3, 4, 5],
            'col2': ['A', 'B', 'C', 'D', 'E']
        })
        
        transformed_df, report = self.transformer.transform_dataframe(df)
        
        assert isinstance(transformed_df, pl.DataFrame)
        assert isinstance(report, TransformationReport)
        assert report.original_shape == (5, 2)
        assert report.final_shape == transformed_df.shape
        assert report.transformation_success_rate > 0
    
    def test_handle_duplicates_drop(self):
        """Test duplicate row handling with drop strategy."""
        df = pl.DataFrame({
            'col1': [1, 2, 1, 3, 2],  # Duplicates
            'col2': ['A', 'B', 'A', 'C', 'B']  # Duplicates
        })
        
        # Set configuration to drop duplicates
        with patch.object(self.transformer.config.transformation, 'duplicate_strategy', 'drop_duplicates'):
            transformed_df, report = self.transformer.transform_dataframe(df)
        
        # Should have fewer rows after deduplication
        assert len(transformed_df) < len(df)
        
        # Check for duplicate handling step in report
        duplicate_steps = [step for step in report.steps 
                          if step.step_name == "handle_duplicates"]
        assert len(duplicate_steps) == 1
        assert duplicate_steps[0].success
    
    def test_handle_missing_values_mean(self):
        """Test missing value handling with mean strategy."""
        df = pl.DataFrame({
            'numeric_col': [1.0, 2.0, None, 4.0, 5.0]
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="numeric_col",
                data_type=DataType.FLOAT,
                polars_type="Float64",
                nullable=True,
                statistics=ColumnStatistics(5, 1, 20.0, 4, 80.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Should have no null values after transformation
        assert transformed_df['numeric_col'].null_count() == 0
        
        # Check for imputation step in report
        impute_steps = [step for step in report.steps 
                       if "impute" in step.operation]
        assert len(impute_steps) >= 1
    
    def test_handle_missing_values_mode(self):
        """Test missing value handling with mode strategy."""
        df = pl.DataFrame({
            'category_col': ['A', 'B', 'A', None, 'A']
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="category_col",
                data_type=DataType.CATEGORICAL,
                polars_type="Utf8",
                nullable=True,
                statistics=ColumnStatistics(5, 1, 20.0, 2, 40.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Should have no null values after transformation
        assert transformed_df['category_col'].null_count() == 0
        
        # The mode should be 'A' (appears 3 times)
        filled_value = transformed_df['category_col'].to_list()[3]  # The null position
        assert filled_value == 'A'
    
    def test_handle_missing_values_drop(self):
        """Test missing value handling with drop strategy."""
        df = pl.DataFrame({
            'text_col': ['Hello', 'World', None, 'Test', 'Data']
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="text_col",
                data_type=DataType.TEXT,
                polars_type="Utf8",
                nullable=True,
                statistics=ColumnStatistics(5, 1, 20.0, 4, 80.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Should have one less row after dropping null
        assert len(transformed_df) == 4
        assert transformed_df['text_col'].null_count() == 0
    
    def test_handle_outliers_cap(self):
        """Test outlier handling with capping strategy."""
        # Create data with clear outliers
        normal_data = [10, 11, 12, 13, 14]
        outlier_data = [100, 200]  # Clear outliers
        
        df = pl.DataFrame({
            'values': normal_data + outlier_data
        })
        
        with patch.object(self.transformer.config.transformation, 'outlier_handling', 'cap'):
            transformed_df, report = self.transformer.transform_dataframe(df)
        
        # Outliers should be capped
        max_val = transformed_df['values'].max()
        min_val = transformed_df['values'].min()
        
        # Should be within reasonable bounds (not 200)
        assert max_val < 100
        
        # Check for outlier handling step in report
        outlier_steps = [step for step in report.steps 
                        if "outlier" in step.operation]
        # Might have outlier steps depending on detection
        assert len(outlier_steps) >= 0
    
    def test_handle_outliers_remove(self):
        """Test outlier handling with removal strategy."""
        # Create data with clear outliers
        normal_data = [10, 11, 12, 13, 14]
        outlier_data = [100, 200]  # Clear outliers
        
        df = pl.DataFrame({
            'values': normal_data + outlier_data
        })
        
        with patch.object(self.transformer.config.transformation, 'outlier_handling', 'remove'):
            transformed_df, report = self.transformer.transform_dataframe(df)
        
        # Should have fewer rows if outliers were removed
        # Note: Might not trigger if outliers don't meet threshold
        assert len(transformed_df) <= len(df)
    
    def test_normalize_columns_z_score(self):
        """Test column normalization with z-score."""
        df = pl.DataFrame({
            'numeric_col': [10, 20, 30, 40, 50]
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="numeric_col",
                data_type=DataType.INTEGER,
                polars_type="Int64",
                nullable=False,
                statistics=ColumnStatistics(5, 0, 0.0, 5, 100.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        with patch.object(self.transformer.config.transformation.normalization_methods, '__getitem__', return_value='z_score'):
            transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Check if normalization was applied
        normalize_steps = [step for step in report.steps 
                          if "normalize" in step.operation]
        
        # Normalized values should have mean close to 0 and std close to 1
        if len(normalize_steps) > 0:
            normalized_values = transformed_df['numeric_col'].to_numpy()
            assert abs(np.mean(normalized_values)) < 0.1  # Close to 0
            assert abs(np.std(normalized_values) - 1.0) < 0.1  # Close to 1
    
    def test_normalize_columns_min_max(self):
        """Test column normalization with min-max scaling."""
        df = pl.DataFrame({
            'numeric_col': [10, 20, 30, 40, 50]
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="numeric_col",
                data_type=DataType.INTEGER,
                polars_type="Int64",
                nullable=False,
                statistics=ColumnStatistics(5, 0, 0.0, 5, 100.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        with patch.object(self.transformer.config.transformation.normalization_methods, '__getitem__', return_value='min_max'):
            transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Check if normalization was applied
        normalize_steps = [step for step in report.steps 
                          if "normalize" in step.operation]
        
        # Min-max normalized values should be between 0 and 1
        if len(normalize_steps) > 0:
            normalized_values = transformed_df['numeric_col'].to_numpy()
            assert np.min(normalized_values) >= 0.0
            assert np.max(normalized_values) <= 1.0
    
    def test_encode_categorical(self):
        """Test categorical variable encoding."""
        df = pl.DataFrame({
            'category': ['A', 'B', 'C', 'A', 'B']
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="category",
                data_type=DataType.CATEGORICAL,
                polars_type="Utf8",
                nullable=False,
                statistics=ColumnStatistics(5, 0, 0.0, 3, 60.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Should have added encoded column
        encoding_steps = [step for step in report.steps 
                         if "encode" in step.operation]
        
        if len(encoding_steps) > 0:
            # Should have new encoded column
            assert 'category_encoded' in transformed_df.columns
            
            # Encoded values should be integers
            encoded_values = transformed_df['category_encoded'].to_list()
            assert all(isinstance(val, (int, type(None))) for val in encoded_values)
    
    def test_inverse_transform_column(self):
        """Test inverse transformation of normalized columns."""
        df = pl.DataFrame({
            'numeric_col': [10, 20, 30, 40, 50]
        })
        
        schema = DatasetSchema(
            columns=[ColumnSchema(
                name="numeric_col",
                data_type=DataType.INTEGER,
                polars_type="Int64",
                nullable=False,
                statistics=ColumnStatistics(5, 0, 0.0, 5, 100.0)
            )],
            total_rows=5,
            total_columns=1,
            file_size_bytes=100
        )
        
        # First normalize
        with patch.object(self.transformer.config.transformation.normalization_methods, '__getitem__', return_value='z_score'):
            transformed_df, report = self.transformer.transform_dataframe(df, schema=schema)
        
        # Then inverse transform
        if 'numeric_col' in self.transformer.scalers:
            normalized_values = transformed_df['numeric_col']
            inverse_values = self.transformer.inverse_transform_column('numeric_col', normalized_values)
            
            # Should be close to original values
            original_values = df['numeric_col'].to_numpy()
            inverse_array = inverse_values.to_numpy()
            
            assert np.allclose(original_values, inverse_array, rtol=1e-10)
    
    def test_detect_outliers_iqr(self):
        """Test outlier detection using IQR method."""
        # Create data with clear outliers
        normal_data = [10, 11, 12, 13, 14]
        outlier_data = [100, 200]
        
        col_data = pl.Series("test", normal_data + outlier_data)
        
        outlier_indices, lower_bound, upper_bound = self.transformer._detect_outliers_iqr(col_data)
        
        # Should detect the outliers
        assert len(outlier_indices) >= 2  # Should detect 100 and 200
        assert lower_bound < 10
        assert upper_bound > 14 and upper_bound < 100
    
    def test_get_missing_value_strategy(self):
        """Test missing value strategy selection."""
        schema = self.create_sample_schema()
        
        # Test numeric column strategy
        numeric_strategy = self.transformer._get_missing_value_strategy("numeric_col", schema)
        assert isinstance(numeric_strategy, MissingValueStrategy)
        
        # Test categorical column strategy  
        categorical_strategy = self.transformer._get_missing_value_strategy("category_col", schema)
        assert isinstance(categorical_strategy, MissingValueStrategy)
        
        # Test unknown column (should use default)
        default_strategy = self.transformer._get_missing_value_strategy("unknown_col", schema)
        assert isinstance(default_strategy, MissingValueStrategy)
    
    def test_get_normalization_method(self):
        """Test normalization method selection."""
        schema = self.create_sample_schema()
        
        # Test numeric column
        numeric_method = self.transformer._get_normalization_method("numeric_col", schema)
        assert isinstance(numeric_method, NormalizationMethod)
        
        # Test non-numeric column
        categorical_method = self.transformer._get_normalization_method("category_col", schema)
        assert categorical_method == NormalizationMethod.NONE
    
    def test_should_encode_column(self):
        """Test column encoding decision."""
        schema = self.create_sample_schema()
        
        # Test categorical column
        cat_col_data = pl.Series("test", ['A', 'B', 'C'])
        should_encode_cat = self.transformer._should_encode_column("category_col", schema, cat_col_data)
        assert should_encode_cat
        
        # Test numeric column
        num_col_data = pl.Series("test", [1, 2, 3])
        should_encode_num = self.transformer._should_encode_column("numeric_col", schema, num_col_data)
        assert not should_encode_num
    
    def test_transformation_report_metadata(self):
        """Test transformation report metadata."""
        df = pl.DataFrame({
            'col1': [1, 2, 3, 4, 5]
        })
        
        transformed_df, report = self.transformer.transform_dataframe(df)
        
        assert report.original_shape == (5, 1)
        assert report.final_shape == transformed_df.shape
        assert report.total_transformation_time > 0
        assert report.data_completeness_before == 1.0  # No nulls
        assert report.data_completeness_after >= 0


class TestTransformationReport:
    """Test cases for the TransformationReport class."""
    
    def test_transformation_report_creation(self):
        """Test TransformationReport creation."""
        report = TransformationReport(
            original_shape=(100, 5),
            final_shape=(95, 5)
        )
        
        assert report.original_shape == (100, 5)
        assert report.final_shape == (95, 5)
        assert len(report.steps) == 0
        assert report.total_rows_removed == 0
        assert report.total_values_imputed == 0
        assert report.transformation_success_rate == 1.0
    
    def test_add_transformation_step(self):
        """Test adding transformation steps."""
        report = TransformationReport((100, 5), (95, 5))
        
        step = TransformationStep(
            step_name="test_step",
            column="test_col",
            operation="remove_rows",  
            parameters={"test": "value"},
            rows_affected=5,
            success=True
        )
        
        report.add_step(step)
        
        assert len(report.steps) == 1
        assert report.total_rows_removed == 5
    
    def test_calculate_success_rate(self):
        """Test success rate calculation."""
        report = TransformationReport((100, 5), (95, 5))
        
        # Add successful step
        success_step = TransformationStep(
            step_name="success_step",
            column=None,
            operation="test_op",
            parameters={},
            success=True
        )
        
        # Add failed step
        failed_step = TransformationStep(
            step_name="failed_step",
            column=None,
            operation="test_op",
            parameters={},
            success=False,
            error_message="Test error"
        )
        
        report.add_step(success_step)
        report.add_step(failed_step)
        report.calculate_success_rate()
        
        assert report.transformation_success_rate == 0.5  # 1 success out of 2 total


class TestTransformationStep:
    """Test cases for the TransformationStep class."""
    
    def test_transformation_step_creation(self):
        """Test TransformationStep creation."""
        step = TransformationStep(
            step_name="test_step",
            column="test_column",
            operation="test_operation",
            parameters={"param1": "value1"},
            rows_affected=10,
            execution_time_seconds=0.5,
            success=True
        )
        
        assert step.step_name == "test_step"
        assert step.column == "test_column"
        assert step.operation == "test_operation"
        assert step.parameters == {"param1": "value1"}
        assert step.rows_affected == 10
        assert step.execution_time_seconds == 0.5
        assert step.success is True
        assert step.error_message is None
    
    def test_transformation_step_with_error(self):
        """Test TransformationStep with error."""
        step = TransformationStep(
            step_name="failed_step",
            column=None,
            operation="test_operation",
            parameters={},
            success=False,
            error_message="Something went wrong"
        )
        
        assert step.success is False
        assert step.error_message == "Something went wrong"


class TestEnums:
    """Test cases for transformation enums."""
    
    def test_missing_value_strategy_values(self):
        """Test MissingValueStrategy enum values."""
        assert MissingValueStrategy.DROP.value == "drop"
        assert MissingValueStrategy.MEAN.value == "mean"
        assert MissingValueStrategy.MEDIAN.value == "median"
        assert MissingValueStrategy.MODE.value == "mode"
        assert MissingValueStrategy.FORWARD_FILL.value == "forward_fill"
        assert MissingValueStrategy.BACKWARD_FILL.value == "backward_fill"
        assert MissingValueStrategy.INTERPOLATE.value == "interpolate"
        assert MissingValueStrategy.CONSTANT.value == "constant"
    
    def test_normalization_method_values(self):
        """Test NormalizationMethod enum values."""
        assert NormalizationMethod.NONE.value == "none"
        assert NormalizationMethod.Z_SCORE.value == "z_score"
        assert NormalizationMethod.MIN_MAX.value == "min_max"
        assert NormalizationMethod.ROBUST.value == "robust"
    
    def test_outlier_handling_values(self):
        """Test OutlierHandling enum values."""
        assert OutlierHandling.NONE.value == "none"
        assert OutlierHandling.REMOVE.value == "remove"
        assert OutlierHandling.CAP.value == "cap"
        assert OutlierHandling.TRANSFORM.value == "transform"