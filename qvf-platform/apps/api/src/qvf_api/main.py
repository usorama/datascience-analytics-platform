"""QVF API FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, qvf_scoring, work_items
from .config import get_settings

settings = get_settings()

app = FastAPI(
    title="QVF Platform API",
    description="API for the Quality Value Framework Platform",
    version="0.1.0",
)

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
    """Root endpoint."""
    return {"message": "QVF Platform API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)