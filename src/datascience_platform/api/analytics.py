"""FastAPI endpoints for the Analytics Pipeline.

Provides REST API endpoints for running analytics pipelines,
monitoring progress, and retrieving results.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from datascience_platform.core.config import settings
from datascience_platform.core.exceptions import DataSciencePlatformError
from datascience_platform.orchestrator.pipeline import AnalyticsPipeline, PipelineConfig, PipelineStatus
# Import models - will be created below if import fails
try:
    from datascience_platform.models.analytics import (
        AnalysisRequest,
        AnalysisResponse,
        PipelineStatusResponse,
        FileUploadResponse
    )
except ImportError:
    # Models will be imported when the module is properly loaded
    pass

logger = logging.getLogger(__name__)


# Global pipeline storage (in a production environment, use a proper database)
active_pipelines: Dict[str, AnalyticsPipeline] = {}
pipeline_results: Dict[str, Dict[str, Any]] = {}

# Thread pool for running pipelines
executor = ThreadPoolExecutor(max_workers=4)


def get_upload_dir() -> Path:
    """Get upload directory, creating if it doesn't exist."""
    upload_dir = settings.temp_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def get_output_dir() -> Path:
    """Get output directory, creating if it doesn't exist."""
    output_dir = settings.temp_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


async def run_pipeline_async(pipeline_id: str, pipeline: AnalyticsPipeline):
    """Run analytics pipeline asynchronously."""
    try:
        logger.info(f"Starting pipeline {pipeline_id}")
        
        # Run pipeline in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(executor, pipeline.execute)
        
        # Store results
        pipeline_results[pipeline_id] = results
        logger.info(f"Pipeline {pipeline_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline {pipeline_id} failed: {e}")
        pipeline_results[pipeline_id] = {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# FastAPI app setup
app = FastAPI(
    title="DataScience Analytics Platform API",
    description="REST API for running comprehensive data analytics pipelines",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """API root endpoint with basic information."""
    return """
    <html>
        <head>
            <title>DataScience Analytics Platform API</title>
        </head>
        <body>
            <h1>DataScience Analytics Platform API</h1>
            <p>Welcome to the DataScience Analytics Platform REST API.</p>
            <ul>
                <li><a href="/docs">API Documentation (Swagger UI)</a></li>
                <li><a href="/redoc">API Documentation (ReDoc)</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "active_pipelines": len(active_pipelines)
    }


@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload a data file for analysis.
    
    Args:
        file: The data file to upload
        
    Returns:
        FileUploadResponse with file information
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_extension = Path(file.filename).suffix.lower()
        supported_extensions = [".csv", ".json", ".xlsx", ".xls", ".parquet"]
        
        if file_extension not in supported_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Supported types: {supported_extensions}"
            )
        
        # Generate unique filename
        upload_dir = get_upload_dir()
        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        # Save file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"File uploaded: {file_path}")
        
        return FileUploadResponse(
            file_id=unique_filename,
            filename=file.filename,
            file_path=str(file_path),
            file_size=len(contents),
            file_type=file_extension,
            upload_timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Start a comprehensive analytics pipeline.
    
    Args:
        request: Analysis request configuration
        background_tasks: FastAPI background tasks
        
    Returns:
        AnalysisResponse with pipeline ID and initial status
    """
    try:
        # Generate unique pipeline ID
        pipeline_id = str(uuid.uuid4())
        
        # Validate data source
        data_source_path = Path(request.data_source)
        if not data_source_path.exists():
            # Check if it's an uploaded file ID
            upload_dir = get_upload_dir()
            uploaded_file_path = upload_dir / request.data_source
            if uploaded_file_path.exists():
                data_source_path = uploaded_file_path
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Data source not found: {request.data_source}"
                )
        
        # Create output directory for this pipeline
        pipeline_output_dir = get_output_dir() / pipeline_id
        pipeline_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create pipeline configuration
        pipeline_config = PipelineConfig(
            data_source=data_source_path,
            data_format=request.data_format,
            read_options=request.read_options or {},
            target_column=request.target_column,
            time_column=request.time_column,
            business_context=request.business_context,
            validate_data=request.validate_data,
            strict_validation=request.strict_validation,
            sample_size=request.sample_size,
            ml_enabled=request.ml_enabled,
            ml_time_limit=request.ml_time_limit,
            generate_dashboard=request.generate_dashboard,
            dashboard_theme=request.dashboard_theme,
            dashboard_title=request.dashboard_title,
            output_dir=pipeline_output_dir,
            save_intermediate=request.save_intermediate,
            export_formats=request.export_formats
        )
        
        # Create and store pipeline
        pipeline = AnalyticsPipeline(pipeline_config)
        active_pipelines[pipeline_id] = pipeline
        
        # Start pipeline in background
        background_tasks.add_task(run_pipeline_async, pipeline_id, pipeline)
        
        logger.info(f"Started analytics pipeline {pipeline_id} for: {data_source_path}")
        
        return AnalysisResponse(
            pipeline_id=pipeline_id,
            status=PipelineStatus.RUNNING.value,
            message="Analytics pipeline started successfully",
            start_timestamp=datetime.now().isoformat(),
            estimated_duration_minutes=5,  # Rough estimate
            output_directory=str(pipeline_output_dir)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")


@app.get("/analyze/{pipeline_id}/status", response_model=PipelineStatusResponse)
async def get_analysis_status(pipeline_id: str):
    """Get the current status of an analytics pipeline.
    
    Args:
        pipeline_id: Unique identifier for the pipeline
        
    Returns:
        PipelineStatusResponse with current status and progress
    """
    try:
        # Check if pipeline exists
        if pipeline_id not in active_pipelines and pipeline_id not in pipeline_results:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        # Get current status
        if pipeline_id in active_pipelines:
            pipeline = active_pipelines[pipeline_id]
            status_info = pipeline.get_status()
            
            return PipelineStatusResponse(
                pipeline_id=pipeline_id,
                status=status_info["status"],
                progress=status_info["progress"],
                message=status_info["progress"].get("stage_messages", {}).get(status_info["progress"].get("current_stage"), "")
            )
        
        # Pipeline completed - return final status
        results = pipeline_results[pipeline_id]
        return PipelineStatusResponse(
            pipeline_id=pipeline_id,
            status=results.get("status", "completed"),
            progress=results.get("progress", {}),
            message="Pipeline execution completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline status: {str(e)}")


@app.get("/analyze/{pipeline_id}/results")
async def get_analysis_results(pipeline_id: str):
    """Get the results of a completed analytics pipeline.
    
    Args:
        pipeline_id: Unique identifier for the pipeline
        
    Returns:
        Complete pipeline results including insights and analysis
    """
    try:
        # Check if pipeline exists and is completed
        if pipeline_id not in pipeline_results:
            if pipeline_id in active_pipelines:
                pipeline = active_pipelines[pipeline_id]
                if pipeline.status != PipelineStatus.COMPLETED:
                    raise HTTPException(
                        status_code=202,
                        detail=f"Pipeline {pipeline_id} is still running. Check status endpoint for progress."
                    )
                # Pipeline just completed, get results
                results = pipeline.get_results()
            else:
                raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        else:
            results = pipeline_results[pipeline_id]
        
        return JSONResponse(content=results)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get pipeline results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pipeline results: {str(e)}")


@app.get("/analyze/{pipeline_id}/dashboard")
async def get_dashboard(pipeline_id: str):
    """Get the generated dashboard for a completed pipeline.
    
    Args:
        pipeline_id: Unique identifier for the pipeline
        
    Returns:
        HTML dashboard file
    """
    try:
        # Check if pipeline exists and is completed
        if pipeline_id not in pipeline_results:
            if pipeline_id in active_pipelines:
                pipeline = active_pipelines[pipeline_id]
                if pipeline.status != PipelineStatus.COMPLETED:
                    raise HTTPException(
                        status_code=202,
                        detail=f"Pipeline {pipeline_id} is still running. Dashboard not ready yet."
                    )
            else:
                raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        # Look for dashboard file
        output_dir = get_output_dir() / pipeline_id
        dashboard_file = output_dir / "dashboard.html"
        
        if not dashboard_file.exists():
            raise HTTPException(status_code=404, detail="Dashboard file not found")
        
        return FileResponse(
            str(dashboard_file),
            media_type="text/html",
            filename=f"dashboard_{pipeline_id}.html"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")


@app.get("/analyze/{pipeline_id}/insights")
async def get_insights_report(pipeline_id: str):
    """Get the insights report for a completed pipeline.
    
    Args:
        pipeline_id: Unique identifier for the pipeline
        
    Returns:
        Markdown insights report file
    """
    try:
        # Check if pipeline exists and is completed
        if pipeline_id not in pipeline_results:
            if pipeline_id in active_pipelines:
                pipeline = active_pipelines[pipeline_id]
                if pipeline.status != PipelineStatus.COMPLETED:
                    raise HTTPException(
                        status_code=202,
                        detail=f"Pipeline {pipeline_id} is still running. Insights not ready yet."
                    )
            else:
                raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        # Look for insights report file
        output_dir = get_output_dir() / pipeline_id
        insights_file = output_dir / "insights_report.md"
        
        if not insights_file.exists():
            raise HTTPException(status_code=404, detail="Insights report file not found")
        
        return FileResponse(
            str(insights_file),
            media_type="text/markdown",
            filename=f"insights_{pipeline_id}.md"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get insights report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights report: {str(e)}")


@app.delete("/analyze/{pipeline_id}")
async def cancel_analysis(pipeline_id: str):
    """Cancel a running analytics pipeline.
    
    Args:
        pipeline_id: Unique identifier for the pipeline
        
    Returns:
        Cancellation confirmation
    """
    try:
        if pipeline_id not in active_pipelines:
            raise HTTPException(status_code=404, detail=f"Pipeline {pipeline_id} not found")
        
        pipeline = active_pipelines[pipeline_id]
        pipeline.cancel()
        
        return {
            "pipeline_id": pipeline_id,
            "status": "cancelled",
            "message": "Pipeline cancellation requested",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel pipeline: {str(e)}")


@app.get("/pipelines")
async def list_pipelines():
    """List all pipelines (active and completed).
    
    Returns:
        List of all pipelines with their current status
    """
    try:
        pipelines = []
        
        # Add active pipelines
        for pipeline_id, pipeline in active_pipelines.items():
            status_info = pipeline.get_status()
            pipelines.append({
                "pipeline_id": pipeline_id,
                "status": status_info["status"],
                "progress": status_info["progress"].get("overall_progress", 0),
                "data_source": str(pipeline.config.data_source),
                "start_time": status_info["progress"].get("start_time"),
                "type": "active"
            })
        
        # Add completed pipelines
        for pipeline_id, results in pipeline_results.items():
            pipelines.append({
                "pipeline_id": pipeline_id,
                "status": results.get("status", "completed"),
                "progress": 100.0 if results.get("status") == "completed" else 0.0,
                "data_source": results.get("config", {}).get("data_source"),
                "start_time": results.get("progress", {}).get("start_time"),
                "end_time": results.get("progress", {}).get("end_time"),
                "type": "completed"
            })
        
        return {
            "pipelines": pipelines,
            "total_count": len(pipelines),
            "active_count": len(active_pipelines),
            "completed_count": len(pipeline_results)
        }
        
    except Exception as e:
        logger.error(f"Failed to list pipelines: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list pipelines: {str(e)}")


@app.get("/config")
async def get_configuration():
    """Get current platform configuration.
    
    Returns:
        Current configuration settings
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "supported_formats": settings.supported_formats,
        "api_host": settings.api_host,
        "api_port": settings.api_port,
        "max_memory_usage_gb": settings.max_memory_usage_gb,
        "ml_random_seed": settings.ml_random_seed,
        "upload_directory": str(get_upload_dir()),
        "output_directory": str(get_output_dir())
    }


# Create router for modular usage
from fastapi import APIRouter
router = APIRouter()

# Add all routes to router
for route in app.routes:
    if hasattr(route, 'methods'):
        router.routes.append(route)
