# CLAUDE.md - ML Module Development Guide

This file provides guidance to Claude Code (claude.ai/code) when working with the ML module of the DataScience Platform.

## Module Overview

The ML module (`src/datascience_platform/ml/`) provides comprehensive AutoML and statistical analysis capabilities with production-ready implementations. It's designed for both interactive analysis and automated pipeline integration.

## Key Components

### Core Engines

#### `automl.py` - ML Pipeline Builder & AutoML Engine
```python
from datascience_platform.ml import AutoMLEngine

# Primary class for automated machine learning
automl = AutoMLEngine()
results = automl.train_model(df, 'target_column', time_limit=300)
```

**Key Features:**
- **AutoGluon Integration**: Primary ML framework with sklearn fallback
- **Task Auto-Detection**: Automatically determines regression vs classification
- **Graceful Degradation**: Falls back to sklearn if AutoGluon unavailable
- **Model Management**: Automatic saving/loading and cleanup of temporary files

**Production Considerations:**
- Uses temporary directories that auto-cleanup on destruction
- Handles memory constraints with configurable batch processing  
- Thread-safe for concurrent usage
- Automatic model serialization for deployment

#### `statistics.py` - Statistical Analysis Engine
```python
from datascience_platform.ml import StatisticsEngine

stats_engine = StatisticsEngine()
results = stats_engine.analyze_dataset(df)
```

**Capabilities:**
- **Comprehensive Descriptive Statistics**: All standard statistical measures
- **Multi-Method Correlation Analysis**: Pearson, Spearman, Kendall
- **Advanced Outlier Detection**: IQR, Z-score, Modified Z-score methods
- **Distribution Analysis**: Normality tests, skewness, kurtosis classification
- **Missing Data Pattern Analysis**: Pattern detection and impact assessment

#### `patterns.py` - Pattern Detection Engine
```python
from datascience_platform.ml import PatternDetector

pattern_detector = PatternDetector()
results = pattern_detector.detect_patterns(df, time_column='date', target_column='target')
```

**Pattern Detection Methods:**
- **Clustering**: K-means (with optimal k detection), DBSCAN, Hierarchical
- **Anomaly Detection**: Isolation Forest, Local Outlier Factor
- **Time Series Analysis**: Seasonality detection, change points, trend analysis
- **Data Quality Assessment**: Duplicates, constant columns, cardinality issues

#### `explainer.py` - Model Interpretability Engine
```python
from datascience_platform.ml import ModelExplainer

explainer = ModelExplainer()
explanations = explainer.explain_model(model, X_train, y_train, X_test)
```

**Explainability Features:**
- **SHAP Integration**: Global and local explanations with fallback methods
- **Multiple Explainer Types**: Tree, Linear, Kernel explainers
- **Visualization Generation**: Base64-encoded plots for web integration
- **Feature Importance**: Multiple methods with consensus ranking

#### `insights.py` - Insight Generation & Orchestration
```python
from datascience_platform.ml import InsightGenerator

insight_generator = InsightGenerator()
results = insight_generator.generate_comprehensive_insights(
    df, target_column='target', business_context='sales'
)
```

**Orchestration Capabilities:**
- **Multi-Engine Coordination**: Combines all analysis engines
- **Priority Ranking**: Insights ranked by business impact and statistical significance
- **Natural Language Generation**: Human-readable insights and recommendations
- **Business Context Integration**: Domain-specific insights based on context
- **Report Export**: Markdown, JSON formats for integration

## AutoGluon Integration Details

### Installation Requirements
```bash
# Core functionality (always works)
pip install pandas numpy scikit-learn scipy

# Enhanced AutoML capabilities
pip install autogluon.tabular

# Model explainability
pip install shap matplotlib seaborn
```

### AutoGluon vs Sklearn Fallback Logic
```python
# The system automatically detects available frameworks
try:
    from autogluon.tabular import TabularPredictor
    AUTOGLUON_AVAILABLE = True
except ImportError:
    AUTOGLUON_AVAILABLE = False
    # Falls back to sklearn RandomForest
```

**Production Deployment Strategy:**
- **Development**: Use full AutoGluon for best performance
- **Production**: Can deploy with sklearn-only for reduced dependencies
- **Hybrid**: AutoGluon for training, sklearn for inference

### Model Lifecycle Management
```python
# Training with cleanup
automl = AutoMLEngine()
try:
    results = automl.train_model(df, 'target')
    # Model automatically saved to temporary directory
    predictions = automl.predict(new_data)
finally:
    automl.cleanup()  # Explicit cleanup if needed
```

## Statistical Analysis Architecture

### Multi-Method Approach
The statistics engine uses multiple methods for robustness:

```python
# Example: Outlier detection uses 3 methods
outlier_results = {
    'iqr': {...},           # Interquartile Range method
    'zscore': {...},        # Z-score method  
    'modified_zscore': {...} # Modified Z-score (median-based)
}
```

### Distribution Analysis Pipeline
```python
# Normality testing cascade
if len(series) <= 5000:
    shapiro_test()          # Best for small samples
if len(series) >= 8:
    dagostino_test()        # D'Agostino's test
kolmogorov_smirnov_test()   # Always performed
```

## Production Usage Patterns

### Memory Management
```python
# Automatic sampling for large datasets
if len(cluster_data) > 10000:
    # System automatically samples for expensive operations
    sample_data = cluster_data.sample(n=5000)
```

### Batch Processing
```python
def process_multiple_datasets(datasets):
    insight_generator = InsightGenerator()
    
    results = {}
    for name, df in datasets.items():
        try:
            results[name] = insight_generator.generate_comprehensive_insights(df)
        except Exception as e:
            logger.error(f"Failed to process {name}: {e}")
            results[name] = {'error': str(e)}
    
    return results
```

### Error Handling Strategy
```python
# Graceful degradation pattern used throughout
try:
    advanced_analysis()
except ImportError:
    logger.warning("Advanced features unavailable, using fallback")
    basic_analysis()
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    return {'error': str(e)}
```

## Integration with Other Modules

### ADO Module Integration
```python
# ML insights can enhance ADO analysis
from datascience_platform.ado import ADOAnalyzer
from datascience_platform.ml import InsightGenerator

# Combine ADO metrics with ML insights
ado_data = ado_analyzer.get_metrics()
ml_insights = insight_generator.generate_comprehensive_insights(
    ado_data, business_context='agile_development'
)
```

### Dashboard Generation Integration
```python
# ML results feed into dashboard generation
ml_results = automl.train_model(df, 'target')
dashboard_data = {
    'ml_performance': ml_results['evaluation'],
    'feature_importance': ml_results['feature_importance'],
    'predictions': predictions
}
```

### ETL Pipeline Integration
```python
# ML analysis as part of ETL pipeline
def etl_with_ml_analysis(raw_data):
    # Extract & Transform
    cleaned_data = etl_pipeline.process(raw_data)
    
    # ML Analysis
    ml_insights = insight_generator.generate_comprehensive_insights(cleaned_data)
    
    # Load with insights
    return {
        'processed_data': cleaned_data,
        'insights': ml_insights,
        'quality_score': ml_insights['data_quality_assessment']['overall_score']
    }
```

## Development Guidelines

### Adding New Statistical Methods
```python
# Extend StatisticsEngine
class EnhancedStatisticsEngine(StatisticsEngine):
    def analyze_dataset(self, df):
        # Call parent method
        results = super().analyze_dataset(df)
        
        # Add custom analysis
        results['custom_analysis'] = self._custom_analysis(df)
        return results
    
    def _custom_analysis(self, df):
        # Implement custom statistical methods
        return custom_results
```

### Adding New Pattern Detection
```python
# Extend PatternDetector
class DomainSpecificPatternDetector(PatternDetector):
    def detect_patterns(self, df, **kwargs):
        results = super().detect_patterns(df, **kwargs)
        
        # Add domain-specific patterns
        results['domain_patterns'] = self._detect_domain_patterns(df)
        return results
```

### Custom Insight Generation
```python
# Extend InsightGenerator for domain-specific insights
class SalesInsightGenerator(InsightGenerator):
    def _generate_business_insights(self, df, statistical_results, pattern_results, business_context):
        insights = super()._generate_business_insights(
            df, statistical_results, pattern_results, business_context
        )
        
        # Add sales-specific insights
        if 'sales' in business_context.lower():
            insights.extend(self._generate_sales_insights(df, statistical_results))
        
        return insights
```

## Performance Optimization

### Computational Efficiency
- **Automatic Sampling**: Large datasets automatically sampled for expensive operations
- **Vectorized Operations**: Numpy/pandas vectorization used throughout
- **Memory Management**: Temporary files and models automatically cleaned up
- **Caching**: Results cached where appropriate to avoid recomputation

### Scalability Considerations
```python
# Configure for large datasets
automl = AutoMLEngine()
results = automl.train_model(
    df, 'target',
    time_limit=60,          # Shorter time for large datasets
    quality_preset='fast'   # Faster preset for initial exploration
)
```

## Testing and Validation

### Unit Testing Pattern
```python
def test_statistics_engine():
    # Test with known dataset
    df = create_test_dataset()
    
    stats_engine = StatisticsEngine()
    results = stats_engine.analyze_dataset(df)
    
    # Validate expected structure
    assert 'correlations' in results
    assert 'outliers' in results
    assert 'distributions' in results
```

### Integration Testing
```python
def test_full_pipeline():
    # Test complete insight generation pipeline
    df = load_test_data()
    
    insight_generator = InsightGenerator()
    results = insight_generator.generate_comprehensive_insights(df)
    
    # Validate complete output structure
    assert 'key_insights' in results
    assert 'actionable_recommendations' in results
    assert 'data_quality_assessment' in results
```

## Common Development Tasks

### Adding a New ML Algorithm
1. Update `automl.py` to include new algorithm in sklearn fallback
2. Add algorithm-specific parameters to configuration
3. Update feature importance extraction for new algorithm type
4. Add appropriate tests and documentation

### Enhancing Explainability
1. Add new explainer type in `explainer.py`
2. Implement model-specific explanation logic
3. Add visualization generation if needed
4. Update explanation summary generation

### Adding Business Context
1. Update `insights.py` business context detection
2. Add domain-specific insight generation methods
3. Include relevant recommendations for the domain
4. Add contextual interpretation of statistical results

## Dependencies and Compatibility

### Required Dependencies
```python
# Core dependencies (always required)
import pandas as pd
import numpy as np
import scipy
from sklearn import *

# Optional but recommended
import matplotlib.pyplot as plt
import seaborn as sns
```

### Optional Dependencies
```python
# AutoML capabilities
try:
    from autogluon.tabular import TabularPredictor
except ImportError:
    # Graceful fallback to sklearn

# Model explanations  
try:
    import shap
except ImportError:
    # Use permutation importance fallback
```

## Configuration and Customization

### Logging Configuration
```python
import logging
logger = logging.getLogger(__name__)

# All modules use consistent logging
logger.info("Starting analysis...")
logger.warning("Fallback method used")
logger.error("Analysis failed")
```

### Performance Tuning
```python
# Configurable parameters throughout
CLUSTERING_SAMPLE_SIZE = 5000
AUTOML_TIME_LIMIT = 300
SHAP_SAMPLE_SIZE = 500
OUTLIER_THRESHOLD = 0.1
```

## Output Formats and Schemas

### Standard Result Structure
```python
{
    'overview': {...},           # Dataset overview
    'statistics': {...},         # Statistical analysis results  
    'patterns': {...},          # Pattern detection results
    'ml_results': {...},        # ML model results
    'insights': [...],          # Ranked insights
    'recommendations': [...],   # Actionable recommendations
    'metadata': {...}           # Analysis metadata
}
```

### Insight Schema
```python
{
    'type': str,                # analysis|pattern|ml|time_series
    'category': str,            # correlation|clustering|etc
    'title': str,               # Human-readable title
    'description': str,         # Detailed explanation
    'impact': str,              # high|medium|low
    'priority_score': int,      # 1-10 ranking score
    'columns_affected': list,   # Relevant columns
    'metadata': dict            # Additional context
}
```

This documentation provides the essential context Claude Code needs to effectively work with the ML module, focusing on development patterns, integration points, and production considerations rather than duplicating user-facing documentation.