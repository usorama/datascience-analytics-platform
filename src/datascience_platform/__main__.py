"""Main CLI entry point for the DataScience Analytics Platform."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import uvicorn

from datascience_platform import __version__
from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
from datascience_platform.orchestrator.pipeline import AnalyticsPipeline, PipelineConfig
from datascience_platform.cli.commands import cli as existing_cli


@click.group()
@click.version_option(version=__version__, prog_name="DataScience Analytics Platform")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str]) -> None:
    """DataScience Analytics Platform - Comprehensive data analytics toolkit.
    
    This platform provides end-to-end data analytics capabilities including:
    - Data loading and validation from multiple formats
    - Automated statistical analysis and pattern detection  
    - Machine learning insights and predictive modeling
    - Interactive dashboard generation
    - REST API for programmatic access
    """
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    
    if debug:
        click.echo("Debug mode enabled")
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    if config:
        click.echo(f"Using config file: {config}")
        ctx.obj["config_file"] = config


@cli.command()
@click.argument("data_source", type=click.Path(exists=True))
@click.option("--target", "-t", help="Target column for ML analysis")
@click.option("--time-col", help="Time column for time series analysis")
@click.option("--context", help="Business context (e.g., 'sales', 'marketing')")
@click.option("--output", "-o", type=click.Path(), default="./analytics_output", 
              help="Output directory for results")
@click.option("--format", "data_format", type=click.Choice(["csv", "json", "parquet", "xlsx", "xls"]),
              help="Data format (auto-detected if not specified)")
@click.option("--sample-size", type=int, help="Sample size for analysis")
@click.option("--no-ml", is_flag=True, help="Disable ML analysis")
@click.option("--no-dashboard", is_flag=True, help="Disable dashboard generation")
@click.option("--theme", type=click.Choice(["light", "dark"]), default="light",
              help="Dashboard theme")
@click.option("--title", help="Custom dashboard title")
@click.option("--strict", is_flag=True, help="Use strict data validation")
@click.option("--save-intermediate", is_flag=True, help="Save intermediate processing results")
@click.pass_context
def analyze(ctx: click.Context, data_source: str, target: Optional[str], 
           time_col: Optional[str], context: Optional[str], output: str,
           data_format: Optional[str], sample_size: Optional[int],
           no_ml: bool, no_dashboard: bool, theme: str, title: Optional[str],
           strict: bool, save_intermediate: bool) -> None:
    """Run comprehensive analytics pipeline on your data.
    
    This command executes the complete analytics workflow:
    1. Load and validate data
    2. Perform statistical analysis and pattern detection
    3. Generate ML insights (if enabled)
    4. Create interactive dashboard (if enabled)
    5. Export results and reports
    
    Example:
        datascience-platform analyze sales_data.csv --target revenue --time-col date --context sales
    """
    try:
        click.echo(f"🚀 Starting comprehensive analytics for: {data_source}")
        
        # Create pipeline configuration
        config = PipelineConfig(
            data_source=data_source,
            data_format=data_format,
            target_column=target,
            time_column=time_col,
            business_context=context,
            output_dir=Path(output),
            sample_size=sample_size,
            ml_enabled=not no_ml,
            generate_dashboard=not no_dashboard,
            dashboard_theme=theme,
            dashboard_title=title,
            strict_validation=strict,
            save_intermediate=save_intermediate
        )
        
        # Create and execute pipeline
        pipeline = AnalyticsPipeline(config)
        
        # Add progress callback for CLI output
        def progress_callback(progress_data):
            status = progress_data["status"]
            progress_info = progress_data["progress"]
            
            current_stage = progress_info.get("current_stage")
            overall_progress = progress_info.get("overall_progress", 0)
            
            if current_stage:
                stage_message = progress_info.get("stage_messages", {}).get(current_stage, "")
                click.echo(f"[{overall_progress:.1f}%] {current_stage}: {stage_message}")
        
        pipeline.add_progress_callback(progress_callback)
        
        # Execute pipeline
        results = pipeline.execute()
        
        # Display results summary
        click.echo("\n✅ Analytics pipeline completed successfully!")
        click.echo(f"📊 Dataset: {results['data_shape'][0]:,} rows × {results['data_shape'][1]} columns")
        
        if results.get('validation_results'):
            validation = results['validation_results']
            status = "✅ PASSED" if validation['is_valid'] else "❌ FAILED"
            click.echo(f"🔍 Data Validation: {status}")
        
        if results.get('analysis_results'):
            insights = results['analysis_results'].get('key_insights', [])
            click.echo(f"💡 Key Insights: {len(insights)} generated")
        
        if results.get('dashboard_generated'):
            click.echo(f"📈 Dashboard: Generated and saved")
        
        click.echo(f"📁 Output Directory: {results['output_directory']}")
        
        # List output files
        output_path = Path(results['output_directory'])
        if output_path.exists():
            files = list(output_path.glob("*"))
            if files:
                click.echo("\n📄 Generated Files:")
                for file in files:
                    click.echo(f"  • {file.name}")
        
    except DataSciencePlatformError as e:
        click.echo(f"❌ Analytics failed: {str(e)}", err=True)
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


@cli.command()
@click.option("--host", default="localhost", help="API server host")
@click.option("--port", default=8000, type=int, help="API server port")
@click.option("--workers", default=1, type=int, help="Number of worker processes")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.pass_context
def server(ctx: click.Context, host: str, port: int, workers: int, reload: bool) -> None:
    """Start the analytics API server.
    
    The server provides REST API endpoints for:
    - File upload and management
    - Analytics pipeline execution
    - Progress monitoring
    - Results retrieval
    - Dashboard access
    
    Example:
        datascience-platform server --host 0.0.0.0 --port 8080
    """
    try:
        click.echo(f"🚀 Starting DataScience Analytics API server")
        click.echo(f"📡 Server: http://{host}:{port}")
        click.echo(f"📖 API Docs: http://{host}:{port}/docs")
        click.echo(f"📚 ReDoc: http://{host}:{port}/redoc")
        
        # Import app here to avoid circular imports
        from datascience_platform.api.analytics import app
        
        # Run server
        uvicorn.run(
            "datascience_platform.api.analytics:app",
            host=host,
            port=port,
            workers=workers if not reload else 1,
            reload=reload,
            log_level="debug" if ctx.obj.get("debug") else "info"
        )
        
    except Exception as e:
        click.echo(f"❌ Server failed to start: {str(e)}", err=True)
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


@cli.command()
@click.argument("pipeline_results", type=click.Path(exists=True))
@click.option("--format", "export_format", type=click.Choice(["json", "csv", "xlsx"]),
              default="json", help="Export format")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def export(ctx: click.Context, pipeline_results: str, export_format: str, 
          output: Optional[str]) -> None:
    """Export pipeline results to different formats.
    
    Export analysis results, insights, and data to various formats
    for further analysis or reporting.
    
    Example:
        datascience-platform export ./analytics_output/execution_summary.json --format xlsx
    """
    try:
        results_path = Path(pipeline_results)
        
        if results_path.is_dir():
            # Look for execution summary in directory
            summary_file = results_path / "execution_summary.json"
            if summary_file.exists():
                results_path = summary_file
            else:
                raise click.ClickException(f"No execution summary found in {results_path}")
        
        # Load results
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        # Generate output filename if not provided
        if not output:
            base_name = results_path.stem
            timestamp = results.get("progress", {}).get("start_time", "unknown").replace(":", "-")
            output = f"{base_name}_export_{timestamp}.{export_format}"
        
        output_path = Path(output)
        
        # Export based on format
        if export_format == "json":
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
                
        elif export_format == "csv":
            import pandas as pd
            
            # Extract key metrics for CSV export
            export_data = []
            
            # Basic info
            config = results.get("pipeline_config", {})
            progress = results.get("progress", {})
            
            export_data.append({
                "metric": "data_source",
                "value": config.get("data_source"),
                "category": "configuration"
            })
            
            export_data.append({
                "metric": "execution_time_seconds",
                "value": progress.get("elapsed_time"),
                "category": "performance"
            })
            
            # Add insights if available
            results_summary = results.get("results_summary", {})
            for key, value in results_summary.items():
                export_data.append({
                    "metric": key,
                    "value": value,
                    "category": "results"
                })
            
            df = pd.DataFrame(export_data)
            df.to_csv(output_path, index=False)
            
        elif export_format == "xlsx":
            import pandas as pd
            
            with pd.ExcelWriter(output_path) as writer:
                # Configuration sheet
                config_df = pd.DataFrame([
                    {"parameter": k, "value": v} 
                    for k, v in results.get("pipeline_config", {}).items()
                ])
                config_df.to_excel(writer, sheet_name="Configuration", index=False)
                
                # Results summary sheet
                summary_df = pd.DataFrame([
                    {"metric": k, "value": v}
                    for k, v in results.get("results_summary", {}).items()
                ])
                summary_df.to_excel(writer, sheet_name="Summary", index=False)
                
                # Progress sheet
                progress_data = results.get("progress", {})
                if "stage_progress" in progress_data:
                    progress_df = pd.DataFrame([
                        {"stage": k, "progress": v}
                        for k, v in progress_data["stage_progress"].items()
                    ])
                    progress_df.to_excel(writer, sheet_name="Progress", index=False)
        
        click.echo(f"✅ Results exported to: {output_path}")
        click.echo(f"📊 Format: {export_format.upper()}")
        
    except Exception as e:
        click.echo(f"❌ Export failed: {str(e)}", err=True)
        if ctx.obj.get("debug"):
            raise
        sys.exit(1)


# Add existing CLI commands as subgroups
# Import the individual command groups from the existing CLI
from datascience_platform.cli.commands import data, schema, config, info

cli.add_command(data, name="data")
cli.add_command(schema, name="schema")  
cli.add_command(config, name="config")
cli.add_command(info, name="info")


def main(args: Optional[list] = None) -> int:
    """Main entry point for the CLI application.
    
    Args:
        args: Optional command line arguments (uses sys.argv if None)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        if args is None:
            args = sys.argv[1:]
        
        # Handle the case where Click is called programmatically
        cli(args, standalone_mode=False)
        return 0
        
    except click.ClickException as e:
        e.show()
        return e.exit_code
    
    except click.Abort:
        click.echo("Aborted!", err=True)
        return 1
    
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())