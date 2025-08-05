#!/usr/bin/env python3
"""
Test script for the DataScience Platform ML modules

This script performs basic testing of all ML modules to ensure they work correctly.
"""

import pandas as pd
import numpy as np
import sys
import os
import traceback

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_test_dataset():
    """Create a simple test dataset."""
    np.random.seed(42)
    n_samples = 200
    
    data = {
        'numeric_1': np.random.normal(0, 1, n_samples),
        'numeric_2': np.random.normal(5, 2, n_samples),
        'numeric_3': np.random.exponential(2, n_samples),
        'categorical_1': np.random.choice(['A', 'B', 'C'], n_samples),
        'categorical_2': np.random.choice(['X', 'Y'], n_samples, p=[0.7, 0.3]),
        'target_regression': np.random.normal(10, 3, n_samples),
        'target_classification': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    }
    
    # Add some correlation
    data['numeric_correlated'] = data['numeric_1'] * 0.8 + np.random.normal(0, 0.5, n_samples)
    
    # Add some missing values
    missing_indices = np.random.choice(n_samples, size=10, replace=False)
    for idx in missing_indices:
        data['numeric_2'][idx] = np.nan
    
    df = pd.DataFrame(data)
    return df

def test_statistics_engine():
    """Test the StatisticsEngine."""
    print("Testing StatisticsEngine...")
    
    try:
        from datascience_platform.ml import StatisticsEngine
        
        df = create_test_dataset()
        stats_engine = StatisticsEngine()
        
        # Test basic analysis
        results = stats_engine.analyze_dataset(df)
        
        # Check required sections
        required_sections = ['overview', 'descriptive_stats', 'correlations', 'outliers', 'distributions', 'missing_data']
        for section in required_sections:
            assert section in results, f"Missing section: {section}"
        
        # Test insights generation
        insights = stats_engine.get_summary_insights()
        assert isinstance(insights, list), "Insights should be a list"
        assert len(insights) > 0, "Should generate some insights"
        
        print("✅ StatisticsEngine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ StatisticsEngine test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_pattern_detector():
    """Test the PatternDetector."""
    print("Testing PatternDetector...")
    
    try:
        from datascience_platform.ml import PatternDetector
        
        df = create_test_dataset()
        pattern_detector = PatternDetector()
        
        # Test pattern detection
        results = pattern_detector.detect_patterns(df)
        
        # Check required sections
        required_sections = ['clustering', 'anomalies', 'trends', 'feature_interactions', 'data_quality_patterns']
        for section in required_sections:
            assert section in results, f"Missing section: {section}"
        
        # Test insights generation
        insights = pattern_detector.get_pattern_insights()
        assert isinstance(insights, list), "Insights should be a list"
        
        print("✅ PatternDetector tests passed")
        return True
        
    except Exception as e:
        print(f"❌ PatternDetector test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_automl_engine():
    """Test the AutoMLEngine."""
    print("Testing AutoMLEngine...")
    
    try:
        from datascience_platform.ml import AutoMLEngine
        
        df = create_test_dataset()
        automl = AutoMLEngine()
        
        # Test classification
        results = automl.train_model(
            df=df,
            target_column='target_classification',
            task_type='classification',
            time_limit=30  # Short time for testing
        )
        
        # Check required sections
        required_sections = ['framework', 'task_type', 'evaluation', 'feature_importance']
        for section in required_sections:
            assert section in results, f"Missing section: {section}"
        
        assert results['task_type'] == 'classification', "Should detect classification task"
        
        # Test predictions
        predictions = automl.predict(df.head(5))
        assert len(predictions) == 5, "Should return 5 predictions"
        
        # Test insights
        insights = automl.get_model_insights()  
        assert isinstance(insights, list), "Insights should be a list"
        
        print("✅ AutoMLEngine tests passed")
        return True
        
    except Exception as e:
        print(f"❌ AutoMLEngine test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_insight_generator():
    """Test the InsightGenerator."""
    print("Testing InsightGenerator...")
    
    try:
        from datascience_platform.ml import InsightGenerator
        
        df = create_test_dataset()
        insight_generator = InsightGenerator()
        
        # Test comprehensive insights
        results = insight_generator.generate_comprehensive_insights(
            df=df,
            target_column='target_classification',
            business_context='test_analysis'
        )
        
        # Check required sections
        required_sections = ['dataset_overview', 'key_insights', 'actionable_recommendations', 'data_quality_assessment']
        for section in required_sections:
            assert section in results, f"Missing section: {section}"
        
        # Test report export
        report = insight_generator.export_insights_report(results)
        assert isinstance(report, str), "Report should be a string"
        assert len(report) > 100, "Report should have substantial content"
        
        print("✅ InsightGenerator tests passed")
        return True
        
    except Exception as e:
        print(f"❌ InsightGenerator test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_model_explainer():
    """Test the ModelExplainer."""
    print("Testing ModelExplainer...")
    
    try:
        from datascience_platform.ml import ModelExplainer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        df = create_test_dataset()
        
        # Prepare data for sklearn model
        X = df[['numeric_1', 'numeric_2', 'numeric_3']].fillna(0)
        y = df['target_classification']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Train a simple model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Test explainer
        explainer = ModelExplainer()
        explanations = explainer.explain_model(
            model=model,
            X_train=X_train,
            y_train=y_train,
            X_test=X_test.head(3)
        )
        
        # Check required sections
        required_sections = ['global_explanations', 'feature_importance', 'model_behavior']
        for section in required_sections:
            assert section in explanations, f"Missing section: {section}"
        
        # Test single prediction explanation
        single_explanation = explainer.explain_prediction(X_test.iloc[0])
        assert 'prediction' in single_explanation, "Should include prediction"
        
        # Test insights
        insights = explainer.get_explanation_summary()
        assert isinstance(insights, list), "Insights should be a list"
        
        print("✅ ModelExplainer tests passed")
        return True
        
    except Exception as e:
        print(f"❌ ModelExplainer test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_module_imports():
    """Test that all modules can be imported correctly."""
    print("Testing module imports...")
    
    try:
        # Test individual imports
        from datascience_platform.ml import StatisticsEngine
        from datascience_platform.ml import PatternDetector
        from datascience_platform.ml import AutoMLEngine
        from datascience_platform.ml import InsightGenerator
        from datascience_platform.ml import ModelExplainer
        
        # Test package import
        import datascience_platform.ml as ml
        
        # Test __all__ imports (at module level)
        # from datascience_platform.ml import *  # Commented out due to function scope
        
        print("✅ All module imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Module import test failed: {str(e)}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and return summary."""
    print("=" * 60)
    print("RUNNING ML MODULES TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_module_imports),
        ("StatisticsEngine", test_statistics_engine),
        ("PatternDetector", test_pattern_detector),
        ("AutoMLEngine", test_automl_engine),
        ("InsightGenerator", test_insight_generator),
        ("ModelExplainer", test_model_explainer)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\\n{test_name}:")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:<20}: {status}")
    
    print(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ML modules are working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the errors above.")
        return False

def main():
    """Main test function."""
    try:
        success = run_all_tests()
        
        if success:
            print("\\n" + "=" * 60)
            print("NEXT STEPS")
            print("=" * 60)
            print("1. Run the example usage script: python example_ml_usage.py")
            print("2. Try the modules with your own data")
            print("3. Install optional dependencies for enhanced features:")
            print("   - pip install autogluon.tabular  # For advanced AutoML")
            print("   - pip install shap               # For model explanations")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"\\nUnexpected error during testing: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)