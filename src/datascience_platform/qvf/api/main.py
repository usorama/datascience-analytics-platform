"""QVF Admin API Application

Main FastAPI application for QVF administration with integrated UI serving.
Provides both REST API endpoints and serves the React admin interface.

This module creates a production-ready FastAPI application that combines:
- QVF configuration management APIs
- Static file serving for the React admin UI
- CORS support for development
- Error handling and logging
- Health checks and monitoring
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

from .config_api import router as config_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="QVF Administration API",
    description="Quantified Value Framework Configuration Management System",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(config_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "qvf-admin-api",
        "version": "2.0.0"
    }

# Serve React admin interface (if built)
admin_ui_path = Path(__file__).parent.parent / "ui" / "admin" / "build"
if admin_ui_path.exists():
    # Mount static files
    app.mount("/static", StaticFiles(directory=str(admin_ui_path / "static")), name="static")
    
    @app.get("/admin", response_class=HTMLResponse)
    @app.get("/admin/{path:path}", response_class=HTMLResponse)
    async def serve_admin_ui(path: str = ""):
        """Serve the React admin interface."""
        index_file = admin_ui_path / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Admin UI not found")

# Development server function
def run_development_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = True
):
    """Run development server with hot reload."""
    logger.info(f"Starting QVF Admin API server at http://{host}:{port}")
    logger.info(f"API documentation available at http://{host}:{port}/api/docs")
    
    if admin_ui_path.exists():
        logger.info(f"Admin UI available at http://{host}:{port}/admin")
    else:
        logger.warning("Admin UI not built. Run the dashboard generator to create the UI.")
    
    uvicorn.run(
        "src.datascience_platform.qvf.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

# Production server configuration
def create_production_app():
    """Create production-configured FastAPI app."""
    # Disable docs in production
    prod_app = FastAPI(
        title="QVF Administration API",
        description="Quantified Value Framework Configuration Management System", 
        version="2.0.0",
        docs_url=None,  # Disable in production
        redoc_url=None  # Disable in production
    )
    
    # More restrictive CORS for production
    prod_app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://yourdomain.com"],  # Replace with actual domain
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
    
    # Include routers
    prod_app.include_router(config_router)
    
    # Production health check
    @prod_app.get("/health")
    async def prod_health_check():
        return {
            "status": "healthy",
            "service": "qvf-admin-api",
            "version": "2.0.0",
            "environment": "production"
        }
    
    return prod_app

if __name__ == "__main__":
    run_development_server()