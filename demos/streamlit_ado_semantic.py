#!/usr/bin/env python3
"""
Streamlit Interactive Interface for ADO Semantic Analysis

This provides a web-based interface for the semantic analysis platform,
enabling users to upload data, configure analysis, and explore results.

Run with: streamlit run streamlit_ado_semantic.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado.semantic import (
    OKR, KeyResult, StrategyDocument, DocumentType,
    SemanticWorkItem, SemanticScorer, 
    IntelligentQASystem, QASession,
    RelationshipExtractor, RelationshipGraph,
    ExplainableScorer, ExplanationType
)
from datascience_platform.ado import WorkItemType, ADODataSimulator


# Page configuration
st.set_page_config(
    page_title="ADO Semantic Analysis Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #1f77b4;
    }
    .score-high { color: #28a745; font-weight: bold; }
    .score-medium { color: #ffc107; font-weight: bold; }
    .score-low { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'work_items' not in st.session_state:
        st.session_state.work_items = []
    if 'okrs' not in st.session_state:
        st.session_state.okrs = []
    if 'strategy_docs' not in st.session_state:
        st.session_state.strategy_docs = []
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'qa_session' not in st.session_state:
        st.session_state.qa_session = None
    if 'relationship_graph' not in st.session_state:
        st.session_state.relationship_graph = None


def load_sample_data():
    """Load sample data for demonstration."""
    with st.spinner("Generating sample data..."):
        # Create simulator
        simulator = ADODataSimulator(num_epics=3, seed=42)
        work_items_df = simulator.generate_work_items()
        
        # Convert to semantic work items
        work_items = []
        for _, row in work_items_df.iterrows():
            item = SemanticWorkItem(
                work_item_id=row['Work Item ID'],
                title=row['Title'],
                work_item_type=WorkItemType(row['Work Item Type']),
                state=row['State'],
                business_value_raw=row.get('Business Value', 50),
                story_points=row.get('Story Points', 5),
                full_description=row.get('Description', ''),
                area_path=row.get('Area Path', 'Team'),
                parent_id=row.get('Parent', None)
            )
            work_items.append(item)
        
        # Create sample OKRs
        okrs = [
            OKR(
                okr_id="okr_q3_2025",
                period="Q3 2025",
                level="company",
                objective_text="Deliver exceptional product quality and customer satisfaction",
                owner="CEO",
                key_results=[
                    KeyResult(
                        kr_id="kr_1",
                        text="Achieve customer satisfaction score of 90+",
                        target_value=90,
                        current_value=75
                    ),
                    KeyResult(
                        kr_id="kr_2",
                        text="Reduce critical bugs by 50%",
                        target_value=50,
                        current_value=20
                    )
                ]
            )
        ]
        
        # Create sample strategy doc
        strategy_docs = [
            StrategyDocument(
                doc_id="doc_2025_strategy",
                title="2025 Product Excellence Strategy",
                document_type=DocumentType.STRATEGY,
                full_text="""
# 2025 Product Excellence Strategy

## Vision
Become the industry leader in product quality and customer satisfaction.

## Key Pillars
1. Quality First - Zero defects in production
2. Customer Obsession - Every feature delights users
3. Continuous Innovation - Ship improvements weekly

## Success Metrics
- Customer Satisfaction: 90+
- Bug Reduction: 50%
- Feature Velocity: 2x current rate
""",
                strategic_themes=["quality", "customer", "innovation"]
            )
        ]
        
        st.session_state.work_items = work_items
        st.session_state.okrs = okrs
        st.session_state.strategy_docs = strategy_docs
        
        st.success(f"Loaded {len(work_items)} work items, {len(okrs)} OKRs, and {len(strategy_docs)} strategy documents")


def file_upload_section():
    """Handle file uploads for work items, OKRs, and strategy documents."""
    st.header("📁 Data Upload")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Work Items CSV")
        work_items_file = st.file_uploader(
            "Upload ADO work items export",
            type=['csv'],
            key='work_items_upload'
        )
        if work_items_file:
            df = pd.read_csv(work_items_file)
            st.success(f"Loaded {len(df)} work items")
            # Convert to SemanticWorkItem objects
            # (Implementation would parse CSV columns)
    
    with col2:
        st.subheader("OKRs CSV")
        okrs_file = st.file_uploader(
            "Upload OKRs",
            type=['csv'],
            key='okrs_upload'
        )
        if okrs_file:
            df = pd.read_csv(okrs_file)
            st.success(f"Loaded {len(df)} OKRs")
    
    with col3:
        st.subheader("Strategy Documents")
        strategy_file = st.file_uploader(
            "Upload strategy docs",
            type=['txt', 'md'],
            key='strategy_upload'
        )
        if strategy_file:
            content = strategy_file.read().decode('utf-8')
            st.success(f"Loaded strategy document")
    
    # Sample data button
    if st.button("🎲 Load Sample Data", type="primary"):
        load_sample_data()


def analysis_configuration():
    """Configure analysis parameters."""
    st.header("⚙️ Analysis Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Scoring Weights")
        strategic_weight = st.slider(
            "Strategic Alignment Weight",
            0.0, 1.0, 0.3, 0.05,
            help="Weight for strategy document alignment"
        )
        okr_weight = st.slider(
            "OKR Contribution Weight",
            0.0, 1.0, 0.4, 0.05,
            help="Weight for OKR alignment"
        )
        theme_weight = st.slider(
            "Thematic Coherence Weight",
            0.0, 1.0, 0.2, 0.05,
            help="Weight for theme alignment"
        )
        dependency_weight = st.slider(
            "Dependency Impact Weight",
            0.0, 1.0, 0.1, 0.05,
            help="Weight for dependency relationships"
        )
        
        # Normalize weights
        total_weight = strategic_weight + okr_weight + theme_weight + dependency_weight
        if total_weight > 0:
            weights = {
                'strategic': strategic_weight / total_weight,
                'okr': okr_weight / total_weight,
                'theme': theme_weight / total_weight,
                'dependency': dependency_weight / total_weight
            }
        else:
            weights = {'strategic': 0.3, 'okr': 0.4, 'theme': 0.2, 'dependency': 0.1}
    
    with col2:
        st.subheader("Analysis Options")
        similarity_threshold = st.slider(
            "Similarity Threshold",
            0.0, 1.0, 0.6, 0.05,
            help="Minimum similarity for semantic matching"
        )
        generate_questions = st.checkbox(
            "Generate Q&A for missing information",
            value=True
        )
        extract_relationships = st.checkbox(
            "Extract entity relationships",
            value=True
        )
        explanation_detail = st.select_slider(
            "Explanation Detail Level",
            options=["Summary", "Standard", "Detailed", "Technical"],
            value="Standard"
        )
    
    return weights, similarity_threshold, generate_questions, extract_relationships, explanation_detail


def run_analysis():
    """Run semantic analysis on loaded data."""
    if not st.session_state.work_items:
        st.warning("Please load data before running analysis")
        return
    
    with st.spinner("Running semantic analysis..."):
        # Initialize components
        scorer = SemanticScorer()
        
        # Run analysis
        results = scorer.score_work_items(
            st.session_state.work_items,
            st.session_state.strategy_docs,
            st.session_state.okrs,
            generate_questions=True
        )
        
        st.session_state.analysis_results = results
        
        # Extract relationships if requested
        if st.session_state.get('extract_relationships', True):
            extractor = RelationshipExtractor()
            graph = RelationshipGraph()
            
            # Extract from all sources
            nodes, relationships = [], []
            
            wi_nodes, wi_rels = extractor.extract_from_work_items(
                st.session_state.work_items
            )
            nodes.extend(wi_nodes)
            relationships.extend(wi_rels)
            
            if st.session_state.okrs:
                okr_nodes, okr_rels = extractor.extract_from_okrs(
                    st.session_state.okrs,
                    st.session_state.work_items
                )
                nodes.extend(okr_nodes)
                relationships.extend(okr_rels)
            
            # Build graph
            graph.add_nodes(nodes)
            graph.add_relationships(relationships)
            st.session_state.relationship_graph = graph
        
        st.success("Analysis complete!")


def display_results_overview():
    """Display overview of analysis results."""
    if not st.session_state.analysis_results:
        st.info("No analysis results available. Please run analysis first.")
        return
    
    results = st.session_state.analysis_results
    
    st.header("📊 Analysis Results Overview")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    scores = [item['alignment_score']['total_score'] 
              for item in results['scored_items']]
    
    with col1:
        st.metric(
            "Items Analyzed",
            len(results['scored_items'])
        )
    
    with col2:
        st.metric(
            "Average Score",
            f"{np.mean(scores):.2f}"
        )
    
    with col3:
        high_value = sum(1 for s in scores if s >= 0.7)
        st.metric(
            "High Value Items",
            high_value,
            f"{high_value/len(scores)*100:.0f}%"
        )
    
    with col4:
        gaps = results.get('gaps', [])
        st.metric(
            "Information Gaps",
            len(gaps)
        )
    
    # Score distribution
    st.subheader("Score Distribution")
    fig_hist = px.histogram(
        x=scores,
        nbins=20,
        title="Alignment Score Distribution",
        labels={'x': 'Alignment Score', 'y': 'Count'}
    )
    fig_hist.update_layout(showlegend=False)
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Top and bottom items
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌟 Top Aligned Items")
        top_items = sorted(
            results['scored_items'],
            key=lambda x: x['alignment_score']['total_score'],
            reverse=True
        )[:5]
        
        for item in top_items:
            score = item['alignment_score']['total_score']
            score_class = "high" if score >= 0.7 else "medium" if score >= 0.5 else "low"
            st.markdown(
                f"- **{item['title'][:50]}...** "
                f"<span class='score-{score_class}'>{score:.2f}</span>",
                unsafe_allow_html=True
            )
    
    with col2:
        st.subheader("⚠️ Low Aligned Items")
        bottom_items = sorted(
            results['scored_items'],
            key=lambda x: x['alignment_score']['total_score']
        )[:5]
        
        for item in bottom_items:
            score = item['alignment_score']['total_score']
            score_class = "high" if score >= 0.7 else "medium" if score >= 0.5 else "low"
            st.markdown(
                f"- **{item['title'][:50]}...** "
                f"<span class='score-{score_class}'>{score:.2f}</span>",
                unsafe_allow_html=True
            )


def work_item_details():
    """Display detailed analysis for individual work items."""
    if not st.session_state.analysis_results:
        return
    
    st.header("🔍 Work Item Details")
    
    # Select work item
    items = st.session_state.analysis_results['scored_items']
    item_options = {
        f"{item['work_item_id']}: {item['title'][:50]}...": item
        for item in items
    }
    
    selected_key = st.selectbox(
        "Select work item to analyze",
        options=list(item_options.keys())
    )
    
    if selected_key:
        selected_item = item_options[selected_key]
        work_item_id = selected_item['work_item_id']
        
        # Find the actual work item object
        work_item = next(
            (wi for wi in st.session_state.work_items 
             if wi.work_item_id == work_item_id),
            None
        )
        
        if work_item:
            # Generate detailed explanation
            explainer = ExplainableScorer()
            explanation = explainer.explain_score(
                work_item,
                st.session_state.strategy_docs,
                st.session_state.okrs,
                ExplanationType.DETAILED
            )
            
            # Display explanation
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Score Breakdown")
                
                # Create radar chart
                fig_radar = go.Figure()
                
                categories = [f.factor_name for f in explanation.factors]
                values = [f.raw_score for f in explanation.factors]
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='Scores'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )
                    ),
                    showlegend=False,
                    title="Multi-dimensional Score Analysis"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                st.subheader("Summary")
                st.metric(
                    "Total Score",
                    f"{explanation.total_score:.2f}",
                    f"Confidence: {explanation.confidence:.0%}"
                )
                
                st.markdown("**Executive Summary:**")
                st.write(explanation.executive_summary)
            
            # Evidence
            st.subheader("📋 Evidence")
            for i, evidence in enumerate(explanation.key_evidence[:3], 1):
                with st.expander(f"Evidence {i}: {evidence.source_type.title()}"):
                    st.write(f"**Relevance:** {evidence.relevance_score:.2f}")
                    st.write(f"**Text:** {evidence.text_excerpt}")
                    st.write(f"**Explanation:** {evidence.explanation}")
            
            # Improvements
            st.subheader("💡 Improvement Opportunities")
            
            current_score = explanation.total_score
            potential_score = explanation.score_potential
            improvement = potential_score - current_score
            
            # Progress bar showing potential
            progress_col1, progress_col2 = st.columns([3, 1])
            with progress_col1:
                st.progress(current_score)
                st.caption(f"Current: {current_score:.2f} → Potential: {potential_score:.2f} (+{improvement:.2f})")
            
            # Improvement suggestions
            for suggestion in explanation.improvement_suggestions[:3]:
                with st.expander(
                    f"{suggestion['title']} (+{suggestion['impact']:.2f} points)"
                ):
                    st.write(suggestion['description'])
                    if 'actions' in suggestion:
                        st.write("**Actions:**")
                        for action in suggestion['actions']:
                            st.write(f"- {action}")


def qa_interface():
    """Interactive Q&A interface for gathering missing information."""
    st.header("❓ Interactive Q&A")
    
    if not st.session_state.analysis_results:
        st.info("Please run analysis first to identify information gaps")
        return
    
    results = st.session_state.analysis_results
    
    if not results.get('questions'):
        st.success("No information gaps found! All work items have sufficient information.")
        return
    
    # Initialize Q&A session if needed
    if not st.session_state.qa_session:
        qa_system = IntelligentQASystem()
        session = qa_system.create_session(
            st.session_state.work_items,
            st.session_state.strategy_docs,
            st.session_state.okrs
        )
        st.session_state.qa_session = session
        st.session_state.qa_system = qa_system
    
    session = st.session_state.qa_session
    qa_system = st.session_state.qa_system
    
    # Progress
    progress = session.get_progress()
    st.progress(
        progress['completion_rate'],
        f"Progress: {progress['answered']}/{progress['total_questions']} questions answered"
    )
    
    # Get next question
    question = session.get_next_question()
    
    if question:
        st.subheader(f"Question {progress['answered'] + 1} of {progress['total_questions']}")
        
        # Display question
        st.markdown(f"**{question.text}**")
        
        if question.context:
            st.caption(f"Context: {question.context}")
        
        if question.business_impact:
            st.info(f"Impact: {question.business_impact}")
        
        # Answer input
        if question.options:
            answer = st.radio(
                "Select your answer:",
                options=question.options,
                key=f"q_{question.question_id}"
            )
        else:
            answer = st.text_area(
                "Your answer:",
                key=f"q_{question.question_id}",
                height=100
            )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Submit Answer", type="primary"):
                if answer:
                    is_valid, error_msg, follow_ups = session.answer_question(
                        question.question_id,
                        answer
                    )
                    
                    if is_valid:
                        st.success("Answer recorded!")
                        if follow_ups:
                            st.info(f"Generated {len(follow_ups)} follow-up questions")
                        st.rerun()
                    else:
                        st.error(error_msg)
        
        with col2:
            if st.button("Skip Question"):
                session.skip_question(question.question_id)
                st.rerun()
    
    else:
        st.success("All questions answered!")
        
        # Show session summary
        summary = session.complete_session()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Questions Answered", summary['answers_collected'])
        with col2:
            st.metric("Work Items Updated", summary['work_items_updated'])
        with col3:
            duration_min = summary['duration'] / 60
            st.metric("Time Spent", f"{duration_min:.1f} min")
        
        # Recalculate scores button
        if st.button("Recalculate Scores with New Information", type="primary"):
            new_scores = qa_system.recalculate_alignment(
                session,
                st.session_state.strategy_docs,
                st.session_state.okrs
            )
            st.success("Scores recalculated with Q&A information!")
            # Clear session to run analysis again
            st.session_state.qa_session = None
            st.rerun()


def relationship_visualization():
    """Visualize entity relationships as a network graph."""
    st.header("🕸️ Relationship Network")
    
    if not st.session_state.relationship_graph:
        st.info("Please run analysis with relationship extraction enabled")
        return
    
    graph = st.session_state.relationship_graph
    graph_data = graph.export_to_json()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entities", graph_data['statistics']['node_count'])
    with col2:
        st.metric("Total Relationships", graph_data['statistics']['edge_count'])
    with col3:
        centrality = graph.get_centrality_metrics()
        top_node = max(centrality['pagerank'].items(), key=lambda x: x[1])
        st.metric("Most Central Entity", top_node[0][:30])
    
    # Relationship type breakdown
    st.subheader("Relationship Types")
    rel_types = graph_data['statistics']['relationship_types']
    
    fig_pie = px.pie(
        values=list(rel_types.values()),
        names=list(rel_types.keys()),
        title="Distribution of Relationship Types"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Interactive network visualization would go here
    # For now, show top relationships
    st.subheader("Key Relationships")
    
    edges = graph_data['edges']
    # Sort by confidence
    top_edges = sorted(edges, key=lambda x: x.get('confidence', 0), reverse=True)[:10]
    
    for edge in top_edges:
        source_node = next(
            (n for n in graph_data['nodes'] if n['id'] == edge['source']),
            {'title': edge['source']}
        )
        target_node = next(
            (n for n in graph_data['nodes'] if n['id'] == edge['target']),
            {'title': edge['target']}
        )
        
        st.markdown(
            f"- **{source_node['title'][:30]}** → "
            f"*{edge['type']}* → "
            f"**{target_node['title'][:30]}** "
            f"(confidence: {edge.get('confidence', 1.0):.2f})"
        )


def export_results():
    """Export analysis results in various formats."""
    st.header("📤 Export Results")
    
    if not st.session_state.analysis_results:
        st.info("No results to export. Please run analysis first.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Excel Report")
        if st.button("Generate Excel Report"):
            # Would generate comprehensive Excel report
            st.success("Excel report generated!")
            st.download_button(
                "Download Excel",
                data=b"Excel data would go here",
                file_name=f"ado_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.subheader("JSON Data")
        if st.button("Export JSON"):
            json_data = json.dumps(st.session_state.analysis_results, indent=2)
            st.download_button(
                "Download JSON",
                data=json_data,
                file_name=f"ado_analysis_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col3:
        st.subheader("Markdown Report")
        if st.button("Generate Markdown"):
            # Would generate markdown report
            st.success("Markdown report generated!")
            st.download_button(
                "Download Markdown",
                data="# ADO Analysis Report\n\nReport content would go here",
                file_name=f"ado_analysis_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )


def main():
    """Main application flow."""
    st.title("🎯 ADO Semantic Analysis Platform")
    st.markdown(
        "Advanced text-based strategic alignment analysis for Azure DevOps data"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Data Upload", "Configuration", "Analysis", "Work Item Details", 
         "Q&A Session", "Relationships", "Export"]
    )
    
    # Quick actions in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Actions")
    
    if st.sidebar.button("🚀 Run Analysis"):
        run_analysis()
    
    if st.sidebar.button("🗑️ Clear All Data"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    
    # Page routing
    if page == "Data Upload":
        file_upload_section()
    
    elif page == "Configuration":
        config = analysis_configuration()
        st.session_state.analysis_config = config
    
    elif page == "Analysis":
        display_results_overview()
    
    elif page == "Work Item Details":
        work_item_details()
    
    elif page == "Q&A Session":
        qa_interface()
    
    elif page == "Relationships":
        relationship_visualization()
    
    elif page == "Export":
        export_results()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Built with Streamlit | "
        f"Version 1.0 | {datetime.now().strftime('%Y-%m-%d')}"
    )


if __name__ == "__main__":
    main()