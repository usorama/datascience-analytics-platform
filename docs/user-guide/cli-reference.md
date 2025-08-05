# CLI Reference Guide

The DataScience Analytics Platform provides a comprehensive command-line interface (CLI) for data processing, validation, and management operations. This guide covers all available commands, options, and usage examples.

## Installation and Setup

The CLI is available after installing the platform:

```bash
# Install the platform
pip install -e .

# Verify CLI installation
datascience-platform --help

# Check version and system info
datascience-platform info
```

## Global Options

These options are available for all commands:

```bash
datascience-platform [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--debug` | Enable debug mode with verbose output | False |
| `--config PATH` | Path to configuration file | None |
| `--version` | Show version and exit | - |
| `--help` | Show help message and exit | - |

### Examples

```bash
# Enable debug mode
datascience-platform --debug data read sample.csv

# Use custom configuration
datascience-platform --config /path/to/config.json data validate sample.csv

# Show version information
datascience-platform --version
```

## Command Groups

The CLI is organized into logical command groups:

- **data**: Data operations (read, validate, transform)
- **schema**: Schema management operations
- **config**: Configuration management
- **info**: System information

## Data Commands

### `data read`

Read and display data from various file formats.

```bash
datascience-platform data read [OPTIONS] FILE_PATH
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--format` | Choice | File format (csv, json, parquet, xlsx, xls) | Auto-detect |
| `--output PATH` | Path | Output file path | None |
| `--head N` | Integer | Number of rows to display | 10 |
| `--use-polars` | Flag | Use Polars for data processing | True |
| `--chunk-size N` | Integer | Read data in chunks of this size | None |
| `--encoding` | String | File encoding | utf-8 |
| `--delimiter` | String | Column delimiter for CSV files | Auto-detect |

#### Examples

```bash
# Basic usage - read and preview CSV
datascience-platform data read sales_data.csv

# Read with specific format and show more rows
datascience-platform data read data.txt --format csv --head 50

# Read large file in chunks
datascience-platform data read large_dataset.csv --chunk-size 10000

# Read with specific encoding and delimiter
datascience-platform data read data.csv --encoding latin-1 --delimiter ";"

# Read and save to different format
datascience-platform data read input.csv --output output.parquet

# Read Excel file
datascience-platform data read report.xlsx --head 20

# Use pandas instead of polars
datascience-platform data read data.csv --use-polars=false
```

#### Output

The command displays:
- File information (when `--debug` is used)
- Data shape (rows × columns)
- Column names and types
- Data preview (first N rows)
- Processing information for chunked reading

```bash
$ datascience-platform data read sales_data.csv --head 5
Data shape: (1000, 8)
Columns: ['date', 'product', 'category', 'price', 'quantity', 'customer_id', 'region', 'sales_rep']

Data preview:
┌────────────┬─────────────┬──────────┬───────┬──────────┬─────────────┬──────────┬───────────┐
│ date       ┆ product     ┆ category ┆ price ┆ quantity ┆ customer_id ┆ region   ┆ sales_rep │
│ ---        ┆ ---         ┆ ---      ┆ ---   ┆ ---      ┆ ---         ┆ ---      ┆ ---       │
│ str        ┆ str         ┆ str      ┆ f64   ┆ i64      ┆ str         ┆ str      ┆ str       │
╞════════════╪═════════════╪══════════╪═══════╪══════════╪═════════════╪══════════╪═══════════╡
│ 2024-01-01 ┆ Widget A    ┆ Widgets  ┆ 29.99 ┆ 2        ┆ CUST001     ┆ North    ┆ John Doe  │
│ 2024-01-01 ┆ Gadget B    ┆ Gadgets  ┆ 49.99 ┆ 1        ┆ CUST002     ┆ South    ┆ Jane Doe  │
└────────────┴─────────────┴──────────┴───────┴──────────┴─────────────┴──────────┴───────────┘
```

### `data validate`

Validate data quality and schema compliance.

```bash
datascience-platform data validate [OPTIONS] FILE_PATH
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--schema NAME` | String | Schema name to validate against | None |
| `--output PATH` | Path | Output validation report to file | None |
| `--format` | Choice | Output format (json, text) | text |
| `--strict` | Flag | Use strict validation mode | False |
| `--sample-size N` | Integer | Validate only a sample of rows | None |

#### Examples

```bash
# Basic validation
datascience-platform data validate customer_data.csv

# Validate against specific schema
datascience-platform data validate data.csv --schema customer_schema

# Strict validation mode
datascience-platform data validate data.csv --strict

# Generate JSON report
datascience-platform data validate data.csv --output report.json --format json

# Validate sample of large dataset
datascience-platform data validate large_data.csv --sample-size 10000
```

#### Output

```bash
$ datascience-platform data validate sales_data.csv
Validating data from: sales_data.csv
Data shape: (1000, 8)
✅ Validation passed!

Warnings (2):
  • Column 'price' has 5 potential outliers (values > 3 standard deviations)
  • Column 'customer_id' has non-standard format in 3 rows
```

#### Validation Report Structure

**Text Format:**
```
Validation Report for sales_data.csv
==================================================

Status: PASSED
Rows validated: 1000
Columns validated: 8

Warnings (2):
  • Column 'price' has 5 potential outliers
  • Column 'customer_id' has non-standard format in 3 rows
```

**JSON Format:**
```json
{
  "is_valid": true,
  "rows_validated": 1000,
  "columns_validated": 8,
  "errors": [],
  "warnings": [
    "Column 'price' has 5 potential outliers",
    "Column 'customer_id' has non-standard format in 3 rows"
  ],
  "validation_details": {
    "quality_score": 0.85,
    "completeness": 0.98,
    "consistency": 0.95
  }
}
```

## Schema Commands

### `schema list`

List all registered schemas.

```bash
datascience-platform schema list
```

#### Examples

```bash
# List all schemas
datascience-platform schema list
```

#### Output

```bash
$ datascience-platform schema list
Registered schemas:
  • customer_schema (v1.0) - 12 columns
  • product_schema (v2.1) - 8 columns
  • sales_schema (v1.5) - 15 columns
```

### `schema show`

Show details of a specific schema.

```bash
datascience-platform schema show SCHEMA_NAME
```

#### Examples

```bash
# Show schema details
datascience-platform schema show customer_schema
```

#### Output

```bash
$ datascience-platform schema show customer_schema
Schema: customer_schema
Version: 1.0
Description: Customer data schema with contact information

Columns (12):
  • customer_id: str [NOT NULL, UNIQUE]
  • first_name: str [NOT NULL]
  • last_name: str [NOT NULL]
  • email: str [NOT NULL]
    Email address for customer communications
  • phone: str
    Contact phone number
  • birth_date: date
  • registration_date: datetime [NOT NULL]
  • status: str [VALUES:['active', 'inactive', 'suspended']]
  • credit_limit: float [MIN:0, MAX:50000]
  • address_line1: str
  • city: str
  • country: str [NOT NULL]

Primary Key: customer_id
Indexes: email, registration_date
```

### `schema create-sample`

Create and register a sample schema for demonstration.

```bash
datascience-platform schema create-sample
```

#### Examples

```bash
# Create sample schema
datascience-platform schema create-sample
```

#### Output

```bash
$ datascience-platform schema create-sample
✅ Sample schema 'sample_customer_data' created and registered!
Schema has 8 columns

Schema Details:
Name: sample_customer_data
Version: 1.0
Description: Sample customer data schema for demonstration

Columns (8):
  • id: int [NOT NULL, UNIQUE]
  • name: str [NOT NULL]
  • email: str [NOT NULL]
  • age: int [MIN:18, MAX:120]
  • city: str
  • country: str [NOT NULL]
  • signup_date: date [NOT NULL]
  • is_active: bool [NOT NULL]

Primary Key: id
```

## Configuration Commands

### `config show`

Show current configuration.

```bash
datascience-platform config show
```

#### Examples

```bash
# Show all configuration
datascience-platform config show
```

#### Output

```bash
$ datascience-platform config show
Current Configuration:
====================
debug: False
max_file_size_mb: 1024
chunk_size_rows: 10000
supported_formats: ['csv', 'json', 'parquet', 'xlsx', 'xls']
default_encoding: utf-8
null_threshold: 0.5
outlier_std_threshold: 3.0
max_memory_usage_gb: 4
enable_parallel_processing: True
```

### `config set`

Set a configuration value.

```bash
datascience-platform config set KEY VALUE
```

#### Examples

```bash
# Set configuration values
datascience-platform config set debug true
datascience-platform config set max_file_size_mb 2048
datascience-platform config set null_threshold 0.3
```

#### Output

```bash
$ datascience-platform config set debug true
✅ Set debug = True
Note: Configuration changes are not persistent. Use environment variables or config files for permanent changes.
```

## System Information Command

### `info`

Show platform information and system status.

```bash
datascience-platform info
```

#### Examples

```bash
# Show system information
datascience-platform info
```

#### Output

```bash
$ datascience-platform info
DataScience Analytics Platform v0.1.0
==================================================
Python version: 3.11.5 (main, Aug 24 2023, 15:09:45) [Clang 14.0.3]
Platform: macOS-13.5-arm64-arm-64bit
Pandas version: 2.1.0
Polars version: 0.20.0
Pandera version: 0.17.0

Configuration:
  Debug mode: False
  Supported formats: csv, json, parquet, xlsx, xls
  Default chunk size: 10000
  Max memory usage: 4GB
  Registered schemas: 3
    customer_schema, product_schema, sales_schema
```

## Environment Variables

Configure the platform behavior using environment variables:

### ETL Configuration

```bash
# Maximum file size for processing (MB)
export MAX_FILE_SIZE_MB=2048

# Default chunk size for reading large files
export CHUNK_SIZE_ROWS=20000

# Default file encoding
export DEFAULT_ENCODING=utf-8

# Supported file formats (comma-separated)
export SUPPORTED_FORMATS=csv,json,parquet,xlsx,xls
```

### Validation Configuration

```bash
# Threshold for null values (0.0-1.0)
export NULL_THRESHOLD=0.3

# Standard deviation threshold for outlier detection
export OUTLIER_STD_THRESHOLD=2.5

# Enable strict validation mode
export STRICT_VALIDATION=false
```

### Performance Configuration

```bash
# Maximum memory usage (GB)
export MAX_MEMORY_USAGE_GB=8

# Enable parallel processing
export ENABLE_PARALLEL_PROCESSING=true

# Number of worker processes
export MAX_WORKERS=4
```

### Logging Configuration

```bash
# Logging level (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=INFO

# Enable debug mode
export DEBUG=false

# Log file path
export LOG_FILE=/tmp/datascience_platform.log
```

## Advanced Usage Patterns

### Pipeline Operations

Chain multiple operations together:

```bash
# Read, validate, and save report
datascience-platform data read input.csv --output temp.parquet && \
datascience-platform data validate temp.parquet --output validation.json --format json
```

### Batch Processing

Process multiple files:

```bash
# Process all CSV files in a directory
for file in *.csv; do
    echo "Processing $file..."
    datascience-platform data validate "$file" --output "${file%.csv}_report.json" --format json
done
```

### Configuration Management

Use different configurations for different environments:

```bash
# Development environment
export DEBUG=true
export LOG_LEVEL=DEBUG
export MAX_FILE_SIZE_MB=512

# Production environment
export DEBUG=false
export LOG_LEVEL=INFO
export MAX_FILE_SIZE_MB=4096
```

## Troubleshooting

### Common Issues and Solutions

#### Memory Errors

```bash
# Problem: OutOfMemoryError with large files
# Solution: Use chunked processing
datascience-platform data read large_file.csv --chunk-size 5000
```

#### Encoding Issues

```bash
# Problem: UnicodeDecodeError
# Solution: Specify correct encoding
datascience-platform data read data.csv --encoding latin-1
```

#### Schema Not Found

```bash
# Problem: Schema 'my_schema' not found
# Solution: List available schemas first
datascience-platform schema list

# Or create a sample schema
datascience-platform schema create-sample
```

#### Performance Issues

```bash
# Problem: Slow processing
# Solution: Enable Polars and use appropriate chunk size
datascience-platform data read data.csv --use-polars --chunk-size 10000
```

#### File Format Issues

```bash
# Problem: Auto-detection fails
# Solution: Specify format explicitly
datascience-platform data read data.txt --format csv --delimiter "|"
```

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
# Global debug mode
datascience-platform --debug data read problematic_file.csv

# Or set environment variable
export DEBUG=true
datascience-platform data read problematic_file.csv
```

Debug mode provides:
- Detailed file information
- Processing steps and timing
- Memory usage statistics
- Full error stack traces
- Configuration details

### Logging

Configure logging for persistent troubleshooting:

```bash
# Set log level and file
export LOG_LEVEL=DEBUG
export LOG_FILE=/tmp/datascience_platform.log

# Run commands and check logs
datascience-platform data read data.csv
tail -f /tmp/datascience_platform.log
```

## Performance Tips

### Optimal Settings for Different Use Cases

#### Small Files (< 100MB)
```bash
# Use default settings
datascience-platform data read small_file.csv
```

#### Medium Files (100MB - 1GB)
```bash
# Use moderate chunk size
datascience-platform data read medium_file.csv --chunk-size 20000
```

#### Large Files (> 1GB)
```bash
# Use large chunks and Polars
datascience-platform data read large_file.csv --chunk-size 50000 --use-polars
```

#### Memory-Constrained Environments
```bash
# Use small chunks
export MAX_MEMORY_USAGE_GB=2
datascience-platform data read data.csv --chunk-size 5000
```

#### High-Performance Environments
```bash
# Maximize performance
export MAX_MEMORY_USAGE_GB=16
export ENABLE_PARALLEL_PROCESSING=true
datascience-platform data read data.csv --chunk-size 100000 --use-polars
```

## Integration Examples

### Shell Scripts

Create reusable scripts for common tasks:

```bash
#!/bin/bash
# data_pipeline.sh - Complete data processing pipeline

INPUT_FILE=$1
OUTPUT_DIR=$2

echo "Processing $INPUT_FILE..."

# Step 1: Validate input
datascience-platform data validate "$INPUT_FILE" \
    --output "$OUTPUT_DIR/validation_report.json" \
    --format json

# Step 2: Process data
datascience-platform data read "$INPUT_FILE" \
    --output "$OUTPUT_DIR/processed_data.parquet" \
    --use-polars

echo "Pipeline complete. Results in $OUTPUT_DIR"
```

### Makefile Integration

```makefile
# Makefile for data processing tasks

DATA_DIR = data
OUTPUT_DIR = output

.PHONY: validate process info

validate:
	@for file in $(DATA_DIR)/*.csv; do \
		echo "Validating $$file..."; \
		datascience-platform data validate "$$file" \
			--output "$(OUTPUT_DIR)/$$(basename $$file .csv)_validation.json" \
			--format json; \
	done

process:
	@for file in $(DATA_DIR)/*.csv; do \
		echo "Processing $$file..."; \
		datascience-platform data read "$$file" \
			--output "$(OUTPUT_DIR)/$$(basename $$file .csv).parquet"; \
	done

info:
	datascience-platform info

clean:
	rm -rf $(OUTPUT_DIR)/*
```

This CLI reference guide provides comprehensive coverage of all available commands, options, and usage patterns. For Python API usage, see the API Reference guide.