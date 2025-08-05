"""Main Analytics Pipeline Orchestrator

This module provides the core orchestration functionality for the entire
data science analytics workflow, coordinating ETL, ML, and Dashboard components.
"""

import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

import pandas as pd
import polars as pl
from pydantic import BaseModel, Field, validator

from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
from datascience_platform.etl.reader import DataReader, ReadOptions
from datascience_platform.etl.validator import DataValidator, validate_dataframe
from datascience_platform.ml.insights import InsightGenerator
from datascience_platform.dashboard.generator import DashboardGenerator

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PipelineStage(str, Enum):
    """Pipeline execution stages."""
    INITIALIZATION = "initialization"
    DATA_LOADING = "data_loading"
    DATA_VALIDATION = "data_validation"
    DATA_PROCESSING = "data_processing"
    ANALYSIS = "analysis"
    DASHBOARD_GENERATION = "dashboard_generation"
    FINALIZATION = "finalization"


class PipelineConfig(BaseModel):
    """Configuration for analytics pipeline execution."""
    
    # Data source configuration
    data_source: Union[str, Path] = Field(..., description="Path to data file")
    data_format: Optional[str] = Field(None, description="Data format (auto-detected if None)")
    read_options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Data reading options")
    
    # Analysis configuration
    target_column: Optional[str] = Field(None, description="Target column for ML analysis")
    time_column: Optional[str] = Field(None, description="Time column for time series analysis")
    business_context: Optional[str] = Field(None, description="Business context for relevant insights")
    
    # Processing options
    validate_data: bool = Field(True, description="Perform data validation")
    strict_validation: bool = Field(False, description="Use strict validation mode")
    sample_size: Optional[int] = Field(None, description="Sample size for analysis (None for full dataset)")
    
    # ML configuration
    ml_enabled: bool = Field(True, description="Enable ML analysis")
    ml_time_limit: int = Field(120, description="Time limit for ML training (seconds)")
    
    # Dashboard configuration
    generate_dashboard: bool = Field(True, description="Generate dashboard")
    dashboard_theme: str = Field("light", description="Dashboard theme (light/dark)")
    dashboard_title: Optional[str] = Field(None, description="Custom dashboard title")
    
    # Output configuration
    output_dir: Path = Field(default_factory=lambda: Path("./output"), description="Output directory")
    save_intermediate: bool = Field(False, description="Save intermediate results")
    export_formats: List[str] = Field(default=["html"], description="Export formats for dashboard")
    
    @validator("data_source")
    def validate_data_source(cls, v):
        """Validate data source exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Data source not found: {v}")
        return v
    
    @validator("output_dir")
    def validate_output_dir(cls, v):
        """Ensure output directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return path


class PipelineProgress:
    """Track pipeline execution progress."""
    
    def __init__(self):
        self.current_stage: Optional[PipelineStage] = None
        self.stage_progress: Dict[PipelineStage, float] = {}
        self.stage_messages: Dict[PipelineStage, str] = {}
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[str] = None
    
    def start_stage(self, stage: PipelineStage, message: str = ""):
        """Start a pipeline stage."""
        self.current_stage = stage
        self.stage_progress[stage] = 0.0
        self.stage_messages[stage] = message
        if self.start_time is None:
            self.start_time = datetime.now()
        logger.info(f"Starting stage: {stage.value} - {message}")
    
    def update_stage(self, progress: float, message: str = ""):
        """Update current stage progress."""
        if self.current_stage:
            self.stage_progress[self.current_stage] = min(100.0, max(0.0, progress))
            if message:
                self.stage_messages[self.current_stage] = message
            logger.debug(f"Stage {self.current_stage.value}: {progress:.1f}% - {message}")
    
    def complete_stage(self, message: str = ""):
        """Complete current stage."""
        if self.current_stage:
            self.stage_progress[self.current_stage] = 100.0
            if message:
                self.stage_messages[self.current_stage] = message
            logger.info(f"Completed stage: {self.current_stage.value} - {message}")
    
    def set_error(self, error: str):
        """Set pipeline error."""
        self.error = error
        self.end_time = datetime.now()
        logger.error(f"Pipeline error: {error}")
    
    def finish(self):
        """Mark pipeline as finished."""
        self.end_time = datetime.now()
        self.current_stage = None
    
    def get_overall_progress(self) -> float:
        """Get overall pipeline progress percentage."""
        if not self.stage_progress:
            return 0.0
        
        total_stages = len(PipelineStage)
        completed_progress = sum(self.stage_progress.values())
        return completed_progress / total_stages
    
    def get_elapsed_time(self) -> Optional[float]:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return None
        
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary."""
        return {
            "current_stage": self.current_stage.value if self.current_stage else None,
            "stage_progress": {k.value: v for k, v in self.stage_progress.items()},
            "stage_messages": {k.value: v for k, v in self.stage_messages.items()},
            "overall_progress": self.get_overall_progress(),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "elapsed_time": self.get_elapsed_time(),
            "error": self.error
        }


class AnalyticsPipeline:
    """Main analytics pipeline orchestrator.
    
    Coordinates the entire data science workflow from data loading
    through analysis to dashboard generation.
    """
    
    def __init__(self, config: PipelineConfig):
        """Initialize analytics pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config
        self.status = PipelineStatus.PENDING
        self.progress = PipelineProgress()
        
        # Initialize components
        self.data_reader = DataReader()
        self.data_validator = DataValidator(strict_mode=config.strict_validation)
        self.insight_generator = InsightGenerator()
        self.dashboard_generator = DashboardGenerator(
            theme=config.dashboard_theme,
            compress=True
        )
        
        # Results storage
        self.results = {
            "raw_data": None,
            "processed_data": None,
            "validation_results": None,
            "analysis_results": None,
            "dashboard_html": None,
            "insights_report": None
        }
        
        # Progress callbacks
        self._progress_callbacks: List[Callable[[Dict[str, Any]], None]] = []
    
    def add_progress_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self):
        """Notify all progress callbacks."""
        progress_data = {
            "status": self.status.value,
            "progress": self.progress.to_dict()
        }
        
        for callback in self._progress_callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    def execute(self) -> Dict[str, Any]:
        """Execute the complete analytics pipeline.
        
        Returns:
            Dictionary containing all pipeline results
            
        Raises:
            DataSciencePlatformError: If pipeline execution fails
        """
        try:
            self.status = PipelineStatus.RUNNING
            logger.info(f"Starting analytics pipeline for: {self.config.data_source}")
            
            # Execute pipeline stages
            self._initialize()
            self._load_data()
            
            if self.config.validate_data:
                self._validate_data()
            
            self._process_data()
            self._analyze_data()
            
            if self.config.generate_dashboard:
                self._generate_dashboard()
            
            self._finalize()
            
            self.status = PipelineStatus.COMPLETED
            self.progress.finish()
            logger.info("Analytics pipeline completed successfully")
            
            return self.get_results()
            
        except Exception as e:
            self.status = PipelineStatus.FAILED
            self.progress.set_error(str(e))
            logger.error(f"Pipeline execution failed: {e}")
            
            if isinstance(e, DataSciencePlatformError):
                raise
            raise DataSciencePlatformError(f"Pipeline execution failed: {str(e)}") from e
        
        finally:
            self._notify_progress()
    
    def _initialize(self):
        """Initialize pipeline execution."""
        self.progress.start_stage(
            PipelineStage.INITIALIZATION,
            "Initializing pipeline components"
        )
        
        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize logging for this run
        log_file = self.config.output_dir / "pipeline.log"
        
        self.progress.complete_stage("Pipeline initialization complete")
        self._notify_progress()
    
    def _load_data(self):
        """Load data from source."""
        self.progress.start_stage(
            PipelineStage.DATA_LOADING,
            f"Loading data from {self.config.data_source}"
        )
        
        try:
            # Configure read options
            read_options = ReadOptions(**self.config.read_options)
            self.data_reader = DataReader(read_options)
            
            # Get file info first
            self.progress.update_stage(20, "Getting file information")
            file_info = self.data_reader.get_file_info(self.config.data_source)
            logger.info(f"File info: {file_info}")
            
            # Load data
            self.progress.update_stage(50, "Reading data file")
            self.results["raw_data"] = self.data_reader.read(
                self.config.data_source,
                format=self.config.data_format
            )
            
            # Apply sampling if configured
            if self.config.sample_size and len(self.results["raw_data"]) > self.config.sample_size:
                self.progress.update_stage(80, "Applying data sampling")
                if isinstance(self.results["raw_data"], pl.DataFrame):
                    self.results["raw_data"] = self.results["raw_data"].sample(n=self.config.sample_size)
                else:
                    self.results["raw_data"] = self.results["raw_data"].sample(n=self.config.sample_size)
            
            data_shape = self.results["raw_data"].shape
            self.progress.complete_stage(f"Data loaded: {data_shape[0]} rows, {data_shape[1]} columns")
            
        except Exception as e:
            raise DataSciencePlatformError(f"Data loading failed: {str(e)}") from e
        
        self._notify_progress()
    
    def _validate_data(self):
        """Validate loaded data."""
        self.progress.start_stage(
            PipelineStage.DATA_VALIDATION,
            "Validating data quality and structure"
        )
        
        try:
            # Convert to pandas for validation if needed
            data_for_validation = self.results["raw_data"]
            if isinstance(data_for_validation, pl.DataFrame):
                data_for_validation = data_for_validation.to_pandas()
            
            # Perform validation
            self.progress.update_stage(50, "Running data validation checks")
            validation_result = validate_dataframe(
                data_for_validation,
                strict_mode=self.config.strict_validation
            )
            
            self.results["validation_results"] = validation_result
            
            # Log validation results
            if validation_result.is_valid:
                message = "Data validation passed"
                logger.info(message)
            else:
                message = f"Data validation issues found: {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings"
                logger.warning(message)
                
                for error in validation_result.errors:
                    logger.error(f"Validation error: {error}")
                for warning in validation_result.warnings:
                    logger.warning(f"Validation warning: {warning}")
            
            self.progress.complete_stage(message)
            
        except Exception as e:
            raise DataSciencePlatformError(f"Data validation failed: {str(e)}") from e
        
        self._notify_progress()
    
    def _process_data(self):
        """Process and prepare data for analysis."""
        self.progress.start_stage(
            PipelineStage.DATA_PROCESSING,
            "Processing and preparing data"
        )
        
        try:
            # Start with raw data
            processed_data = self.results["raw_data"]
            
            # Convert to pandas for analysis if needed
            if isinstance(processed_data, pl.DataFrame):
                self.progress.update_stage(30, "Converting to pandas format")
                processed_data = processed_data.to_pandas()
            
            # Basic data cleaning
            self.progress.update_stage(60, "Performing data cleaning")
            
            # Remove completely empty rows and columns
            processed_data = processed_data.dropna(how='all')
            processed_data = processed_data.dropna(axis=1, how='all')
            
            # Store processed data
            self.results["processed_data"] = processed_data
            
            # Save intermediate results if configured
            if self.config.save_intermediate:
                self.progress.update_stage(80, "Saving intermediate results")
                output_file = self.config.output_dir / "processed_data.csv"
                processed_data.to_csv(output_file, index=False)
                logger.info(f"Processed data saved to: {output_file}")
            
            self.progress.complete_stage(
                f"Data processing complete: {processed_data.shape[0]} rows, {processed_data.shape[1]} columns"
            )
            
        except Exception as e:
            raise DataSciencePlatformError(f"Data processing failed: {str(e)}") from e
        
        self._notify_progress()
    
    def _analyze_data(self):
        """Perform comprehensive data analysis."""
        self.progress.start_stage(
            PipelineStage.ANALYSIS,
            "Running comprehensive data analysis"
        )
        
        try:
            data = self.results["processed_data"]
            
            # Generate comprehensive insights
            self.progress.update_stage(30, "Generating statistical insights")
            
            analysis_results = self.insight_generator.generate_comprehensive_insights(
                df=data,
                target_column=self.config.target_column,
                time_column=self.config.time_column,
                business_context=self.config.business_context
            )
            
            self.results["analysis_results"] = analysis_results
            
            # Generate insights report
            self.progress.update_stage(70, "Creating insights report")
            insights_report = self.insight_generator.export_insights_report(
                analysis_results, format='markdown'
            )
            self.results["insights_report"] = insights_report
            
            # Save insights report
            if self.config.save_intermediate or True:  # Always save insights
                self.progress.update_stage(90, "Saving insights report")
                report_file = self.config.output_dir / "insights_report.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(insights_report)
                logger.info(f"Insights report saved to: {report_file}")
            
            # Log key insights
            key_insights = analysis_results.get('key_insights', [])
            logger.info(f"Generated {len(key_insights)} key insights")
            for i, insight in enumerate(key_insights[:3], 1):  # Log top 3
                logger.info(f"Key insight {i}: {insight.get('title', 'Untitled')}")
            
            self.progress.complete_stage(
                f"Analysis complete: {len(key_insights)} key insights generated"
            )
            
        except Exception as e:
            raise DataSciencePlatformError(f"Data analysis failed: {str(e)}") from e
        
        self._notify_progress()
    
    def _generate_dashboard(self):
        """Generate interactive dashboard."""
        self.progress.start_stage(
            PipelineStage.DASHBOARD_GENERATION,
            "Generating interactive dashboard"
        )
        
        try:
            data = self.results["processed_data"]
            analysis_results = self.results["analysis_results"]
            
            # Configure dashboard
            self.progress.update_stage(20, "Configuring dashboard")
            
            dashboard_title = self.config.dashboard_title or f"Analytics Dashboard - {Path(self.config.data_source).stem}"
            
            self.dashboard_generator.set_config(
                title=dashboard_title,
                description=f"Comprehensive analytics dashboard generated from {self.config.data_source}",
                theme_switcher=True,
                responsive=True
            )
            
            # Add KPI cards from analysis results
            self.progress.update_stage(40, "Adding KPI cards")
            self._add_kpi_cards(analysis_results)
            
            # Add charts
            self.progress.update_stage(60, "Generating charts")
            self._add_analytical_charts(data, analysis_results)
            
            # Add data table
            self.progress.update_stage(80, "Adding data table")
            self.dashboard_generator.add_data_table(
                data=data.head(100),  # Limit to first 100 rows for performance
                table_id="main_data_table",
                title="Data Preview",
                searchable=True,
                sortable=True,
                paginated=True,
                page_size=10
            )
            
            # Generate HTML
            self.progress.update_stage(90, "Generating HTML dashboard")
            dashboard_file = self.config.output_dir / "dashboard.html"
            dashboard_html = self.dashboard_generator.generate_html(str(dashboard_file))
            
            self.results["dashboard_html"] = dashboard_html
            
            logger.info(f"Dashboard generated: {dashboard_file}")
            self.progress.complete_stage(f"Dashboard saved to: {dashboard_file}")
            
        except Exception as e:
            raise DataSciencePlatformError(f"Dashboard generation failed: {str(e)}") from e
        
        self._notify_progress()
    
    def _add_kpi_cards(self, analysis_results: Dict[str, Any]):
        """Add KPI cards to dashboard from analysis results."""
        try:
            overview = analysis_results.get('dataset_overview', {})
            quality = analysis_results.get('data_quality_assessment', {})
            
            # Dataset size KPI
            size_info = overview.get('size', {})
            if size_info:
                self.dashboard_generator.add_kpi_card(
                    title="Dataset Size",
                    value=f"{size_info.get('rows', 0):,} × {size_info.get('columns', 0)}",
                    subtitle="Rows × Columns",
                    icon="table"
                )
            
            # Data quality KPI
            if quality:
                quality_score = quality.get('overall_score', 0)
                self.dashboard_generator.add_kpi_card(
                    title="Data Quality",
                    value=f"{quality_score:.0f}/100",
                    subtitle=quality.get('assessment', 'Unknown'),
                    trend=quality_score - 70,  # Show as trend relative to "good" threshold
                    format_type="number",
                    icon="shield-check"
                )
            
            # Key insights count
            key_insights = analysis_results.get('key_insights', [])
            self.dashboard_generator.add_kpi_card(
                title="Key Insights",
                value=len(key_insights),
                subtitle="High Priority Findings",
                format_type="number",
                icon="lightbulb"
            )
            
            # Memory usage KPI
            memory_mb = size_info.get('memory_usage_mb', 0)
            if memory_mb > 0:
                self.dashboard_generator.add_kpi_card(
                    title="Memory Usage",
                    value=f"{memory_mb:.1f} MB",
                    subtitle="Dataset Size in Memory",
                    icon="memory"
                )
            
        except Exception as e:
            logger.warning(f"Failed to add KPI cards: {e}")
    
    def _add_analytical_charts(self, data: pd.DataFrame, analysis_results: Dict[str, Any]):
        """Add analytical charts to dashboard."""
        try:
            # Get numerical and categorical columns
            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = data.select_dtypes(include=['object', 'category']).columns.tolist()
            datetime_cols = data.select_dtypes(include=['datetime64']).columns.tolist()
            
            chart_count = 0
            max_charts = 8  # Limit number of charts
            
            # Add correlation heatmap if we have numeric columns
            if len(numeric_cols) >= 2 and chart_count < max_charts:
                correlation_data = data[numeric_cols].corr()
                if not correlation_data.empty:
                    self.dashboard_generator.add_chart(
                        chart_type="heatmap_chart",
                        data=correlation_data,
                        chart_id="correlation_heatmap",
                        title="Feature Correlation Matrix",
                        height=400
                    )
                    chart_count += 1
            
            # Add distribution charts for top numeric columns
            for i, col in enumerate(numeric_cols[:3]):  # Max 3 distribution charts
                if chart_count >= max_charts:
                    break
                    
                if data[col].notna().sum() > 0:  # Only if column has data
                    self.dashboard_generator.add_chart(
                        chart_type="histogram_chart",
                        data=data[[col]],
                        chart_id=f"dist_{col.replace(' ', '_')}",
                        title=f"Distribution of {col}",
                        height=300,
                        x_column=col
                    )
                    chart_count += 1
            
            # Add time series chart if we have datetime and numeric columns
            if datetime_cols and numeric_cols and chart_count < max_charts:
                time_col = datetime_cols[0]
                numeric_col = numeric_cols[0]
                
                # Create time series data
                ts_data = data[[time_col, numeric_col]].dropna()
                if len(ts_data) > 1:
                    self.dashboard_generator.add_chart(
                        chart_type="line_chart",
                        data=ts_data,
                        chart_id="time_series",
                        title=f"{numeric_col} over Time",
                        height=350,
                        x_column=time_col,
                        y_column=numeric_col
                    )
                    chart_count += 1
            
            # Add categorical charts
            for col in categorical_cols[:2]:  # Max 2 categorical charts
                if chart_count >= max_charts:
                    break
                    
                value_counts = data[col].value_counts().head(10)  # Top 10 categories
                if len(value_counts) > 1:
                    chart_data = pd.DataFrame({
                        'category': value_counts.index,
                        'count': value_counts.values
                    })
                    
                    self.dashboard_generator.add_chart(
                        chart_type="bar_chart",
                        data=chart_data,
                        chart_id=f"cat_{col.replace(' ', '_')}",
                        title=f"Distribution of {col}",
                        height=300,
                        x_column='category',
                        y_column='count'
                    )
                    chart_count += 1
            
            # Add scatter plot for numeric relationships
            if len(numeric_cols) >= 2 and chart_count < max_charts:
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                scatter_data = data[[x_col, y_col]].dropna()
                
                if len(scatter_data) > 1:
                    self.dashboard_generator.add_chart(
                        chart_type="scatter_chart",
                        data=scatter_data,
                        chart_id="scatter_plot",
                        title=f"{x_col} vs {y_col}",
                        height=350,
                        x_column=x_col,
                        y_column=y_col
                    )
                    chart_count += 1
            
            logger.info(f"Added {chart_count} charts to dashboard")
            
        except Exception as e:
            logger.warning(f"Failed to add analytical charts: {e}")
    
    def _finalize(self):
        """Finalize pipeline execution."""
        self.progress.start_stage(
            PipelineStage.FINALIZATION,
            "Finalizing pipeline execution"
        )
        
        try:
            # Generate execution summary
            self.progress.update_stage(50, "Generating execution summary")
            summary = self._generate_execution_summary()
            
            # Save summary
            summary_file = self.config.output_dir / "execution_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(summary, f, indent=2, default=str)
            
            logger.info(f"Execution summary saved to: {summary_file}")
            
            self.progress.complete_stage("Pipeline execution finalized")
            
        except Exception as e:
            logger.warning(f"Finalization warning: {e}")
            self.progress.complete_stage("Pipeline execution completed with warnings")
        
        self._notify_progress()
    
    def _generate_execution_summary(self) -> Dict[str, Any]:
        """Generate pipeline execution summary."""
        return {
            "pipeline_config": self.config.dict(),
            "execution_status": self.status.value,
            "progress": self.progress.to_dict(),
            "results_summary": {
                "data_shape": self.results["processed_data"].shape if self.results["processed_data"] is not None else None,
                "validation_passed": self.results["validation_results"].is_valid if self.results["validation_results"] else None,
                "insights_generated": len(self.results["analysis_results"].get("key_insights", [])) if self.results["analysis_results"] else 0,
                "dashboard_generated": self.results["dashboard_html"] is not None
            },
            "output_files": list(self.config.output_dir.glob("*"))
        }
    
    def get_results(self) -> Dict[str, Any]:
        """Get pipeline execution results.
        
        Returns:
            Dictionary containing all pipeline results
        """
        return {
            "status": self.status.value,
            "progress": self.progress.to_dict(),
            "config": self.config.dict(),
            "data_shape": self.results["processed_data"].shape if self.results["processed_data"] is not None else None,
            "validation_results": self.results["validation_results"].dict() if self.results["validation_results"] else None,
            "analysis_results": self.results["analysis_results"],
            "insights_report": self.results["insights_report"],
            "dashboard_generated": self.results["dashboard_html"] is not None,
            "output_directory": str(self.config.output_dir)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status.
        
        Returns:
            Dictionary with current status and progress
        """
        return {
            "status": self.status.value,
            "progress": self.progress.to_dict()
        }
    
    def cancel(self):
        """Cancel pipeline execution."""
        if self.status == PipelineStatus.RUNNING:
            self.status = PipelineStatus.CANCELLED
            self.progress.set_error("Pipeline execution cancelled by user")
            logger.info("Pipeline execution cancelled")
        
        self._notify_progress()
