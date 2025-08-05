"""CLI commands for the DataScience Analytics Platform."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import click
import pandas as pd
import polars as pl

from datascience_platform import __version__
from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
from datascience_platform.etl.reader import DataReader, ReadOptions
from datascience_platform.etl.validator import DataValidator, validate_dataframe
from datascience_platform.etl.schema import create_sample_schema, schema_registry


@click.group()
@click.version_option(version=__version__, prog_name="DataScience Analytics Platform")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str]) -> None:
    """DataScience Analytics Platform - ETL, validation, and analytics tools."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    
    if debug:
        click.echo("Debug mode enabled")
    
    if config:
        click.echo(f"Using config file: {config}")
        # TODO: Load configuration from file
        ctx.obj["config_file"] = config


@cli.group()
def data() -> None:
    """Data operations (read, validate, transform)."""
    pass


@data.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["csv", "json", "parquet", "xlsx", "xls"]), 
              help="File format (auto-detected if not specified)")
@click.option("--output", type=click.Path(), help="Output file path")
@click.option("--head", type=int, default=10, help="Number of rows to display")
@click.option("--use-polars", is_flag=True, default=True, help="Use Polars for data processing")
@click.option("--chunk-size", type=int, help="Read data in chunks of this size")
@click.option("--encoding", default="utf-8", help="File encoding")
@click.option("--delimiter", help="Column delimiter for CSV files")
@click.pass_context
def read(
    ctx: click.Context,
    file_path: str,
    format: Optional[str],
    output: Optional[str],
    head: int,
    use_polars: bool,
    chunk_size: Optional[int],
    encoding: str,
    delimiter: Optional[str]
) -> None:
    """Read and display data from various file formats."""
    try:
        # Create read options
        options = ReadOptions(
            use_polars=use_polars,
            chunk_size=chunk_size,
            encoding=encoding,
            delimiter=delimiter
        )
        
        reader = DataReader(options)
        
        if ctx.obj.get("debug"):
            click.echo(f"Reading file: {file_path}")
            file_info = reader.get_file_info(file_path)
            click.echo(f"File info: {json.dumps(file_info, indent=2)}")
        
        # Read data
        if chunk_size:
            click.echo(f"Reading data in chunks of {chunk_size} rows...")
            chunks = reader.read_chunked(file_path, format=format)
            
            if isinstance(chunks, list):
                click.echo(f"Data split into {len(chunks)} chunks")
                if chunks:
                    click.echo(f"First chunk preview (head={head}):")
                    df = chunks[0]
            else:
                click.echo("Reading chunked data...")
                # For pandas chunked reading
                df = next(iter(chunks))
                click.echo(f"First chunk preview (head={head}):")
        else:
            df = reader.read(file_path, format=format)
            click.echo(f"Data shape: {df.shape}")
        
        # Display data preview
        if use_polars and hasattr(df, 'head'):
            preview = df.head(head)
            click.echo("\nData preview:")
            click.echo(str(preview))
        elif hasattr(df, 'head'):
            preview = df.head(head)
            click.echo("\nData preview:")
            click.echo(str(preview))
        
        # Save to output file if specified
        if output:
            output_path = Path(output)
            output_format = output_path.suffix.lower()
            
            if output_format == ".csv":
                if use_polars:
                    df.write_csv(output)
                else:
                    df.to_csv(output, index=False)
            elif output_format == ".parquet":
                if use_polars:
                    df.write_parquet(output)
                else:
                    df.to_parquet(output, index=False)
            elif output_format == ".json":
                if use_polars:
                    df.write_json(output)
                else:
                    df.to_json(output, orient="records", indent=2)
            else:
                raise click.ClickException(f"Unsupported output format: {output_format}")
            
            click.echo(f"Data saved to: {output}")
    
    except DataSciencePlatformError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        if ctx.obj.get("debug"):
            raise
        raise click.ClickException(f"Error reading data: {str(e)}")


@data.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--schema", help="Schema name to validate against")
@click.option("--output", type=click.Path(), help="Output validation report to file")
@click.option("--format", type=click.Choice(["json", "text"]), default="text", 
              help="Output format for validation report")
@click.option("--strict", is_flag=True, help="Use strict validation mode")
@click.option("--sample-size", type=int, help="Validate only a sample of rows")
@click.pass_context
def validate(
    ctx: click.Context,
    file_path: str,
    schema: Optional[str],
    output: Optional[str],
    format: str,
    strict: bool,
    sample_size: Optional[int]
) -> None:
    """Validate data quality and schema compliance."""
    try:
        # Read data first
        reader = DataReader()
        df = reader.read(file_path)
        
        click.echo(f"Validating data from: {file_path}")
        click.echo(f"Data shape: {df.shape}")
        
        # Get schema if specified
        data_schema = None
        if schema:
            data_schema = schema_registry.get_schema(schema)
            if data_schema is None:
                available_schemas = schema_registry.list_schemas()
                raise click.ClickException(
                    f"Schema '{schema}' not found. Available schemas: {available_schemas}"
                )
        
        # Perform validation
        if data_schema:
            validator = DataValidator(strict_mode=strict)
            result = validator.validate_with_schema(df, data_schema, sample_size=sample_size)
        else:
            result = validate_dataframe(df, strict_mode=strict)
        
        # Display results
        if result.is_valid:
            click.echo("✅ Validation passed!")
        else:
            click.echo("❌ Validation failed!")
        
        if result.errors:
            click.echo(f"\nErrors ({len(result.errors)}):")
            for error in result.errors:
                click.echo(f"  • {error}")
        
        if result.warnings:
            click.echo(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                click.echo(f"  • {warning}")
        
        # Show validation details
        if ctx.obj.get("debug") and result.validation_details:
            click.echo(f"\nValidation details:")
            click.echo(json.dumps(result.validation_details, indent=2))
        
        # Save report if requested
        if output:
            if format == "json":
                report = result.dict()
                with open(output, 'w') as f:
                    json.dump(report, f, indent=2)
            else:
                with open(output, 'w') as f:
                    f.write(f"Validation Report for {file_path}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Status: {'PASSED' if result.is_valid else 'FAILED'}\n")
                    f.write(f"Rows validated: {result.rows_validated}\n")
                    f.write(f"Columns validated: {result.columns_validated}\n\n")
                    
                    if result.errors:
                        f.write(f"Errors ({len(result.errors)}):\n")
                        for error in result.errors:
                            f.write(f"  • {error}\n")
                        f.write("\n")
                    
                    if result.warnings:
                        f.write(f"Warnings ({len(result.warnings)}):\n")
                        for warning in result.warnings:
                            f.write(f"  • {warning}\n")
            
            click.echo(f"Validation report saved to: {output}")
    
    except DataSciencePlatformError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        if ctx.obj.get("debug"):
            raise
        raise click.ClickException(f"Error validating data: {str(e)}")


@cli.group()
def schema() -> None:
    """Schema management operations."""
    pass


@schema.command()
def list() -> None:
    """List all registered schemas."""
    schemas = schema_registry.list_schemas()
    
    if not schemas:
        click.echo("No schemas registered.")
        return
    
    click.echo("Registered schemas:")
    for schema_name in schemas:
        schema_obj = schema_registry.get_schema(schema_name)
        if schema_obj:
            click.echo(f"  • {schema_name} (v{schema_obj.version}) - {len(schema_obj.columns)} columns")
        else:
            click.echo(f"  • {schema_name}")


@schema.command()
@click.argument("schema_name")
def show(schema_name: str) -> None:
    """Show details of a specific schema."""
    schema_obj = schema_registry.get_schema(schema_name)
    
    if schema_obj is None:
        available_schemas = schema_registry.list_schemas()
        raise click.ClickException(
            f"Schema '{schema_name}' not found. Available schemas: {available_schemas}"
        )
    
    click.echo(f"Schema: {schema_obj.name}")
    click.echo(f"Version: {schema_obj.version}")
    if schema_obj.description:
        click.echo(f"Description: {schema_obj.description}")
    
    click.echo(f"\nColumns ({len(schema_obj.columns)}):")
    for col in schema_obj.columns:
        constraints = []
        if not col.nullable:
            constraints.append("NOT NULL")
        if col.unique:
            constraints.append("UNIQUE")
        if col.min_value is not None:
            constraints.append(f"MIN:{col.min_value}")
        if col.max_value is not None:
            constraints.append(f"MAX:{col.max_value}")
        if col.allowed_values:
            constraints.append(f"VALUES:{col.allowed_values}")
        
        constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
        click.echo(f"  • {col.name}: {col.dtype}{constraint_str}")
        if col.description:
            click.echo(f"    {col.description}")
    
    if schema_obj.primary_key:
        click.echo(f"\nPrimary Key: {', '.join(schema_obj.primary_key)}")
    
    if schema_obj.indexes:
        click.echo(f"Indexes: {', '.join(schema_obj.indexes)}")


@schema.command()
def create_sample() -> None:
    """Create and register a sample schema for demonstration."""
    sample_schema = create_sample_schema()
    schema_registry.register_schema(sample_schema)
    
    click.echo(f"✅ Sample schema '{sample_schema.name}' created and registered!")
    click.echo(f"Schema has {len(sample_schema.columns)} columns")
    
    # Show the created schema  
    click.echo(f"\nSchema Details:")
    click.echo(f"Name: {sample_schema.name}")
    click.echo(f"Version: {sample_schema.version}")
    if sample_schema.description:
        click.echo(f"Description: {sample_schema.description}")
    
    click.echo(f"\nColumns ({len(sample_schema.columns)}):")
    for col in sample_schema.columns:
        constraints = []
        if not col.nullable:
            constraints.append("NOT NULL")
        if col.unique:
            constraints.append("UNIQUE")
        if col.min_value is not None:
            constraints.append(f"MIN:{col.min_value}")
        if col.max_value is not None:
            constraints.append(f"MAX:{col.max_value}")
        if col.allowed_values:
            constraints.append(f"VALUES:{col.allowed_values}")
        
        constraint_str = f" [{', '.join(constraints)}]" if constraints else ""
        click.echo(f"  • {col.name}: {col.dtype}{constraint_str}")
        if col.description:
            click.echo(f"    {col.description}")
    
    if sample_schema.primary_key:
        click.echo(f"\nPrimary Key: {', '.join(sample_schema.primary_key)}")
    
    if sample_schema.indexes:
        click.echo(f"Indexes: {', '.join(sample_schema.indexes)}")


@cli.group()
def config() -> None:
    """Configuration management."""
    pass


@config.command()
def show() -> None:
    """Show current configuration."""
    config_dict = settings.dict()
    
    click.echo("Current Configuration:")
    click.echo("=" * 20)
    
    for key, value in config_dict.items():
        click.echo(f"{key}: {value}")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """Set a configuration value."""
    try:
        # Try to parse value as appropriate type
        if value.lower() in ("true", "false"):
            parsed_value = value.lower() == "true"
        elif value.isdigit():
            parsed_value = int(value)
        elif "." in value and all(part.isdigit() for part in value.split(".", 1)):
            parsed_value = float(value)
        else:
            parsed_value = value
        
        # Update settings (this is a simplified approach)
        current_config = settings.dict()
        if key not in current_config:
            raise click.ClickException(f"Unknown configuration key: {key}")
        
        current_config[key] = parsed_value
        click.echo(f"✅ Set {key} = {parsed_value}")
        click.echo("Note: Configuration changes are not persistent. Use environment variables or config files for permanent changes.")
    
    except Exception as e:
        raise click.ClickException(f"Error setting configuration: {str(e)}")


@cli.command()
def info() -> None:
    """Show platform information and system status."""
    click.echo(f"DataScience Analytics Platform v{__version__}")
    click.echo("=" * 50)
    
    # System information
    import sys
    import platform
    
    click.echo(f"Python version: {sys.version}")
    click.echo(f"Platform: {platform.platform()}")
    
    # Package versions
    try:
        import pandas
        click.echo(f"Pandas version: {pandas.__version__}")
    except ImportError:
        click.echo("Pandas: Not installed")
    
    try:
        import polars
        click.echo(f"Polars version: {polars.__version__}")
    except ImportError:
        click.echo("Polars: Not installed")
    
    try:
        import pandera
        click.echo(f"Pandera version: {pandera.__version__}")
    except ImportError:
        click.echo("Pandera: Not installed")
    
    # Configuration summary
    click.echo(f"\nConfiguration:")
    click.echo(f"  Debug mode: {settings.debug}")
    click.echo(f"  Supported formats: {', '.join(settings.supported_formats)}")
    click.echo(f"  Default chunk size: {settings.default_chunk_size}")
    click.echo(f"  Max memory usage: {settings.max_memory_usage_gb}GB")
    
    # Schema information
    schemas = schema_registry.list_schemas()
    click.echo(f"  Registered schemas: {len(schemas)}")
    if schemas:
        click.echo(f"    {', '.join(schemas)}")


if __name__ == "__main__":
    cli()