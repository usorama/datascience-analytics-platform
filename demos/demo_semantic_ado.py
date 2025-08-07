#!/usr/bin/env python3
"""
Semantic ADO Analysis Demo

This demonstrates how the enhanced DataScience Analytics Platform uses
natural language processing to understand strategic alignment between
OKRs, strategy documents, and work items.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado.semantic import (
    OKR, KeyResult, StrategyDocument, DocumentSection,
    SemanticWorkItem, DocumentType,
    TextPreprocessor, DocumentParser,
    SemanticEmbedder, StrategicAlignmentCalculator, SemanticScorer
)
from datascience_platform.ado import ADODataSimulator, WorkItemType


def create_sample_strategy_docs():
    """Create sample strategy documents for demo."""
    docs = []
    
    # Company Vision 2025
    vision_doc = StrategyDocument(
        doc_id="doc_vision_2025",
        title="Company Vision 2025",
        document_type=DocumentType.VISION,
        full_text="""
# Company Vision 2025

We aspire to be the leading platform for intelligent business automation, 
empowering organizations to achieve operational excellence through AI-driven insights.

## Strategic Pillars

1. **Customer Experience Excellence**
   - Deliver intuitive, AI-powered experiences that delight users
   - Achieve industry-leading NPS of 70+
   - Reduce customer effort score by 50%

2. **Operational Efficiency Through Automation**
   - Automate 80% of routine business processes
   - Reduce operational costs by 35%
   - Improve process efficiency by 3x

3. **Innovation and Market Leadership**
   - Launch 5 breakthrough AI features annually
   - Maintain 25% market share in our segment
   - File 20+ patents in AI/ML applications

4. **Security and Compliance First**
   - Achieve SOC2, ISO 27001, and GDPR compliance
   - Zero security breaches
   - 99.99% uptime SLA

5. **Sustainable Growth**
   - Reach $500M ARR by 2025
   - Maintain 40% YoY growth
   - Achieve carbon neutrality
""",
        created_date=datetime(2025, 1, 15),
        strategic_pillars=[
            "Customer Experience Excellence",
            "Operational Efficiency Through Automation",
            "Innovation and Market Leadership",
            "Security and Compliance First",
            "Sustainable Growth"
        ]
    )
    docs.append(vision_doc)
    
    # Product Strategy Q3 2025
    product_strategy = StrategyDocument(
        doc_id="doc_product_q3_2025",
        title="Product Strategy Q3 2025",
        document_type=DocumentType.STRATEGY,
        full_text="""
# Product Strategy Q3 2025

## Executive Summary
Focus on AI-powered features that directly impact customer value realization
and operational efficiency.

## Key Initiatives

### 1. Intelligent Automation Suite
- Natural language process automation
- Predictive workflow optimization
- Self-healing systems

### 2. Advanced Analytics Platform
- Real-time business intelligence
- Predictive analytics for all users
- Automated insight generation

### 3. Security Enhancement Program
- Zero-trust architecture implementation
- AI-powered threat detection
- Automated compliance reporting

## Success Metrics
- Feature adoption rate > 60%
- Customer satisfaction > 85%
- Time-to-value < 7 days
- Security incidents = 0
""",
        created_date=datetime(2025, 6, 1),
        strategic_themes=["innovation", "customer", "efficiency", "security"]
    )
    docs.append(product_strategy)
    
    return docs


def create_sample_okrs():
    """Create sample OKRs for demo."""
    okrs = []
    
    # Company OKR
    company_okr = OKR(
        okr_id="okr_company_q3_2025",
        period="Q3 2025",
        level="company",
        objective_text="Accelerate customer value realization through intelligent automation",
        owner="CEO",
        key_results=[
            KeyResult(
                kr_id="kr_1",
                text="Increase customer NPS from 45 to 60",
                target_value=60,
                current_value=45,
                unit="NPS"
            ),
            KeyResult(
                kr_id="kr_2",
                text="Reduce average time-to-value from 21 days to 7 days",
                target_value=7,
                current_value=21,
                unit="days"
            ),
            KeyResult(
                kr_id="kr_3",
                text="Achieve 80% automation rate for tier-1 processes",
                target_value=80,
                current_value=55,
                unit="%"
            )
        ],
        strategic_pillars=["Customer Experience Excellence", "Operational Efficiency"],
        business_impact="Direct impact on customer retention and expansion revenue"
    )
    okrs.append(company_okr)
    
    # Product Team OKR
    product_okr = OKR(
        okr_id="okr_product_q3_2025",
        period="Q3 2025",
        level="team",
        objective_text="Launch AI-powered features that transform user productivity",
        owner="VP Product",
        team="Product",
        key_results=[
            KeyResult(
                kr_id="kr_p1",
                text="Ship natural language automation builder with 90% accuracy",
                target_value=90,
                current_value=0,
                unit="% accuracy"
            ),
            KeyResult(
                kr_id="kr_p2",
                text="Achieve 70% adoption rate for AI assistant features",
                target_value=70,
                current_value=0,
                unit="% adoption"
            ),
            KeyResult(
                kr_id="kr_p3",
                text="Reduce feature configuration time by 75%",
                target_value=75,
                current_value=0,
                unit="% reduction"
            )
        ],
        parent_okr_id="okr_company_q3_2025",
        strategic_pillars=["Innovation and Market Leadership"]
    )
    okrs.append(product_okr)
    
    # Engineering Team OKR
    eng_okr = OKR(
        okr_id="okr_engineering_q3_2025",
        period="Q3 2025",
        level="team",
        objective_text="Build scalable, secure infrastructure for AI workloads",
        owner="VP Engineering",
        team="Engineering",
        key_results=[
            KeyResult(
                kr_id="kr_e1",
                text="Achieve 99.99% uptime for AI services",
                target_value=99.99,
                current_value=99.5,
                unit="% uptime"
            ),
            KeyResult(
                kr_id="kr_e2",
                text="Reduce AI inference latency to under 100ms p95",
                target_value=100,
                current_value=250,
                unit="ms"
            ),
            KeyResult(
                kr_id="kr_e3",
                text="Complete SOC2 Type II certification",
                target_value=100,
                current_value=60,
                unit="% complete"
            )
        ],
        parent_okr_id="okr_company_q3_2025",
        strategic_pillars=["Security and Compliance First", "Operational Efficiency"]
    )
    okrs.append(eng_okr)
    
    return okrs


def create_sample_work_items():
    """Create sample work items with rich text descriptions."""
    items = []
    
    # Epic 1: Natural Language Automation
    epic1 = SemanticWorkItem(
        work_item_id=1001,
        title="Natural Language Process Automation Platform",
        work_item_type=WorkItemType.EPIC,
        state="Active",
        business_value_raw=95,
        story_points=100,
        full_description="""
## Overview
Build a comprehensive platform that allows users to create automated workflows 
using natural language descriptions instead of complex configuration.

## Business Justification
Current workflow automation tools require technical expertise and significant 
time investment. Our research shows that 73% of business users abandon automation 
attempts due to complexity. By enabling natural language automation, we can:
- Reduce automation setup time from hours to minutes
- Increase automation adoption from 15% to 70%
- Directly support our Q3 OKR of reducing time-to-value to 7 days

## Success Criteria
- Users can describe a process in plain English and get a working automation
- 90% accuracy in understanding user intent
- Support for 50+ common business processes
- Integration with existing systems (CRM, ERP, etc.)

## Strategic Alignment
This directly supports our Customer Experience Excellence pillar by removing 
technical barriers and our Operational Efficiency pillar by democratizing automation.
""",
        acceptance_criteria_text="""
- Natural language input processed with >90% accuracy
- Visual workflow builder generated from text description
- One-click deployment of automated workflows
- Real-time validation and error handling
- Support for conditional logic and loops
""",
        business_justification="Reduces customer time-to-value from 21 to 7 days, directly impacting Q3 company OKR",
        pi_number=15,
        area_path="Product Team",
        strategic_themes=["customer_experience", "innovation", "efficiency"]
    )
    items.append(epic1)
    
    # Feature 1: NLP Engine
    feature1 = SemanticWorkItem(
        work_item_id=1002,
        parent_id=1001,
        title="Advanced NLP Engine for Workflow Understanding",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=85,
        story_points=40,
        full_description="""
Develop state-of-the-art NLP engine that can understand business process 
descriptions and convert them into structured workflow definitions.

Key capabilities:
- Intent recognition for business processes
- Entity extraction (systems, data, conditions, actions)
- Context understanding across multiple sentences
- Support for industry-specific terminology

This is the core AI component that enables natural language automation,
directly supporting our innovation strategy and AI-first approach.
""",
        acceptance_criteria_text="""
- Parse complex business process descriptions
- Extract all workflow components with 90% accuracy
- Handle ambiguity through clarifying questions
- Support 10+ languages
""",
        area_path="AI/ML Team",
        strategic_themes=["innovation", "customer_experience"]
    )
    items.append(feature1)
    
    # Feature 2: Security Framework
    feature2 = SemanticWorkItem(
        work_item_id=1003,
        parent_id=1001,
        title="Zero-Trust Security Framework for Automated Workflows",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=90,
        story_points=50,
        full_description="""
Implement comprehensive security framework ensuring all automated workflows 
adhere to zero-trust principles and maintain SOC2 compliance.

## Requirements
- Every workflow action must be authenticated and authorized
- Audit trail for all automated actions
- Encryption at rest and in transit
- Role-based access control with principle of least privilege

## Compliance Impact
This feature is critical for maintaining our SOC2 Type II certification and 
supports our Security and Compliance First strategic pillar.
""",
        business_justification="Required for SOC2 compliance and enterprise customer adoption",
        area_path="Security Team",
        strategic_themes=["security_compliance", "quality"]
    )
    items.append(feature2)
    
    # User Story 1: Voice Input
    story1 = SemanticWorkItem(
        work_item_id=1004,
        parent_id=1002,
        title="As a business user, I want to describe workflows using voice input",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=70,
        story_points=13,
        full_description="""
Enable voice input for workflow creation to further reduce barriers for 
non-technical users. This supports accessibility requirements and improves 
user experience for mobile users.

Technical approach:
- Integrate with speech-to-text APIs
- Implement voice command recognition
- Add confirmation and correction flows
""",
        acceptance_criteria_text="""
- Voice input accurately transcribed in real-time
- Support for voice commands like "correct that" or "start over"
- Visual feedback during voice input
- Fallback to text input always available
""",
        area_path="Mobile Team",
        strategic_themes=["customer_experience", "innovation"]
    )
    items.append(story1)
    
    # User Story 2: Compliance Reporting
    story2 = SemanticWorkItem(
        work_item_id=1005,
        parent_id=1003,
        title="As a compliance officer, I need automated SOC2 evidence collection",
        work_item_type=WorkItemType.USER_STORY,
        state="Active",
        business_value_raw=80,
        story_points=8,
        full_description="""
Automate the collection and organization of evidence required for SOC2 audits.
This will save 40 hours per quarter in manual evidence gathering and ensure
we maintain continuous compliance.

The system should automatically:
- Log all access control changes
- Document security incidents and responses  
- Track system availability metrics
- Generate audit-ready reports
""",
        acceptance_criteria_text="""
- Automated daily evidence collection
- Quarterly compliance reports generated
- Integration with audit tools
- Real-time compliance dashboard
""",
        area_path="Compliance Team",
        strategic_themes=["security_compliance", "efficiency"]
    )
    items.append(story2)
    
    # Low-alignment item for contrast
    story3 = SemanticWorkItem(
        work_item_id=1006,
        parent_id=None,
        title="Update team page profile photos",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=10,
        story_points=2,
        full_description="Update profile photos on the team page to reflect new hires",
        area_path="Marketing Team",
        strategic_themes=[]
    )
    items.append(story3)
    
    return items


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"{title.center(70)}")
    print(f"{'=' * 70}\n")


def demonstrate_semantic_analysis():
    """Main demo of semantic ADO analysis."""
    print_section("Semantic ADO Analysis Demo - August 5, 2025")
    
    # Create sample data
    print("1. Creating sample data...")
    strategy_docs = create_sample_strategy_docs()
    okrs = create_sample_okrs()
    work_items = create_sample_work_items()
    
    print(f"   ✓ {len(strategy_docs)} strategy documents")
    print(f"   ✓ {len(okrs)} OKRs with {sum(len(okr.key_results) for okr in okrs)} key results")
    print(f"   ✓ {len(work_items)} work items")
    
    # Initialize semantic components
    print("\n2. Initializing semantic analysis engine...")
    embedder = SemanticEmbedder()
    scorer = SemanticScorer(embedder=embedder)
    
    # Process text
    print("\n3. Processing text content...")
    preprocessor = TextPreprocessor()
    for item in work_items:
        # Extract themes
        if item.full_description:
            item.strategic_themes.extend(
                scorer.theme_extractor.extract_themes(item.full_description)
            )
            item.strategic_themes = list(set(item.strategic_themes))
    
    # Run semantic scoring
    print("\n4. Calculating semantic alignment scores...")
    results = scorer.score_work_items(
        work_items,
        strategy_docs,
        okrs,
        generate_questions=True
    )
    
    # Display results
    print_section("Semantic Alignment Results")
    
    print("TOP STRATEGICALLY ALIGNED ITEMS:")
    print("-" * 70)
    
    # Sort by alignment score
    scored_items = sorted(
        results['scored_items'],
        key=lambda x: x['alignment_score']['total_score'],
        reverse=True
    )
    
    for item in scored_items[:5]:
        print(f"\n[{item['work_item_id']}] {item['title']}")
        print(f"Type: {item['type']}")
        
        scores = item['alignment_score']
        print(f"\nAlignment Scores:")
        print(f"  • Strategic Alignment: {scores['strategic_alignment']:.2f}")
        print(f"  • OKR Contribution: {scores['okr_contribution']:.2f}")
        print(f"  • Thematic Coherence: {scores['thematic_coherence']:.2f}")
        print(f"  • Total Score: {scores['total_score']:.2f} (Confidence: {scores['confidence']:.0%})")
        
        print(f"\nExplanation: {scores['explanation']}")
        
        if item['evidence']:
            print(f"\nEvidence:")
            for evidence in item['evidence'][:2]:
                print(f"  • {evidence}")
        
        print("-" * 70)
    
    # Show gaps and questions
    if results['gaps']:
        print_section("Identified Information Gaps")
        
        for gap in results['gaps']:
            print(f"\n❗ {gap.description}")
            print(f"   Severity: {gap.severity.upper()}")
            print(f"   Impact: {gap.potential_impact}")
            if gap.affected_items:
                print(f"   Affected items: {', '.join(str(id) for id in gap.affected_items[:5])}")
    
    if results['questions']:
        print_section("Intelligent Questions for Clarification")
        
        for i, question in enumerate(results['questions'][:5], 1):
            print(f"\nQ{i}: {question.text}")
            print(f"Context: {question.context}")
            print(f"Impact: {question.business_impact}")
            if question.options:
                print("Options:")
                for j, option in enumerate(question.options, 1):
                    print(f"  {j}. {option}")
    
    # Show insights
    insights = results['insights']
    if 'summary' in insights:
        print_section("Strategic Insights")
        
        summary = insights['summary']
        if 'alignment_distribution' in summary:
            dist = summary['alignment_distribution']
            print("Work Item Alignment Distribution:")
            print(f"  • High alignment (≥0.7): {dist['high']:.0%}")
            print(f"  • Medium alignment (0.3-0.7): {dist['medium']:.0%}")
            print(f"  • Low alignment (<0.3): {dist['low']:.0%}")
            print(f"  • Average score: {dist['mean']:.2f} (σ={dist['std']:.2f})")
        
        if 'theme_analysis' in summary:
            theme_analysis = summary['theme_analysis']
            print("\nStrategic Theme Coverage:")
            if theme_analysis['well_covered']:
                print(f"  ✓ Well covered: {', '.join(theme_analysis['well_covered'])}")
            if theme_analysis['under_covered']:
                print(f"  ⚠ Under covered: {', '.join(theme_analysis['under_covered'])}")
    
    # Demonstrate contrast with low-alignment item
    print_section("Example: Low Strategic Alignment")
    
    low_item = next((item for item in scored_items if item['work_item_id'] == 1006), None)
    if low_item:
        print(f"[{low_item['work_item_id']}] {low_item['title']}")
        scores = low_item['alignment_score']
        print(f"\nTotal Score: {scores['total_score']:.2f}")
        print(f"Explanation: {scores['explanation']}")
        print("\nRecommendation: This item shows limited strategic value. Consider:")
        print("  1. Cancelling or deferring this work")
        print("  2. Updating the description to show strategic connection")
        print("  3. Bundling with other strategic initiatives")


def demonstrate_interactive_qa():
    """Demonstrate interactive Q&A capability."""
    print_section("Interactive Q&A Demo")
    
    print("The system can intelligently ask questions to gather missing information:")
    print("\nExample Q&A Session:")
    print("-" * 50)
    
    print("\nSystem: I notice that several work items lack clear strategic alignment.")
    print("System: What strategic objective does 'Update team page profile photos' support?")
    print("\nOptions:")
    print("  1. Customer Experience improvement")
    print("  2. Operational Excellence")  
    print("  3. Revenue Growth")
    print("  4. Technical Debt Reduction")
    print("  5. Not strategically aligned (consider cancelling)")
    print("  6. Other (please specify)")
    
    print("\nUser selects: 5. Not strategically aligned")
    
    print("\nSystem: Thank you. Based on your response, I recommend:")
    print("  • Cancel or defer this item to focus on strategic work")
    print("  • Current strategic alignment score: 0.08/1.00")
    print("  • This would free up 2 story points for strategic initiatives")
    
    print("\nSystem: Would you like me to suggest strategic work items that could")
    print("        use these 2 story points instead?")


def main():
    """Run all demos."""
    try:
        # Main semantic analysis demo
        demonstrate_semantic_analysis()
        
        # Interactive Q&A demo
        demonstrate_interactive_qa()
        
        print_section("Demo Complete")
        print("Key Capabilities Demonstrated:")
        print("  ✓ Semantic understanding of strategy documents and OKRs")
        print("  ✓ Multi-dimensional alignment scoring with explanations")
        print("  ✓ Evidence-based prioritization recommendations")
        print("  ✓ Intelligent gap detection and question generation")
        print("  ✓ Natural language explanations for all decisions")
        
        print("\nThis semantic analysis transforms subjective 'business value' scores")
        print("into objective, explainable strategic alignment measurements.")
        
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()