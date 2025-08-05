# Getting Started with DataScience Analytics Platform

Welcome to the DataScience Analytics Platform! This guide will help you get up and running quickly with our powerful ETL pipeline engine built on Polars for high-performance data processing.

## Overview

The DataScience Analytics Platform is a comprehensive solution for:
- **ETL Operations**: Extract, Transform, and Load data from various sources
- **Data Validation**: Ensure data quality and schema compliance
- **Data Analytics**: Perform analysis and generate insights
- **Schema Management**: Define and manage data schemas

## Prerequisites

Before installing the DataScience Analytics Platform, ensure you have:

- **Python 3.9 or higher** (Python 3.11+ recommended for optimal performance)
- **pip** or **poetry** package manager
- **Git** (for cloning the repository)
- At least **4GB RAM** for processing large datasets
- **50MB** of free disk space for installation

## Installation

### Option 1: Using Poetry (Recommended)

Poetry provides better dependency management and virtual environment handling:

```bash
# Clone the repository
git clone <repository-url>
cd ds-package

# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies and create virtual environment
poetry install

# Activate the virtual environment
poetry shell
```

### Option 2: Using pip

```bash
# Clone the repository
git clone <repository-url>
cd ds-package

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Verify Installation

Test your installation by running:

```bash
# Check the CLI is working
datascience-platform --help

# Check version and system info
datascience-platform info
```

You should see the platform version and system information displayed.

## Quick Start Guide

### 1. Basic Data Reading

Let's start by reading a CSV file and exploring its structure:

```python
from datascience_platform.etl import DataReader

# Initialize the data reader
reader = DataReader()

# Read a CSV file (replace with your file path)
df = reader.read("path/to/your/data.csv")

# Display basic information
print(f"Data shape: {df.shape}")
print(f"Columns: {df.columns}")
print(f"Data types: {df.dtypes}")

# Show first few rows
print(df.head())
```

### 2. Schema Detection and Validation

Automatically detect the schema of your data and validate its quality:

```python
from datascience_platform.etl import SchemaDetector, DataValidator

# Detect schema automatically
detector = SchemaDetector()
schema = detector.detect_schema(df)

# Explore the detected schema
print(f"Schema name: {schema.name}")
print(f"Overall quality score: {schema.overall_quality_score:.2f}")

for column in schema.columns:
    print(f"Column: {column.name}")
    print(f"  Type: {column.dtype}")
    print(f"  Nullable: {column.nullable}")
    print(f"  Quality Score: {column.quality_score:.2f}")

# Validate data against the schema
validator = DataValidator()
validation_result = validator.validate_with_schema(df, schema)

if validation_result.is_valid:
    print("✅ Data validation passed!")
else:
    print("❌ Data validation failed:")
    for error in validation_result.errors:
        print(f"  • {error}")
```

### 3. Data Transformation and Cleaning

Clean and transform your data using built-in strategies:

```python
from datascience_platform.etl import DataTransformer

# Initialize transformer
transformer = DataTransformer()

# Apply automatic transformations based on schema
cleaned_df, transform_report = transformer.transform_dataframe(df, schema=schema)

print("Transformation Summary:")
print(f"  Original shape: {transform_report.original_shape}")
print(f"  Final shape: {transform_report.final_shape}")
print(f"  Rows removed: {transform_report.total_rows_removed}")
print(f"  Values imputed: {transform_report.total_values_imputed}")
print(f"  Success rate: {transform_report.transformation_success_rate:.2%}")

# Display cleaned data
print("\nCleaned data preview:")
print(cleaned_df.head())
```

### 4. Using the Command Line Interface

The platform provides a powerful CLI for common operations:

```bash
# Read and preview data
datascience-platform data read sales_data.csv --head 20

# Validate data quality
datascience-platform data validate sales_data.csv --output validation_report.json

# List available schemas
datascience-platform schema list

# Create a sample schema for testing
datascience-platform schema create-sample

# Show current configuration
datascience-platform config show
```

## Common Use Cases

### Use Case 1: Data Quality Assessment

Perfect for assessing the quality of new datasets:

```python
from datascience_platform.etl import DataReader, SchemaDetector, DataValidator

# Read your data
reader = DataReader()
df = reader.read("new_dataset.csv")

# Detect schema and assess quality
detector = SchemaDetector()
schema = detector.detect_schema(df)

# Generate quality report
validator = DataValidator()
report = validator.generate_quality_report(df, schema)

print(f"Overall Quality Score: {report.overall_score:.2f}")
print(f"Data Completeness: {report.completeness:.2%}")
print(f"Data Consistency: {report.consistency:.2%}")
```

### Use Case 2: Automated Data Pipeline

Set up an automated pipeline for regular data processing:

```python
from datascience_platform.etl import DataReader, DataValidator, DataTransformer
from datascience_platform.core.config import settings

def process_data_pipeline(input_file: str, output_file: str):
    """Complete data processing pipeline."""
    
    # Step 1: Read data
    reader = DataReader()
    df = reader.read(input_file)
    print(f"✅ Read {df.shape[0]} rows from {input_file}")
    
    # Step 2: Validate data
    validator = DataValidator()
    validation_result = validator.validate_dataframe(df)
    
    if not validation_result.is_valid:
        print(f"⚠️  Data validation issues found:")
        for error in validation_result.errors[:5]:  # Show first 5 errors
            print(f"   • {error}")
    
    # Step 3: Transform and clean
    transformer = DataTransformer()
    cleaned_df, report = transformer.transform_dataframe(df)
    print(f"✅ Cleaned data: {cleaned_df.shape[0]} rows remaining")
    
    # Step 4: Save processed data
    if output_file.endswith('.csv'):
        cleaned_df.write_csv(output_file)
    elif output_file.endswith('.parquet'):
        cleaned_df.write_parquet(output_file)
    
    print(f"✅ Saved processed data to {output_file}")
    return cleaned_df, report

# Use the pipeline
result_df, transform_report = process_data_pipeline(
    "raw_data.csv", 
    "processed_data.parquet"
)
```

### Use Case 3: Large File Processing

Handle large datasets efficiently with chunked processing:

```python
from datascience_platform.etl import DataReader, ReadOptions

# Configure for large file processing
options = ReadOptions(
    chunk_size=50000,  # Process 50k rows at a time
    use_polars=True,   # Use Polars for better performance
)

reader = DataReader(options)

# Process large file in chunks
total_rows = 0
chunks_processed = 0

for chunk in reader.read_chunked("large_dataset.csv"):
    # Process each chunk
    chunk_rows = chunk.shape[0]
    total_rows += chunk_rows
    chunks_processed += 1
    
    # Your processing logic here
    print(f"Processed chunk {chunks_processed}: {chunk_rows} rows")

print(f"✅ Total processed: {total_rows} rows in {chunks_processed} chunks")
```

## Configuration

### Environment Variables

Customize the platform behavior using environment variables:

```bash
# ETL Configuration
export MAX_FILE_SIZE_MB=2048
export CHUNK_SIZE_ROWS=20000
export DEFAULT_ENCODING=utf-8

# Validation Configuration
export NULL_THRESHOLD=0.3
export OUTLIER_STD_THRESHOLD=2.5

# Performance Configuration
export MAX_MEMORY_USAGE_GB=8
export ENABLE_PARALLEL_PROCESSING=true

# Logging Configuration
export LOG_LEVEL=INFO
export DEBUG=false
```

### Programmatic Configuration

```python
from datascience_platform.core.config import Settings, ETLConfig, ValidationConfig

# Create custom configuration
custom_settings = Settings(
    etl=ETLConfig(
        max_file_size_mb=1024,
        chunk_size_rows=10000,
    ),
    validation=ValidationConfig(
        null_threshold=0.2,
        outlier_std_threshold=3.0,
    ),
    debug=True
)

# Use configuration in your code
reader = DataReader(settings=custom_settings)
```

## Next Steps

Now that you're familiar with the basics:

1. **Explore the CLI Reference**: Learn about all available command-line tools
2. **Check the API Reference**: Dive deeper into the Python API
3. **Try the Examples**: Run the provided example scripts
4. **Read the Architecture Guide**: Understand how the platform works internally

## Getting Help

- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: See `docs/examples/` for practical use cases
- **CLI Help**: Run `datascience-platform --help` for command-line assistance
- **API Help**: Use Python's `help()` function on any class or method

## Troubleshooting

### Common Issues

**Memory Errors with Large Files**
```bash
# Use chunked processing
datascience-platform data read large_file.csv --chunk-size 10000
```

**Encoding Issues**
```bash
# Specify encoding explicitly
datascience-platform data read data.csv --encoding utf-8
```

**Import Errors**
```bash
# Ensure the package is properly installed
pip install -e .
# Or with poetry
poetry install
```

**Performance Issues**
```python
# Enable Polars for better performance
from datascience_platform.etl import DataReader, ReadOptions

options = ReadOptions(use_polars=True)
reader = DataReader(options)
```

For more detailed troubleshooting, see the CLI Reference guide.