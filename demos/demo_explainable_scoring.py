#!/usr/bin/env python3
"""
Explainable Scoring Demo

This demonstrates how the system provides comprehensive explanations
for strategic alignment scores, making decisions transparent and actionable.
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado.semantic import (
    OKR, KeyResult, StrategyDocument, DocumentType,
    SemanticWorkItem, SemanticScorer
)
from datascience_platform.ado.semantic.explainability import (
    ExplainableScorer, ExplanationType
)
from datascience_platform.ado import WorkItemType


def create_diverse_work_items():
    """Create work items with varying alignment levels for comparison."""
    items = []
    
    # High alignment item
    high_item = SemanticWorkItem(
        work_item_id=4001,
        title="Implement Zero-Downtime Deployment Pipeline",
        work_item_type=WorkItemType.EPIC,
        state="Active",
        business_value_raw=90,
        story_points=55,
        full_description="""
Build a comprehensive zero-downtime deployment system to achieve our 99.99% uptime 
target and support rapid feature delivery. This directly contributes to our Q3 OKR 
for operational excellence and customer satisfaction.

Business Impact:
- Reduces deployment risk by 90%
- Enables daily releases instead of weekly
- Supports our uptime SLA commitment
- Improves developer productivity by 40%

Technical Approach:
- Blue-green deployment strategy
- Automated rollback capabilities
- Progressive rollout with feature flags
- Real-time health monitoring

Success Metrics:
- Zero customer-impacting deployments
- < 5 minute deployment time
- 100% automated deployment process
- 99.99% uptime maintained
""",
        business_justification="Critical for achieving our uptime OKR and enabling rapid innovation",
        acceptance_criteria_text="""
- Zero-downtime deployments for all services
- Automated rollback within 30 seconds
- Deployment dashboard with real-time metrics
- Load balancer integration
- Database migration support
""",
        area_path="Platform Team",
        strategic_themes=["operational_excellence", "reliability", "automation"]
    )
    items.append(high_item)
    
    # Medium alignment item
    medium_item = SemanticWorkItem(
        work_item_id=4002,
        title="Redesign User Profile Page",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=60,
        story_points=21,
        full_description="""
Modernize the user profile page with improved UX and performance.
This will enhance user engagement and reduce support tickets related
to profile management.

Changes include:
- New responsive design
- Faster loading times
- Better mobile experience
- Simplified navigation
""",
        acceptance_criteria_text="""
- Page loads in under 2 seconds
- Mobile-first responsive design
- Accessibility WCAG 2.1 AA compliant
""",
        area_path="Frontend Team",
        strategic_themes=["customer_experience"]
    )
    items.append(medium_item)
    
    # Low alignment item
    low_item = SemanticWorkItem(
        work_item_id=4003,
        title="Update team wiki documentation",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=20,
        story_points=5,
        full_description="Update the internal team wiki with latest processes",
        area_path="Engineering Team"
    )
    items.append(low_item)
    
    # Item with good technical description but unclear business value
    technical_item = SemanticWorkItem(
        work_item_id=4004,
        title="Migrate to Kubernetes 1.29",
        work_item_type=WorkItemType.FEATURE,
        state="New",
        business_value_raw=40,
        story_points=34,
        full_description="""
Upgrade our Kubernetes clusters from 1.27 to 1.29 to get the latest features:
- Improved pod scheduling
- Better resource management
- Enhanced security features
- New API capabilities

Technical steps:
1. Test in staging environment
2. Update deployment scripts
3. Migrate one cluster at a time
4. Update documentation
""",
        technical_notes="Kubernetes 1.29 includes important security patches",
        area_path="Infrastructure Team",
        strategic_themes=["security"]
    )
    items.append(technical_item)
    
    return items


def create_strategy_and_okrs():
    """Create strategy document and OKRs for alignment."""
    # Strategy document
    strategy = StrategyDocument(
        doc_id="doc_2025_operational_excellence",
        title="2025 Operational Excellence Strategy",
        document_type=DocumentType.STRATEGY,
        full_text="""
# 2025 Operational Excellence Strategy

## Vision
Achieve industry-leading reliability and efficiency through automation and continuous improvement.

## Key Pillars

### 1. Reliability First
- Target 99.99% uptime for all critical services
- Zero-downtime deployments
- Automated failure recovery

### 2. Developer Productivity
- Reduce deployment time by 80%
- Automate 90% of operational tasks
- Self-service infrastructure

### 3. Customer Experience
- Page load times under 2 seconds
- 50% reduction in support tickets
- Proactive issue resolution

## Success Metrics
- System uptime: 99.99%
- Deployment frequency: Daily
- Mean time to recovery: < 5 minutes
- Customer satisfaction: > 90
""",
        strategic_themes=["reliability", "automation", "efficiency", "customer_experience"],
        strategic_pillars=["Reliability First", "Developer Productivity", "Customer Experience"]
    )
    
    # Company OKR
    company_okr = OKR(
        okr_id="okr_2025_q3",
        period="Q3 2025",
        level="company",
        objective_text="Deliver exceptional reliability and performance for our customers",
        owner="CEO",
        key_results=[
            KeyResult(
                kr_id="kr_uptime",
                text="Achieve 99.99% uptime across all critical services",
                target_value=99.99,
                current_value=99.5,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_deployment",
                text="Deploy new features daily with zero customer impact",
                target_value=30,
                current_value=4,
                unit="deployments/month"
            ),
            KeyResult(
                kr_id="kr_performance",
                text="All pages load in under 2 seconds (p95)",
                target_value=2.0,
                current_value=3.5,
                unit="seconds"
            )
        ]
    )
    
    return [strategy], [company_okr]


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"{title.center(70)}")
    print(f"{'=' * 70}\n")


def display_explanation(explanation):
    """Display explanation in readable format."""
    print(f"\nWork Item: {explanation.work_item_title}")
    print(f"Total Score: {explanation.total_score:.2f}/1.00 "
          f"(Confidence: {explanation.confidence:.0%})")
    print("-" * 50)
    
    # Executive summary
    print("\nEXECUTIVE SUMMARY:")
    print(explanation.executive_summary)
    
    # Score breakdown
    print("\nSCORE BREAKDOWN:")
    print(f"{'Factor':<25} {'Weight':<10} {'Score':<10} {'Contribution':<15}")
    print("-" * 70)
    
    for factor in sorted(explanation.factors, key=lambda f: f.weighted_score, reverse=True):
        print(f"{factor.factor_name:<25} {factor.weight:<10.0%} "
              f"{factor.raw_score:<10.2f} {factor.weighted_score:<15.2f}")
    
    # Key evidence
    print("\nKEY EVIDENCE:")
    for i, evidence in enumerate(explanation.key_evidence[:3], 1):
        print(f"{i}. [{evidence.source_type}] {evidence.text_excerpt[:80]}...")
        print(f"   → {evidence.explanation}")
    
    # Improvement opportunities
    print("\nIMPROVEMENT OPPORTUNITIES:")
    print(f"Current Score: {explanation.total_score:.2f}")
    print(f"Potential Score: {explanation.score_potential:.2f} "
          f"(+{explanation.score_potential - explanation.total_score:.2f})")
    
    for i, suggestion in enumerate(explanation.improvement_suggestions[:3], 1):
        print(f"\n{i}. {suggestion['title']} (+{suggestion['impact']:.2f} points)")
        print(f"   {suggestion['description']}")
        if 'actions' in suggestion:
            for action in suggestion['actions']:
                print(f"   • {action}")


def main():
    """Run the explainable scoring demo."""
    print_section("Explainable Scoring System Demo - August 5, 2025")
    
    # Create test data
    print("1. Creating test data...")
    work_items = create_diverse_work_items()
    strategy_docs, okrs = create_strategy_and_okrs()
    
    print(f"   ✓ {len(work_items)} work items with varying alignment")
    print(f"   ✓ {len(strategy_docs)} strategy documents")
    print(f"   ✓ {len(okrs)} OKRs")
    
    # Initialize scoring system
    print("\n2. Initializing explainable scoring system...")
    scorer = SemanticScorer()
    explainer = ExplainableScorer(alignment_calculator=scorer.alignment_calculator)
    
    # Score all items first
    print("\n3. Calculating alignment scores...")
    results = scorer.score_work_items(work_items, strategy_docs, okrs)
    print(f"   ✓ Scored {len(results['scored_items'])} items")
    
    # Generate explanations for each item
    print_section("Individual Score Explanations")
    
    explanations = []
    for item in work_items:
        explanation = explainer.explain_score(
            item,
            strategy_docs,
            okrs,
            ExplanationType.DETAILED
        )
        explanations.append(explanation)
        display_explanation(explanation)
        print("\n" + "="*70 + "\n")
    
    # Generate comparative analysis
    print_section("Comparative Analysis")
    
    comparison = explainer.generate_comparison_explanation(
        work_items,
        strategy_docs,
        okrs
    )
    print(comparison)
    
    # Show reasoning path example
    print_section("Detailed Reasoning Path Example")
    
    high_score_item = work_items[0]  # Zero-downtime deployment
    high_explanation = explanations[0]
    
    print(f"Examining: '{high_score_item.title}'")
    print("\nSTEP-BY-STEP REASONING:")
    for step in high_explanation.reasoning_path:
        print(f"  {step}")
    
    # Show visual data
    print_section("Visual Explanation Data")
    
    visual_data = explainer.generate_visual_explanation(
        high_score_item,
        high_score_item.alignment_score
    )
    
    print("RADAR CHART DATA (for multi-dimensional visualization):")
    radar = visual_data['radar_chart']
    for category, value in zip(radar['categories'], radar['values']):
        bar_length = int(value * 50)
        bar = '█' * bar_length
        print(f"{category:<25} {bar} {value:.2f}")
    
    print("\nIMPROVEMENT WATERFALL DATA:")
    waterfall = visual_data['improvement_waterfall']
    cumulative = waterfall['values'][0]
    print(f"{'Stage':<30} {'Impact':<10} {'Cumulative':<10}")
    print("-" * 50)
    print(f"{waterfall['categories'][0]:<30} {'-':<10} {cumulative:.2f}")
    
    for category, impact in zip(waterfall['categories'][1:], waterfall['values'][1:]):
        cumulative += impact
        print(f"{category:<30} +{impact:<9.2f} {cumulative:.2f}")
    
    # Export markdown report
    print_section("Exporting Detailed Reports")
    
    for i, explanation in enumerate(explanations):
        filename = f"score_explanation_{explanation.work_item_id}.md"
        with open(filename, 'w') as f:
            f.write(explanation.to_markdown())
        print(f"   ✓ Exported {filename}")
    
    # Export JSON for programmatic access
    json_data = {
        'generated_at': datetime.now().isoformat(),
        'explanations': [exp.to_json() for exp in explanations]
    }
    
    with open('score_explanations.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    print("   ✓ Exported score_explanations.json")
    
    # Demonstrate counterfactual analysis
    print_section("Counterfactual Analysis")
    
    low_score_item = work_items[2]  # Wiki documentation
    print(f"Analyzing: '{low_score_item.title}'")
    print(f"Current Score: {low_score_item.alignment_score.total_score:.2f}")
    print("\nWhat would improve this score?")
    
    low_explanation = explanations[2]
    print(f"\nMaximum achievable score: {low_explanation.score_potential:.2f}")
    print("\nRequired changes:")
    
    for suggestion in low_explanation.improvement_suggestions:
        print(f"\n• {suggestion['title']} (Impact: +{suggestion['impact']:.2f})")
        print(f"  Effort: {suggestion['effort']}")
        for action in suggestion.get('actions', []):
            print(f"  - {action}")
    
    # Key insights
    print_section("Key Insights from Explainable Scoring")
    
    print("TRANSPARENCY BENEFITS:")
    print("• Every score has clear, traceable reasoning")
    print("• Evidence is provided for all scoring decisions")
    print("• Improvement paths are specific and actionable")
    
    print("\nDECISION SUPPORT:")
    print("• High-scoring items clearly show strategic value")
    print("• Low-scoring items have specific improvement suggestions")
    print("• Comparative analysis enables informed prioritization")
    
    print("\nCONTINUOUS IMPROVEMENT:")
    print("• Teams understand what makes work strategic")
    print("• Planning improves as patterns become clear")
    print("• Alignment naturally increases over time")
    
    print_section("Demo Complete")
    print("The Explainable Scoring System successfully:")
    print("✓ Provided transparent scoring breakdowns")
    print("✓ Generated executive and detailed explanations")
    print("✓ Identified specific improvement opportunities")
    print("✓ Created visual data for dashboards")
    print("✓ Enabled comparative analysis")
    print("✓ Exported reports in multiple formats")


if __name__ == "__main__":
    main()