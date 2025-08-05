#!/usr/bin/env python3
"""Example Analytics Pipeline Script

Demonstrates how to use the DataScience Analytics Platform to:
1. Load a CSV file
2. Run the complete analysis pipeline
3. Generate a dashboard
4. Show how all components work together

Usage:
    python example_pipeline.py [path_to_csv_file]
"""

import sys
from pathlib import Path

# Add the src directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.orchestrator.pipeline import AnalyticsPipeline, PipelineConfig
from datascience_platform.core.exceptions import DataSciencePlatformError


def create_sample_data():
    """Create a sample dataset for demonstration."""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    print("📈 Creating sample dataset...")
    
    # Generate sample sales data
    np.random.seed(42)
    n_records = 1000
    
    # Date range for the last 2 years
    start_date = datetime.now() - timedelta(days=730)
    dates = [start_date + timedelta(days=i) for i in range(n_records)]
    
    # Sample data with realistic patterns
    data = {
        'date': dates,
        'sales_amount': np.random.normal(5000, 1500, n_records) + 
                       np.sin(np.arange(n_records) * 2 * np.pi / 365) * 1000,  # Seasonal pattern
        'customer_count': np.random.poisson(50, n_records),
        'product_category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], n_records, 
                                           p=[0.3, 0.25, 0.2, 0.25]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'marketing_spend': np.random.exponential(500, n_records),
        'customer_satisfaction': np.random.normal(4.2, 0.8, n_records).clip(1, 5),
        'temperature': np.random.normal(20, 10, n_records),  # Weather correlation
    }
    
    # Add some correlations
    # Higher marketing spend should lead to higher sales (with noise)
    data['sales_amount'] += data['marketing_spend'] * 0.5 + np.random.normal(0, 200, n_records)
    
    # Temperature affects sales for certain categories
    electronics_mask = np.array(data['product_category']) == 'Electronics'
    data['sales_amount'] += np.where(electronics_mask, data['temperature'] * -20, data['temperature'] * 10)
    
    # Ensure positive sales
    data['sales_amount'] = np.maximum(data['sales_amount'], 100)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some missing values to make it realistic
    missing_indices = np.random.choice(n_records, size=int(n_records * 0.05), replace=False)
    df.loc[missing_indices, 'customer_satisfaction'] = np.nan
    
    # Save to CSV
    output_file = Path("sample_sales_data.csv")
    df.to_csv(output_file, index=False)
    
    print(f"✅ Sample dataset created: {output_file}")
    print(f"📊 Dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"📅 Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    return output_file


def demonstrate_basic_pipeline(data_file: Path):
    """Demonstrate basic pipeline functionality."""
    print("\n🚀 Starting Basic Analytics Pipeline")
    print("=" * 50)
    
    try:
        # Create pipeline configuration
        config = PipelineConfig(
            data_source=data_file,
            target_column="sales_amount",
            time_column="date",
            business_context="sales",
            output_dir=Path("./pipeline_output_basic"),
            validate_data=True,
            ml_enabled=True,
            ml_time_limit=60,  # Shorter time for demo
            generate_dashboard=True,
            dashboard_theme="light",
            dashboard_title="Sales Analytics Dashboard - Basic Demo",
            save_intermediate=True
        )
        
        # Create pipeline
        pipeline = AnalyticsPipeline(config)
        
        # Add progress callback
        def progress_callback(progress_data):
            status = progress_data["status"]
            progress_info = progress_data["progress"]
            
            current_stage = progress_info.get("current_stage")
            overall_progress = progress_info.get("overall_progress", 0)
            
            if current_stage:
                stage_message = progress_info.get("stage_messages", {}).get(current_stage, "")
                print(f"  [{overall_progress:.1f}%] {current_stage.replace('_', ' ').title()}: {stage_message}")
        
        pipeline.add_progress_callback(progress_callback)
        
        # Execute pipeline
        results = pipeline.execute()
        
        # Display results
        print("\n✅ Basic Pipeline Completed Successfully!")
        print(f"📊 Data Shape: {results['data_shape'][0]:,} rows × {results['data_shape'][1]} columns")
        
        if results.get('validation_results'):
            validation = results['validation_results']
            status = "✅ PASSED" if validation['is_valid'] else "❌ FAILED"
            print(f"🔍 Validation: {status}")
            if not validation['is_valid']:
                print(f"  Errors: {len(validation['errors'])}")
                print(f"  Warnings: {len(validation['warnings'])}")
        
        if results.get('analysis_results'):
            analysis = results['analysis_results']
            key_insights = analysis.get('key_insights', [])
            print(f"💡 Key Insights: {len(key_insights)} generated")
            
            # Show first few insights
            for i, insight in enumerate(key_insights[:3], 1):
                print(f"  {i}. {insight.get('title', 'Untitled')}")
        
        if results.get('dashboard_generated'):
            print("📈 Dashboard: Generated successfully")
        
        print(f"📁 Output: {results['output_directory']}")
        
        return results
        
    except DataSciencePlatformError as e:
        print(f"❌ Pipeline failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def demonstrate_advanced_pipeline(data_file: Path):
    """Demonstrate advanced pipeline with custom options."""
    print("\n🚀 Starting Advanced Analytics Pipeline")
    print("=" * 50)
    
    try:
        # Create advanced configuration
        config = PipelineConfig(
            data_source=data_file,
            target_column="sales_amount",
            time_column="date",
            business_context="sales and marketing analytics",
            output_dir=Path("./pipeline_output_advanced"),
            read_options={
                "use_polars": False,  # Use pandas for this demo
                "encoding": "utf-8"
            },
            validate_data=True,
            strict_validation=True,
            sample_size=500,  # Analyze only 500 records for faster demo
            ml_enabled=True,
            ml_time_limit=90,
            generate_dashboard=True,
            dashboard_theme="dark",
            dashboard_title="Advanced Sales Analytics - Dark Theme",
            save_intermediate=True,
            export_formats=["html", "pdf"]
        )
        
        # Create pipeline
        pipeline = AnalyticsPipeline(config)
        
        # Add detailed progress callback
        def detailed_progress_callback(progress_data):
            status = progress_data["status"]
            progress_info = progress_data["progress"]
            
            current_stage = progress_info.get("current_stage")
            overall_progress = progress_info.get("overall_progress", 0)
            elapsed_time = progress_info.get("elapsed_time", 0)
            
            if current_stage:
                stage_message = progress_info.get("stage_messages", {}).get(current_stage, "")
                stage_progress = progress_info.get("stage_progress", {}).get(current_stage, 0)
                
                print(f"  [{overall_progress:.1f}%] {current_stage.replace('_', ' ').title()} "
                      f"({stage_progress:.1f}%) - {stage_message} [{elapsed_time:.1f}s]")
        
        pipeline.add_progress_callback(detailed_progress_callback)
        
        # Execute pipeline
        results = pipeline.execute()
        
        # Display detailed results
        print("\n✅ Advanced Pipeline Completed Successfully!")
        print(f"📊 Data Shape: {results['data_shape'][0]:,} rows × {results['data_shape'][1]} columns")
        print(f"⏱️ Execution Time: {results['progress']['elapsed_time']:.2f} seconds")
        
        if results.get('analysis_results'):
            analysis = results['analysis_results']
            
            # Show key insights
            key_insights = analysis.get('key_insights', [])
            print(f"\n💡 Key Insights ({len(key_insights)}):")
            for i, insight in enumerate(key_insights, 1):
                print(f"  {i}. {insight.get('title', 'Untitled')}")
                print(f"     {insight.get('description', 'No description')[:100]}...")
            
            # Show data quality assessment
            quality = analysis.get('data_quality_assessment', {})
            if quality:
                print(f"\n🔍 Data Quality: {quality.get('overall_score', 0):.1f}/100 ({quality.get('assessment', 'Unknown')})")
            
            # Show recommendations
            recommendations = analysis.get('actionable_recommendations', [])
            print(f"\n🎯 Recommendations ({len(recommendations)}):")
            for i, rec in enumerate(recommendations[:3], 1):  # Show first 3
                print(f"  {i}. {rec.get('title', 'Untitled')}")
        
        print(f"\n📁 Output Directory: {results['output_directory']}")
        
        # List generated files
        output_path = Path(results['output_directory'])
        if output_path.exists():
            files = list(output_path.glob("*"))
            if files:
                print("\n📄 Generated Files:")
                for file in files:
                    size = file.stat().st_size / 1024  # KB
                    print(f"  • {file.name} ({size:.1f} KB)")
        
        return results
        
    except DataSciencePlatformError as e:
        print(f"❌ Pipeline failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


def demonstrate_component_integration():
    """Demonstrate how individual components work together."""
    print("\n🔧 Component Integration Demonstration")
    print("=" * 50)
    
    try:
        # 1. Data Loading Component
        print("\n1️⃣ Data Loading (ETL Reader)")
        from datascience_platform.etl.reader import DataReader, ReadOptions
        
        data_file = Path("sample_sales_data.csv")
        if not data_file.exists():
            data_file = create_sample_data()
        
        read_options = ReadOptions(use_polars=False, encoding="utf-8")
        reader = DataReader(read_options)
        
        file_info = reader.get_file_info(data_file)
        print(f"  📊 File Info: {file_info['rows']} rows, {file_info['columns']} columns, {file_info['size_mb']} MB")
        
        data = reader.read(data_file)
        print(f"  ✅ Data loaded: {data.shape}")
        
        # 2. Data Validation Component  
        print("\n2️⃣ Data Validation")
        from datascience_platform.etl.validator import validate_dataframe
        
        validation_result = validate_dataframe(data, strict_mode=False)
        status = "✅ PASSED" if validation_result.is_valid else "❌ FAILED"
        print(f"  {status} - {len(validation_result.errors)} errors, {len(validation_result.warnings)} warnings")
        
        # 3. ML Analysis Component
        print("\n3️⃣ ML Analysis (Insights Generator)")
        from datascience_platform.ml.insights import InsightGenerator
        
        insight_generator = InsightGenerator()
        analysis_results = insight_generator.generate_comprehensive_insights(
            df=data,
            target_column="sales_amount",
            time_column="date", 
            business_context="sales"
        )
        
        key_insights = analysis_results.get('key_insights', [])
        print(f"  💡 Generated {len(key_insights)} key insights")
        
        # 4. Dashboard Generation Component
        print("\n4️⃣ Dashboard Generation")
        from datascience_platform.dashboard.generator import DashboardGenerator
        
        dashboard_gen = DashboardGenerator(theme="light")
        dashboard_gen.set_config(
            title="Component Integration Demo",
            description="Demonstrating component integration"
        )
        
        # Add some basic components
        dashboard_gen.add_kpi_card(
            title="Total Records",
            value=len(data),
            subtitle="Dataset Size"
        )
        
        # Add a simple chart
        numeric_cols = data.select_dtypes(include=['number']).columns[:2]
        if len(numeric_cols) >= 2:
            dashboard_gen.add_chart(
                chart_type="scatter_chart",
                data=data[numeric_cols].head(100),
                chart_id="sample_scatter",
                title=f"{numeric_cols[0]} vs {numeric_cols[1]}",
                x_column=numeric_cols[0],
                y_column=numeric_cols[1]
            )
        
        # Generate dashboard
        output_file = "component_demo_dashboard.html"
        dashboard_html = dashboard_gen.generate_html(output_file)
        print(f"  📈 Dashboard generated: {output_file}")
        
        print("\n✅ All components integrated successfully!")
        print("\n🔗 Component Flow:")
        print("  Data Reader → Data Validator → Insight Generator → Dashboard Generator")
        
    except Exception as e:
        print(f"❌ Component integration failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demonstration function."""
    print("🎆 DataScience Analytics Platform - Example Pipeline")
    print("=" * 60)
    
    # Check if data file is provided as argument
    if len(sys.argv) > 1:
        data_file = Path(sys.argv[1])
        if not data_file.exists():
            print(f"❌ Data file not found: {data_file}")
            return
    else:
        # Create sample data
        data_file = create_sample_data()
    
    print(f"\n📁 Using data file: {data_file}")
    
    # Run demonstrations
    try:
        # 1. Component Integration Demo
        demonstrate_component_integration()
        
        # 2. Basic Pipeline Demo
        basic_results = demonstrate_basic_pipeline(data_file)
        
        # 3. Advanced Pipeline Demo
        advanced_results = demonstrate_advanced_pipeline(data_file)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎆 Demo Completed Successfully!")
        print("\n📄 Check the generated files:")
        print("  • sample_sales_data.csv - Sample dataset")
        print("  • component_demo_dashboard.html - Component demo dashboard")
        print("  • ./pipeline_output_basic/ - Basic pipeline results")
        print("  • ./pipeline_output_advanced/ - Advanced pipeline results")
        
        print("\n🚀 Next Steps:")
        print("  1. Open the generated dashboards in your browser")
        print("  2. Check the insights reports (*.md files)")
        print("  3. Try the CLI: python -m datascience_platform analyze your_data.csv")
        print("  4. Start the API server: python -m datascience_platform server")
        
    except KeyboardInterrupt:
        print("\n❌ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
