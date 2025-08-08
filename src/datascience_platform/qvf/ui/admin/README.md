# QVF Admin Interface

A comprehensive, production-ready administration interface for the Quantified Value Framework (QVF). This system provides enterprise-grade configuration management, real-time validation, and intuitive weight adjustment for QVF prioritization.

## 🎯 Overview

The QVF Admin Interface integrates seamlessly with the DataScience Platform to provide:

- **Interactive Weight Configuration**: Real-time sliders with validation
- **Configuration Management**: Full CRUD operations for QVF configurations
- **Validation System**: Immediate feedback on configuration validity
- **Export/Import**: Backup and share configurations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Accessibility**: Full keyboard navigation and screen reader support
- **TypeScript/React**: Modern, type-safe frontend with Tremor UI

## 🚀 Quick Start

### 1. Generate Admin Dashboard

```bash
# Using the CLI (recommended)
python -m datascience_platform.qvf.ui.admin.cli generate --auto-install --auto-open

# Or programmatically
python -c "
from datascience_platform.qvf.ui import generate_qvf_admin_dashboard
generate_qvf_admin_dashboard('./my_qvf_admin', title='My QVF Admin')
"
```

### 2. Start the API Server

```bash
# Start the FastAPI backend
python -m datascience_platform.qvf.api.main

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

### 3. Launch Frontend

```bash
# In the generated dashboard directory
cd ./my_qvf_admin
npm install
npm run dev

# Open http://localhost:3000
```

## 📋 Features

### Configuration Management
- **Create/Edit/Delete** QVF configurations
- **Preset Templates** (Agile, Enterprise, Startup)
- **Configuration Validation** with detailed feedback
- **Export/Import** in JSON format
- **Version Management** with change tracking

### Weight Editor
- **Interactive Sliders** for category weights
- **Real-time Validation** with visual feedback
- **Preset Buttons** for common weight distributions
- **Normalization Tools** to ensure weights sum to 1.0
- **Visual Progress Indicators** with percentage display

### Validation System
- **Real-time Feedback** as you type/adjust
- **Comprehensive Checks** for mathematical validity
- **Detailed Issue Reports** with actionable suggestions
- **Consistency Validation** using AHP mathematical framework
- **Data Quality Assessment** for configuration reliability

### User Experience
- **Responsive Design** adapts to all screen sizes
- **Dark/Light Mode** with system preference detection
- **Accessibility Support** (WCAG 2.1 compliant)
- **Loading States** with skeleton screens
- **Error Boundaries** with graceful fallbacks
- **Toast Notifications** for user feedback

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
src/datascience_platform/qvf/
├── api/
│   ├── config_api.py      # REST endpoints
│   └── main.py           # FastAPI application
├── core/
│   ├── criteria.py       # QVF criteria engine
│   ├── scoring.py        # Scoring integration
│   └── financial.py     # Financial calculations
└── ui/
    └── admin/            # Admin interface
```

### Frontend (TypeScript/React)
```
generated_dashboard/
├── src/
│   ├── components/
│   │   ├── admin/        # Admin components
│   │   └── ui/          # Reusable UI components
│   ├── hooks/           # React hooks for API
│   ├── types/           # TypeScript definitions
│   └── utils/           # Utilities and helpers
├── public/              # Static assets
└── package.json         # Dependencies and scripts
```

## 🔧 API Reference

### Configurations
```typescript
GET    /api/v1/qvf/configurations           // List all configurations
POST   /api/v1/qvf/configurations           // Create new configuration  
GET    /api/v1/qvf/configurations/{id}      // Get configuration details
PUT    /api/v1/qvf/configurations/{id}      // Update configuration
DELETE /api/v1/qvf/configurations/{id}      // Delete configuration
GET    /api/v1/qvf/configurations/{id}/export // Export configuration
```

### Validation
```typescript
POST   /api/v1/qvf/validate/weights         // Validate weight configuration
POST   /api/v1/qvf/validate/configuration/{id} // Validate full configuration
```

### Presets
```typescript
GET    /api/v1/qvf/presets                  // List available presets
POST   /api/v1/qvf/presets/{type}          // Create from preset
```

## 💻 Development

### Local Development Setup

1. **Backend Development**
```bash
# Install Python dependencies
pip install -r requirements.txt
pip install -e .

# Start FastAPI with hot reload
python -m datascience_platform.qvf.api.main
```

2. **Frontend Development**
```bash
# Generate dashboard first
python -m datascience_platform.qvf.ui.admin.cli generate

# In dashboard directory
cd ./qvf_admin_dashboard
npm install
npm run dev
```

### Environment Variables
```bash
# API Configuration
QVF_API_HOST=localhost
QVF_API_PORT=8000
QVF_API_CORS_ORIGINS=http://localhost:3000

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1/qvf
```

### Custom Styling
```css
/* Override in src/styles/custom.css */
:root {
  --qvf-primary: #3B82F6;
  --qvf-secondary: #6B7280;
  --qvf-success: #10B981;
  --qvf-warning: #F59E0B;
  --qvf-danger: #EF4444;
}
```

## 🧪 Testing

### Backend Testing
```bash
# Run QVF engine tests
python -m pytest src/datascience_platform/qvf/core/tests/

# Test API endpoints
python -c "
import requests
response = requests.get('http://localhost:8000/api/v1/qvf/configurations')
print(response.json())
"
```

### Frontend Testing
```bash
# In dashboard directory
npm run test        # Jest unit tests
npm run e2e         # Cypress integration tests
npm run type-check  # TypeScript validation
```

### Demo Script
```bash
# Run comprehensive demo
python demos/qvf_admin_demo.py

# This will:
# - Generate sample dashboards
# - Test backend integration
# - Validate API endpoints
# - Show usage examples
```

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
# Backend
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "datascience_platform.qvf.api.main"]

# Frontend
FROM node:18-alpine
COPY generated_dashboard /app
WORKDIR /app
RUN npm install && npm run build
CMD ["npm", "start"]
```

### Environment-Specific Builds
```bash
# Development build
npm run dev

# Production build  
npm run build
npm start

# Static export
npm run build && npm run export
```

### Performance Optimization
- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Remove unused code
- **Compression**: Gzip compression enabled
- **Caching**: Aggressive caching for static assets
- **Bundle Analysis**: `npm run analyze` to inspect bundle size

## 🔒 Security

### Authentication
```typescript
// Add authentication to API calls
const apiClient = new QVFApiClient({
  baseURL: '/api/v1/qvf',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### CORS Configuration
```python
# Production CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

## 🎨 Customization

### Theme Customization
```typescript
// Custom theme configuration
const customTheme = {
  colors: {
    primary: '#your-primary-color',
    secondary: '#your-secondary-color'
  },
  fontFamily: 'Your-Font-Family'
};
```

### Component Override
```typescript
// Custom weight editor
import { WeightEditor } from '@/components/admin';

const CustomWeightEditor = (props) => {
  return (
    <div className="custom-styling">
      <WeightEditor {...props} />
    </div>
  );
};
```

## 📊 Monitoring & Analytics

### Performance Monitoring
```typescript
// Built-in performance tracking
const monitor = new QVFPerformanceMonitor();
monitor.trackOperation('weight-validation', duration);
monitor.trackUserInteraction('slider-adjustment');
```

### Error Reporting
```typescript
// Automatic error reporting
window.addEventListener('unhandledrejection', (event) => {
  console.error('QVF Admin Error:', event.reason);
  // Send to your error reporting service
});
```

## 🤝 Contributing

### Development Guidelines
1. **TypeScript First**: All new code must be TypeScript
2. **Accessibility**: Follow WCAG 2.1 guidelines
3. **Testing**: Unit tests for all new features
4. **Documentation**: Update README and inline docs
5. **Performance**: Consider impact on bundle size

### Code Standards
```bash
# Formatting
npm run format      # Prettier
npm run lint        # ESLint
npm run type-check  # TypeScript

# Git hooks
npm run pre-commit  # Runs all checks
```

## 📚 Examples

### Basic Usage
```python
from datascience_platform.qvf.ui import generate_qvf_admin_dashboard

# Generate dashboard
dashboard_path = generate_qvf_admin_dashboard(
    output_dir="./my-admin",
    title="My QVF Admin",
    theme="dark"
)

print(f"Dashboard created at: {dashboard_path}")
```

### Advanced Configuration
```python
from datascience_platform.qvf.ui.admin import QVFAdminConfig, QVFAdminDashboardGenerator

config = QVFAdminConfig(
    title="Enterprise QVF System",
    description="Advanced QVF management for large teams",
    output_dir=Path("./enterprise-qvf"),
    theme="light",
    enable_dark_mode=True,
    api_base_url="/api/v1/qvf",
    responsive=True,
    accessibility=True
)

generator = QVFAdminDashboardGenerator(config)
path = generator.generate_admin_dashboard()
```

### React Integration
```typescript
import { QVFAdminApp, useConfigurations } from '@/components/admin';

function MyApp() {
  const { configurations, isLoading } = useConfigurations();
  
  return (
    <div>
      <h1>My App</h1>
      <QVFAdminApp />
    </div>
  );
}
```

## 📞 Support

### Common Issues

**Q: Dashboard generation fails with import error**
A: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Q: Frontend shows API connection errors**  
A: Check that the FastAPI server is running on the correct port

**Q: Weights don't sum to 1.0**
A: Use the "Normalize" button or adjust manually until total equals 100%

**Q: Dark mode not working**
A: Ensure `enable_dark_mode=True` in configuration and CSS classes are properly set

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/your-org/ds-package/issues)
- **Documentation**: See `/docs` directory in the repository
- **Examples**: Check `/demos` directory for working examples

## 📈 Roadmap

### Upcoming Features
- [ ] **User Management**: Role-based access control
- [ ] **Audit Logging**: Track all configuration changes
- [ ] **Collaboration**: Real-time collaborative editing
- [ ] **Templates**: Custom configuration templates
- [ ] **Integration**: Direct Azure DevOps field mapping
- [ ] **Analytics**: Usage analytics and insights
- [ ] **Mobile App**: React Native mobile companion

### Version History
- **v2.0.0**: Complete TypeScript/React rewrite with Tremor UI
- **v1.5.0**: Added real-time validation and export/import
- **v1.0.0**: Initial admin interface with basic CRUD operations

---

Built with ❤️ by the DataScience Platform team using React, TypeScript, Tremor UI, and FastAPI.