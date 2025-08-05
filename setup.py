"""Setup script for DataScience Analytics Platform Dashboard Generator"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "jinja2>=3.1.0",
    ]

setup(
    name="datascience-dashboard-generator",
    version="1.0.0",
    author="DataScience Platform Team",
    author_email="team@datascienceplatform.com",
    description="Interactive HTML/JS/CSS dashboard generator for data science analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/datascienceplatform/dashboard-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "datascience_platform.dashboard": [
            "templates/*.html",
            "templates/components/*.html",
            "static/*.css",
            "static/*.js",
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "ml": [
            "scipy>=1.10.0",
            "scikit-learn>=1.3.0",
            "seaborn>=0.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ds-dashboard=datascience_platform.dashboard.cli:main",
        ],
    },
    keywords="dashboard, data visualization, plotly, interactive, html, analytics",
    project_urls={
        "Bug Reports": "https://github.com/datascienceplatform/dashboard-generator/issues",
        "Source": "https://github.com/datascienceplatform/dashboard-generator",
        "Documentation": "https://dashboard-generator.readthedocs.io/",
    },
)