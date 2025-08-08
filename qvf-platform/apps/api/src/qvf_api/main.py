"""QVF API FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers import auth, qvf_scoring, work_items
from .config import get_settings
from .services import qvf_service
from .database import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="QVF Platform API",
    description="API for the Quality Value Framework Platform",
    version="0.1.0",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting QVF Platform API...")
    try:
        # Initialize database tables
        init_database()
        logger.info("Database initialized successfully")
        
        # Initialize test users and sample data
        from .init_db import create_test_users, create_sample_qvf_session
        from .database import SessionLocal
        
        db = SessionLocal()
        try:
            user_count = create_test_users(db)
            if user_count > 0:
                logger.info(f"Created {user_count} test users")
                create_sample_qvf_session(db)
                logger.info("Sample QVF session created")
            else:
                logger.info("Test users already exist")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Don't fail startup - the API can still work without database
    
    # Log QVF service status
    qvf_health = qvf_service.get_health_status()
    logger.info(f"QVF Service Status: {qvf_health.get('status')}")
    logger.info("QVF Platform API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down QVF Platform API...")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(qvf_scoring.router, prefix="/api/v1/qvf", tags=["qvf"])
app.include_router(work_items.router, prefix="/api/v1/work-items", tags=["work-items"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    qvf_status = qvf_service.get_health_status()
    return {
        "message": "QVF Platform API",
        "version": "0.1.0",
        "status": "operational",
        "qvf_core_available": qvf_status.get("qvf_core", False),
        "ai_features_available": qvf_status.get("ai_features", False),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth_login": "/api/v1/auth/token",
            "auth_me": "/api/v1/auth/me",
            "auth_health": "/api/v1/auth/health",
            "qvf_health": "/api/v1/qvf/health",
            "qvf_test": "/api/v1/qvf/test",
            "qvf_criteria": "/api/v1/qvf/criteria",
            "qvf_score": "/api/v1/qvf/score"
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    qvf_health = qvf_service.get_health_status()
    
    # Check database/authentication health
    auth_health = {"status": "healthy", "users": 0, "sessions": 0}
    try:
        from .database import SessionLocal
        from .models import User, UserSession
        
        db = SessionLocal()
        try:
            user_count = db.query(User).count()
            session_count = db.query(UserSession).filter(UserSession.is_active == True).count()
            auth_health.update({
                "status": "healthy",
                "users": user_count,
                "sessions": session_count
            })
        finally:
            db.close()
    except Exception as e:
        auth_health = {"status": "error", "error": str(e)}
    
    overall_status = "healthy"
    if qvf_health.get("status") == "error" or auth_health.get("status") == "error":
        overall_status = "unhealthy"
    elif qvf_health.get("status") == "degraded":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "api": "healthy",
        "qvf_engine": qvf_health,
        "authentication": auth_health,
        "timestamp": str(__import__('datetime').datetime.utcnow()),
        "version": "0.1.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)