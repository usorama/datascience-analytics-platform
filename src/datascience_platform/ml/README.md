# DataScience Platform ML Module

A comprehensive machine learning insights generation engine that provides automated statistical analysis, pattern detection, AutoML capabilities, and model explanations for any dataset.

## Features

### 🔍 Statistical Analysis (`statistics.py`)
- **Descriptive Statistics**: Comprehensive statistical summaries for all data types
- **Correlation Analysis**: Pearson, Spearman, and Kendall correlation matrices
- **Outlier Detection**: Multiple methods including IQR, Z-score, and Modified Z-score
- **Distribution Analysis**: Normality tests and distribution classification
- **Missing Data Analysis**: Pattern detection and impact assessment

### 🔮 Pattern Detection (`patterns.py`)
- **Clustering**: K-means, DBSCAN, and Hierarchical clustering with optimal cluster detection
- **Anomaly Detection**: Isolation Forest and Local Outlier Factor algorithms
- **Trend Analysis**: Linear trends, moving averages, and volatility analysis
- **Time Series Patterns**: Seasonality detection, change point identification, and decomposition
- **Data Quality Patterns**: Duplicate detection, constant columns, and cardinality analysis

### 🤖 AutoML Engine (`automl.py`)
- **AutoGluon Integration**: State-of-the-art automated machine learning
- **Sklearn Fallback**: Robust fallback when AutoGluon is not available
- **Task Auto-Detection**: Automatic classification vs regression detection
- **Feature Importance**: Multiple methods for understanding feature contributions
- **Model Performance**: Comprehensive evaluation metrics

### 💡 Insight Generation (`insights.py`)
- **Comprehensive Analysis**: Combines all analyses into actionable insights
- **Priority Ranking**: Insights ranked by importance and business impact
- **Natural Language**: Human-readable explanations and recommendations
- **Business Context**: Domain-specific insights based on business context
- **Report Generation**: Markdown reports for easy sharing

### 🔬 Model Explanation (`explainer.py`)
- **SHAP Integration**: Advanced model explainability with SHAP values
- **Multiple Explainers**: Tree, Linear, and Kernel explainers
- **Global Explanations**: Overall model behavior and feature importance
- **Local Explanations**: Individual prediction explanations
- **Visualization**: Feature importance plots and explanation visualizations

## Installation

### Basic Installation
```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn
```

### Full Installation (Recommended)
```bash
pip install -r requirements_ml.txt
```

### Optional Dependencies
```bash
# For advanced AutoML capabilities
pip install autogluon.tabular

# For model explanations
pip install shap

# For enhanced ML algorithms
pip install xgboost lightgbm
```

## Quick Start

### Basic Usage
```python
from datascience_platform.ml import InsightGenerator
import pandas as pd

# Load your data
df = pd.read_csv('your_data.csv')

# Generate comprehensive insights
insight_generator = InsightGenerator()
results = insight_generator.generate_comprehensive_insights(
    df=df,
    target_column='your_target_column',  # Optional
    time_column='your_time_column',      # Optional
    business_context='your_domain'       # Optional
)

# Access key insights
print("Key Insights:")
for insight in results['key_insights']:
    print(f"- {insight['title']}: {insight['description']}")

# Export detailed report
report = insight_generator.export_insights_report(results)
with open('insights_report.md', 'w') as f:
    f.write(report)
```

### Individual Module Usage

#### Statistical Analysis
```python
from datascience_platform.ml import StatisticsEngine

stats_engine = StatisticsEngine()
results = stats_engine.analyze_dataset(df)

# Access specific results
correlations = results['correlations']['strong_correlations']
outliers = results['outliers']
distributions = results['distributions']
```

#### Pattern Detection
```python
from datascience_platform.ml import PatternDetector

pattern_detector = PatternDetector()
results = pattern_detector.detect_patterns(
    df, 
    time_column='date_column',
    target_column='target_column'
)

# Access clustering results
clusters = results['clustering']['kmeans']
anomalies = results['anomalies']['isolation_forest']
```

#### AutoML Training
```python
from datascience_platform.ml import AutoMLEngine

automl = AutoMLEngine()
results = automl.train_model(
    df=df,
    target_column='target',
    task_type='classification',  # or 'regression'
    time_limit=300
)

# Make predictions
predictions = automl.predict(new_data)
```

#### Model Explanation
```python
from datascience_platform.ml import ModelExplainer

explainer = ModelExplainer()
explanations = explainer.explain_model(
    model=trained_model,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test
)

# Explain single prediction
explanation = explainer.explain_prediction(single_instance)
```

## Advanced Usage

### Custom Analysis Pipeline
```python
from datascience_platform.ml import *
import pandas as pd

def custom_analysis_pipeline(df, target_col=None):
    \"\"\"Custom analysis pipeline combining multiple engines.\"\"\"
    
    # Step 1: Statistical Analysis
    stats_engine = StatisticsEngine()
    stats_results = stats_engine.analyze_dataset(df)
    
    # Step 2: Pattern Detection
    pattern_detector = PatternDetector()
    pattern_results = pattern_detector.detect_patterns(df, target_column=target_col)
    
    # Step 3: AutoML (if target provided)
    ml_results = None
    if target_col:
        automl = AutoMLEngine()
        ml_results = automl.train_model(df, target_col, time_limit=120)
    
    # Step 4: Generate Insights
    insight_generator = InsightGenerator()
    insights = insight_generator.generate_comprehensive_insights(
        df, target_col, business_context='custom_analysis'
    )
    
    return {
        'statistics': stats_results,
        'patterns': pattern_results,
        'ml_model': ml_results,
        'insights': insights
    }

# Run custom pipeline
results = custom_analysis_pipeline(df, 'target_column')
```

### Batch Processing
```python
def analyze_multiple_datasets(datasets, target_columns):
    \"\"\"Analyze multiple datasets in batch.\"\"\"
    
    all_results = {}
    insight_generator = InsightGenerator()
    
    for name, (df, target_col) in zip(datasets.keys(), datasets.values()):
        print(f"Analyzing dataset: {name}")
        
        try:
            results = insight_generator.generate_comprehensive_insights(
                df=df,
                target_column=target_col,
                business_context=name
            )
            all_results[name] = results
            
        except Exception as e:
            print(f"Error analyzing {name}: {str(e)}")
            all_results[name] = {'error': str(e)}
    
    return all_results
```

## Configuration

### Logging Configuration
```python
import logging

# Configure logging for ML modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific log levels
logging.getLogger('datascience_platform.ml').setLevel(logging.DEBUG)
```

### Performance Tuning
```python
# For large datasets, consider these settings:

# 1. Limit sample sizes for expensive operations
pattern_detector = PatternDetector()
# Clustering automatically samples large datasets

# 2. Reduce AutoML time limits for faster results
automl = AutoMLEngine()
results = automl.train_model(df, target_col, time_limit=60)  # 1 minute

# 3. Use subset of data for SHAP explanations
explainer = ModelExplainer()
# SHAP automatically samples large datasets
```

## Output Formats

### Insight Structure
```python
{
    'type': 'statistical|pattern|ml|time_series|cross_analysis',
    'category': 'correlation|clustering|outliers|trends|etc',
    'title': 'Human-readable title',
    'description': 'Detailed description',
    'impact': 'high|medium|low',
    'priority_score': 1-10,
    'columns_affected': ['col1', 'col2'],
    'recommendations': ['action1', 'action2']
}
```

### Report Export
The system can export comprehensive reports in multiple formats:
- **Markdown**: Human-readable reports with sections and formatting
- **JSON**: Structured data for programmatic access
- **HTML**: Web-ready reports with visualizations

## Error Handling

The ML modules include comprehensive error handling:

```python
try:
    results = insight_generator.generate_comprehensive_insights(df)
except ValueError as e:
    print(f"Data validation error: {e}")
except ImportError as e:
    print(f"Missing dependency: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

- **Memory**: Large datasets are automatically sampled for expensive operations
- **Time**: Most operations complete within seconds; AutoML can be time-limited
- **CPU**: Parallel processing used where possible (clustering, model training)
- **Storage**: Temporary model files are automatically cleaned up

## Extensibility

### Custom Statistics
```python
class CustomStatisticsEngine(StatisticsEngine):
    def custom_analysis(self, df):
        # Add custom statistical methods
        pass
```

### Custom Patterns
```python
class CustomPatternDetector(PatternDetector):
    def detect_custom_patterns(self, df):
        # Add domain-specific pattern detection
        pass
```

## Integration Examples

### Jupyter Notebook Integration
```python
# Display insights in notebook
from IPython.display import Markdown, display

results = insight_generator.generate_comprehensive_insights(df)
report = insight_generator.export_insights_report(results)
display(Markdown(report))
```

### Web Application Integration
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_data():
    # Get data from request
    df = pd.read_json(request.json['data'])
    
    # Generate insights
    insight_generator = InsightGenerator()
    results = insight_generator.generate_comprehensive_insights(df)
    
    return jsonify(results)
```

### Automated Pipeline Integration
```python
import schedule
import time

def automated_analysis():
    # Load latest data
    df = pd.read_sql('SELECT * FROM latest_data', connection)
    
    # Generate insights
    results = insight_generator.generate_comprehensive_insights(df)
    
    # Send report
    send_report_email(results)

# Schedule daily analysis
schedule.every().day.at("09:00").do(automated_analysis)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## Troubleshooting

### Common Issues

1. **ImportError for AutoGluon/SHAP**: These are optional dependencies
   ```python
   # Install optional dependencies
   pip install autogluon.tabular shap
   ```

2. **Memory errors with large datasets**: The system automatically samples large datasets
   ```python
   # For very large datasets, pre-sample before analysis
   df_sample = df.sample(n=10000)
   ```

3. **Long analysis times**: Reduce time limits and sample sizes
   ```python
   automl = AutoMLEngine()
   results = automl.train_model(df, target_col, time_limit=30)
   ```

## API Reference

### StatisticsEngine
- `analyze_dataset(df)`: Complete statistical analysis
- `get_summary_insights()`: Human-readable insights

### PatternDetector
- `detect_patterns(df, time_column, target_column)`: Full pattern analysis
- `get_pattern_insights()`: Pattern-based insights

### AutoMLEngine
- `train_model(df, target_column, ...)`: Train ML model
- `predict(df)`: Make predictions
- `get_model_insights()`: Model-specific insights

### InsightGenerator
- `generate_comprehensive_insights(df, ...)`: Complete analysis
- `export_insights_report(results, format)`: Export reports

### ModelExplainer
- `explain_model(model, X_train, y_train, ...)`: Full model explanation
- `explain_prediction(instance)`: Single prediction explanation
- `get_explanation_summary()`: Summary insights

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This module is part of the DataScience Platform and follows the same licensing terms.