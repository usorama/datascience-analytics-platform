#!/usr/bin/env python3
"""
Demo: MLE-STAR Inspired ML Pipeline Optimization

This demonstrates the ablation-driven, component-focused optimization approach
for automated ML pipeline improvement without requiring LLMs.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.mle_star import (
    MLPipelineAnalyzer, PipelineComponent, ComponentType,
    AblationStudyEngine, ComponentImpactAnalyzer,
    ComponentOptimizer, RefinementEngine, OptimizationStrategy,
    MLTechniqueRepository, PerformanceBenchmark
)


def print_section(title: str, emoji: str = ""):
    """Print formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"{emoji} {title.center(78)} {emoji}")
    print(f"{'=' * 80}\n")


def create_sample_pipeline():
    """Create a sample ML pipeline for demonstration."""
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('selector', SelectKBest(f_classif, k=10)),
        ('classifier', RandomForestClassifier(n_estimators=50, random_state=42))
    ])
    return pipeline


def create_pipeline_config():
    """Create pipeline configuration for analysis."""
    config = {
        "scaler": {
            "name": "Standard Scaler",
            "type": "preprocessing",
            "description": "Standardize features to zero mean and unit variance",
            "parameters": {},
            "dependencies": []
        },
        "selector": {
            "name": "Feature Selector",
            "type": "feature_selection", 
            "description": "Select K best features using ANOVA F-test",
            "parameters": {"k": 10},
            "dependencies": ["scaler"]
        },
        "classifier": {
            "name": "Random Forest",
            "type": "model",
            "description": "Random Forest classifier with 50 trees",
            "parameters": {"n_estimators": 50, "max_depth": None},
            "dependencies": ["selector"]
        }
    }
    return config


def demonstrate_pipeline_analysis():
    """Demonstrate ML pipeline analysis capabilities."""
    print_section("Pipeline Analysis", "🔍")
    
    # Create analyzer
    analyzer = MLPipelineAnalyzer()
    
    # Analyze pipeline configuration
    config = create_pipeline_config()
    components = analyzer.analyze_pipeline_config(config)
    
    print(f"✅ Identified {len(components)} pipeline components:")
    for comp_id, component in components.items():
        print(f"  • {component.name} ({component.component_type.value})")
    
    # Get execution order
    execution_order = analyzer.get_execution_order()
    print(f"\n📋 Execution order: {' → '.join(execution_order)}")
    
    # Calculate complexity scores
    complexity_scores = analyzer.calculate_complexity_scores()
    print("\n📊 Complexity scores:")
    for comp_id, score in complexity_scores.items():
        print(f"  • {comp_id}: {score:.2f}")
    
    # Identify bottlenecks
    bottlenecks = analyzer.identify_bottlenecks()
    if bottlenecks:
        print("\n⚠️  Potential bottlenecks:")
        for comp_id, issue in bottlenecks:
            print(f"  • {comp_id}: {issue}")
    
    # Generate report
    report_df = analyzer.generate_component_report()
    print("\n📑 Component Report:")
    print(report_df.to_string(index=False))
    
    return components


def demonstrate_ablation_study(pipeline, X, y, components):
    """Demonstrate ablation study to identify critical components."""
    print_section("Ablation Study", "🧪")
    
    # Create ablation engine
    ablation_engine = AblationStudyEngine(
        performance_metric='accuracy',
        n_cv_folds=3,  # Fewer folds for demo speed
        parallel_execution=False  # Sequential for demo clarity
    )
    
    # Define evaluation function
    def evaluation_function(pipe, X, y, cv_folds):
        from sklearn.model_selection import cross_val_score
        return cross_val_score(pipe, X, y, cv=cv_folds, scoring='accuracy')
    
    # Run ablation study
    print("Running ablation study on each component...")
    ablation_results = ablation_engine.run_ablation_study(
        pipeline, (X, y), components, evaluation_function
    )
    
    # Generate ablation report
    ablation_df = ablation_engine.generate_report()
    print("\n📊 Ablation Study Results:")
    print(ablation_df.to_string(index=False))
    
    # Identify critical components
    critical_components = ablation_engine.identify_critical_components(top_n=3)
    print("\n🎯 Critical Components (by impact):")
    for i, impact in enumerate(critical_components, 1):
        print(f"{i}. {impact.component_id}")
        print(f"   Impact: {impact.impact_score:.4f} | P-value: {impact.statistical_significance:.4f}")
        print(f"   Effect size: {impact.effect_size:.2f} | Priority: {impact.priority}")
        print(f"   Recommendation: {impact.recommendation}")
    
    # Analyze interactions
    impact_analyzer = ComponentImpactAnalyzer(ablation_results)
    optimization_strategy = impact_analyzer.recommend_optimization_strategy()
    
    print("\n💡 Optimization Strategy:")
    print(f"Immediate focus: {optimization_strategy['immediate_focus']}")
    print(f"Estimated improvement potential: {optimization_strategy['estimated_improvement']:.4f}")
    for rec in optimization_strategy['recommendations']:
        print(f"  • {rec}")
    
    return ablation_results


def demonstrate_technique_repository():
    """Demonstrate ML technique repository and recommendations."""
    print_section("ML Technique Repository", "📚")
    
    # Create repository
    repository = MLTechniqueRepository()
    
    # Search for techniques
    print("Searching for feature selection techniques...")
    feature_techniques = repository.search_techniques(
        category=ComponentType.FEATURE_SELECTION
    )
    
    print(f"\n✅ Found {len(feature_techniques)} feature selection techniques:")
    for tech in feature_techniques[:3]:
        print(f"  • {tech.name}: {tech.description}")
        print(f"    Complexity: {tech.complexity} | Interpretability: {tech.interpretability:.1f}")
    
    # Get recommendations
    data_stats = {
        'n_samples': 1000,
        'n_features': 20,
        'feature_types': {'numeric': 15, 'categorical': 5}
    }
    
    requirements = {
        'interpretability': 0.7,
        'max_complexity': 'medium'
    }
    
    print("\n🎯 Technique Recommendations for feature engineering:")
    recommendations = repository.recommend_techniques(
        'feature_engineering', data_stats, requirements
    )
    
    for tech, score in recommendations[:3]:
        print(f"  • {tech.name} (score: {score:.2f})")
        print(f"    {tech.description}")
        print(f"    Pros: {', '.join(tech.pros[:2])}")
    
    return repository


def demonstrate_component_optimization(pipeline, X, y, ablation_results):
    """Demonstrate optimization of individual components."""
    print_section("Component Optimization", "⚡")
    
    # Create optimizer
    optimizer = ComponentOptimizer(
        optimization_strategy=OptimizationStrategy.RANDOM_SEARCH,
        n_iterations=20,  # Fewer iterations for demo
        cv_folds=3
    )
    
    # Define search spaces
    search_spaces = {
        "selector": {
            "selector__k": [5, 10, 15, 20]
        },
        "classifier": {
            "classifier__n_estimators": [50, 100, 200],
            "classifier__max_depth": [5, 10, 20, None],
            "classifier__min_samples_split": [2, 5, 10]
        }
    }
    
    # Optimize the most impactful component
    target_component = "classifier"  # Usually determined by ablation
    
    print(f"Optimizing component: {target_component}")
    
    # Create a dummy component for the demo
    component = PipelineComponent(
        component_id=target_component,
        component_type=ComponentType.MODEL_SELECTION,
        name="Random Forest Classifier",
        description="Optimizing Random Forest hyperparameters"
    )
    
    # Define evaluation function
    def evaluation_function(pipe, X, y):
        from sklearn.model_selection import cross_val_score
        return cross_val_score(pipe, X, y, cv=3, scoring='accuracy')
    
    # Run optimization
    optimization_result = optimizer.optimize_component(
        component,
        pipeline,
        (X, y),
        search_spaces[target_component],
        evaluation_function
    )
    
    print(f"\n✅ Optimization Results:")
    print(f"Original performance: {optimization_result.original_performance:.4f}")
    print(f"Optimized performance: {optimization_result.optimized_performance:.4f}")
    print(f"Improvement: {optimization_result.improvement:.4f} ({optimization_result.relative_improvement:.1%})")
    print(f"Best parameters: {optimization_result.best_params}")
    print(f"Optimization time: {optimization_result.execution_time:.1f}s")
    
    return optimization_result


def demonstrate_refinement_engine(pipeline, X, y, components, ablation_results):
    """Demonstrate the two-loop refinement process."""
    print_section("Two-Loop Refinement Engine", "🔄")
    
    # Create refinement engine
    refinement_engine = RefinementEngine(
        max_outer_iterations=3,  # Fewer iterations for demo
        max_inner_iterations=2,
        convergence_threshold=0.001,
        min_improvement=0.005
    )
    
    # Create component optimizer
    component_optimizer = ComponentOptimizer(
        optimization_strategy=OptimizationStrategy.RANDOM_SEARCH,
        n_iterations=10  # Fewer iterations for demo speed
    )
    
    # Define search spaces for all components
    search_spaces = {
        "scaler": {
            # StandardScaler has no hyperparameters
        },
        "selector": {
            "selector__k": [5, 10, 15, 20]
        },
        "classifier": {
            "classifier__n_estimators": [50, 100, 200],
            "classifier__max_depth": [5, 10, None],
            "classifier__min_samples_split": [2, 5]
        }
    }
    
    # Define evaluation function
    def evaluation_function(pipe, X, y):
        from sklearn.model_selection import cross_val_score
        return cross_val_score(pipe, X, y, cv=3, scoring='accuracy')
    
    print("Starting two-loop refinement process...")
    print("Outer loop: Select components based on ablation impact")
    print("Inner loop: Optimize selected component\n")
    
    # Run refinement
    refinement_results = refinement_engine.run_refinement(
        pipeline,
        (X, y),
        components,
        ablation_results,
        search_spaces,
        evaluation_function,
        component_optimizer
    )
    
    print(f"\n✅ Refinement Complete!")
    print(f"Initial performance: {refinement_results['initial_performance']:.4f}")
    print(f"Final performance: {refinement_results['final_performance']:.4f}")
    print(f"Total improvement: {refinement_results['total_improvement']:.4f}")
    print(f"Relative improvement: {refinement_results['relative_improvement']:.1%}")
    print(f"Total iterations: {refinement_results['iterations']}")
    
    # Show refinement history
    progress_df = refinement_engine.visualize_refinement_progress()
    print("\n📈 Refinement Progress:")
    print(progress_df.to_string(index=False))
    
    return refinement_results


def demonstrate_performance_benchmarking(repository, X, y):
    """Demonstrate technique benchmarking capabilities."""
    print_section("Performance Benchmarking", "📊")
    
    # Create benchmark system
    benchmark = PerformanceBenchmark(repository)
    
    # Compare different scaling techniques
    print("Benchmarking scaling techniques...")
    scaling_techniques = ["standard_scaler", "minmax_scaler", "robust_scaler"]
    
    comparison_df = benchmark.compare_techniques(
        scaling_techniques, X, y, cv_folds=3, scoring='accuracy'
    )
    
    print("\n📊 Scaling Technique Comparison:")
    print(comparison_df.to_string(index=False))
    
    # Find best technique for feature selection
    print("\n🔍 Finding best feature selection technique...")
    from datascience_platform.mle_star.pipeline import ComponentType as MLEComponentType
    
    best_technique_id, best_result = benchmark.find_best_technique(
        MLEComponentType.FEATURE_SELECTION,
        X, y,
        requirements={'max_complexity': 'medium'}
    )
    
    if best_technique_id:
        best_technique = repository.get_technique(best_technique_id)
        print(f"\n✅ Best technique: {best_technique.name}")
        print(f"Performance: {best_result.performance_scores['accuracy_mean']:.4f}")
        print(f"Execution time: {best_result.execution_time:.2f}s")
    
    return benchmark


def main():
    """Run the complete MLE-STAR demo."""
    print_section("MLE-STAR ML Pipeline Optimization Demo", "🚀")
    
    # Generate sample data
    print("Generating sample dataset...")
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_classes=2,
        random_state=42
    )
    
    # Convert to DataFrame for better handling
    X = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    y = pd.Series(y, name="target")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"✅ Dataset: {X_train.shape[0]} training samples, {X_train.shape[1]} features")
    
    # Create initial pipeline
    pipeline = create_sample_pipeline()
    
    # Baseline evaluation
    print("\n📊 Baseline Performance:")
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    baseline_accuracy = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {baseline_accuracy:.4f}")
    
    # Step 1: Pipeline Analysis
    components = demonstrate_pipeline_analysis()
    
    # Step 2: Ablation Study
    ablation_results = demonstrate_ablation_study(
        pipeline, X_train, y_train, components
    )
    
    # Step 3: Technique Repository
    repository = demonstrate_technique_repository()
    
    # Step 4: Component Optimization
    optimization_result = demonstrate_component_optimization(
        pipeline, X_train, y_train, ablation_results
    )
    
    # Step 5: Two-Loop Refinement
    refinement_results = demonstrate_refinement_engine(
        pipeline, X_train, y_train, components, ablation_results
    )
    
    # Step 6: Performance Benchmarking
    benchmark = demonstrate_performance_benchmarking(repository, X_train, y_train)
    
    # Final evaluation
    print_section("Final Results", "🏆")
    
    optimized_pipeline = refinement_results['optimized_pipeline']
    optimized_pipeline.fit(X_train, y_train)
    y_pred_optimized = optimized_pipeline.predict(X_test)
    final_accuracy = accuracy_score(y_test, y_pred_optimized)
    
    print(f"Baseline test accuracy: {baseline_accuracy:.4f}")
    print(f"Optimized test accuracy: {final_accuracy:.4f}")
    print(f"Improvement: {final_accuracy - baseline_accuracy:.4f} ({(final_accuracy/baseline_accuracy - 1)*100:.1f}%)")
    
    print("\n📋 Classification Report (Optimized Model):")
    print(classification_report(y_test, y_pred_optimized))
    
    # Summary
    print_section("Summary", "📝")
    print("The MLE-STAR approach successfully:")
    print("1. ✅ Analyzed the ML pipeline structure")
    print("2. ✅ Identified critical components via ablation")
    print("3. ✅ Selected optimization targets based on impact")
    print("4. ✅ Optimized components using automated search")
    print("5. ✅ Improved pipeline performance systematically")
    print("\nKey insight: Focus optimization efforts on high-impact components")
    print("identified through ablation studies for maximum ROI.")


if __name__ == "__main__":
    main()