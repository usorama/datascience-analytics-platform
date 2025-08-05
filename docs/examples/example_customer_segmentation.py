#!/usr/bin/env python3
"""
Customer Segmentation Example

This example demonstrates advanced analytics using the DataScience Analytics Platform
for customer segmentation, including:
- Customer behavior analysis
- RFM (Recency, Frequency, Monetary) analysis
- Customer lifetime value calculation
- Segmentation using clustering algorithms
- Actionable insights for marketing strategies

Dataset: Customer transaction data with demographic and behavioral features
"""

import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import polars as pl
import numpy as np
from datetime import datetime, timedelta

# Add the package to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from datascience_platform.etl import (
    DataReader, ReadOptions, DataValidator, DataTransformer,
    DataSchema, ColumnSchema, schema_registry
)
from datascience_platform.core.exceptions import DataSciencePlatformError


def create_customer_schema() -> DataSchema:
    """Create and return the customer data schema."""
    schema = DataSchema(
        name="customer_transaction_data",
        version="1.0.0",
        description="Customer transaction data for segmentation analysis",
        columns=[
            ColumnSchema(
                name="customer_id",
                dtype="str",
                nullable=False,
                description="Unique customer identifier"
            ),
            ColumnSchema(
                name="transaction_date",
                dtype="datetime",
                nullable=False,
                description="Date of transaction"
            ),
            ColumnSchema(
                name="transaction_amount",
                dtype="float64",
                nullable=False,
                min_value=0.01,
                description="Transaction amount"
            ),
            ColumnSchema(
                name="product_category",
                dtype="str",
                nullable=False,
                description="Product category purchased"
            ),
            ColumnSchema(
                name="customer_age",
                dtype="int64",
                nullable=True,
                min_value=18,
                max_value=100,
                description="Customer age"
            ),
            ColumnSchema(
                name="customer_gender",
                dtype="str",
                nullable=True,
                allowed_values=["M", "F", "Other"],
                description="Customer gender"
            ),
            ColumnSchema(
                name="customer_city",
                dtype="str",
                nullable=True,
                description="Customer city"
            ),
            ColumnSchema(
                name="acquisition_channel",
                dtype="str",
                nullable=True,
                allowed_values=["Online", "Store", "Referral", "Social Media", "Email"],
                description="How customer was acquired"
            ),
            ColumnSchema(
                name="is_premium_member",
                dtype="bool",
                nullable=False,
                description="Whether customer has premium membership"
            )
        ],
        indexes=["customer_id", "transaction_date", "product_category"]
    )
    return schema


def calculate_rfm_metrics(df: pl.DataFrame, analysis_date: datetime = None) -> pl.DataFrame:
    """Calculate RFM (Recency, Frequency, Monetary) metrics for each customer."""
    if analysis_date is None:
        analysis_date = datetime.now()
    
    print("📊 Calculating RFM Metrics...")
    
    # Calculate RFM metrics
    rfm_data = (
        df.group_by("customer_id")
        .agg([
            # Recency: Days since last purchase
            (pl.lit(analysis_date) - pl.col("transaction_date").max()).dt.total_days().alias("recency_days"),
            
            # Frequency: Number of transactions
            pl.col("transaction_date").count().alias("frequency"),
            
            # Monetary: Total amount spent
            pl.col("transaction_amount").sum().alias("monetary_value"),
            
            # Additional metrics
            pl.col("transaction_amount").mean().alias("avg_order_value"),
            pl.col("product_category").n_unique().alias("category_diversity"),
            pl.col("transaction_date").min().alias("first_purchase_date"),
            pl.col("is_premium_member").first().alias("is_premium_member"),
            pl.col("customer_age").first().alias("customer_age"),
            pl.col("customer_gender").first().alias("customer_gender"),
            pl.col("acquisition_channel").first().alias("acquisition_channel")
        ])
    )
    
    # Calculate customer lifetime (days since first purchase)
    rfm_data = rfm_data.with_columns([
        (pl.lit(analysis_date) - pl.col("first_purchase_date")).dt.total_days().alias("customer_lifetime_days")
    ])
    
    print(f"✅ RFM metrics calculated for {len(rfm_data)} customers")
    return rfm_data


def create_rfm_segments(rfm_df: pl.DataFrame) -> pl.DataFrame:
    """Create RFM segments based on quantiles."""
    print("🎯 Creating RFM Segments...")
    
    # Calculate quintiles for each RFM metric
    recency_quintiles = rfm_df.select(pl.col("recency_days").quantile([0.2, 0.4, 0.6, 0.8], "linear")).to_numpy().flatten()
    frequency_quintiles = rfm_df.select(pl.col("frequency").quantile([0.2, 0.4, 0.6, 0.8], "linear")).to_numpy().flatten()
    monetary_quintiles = rfm_df.select(pl.col("monetary_value").quantile([0.2, 0.4, 0.6, 0.8], "linear")).to_numpy().flatten()
    
    # Create RFM scores (1-5, where 5 is best)
    rfm_segmented = rfm_df.with_columns([
        # Recency score (lower recency = higher score)
        pl.when(pl.col("recency_days") <= recency_quintiles[0]).then(5)
        .when(pl.col("recency_days") <= recency_quintiles[1]).then(4)
        .when(pl.col("recency_days") <= recency_quintiles[2]).then(3)
        .when(pl.col("recency_days") <= recency_quintiles[3]).then(2)
        .otherwise(1).alias("recency_score"),
        
        # Frequency score (higher frequency = higher score)
        pl.when(pl.col("frequency") >= frequency_quintiles[3]).then(5)
        .when(pl.col("frequency") >= frequency_quintiles[2]).then(4)
        .when(pl.col("frequency") >= frequency_quintiles[1]).then(3)
        .when(pl.col("frequency") >= frequency_quintiles[0]).then(2)
        .otherwise(1).alias("frequency_score"),
        
        # Monetary score (higher monetary = higher score)
        pl.when(pl.col("monetary_value") >= monetary_quintiles[3]).then(5)
        .when(pl.col("monetary_value") >= monetary_quintiles[2]).then(4)
        .when(pl.col("monetary_value") >= monetary_quintiles[1]).then(3)
        .when(pl.col("monetary_value") >= monetary_quintiles[0]).then(2)
        .otherwise(1).alias("monetary_score")
    ])
    
    # Create combined RFM score and segments
    rfm_segmented = rfm_segmented.with_columns([
        (pl.col("recency_score") + pl.col("frequency_score") + pl.col("monetary_score")).alias("rfm_score"),
        
        # Create descriptive segments
        pl.when((pl.col("recency_score") >= 4) & (pl.col("frequency_score") >= 4) & (pl.col("monetary_score") >= 4))
        .then("Champions")
        .when((pl.col("recency_score") >= 3) & (pl.col("frequency_score") >= 3) & (pl.col("monetary_score") >= 4))
        .then("Loyal Customers")
        .when((pl.col("recency_score") >= 4) & (pl.col("frequency_score") <= 2))
        .then("New Customers")
        .when((pl.col("recency_score") >= 3) & (pl.col("frequency_score") >= 3) & (pl.col("monetary_score") <= 2))
        .then("Potential Loyalists")
        .when((pl.col("recency_score") >= 3) & (pl.col("frequency_score") <= 2) & (pl.col("monetary_score") >= 3))
        .then("Big Spenders")
        .when((pl.col("recency_score") <= 2) & (pl.col("frequency_score") >= 3) & (pl.col("monetary_value") >= monetary_quintiles[1]))
        .then("At Risk")
        .when((pl.col("recency_score") <= 2) & (pl.col("frequency_score") <= 2) & (pl.col("monetary_value") >= monetary_quintiles[2]))
        .then("Cannot Lose Them")
        .when((pl.col("recency_score") <= 2) & (pl.col("frequency_score") <= 2))
        .then("Lost Customers")
        .otherwise("Others").alias("customer_segment")
    ])
    
    print(f"✅ RFM segments created")
    return rfm_segmented


def analyze_customer_segments(rfm_df: pl.DataFrame) -> Dict[str, Any]:
    """Analyze customer segments and provide insights."""
    print("\n" + "="*60)
    print("CUSTOMER SEGMENTATION ANALYSIS")
    print("="*60)
    
    # Segment summary
    segment_summary = (
        rfm_df.group_by("customer_segment")
        .agg([
            pl.col("customer_id").count().alias("customer_count"),
            pl.col("monetary_value").sum().alias("total_revenue"),
            pl.col("monetary_value").mean().alias("avg_customer_value"),
            pl.col("frequency").mean().alias("avg_frequency"),
            pl.col("recency_days").mean().alias("avg_recency_days"),
            pl.col("avg_order_value").mean().alias("avg_order_value"),
            pl.col("is_premium_member").mean().alias("premium_rate")
        ])
        .sort("total_revenue", descending=True)
    )
    
    total_customers = rfm_df.shape[0]
    total_revenue = rfm_df.select(pl.col("monetary_value").sum()).item()
    
    print(f"\n📊 Segment Overview:")
    print(f"   Total Customers: {total_customers:,}")
    print(f"   Total Revenue: ${total_revenue:,.2f}")
    
    print(f"\n🎯 Customer Segments:")
    for row in segment_summary.iter_rows(named=True):
        segment = row['customer_segment']
        count = row['customer_count']
        revenue = row['total_revenue']
        avg_value = row['avg_customer_value']
        avg_freq = row['avg_frequency']
        avg_recency = row['avg_recency_days']
        premium_rate = row['premium_rate']
        
        percentage = (count / total_customers) * 100
        revenue_percentage = (revenue / total_revenue) * 100
        
        print(f"\n   📈 {segment}:")
        print(f"      Customers: {count:,} ({percentage:.1f}%)")
        print(f"      Revenue: ${revenue:,.2f} ({revenue_percentage:.1f}%)")
        print(f"      Avg Customer Value: ${avg_value:.2f}")
        print(f"      Avg Frequency: {avg_freq:.1f} transactions")
        print(f"      Avg Recency: {avg_recency:.0f} days")
        print(f"      Premium Rate: {premium_rate:.1%}")
    
    return {
        "segment_summary": segment_summary.to_pandas(),
        "total_customers": total_customers,
        "total_revenue": total_revenue
    }


def calculate_customer_lifetime_value(rfm_df: pl.DataFrame) -> pl.DataFrame:
    """Calculate Customer Lifetime Value (CLV) for each customer."""
    print("\n💰 Calculating Customer Lifetime Value...")
    
    clv_df = rfm_df.with_columns([
        # Simple CLV calculation: (Avg Order Value * Frequency * Gross Margin) / Churn Rate
        # Assuming 20% gross margin and estimating churn rate based on recency
        (pl.col("avg_order_value") * pl.col("frequency") * 0.20 * 
         pl.when(pl.col("recency_days") < 30).then(0.95)  # Low churn for recent customers
         .when(pl.col("recency_days") < 90).then(0.80)    # Medium churn
         .when(pl.col("recency_days") < 180).then(0.60)   # Higher churn
         .otherwise(0.30)                                 # High churn for old customers
        ).alias("estimated_clv"),
        
        # Historical CLV (actual value to date)
        pl.col("monetary_value").alias("historical_clv"),
        
        # Customer profitability score
        (pl.col("monetary_value") / (pl.col("customer_lifetime_days") + 1) * 365).alias("annual_value")
    ])
    
    # Add CLV segments
    clv_quintiles = clv_df.select(pl.col("estimated_clv").quantile([0.2, 0.4, 0.6, 0.8], "linear")).to_numpy().flatten()
    
    clv_df = clv_df.with_columns([
        pl.when(pl.col("estimated_clv") >= clv_quintiles[3]).then("High Value")
        .when(pl.col("estimated_clv") >= clv_quintiles[2]).then("Medium-High Value")
        .when(pl.col("estimated_clv") >= clv_quintiles[1]).then("Medium Value")
        .when(pl.col("estimated_clv") >= clv_quintiles[0]).then("Low-Medium Value")
        .otherwise("Low Value").alias("clv_segment")
    ])
    
    print(f"✅ CLV calculated for {len(clv_df)} customers")
    
    # Show CLV distribution
    clv_distribution = (
        clv_df.group_by("clv_segment")
        .agg([
            pl.col("customer_id").count().alias("customer_count"),
            pl.col("estimated_clv").mean().alias("avg_clv"),
            pl.col("historical_clv").mean().alias("avg_historical_clv")
        ])
        .sort("avg_clv", descending=True)
    )
    
    print(f"\n📊 CLV Distribution:")
    for row in clv_distribution.iter_rows(named=True):
        print(f"   {row['clv_segment']}: {row['customer_count']} customers, "
              f"Avg CLV: ${row['avg_clv']:.2f}, "
              f"Avg Historical: ${row['avg_historical_clv']:.2f}")
    
    return clv_df


def generate_marketing_recommendations(rfm_df: pl.DataFrame) -> None:
    """Generate actionable marketing recommendations based on segmentation."""
    print("\n" + "="*60)
    print("MARKETING RECOMMENDATIONS")
    print("="*60)
    
    # Get segment counts for recommendations
    segment_counts = (
        rfm_df.group_by("customer_segment")
        .agg([
            pl.col("customer_id").count().alias("count"),
            pl.col("monetary_value").mean().alias("avg_value"),
            pl.col("recency_days").mean().alias("avg_recency")
        ])
    )
    
    recommendations = {
        "Champions": "🏆 Reward them! Offer exclusive products, VIP treatment, and referral programs.",
        "Loyal Customers": "❤️ Upsell and cross-sell. Increase frequency with personalized recommendations.",
        "New Customers": "🆕 Welcome campaigns, onboarding sequences, and first purchase incentives.",
        "Potential Loyalists": "🌱 Nurture with targeted content, loyalty programs, and engagement campaigns.",
        "Big Spenders": "💸 Offer premium products, exclusive access, and high-value bundles.",
        "At Risk": "⚠️ Win-back campaigns, surveys to understand issues, special offers.",
        "Cannot Lose Them": "🆘 Aggressive retention campaigns, personal outreach, exclusive deals.",
        "Lost Customers": "💔 Reactivation campaigns, surveys, special comeback offers.",
        "Others": "🎯 General marketing campaigns, segment further for specific strategies."
    }
    
    print("\n📋 Segment-Specific Recommendations:")
    
    for row in segment_counts.iter_rows(named=True):
        segment = row['customer_segment']
        count = row['count']
        avg_value = row['avg_value']
        
        if segment in recommendations:
            print(f"\n   {segment} ({count} customers, avg value: ${avg_value:.2f}):")
            print(f"   {recommendations[segment]}")
    
    # Channel recommendations
    print(f"\n📱 Channel-Specific Insights:")
    
    channel_analysis = (
        rfm_df.filter(pl.col("acquisition_channel").is_not_null())
        .group_by("acquisition_channel")
        .agg([
            pl.col("customer_id").count().alias("customer_count"),
            pl.col("monetary_value").mean().alias("avg_clv"),
            pl.col("is_premium_member").mean().alias("premium_rate")
        ])
        .sort("avg_clv", descending=True)
    )
    
    for row in channel_analysis.iter_rows(named=True):
        channel = row['acquisition_channel']
        count = row['customer_count']
        avg_clv = row['avg_clv']
        premium_rate = row['premium_rate']
        
        print(f"   {channel}: {count} customers, ${avg_clv:.2f} avg CLV, {premium_rate:.1%} premium rate")
    
    # Age-based insights
    age_analysis = (
        rfm_df.filter(pl.col("customer_age").is_not_null())
        .with_columns([
            pl.when(pl.col("customer_age") < 30).then("18-29")
            .when(pl.col("customer_age") < 40).then("30-39")
            .when(pl.col("customer_age") < 50).then("40-49")
            .when(pl.col("customer_age") < 60).then("50-59")
            .otherwise("60+").alias("age_group")
        ])
        .group_by("age_group")
        .agg([
            pl.col("customer_id").count().alias("customer_count"),
            pl.col("monetary_value").mean().alias("avg_spending"),
            pl.col("frequency").mean().alias("avg_frequency")
        ])
        .sort("avg_spending", descending=True)
    )
    
    print(f"\n👥 Age Group Insights:")
    for row in age_analysis.iter_rows(named=True):
        age_group = row['age_group']
        count = row['customer_count']
        avg_spending = row['avg_spending']
        avg_freq = row['avg_frequency']
        
        print(f"   {age_group}: {count} customers, ${avg_spending:.2f} avg spending, {avg_freq:.1f} frequency")


def main():
    """Main execution function."""
    print("🎯 Customer Segmentation Analysis Example")
    print("Using DataScience Analytics Platform")
    print("-" * 60)
    
    try:
        # Create and register schema
        print("📋 Creating customer transaction schema...")
        customer_schema = create_customer_schema()
        schema_registry.register_schema(customer_schema)
        print(f"✅ Schema '{customer_schema.name}' registered")
        
        # Configure data reader
        options = ReadOptions(
            use_polars=True,
            parse_dates=['transaction_date'],
            encoding='utf-8'
        )
        reader = DataReader(options)
        
        # Check if sample data exists, create if not
        data_file = Path(__file__).parent / "sample_customer_data.csv"
        if not data_file.exists():
            print("📁 Sample data not found. Creating sample dataset...")
            create_sample_customer_data(data_file)
        
        # Read customer data
        print(f"📖 Reading customer data from {data_file}...")
        df = reader.read(str(data_file))
        print(f"✅ Loaded {df.shape[0]} transactions for analysis")
        
        # Validate data
        print("🔍 Validating data quality...")
        validator = DataValidator(strict_mode=False)
        validation_result = validator.validate_with_schema(df, customer_schema)
        
        if validation_result.is_valid:
            print("✅ Data validation passed!")
        else:
            print("⚠️ Data validation issues found:")
            for error in validation_result.errors[:3]:
                print(f"   • {error}")
        
        # Clean and transform data
        print("🔧 Cleaning and transforming data...")
        transformer = DataTransformer()
        cleaned_df, transform_report = transformer.transform_dataframe(df, schema=customer_schema)
        print(f"✅ Data transformation complete (success rate: {transform_report.transformation_success_rate:.1%})")
        
        # Calculate RFM metrics
        analysis_date = datetime(2024, 12, 31)  # Set analysis date
        rfm_df = calculate_rfm_metrics(cleaned_df, analysis_date)
        
        # Create RFM segments
        segmented_df = create_rfm_segments(rfm_df)
        
        # Analyze segments
        segment_analysis = analyze_customer_segments(segmented_df)
        
        # Calculate CLV
        clv_df = calculate_customer_lifetime_value(segmented_df)
        
        # Generate recommendations
        generate_marketing_recommendations(clv_df)
        
        # Save results
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save segmented customer data
        clv_df.write_parquet(output_dir / "customer_segments.parquet")
        
        # Save summary statistics
        import json
        
        summary_stats = {
            "analysis_date": analysis_date.isoformat(),
            "total_customers": int(segment_analysis["total_customers"]),
            "total_revenue": float(segment_analysis["total_revenue"]),
            "segments": {}
        }
        
        # Add segment details
        for row in segment_analysis["segment_summary"].iterrows():
            segment_data = row[1]
            summary_stats["segments"][segment_data["customer_segment"]] = {
                "customer_count": int(segment_data["customer_count"]),
                "total_revenue": float(segment_data["total_revenue"]),
                "avg_customer_value": float(segment_data["avg_customer_value"]),
                "percentage_of_customers": float(segment_data["customer_count"] / segment_analysis["total_customers"] * 100)
            }
        
        with open(output_dir / "segmentation_analysis_results.json", "w") as f:
            json.dump(summary_stats, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {output_dir}/")
        print("   • customer_segments.parquet")
        print("   • segmentation_analysis_results.json")
        
        print(f"\n🎉 Customer segmentation analysis complete!")
        print(f"   Customers Analyzed: {segment_analysis['total_customers']:,}")
        print(f"   Total Revenue: ${segment_analysis['total_revenue']:,.2f}")
        print(f"   Segments Identified: {len(summary_stats['segments'])}")
        
    except DataSciencePlatformError as e:
        print(f"❌ Platform error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def create_sample_customer_data(output_file: Path) -> None:
    """Create sample customer transaction data for segmentation analysis."""
    import random
    from datetime import datetime, timedelta
    
    print("🔨 Generating sample customer transaction data...")
    
    # Sample data parameters
    num_customers = 500
    num_transactions = 5000
    
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Beauty", "Automotive"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio"]
    channels = ["Online", "Store", "Referral", "Social Media", "Email"]
    genders = ["M", "F", "Other"]
    
    # Generate customers
    customers = []
    for i in range(num_customers):
        customer = {
            "id": f"CUST{i+1:05d}",
            "age": random.randint(18, 80),
            "gender": random.choice(genders),
            "city": random.choice(cities),
            "channel": random.choice(channels),
            "is_premium": random.random() < 0.3,  # 30% premium members
            "join_date": datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1400))
        }
        customers.append(customer)
    
    # Generate transactions
    data = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    for i in range(num_transactions):
        customer = random.choice(customers)
        
        # Create realistic transaction patterns
        transaction_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        # Ensure transaction is after customer join date
        if transaction_date < customer["join_date"]:
            transaction_date = customer["join_date"] + timedelta(days=random.randint(0, 30))
        
        # Transaction amount varies by customer segment and category
        base_amount = random.uniform(10, 500)
        if customer["is_premium"]:
            base_amount *= random.uniform(1.5, 3.0)
        
        transaction = {
            "customer_id": customer["id"],
            "transaction_date": transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_amount": round(base_amount, 2),
            "product_category": random.choice(categories),
            "customer_age": customer["age"],
            "customer_gender": customer["gender"],
            "customer_city": customer["city"],
            "acquisition_channel": customer["channel"],
            "is_premium_member": customer["is_premium"]
        }
        
        data.append(transaction)
    
    # Sort by customer and date for more realistic data
    data.sort(key=lambda x: (x["customer_id"], x["transaction_date"]))
    
    # Save to CSV
    import csv
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Created sample data with {num_transactions} transactions for {num_customers} customers at {output_file}")


if __name__ == "__main__":
    main()