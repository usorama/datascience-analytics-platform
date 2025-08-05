"""Unit tests for the pipeline orchestrator."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd
import polars as pl

from datascience_platform.core.orchestrator import (
    PipelineOrchestrator,
    PipelineConfig,
    PipelineResult
)
from datascience_platform.core.exceptions import ETLError
from datascience_platform.etl.validator import ValidationResult


class TestPipelineConfig:
    """Test cases for PipelineConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineConfig()
        
        assert config.use_polars is True
        assert config.chunk_size is None
        assert config.strict_validation is True
        assert config.schema is None
        assert config.generate_insights is True
        assert config.target_column is None
        assert config.time_column is None
        assert config.business_context is None
        assert config.generate_dashboard is True
        assert config.dashboard_theme == 'light'
        assert config.dashboard_title is None
        assert config.output_path is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = PipelineConfig(
            use_polars=False,
            chunk_size=1000,
            strict_validation=False,
            generate_insights=False,
            target_column='score',
            dashboard_theme='dark',
            dashboard_title='Custom Dashboard'
        )
        
        assert config.use_polars is False
        assert config.chunk_size == 1000
        assert config.strict_validation is False
        assert config.generate_insights is False
        assert config.target_column == 'score'
        assert config.dashboard_theme == 'dark'
        assert config.dashboard_title == 'Custom Dashboard'


class TestPipelineResult:
    """Test cases for PipelineResult dataclass."""
    
    def test_default_result(self):
        """Test default result values."""
        result = PipelineResult(success=False)
        
        assert result.success is False
        assert result.data is None
        assert result.validation_result is None
        assert result.insights is None
        assert result.dashboard_path is None
        assert result.errors == []
        assert result.warnings == []
        assert result.execution_time is None
        assert result.metadata == {}
    
    def test_result_with_data(self):
        """Test result with actual data."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        validation = ValidationResult(is_valid=True)
        
        result = PipelineResult(
            success=True,
            data=df,
            validation_result=validation,
            execution_time=1.5
        )
        
        assert result.success is True
        assert isinstance(result.data, pd.DataFrame)
        assert result.validation_result.is_valid is True
        assert result.execution_time == 1.5


class TestPipelineOrchestrator:
    """Test cases for PipelineOrchestrator."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization with default config."""
        orchestrator = PipelineOrchestrator()
        
        assert isinstance(orchestrator.config, PipelineConfig)
        assert orchestrator.data_reader is not None
        assert orchestrator.data_validator is not None
    
    def test_orchestrator_with_custom_config(self):
        """Test orchestrator initialization with custom config."""
        config = PipelineConfig(
            use_polars=False,
            strict_validation=False,
            generate_insights=False,
            generate_dashboard=False
        )
        
        orchestrator = PipelineOrchestrator(config)
        
        assert orchestrator.config.use_polars is False
        assert orchestrator.config.strict_validation is False
        assert orchestrator.config.generate_insights is False
        assert orchestrator.config.generate_dashboard is False
    
    def test_get_pipeline_status(self):
        """Test pipeline status reporting."""
        orchestrator = PipelineOrchestrator()
        status = orchestrator.get_pipeline_status()
        
        assert isinstance(status, dict)
        assert 'config' in status
        assert 'components' in status
        assert 'settings' in status
        
        assert isinstance(status['config']['use_polars'], bool)
        assert isinstance(status['components']['ml_available'], bool)
        assert isinstance(status['components']['dashboard_available'], bool)
    
    @patch('datascience_platform.core.orchestrator.DataReader')
    def test_extract_data_success(self, mock_reader_class):
        """Test successful data extraction."""
        # Setup mock
        mock_reader = Mock()
        mock_df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})
        mock_reader.read.return_value = mock_df
        mock_reader_class.return_value = mock_reader
        
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        # Test extraction
        data = orchestrator._extract_data("test.csv", result)
        
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3
        assert 'input_path' in result.metadata
        assert 'data_shape' in result.metadata
        mock_reader.read.assert_called_once_with("test.csv")
    
    @patch('datascience_platform.core.orchestrator.DataReader')
    def test_extract_data_chunked(self, mock_reader_class):
        """Test data extraction with chunking."""
        # Setup mock
        mock_reader = Mock()
        chunk1 = pd.DataFrame({'id': [1, 2], 'value': [10, 20]})
        chunk2 = pd.DataFrame({'id': [3, 4], 'value': [30, 40]})
        mock_reader.read_chunked.return_value = [chunk1, chunk2]
        mock_reader_class.return_value = mock_reader
        
        config = PipelineConfig(chunk_size=2, use_polars=False)
        orchestrator = PipelineOrchestrator(config)
        result = PipelineResult(success=False)
        
        # Test extraction
        data = orchestrator._extract_data("test.csv", result)
        
        assert data is not None
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4  # Concatenated chunks
        mock_reader.read_chunked.assert_called_once_with("test.csv")
    
    @patch('datascience_platform.core.orchestrator.DataReader')
    def test_extract_data_failure(self, mock_reader_class):
        """Test data extraction failure handling."""
        # Setup mock to raise exception
        mock_reader = Mock()
        mock_reader.read.side_effect = ETLError("File not found")
        mock_reader_class.return_value = mock_reader
        
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        # Test extraction
        data = orchestrator._extract_data("nonexistent.csv", result)
        
        assert data is None
        assert len(result.errors) > 0
        assert "Data extraction failed" in result.errors[0]
    
    def test_validate_data_success(self):
        """Test successful data validation."""
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'score': [85.5, 92.3, 78.1]
        })
        
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        # Test validation
        validation_result = orchestrator._validate_data(df, result)
        
        assert validation_result is not None
        assert isinstance(validation_result, ValidationResult)
        # Basic validation should pass for clean data
        assert validation_result.is_valid or len(result.warnings) > 0
    
    def test_validate_data_with_polars(self):
        """Test data validation with Polars DataFrame."""
        df = pl.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'score': [85.5, 92.3, 78.1]
        })
        
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        # Test validation
        validation_result = orchestrator._validate_data(df, result)
        
        assert validation_result is not None
        assert isinstance(validation_result, ValidationResult)
    
    @patch('datascience_platform.etl.validator.validate_dataframe')
    def test_validate_data_failure(self, mock_validate):
        """Test validation failure handling."""
        mock_validate.side_effect = Exception("Validation error")
        
        df = pd.DataFrame({'id': [1, 2, 3]})
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        # Test validation
        validation_result = orchestrator._validate_data(df, result)
        
        assert validation_result is None
        assert len(result.errors) > 0
        assert "Data validation failed" in result.errors[0]
    
    @patch('datascience_platform.core.orchestrator.ML_AVAILABLE', True)
    @patch('datascience_platform.core.orchestrator.InsightGenerator')
    def test_generate_insights_success(self, mock_insight_class):
        """Test successful insights generation."""
        # Setup mock
        mock_generator = Mock()
        mock_insights = {'data_overview': {'rows': 3, 'columns': 2}}
        mock_generator.generate_comprehensive_insights.return_value = mock_insights
        mock_insight_class.return_value = mock_generator
        
        config = PipelineConfig(generate_insights=True)
        orchestrator = PipelineOrchestrator(config)
        result = PipelineResult(success=False)
        
        df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})
        
        # Test insights generation
        insights = orchestrator._generate_insights(df, result)
        
        assert insights is not None
        assert isinstance(insights, dict)
        assert 'data_overview' in insights
        mock_generator.generate_comprehensive_insights.assert_called_once()
    
    @patch('datascience_platform.core.orchestrator.ML_AVAILABLE', False)
    def test_generate_insights_ml_not_available(self):
        """Test insights generation when ML components are not available."""
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        df = pd.DataFrame({'id': [1, 2, 3]})
        
        # Test insights generation
        insights = orchestrator._generate_insights(df, result)
        
        assert insights is None
        assert len(result.warnings) > 0
        assert "ML components not available" in result.warnings[0]
    
    @patch('datascience_platform.core.orchestrator.DASHBOARD_AVAILABLE', True)
    @patch('datascience_platform.core.orchestrator.DashboardGenerator')
    def test_generate_dashboard_success(self, mock_dashboard_class):
        """Test successful dashboard generation."""
        # Setup mock
        mock_generator = Mock()
        mock_generator.config = {'title': 'Test Dashboard'}
        mock_dashboard_class.return_value = mock_generator
        
        config = PipelineConfig(generate_dashboard=True)
        orchestrator = PipelineOrchestrator(config)
        result = PipelineResult(success=False)
        
        df = pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})
        insights = {'test': 'insight'}
        
        with patch('pathlib.Path.mkdir'):
            # Test dashboard generation
            dashboard_path = orchestrator._generate_dashboard(
                df, insights, "/tmp/output", result
            )
        
        assert dashboard_path is not None
        assert isinstance(dashboard_path, Path)
        assert 'dashboard_config' in result.metadata
    
    @patch('datascience_platform.core.orchestrator.DASHBOARD_AVAILABLE', False)
    def test_generate_dashboard_not_available(self):
        """Test dashboard generation when components are not available."""
        orchestrator = PipelineOrchestrator()
        result = PipelineResult(success=False)
        
        df = pd.DataFrame({'id': [1, 2, 3]})
        
        # Test dashboard generation
        dashboard_path = orchestrator._generate_dashboard(
            df, None, "/tmp/output", result
        )
        
        assert dashboard_path is None
        assert len(result.warnings) > 0
        assert "Dashboard components not available" in result.warnings[0]
    
    def test_execute_stage_extract(self):
        """Test executing extract stage individually."""
        with patch.object(PipelineOrchestrator, '_extract_data') as mock_extract:
            mock_df = pd.DataFrame({'id': [1, 2, 3]})
            mock_extract.return_value = mock_df
            
            orchestrator = PipelineOrchestrator()
            
            # Test extract stage
            result = orchestrator.execute_stage('extract', input_path='test.csv')
            
            assert result['success'] is True
            assert result['result'] is mock_df
            assert result['error'] is None
            mock_extract.assert_called_once()
    
    def test_execute_stage_validate(self):
        """Test executing validate stage individually."""
        with patch.object(PipelineOrchestrator, '_validate_data') as mock_validate:
            mock_result = ValidationResult(is_valid=True)
            mock_validate.return_value = mock_result
            
            orchestrator = PipelineOrchestrator()
            df = pd.DataFrame({'id': [1, 2, 3]})
            
            # Test validate stage
            result = orchestrator.execute_stage('validate', data=df)
            
            assert result['success'] is True
            assert result['result'] is mock_result
            assert result['error'] is None
            mock_validate.assert_called_once_with(df, unittest.mock.ANY)
    
    def test_execute_stage_invalid(self):
        """Test executing invalid stage."""
        orchestrator = PipelineOrchestrator()
        
        # Test invalid stage
        result = orchestrator.execute_stage('invalid_stage')
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "Unknown stage" in result['error']
    
    def test_execute_stage_missing_args(self):
        """Test executing stage with missing required arguments."""
        orchestrator = PipelineOrchestrator()
        
        # Test extract without input_path
        result = orchestrator.execute_stage('extract')
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "input_path required" in result['error']
        
        # Test validate without data
        result = orchestrator.execute_stage('validate')
        
        assert result['success'] is False
        assert result['error'] is not None
        assert "data required" in result['error']
    
    @patch('datascience_platform.core.orchestrator.DataReader')
    @patch('datascience_platform.etl.validator.validate_dataframe')
    def test_full_pipeline_execution(self, mock_validate, mock_reader_class):
        """Test complete pipeline execution."""
        # Setup mocks
        mock_reader = Mock()
        mock_df = pd.DataFrame({'id': [1, 2, 3], 'score': [85, 90, 78]})
        mock_reader.read.return_value = mock_df
        mock_reader_class.return_value = mock_reader
        
        mock_validation = ValidationResult(is_valid=True)
        mock_validate.return_value = mock_validation
        
        config = PipelineConfig(
            generate_insights=False,  # Disable to avoid ML dependencies
            generate_dashboard=False  # Disable to avoid dashboard dependencies
        )
        
        orchestrator = PipelineOrchestrator(config)
        
        # Execute pipeline
        result = orchestrator.execute_pipeline("test.csv")
        
        assert result.success is True
        assert result.data is not None
        assert result.validation_result is not None
        assert result.execution_time is not None
        assert len(result.errors) == 0
        
        # Check metadata
        assert 'input_path' in result.metadata
        assert 'data_shape' in result.metadata
    
    @patch('datascience_platform.core.orchestrator.DataReader')
    def test_pipeline_execution_with_extraction_failure(self, mock_reader_class):
        """Test pipeline execution with extraction failure."""
        # Setup mock to fail
        mock_reader = Mock()
        mock_reader.read.side_effect = ETLError("File not found")
        mock_reader_class.return_value = mock_reader
        
        orchestrator = PipelineOrchestrator()
        
        # Execute pipeline
        result = orchestrator.execute_pipeline("nonexistent.csv")
        
        assert result.success is False
        assert result.data is None
        assert len(result.errors) > 0
        assert result.execution_time is not None


class TestPipelineIntegration:
    """Integration tests for pipeline orchestrator."""
    
    def test_orchestrator_with_real_data(self, sample_csv_file):
        """Test orchestrator with real sample data."""
        config = PipelineConfig(
            use_polars=False,
            generate_insights=False,  # Disable ML to avoid dependencies
            generate_dashboard=False  # Disable dashboard to avoid dependencies
        )
        
        orchestrator = PipelineOrchestrator(config)
        
        # Execute pipeline
        result = orchestrator.execute_pipeline(sample_csv_file)
        
        # Should succeed with basic ETL
        assert result.success is True
        assert result.data is not None
        assert len(result.data) == 5  # Sample CSV has 5 rows
        assert result.validation_result is not None
        assert result.execution_time is not None
    
    def test_orchestrator_stage_by_stage(self, sample_csv_file):
        """Test orchestrator executing stages individually."""
        orchestrator = PipelineOrchestrator()
        
        # Stage 1: Extract
        extract_result = orchestrator.execute_stage('extract', input_path=sample_csv_file)
        assert extract_result['success'] is True
        data = extract_result['result']
        assert data is not None
        
        # Stage 2: Validate
        validate_result = orchestrator.execute_stage('validate', data=data)
        assert validate_result['success'] is True
        validation = validate_result['result']
        assert validation is not None
        
        # Stages should work independently
        assert isinstance(data, (pd.DataFrame, pl.DataFrame))
        assert isinstance(validation, ValidationResult)


# Import statement for unittest.mock.ANY
import unittest.mock