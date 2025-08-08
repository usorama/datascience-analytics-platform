"""QVF Configuration Management API

FastAPI endpoints for QVF configuration management including:
- CRUD operations for QVF configurations
- Real-time validation and feedback
- Configuration presets management
- Export/import functionality
- Weight validation and normalization

This API serves the QVF admin interface and provides enterprise-grade
configuration management for the Quantified Value Framework.
"""

import logging
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..core.criteria import (
    QVFCriteriaEngine, QVFCriteriaConfiguration, QVFCriterion,
    CriteriaWeights, CriteriaCategory, QVFValidationError,
    create_agile_configuration, create_enterprise_configuration,
    create_startup_configuration
)

logger = logging.getLogger(__name__)

# Create FastAPI router
router = APIRouter(prefix="/api/v1/qvf", tags=["QVF Configuration"])

# Global QVF engine instance
qvf_engine = QVFCriteriaEngine()

# In-memory storage for configurations (in production, use database)
_configuration_storage: Dict[str, QVFCriteriaConfiguration] = {}


# Pydantic models for API requests/responses
class ConfigurationCreateRequest(BaseModel):
    """Request model for creating new QVF configuration."""
    name: str = Field(..., description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    criteria: Optional[List[Dict[str, Any]]] = Field(None, description="Custom criteria definitions")
    category_weights: Optional[Dict[str, float]] = Field(None, description="Custom category weights")
    preset_type: Optional[str] = Field(None, description="Preset type: agile, enterprise, startup")


class ConfigurationUpdateRequest(BaseModel):
    """Request model for updating QVF configuration."""
    name: Optional[str] = Field(None, description="Configuration name")
    description: Optional[str] = Field(None, description="Configuration description")
    criteria: Optional[List[Dict[str, Any]]] = Field(None, description="Updated criteria")
    category_weights: Optional[Dict[str, float]] = Field(None, description="Updated category weights")


class WeightValidationRequest(BaseModel):
    """Request model for validating criteria weights."""
    category_weights: Dict[str, float] = Field(..., description="Category weights to validate")
    criteria_weights: Optional[Dict[str, Dict[str, float]]] = Field(None, description="Individual criteria weights by category")


class ValidationResponse(BaseModel):
    """Response model for validation results."""
    is_valid: bool = Field(..., description="Whether configuration is valid")
    issues: List[str] = Field(..., description="List of validation issues")
    normalized_weights: Optional[Dict[str, float]] = Field(None, description="Normalized weights if applicable")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")


class ConfigurationSummary(BaseModel):
    """Summary model for configuration listing."""
    configuration_id: str
    name: str
    description: Optional[str]
    created_date: datetime
    last_modified: datetime
    criteria_count: int
    is_valid: bool


# Initialize default configurations on startup
def initialize_default_configurations():
    """Initialize default QVF configurations."""
    try:
        # Create and store default configurations
        default_config = qvf_engine.get_default_configuration()
        agile_config = create_agile_configuration()
        enterprise_config = create_enterprise_configuration()
        startup_config = create_startup_configuration()
        
        _configuration_storage[default_config.configuration_id] = default_config
        _configuration_storage[agile_config.configuration_id] = agile_config
        _configuration_storage[enterprise_config.configuration_id] = enterprise_config
        _configuration_storage[startup_config.configuration_id] = startup_config
        
        logger.info(f"Initialized {len(_configuration_storage)} default QVF configurations")
        
    except Exception as e:
        logger.error(f"Failed to initialize default configurations: {e}")


# Configuration CRUD endpoints
@router.get("/configurations", response_model=List[ConfigurationSummary])
async def list_configurations() -> List[ConfigurationSummary]:
    """List all QVF configurations with summary information."""
    try:
        if not _configuration_storage:
            initialize_default_configurations()
        
        summaries = []
        for config in _configuration_storage.values():
            # Validate configuration to get is_valid status
            validation_issues = qvf_engine.validate_configuration(config)
            
            summary = ConfigurationSummary(
                configuration_id=config.configuration_id,
                name=config.name,
                description=config.description,
                created_date=config.created_date,
                last_modified=config.last_modified,
                criteria_count=len(config.get_active_criteria()),
                is_valid=len(validation_issues) == 0
            )
            summaries.append(summary)
        
        # Sort by last modified date
        summaries.sort(key=lambda x: x.last_modified, reverse=True)
        
        logger.info(f"Listed {len(summaries)} QVF configurations")
        return summaries
        
    except Exception as e:
        logger.error(f"Failed to list configurations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list configurations: {str(e)}")


@router.get("/configurations/{configuration_id}")
async def get_configuration(configuration_id: str) -> Dict[str, Any]:
    """Get detailed QVF configuration by ID."""
    try:
        if configuration_id not in _configuration_storage:
            raise HTTPException(status_code=404, detail=f"Configuration '{configuration_id}' not found")
        
        config = _configuration_storage[configuration_id]
        
        # Convert to dictionary for JSON response
        config_dict = config.model_dump()
        
        # Add validation status
        validation_issues = qvf_engine.validate_configuration(config)
        config_dict['validation'] = {
            'is_valid': len(validation_issues) == 0,
            'issues': validation_issues
        }
        
        logger.info(f"Retrieved configuration '{configuration_id}'")
        return config_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get configuration {configuration_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")


@router.post("/configurations", response_model=Dict[str, Any])
async def create_configuration(request: ConfigurationCreateRequest) -> Dict[str, Any]:
    """Create new QVF configuration."""
    try:
        # Handle preset creation
        if request.preset_type:
            if request.preset_type.lower() == "agile":
                config = create_agile_configuration()
            elif request.preset_type.lower() == "enterprise":
                config = create_enterprise_configuration()
            elif request.preset_type.lower() == "startup":
                config = create_startup_configuration()
            else:
                raise HTTPException(status_code=400, detail=f"Unknown preset type: {request.preset_type}")
            
            # Override name and description if provided
            if request.name:
                config.name = request.name
            if request.description:
                config.description = request.description
                
        else:
            # Create custom configuration
            custom_criteria = None
            custom_weights = None
            
            if request.criteria:
                # Convert criteria dictionaries to QVFCriterion objects
                custom_criteria = []
                for criteria_dict in request.criteria:
                    criterion = QVFCriterion(**criteria_dict)
                    custom_criteria.append(criterion)
            
            if request.category_weights:
                custom_weights = CriteriaWeights(**request.category_weights)
            
            config = qvf_engine.create_custom_configuration(
                name=request.name,
                description=request.description or "",
                custom_criteria=custom_criteria,
                custom_weights=custom_weights
            )
        
        # Store configuration
        _configuration_storage[config.configuration_id] = config
        
        # Validate and return
        validation_issues = qvf_engine.validate_configuration(config)
        
        result = config.model_dump()
        result['validation'] = {
            'is_valid': len(validation_issues) == 0,
            'issues': validation_issues
        }
        
        logger.info(f"Created configuration '{config.configuration_id}' - {config.name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create configuration: {str(e)}")


@router.put("/configurations/{configuration_id}")
async def update_configuration(configuration_id: str, request: ConfigurationUpdateRequest) -> Dict[str, Any]:
    """Update existing QVF configuration."""
    try:
        if configuration_id not in _configuration_storage:
            raise HTTPException(status_code=404, detail=f"Configuration '{configuration_id}' not found")
        
        config = _configuration_storage[configuration_id]
        
        # Update fields
        if request.name:
            config.name = request.name
        if request.description is not None:
            config.description = request.description
        
        if request.category_weights:
            config.category_weights = CriteriaWeights(**request.category_weights)
            config.calculate_global_weights()
        
        if request.criteria:
            # Replace criteria
            new_criteria = []
            for criteria_dict in request.criteria:
                criterion = QVFCriterion(**criteria_dict)
                new_criteria.append(criterion)
            config.criteria = new_criteria
            config.calculate_global_weights()
        
        # Update last modified
        config.last_modified = datetime.now()
        
        # Store updated configuration
        _configuration_storage[configuration_id] = config
        
        # Validate and return
        validation_issues = qvf_engine.validate_configuration(config)
        
        result = config.model_dump()
        result['validation'] = {
            'is_valid': len(validation_issues) == 0,
            'issues': validation_issues
        }
        
        logger.info(f"Updated configuration '{configuration_id}'")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration {configuration_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@router.delete("/configurations/{configuration_id}")
async def delete_configuration(configuration_id: str) -> Dict[str, str]:
    """Delete QVF configuration."""
    try:
        if configuration_id not in _configuration_storage:
            raise HTTPException(status_code=404, detail=f"Configuration '{configuration_id}' not found")
        
        config_name = _configuration_storage[configuration_id].name
        del _configuration_storage[configuration_id]
        
        logger.info(f"Deleted configuration '{configuration_id}' - {config_name}")
        return {"message": f"Configuration '{config_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete configuration {configuration_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete configuration: {str(e)}")


@router.get("/configurations/{configuration_id}/export")
async def export_configuration(configuration_id: str) -> Dict[str, Any]:
    """Export QVF configuration for backup or sharing."""
    try:
        if configuration_id not in _configuration_storage:
            raise HTTPException(status_code=404, detail=f"Configuration '{configuration_id}' not found")
        
        config = _configuration_storage[configuration_id]
        exported_data = qvf_engine.export_configuration(config)
        
        # Add export metadata
        exported_data['export_metadata'] = {
            'exported_at': datetime.now().isoformat(),
            'exported_by': 'qvf-admin-api',
            'version': '2.0.0'
        }
        
        logger.info(f"Exported configuration '{configuration_id}'")
        return exported_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export configuration {configuration_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export configuration: {str(e)}")


# Validation endpoints
@router.post("/validate/weights", response_model=ValidationResponse)
async def validate_weights(request: WeightValidationRequest) -> ValidationResponse:
    """Validate criteria weights and provide real-time feedback."""
    try:
        issues = []
        suggestions = []
        normalized_weights = None
        
        # Validate category weights
        try:
            weights_obj = CriteriaWeights(**request.category_weights)
            # If we got here, weights are valid
            normalized_weights = request.category_weights
        except Exception as e:
            issues.append(f"Category weights validation failed: {str(e)}")
            
            # Try to normalize weights
            total = sum(request.category_weights.values())
            if total > 0:
                normalized_weights = {k: v/total for k, v in request.category_weights.items()}
                suggestions.append(f"Weights sum to {total:.3f}, consider normalizing to sum to 1.0")
            else:
                suggestions.append("All weights are zero, assign positive values to categories")
        
        # Validate individual criteria weights if provided
        if request.criteria_weights:
            for category, criteria_weights in request.criteria_weights.items():
                criteria_total = sum(criteria_weights.values())
                if abs(criteria_total - 1.0) > 1e-6:
                    issues.append(f"Criteria weights in category '{category}' sum to {criteria_total:.3f}, should sum to 1.0")
                    
                if criteria_total == 0:
                    issues.append(f"All criteria weights in category '{category}' are zero")
        
        # Generate suggestions
        if normalized_weights:
            # Check for extreme weights
            for category, weight in normalized_weights.items():
                if weight > 0.6:
                    suggestions.append(f"Category '{category}' has high weight ({weight:.1%}), consider balancing")
                elif weight < 0.05:
                    suggestions.append(f"Category '{category}' has very low weight ({weight:.1%}), consider if it's needed")
        
        is_valid = len(issues) == 0
        
        logger.info(f"Weight validation completed: {len(issues)} issues, {len(suggestions)} suggestions")
        
        return ValidationResponse(
            is_valid=is_valid,
            issues=issues,
            normalized_weights=normalized_weights,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"Weight validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/validate/configuration/{configuration_id}", response_model=ValidationResponse)
async def validate_configuration(configuration_id: str) -> ValidationResponse:
    """Validate complete QVF configuration."""
    try:
        if configuration_id not in _configuration_storage:
            raise HTTPException(status_code=404, detail=f"Configuration '{configuration_id}' not found")
        
        config = _configuration_storage[configuration_id]
        issues = qvf_engine.validate_configuration(config)
        
        suggestions = []
        if issues:
            suggestions.append("Review configuration settings and ensure all weights sum to 1.0")
            suggestions.append("Verify that data sources match your Azure DevOps work item fields")
        else:
            suggestions.append("Configuration is valid and ready for use")
        
        logger.info(f"Configuration validation completed for '{configuration_id}': {len(issues)} issues")
        
        return ValidationResponse(
            is_valid=len(issues) == 0,
            issues=issues,
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# Preset management endpoints
@router.get("/presets")
async def list_presets() -> Dict[str, Any]:
    """List available QVF configuration presets."""
    presets = {
        "agile": {
            "name": "Agile Team Configuration",
            "description": "Optimized for Agile teams focusing on customer value and business outcomes",
            "category_weights": {
                "business_value": 0.30,
                "customer_value": 0.30,
                "implementation_complexity": 0.20,
                "strategic_alignment": 0.15,
                "risk_assessment": 0.05
            }
        },
        "enterprise": {
            "name": "Enterprise Portfolio Configuration", 
            "description": "Optimized for enterprise portfolio management with strategic alignment focus",
            "category_weights": {
                "strategic_alignment": 0.35,
                "business_value": 0.25,
                "risk_assessment": 0.20,
                "customer_value": 0.15,
                "implementation_complexity": 0.05
            }
        },
        "startup": {
            "name": "Startup Configuration",
            "description": "Optimized for startups focusing on customer value and implementation speed", 
            "category_weights": {
                "customer_value": 0.35,
                "business_value": 0.30,
                "implementation_complexity": 0.25,
                "strategic_alignment": 0.07,
                "risk_assessment": 0.03
            }
        }
    }
    
    return {"presets": presets}


@router.post("/presets/{preset_type}")
async def create_preset_configuration(preset_type: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Create configuration from preset."""
    request = ConfigurationCreateRequest(
        name=name or f"QVF {preset_type.title()} Configuration",
        preset_type=preset_type
    )
    
    return await create_configuration(request)


# Utility endpoints
@router.get("/categories")
async def get_criteria_categories() -> Dict[str, Any]:
    """Get available QVF criteria categories."""
    categories = {}
    for category in CriteriaCategory:
        categories[category.value] = {
            "name": category.value.replace('_', ' ').title(),
            "description": f"Criteria related to {category.value.replace('_', ' ')}"
        }
    
    return {"categories": categories}


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "qvf-configuration-api",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Initialize configurations on module import
try:
    initialize_default_configurations()
except Exception as e:
    logger.warning(f"Failed to initialize configurations during import: {e}")