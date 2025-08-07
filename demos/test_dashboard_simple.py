#!/usr/bin/env python3
"""
Simple test script for the DataScience Analytics Dashboard Generator
"""

import pandas as pd
import numpy as np
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
    dashboard.add_chart(
        chart_type="line_chart",
        data=sales_data,
        chart_id="sales_trend",
        title="Sales Trend",
        x="date",
        y="sales",
        height=400,
        width_class="col-12 col-lg-8"
    )
    
    # Add a bar chart
    dashboard.add_chart(
        chart_type="bar_chart",
        data=product_data.sort_values('sales', ascending=True),
        chart_id="product_sales",
        title="Sales by Product",
        x="sales",
        y="product",
        orientation="h",
        height=400,
        width_class="col-12 col-lg-4"
    )
    
    # Add a data table
    dashboard.add_data_table(
        data=product_data.round(2),
        table_id="products_table",
        title="Product Details",
        searchable=True,
        sortable=True,
        paginated=False,
        width_class="col-12"
    )
    
    return dashboard

def main():
    """Main function"""
    
    print("=== Simple Dashboard Test ===")
    print()
    
    try:
        # Create dashboard
        dashboard = create_simple_dashboard()
        
        # Generate HTML
        print("Generating dashboard HTML...")
        output_path = "test_dashboard.html"
        html_content = dashboard.generate_html(output_path)
        
        print(f"✅ Dashboard generated successfully!")
        print(f"📄 File saved as: {output_path}")
        print(f"📊 Dashboard size: {len(html_content):,} characters")
        print(f"🌐 Open {output_path} in your browser to view!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())