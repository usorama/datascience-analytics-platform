#!/usr/bin/env python3
"""
Example usage of the DataScience Platform ML Insights Generation Engine

This script demonstrates how to use all the ML modules together to generate
comprehensive insights from a dataset.
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datascience_platform.ml import (
    StatisticsEngine,
    PatternDetector,
    AutoMLEngine,
    InsightGenerator,
    ModelExplainer
)

def create_sample_dataset():
    """Create a sample dataset for demonstration."""
    np.random.seed(42)
    n_samples = 1000
    
    # Generate synthetic data
    data = {
        'customer_id': range(1, n_samples + 1),
        'age': np.random.normal(35, 12, n_samples).clip(18, 80),
        'income': np.random.lognormal(10, 0.5, n_samples),
        'credit_score': np.random.normal(650, 100, n_samples).clip(300, 850),
        'months_since_last_purchase': np.random.poisson(6, n_samples),
        'total_purchases': np.random.poisson(15, n_samples),
        'average_purchase_amount': np.random.gamma(2, 50, n_samples),
        'is_premium_customer': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_samples),
        'satisfaction_score': np.random.uniform(1, 10, n_samples),
    }
    
    # Add some relationships and patterns
    # Higher income tends to lead to higher purchase amounts
    data['average_purchase_amount'] = data['average_purchase_amount'] + data['income'] * 0.001
    
    # Premium customers have higher satisfaction
    data['satisfaction_score'] = np.where(
        data['is_premium_customer'] == 1,
        data['satisfaction_score'] + 2,
        data['satisfaction_score']
    ).clip(1, 10)
    
    # Add some missing values
    missing_indices = np.random.choice(n_samples, size=int(0.05 * n_samples), replace=False)
    for idx in missing_indices:
        data['satisfaction_score'][idx] = np.nan
    
    # Add time series component
    start_date = datetime.now() - timedelta(days=n_samples)
    data['purchase_date'] = [start_date + timedelta(days=i) for i in range(n_samples)]
    
    # Create target variable (customer will churn)
    churn_probability = (
        0.1 +  # Base probability
        0.3 * (data['satisfaction_score'] < 5) +  # Low satisfaction increases churn
        0.2 * (data['months_since_last_purchase'] > 10) +  # Long time since purchase
        -0.1 * data['is_premium_customer']  # Premium customers less likely to churn
    )
    churn_probability = np.clip(churn_probability, 0, 1)
    data['will_churn'] = np.random.binomial(1, churn_probability, n_samples)
    
    df = pd.DataFrame(data)
    
    # Convert data types
    df['age'] = df['age'].astype(int)
    df['credit_score'] = df['credit_score'].astype(int)
    df['income'] = df['income'].round(2)
    df['average_purchase_amount'] = df['average_purchase_amount'].round(2)
    df['satisfaction_score'] = df['satisfaction_score'].round(1)
    
    return df

def demonstrate_statistics_engine():
    """Demonstrate the StatisticsEngine."""
    print("\\n" + "="*60)
    print("STATISTICAL ANALYSIS DEMONSTRATION")
    print("="*60)
    
    # Create sample data
    df = create_sample_dataset()
    print(f"Created sample dataset with shape: {df.shape}")
    
    # Initialize and run statistical analysis
    stats_engine = StatisticsEngine()
    results = stats_engine.analyze_dataset(df)
    
    # Display key results
    print("\\nDataset Overview:")
    overview = results['overview']
    print(f"- Shape: {overview['shape']}")
    print(f"- Memory usage: {overview['memory_usage'] / (1024*1024):.2f} MB")
    print(f"- Numerical columns: {len(overview['columns']['numerical'])}")
    print(f"- Categorical columns: {len(overview['columns']['categorical'])}")
    
    print("\\nMissing Data Analysis:")
    missing = results['missing_data']
    print(f"- Total missing: {missing['missing_percentage']:.2f}%")
    
    print("\\nStrong Correlations Found:")
    correlations = results['correlations']['strong_correlations']
    for corr in correlations[:3]:  # Show top 3
        print(f"- {corr['column1']} ↔ {corr['column2']}: {corr['correlation']:.3f}")
    
    print("\\nKey Statistical Insights:")
    insights = stats_engine.get_summary_insights()
    for insight in insights:
        print(f"- {insight}")
    
    return df, results

def demonstrate_pattern_detector():
    """Demonstrate the PatternDetector."""
    print("\\n" + "="*60)
    print("PATTERN DETECTION DEMONSTRATION")
    print("="*60)
    
    df = create_sample_dataset()
    
    # Initialize and run pattern detection
    pattern_detector = PatternDetector()
    results = pattern_detector.detect_patterns(
        df, 
        time_column='purchase_date',
        target_column='will_churn'
    )
    
    # Display clustering results
    print("\\nClustering Analysis:")
    clustering = results['clustering']
    if 'kmeans' in clustering and 'n_clusters' in clustering['kmeans']:
        kmeans = clustering['kmeans']
        print(f"- Optimal clusters: {kmeans['n_clusters']}")
        print(f"- Silhouette score: {kmeans['silhouette_score']:.3f}")
        print(f"- Cluster sizes: {kmeans['cluster_sizes']}")
    
    # Display anomaly detection
    print("\\nAnomaly Detection:")
    anomalies = results['anomalies']
    if 'isolation_forest' in anomalies:
        iso_forest = anomalies['isolation_forest']
        print(f"- Anomaly percentage: {iso_forest['anomaly_percentage']:.2f}%")
        print(f"- Anomalies detected: {iso_forest['anomaly_count']}")
    
    # Display trend analysis
    print("\\nTrend Analysis:")
    trends = results['trends']
    for col, trend_info in list(trends.items())[:3]:  # Show first 3 columns
        if isinstance(trend_info, dict) and 'linear_trend' in trend_info:
            linear = trend_info['linear_trend']
            print(f"- {col}: {linear['trend_direction']} trend (strength: {linear['trend_strength']})")
    
    print("\\nPattern Insights:")
    insights = pattern_detector.get_pattern_insights()
    for insight in insights:
        print(f"- {insight}")
    
    return results

def demonstrate_automl_engine():
    """Demonstrate the AutoMLEngine."""
    print("\\n" + "="*60)
    print("AUTOML DEMONSTRATION")
    print("="*60)
    
    df = create_sample_dataset()
    
    # Initialize AutoML engine
    automl_engine = AutoMLEngine()
    
    # Train a classification model to predict churn
    print("Training classification model to predict customer churn...")
    results = automl_engine.train_model(
        df=df,
        target_column='will_churn',
        task_type='classification',
        time_limit=60,  # 1 minute limit for demo
        exclude_columns=['customer_id', 'purchase_date']
    )
    
    print("\\nModel Training Results:")
    print(f"- Framework: {results['framework']}")
    print(f"- Task type: {results['task_type']}")
    print(f"- Data shape: {results['data_shape']}")
    
    print("\\nModel Performance:")
    evaluation = results['evaluation']
    if 'accuracy' in evaluation:
        print(f"- Accuracy: {evaluation['accuracy']:.3f}")
    if 'f1' in evaluation:
        print(f"- F1-score: {evaluation['f1']:.3f}")
    if 'auc' in evaluation:
        print(f"- AUC: {evaluation['auc']:.3f}")
    
    print("\\nTop Feature Importance:")
    feature_importance = results['feature_importance']
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
    for feature, importance in sorted_features[:5]:
        print(f"- {feature}: {importance:.3f}")
    
    print("\\nAutoML Insights:")
    insights = automl_engine.get_model_insights()
    for insight in insights:
        print(f"- {insight}")
    
    return automl_engine, results

def demonstrate_insight_generator():
    """Demonstrate the InsightGenerator."""
    print("\\n" + "="*60)
    print("COMPREHENSIVE INSIGHT GENERATION DEMONSTRATION")
    print("="*60)
    
    df = create_sample_dataset()
    
    # Initialize insight generator
    insight_generator = InsightGenerator()
    
    # Generate comprehensive insights
    print("Generating comprehensive insights...")
    insights_result = insight_generator.generate_comprehensive_insights(
        df=df,
        target_column='will_churn',
        time_column='purchase_date',
        business_context='customer retention and churn prediction'
    )
    
    print("\\nDataset Overview:")
    overview = insights_result['dataset_overview']
    print(overview['summary'])
    
    print("\\nData Quality Assessment:")
    quality = insights_result['data_quality_assessment']
    print(f"- Overall score: {quality['overall_score']:.1f}/100 ({quality['assessment']})")
    
    print("\\nKey Insights:")
    key_insights = insights_result['key_insights']
    for i, insight in enumerate(key_insights[:5], 1):  # Show top 5
        print(f"{i}. {insight['title']}")
        print(f"   {insight['description']}")
    
    print("\\nActionable Recommendations:")
    recommendations = insights_result['actionable_recommendations']
    for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
        print(f"{i}. {rec['title']}")
        print(f"   {rec['description']}")
        if rec.get('actions'):
            print(f"   Actions: {', '.join(rec['actions'][:2])}...")
    
    print("\\nNext Steps:")
    next_steps = insights_result['next_steps']
    for i, step in enumerate(next_steps, 1):
        print(f"{i}. {step}")
    
    # Export report
    report = insight_generator.export_insights_report(insights_result, format='markdown')
    with open('insights_report.md', 'w') as f:
        f.write(report)
    print("\\nDetailed report exported to 'insights_report.md'")
    
    return insights_result

def demonstrate_model_explainer():
    """Demonstrate the ModelExplainer."""
    print("\\n" + "="*60)
    print("MODEL EXPLAINER DEMONSTRATION")
    print("="*60)
    
    df = create_sample_dataset()
    
    # First, train a simple model for explanation
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
    
    # Prepare data
    X = df.drop(['will_churn', 'customer_id', 'purchase_date', 'region'], axis=1)
    y = df['will_churn']
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    print(f"Trained RandomForest model with accuracy: {model.score(X_test, y_test):.3f}")
    
    # Initialize model explainer
    explainer = ModelExplainer()
    
    # Generate explanations
    print("\\nGenerating model explanations...")
    explanations = explainer.explain_model(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test.head(5)  # Explain first 5 test instances
    )
    
    print("\\nModel Complexity Assessment:")
    complexity = explanations['global_explanations']['model_complexity']
    print(f"- Assessment: {complexity['assessment']}")
    print(f"- Number of estimators: {complexity.get('n_estimators', 'N/A')}")
    
    print("\\nFeature Importance (Top 5):")
    feature_importance = explanations['feature_importance']
    if 'summary' in feature_importance:
        ranking = feature_importance['summary']['ranking']
        for i, (feature, importance) in enumerate(ranking[:5], 1):
            print(f"{i}. {feature}: {importance:.3f}")
    
    print("\\nModel Behavior Summary:")
    behavior_summary = explanations['global_explanations']['model_behavior_summary']
    print(f"- {behavior_summary}")
    
    # Explain a single prediction
    print("\\nSingle Prediction Explanation:")
    single_instance = X_test.iloc[0]
    prediction_explanation = explainer.explain_prediction(single_instance)
    print(f"- Prediction: {prediction_explanation['prediction']:.3f}")
    print("- Top contributing features:")
    
    contributions = prediction_explanation.get('feature_contributions', [])
    for contrib in contributions[:3]:
        print(f"  • {contrib['feature']}: {contrib['contribution']:.3f}")
    
    print("\\nExplainer Insights:")
    insights = explainer.get_explanation_summary()
    for insight in insights:
        print(f"- {insight}")
    
    return explanations

def main():
    """Main demonstration function."""
    print("DataScience Platform ML Insights Generation Engine Demo")
    print("=" * 60)
    
    try:
        # Run all demonstrations
        df, stats_results = demonstrate_statistics_engine()
        pattern_results = demonstrate_pattern_detector()
        automl_engine, ml_results = demonstrate_automl_engine()
        insights_result = demonstrate_insight_generator()
        explanations = demonstrate_model_explainer()
        
        print("\\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\\nAll ML modules have been demonstrated!")
        print("\\nGenerated files:")
        print("- insights_report.md: Comprehensive insights report")
        
        print("\\nNext steps:")
        print("1. Review the generated insights report")
        print("2. Customize the modules for your specific use case")
        print("3. Integrate with your data pipeline")
        print("4. Set up automated insight generation")
        
    except Exception as e:
        print(f"\\nError during demonstration: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if 'automl_engine' in locals():
            automl_engine.cleanup()

if __name__ == "__main__":
    main()