"""Azure DevOps Work Item Models

This module defines the data models for ADO work items with support for
hierarchical relationships and business value normalization.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
import numpy as np


class WorkItemType(str, Enum):
    """ADO work item types in hierarchical order."""
    EPIC = "Epic"
    PIO = "PIO"  # Program Increment Objective
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    BUG = "Bug"


class WorkItemState(str, Enum):
    """ADO work item states."""
    NEW = "New"
    ACTIVE = "Active"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"
    DEFERRED = "Deferred"
    REMOVED = "Removed"


class TeamMetrics(BaseModel):
    """Team-specific metrics for a work item."""
    team_name: str
    velocity: Optional[float] = Field(None, description="Team velocity in story points per PI")
    capacity: Optional[float] = Field(None, description="Team capacity for current PI")
    historical_completion_rate: Optional[float] = Field(None, ge=0, le=1)
    
    
class ADOWorkItem(BaseModel):
    """Base model for Azure DevOps work items."""
    
    # Core fields
    work_item_id: int = Field(..., description="Unique ADO work item ID")
    title: str = Field(..., description="Work item title")
    work_item_type: WorkItemType
    state: WorkItemState
    
    # Hierarchical relationships
    parent_id: Optional[int] = Field(None, description="Parent work item ID")
    children_ids: List[int] = Field(default_factory=list, description="Child work item IDs")
    
    # Business value fields
    business_value_raw: Optional[float] = Field(None, ge=0, description="Original business value")
    business_value_normalized: Optional[float] = Field(None, ge=0, le=1, description="Normalized business value (0-1)")
    
    # Effort and complexity
    story_points: Optional[float] = Field(None, ge=0, description="Story points estimate")
    effort_hours: Optional[float] = Field(None, ge=0, description="Effort in hours")
    complexity_score: Optional[float] = Field(None, ge=0, le=100, description="Complexity score (0-100)")
    risk_score: Optional[float] = Field(None, ge=0, le=100, description="Risk score (0-100)")
    
    # Time fields
    created_date: Optional[datetime] = None
    activated_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    closed_date: Optional[datetime] = None
    target_date: Optional[datetime] = None
    
    # Planning fields
    iteration_path: Optional[str] = Field(None, description="Sprint/Iteration path")
    area_path: Optional[str] = Field(None, description="Area/Team path")
    assigned_to: Optional[str] = Field(None, description="Assigned user")
    pi_number: Optional[int] = Field(None, description="Program Increment number")
    
    # Strategic alignment
    strategy_pillar: Optional[str] = Field(None, description="Strategic pillar alignment")
    okr_alignment: Optional[str] = Field(None, description="OKR alignment")
    
    # Metrics
    cycle_time_days: Optional[float] = Field(None, ge=0, description="Cycle time in days")
    lead_time_days: Optional[float] = Field(None, ge=0, description="Lead time in days")
    blocked_days: Optional[float] = Field(None, ge=0, description="Days blocked")
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    team_metrics: Optional[TeamMetrics] = None
    
    @validator('business_value_normalized')
    def validate_normalized_value(cls, v, values):
        """Ensure normalized value is between 0 and 1."""
        if v is not None and 'business_value_raw' in values and values['business_value_raw'] is not None:
            # If raw value exists but normalized doesn't, calculate it
            if v is None:
                return min(values['business_value_raw'] / 100.0, 1.0)
        return v
    
    def calculate_cycle_time(self) -> Optional[float]:
        """Calculate cycle time from activated to resolved."""
        if self.activated_date and self.resolved_date:
            return (self.resolved_date - self.activated_date).days
        return None
    
    def calculate_lead_time(self) -> Optional[float]:
        """Calculate lead time from created to resolved."""
        if self.created_date and self.resolved_date:
            return (self.resolved_date - self.created_date).days
        return None
    
    def calculate_roi_score(self) -> Optional[float]:
        """Calculate ROI score based on value and effort."""
        if self.business_value_normalized and self.story_points and self.story_points > 0:
            return self.business_value_normalized / self.story_points
        return None
    
    def is_completed(self) -> bool:
        """Check if work item is completed."""
        return self.state in [WorkItemState.CLOSED, WorkItemState.RESOLVED]
    
    def is_cancelled(self) -> bool:
        """Check if work item is cancelled or deferred."""
        return self.state in [WorkItemState.CANCELLED, WorkItemState.DEFERRED, WorkItemState.REMOVED]
    
    def is_active(self) -> bool:
        """Check if work item is active."""
        return self.state in [WorkItemState.ACTIVE, WorkItemState.IN_PROGRESS]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Epic(ADOWorkItem):
    """Epic-level work item with additional strategic fields."""
    
    work_item_type: Literal[WorkItemType.EPIC] = Field(default=WorkItemType.EPIC)
    
    # Epic-specific fields
    business_case: Optional[str] = Field(None, description="Business case description")
    success_criteria: Optional[str] = Field(None, description="Success criteria")
    target_market_size: Optional[float] = Field(None, description="Target market size")
    revenue_impact: Optional[float] = Field(None, description="Estimated revenue impact")
    
    # Roll-up metrics from children
    total_story_points: Optional[float] = Field(None, description="Sum of all child story points")
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    def calculate_epic_health_score(self) -> float:
        """Calculate epic health score based on multiple factors."""
        scores = []
        
        # Progress score
        if self.completion_percentage is not None:
            progress_score = self.completion_percentage / 100
            scores.append(progress_score)
        
        # Value score
        if self.business_value_normalized is not None:
            scores.append(self.business_value_normalized)
        
        # Risk-adjusted score
        if self.risk_score is not None:
            risk_factor = 1 - (self.risk_score / 100)
            scores.append(risk_factor)
        
        return np.mean(scores) if scores else 0.0


class PIO(ADOWorkItem):
    """Program Increment Objective work item."""
    
    work_item_type: Literal[WorkItemType.PIO] = Field(default=WorkItemType.PIO)
    
    # PIO-specific fields
    pi_confidence: Optional[float] = Field(None, ge=0, le=100, description="PI planning confidence %")
    stretch_goal: bool = Field(False, description="Is this a stretch goal?")
    committed: bool = Field(True, description="Is this committed for the PI?")
    
    # Dependencies
    depends_on: List[int] = Field(default_factory=list, description="Work item IDs this depends on")
    blocks: List[int] = Field(default_factory=list, description="Work item IDs this blocks")


class Feature(ADOWorkItem):
    """Feature-level work item."""
    
    work_item_type: Literal[WorkItemType.FEATURE] = Field(default=WorkItemType.FEATURE)
    
    # Feature-specific fields
    mvp_scope: Optional[str] = Field(None, description="MVP scope definition")
    enabler_type: Optional[str] = Field(None, description="Type of enabler (if applicable)")
    architectural_impact: Optional[str] = Field(None, description="Architectural impact assessment")
    
    # Feature toggle info
    feature_flag: Optional[str] = Field(None, description="Feature flag name")
    rollout_percentage: Optional[float] = Field(None, ge=0, le=100)


class UserStory(ADOWorkItem):
    """User Story work item."""
    
    work_item_type: Literal[WorkItemType.USER_STORY] = Field(default=WorkItemType.USER_STORY)
    
    # Story-specific fields
    acceptance_criteria: Optional[str] = Field(None, description="Acceptance criteria")
    story_type: Optional[str] = Field(None, description="Type: User Story, Technical Story, etc.")
    
    # Testing fields
    test_cases_count: Optional[int] = Field(None, ge=0)
    test_automation_percentage: Optional[float] = Field(None, ge=0, le=100)
    
    # Definition of Done
    dod_checklist: Dict[str, bool] = Field(default_factory=dict, description="Definition of Done checklist")
    
    def is_ready(self) -> bool:
        """Check if story meets Definition of Ready."""
        ready_criteria = [
            self.title is not None and len(self.title) > 0,
            self.acceptance_criteria is not None,
            self.story_points is not None,
            self.assigned_to is not None
        ]
        return all(ready_criteria)


class WorkItemHierarchy(BaseModel):
    """Represents the hierarchical structure of work items."""
    
    root_items: List[ADOWorkItem] = Field(default_factory=list, description="Top-level work items")
    all_items: Dict[int, ADOWorkItem] = Field(default_factory=dict, description="All items by ID")
    parent_child_map: Dict[int, List[int]] = Field(default_factory=dict, description="Parent to children mapping")
    child_parent_map: Dict[int, int] = Field(default_factory=dict, description="Child to parent mapping")
    
    def add_work_item(self, item: ADOWorkItem):
        """Add a work item to the hierarchy."""
        self.all_items[item.work_item_id] = item
        
        # Update parent-child relationships
        if item.parent_id:
            self.child_parent_map[item.work_item_id] = item.parent_id
            if item.parent_id not in self.parent_child_map:
                self.parent_child_map[item.parent_id] = []
            self.parent_child_map[item.parent_id].append(item.work_item_id)
        else:
            # Root item
            self.root_items.append(item)
    
    def get_children(self, parent_id: int) -> List[ADOWorkItem]:
        """Get all direct children of a work item."""
        child_ids = self.parent_child_map.get(parent_id, [])
        return [self.all_items[child_id] for child_id in child_ids if child_id in self.all_items]
    
    def get_descendants(self, parent_id: int) -> List[ADOWorkItem]:
        """Get all descendants (recursive) of a work item."""
        descendants = []
        children = self.get_children(parent_id)
        
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child.work_item_id))
        
        return descendants
    
    def get_parent(self, child_id: int) -> Optional[ADOWorkItem]:
        """Get parent of a work item."""
        parent_id = self.child_parent_map.get(child_id)
        return self.all_items.get(parent_id) if parent_id else None
    
    def get_ancestors(self, child_id: int) -> List[ADOWorkItem]:
        """Get all ancestors (recursive) of a work item."""
        ancestors = []
        parent = self.get_parent(child_id)
        
        while parent:
            ancestors.append(parent)
            parent = self.get_parent(parent.work_item_id)
        
        return ancestors
    
    def calculate_rollup_metrics(self, item_id: int) -> Dict[str, Any]:
        """Calculate roll-up metrics for a work item including all descendants."""
        item = self.all_items.get(item_id)
        if not item:
            return {}
        
        descendants = self.get_descendants(item_id)
        all_items = [item] + descendants
        
        # Calculate metrics
        total_points = sum(i.story_points or 0 for i in all_items)
        completed_points = sum(i.story_points or 0 for i in all_items if i.is_completed())
        cancelled_points = sum(i.story_points or 0 for i in all_items if i.is_cancelled())
        
        completion_rate = completed_points / total_points if total_points > 0 else 0
        
        # Risk and complexity averages
        risk_scores = [i.risk_score for i in all_items if i.risk_score is not None]
        avg_risk = np.mean(risk_scores) if risk_scores else None
        
        complexity_scores = [i.complexity_score for i in all_items if i.complexity_score is not None]
        avg_complexity = np.mean(complexity_scores) if complexity_scores else None
        
        return {
            "total_story_points": total_points,
            "completed_story_points": completed_points,
            "cancelled_story_points": cancelled_points,
            "completion_percentage": completion_rate * 100,
            "total_items": len(all_items),
            "completed_items": sum(1 for i in all_items if i.is_completed()),
            "active_items": sum(1 for i in all_items if i.is_active()),
            "average_risk_score": avg_risk,
            "average_complexity_score": avg_complexity,
            "descendant_count": len(descendants)
        }
    
    def get_hierarchy_level(self, item_id: int) -> int:
        """Get the hierarchy level of a work item (0 for root)."""
        ancestors = self.get_ancestors(item_id)
        return len(ancestors)
    
    def validate_hierarchy(self) -> Dict[str, List[str]]:
        """Validate the hierarchy for consistency issues."""
        errors = []
        warnings = []
        
        # Check for circular dependencies
        for item_id in self.all_items:
            ancestors = self.get_ancestors(item_id)
            ancestor_ids = [a.work_item_id for a in ancestors]
            if item_id in ancestor_ids:
                errors.append(f"Circular dependency detected for item {item_id}")
        
        # Check for orphaned items
        for item_id, item in self.all_items.items():
            if item.parent_id and item.parent_id not in self.all_items:
                warnings.append(f"Item {item_id} references non-existent parent {item.parent_id}")
        
        # Check work item type hierarchy (Epic > PIO/Feature > User Story)
        for item_id, item in self.all_items.items():
            parent = self.get_parent(item_id)
            if parent:
                valid_parent_types = {
                    WorkItemType.USER_STORY: [WorkItemType.FEATURE, WorkItemType.PIO],
                    WorkItemType.FEATURE: [WorkItemType.EPIC, WorkItemType.PIO],
                    WorkItemType.PIO: [WorkItemType.EPIC],
                    WorkItemType.EPIC: []
                }
                
                allowed_parents = valid_parent_types.get(item.work_item_type, [])
                if allowed_parents and parent.work_item_type not in allowed_parents:
                    warnings.append(
                        f"{item.work_item_type} {item_id} has invalid parent type {parent.work_item_type}"
                    )
        
        return {
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0
        }