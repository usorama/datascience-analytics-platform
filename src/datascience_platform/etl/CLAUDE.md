# ETL Module - Production Data Pipeline

The ETL (Extract, Transform, Load) module provides enterprise-grade data processing capabilities for the DataScience Platform. Built for production workloads with comprehensive validation, transformation, and quality assurance features.

## Overview

The ETL module delivers a complete data processing pipeline with:
- **Multi-format data ingestion** (CSV, JSON, Excel, Parquet)
- **Intelligent data transformations** with multiple strategies
- **Comprehensive validation** using schema-driven quality checks
- **Production-ready scalability** with chunked processing and memory optimization
- **Full audit trails** with detailed transformation reporting

## Key Components

### 📖 reader.py - Universal Data Reader
Multi-format data reader supporting production-scale ingestion:

```python
from datascience_platform.etl import DataReader, ReadOptions

# Configure for large files with chunked processing
options = ReadOptions(
    chunk_size=10000,     # Process in 10K row chunks
    use_polars=True,      # Use Polars for performance
    encoding="utf-8",
    max_rows=1000000      # Limit for testing
)

reader = DataReader(options)
df = reader.read("data/large_dataset.csv")

# Get file metadata before processing
file_info = reader.get_file_info("data/sales_data.parquet")
print(f"File size: {file_info['size_mb']} MB, Rows: {file_info.get('estimated_rows')}")
```

**Key Features:**
- Auto-detects file format from extension
- Chunked reading for memory-efficient processing of large files
- Polars/Pandas interoperability with performance optimization
- Comprehensive file metadata extraction
- Graceful error handling with detailed error context

### 🔧 transformer.py - Advanced Data Transformation
Comprehensive data cleaning and transformation engine:

```python
from datascience_platform.etl import DataTransformer
import polars as pl

transformer = DataTransformer()
df = pl.read_csv("raw_data.csv")

# Apply full transformation pipeline
cleaned_df, report = transformer.transform_dataframe(df, schema)

print(f"Data completeness improved: {report.data_completeness_before:.2%} → {report.data_completeness_after:.2%}")
print(f"Rows processed: {report.original_shape[0]:,}")
print(f"Values imputed: {report.total_values_imputed:,}")
print(f"Outliers handled: {report.total_outliers_handled:,}")
```

**Transformation Strategies:**

1. **Missing Value Handling:**
   - `DROP` - Remove rows with missing values
   - `MEAN/MEDIAN/MODE` - Statistical imputation
   - `FORWARD_FILL/BACKWARD_FILL` - Time-series propagation
   - `INTERPOLATE` - Linear interpolation for numeric data
   - `CONSTANT` - Fill with specified value

2. **Outlier Detection & Handling:**
   - `IQR Method` - Interquartile range outlier detection
   - `REMOVE` - Drop outlier rows
   - `CAP` - Cap to statistical bounds
   - `TRANSFORM` - Log transformation for distribution normalization

3. **Data Normalization:**
   - `Z_SCORE` - Standard score normalization
   - `MIN_MAX` - 0-1 range scaling
   - `ROBUST` - Robust scaling (median/IQR based)

4. **Categorical Encoding:**
   - Label encoding for categorical variables
   - Intelligent type detection and conversion

### ✅ validator.py - Data Quality Assurance
Production-grade validation with comprehensive quality checks:

```python
from datascience_platform.etl import DataValidator, validate_dataframe

# Quick quality assessment
result = validate_dataframe(df, quality_checks={
    "missing_threshold": 0.3,        # Flag columns with >30% missing
    "duplicate_threshold": 0.05,     # Flag if >5% duplicates
    "check_outliers": True
})

print(f"Validation {'PASSED' if result.is_valid else 'FAILED'}")
print(f"Errors: {len(result.errors)}, Warnings: {len(result.warnings)}")

# Schema-based validation
validator = DataValidator(strict_mode=True)
result = validator.validate_with_schema(df, user_schema)
```

**Quality Checks:**
- **Duplicate Detection** - Configurable thresholds and strategies
- **Missing Value Analysis** - Per-column completeness assessment
- **Data Type Validation** - Type consistency and appropriateness
- **Outlier Detection** - Statistical outlier identification
- **Schema Compliance** - Structure and constraint validation
- **Primary Key Integrity** - Uniqueness and null constraints

### 📋 schema.py - Schema-Driven Data Modeling
Comprehensive schema definition and validation framework:

```python
from datascience_platform.etl import DataSchema, ColumnSchema

# Define production schema
user_schema = DataSchema(
    name="user_analytics",
    version="2.1.0",
    columns=[
        ColumnSchema(
            name="user_id",
            dtype="int64",
            nullable=False,
            unique=True,
            min_value=1
        ),
        ColumnSchema(
            name="revenue",
            dtype="float64",
            nullable=True,
            min_value=0.0,
            max_value=1000000.0
        ),
        ColumnSchema(
            name="status",
            dtype="category",
            allowed_values=["active", "churned", "trial"]
        )
    ],
    primary_key=["user_id"],
    indexes=["status", "signup_date"]
)

# Validate against schema
pandera_schema = user_schema.to_pandera_schema()
validated_df = pandera_schema.validate(df)
```

## Supported Data Formats

### Input Formats
- **CSV** - Delimiter detection, encoding handling, chunked reading
- **JSON** - Nested structure flattening, array processing
- **Excel** - Multi-sheet support, formula evaluation
- **Parquet** - Columnar format with metadata preservation

### Performance Characteristics
- **CSV**: Up to 1M+ rows/minute with chunked processing
- **Parquet**: Native columnar efficiency with metadata
- **JSON**: Automatic schema inference and normalization
- **Excel**: Sheet-aware processing with type detection

## Data Validation Features

### Schema Validation
- **Structure Compliance** - Column presence and naming
- **Type Safety** - Data type validation and coercion
- **Constraint Enforcement** - Range, uniqueness, pattern matching
- **Primary Key Integrity** - Multi-column key validation
- **Foreign Key Relationships** - Cross-table referential integrity

### Quality Assessment
- **Completeness Scoring** - Missing value analysis
- **Consistency Checks** - Data distribution analysis
- **Accuracy Validation** - Pattern and format verification
- **Timeliness Assessment** - Date range and sequence validation

## Production Usage Patterns

### High-Volume Data Processing
```python
# Process 100M+ row datasets efficiently
options = ReadOptions(
    chunk_size=50000,
    use_polars=True,
    max_rows=None  # Process full dataset
)

reader = DataReader(options)
transformer = DataTransformer()

# Stream processing for memory efficiency
for chunk in reader.read_chunked("massive_dataset.csv"):
    cleaned_chunk, report = transformer.transform_dataframe(chunk)
    # Process or save cleaned chunk
    save_processed_chunk(cleaned_chunk)
```

### Real-Time Data Validation
```python
# API endpoint data validation
@app.post("/api/data/validate")
async def validate_incoming_data(data: dict):
    df = pl.DataFrame(data)
    result = validate_dataframe(df, schema=api_schema)
    
    if not result.is_valid:
        raise HTTPException(400, detail={
            "errors": result.errors,
            "warnings": result.warnings
        })
    
    return {"status": "valid", "rows": len(df)}
```

### Data Pipeline Integration
```python
# Full ETL pipeline with monitoring
def process_data_pipeline(input_file: str, output_file: str):
    # Extract
    reader = DataReader()
    df = reader.read(input_file)
    
    # Transform with full reporting
    transformer = DataTransformer()
    cleaned_df, transform_report = transformer.transform_dataframe(df)
    
    # Validate before load
    validator = DataValidator()
    validation_result = validator.validate_data_quality(cleaned_df)
    
    if validation_result.is_valid:
        # Load to destination
        cleaned_df.write_parquet(output_file)
        
        # Generate pipeline report
        return {
            "status": "success",
            "input_rows": df.shape[0],
            "output_rows": cleaned_df.shape[0],
            "data_quality_score": validation_result.data_completeness_after,
            "transformation_time": transform_report.total_transformation_time
        }
    else:
        raise DataPipelineError("Validation failed", validation_result.errors)
```

## Integration with Other Modules

### ML Pipeline Integration
- **Feature Engineering**: Automated feature preparation for ML models
- **Data Splitting**: Train/validation/test set creation with stratification
- **Pipeline Compatibility**: Direct integration with scikit-learn pipelines

### Dashboard Generation
- **Schema Export**: Automatic TypeScript type generation
- **Metadata Extraction**: Column statistics for visualization
- **Quality Metrics**: Data quality dashboards and alerts

### NLP Processing
- **Text Preprocessing**: Automated text cleaning and normalization
- **Embedding Preparation**: Format data for vector embedding
- **Domain Adaptation**: Specialized transformations for NLP workloads

## Performance Optimization

### Memory Management
- **Chunked Processing** - Configurable batch sizes for large datasets
- **Lazy Evaluation** - Polars lazy evaluation for memory efficiency
- **Streaming Support** - Process data without loading entire files

### Compute Optimization
- **Vectorized Operations** - NumPy/Polars vectorization
- **Parallel Processing** - Multi-core transformation operations
- **Caching Strategy** - Intelligent caching of transformation results

## Error Handling & Monitoring

### Comprehensive Error Context
- **File-Level Errors** - Path, format, and access issues
- **Data-Level Errors** - Validation failures with row/column context
- **Transform Errors** - Operation failures with recovery strategies
- **Quality Errors** - Data quality issues with severity levels

### Production Monitoring
- **Transformation Metrics** - Processing time, success rates
- **Data Quality Dashboards** - Real-time quality monitoring
- **Alert Systems** - Threshold-based quality alerts
- **Audit Trails** - Complete transformation history

## Links to Documentation

- **Main Documentation**: `/Users/umasankrudhya/Projects/ds-package/IMPLEMENTATION_SUMMARY.md`
- **API Reference**: `/Users/umasankrudhya/Projects/ds-package/docs/`
- **Example Usage**: `/Users/umasankrudhya/Projects/ds-package/examples/`
- **Test Suite**: `/Users/umasankrudhya/Projects/ds-package/tests/unit/etl/`

## Quick Start Commands

```bash
# Install with ETL dependencies
pip install -e ".[full]"

# Test ETL pipeline
python3 -c "from datascience_platform.etl import DataReader; print('ETL module ready')"

# Run comprehensive ETL tests  
python3 -m pytest tests/unit/etl/ -v --cov=src/datascience_platform/etl

# Process sample data
./dsplatform data read examples/sample_data.csv
./dsplatform data validate examples/sample_data.csv
```

The ETL module provides the foundation for all data processing operations in the DataScience Platform, ensuring data quality, transformation consistency, and production scalability across all workflows.