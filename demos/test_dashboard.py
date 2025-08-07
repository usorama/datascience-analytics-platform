#!/usr/bin/env python3
"""
Simple test script for the DataScience Analytics Dashboard Generator
Bypasses the main package init to avoid dependency conflicts
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import directly from dashboard module
from datascience_platform.dashboard.generator import DashboardGenerator

def generate_simple_data():
    """Generate simple test data"""
    
    # Simple sales data
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    sales_data = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, len(dates)),
        'visitors': np.random.normal(500, 100, len(dates))
    })
    sales_data['sales'] = sales_data['sales'].clip(lower=0)
    sales_data['visitors'] = sales_data['visitors'].clip(lower=0).astype(int)
    
    # Product data
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    product_data = pd.DataFrame({
        'product': products,
        'sales': np.random.uniform(10000, 50000, len(products)),
        'rating': np.random.uniform(3.5, 5.0, len(products))
    })
    
    return sales_data, product_data

def create_simple_dashboard():
    """Create a simple test dashboard"""
    
    print("Generating test data...")
    sales_data, product_data = generate_simple_data()
    
    print("Creating dashboard...")
    
    # Initialize dashboard generator
    dashboard = DashboardGenerator(theme='light', compress=False)
    
    # Set dashboard configuration
    dashboard.set_config(
        title="Test Dashboard",
        description="Simple test dashboard",
        export_enabled=True,
        theme_switcher=True
    )
    
    # Add KPI cards
    total_sales = sales_data['sales'].sum()
    avg_visitors = sales_data['visitors'].mean()
    
    dashboard.add_kpi_card(
        title="Total Sales",
        value=total_sales,
        subtitle="Q1 2024",
        trend=5.2,
        format_type="currency",
        icon="fas fa-dollar-sign"
    )
    
    dashboard.add_kpi_card(
        title="Avg Daily Visitors",
        value=int(avg_visitors),
        subtitle="Daily Average",
        trend=-2.1,
        format_type="number",
        icon="fas fa-users"
    )
    
    # Add a simple line chart
    dashboard.add_chart(\n        chart_type=\"line_chart\",\n        data=sales_data,\n        chart_id=\"sales_trend\",\n        title=\"Sales Trend\",\n        x=\"date\",\n        y=\"sales\",\n        height=400,\n        width_class=\"col-12 col-lg-8\"\n    )\n    \n    # Add a bar chart\n    dashboard.add_chart(\n        chart_type=\"bar_chart\",\n        data=product_data.sort_values('sales', ascending=True),\n        chart_id=\"product_sales\",\n        title=\"Sales by Product\",\n        x=\"sales\",\n        y=\"product\",\n        orientation=\"h\",\n        height=400,\n        width_class=\"col-12 col-lg-4\"\n    )\n    \n    # Add a data table\n    dashboard.add_data_table(\n        data=product_data.round(2),\n        table_id=\"products_table\",\n        title=\"Product Details\",\n        searchable=True,\n        sortable=True,\n        paginated=False,\n        width_class=\"col-12\"\n    )\n    \n    return dashboard\n\ndef main():\n    \"\"\"Main function\"\"\"\n    \n    print(\"=== Simple Dashboard Test ===\")\n    print()\n    \n    try:\n        # Create dashboard\n        dashboard = create_simple_dashboard()\n        \n        # Generate HTML\n        print(\"Generating dashboard HTML...\")\n        output_path = \"test_dashboard.html\"\n        html_content = dashboard.generate_html(output_path)\n        \n        print(f\"✅ Dashboard generated successfully!\")\n        print(f\"📄 File saved as: {output_path}\")\n        print(f\"📊 Dashboard size: {len(html_content):,} characters\")\n        print(f\"🌐 Open {output_path} in your browser to view!\")\n        \n    except Exception as e:\n        print(f\"❌ Error: {e}\")\n        import traceback\n        traceback.print_exc()\n        return 1\n    \n    return 0\n\nif __name__ == \"__main__\":\n    exit(main())