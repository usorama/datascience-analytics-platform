# DataScience Analytics Platform 🚀

Transform any CSV file into actionable insights with automated ETL, machine learning analysis, and interactive dashboards - all in a single command!

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 🎯 What It Does

The DataScience Analytics Platform automatically:
- 📊 **Processes** any CSV file with intelligent ETL pipeline
- 🤖 **Analyzes** data using machine learning to find patterns and insights
- 📈 **Generates** beautiful, interactive HTML dashboards
- 💡 **Delivers** actionable business insights and KPIs
- 🔌 **Works** completely offline with self-contained dashboards

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/datascience-analytics-platform.git
cd datascience-analytics-platform
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install the package:**
```bash
pip install -e .
```

### Basic Usage

#### Option 1: Run the Demo
```bash
python FINAL_WORKING_DEMO.py
```
This creates sample e-commerce data and generates a complete analytics dashboard.

#### Option 2: Analyze Your Own Data
```bash
# Using the CLI
python -m datascience_platform analyze your_data.csv --target revenue

# Or using Python
from datascience_platform import AnalyticsPipeline

pipeline = AnalyticsPipeline()
result = pipeline.run("your_data.csv", target_column="sales")
```

## 📋 Features

### ETL Pipeline
- ✅ High-performance CSV processing (5-10x faster than pandas)
- ✅ Automatic delimiter and encoding detection
- ✅ Data validation and quality assessment
- ✅ Missing value handling and outlier detection
- ✅ Support for files from 1KB to 10GB+

### Machine Learning
- ✅ Statistical analysis and correlations
- ✅ Pattern and anomaly detection
- ✅ Time series analysis
- ✅ Automated insight generation
- ✅ Business recommendations

### Dashboard Generation
- ✅ Interactive Plotly charts (8 types)
- ✅ Responsive design for mobile/desktop
- ✅ Light/dark theme support
- ✅ Self-contained HTML (works offline)
- ✅ Export to PDF/PNG

## 🛠️ Installation Guide for New Machine

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git

### Step-by-Step Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/datascience-analytics-platform.git
cd datascience-analytics-platform
```

2. **Create a virtual environment (recommended):**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install the package in development mode:**
```bash
pip install -e .
```

5. **Verify installation:**
```bash
python -c "import datascience_platform; print('✅ Installation successful!')"
```

6. **Run the demo:**
```bash
python FINAL_WORKING_DEMO.py
```

## 📁 Project Structure

```
datascience-analytics-platform/
├── src/datascience_platform/    # Core package
│   ├── etl/                     # ETL pipeline modules
│   ├── ml/                      # Machine learning modules
│   ├── dashboard/               # Dashboard generation
│   ├── api/                     # REST API
│   └── cli/                     # Command-line interface
├── docs/                        # Documentation
│   ├── user-guide/             # User guides
│   └── examples/               # Example scripts
├── tests/                       # Test suite
├── requirements.txt             # Dependencies
├── pyproject.toml              # Project configuration
└── FINAL_WORKING_DEMO.py       # Working demo script
```

## 🔧 Troubleshooting

### Common Issues

1. **Import errors after cloning:**
   - Make sure you installed with `pip install -e .`
   - Activate your virtual environment
   - Check Python version: `python --version` (needs 3.9+)

2. **Missing dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Permission errors:**
   - On macOS/Linux: Use `python3` instead of `python`
   - On Windows: Run as administrator if needed

## 📊 Example Output

Running the demo creates:
- `ecommerce_analytics_data.csv` - Sample data file
- `analytics_dashboard.html` - Interactive dashboard

The dashboard includes:
- Key Performance Indicators (KPIs)
- Revenue trends over time
- Category and regional analysis
- Interactive charts with zoom/pan
- Actionable business insights

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [Polars](https://www.pola.rs/) - Lightning-fast DataFrame library
- [Plotly](https://plotly.com/) - Interactive visualization library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web API framework
- [Click](https://click.palletsprojects.com/) - Command line interface
- [scikit-learn](https://scikit-learn.org/) - Machine learning library

---

**Need help?** Open an issue on GitHub or check the [documentation](docs/user-guide/getting-started.md).