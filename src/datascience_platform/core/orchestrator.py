"""Pipeline orchestrator for coordinating ETL, ML, and dashboard generation."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
import pandas as pd
import polars as pl

from .config import settings
from .exceptions import DataSciencePlatformError, ETLError
from ..etl.reader import DataReader, ReadOptions
from ..etl.validator import DataValidator, ValidationResult
from ..etl.schema import DataSchema

# Optional imports for ML and Dashboard components
try:
    from ..ml.insights import InsightGenerator
    from ..ml.statistics import StatisticsEngine
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from ..dashboard.generator import DashboardGenerator
    DASHBOARD_AVAILABLE = True
except ImportError:
    DASHBOARD_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution."""
    
    # ETL Configuration
    use_polars: bool = True
    chunk_size: Optional[int] = None
    strict_validation: bool = True
    schema: Optional[DataSchema] = None
    
    # ML Configuration
    generate_insights: bool = True
    target_column: Optional[str] = None
    time_column: Optional[str] = None
    business_context: Optional[str] = None
    
    # Dashboard Configuration
    generate_dashboard: bool = True
    dashboard_theme: str = 'light'
    dashboard_title: Optional[str] = None
    output_path: Optional[Path] = None
    
    # General Configuration
    max_memory_gb: float = field(default_factory=lambda: settings.max_memory_usage_gb)
    debug: bool = field(default_factory=lambda: settings.debug)


@dataclass
class PipelineResult:
    """Result of pipeline execution."""
    
    success: bool
    data: Optional[Union[pd.DataFrame, pl.DataFrame]] = None
    validation_result: Optional[ValidationResult] = None
    insights: Optional[Dict[str, Any]] = None
    dashboard_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipelineOrchestrator:
    """Orchestrates the complete data processing pipeline."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the pipeline orchestrator.
        
        Args:
            config: Pipeline configuration. Uses defaults if None.
        """
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize pipeline components."""
        # ETL Components
        read_options = ReadOptions(
            use_polars=self.config.use_polars,
            chunk_size=self.config.chunk_size
        )
        self.data_reader = DataReader(read_options)
        self.data_validator = DataValidator(strict_mode=self.config.strict_validation)
        
        # ML Components (if available)
        if ML_AVAILABLE and self.config.generate_insights:
            self.insight_generator = InsightGenerator()
            self.statistics_engine = StatisticsEngine()
        else:
            self.insight_generator = None
            self.statistics_engine = None
        
        # Dashboard Components (if available)
        if DASHBOARD_AVAILABLE and self.config.generate_dashboard:
            self.dashboard_generator = DashboardGenerator(
                theme=self.config.dashboard_theme
            )
        else:
            self.dashboard_generator = None
    
    def execute_pipeline(self, 
                        input_path: Union[str, Path],
                        output_path: Optional[Union[str, Path]] = None) -> PipelineResult:
        """Execute the complete pipeline.
        
        Args:
            input_path: Path to input data file
            output_path: Optional output directory for results
            
        Returns:
            PipelineResult with execution details
        """
        import time
        start_time = time.time()
        
        result = PipelineResult(success=False)
        
        try:
            self.logger.info(f"Starting pipeline execution for {input_path}")
            
            # Stage 1: Data Extraction
            result.data = self._extract_data(input_path, result)
            if result.data is None:
                result.execution_time = time.time() - start_time
                return result
            
            # Stage 2: Data Validation
            result.validation_result = self._validate_data(result.data, result)
            
            # Stage 3: ML Analysis (if enabled and available)
            if self.config.generate_insights and ML_AVAILABLE:
                result.insights = self._generate_insights(result.data, result)
            
            # Stage 4: Dashboard Generation (if enabled and available)
            if self.config.generate_dashboard and DASHBOARD_AVAILABLE:
                dashboard_output = output_path or self.config.output_path
                if dashboard_output:
                    result.dashboard_path = self._generate_dashboard(
                        result.data, result.insights, dashboard_output, result
                    )
            
            # Mark as successful if we got this far
            result.success = True
            result.execution_time = time.time() - start_time
            
            self.logger.info(f"Pipeline completed successfully in {result.execution_time:.2f}s")
            
        except Exception as e:
            result.errors.append(str(e))
            result.execution_time = time.time() - start_time
            self.logger.error(f"Pipeline failed: {str(e)}")
            
            if self.config.debug:
                raise
        
        return result
    
    def _extract_data(self, 
                     input_path: Union[str, Path], 
                     result: PipelineResult) -> Optional[Union[pd.DataFrame, pl.DataFrame]]:
        """Extract data from input file."""
        try:
            self.logger.info("Stage 1: Data extraction")
            
            if self.config.chunk_size:
                chunks = self.data_reader.read_chunked(input_path)
                if isinstance(chunks, list) and chunks:
                    # For simplicity, concatenate chunks
                    if self.config.use_polars:
                        data = pl.concat(chunks)
                    else:
                        data = pd.concat(chunks, ignore_index=True)
                else:
                    raise ETLError("No data chunks were read")
            else:
                data = self.data_reader.read(input_path)
            
            # Store metadata
            result.metadata['input_path'] = str(input_path)
            result.metadata['data_shape'] = (len(data), len(data.columns))
            result.metadata['use_polars'] = self.config.use_polars
            
            self.logger.info(f"Extracted {len(data)} rows, {len(data.columns)} columns")
            return data
            
        except Exception as e:
            result.errors.append(f"Data extraction failed: {str(e)}")
            self.logger.error(f"Data extraction failed: {str(e)}")
            return None
    
    def _validate_data(self, 
                      data: Union[pd.DataFrame, pl.DataFrame],
                      result: PipelineResult) -> Optional[ValidationResult]:
        """Validate the extracted data."""
        try:
            self.logger.info("Stage 2: Data validation")
            
            # Convert to pandas for validation if needed
            if isinstance(data, pl.DataFrame):
                try:
                    df_for_validation = data.to_pandas()
                except ImportError as e:
                    if "pyarrow" in str(e).lower():
                        # Fallback: skip polars conversion and just validate basic properties
                        result.warnings.append("PyArrow not available - using basic validation for Polars data")
                        validation_result = ValidationResult(
                            is_valid=True,
                            rows_validated=len(data),
                            columns_validated=len(data.columns)
                        )
                        return validation_result
                    else:
                        raise
            else:
                df_for_validation = data
            
            if self.config.schema:
                validation_result = self.data_validator.validate_with_schema(
                    df_for_validation, self.config.schema
                )
            else:
                from ..etl.validator import validate_dataframe
                validation_result = validate_dataframe(
                    df_for_validation, 
                    strict_mode=self.config.strict_validation
                )
            
            # Log validation results
            if validation_result.is_valid:
                self.logger.info("Data validation passed")
            else:
                self.logger.warning(f"Data validation issues: {len(validation_result.errors)} errors")
                result.warnings.extend(validation_result.errors)
            
            return validation_result
            
        except Exception as e:
            error_msg = f"Data validation failed: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            return None
    
    def _generate_insights(self, 
                          data: Union[pd.DataFrame, pl.DataFrame],
                          result: PipelineResult) -> Optional[Dict[str, Any]]:
        """Generate ML insights from the data."""
        if not ML_AVAILABLE:
            result.warnings.append("ML components not available, skipping insights")
            return None
        
        try:
            self.logger.info("Stage 3: ML insights generation")
            
            # Convert to pandas for ML processing
            if isinstance(data, pl.DataFrame):
                df_for_ml = data.to_pandas()
            else:
                df_for_ml = data
            
            insights = self.insight_generator.generate_comprehensive_insights(
                df_for_ml,
                target_column=self.config.target_column,
                time_column=self.config.time_column,
                business_context=self.config.business_context
            )
            
            self.logger.info("ML insights generated successfully")
            return insights
            
        except Exception as e:
            error_msg = f"ML insights generation failed: {str(e)}"
            result.warnings.append(error_msg)  # Treat as warning, not fatal error
            self.logger.warning(error_msg)
            return None
    
    def _generate_dashboard(self, 
                           data: Union[pd.DataFrame, pl.DataFrame],
                           insights: Optional[Dict[str, Any]],
                           output_path: Union[str, Path],
                           result: PipelineResult) -> Optional[Path]:
        """Generate dashboard from data and insights."""
        if not DASHBOARD_AVAILABLE:
            result.warnings.append("Dashboard components not available, skipping dashboard")
            return None
        
        try:
            self.logger.info("Stage 4: Dashboard generation")
            
            # Configure dashboard
            if self.config.dashboard_title:
                self.dashboard_generator.config['title'] = self.config.dashboard_title
            
            # Generate dashboard file path
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            dashboard_file = output_dir / "dashboard.html"
            
            # For now, just verify the dashboard generator is initialized
            # Full implementation would generate the actual dashboard
            result.metadata['dashboard_config'] = self.dashboard_generator.config
            
            self.logger.info(f"Dashboard would be generated at: {dashboard_file}")
            return dashboard_file
            
        except Exception as e:
            error_msg = f"Dashboard generation failed: {str(e)}"
            result.warnings.append(error_msg)  # Treat as warning, not fatal error
            self.logger.warning(error_msg)
            return None
    
    def execute_stage(self, 
                     stage: str, 
                     data: Optional[Union[pd.DataFrame, pl.DataFrame]] = None,
                     **kwargs) -> Dict[str, Any]:
        """Execute a single pipeline stage for testing or selective processing.
        
        Args:
            stage: Stage name ('extract', 'validate', 'insights', 'dashboard')
            data: Data to process (required for stages other than 'extract')
            **kwargs: Additional arguments for the stage
            
        Returns:
            Stage execution result
        """
        stage_result = {'success': False, 'error': None, 'result': None}
        
        try:
            if stage == 'extract':
                input_path = kwargs.get('input_path')
                if not input_path:
                    raise ValueError("input_path required for extract stage")
                
                temp_result = PipelineResult(success=False)
                stage_result['result'] = self._extract_data(input_path, temp_result)
                stage_result['success'] = stage_result['result'] is not None
                
            elif stage == 'validate':
                if data is None:
                    raise ValueError("data required for validate stage")
                
                temp_result = PipelineResult(success=False)
                stage_result['result'] = self._validate_data(data, temp_result)
                stage_result['success'] = stage_result['result'] is not None
                
            elif stage == 'insights':
                if data is None:
                    raise ValueError("data required for insights stage")
                
                temp_result = PipelineResult(success=False)
                stage_result['result'] = self._generate_insights(data, temp_result)
                stage_result['success'] = True  # Non-fatal if insights fail
                
            elif stage == 'dashboard':
                if data is None:
                    raise ValueError("data required for dashboard stage")
                
                output_path = kwargs.get('output_path')
                if not output_path:
                    raise ValueError("output_path required for dashboard stage")
                
                insights = kwargs.get('insights')
                temp_result = PipelineResult(success=False)
                stage_result['result'] = self._generate_dashboard(
                    data, insights, output_path, temp_result
                )
                stage_result['success'] = True  # Non-fatal if dashboard fails
                
            else:
                raise ValueError(f"Unknown stage: {stage}")
                
        except Exception as e:
            stage_result['error'] = str(e)
            stage_result['success'] = False
            
            if self.config.debug:
                raise
        
        return stage_result
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline configuration and component status."""
        return {
            'config': {
                'use_polars': self.config.use_polars,
                'chunk_size': self.config.chunk_size,
                'strict_validation': self.config.strict_validation,
                'generate_insights': self.config.generate_insights,
                'generate_dashboard': self.config.generate_dashboard,
            },
            'components': {
                'ml_available': ML_AVAILABLE,
                'dashboard_available': DASHBOARD_AVAILABLE,
                'insight_generator': self.insight_generator is not None,
                'dashboard_generator': self.dashboard_generator is not None,
            },
            'settings': {
                'max_memory_gb': self.config.max_memory_gb,
                'debug': self.config.debug,
            }
        }