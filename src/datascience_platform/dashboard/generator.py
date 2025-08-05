"""Dashboard Generator - Creates self-contained HTML dashboards with embedded data and interactivity"""

import os
import json
import gzip
import base64
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template
from .charts import ChartBuilder


class DashboardGenerator:
    """Generates self-contained HTML dashboards with embedded data and interactive charts"""
    
    def __init__(self, theme: str = 'light', compress: bool = True):
        """Initialize dashboard generator
        
        Args:
            theme: 'light' or 'dark' theme
            compress: Whether to compress embedded data
        """
        self.theme = theme
        self.compress = compress
        self.chart_builder = ChartBuilder(theme)
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / 'templates'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
        
        # Dashboard configuration
        self.config = {
            'title': 'DataScience Analytics Dashboard',
            'description': 'Interactive data visualization dashboard',
            'favicon': None,
            'export_enabled': True,
            'theme_switcher': True,
            'responsive': True
        }
        
        # Dashboard components
        self.components = {
            'kpis': [],
            'charts': [],
            'tables': [],
            'filters': []
        }
        
        # Embedded data store
        self.data_store = {}
    
    def set_config(self, **kwargs) -> 'DashboardGenerator':
        """Set dashboard configuration
        
        Args:
            **kwargs: Configuration options (title, description, etc.)
            
        Returns:
            Self for method chaining
        """
        self.config.update(kwargs)
        return self
    
    def add_kpi_card(self, title: str, value: Union[str, float, int], 
                     subtitle: Optional[str] = None, trend: Optional[float] = None,
                     format_type: str = 'number', icon: Optional[str] = None) -> 'DashboardGenerator':
        """Add KPI card to dashboard
        
        Args:
            title: KPI title
            value: KPI value
            subtitle: Optional subtitle
            trend: Trend percentage (positive/negative)
            format_type: 'number', 'currency', 'percentage'
            icon: Optional icon class/name
            
        Returns:
            Self for method chaining
        """
        kpi = {
            'id': f"kpi_{len(self.components['kpis'])}",
            'title': title,
            'value': value,
            'subtitle': subtitle,
            'trend': trend,
            'format_type': format_type,
            'icon': icon
        }
        self.components['kpis'].append(kpi)
        return self
    
    def add_chart(self, chart_type: str, data: pd.DataFrame, chart_id: str,
                  title: str = "", height: int = 400, width_class: str = 'col-12 col-lg-6',
                  **chart_kwargs) -> 'DashboardGenerator':
        """Add chart to dashboard
        
        Args:
            chart_type: Type of chart ('line', 'bar', 'scatter', 'heatmap', etc.)
            data: DataFrame with chart data
            chart_id: Unique identifier for the chart
            title: Chart title
            height: Chart height in pixels
            width_class: Bootstrap grid classes for responsive width
            **chart_kwargs: Additional arguments passed to chart builder
            
        Returns:
            Self for method chaining
        """
        # Store data for offline use
        data_key = f"data_{chart_id}"
        self.data_store[data_key] = self._serialize_data(data)
        
        # Generate chart JSON
        chart_method = getattr(self.chart_builder, chart_type, None)
        if chart_method is None:
            chart_method = getattr(self.chart_builder, f"{chart_type}_chart", None)
        
        if chart_method is None:
            raise ValueError(f"Unknown chart type: {chart_type}")
        
        # Special handling for gauge charts which don't use DataFrame
        if chart_type == 'gauge_chart':
            chart_json = chart_method(title=title, height=height, **chart_kwargs)
        else:
            chart_json = chart_method(data, title=title, height=height, **chart_kwargs)
        
        chart = {
            'id': chart_id,
            'type': chart_type,
            'title': title,
            'height': height,
            'width_class': width_class,
            'chart_json': chart_json,
            'data_key': data_key,
            'config': self.chart_builder.get_chart_config()
        }
        
        self.components['charts'].append(chart)
        return self
    
    def add_data_table(self, data: pd.DataFrame, table_id: str, title: str = "",
                      searchable: bool = True, sortable: bool = True,
                      paginated: bool = True, page_size: int = 10,
                      width_class: str = 'col-12') -> 'DashboardGenerator':
        """Add data table to dashboard
        
        Args:
            data: DataFrame to display
            table_id: Unique identifier for the table
            title: Table title
            searchable: Enable search functionality
            sortable: Enable column sorting
            paginated: Enable pagination
            page_size: Rows per page
            width_class: Bootstrap grid classes for responsive width
            
        Returns:
            Self for method chaining
        """
        # Store data for offline use
        data_key = f"data_{table_id}"
        self.data_store[data_key] = self._serialize_data(data)
        
        table = {
            'id': table_id,
            'title': title,
            'width_class': width_class,
            'data_key': data_key,
            'searchable': searchable,
            'sortable': sortable,
            'paginated': paginated,
            'page_size': page_size,
            'columns': list(data.columns),
            'rows': data.to_dict('records')
        }
        
        self.components['tables'].append(table)
        return self
    
    def add_filter(self, filter_id: str, label: str, filter_type: str,
                  options: Optional[List[Dict]] = None, default_value: Any = None,
                  target_components: Optional[List[str]] = None) -> 'DashboardGenerator':
        """Add interactive filter to dashboard
        
        Args:
            filter_id: Unique identifier for the filter
            label: Filter label
            filter_type: 'select', 'multiselect', 'date', 'daterange', 'slider'
            options: List of options for select filters [{'label': 'Label', 'value': 'value'}]
            default_value: Default filter value
            target_components: List of component IDs that this filter affects
            
        Returns:
            Self for method chaining
        """
        filter_config = {
            'id': filter_id,
            'label': label,
            'type': filter_type,
            'options': options or [],
            'default_value': default_value,
            'target_components': target_components or []
        }
        
        self.components['filters'].append(filter_config)
        return self
    
    def _serialize_data(self, data: pd.DataFrame) -> str:
        """Serialize DataFrame for embedding in HTML
        
        Args:
            data: DataFrame to serialize
            
        Returns:
            Serialized data string (compressed if enabled)
        """
        json_str = data.to_json(orient='records', date_format='iso')
        
        if self.compress:
            # Compress data and encode as base64
            compressed = gzip.compress(json_str.encode('utf-8'))
            return base64.b64encode(compressed).decode('ascii')
        
        return json_str
    
    def _get_static_assets(self) -> Dict[str, str]:
        """Load static CSS and JS assets
        
        Returns:
            Dictionary with 'css' and 'js' keys containing asset content
        """
        static_dir = Path(__file__).parent / 'static'
        assets = {}
        
        # Load CSS
        css_file = static_dir / 'styles.css'
        if css_file.exists():
            with open(css_file, 'r', encoding='utf-8') as f:
                assets['css'] = f.read()
        else:
            assets['css'] = ""
        
        # Load JS
        js_file = static_dir / 'dashboard.js'
        if js_file.exists():
            with open(js_file, 'r', encoding='utf-8') as f:
                assets['js'] = f.read()
        else:
            assets['js'] = ""
        
        return assets
    
    def generate_html(self, output_path: Optional[str] = None) -> str:
        """Generate complete dashboard HTML
        
        Args:
            output_path: Optional path to save HTML file
            
        Returns:
            Generated HTML content
        """
        # Load main template
        template = self.jinja_env.get_template('base.html')
        
        # Get static assets
        assets = self._get_static_assets()
        
        # Prepare template context
        from datetime import datetime
        context = {
            'config': self.config,
            'theme': self.theme,
            'components': self.components,
            'data_store': self.data_store,
            'assets': assets,
            'compress': self.compress,
            'current_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Render template
        html_content = template.render(**context)
        
        # Save to file if path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def generate_pdf_export_html(self) -> str:
        """Generate print-optimized HTML for PDF export
        
        Returns:
            Print-optimized HTML content
        """
        # Use print template if available, otherwise base template with print styles
        try:
            template = self.jinja_env.get_template('print.html')
        except:
            template = self.jinja_env.get_template('base.html')
        
        # Get static assets
        assets = self._get_static_assets()
        
        # Add print-specific styles
        print_css = """
        @media print {
            .no-print { display: none !important; }
            .chart-container { page-break-inside: avoid; }
            body { background: white !important; }
        }
        """
        assets['css'] += print_css
        
        # Prepare context for print
        context = {
            'config': {**self.config, 'print_mode': True},
            'theme': 'light',  # Force light theme for print
            'components': self.components,
            'data_store': self.data_store,
            'assets': assets,
            'compress': self.compress
        }
        
        return template.render(**context)
    
    def clear_components(self) -> 'DashboardGenerator':
        """Clear all dashboard components
        
        Returns:
            Self for method chaining
        """
        self.components = {
            'kpis': [],
            'charts': [],
            'tables': [],
            'filters': []
        }
        self.data_store = {}
        return self
    
    def set_theme(self, theme: str) -> 'DashboardGenerator':
        """Change dashboard theme
        
        Args:
            theme: 'light' or 'dark'
            
        Returns:
            Self for method chaining
        """
        self.theme = theme
        self.chart_builder = ChartBuilder(theme)
        return self