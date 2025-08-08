"""QVF Scoring router."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..services.qvf_service import qvf_service
from ..auth import get_current_active_user, require_roles
from ..models.auth_models import User, UserRole

logger = logging.getLogger(__name__)
router = APIRouter()


class WorkItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    business_value: Optional[int] = Field(default=5, ge=1, le=10)
    technical_complexity: Optional[int] = Field(default=5, ge=1, le=10)
    story_points: Optional[int] = Field(default=3, ge=1, le=21)
    priority: Optional[str] = "Medium"
    risk_level: Optional[int] = Field(default=3, ge=1, le=10)


class QVFScoreRequest(BaseModel):
    work_items: List[WorkItem]
    criteria_weights: Optional[Dict[str, float]] = None


class QVFScoreResponse(BaseModel):
    scores: List[Dict[str, Any]]
    summary: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@router.post("/score", response_model=QVFScoreResponse)
async def calculate_qvf_scores(
    request: QVFScoreRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Calculate QVF scores for work items using the QVF core engine."""
    try:
        # Convert Pydantic models to dicts for service layer
        work_items_dict = [item.model_dump() for item in request.work_items]
        
        # Calculate scores using QVF service
        result = qvf_service.calculate_qvf_scores(
            work_items_dict, 
            request.criteria_weights
        )
        
        logger.info(f"Successfully calculated QVF scores for {len(request.work_items)} work items")
        
        return QVFScoreResponse(
            scores=result["scores"],
            summary=result["summary"],
            metadata=result.get("metadata")
        )
    
    except Exception as e:
        logger.error(f"QVF scoring error: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to calculate QVF scores: {str(e)}"
        )


@router.get("/criteria")
async def get_qvf_criteria():
    """Get available QVF scoring criteria from the QVF core engine."""
    try:
        criteria = qvf_service.get_available_criteria()
        logger.info("Successfully retrieved QVF criteria")
        return criteria
    
    except Exception as e:
        logger.error(f"Failed to get QVF criteria: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve QVF criteria: {str(e)}"
        )


@router.get("/health")
async def get_qvf_health():
    """Get health status of QVF service and core engine."""
    try:
        health_status = qvf_service.get_health_status()
        return health_status
    
    except Exception as e:
        logger.error(f"QVF health check failed: {str(e)}")
        return {
            "status": "error",
            "qvf_core": False,
            "criteria_engine": False,
            "ai_features": False,
            "error": str(e)
        }


@router.get("/test", response_model=QVFScoreResponse)
async def test_qvf_calculation():
    """Test QVF calculation with sample data."""
    try:
        result = qvf_service.test_qvf_calculation()
        logger.info("Successfully executed QVF test calculation")
        
        return QVFScoreResponse(
            scores=result["scores"],
            summary=result["summary"],
            metadata=result.get("metadata")
        )
    
    except Exception as e:
        logger.error(f"QVF test calculation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"QVF test calculation failed: {str(e)}"
        )