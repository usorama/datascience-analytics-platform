#!/usr/bin/env python3
"""
Comprehensive Integrated Demo - ADO Semantic Analysis Platform

This demonstrates the complete end-to-end workflow of the semantic analysis
platform, showcasing all major features working together.
"""

import sys
from pathlib import Path
from datetime import datetime
import json
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado.semantic import (
    # Models
    OKR, KeyResult, StrategyDocument, DocumentType,
    SemanticWorkItem,
    # Processing
    DocumentParser, TextPreprocessor,
    # Analysis
    SemanticScorer, SemanticEmbedder,
    # Q&A
    IntelligentQASystem,
    # Relationships
    RelationshipExtractor, RelationshipGraph,
    # Explainability
    ExplainableScorer, ExplanationType
)
from datascience_platform.ado import WorkItemType, ADOAnalyzer, ADODataSimulator
from datascience_platform.viz import DashboardGenerator


def print_section(title: str, emoji: str = ""):
    """Print formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{emoji} {title.center(78)} {emoji}")
    print(f"{'=' * 80}\n")


def create_realistic_scenario():
    """Create a realistic business scenario with interconnected data."""
    print_section("Setting Up Realistic Business Scenario", "🏢")
    
    # Company context
    print("COMPANY: TechVision Inc.")
    print("CONTEXT: Q3 2025 Planning - Digital Transformation Initiative")
    print("CHALLENGE: Aligning 50+ work items with strategic objectives")
    
    # Strategy documents
    strategy_docs = []
    
    # Digital Transformation Strategy
    digital_strategy = StrategyDocument(
        doc_id="doc_digital_transformation_2025",
        title="Digital Transformation Strategy 2025",
        document_type=DocumentType.STRATEGY,
        full_text="""
# Digital Transformation Strategy 2025

## Executive Summary
TechVision Inc. will become a fully digital-first organization by Q4 2025,
leveraging AI, automation, and cloud technologies to deliver exceptional
customer experiences and operational efficiency.

## Strategic Pillars

### 1. AI-Powered Customer Experience
Transform every customer touchpoint with intelligent, personalized experiences
- Deploy AI chatbots for 24/7 support
- Implement predictive analytics for customer needs
- Create personalized product recommendations
- Target: 90+ NPS score

### 2. Cloud-Native Architecture
Migrate all systems to cloud-native architecture for scalability and resilience
- Complete migration to Kubernetes
- Implement microservices architecture
- Achieve 99.99% uptime SLA
- Enable global deployment

### 3. Data-Driven Decision Making
Embed analytics and insights into every business process
- Real-time business intelligence dashboards
- Predictive analytics for all departments
- Automated reporting and alerts
- Data literacy training for all employees

### 4. Security and Compliance Excellence
Maintain highest standards of security and regulatory compliance
- Achieve SOC2 Type II certification
- Implement zero-trust security model
- GDPR and CCPA compliance
- Regular security audits

### 5. Employee Digital Empowerment
Equip employees with digital tools and skills for maximum productivity
- Digital collaboration platforms
- AI-assisted development tools
- Continuous learning programs
- Remote-first work environment

## Success Metrics
- Customer satisfaction: 90+ NPS
- Digital revenue: 80% of total
- Operational efficiency: 40% cost reduction
- Employee productivity: 2x improvement
- Security incidents: Zero critical
""",
        created_date=datetime(2025, 1, 15),
        strategic_pillars=[
            "AI-Powered Customer Experience",
            "Cloud-Native Architecture", 
            "Data-Driven Decision Making",
            "Security and Compliance Excellence",
            "Employee Digital Empowerment"
        ],
        strategic_themes=["ai", "cloud", "data", "security", "digital", "transformation"]
    )
    strategy_docs.append(digital_strategy)
    
    # Company OKRs
    okrs = []
    
    # Q3 Company OKR
    company_okr = OKR(
        okr_id="okr_company_q3_2025",
        period="Q3 2025",
        level="company",
        objective_text="Accelerate digital transformation to become industry leader in customer experience and operational efficiency",
        owner="CEO",
        key_results=[
            KeyResult(
                kr_id="kr_nps",
                text="Increase NPS score from 65 to 80",
                target_value=80,
                current_value=65,
                unit="NPS"
            ),
            KeyResult(
                kr_id="kr_digital_revenue",
                text="Achieve 60% of revenue from digital channels",
                target_value=60,
                current_value=42,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_automation",
                text="Automate 50% of manual processes",
                target_value=50,
                current_value=20,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_cloud_migration",
                text="Migrate 75% of applications to cloud",
                target_value=75,
                current_value=30,
                unit="%"
            )
        ],
        strategic_pillars=["AI-Powered Customer Experience", "Cloud-Native Architecture"]
    )
    okrs.append(company_okr)
    
    # Engineering OKR
    eng_okr = OKR(
        okr_id="okr_engineering_q3_2025",
        period="Q3 2025",
        level="team",
        objective_text="Build scalable, secure cloud infrastructure to support digital transformation",
        owner="VP Engineering",
        team="Engineering",
        parent_okr_id="okr_company_q3_2025",
        key_results=[
            KeyResult(
                kr_id="kr_uptime",
                text="Achieve 99.9% uptime for critical services",
                target_value=99.9,
                current_value=98.5,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_deployment",
                text="Deploy to production 20 times per day",
                target_value=20,
                current_value=5,
                unit="deployments/day"
            ),
            KeyResult(
                kr_id="kr_security",
                text="Zero critical security vulnerabilities",
                target_value=0,
                current_value=3,
                unit="vulnerabilities"
            )
        ]
    )
    okrs.append(eng_okr)
    
    # Product OKR
    product_okr = OKR(
        okr_id="okr_product_q3_2025",
        period="Q3 2025",
        level="team",
        objective_text="Launch AI-powered features that delight customers and drive engagement",
        owner="VP Product",
        team="Product",
        parent_okr_id="okr_company_q3_2025",
        key_results=[
            KeyResult(
                kr_id="kr_ai_adoption",
                text="60% of users actively using AI features",
                target_value=60,
                current_value=15,
                unit="%"
            ),
            KeyResult(
                kr_id="kr_feature_satisfaction",
                text="85% satisfaction rate for new features",
                target_value=85,
                current_value=72,
                unit="%"
            )
        ]
    )
    okrs.append(product_okr)
    
    # Work items with varying levels of detail and alignment
    work_items = []
    
    # High-alignment epic
    epic1 = SemanticWorkItem(
        work_item_id=5001,
        title="AI Customer Service Platform",
        work_item_type=WorkItemType.EPIC,
        state="Active",
        business_value_raw=95,
        story_points=144,
        full_description="""
## Overview
Build a comprehensive AI-powered customer service platform that transforms how we 
interact with customers, directly supporting our digital transformation strategy.

## Business Justification
Current customer service costs $12M annually with 65 NPS score. This platform will:
- Reduce service costs by 60% through automation
- Improve NPS to 80+ through instant, personalized responses
- Enable 24/7 multilingual support
- Scale to handle 10x volume without additional headcount

## Strategic Alignment
This epic directly supports:
- AI-Powered Customer Experience pillar
- Q3 OKR: Increase NPS from 65 to 80
- Digital revenue growth through better customer retention

## Technical Approach
- Natural language processing for intent recognition
- Machine learning for response generation
- Integration with existing CRM and knowledge base
- Real-time sentiment analysis
- Seamless handoff to human agents

## Success Metrics
- Response time: < 2 seconds
- Resolution rate: > 80% without human intervention
- Customer satisfaction: > 85%
- Cost per interaction: < $0.50
""",
        business_justification="Transforms customer service while reducing costs by $7M annually",
        acceptance_criteria_text="""
- AI handles 80% of inquiries without human intervention
- Average response time under 2 seconds
- Multilingual support for 10 languages
- Sentiment analysis accuracy > 90%
- Seamless CRM integration
- GDPR compliant data handling
""",
        area_path="AI/ML Team",
        strategic_themes=["ai", "customer_experience", "digital_transformation"],
        pi_number=15
    )
    work_items.append(epic1)
    
    # Medium-alignment feature
    feature1 = SemanticWorkItem(
        work_item_id=5002,
        parent_id=5001,
        title="Implement NLP Intent Recognition Engine",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=80,
        story_points=55,
        full_description="""
Develop the core NLP engine that understands customer intents from natural language.
This is the foundation of our AI customer service platform.

Technical requirements:
- Support 95% accuracy on common intents
- Process requests in under 100ms
- Handle misspellings and colloquialisms
- Multi-language support

This contributes to our NPS improvement OKR by ensuring customers get accurate help quickly.
""",
        acceptance_criteria_text="""
- 95% accuracy on test dataset
- <100ms processing time
- Handles 20 intent categories
- Supports English, Spanish, French initially
""",
        area_path="AI/ML Team",
        strategic_themes=["ai", "nlp", "customer_experience"]
    )
    work_items.append(feature1)
    
    # Low-alignment item
    story1 = SemanticWorkItem(
        work_item_id=5003,
        title="Update team meeting room calendar",
        work_item_type=WorkItemType.USER_STORY,
        state="New",
        business_value_raw=10,
        story_points=2,
        full_description="Update the conference room booking system with new room names",
        area_path="Facilities Team"
    )
    work_items.append(story1)
    
    # Technical debt item
    feature2 = SemanticWorkItem(
        work_item_id=5004,
        title="Database Performance Optimization",
        work_item_type=WorkItemType.FEATURE,
        state="Active",
        business_value_raw=70,
        story_points=34,
        full_description="""
Optimize database queries and indexing to improve application performance.
Current response times are affecting user experience and our ability to scale.

Performance impact:
- Reduce query times by 70%
- Enable handling 5x current load
- Reduce infrastructure costs

This supports our operational efficiency goals and cloud migration strategy.
""",
        technical_notes="PostgreSQL query optimization and index tuning",
        area_path="Platform Team",
        strategic_themes=["performance", "scalability", "efficiency"]
    )
    work_items.append(feature2)
    
    # Add more work items to simulate realistic portfolio
    simulator = ADODataSimulator(num_epics=2, seed=42)
    simulated_df = simulator.generate_work_items()
    
    # Convert first 10 simulated items
    for idx, row in simulated_df.head(10).iterrows():
        item = SemanticWorkItem(
            work_item_id=5100 + idx,
            title=row['Title'],
            work_item_type=WorkItemType(row['Work Item Type']),
            state=row['State'],
            business_value_raw=row.get('Business Value', 50),
            story_points=row.get('Story Points', 8),
            full_description=row.get('Description', ''),
            area_path=row.get('Area Path', 'Team'),
            parent_id=row.get('Parent', None)
        )
        work_items.append(item)
    
    print(f"\n✅ Created scenario with:")
    print(f"   • {len(strategy_docs)} strategy documents")
    print(f"   • {len(okrs)} OKRs with {sum(len(okr.key_results) for okr in okrs)} key results")
    print(f"   • {len(work_items)} work items across multiple teams")
    
    return strategy_docs, okrs, work_items


def demonstrate_semantic_analysis(strategy_docs, okrs, work_items):
    """Demonstrate core semantic analysis capabilities."""
    print_section("Semantic Analysis Engine", "🧠")
    
    print("Initializing semantic analysis components...")
    embedder = SemanticEmbedder()
    scorer = SemanticScorer(embedder=embedder)
    
    # Perform analysis
    print("\nAnalyzing strategic alignment...")
    start_time = time.time()
    
    results = scorer.score_work_items(
        work_items,
        strategy_docs,
        okrs,
        generate_questions=True
    )
    
    analysis_time = time.time() - start_time
    print(f"✅ Analysis completed in {analysis_time:.2f} seconds")
    
    # Show results summary
    print("\nANALYSIS SUMMARY:")
    print("-" * 60)
    
    scores = [item['alignment_score']['total_score'] 
              for item in results['scored_items']]
    
    print(f"Items analyzed: {len(scores)}")
    print(f"Average alignment score: {sum(scores)/len(scores):.2f}")
    print(f"High-value items (≥0.7): {sum(1 for s in scores if s >= 0.7)}")
    print(f"Medium-value items (0.3-0.7): {sum(1 for s in scores if 0.3 <= s < 0.7)}")
    print(f"Low-value items (<0.3): {sum(1 for s in scores if s < 0.3)}")
    
    # Information gaps
    gaps = results.get('gaps', [])
    print(f"\nInformation gaps identified: {len(gaps)}")
    for gap in gaps[:2]:
        print(f"  • {gap.description}")
    
    # Questions generated
    questions = results.get('questions', [])
    print(f"\nQuestions generated: {len(questions)}")
    
    return results


def demonstrate_explainable_scoring(work_items, strategy_docs, okrs):
    """Demonstrate explainable scoring system."""
    print_section("Explainable Scoring System", "📊")
    
    explainer = ExplainableScorer()
    
    # Pick high and low scoring items
    high_item = work_items[0]  # AI Customer Service Platform
    low_item = work_items[2]   # Meeting room calendar
    
    print("Generating detailed explanations for contrasting items...")
    
    # High-scoring item explanation
    print("\n1. HIGH-SCORING ITEM ANALYSIS")
    print("-" * 40)
    
    high_explanation = explainer.explain_score(
        high_item,
        strategy_docs,
        okrs,
        ExplanationType.DETAILED
    )
    
    print(f"Item: {high_item.title}")
    print(f"Score: {high_explanation.total_score:.2f} (Confidence: {high_explanation.confidence:.0%})")
    print(f"\nExecutive Summary:")
    print(high_explanation.executive_summary)
    
    print(f"\nScore Breakdown:")
    for factor in high_explanation.factors:
        print(f"  • {factor.factor_name}: {factor.raw_score:.2f} "
              f"(contributes {factor.contribution_percentage:.0f}%)")
    
    print(f"\nImprovement Potential: +{high_explanation.score_potential - high_explanation.total_score:.2f}")
    
    # Low-scoring item explanation
    print("\n2. LOW-SCORING ITEM ANALYSIS")
    print("-" * 40)
    
    low_explanation = explainer.explain_score(
        low_item,
        strategy_docs,
        okrs,
        ExplanationType.DETAILED
    )
    
    print(f"Item: {low_item.title}")
    print(f"Score: {low_explanation.total_score:.2f}")
    print(f"\nExplanation: {low_explanation.summary}")
    print(f"\nKey improvement:")
    if low_explanation.improvement_suggestions:
        top_improvement = low_explanation.improvement_suggestions[0]
        print(f"  • {top_improvement['title']} (+{top_improvement['impact']:.2f} points)")
    
    # Export explanation
    report_path = Path("high_score_explanation.md")
    with open(report_path, 'w') as f:
        f.write(high_explanation.to_markdown())
    print(f"\n✅ Detailed explanation exported to {report_path}")


def demonstrate_relationship_extraction(work_items, okrs, strategy_docs):
    """Demonstrate relationship extraction and graph building."""
    print_section("Relationship Extraction & Knowledge Graph", "🕸️")
    
    print("Extracting entities and relationships...")
    
    extractor = RelationshipExtractor()
    graph = RelationshipGraph()
    
    # Extract from all sources
    all_nodes = []
    all_relationships = []
    
    # Work items
    wi_nodes, wi_rels = extractor.extract_from_work_items(work_items)
    all_nodes.extend(wi_nodes)
    all_relationships.extend(wi_rels)
    print(f"  • Work items: {len(wi_nodes)} entities, {len(wi_rels)} relationships")
    
    # OKRs
    okr_nodes, okr_rels = extractor.extract_from_okrs(okrs, work_items)
    all_nodes.extend(okr_nodes)
    all_relationships.extend(okr_rels)
    print(f"  • OKRs: {len(okr_nodes)} entities, {len(okr_rels)} relationships")
    
    # Strategy documents
    doc_nodes, doc_rels = extractor.extract_from_strategy_docs(strategy_docs)
    all_nodes.extend(doc_nodes)
    all_relationships.extend(doc_rels)
    print(f"  • Strategy: {len(doc_nodes)} entities, {len(doc_rels)} relationships")
    
    # Find semantic relationships
    semantic_rels = extractor.find_semantic_relationships(all_nodes[:20], top_k=3)
    all_relationships.extend(semantic_rels)
    print(f"  • Semantic: {len(semantic_rels)} relationships discovered")
    
    # Build graph
    graph.add_nodes(all_nodes)
    graph.add_relationships(all_relationships)
    
    graph_data = graph.export_to_json()
    print(f"\n✅ Built knowledge graph with {graph_data['statistics']['node_count']} nodes "
          f"and {graph_data['statistics']['edge_count']} edges")
    
    # Analyze key entities
    print("\nKEY ENTITY ANALYSIS:")
    centrality = graph.get_centrality_metrics()
    top_central = sorted(
        centrality['pagerank'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    print("Most important entities:")
    for entity_id, score in top_central:
        if entity_id in graph.graph.nodes:
            node = graph.graph.nodes[entity_id]
            print(f"  • {node['title'][:50]} ({node['entity_type']}): {score:.3f}")
    
    # Impact analysis
    ai_epic_id = "wi_5001"
    print(f"\nIMPACT ANALYSIS for '{work_items[0].title}':")
    impact = graph.get_impact_analysis(ai_epic_id)
    print(f"  • Directly impacts: {len(impact['directly_impacts'])} entities")
    print(f"  • Indirectly impacts: {len(impact['indirectly_impacts'])} entities")
    print(f"  • Total downstream impact: {impact['total_affected']} entities")
    
    return graph


def demonstrate_interactive_qa(work_items, strategy_docs, okrs, results):
    """Demonstrate Q&A system for gathering missing information."""
    print_section("Intelligent Q&A System", "❓")
    
    qa_system = IntelligentQASystem()
    
    # Create Q&A session
    print("Creating Q&A session to address information gaps...")
    session = qa_system.create_session(
        work_items,
        strategy_docs,
        okrs,
        focus_areas=["strategic_alignment", "metrics"]
    )
    
    progress = session.get_progress()
    print(f"\n✅ Generated {progress['total_questions']} questions")
    print(f"   • Critical: {progress['by_severity']['critical']['total']}")
    print(f"   • High: {progress['by_severity']['high']['total']}")
    print(f"   • Medium: {progress['by_severity']['medium']['total']}")
    
    # Simulate answering some questions
    print("\nSIMULATING Q&A INTERACTION:")
    print("-" * 40)
    
    # Answer first 3 questions
    for i in range(min(3, progress['total_questions'])):
        question = session.get_next_question()
        if not question:
            break
        
        print(f"\nQ{i+1}: {question.text}")
        print(f"Context: {question.context}")
        
        # Simulate answer based on question type
        if "strategic objective" in question.text.lower():
            answer = "Operational Excellence"
        elif "metric" in question.text.lower():
            answer = "Reduce meeting scheduling time by 50%"
        else:
            answer = "This supports internal efficiency improvements"
        
        print(f"A: {answer}")
        
        is_valid, error_msg, follow_ups = session.answer_question(
            question.question_id,
            answer
        )
        
        if is_valid:
            print("✓ Answer recorded")
            if follow_ups:
                print(f"  → Generated {len(follow_ups)} follow-up questions")
    
    # Complete session
    summary = session.complete_session()
    print(f"\n✅ Q&A session completed:")
    print(f"   • Questions answered: {summary['answers_collected']}")
    print(f"   • Work items updated: {summary['work_items_updated']}")
    
    # Recalculate scores
    print("\nRecalculating alignment scores with new information...")
    new_scores = qa_system.recalculate_alignment(session, strategy_docs, okrs)
    
    # Show improvement
    improvements = []
    for item_id, new_score in new_scores.items():
        old_item = next(
            (item for item in results['scored_items'] 
             if item['work_item_id'] == item_id),
            None
        )
        if old_item:
            old_score = old_item['alignment_score']['total_score']
            improvement = new_score.total_score - old_score
            if improvement > 0:
                improvements.append((item_id, improvement))
    
    if improvements:
        print("\nSCORE IMPROVEMENTS:")
        for item_id, improvement in improvements[:3]:
            print(f"  • Item {item_id}: +{improvement:.2f} points")


def demonstrate_dashboard_generation(results, work_items):
    """Generate visual dashboards from analysis results."""
    print_section("Dashboard Generation", "📈")
    
    print("Generating interactive dashboards...")
    
    # Prepare data for dashboard
    dashboard_data = []
    for item in results['scored_items']:
        # Find original work item
        work_item = next(
            (wi for wi in work_items if wi.work_item_id == item['work_item_id']),
            None
        )
        if work_item:
            dashboard_data.append({
                'Work Item ID': item['work_item_id'],
                'Title': item['title'],
                'Type': item['type'],
                'Alignment Score': item['alignment_score']['total_score'],
                'Strategic Alignment': item['alignment_score']['strategic_alignment'],
                'OKR Contribution': item['alignment_score']['okr_contribution'],
                'Confidence': item['alignment_score']['confidence'],
                'Team': work_item.area_path,
                'State': work_item.state,
                'Story Points': work_item.story_points
            })
    
    # Create dashboard
    dashboard_gen = DashboardGenerator()
    
    # Add various visualizations
    dashboard = dashboard_gen.create_dashboard(
        title="ADO Strategic Alignment Dashboard",
        data=dashboard_data
    )
    
    # Save dashboard
    output_path = Path("strategic_alignment_dashboard.html")
    dashboard_gen.save_dashboard(dashboard, str(output_path))
    
    print(f"✅ Interactive dashboard saved to {output_path}")
    print("   Dashboard includes:")
    print("   • Alignment score distribution")
    print("   • Team-wise analysis")
    print("   • Strategic vs OKR contribution scatter")
    print("   • Work type breakdown")


def demonstrate_end_to_end_workflow():
    """Run complete end-to-end demonstration."""
    print_section("ADO Semantic Analysis Platform - Integrated Demo", "🚀")
    print(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    
    # Step 1: Create scenario
    strategy_docs, okrs, work_items = create_realistic_scenario()
    
    # Step 2: Semantic analysis
    results = demonstrate_semantic_analysis(strategy_docs, okrs, work_items)
    
    # Step 3: Explainable scoring
    demonstrate_explainable_scoring(work_items, strategy_docs, okrs)
    
    # Step 4: Relationship extraction
    graph = demonstrate_relationship_extraction(work_items, okrs, strategy_docs)
    
    # Step 5: Interactive Q&A
    demonstrate_interactive_qa(work_items, strategy_docs, okrs, results)
    
    # Step 6: Dashboard generation
    demonstrate_dashboard_generation(results, work_items)
    
    # Final summary
    print_section("Demonstration Complete", "✨")
    
    print("KEY OUTCOMES:")
    print("✓ Analyzed 14+ work items for strategic alignment")
    print("✓ Generated explainable scores with improvement recommendations")
    print("✓ Built knowledge graph with 50+ entities and relationships")
    print("✓ Identified and addressed information gaps through Q&A")
    print("✓ Created interactive dashboards for stakeholder communication")
    
    print("\nBUSINESS VALUE DELIVERED:")
    print("• Objective prioritization based on strategic alignment")
    print("• Clear explanations for every scoring decision")
    print("• Actionable recommendations for improving alignment")
    print("• Reduced subjective bias in planning decisions")
    print("• Improved visibility into work-strategy connections")
    
    print("\nNEXT STEPS:")
    print("1. Run Streamlit interface: streamlit run streamlit_ado_semantic.py")
    print("2. Upload your actual ADO data (CSV export)")
    print("3. Configure scoring weights for your organization")
    print("4. Review and act on alignment insights")
    print("5. Use Q&A to continuously improve data quality")
    
    print("\n" + "="*80)
    print("Thank you for exploring the ADO Semantic Analysis Platform!")
    print("Built with Python, NLP, and a focus on explainable AI")
    print("="*80)


def main():
    """Main entry point."""
    try:
        demonstrate_end_to_end_workflow()
    except Exception as e:
        print(f"\n❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()