#!/usr/bin/env python3
"""
Example usage of the DataScience Analytics Dashboard Generator

This script demonstrates how to create interactive dashboards with:
- KPI cards
- Interactive charts (line, bar, scatter, heatmap, etc.)
- Data tables
- Filters
- Responsive design and theming
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datascience_platform.dashboard import DashboardGenerator

def generate_sample_data():
    """Generate sample data for demonstration"""
    
    # Time series data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    ts_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 100,
        'visitors': np.random.normal(500, 100, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 50,
        'conversion_rate': np.random.normal(0.05, 0.01, len(dates))
    })
    ts_data['sales'] = ts_data['sales'].clip(lower=0)
    ts_data['visitors'] = ts_data['visitors'].clip(lower=0).astype(int)
    ts_data['conversion_rate'] = ts_data['conversion_rate'].clip(0, 1)
    
    # Product data
    products = ['Product A', 'Product B', 'Product C', 'Product D', 'Product E']
    product_data = pd.DataFrame({
        'product': products,
        'sales': np.random.uniform(10000, 50000, len(products)),
        'profit_margin': np.random.uniform(0.1, 0.4, len(products)),
        'units_sold': np.random.randint(100, 1000, len(products)),
        'rating': np.random.uniform(3.5, 5.0, len(products))
    })
    
    # Regional data
    regions = ['North', 'South', 'East', 'West', 'Central']
    regional_data = pd.DataFrame({
        'region': regions,
        'sales': np.random.uniform(20000, 80000, len(regions)),
        'customers': np.random.randint(500, 2000, len(regions)),
        'growth_rate': np.random.uniform(-0.1, 0.3, len(regions))
    })
    
    # Customer segments
    segments = ['Premium', 'Standard', 'Budget', 'Enterprise']
    segment_data = pd.DataFrame({
        'segment': segments,
        'customers': np.random.randint(100, 1000, len(segments)),
        'avg_order_value': np.random.uniform(50, 500, len(segments)),
        'lifetime_value': np.random.uniform(200, 2000, len(segments))
    })
    
    # Correlation matrix data
    metrics = ['Sales', 'Marketing Spend', 'Customer Satisfaction', 'Product Quality', 'Support Tickets']
    correlation_data = pd.DataFrame(
        np.random.uniform(-1, 1, (len(metrics), len(metrics))),
        index=metrics,
        columns=metrics
    )
    # Make it symmetric
    correlation_data = (correlation_data + correlation_data.T) / 2
    np.fill_diagonal(correlation_data.values, 1)
    
    return {
        'time_series': ts_data,
        'products': product_data,
        'regions': regional_data,
        'segments': segment_data,
        'correlation': correlation_data
    }

def create_sample_dashboard():
    """Create a comprehensive sample dashboard"""
    
    print("Generating sample data...")
    data = generate_sample_data()
    
    print("Creating dashboard...")
    
    # Initialize dashboard generator
    dashboard = DashboardGenerator(theme='light', compress=True)
    
    # Set dashboard configuration
    dashboard.set_config(
        title="Sales Analytics Dashboard",
        description="Comprehensive sales and marketing analytics dashboard",
        export_enabled=True,
        theme_switcher=True
    )
    
    # Add KPI cards
    total_sales = data['time_series']['sales'].sum()
    avg_visitors = data['time_series']['visitors'].mean()
    avg_conversion = data['time_series']['conversion_rate'].mean()
    sales_growth = ((data['time_series']['sales'].tail(30).mean() / 
                    data['time_series']['sales'].head(30).mean()) - 1) * 100
    
    dashboard.add_kpi_card(
        title="Total Sales",
        value=total_sales,
        subtitle="Year to Date",
        trend=sales_growth,
        format_type="currency",
        icon="fas fa-dollar-sign"
    )
    
    dashboard.add_kpi_card(
        title="Avg Daily Visitors",
        value=int(avg_visitors),
        subtitle="Daily Average",
        trend=5.2,
        format_type="number",
        icon="fas fa-users"
    )
    
    dashboard.add_kpi_card(
        title="Conversion Rate",
        value=avg_conversion * 100,
        subtitle="Overall Rate",
        trend=-2.1,
        format_type="percentage",
        icon="fas fa-chart-line"
    )
    
    dashboard.add_kpi_card(
        title="Active Products",
        value=len(data['products']),
        subtitle="In Catalog",
        trend=0.0,
        format_type="number",
        icon="fas fa-box"
    )
    
    # Add filters
    dashboard.add_filter(
        filter_id="date_range",
        label="Date Range",
        filter_type="daterange",
        target_components=["sales_trend", "visitor_trend"]
    )
    
    dashboard.add_filter(
        filter_id="region_filter",
        label="Region",
        filter_type="select",
        options=[
            {"label": "All Regions", "value": "all"},
            {"label": "North", "value": "north"},
            {"label": "South", "value": "south"},
            {"label": "East", "value": "east"},
            {"label": "West", "value": "west"},
            {"label": "Central", "value": "central"}
        ],
        default_value="all",
        target_components=["regional_sales"]
    )
    
    dashboard.add_filter(
        filter_id="sales_threshold",
        label="Min Sales Threshold",
        filter_type="slider",
        options=[
            {"label": "0", "value": 0},
            {"label": "100K", "value": 100000}
        ],
        default_value=0,
        target_components=["product_sales"]
    )
    
    # Add charts
    
    # Time series chart
    dashboard.add_chart(
        chart_type="time_series",
        data=data['time_series'],
        chart_id="sales_trend",
        title="Sales Trend Over Time",
        x="date",
        y="sales",
        height=400,
        width_class="col-12 col-lg-8"
    )
    
    # Bar chart for products
    dashboard.add_chart(
        chart_type="bar",
        data=data['products'].sort_values('sales', ascending=True),
        chart_id="product_sales",
        title="Sales by Product",
        x="sales",
        y="product",
        orientation="h",
        height=400,
        width_class="col-12 col-lg-4"
    )
    
    # Scatter plot
    dashboard.add_chart(
        chart_type="scatter_plot",
        data=data['products'],
        chart_id="profit_vs_rating",
        title="Profit Margin vs Product Rating",
        x="rating",
        y="profit_margin",
        size="units_sold",
        color="product",
        height=400,
        width_class="col-12 col-lg-6"
    )
    
    # Pie chart for segments
    dashboard.add_chart(
        chart_type="pie",
        data=data['segments'],
        chart_id="customer_segments",
        title="Customer Distribution by Segment",
        names="segment",
        values="customers",
        height=400,
        width_class="col-12 col-lg-6"
    )
    
    # Heatmap for correlations
    dashboard.add_chart(
        chart_type="heatmap",
        data=data['correlation'],
        chart_id="metric_correlations",
        title="Metric Correlations",
        height=500,
        width_class="col-12 col-lg-8"
    )
    
    # Gauge chart for conversion rate
    dashboard.add_chart(
        chart_type="gauge_chart",
        data=pd.DataFrame({'value': [avg_conversion * 100]}),  # Dummy data for gauge
        chart_id="conversion_gauge",
        title="Conversion Rate Gauge",
        value=avg_conversion * 100,
        min_val=0,
        max_val=10,
        height=400,
        width_class="col-12 col-lg-4"
    )
    
    # Add data tables
    
    # Products table
    dashboard.add_data_table(
        data=data['products'].round(2),
        table_id="products_table",
        title="Product Performance Details",
        searchable=True,
        sortable=True,
        paginated=True,
        page_size=10,
        width_class="col-12 col-lg-6"
    )
    
    # Regional performance table
    dashboard.add_data_table(
        data=data['regions'].round(2),
        table_id="regional_table",
        title="Regional Performance",
        searchable=True,
        sortable=True,
        paginated=False,
        width_class="col-12 col-lg-6"
    )
    
    return dashboard

def main():
    """Main function to generate and save the dashboard"""
    
    print("=== DataScience Analytics Dashboard Generator Demo ===")
    print()
    
    try:
        # Create dashboard
        dashboard = create_sample_dashboard()
        
        # Generate HTML
        print("Generating dashboard HTML...")
        output_path = "sample_dashboard.html"
        html_content = dashboard.generate_html(output_path)
        
        print(f"✅ Dashboard generated successfully!")
        print(f"📄 File saved as: {output_path}")
        print(f"📊 Dashboard size: {len(html_content):,} characters")
        print(f"🎨 Theme: {dashboard.theme}")
        print(f"🗜️  Compression: {'Enabled' if dashboard.compress else 'Disabled'}")
        print()
        print("Dashboard Features:")
        print("- 📈 Interactive Plotly charts with zoom/pan")
        print("- 📋 Sortable and searchable data tables")
        print("- 🔍 Interactive filters")
        print("- 🌓 Light/dark theme switching")
        print("- 📱 Mobile responsive design")
        print("- 💾 Offline functionality (all data embedded)")
        print("- 📤 Export to PDF/PNG")
        print("- ⌨️  Keyboard shortcuts (Ctrl+D for theme, Ctrl+E for export)")
        print()
        print(f"🌐 Open {output_path} in your browser to view the dashboard!")
        
        # Also generate a dark theme version
        print("\nGenerating dark theme version...")
        dashboard.set_theme('dark')
        dark_output = "sample_dashboard_dark.html"
        dashboard.generate_html(dark_output)
        print(f"🌙 Dark theme version saved as: {dark_output}")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())