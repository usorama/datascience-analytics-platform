"""Dashboard Generator Module for DataScience Analytics Platform

This module provides comprehensive dashboard generation capabilities including:
- Interactive chart components using Plotly
- Responsive HTML templates with Jinja2
- Offline-capable dashboard generation
- Mobile-first responsive design
- Theme switching and export functionality
"""

from .generator import DashboardGenerator
from .charts import ChartBuilder

__all__ = ['DashboardGenerator', 'ChartBuilder']