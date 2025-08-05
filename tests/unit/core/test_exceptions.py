"""Unit tests for the exceptions module."""

import pytest

from datascience_platform.core.exceptions import (
    DataSciencePlatformError,
    ConfigurationError,
    ValidationError,
    ETLError,
    DataReaderError,
    DataValidationError,
    APIError,
    MLModelError,
)


class TestDataSciencePlatformError:
    """Test cases for the base DataSciencePlatformError class."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        error = DataSciencePlatformError("Test error message")
        
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.details == {}
    
    def test_exception_with_error_code(self):
        """Test exception with error code."""
        error = DataSciencePlatformError(
            "Test error", 
            error_code="TEST_ERROR"
        )
        
        assert str(error) == "[TEST_ERROR] Test error"
        assert error.error_code == "TEST_ERROR"
    
    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"key": "value", "number": 42}
        error = DataSciencePlatformError(
            "Test error",
            details=details
        )
        
        assert error.details == details
    
    def test_exception_to_dict(self):
        """Test exception serialization to dict."""
        error = DataSciencePlatformError(
            "Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error"] == "DataSciencePlatformError"
        assert error_dict["message"] == "Test error"
        assert error_dict["error_code"] == "TEST_ERROR"
        assert error_dict["details"]["key"] == "value"


class TestConfigurationError:
    """Test cases for ConfigurationError."""
    
    def test_basic_configuration_error(self):
        """Test basic configuration error."""
        error = ConfigurationError("Invalid configuration")
        
        assert str(error) == "[CONFIG_ERROR] Invalid configuration"
        assert error.error_code == "CONFIG_ERROR"
    
    def test_configuration_error_with_details(self):
        """Test configuration error with config details."""
        error = ConfigurationError(
            "Invalid value",
            config_key="max_memory",
            config_value="invalid"
        )
        
        assert error.details["config_key"] == "max_memory"
        assert error.details["config_value"] == "invalid"
    
    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from DataSciencePlatformError."""
        error = ConfigurationError("Test")
        assert isinstance(error, DataSciencePlatformError)


class TestValidationError:
    """Test cases for ValidationError."""
    
    def test_basic_validation_error(self):
        """Test basic validation error."""
        error = ValidationError("Validation failed")
        
        assert str(error) == "[VALIDATION_ERROR] Validation failed"
        assert error.error_code == "VALIDATION_ERROR"
    
    def test_validation_error_with_errors_list(self):
        """Test validation error with list of errors."""
        validation_errors = ["Error 1", "Error 2"]
        error = ValidationError(
            "Multiple validation errors",
            validation_errors=validation_errors
        )
        
        assert error.details["validation_errors"] == validation_errors
    
    def test_validation_error_with_schema(self):
        """Test validation error with schema name."""
        error = ValidationError(
            "Schema validation failed",
            schema_name="user_schema"
        )
        
        assert error.details["schema_name"] == "user_schema"
    
    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from DataSciencePlatformError."""
        error = ValidationError("Test")
        assert isinstance(error, DataSciencePlatformError)


class TestETLError:
    """Test cases for ETLError."""
    
    def test_basic_etl_error(self):
        """Test basic ETL error."""
        error = ETLError("ETL operation failed")
        
        assert str(error) == "[ETL_ERROR] ETL operation failed"
        assert error.error_code == "ETL_ERROR"
    
    def test_etl_error_with_operation(self):
        """Test ETL error with operation details."""
        error = ETLError(
            "Transform failed",
            operation="transform",
            file_path="/path/to/file.csv",
            row_number=42
        )
        
        assert error.details["operation"] == "transform"
        assert error.details["file_path"] == "/path/to/file.csv"
        assert error.details["row_number"] == 42
    
    def test_etl_error_inheritance(self):
        """Test that ETLError inherits from DataSciencePlatformError."""
        error = ETLError("Test")
        assert isinstance(error, DataSciencePlatformError)


class TestDataReaderError:
    """Test cases for DataReaderError."""
    
    def test_basic_data_reader_error(self):
        """Test basic data reader error."""
        error = DataReaderError("Failed to read file")
        
        assert str(error) == "[ETL_ERROR] Failed to read file"
        assert error.error_code == "ETL_ERROR"
    
    def test_data_reader_error_with_details(self):
        """Test data reader error with file details."""
        error = DataReaderError(
            "Unsupported format",
            file_path="/path/to/file.xyz",
            file_format="xyz"
        )
        
        assert error.details["file_path"] == "/path/to/file.xyz"
        assert error.details["file_format"] == "xyz"
        assert error.details["operation"] == "extract"
    
    def test_data_reader_error_inheritance(self):
        """Test that DataReaderError inherits from ETLError."""
        error = DataReaderError("Test")
        assert isinstance(error, ETLError)
        assert isinstance(error, DataSciencePlatformError)


class TestDataValidationError:
    """Test cases for DataValidationError."""
    
    def test_basic_data_validation_error(self):
        """Test basic data validation error."""
        error = DataValidationError("Data validation failed")
        
        assert str(error) == "[VALIDATION_ERROR] Data validation failed"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.details["schema_name"] == "data_validation"
    
    def test_data_validation_error_with_type_details(self):
        """Test data validation error with type details."""
        error = DataValidationError(
            "Type mismatch",
            column_name="age",
            expected_type="int",
            actual_type="str"
        )
        
        assert error.details["column_name"] == "age"
        assert error.details["expected_type"] == "int"
        assert error.details["actual_type"] == "str"
    
    def test_data_validation_error_inheritance(self):
        """Test that DataValidationError inherits from ValidationError."""
        error = DataValidationError("Test")
        assert isinstance(error, ValidationError)
        assert isinstance(error, DataSciencePlatformError)


class TestAPIError:
    """Test cases for APIError."""
    
    def test_basic_api_error(self):
        """Test basic API error."""
        error = APIError("API request failed")
        
        assert str(error) == "[API_ERROR] API request failed"
        assert error.error_code == "API_ERROR"
        assert error.details["status_code"] == 500
    
    def test_api_error_with_status_code(self):
        """Test API error with custom status code."""
        error = APIError(
            "Not found",
            status_code=404,
            endpoint="/api/users/123"
        )
        
        assert error.details["status_code"] == 404
        assert error.details["endpoint"] == "/api/users/123"
    
    def test_api_error_inheritance(self):
        """Test that APIError inherits from DataSciencePlatformError."""
        error = APIError("Test")
        assert isinstance(error, DataSciencePlatformError)


class TestMLModelError:
    """Test cases for MLModelError."""
    
    def test_basic_ml_model_error(self):
        """Test basic ML model error."""
        error = MLModelError("Model training failed")
        
        assert str(error) == "[ML_MODEL_ERROR] Model training failed"
        assert error.error_code == "ML_MODEL_ERROR"
    
    def test_ml_model_error_with_details(self):
        """Test ML model error with model details."""
        error = MLModelError(
            "Prediction failed",
            model_name="RandomForest",
            operation="predict"
        )
        
        assert error.details["model_name"] == "RandomForest"
        assert error.details["operation"] == "predict"
    
    def test_ml_model_error_inheritance(self):
        """Test that MLModelError inherits from DataSciencePlatformError."""
        error = MLModelError("Test")
        assert isinstance(error, DataSciencePlatformError)


class TestExceptionHierarchy:
    """Test cases for exception hierarchy and inheritance."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from DataSciencePlatformError."""
        exceptions = [
            ConfigurationError("test"),
            ValidationError("test"),
            ETLError("test"),
            DataReaderError("test"),
            DataValidationError("test"),
            APIError("test"),
            MLModelError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, DataSciencePlatformError)
            assert isinstance(exc, Exception)
    
    def test_specific_inheritance_chains(self):
        """Test specific inheritance chains."""
        # DataReaderError -> ETLError -> DataSciencePlatformError
        reader_error = DataReaderError("test")
        assert isinstance(reader_error, ETLError)
        assert isinstance(reader_error, DataSciencePlatformError)
        
        # DataValidationError -> ValidationError -> DataSciencePlatformError
        validation_error = DataValidationError("test")
        assert isinstance(validation_error, ValidationError)
        assert isinstance(validation_error, DataSciencePlatformError)
    
    def test_error_codes_are_unique(self):
        """Test that different exception types have different error codes."""
        error_codes = {
            ConfigurationError("test").error_code,
            ValidationError("test").error_code,
            ETLError("test").error_code,
            APIError("test").error_code,
            MLModelError("test").error_code,
        }
        
        # Should have 5 unique error codes
        assert len(error_codes) == 5
        
        # Specific error codes
        assert "CONFIG_ERROR" in error_codes
        assert "VALIDATION_ERROR" in error_codes
        assert "ETL_ERROR" in error_codes
        assert "API_ERROR" in error_codes
        assert "ML_MODEL_ERROR" in error_codes


class TestExceptionUsagePatterns:
    """Test cases for common exception usage patterns."""
    
    def test_raising_and_catching_exceptions(self):
        """Test raising and catching custom exceptions."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Test config error")
        
        assert "Test config error" in str(exc_info.value)
        assert exc_info.value.error_code == "CONFIG_ERROR"
    
    def test_exception_chaining(self):
        """Test exception chaining with raise from."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise ETLError("ETL failed") from e
        except ETLError as etl_error:
            assert etl_error.__cause__ is not None
            assert isinstance(etl_error.__cause__, ValueError)
            assert str(etl_error.__cause__) == "Original error"
    
    def test_exception_details_serialization(self):
        """Test that exception details can be serialized."""
        error = ValidationError(
            "Complex validation error",
            validation_errors=["error1", "error2"],
            schema_name="test_schema"
        )
        
        error_dict = error.to_dict()
        
        # Should be JSON serializable
        import json
        json_str = json.dumps(error_dict)
        recovered = json.loads(json_str)
        
        assert recovered["message"] == "Complex validation error"
        assert recovered["details"]["validation_errors"] == ["error1", "error2"]
        assert recovered["details"]["schema_name"] == "test_schema"