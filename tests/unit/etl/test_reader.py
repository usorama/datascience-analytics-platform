"""
Unit tests for the CSV reader module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import polars as pl
import chardet

from src.datascience_platform.etl.reader import CSVReader, ReadResult
from src.datascience_platform.core.exceptions import FileReadError, ProcessingError


class TestCSVReader:
    """Test cases for the CSVReader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reader = CSVReader()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_csv(self, content: str, filename: str = "test.csv", encoding: str = "utf-8") -> Path:
        """Create a temporary CSV file for testing."""
        file_path = Path(self.temp_dir) / filename
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return file_path
    
    def test_detect_encoding_utf8(self):
        """Test encoding detection for UTF-8 files."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        encoding = self.reader.detect_encoding(file_path)
        assert encoding in ['utf-8', 'ascii']  # ASCII is subset of UTF-8
    
    def test_detect_encoding_file_not_found(self):
        """Test encoding detection with non-existent file."""
        with pytest.raises(FileReadError) as exc_info:
            self.reader.detect_encoding("nonexistent.csv")
        
        assert "File not found" in str(exc_info.value)
    
    def test_detect_delimiter_comma(self):
        """Test delimiter detection for comma-separated files."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        delimiter = self.reader.detect_delimiter(file_path, "utf-8")
        assert delimiter == ","
    
    def test_detect_delimiter_semicolon(self):
        """Test delimiter detection for semicolon-separated files."""
        content = "name;age;city\nJohn;25;New York\nJane;30;London"
        file_path = self.create_test_csv(content)
        
        delimiter = self.reader.detect_delimiter(file_path, "utf-8")
        assert delimiter == ";"
    
    def test_detect_delimiter_tab(self):
        """Test delimiter detection for tab-separated files."""
        content = "name\tage\tcity\nJohn\t25\tNew York\nJane\t30\tLondon"
        file_path = self.create_test_csv(content)
        
        delimiter = self.reader.detect_delimiter(file_path, "utf-8")
        assert delimiter == "\t"
    
    def test_get_file_info(self):
        """Test file information retrieval."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        file_info = self.reader.get_file_info(file_path)
        
        assert file_info['file_path'] == str(file_path)
        assert file_info['file_size_bytes'] > 0
        assert file_info['file_size_mb'] > 0
        assert file_info['exists'] is True
    
    def test_get_file_info_nonexistent(self):
        """Test file information for non-existent file."""
        with pytest.raises(FileReadError):
            self.reader.get_file_info("nonexistent.csv")
    
    def test_read_csv_basic(self):
        """Test basic CSV reading functionality."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London\nBob,35,Paris"
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path)
        
        assert isinstance(result, ReadResult)
        assert isinstance(result.dataframe, pl.DataFrame)
        assert result.dataframe.shape == (3, 3)
        assert result.dataframe.columns == ['name', 'age', 'city']
        assert result.encoding in ['utf-8', 'ascii']
        assert result.delimiter == ','
        assert result.rows_read == 3
    
    def test_read_csv_with_custom_delimiter(self):
        """Test CSV reading with custom delimiter."""
        content = "name;age;city\nJohn;25;New York\nJane;30;London"
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path, delimiter=';')
        
        assert result.dataframe.shape == (2, 3)
        assert result.delimiter == ';'
    
    def test_read_csv_with_max_rows(self):
        """Test CSV reading with row limit."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London\nBob,35,Paris"
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path, max_rows=2)
        
        assert result.dataframe.shape == (2, 3)
        assert result.rows_read == 2
    
    def test_read_csv_with_specific_columns(self):
        """Test CSV reading with column selection."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path, columns=['name', 'age'])
        
        assert result.dataframe.shape == (2, 2)
        assert result.dataframe.columns == ['name', 'age']
    
    def test_read_csv_file_too_large(self):
        """Test CSV reading with file size limit."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        # Mock config to have very small file size limit
        with patch.object(self.reader.config.etl, 'max_file_size_mb', 0.000001):
            with pytest.raises(FileReadError) as exc_info:
                self.reader.read_csv(file_path)
            
            assert "exceeds maximum allowed size" in str(exc_info.value)
    
    def test_read_csv_chunked_reading(self):
        """Test CSV reading with chunking."""
        # Create larger content to trigger chunking
        rows = ["name,age,city"]
        for i in range(1000):
            rows.append(f"Person{i},{20+i%50},City{i%10}")
        content = "\n".join(rows)
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path, chunk_size=100)
        
        assert result.dataframe.shape == (1000, 3)
        assert result.metadata['read_method'] == 'chunked'
        assert result.metadata['chunk_size'] == 100
    
    def test_read_csv_with_progress_callback(self):
        """Test CSV reading with progress callback."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London"
        file_path = self.create_test_csv(content)
        
        progress_calls = []
        
        def progress_callback(current, total):
            progress_calls.append((current, total))
        
        reader = CSVReader(progress_callback=progress_callback)
        result = reader.read_csv(file_path)
        
        assert isinstance(result, ReadResult)
        # Progress callback might not be called for small files
    
    def test_preview_csv(self):
        """Test CSV preview functionality."""
        content = "name,age,city\nJohn,25,New York\nJane,30,London\nBob,35,Paris"
        file_path = self.create_test_csv(content)
        
        preview_df = self.reader.preview_csv(file_path, n_rows=2)
        
        assert isinstance(preview_df, pl.DataFrame)
        assert preview_df.shape == (2, 3)
        assert preview_df.columns == ['name', 'age', 'city']
    
    def test_read_csv_malformed_file(self):
        """Test CSV reading with malformed file."""
        # Create a malformed CSV (inconsistent columns)
        content = "name,age,city\nJohn,25\nJane,30,London,Extra"
        file_path = self.create_test_csv(content)
        
        # Should handle malformed CSV gracefully
        result = self.reader.read_csv(file_path)
        assert isinstance(result, ReadResult)
    
    def test_read_csv_empty_file(self):
        """Test CSV reading with empty file."""
        file_path = self.create_test_csv("")
        
        result = self.reader.read_csv(file_path)
        
        assert result.dataframe.shape[0] == 0  # No rows
    
    def test_read_csv_only_headers(self):
        """Test CSV reading with only headers."""
        content = "name,age,city"
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path)
        
        assert result.dataframe.shape == (0, 3)  # No data rows, but has columns
        assert result.dataframe.columns == ['name', 'age', 'city']
    
    @patch('chardet.detect')
    def test_detect_encoding_fallback(self, mock_detect):
        """Test encoding detection fallback when chardet fails."""
        mock_detect.return_value = {'encoding': None}
        
        content = "name,age,city\nJohn,25,New York"
        file_path = self.create_test_csv(content)
        
        encoding = self.reader.detect_encoding(file_path)
        assert encoding == 'utf-8'  # Should fallback to UTF-8
    
    def test_read_csv_with_quotes(self):
        """Test CSV reading with quoted fields."""
        content = 'name,age,description\n"John Doe",25,"A person from ""New York"""\n"Jane Smith",30,"Lives in London"'
        file_path = self.create_test_csv(content)
        
        result = self.reader.read_csv(file_path)
        
        assert result.dataframe.shape == (2, 3)
        # Check that quoted fields are handled correctly
        names = result.dataframe['name'].to_list()
        assert 'John Doe' in names
        assert 'Jane Smith' in names


class TestReadResult:
    """Test cases for the ReadResult class."""
    
    def test_read_result_creation(self):
        """Test ReadResult creation."""
        df = pl.DataFrame({
            'name': ['John', 'Jane'],
            'age': [25, 30]
        })
        
        metadata = {'test': 'value'}
        
        result = ReadResult(
            dataframe=df,
            metadata=metadata,
            encoding='utf-8',
            delimiter=',',
            rows_read=2,
            file_size_bytes=1024
        )
        
        assert result.dataframe.equals(df)
        assert result.metadata == metadata
        assert result.encoding == 'utf-8'
        assert result.delimiter == ','
        assert result.rows_read == 2
        assert result.file_size_bytes == 1024