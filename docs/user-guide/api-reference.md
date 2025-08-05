# API Reference Guide

This guide provides comprehensive documentation for the DataScience Analytics Platform Python API. The platform provides a clean, object-oriented interface for ETL operations, data validation, and schema management.

## Installation and Setup

```python
# Import the main ETL components
from datascience_platform.etl import (
    DataReader, ReadOptions,
    DataValidator, ValidationResult,
    DataSchema, ColumnSchema,
    schema_registry
)

# Import core functionality
from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
```

## Core Modules

### datascience_platform.etl

The main ETL module containing all data processing functionality:

- **DataReader**: Universal data reader for multiple file formats
- **DataValidator**: Data validation engine with schema support
- **DataSchema/ColumnSchema**: Schema definition and management
- **SchemaRegistry**: Registry for managing data schemas

### datascience_platform.core

Core functionality and configuration:

- **Config/Settings**: Platform configuration management
- **Exceptions**: Custom exception hierarchy

## Data Reading

### DataReader Class

The `DataReader` class provides universal data reading capabilities with support for multiple file formats and processing options.

#### Constructor

```python
class DataReader:
    def __init__(self, options: Optional[ReadOptions] = None) -> None
```

**Parameters:**
- `options` (ReadOptions, optional): Configuration options for reading

**Example:**
```python
from datascience_platform.etl import DataReader, ReadOptions

# Default reader
reader = DataReader()

# Reader with custom options
options = ReadOptions(
    chunk_size=10000,
    encoding='utf-8',
    use_polars=True
)
reader = DataReader(options)
```

#### Methods

##### read()

Read data from a file with automatic format detection.

```python
def read(
    self,
    file_path: Union[str, Path],
    format: Optional[str] = None,
    **kwargs: Any
) -> Union[pd.DataFrame, pl.DataFrame]
```

**Parameters:**
- `file_path` (str | Path): Path to the data file
- `format` (str, optional): File format ('csv', 'json', 'parquet', 'xlsx', 'xls')
- `**kwargs`: Additional options to override defaults

**Returns:**
- DataFrame (pandas or polars depending on configuration)

**Raises:**
- `DataReaderError`: If file cannot be read or format is unsupported

**Examples:**
```python
# Basic usage
df = reader.read("sales_data.csv")

# Specify format explicitly
df = reader.read("data.txt", format="csv")

# Override options for this read
df = reader.read("data.csv", delimiter=";", encoding="latin-1")

# Read Excel file
df = reader.read("report.xlsx")

# Read Parquet file
df = reader.read("processed_data.parquet")
```

##### read_chunked()

Read large files in chunks for memory-efficient processing.

```python
def read_chunked(
    self,
    file_path: Union[str, Path],
    format: Optional[str] = None,
    **kwargs: Any
) -> Union[List[pd.DataFrame], List[pl.DataFrame], Iterator]
```

**Parameters:**
- `file_path` (str | Path): Path to the data file
- `format` (str, optional): File format
- `**kwargs`: Additional options

**Returns:**
- List of DataFrames or Iterator depending on backend

**Examples:**
```python
# Read in chunks
chunks = reader.read_chunked("large_file.csv", chunk_size=50000)

# Process each chunk
for i, chunk in enumerate(chunks):
    print(f"Processing chunk {i}: {chunk.shape[0]} rows")
    # Process chunk here
```

##### get_file_info()

Get information about a file before reading.

```python
def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]
```

**Parameters:**
- `file_path` (str | Path): Path to the file

**Returns:**
- Dictionary with file information (size, format, encoding, etc.)

**Example:**
```python
info = reader.get_file_info("data.csv")
print(f"File size: {info['size_mb']:.2f} MB")
print(f"Detected format: {info['format']}")
print(f"Detected encoding: {info['encoding']}")
```

### ReadOptions Class

Configuration class for customizing data reading behavior.

```python
class ReadOptions(BaseModel):
    chunk_size: Optional[int] = None
    skip_rows: int = 0
    max_rows: Optional[int] = None
    encoding: str = "utf-8"
    delimiter: Optional[str] = None
    header: Union[bool, int, List[int]] = True
    na_values: Optional[List[str]] = None
    dtype: Optional[Dict[str, str]] = None
    parse_dates: Optional[List[str]] = None
    use_polars: bool = True
```

**Parameters:**
- `chunk_size`: Number of rows per chunk for large files
- `skip_rows`: Number of rows to skip at the beginning
- `max_rows`: Maximum number of rows to read
- `encoding`: File encoding (default: 'utf-8')
- `delimiter`: Column delimiter for CSV files
- `header`: Row(s) to use as column names
- `na_values`: Additional strings to recognize as NA/NaN
- `dtype`: Explicit data types for columns
- `parse_dates`: Columns to parse as dates
- `use_polars`: Whether to use Polars (default: True)

**Examples:**
```python
# Basic options
options = ReadOptions(
    chunk_size=10000,
    encoding='utf-8'
)

# Advanced CSV options
csv_options = ReadOptions(
    delimiter=';',
    skip_rows=2,
    max_rows=100000,
    na_values=['N/A', 'NULL', ''],
    parse_dates=['date_column']
)

# Custom data types
typed_options = ReadOptions(
    dtype={
        'id': 'int64',
        'name': 'string',
        'price': 'float64'
    }
)
```

## Data Validation

### DataValidator Class

Comprehensive data validation engine with schema support.

#### Constructor

```python
class DataValidator:
    def __init__(self, strict_mode: Optional[bool] = None) -> None
```

**Parameters:**
- `strict_mode` (bool, optional): Enable strict validation mode

**Example:**
```python
# Default validator
validator = DataValidator()

# Strict validation
strict_validator = DataValidator(strict_mode=True)
```

#### Methods

##### validate_with_schema()

Validate data against a defined schema.

```python
def validate_with_schema(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    schema: DataSchema,
    sample_size: Optional[int] = None
) -> ValidationResult
```

**Parameters:**
- `data`: DataFrame to validate
- `schema`: Schema definition for validation
- `sample_size`: Number of rows to validate (optional)

**Returns:**
- `ValidationResult` object with validation details

**Example:**
```python
# Validate against schema
result = validator.validate_with_schema(df, my_schema)

if result.is_valid:
    print("✅ Validation passed!")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  • {error}")

# Check warnings
if result.has_warnings():
    print("⚠️ Warnings:")
    for warning in result.warnings:
        print(f"  • {warning}")
```

##### validate_dataframe()

Basic data validation without a schema.

```python
def validate_dataframe(
    self,
    data: Union[pd.DataFrame, pl.DataFrame]
) -> ValidationResult
```

**Parameters:**
- `data`: DataFrame to validate

**Returns:**
- `ValidationResult` object

**Example:**
```python
# Basic validation
result = validator.validate_dataframe(df)
print(f"Data quality score: {result.validation_details.get('quality_score', 'N/A')}")
```

##### generate_quality_report()

Generate comprehensive data quality report.

```python
def generate_quality_report(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    schema: Optional[DataSchema] = None
) -> Dict[str, Any]
```

**Parameters:**
- `data`: DataFrame to analyze
- `schema`: Optional schema for enhanced reporting

**Returns:**
- Dictionary with quality metrics

**Example:**
```python
report = validator.generate_quality_report(df, schema)
print(f"Completeness: {report['completeness']:.2%}")
print(f"Consistency: {report['consistency']:.2%}")
print(f"Validity: {report['validity']:.2%}")
```

### ValidationResult Class

Container for validation results and errors.

```python
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    schema_name: Optional[str] = None
    rows_validated: int = 0
    columns_validated: int = 0
    validation_details: Dict[str, Any] = {}
```

**Methods:**
- `add_error(error: str)`: Add validation error
- `add_warning(warning: str)`: Add validation warning
- `has_errors() -> bool`: Check if validation has errors
- `has_warnings() -> bool`: Check if validation has warnings

**Example:**
```python
result = validator.validate_with_schema(df, schema)

print(f"Valid: {result.is_valid}")
print(f"Rows validated: {result.rows_validated}")
print(f"Columns validated: {result.columns_validated}")

if result.has_errors():
    print(f"Errors ({len(result.errors)}):")
    for error in result.errors:
        print(f"  • {error}")
```

## Schema Management

### ColumnSchema Class

Definition for individual column validation rules.

```python
class ColumnSchema(BaseModel):
    name: str
    dtype: str
    nullable: bool = True
    unique: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    description: Optional[str] = None
```

**Example:**
```python
# Basic column
id_column = ColumnSchema(
    name="customer_id",
    dtype="str",
    nullable=False,
    unique=True,
    description="Unique customer identifier"
)

# Numeric column with constraints
age_column = ColumnSchema(
    name="age",
    dtype="int64",
    nullable=False,
    min_value=0,
    max_value=120
)

# Categorical column
status_column = ColumnSchema(
    name="status",
    dtype="str",
    nullable=False,
    allowed_values=["active", "inactive", "suspended"]
)

# Email column with pattern
email_column = ColumnSchema(
    name="email",
    dtype="str",
    nullable=False,
    unique=True,
    regex_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
```

### DataSchema Class

Complete schema definition for a dataset.

```python
class DataSchema(BaseModel):
    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    columns: List[ColumnSchema]
    primary_key: Optional[List[str]] = None
    foreign_keys: Optional[Dict[str, str]] = None
    indexes: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
```

**Example:**
```python
# Create complete schema
customer_schema = DataSchema(
    name="customer_schema",
    version="1.0.0",
    description="Customer data schema with validation rules",
    columns=[
        ColumnSchema(
            name="customer_id",
            dtype="str",
            nullable=False,
            unique=True
        ),
        ColumnSchema(
            name="first_name",
            dtype="str",
            nullable=False
        ),
        ColumnSchema(
            name="last_name",
            dtype="str",
            nullable=False
        ),
        ColumnSchema(
            name="email",
            dtype="str",
            nullable=False,
            unique=True,
            regex_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        ),
        ColumnSchema(
            name="age",
            dtype="int64",
            nullable=True,
            min_value=0,
            max_value=120
        ),
        ColumnSchema(
            name="registration_date",
            dtype="datetime",
            nullable=False
        )
    ],
    primary_key=["customer_id"],
    indexes=["email", "registration_date"]
)
```

### SchemaRegistry

Global registry for managing schemas.

**Methods:**

##### register_schema()

Register a schema in the global registry.

```python
def register_schema(schema: DataSchema) -> None
```

**Example:**
```python
from datascience_platform.etl import schema_registry

# Register schema
schema_registry.register_schema(customer_schema)
```

##### get_schema()

Retrieve a schema by name.

```python
def get_schema(name: str) -> Optional[DataSchema]
```

**Example:**
```python
# Get registered schema
schema = schema_registry.get_schema("customer_schema")
if schema:
    print(f"Found schema: {schema.name} v{schema.version}")
```

##### list_schemas()

List all registered schema names.

```python
def list_schemas() -> List[str]
```

**Example:**
```python
# List all schemas
schemas = schema_registry.list_schemas()
print(f"Available schemas: {', '.join(schemas)}")
```

##### remove_schema()

Remove a schema from the registry.

```python
def remove_schema(name: str) -> bool
```

**Example:**
```python
# Remove schema
removed = schema_registry.remove_schema("old_schema")
if removed:
    print("Schema removed successfully")
```

## Data Transformation

### DataTransformer Class

Advanced data cleaning and transformation capabilities.

#### Constructor

```python
class DataTransformer:
    def __init__(self, config: Optional[TransformationConfig] = None) -> None
```

**Example:**
```python
from datascience_platform.etl import DataTransformer

# Default transformer
transformer = DataTransformer()

# Custom configuration
from datascience_platform.core.config import TransformationConfig
custom_config = TransformationConfig(
    missing_value_strategies={
        "numeric": "median",
        "categorical": "mode",
        "text": "drop"
    },
    outlier_handling="cap"
)
transformer = DataTransformer(custom_config)
```

#### Methods

##### transform_dataframe()

Apply comprehensive transformations to a DataFrame.

```python
def transform_dataframe(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    schema: Optional[DataSchema] = None
) -> Tuple[Union[pd.DataFrame, pl.DataFrame], TransformationReport]
```

**Parameters:**
- `data`: DataFrame to transform
- `schema`: Optional schema to guide transformations

**Returns:**
- Tuple of (transformed_dataframe, transformation_report)

**Example:**
```python
# Apply transformations
cleaned_df, report = transformer.transform_dataframe(df, schema=my_schema)

print(f"Original shape: {report.original_shape}")
print(f"Final shape: {report.final_shape}")
print(f"Rows removed: {report.total_rows_removed}")
print(f"Values imputed: {report.total_values_imputed}")
print(f"Success rate: {report.transformation_success_rate:.2%}")
```

##### handle_missing_values()

Handle missing values using various strategies.

```python
def handle_missing_values(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    strategy: Union[str, Dict[str, str]] = "auto"
) -> Union[pd.DataFrame, pl.DataFrame]
```

**Parameters:**
- `data`: DataFrame with missing values
- `strategy`: Strategy for handling missing values

**Strategies:**
- `"drop"`: Remove rows/columns with missing values
- `"mean"`: Fill with column mean (numeric only)
- `"median"`: Fill with column median (numeric only)
- `"mode"`: Fill with most frequent value
- `"forward_fill"`: Forward fill for time series
- `"backward_fill"`: Backward fill for time series
- `"interpolate"`: Linear interpolation (numeric only)

**Example:**
```python
# Auto strategy (different per column type)
cleaned_df = transformer.handle_missing_values(df, strategy="auto")

# Specific strategy for all columns
cleaned_df = transformer.handle_missing_values(df, strategy="median")

# Different strategies per column
strategies = {
    "age": "median",
    "name": "drop",
    "category": "mode"
}
cleaned_df = transformer.handle_missing_values(df, strategy=strategies)
```

##### detect_and_handle_outliers()

Detect and handle outliers in numeric columns.

```python
def detect_and_handle_outliers(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    method: str = "iqr",
    action: str = "cap"
) -> Union[pd.DataFrame, pl.DataFrame]
```

**Parameters:**
- `data`: DataFrame to process
- `method`: Outlier detection method ("iqr", "zscore", "isolation_forest")
- `action`: Action to take ("cap", "remove", "flag")

**Example:**
```python
# Remove outliers using IQR method
cleaned_df = transformer.detect_and_handle_outliers(
    df, 
    method="iqr", 
    action="remove"
)

# Cap outliers using Z-score method
capped_df = transformer.detect_and_handle_outliers(
    df, 
    method="zscore", 
    action="cap"
)
```

##### normalize_data()

Normalize numeric columns using various scaling methods.

```python
def normalize_data(
    self,
    data: Union[pd.DataFrame, pl.DataFrame],
    method: str = "standard"
) -> Union[pd.DataFrame, pl.DataFrame]
```

**Parameters:**
- `data`: DataFrame to normalize
- `method`: Normalization method ("standard", "minmax", "robust")

**Example:**
```python
# Standard scaling (z-score)
normalized_df = transformer.normalize_data(df, method="standard")

# Min-max scaling to [0, 1]
scaled_df = transformer.normalize_data(df, method="minmax")

# Robust scaling (median and IQR)
robust_df = transformer.normalize_data(df, method="robust")
```

## Configuration Management

### Settings

Global configuration object for the platform.

```python
from datascience_platform.core.config import settings

# Access current settings
print(f"Debug mode: {settings.debug}")
print(f"Max file size: {settings.max_file_size_mb}MB")
print(f"Supported formats: {settings.supported_formats}")
```

### Custom Configuration

Create custom configuration for specific use cases.

```python
from datascience_platform.core.config import Settings, ETLConfig, ValidationConfig

# Create custom settings
custom_settings = Settings(
    etl=ETLConfig(
        max_file_size_mb=2048,
        chunk_size_rows=20000,
        supported_formats=["csv", "parquet", "json"]
    ),
    validation=ValidationConfig(
        null_threshold=0.3,
        outlier_std_threshold=2.5,
        strict_mode=True
    ),
    debug=True
)

# Use custom settings
reader = DataReader(settings=custom_settings)
```

## Error Handling

### Exception Hierarchy

The platform provides a structured exception hierarchy for better error handling.

```python
from datascience_platform.core.exceptions import (
    DataSciencePlatformError,  # Base exception
    DataReaderError,           # File reading errors
    DataValidationError,       # Validation errors
    SchemaError,              # Schema-related errors
    ConfigurationError        # Configuration errors
)
```

### Error Handling Examples

```python
try:
    # Read data
    df = reader.read("data.csv")
    
    # Validate data
    result = validator.validate_with_schema(df, schema)
    
    # Transform data
    cleaned_df, report = transformer.transform_dataframe(df)
    
except DataReaderError as e:
    print(f"Failed to read file: {e.message}")
    print(f"File path: {e.details.get('file_path')}")
    if e.original_exception:
        print(f"Root cause: {e.original_exception}")

except DataValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Schema: {e.details.get('schema_name')}")
    print(f"Errors: {e.details.get('errors', [])}")

except DataSciencePlatformError as e:
    print(f"Platform error: {e.message}")
    if e.details:
        print(f"Details: {e.details}")

except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Best Practices

### Memory Management

```python
# For large files, use chunked processing
options = ReadOptions(chunk_size=50000)
reader = DataReader(options)

for chunk in reader.read_chunked("large_file.csv"):
    # Process chunk
    result = validator.validate_dataframe(chunk)
    # Process or save results
```

### Schema-First Development

```python
# Define schema first
schema = DataSchema(
    name="customer_data",
    version="1.0.0",
    columns=[
        ColumnSchema(name="id", dtype="str", nullable=False, unique=True),
        ColumnSchema(name="name", dtype="str", nullable=False),
        ColumnSchema(name="email", dtype="str", nullable=False, unique=True)
    ]
)

# Register schema
schema_registry.register_schema(schema)

# Use schema for validation
reader = DataReader()
validator = DataValidator()

df = reader.read("customer_data.csv")
result = validator.validate_with_schema(df, schema)

if not result.is_valid:
    print("Data does not match schema!")
    for error in result.errors:
        print(f"  • {error}")
```

### Configuration Management

```python
# Use environment-specific configurations
import os

if os.getenv("ENV") == "production":
    settings = Settings(
        etl=ETLConfig(max_file_size_mb=4096),
        validation=ValidationConfig(strict_mode=True),
        debug=False
    )
else:
    settings = Settings(
        etl=ETLConfig(max_file_size_mb=512),
        validation=ValidationConfig(strict_mode=False),
        debug=True
    )
```

### Performance Optimization

```python
# Use Polars for better performance
options = ReadOptions(use_polars=True, chunk_size=100000)
reader = DataReader(options)

# Parallel processing for validation
validator = DataValidator()
validator.enable_parallel_processing = True

# Efficient transformations
transformer = DataTransformer()
transformer.config.enable_vectorization = True
```

## Complete Example

Here's a complete example demonstrating the full API:

```python
from datascience_platform.etl import (
    DataReader, ReadOptions, DataValidator, DataTransformer,
    DataSchema, ColumnSchema, schema_registry
)

# 1. Define schema
customer_schema = DataSchema(
    name="customer_data",
    version="1.0.0",
    description="Customer database schema",
    columns=[
        ColumnSchema(
            name="customer_id",
            dtype="str",
            nullable=False,
            unique=True,
            description="Unique customer identifier"
        ),
        ColumnSchema(
            name="first_name",
            dtype="str",
            nullable=False
        ),
        ColumnSchema(
            name="email",
            dtype="str",
            nullable=False,
            unique=True,
            regex_pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        ),
        ColumnSchema(
            name="age",
            dtype="int64",
            nullable=True,
            min_value=18,
            max_value=120
        ),
        ColumnSchema(
            name="signup_date",
            dtype="datetime",
            nullable=False
        )
    ],
    primary_key=["customer_id"]
)

# 2. Register schema
schema_registry.register_schema(customer_schema)

# 3. Configure reading options
options = ReadOptions(
    encoding='utf-8',
    use_polars=True,
    parse_dates=['signup_date']
)

# 4. Initialize components
reader = DataReader(options)
validator = DataValidator(strict_mode=True)
transformer = DataTransformer()

try:
    # 5. Read data
    print("Reading customer data...")
    df = reader.read("customer_data.csv")
    print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    
    # 6. Validate data
    print("Validating data...")
    validation_result = validator.validate_with_schema(df, customer_schema)
    
    if validation_result.is_valid:
        print("✅ Data validation passed!")
    else:
        print("❌ Data validation failed:")
        for error in validation_result.errors[:5]:  # Show first 5 errors
            print(f"  • {error}")
    
    # 7. Transform data
    print("Transforming data...")
    cleaned_df, transform_report = transformer.transform_dataframe(
        df, 
        schema=customer_schema
    )
    
    print(f"Transformation complete:")
    print(f"  Original rows: {transform_report.original_shape[0]}")
    print(f"  Final rows: {transform_report.final_shape[0]}")
    print(f"  Success rate: {transform_report.transformation_success_rate:.1%}")
    
    # 8. Save cleaned data
    if hasattr(cleaned_df, 'write_parquet'):  # Polars
        cleaned_df.write_parquet("cleaned_customer_data.parquet")
    else:  # Pandas
        cleaned_df.to_parquet("cleaned_customer_data.parquet", index=False)
    
    print("✅ Pipeline completed successfully!")
    
except Exception as e:
    print(f"❌ Pipeline failed: {str(e)}")
    raise
```

This API reference provides comprehensive coverage of all classes, methods, and usage patterns in the DataScience Analytics Platform.