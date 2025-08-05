# Setup Instructions for New Machine 🚀

Follow these steps to clone and run the DataScience Analytics Platform on a new laptop.

## Prerequisites

Ensure you have the following installed:
- **Python 3.9+** (check with `python --version` or `python3 --version`)
- **pip** (comes with Python)
- **git** (check with `git --version`)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/usorama/datascience-analytics-platform.git
cd datascience-analytics-platform
```

### 2. Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install the Package

```bash
pip install -e .
```

### 5. Verify Installation

```bash
python -c "import datascience_platform; print('✅ Installation successful!')"
```

### 6. Run the Demo

```bash
python FINAL_WORKING_DEMO.py
```

This will:
- Create sample e-commerce data
- Process it through the ETL pipeline
- Generate ML insights
- Create an interactive dashboard (`analytics_dashboard.html`)

## Quick Test Commands

### Test with your own CSV:
```bash
# Make sure your CSV has numeric columns for analysis
python -m datascience_platform analyze your_file.csv --target your_target_column
```

### Start the API server:
```bash
python -m datascience_platform server --port 8080
```

### Get help:
```bash
python -m datascience_platform --help
```

## Troubleshooting

### Issue: Import errors
**Solution:**
```bash
# Make sure you're in the virtual environment
which python  # Should show venv path

# Reinstall in development mode
pip install -e .
```

### Issue: Missing dependencies
**Solution:**
```bash
pip install --force-reinstall -r requirements.txt
```

### Issue: Python version error
**Solution:**
- Install Python 3.9 or higher from [python.org](https://www.python.org/downloads/)
- Use `python3` instead of `python` on macOS/Linux

### Issue: Permission denied
**Solution:**
- On macOS/Linux: Use `sudo` if needed for global installs
- Better: Always use virtual environments (no sudo needed)

## What's Included

After setup, you'll have:
- Complete ETL pipeline for CSV processing
- ML analysis engine with insights generation
- Dashboard generator creating self-contained HTML files
- CLI interface for easy usage
- REST API for programmatic access
- Comprehensive documentation in `/docs`

## Next Steps

1. **Run the demo** to see the platform in action
2. **Try your own CSV files** for analysis
3. **Check the documentation** in `/docs/user-guide/`
4. **Explore examples** in `/docs/examples/`

## Repository Information

- **GitHub URL**: https://github.com/usorama/datascience-analytics-platform
- **License**: MIT
- **Python**: 3.9+
- **Key Dependencies**: pandas, polars, scikit-learn, plotly, fastapi

---

**Questions?** Open an issue on [GitHub](https://github.com/usorama/datascience-analytics-platform/issues)