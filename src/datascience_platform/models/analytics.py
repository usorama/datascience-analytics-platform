"""Pydantic models for analytics API requests and responses."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class AnalysisRequest(BaseModel):
    """Request model for starting an analytics pipeline."""
    
    # Data source configuration
    data_source: str = Field(
        ..., 
        description="Path to data file or uploaded file ID",
        example="data/sales_data.csv"
    )
    data_format: Optional[str] = Field(
        None,
        description="Data format (auto-detected if not provided)",
        example="csv"
    )
    read_options: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional data reading options",
        example={"encoding": "utf-8", "delimiter": ","}
    )
    
    # Analysis configuration
    target_column: Optional[str] = Field(
        None,
        description="Target column for ML analysis",
        example="revenue"
    )
    time_column: Optional[str] = Field(
        None,
        description="Time column for time series analysis",
        example="date"
    )
    business_context: Optional[str] = Field(
        None,
        description="Business context for relevant insights",
        example="sales"
    )
    
    # Processing options
    validate_data: bool = Field(
        True,
        description="Perform data validation"
    )
    strict_validation: bool = Field(
        False,
        description="Use strict validation mode"
    )
    sample_size: Optional[int] = Field(
        None,
        description="Sample size for analysis (None for full dataset)",
        example=10000
    )
    
    # ML configuration
    ml_enabled: bool = Field(
        True,
        description="Enable ML analysis"
    )
    ml_time_limit: int = Field(
        120,
        description="Time limit for ML training (seconds)",
        ge=30,
        le=3600
    )
    
    # Dashboard configuration
    generate_dashboard: bool = Field(
        True,
        description="Generate interactive dashboard"
    )
    dashboard_theme: str = Field(
        "light",
        description="Dashboard theme",
        pattern="^(light|dark)$"
    )
    dashboard_title: Optional[str] = Field(
        None,
        description="Custom dashboard title",
        example="Sales Analytics Dashboard"
    )
    
    # Output configuration
    save_intermediate: bool = Field(
        False,
        description="Save intermediate processing results"
    )
    export_formats: List[str] = Field(
        ["html"],
        description="Export formats for dashboard",
        example=["html", "pdf"]
    )
    
    @validator("sample_size")
    def validate_sample_size(cls, v):
        """Validate sample size is positive."""
        if v is not None and v <= 0:
            raise ValueError("sample_size must be positive")
        return v
    
    @validator("export_formats")
    def validate_export_formats(cls, v):
        """Validate export formats."""
        valid_formats = ["html", "pdf", "png", "svg"]
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid export format: {fmt}. Valid formats: {valid_formats}")
        return v
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "data_source": "sales_data.csv",
                "data_format": "csv",
                "target_column": "revenue",
                "time_column": "date",
                "business_context": "sales",
                "validate_data": True,
                "ml_enabled": True,
                "generate_dashboard": True,
                "dashboard_theme": "light",
                "dashboard_title": "Sales Analytics Dashboard"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis pipeline creation."""
    
    pipeline_id: str = Field(
        ...,
        description="Unique identifier for the analytics pipeline",
        example="12345678-1234-1234-1234-123456789012"
    )
    status: str = Field(
        ...,
        description="Current pipeline status",
        example="running"
    )
    message: str = Field(
        ...,
        description="Status message",
        example="Analytics pipeline started successfully"
    )
    start_timestamp: str = Field(
        ...,
        description="Pipeline start timestamp (ISO format)",
        example="2024-01-15T10:30:00Z"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None,
        description="Estimated completion time in minutes",
        example=5
    )
    output_directory: str = Field(
        ...,
        description="Directory where results will be saved",
        example="/output/12345678-1234-1234-1234-123456789012"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "pipeline_id": "12345678-1234-1234-1234-123456789012",
                "status": "running",
                "message": "Analytics pipeline started successfully",
                "start_timestamp": "2024-01-15T10:30:00Z",
                "estimated_duration_minutes": 5,
                "output_directory": "/output/12345678-1234-1234-1234-123456789012"
            }
        }


class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status."""
    
    pipeline_id: str = Field(
        ...,
        description="Unique identifier for the analytics pipeline",
        example="12345678-1234-1234-1234-123456789012"
    )
    status: str = Field(
        ...,
        description="Current pipeline status",
        example="running"
    )
    progress: Dict[str, Any] = Field(
        ...,
        description="Detailed progress information",
        example={
            "current_stage": "analysis",
            "overall_progress": 65.0,
            "stage_progress": {
                "initialization": 100.0,
                "data_loading": 100.0,
                "analysis": 30.0
            },
            "elapsed_time": 120.5
        }
    )
    message: str = Field(
        ...,
        description="Current status message",
        example="Running comprehensive data analysis"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "pipeline_id": "12345678-1234-1234-1234-123456789012",
                "status": "running",
                "progress": {
                    "current_stage": "analysis",
                    "overall_progress": 65.0,
                    "stage_progress": {
                        "initialization": 100.0,
                        "data_loading": 100.0,
                        "analysis": 30.0
                    },
                    "elapsed_time": 120.5
                },
                "message": "Running comprehensive data analysis"
            }
        }


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    
    file_id: str = Field(
        ...,
        description="Unique identifier for the uploaded file",
        example="abc123def456_data.csv"
    )
    filename: str = Field(
        ...,
        description="Original filename",
        example="data.csv"
    )
    file_path: str = Field(
        ...,
        description="Server path to the uploaded file",
        example="/uploads/abc123def456_data.csv"
    )
    file_size: int = Field(
        ...,
        description="File size in bytes",
        example=1024000
    )
    file_type: str = Field(
        ...,
        description="File extension/type",
        example=".csv"
    )
    upload_timestamp: str = Field(
        ...,
        description="Upload timestamp (ISO format)",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "file_id": "abc123def456_data.csv",
                "filename": "data.csv",
                "file_path": "/uploads/abc123def456_data.csv",
                "file_size": 1024000,
                "file_type": ".csv",
                "upload_timestamp": "2024-01-15T10:30:00Z"
            }
        }


class PipelineListItem(BaseModel):
    """Model for pipeline list item."""
    
    pipeline_id: str = Field(
        ...,
        description="Unique identifier for the pipeline"
    )
    status: str = Field(
        ...,
        description="Current pipeline status"
    )
    progress: float = Field(
        ...,
        description="Progress percentage (0-100)",
        ge=0.0,
        le=100.0
    )
    data_source: Optional[str] = Field(
        None,
        description="Original data source"
    )
    start_time: Optional[str] = Field(
        None,
        description="Pipeline start time (ISO format)"
    )
    end_time: Optional[str] = Field(
        None,
        description="Pipeline end time (ISO format)"
    )
    type: str = Field(
        ...,
        description="Pipeline type (active/completed)",
        pattern="^(active|completed)$"
    )


class PipelineListResponse(BaseModel):
    """Response model for pipeline list."""
    
    pipelines: List[PipelineListItem] = Field(
        ...,
        description="List of pipelines"
    )
    total_count: int = Field(
        ...,
        description="Total number of pipelines",
        ge=0
    )
    active_count: int = Field(
        ...,
        description="Number of active pipelines",
        ge=0
    )
    completed_count: int = Field(
        ...,
        description="Number of completed pipelines",
        ge=0
    )


class ConfigurationResponse(BaseModel):
    """Response model for platform configuration."""
    
    app_name: str = Field(
        ...,
        description="Application name"
    )
    app_version: str = Field(
        ...,
        description="Application version"
    )
    supported_formats: List[str] = Field(
        ...,
        description="Supported file formats"
    )
    api_host: str = Field(
        ...,
        description="API host"
    )
    api_port: int = Field(
        ...,
        description="API port"
    )
    max_memory_usage_gb: float = Field(
        ...,
        description="Maximum memory usage in GB"
    )
    ml_random_seed: int = Field(
        ...,
        description="Random seed for ML operations"
    )
    upload_directory: str = Field(
        ...,
        description="Upload directory path"
    )
    output_directory: str = Field(
        ...,
        description="Output directory path"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    error: str = Field(
        ...,
        description="Error type or code",
        example="ValidationError"
    )
    message: str = Field(
        ...,
        description="Detailed error message",
        example="Invalid data format specified"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    timestamp: str = Field(
        ...,
        description="Error timestamp (ISO format)",
        example="2024-01-15T10:30:00Z"
    )
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid data format specified",
                "details": {
                    "field": "data_format",
                    "value": "invalid_format"
                },
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
