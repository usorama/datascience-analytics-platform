# CLAUDE.md - ADO Analytics Module

## Module Overview

The **ADO Analytics Module** (`datascience_platform.ado`) provides specialized functionality for analyzing Azure DevOps work items using advanced analytics, machine learning, and strategic alignment frameworks. This module implements the **Quantified Value Framework (QVF)** with **Analytic Hierarchy Process (AHP)** for objective prioritization and comprehensive Agile metrics.

### Core Purpose
- Transform raw ADO data into actionable insights for Agile planning
- Provide semantic analysis and strategic alignment scoring
- Generate comprehensive metrics for PI planning and team performance
- Enable data-driven decision making for project prioritization

## Key Components

### Core Analytics (`analyzer.py`)
```python
from datascience_platform.ado import ADOAnalyzer

analyzer = ADOAnalyzer()
results = analyzer.analyze_dataset("ado_data.csv")
```

**Responsibilities:**
- Main orchestration of ADO analysis workflows
- Integration with AHP prioritization engine
- Comprehensive metrics calculation and reporting
- Dashboard generation coordination

### Data Models (`models.py`)
**Pydantic Models:**
- `ADOWorkItem` - Base work item with validation
- `Epic`, `PIO`, `Feature`, `UserStory` - Hierarchical types
- `WorkItemHierarchy` - Parent-child relationships
- `WorkItemState`, `WorkItemType` - Enums for type safety

**Key Features:**
- Automatic business value normalization
- Hierarchical relationship validation
- Type-safe data structures with Pydantic

### Semantic Analysis (`semantic/`)
**Components:**
- `embedder.py` - Production semantic embeddings with GPU acceleration
- `alignment.py` - Strategic alignment scoring with evidence tracking
- `explainability.py` - Transparent scoring methodology
- `qa_system.py` - Natural language Q&A over ADO data
- `relationship_extractor.py` - Entity relationship detection

**Integration with NLP Core:**
```python
from datascience_platform.ado.semantic import SemanticAlignmentScorer
scorer = SemanticAlignmentScorer()
alignment = scorer.score_alignment(work_items, strategic_objectives)
```

### Data Validation (`data_validator.py`)
**Processors:**
- `RobustDataProcessor` - Handles missing data and type inference
- `FilterableDataProcessor` - Advanced filtering and quality checks
- `DataTypeInferencer` - Intelligent type detection and conversion

**Error Handling:**
- `DataValidationError` - Custom exception hierarchy
- Comprehensive validation reporting
- Graceful degradation for data quality issues

### Additional Components

#### AHP Engine (`ahp.py`)
- `AHPEngine` - Analytic Hierarchy Process implementation
- `AHPConfiguration` - Configurable criteria and weights
- `PairwiseComparison` - Decision matrix calculations

#### Metrics Calculator (`metrics.py`)
- `AgileMetricsCalculator` - 20+ Agile metrics
- `PIMetrics` - Program Increment specific calculations
- `TeamMetrics` - Team performance indicators
- `FlowMetrics` - Lean flow analysis

#### Data Simulation (`simulation.py`)
- `ADODataSimulator` - Generate realistic test data
- Configurable work item hierarchies
- Business value distribution modeling

## Platform Integration

### With NLP Core
```python
# Automatic fallback to enhanced NLP when available
from datascience_platform.nlp.core.embedder import SemanticEmbedder
embedder = SemanticEmbedder()  # GPU acceleration (MPS/CUDA/CPU)
```

### With Dashboard Generator
```python
# Automatic dashboard generation
results = analyzer.analyze_dataset(data)
dashboard_path = analyzer.generate_dashboard(results)
```

### With Orchestrator Pipeline
```python
from datascience_platform.orchestrator.pipeline import AnalyticsPipeline
pipeline = AnalyticsPipeline(config)
pipeline.add_analyzer("ado", ADOAnalyzer())
```

## Important Patterns & Conventions

### 1. Hierarchical Data Handling
```python
# Work items follow strict hierarchy: Epic > PIO > Feature > User Story
hierarchy = WorkItemHierarchy.from_dataframe(df)
epic = hierarchy.get_epic_by_id("EPIC-123")
features = hierarchy.get_children(epic, WorkItemType.FEATURE)
```

### 2. Business Value Normalization
```python
# Automatic normalization across work item types
work_item = ADOWorkItem(
    business_value=850,  # Raw value
    work_item_type=WorkItemType.FEATURE
)
# work_item.business_value_normalized auto-calculated (0.0-1.0)
```

### 3. Semantic Scoring Framework
```python
# Multi-dimensional alignment scoring
alignment_score = scorer.calculate_alignment_score(
    work_item_text="User authentication system",
    strategic_objectives=["Improve security", "Enhance user experience"],
    dimensions=["relevance", "impact", "feasibility"]
)
```

### 4. AHP Decision Making
```python
# Configurable criteria for prioritization
ahp_config = AHPConfiguration(criteria=[
    AHPCriterion(name="business_value", weight=0.4),
    AHPCriterion(name="technical_risk", weight=0.3),
    AHPCriterion(name="strategic_alignment", weight=0.3)
])
```

## Testing Requirements

### Unit Testing
```bash
# Component-specific tests
python3 -m pytest tests/unit/ado/ -v
python3 test_ado_quick.py  # Quick validation

# Semantic analysis tests
python3 -m pytest tests/unit/ado/semantic/ -v
```

### Integration Testing
```bash
# Full ADO analysis pipeline
python3 demo_ado_analysis.py
python3 demo_semantic_ado.py

# Data validation testing
python3 -m pytest tests/integration/ado/test_data_validation.py -v
```

### Performance Testing
- **Batch Processing**: Test with 1000+ work items
- **Memory Usage**: Monitor during large dataset processing
- **GPU Acceleration**: Validate MPS/CUDA performance gains
- **Cache Efficiency**: Measure semantic embedding cache hit rates

## Performance Considerations

### Memory Optimization
```python
# Use batch processing for large datasets
analyzer = ADOAnalyzer()
for batch in analyzer.process_in_batches(large_dataset, batch_size=100):
    results = analyzer.analyze_batch(batch)
```

### GPU Acceleration
- **MPS Support**: Automatic Apple Silicon GPU detection
- **CUDA Support**: NVIDIA GPU acceleration when available
- **Fallback**: CPU processing with optimized numpy operations

### Caching Strategy
- **Semantic Embeddings**: TTL-based cache with LRU eviction
- **AHP Calculations**: Cache decision matrices
- **Metrics**: Cache expensive statistical calculations

## Example Usage Patterns

### Basic ADO Analysis
```python
from datascience_platform.ado import ADOAnalyzer

# Initialize with default AHP configuration
analyzer = ADOAnalyzer()

# Load and analyze ADO data
results = analyzer.analyze_dataset("sprint_data.csv")
print(f"Prioritized backlog: {results['prioritized_items']}")
print(f"PI metrics: {results['pi_metrics']}")
```

### Advanced Semantic Analysis
```python
from datascience_platform.ado.semantic import SemanticAlignmentScorer

scorer = SemanticAlignmentScorer()
alignment_results = scorer.analyze_portfolio_alignment(
    work_items=work_items,
    strategic_objectives=objectives,
    include_evidence=True,
    explain_scoring=True
)
```

### Custom AHP Configuration
```python
from datascience_platform.ado import AHPConfiguration, AHPCriterion

# Define custom prioritization criteria
custom_config = AHPConfiguration(
    criteria=[
        AHPCriterion(name="roi_score", weight=0.5, higher_is_better=True),
        AHPCriterion(name="complexity", weight=0.3, higher_is_better=False),
        AHPCriterion(name="alignment", weight=0.2, higher_is_better=True)
    ],
    consistency_threshold=0.1
)

analyzer = ADOAnalyzer(ahp_config=custom_config)
```

### Data Validation and Cleanup
```python
from datascience_platform.ado import RobustDataProcessor

processor = RobustDataProcessor()
cleaned_data = processor.process_dataframe(
    raw_ado_data,
    handle_missing="interpolate",
    validate_hierarchy=True,
    infer_types=True
)
```

## Error Handling & Diagnostics

### Common Issues
- **Invalid Hierarchy**: Parent-child relationship violations
- **Missing Required Fields**: Title, work item type, state
- **Data Type Mismatches**: Business value, effort estimation
- **Semantic Model Loading**: GPU/model availability issues

### Debugging Support
```python
import logging
logging.getLogger('datascience_platform.ado').setLevel(logging.DEBUG)

# Enable detailed AHP logging
logging.getLogger('datascience_platform.ado.ahp').setLevel(logging.DEBUG)
```

## Links to Documentation

- **Main Platform Documentation**: `/IMPLEMENTATION_SUMMARY.md`
- **NLP Integration**: `/src/datascience_platform/nlp/CLAUDE.md`
- **Dashboard Generation**: `/src/datascience_platform/dashboard/CLAUDE.md`
- **Testing Guide**: `/docs/testing.md`
- **Performance Optimization**: `/docs/performance.md`

## Module Structure Summary
```
src/datascience_platform/ado/
├── __init__.py              # Public API exports
├── analyzer.py              # Main analysis orchestrator
├── models.py                # Pydantic data models
├── ahp.py                   # Analytic Hierarchy Process
├── metrics.py               # Agile metrics calculations
├── simulation.py            # Test data generation
├── data_validator.py        # Robust data processing
└── semantic/                # Semantic analysis subsystem
    ├── __init__.py
    ├── embedder.py          # Production semantic embeddings
    ├── alignment.py         # Strategic alignment scoring
    ├── explainability.py    # Transparent methodology
    ├── qa_system.py         # Natural language Q&A
    └── relationship_extractor.py  # Entity relationships
```

---

**Version**: 2.0.0 | **Last Updated**: January 2025