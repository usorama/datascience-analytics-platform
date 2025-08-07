"""Dashboard Generator

Main module that orchestrates the generation of TypeScript/React dashboards
from ML outputs.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import logging

from .analyzer import DataAnalyzer, VisualizationRecommender
from .optimizer import MLOutputOptimizer, OptimizationStatus
from .components import ComponentGenerator, FilterGenerator

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for dashboard generation."""
    title: str = "ML Analytics Dashboard"
    description: str = "Data-driven insights powered by machine learning"
    output_dir: Path = Path("./generated_dashboard")
    theme: str = "light"
    auto_refresh: bool = False
    refresh_interval: int = 3600  # seconds
    use_tremor: bool = True
    include_export: bool = True
    responsive: bool = True


class DashboardGenerator:
    """Generates complete TypeScript/React dashboards from ML outputs."""
    
    def __init__(self, config: Optional[DashboardConfig] = None):
        """
        Initialize dashboard generator.
        
        Args:
            config: Dashboard configuration
        """
        self.config = config or DashboardConfig()
        self.data_analyzer = DataAnalyzer()
        self.viz_recommender = VisualizationRecommender()
        self.ml_optimizer = MLOutputOptimizer()
        self.component_generator = ComponentGenerator(use_tremor=self.config.use_tremor)
        self.filter_generator = FilterGenerator()
        
        # Generation state
        self.analysis_results: Optional[Dict[str, Any]] = None
        self.ml_outputs: Optional[Dict[str, Any]] = None
        self.optimization_status: Optional[OptimizationStatus] = None
    
    def generate_dashboard(
        self,
        data: pd.DataFrame,
        ml_outputs: Dict[str, Any],
        ml_pipeline: Optional[Any] = None,
        refinement_history: Optional[List[Any]] = None
    ) -> Tuple[bool, Path]:
        """
        Generate a complete dashboard from data and ML outputs.
        
        Args:
            data: Input data for analysis
            ml_outputs: ML model outputs and results
            ml_pipeline: Optional ML pipeline for convergence check
            refinement_history: Optional MLE-STAR refinement history
            
        Returns:
            Tuple of (success, output_path)
        """
        try:
            # Step 1: Check ML optimization is complete
            logger.info("Checking ML optimization status...")
            self.optimization_status = self.ml_optimizer.check_optimization_complete(
                ml_pipeline, refinement_history
            )
            
            if not self.optimization_status.ready_for_dashboard:
                logger.warning("ML optimization not complete, proceeding anyway...")
            
            # Step 2: Analyze data
            logger.info("Analyzing data structure...")
            self.analysis_results = self.data_analyzer.analyze_dataframe(data)
            
            # Step 3: Optimize ML outputs for dashboard
            logger.info("Optimizing ML outputs for visualization...")
            self.ml_outputs = self.ml_optimizer.optimize_for_dashboard(ml_outputs)
            
            # Step 4: Generate dashboard structure
            logger.info("Generating dashboard structure...")
            dashboard_structure = self._generate_dashboard_structure()
            
            # Step 5: Generate components
            logger.info("Generating React components...")
            components = self._generate_all_components(dashboard_structure)
            
            # Step 6: Write files
            logger.info("Writing dashboard files...")
            self._write_dashboard_files(components)
            
            # Step 7: Generate supporting files
            logger.info("Generating supporting files...")
            self._generate_supporting_files()
            
            # Step 8: Copy static assets
            self._copy_static_assets()
            
            logger.info(f"Dashboard generated successfully at {self.config.output_dir}")
            return True, self.config.output_dir
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return False, self.config.output_dir
    
    def _generate_dashboard_structure(self) -> Dict[str, Any]:
        """Generate the dashboard structure based on analysis."""
        # Get visualization recommendations
        viz_recommendations = self.viz_recommender.recommend_visualizations(
            self.analysis_results,
            self.ml_outputs
        )
        
        # Generate filter configurations
        filter_configs = self.filter_generator.generate_filter_configs(
            self.analysis_results['columns']
        )
        
        # Organize visualizations by tab
        tab_visualizations = {
            'analytics': [],
            'ml': [],
            'decisions': []
        }
        
        # Distribute visualizations across tabs
        for i, viz in enumerate(viz_recommendations):
            viz_config = {
                'id': f'viz_{i}',
                'type': viz.chart_type.value,
                'title': viz.title,
                'description': viz.description,
                'dataColumns': viz.data_columns,
                'config': viz.config,
                'priority': viz.priority
            }
            
            # Assign to appropriate tab
            if 'ml' in viz.title.lower() or 'model' in viz.title.lower():
                tab_visualizations['ml'].append(viz_config)
            elif 'decision' in viz.title.lower() or 'prediction' in viz.title.lower():
                tab_visualizations['decisions'].append(viz_config)
            else:
                tab_visualizations['analytics'].append(viz_config)
        
        # Ensure each tab has content
        self._balance_tab_content(tab_visualizations)
        
        return {
            'title': self.config.title,
            'description': self.config.description,
            'filters': filter_configs,
            'visualizations': tab_visualizations,
            'theme': self.config.theme,
            'dataShape': self.analysis_results['shape'],
            'patterns': self.analysis_results['patterns'],
            'optimization_status': {
                'converged': self.optimization_status.is_converged,
                'iterations': self.optimization_status.iterations_completed,
                'performance': self.optimization_status.current_performance
            }
        }
    
    def _balance_tab_content(self, tab_visualizations: Dict[str, List[Any]]):
        """Ensure each tab has appropriate content."""
        # Add default content if tabs are empty
        if not tab_visualizations['analytics']:
            # Add summary statistics
            tab_visualizations['analytics'].append({
                'id': 'summary_stats',
                'type': 'table',
                'title': 'Summary Statistics',
                'description': 'Overview of key metrics',
                'dataColumns': ['metric', 'value'],
                'config': {'sortable': True}
            })
        
        if not tab_visualizations['ml']:
            # Add model performance
            tab_visualizations['ml'].append({
                'id': 'model_performance',
                'type': 'kpi',
                'title': 'Model Performance',
                'description': 'Key performance indicators',
                'dataColumns': ['metric', 'value'],
                'config': {'format': 'percentage'}
            })
        
        if not tab_visualizations['decisions']:
            # Add recommendations table
            tab_visualizations['decisions'].append({
                'id': 'recommendations',
                'type': 'table',
                'title': 'Recommendations',
                'description': 'Actionable insights from ML analysis',
                'dataColumns': ['item', 'score', 'recommendation'],
                'config': {'sortable': True, 'searchable': True}
            })
    
    def _generate_all_components(
        self,
        dashboard_structure: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate all dashboard components."""
        components = {}
        
        # Generate scaffold
        scaffold = self.component_generator.generate_dashboard_scaffold(dashboard_structure)
        components.update(scaffold)
        
        # Generate tab components
        components['tabs/AnalyticsTab.tsx'] = self._generate_analytics_tab(
            dashboard_structure['visualizations']['analytics']
        )
        components['tabs/MLOutputsTab.tsx'] = self._generate_ml_outputs_tab(
            dashboard_structure['visualizations']['ml']
        )
        components['tabs/DecisionsTab.tsx'] = self._generate_decisions_tab(
            dashboard_structure['visualizations']['decisions']
        )
        
        # Generate visualization components
        for tab_name, visualizations in dashboard_structure['visualizations'].items():
            for viz in visualizations:
                component_name = f"visualizations/{viz['id']}.tsx"
                components[component_name] = self._generate_visualization_component(viz)
        
        return components
    
    def _generate_analytics_tab(self, visualizations: List[Dict[str, Any]]) -> str:
        """Generate the analytics tab component."""
        imports = set()
        viz_imports = []
        
        for viz in visualizations:
            viz_imports.append(f"import {{ {viz['id']} }} from '../visualizations/{viz['id']}';")
            
        return f"""import React from 'react';
import {{ Grid, Card }} from '@tremor/react';
import {{ useFilteredData }} from '../hooks';
{chr(10).join(viz_imports)}

interface AnalyticsTabProps {{
  data: any;
  filters: any;
  config: any;
}}

export const AnalyticsTab: React.FC<AnalyticsTabProps> = ({{ data, filters, config }}) => {{
  const filteredData = useFilteredData(data.analytics || [], filters);
  
  return (
    <div className="space-y-6">
      <Grid numItems={{1}} numItemsSm={{2}} numItemsLg={{3}} className="gap-6">
        {' '.join([f'<{viz["id"]} data={{filteredData}} config={{config}} />' for viz in visualizations[:3]])}
      </Grid>
      
      <div className="space-y-6">
        {' '.join([f'<{viz["id"]} data={{filteredData}} config={{config}} />' for viz in visualizations[3:]])}
      </div>
    </div>
  );
}};"""
    
    def _generate_ml_outputs_tab(self, visualizations: List[Dict[str, Any]]) -> str:
        """Generate the ML outputs tab component."""
        viz_imports = [f"import {{ {viz['id']} }} from '../visualizations/{viz['id']}';" 
                      for viz in visualizations]
        
        return f"""import React from 'react';
import {{ Grid, Card, Title, Text }} from '@tremor/react';
import {{ useDashboardStore }} from '../store';
{chr(10).join(viz_imports)}

interface MLOutputsTabProps {{
  data: any;
  filters: any;
  config: any;
}}

export const MLOutputsTab: React.FC<MLOutputsTabProps> = ({{ data, filters, config }}) => {{
  const {{ mlOutputs }} = useDashboardStore();
  
  return (
    <div className="space-y-6">
      {{/* Optimization Status */}}
      <Card>
        <Title>ML Optimization Status</Title>
        <Text>Iterations: {{config.optimization_status?.iterations || 0}}</Text>
        <Text>Performance: {{(config.optimization_status?.performance || 0).toFixed(4)}}</Text>
        <Text>Status: {{config.optimization_status?.converged ? 'Converged ✓' : 'In Progress...'}}</Text>
      </Card>
      
      {{/* ML Visualizations */}}
      <Grid numItems={{1}} numItemsLg={{2}} className="gap-6">
        {' '.join([f'<{viz["id"]} data={{mlOutputs}} config={{config}} />' for viz in visualizations])}
      </Grid>
    </div>
  );
}};"""
    
    def _generate_decisions_tab(self, visualizations: List[Dict[str, Any]]) -> str:
        """Generate the decisions and predictions tab component."""
        viz_imports = [f"import {{ {viz['id']} }} from '../visualizations/{viz['id']}';" 
                      for viz in visualizations]
        
        return f"""import React from 'react';
import {{ Card, Title, Text, Badge, List, ListItem }} from '@tremor/react';
import {{ useFilteredData }} from '../hooks';
{chr(10).join(viz_imports)}

interface DecisionsTabProps {{
  data: any;
  filters: any;
  config: any;
}}

export const DecisionsTab: React.FC<DecisionsTabProps> = ({{ data, filters, config }}) => {{
  const predictions = useFilteredData(data.predictions || [], filters);
  
  // Categorize predictions
  const highValue = predictions.filter(p => p.value_score > 0.7);
  const mediumValue = predictions.filter(p => p.value_score > 0.3 && p.value_score <= 0.7);
  const lowValue = predictions.filter(p => p.value_score <= 0.3);
  
  return (
    <div className="space-y-6">
      {{/* Summary Cards */}}
      <Grid numItems={{1}} numItemsSm={{3}} className="gap-6">
        <Card>
          <Title>High Value Items</Title>
          <Text className="text-3xl font-bold text-green-600">{{highValue.length}}</Text>
          <Text>Recommended for immediate attention</Text>
        </Card>
        
        <Card>
          <Title>Medium Value Items</Title>
          <Text className="text-3xl font-bold text-yellow-600">{{mediumValue.length}}</Text>
          <Text>Should be reviewed</Text>
        </Card>
        
        <Card>
          <Title>Low Value Items</Title>
          <Text className="text-3xl font-bold text-gray-600">{{lowValue.length}}</Text>
          <Text>Can be deprioritized</Text>
        </Card>
      </Grid>
      
      {{/* QVF Framework Analysis */}}
      <Card>
        <Title>Quantified Value Framework (QVF) Analysis</Title>
        <Text>Optimization recommendations based on capacity and value</Text>
        
        <div className="mt-4 space-y-4">
          <div>
            <Text className="font-semibold">PI Capacity Optimization:</Text>
            <List>
              <ListItem>
                <span>Total Capacity: {{data.capacity?.total || 0}} story points</span>
              </ListItem>
              <ListItem>
                <span>Allocated to High Value: {{data.capacity?.high_value || 0}} points</span>
              </ListItem>
              <ListItem>
                <span>Optimization Potential: {{data.capacity?.optimization_potential || 0}}%</span>
              </ListItem>
            </List>
          </div>
        </div>
      </Card>
      
      {{/* Decision Visualizations */}}
      {' '.join([f'<{viz["id"]} data={{predictions}} config={{config}} />' for viz in visualizations])}
    </div>
  );
}};"""
    
    def _generate_visualization_component(self, viz_config: Dict[str, Any]) -> str:
        """Generate a single visualization component."""
        chart_type = viz_config['type']
        imports = self._get_chart_imports(chart_type)
        
        return f"""import React from 'react';
{imports}

interface {viz_config['id']}Props {{
  data: any[];
  config: any;
}}

export const {viz_config['id']}: React.FC<{viz_config['id']}Props> = ({{ data, config }}) => {{
  {self._get_chart_implementation(viz_config)}
}};"""
    
    def _get_chart_imports(self, chart_type: str) -> str:
        """Get imports for specific chart type."""
        if self.config.use_tremor:
            chart_imports = {
                'bar': "import { BarChart, Card, Title } from '@tremor/react';",
                'line': "import { LineChart, Card, Title } from '@tremor/react';",
                'scatter': "import { ScatterChart, Card, Title } from '@tremor/react';",
                'pie': "import { DonutChart, Card, Title } from '@tremor/react';",
                'heatmap': "import { Card, Title } from '@tremor/react';",
                'kpi': "import { Card, Metric, Text, Flex, ProgressBar } from '@tremor/react';",
                'table': "import { Card, Title, Table, TableHead, TableRow, TableHeaderCell, TableBody, TableCell } from '@tremor/react';"
            }
            return chart_imports.get(chart_type, "import { Card, Title } from '@tremor/react';")
        else:
            return "import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';"
    
    def _get_chart_implementation(self, viz_config: Dict[str, Any]) -> str:
        """Get chart implementation based on type."""
        chart_type = viz_config['type']
        
        implementations = {
            'bar': f"""
  return (
    <Card>
      <Title>{viz_config['title']}</Title>
      <BarChart
        data={{data}}
        index="{{viz_config['config'].get('x', 'category')}}"
        categories={{["{viz_config['config'].get('y', 'value')}"]}}
        colors={{["blue"]}}
        className="h-80 mt-4"
      />
    </Card>
  );""",
            'line': f"""
  return (
    <Card>
      <Title>{viz_config['title']}</Title>
      <LineChart
        data={{data}}
        index="{{viz_config['config'].get('x', 'date')}}"
        categories={{["{viz_config['config'].get('y', 'value')}"]}}
        colors={{["blue"]}}
        className="h-80 mt-4"
        showLegend={{true}}
      />
    </Card>
  );""",
            'kpi': f"""
  const value = data[0]?.{viz_config['dataColumns'][0] if viz_config['dataColumns'] else 'value'} || 0;
  const target = 100;
  const percentage = (value / target) * 100;
  
  return (
    <Card>
      <Flex alignItems="start">
        <div>
          <Text>{viz_config['title']}</Text>
          <Metric>{{value.toFixed(2)}}</Metric>
        </div>
      </Flex>
      <Flex className="mt-4">
        <Text className="truncate">{{percentage.toFixed(1)}}% of target</Text>
        <Text>{{target}}</Text>
      </Flex>
      <ProgressBar value={{percentage}} className="mt-2" />
    </Card>
  );""",
            'table': f"""
  return (
    <Card>
      <Title>{viz_config['title']}</Title>
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            {' '.join([f'<TableHeaderCell>{col}</TableHeaderCell>' for col in viz_config.get('dataColumns', ['Column'])])}
          </TableRow>
        </TableHead>
        <TableBody>
          {{data.slice(0, 10).map((item, idx) => (
            <TableRow key={{idx}}>
              {' '.join([f'<TableCell>{{item.{col}}}</TableCell>' for col in viz_config.get('dataColumns', ['value'])])}
            </TableRow>
          ))}}
        </TableBody>
      </Table>
    </Card>
  );"""
        }
        
        return implementations.get(chart_type, implementations['table'])
    
    def _write_dashboard_files(self, components: Dict[str, str]):
        """Write all component files to disk."""
        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create src directory structure
        src_dir = self.config.output_dir / "src"
        src_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (src_dir / "tabs").mkdir(exist_ok=True)
        (src_dir / "visualizations").mkdir(exist_ok=True)
        
        # Write component files
        for file_path, content in components.items():
            full_path = src_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def _generate_supporting_files(self):
        """Generate package.json, tsconfig, etc."""
        # package.json
        package_json = {
            "name": "ml-analytics-dashboard",
            "version": "1.0.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "@tremor/react": "^3.11.1",
                "next": "14.0.0",
                "react": "^18",
                "react-dom": "^18",
                "zustand": "^4.4.7",
                "recharts": "^2.10.0"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10.0.1",
                "postcss": "^8",
                "tailwindcss": "^3.3.0",
                "typescript": "^5"
            }
        }
        
        with open(self.config.output_dir / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "es5",
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "paths": {
                    "@/*": ["./src/*"]
                }
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
            "exclude": ["node_modules"]
        }
        
        with open(self.config.output_dir / "tsconfig.json", 'w') as f:
            json.dump(tsconfig, f, indent=2)
        
        # tailwind.config.js
        tailwind_config = """import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './node_modules/@tremor/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
export default config"""
        
        with open(self.config.output_dir / "tailwind.config.ts", 'w') as f:
            f.write(tailwind_config)
        
        # App entry point
        app_tsx = """import React from 'react';
import Dashboard from './src/Dashboard';
import dashboardData from './data/dashboard-data.json';
import dashboardConfig from './data/dashboard-config.json';

function App() {
  return <Dashboard config={dashboardConfig} data={dashboardData} />;
}

export default App;"""
        
        # Create src/app directory for Next.js
        app_dir = self.config.output_dir / "src" / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Write page.tsx
        with open(app_dir / "page.tsx", 'w') as f:
            f.write(app_tsx)
        
        # Write layout.tsx
        layout_tsx = """import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ML Analytics Dashboard',
  description: 'Generated by DataScience Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}"""
        
        with open(app_dir / "layout.tsx", 'w') as f:
            f.write(layout_tsx)
        
        # Write globals.css
        globals_css = """@tailwind base;
@tailwind components;
@tailwind utilities;"""
        
        with open(app_dir / "globals.css", 'w') as f:
            f.write(globals_css)
        
        # README
        readme = f"""# ML Analytics Dashboard

This dashboard was automatically generated by the DataScience Platform.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Features

- **Left Filter Panel**: Persistent filters across all tabs
- **Three Tabs**:
  - Analytics: Data insights and NLP/NLU analysis
  - ML Outputs: Machine learning results with explanations
  - Decisions: Valuable items, predictions, and QVF optimization

## Data

The dashboard reads data from:
- `data/dashboard-data.json`: Main data file
- `data/dashboard-config.json`: Dashboard configuration

## Customization

Edit the components in `src/` to customize the dashboard.

Generated on: {self.optimization_status.time_elapsed if self.optimization_status else 'N/A'}
ML Optimization Status: {'Converged' if self.optimization_status and self.optimization_status.is_converged else 'In Progress'}
"""
        
        with open(self.config.output_dir / "README.md", 'w') as f:
            f.write(readme)
    
    def _copy_static_assets(self):
        """Copy or generate static data files."""
        # Create data directory
        data_dir = self.config.output_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Generate sample data file
        sample_data = {
            'analytics': self._prepare_analytics_data(),
            'predictions': self._prepare_predictions_data(),
            'capacity': {
                'total': 500,
                'high_value': 300,
                'optimization_potential': 15
            },
            'ml_outputs': self.ml_outputs if self.ml_outputs else {}
        }
        
        with open(data_dir / "dashboard-data.json", 'w') as f:
            json.dump(sample_data, f, indent=2, default=str)
        
        # Generate config file
        config_data = {
            'title': self.config.title,
            'description': self.config.description,
            'theme': self.config.theme,
            'filters': self.filter_generator.generate_filter_configs(
                self.analysis_results['columns']
            ) if self.analysis_results else [],
            'optimization_status': {
                'converged': self.optimization_status.is_converged,
                'iterations': self.optimization_status.iterations_completed,
                'performance': float(self.optimization_status.current_performance)
            } if self.optimization_status else {}
        }
        
        with open(data_dir / "dashboard-config.json", 'w') as f:
            json.dump(config_data, f, indent=2, default=str)
    
    def _prepare_analytics_data(self) -> List[Dict[str, Any]]:
        """Prepare data for analytics tab."""
        # Generate sample analytics data
        return [
            {
                'date': '2025-01-01',
                'value': 100,
                'category': 'A',
                'trend': 'increasing'
            },
            {
                'date': '2025-01-02',
                'value': 120,
                'category': 'A',
                'trend': 'increasing'
            },
            # Add more sample data as needed
        ]
    
    def _prepare_predictions_data(self) -> List[Dict[str, Any]]:
        """Prepare predictions data."""
        return [
            {
                'id': 1,
                'title': 'High Value Epic',
                'value_score': 0.85,
                'confidence': 0.92,
                'recommendation': 'Prioritize for next PI'
            },
            {
                'id': 2,
                'title': 'Medium Value Feature',
                'value_score': 0.45,
                'confidence': 0.78,
                'recommendation': 'Consider for future'
            },
            # Add more predictions as needed
        ]