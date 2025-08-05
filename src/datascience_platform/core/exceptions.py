"""Custom exceptions for the DataScience Analytics Platform."""

from typing import Any, Dict, Optional


class DataSciencePlatformError(Exception):
    """Base exception class for the DataScience Analytics Platform."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ConfigurationError(DataSciencePlatformError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
    ) -> None:
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: The configuration key that caused the error
            config_value: The invalid configuration value
        """
        details = {}
        if config_key is not None:
            details["config_key"] = config_key
        if config_value is not None:
            details["config_value"] = config_value
            
        super().__init__(message, error_code="CONFIG_ERROR", details=details)


class ValidationError(DataSciencePlatformError):
    """Exception raised for data validation errors."""
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[list] = None,
        schema_name: Optional[str] = None,
    ) -> None:
        """Initialize validation error.
        
        Args:
            message: Error message
            validation_errors: List of specific validation errors
            schema_name: Name of the schema that failed validation
        """
        details = {}
        if validation_errors:
            details["validation_errors"] = validation_errors
        if schema_name:
            details["schema_name"] = schema_name
            
        super().__init__(message, error_code="VALIDATION_ERROR", details=details)


class ETLError(DataSciencePlatformError):
    """Exception raised for ETL operation errors."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        file_path: Optional[str] = None,
        row_number: Optional[int] = None,
    ) -> None:
        """Initialize ETL error.
        
        Args:
            message: Error message
            operation: The ETL operation that failed (extract, transform, load)
            file_path: Path to the file being processed
            row_number: Row number where the error occurred
        """
        details = {}
        if operation:
            details["operation"] = operation
        if file_path:
            details["file_path"] = file_path
        if row_number is not None:
            details["row_number"] = row_number
            
        super().__init__(message, error_code="ETL_ERROR", details=details)


class DataReaderError(ETLError):
    """Exception raised for data reading errors."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        file_format: Optional[str] = None,
    ) -> None:
        """Initialize data reader error.
        
        Args:
            message: Error message
            file_path: Path to the file that couldn't be read
            file_format: Format of the file
        """
        details = {}
        if file_format:
            details["file_format"] = file_format
            
        super().__init__(
            message,
            operation="extract",
            file_path=file_path,
        )
        self.details.update(details)


class DataValidationError(ValidationError):
    """Exception raised for data validation errors during ETL."""
    
    def __init__(
        self,
        message: str,
        column_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_type: Optional[str] = None,
    ) -> None:
        """Initialize data validation error.
        
        Args:
            message: Error message
            column_name: Name of the column that failed validation
            expected_type: Expected data type
            actual_type: Actual data type found
        """
        details = {}
        if column_name:
            details["column_name"] = column_name
        if expected_type:
            details["expected_type"] = expected_type
        if actual_type:
            details["actual_type"] = actual_type
            
        super().__init__(message, schema_name="data_validation")
        self.details.update(details)


class APIError(DataSciencePlatformError):
    """Exception raised for API-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        endpoint: Optional[str] = None,
    ) -> None:
        """Initialize API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            endpoint: API endpoint that caused the error
        """
        details = {
            "status_code": status_code,
        }
        if endpoint:
            details["endpoint"] = endpoint
            
        super().__init__(message, error_code="API_ERROR", details=details)


class MLModelError(DataSciencePlatformError):
    """Exception raised for machine learning model errors."""
    
    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        operation: Optional[str] = None,
    ) -> None:
        """Initialize ML model error.
        
        Args:
            message: Error message
            model_name: Name of the model that caused the error
            operation: ML operation (train, predict, evaluate, etc.)
        """
        details = {}
        if model_name:
            details["model_name"] = model_name
        if operation:
            details["operation"] = operation
            
        super().__init__(message, error_code="ML_MODEL_ERROR", details=details)