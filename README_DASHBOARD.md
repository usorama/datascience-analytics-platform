# DataScience Analytics Platform - Dashboard Generator

A comprehensive HTML/JS/CSS dashboard generator that creates interactive, offline-capable analytics dashboards with modern responsive design.

## 🚀 Features

### Interactive Visualizations
- **8 Chart Types**: Line charts, bar charts, scatter plots, pie charts, heatmaps, gauge charts, distribution plots, and time series
- **Plotly Integration**: Fully interactive charts with zoom, pan, hover, and export capabilities
- **Responsive Design**: Charts automatically resize for different screen sizes

### Dashboard Components
- **KPI Cards**: Metric cards with trend indicators, icons, and different formatting options
- **Data Tables**: Sortable, searchable, paginated tables with DataTables integration
- **Interactive Filters**: Date ranges, dropdowns, sliders, and multi-select filters
- **Theme Support**: Light and dark themes with smooth transitions

### Modern Design
- **Bootstrap 5**: Modern, responsive grid system and components
- **Font Awesome**: Comprehensive icon library
- **CSS Grid/Flexbox**: Advanced layout capabilities
- **Mobile-First**: Optimized for mobile devices and tablets

### Offline Capabilities
- **Self-Contained**: Single HTML file with all dependencies embedded
- **Data Compression**: Optional gzip compression for embedded data
- **No External Dependencies**: Works completely offline

### Export & Sharing
- **PDF Export**: Generate PDF reports using html2canvas and jsPDF
- **PNG Export**: Export dashboard as high-resolution images
- **Chart Export**: Individual chart export functionality

## 📁 Project Structure

```
src/datascience_platform/dashboard/
├── __init__.py                 # Package initialization
├── generator.py               # Main dashboard generator class
├── charts.py                  # Plotly chart builders
├── templates/                 # Jinja2 HTML templates
│   ├── base.html             # Main dashboard template
│   └── components/           # Reusable components
│       ├── kpi_card.html     # KPI metric cards
│       ├── chart_container.html # Chart containers
│       ├── data_table.html   # Data table components
│       └── filters.html      # Filter components
└── static/                   # CSS and JavaScript assets
    ├── styles.css           # Modern CSS with theme support
    └── dashboard.js         # Interactive JavaScript functionality
```

## 🛠 Installation

### Requirements
```bash
pip install pandas numpy plotly jinja2
```

### Optional Dependencies
```bash
# For enhanced functionality
pip install scipy scikit-learn seaborn

# For development
pip install pytest pytest-cov black flake8 mypy
```

## 📖 Quick Start

### Basic Example

```python
from datascience_platform.dashboard import DashboardGenerator
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=100),
    'sales': np.random.normal(1000, 200, 100),
    'visitors': np.random.randint(400, 800, 100)
})

# Initialize dashboard
dashboard = DashboardGenerator(theme='light', compress=True)

# Configure dashboard
dashboard.set_config(
    title="My Analytics Dashboard",
    description="Sales and visitor analytics",
    export_enabled=True,
    theme_switcher=True
)

# Add KPI card
dashboard.add_kpi_card(
    title="Total Sales",
    value=data['sales'].sum(),
    trend=12.5,
    format_type="currency",
    icon="fas fa-dollar-sign"
)

# Add line chart
dashboard.add_chart(
    chart_type="line_chart",
    data=data,
    chart_id="sales_trend",
    title="Sales Over Time",
    x="date",
    y="sales"
)

# Add data table
dashboard.add_data_table(
    data=data,
    table_id="data_table",
    title="Raw Data",
    searchable=True,
    sortable=True
)

# Generate HTML
html_content = dashboard.generate_html("my_dashboard.html")
```

## 📊 Chart Types

### 1. Line Charts & Time Series
```python
dashboard.add_chart(
    chart_type="line_chart",
    data=df,
    chart_id="trend_chart",
    title="Revenue Trend",
    x="date",
    y="revenue",
    height=400
)

# Time series with range selector
dashboard.add_chart(
    chart_type="time_series", 
    data=df,
    chart_id="ts_chart",
    title="Time Series Analysis",
    x="date",
    y="value",
    range_selector=True
)
```

### 2. Bar Charts
```python
# Vertical bar chart
dashboard.add_chart(
    chart_type="bar_chart",
    data=df,
    chart_id="vertical_bars",
    title="Sales by Category",
    x="category",
    y="sales"
)

# Horizontal bar chart
dashboard.add_chart(
    chart_type="bar_chart",
    data=df,
    chart_id="horizontal_bars", 
    title="Top Products",
    x="sales",
    y="product",
    orientation="h"
)
```

### 3. Scatter Plots
```python
dashboard.add_chart(
    chart_type="scatter_plot",
    data=df,
    chart_id="scatter",
    title="Price vs Quality",
    x="price",
    y="quality_score",
    size="market_share",
    color="category"
)
```

### 4. Pie Charts
```python
dashboard.add_chart(
    chart_type="pie_chart",
    data=df,
    chart_id="market_share",
    title="Market Share",
    names="company",
    values="revenue"
)
```

### 5. Heatmaps
```python
# Correlation heatmap
correlation_matrix = df.corr()
dashboard.add_chart(
    chart_type="heatmap",
    data=correlation_matrix,
    chart_id="correlation",
    title="Feature Correlations"
)
```

### 6. Gauge Charts
```python
dashboard.add_chart(
    chart_type="gauge_chart",
    data=pd.DataFrame(),  # No data needed
    chart_id="performance",
    title="Performance Score",
    value=85.5,
    min_val=0,
    max_val=100
)
```

### 7. Distribution Plots
```python
# Histogram
dashboard.add_chart(
    chart_type="distribution_plot",
    data=df,
    chart_id="histogram",
    title="Sales Distribution",
    column="sales",
    plot_type="histogram"
)

# Box plot
dashboard.add_chart(
    chart_type="distribution_plot",
    data=df,
    chart_id="boxplot",
    title="Revenue Box Plot", 
    column="revenue",
    plot_type="box"
)
```

## 📈 KPI Cards

```python
# Currency format with trend
dashboard.add_kpi_card(
    title="Monthly Revenue",
    value=125000.50,
    subtitle="This Month",
    trend=8.5,  # 8.5% increase
    format_type="currency",
    icon="fas fa-dollar-sign"
)

# Percentage format
dashboard.add_kpi_card(
    title="Conversion Rate", 
    value=3.45,
    trend=-1.2,  # 1.2% decrease
    format_type="percentage",
    icon="fas fa-chart-line"
)

# Number format
dashboard.add_kpi_card(
    title="Active Users",
    value=12547,
    trend=15.3,
    format_type="number",
    icon="fas fa-users"
)
```

## 🔍 Interactive Filters

### Date Range Filter
```python
dashboard.add_filter(
    filter_id="date_range",
    label="Date Range",
    filter_type="daterange",
    target_components=["sales_chart", "revenue_table"]
)
```

### Dropdown Filter
```python
dashboard.add_filter(
    filter_id="category",
    label="Product Category",
    filter_type="select",
    options=[
        {"label": "All Categories", "value": "all"},
        {"label": "Electronics", "value": "electronics"},
        {"label": "Clothing", "value": "clothing"}
    ],
    default_value="all",
    target_components=["product_chart"]
)
```

### Slider Filter
```python
dashboard.add_filter(
    filter_id="price_range",
    label="Price Range",
    filter_type="slider", 
    options=[
        {"label": "$0", "value": 0},
        {"label": "$1000", "value": 1000}
    ],
    default_value=500,
    target_components=["price_chart"]
)
```

## 📋 Data Tables

```python
dashboard.add_data_table(
    data=df,
    table_id="sales_table",
    title="Sales Data",
    searchable=True,      # Enable search
    sortable=True,        # Enable column sorting
    paginated=True,       # Enable pagination
    page_size=25,         # Rows per page
    width_class="col-12"  # Full width
)
```

## 🎨 Theming

### Light Theme (Default)
```python
dashboard = DashboardGenerator(theme='light')
```

### Dark Theme
```python
dashboard = DashboardGenerator(theme='dark')
```

### Dynamic Theme Switching
```python
dashboard.set_config(theme_switcher=True)

# Users can toggle themes with:
# - Theme toggle button in navbar
# - Keyboard shortcut: Ctrl+D (Cmd+D on Mac)
```

## 💾 Data Management

### Data Compression
```python
# Enable compression for smaller file sizes
dashboard = DashboardGenerator(compress=True)
```

### Offline Capability
All data is embedded in the HTML file, making dashboards fully functional offline:
- Chart data is serialized and embedded
- All CSS and JavaScript is inlined
- External CDN resources are loaded but dashboard works without them

## 📤 Export Features

### Built-in Export Options
- **PDF Export**: Ctrl+E or export menu
- **PNG Export**: Export menu 
- **Individual Chart Export**: Chart action buttons

### Programmatic Export
```python
# Generate print-optimized version
pdf_html = dashboard.generate_pdf_export_html()

# Save as file
with open("dashboard_print.html", "w") as f:
    f.write(pdf_html)
```

## ⌨️ Keyboard Shortcuts

- **Ctrl+D / Cmd+D**: Toggle light/dark theme
- **Ctrl+E / Cmd+E**: Export dashboard as PDF
- **Escape**: Close fullscreen chart view

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 576px (1 column layout)
- **Tablet**: 576px - 768px (2 column layout)
- **Desktop**: 768px - 1200px (3-4 column layout)
- **Large Desktop**: > 1200px (4+ column layout)

### Grid Classes
```python
# Full width on mobile, half width on large screens
width_class="col-12 col-lg-6"

# Quarter width on extra large screens
width_class="col-12 col-xl-3"

# Custom responsive behavior
width_class="col-12 col-md-6 col-lg-4 col-xl-3"
```

## 🔧 Advanced Configuration

### Dashboard Config
```python
dashboard.set_config(
    title="Custom Dashboard",
    description="Dashboard description",
    favicon="path/to/favicon.ico",
    export_enabled=True,
    theme_switcher=True,
    responsive=True
)
```

### Chart Customization
```python
dashboard.add_chart(
    chart_type="line_chart",
    data=df,
    chart_id="custom_chart",
    title="Custom Chart",
    x="date",
    y="value",
    height=500,
    width_class="col-12",
    # Pass additional Plotly arguments
    line_shape="spline",
    markers=True,
    color_discrete_sequence=["#FF6B6B", "#4ECDC4"]
)
```

## 🚀 Performance Optimization

### Best Practices
1. **Data Size**: Keep datasets reasonable (< 10MB uncompressed)
2. **Chart Count**: Limit to ~20 charts per dashboard for best performance
3. **Compression**: Enable compression for large datasets
4. **Image Optimization**: Use appropriate chart heights (300-600px)

### File Size Management
```python
# Monitor dashboard size
html_content = dashboard.generate_html()
print(f"Dashboard size: {len(html_content):,} characters")

# Enable compression
dashboard = DashboardGenerator(compress=True)
```

## 🧪 Testing

Run the included examples:

```bash
# Simple test dashboard
python3 test_dashboard_simple.py

# Comprehensive demo dashboard  
python3 demo_dashboard.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**ImportError: No module named 'datascience_platform'**
```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/ds-package/src"
```

**Charts not displaying**
- Check that data columns exist
- Verify chart_type matches available methods
- Ensure data is not empty

**Large file sizes**
- Enable compression: `DashboardGenerator(compress=True)`
- Reduce data size or use sampling
- Limit chart count per dashboard

**Browser compatibility**
- Modern browsers required (Chrome 60+, Firefox 55+, Safari 12+)
- JavaScript must be enabled
- Use HTTPS for advanced features

### Performance Tips

1. **Optimize data before adding to dashboard**
2. **Use appropriate chart types for data size**
3. **Enable compression for production dashboards**
4. **Test on target devices and browsers**

---

Built with ❤️ for the DataScience Analytics Platform