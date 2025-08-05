"""Data schema definitions and validation for the DataScience Analytics Platform."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union

import pandera as pa
from pydantic import BaseModel, Field, field_validator


class BaseSchema(BaseModel):
    """Base schema class for data validation."""
    
    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        validate_assignment = True


class ColumnSchema(BaseSchema):
    """Schema definition for a single column."""
    
    name: str = Field(..., description="Column name")
    dtype: str = Field(..., description="Data type (pandas/polars compatible)")
    nullable: bool = Field(default=True, description="Whether column can contain null values")
    unique: bool = Field(default=False, description="Whether column values must be unique")
    min_value: Optional[Union[int, float]] = Field(default=None, description="Minimum allowed value")
    max_value: Optional[Union[int, float]] = Field(default=None, description="Maximum allowed value")
    allowed_values: Optional[List[Any]] = Field(default=None, description="List of allowed values")
    regex_pattern: Optional[str] = Field(default=None, description="Regex pattern for string validation")
    description: Optional[str] = Field(default=None, description="Column description")
    
    @field_validator("dtype")
    @classmethod
    def validate_dtype(cls, v: str) -> str:
        """Validate data type."""
        valid_types = {
            "int", "int8", "int16", "int32", "int64",
            "uint8", "uint16", "uint32", "uint64",
            "float", "float32", "float64",
            "bool", "boolean",
            "str", "string", "object",
            "datetime", "datetime64", "date",
            "category"
        }
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid dtype '{v}'. Must be one of {valid_types}")
        return v.lower()


class DataSchema(BaseSchema):
    """Schema definition for a complete dataset."""
    
    name: str = Field(..., description="Schema name")
    version: str = Field(default="1.0.0", description="Schema version")
    description: Optional[str] = Field(default=None, description="Schema description")
    columns: List[ColumnSchema] = Field(..., description="List of column schemas")
    primary_key: Optional[List[str]] = Field(default=None, description="Primary key columns")
    foreign_keys: Optional[Dict[str, str]] = Field(default=None, description="Foreign key relationships")
    indexes: Optional[List[str]] = Field(default=None, description="Columns to index")
    constraints: Optional[List[str]] = Field(default=None, description="Additional constraints")
    
    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v: List[ColumnSchema]) -> List[ColumnSchema]:
        """Validate column definitions."""
        if not v:
            raise ValueError("Schema must have at least one column")
        
        # Check for duplicate column names
        column_names = [col.name for col in v]
        if len(column_names) != len(set(column_names)):
            raise ValueError("Column names must be unique")
        
        return v
    
    @field_validator("primary_key")
    @classmethod
    def validate_primary_key(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Validate primary key columns exist."""
        if v and hasattr(info.data, 'columns') and info.data['columns']:
            column_names = {col.name for col in info.data['columns']}
            for pk_col in v:
                if pk_col not in column_names:
                    raise ValueError(f"Primary key column '{pk_col}' not found in schema")
        return v
    
    def get_column_schema(self, column_name: str) -> Optional[ColumnSchema]:
        """Get schema for a specific column."""
        for col in self.columns:
            if col.name == column_name:
                return col
        return None
    
    def get_column_names(self) -> List[str]:
        """Get list of all column names."""
        return [col.name for col in self.columns]
    
    def to_pandera_schema(self) -> pa.DataFrameSchema:
        """Convert to Pandera schema for validation."""
        columns = {}
        
        for col in self.columns:
            # Map our dtype to pandas/pandera dtype
            dtype_mapping = {
                "int": "int64",
                "int8": "int8",
                "int16": "int16", 
                "int32": "int32",
                "int64": "int64",
                "uint8": "uint8",
                "uint16": "uint16",
                "uint32": "uint32",
                "uint64": "uint64",
                "float": "float64",
                "float32": "float32",
                "float64": "float64",
                "bool": "bool",
                "boolean": "bool",
                "str": "object",
                "string": "object",
                "object": "object",
                "datetime": "datetime64[ns]",
                "datetime64": "datetime64[ns]",
                "date": "datetime64[ns]",
                "category": "category"
            }
            
            pandera_dtype = dtype_mapping.get(col.dtype, col.dtype)
            
            # Build column checks
            checks = []
            
            if col.min_value is not None:
                checks.append(pa.Check.greater_than_or_equal_to(col.min_value))
            
            if col.max_value is not None:
                checks.append(pa.Check.less_than_or_equal_to(col.max_value))
            
            if col.allowed_values is not None:
                checks.append(pa.Check.isin(col.allowed_values))
            
            if col.regex_pattern is not None:
                checks.append(pa.Check.str_matches(col.regex_pattern))
            
            if col.unique:
                checks.append(pa.Check.unique())
            
            columns[col.name] = pa.Column(
                dtype=pandera_dtype,
                nullable=col.nullable,
                checks=checks,
                description=col.description
            )
        
        return pa.DataFrameSchema(
            columns=columns,
            name=self.name,
            description=self.description
        )


class SchemaRegistry:
    """Registry for managing data schemas."""
    
    def __init__(self) -> None:
        """Initialize schema registry."""
        self._schemas: Dict[str, DataSchema] = {}
    
    def register_schema(self, schema: DataSchema) -> None:
        """Register a new schema."""
        self._schemas[schema.name] = schema
    
    def get_schema(self, name: str) -> Optional[DataSchema]:
        """Get schema by name."""
        return self._schemas.get(name)
    
    def list_schemas(self) -> List[str]:
        """List all registered schema names."""
        return list(self._schemas.keys())
    
    def remove_schema(self, name: str) -> bool:
        """Remove schema from registry."""
        if name in self._schemas:
            del self._schemas[name]
            return True
        return False


# Global schema registry instance
schema_registry = SchemaRegistry()


def create_sample_schema() -> DataSchema:
    """Create a sample schema for demonstration purposes."""
    columns = [
        ColumnSchema(
            name="id",
            dtype="int64",
            nullable=False,
            unique=True,
            min_value=1,
            description="Unique identifier"
        ),
        ColumnSchema(
            name="name",
            dtype="string",
            nullable=False,
            description="Name field"
        ),
        ColumnSchema(
            name="age",
            dtype="int32",
            nullable=True,
            min_value=0,
            max_value=150,
            description="Age in years"
        ),
        ColumnSchema(
            name="email",
            dtype="string",
            nullable=True,
            regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            description="Email address"
        ),
        ColumnSchema(
            name="status",
            dtype="category",
            nullable=False,
            allowed_values=["active", "inactive", "pending"],
            description="Account status"
        ),
        ColumnSchema(
            name="created_at",
            dtype="datetime64",
            nullable=False,
            description="Record creation timestamp"
        ),
        ColumnSchema(
            name="score",
            dtype="float64",
            nullable=True,
            min_value=0.0,
            max_value=100.0,
            description="Performance score"
        )
    ]
    
    return DataSchema(
        name="sample_user_data",
        version="1.0.0",
        description="Sample user data schema for demonstration",
        columns=columns,
        primary_key=["id"],
        indexes=["email", "status"]
    )