#!/usr/bin/env python3
"""Quick test of ADO Analytics module"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from datascience_platform.ado import ADOAnalyzer

print("Testing ADO Analytics Module...")

# Create analyzer
analyzer = ADOAnalyzer()

# Load simulated data
print("\n1. Loading simulated data...")
work_items = analyzer.load_simulated_data(
    scenario='custom',
    num_pis=2,
    num_epics=3,
    completion_rate=0.75
)
print(f"✓ Loaded {len(work_items)} work items")

# Configure AHP
print("\n2. Configuring AHP...")
ahp_config = analyzer.configure_ahp(preferences={
    'business_value': 5,
    'roi_efficiency': 4,
    'strategic_alignment': 3,
    'risk_complexity': 2,
    'team_confidence': 3
})
print(f"✓ AHP configured (CR: {ahp_config['consistency_ratio']:.3f})")

# Run analysis without dashboard
print("\n3. Running analysis...")
results = analyzer.analyze(generate_dashboard=False)

# Display results
print("\n4. Results Summary:")
print(f"   - Total items: {results['summary']['total_items']}")
print(f"   - Completion rate: {results['summary']['completion_rate']:.1f}%")
print(f"   - Top priority: {analyzer.top_priorities[0]['title'][:50]}...")
print(f"   - PI Predictability: {analyzer.predictability_score:.1f}%")

print("\n✅ ADO module test successful!")