#!/usr/bin/env python3
"""
Comprehensive Example: DataScience Analytics Dashboard Generator

This script demonstrates all features of the dashboard generator:
- Multiple chart types (line, bar, scatter, pie, heatmap, gauge)
- KPI cards with trends
- Interactive data tables
- Filters and interactivity
- Responsive design
- Theme switching
- Export functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datascience_platform.dashboard.generator import DashboardGenerator

def generate_comprehensive_data():
    """Generate comprehensive sample data for all chart types"""
    
    # Time series data (daily sales over 6 months)
    dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
    time_series = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(5000, 1000, len(dates)) + 
                np.sin(np.arange(len(dates)) * 2 * np.pi / 30) * 500,  # Monthly seasonality
        'orders': np.random.poisson(50, len(dates)),
        'visitors': np.random.normal(2000, 400, len(dates)),
        'conversion_rate': np.random.beta(2, 50, len(dates))  # Realistic conversion rates
    })
    time_series['sales'] = time_series['sales'].clip(lower=0)
    time_series['visitors'] = time_series['visitors'].clip(lower=0).astype(int)
    time_series['revenue_per_visitor'] = time_series['sales'] / time_series['visitors']
    
    # Product performance data
    products = [
        'Premium Laptop', 'Gaming Mouse', 'Wireless Headphones', 
        'Smart Watch', 'Tablet Pro', 'Bluetooth Speaker',
        'USB Drive', 'Webcam HD', 'Keyboard Mechanical'
    ]
    product_data = pd.DataFrame({
        'product': products,
        'sales': np.random.uniform(50000, 200000, len(products)),
        'units_sold': np.random.randint(100, 2000, len(products)),
        'profit_margin': np.random.uniform(0.15, 0.45, len(products)),
        'customer_rating': np.random.uniform(3.2, 4.9, len(products)),
        'return_rate': np.random.uniform(0.02, 0.15, len(products)),
        'category': np.random.choice(['Electronics', 'Computers', 'Accessories'], len(products))
    })
    product_data['avg_price'] = product_data['sales'] / product_data['units_sold']
    product_data['profit'] = product_data['sales'] * product_data['profit_margin']
    
    # Regional performance data
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa']
    regional_data = pd.DataFrame({
        'region': regions,
        'revenue': np.random.uniform(500000, 2000000, len(regions)),
        'customers': np.random.randint(5000, 25000, len(regions)),
        'growth_rate': np.random.uniform(-0.05, 0.25, len(regions)),
        'market_share': np.random.uniform(0.1, 0.4, len(regions)),
        'satisfaction_score': np.random.uniform(3.5, 4.8, len(regions))
    })
    regional_data['revenue_per_customer'] = regional_data['revenue'] / regional_data['customers']
    
    # Customer segments
    segments = ['Enterprise', 'SMB', 'Individual Pro', 'Student', 'Hobbyist']
    segment_data = pd.DataFrame({
        'segment': segments,
        'customers': np.random.randint(1000, 15000, len(segments)),
        'avg_order_value': np.random.uniform(200, 1200, len(segments)),
        'lifetime_value': np.random.uniform(800, 5000, len(segments)),
        'churn_rate': np.random.uniform(0.05, 0.25, len(segments)),
        'acquisition_cost': np.random.uniform(50, 300, len(segments))
    })
    
    # Marketing channels performance
    channels = ['Google Ads', 'Facebook', 'Email', 'Organic Search', 'Direct', 'Referral']
    marketing_data = pd.DataFrame({
        'channel': channels,
        'spend': np.random.uniform(10000, 100000, len(channels)),
        'impressions': np.random.randint(100000, 2000000, len(channels)),
        'clicks': np.random.randint(5000, 50000, len(channels)),
        'conversions': np.random.randint(100, 2000, len(channels)),
        'revenue': np.random.uniform(50000, 500000, len(channels))
    })
    marketing_data['ctr'] = marketing_data['clicks'] / marketing_data['impressions']
    marketing_data['conversion_rate'] = marketing_data['conversions'] / marketing_data['clicks']
    marketing_data['roas'] = marketing_data['revenue'] / marketing_data['spend']  # Return on Ad Spend
    marketing_data['cpc'] = marketing_data['spend'] / marketing_data['clicks']  # Cost per Click
    
    # Correlation matrix for business metrics
    metrics = ['Sales', 'Marketing Spend', 'Customer Satisfaction', 'Product Quality', 'Support Response Time']
    correlation_matrix = pd.DataFrame(
        np.random.uniform(-0.8, 0.8, (len(metrics), len(metrics))),
        index=metrics,
        columns=metrics
    )
    # Make it symmetric and set diagonal to 1
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix.values, 1.0)
    
    return {
        'time_series': time_series,
        'products': product_data,
        'regions': regional_data,
        'segments': segment_data,
        'marketing': marketing_data,
        'correlations': correlation_matrix
    }

def create_comprehensive_dashboard():
    """Create a comprehensive dashboard showcasing all features"""
    
    print("🔄 Generating comprehensive sample data...")
    data = generate_comprehensive_data()
    
    print("🎨 Creating comprehensive dashboard...")
    
    # Initialize dashboard with dark theme and compression
    dashboard = DashboardGenerator(theme='light', compress=True)
    
    # Configure dashboard
    dashboard.set_config(
        title="📊 E-Commerce Analytics Dashboard",
        description="Comprehensive business intelligence dashboard with real-time insights",
        export_enabled=True,
        theme_switcher=True
    )
    
    # Calculate KPI values
    total_revenue = data['time_series']['sales'].sum()
    total_orders = data['time_series']['orders'].sum()
    avg_conversion = data['time_series']['conversion_rate'].mean()
    revenue_growth = ((data['time_series']['sales'].tail(30).mean() / 
                      data['time_series']['sales'].head(30).mean()) - 1) * 100
    
    # Add KPI Cards
    print("📈 Adding KPI cards...")
    dashboard.add_kpi_card(
        title="Total Revenue",
        value=total_revenue,
        subtitle="Last 6 Months",
        trend=revenue_growth,
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
        title="Conversion Rate",
        value=avg_conversion * 100,
        subtitle="Average Rate",
        trend=-1.2,
        format_type="percentage",
        icon="fas fa-chart-line"
    )
    
    dashboard.add_kpi_card(
        title="Product Categories",
        value=len(data['products']['category'].unique()),
        subtitle="Active Categories",
        trend=0.0,
        format_type="number",
        icon="fas fa-tags"
    )
    
    # Add Filters
    print("🔍 Adding interactive filters...")
    dashboard.add_filter(
        filter_id="date_range",
        label="Date Range",
        filter_type="daterange",
        target_components=["revenue_trend", "orders_chart"]
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
        target_components=["product_performance", "profit_analysis"]
    )
    
    dashboard.add_filter(
        filter_id="revenue_threshold",
        label="Min Revenue Threshold ($)",
        filter_type="slider",
        options=[
            {"label": "$0", "value": 0},
            {"label": "$500K", "value": 500000}
        ],
        default_value=100000,
        target_components=["regional_performance"]
    )
    
    # Add Charts
    print("📊 Adding interactive charts...")
    
    # 1. Revenue Trend (Time Series)
    dashboard.add_chart(
        chart_type="time_series",
        data=data['time_series'],
        chart_id="revenue_trend",
        title="📈 Revenue Trend Over Time",
        x="date",
        y="sales",
        range_selector=True,
        height=450,
        width_class="col-12 col-xl-8"
    )
    
    # 2. Conversion Rate Gauge
    dashboard.add_chart(
        chart_type="gauge_chart",
        data=pd.DataFrame(),  # Dummy data
        chart_id="conversion_gauge",
        title="🎯 Conversion Rate",
        value=avg_conversion * 100,
        min_val=0,
        max_val=8,
        height=450,
        width_class="col-12 col-xl-4"
    )
    
    # 3. Product Performance (Horizontal Bar)
    top_products = data['products'].nlargest(8, 'sales')\n    dashboard.add_chart(\n        chart_type=\"bar_chart\",\n        data=top_products,\n        chart_id=\"product_performance\",\n        title=\"🏆 Top Products by Sales\",\n        x=\"sales\",\n        y=\"product\",\n        orientation=\"h\",\n        height=500,\n        width_class=\"col-12 col-lg-6\"\n    )\n    \n    # 4. Profit vs Rating Scatter Plot\n    dashboard.add_chart(\n        chart_type=\"scatter_plot\",\n        data=data['products'],\n        chart_id=\"profit_analysis\",\n        title=\"💰 Profit vs Customer Rating\",\n        x=\"customer_rating\",\n        y=\"profit_margin\",\n        size=\"units_sold\",\n        color=\"category\",\n        height=500,\n        width_class=\"col-12 col-lg-6\"\n    )\n    \n    # 5. Regional Revenue (Pie Chart)\n    dashboard.add_chart(\n        chart_type=\"pie_chart\",\n        data=data['regions'],\n        chart_id=\"regional_revenue\",\n        title=\"🌍 Revenue by Region\",\n        names=\"region\",\n        values=\"revenue\",\n        height=450,\n        width_class=\"col-12 col-lg-6\"\n    )\n    \n    # 6. Marketing Channel Performance\n    dashboard.add_chart(\n        chart_type=\"bar_chart\",\n        data=data['marketing'].sort_values('roas', ascending=False),\n        chart_id=\"marketing_roas\",\n        title=\"📢 Marketing ROAS by Channel\",\n        x=\"channel\",\n        y=\"roas\",\n        height=450,\n        width_class=\"col-12 col-lg-6\"\n    )\n    \n    # 7. Business Metrics Correlation Heatmap\n    dashboard.add_chart(\n        chart_type=\"heatmap\",\n        data=data['correlations'],\n        chart_id=\"metrics_correlation\",\n        title=\"🔗 Business Metrics Correlation\",\n        height=500,\n        width_class=\"col-12 col-lg-8\"\n    )\n    \n    # 8. Customer Segments Distribution\n    dashboard.add_chart(\n        chart_type=\"distribution_plot\",\n        data=data['segments'],\n        chart_id=\"customer_distribution\",\n        title=\"👥 Customer Segments\",\n        column=\"lifetime_value\",\n        plot_type=\"histogram\",\n        height=500,\n        width_class=\"col-12 col-lg-4\"\n    )\n    \n    # Add Data Tables\n    print(\"📋 Adding data tables...\")\n    \n    # Product Performance Table\n    dashboard.add_data_table(\n        data=data['products'].round(2),\n        table_id=\"products_table\",\n        title=\"📦 Product Performance Details\",\n        searchable=True,\n        sortable=True,\n        paginated=True,\n        page_size=10,\n        width_class=\"col-12 col-xl-8\"\n    )\n    \n    # Marketing Performance Summary\n    marketing_summary = data['marketing'][['channel', 'spend', 'conversions', 'roas', 'cpc']].round(2)\n    dashboard.add_data_table(\n        data=marketing_summary,\n        table_id=\"marketing_table\",\n        title=\"📊 Marketing Performance Summary\",\n        searchable=False,\n        sortable=True,\n        paginated=False,\n        width_class=\"col-12 col-xl-4\"\n    )\n    \n    # Regional Performance Table\n    dashboard.add_data_table(\n        data=data['regions'].round(2),\n        table_id=\"regions_table\",\n        title=\"🌎 Regional Performance Overview\",\n        searchable=True,\n        sortable=True,\n        paginated=False,\n        width_class=\"col-12\"\n    )\n    \n    return dashboard\n\ndef main():\n    \"\"\"Main function to generate comprehensive dashboard\"\"\"\n    \n    print(\"🚀 === DataScience Analytics Dashboard Generator - Comprehensive Demo ===\")\n    print()\n    \n    try:\n        # Create comprehensive dashboard\n        dashboard = create_comprehensive_dashboard()\n        \n        # Generate both light and dark theme versions\n        print(\"🌞 Generating light theme dashboard...\")\n        light_output = \"comprehensive_dashboard_light.html\"\n        light_html = dashboard.generate_html(light_output)\n        \n        print(\"🌙 Generating dark theme dashboard...\")\n        dashboard.set_theme('dark')\n        dark_output = \"comprehensive_dashboard_dark.html\"\n        dark_html = dashboard.generate_html(dark_output)\n        \n        print(\"\\n✅ === Dashboard Generation Complete! ===\")\n        print(f\"📄 Light theme: {light_output} ({len(light_html):,} chars)\")\n        print(f\"📄 Dark theme: {dark_output} ({len(dark_html):,} chars)\")\n        print()\n        print(\"🎯 Dashboard Features Demonstrated:\")\n        print(\"   📊 8 Different chart types (line, bar, scatter, pie, heatmap, gauge, distribution)\")\n        print(\"   📈 4 KPI cards with trend indicators\")\n        print(\"   🔍 3 Interactive filters (date range, dropdown, slider)\")\n        print(\"   📋 3 Data tables with search/sort/pagination\")\n        print(\"   🎨 Light & dark theme support\")\n        print(\"   📱 Fully responsive mobile design\")\n        print(\"   💾 Offline-capable (all data embedded)\")\n        print(\"   📤 Export functionality (PDF/PNG)\")\n        print(\"   ⌨️  Keyboard shortcuts (Ctrl+D, Ctrl+E)\")\n        print(\"   🗜️  Data compression enabled\")\n        print()\n        print(f\"🌐 Open the HTML files in your browser to explore the interactive dashboard!\")\n        \n    except Exception as e:\n        print(f\"❌ Error generating dashboard: {e}\")\n        import traceback\n        traceback.print_exc()\n        return 1\n    \n    return 0\n\nif __name__ == \"__main__\":\n    exit(main())