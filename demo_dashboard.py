#!/usr/bin/env python3
"""
DataScience Analytics Dashboard Generator - Demo Script
Creates a comprehensive dashboard showcasing all features
"""

import pandas as pd
import numpy as np
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datascience_platform.dashboard.generator import DashboardGenerator

def generate_demo_data():
    """Generate demonstration data"""
    
    # Time series data
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
    time_series = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(5000, 1000, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 30) * 500,
        'orders': np.random.poisson(50, len(dates)),
        'visitors': np.random.normal(2000, 400, len(dates))
    })
    time_series['sales'] = time_series['sales'].clip(lower=0)
    time_series['visitors'] = time_series['visitors'].clip(lower=0).astype(int)
    
    # Product data
    products = ['Laptop Pro', 'Gaming Mouse', 'Wireless Headphones', 'Smart Watch', 'Tablet', 'Bluetooth Speaker']
    product_data = pd.DataFrame({
        'product': products,
        'sales': np.random.uniform(50000, 200000, len(products)),
        'units_sold': np.random.randint(100, 2000, len(products)),
        'rating': np.random.uniform(3.5, 4.9, len(products)),
        'category': np.random.choice(['Electronics', 'Computers', 'Accessories'], len(products))
    })
    
    # Regional data  
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    regional_data = pd.DataFrame({
        'region': regions,
        'revenue': np.random.uniform(500000, 2000000, len(regions)),
        'customers': np.random.randint(5000, 25000, len(regions))
    })
    
    # Correlation matrix
    metrics = ['Sales', 'Marketing', 'Satisfaction', 'Quality']
    correlation_data = pd.DataFrame(
        np.random.uniform(-0.8, 0.8, (len(metrics), len(metrics))),
        index=metrics,
        columns=metrics
    )
    np.fill_diagonal(correlation_data.values, 1.0)
    
    return time_series, product_data, regional_data, correlation_data

def create_demo_dashboard():
    """Create demonstration dashboard"""
    
    print("Generating demo data...")
    time_series, products, regions, correlations = generate_demo_data()
    
    print("Creating dashboard...")
    dashboard = DashboardGenerator(theme='light', compress=True)
    
    # Configure dashboard
    dashboard.set_config(
        title="E-Commerce Analytics Dashboard",
        description="Business intelligence dashboard with interactive visualizations",
        export_enabled=True,
        theme_switcher=True
    )
    
    # Add KPI cards
    total_revenue = time_series['sales'].sum()
    total_orders = time_series['orders'].sum()
    
    dashboard.add_kpi_card(
        title="Total Revenue",
        value=total_revenue,  
        subtitle="Last 6 Months",
        trend=12.5,
        format_type="currency",
        icon="fas fa-dollar-sign"
    )
    
    dashboard.add_kpi_card(
        title="Total Orders",
        value=int(total_orders),
        subtitle="Order Volume", 
        trend=8.3,
        format_type="number",
        icon="fas fa-shopping-cart"
    )
    
    dashboard.add_kpi_card(
        title="Products",
        value=len(products),
        subtitle="Active Products",
        trend=0.0,
        format_type="number", 
        icon="fas fa-box"
    )
    
    dashboard.add_kpi_card(
        title="Regions",
        value=len(regions),
        subtitle="Global Markets",
        trend=5.2,
        format_type="number",
        icon="fas fa-globe"
    )
    
    # Add filters
    dashboard.add_filter(
        filter_id="date_range",
        label="Date Range",
        filter_type="daterange",
        target_components=["sales_trend", "orders_chart"]
    )
    
    dashboard.add_filter(
        filter_id="category_filter", 
        label="Product Category",
        filter_type="select",
        options=[
            {"label": "All Categories", "value": "all"},
            {"label": "Electronics", "value": "electronics"},
            {"label": "Computers", "value": "computers"},
            {"label": "Accessories", "value": "accessories"}
        ],
        default_value="all",
        target_components=["product_sales"]
    )
    
    # Add charts
    
    # Time series chart
    dashboard.add_chart(
        chart_type="time_series",
        data=time_series,
        chart_id="sales_trend",
        title="Revenue Trend",
        x="date",
        y="sales", 
        height=400,
        width_class="col-12 col-lg-8"
    )
    
    # Gauge chart - need to handle this specially
    avg_rating = products['rating'].mean()
    dashboard.add_chart(
        chart_type="gauge_chart",
        data=pd.DataFrame(),
        chart_id="rating_gauge", 
        title="Avg Rating",
        value=avg_rating,
        min_val=0,
        max_val=5,
        height=400,
        width_class="col-12 col-lg-4"
    )
    
    # Bar chart
    top_products = products.nlargest(5, 'sales')
    dashboard.add_chart(
        chart_type="bar_chart",
        data=top_products,
        chart_id="product_sales",
        title="Top Products",
        x="sales", 
        y="product",
        orientation="h",
        height=400,
        width_class="col-12 col-lg-6"
    )  
    
    # Scatter plot
    dashboard.add_chart(
        chart_type="scatter_plot",
        data=products,
        chart_id="sales_vs_rating",
        title="Sales vs Rating",
        x="rating",
        y="sales",
        size="units_sold",
        color="category",
        height=400,
        width_class="col-12 col-lg-6"
    )
    
    # Pie chart
    dashboard.add_chart(
        chart_type="pie_chart",
        data=regions,
        chart_id="regional_revenue",
        title="Revenue by Region",
        names="region",
        values="revenue",
        height=400,
        width_class="col-12 col-lg-6"
    )
    
    # Heatmap
    dashboard.add_chart(
        chart_type="heatmap",
        data=correlations,
        chart_id="correlations",
        title="Metric Correlations", 
        height=400,
        width_class="col-12 col-lg-6"
    )
    
    # Add data tables
    dashboard.add_data_table(
        data=products.round(2),
        table_id="products_table",
        title="Product Details",
        searchable=True,
        sortable=True,
        paginated=True,
        page_size=10,
        width_class="col-12 col-lg-8"
    )
    
    dashboard.add_data_table(
        data=regions.round(0),
        table_id="regions_table", 
        title="Regional Summary",
        searchable=False,
        sortable=True,
        paginated=False,
        width_class="col-12 col-lg-4"
    )
    
    return dashboard

def main():
    """Main function"""
    
    print("=== Dashboard Generator Demo ===")
    print()
    
    try:
        dashboard = create_demo_dashboard()
        
        # Generate light theme
        print("Generating light theme dashboard...")
        light_output = "demo_dashboard_light.html"
        light_html = dashboard.generate_html(light_output)
        
        # Generate dark theme  
        print("Generating dark theme dashboard...")
        dashboard.set_theme('dark')
        dark_output = "demo_dashboard_dark.html"
        dark_html = dashboard.generate_html(dark_output)
        
        print()
        print("✅ Dashboard generation complete!")
        print(f"📄 Light theme: {light_output} ({len(light_html):,} chars)")
        print(f"📄 Dark theme: {dark_output} ({len(dark_html):,} chars)")
        print()
        print("Features included:")
        print("- 📊 6 different chart types")
        print("- 📈 4 KPI cards with trends") 
        print("- 🔍 2 interactive filters")
        print("- 📋 2 data tables")
        print("- 🎨 Light & dark themes")
        print("- 📱 Mobile responsive")
        print("- 💾 Offline capable")
        print("- 📤 Export functionality")
        print()
        print("🌐 Open the HTML files in your browser!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())