"""
Unit tests for the schema detection module.
"""

import pytest
from datetime import datetime

import polars as pl

from src.datascience_platform.etl.schema import (
    SchemaDetector, DataType, ColumnSchema, DatasetSchema, ColumnStatistics
)
from src.datascience_platform.core.exceptions import SchemaDetectionError


class TestSchemaDetector:
    """Test cases for the SchemaDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = SchemaDetector()
    
    def test_detect_integer_column(self):
        """Test detection of integer columns."""
        df = pl.DataFrame({
            'numbers': [1, 2, 3, 4, 5]
        })
        
        schema = self.detector.detect_schema(df)
        
        assert len(schema.columns) == 1
        col_schema = schema.columns[0]
        assert col_schema.name == 'numbers'
        assert col_schema.data_type == DataType.INTEGER
        assert not col_schema.nullable
    
    def test_detect_float_column(self):
        """Test detection of float columns."""
        df = pl.DataFrame({
            'prices': [10.5, 20.7, 30.9, 40.1]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.FLOAT
    
    def test_detect_string_column(self):
        """Test detection of string columns."""
        df = pl.DataFrame({
            'names': ['John', 'Jane', 'Bob', 'Alice']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.CATEGORICAL  # Low unique count -> categorical
    
    def test_detect_text_column(self):
        """Test detection of text columns with high uniqueness."""
        df = pl.DataFrame({
            'descriptions': [f'This is description number {i}' for i in range(100)]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.TEXT  # High unique count -> text
    
    def test_detect_boolean_column(self):
        """Test detection of boolean columns."""
        df = pl.DataFrame({
            'flags': [True, False, True, False, True]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.BOOLEAN
    
    def test_detect_email_column(self):
        """Test detection of email columns."""
        df = pl.DataFrame({
            'emails': [
                'john@example.com',
                'jane@test.org',
                'bob@company.net',
                'alice@domain.com'
            ]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.EMAIL
    
    def test_detect_url_column(self):
        """Test detection of URL columns."""
        df = pl.DataFrame({
            'urls': [
                'https://example.com',
                'http://test.org',
                'https://company.net/path',
                'http://domain.com/page?param=value'
            ]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.URL
    
    def test_detect_phone_column(self):
        """Test detection of phone number columns."""
        df = pl.DataFrame({
            'phones': [
                '+1-555-123-4567',
                '(555) 987-6543',
                '555-111-2222',
                '+44 20 7946 0958'
            ]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.PHONE
    
    def test_detect_nullable_column(self):
        """Test detection of nullable columns."""
        df = pl.DataFrame({
            'nullable_nums': [1, 2, None, 4, 5]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.nullable
        assert col_schema.statistics.null_count == 1
        assert col_schema.statistics.null_percentage == 20.0
    
    def test_detect_column_statistics_numeric(self):
        """Test calculation of statistics for numeric columns."""
        df = pl.DataFrame({
            'scores': [85, 92, 78, 96, 88, 90, 85]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        stats = col_schema.statistics
        
        assert stats.count == 7
        assert stats.null_count == 0
        assert stats.unique_count == 6  # 85 appears twice
        assert stats.min_value == 78
        assert stats.max_value == 96
        assert stats.mean_value is not None
        assert stats.median_value is not None
        assert stats.std_dev is not None
    
    def test_detect_column_statistics_string(self):
        """Test calculation of statistics for string columns."""
        df = pl.DataFrame({
            'words': ['hello', 'world', 'python', 'polars', 'hi']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        stats = col_schema.statistics
        
        assert stats.min_length == 2  # 'hi'
        assert stats.max_length == 6  # 'python', 'polars'
        assert stats.avg_length is not None
    
    def test_detect_outliers(self):
        """Test outlier detection in numeric columns."""
        # Create data with clear outliers
        normal_data = [10, 12, 11, 13, 12, 14, 11]
        outliers = [100, 2]  # Clear outliers
        data = normal_data + outliers
        
        df = pl.DataFrame({
            'values': data
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        stats = col_schema.statistics
        
        assert stats.outliers_count is not None
        assert stats.outliers_count > 0
        assert stats.outliers_percentage is not None
    
    def test_detect_categorical_values(self):
        """Test detection and counting of categorical values."""
        df = pl.DataFrame({
            'categories': ['A', 'B', 'A', 'C', 'B', 'A']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        stats = col_schema.statistics
        
        assert stats.top_values is not None
        assert len(stats.top_values) == 3  # A, B, C
        # Check that most frequent value is first
        assert stats.top_values[0][0] == 'A'  # A appears 3 times
        assert stats.top_values[0][1] == 3
    
    def test_infer_numeric_from_string(self):
        """Test inference of numeric types from string data."""
        df = pl.DataFrame({
            'string_numbers': ['123', '456', '789', '101']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        # Should detect as integer despite being stored as strings
        assert col_schema.data_type == DataType.INTEGER
    
    def test_infer_float_from_string(self):
        """Test inference of float types from string data."""
        df = pl.DataFrame({
            'string_floats': ['12.3', '45.6', '78.9', '10.1']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.FLOAT
    
    def test_infer_datetime_from_string(self):
        """Test inference of datetime types from string data."""
        df = pl.DataFrame({
            'string_dates': ['2023-01-01', '2023-02-15', '2023-03-30', '2023-12-25']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.DATE
    
    def test_generate_constraints_numeric(self):
        """Test constraint generation for numeric columns."""
        df = pl.DataFrame({
            'ages': [25, 30, 35, 40, 45]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        constraints = col_schema.constraints
        
        assert 'data_type' in constraints
        assert 'min_value' in constraints
        assert 'max_value' in constraints
        assert constraints['min_value'] == 25
        assert constraints['max_value'] == 45
        assert not constraints['nullable']
    
    def test_generate_constraints_categorical(self):
        """Test constraint generation for categorical columns."""
        df = pl.DataFrame({
            'sizes': ['S', 'M', 'L', 'M', 'S']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        constraints = col_schema.constraints
        
        assert 'allowed_values' in constraints
        assert set(constraints['allowed_values']) == {'S', 'M', 'L'}
    
    def test_generate_constraints_email(self):
        """Test constraint generation for email columns."""
        df = pl.DataFrame({
            'emails': ['test@example.com', 'user@domain.org']
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        constraints = col_schema.constraints
        
        assert 'pattern' in constraints
        # Should contain email regex pattern
        assert '@' in constraints['pattern']
    
    def test_quality_score_calculation(self):
        """Test quality score calculation."""
        # High quality data
        df_good = pl.DataFrame({
            'clean_data': [1, 2, 3, 4, 5]
        })
        
        schema_good = self.detector.detect_schema(df_good)
        col_good = schema_good.columns[0]
        
        # Low quality data with nulls
        df_bad = pl.DataFrame({
            'dirty_data': [1, None, None, None, 5]
        })
        
        schema_bad = self.detector.detect_schema(df_bad)
        col_bad = schema_bad.columns[0]
        
        assert col_good.quality_score > col_bad.quality_score
    
    def test_dataset_schema_quality_scores(self):
        """Test overall dataset quality score calculation."""
        df = pl.DataFrame({
            'good_col': [1, 2, 3, 4, 5],
            'bad_col': [None, None, None, None, 1],
            'ok_col': ['A', 'B', None, 'C', 'D']
        })
        
        schema = self.detector.detect_schema(df)
        
        assert 0 <= schema.overall_quality_score <= 1
        assert 0 <= schema.completeness_score <= 1
        assert 0 <= schema.consistency_score <= 1
        
        # Should be less than perfect due to nulls
        assert schema.completeness_score < 1.0
    
    def test_empty_dataframe(self):
        """Test schema detection on empty DataFrame."""
        df = pl.DataFrame()
        
        schema = self.detector.detect_schema(df)
        
        assert schema.total_rows == 0
        assert schema.total_columns == 0
        assert len(schema.columns) == 0
        assert schema.overall_quality_score == 1.0  # Empty is technically perfect
    
    def test_single_null_column(self):
        """Test schema detection on column with only nulls."""
        df = pl.DataFrame({
            'null_col': [None, None, None, None]
        })
        
        schema = self.detector.detect_schema(df)
        
        col_schema = schema.columns[0]
        assert col_schema.data_type == DataType.UNKNOWN
        assert col_schema.nullable
        assert col_schema.statistics.null_percentage == 100.0
    
    def test_schema_metadata(self):
        """Test schema metadata fields."""
        df = pl.DataFrame({
            'test_col': [1, 2, 3]
        })
        
        schema = self.detector.detect_schema(df)
        
        assert isinstance(schema.created_at, datetime)
        assert schema.total_rows == 3
        assert schema.total_columns == 1
    
    def test_get_column_by_name(self):
        """Test getting column schema by name."""
        df = pl.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C']
        })
        
        schema = self.detector.detect_schema(df)
        
        col1 = schema.get_column('col1')
        assert col1 is not None
        assert col1.name == 'col1'
        
        nonexistent = schema.get_column('nonexistent')
        assert nonexistent is None
    
    def test_get_columns_by_type(self):
        """Test getting columns by data type."""
        df = pl.DataFrame({
            'num1': [1, 2, 3],
            'num2': [4, 5, 6],
            'text1': ['A', 'B', 'C']
        })
        
        schema = self.detector.detect_schema(df)
        
        numeric_cols = schema.get_columns_by_type(DataType.INTEGER)
        assert len(numeric_cols) == 2
        assert all(col.data_type == DataType.INTEGER for col in numeric_cols)
        
        text_cols = schema.get_columns_by_type(DataType.CATEGORICAL)
        assert len(text_cols) == 1


class TestColumnStatistics:
    """Test cases for the ColumnStatistics class."""
    
    def test_column_statistics_creation(self):
        """Test ColumnStatistics creation with required fields."""
        stats = ColumnStatistics(
            count=100,
            null_count=5,
            null_percentage=5.0,
            unique_count=90,
            unique_percentage=90.0
        )
        
        assert stats.count == 100
        assert stats.null_count == 5
        assert stats.null_percentage == 5.0
        assert stats.unique_count == 90
        assert stats.unique_percentage == 90.0
    
    def test_column_statistics_optional_fields(self):
        """Test ColumnStatistics with optional fields."""
        stats = ColumnStatistics(
            count=100,
            null_count=0,
            null_percentage=0.0,
            unique_count=100,
            unique_percentage=100.0,
            min_value=1,
            max_value=100,
            mean_value=50.5,
            median_value=50.0,
            std_dev=28.87
        )
        
        assert stats.min_value == 1
        assert stats.max_value == 100
        assert stats.mean_value == 50.5
        assert stats.median_value == 50.0
        assert stats.std_dev == 28.87


class TestDataType:
    """Test cases for the DataType enum."""
    
    def test_data_type_values(self):
        """Test DataType enum values."""
        assert DataType.NUMERIC.value == "numeric"
        assert DataType.INTEGER.value == "integer"
        assert DataType.FLOAT.value == "float"
        assert DataType.DATETIME.value == "datetime"
        assert DataType.DATE.value == "date"
        assert DataType.TIME.value == "time"
        assert DataType.CATEGORICAL.value == "categorical"
        assert DataType.TEXT.value == "text"
        assert DataType.BOOLEAN.value == "boolean"
        assert DataType.URL.value == "url"
        assert DataType.EMAIL.value == "email"
        assert DataType.PHONE.value == "phone"
        assert DataType.UNKNOWN.value == "unknown"