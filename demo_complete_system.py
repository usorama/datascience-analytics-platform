#!/usr/bin/env python3
"""
Complete System Demo - DataScience Analytics Platform
This script demonstrates the entire platform working end-to-end
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Create sample data for demonstration
def create_sample_ecommerce_data():
    """Create realistic e-commerce data for demonstration"""
    print("📊 Creating sample e-commerce dataset...")
    
    np.random.seed(42)
    n_orders = 5000
    n_customers = 800
    n_products = 150
    
    # Generate dates over the last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, periods=n_orders)
    
    # Product categories and their price ranges
    categories = {
        'Electronics': (50, 2000),
        'Clothing': (20, 200),
        'Home & Garden': (15, 500),
        'Books': (10, 50),
        'Sports': (25, 300),
        'Beauty': (15, 150)
    }
    
    # Generate order data
    data = []
    for i in range(n_orders):
        category = np.random.choice(list(categories.keys()))
        price_range = categories[category]
        
        order = {
            'order_id': f'ORD{i+1:05d}',
            'date': dates[i],
            'customer_id': f'CUST{np.random.randint(1, n_customers):04d}',
            'product_id': f'PROD{np.random.randint(1, n_products):03d}',
            'category': category,
            'quantity': np.random.randint(1, 5),
            'unit_price': round(np.random.uniform(price_range[0], price_range[1]), 2),
            'discount_percent': np.random.choice([0, 5, 10, 15, 20], p=[0.5, 0.2, 0.15, 0.1, 0.05]),
            'shipping_cost': round(np.random.uniform(5, 25), 2),
            'region': np.random.choice(['North', 'South', 'East', 'West'], p=[0.3, 0.25, 0.25, 0.2]),
            'payment_method': np.random.choice(['Credit Card', 'PayPal', 'Debit Card', 'Bank Transfer'], 
                                             p=[0.4, 0.3, 0.2, 0.1])
        }
        
        # Calculate totals
        subtotal = order['quantity'] * order['unit_price']
        discount = subtotal * order['discount_percent'] / 100
        order['revenue'] = round(subtotal - discount + order['shipping_cost'], 2)
        
        # Add some seasonal patterns
        month = dates[i].month
        if month in [11, 12]:  # Holiday season
            order['quantity'] = min(order['quantity'] * 2, 10)
            order['revenue'] = round(order['revenue'] * 1.5, 2)
        
        data.append(order)
    
    df = pd.DataFrame(data)
    
    # Add some data quality issues for realistic testing
    # Add some missing values
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices, 'region'] = np.nan
    
    # Add some outliers
    outlier_indices = np.random.choice(df.index, size=20, replace=False)
    df.loc[outlier_indices, 'revenue'] = df.loc[outlier_indices, 'revenue'] * 10
    
    # Save to CSV
    filename = 'ecommerce_data.csv'
    df.to_csv(filename, index=False)
    print(f"✅ Created {filename} with {len(df):,} orders")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Categories: {', '.join(df['category'].unique())}")
    print(f"   Total revenue: ${df['revenue'].sum():,.2f}")
    
    return filename

def demonstrate_platform():
    """Demonstrate the complete platform functionality"""
    print("\n" + "="*60)
    print("🚀 DataScience Analytics Platform - Complete System Demo")
    print("="*60 + "\n")
    
    # Create sample data
    csv_file = create_sample_ecommerce_data()
    
    try:
        # Import our platform components
        print("\n📦 Importing DataScience Platform components...")
        from datascience_platform.etl.reader import DataReader
        from datascience_platform.etl.schema import SchemaDetector
        from datascience_platform.etl.validator import DataValidator
        from datascience_platform.etl.transformer import DataTransformer
        from datascience_platform.ml.insights import InsightGenerator
        from datascience_platform.dashboard.generator import DashboardGenerator
        from datascience_platform.core.orchestrator import PipelineOrchestrator, PipelineConfig
        
        print("✅ All components imported successfully!")
        
        # Method 1: Using the Pipeline Orchestrator (Recommended)
        print("\n" + "-"*60)
        print("📍 Method 1: Using Pipeline Orchestrator (Recommended)")
        print("-"*60)
        
        # Configure the pipeline
        config = PipelineConfig(
            validate_data=True,
            transform_data=True,
            generate_insights=True,
            create_dashboard=True,
            dashboard_config={
                'theme': 'light',
                'title': 'E-commerce Analytics Dashboard'
            }
        )
        
        # Create and run the pipeline
        print("\n🔄 Running complete analytics pipeline...")
        orchestrator = PipelineOrchestrator(config)
        
        # Define progress callback
        def progress_callback(stage, message, progress):
            print(f"   [{progress:3.0%}] {stage}: {message}")
        
        # Run the pipeline
        result = orchestrator.run(csv_file, progress_callback=progress_callback)
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"   Execution time: {result.execution_time:.2f} seconds")
        print(f"   Rows processed: {result.row_count:,}")
        print(f"   Columns analyzed: {result.column_count}")
        
        # Display insights
        if result.insights:
            print("\n💡 Key Insights Generated:")
            insights = result.insights[:5]  # Show top 5 insights
            for i, insight in enumerate(insights, 1):
                if isinstance(insight, dict):
                    print(f"   {i}. {insight.get('type', 'Unknown')}: {insight.get('description', 'N/A')}")
                else:
                    print(f"   {i}. {insight}")
        
        # Method 2: Using Components Individually
        print("\n" + "-"*60)
        print("📍 Method 2: Using Individual Components")
        print("-"*60)
        
        # Step 1: Read and detect schema
        print("\n1️⃣ Reading CSV and detecting schema...")
        reader = DataReader()
        df = reader.read(csv_file)
        
        schema_detector = SchemaDetector()
        schema = schema_detector.detect_schema(df)
        print(f"   ✅ Detected {len(schema['columns'])} columns")
        print(f"   ✅ Data quality score: {schema.get('quality_score', 0):.1%}")
        
        # Step 2: Validate data
        print("\n2️⃣ Validating data quality...")
        validator = DataValidator()
        validation_report = validator.validate(df, schema)
        print(f"   ✅ Validation complete: {validation_report.get('status', 'Unknown')}")
        if 'summary' in validation_report:
            summary = validation_report['summary']
            print(f"   📊 Total issues: {summary.get('total_issues', 0)}")
        
        # Step 3: Transform data
        print("\n3️⃣ Transforming and cleaning data...")
        transformer = DataTransformer()
        transformed_df, transform_report = transformer.transform(df)
        print(f"   ✅ Transformation complete")
        print(f"   📊 Rows after cleaning: {len(transformed_df):,}")
        
        # Step 4: Generate insights
        print("\n4️⃣ Generating ML-powered insights...")
        insight_gen = InsightGenerator()
        insights = insight_gen.generate_insights(transformed_df, target_column='revenue')
        print(f"   ✅ Generated {len(insights)} insights")
        
        # Step 5: Create dashboard
        print("\n5️⃣ Creating interactive dashboard...")
        dashboard_gen = DashboardGenerator()
        
        # Configure dashboard
        dashboard_gen.set_title("E-commerce Analytics Dashboard")
        dashboard_gen.set_theme("dark")
        
        # Add KPIs
        total_revenue = transformed_df['revenue'].sum()
        avg_order_value = transformed_df['revenue'].mean()
        total_orders = len(transformed_df)
        
        dashboard_gen.add_kpi("Total Revenue", f"${total_revenue:,.0f}", "trending_up", "#28a745")
        dashboard_gen.add_kpi("Average Order", f"${avg_order_value:.2f}", "shopping_cart", "#17a2b8")
        dashboard_gen.add_kpi("Total Orders", f"{total_orders:,}", "receipt", "#6c757d")
        
        # Add charts
        # Revenue over time
        revenue_by_date = transformed_df.groupby('date')['revenue'].sum().reset_index()
        dashboard_gen.add_chart(
            chart_type="line",
            data=revenue_by_date,
            x="date",
            y="revenue",
            title="Revenue Trend Over Time"
        )
        
        # Revenue by category
        revenue_by_category = transformed_df.groupby('category')['revenue'].sum().reset_index()
        dashboard_gen.add_chart(
            chart_type="bar",
            data=revenue_by_category,
            x="category",
            y="revenue",
            title="Revenue by Product Category"
        )
        
        # Generate dashboard
        dashboard_path = "ecommerce_dashboard.html"
        dashboard_gen.generate(dashboard_path)
        print(f"   ✅ Dashboard saved to: {dashboard_path}")
        
        # Method 3: Using CLI
        print("\n" + "-"*60)
        print("📍 Method 3: Command Line Interface Examples")
        print("-"*60)
        
        print("\n🖥️  CLI commands you can run:")
        print("   # Analyze data with CLI")
        print("   $ python -m datascience_platform analyze ecommerce_data.csv --target revenue")
        print()
        print("   # Start API server")
        print("   $ python -m datascience_platform server --port 8080")
        print()
        print("   # Get help")
        print("   $ python -m datascience_platform --help")
        
        # Summary
        print("\n" + "="*60)
        print("✨ Demo Complete! Summary:")
        print("="*60)
        print(f"\n📊 Data Processing:")
        print(f"   - Input file: {csv_file}")
        print(f"   - Rows processed: {len(df):,}")
        print(f"   - Data quality issues found and handled: ✅")
        print(f"   - Insights generated: {len(insights)}")
        
        print(f"\n📈 Output Files:")
        print(f"   - Dashboard: {dashboard_path}")
        if 'outputs' in result.__dict__:
            for output in result.outputs:
                print(f"   - {output}")
        
        print(f"\n🚀 Platform Capabilities Demonstrated:")
        print(f"   ✅ High-performance CSV processing with Polars")
        print(f"   ✅ Automatic schema detection and validation")
        print(f"   ✅ Data quality assessment and cleaning")
        print(f"   ✅ ML-powered insight generation")
        print(f"   ✅ Interactive dashboard creation")
        print(f"   ✅ Multiple usage methods (API, CLI, Python)")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Open {dashboard_path} in your browser")
        print(f"   2. Try the CLI commands shown above")
        print(f"   3. Explore the Python API in a Jupyter notebook")
        print(f"   4. Check the /docs folder for detailed documentation")
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n📝 Make sure you have installed the package:")
        print("   $ pip install -e .")
        print("\n📦 Or install dependencies:")
        print("   $ pip install -r requirements.txt")
    
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("\n🔍 Check the following:")
        print("   1. All dependencies are installed")
        print("   2. You're in the correct directory")
        print("   3. The package is properly installed")
    
    finally:
        print("\n" + "="*60)
        print("Thank you for trying the DataScience Analytics Platform!")
        print("="*60 + "\n")

if __name__ == "__main__":
    demonstrate_platform()