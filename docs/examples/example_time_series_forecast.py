#!/usr/bin/env python3
"""
Time Series Forecasting Example

This example demonstrates time series analysis and forecasting using the 
DataScience Analytics Platform, including:
- Time series data validation and preprocessing
- Trend and seasonality analysis
- Multiple forecasting approaches (moving averages, exponential smoothing)
- Forecast accuracy evaluation
- Visualization of results and predictions

Dataset: Daily sales/revenue data with seasonal patterns
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import polars as pl
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Add the package to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from datascience_platform.etl import (
    DataReader, ReadOptions, DataValidator, DataTransformer,
    DataSchema, ColumnSchema, schema_registry
)
from datascience_platform.core.exceptions import DataSciencePlatformError


def create_time_series_schema() -> DataSchema:
    """Create and return the time series data schema."""
    schema = DataSchema(
        name="daily_sales_data",
        version="1.0.0",
        description="Daily sales time series data for forecasting",
        columns=[
            ColumnSchema(
                name="date",
                dtype="datetime",
                nullable=False,
                unique=True,
                description="Date of the observation"
            ),
            ColumnSchema(
                name="sales_amount",
                dtype="float64",
                nullable=False,
                min_value=0.0,
                description="Daily sales amount"
            ),
            ColumnSchema(
                name="transactions_count",
                dtype="int64",
                nullable=False,
                min_value=0,
                description="Number of daily transactions"
            ),
            ColumnSchema(
                name="avg_transaction_value",
                dtype="float64",
                nullable=False,
                min_value=0.0,
                description="Average transaction value"
            ),
            ColumnSchema(
                name="day_of_week",
                dtype="int64",
                nullable=False,
                min_value=0,
                max_value=6,
                description="Day of week (0=Monday, 6=Sunday)"
            ),
            ColumnSchema(
                name="is_weekend",
                dtype="bool",
                nullable=False,
                description="Whether the day is weekend"
            ),
            ColumnSchema(
                name="is_holiday",
                dtype="bool",
                nullable=False,
                description="Whether the day is a holiday"
            ),
            ColumnSchema(
                name="weather_category",
                dtype="str",
                nullable=True,
                allowed_values=["Sunny", "Cloudy", "Rainy", "Snowy"],
                description="Weather category"
            ),
            ColumnSchema(
                name="promotional_campaign",
                dtype="bool",
                nullable=False,
                description="Whether there was a promotional campaign"
            )
        ],
        primary_key=["date"],
        indexes=["date"]
    )
    return schema


def analyze_time_series_patterns(df: pl.DataFrame) -> Dict[str, Any]:
    """Analyze time series patterns including trend, seasonality, and outliers."""
    print("\n" + "="*60)
    print("TIME SERIES PATTERN ANALYSIS")
    print("="*60)
    
    # Sort by date
    df = df.sort("date")
    
    # Basic statistics
    total_days = len(df)
    date_range = df.select([pl.col("date").min(), pl.col("date").max()])
    start_date, end_date = date_range.row(0)
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Time Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Total Days: {total_days}")
    print(f"   Missing Days: {(end_date - start_date).days + 1 - total_days}")
    
    # Sales statistics
    sales_stats = df.select([
        pl.col("sales_amount").mean().alias("mean"),
        pl.col("sales_amount").median().alias("median"),
        pl.col("sales_amount").std().alias("std"),
        pl.col("sales_amount").min().alias("min"),
        pl.col("sales_amount").max().alias("max")
    ]).row(0)
    
    print(f"\n💰 Sales Statistics:")
    print(f"   Mean Daily Sales: ${sales_stats[0]:,.2f}")
    print(f"   Median Daily Sales: ${sales_stats[1]:,.2f}")
    print(f"   Standard Deviation: ${sales_stats[2]:,.2f}")
    print(f"   Min Daily Sales: ${sales_stats[3]:,.2f}")
    print(f"   Max Daily Sales: ${sales_stats[4]:,.2f}")
    
    # Day of week analysis
    dow_analysis = (
        df.group_by("day_of_week")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
        .sort("day_of_week")
    )
    
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    print(f"\n📅 Day of Week Patterns:")
    for row in dow_analysis.iter_rows(named=True):
        day_name = day_names[row['day_of_week']]
        avg_sales = row['avg_sales']
        count = row['count']
        print(f"   {day_name}: ${avg_sales:,.2f} avg ({count} days)")
    
    # Weekend vs weekday analysis
    weekend_analysis = (
        df.group_by("is_weekend")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").sum().alias("total_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
    )
    
    print(f"\n🏢 Weekend vs Weekday Analysis:")
    for row in weekend_analysis.iter_rows(named=True):
        period = "Weekend" if row['is_weekend'] else "Weekday"
        avg_sales = row['avg_sales']
        total_sales = row['total_sales']
        count = row['count']
        print(f"   {period}: ${avg_sales:,.2f} avg, ${total_sales:,.2f} total ({count} days)")
    
    # Holiday impact
    holiday_analysis = (
        df.group_by("is_holiday")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
    )
    
    print(f"\n🎉 Holiday Impact:")
    for row in holiday_analysis.iter_rows(named=True):
        period = "Holiday" if row['is_holiday'] else "Regular Day"
        avg_sales = row['avg_sales']
        count = row['count']
        print(f"   {period}: ${avg_sales:,.2f} avg ({count} days)")
    
    # Weather impact (if available)
    if df.select(pl.col("weather_category").is_not_null().sum()).item() > 0:
        weather_analysis = (
            df.filter(pl.col("weather_category").is_not_null())
            .group_by("weather_category")
            .agg([
                pl.col("sales_amount").mean().alias("avg_sales"),
                pl.col("sales_amount").count().alias("count")
            ])
            .sort("avg_sales", descending=True)
        )
        
        print(f"\n🌤️ Weather Impact:")
        for row in weather_analysis.iter_rows(named=True):
            weather = row['weather_category']
            avg_sales = row['avg_sales']
            count = row['count']
            print(f"   {weather}: ${avg_sales:,.2f} avg ({count} days)")
    
    # Promotional campaign impact
    promo_analysis = (
        df.group_by("promotional_campaign")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
    )
    
    print(f"\n📢 Promotional Campaign Impact:")
    for row in promo_analysis.iter_rows(named=True):
        period = "With Promotion" if row['promotional_campaign'] else "No Promotion"
        avg_sales = row['avg_sales']
        count = row['count']
        print(f"   {period}: ${avg_sales:,.2f} avg ({count} days)")
    
    return {
        "total_days": total_days,
        "date_range": (start_date, end_date),
        "sales_stats": sales_stats,
        "dow_analysis": dow_analysis.to_pandas(),
        "weekend_analysis": weekend_analysis.to_pandas(),
        "holiday_analysis": holiday_analysis.to_pandas(),
        "promo_analysis": promo_analysis.to_pandas()
    }


def calculate_moving_averages(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate various moving averages for trend analysis."""
    print("\n📈 Calculating Moving Averages...")
    
    df_with_ma = df.sort("date").with_columns([
        # Simple moving averages
        pl.col("sales_amount").rolling_mean(window_size=7).alias("ma_7"),
        pl.col("sales_amount").rolling_mean(window_size=14).alias("ma_14"),
        pl.col("sales_amount").rolling_mean(window_size=30).alias("ma_30"),
        
        # Exponential moving averages (approximation)
        pl.col("sales_amount").ewm_mean(alpha=0.3).alias("ema_7"),
        pl.col("sales_amount").ewm_mean(alpha=0.15).alias("ema_14"),
        pl.col("sales_amount").ewm_mean(alpha=0.067).alias("ema_30"),
    ])
    
    print("✅ Moving averages calculated (7-day, 14-day, 30-day)")
    return df_with_ma


def detect_trend_and_seasonality(df: pl.DataFrame) -> Dict[str, Any]:
    """Detect overall trend and seasonal patterns."""
    print("\n🔍 Detecting Trend and Seasonality...")
    
    # Add time-based features
    df_enhanced = df.sort("date").with_columns([
        pl.col("date").dt.year().alias("year"),
        pl.col("date").dt.month().alias("month"),
        pl.col("date").dt.quarter().alias("quarter"),
        pl.col("date").dt.week().alias("week"),
        (pl.col("date").dt.ordinal_day() - pl.col("date").dt.ordinal_day().min()).alias("days_from_start")
    ])
    
    # Monthly seasonality
    monthly_pattern = (
        df_enhanced.group_by("month")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").std().alias("std_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
        .sort("month")
    )
    
    print(f"\n📅 Monthly Seasonality Pattern:")
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    for row in monthly_pattern.iter_rows(named=True):
        month_name = month_names[row['month'] - 1]
        avg_sales = row['avg_sales']
        std_sales = row['std_sales']
        count = row['count']
        print(f"   {month_name}: ${avg_sales:,.2f} ± ${std_sales:,.2f} ({count} days)")
    
    # Quarterly analysis
    quarterly_pattern = (
        df_enhanced.group_by("quarter")
        .agg([
            pl.col("sales_amount").mean().alias("avg_sales"),
            pl.col("sales_amount").sum().alias("total_sales"),
            pl.col("sales_amount").count().alias("count")
        ])
        .sort("quarter")
    )
    
    print(f"\n📊 Quarterly Performance:")
    for row in quarterly_pattern.iter_rows(named=True):
        quarter = f"Q{row['quarter']}"
        avg_sales = row['avg_sales']
        total_sales = row['total_sales']
        count = row['count']
        print(f"   {quarter}: ${avg_sales:,.2f} avg, ${total_sales:,.2f} total ({count} days)")
    
    # Year-over-year growth (if multiple years)
    yearly_analysis = (
        df_enhanced.group_by("year")
        .agg([
            pl.col("sales_amount").mean().alias("avg_daily_sales"),
            pl.col("sales_amount").sum().alias("total_sales"),
            pl.col("sales_amount").count().alias("days")
        ])
        .sort("year")
    )
    
    if len(yearly_analysis) > 1:
        print(f"\n📈 Year-over-Year Analysis:")
        yearly_data = yearly_analysis.to_pandas()
        for i, row in yearly_data.iterrows():
            year = int(row['year'])
            avg_sales = row['avg_daily_sales']
            total_sales = row['total_sales']
            days = row['days']
            
            growth_rate = ""
            if i > 0:
                prev_avg = yearly_data.iloc[i-1]['avg_daily_sales']
                growth = (avg_sales - prev_avg) / prev_avg * 100
                growth_rate = f" ({growth:+.1f}% vs prev year)"
            
            print(f"   {year}: ${avg_sales:,.2f} avg daily{growth_rate}, ${total_sales:,.2f} total ({days} days)")
    
    return {
        "monthly_pattern": monthly_pattern.to_pandas(),
        "quarterly_pattern": quarterly_pattern.to_pandas(),
        "yearly_analysis": yearly_analysis.to_pandas()
    }


def simple_forecasting(df: pl.DataFrame, forecast_days: int = 30) -> Dict[str, Any]:
    """Implement simple forecasting methods."""
    print(f"\n🔮 Generating {forecast_days}-day Forecast...")
    
    # Sort data by date
    df_sorted = df.sort("date")
    
    # Get last date and create forecast dates
    last_date = df_sorted.select(pl.col("date").max()).item()
    forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
    
    # Calculate moving averages for forecasting
    recent_data = df_sorted.tail(90)  # Use last 90 days for forecasting
    
    # Method 1: Simple moving average
    ma_7 = recent_data.select(pl.col("sales_amount").tail(7).mean()).item()
    ma_14 = recent_data.select(pl.col("sales_amount").tail(14).mean()).item()
    ma_30 = recent_data.select(pl.col("sales_amount").tail(30).mean()).item()
    
    # Method 2: Exponential smoothing (simple)
    alpha = 0.3
    last_value = recent_data.select(pl.col("sales_amount").last()).item()
    ema_forecast = last_value  # Starting point
    
    # Method 3: Seasonal naive (same day of week from recent weeks)
    seasonal_forecasts = []
    for i, forecast_date in enumerate(forecast_dates):
        dow = forecast_date.weekday()
        
        # Get same day of week from recent history
        same_dow_data = (
            recent_data.filter(pl.col("day_of_week") == dow)
            .select(pl.col("sales_amount").mean())
            .item()
        )
        seasonal_forecasts.append(same_dow_data)
    
    # Create forecast dataframe
    forecasts = []
    for i, date in enumerate(forecast_dates):
        dow = date.weekday()
        is_weekend = dow >= 5
        
        # Combine different methods
        seasonal_component = seasonal_forecasts[i]
        trend_component = ma_30  # Use long-term average as trend
        
        # Simple ensemble forecast
        forecast_value = (seasonal_component * 0.6 + trend_component * 0.4)
        
        # Add some realistic noise/uncertainty
        uncertainty = forecast_value * 0.1  # 10% uncertainty
        
        forecasts.append({
            "date": date,
            "forecast_sales": forecast_value,
            "forecast_lower": forecast_value - uncertainty,
            "forecast_upper": forecast_value + uncertainty,
            "method": "ensemble",
            "day_of_week": dow,
            "is_weekend": is_weekend
        })
    
    forecast_df = pl.DataFrame(forecasts)
    
    # Calculate forecast statistics
    total_forecast = forecast_df.select(pl.col("forecast_sales").sum()).item()
    avg_forecast = forecast_df.select(pl.col("forecast_sales").mean()).item()
    
    print(f"✅ Forecast generated:")
    print(f"   Forecast Period: {forecast_dates[0].strftime('%Y-%m-%d')} to {forecast_dates[-1].strftime('%Y-%m-%d')}")
    print(f"   Predicted Total Sales: ${total_forecast:,.2f}")
    print(f"   Predicted Avg Daily Sales: ${avg_forecast:,.2f}")
    
    # Show first few days of forecast
    print(f"\n📅 First 7 Days Forecast:")
    for row in forecast_df.head(7).iter_rows(named=True):
        date_str = row['date'].strftime('%Y-%m-%d')
        forecast = row['forecast_sales']
        lower = row['forecast_lower']
        upper = row['forecast_upper']
        dow_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][row['day_of_week']]
        
        print(f"   {date_str} ({dow_name}): ${forecast:,.2f} (${lower:,.2f} - ${upper:,.2f})")
    
    return {
        "forecast_df": forecast_df,
        "forecast_methods": {
            "ma_7": ma_7,
            "ma_14": ma_14,
            "ma_30": ma_30
        },
        "forecast_summary": {
            "total_forecast": total_forecast,
            "avg_forecast": avg_forecast,
            "forecast_days": forecast_days
        }
    }


def evaluate_forecast_accuracy(df: pl.DataFrame) -> Dict[str, Any]:
    """Evaluate forecast accuracy using historical data."""
    print("\n🎯 Evaluating Forecast Accuracy (Backtesting)...")
    
    # Use last 30 days as test set
    test_days = 30
    if len(df) < test_days + 30:
        print("⚠️ Not enough historical data for proper backtesting")
        return {}
    
    # Split data
    train_data = df.head(len(df) - test_days)
    test_data = df.tail(test_days)
    
    # Generate forecasts for test period
    test_forecasts = []
    
    for i in range(test_days):
        # Use data up to current point for forecasting
        current_train = df.head(len(df) - test_days + i)
        
        # Simple forecast: 7-day moving average
        if len(current_train) >= 7:
            forecast = current_train.select(pl.col("sales_amount").tail(7).mean()).item()
        else:
            forecast = current_train.select(pl.col("sales_amount").mean()).item()
        
        test_forecasts.append(forecast)
    
    # Calculate accuracy metrics
    actual_values = test_data.select(pl.col("sales_amount")).to_numpy().flatten()
    forecast_values = np.array(test_forecasts)
    
    # Mean Absolute Error
    mae = np.mean(np.abs(actual_values - forecast_values))
    
    # Mean Absolute Percentage Error
    mape = np.mean(np.abs((actual_values - forecast_values) / actual_values)) * 100
    
    # Root Mean Square Error
    rmse = np.sqrt(np.mean((actual_values - forecast_values) ** 2))
    
    # Mean Absolute Scaled Error (MASE)
    naive_error = np.mean(np.abs(np.diff(train_data.select(pl.col("sales_amount")).to_numpy().flatten())))
    mase = mae / naive_error if naive_error > 0 else float('inf')
    
    print(f"✅ Forecast Accuracy Metrics (based on {test_days}-day backtest):")
    print(f"   Mean Absolute Error (MAE): ${mae:.2f}")
    print(f"   Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
    print(f"   Root Mean Square Error (RMSE): ${rmse:.2f}")
    print(f"   Mean Absolute Scaled Error (MASE): {mase:.3f}")
    
    # Interpretation
    if mape < 5:
        accuracy = "Excellent"
    elif mape < 10:
        accuracy = "Good"
    elif mape < 20:
        accuracy = "Reasonable"
    else:
        accuracy = "Poor"
    
    print(f"   Forecast Accuracy: {accuracy}")
    
    return {
        "mae": mae,
        "mape": mape,
        "rmse": rmse,
        "mase": mase,
        "accuracy_rating": accuracy,
        "actual_values": actual_values,
        "forecast_values": forecast_values
    }


def generate_insights_and_recommendations(
    pattern_analysis: Dict[str, Any],
    trend_analysis: Dict[str, Any],
    forecast_results: Dict[str, Any],
    accuracy_results: Dict[str, Any]
) -> None:
    """Generate business insights and recommendations."""
    print("\n" + "="*60)
    print("BUSINESS INSIGHTS & RECOMMENDATIONS")
    print("="*60)
    
    print(f"\n🔍 Key Findings:")
    
    # Seasonal patterns
    if 'monthly_pattern' in trend_analysis:
        monthly_data = trend_analysis['monthly_pattern']
        best_month = monthly_data.loc[monthly_data['avg_sales'].idxmax()]
        worst_month = monthly_data.loc[monthly_data['avg_sales'].idxmin()]
        
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        print(f"   📅 Seasonality: Best month is {month_names[int(best_month['month'])-1]} "
              f"(${best_month['avg_sales']:,.2f}), worst is {month_names[int(worst_month['month'])-1]} "
              f"(${worst_month['avg_sales']:,.2f})")
    
    # Weekend vs weekday performance
    if 'weekend_analysis' in pattern_analysis:
        weekend_data = pattern_analysis['weekend_analysis']
        weekend_avg = weekend_data[weekend_data['is_weekend'] == True]['avg_sales'].iloc[0]
        weekday_avg = weekend_data[weekend_data['is_weekend'] == False]['avg_sales'].iloc[0]
        
        if weekend_avg > weekday_avg:
            print(f"   🏖️ Weekend Performance: Weekends outperform weekdays by "
                  f"${weekend_avg - weekday_avg:,.2f} per day ({((weekend_avg/weekday_avg-1)*100):+.1f}%)")
        else:
            print(f"   🏢 Weekday Performance: Weekdays outperform weekends by "
                  f"${weekday_avg - weekend_avg:,.2f} per day ({((weekday_avg/weekend_avg-1)*100):+.1f}%)")
    
    # Holiday impact
    if 'holiday_analysis' in pattern_analysis:
        holiday_data = pattern_analysis['holiday_analysis']
        if len(holiday_data) == 2:
            holiday_avg = holiday_data[holiday_data['is_holiday'] == True]['avg_sales'].iloc[0]
            regular_avg = holiday_data[holiday_data['is_holiday'] == False]['avg_sales'].iloc[0]
            
            impact = (holiday_avg / regular_avg - 1) * 100
            print(f"   🎉 Holiday Impact: Holidays show {impact:+.1f}% sales vs regular days")
    
    # Promotional campaign effectiveness
    if 'promo_analysis' in pattern_analysis:
        promo_data = pattern_analysis['promo_analysis']
        if len(promo_data) == 2:
            promo_avg = promo_data[promo_data['promotional_campaign'] == True]['avg_sales'].iloc[0]
            no_promo_avg = promo_data[promo_data['promotional_campaign'] == False]['avg_sales'].iloc[0]
            
            impact = (promo_avg / no_promo_avg - 1) * 100
            print(f"   📢 Promotion Impact: Campaigns increase sales by {impact:+.1f}%")
    
    # Forecast insights
    if forecast_results:
        forecast_avg = forecast_results['forecast_summary']['avg_forecast']
        historical_avg = pattern_analysis['sales_stats'][0]  # mean
        
        forecast_change = (forecast_avg / historical_avg - 1) * 100
        print(f"   🔮 Forecast Trend: Next period predicted {forecast_change:+.1f}% vs historical average")
    
    print(f"\n💡 Strategic Recommendations:")
    
    # Seasonal recommendations
    if 'monthly_pattern' in trend_analysis:
        print(f"   📅 Seasonal Strategy:")
        print(f"      • Increase inventory and marketing spend during peak months")
        print(f"      • Plan maintenance and staff vacations during low months")
        print(f"      • Develop counter-seasonal promotions to smooth demand")
    
    # Day-of-week recommendations
    if 'weekend_analysis' in pattern_analysis:
        weekend_data = pattern_analysis['weekend_analysis']
        weekend_avg = weekend_data[weekend_data['is_weekend'] == True]['avg_sales'].iloc[0]
        weekday_avg = weekend_data[weekend_data['is_weekend'] == False]['avg_sales'].iloc[0]
        
        print(f"   📊 Operational Strategy:")
        if weekend_avg > weekday_avg:
            print(f"      • Optimize weekend staffing and inventory")
            print(f"      • Consider weekend-specific promotions")
            print(f"      • Focus marketing campaigns on weekday sales")
        else:
            print(f"      • Focus on weekday customer retention")
            print(f"      • Develop weekend attraction strategies")
            print(f"      • Consider extended weekend hours")
    
    # Promotion recommendations
    if 'promo_analysis' in pattern_analysis:
        print(f"   📢 Marketing Strategy:")
        print(f"      • Analyze promotion ROI and optimize campaign timing")
        print(f"      • Test different promotion types and intensities")
        print(f"      • Coordinate promotions with seasonal patterns")
    
    # Forecasting recommendations
    if accuracy_results:
        mape = accuracy_results.get('mape', 0)
        print(f"   🎯 Forecasting Strategy:")
        if mape < 10:
            print(f"      • Current forecasting accuracy is good - use for planning")
            print(f"      • Consider automated inventory management")
        else:
            print(f"      • Improve forecasting with external data (weather, events)")
            print(f"      • Consider more sophisticated models")
        print(f"      • Implement rolling forecasts and regular model updates")
        print(f"      • Use forecast uncertainty ranges for risk management")


def main():
    """Main execution function."""
    print("📈 Time Series Forecasting Analysis Example")
    print("Using DataScience Analytics Platform")
    print("-" * 60)
    
    try:
        # Create and register schema
        print("📋 Creating time series data schema...")
        ts_schema = create_time_series_schema()
        schema_registry.register_schema(ts_schema)
        print(f"✅ Schema '{ts_schema.name}' registered")
        
        # Configure data reader
        options = ReadOptions(
            use_polars=True,
            parse_dates=['date'],
            encoding='utf-8'
        )
        reader = DataReader(options)
        
        # Check if sample data exists, create if not
        data_file = Path(__file__).parent / "sample_time_series_data.csv"
        if not data_file.exists():
            print("📁 Sample data not found. Creating sample dataset...")
            create_sample_time_series_data(data_file)
        
        # Read time series data
        print(f"📖 Reading time series data from {data_file}...")
        df = reader.read(str(data_file))
        print(f"✅ Loaded {df.shape[0]} daily records")
        
        # Validate data
        print("🔍 Validating data quality...")
        validator = DataValidator(strict_mode=False)
        validation_result = validator.validate_with_schema(df, ts_schema)
        
        if validation_result.is_valid:
            print("✅ Data validation passed!")
        else:
            print("⚠️ Data validation issues found:")
            for error in validation_result.errors[:3]:
                print(f"   • {error}")
        
        # Clean and transform data
        print("🔧 Cleaning and transforming data...")
        transformer = DataTransformer()
        cleaned_df, transform_report = transformer.transform_dataframe(df, schema=ts_schema)
        print(f"✅ Data transformation complete")
        
        # Add moving averages
        df_with_ma = calculate_moving_averages(cleaned_df)
        
        # Analyze patterns
        pattern_analysis = analyze_time_series_patterns(df_with_ma)
        
        # Detect trend and seasonality
        trend_analysis = detect_trend_and_seasonality(df_with_ma)
        
        # Generate forecasts
        forecast_results = simple_forecasting(df_with_ma, forecast_days=30)
        
        # Evaluate accuracy
        accuracy_results = evaluate_forecast_accuracy(df_with_ma)
        
        # Generate insights and recommendations
        generate_insights_and_recommendations(
            pattern_analysis, trend_analysis, forecast_results, accuracy_results
        )
        
        # Save results
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save enhanced data with moving averages
        df_with_ma.write_parquet(output_dir / "time_series_with_analysis.parquet")
        
        # Save forecast
        if forecast_results:
            forecast_results['forecast_df'].write_parquet(output_dir / "sales_forecast.parquet")
        
        # Save analysis summary
        import json
        
        summary = {
            "analysis_period": {
                "start_date": pattern_analysis['date_range'][0].isoformat(),
                "end_date": pattern_analysis['date_range'][1].isoformat(),
                "total_days": pattern_analysis['total_days']
            },
            "sales_summary": {
                "mean_daily_sales": float(pattern_analysis['sales_stats'][0]),
                "median_daily_sales": float(pattern_analysis['sales_stats'][1]),
                "std_daily_sales": float(pattern_analysis['sales_stats'][2]),
                "min_daily_sales": float(pattern_analysis['sales_stats'][3]),
                "max_daily_sales": float(pattern_analysis['sales_stats'][4])
            },
            "forecast_summary": forecast_results.get('forecast_summary', {}),
            "accuracy_metrics": {
                "mae": accuracy_results.get('mae', None),
                "mape": accuracy_results.get('mape', None),
                "rmse": accuracy_results.get('rmse', None),
                "accuracy_rating": accuracy_results.get('accuracy_rating', 'Unknown')
            }
        }
        
        with open(output_dir / "time_series_analysis_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to {output_dir}/")
        print("   • time_series_with_analysis.parquet")
        print("   • sales_forecast.parquet")
        print("   • time_series_analysis_results.json")
        
        print(f"\n🎉 Time series analysis complete!")
        print(f"   Days Analyzed: {pattern_analysis['total_days']}")
        print(f"   Average Daily Sales: ${pattern_analysis['sales_stats'][0]:,.2f}")
        if forecast_results:
            print(f"   30-Day Forecast Total: ${forecast_results['forecast_summary']['total_forecast']:,.2f}")
        
    except DataSciencePlatformError as e:
        print(f"❌ Platform error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


def create_sample_time_series_data(output_file: Path) -> None:
    """Create sample daily sales time series data."""
    import random
    import math
    from datetime import datetime, timedelta
    
    print("🔨 Generating sample time series data...")
    
    # Parameters
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    current_date = start_date
    
    # Base parameters
    base_sales = 10000  # Base daily sales
    trend_rate = 0.0002  # Small positive trend
    
    # Seasonal parameters
    seasonal_amplitude = 0.3  # 30% seasonal variation
    
    # Holiday dates (simplified)
    holidays = [
        datetime(2023, 1, 1), datetime(2023, 7, 4), datetime(2023, 12, 25),
        datetime(2024, 1, 1), datetime(2024, 7, 4), datetime(2024, 12, 25)
    ]
    
    weather_conditions = ["Sunny", "Cloudy", "Rainy", "Snowy"]
    
    data = []
    day_counter = 0
    
    while current_date <= end_date:
        # Day of week (0=Monday, 6=Sunday)
        dow = current_date.weekday()
        is_weekend = dow >= 5
        is_holiday = current_date in holidays
        
        # Base sales with trend
        trend_component = base_sales * (1 + trend_rate * day_counter)
        
        # Seasonal component (annual cycle)
        day_of_year = current_date.timetuple().tm_yday
        seasonal_component = seasonal_amplitude * math.sin(2 * math.pi * day_of_year / 365.25)
        
        # Weekly pattern (weekends typically different)
        if is_weekend:
            weekly_multiplier = random.uniform(1.1, 1.3)  # Weekends higher
        else:
            weekly_multiplier = random.uniform(0.9, 1.1)
        
        # Holiday effect
        if is_holiday:
            holiday_multiplier = random.uniform(0.7, 1.5)  # Varies by holiday
        else:
            holiday_multiplier = 1.0
        
        # Promotional campaigns (random 20% of days)
        has_promotion = random.random() < 0.2
        if has_promotion:
            promo_multiplier = random.uniform(1.1, 1.4)
        else:
            promo_multiplier = 1.0
        
        # Weather effect
        weather = random.choice(weather_conditions)
        if weather == "Sunny":
            weather_multiplier = random.uniform(1.05, 1.15)
        elif weather == "Rainy":
            weather_multiplier = random.uniform(0.85, 0.95)
        elif weather == "Snowy":
            weather_multiplier = random.uniform(0.7, 0.9)
        else:  # Cloudy
            weather_multiplier = random.uniform(0.95, 1.05)
        
        # Calculate final sales amount
        sales_amount = (trend_component * 
                       (1 + seasonal_component) * 
                       weekly_multiplier * 
                       holiday_multiplier * 
                       promo_multiplier * 
                       weather_multiplier)
        
        # Add some random noise
        noise = random.uniform(0.9, 1.1)
        sales_amount *= noise
        
        # Ensure minimum sales
        sales_amount = max(sales_amount, 1000)
        
        # Calculate transactions and avg transaction value
        base_transactions = int(sales_amount / random.uniform(40, 80))
        transactions_count = max(base_transactions, 10)
        avg_transaction_value = sales_amount / transactions_count
        
        record = {
            "date": current_date.strftime("%Y-%m-%d"),
            "sales_amount": round(sales_amount, 2),
            "transactions_count": transactions_count,
            "avg_transaction_value": round(avg_transaction_value, 2),
            "day_of_week": dow,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "weather_category": weather,
            "promotional_campaign": has_promotion
        }
        
        data.append(record)
        current_date += timedelta(days=1)
        day_counter += 1
    
    # Save to CSV
    import csv
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Created sample time series data with {len(data)} daily records at {output_file}")


if __name__ == "__main__":
    main()