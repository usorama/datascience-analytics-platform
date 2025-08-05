# DataScience Analytics Platform - Orchestrator & Integration

This document describes the main orchestrator and integration layer that connects all components of the DataScience Analytics Platform.

## 🏗️ Architecture Overview

The orchestrator provides a unified interface that coordinates:
- **ETL Components**: Data reading, validation, and transformation
- **ML Components**: Statistical analysis, pattern detection, and insights generation
- **Dashboard Components**: Interactive visualization and reporting
- **API Layer**: REST endpoints for programmatic access
- **CLI Interface**: Command-line tools for batch processing

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Example Pipeline

```bash
# Run the comprehensive example
python example_pipeline.py

# Or analyze your own data
python -m datascience_platform analyze your_data.csv --target revenue --time-col date
```

### 3. Start API Server

```bash
# Start the REST API server
python -m datascience_platform server --host 0.0.0.0 --port 8080

# Access API documentation at: http://localhost:8080/docs
```

## 📊 Core Components

### Analytics Pipeline Orchestrator (`orchestrator/pipeline.py`)

The main `AnalyticsPipeline` class coordinates the entire workflow:

```python
from datascience_platform.orchestrator.pipeline import AnalyticsPipeline, PipelineConfig

# Create configuration
config = PipelineConfig(
    data_source="sales_data.csv",
    target_column="revenue",
    time_column="date",
    business_context="sales",
    output_dir=Path("./results")
)

# Create and execute pipeline
pipeline = AnalyticsPipeline(config)
results = pipeline.execute()
```

**Pipeline Stages:**
1. **Initialization** - Setup and configuration
2. **Data Loading** - Read and parse data files
3. **Data Validation** - Quality checks and schema validation
4. **Data Processing** - Cleaning and preparation
5. **Analysis** - Statistical analysis and ML insights
6. **Dashboard Generation** - Interactive visualizations
7. **Finalization** - Results compilation and export

### API Endpoints (`api/analytics.py`)

RESTful API for programmatic access:

```python
# Start analysis
POST /analyze
{
    "data_source": "data.csv",
    "target_column": "revenue",
    "business_context": "sales"
}

# Check status
GET /analyze/{pipeline_id}/status

# Get results
GET /analyze/{pipeline_id}/results

# Download dashboard
GET /analyze/{pipeline_id}/dashboard
```

### Data Models (`models/analytics.py`)

Pydantic models for API requests/responses:

- `AnalysisRequest` - Pipeline configuration
- `AnalysisResponse` - Pipeline creation response
- `PipelineStatusResponse` - Progress tracking
- `FileUploadResponse` - File upload confirmation

### CLI Interface (`__main__.py`)

Comprehensive command-line interface:

```bash
# Main analysis command
datascience-platform analyze data.csv --target sales --context marketing

# Start API server
datascience-platform server --port 8080

# Export results
datascience-platform export results.json --format xlsx

# Data operations
datascience-platform data read data.csv --head 20
datascience-platform data validate data.csv --schema sales_schema
```

## 🔧 Configuration Options

### Pipeline Configuration

```python
config = PipelineConfig(
    # Data source
    data_source="path/to/data.csv",
    data_format="csv",  # auto-detected if None
    read_options={"encoding": "utf-8", "delimiter": ","},
    
    # Analysis configuration
    target_column="revenue",
    time_column="date",
    business_context="sales and marketing",
    
    # Processing options
    validate_data=True,
    strict_validation=False,
    sample_size=10000,  # None for full dataset
    
    # ML configuration
    ml_enabled=True,
    ml_time_limit=120,  # seconds
    
    # Dashboard options
    generate_dashboard=True,
    dashboard_theme="light",  # or "dark"
    dashboard_title="Custom Dashboard Title",
    
    # Output configuration
    output_dir=Path("./output"),
    save_intermediate=True,
    export_formats=["html", "pdf"]
)
```

### Environment Variables

```bash
# Application settings
DSP_DEBUG=true
DSP_LOG_LEVEL=INFO

# API settings
DSP_API_HOST=0.0.0.0
DSP_API_PORT=8080

# Processing settings
DSP_MAX_MEMORY_USAGE_GB=8.0
DSP_DEFAULT_CHUNK_SIZE=50000

# ML settings
DSP_ML_RANDOM_SEED=42
DSP_ML_TEST_SIZE=0.2
```

## 📈 Progress Tracking

The orchestrator provides real-time progress tracking:

```python
def progress_callback(progress_data):
    status = progress_data["status"]
    progress = progress_data["progress"]
    
    current_stage = progress["current_stage"]
    overall_progress = progress["overall_progress"]
    
    print(f"[{overall_progress:.1f}%] {current_stage}: {status}")

pipeline.add_progress_callback(progress_callback)
```

**Progress Information:**
- Current pipeline stage
- Stage-specific progress (0-100%)
- Overall progress percentage
- Elapsed time
- Stage-specific messages
- Error information (if any)

## 🎯 Integration Examples

### 1. Basic Analysis

```python
from datascience_platform.orchestrator.pipeline import AnalyticsPipeline, PipelineConfig

config = PipelineConfig(
    data_source="sales_data.csv",
    target_column="revenue",
    output_dir=Path("./basic_analysis")
)

pipeline = AnalyticsPipeline(config)
results = pipeline.execute()

print(f"Analysis complete! {len(results['analysis_results']['key_insights'])} insights generated")
```

### 2. Time Series Analysis

```python
config = PipelineConfig(
    data_source="time_series_data.csv",
    target_column="sales",
    time_column="date",
    business_context="sales forecasting",
    dashboard_title="Sales Forecasting Dashboard"
)

pipeline = AnalyticsPipeline(config)
results = pipeline.execute()
```

### 3. API Integration

```python
import requests

# Upload file
with open("data.csv", "rb") as f:
    response = requests.post("http://localhost:8080/upload", 
                           files={"file": f})
file_info = response.json()

# Start analysis
analysis_request = {
    "data_source": file_info["file_id"],
    "target_column": "revenue",
    "business_context": "sales"
}

response = requests.post("http://localhost:8080/analyze", 
                        json=analysis_request)
pipeline_info = response.json()
pipeline_id = pipeline_info["pipeline_id"]

# Monitor progress
while True:
    response = requests.get(f"http://localhost:8080/analyze/{pipeline_id}/status")
    status = response.json()
    
    if status["status"] == "completed":
        break
    elif status["status"] == "failed":
        print("Analysis failed!")
        break
    
    print(f"Progress: {status['progress']['overall_progress']:.1f}%")
    time.sleep(5)

# Get results
response = requests.get(f"http://localhost:8080/analyze/{pipeline_id}/results")
results = response.json()
```

## 🔍 Component Integration

The orchestrator seamlessly integrates all platform components:

### Data Flow

```
Data Source → ETL Reader → Data Validator → ML Insights → Dashboard Generator → Results
     ↓            ↓             ↓              ↓              ↓            ↓
  Raw Data → Parsed Data → Validated Data → Analysis → Visualizations → Reports
```

### Component Dependencies

- **ETL Components** (`etl/`)
  - `reader.py` - Multi-format data loading
  - `validator.py` - Data quality checks
  - `transformer.py` - Data preprocessing

- **ML Components** (`ml/`)
  - `insights.py` - Comprehensive analysis engine
  - `statistics.py` - Statistical computations
  - `patterns.py` - Pattern detection
  - `automl.py` - Automated machine learning

- **Dashboard Components** (`dashboard/`)
  - `generator.py` - HTML dashboard creation
  - `charts.py` - Interactive chart generation

## 🚦 Error Handling

The orchestrator provides comprehensive error handling:

```python
try:
    results = pipeline.execute()
except DataSciencePlatformError as e:
    print(f"Platform error: {e}")
    # Handle specific platform errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle general errors
```

**Error Types:**
- `DataReaderError` - Data loading issues
- `ValidationError` - Data quality problems
- `AnalysisError` - ML/statistical analysis failures
- `DashboardError` - Visualization generation issues

## 📊 Output Structure

The orchestrator generates a structured output directory:

```
output/
├── dashboard.html              # Interactive dashboard
├── insights_report.md          # Comprehensive insights report
├── execution_summary.json      # Pipeline execution metadata
├── processed_data.csv          # Cleaned dataset (if save_intermediate=True)
├── validation_report.json      # Data quality assessment
└── pipeline.log               # Execution logs
```

## 🎨 Dashboard Features

Generated dashboards include:

- **KPI Cards** - Key metrics and summary statistics
- **Interactive Charts** - Correlation heatmaps, distributions, time series
- **Data Tables** - Searchable and sortable data views
- **Insights Panel** - Key findings and recommendations
- **Export Options** - PDF export and data downloads
- **Theme Support** - Light and dark themes
- **Responsive Design** - Mobile and desktop compatibility

## 🔄 Extensibility

The orchestrator is designed for easy extension:

### Custom Pipeline Stages

```python
class CustomAnalyticsPipeline(AnalyticsPipeline):
    def _custom_analysis_stage(self):
        """Add custom analysis stage."""
        self.progress.start_stage("custom_analysis", "Running custom analysis")
        
        # Your custom analysis logic here
        custom_results = self._run_custom_analysis()
        
        self.results["custom_analysis"] = custom_results
        self.progress.complete_stage("Custom analysis completed")
    
    def execute(self):
        """Override execute to include custom stage."""
        # Run standard pipeline
        results = super().execute()
        
        # Add custom analysis
        self._custom_analysis_stage()
        
        return self.get_results()
```

### Custom Data Sources

```python
from datascience_platform.etl.reader import DataReader

class CustomDataReader(DataReader):
    def read_custom_format(self, file_path, **kwargs):
        """Add support for custom data format."""
        # Your custom reading logic
        return processed_dataframe
```

### Custom Visualizations

```python
from datascience_platform.dashboard.generator import DashboardGenerator

class CustomDashboardGenerator(DashboardGenerator):
    def add_custom_chart(self, data, chart_id, **kwargs):
        """Add custom chart type."""
        # Your custom chart logic
        chart_config = self._create_custom_chart(data, **kwargs)
        
        self.components['charts'].append({
            'id': chart_id,
            'type': 'custom',
            'config': chart_config
        })
```

## 🧪 Testing

Test the orchestrator components:

```bash
# Run all tests
pytest tests/

# Test specific components
pytest tests/test_orchestrator.py
pytest tests/test_api.py

# Run with coverage
pytest --cov=datascience_platform tests/
```

## 📚 API Documentation

When running the API server, comprehensive documentation is available:

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`
- **OpenAPI Spec**: `http://localhost:8080/openapi.json`

## 🤝 Contributing

To extend the orchestrator:

1. Follow the existing architectural patterns
2. Add appropriate error handling
3. Include progress tracking for long-running operations
4. Update the API endpoints if needed
5. Add comprehensive tests
6. Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
