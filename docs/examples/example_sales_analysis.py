#!/usr/bin/env python3
"""
Sales Data Analysis Example

This example demonstrates how to use the DataScience Analytics Platform
to analyze sales data, including:
- Reading and validating sales data
- Performing data quality checks
- Generating sales insights and visualizations
- Creating summary reports

Dataset: Sales transactions with products, customers, and regional data
"""

import sys
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import polars as pl

# Add the package to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from datascience_platform.etl import (
    DataReader, ReadOptions, DataValidator, DataTransformer,
    DataSchema, ColumnSchema, schema_registry
)
from datascience_platform.core.exceptions import DataSciencePlatformError


def create_sales_schema() -> DataSchema:
    """Create and return the sales data schema."""
    schema = DataSchema(
        name="sales_data",
        version="1.0.0",
        description="Sales transaction data schema",
        columns=[
            ColumnSchema(
                name="transaction_id",
                dtype="str",
                nullable=False,
                unique=True,
                description="Unique transaction identifier"
            ),
            ColumnSchema(
                name="date",
                dtype="datetime",
                nullable=False,
                description="Transaction date"
            ),
            ColumnSchema(
                name="product_name",
                dtype="str",
                nullable=False,
                description="Product name"
            ),
            ColumnSchema(
                name="product_category",
                dtype="str",
                nullable=False,
                allowed_values=["Electronics", "Clothing", "Home & Garden", "Sports", "Books"],
                description="Product category"
            ),
            ColumnSchema(
                name="unit_price",
                dtype="float64",
                nullable=False,
                min_value=0.01,
                max_value=10000.0,
                description="Price per unit"
            ),
            ColumnSchema(
                name="quantity",
                dtype="int64",
                nullable=False,
                min_value=1,
                max_value=1000,
                description="Quantity sold"
            ),
            ColumnSchema(
                name="total_amount",
                dtype="float64",
                nullable=False,
                min_value=0.01,
                description="Total transaction amount"
            ),
            ColumnSchema(
                name="customer_id",
                dtype="str",
                nullable=False,
                description="Customer identifier"
            ),
            ColumnSchema(
                name="customer_segment",
                dtype="str",
                nullable=False,
                allowed_values=["Premium", "Standard", "Basic"],
                description="Customer segment"
            ),
            ColumnSchema(
                name="sales_rep",
                dtype="str",
                nullable=True,
                description="Sales representative"
            ),
            ColumnSchema(
                name="region",
                dtype="str",
                nullable=False,
                allowed_values=["North", "South", "East", "West", "Central"],
                description="Sales region"
            ),
            ColumnSchema(
                name="discount_percent",
                dtype="float64",
                nullable=True,
                min_value=0.0,
                max_value=50.0,
                description="Discount percentage applied"
            )
        ],
        primary_key=["transaction_id"],
        indexes=["date", "customer_id", "product_category", "region"]
    )
    return schema


def analyze_sales_performance(df: pl.DataFrame) -> Dict[str, Any]:
    """Analyze sales performance metrics."""
    print("\n" + "="*50)
    print("SALES PERFORMANCE ANALYSIS")
    print("="*50)
    
    # Basic metrics
    total_revenue = df.select(pl.col("total_amount").sum()).item()
    total_transactions = len(df)
    avg_transaction_value = df.select(pl.col("total_amount").mean()).item()
    unique_customers = df.select(pl.col("customer_id").n_unique()).item()
    
    print(f"\n📊 Key Metrics:")
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    print(f"   Total Transactions: {total_transactions:,}")
    print(f"   Average Transaction Value: ${avg_transaction_value:.2f}")
    print(f"   Unique Customers: {unique_customers:,}")
    
    # Top products
    print(f"\n🏆 Top 5 Products by Revenue:")
    top_products = (
        df.group_by("product_name")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("quantity").sum().alias("units_sold")
        ])
        .sort("revenue", descending=True)
        .head(5)
    )
    
    for i, row in enumerate(top_products.iter_rows(named=True), 1):
        print(f"   {i}. {row['product_name']}: ${row['revenue']:,.2f} ({row['units_sold']} units)")
    
    # Regional performance
    print(f"\n🌍 Regional Performance:")
    regional_sales = (
        df.group_by("region")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("transaction_id").count().alias("transactions")
        ])
        .sort("revenue", descending=True)
    )
    
    for row in regional_sales.iter_rows(named=True):
        print(f"   {row['region']}: ${row['revenue']:,.2f} ({row['transactions']} transactions)")
    
    # Customer segment analysis
    print(f"\n👥 Customer Segment Analysis:")
    segment_analysis = (
        df.group_by("customer_segment")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("total_amount").mean().alias("avg_transaction"),
            pl.col("customer_id").n_unique().alias("unique_customers")
        ])
        .sort("revenue", descending=True)
    )
    
    for row in segment_analysis.iter_rows(named=True):
        print(f"   {row['customer_segment']}: ${row['revenue']:,.2f} revenue, "
              f"${row['avg_transaction']:.2f} avg transaction, "
              f"{row['unique_customers']} customers")
    
    return {
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "avg_transaction_value": avg_transaction_value,
        "unique_customers": unique_customers,
        "top_products": top_products.to_pandas(),
        "regional_sales": regional_sales.to_pandas(),
        "segment_analysis": segment_analysis.to_pandas()
    }


def analyze_trends(df: pl.DataFrame) -> Dict[str, Any]:
    """Analyze sales trends over time."""
    print("\n" + "="*50)
    print("SALES TRENDS ANALYSIS")
    print("="*50)
    
    # Monthly trends
    monthly_sales = (
        df.with_columns([
            pl.col("date").dt.strftime("%Y-%m").alias("month")
        ])
        .group_by("month")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("transaction_id").count().alias("transactions")
        ])
        .sort("month")
    )
    
    print(f"\n📈 Monthly Sales Trends:")
    for row in monthly_sales.iter_rows(named=True):
        print(f"   {row['month']}: ${row['revenue']:,.2f} ({row['transactions']} transactions)")
    
    # Category trends
    category_trends = (
        df.with_columns([
            pl.col("date").dt.strftime("%Y-%m").alias("month")
        ])
        .group_by(["month", "product_category"])
        .agg([
            pl.col("total_amount").sum().alias("revenue")
        ])
        .sort(["month", "revenue"], descending=[False, True])
    )
    
    print(f"\n📊 Top Category by Month:")
    top_category_by_month = (
        category_trends
        .group_by("month")
        .agg([
            pl.col("product_category").first().alias("top_category"),
            pl.col("revenue").first().alias("top_revenue")
        ])
        .sort("month")
    )
    
    for row in top_category_by_month.iter_rows(named=True):
        print(f"   {row['month']}: {row['top_category']} (${row['top_revenue']:,.2f})")
    
    return {
        "monthly_sales": monthly_sales.to_pandas(),
        "category_trends": category_trends.to_pandas()
    }


def identify_insights(df: pl.DataFrame) -> None:
    """Identify key business insights from the data."""
    print("\n" + "="*50)
    print("KEY BUSINESS INSIGHTS")
    print("="*50)
    
    # High-value customers
    high_value_customers = (
        df.group_by("customer_id")
        .agg([
            pl.col("total_amount").sum().alias("total_spent"),
            pl.col("transaction_id").count().alias("transaction_count"),
            pl.col("total_amount").mean().alias("avg_transaction")
        ])
        .filter(pl.col("total_spent") > pl.col("total_spent").quantile(0.9))
        .sort("total_spent", descending=True)
        .head(10)
    )
    
    print(f"\n💰 Top 10 High-Value Customers:")
    for i, row in enumerate(high_value_customers.iter_rows(named=True), 1):
        print(f"   {i}. Customer {row['customer_id']}: ${row['total_spent']:,.2f} "
              f"({row['transaction_count']} transactions, avg: ${row['avg_transaction']:.2f})")
    
    # Discount analysis
    discount_impact = (
        df.filter(pl.col("discount_percent").is_not_null())
        .group_by("discount_percent")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("quantity").sum().alias("units_sold"),
            pl.col("transaction_id").count().alias("transactions")
        ])
        .sort("discount_percent")
    )
    
    if len(discount_impact) > 0:
        print(f"\n🏷️ Discount Impact Analysis:")
        for row in discount_impact.iter_rows(named=True):
            print(f"   {row['discount_percent']:.0f}% discount: ${row['revenue']:,.2f} revenue, "
                  f"{row['units_sold']} units, {row['transactions']} transactions")
    
    # Seasonal patterns
    seasonal_analysis = (
        df.with_columns([
            pl.col("date").dt.quarter().alias("quarter"),
            pl.col("date").dt.month().alias("month")
        ])
        .group_by("quarter")
        .agg([
            pl.col("total_amount").sum().alias("revenue"),
            pl.col("transaction_id").count().alias("transactions")
        ])
        .sort("quarter")
    )
    
    print(f"\n🗓️ Quarterly Performance:")
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    for row in seasonal_analysis.iter_rows(named=True):
        quarter_name = quarters[int(row['quarter']) - 1]
        print(f"   {quarter_name}: ${row['revenue']:,.2f} ({row['transactions']} transactions)")


def main():
    """Main execution function."""
    print("🚀 Sales Data Analysis Example")
    print("Using DataScience Analytics Platform")
    print("-" * 50)
    
    try:
        # Create and register schema
        print("📋 Creating sales data schema...")
        sales_schema = create_sales_schema()
        schema_registry.register_schema(sales_schema)
        print(f"✅ Schema '{sales_schema.name}' registered with {len(sales_schema.columns)} columns")
        
        # Configure data reader
        options = ReadOptions(
            use_polars=True,
            parse_dates=['date'],
            encoding='utf-8'
        )
        reader = DataReader(options)
        
        # Check if sample data exists, if not create it
        data_file = Path(__file__).parent / "sample_sales_data.csv"
        if not data_file.exists():
            print("📁 Sample data not found. Creating sample dataset...")
            create_sample_sales_data(data_file)
        
        # Read sales data
        print(f"📖 Reading sales data from {data_file}...")
        df = reader.read(str(data_file))
        print(f"✅ Loaded {df.shape[0]} transactions with {df.shape[1]} columns")
        
        # Validate data
        print("🔍 Validating data quality...")
        validator = DataValidator(strict_mode=False)
        validation_result = validator.validate_with_schema(df, sales_schema)
        
        if validation_result.is_valid:
            print("✅ Data validation passed!")
        else:
            print("⚠️ Data validation issues found:")
            for error in validation_result.errors[:3]:
                print(f"   • {error}")
        
        if validation_result.has_warnings():
            print("📝 Validation warnings:")
            for warning in validation_result.warnings[:3]:
                print(f"   • {warning}")
        
        # Transform data if needed
        print("🔧 Cleaning and transforming data...")
        transformer = DataTransformer()
        cleaned_df, transform_report = transformer.transform_dataframe(df, schema=sales_schema)
        
        print(f"✅ Data transformation complete:")
        print(f"   Original rows: {transform_report.original_shape[0]}")
        print(f"   Final rows: {transform_report.final_shape[0]}")
        print(f"   Success rate: {transform_report.transformation_success_rate:.1%}")
        
        # Perform analysis
        performance_metrics = analyze_sales_performance(cleaned_df)
        trend_analysis = analyze_trends(cleaned_df)
        identify_insights(cleaned_df)
        
        # Save results
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save cleaned data
        cleaned_df.write_parquet(output_dir / "cleaned_sales_data.parquet")
        
        # Save analysis results as JSON
        import json
        analysis_results = {
            "performance_metrics": {
                "total_revenue": performance_metrics["total_revenue"],
                "total_transactions": performance_metrics["total_transactions"],
                "avg_transaction_value": performance_metrics["avg_transaction_value"],
                "unique_customers": performance_metrics["unique_customers"]
            },
            "validation_summary": {
                "is_valid": validation_result.is_valid,
                "error_count": len(validation_result.errors),
                "warning_count": len(validation_result.warnings)
            },
            "transformation_summary": {
                "original_shape": transform_report.original_shape,
                "final_shape": transform_report.final_shape,
                "success_rate": transform_report.transformation_success_rate
            }
        }
        
        with open(output_dir / "sales_analysis_results.json", "w") as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {output_dir}/")
        print("   • cleaned_sales_data.parquet")
        print("   • sales_analysis_results.json")
        
        print(f"\n🎉 Sales analysis complete!")
        print(f"   Total Revenue Analyzed: ${performance_metrics['total_revenue']:,.2f}")
        print(f"   Transactions Processed: {performance_metrics['total_transactions']:,}")
        
    except DataSciencePlatformError as e:
        print(f"❌ Platform error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def create_sample_sales_data(output_file: Path) -> None:
    """Create sample sales data for demonstration."""
    import random
    from datetime import datetime, timedelta
    
    print("🔨 Generating sample sales data...")
    
    # Sample data parameters
    num_transactions = 1000
    products = [
        ("Laptop Pro", "Electronics", 1299.99),
        ("Wireless Headphones", "Electronics", 199.99),
        ("Running Shoes", "Sports", 89.99),
        ("Yoga Mat", "Sports", 29.99),
        ("Coffee Maker", "Home & Garden", 79.99),
        ("Desk Chair", "Home & Garden", 249.99),
        ("Python Programming Book", "Books", 39.99),
        ("Data Science Handbook", "Books", 49.99),
        ("Winter Jacket", "Clothing", 129.99),
        ("Casual T-Shirt", "Clothing", 19.99)
    ]
    
    regions = ["North", "South", "East", "West", "Central"]
    segments = ["Premium", "Standard", "Basic"]
    sales_reps = ["Alice Johnson", "Bob Smith", "Carol Brown", "David Wilson", "Eva Davis"]
    
    # Generate data
    data = []
    start_date = datetime(2024, 1, 1)
    
    for i in range(num_transactions):
        product_name, category, base_price = random.choice(products)
        quantity = random.randint(1, 5)
        
        # Add some price variation
        price_variation = random.uniform(0.9, 1.1)
        unit_price = round(base_price * price_variation, 2)
        
        # Calculate discount
        discount = None
        if random.random() < 0.3:  # 30% chance of discount
            discount = random.choice([5.0, 10.0, 15.0, 20.0])
        
        # Calculate total
        subtotal = unit_price * quantity
        if discount:
            total_amount = round(subtotal * (1 - discount / 100), 2)
        else:
            total_amount = subtotal
        
        # Generate transaction
        transaction = {
            "transaction_id": f"TXN{i+1:06d}",
            "date": (start_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "product_name": product_name,
            "product_category": category,
            "unit_price": unit_price,
            "quantity": quantity,
            "total_amount": total_amount,
            "customer_id": f"CUST{random.randint(1, 200):04d}",
            "customer_segment": random.choice(segments),
            "sales_rep": random.choice(sales_reps) if random.random() < 0.8 else None,
            "region": random.choice(regions),
            "discount_percent": discount
        }
        
        data.append(transaction)
    
    # Save to CSV
    import csv
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Created sample data with {num_transactions} transactions at {output_file}")


if __name__ == "__main__":
    main()