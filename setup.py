#!/usr/bin/env python
"""
DataScience Platform - ML-Powered Analytics with NLP Enhancement

A comprehensive platform for data analysis, ML optimization, and dashboard generation.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datascience-platform",
    version="2.0.0",
    author="DataScience Platform Team",
    author_email="team@dsplatform.ai",
    description="ML-powered analytics platform with NLP enhancement and auto-dashboards",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ds-package",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/ds-package/issues",
        "Documentation": "https://github.com/yourusername/ds-package/wiki",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "pandas>=1.5.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "pydantic>=2.0.0",
        
        # NLP dependencies (optional but recommended)
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
        
        # Dashboard dependencies
        "jinja2>=3.0.0",
        
        # Optional but recommended
        "faiss-cpu>=1.7.4",
        "plotly>=5.0.0",
        "streamlit>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
        "gpu": [
            "torch>=2.0.0",
            "faiss-gpu>=1.7.4",
        ],
        "full": [
            "sentence-transformers>=2.2.0",
            "transformers>=4.30.0",
            "faiss-cpu>=1.7.4",
            "optuna>=3.0.0",
            "shap>=0.40.0",
            "mlflow>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dsplatform=datascience_platform.cli.commands:main",
            "ds-analyze=datascience_platform.cli.commands:analyze",
            "ds-dashboard=datascience_platform.cli.commands:dashboard",
        ],
    },
    include_package_data=True,
    package_data={
        "datascience_platform": [
            "dashboard/templates/*.html",
            "dashboard/static/*",
        ],
    },
)
