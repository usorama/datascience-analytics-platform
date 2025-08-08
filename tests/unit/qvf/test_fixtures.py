"""Test fixtures for QVF unit tests.

Provides reusable test data and helper functions for QVF testing.
"""

from datetime import datetime
from typing import List, Dict, Any

from datascience_platform.ado.models import ADOWorkItem, WorkItemType, WorkItemState, TeamMetrics
from datascience_platform.qvf.core.criteria import (
    QVFCriteriaConfiguration, QVFCriterion, CriteriaCategory, CriteriaWeights
)
from datascience_platform.qvf.core.financial import FinancialMetrics, RiskLevel, CurrencyType


def create_test_work_item(
    work_item_id: int = 1,
    title: str = "Test Work Item",
    work_item_type: WorkItemType = WorkItemType.USER_STORY,
    business_value: float = 50.0,
    story_points: float = 5.0,
    **kwargs
) -> ADOWorkItem:
    """Create a test work item with default values.
    
    Args:
        work_item_id: Work item ID
        title: Work item title
        work_item_type: Type of work item
        business_value: Business value score
        story_points: Story points estimate
        **kwargs: Additional fields
        
    Returns:
        Test ADO work item
    """
    default_custom_fields = {
        "revenue_impact": 25000.0,
        "cost_savings": 10000.0,
        "time_criticality": "Medium",
        "okr_alignment_score": 0.7,
        "vision_alignment_score": 0.6,
        "portfolio_balance_score": 0.5,
        "user_impact_count": 1000,
        "csat_impact": "High",
        "competitive_impact": "Competitive Parity",
        "dependency_count": 2,
        "business_risk": "Medium",
        "technical_risk": "Low",
        "compliance_risk": "Low"
    }
    
    # Merge with provided custom fields
    custom_fields = {**default_custom_fields, **kwargs.get('custom_fields', {})}
    
    return ADOWorkItem(
        work_item_id=work_item_id,
        title=title,
        work_item_type=work_item_type,
        state=WorkItemState.ACTIVE,
        business_value_raw=business_value,
        business_value_normalized=business_value / 100.0,
        story_points=story_points,
        complexity_score=story_points * 10,
        risk_score=30.0,
        strategy_pillar="Customer Experience",
        custom_fields=custom_fields,
        **{k: v for k, v in kwargs.items() if k != 'custom_fields'}
    )


def create_test_criteria_config(
    config_name: str = "Test Configuration",
    category_weights: CriteriaWeights = None
) -> QVFCriteriaConfiguration:
    """Create a test QVF criteria configuration.
    
    Args:
        config_name: Name of the configuration
        category_weights: Optional custom category weights
        
    Returns:
        Test QVF criteria configuration
    """
    if category_weights is None:
        category_weights = CriteriaWeights()
    
    # Create simplified test criteria
    criteria = [
        # Business Value criteria
        QVFCriterion(
            criterion_id="test_business_value",
            name="Business Value",
            description="Test business value criterion",
            category=CriteriaCategory.BUSINESS_VALUE,
            weight=1.0,  # Only criterion in category
            data_source="business_value_raw",
            importance_rank=1
        ),
        
        # Strategic Alignment criteria
        QVFCriterion(
            criterion_id="test_strategic_alignment",
            name="Strategic Alignment",
            description="Test strategic alignment criterion",
            category=CriteriaCategory.STRATEGIC_ALIGNMENT,
            weight=1.0,  # Only criterion in category
            data_source="custom_fields.okr_alignment_score",
            importance_rank=2
        ),
        
        # Customer Value criteria
        QVFCriterion(
            criterion_id="test_customer_value",
            name="Customer Value",
            description="Test customer value criterion",
            category=CriteriaCategory.CUSTOMER_VALUE,
            weight=1.0,  # Only criterion in category
            data_source="custom_fields.user_impact_count",
            normalization_method="minmax",
            scoring_function="logarithmic",
            importance_rank=3
        ),
        
        # Implementation Complexity criteria
        QVFCriterion(
            criterion_id="test_complexity",
            name="Implementation Complexity",
            description="Test complexity criterion",
            category=CriteriaCategory.IMPLEMENTATION_COMPLEXITY,
            weight=1.0,  # Only criterion in category
            data_source="story_points",
            higher_is_better=False,  # Lower complexity is better
            importance_rank=4
        ),
        
        # Risk Assessment criteria
        QVFCriterion(
            criterion_id="test_risk",
            name="Risk Assessment",
            description="Test risk criterion",
            category=CriteriaCategory.RISK_ASSESSMENT,
            weight=1.0,  # Only criterion in category
            data_source="risk_score",
            higher_is_better=False,  # Lower risk is better
            importance_rank=5
        )
    ]
    
    config = QVFCriteriaConfiguration(
        configuration_id="test_config_1",
        name=config_name,
        description="Test configuration for unit tests",
        criteria=criteria,
        category_weights=category_weights
    )
    
    # Calculate global weights
    config.calculate_global_weights()
    
    return config


def create_test_financial_metrics(
    initial_investment: float = 100000.0,
    expected_revenue: List[float] = None,
    risk_level: RiskLevel = RiskLevel.MEDIUM
) -> FinancialMetrics:
    """Create test financial metrics.
    
    Args:
        initial_investment: Initial investment amount
        expected_revenue: List of expected revenue per period
        risk_level: Risk level for the investment
        
    Returns:
        Test financial metrics
    """
    if expected_revenue is None:
        expected_revenue = [50000.0, 75000.0, 100000.0, 125000.0]
    
    return FinancialMetrics(
        initial_investment=initial_investment,
        implementation_cost=25000.0,
        ongoing_costs=[10000.0, 12000.0, 15000.0, 18000.0],
        expected_revenue=expected_revenue,
        cost_savings=[5000.0, 7500.0, 10000.0, 12500.0],
        productivity_gains=[2000.0, 3000.0, 4000.0, 5000.0],
        risk_level=risk_level,
        implementation_timeline_months=12.0,
        benefit_realization_delay_months=3.0,
        cost_of_delay_per_month=15000.0,
        competitive_advantage_value=50000.0,
        market_opportunity_size=500000.0,
        quality_improvement_factor=1.2,
        operational_efficiency_gain=0.15,
        customer_satisfaction_impact=0.25,
        discount_rate=0.10,
        currency=CurrencyType.USD,
        inflation_rate=0.03
    )


def create_multiple_test_work_items(count: int = 5) -> List[ADOWorkItem]:
    """Create multiple test work items with varying attributes.
    
    Args:
        count: Number of work items to create
        
    Returns:
        List of test work items
    """
    work_items = []
    
    for i in range(count):
        # Vary attributes to create realistic test data
        business_value = 20.0 + (i * 15.0)  # 20, 35, 50, 65, 80
        story_points = 2.0 + (i * 2.0)       # 2, 4, 6, 8, 10
        
        # Vary custom field values
        custom_fields = {
            "revenue_impact": 10000.0 + (i * 15000.0),
            "cost_savings": 5000.0 + (i * 7500.0),
            "time_criticality": ["Low", "Medium", "High", "Critical", "Medium"][i],
            "okr_alignment_score": 0.3 + (i * 0.15),  # 0.3 to 0.9
            "vision_alignment_score": 0.2 + (i * 0.2),
            "portfolio_balance_score": 0.4 + (i * 0.1),
            "user_impact_count": 500 + (i * 1500),
            "csat_impact": ["Low", "Medium", "High", "Very High", "High"][i],
            "competitive_impact": ["No Impact", "Minor Advantage", "Competitive Parity", "Significant Advantage", "Game Changer"][i],
            "dependency_count": i + 1,
            "business_risk": ["Low", "Medium", "High", "Medium", "Low"][i],
            "technical_risk": ["Very Low", "Low", "Medium", "Low", "Very Low"][i],
            "compliance_risk": ["None", "Low", "Medium", "High", "Low"][i]
        }
        
        work_item = create_test_work_item(
            work_item_id=i + 1,
            title=f"Test Work Item {i + 1}",
            work_item_type=[WorkItemType.TASK, WorkItemType.USER_STORY, WorkItemType.FEATURE, WorkItemType.EPIC, WorkItemType.USER_STORY][i],
            business_value=business_value,
            story_points=story_points,
            complexity_score=story_points * 8 + (i * 5),
            risk_score=15.0 + (i * 10.0),
            custom_fields=custom_fields
        )
        
        work_items.append(work_item)
    
    return work_items


def create_test_pairwise_comparisons() -> List[Dict[str, Any]]:
    """Create test pairwise comparison data.
    
    Returns:
        List of pairwise comparison dictionaries
    """
    return [
        {
            "criterion_a": "test_business_value",
            "criterion_b": "test_strategic_alignment",
            "comparison_value": 3  # Business value is 3x more important
        },
        {
            "criterion_a": "test_business_value",
            "criterion_b": "test_customer_value",
            "comparison_value": 2  # Business value is 2x more important
        },
        {
            "criterion_a": "test_strategic_alignment",
            "criterion_b": "test_complexity",
            "comparison_value": 4  # Strategic alignment is 4x more important
        },
        {
            "criterion_a": "test_customer_value",
            "criterion_b": "test_risk",
            "comparison_value": 3  # Customer value is 3x more important
        }
    ]