"""Data validation functionality for the DataScience Analytics Platform."""

from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import polars as pl
import pandera as pa
from pydantic import BaseModel, Field

from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import ValidationError, DataValidationError
from datascience_platform.etl.schema import DataSchema


class ValidationResult(BaseModel):
    """Result of data validation."""
    
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: List[str] = Field(default_factory=list, description="List of validation warnings")
    schema_name: Optional[str] = Field(default=None, description="Name of schema used for validation")
    rows_validated: int = Field(default=0, description="Number of rows validated")
    columns_validated: int = Field(default=0, description="Number of columns validated")
    validation_details: Dict[str, Any] = Field(default_factory=dict, description="Detailed validation results")
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0


class DataValidator:
    """Data validation engine with schema support."""
    
    def __init__(self, strict_mode: Optional[bool] = None) -> None:
        """Initialize data validator.
        
        Args:
            strict_mode: Whether to use strict validation (uses config default if not provided)
        """
        self.strict_mode = strict_mode if strict_mode is not None else settings.validation_strict
    
    def validate_with_schema(
        self,
        data: Union[pd.DataFrame, pl.DataFrame],
        schema: DataSchema,
        sample_size: Optional[int] = None
    ) -> ValidationResult:
        """Validate data against a schema.
        
        Args:
            data: DataFrame to validate
            schema: Schema definition for validation
            sample_size: Number of rows to validate (validates all if None)
            
        Returns:
            Validation result with errors and warnings
        """
        result = ValidationResult(
            is_valid=True,  # Start as valid, will be set to False if errors found
            schema_name=schema.name,
            rows_validated=len(data),
            columns_validated=len(data.columns) if hasattr(data, 'columns') else 0
        )
        
        # Sample data if requested
        if sample_size and len(data) > sample_size:
            if isinstance(data, pl.DataFrame):
                data_sample = data.sample(sample_size)
            else:
                data_sample = data.sample(n=sample_size)
            result.rows_validated = sample_size
        else:
            data_sample = data
        
        try:
            # Convert to pandas if using Polars (Pandera works with pandas)
            if isinstance(data_sample, pl.DataFrame):
                df_to_validate = data_sample.to_pandas()
            else:
                df_to_validate = data_sample
            
            # Create Pandera schema and validate
            pandera_schema = schema.to_pandera_schema()
            validated_df = pandera_schema.validate(df_to_validate, lazy=True)
            
            # If we get here, validation passed
            result.validation_details["pandera_validation"] = "passed"
            
        except pa.errors.SchemaErrors as e:
            # Handle multiple validation errors
            for error in e.schema_errors:
                result.add_error(f"Schema error: {str(error)}")
            
            result.validation_details["pandera_errors"] = [str(err) for err in e.schema_errors]
            
        except pa.errors.SchemaError as e:
            # Handle single validation error
            result.add_error(f"Schema validation failed: {str(e)}")
            result.validation_details["pandera_error"] = str(e)
        
        except Exception as e:
            result.add_error(f"Validation error: {str(e)}")
            result.validation_details["unexpected_error"] = str(e)
        
        # Additional custom validations
        self._perform_custom_validations(data_sample, schema, result)
        
        return result
    
    def validate_data_quality(
        self,
        data: Union[pd.DataFrame, pl.DataFrame],
        checks: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Perform general data quality validation.
        
        Args:
            data: DataFrame to validate
            checks: Custom validation checks to perform
            
        Returns:
            Validation result with quality assessment
        """
        result = ValidationResult(
            is_valid=True,  # Start as valid, will be set to False if errors found
            rows_validated=len(data),
            columns_validated=len(data.columns) if hasattr(data, 'columns') else 0
        )
        
        # Convert to pandas for consistency
        if isinstance(data, pl.DataFrame):
            df = data.to_pandas()
        else:
            df = data
        
        # Default quality checks
        default_checks = {
            "check_duplicates": True,
            "check_missing_values": True,
            "check_data_types": True,
            "check_outliers": False,
            "missing_threshold": 0.5,  # Flag columns with >50% missing values
            "duplicate_threshold": 0.1  # Flag if >10% rows are duplicates
        }
        
        if checks:
            default_checks.update(checks)
        
        # Check for duplicates
        if default_checks.get("check_duplicates"):
            duplicate_count = df.duplicated().sum()
            duplicate_percentage = duplicate_count / len(df)
            
            result.validation_details["duplicates"] = {
                "count": int(duplicate_count),
                "percentage": float(duplicate_percentage)
            }
            
            if duplicate_percentage > default_checks.get("duplicate_threshold", 0.1):
                result.add_warning(
                    f"High duplicate rate: {duplicate_percentage:.2%} of rows are duplicates"
                )
        
        # Check for missing values
        if default_checks.get("check_missing_values"):
            missing_info = {}
            missing_threshold = default_checks.get("missing_threshold", 0.5)
            
            for column in df.columns:
                missing_count = df[column].isnull().sum()
                missing_percentage = missing_count / len(df)
                
                missing_info[column] = {
                    "count": int(missing_count),
                    "percentage": float(missing_percentage)
                }
                
                if missing_percentage > missing_threshold:
                    result.add_warning(
                        f"Column '{column}' has high missing value rate: {missing_percentage:.2%}"
                    )
                elif missing_percentage == 1.0:
                    result.add_error(f"Column '{column}' is completely empty")
            
            result.validation_details["missing_values"] = missing_info
        
        # Check data types
        if default_checks.get("check_data_types"):
            dtype_info = {}
            
            for column in df.columns:
                dtype = str(df[column].dtype)
                unique_count = df[column].nunique()
                
                dtype_info[column] = {
                    "dtype": dtype,
                    "unique_values": int(unique_count)
                }
                
                # Flag potential issues
                if dtype == "object" and unique_count > len(df) * 0.8:
                    result.add_warning(
                        f"Column '{column}' might be better as a different data type (mostly unique text values)"
                    )
                elif dtype == "object" and unique_count < 10:
                    result.add_warning(
                        f"Column '{column}' might be better as categorical (only {unique_count} unique values)"
                    )
            
            result.validation_details["data_types"] = dtype_info
        
        # Check for outliers (basic statistical approach)
        if default_checks.get("check_outliers"):
            outlier_info = {}
            numeric_columns = df.select_dtypes(include=['number']).columns
            
            for column in numeric_columns:
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                outlier_count = len(outliers)
                outlier_percentage = outlier_count / len(df)
                
                outlier_info[column] = {
                    "count": outlier_count,
                    "percentage": float(outlier_percentage),
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound)
                }
                
                if outlier_percentage > 0.05:  # More than 5% outliers
                    result.add_warning(
                        f"Column '{column}' has {outlier_percentage:.2%} potential outliers"
                    )
            
            result.validation_details["outliers"] = outlier_info
        
        return result
    
    def validate_column_consistency(
        self,
        data: Union[pd.DataFrame, pl.DataFrame],
        column_rules: Dict[str, Dict[str, Any]]
    ) -> ValidationResult:
        """Validate column-specific rules and constraints.
        
        Args:
            data: DataFrame to validate
            column_rules: Dictionary of column names and their validation rules
            
        Returns:
            Validation result
        """
        result = ValidationResult(
            rows_validated=len(data),
            columns_validated=len(column_rules)
        )
        
        # Convert to pandas for consistency
        if isinstance(data, pl.DataFrame):
            df = data.to_pandas()
        else:
            df = data
        
        for column, rules in column_rules.items():
            if column not in df.columns:
                result.add_error(f"Column '{column}' not found in data")
                continue
            
            column_data = df[column]
            
            # Check data type
            if "dtype" in rules:
                expected_dtype = rules["dtype"]
                actual_dtype = str(column_data.dtype)
                
                if actual_dtype != expected_dtype:
                    if self.strict_mode:
                        result.add_error(
                            f"Column '{column}' has wrong data type: expected {expected_dtype}, got {actual_dtype}"
                        )
                    else:
                        result.add_warning(
                            f"Column '{column}' has unexpected data type: expected {expected_dtype}, got {actual_dtype}"
                        )
            
            # Check for null values
            if "nullable" in rules and not rules["nullable"]:
                null_count = column_data.isnull().sum()
                if null_count > 0:
                    result.add_error(f"Column '{column}' contains {null_count} null values but should not be nullable")
            
            # Check uniqueness
            if rules.get("unique", False):
                duplicate_count = column_data.duplicated().sum()
                if duplicate_count > 0:
                    result.add_error(f"Column '{column}' contains {duplicate_count} duplicate values but should be unique")
            
            # Check value ranges
            if "min_value" in rules:
                min_violations = column_data < rules["min_value"]
                violation_count = min_violations.sum()
                if violation_count > 0:
                    result.add_error(
                        f"Column '{column}' has {violation_count} values below minimum {rules['min_value']}"
                    )
            
            if "max_value" in rules:
                max_violations = column_data > rules["max_value"]
                violation_count = max_violations.sum()
                if violation_count > 0:
                    result.add_error(
                        f"Column '{column}' has {violation_count} values above maximum {rules['max_value']}"
                    )
            
            # Check allowed values
            if "allowed_values" in rules:
                allowed_values = set(rules["allowed_values"])
                invalid_values = set(column_data.unique()) - allowed_values
                if invalid_values:
                    result.add_error(
                        f"Column '{column}' contains invalid values: {invalid_values}"
                    )
        
        return result
    
    def _perform_custom_validations(
        self,
        data: Union[pd.DataFrame, pl.DataFrame],
        schema: DataSchema,
        result: ValidationResult
    ) -> None:
        """Perform additional custom validations."""
        
        # Convert to pandas for consistency
        if isinstance(data, pl.DataFrame):
            df = data.to_pandas()
        else:
            df = data
        
        # Check if all schema columns exist in data
        schema_columns = set(schema.get_column_names())
        data_columns = set(df.columns)
        
        missing_columns = schema_columns - data_columns
        if missing_columns:
            for col in missing_columns:
                result.add_error(f"Required column '{col}' is missing from data")
        
        extra_columns = data_columns - schema_columns
        if extra_columns:
            for col in extra_columns:
                if self.strict_mode:
                    result.add_error(f"Unexpected column '{col}' found in data")
                else:
                    result.add_warning(f"Extra column '{col}' found in data")
        
        # Validate primary key constraints
        if schema.primary_key:
            pk_columns = [col for col in schema.primary_key if col in df.columns]
            if pk_columns:
                # Check for null values in primary key columns
                for col in pk_columns:
                    null_count = df[col].isnull().sum()
                    if null_count > 0:
                        result.add_error(f"Primary key column '{col}' contains {null_count} null values")
                
                # Check for duplicate primary key combinations
                if len(pk_columns) > 1:
                    duplicate_count = df[pk_columns].duplicated().sum()
                    if duplicate_count > 0:
                        result.add_error(f"Primary key has {duplicate_count} duplicate combinations")
                else:
                    duplicate_count = df[pk_columns[0]].duplicated().sum()
                    if duplicate_count > 0:
                        result.add_error(f"Primary key column '{pk_columns[0]}' has {duplicate_count} duplicates")


def validate_dataframe(
    data: Union[pd.DataFrame, pl.DataFrame],
    schema: Optional[DataSchema] = None,
    quality_checks: Optional[Dict[str, Any]] = None,
    strict_mode: Optional[bool] = None
) -> ValidationResult:
    """Convenience function to validate a DataFrame.
    
    Args:
        data: DataFrame to validate
        schema: Optional schema for validation
        quality_checks: Optional quality checks to perform
        strict_mode: Whether to use strict validation
        
    Returns:
        Validation result
    """
    validator = DataValidator(strict_mode=strict_mode)
    
    if schema:
        return validator.validate_with_schema(data, schema)
    else:
        return validator.validate_data_quality(data, quality_checks)