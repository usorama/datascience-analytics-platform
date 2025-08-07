#!/usr/bin/env python3
"""
Simple Demo - DataScience Analytics Platform
This demonstrates the platform using the actual implemented components
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*60)
print("🚀 DataScience Analytics Platform - Simple Demo")
print("="*60)

# Create sample data
print("\n📊 Creating sample sales data...")
np.random.seed(42)
n_records = 1000

dates = pd.date_range(start='2024-01-01', end='2024-12-31', periods=n_records)
categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home']
regions = ['North', 'South', 'East', 'West']

data = {
    'date': dates,
    'product_id': [f'PROD{i:04d}' for i in np.random.randint(1, 100, n_records)],
    'category': np.random.choice(categories, n_records),
    'region': np.random.choice(regions, n_records),
    'quantity': np.random.randint(1, 10, n_records),
    'price': np.round(np.random.uniform(10, 500, n_records), 2),
    'revenue': np.round(np.random.uniform(50, 5000, n_records), 2)
}

df = pd.DataFrame(data)
csv_file = 'sample_sales_data.csv'
df.to_csv(csv_file, index=False)
print(f"✅ Created {csv_file} with {len(df):,} records")

try:
    # Import what we actually have
    print("\n📦 Importing platform components...")
    from datascience_platform.etl.reader import DataReader
    from datascience_platform.etl.validator import DataValidator
    from datascience_platform.etl.transformer import DataTransformer
    
    # Try to import ML components if they exist
    try:
        from datascience_platform.ml.statistics import StatisticalAnalyzer
        from datascience_platform.ml.insights import InsightGenerator
        ml_available = True
    except ImportError:
        print("⚠️  ML components not found, skipping ML analysis")
        ml_available = False
    
    # Try to import dashboard generator
    try:
        from datascience_platform.dashboard.generator import DashboardGenerator
        dashboard_available = True
    except ImportError:
        print("⚠️  Dashboard generator not found, skipping dashboard creation")
        dashboard_available = False
    
    print("✅ Core components imported successfully!")
    
    # Step 1: Read data
    print("\n1️⃣ Reading CSV file...")
    reader = DataReader()
    df_result = reader.read(csv_file)
    print(f"   ✅ Loaded {len(df_result)} rows, {len(df_result.columns)} columns")
    
    # Step 2: Validate data
    print("\n2️⃣ Validating data...")
    validator = DataValidator()
    # Simple validation without schema
    validation_result = validator.validate(df_result)
    print(f"   ✅ Validation complete")
    
    # Step 3: Transform data
    print("\n3️⃣ Transforming data...")
    transformer = DataTransformer()
    transformed_df, transform_report = transformer.transform(df_result)
    print(f"   ✅ Transformation complete")
    print(f"   📊 Final shape: {transformed_df.shape}")
    
    # Step 4: Statistical Analysis (if available)
    if ml_available:
        print("\n4️⃣ Running statistical analysis...")
        analyzer = StatisticalAnalyzer()
        stats = analyzer.analyze(transformed_df)
        print(f"   ✅ Generated statistics for all columns")
        
        # Generate insights
        print("\n5️⃣ Generating insights...")
        insight_gen = InsightGenerator()
        insights = insight_gen.generate_insights(transformed_df, target_column='revenue')
        print(f"   ✅ Generated {len(insights)} insights")
        
        # Show top insights
        print("\n💡 Top Insights:")
        for i, insight in enumerate(insights[:3], 1):
            if isinstance(insight, dict):
                print(f"   {i}. {insight.get('description', insight)}")
            else:
                print(f"   {i}. {insight}")
    
    # Step 5: Create Dashboard (if available)
    if dashboard_available:
        print("\n6️⃣ Creating dashboard...")
        dashboard = DashboardGenerator()
        
        # Set basic properties
        dashboard.set_title("Sales Analytics Dashboard")
        dashboard.set_theme("light")
        
        # Add some KPIs
        total_revenue = float(transformed_df['revenue'].sum())
        avg_revenue = float(transformed_df['revenue'].mean())
        
        dashboard.add_kpi("Total Revenue", f"${total_revenue:,.0f}", "trending_up")
        dashboard.add_kpi("Average Sale", f"${avg_revenue:.2f}", "shopping_cart")
        
        # Add a simple chart
        # Group by category
        if hasattr(transformed_df, 'to_pandas'):
            chart_df = transformed_df.to_pandas()
        else:
            chart_df = transformed_df
            
        category_revenue = chart_df.groupby('category')['revenue'].sum().reset_index()
        
        dashboard.add_chart(
            chart_type="bar",
            data=category_revenue,
            x="category",
            y="revenue",
            title="Revenue by Category"
        )
        
        # Generate dashboard
        dashboard_file = "simple_dashboard.html"
        dashboard.generate(dashboard_file)
        print(f"   ✅ Dashboard saved to: {dashboard_file}")
    
    print("\n" + "="*60)
    print("✨ Demo Complete!")
    print("="*60)
    
    print("\n📋 Summary:")
    print(f"   - Data loaded: ✅")
    print(f"   - Data validated: ✅")
    print(f"   - Data transformed: ✅")
    if ml_available:
        print(f"   - ML analysis: ✅")
    if dashboard_available:
        print(f"   - Dashboard created: ✅")
    
    print("\n🎯 The DataScience Analytics Platform successfully processed your data!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n🔍 This might be due to:")
    print("   1. Missing dependencies - run: pip install -r requirements.txt")
    print("   2. Import path issues - ensure you're in the project directory")
    print("   3. Missing components - some modules might not be implemented yet")
    
    import traceback
    print("\n🐛 Full error trace:")
    traceback.print_exc()

print("\n")