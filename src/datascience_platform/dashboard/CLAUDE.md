# CLAUDE.md - Dashboard Generation System

This file provides guidance for working with the DataScience Platform's dashboard generation system.

## System Overview

The dashboard generation system creates production-ready TypeScript/React dashboards from ML outputs and data analysis. It provides two complementary generation approaches:

1. **HTML Dashboards** - Self-contained HTML files with embedded data and interactivity
2. **Next.js Applications** - Full TypeScript/React applications with modern architecture

## Key Components

### 📁 generative/ - TypeScript/React Code Generation
Advanced Next.js 14 application generator with:
- **analyzer.py** - Data structure analysis and visualization recommendations
- **generator.py** - Main orchestrator for TypeScript/React dashboard creation
- **optimizer.py** - ML output optimization for dashboard consumption
- **components.py** - React component generation (Tremor UI framework)

### 📁 templates/ - HTML Templates
Jinja2-based templates for self-contained HTML dashboards:
- **base.html** - Main dashboard template with embedded JavaScript
- **components/** - Reusable HTML components (filters, tables, charts)
- **print.html** - Print-optimized layout for PDF export

### 📁 static/ - CSS/JS Assets
Static assets for HTML dashboards:
- **styles.css** - Responsive CSS with dark/light theme support
- **dashboard.js** - Interactive JavaScript for charts and filters

## Next.js 14 Application Generation

### Complete Application Structure
```
generated_dashboard/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Root layout with Inter font
│   │   ├── page.tsx           # Main dashboard page
│   │   └── globals.css        # Tailwind CSS imports
│   ├── tabs/                  # Three-tab architecture
│   │   ├── AnalyticsTab.tsx   # Data insights and NLP analysis
│   │   ├── MLOutputsTab.tsx   # Model outputs and performance
│   │   └── DecisionsTab.tsx   # QVF framework and predictions
│   ├── visualizations/        # Chart components
│   ├── Dashboard.tsx          # Main dashboard orchestrator
│   ├── Layout.tsx            # Left filter panel layout
│   ├── FilterPanel.tsx       # Persistent filtering interface
│   ├── TabContainer.tsx      # Tab navigation system
│   ├── types.ts             # TypeScript definitions
│   ├── hooks.ts             # Custom React hooks
│   ├── store.ts             # Zustand state management
│   └── utils.ts             # Utility functions
├── data/
│   ├── dashboard-data.json   # Embedded data file
│   └── dashboard-config.json # Dashboard configuration
├── package.json             # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.ts      # Tailwind CSS setup
└── README.md              # Generated documentation
```

### Production Features

#### 🎨 Design System
- **Tremor UI Components** - Professional dashboard component library
- **Tailwind CSS** - Responsive design with dark/light themes
- **Accessibility** - WCAG 2.1 compliant with proper ARIA labels
- **Responsive Design** - Mobile-first approach with grid layouts

#### ⚡ Performance
- **Next.js 14** - Latest version with App Router and server components
- **TypeScript** - Full type safety with comprehensive interfaces
- **Zustand Store** - Lightweight state management with persistence
- **Custom Hooks** - Optimized data filtering and chart rendering

#### 🔧 Development Experience
- **Hot Reload** - Instant development feedback
- **ESLint/Prettier** - Code quality and formatting
- **Component-Based** - Modular, reusable architecture
- **Type Safety** - Comprehensive TypeScript definitions

## Three-Tab Architecture

### 📊 Analytics Tab
Data insights and exploratory analysis:
- **Summary Statistics** - Key metrics and distributions
- **Correlation Analysis** - Feature relationships
- **Time Series** - Temporal patterns and trends
- **NLP Analysis** - Semantic embeddings and text insights

### 🤖 ML Outputs Tab
Machine learning results and model performance:
- **Model Performance** - Accuracy, precision, recall metrics
- **Feature Importance** - Variable significance rankings
- **Optimization Status** - MLE-STAR convergence tracking
- **Prediction Confidence** - Model certainty indicators

### 🎯 Decisions & Predictions Tab
Actionable insights and QVF framework analysis:
- **Value Scoring** - High/medium/low value categorization
- **PI Capacity Optimization** - Resource allocation recommendations
- **Prediction Tables** - Sorted by confidence and value
- **QVF Analysis** - Quantified Value Framework alignment

## ML Integration Capabilities

### MLE-STAR Pipeline Integration
- **Convergence Detection** - Automatic optimization completion checking
- **Performance Tracking** - Multi-iteration improvement visualization
- **Component Analysis** - Pipeline element effectiveness scoring
- **Ablation Studies** - Feature removal impact assessment

### ADO Analytics Integration
- **Semantic Alignment** - Work item value scoring with evidence
- **Agile Metrics** - 20+ velocity and quality measurements
- **PI Planning** - Capacity optimization with QVF framework
- **Velocity Prediction** - Sprint and PI outcome forecasting

### NLP Enhancement Integration
- **Transformer Embeddings** - GPU-accelerated semantic analysis
- **Similarity Scoring** - Work item alignment measurement
- **Text Analysis** - Requirement quality and completeness scoring
- **Knowledge Extraction** - Automatic insight discovery

## Usage Patterns

### Quick Dashboard Generation
```python
from datascience_platform.dashboard.generative import DashboardGenerator, DashboardConfig

# Configure dashboard
config = DashboardConfig(
    title="ML Analytics Dashboard",
    description="Production insights from ML pipeline",
    output_dir=Path("./my_dashboard"),
    theme="light",
    use_tremor=True
)

# Generate complete Next.js application
generator = DashboardGenerator(config)
success, output_path = generator.generate_dashboard(
    data=df,
    ml_outputs=ml_results,
    ml_pipeline=pipeline,
    refinement_history=mle_star_history
)

if success:
    print(f"Dashboard generated at: {output_path}")
    # Navigate to directory and run: npm install && npm run dev
```

### HTML Dashboard for Embedded Use
```python
from datascience_platform.dashboard import DashboardGenerator

# Create self-contained HTML dashboard
html_generator = DashboardGenerator(theme='light', compress=True)

# Add components
html_generator.add_kpi_card("Model Accuracy", 0.94, trend=5.2)
html_generator.add_chart('line', df, 'performance_over_time', 
                        title="Training Progress")
html_generator.add_data_table(predictions_df, 'predictions', 
                             title="Model Predictions")

# Generate single HTML file
html_content = html_generator.generate_html("dashboard.html")
```

### Advanced Customization
```python
# Custom visualization recommendations
from datascience_platform.dashboard.generative import VisualizationRecommender

recommender = VisualizationRecommender()
recommendations = recommender.recommend_visualizations(
    data_analysis_results,
    ml_outputs,
    preference_config={'chart_types': ['bar', 'line', 'scatter']}
)

# Custom filter generation
from datascience_platform.dashboard.generative import FilterGenerator

filter_gen = FilterGenerator()
filters = filter_gen.generate_filter_configs(column_analyses)
```

## Production Deployment

### Development Workflow
```bash
# Navigate to generated dashboard
cd generated_dashboard

# Install dependencies
npm install

# Start development server
npm run dev
# Dashboard available at http://localhost:3000

# Build for production
npm run build

# Start production server
npm start
```

### Deployment Options
- **Vercel** - Automatic deployment from Git
- **Netlify** - Static site generation support
- **Docker** - Containerized deployment
- **Traditional Hosting** - Static build output

## Key Files Reference

### Core Generation Files
- `generator.py` - Main dashboard generation orchestrator
- `components.py` - React component generation logic
- `analyzer.py` - Data analysis and visualization planning
- `optimizer.py` - ML output optimization for dashboards

### Template Files
- `templates/base.html` - Main HTML dashboard template
- `static/styles.css` - Dashboard styling and themes
- `static/dashboard.js` - Interactive JavaScript functionality

### Supporting Documentation
- `charts.py` - Chart generation utilities for HTML dashboards
- `__init__.py` - Module exports and public API

## Links to Main Documentation

- **[IMPLEMENTATION_SUMMARY.md](../../../IMPLEMENTATION_SUMMARY.md)** - Complete platform overview
- **[Project README](../../../README.md)** - Installation and quick start
- **[ADO Analytics](../ado/CLAUDE.md)** - Agile metrics and semantic analysis
- **[NLP Components](../nlp/CLAUDE.md)** - Transformer-based text analysis
- **[MLE-STAR Pipeline](../mle_star/CLAUDE.md)** - ML optimization framework

## Development Guidelines

### Component Generation Best Practices
1. **Type Safety** - Generate comprehensive TypeScript interfaces
2. **Accessibility** - Include proper ARIA labels and semantic HTML
3. **Responsive Design** - Use Tremor's grid system for mobile compatibility
4. **Performance** - Implement data virtualization for large datasets
5. **Error Boundaries** - Include error handling in generated components

### Customization Points
- **Theme Configuration** - Light/dark mode with CSS variables
- **Component Library** - Tremor UI (recommended) or Recharts fallback
- **Data Binding** - Flexible column mapping and aggregation
- **Filter Logic** - Custom filter implementations for domain-specific needs

### Quality Assurance
- **Generated Code Quality** - ESLint and Prettier configuration
- **Type Coverage** - 100% TypeScript coverage in generated code
- **Testing Framework** - Ready for Jest/Testing Library integration
- **Build Verification** - Automatic build success checking

The dashboard generation system provides enterprise-grade analytics dashboards with minimal configuration, leveraging modern web technologies and production-ready architecture patterns.