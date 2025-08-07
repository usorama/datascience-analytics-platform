#!/usr/bin/env python3
"""
Azure DevOps Analytics Demo

This script demonstrates how to use the DataScience Analytics Platform
with ADO-specific enhancements including:
- Quantified Value Framework (QVF) with AHP
- Comprehensive Agile metrics
- Objective prioritization
- Data simulation for testing
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado import (
    ADOAnalyzer, ADODataSimulator, AHPConfiguration, AHPCriterion
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"{title.center(60)}")
    print(f"{'=' * 60}\n")


def demo_basic_analysis():
    """Demonstrate basic ADO analysis with simulated data."""
    print_section("Basic ADO Analysis Demo")
    
    # Create analyzer with default AHP configuration
    analyzer = ADOAnalyzer()
    
    # Load simulated data (balanced team scenario)
    print("Loading simulated ADO data (balanced team scenario)...")
    work_items = analyzer.load_simulated_data(scenario='balanced')
    print(f"✓ Loaded {len(work_items)} work items")
    
    # Configure AHP with preferences
    print("\nConfiguring AHP with default preferences...")
    ahp_config = analyzer.configure_ahp(preferences={
        'business_value': 5,      # Most important
        'roi_efficiency': 4,      # Very important
        'strategic_alignment': 3, # Important
        'risk_complexity': 2,     # Somewhat important
        'team_confidence': 3      # Important
    })
    
    print(f"✓ AHP weights calculated:")
    for criterion, weight in ahp_config['weights'].items():
        print(f"  - {criterion}: {weight:.3f}")
    print(f"✓ Consistency Ratio: {ahp_config['consistency_ratio']:.3f} (Consistent: {ahp_config['is_consistent']})")
    
    # Run analysis
    print("\nRunning comprehensive analysis...")
    results = analyzer.analyze(generate_dashboard=True)
    
    # Display key results
    print("\n📊 ANALYSIS SUMMARY:")
    summary = results['summary']
    print(f"  Total Work Items: {summary['total_items']}")
    print(f"  Completion Rate: {summary['completion_rate']:.1f}%")
    print(f"  Total Story Points: {summary['total_story_points']}")
    
    print("\n🎯 TOP 5 PRIORITIES (by AHP Score):")
    for item in analyzer.top_priorities[:5]:
        print(f"  {item['rank']}. [{item['work_item_id']}] {item['title'][:50]}...")
        print(f"     Type: {item['type']}, AHP Score: {item['ahp_score']:.3f}")
    
    print("\n⚠️  ITEMS TO DEFER:")
    for item in analyzer.defer_candidates[:3]:
        print(f"  - [{item['work_item_id']}] {item['title'][:50]}...")
        print(f"    AHP Score: {item['ahp_score']:.3f}, Reason: {item['reason']}")
    
    print("\n📈 PREDICTABILITY METRICS:")
    predictability = results['predictability']
    print(f"  Average Velocity: {predictability['average_velocity']:.1f} story points/PI")
    print(f"  Velocity Trend: {predictability['velocity_trend']}")
    print(f"  Average Predictability: {predictability['average_predictability']:.1f}%")
    
    print("\n💡 KEY INSIGHTS:")
    for insight in results['insights'][:3]:
        print(f"  - {insight['title']} [{insight['severity'].upper()}]")
        print(f"    {insight['description']}")
        print(f"    → {insight['recommendation']}")
    
    if 'dashboard_path' in results:
        print(f"\n✅ Dashboard generated: {results['dashboard_path']}")


def demo_scenario_comparison():
    """Compare different team scenarios."""
    print_section("Team Scenario Comparison")
    
    scenarios = {
        'high_performing': "High-performing team (90% completion)",
        'struggling': "Struggling team (55% completion)",
        'growing': "Growing team (70% completion)"
    }
    
    scenario_results = {}
    
    for scenario_key, description in scenarios.items():
        print(f"\nAnalyzing: {description}")
        
        # Create analyzer
        analyzer = ADOAnalyzer()
        
        # Load scenario data
        analyzer.load_simulated_data(scenario=scenario_key)
        
        # Configure AHP
        analyzer.configure_ahp(preferences={
            'business_value': 5,
            'roi_efficiency': 4,
            'strategic_alignment': 3,
            'risk_complexity': 2,
            'team_confidence': 3
        })
        
        # Run analysis
        results = analyzer.analyze(generate_dashboard=False)
        
        # Store key metrics
        scenario_results[scenario_key] = {
            'description': description,
            'completion_rate': results['summary']['completion_rate'],
            'predictability': results['predictability']['average_predictability'],
            'velocity': results['predictability']['average_velocity'],
            'insights_count': len(results['insights'])
        }
        
        print(f"  ✓ Completion: {results['summary']['completion_rate']:.1f}%")
        print(f"  ✓ Predictability: {results['predictability']['average_predictability']:.1f}%")
        print(f"  ✓ Insights generated: {len(results['insights'])}")
    
    # Compare scenarios
    print("\n📊 SCENARIO COMPARISON:")
    print(f"{'Scenario':<20} {'Completion':<12} {'Predictability':<15} {'Velocity':<10}")
    print("-" * 60)
    for key, metrics in scenario_results.items():
        print(f"{key:<20} {metrics['completion_rate']:>10.1f}% {metrics['predictability']:>13.1f}% {metrics['velocity']:>8.1f}")


def demo_custom_ahp_criteria():
    """Demonstrate custom AHP criteria configuration."""
    print_section("Custom AHP Criteria Demo")
    
    # Create custom AHP configuration
    custom_criteria = [
        AHPCriterion(
            name="customer_impact",
            description="Direct impact on customer experience",
            weight=0.0,
            data_source="business_value_normalized",  # Reuse existing field
            higher_is_better=True,
            normalization_method="minmax"
        ),
        AHPCriterion(
            name="technical_debt",
            description="Reduction in technical debt",
            weight=0.0,
            data_source="complexity_score",
            higher_is_better=False,  # Lower complexity = less debt
            normalization_method="minmax"
        ),
        AHPCriterion(
            name="time_criticality",
            description="Urgency based on target date",
            weight=0.0,
            data_source="days_until_target",  # Custom calculated field
            higher_is_better=False,  # Fewer days = more urgent
            normalization_method="minmax"
        )
    ]
    
    custom_config = AHPConfiguration(criteria=custom_criteria)
    
    # Create analyzer with custom configuration
    analyzer = ADOAnalyzer(ahp_config=custom_config)
    
    # Load data
    print("Loading simulated data...")
    work_items = analyzer.load_simulated_data(
        scenario='custom',
        num_pis=2,
        num_epics=5,
        completion_rate=0.8
    )
    
    # Add custom field calculations
    for item in work_items:
        # Calculate days until target
        if item.target_date:
            days_until = (item.target_date - datetime.now()).days
            item.custom_fields['days_until_target'] = max(0, days_until)
        else:
            item.custom_fields['days_until_target'] = 365  # Default far future
    
    # Configure AHP with custom preferences
    print("\nConfiguring custom AHP criteria...")
    ahp_config = analyzer.configure_ahp(preferences={
        'customer_impact': 5,     # Most important
        'technical_debt': 3,      # Important
        'time_criticality': 4     # Very important
    })
    
    print(f"\n✓ Custom criteria weights:")
    for criterion, weight in ahp_config['weights'].items():
        print(f"  - {criterion}: {weight:.3f}")
    
    # Run analysis
    results = analyzer.analyze(generate_dashboard=False)
    
    print("\n🎯 Top priorities with custom criteria:")
    for item in analyzer.top_priorities[:5]:
        print(f"  {item['rank']}. [{item['work_item_id']}] {item['title'][:40]}...")
        print(f"     Scores: {', '.join(f'{k}={v:.2f}' for k, v in item['criterion_scores'].items())}")


def demo_data_export():
    """Demonstrate exporting analysis data."""
    print_section("Data Export Demo")
    
    # Create simulator
    simulator = ADODataSimulator(seed=42)  # Seed for reproducibility
    
    # Generate data
    print("Generating ADO data with known seed...")
    work_items = simulator.generate_multi_pi_data(
        num_pis=2,
        num_epics=3,
        features_per_epic=(2, 3),
        stories_per_feature=(3, 5)
    )
    
    # Export to CSV format
    print("\nExporting to CSV format...")
    df = simulator.export_to_csv_format(work_items, include_metrics=True)
    
    # Save to file
    output_path = Path("./ado_analysis_output/simulated_ado_data.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Exported {len(df)} work items to: {output_path}")
    print(f"\nData preview:")
    print(df[['WorkItemId', 'Title', 'WorkItemType', 'State', 'StoryPoints']].head())
    
    # Now analyze the exported data
    print("\nAnalyzing exported data...")
    analyzer = ADOAnalyzer()
    analyzer.load_from_csv(output_path)
    
    # Quick analysis
    analyzer.configure_ahp()
    results = analyzer.analyze(generate_dashboard=False)
    
    print(f"\n✓ Analysis complete:")
    print(f"  Total items: {results['summary']['total_items']}")
    print(f"  Completion rate: {results['summary']['completion_rate']:.1f}%")


def main():
    """Run all demos."""
    print("=" * 60)
    print("Azure DevOps Analytics Platform Demo".center(60))
    print("Quantified Value Framework with AHP".center(60))
    print("=" * 60)
    
    demos = [
        ("1. Basic Analysis", demo_basic_analysis),
        ("2. Scenario Comparison", demo_scenario_comparison),
        ("3. Custom AHP Criteria", demo_custom_ahp_criteria),
        ("4. Data Export", demo_data_export)
    ]
    
    print("\nAvailable demos:")
    for name, _ in demos:
        print(f"  {name}")
    
    print("\nRunning all demos...\n")
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Demo Complete!".center(60))
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check ./ado_analysis_output/ for generated dashboards")
    print("2. Review analysis_results.json for detailed metrics")
    print("3. Open the HTML dashboards in your browser")
    print("4. Try with your own ADO CSV export data")


if __name__ == "__main__":
    main()