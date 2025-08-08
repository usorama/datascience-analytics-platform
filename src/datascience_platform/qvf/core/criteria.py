"""QVF Criteria Configuration Engine

This module implements the core criteria configuration system for the
Quantified Value Framework (QVF). It provides comprehensive criteria
definitions, weight validation, and scoring configuration for enterprise
prioritization.

The QVF criteria framework is built on five main categories:
1. Quantified Weighted Value Criteria (Business Value, Risk, Time Criticality, Technical Debt)
2. Strategic Alignment Score (OKR Alignment, Vision Alignment, Portfolio Balance)
3. Customer Value Score (User Impact, Revenue Impact, Market Competitiveness)
4. Implementation Complexity (Technical Complexity, Dependency Count, Resource Requirements)
5. Risk Assessment (Implementation Risk, Business Risk, Technical Risk, Compliance Risk)

Key Features:
- Type-safe Pydantic models with comprehensive validation
- Mathematical weight normalization (weights must sum to 1.0)
- Flexible criteria customization for different organizations
- Integration with existing AHP engine
- Enterprise-scale performance optimization
- Comprehensive error handling and logging

Usage:
    from datascience_platform.qvf.core.criteria import QVFCriteriaEngine
    
    engine = QVFCriteriaEngine()
    config = engine.get_default_configuration()
    
    # Customize weights
    config.category_weights.business_value = 0.35
    config.category_weights.strategic_alignment = 0.30
    
    # Validate configuration
    engine.validate_configuration(config)
    
    # Score work items
    scores = engine.calculate_criteria_scores(work_items, config)

Architecture:
    The criteria engine leverages the existing AHP implementation at
    src/datascience_platform/ado/ahp.py and extends it with QVF-specific
    criteria and business logic. This ensures mathematical rigor while
    providing enterprise-specific functionality.
"""

import logging
import math
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator
import numpy as np
from dataclasses import dataclass, field

# Import existing AHP components
from ...ado.ahp import AHPConfiguration, AHPCriterion, AHPEngine, PairwiseComparison
from ...ado.models import ADOWorkItem, WorkItemType, WorkItemState
from ...core.exceptions import DataSciencePlatformError

logger = logging.getLogger(__name__)


class QVFValidationError(DataSciencePlatformError):
    """Exception raised for QVF criteria validation errors."""
    pass


class CriteriaCategory(str, Enum):
    """QVF criteria categories for organization and weighting."""
    BUSINESS_VALUE = "business_value"
    STRATEGIC_ALIGNMENT = "strategic_alignment"
    CUSTOMER_VALUE = "customer_value"
    IMPLEMENTATION_COMPLEXITY = "implementation_complexity"
    RISK_ASSESSMENT = "risk_assessment"


class QVFCriterion(BaseModel):
    """Enhanced criterion model for QVF with additional metadata.
    
    Extends the base AHP criterion with QVF-specific fields including
    category classification, financial modeling options, and advanced
    scoring parameters.
    """
    
    # Core fields (inherited from AHPCriterion concept)
    criterion_id: str = Field(..., description="Unique criterion identifier")
    name: str = Field(..., description="Display name for the criterion")
    description: str = Field(..., description="Detailed description of what this criterion measures")
    category: CriteriaCategory = Field(..., description="QVF category this criterion belongs to")
    
    # Weighting and importance
    weight: float = Field(0.0, ge=0, le=1, description="Normalized weight within category (0-1)")
    global_weight: float = Field(0.0, ge=0, le=1, description="Global weight across all criteria (calculated)")
    importance_rank: int = Field(1, ge=1, le=25, description="Relative importance rank (1=most important)")
    
    # Data sourcing
    data_source: str = Field(..., description="Field name in work item to extract value")
    data_type: str = Field("numeric", description="Expected data type: numeric, categorical, boolean, text")
    higher_is_better: bool = Field(True, description="Whether higher values indicate better score")
    
    # Value processing
    normalization_method: str = Field("minmax", description="Normalization: minmax, zscore, percentile, none")
    value_mapping: Optional[Dict[str, float]] = Field(None, description="Map categorical values to numbers")
    threshold_min: Optional[float] = Field(None, description="Minimum threshold for consideration")
    threshold_max: Optional[float] = Field(None, description="Maximum threshold for consideration")
    
    # Financial modeling (optional)
    financial_multiplier: Optional[float] = Field(None, ge=0, description="Financial impact multiplier")
    cost_of_delay: Optional[float] = Field(None, ge=0, description="Cost of delay per time unit")
    revenue_impact: Optional[float] = Field(None, description="Expected revenue impact")
    
    # Advanced scoring
    scoring_function: str = Field("linear", description="Scoring function: linear, logarithmic, exponential, step")
    diminishing_returns: bool = Field(False, description="Apply diminishing returns scaling")
    confidence_factor: float = Field(1.0, ge=0, le=1, description="Confidence in scoring accuracy")
    
    # Metadata
    is_active: bool = Field(True, description="Whether criterion is active in calculations")
    requires_manual_input: bool = Field(False, description="Whether criterion requires stakeholder input")
    stakeholder_input_type: Optional[str] = Field(None, description="Type of stakeholder input needed")
    
    # Validation and quality
    data_quality_threshold: float = Field(0.5, ge=0, le=1, description="Minimum data quality required")
    validation_rules: List[str] = Field(default_factory=list, description="Custom validation rules")
    
    @field_validator('normalization_method')
    @classmethod
    def validate_normalization(cls, v):
        allowed = ['minmax', 'zscore', 'percentile', 'none']
        if v not in allowed:
            raise ValueError(f"Normalization method must be one of {allowed}")
        return v
    
    @field_validator('scoring_function')
    @classmethod
    def validate_scoring_function(cls, v):
        allowed = ['linear', 'logarithmic', 'exponential', 'step']
        if v not in allowed:
            raise ValueError(f"Scoring function must be one of {allowed}")
        return v
    
    @field_validator('data_type')
    @classmethod
    def validate_data_type(cls, v):
        allowed = ['numeric', 'categorical', 'boolean', 'text']
        if v not in allowed:
            raise ValueError(f"Data type must be one of {allowed}")
        return v
    
    def to_ahp_criterion(self) -> AHPCriterion:
        """Convert QVF criterion to AHP criterion for engine compatibility."""
        return AHPCriterion(
            name=self.criterion_id,
            description=self.description,
            weight=self.global_weight,
            data_source=self.data_source,
            higher_is_better=self.higher_is_better,
            normalization_method=self.normalization_method,
            value_mapping=self.value_mapping,
            threshold_min=self.threshold_min,
            threshold_max=self.threshold_max
        )


class CriteriaWeights(BaseModel):
    """Category-level weights for QVF criteria.
    
    Defines the relative importance of each major criteria category.
    Weights must sum to 1.0 to ensure mathematical validity.
    """
    
    business_value: float = Field(0.25, ge=0, le=1, description="Weight for business value criteria")
    strategic_alignment: float = Field(0.25, ge=0, le=1, description="Weight for strategic alignment criteria")
    customer_value: float = Field(0.20, ge=0, le=1, description="Weight for customer value criteria")
    implementation_complexity: float = Field(0.15, ge=0, le=1, description="Weight for complexity criteria")
    risk_assessment: float = Field(0.15, ge=0, le=1, description="Weight for risk assessment criteria")
    
    @model_validator(mode='after')
    def validate_weights_sum(self):
        """Ensure all weights sum to 1.0 within tolerance."""
        total = (self.business_value + self.strategic_alignment + self.customer_value + 
                self.implementation_complexity + self.risk_assessment)
        tolerance = 1e-10
        
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Category weights must sum to 1.0, got {total:.10f}")
        
        return self
    
    def normalize(self) -> 'CriteriaWeights':
        """Normalize weights to sum to 1.0."""
        total = sum([self.business_value, self.strategic_alignment, self.customer_value, 
                    self.implementation_complexity, self.risk_assessment])
        
        if total == 0:
            raise QVFValidationError("Cannot normalize zero weights")
        
        return CriteriaWeights(
            business_value=self.business_value / total,
            strategic_alignment=self.strategic_alignment / total,
            customer_value=self.customer_value / total,
            implementation_complexity=self.implementation_complexity / total,
            risk_assessment=self.risk_assessment / total
        )
    
    def get_weight_for_category(self, category: CriteriaCategory) -> float:
        """Get weight for a specific category."""
        weight_mapping = {
            CriteriaCategory.BUSINESS_VALUE: self.business_value,
            CriteriaCategory.STRATEGIC_ALIGNMENT: self.strategic_alignment,
            CriteriaCategory.CUSTOMER_VALUE: self.customer_value,
            CriteriaCategory.IMPLEMENTATION_COMPLEXITY: self.implementation_complexity,
            CriteriaCategory.RISK_ASSESSMENT: self.risk_assessment
        }
        return weight_mapping[category]


class QVFCriteriaConfiguration(BaseModel):
    """Complete QVF criteria configuration.
    
    Encapsulates all criteria definitions, weights, and configuration
    parameters for a QVF prioritization session. This configuration
    is used by the QVF engine to score and rank work items.
    """
    
    # Core configuration
    configuration_id: str = Field(..., description="Unique configuration identifier")
    name: str = Field(..., description="Human-readable configuration name")
    description: Optional[str] = Field(None, description="Configuration description and purpose")
    
    # Criteria definitions
    criteria: List[QVFCriterion] = Field(..., description="List of all QVF criteria")
    category_weights: CriteriaWeights = Field(default_factory=CriteriaWeights, description="Category-level weights")
    
    # AHP settings
    consistency_threshold: float = Field(0.10, ge=0, le=1, description="Maximum acceptable consistency ratio")
    use_geometric_mean: bool = Field(True, description="Use geometric mean for AHP calculations")
    enable_sensitivity_analysis: bool = Field(True, description="Enable sensitivity analysis")
    
    # Validation settings
    require_all_criteria: bool = Field(False, description="Whether all criteria must have values")
    min_data_quality: float = Field(0.5, ge=0, le=1, description="Minimum data quality threshold")
    allow_partial_scoring: bool = Field(True, description="Allow scoring with partial data")
    
    # Performance settings
    max_calculation_time_seconds: int = Field(60, ge=1, le=300, description="Maximum calculation time")
    batch_size: int = Field(100, ge=1, le=10000, description="Batch size for large datasets")
    enable_parallel_processing: bool = Field(True, description="Enable parallel processing")
    
    # Financial modeling
    enable_financial_modeling: bool = Field(True, description="Enable financial calculations")
    discount_rate: float = Field(0.10, ge=0, le=1, description="Discount rate for NPV calculations")
    time_horizon_years: float = Field(3.0, ge=0.25, le=10, description="Time horizon for financial modeling")
    
    # Metadata
    created_date: datetime = Field(default_factory=datetime.now, description="Configuration creation date")
    last_modified: datetime = Field(default_factory=datetime.now, description="Last modification date")
    version: str = Field("1.0.0", description="Configuration version")
    created_by: Optional[str] = Field(None, description="Configuration creator")
    
    def get_criteria_by_category(self, category: CriteriaCategory) -> List[QVFCriterion]:
        """Get all criteria for a specific category."""
        return [c for c in self.criteria if c.category == category]
    
    def get_active_criteria(self) -> List[QVFCriterion]:
        """Get all active criteria."""
        return [c for c in self.criteria if c.is_active]
    
    def get_criterion_by_id(self, criterion_id: str) -> Optional[QVFCriterion]:
        """Get criterion by ID."""
        for criterion in self.criteria:
            if criterion.criterion_id == criterion_id:
                return criterion
        return None
    
    def calculate_global_weights(self) -> None:
        """Calculate global weights for all criteria based on category weights."""
        # Group criteria by category
        category_criteria = {}
        for category in CriteriaCategory:
            category_criteria[category] = self.get_criteria_by_category(category)
        
        # Calculate global weights
        for category, criteria_list in category_criteria.items():
            if not criteria_list:
                continue
            
            category_weight = self.category_weights.get_weight_for_category(category)
            
            # Normalize weights within category
            total_category_weight = sum(c.weight for c in criteria_list if c.is_active)
            
            if total_category_weight > 0:
                for criterion in criteria_list:
                    if criterion.is_active:
                        criterion.global_weight = (criterion.weight / total_category_weight) * category_weight
                    else:
                        criterion.global_weight = 0.0
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Check basic requirements
        if not self.criteria:
            issues.append("No criteria defined")
            return issues
        
        active_criteria = self.get_active_criteria()
        if len(active_criteria) < 3:
            issues.append("At least 3 active criteria required")
        
        if len(active_criteria) > 25:
            issues.append("Maximum 25 active criteria allowed")
        
        # Check category distribution
        categories_with_criteria = set(c.category for c in active_criteria)
        if len(categories_with_criteria) < 3:
            issues.append("At least 3 categories must have active criteria")
        
        # Check data sources
        data_sources = [c.data_source for c in active_criteria]
        if len(set(data_sources)) != len(data_sources):
            issues.append("Duplicate data sources found")
        
        # Check weights within categories
        for category in CriteriaCategory:
            category_criteria = [c for c in active_criteria if c.category == category]
            if category_criteria:
                total_weight = sum(c.weight for c in category_criteria)
                if abs(total_weight - 1.0) > 1e-6:
                    issues.append(f"Category {category.value} weights sum to {total_weight:.4f}, should be 1.0")
        
        return issues
    
    def to_ahp_configuration(self) -> AHPConfiguration:
        """Convert to AHP configuration for engine compatibility."""
        ahp_criteria = [c.to_ahp_criterion() for c in self.get_active_criteria()]
        return AHPConfiguration(
            criteria=ahp_criteria,
            consistency_threshold=self.consistency_threshold
        )


class QVFCriteriaEngine:
    """Main engine for QVF criteria configuration and scoring.
    
    This engine provides the core functionality for:
    - Creating and managing QVF criteria configurations
    - Validating criteria setups and weights
    - Calculating work item scores using QVF criteria
    - Generating default enterprise-ready configurations
    - Integration with existing AHP engine
    
    The engine is designed for enterprise scale with support for
    10,000+ work items and <60 second calculation times.
    """
    
    def __init__(self, consistency_threshold: float = 0.10):
        """Initialize QVF criteria engine.
        
        Args:
            consistency_threshold: Maximum acceptable AHP consistency ratio
        """
        self.consistency_threshold = consistency_threshold
        self._default_criteria = None
        
        logger.info(f"QVF Criteria Engine initialized with consistency threshold {consistency_threshold}")
    
    def get_default_configuration(self) -> QVFCriteriaConfiguration:
        """Get default QVF criteria configuration.
        
        Returns a comprehensive, enterprise-ready configuration with
        all major QVF criteria categories properly weighted and configured.
        
        Returns:
            Default QVF criteria configuration
        """
        if self._default_criteria is None:
            self._default_criteria = self._build_default_criteria()
        
        # Create configuration
        config = QVFCriteriaConfiguration(
            configuration_id="qvf_default_v1",
            name="QVF Enterprise Default Configuration",
            description="Comprehensive QVF configuration for enterprise prioritization",
            criteria=self._default_criteria,
            category_weights=CriteriaWeights(),
            consistency_threshold=self.consistency_threshold
        )
        
        # Calculate global weights
        config.calculate_global_weights()
        
        logger.info(f"Generated default configuration with {len(config.criteria)} criteria")
        return config
    
    def _build_default_criteria(self) -> List[QVFCriterion]:
        """Build comprehensive default criteria set.
        
        Creates 20+ criteria across all QVF categories with proper
        weights and configuration for enterprise use.
        
        Returns:
            List of default QVF criteria
        """
        criteria = []
        
        # 1. BUSINESS VALUE CRITERIA (25% weight)
        criteria.extend([
            QVFCriterion(
                criterion_id="bv_business_value_raw",
                name="Business Value (Raw)",
                description="Original business value score from work item",
                category=CriteriaCategory.BUSINESS_VALUE,
                weight=0.40,  # 40% within Business Value category
                data_source="business_value_raw",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                financial_multiplier=1000,  # $1000 per point
                importance_rank=1
            ),
            QVFCriterion(
                criterion_id="bv_revenue_impact",
                name="Revenue Impact",
                description="Expected revenue impact from work item completion",
                category=CriteriaCategory.BUSINESS_VALUE,
                weight=0.30,  # 30% within category
                data_source="custom_fields.revenue_impact",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                financial_multiplier=1.0,
                scoring_function="logarithmic",
                importance_rank=2
            ),
            QVFCriterion(
                criterion_id="bv_cost_savings",
                name="Cost Savings",
                description="Expected cost savings from work item",
                category=CriteriaCategory.BUSINESS_VALUE,
                weight=0.20,  # 20% within category
                data_source="custom_fields.cost_savings",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                financial_multiplier=1.0,
                importance_rank=5
            ),
            QVFCriterion(
                criterion_id="bv_time_criticality",
                name="Time Criticality",
                description="How time-sensitive this work item is",
                category=CriteriaCategory.BUSINESS_VALUE,
                weight=0.10,  # 10% within category
                data_source="custom_fields.time_criticality",
                data_type="categorical",
                value_mapping={
                    "Critical": 1.0,
                    "High": 0.75,
                    "Medium": 0.5,
                    "Low": 0.25,
                    "None": 0.0
                },
                higher_is_better=True,
                cost_of_delay=1000,  # $1000/week delay cost
                importance_rank=8
            )
        ])
        
        # 2. STRATEGIC ALIGNMENT CRITERIA (25% weight)
        criteria.extend([
            QVFCriterion(
                criterion_id="sa_okr_alignment",
                name="OKR Alignment",
                description="Alignment with current quarter OKRs",
                category=CriteriaCategory.STRATEGIC_ALIGNMENT,
                weight=0.40,  # 40% within Strategic Alignment
                data_source="custom_fields.okr_alignment_score",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                threshold_min=0.3,  # Minimum alignment threshold
                importance_rank=3
            ),
            QVFCriterion(
                criterion_id="sa_vision_alignment",
                name="Vision Alignment",
                description="Alignment with organizational vision and strategy",
                category=CriteriaCategory.STRATEGIC_ALIGNMENT,
                weight=0.30,  # 30% within category
                data_source="custom_fields.vision_alignment_score",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                importance_rank=4
            ),
            QVFCriterion(
                criterion_id="sa_portfolio_balance",
                name="Portfolio Balance",
                description="Contribution to balanced portfolio across themes",
                category=CriteriaCategory.STRATEGIC_ALIGNMENT,
                weight=0.20,  # 20% within category
                data_source="custom_fields.portfolio_balance_score",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="zscore",
                importance_rank=10
            ),
            QVFCriterion(
                criterion_id="sa_strategic_theme",
                name="Strategic Theme Priority",
                description="Priority based on strategic theme alignment",
                category=CriteriaCategory.STRATEGIC_ALIGNMENT,
                weight=0.10,  # 10% within category
                data_source="strategy_pillar",
                data_type="categorical",
                value_mapping={
                    "Customer Experience": 1.0,
                    "Operational Excellence": 0.8,
                    "Innovation": 0.9,
                    "Growth": 0.85,
                    "Technical Excellence": 0.6
                },
                higher_is_better=True,
                importance_rank=12
            )
        ])
        
        # 3. CUSTOMER VALUE CRITERIA (20% weight)
        criteria.extend([
            QVFCriterion(
                criterion_id="cv_user_impact",
                name="User Impact",
                description="Number of users impacted by this work item",
                category=CriteriaCategory.CUSTOMER_VALUE,
                weight=0.40,  # 40% within Customer Value
                data_source="custom_fields.user_impact_count",
                data_type="numeric",
                higher_is_better=True,
                normalization_method="minmax",
                scoring_function="logarithmic",
                importance_rank=6
            ),
            QVFCriterion(
                criterion_id="cv_customer_satisfaction",
                name="Customer Satisfaction Impact",
                description="Expected impact on customer satisfaction metrics",
                category=CriteriaCategory.CUSTOMER_VALUE,
                weight=0.35,  # 35% within category
                data_source="custom_fields.csat_impact",
                data_type="categorical",
                value_mapping={
                    "Very High": 1.0,
                    "High": 0.8,
                    "Medium": 0.6,
                    "Low": 0.3,
                    "Very Low": 0.1
                },
                higher_is_better=True,
                importance_rank=7
            ),
            QVFCriterion(
                criterion_id="cv_market_competitiveness",
                name="Market Competitiveness",
                description="Impact on competitive position in market",
                category=CriteriaCategory.CUSTOMER_VALUE,
                weight=0.25,  # 25% within category
                data_source="custom_fields.competitive_impact",
                data_type="categorical",
                value_mapping={
                    "Game Changer": 1.0,
                    "Significant Advantage": 0.8,
                    "Competitive Parity": 0.5,
                    "Minor Advantage": 0.3,
                    "No Impact": 0.0
                },
                higher_is_better=True,
                importance_rank=11
            )
        ])
        
        # 4. IMPLEMENTATION COMPLEXITY CRITERIA (15% weight)
        criteria.extend([
            QVFCriterion(
                criterion_id="ic_technical_complexity",
                name="Technical Complexity",
                description="Technical implementation complexity score",
                category=CriteriaCategory.IMPLEMENTATION_COMPLEXITY,
                weight=0.40,  # 40% within Implementation Complexity
                data_source="complexity_score",
                data_type="numeric",
                higher_is_better=False,  # Lower complexity is better
                normalization_method="minmax",
                importance_rank=9
            ),
            QVFCriterion(
                criterion_id="ic_dependency_count",
                name="Dependency Count",
                description="Number of dependencies this item has",
                category=CriteriaCategory.IMPLEMENTATION_COMPLEXITY,
                weight=0.30,  # 30% within category
                data_source="custom_fields.dependency_count",
                data_type="numeric",
                higher_is_better=False,  # Fewer dependencies is better
                normalization_method="minmax",
                scoring_function="exponential",
                importance_rank=13
            ),
            QVFCriterion(
                criterion_id="ic_resource_requirements",
                name="Resource Requirements",
                description="Amount of resources (people, time) required",
                category=CriteriaCategory.IMPLEMENTATION_COMPLEXITY,
                weight=0.30,  # 30% within category
                data_source="story_points",
                data_type="numeric",
                higher_is_better=False,  # Fewer story points is better for complexity
                normalization_method="minmax",
                diminishing_returns=True,
                importance_rank=15
            )
        ])
        
        # 5. RISK ASSESSMENT CRITERIA (15% weight)
        criteria.extend([
            QVFCriterion(
                criterion_id="ra_implementation_risk",
                name="Implementation Risk",
                description="Risk of implementation failure or delays",
                category=CriteriaCategory.RISK_ASSESSMENT,
                weight=0.30,  # 30% within Risk Assessment
                data_source="risk_score",
                data_type="numeric",
                higher_is_better=False,  # Lower risk is better
                normalization_method="minmax",
                importance_rank=14
            ),
            QVFCriterion(
                criterion_id="ra_business_risk",
                name="Business Risk",
                description="Risk to business if this work is not completed",
                category=CriteriaCategory.RISK_ASSESSMENT,
                weight=0.25,  # 25% within category
                data_source="custom_fields.business_risk",
                data_type="categorical",
                value_mapping={
                    "Critical": 1.0,
                    "High": 0.8,
                    "Medium": 0.6,
                    "Low": 0.3,
                    "Minimal": 0.1
                },
                higher_is_better=True,  # Higher business risk of NOT doing = higher priority
                importance_rank=16
            ),
            QVFCriterion(
                criterion_id="ra_technical_risk",
                name="Technical Risk",
                description="Technical risks and challenges",
                category=CriteriaCategory.RISK_ASSESSMENT,
                weight=0.25,  # 25% within category
                data_source="custom_fields.technical_risk",
                data_type="categorical",
                value_mapping={
                    "High": 0.2,
                    "Medium": 0.5,
                    "Low": 0.8,
                    "Very Low": 1.0
                },
                higher_is_better=True,  # Lower technical risk is better
                importance_rank=17
            ),
            QVFCriterion(
                criterion_id="ra_compliance_risk",
                name="Compliance Risk",
                description="Regulatory and compliance risk considerations",
                category=CriteriaCategory.RISK_ASSESSMENT,
                weight=0.20,  # 20% within category
                data_source="custom_fields.compliance_risk",
                data_type="categorical",
                value_mapping={
                    "Critical": 1.0,
                    "High": 0.8,
                    "Medium": 0.5,
                    "Low": 0.2,
                    "None": 0.0
                },
                higher_is_better=True,  # Higher compliance risk = higher priority
                importance_rank=18
            )
        ])
        
        logger.info(f"Built {len(criteria)} default QVF criteria across {len(set(c.category for c in criteria))} categories")
        return criteria
    
    def validate_configuration(self, config: QVFCriteriaConfiguration) -> List[str]:
        """Validate QVF criteria configuration.
        
        Performs comprehensive validation including:
        - Weight normalization and consistency
        - Category distribution
        - Data source validation
        - AHP consistency requirements
        
        Args:
            config: QVF configuration to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        logger.info(f"Validating QVF configuration '{config.name}'")
        
        issues = config.validate_configuration()
        
        # Additional QVF-specific validations
        try:
            # Test AHP configuration conversion
            ahp_config = config.to_ahp_configuration()
            
            # Validate that we can create an AHP engine
            ahp_engine = AHPEngine(ahp_config)
            
            logger.info(f"QVF configuration validation completed with {len(issues)} issues")
            
        except Exception as e:
            issues.append(f"AHP configuration error: {str(e)}")
            logger.error(f"AHP validation failed: {e}")
        
        if issues:
            logger.warning(f"Configuration validation found issues: {issues}")
        else:
            logger.info("Configuration validation successful")
        
        return issues
    
    def calculate_criteria_scores(
        self,
        work_items: List[ADOWorkItem],
        config: QVFCriteriaConfiguration,
        include_breakdown: bool = True
    ) -> Dict[str, Any]:
        """Calculate QVF criteria scores for work items.
        
        Uses the existing AHP engine with QVF criteria configuration
        to score and rank work items based on the configured criteria.
        
        Args:
            work_items: List of work items to score
            config: QVF criteria configuration
            include_breakdown: Include detailed scoring breakdown
            
        Returns:
            Dictionary containing scores, rankings, and analysis
        """
        logger.info(f"Calculating QVF scores for {len(work_items)} work items")
        
        # Validate configuration first
        validation_issues = self.validate_configuration(config)
        if validation_issues:
            raise QVFValidationError(f"Configuration validation failed: {validation_issues}")
        
        # Convert to AHP configuration
        ahp_config = config.to_ahp_configuration()
        ahp_engine = AHPEngine(ahp_config)
        
        # Create comparison matrix from QVF weights
        # Use weight-based comparison matrix generation
        weights_dict = {}
        for criterion in config.get_active_criteria():
            weights_dict[criterion.criterion_id] = criterion.global_weight
        
        # Generate comparison matrix
        comparison_matrix = ahp_engine.create_comparison_matrix_from_preferences(weights_dict)
        
        # Calculate AHP weights
        ahp_weights = ahp_engine.calculate_weights(comparison_matrix)
        
        # Check consistency
        consistency_ratio = ahp_engine.calculate_consistency_ratio(comparison_matrix)
        
        if consistency_ratio > config.consistency_threshold:
            logger.warning(f"Consistency ratio {consistency_ratio:.3f} exceeds threshold {config.consistency_threshold}")
        
        # Convert work items to scoring format
        scoring_items = []
        for item in work_items:
            item_dict = item.dict() if hasattr(item, 'dict') else item.__dict__
            scoring_items.append(item_dict)
        
        # Calculate scores using AHP engine
        rankings = ahp_engine.rank_work_items(scoring_items)
        
        # Build results
        results = {
            'configuration': {
                'name': config.name,
                'criteria_count': len(config.get_active_criteria()),
                'consistency_ratio': consistency_ratio,
                'is_consistent': consistency_ratio <= config.consistency_threshold
            },
            'scores': []
        }
        
        # Process rankings
        for work_item_idx, total_score, criterion_scores in rankings:
            work_item = work_items[work_item_idx]
            
            score_entry = {
                'work_item_id': work_item.work_item_id,
                'title': work_item.title,
                'work_item_type': work_item.work_item_type.value,
                'total_score': total_score,
                'rank': len(results['scores']) + 1
            }
            
            if include_breakdown:
                # Add category breakdown
                category_scores = {}
                for category in CriteriaCategory:
                    category_criteria = config.get_criteria_by_category(category)
                    category_score = sum(
                        criterion_scores.get(c.criterion_id, 0) * c.global_weight
                        for c in category_criteria if c.is_active
                    )
                    category_scores[category.value] = category_score
                
                score_entry['category_scores'] = category_scores
                score_entry['criterion_scores'] = criterion_scores
            
            results['scores'].append(score_entry)
        
        # Add summary statistics
        scores = [s['total_score'] for s in results['scores']]
        results['statistics'] = {
            'mean_score': np.mean(scores),
            'std_score': np.std(scores),
            'min_score': np.min(scores),
            'max_score': np.max(scores),
            'score_range': np.max(scores) - np.min(scores)
        }
        
        logger.info(f"QVF scoring completed. Mean score: {results['statistics']['mean_score']:.3f}")
        return results
    
    def create_custom_configuration(
        self,
        name: str,
        description: str,
        custom_criteria: Optional[List[QVFCriterion]] = None,
        custom_weights: Optional[CriteriaWeights] = None
    ) -> QVFCriteriaConfiguration:
        """Create custom QVF configuration.
        
        Args:
            name: Configuration name
            description: Configuration description
            custom_criteria: Optional custom criteria (uses defaults if None)
            custom_weights: Optional custom category weights
            
        Returns:
            Custom QVF configuration
        """
        criteria = custom_criteria or self._build_default_criteria()
        weights = custom_weights or CriteriaWeights()
        
        config = QVFCriteriaConfiguration(
            configuration_id=f"qvf_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            description=description,
            criteria=criteria,
            category_weights=weights,
            consistency_threshold=self.consistency_threshold
        )
        
        config.calculate_global_weights()
        
        logger.info(f"Created custom configuration '{name}' with {len(criteria)} criteria")
        return config
    
    def export_configuration(self, config: QVFCriteriaConfiguration) -> Dict[str, Any]:
        """Export configuration for storage or sharing.
        
        Args:
            config: Configuration to export
            
        Returns:
            Serializable configuration dictionary
        """
        return config.model_dump()
    
    def import_configuration(self, config_data: Dict[str, Any]) -> QVFCriteriaConfiguration:
        """Import configuration from exported data.
        
        Args:
            config_data: Exported configuration data
            
        Returns:
            Imported QVF configuration
        """
        return QVFCriteriaConfiguration(**config_data)


# Factory functions for common configurations
def create_agile_configuration() -> QVFCriteriaConfiguration:
    """Create configuration optimized for Agile teams."""
    engine = QVFCriteriaEngine()
    config = engine.get_default_configuration()
    
    # Adjust weights for Agile focus
    config.category_weights.business_value = 0.30
    config.category_weights.customer_value = 0.30
    config.category_weights.implementation_complexity = 0.20
    config.category_weights.strategic_alignment = 0.15
    config.category_weights.risk_assessment = 0.05
    
    config.name = "QVF Agile Team Configuration"
    config.description = "Optimized for Agile teams focusing on customer value and business outcomes"
    config.calculate_global_weights()
    
    return config


def create_enterprise_configuration() -> QVFCriteriaConfiguration:
    """Create configuration for enterprise portfolio management."""
    engine = QVFCriteriaEngine()
    config = engine.get_default_configuration()
    
    # Enterprise focus on strategic alignment and risk
    config.category_weights.strategic_alignment = 0.35
    config.category_weights.business_value = 0.25
    config.category_weights.risk_assessment = 0.20
    config.category_weights.customer_value = 0.15
    config.category_weights.implementation_complexity = 0.05
    
    config.name = "QVF Enterprise Portfolio Configuration"
    config.description = "Optimized for enterprise portfolio management with strategic alignment focus"
    config.calculate_global_weights()
    
    return config


def create_startup_configuration() -> QVFCriteriaConfiguration:
    """Create configuration optimized for startups."""
    engine = QVFCriteriaEngine()
    config = engine.get_default_configuration()
    
    # Startup focus on customer value and speed
    config.category_weights.customer_value = 0.35
    config.category_weights.business_value = 0.30
    config.category_weights.implementation_complexity = 0.25
    config.category_weights.strategic_alignment = 0.07
    config.category_weights.risk_assessment = 0.03
    
    config.name = "QVF Startup Configuration"
    config.description = "Optimized for startups focusing on customer value and implementation speed"
    config.calculate_global_weights()
    
    return config