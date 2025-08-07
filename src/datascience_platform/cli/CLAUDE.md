# CLI Module Documentation

This file provides comprehensive guidance for the DataScience Platform's Command-Line Interface (CLI) module.

## Overview

The CLI module (`src/datascience_platform/cli/`) provides a production-ready command-line interface for all DataScience Platform operations. Built with Click framework, it offers comprehensive data operations, validation, schema management, and configuration capabilities with full error handling and debug modes.

## Key Components

### 1. `commands.py` - Main CLI Commands
**Location**: `/Users/umasankrudhya/Projects/ds-package/src/datascience_platform/cli/commands.py`

The core CLI implementation featuring:
- **Click-based Architecture**: Professional CLI framework with proper argument parsing
- **Command Groups**: Organized command structure (`data`, `schema`, `config`)
- **Error Handling**: Comprehensive exception handling with debug mode support
- **Multiple Entry Points**: Three distinct CLI interfaces for different use cases
- **Integration Layer**: Seamless integration with all platform modules

### 2. `__init__.py` - Module Interface
**Location**: `/Users/umasankrudhya/Projects/ds-package/src/datascience_platform/cli/__init__.py`

Exports the main CLI interface for programmatic access and module importing.

## Production CLI Interfaces

### Primary Interface: `dsplatform`
**Entry Point**: `datascience_platform.cli.commands:main`
**Script**: `./dsplatform` (root directory executable)

Full-featured CLI with all commands and options:
```bash
./dsplatform --help                    # Show all available commands
./dsplatform --debug                   # Enable debug mode
./dsplatform --config config.yaml     # Use custom configuration
```

### Quick Analysis: `ds-analyze`  
**Entry Point**: `datascience_platform.cli.commands:analyze`
**Script**: `./ds-analyze` (root directory executable)

Direct data analysis interface:
```bash
./ds-analyze data.csv                  # Quick data analysis
./ds-analyze data.csv --head 20        # Show first 20 rows
./ds-analyze data.csv --use-polars     # Use Polars engine
```

### Dashboard Generation: `ds-dashboard`
**Entry Point**: `datascience_platform.cli.commands:dashboard`
**Script**: `./ds-dashboard` (root directory executable)

Direct dashboard generation:
```bash
./ds-dashboard data.csv                # Generate dashboard
./ds-dashboard data.csv output_dir     # Custom output directory
```

## Command Structure

### Data Operations (`data` group)

#### `data read` - Data Reading & Analysis
```bash
dsplatform data read <file> [OPTIONS]

Options:
  --format [csv|json|parquet|xlsx|xls]  File format (auto-detected)
  --output PATH                         Output file path
  --head INTEGER                        Number of rows to display [default: 10]
  --use-polars                          Use Polars for processing [default: True]
  --chunk-size INTEGER                  Read data in chunks
  --encoding TEXT                       File encoding [default: utf-8]
  --delimiter TEXT                      Column delimiter for CSV files
```

**Production Features:**
- **Auto-format Detection**: Intelligent file format recognition
- **Dual Engine Support**: Polars (default) and Pandas engines
- **Memory Management**: Configurable chunked reading for large files
- **Format Conversion**: Read in one format, output in another
- **Encoding Support**: Full Unicode and encoding handling

**Examples:**
```bash
# Basic data reading
dsplatform data read sales_data.csv

# Large file processing with chunks
dsplatform data read large_dataset.csv --chunk-size 50000

# Format conversion
dsplatform data read data.xlsx --output data.parquet

# Custom encoding
dsplatform data read data.csv --encoding iso-8859-1
```

#### `data validate` - Data Quality Assessment
```bash
dsplatform data validate <file> [OPTIONS]

Options:
  --schema TEXT                         Schema name to validate against
  --output PATH                         Output validation report
  --format [json|text]                  Report format [default: text]
  --strict                             Use strict validation mode
  --sample-size INTEGER                 Validate only a sample of rows
```

**Production Features:**
- **Schema Validation**: Validate against registered schemas
- **Quality Metrics**: Comprehensive data quality assessment
- **Flexible Reporting**: JSON and text report formats
- **Sampling Support**: Validate large datasets efficiently
- **Strict Mode**: Enhanced validation for production data

**Examples:**
```bash
# Basic validation
dsplatform data validate customer_data.csv

# Schema-based validation
dsplatform data validate data.csv --schema customer_schema

# Generate validation report
dsplatform data validate data.csv --output report.json --format json

# Strict validation with sampling
dsplatform data validate large_data.csv --strict --sample-size 10000
```

### Schema Management (`schema` group)

#### `schema list` - List All Schemas
```bash
dsplatform schema list
```
Shows all registered schemas with version and column count information.

#### `schema show` - Schema Details
```bash
dsplatform schema show <schema_name>
```
Displays comprehensive schema information including:
- Column definitions with constraints
- Data types and validation rules
- Primary keys and indexes
- Schema metadata

#### `schema create-sample` - Create Demo Schema
```bash
dsplatform schema create-sample
```
Creates and registers a sample schema for demonstration and testing purposes.

### Configuration Management (`config` group)

#### `config show` - Current Configuration
```bash
dsplatform config show
```
Displays all current configuration settings and their values.

#### `config set` - Update Configuration
```bash
dsplatform config set <key> <value>
```
Updates configuration values with intelligent type parsing:
- Boolean: `true`/`false`
- Integer: Numeric values
- Float: Decimal values
- String: All other values

**Examples:**
```bash
dsplatform config set debug true
dsplatform config set default_chunk_size 100000
dsplatform config set max_memory_usage_gb 8.0
```

### System Information

#### `info` - Platform Status
```bash
dsplatform info
```
Comprehensive system information including:
- Platform and Python version details
- Installed package versions (pandas, polars, pandera)
- Current configuration summary
- Registered schemas count

## Command-Line Argument Parsing

### Global Options
```bash
--debug                 Enable debug mode with detailed error messages
--config PATH          Path to custom configuration file
--version              Show version and exit
--help                 Show help message and exit
```

### Context Management
The CLI uses Click's context system to pass global options (debug, config) to all subcommands, enabling consistent behavior across the entire interface.

### Error Handling Patterns
```python
# Production error handling
try:
    # Command logic
    pass
except DataSciencePlatformError as e:
    raise click.ClickException(str(e))
except Exception as e:
    if ctx.obj.get("debug"):
        raise  # Full traceback in debug mode
    raise click.ClickException(f"Error: {str(e)}")
```

## Integration with Other Modules

### ETL Integration
```python
from datascience_platform.etl.reader import DataReader, ReadOptions
from datascience_platform.etl.validator import DataValidator, validate_dataframe
from datascience_platform.etl.schema import schema_registry
```

### Dashboard Generation
```python
from datascience_platform.dashboard.generative import DashboardGenerator
```

### Configuration System
```python
from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
```

## Production Usage Patterns

### Batch Processing Pipeline
```bash
# Complete data processing pipeline
./dsplatform data read raw_data.csv --output cleaned_data.parquet
./dsplatform data validate cleaned_data.parquet --schema production_schema
./ds-dashboard cleaned_data.parquet production_dashboard
```

### Data Quality Assessment
```bash
# Comprehensive data quality check
./dsplatform data validate dataset.csv --strict --output quality_report.json
./dsplatform schema show data_schema
```

### Configuration Management
```bash
# Production configuration setup
./dsplatform config set max_memory_usage_gb 16.0
./dsplatform config set default_chunk_size 100000
./dsplatform config show > production_config.txt
```

### System Monitoring
```bash
# System health check
./dsplatform info
./dsplatform schema list
```

## Development Integration

### Console Scripts (setup.py)
```python
entry_points={
    "console_scripts": [
        "dsplatform=datascience_platform.cli.commands:main",
        "ds-analyze=datascience_platform.cli.commands:analyze",
        "ds-dashboard=datascience_platform.cli.commands:dashboard",
    ],
}
```

### Wrapper Scripts
The root directory contains executable wrapper scripts that handle Python path setup:
- `./dsplatform` - Full CLI interface
- `./ds-analyze` - Quick analysis tool  
- `./ds-dashboard` - Dashboard generator

### Programmatic Usage
```python
# Import CLI functions for programmatic use
from datascience_platform.cli.commands import cli, main, analyze, dashboard

# Use Click testing utilities
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(cli, ['data', 'read', 'test.csv'])
```

## Performance Considerations

### Memory Management
- **Chunked Reading**: Configurable chunk sizes for large files
- **Engine Selection**: Polars (default) for better memory efficiency
- **Streaming**: Support for streaming large datasets

### Caching
- **Schema Registry**: In-memory schema caching
- **Configuration**: Cached settings access
- **Validation**: Cached validation rules

### Error Recovery
- **Graceful Degradation**: Fallback mechanisms for missing dependencies
- **Partial Processing**: Continue processing on non-fatal errors
- **Resource Cleanup**: Proper cleanup on interruption

## Links to Documentation

### Main Documentation
- **Root CLAUDE.md**: `/Users/umasankrudhya/Projects/ds-package/CLAUDE.md`
- **Implementation Summary**: `/Users/umasankrudhya/Projects/ds-package/IMPLEMENTATION_SUMMARY.md`

### Module Documentation
- **ETL Module**: `src/datascience_platform/etl/`
- **Dashboard Module**: `src/datascience_platform/dashboard/`
- **Core Configuration**: `src/datascience_platform/core/`

### Examples and Testing
- **Demo Scripts**: `examples/` directory
- **Test Scripts**: `scripts/` directory
- **Verification**: `verify_installation.py`

## CLI Best Practices

### Command Design
1. **Clear Hierarchies**: Logical command grouping (`data`, `schema`, `config`)
2. **Consistent Options**: Standard options across related commands
3. **Help Documentation**: Comprehensive help text for all commands
4. **Error Messages**: Clear, actionable error messages

### Production Readiness
1. **Validation**: Input validation for all parameters
2. **Logging**: Structured logging with configurable levels
3. **Configuration**: Environment-based configuration
4. **Testing**: Comprehensive CLI testing with Click's test utilities

### User Experience
1. **Progress Indicators**: For long-running operations
2. **Confirmation Prompts**: For destructive operations
3. **Output Formatting**: Consistent, readable output formats
4. **Default Values**: Sensible defaults for all options

The CLI module provides a professional, production-ready interface to all DataScience Platform capabilities, designed for both interactive use and automation in production environments.