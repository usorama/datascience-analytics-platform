"""
Data transformation and cleaning functionality.

This module provides comprehensive data cleaning, normalization,
and transformation capabilities with multiple strategies for
handling missing values, outliers, and data inconsistencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import polars as pl
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

from ..core.config import get_settings
from ..core.exceptions import ETLError as TransformationError
from .schema import DataType, DatasetSchema, ColumnSchema


class MissingValueStrategy(Enum):
    """Strategies for handling missing values."""
    
    DROP = "drop"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    INTERPOLATE = "interpolate"
    CONSTANT = "constant"


class NormalizationMethod(Enum):
    """Methods for normalizing numeric data."""
    
    NONE = "none"
    Z_SCORE = "z_score"
    MIN_MAX = "min_max"
    ROBUST = "robust"


class OutlierHandling(Enum):
    """Methods for handling outliers."""
    
    NONE = "none"
    REMOVE = "remove"
    CAP = "cap"
    TRANSFORM = "transform"


@dataclass
class TransformationStep:
    """Record of a single transformation step."""
    
    step_name: str
    column: Optional[str]
    operation: str
    parameters: Dict[str, Any]
    rows_affected: int = 0
    execution_time_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class TransformationReport:
    """Comprehensive report of data transformation operations."""
    
    original_shape: Tuple[int, int]
    final_shape: Tuple[int, int]
    steps: List[TransformationStep] = field(default_factory=list)
    
    # Summary statistics
    total_rows_removed: int = 0
    total_values_imputed: int = 0
    total_outliers_handled: int = 0
    columns_normalized: List[str] = field(default_factory=list)
    columns_encoded: List[str] = field(default_factory=list)
    
    # Quality metrics
    data_completeness_before: float = 1.0
    data_completeness_after: float = 1.0
    transformation_success_rate: float = 1.0
    
    # Metadata
    transformed_at: datetime = field(default_factory=datetime.now)
    total_transformation_time: float = 0.0
    
    def add_step(self, step: TransformationStep):
        """Add a transformation step to the report."""
        self.steps.append(step)
        
        # Update summary statistics
        if not step.success:
            return
        
        if "remove" in step.operation.lower() or "drop" in step.operation.lower():
            self.total_rows_removed += step.rows_affected
        elif "impute" in step.operation.lower() or "fill" in step.operation.lower():
            self.total_values_imputed += step.rows_affected
        elif "outlier" in step.operation.lower():
            self.total_outliers_handled += step.rows_affected
        elif "normalize" in step.operation.lower() and step.column:
            if step.column not in self.columns_normalized:
                self.columns_normalized.append(step.column)
        elif "encode" in step.operation.lower() and step.column:
            if step.column not in self.columns_encoded:
                self.columns_encoded.append(step.column)
    
    def calculate_success_rate(self):
        """Calculate the overall transformation success rate."""
        if not self.steps:
            self.transformation_success_rate = 1.0
            return
        
        successful_steps = sum(1 for step in self.steps if step.success)
        self.transformation_success_rate = successful_steps / len(self.steps)


class DataTransformer:
    """
    Comprehensive data transformation and cleaning engine.
    
    Features:
    - Multiple missing value handling strategies
    - Intelligent duplicate detection and removal
    - Outlier detection and handling
    - Data normalization and standardization
    - Categorical variable encoding
    - Custom transformation pipelines
    """
    
    def __init__(self):
        """Initialize the data transformer."""
        self.config = get_settings()
        self.scalers = {}  # Store fitted scalers for inverse transforms
    
    def transform_dataframe(
        self,
        df: pl.DataFrame,
        schema: Optional[DatasetSchema] = None,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Tuple[pl.DataFrame, TransformationReport]:
        """
        Apply comprehensive data transformation to a DataFrame.
        
        Args:
            df: Input DataFrame to transform
            schema: Dataset schema for guided transformations
            custom_config: Custom transformation configuration
            
        Returns:
            Tuple of (transformed_dataframe, transformation_report)
        """
        start_time = datetime.now()
        
        # Initialize report
        report = TransformationReport(
            original_shape=df.shape,
            final_shape=df.shape,  # Will be updated
        )
        
        # Calculate initial data completeness
        total_cells = len(df) * len(df.columns) if len(df.columns) > 0 else 1
        null_cells = sum(df[col].null_count() for col in df.columns)
        report.data_completeness_before = 1.0 - (null_cells / total_cells)
        
        try:
            # Apply transformation pipeline
            transformed_df = df.clone()
            
            # 1. Handle duplicate rows
            transformed_df = self._handle_duplicates(transformed_df, report)
            
            # 2. Handle missing values
            transformed_df = self._handle_missing_values(transformed_df, schema, report)
            
            # 3. Handle outliers
            transformed_df = self._handle_outliers(transformed_df, schema, report)
            
            # 4. Normalize numeric columns
            transformed_df = self._normalize_columns(transformed_df, schema, report)
            
            # 5. Encode categorical variables
            transformed_df = self._encode_categorical(transformed_df, schema, report)
            
            # Update final statistics
            report.final_shape = transformed_df.shape
            
            # Calculate final data completeness
            if len(transformed_df.columns) > 0:
                total_cells_final = len(transformed_df) * len(transformed_df.columns)
                null_cells_final = sum(transformed_df[col].null_count() for col in transformed_df.columns)
                report.data_completeness_after = 1.0 - (null_cells_final / total_cells_final)
            else:
                report.data_completeness_after = 1.0
            
            report.calculate_success_rate()
            
        except Exception as e:
            # Add error step and return original DataFrame
            error_step = TransformationStep(
                step_name="transformation_pipeline",
                column=None,
                operation="pipeline_execution",
                parameters={},
                success=False,
                error_message=str(e)
            )
            report.add_step(error_step)
            transformed_df = df
        
        # Calculate total transformation time
        end_time = datetime.now()
        report.total_transformation_time = (end_time - start_time).total_seconds()
        
        return transformed_df, report
    
    def _handle_duplicates(self, df: pl.DataFrame, report: TransformationReport) -> pl.DataFrame:
        """Handle duplicate rows based on configuration."""
        step_start = datetime.now()
        
        try:
            original_count = len(df)
            strategy = self.config.transformation.duplicate_strategy
            
            if strategy == "drop_duplicates":
                # Remove all duplicate rows, keeping only the first occurrence
                df_cleaned = df.unique()
            elif strategy == "keep_first":
                # Keep first occurrence of duplicates
                df_cleaned = df.unique(subset=df.columns, keep="first")
            elif strategy == "keep_last":
                # Keep last occurrence of duplicates
                df_cleaned = df.unique(subset=df.columns, keep="last")
            else:
                # No duplicate handling
                df_cleaned = df
            
            rows_removed = original_count - len(df_cleaned)
            
            step = TransformationStep(
                step_name="handle_duplicates",
                column=None,
                operation=f"duplicate_removal_{strategy}",
                parameters={"strategy": strategy},
                rows_affected=rows_removed,
                execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                success=True
            )
            
            report.add_step(step)
            return df_cleaned
            
        except Exception as e:
            step = TransformationStep(
                step_name="handle_duplicates",
                column=None,
                operation="duplicate_removal",
                parameters={"strategy": self.config.transformation.duplicate_strategy},
                execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                success=False,
                error_message=str(e)
            )
            report.add_step(step)
            return df
    
    def _handle_missing_values(
        self, 
        df: pl.DataFrame, 
        schema: Optional[DatasetSchema], 
        report: TransformationReport
    ) -> pl.DataFrame:
        """Handle missing values using configured strategies."""
        df_cleaned = df.clone()
        
        for col_name in df.columns:
            step_start = datetime.now()
            
            try:
                col_data = df_cleaned[col_name]
                null_count = col_data.null_count()
                
                if null_count == 0:
                    continue  # No missing values to handle
                
                # Determine strategy based on column type
                strategy = self._get_missing_value_strategy(col_name, schema)
                
                if strategy == MissingValueStrategy.DROP:
                    # Drop rows with null values in this column
                    df_cleaned = df_cleaned.drop_nulls(subset=[col_name])
                    rows_affected = null_count
                
                elif strategy == MissingValueStrategy.MEAN:
                    # Fill with mean (numeric columns only)
                    if col_data.dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]:
                        mean_val = col_data.mean()
                        df_cleaned = df_cleaned.with_columns(
                            col_data.fill_null(mean_val).alias(col_name)
                        )
                        rows_affected = null_count
                    else:
                        continue
                
                elif strategy == MissingValueStrategy.MEDIAN:
                    # Fill with median (numeric columns only)
                    if col_data.dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]:
                        median_val = col_data.median()
                        df_cleaned = df_cleaned.with_columns(
                            col_data.fill_null(median_val).alias(col_name)
                        )
                        rows_affected = null_count
                    else:
                        continue
                
                elif strategy == MissingValueStrategy.MODE:
                    # Fill with mode (most frequent value)
                    try:
                        mode_val = col_data.drop_nulls().mode().to_list()[0]
                        df_cleaned = df_cleaned.with_columns(
                            col_data.fill_null(mode_val).alias(col_name)
                        )
                        rows_affected = null_count
                    except (IndexError, Exception):
                        continue  # Skip if mode calculation fails
                
                elif strategy == MissingValueStrategy.FORWARD_FILL:
                    # Forward fill (use previous value)
                    df_cleaned = df_cleaned.with_columns(
                        col_data.forward_fill().alias(col_name)
                    )
                    rows_affected = null_count
                
                elif strategy == MissingValueStrategy.BACKWARD_FILL:
                    # Backward fill (use next value)
                    df_cleaned = df_cleaned.with_columns(
                        col_data.backward_fill().alias(col_name)
                    )
                    rows_affected = null_count
                
                elif strategy == MissingValueStrategy.INTERPOLATE:
                    # Linear interpolation (numeric columns only)
                    if col_data.dtype in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]:
                        df_cleaned = df_cleaned.with_columns(
                            col_data.interpolate().alias(col_name)
                        )
                        rows_affected = null_count
                    else:
                        continue
                
                else:
                    continue  # Unknown strategy
                
                step = TransformationStep(
                    step_name="handle_missing_values",
                    column=col_name,
                    operation=f"impute_{strategy.value}",
                    parameters={"strategy": strategy.value, "null_count": null_count},
                    rows_affected=rows_affected,
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=True
                )
                
                report.add_step(step)
                
            except Exception as e:
                step = TransformationStep(
                    step_name="handle_missing_values",
                    column=col_name,
                    operation="impute_error",
                    parameters={"strategy": "unknown"},
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=False,
                    error_message=str(e)
                )
                report.add_step(step)
        
        return df_cleaned
    
    def _handle_outliers(
        self, 
        df: pl.DataFrame, 
        schema: Optional[DatasetSchema], 
        report: TransformationReport
    ) -> pl.DataFrame:
        """Handle outliers in numeric columns."""
        df_cleaned = df.clone()
        outlier_method = OutlierHandling(self.config.transformation.outlier_handling)
        
        if outlier_method == OutlierHandling.NONE:
            return df_cleaned
        
        for col_name in df.columns:
            step_start = datetime.now()
            
            try:
                col_data = df_cleaned[col_name]
                
                # Only handle outliers in numeric columns
                if col_data.dtype not in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]:
                    continue
                
                # Detect outliers using IQR method
                outlier_indices, lower_bound, upper_bound = self._detect_outliers_iqr(col_data)
                
                if len(outlier_indices) == 0:
                    continue  # No outliers found
                
                if outlier_method == OutlierHandling.REMOVE:
                    # Remove rows with outliers
                    df_cleaned = df_cleaned.filter(~pl.arange(0, len(df_cleaned)).is_in(outlier_indices))
                    rows_affected = len(outlier_indices)
                
                elif outlier_method == OutlierHandling.CAP:
                    # Cap outliers to bounds
                    capped_data = col_data.clip(lower_bound, upper_bound)
                    df_cleaned = df_cleaned.with_columns(capped_data.alias(col_name))
                    rows_affected = len(outlier_indices)
                
                elif outlier_method == OutlierHandling.TRANSFORM:
                    # Apply log transformation to reduce outlier impact
                    if col_data.min() > 0:  # Can only log-transform positive values
                        log_data = col_data.log()
                        df_cleaned = df_cleaned.with_columns(log_data.alias(col_name))
                        rows_affected = len(outlier_indices)
                    else:
                        continue
                
                step = TransformationStep(
                    step_name="handle_outliers",
                    column=col_name,
                    operation=f"outlier_{outlier_method.value}",
                    parameters={
                        "method": outlier_method.value,
                        "outlier_count": len(outlier_indices),
                        "lower_bound": float(lower_bound),
                        "upper_bound": float(upper_bound)
                    },
                    rows_affected=rows_affected,
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=True
                )
                
                report.add_step(step)
                
            except Exception as e:
                step = TransformationStep(
                    step_name="handle_outliers",
                    column=col_name,
                    operation="outlier_error",
                    parameters={"method": outlier_method.value},
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=False,
                    error_message=str(e)
                )
                report.add_step(step)
        
        return df_cleaned
    
    def _normalize_columns(
        self, 
        df: pl.DataFrame, 
        schema: Optional[DatasetSchema], 
        report: TransformationReport
    ) -> pl.DataFrame:
        """Normalize numeric columns using configured methods."""
        df_normalized = df.clone()
        
        for col_name in df.columns:
            step_start = datetime.now()
            
            try:
                col_data = df_normalized[col_name]
                
                # Only normalize numeric columns
                if col_data.dtype not in [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.Float32, pl.Float64]:
                    continue
                
                # Get normalization method for this column type
                normalization_method = self._get_normalization_method(col_name, schema)
                
                if normalization_method == NormalizationMethod.NONE:
                    continue
                
                # Convert to numpy for sklearn processing
                non_null_mask = ~col_data.is_null()
                values = col_data.to_numpy().reshape(-1, 1)
                
                if normalization_method == NormalizationMethod.Z_SCORE:
                    scaler = StandardScaler()
                elif normalization_method == NormalizationMethod.MIN_MAX:
                    scaler = MinMaxScaler()
                elif normalization_method == NormalizationMethod.ROBUST:
                    scaler = RobustScaler()
                else:
                    continue
                
                # Fit and transform only non-null values
                if non_null_mask.sum() > 0:
                    non_null_values = values[non_null_mask.to_numpy()]
                    scaler.fit(non_null_values)
                    
                    # Transform all values (sklearn handles NaN appropriately)
                    normalized_values = scaler.transform(values).flatten()
                    
                    # Create new series with normalized values
                    normalized_series = pl.Series(col_name, normalized_values)
                    df_normalized = df_normalized.with_columns(normalized_series)
                    
                    # Store scaler for potential inverse transform
                    self.scalers[col_name] = scaler
                    
                    rows_affected = non_null_mask.sum()
                else:
                    rows_affected = 0
                
                step = TransformationStep(
                    step_name="normalize_column",
                    column=col_name,
                    operation=f"normalize_{normalization_method.value}",
                    parameters={"method": normalization_method.value},
                    rows_affected=rows_affected,
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=True
                )
                
                report.add_step(step)
                
            except Exception as e:
                step = TransformationStep(
                    step_name="normalize_column",
                    column=col_name,
                    operation="normalize_error",
                    parameters={"method": "unknown"},
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=False,
                    error_message=str(e)
                )
                report.add_step(step)
        
        return df_normalized
    
    def _encode_categorical(
        self, 
        df: pl.DataFrame, 
        schema: Optional[DatasetSchema], 
        report: TransformationReport
    ) -> pl.DataFrame:
        """Encode categorical variables."""
        df_encoded = df.clone()
        
        for col_name in df.columns:
            step_start = datetime.now()
            
            try:
                # Determine if column should be encoded
                should_encode = self._should_encode_column(col_name, schema, df_encoded[col_name])
                
                if not should_encode:
                    continue
                
                col_data = df_encoded[col_name]
                
                # Use label encoding for categorical columns
                # First get unique values (excluding nulls)
                unique_values = col_data.drop_nulls().unique().sort()
                
                if len(unique_values) == 0:
                    continue
                
                # Create mapping dictionary
                encoding_map = {val: idx for idx, val in enumerate(unique_values.to_list())}
                
                # Apply encoding
                encoded_series = col_data.map_dict(encoding_map, default=None)
                df_encoded = df_encoded.with_columns(encoded_series.alias(f"{col_name}_encoded"))
                
                # Optionally drop original column
                # df_encoded = df_encoded.drop(col_name)
                
                step = TransformationStep(
                    step_name="encode_categorical",
                    column=col_name,
                    operation="label_encoding",
                    parameters={
                        "unique_categories": len(unique_values),
                        "encoding_map": encoding_map
                    },
                    rows_affected=len(df_encoded),
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=True
                )
                
                report.add_step(step)
                
            except Exception as e:
                step = TransformationStep(
                    step_name="encode_categorical",
                    column=col_name,
                    operation="encode_error",
                    parameters={},
                    execution_time_seconds=(datetime.now() - step_start).total_seconds(),
                    success=False,
                    error_message=str(e)
                )
                report.add_step(step)
        
        return df_encoded
    
    def _get_missing_value_strategy(self, col_name: str, schema: Optional[DatasetSchema]) -> MissingValueStrategy:
        """Determine the appropriate missing value strategy for a column."""
        if schema:
            col_schema = schema.get_column(col_name)
            if col_schema:
                data_type = col_schema.data_type
                
                if data_type in [DataType.INTEGER, DataType.FLOAT, DataType.NUMERIC]:
                    strategy_name = self.config.transformation.missing_value_strategies.get("numeric", "median")
                elif data_type == DataType.CATEGORICAL:
                    strategy_name = self.config.transformation.missing_value_strategies.get("categorical", "mode")
                elif data_type in [DataType.DATETIME, DataType.DATE, DataType.TIME]:
                    strategy_name = self.config.transformation.missing_value_strategies.get("datetime", "forward_fill")
                else:
                    strategy_name = self.config.transformation.missing_value_strategies.get("text", "drop")
                
                return MissingValueStrategy(strategy_name)
        
        # Default strategy if no schema available
        return MissingValueStrategy.MEDIAN
    
    def _get_normalization_method(self, col_name: str, schema: Optional[DatasetSchema]) -> NormalizationMethod:
        """Determine the appropriate normalization method for a column."""
        if schema:
            col_schema = schema.get_column(col_name)
            if col_schema and col_schema.data_type in [DataType.INTEGER, DataType.FLOAT, DataType.NUMERIC]:
                method_name = self.config.transformation.normalization_methods.get("numeric", "z_score")
                return NormalizationMethod(method_name)
        
        return NormalizationMethod.NONE
    
    def _should_encode_column(self, col_name: str, schema: Optional[DatasetSchema], col_data: pl.Series) -> bool:
        """Determine if a column should be encoded."""
        if schema:
            col_schema = schema.get_column(col_name)
            if col_schema:
                return col_schema.data_type == DataType.CATEGORICAL
        
        # Fallback: encode if it's a string column with reasonable number of unique values
        if col_data.dtype == pl.Utf8:
            unique_count = col_data.drop_nulls().n_unique()
            return unique_count <= self.config.validation.max_categories
        
        return False
    
    def _detect_outliers_iqr(self, col_data: pl.Series) -> Tuple[List[int], float, float]:
        """Detect outliers using the IQR method."""
        try:
            non_null_data = col_data.drop_nulls()
            
            if len(non_null_data) < 4:
                return [], 0.0, 0.0
            
            q1 = non_null_data.quantile(0.25)
            q3 = non_null_data.quantile(0.75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # Find indices of outliers in original series
            outlier_mask = (col_data < lower_bound) | (col_data > upper_bound)
            outlier_indices = [i for i, is_outlier in enumerate(outlier_mask.to_list()) if is_outlier]
            
            return outlier_indices, float(lower_bound), float(upper_bound)
            
        except Exception:
            return [], 0.0, 0.0
    
    def inverse_transform_column(self, col_name: str, values: pl.Series) -> pl.Series:
        """Apply inverse transformation to a normalized column."""
        if col_name not in self.scalers:
            return values
        
        try:
            scaler = self.scalers[col_name]
            values_array = values.to_numpy().reshape(-1, 1)
            inverse_values = scaler.inverse_transform(values_array).flatten()
            return pl.Series(col_name, inverse_values)
        except Exception:
            return values