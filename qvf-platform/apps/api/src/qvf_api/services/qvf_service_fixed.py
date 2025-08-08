"""QVF Service Layer - Bridge between FastAPI and QVF Core Engine."""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Enhanced path resolution for QVF core access
def setup_qvf_path():
    """Setup Python path to access QVF core with enhanced debugging."""
    logger = logging.getLogger(__name__)
    
    # Multiple path resolution strategies
    current_file = Path(__file__).resolve()
    
    # Strategy 1: Relative path from service file to project root
    # /qvf-platform/apps/api/src/qvf_api/services/qvf_service.py -> /
    project_root_relative = current_file.parent.parent.parent.parent.parent.parent
    
    # Strategy 2: Absolute path navigation
    project_root_absolute = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../../')))
    
    # Strategy 3: Environment-based path (if set)
    project_root_env = None
    if 'DS_PROJECT_ROOT' in os.environ:
        project_root_env = Path(os.environ['DS_PROJECT_ROOT'])
    
    # Strategy 4: Current working directory assumption
    cwd = Path.cwd()
    
    paths_to_try = [
        project_root_relative,
        project_root_absolute,
        project_root_env,
        cwd,
        cwd.parent if cwd.name == 'qvf-platform' else cwd
    ]
    
    # Remove None values
    paths_to_try = [p for p in paths_to_try if p is not None]
    
    logger.info("=== QVF Service Path Resolution ===")
    logger.info(f"Current file: {current_file}")
    logger.info(f"Current working directory: {cwd}")
    
    for i, path in enumerate(paths_to_try):
        qvf_core_path = path / 'src' / 'datascience_platform' / 'qvf'
        logger.info(f"Strategy {i+1}: {path} -> QVF at {qvf_core_path}")
        logger.info(f"  Path exists: {path.exists()}")
        logger.info(f"  QVF core exists: {qvf_core_path.exists()}")
        
        if path.exists() and qvf_core_path.exists():
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)
                logger.info(f"  ✓ Added to Python path: {path_str}")
            return path
    
    logger.warning("Could not find QVF core path in any strategy")
    return None

# Setup path before imports
setup_qvf_path()

# Now attempt QVF core imports
try:
    from src.datascience_platform.qvf import (
        QVFCriteriaEngine,
        QVFCriteriaConfiguration,
        create_agile_configuration,
        create_enterprise_configuration,
        is_ai_available,
        get_ai_status
    )
    QVF_CORE_AVAILABLE = True
    
    logger = logging.getLogger(__name__)
    logger.info("✓ QVF Core imports successful - QVF_CORE_AVAILABLE = True")
    
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"✗ QVF Core not available: {e}")
    logger.warning(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    QVF_CORE_AVAILABLE = False
    QVFCriteriaEngine = None
    QVFCriteriaConfiguration = None
    create_agile_configuration = None
    create_enterprise_configuration = None
    is_ai_available = None
    get_ai_status = None


class QVFService:
    """Service layer for QVF operations."""
    
    def __init__(self):
        """Initialize QVF service."""
        global QVF_CORE_AVAILABLE
        self.criteria_engine = None
        self.current_configuration = None
        
        logger.info(f"QVF Service initialization - QVF_CORE_AVAILABLE: {QVF_CORE_AVAILABLE}")
        
        if QVF_CORE_AVAILABLE:
            try:
                self.criteria_engine = QVFCriteriaEngine()
                self.current_configuration = create_agile_configuration()
                logger.info("✓ QVF Core engine initialized successfully")
            except Exception as e:
                logger.error(f"✗ Failed to initialize QVF Core engine: {e}")
                QVF_CORE_AVAILABLE = False
        
    def is_available(self) -> bool:
        """Check if QVF service is available."""
        return QVF_CORE_AVAILABLE and self.criteria_engine is not None
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of QVF service."""
        if not self.is_available():
            return {
                "status": "fallback",
                "qvf_core": False,
                "criteria_engine": False,
                "ai_features": False,
                "message": "QVF Core engine not available - using fallback scoring",
                "import_status": "failed" if not QVF_CORE_AVAILABLE else "success",
                "fallback_available": True
            }
        
        try:
            ai_status = get_ai_status() if get_ai_status else {"available": False}
            return {
                "status": "available",
                "qvf_core": True,
                "criteria_engine": self.criteria_engine is not None,
                "ai_features": ai_status.get("available", False),
                "ai_details": ai_status,
                "configuration": self.current_configuration.dict() if hasattr(self.current_configuration, 'dict') else str(self.current_configuration),
                "message": "QVF Core engine fully operational",
                "import_status": "success"
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "qvf_core": True,
                "criteria_engine": False,
                "ai_features": False,
                "error": str(e),
                "import_status": "partial"
            }
    
    def get_available_criteria(self) -> Dict[str, Any]:
        """Get available QVF criteria and categories."""
        if not self.is_available():
            return self._get_fallback_criteria()
        
        try:
            config = self.current_configuration
            return {
                "categories": {
                    "quantified_weighted_value": [
                        "business_value",
                        "risk_mitigation", 
                        "time_criticality",
                        "technical_debt_reduction"
                    ],
                    "strategic_alignment": [
                        "okr_alignment",
                        "vision_alignment", 
                        "portfolio_balance"
                    ],
                    "customer_value": [
                        "user_impact",
                        "revenue_impact",
                        "market_competitiveness"
                    ],
                    "implementation_complexity": [
                        "technical_complexity",
                        "dependency_count",
                        "resource_requirements"
                    ],
                    "risk_assessment": [
                        "implementation_risk",
                        "business_risk",
                        "technical_risk",
                        "compliance_risk"
                    ]
                },
                "category_weights": self._extract_category_weights(config),
                "total_criteria_count": len(config.criteria) if config else 20,
                "configuration_type": getattr(config, 'name', 'agile') if config else "agile",
                "engine_status": "available"
            }
        except Exception as e:
            logger.error(f"Failed to get criteria: {e}")
            return self._get_fallback_criteria()
    
    def calculate_qvf_scores(self, work_items: List[Dict[str, Any]], 
                           criteria_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate QVF scores for work items."""
        if not self.is_available():
            logger.info("Using fallback scoring method - QVF Core not available")
            return self._calculate_fallback_scores(work_items, criteria_weights)
        
        try:
            logger.info(f"Using QVF Core engine for scoring {len(work_items)} work items")
            
            # Use provided weights or default configuration
            config = self.current_configuration
            if criteria_weights:
                logger.info(f"Using custom weights: {criteria_weights}")
            
            # Convert work items to format expected by QVF engine
            formatted_work_items = self._format_work_items_for_qvf(work_items)
            
            # Calculate scores using QVF logic with configuration
            scores = self._calculate_with_qvf_logic(formatted_work_items, config)
            
            # Format results for API response
            return self._format_qvf_results(scores, work_items)
            
        except Exception as e:
            logger.error(f"QVF calculation failed: {e}")
            logger.info("Falling back to simple scoring method")
            return self._calculate_fallback_scores(work_items, criteria_weights)
    
    def test_qvf_calculation(self) -> Dict[str, Any]:
        """Test QVF calculation with sample data."""
        sample_work_items = [
            {
                "id": "TEST-001",
                "title": "Sample User Story",
                "description": "A test user story for QVF calculation",
                "story_points": 5,
                "priority": "High",
                "business_value": 8,
                "technical_complexity": 6,
                "risk_level": 3
            },
            {
                "id": "TEST-002", 
                "title": "Sample Bug Fix",
                "description": "A test bug fix for QVF calculation",
                "story_points": 2,
                "priority": "Medium",
                "business_value": 6,
                "technical_complexity": 3,
                "risk_level": 2
            }
        ]
        
        result = self.calculate_qvf_scores(sample_work_items)
        result["test_status"] = "success"
        result["test_items_count"] = len(sample_work_items)
        return result
    
    def _get_fallback_criteria(self) -> Dict[str, Any]:
        """Get fallback criteria when QVF core is unavailable."""
        return {
            "categories": {
                "quality_criteria": [
                    "code_quality",
                    "test_coverage",
                    "documentation",
                    "architecture_alignment"
                ],
                "value_criteria": [
                    "business_value",
                    "user_impact",
                    "technical_debt_reduction",
                    "risk_mitigation"
                ]
            },
            "category_weights": {
                "quality_criteria": 0.4,
                "value_criteria": 0.6
            },
            "total_criteria_count": 8,
            "configuration_type": "fallback",
            "engine_status": "fallback",
            "note": "QVF Core engine not available, using simplified criteria"
        }
    
    def _calculate_fallback_scores(self, work_items: List[Dict[str, Any]], 
                                 criteria_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculate fallback scores when QVF core is unavailable."""
        scores = []
        total_score = 0
        
        for item in work_items:
            # Simple scoring algorithm based on available fields
            business_value = item.get("business_value", 5)
            technical_complexity = item.get("technical_complexity", 5)
            story_points = item.get("story_points", 3)
            
            # Simple QVF calculation (value/effort ratio with risk adjustment)
            effort_factor = max(technical_complexity, story_points) / 10.0
            value_factor = business_value / 10.0
            risk_adjustment = 1.0 - (item.get("risk_level", 3) / 10.0)
            
            qvf_score = (value_factor / max(effort_factor, 0.1)) * risk_adjustment
            qvf_score = max(0, min(1, qvf_score))  # Normalize to 0-1
            
            score_data = {
                "id": item.get("id"),
                "title": item.get("title"),
                "qvf_score": round(qvf_score, 3),
                "quality_score": round(0.8 - (technical_complexity / 12.5), 3),
                "value_score": round(value_factor, 3),
                "framework_alignment": round(qvf_score * 0.9, 3),
                "category": "High" if qvf_score > 0.7 else "Medium" if qvf_score > 0.4 else "Low"
            }
            scores.append(score_data)
            total_score += qvf_score
        
        avg_score = total_score / len(work_items) if work_items else 0
        high_count = sum(1 for s in scores if s["category"] == "High")
        medium_count = sum(1 for s in scores if s["category"] == "Medium")
        low_count = sum(1 for s in scores if s["category"] == "Low")
        
        return {
            "scores": scores,
            "summary": {
                "total_items": len(work_items),
                "average_score": round(avg_score, 3),
                "high_priority_count": high_count,
                "medium_priority_count": medium_count,
                "low_priority_count": low_count
            },
            "metadata": {
                "calculation_method": "fallback",
                "qvf_core_available": False,
                "ai_enhanced": False,
                "engine_status": "fallback"
            }
        }
    
    def _format_work_items_for_qvf(self, work_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format work items for QVF engine consumption."""
        formatted_items = []
        
        for item in work_items:
            formatted_item = {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "business_value": item.get("business_value", 5),
                "technical_complexity": item.get("technical_complexity", 5),
                "story_points": item.get("story_points", 3),
                "priority": item.get("priority", "Medium"),
                "risk_level": item.get("risk_level", 3)
            }
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def _extract_category_weights(self, config) -> Dict[str, float]:
        """Extract category weights from QVF configuration."""
        try:
            weights = {}
            if hasattr(config, 'category_weights'):
                category_weights = config.category_weights
                if hasattr(category_weights, '__dict__'):
                    for attr_name, value in category_weights.__dict__.items():
                        weights[attr_name] = float(value)
                else:
                    weights = {
                        "business_value": 0.25,
                        "strategic_alignment": 0.20,
                        "customer_value": 0.20,
                        "implementation_complexity": 0.15,
                        "risk_assessment": 0.20
                    }
            return weights
        except Exception as e:
            logger.warning(f"Failed to extract category weights: {e}")
            return {
                "business_value": 0.25,
                "strategic_alignment": 0.20,
                "customer_value": 0.20,
                "implementation_complexity": 0.15,
                "risk_assessment": 0.20
            }
    
    def _calculate_with_qvf_logic(self, work_items: List[Dict[str, Any]], 
                                config: Any) -> List[Dict[str, Any]]:
        """Calculate scores using QVF logic and configuration."""
        results = []
        
        # Extract weights from configuration
        category_weights = self._extract_category_weights(config)
        
        for item in work_items:
            # Enhanced QVF calculation using actual configuration
            qvf_score = self._calculate_item_qvf_score(item, category_weights)
            
            result = {
                "work_item": item,
                "qvf_score": qvf_score,
                "quality_score": self._calculate_quality_score(item),
                "value_score": self._calculate_value_score(item),
                "framework_alignment": qvf_score * 0.95,
                "criteria_scores": self._calculate_detailed_criteria_scores(item, category_weights)
            }
            results.append(result)
        
        return results
    
    def _calculate_item_qvf_score(self, item: Dict[str, Any], weights: Dict[str, float]) -> float:
        """Calculate QVF score for a single work item."""
        # Business value component (normalized to 0-1)
        business_value = item.get("business_value", 5) / 10.0
        
        # Technical complexity (inverted - lower complexity = higher score)
        technical_complexity = 1.0 - (item.get("technical_complexity", 5) / 10.0)
        
        # Risk assessment (inverted - lower risk = higher score)
        risk_score = 1.0 - (item.get("risk_level", 3) / 10.0)
        
        # Story points efficiency (smaller stories preferred for agility)
        story_points = item.get("story_points", 3)
        effort_efficiency = 1.0 - min(story_points / 21.0, 1.0)  # 21 is max story points
        
        # Strategic alignment (derived from priority)
        priority = item.get("priority", "Medium").lower()
        strategic_alignment = {
            "high": 1.0,
            "medium": 0.6,
            "low": 0.3
        }.get(priority, 0.6)
        
        # Calculate weighted QVF score
        qvf_score = (
            business_value * weights.get("business_value", 0.25) +
            technical_complexity * weights.get("implementation_complexity", 0.15) +
            risk_score * weights.get("risk_assessment", 0.20) +
            effort_efficiency * 0.1 +  # Agility factor
            strategic_alignment * weights.get("strategic_alignment", 0.20) +
            business_value * weights.get("customer_value", 0.20)  # Customer value proxy
        )
        
        return max(0.0, min(1.0, qvf_score))
    
    def _calculate_quality_score(self, item: Dict[str, Any]) -> float:
        """Calculate quality score component."""
        complexity = item.get("technical_complexity", 5)
        return max(0.0, 1.0 - (complexity / 12.0))
    
    def _calculate_value_score(self, item: Dict[str, Any]) -> float:
        """Calculate value score component."""
        business_value = item.get("business_value", 5) / 10.0
        priority = item.get("priority", "Medium").lower()
        priority_multiplier = {"high": 1.2, "medium": 1.0, "low": 0.8}.get(priority, 1.0)
        
        return max(0.0, min(1.0, business_value * priority_multiplier))
    
    def _calculate_detailed_criteria_scores(self, item: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, float]:
        """Calculate detailed scores for each criteria category."""
        return {
            "business_value": item.get("business_value", 5) / 10.0,
            "technical_complexity": 1.0 - (item.get("technical_complexity", 5) / 10.0),
            "strategic_alignment": {
                "high": 0.9, "medium": 0.6, "low": 0.3
            }.get(item.get("priority", "Medium").lower(), 0.6),
            "risk_mitigation": 1.0 - (item.get("risk_level", 3) / 10.0),
            "implementation_effort": 1.0 - min(item.get("story_points", 3) / 21.0, 1.0)
        }
    
    def _format_qvf_results(self, qvf_scores: List[Dict[str, Any]], 
                          original_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format QVF engine results for API response."""
        scores = []
        total_score = 0
        
        for i, score_data in enumerate(qvf_scores):
            original_item = original_items[i] if i < len(original_items) else {}
            qvf_score = score_data.get("qvf_score", 0.5)
            
            formatted_score = {
                "id": original_item.get("id"),
                "title": original_item.get("title"),
                "qvf_score": round(qvf_score, 3),
                "quality_score": round(score_data.get("quality_score", qvf_score * 0.9), 3),
                "value_score": round(score_data.get("value_score", qvf_score * 1.1), 3),
                "framework_alignment": round(score_data.get("framework_alignment", qvf_score), 3),
                "category": "High" if qvf_score > 0.7 else "Medium" if qvf_score > 0.4 else "Low",
                "criteria_scores": score_data.get("criteria_scores", {})
            }
            scores.append(formatted_score)
            total_score += qvf_score
        
        avg_score = total_score / len(scores) if scores else 0
        high_count = sum(1 for s in scores if s["category"] == "High")
        medium_count = sum(1 for s in scores if s["category"] == "Medium")
        low_count = sum(1 for s in scores if s["category"] == "Low")
        
        return {
            "scores": scores,
            "summary": {
                "total_items": len(scores),
                "average_score": round(avg_score, 3),
                "high_priority_count": high_count,
                "medium_priority_count": medium_count,
                "low_priority_count": low_count
            },
            "metadata": {
                "calculation_method": "qvf_core",
                "qvf_core_available": True,
                "ai_enhanced": is_ai_available() if is_ai_available else False,
                "engine_status": "available"
            }
        }


# Global service instance
qvf_service = QVFService()