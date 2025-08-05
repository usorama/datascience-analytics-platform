"""Interactive Chart Components using Plotly for Dashboard Generation"""

import json
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder


class ChartBuilder:
    """Builds interactive Plotly charts with responsive design and theme support"""
    
    def __init__(self, theme: str = 'light'):
        """Initialize chart builder with theme configuration
        
        Args:
            theme: 'light' or 'dark' theme
        """
        self.theme = theme
        self.colors = self._get_theme_colors()
        self.base_config = {
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
            'displaylogo': False,
            'responsive': True
        }
        
    def _get_theme_colors(self) -> Dict[str, str]:
        """Get color palette based on theme"""
        if self.theme == 'dark':
            return {
                'background': '#1a1a1a',
                'paper': '#2d2d2d',
                'text': '#ffffff',
                'grid': '#404040',
                'primary': '#3b82f6',
                'secondary': '#8b5cf6',
                'success': '#10b981',
                'warning': '#f59e0b',
                'error': '#ef4444',
                'palette': ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#84cc16', '#f97316']
            }
        else:
            return {
                'background': '#ffffff',
                'paper': '#f8fafc',
                'text': '#1f2937',
                'grid': '#e5e7eb',
                'primary': '#2563eb',
                'secondary': '#7c3aed',
                'success': '#059669',
                'warning': '#d97706',
                'error': '#dc2626',
                'palette': ['#2563eb', '#7c3aed', '#059669', '#d97706', '#dc2626', '#0891b2', '#65a30d', '#ea580c']
            }
    
    def _get_base_layout(self, title: str = "", height: int = 400) -> Dict[str, Any]:
        """Get base layout configuration for all charts"""
        return {
            'title': {
                'text': title,
                'font': {'size': 18, 'color': self.colors['text']},
                'x': 0.5,
                'xanchor': 'center'
            },
            'plot_bgcolor': self.colors['background'],
            'paper_bgcolor': self.colors['paper'],
            'font': {'color': self.colors['text']},
            'height': height,
            'margin': {'l': 50, 'r': 50, 't': 80, 'b': 50},
            'xaxis': {
                'gridcolor': self.colors['grid'],
                'tickfont': {'color': self.colors['text']},
                'title': {'font': {'color': self.colors['text']}}
            },
            'yaxis': {
                'gridcolor': self.colors['grid'],
                'tickfont': {'color': self.colors['text']},
                'title': {'font': {'color': self.colors['text']}}
            }
        }
    
    def line_chart(self, data: pd.DataFrame, x: str, y: Union[str, List[str]], 
                   title: str = "", height: int = 400, **kwargs) -> str:
        """Create interactive line chart
        
        Args:
            data: DataFrame with chart data
            x: Column name for x-axis
            y: Column name(s) for y-axis (single string or list for multiple lines)
            title: Chart title
            height: Chart height in pixels
            **kwargs: Additional Plotly Express arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = px.line(
            data, x=x, y=y, 
            title=title,
            color_discrete_sequence=self.colors['palette'],
            **kwargs
        )
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def bar_chart(self, data: pd.DataFrame, x: str, y: str, 
                  title: str = "", orientation: str = 'v', height: int = 400, **kwargs) -> str:
        """Create interactive bar chart
        
        Args:
            data: DataFrame with chart data
            x: Column name for x-axis
            y: Column name for y-axis
            title: Chart title
            orientation: 'v' for vertical, 'h' for horizontal
            height: Chart height in pixels
            **kwargs: Additional Plotly Express arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = px.bar(
            data, x=x, y=y,
            title=title,
            orientation=orientation,
            color_discrete_sequence=self.colors['palette'],
            **kwargs
        )
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def scatter_plot(self, data: pd.DataFrame, x: str, y: str, 
                     title: str = "", size: Optional[str] = None, 
                     color: Optional[str] = None, height: int = 400, **kwargs) -> str:
        """Create interactive scatter plot
        
        Args:
            data: DataFrame with chart data
            x: Column name for x-axis
            y: Column name for y-axis
            title: Chart title
            size: Column name for bubble size (optional)
            color: Column name for color mapping (optional)
            height: Chart height in pixels
            **kwargs: Additional Plotly Express arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = px.scatter(
            data, x=x, y=y,
            size=size, color=color,
            title=title,
            color_discrete_sequence=self.colors['palette'],
            **kwargs
        )
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def heatmap(self, data: pd.DataFrame, title: str = "", height: int = 400, **kwargs) -> str:
        """Create interactive heatmap
        
        Args:
            data: DataFrame with correlation matrix or pivot table data
            title: Chart title
            height: Chart height in pixels
            **kwargs: Additional Plotly arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='Viridis',
            **kwargs
        ))
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def distribution_plot(self, data: pd.DataFrame, column: str, 
                         plot_type: str = 'histogram', title: str = "", 
                         height: int = 400, **kwargs) -> str:
        """Create distribution plots (histogram, box, violin)
        
        Args:
            data: DataFrame with data
            column: Column name for distribution
            plot_type: 'histogram', 'box', or 'violin'
            title: Chart title
            height: Chart height in pixels
            **kwargs: Additional Plotly Express arguments
            
        Returns:
            JSON string representation of the chart
        """
        if plot_type == 'histogram':
            fig = px.histogram(
                data, x=column,
                title=title,
                color_discrete_sequence=self.colors['palette'],
                **kwargs
            )
        elif plot_type == 'box':
            fig = px.box(
                data, y=column,
                title=title,
                color_discrete_sequence=self.colors['palette'],
                **kwargs
            )
        elif plot_type == 'violin':
            fig = px.violin(
                data, y=column,
                title=title,
                color_discrete_sequence=self.colors['palette'],
                **kwargs
            )
        else:
            raise ValueError("plot_type must be 'histogram', 'box', or 'violin'")
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def pie_chart(self, data: pd.DataFrame, names: str, values: str, 
                  title: str = "", height: int = 400, **kwargs) -> str:
        """Create interactive pie chart
        
        Args:
            data: DataFrame with chart data
            names: Column name for pie slice labels
            values: Column name for pie slice values
            title: Chart title
            height: Chart height in pixels
            **kwargs: Additional Plotly Express arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = px.pie(
            data, names=names, values=values,
            title=title,
            color_discrete_sequence=self.colors['palette'],
            **kwargs
        )
        
        layout = self._get_base_layout(title, height)
        layout['showlegend'] = True
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def gauge_chart(self, value: float, title: str = "", 
                   min_val: float = 0, max_val: float = 100,
                   threshold_colors: Optional[List[Dict]] = None,
                   height: int = 400) -> str:
        """Create gauge/indicator chart
        
        Args:
            value: Current value to display
            title: Chart title
            min_val: Minimum value for gauge
            max_val: Maximum value for gauge
            threshold_colors: List of color thresholds
            height: Chart height in pixels
            
        Returns:
            JSON string representation of the chart
        """
        if threshold_colors is None:
            threshold_colors = [
                {"range": [min_val, max_val * 0.5], "color": self.colors['error']},
                {"range": [max_val * 0.5, max_val * 0.8], "color": self.colors['warning']},
                {"range": [max_val * 0.8, max_val], "color": self.colors['success']}
            ]
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title, 'font': {'color': self.colors['text']}},
            gauge={
                'axis': {'range': [min_val, max_val], 'tickcolor': self.colors['text']},
                'bar': {'color': self.colors['primary']},
                'steps': threshold_colors,
                'borderwidth': 2,
                'bordercolor': self.colors['text']
            }
        ))
        
        layout = self._get_base_layout(title, height)
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def time_series(self, data: pd.DataFrame, x: str, y: str, 
                   title: str = "", range_selector: bool = True,
                   height: int = 400, **kwargs) -> str:
        """Create time series chart with range selector
        
        Args:
            data: DataFrame with time series data
            x: Column name for time axis
            y: Column name for values
            title: Chart title
            range_selector: Whether to include range selector buttons
            height: Chart height in pixels
            **kwargs: Additional Plotly arguments
            
        Returns:
            JSON string representation of the chart
        """
        fig = px.line(
            data, x=x, y=y,
            title=title,
            color_discrete_sequence=self.colors['palette'],
            **kwargs
        )
        
        layout = self._get_base_layout(title, height)
        
        if range_selector:
            layout['xaxis']['rangeselector'] = {
                'buttons': [
                    {'count': 7, 'label': '7D', 'step': 'day', 'stepmode': 'backward'},
                    {'count': 30, 'label': '30D', 'step': 'day', 'stepmode': 'backward'},
                    {'count': 90, 'label': '3M', 'step': 'day', 'stepmode': 'backward'},
                    {'step': 'all', 'label': 'All'}
                ],
                'font': {'color': self.colors['text']},
                'bgcolor': self.colors['paper'],
                'bordercolor': self.colors['grid']
            }
            layout['xaxis']['rangeslider'] = {'visible': True}
        
        fig.update_layout(**layout)
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def get_chart_config(self) -> Dict[str, Any]:
        """Get base Plotly configuration for all charts"""
        return self.base_config