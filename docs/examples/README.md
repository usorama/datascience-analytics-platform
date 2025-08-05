# DataScience Analytics Platform - Examples

This directory contains practical examples demonstrating the capabilities of the DataScience Analytics Platform. Each example showcases different aspects of data processing, validation, and analysis.

## Available Examples

### 1. Sales Data Analysis (`example_sales_analysis.py`)

**What it demonstrates:**
- Reading and validating sales transaction data
- Schema-based data validation
- Sales performance analysis and KPI calculation
- Regional and customer segment analysis
- Data transformation and cleaning

**Key Features:**
- Automatic sample data generation
- Comprehensive sales metrics calculation
- Top products and customer analysis
- Regional performance comparison
- Seasonal trend identification

**Run the example:**
```bash
cd docs/examples
python example_sales_analysis.py
```

**Output:**
- Cleaned sales data (Parquet format)
- Sales analysis results (JSON)
- Console output with detailed insights

### 2. Customer Segmentation (`example_customer_segmentation.py`)

**What it demonstrates:**
- Advanced customer analytics using RFM analysis
- Customer Lifetime Value (CLV) calculation
- Behavioral segmentation and clustering
- Marketing recommendation generation

**Key Features:**
- RFM (Recency, Frequency, Monetary) analysis
- Customer segment identification
- CLV estimation and profitability analysis
- Channel and demographic analysis
- Actionable marketing recommendations

**Run the example:**
```bash
cd docs/examples
python example_customer_segmentation.py
```

**Output:**
- Customer segments with RFM scores (Parquet format)
- Segmentation analysis results (JSON)
- Marketing strategy recommendations

### 3. Time Series Forecasting (`example_time_series_forecast.py`)

**What it demonstrates:**
- Time series data preprocessing and validation
- Trend and seasonality analysis
- Multiple forecasting approaches
- Forecast accuracy evaluation

**Key Features:**
- Pattern detection (weekly, monthly, seasonal)
- Moving averages and exponential smoothing
- Holiday and promotional impact analysis
- Backtesting and accuracy metrics
- Business insights and recommendations

**Run the example:**
```bash
cd docs/examples
python example_time_series_forecast.py
```

**Output:**
- Time series data with calculated features (Parquet format)
- Sales forecasts with confidence intervals (Parquet format)
- Analysis summary and insights (JSON)

## Sample Data

Each example automatically generates realistic sample data if not found:

- **Sales Analysis**: 1,000 transactions across multiple products and regions
- **Customer Segmentation**: 5,000 transactions for 500 customers with demographics
- **Time Series**: 2 years of daily sales data with seasonal patterns

Sample data files are created in the examples directory:
- `sample_sales_data.csv`
- `sample_customer_data.csv` 
- `sample_time_series_data.csv`

## Output Directory

All examples save their results to an `output/` subdirectory:

```
docs/examples/output/
├── cleaned_sales_data.parquet
├── sales_analysis_results.json
├── customer_segments.parquet
├── segmentation_analysis_results.json
├── time_series_with_analysis.parquet
├── sales_forecast.parquet
└── time_series_analysis_results.json
```

## Requirements

These examples require the DataScience Analytics Platform to be installed:

```bash
# From the project root
pip install -e .

# Or with Poetry
poetry install
```

## Customization

### Using Your Own Data

Replace the sample data generation with your own data files:

1. **Sales Analysis**: Provide a CSV with columns matching the sales schema
2. **Customer Segmentation**: Provide customer transaction data
3. **Time Series**: Provide daily time series data

### Modifying Analysis Parameters

Each example includes configurable parameters:

```python
# Sales Analysis
num_transactions = 1000  # Adjust sample size
analysis_period = "2024"  # Change analysis period

# Customer Segmentation
num_customers = 500      # Adjust customer base size
analysis_date = datetime(2024, 12, 31)  # Set analysis date

# Time Series Forecasting
forecast_days = 30       # Change forecast horizon
test_days = 30          # Adjust backtesting period
```

### Adding New Analysis

Extend the examples by adding new analysis functions:

```python
def your_custom_analysis(df: pl.DataFrame) -> Dict[str, Any]:
    """Add your custom analysis here."""
    # Your analysis code
    return results

# Call in main()
custom_results = your_custom_analysis(cleaned_df)
```

## Common Issues and Solutions

### Memory Issues
For large datasets, enable chunked processing:
```python
options = ReadOptions(chunk_size=10000)
reader = DataReader(options)
```

### Date Parsing Issues
Ensure dates are in the correct format:
```python
options = ReadOptions(parse_dates=['date_column'])
```

### Missing Dependencies
If you encounter import errors:
```bash
pip install pandas polars numpy scikit-learn
```

## Next Steps

After running these examples:

1. **Explore the Results**: Check the output files and JSON summaries
2. **Modify Parameters**: Experiment with different settings
3. **Use Real Data**: Replace sample data with your own datasets
4. **Extend Analysis**: Add custom analysis functions
5. **Integrate into Pipelines**: Use the patterns in production workflows

## Getting Help

- Check the [API Reference](../user-guide/api-reference.md) for detailed method documentation
- See the [CLI Reference](../user-guide/cli-reference.md) for command-line usage
- Review the [Getting Started Guide](../user-guide/getting-started.md) for basic concepts

For more advanced usage patterns and production deployment guidance, see the main documentation.