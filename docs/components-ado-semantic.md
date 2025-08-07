# ADO Semantic Analysis Platform

## Overview

The ADO Semantic Analysis Platform is a comprehensive Python-based system that transforms subjective business value assessments into objective, explainable strategic alignment scores. It analyzes text content from Azure DevOps (ADO) work items, OKRs, and strategy documents to quantify strategic alignment using advanced NLP techniques.

## Key Features

### 1. **Semantic Text Analysis**
- Analyzes descriptions, acceptance criteria, and business justifications
- Extracts strategic themes and relationships from text
- Uses transformer-based embeddings for semantic similarity

### 2. **Strategic Alignment Scoring**
- Multi-dimensional scoring across 4 key factors:
  - Strategic document alignment (30%)
  - OKR contribution (40%)
  - Thematic coherence (20%)
  - Dependency impact (10%)
- Fully configurable weights

### 3. **Explainable AI**
- Detailed explanations for every score
- Evidence-based reasoning with source citations
- Improvement recommendations with quantified impact
- Multiple explanation formats (executive, technical, visual)

### 4. **Intelligent Q&A System**
- Identifies missing information automatically
- Generates contextual questions
- Updates scores based on answers
- Learns from patterns over time

### 5. **Relationship Extraction**
- Builds knowledge graphs from work items, OKRs, and strategies
- Identifies dependencies and hierarchies
- Discovers semantic relationships
- Enables impact analysis

### 6. **Interactive Dashboards**
- Streamlit web interface for easy interaction
- Visual analytics and charts
- Export capabilities (Excel, JSON, Markdown)
- Real-time analysis updates

## Architecture

```
datascience_platform/
├── ado/
│   ├── models.py           # Core ADO data models
│   ├── analyzer.py         # ADO analysis engine
│   ├── ahp.py             # AHP prioritization
│   ├── metrics.py         # Agile metrics calculations
│   ├── simulator.py       # Test data generation
│   └── semantic/          # Semantic analysis module
│       ├── models.py      # Semantic data models
│       ├── text_processor.py    # NLP text processing
│       ├── embedder.py         # Semantic embeddings
│       ├── alignment.py        # Strategic alignment calculator
│       ├── qa_system.py        # Interactive Q&A
│       ├── relationship_extractor.py  # Graph building
│       └── explainability.py   # Explainable scoring
```

## Installation

```bash
# Install base requirements
pip install -r requirements.txt

# Install ADO-specific requirements
pip install -r requirements-ado.txt
```

### Key Dependencies
- pandas, polars - Data processing
- numpy, scipy - Mathematical operations
- scikit-learn - Machine learning
- sentence-transformers - Semantic embeddings (optional)
- networkx - Graph analysis
- streamlit - Web interface
- plotly - Interactive visualizations

## Quick Start

### 1. Run Integrated Demo
```bash
python demo_integrated_semantic_ado.py
```

### 2. Launch Interactive Interface
```bash
streamlit run streamlit_ado_semantic.py
```

### 3. Python API Usage
```python
from datascience_platform.ado.semantic import (
    SemanticScorer, IntelligentQASystem, 
    ExplainableScorer, RelationshipExtractor
)

# Score work items
scorer = SemanticScorer()
results = scorer.score_work_items(work_items, strategy_docs, okrs)

# Get explanations
explainer = ExplainableScorer()
explanation = explainer.explain_score(work_item, strategy_docs, okrs)

# Extract relationships
extractor = RelationshipExtractor()
graph = extractor.extract_from_work_items(work_items)

# Run Q&A session
qa_system = IntelligentQASystem()
session = qa_system.create_session(work_items, strategy_docs, okrs)
```

## Use Cases

### 1. PI Planning
- Objectively prioritize features based on strategic alignment
- Identify work items that don't support current objectives
- Ensure balanced portfolio across strategic pillars

### 2. Quarterly Reviews
- Analyze how well execution aligned with strategy
- Identify gaps between planned and actual work
- Generate insights for next quarter planning

### 3. Continuous Improvement
- Use Q&A system to improve work item descriptions
- Track alignment trends over time
- Identify patterns in high-value work

### 4. Stakeholder Communication
- Generate executive reports with clear explanations
- Create visual dashboards for alignment overview
- Export detailed analysis for deep dives

## Input Data Formats

### Work Items CSV
```csv
Work Item ID,Title,Work Item Type,Description,Business Value,Story Points,Area Path
1001,"Implement AI Chat","Epic","Build AI-powered customer chat...",85,89,"Product Team"
```

### OKRs CSV
```csv
Objective,KR1,KR2,KR3,Owner,Period,Level
"Improve customer satisfaction","NPS 80+","Response time <2s","Retention 95%","CEO","Q3 2025","company"
```

### Strategy Documents
- Plain text (.txt) or Markdown (.md) files
- Should include strategic pillars, goals, and success metrics

## Demos Available

1. **demo_semantic_ado.py** - Basic semantic analysis
2. **demo_intelligent_qa.py** - Q&A system interaction
3. **demo_relationship_extraction.py** - Knowledge graph building
4. **demo_explainable_scoring.py** - Detailed explanations
5. **demo_integrated_semantic_ado.py** - Complete workflow

## Configuration

### Scoring Weights
Adjust in code or via Streamlit interface:
```python
weights = {
    'strategic_alignment': 0.3,
    'okr_contribution': 0.4,
    'thematic_coherence': 0.2,
    'dependency_impact': 0.1
}
```

### Similarity Thresholds
```python
similarity_threshold = 0.6  # Minimum semantic similarity
evidence_threshold = 0.5    # Minimum score for evidence inclusion
```

## Advanced Features

### Custom Embeddings
The system uses sentence-transformers by default but includes a mock embedder for environments where it's not available.

### Caching
Embeddings are cached to improve performance on repeated analyses.

### Export Formats
- Excel reports with multiple sheets
- JSON for programmatic access
- Markdown for documentation
- Cypher queries for Neo4j import

## Best Practices

1. **Rich Descriptions**: Include business context in work item descriptions
2. **Clear OKRs**: Use measurable key results with specific targets
3. **Strategy Documents**: Keep strategy documents current and specific
4. **Regular Q&A**: Use the Q&A system to continuously improve data quality
5. **Review Explanations**: Understand why items score high or low

## Troubleshooting

### Low Alignment Scores
- Check if work items have sufficient text descriptions
- Ensure strategy documents are loaded
- Verify OKRs are properly formatted
- Use Q&A system to add missing context

### Performance Issues
- Enable embedding cache
- Reduce batch size for large datasets
- Use sampling for initial analysis

## Future Enhancements

1. **Real-time ADO Integration**: Direct API connection to Azure DevOps
2. **ML Model Fine-tuning**: Custom embeddings for your domain
3. **Predictive Analytics**: Forecast alignment trends
4. **Multi-language Support**: Analyze content in multiple languages
5. **Team Recommendations**: Suggest optimal team assignments

## Contributing

This is part of the DataScience Analytics Platform. Contributions welcome!

## License

See main project license.

## Support

For issues or questions:
1. Check demo scripts for examples
2. Review inline documentation
3. Examine test cases
4. Open an issue with details

---

Built with Python, NLP, and a focus on making strategic alignment transparent and actionable.