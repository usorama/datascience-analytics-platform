# QVF Platform Migration Guide

## Overview
This document provides step-by-step instructions for migrating to the new QVF Platform application structure while preserving all existing functionality.

**Date**: August 8, 2025  
**Migration Type**: Structure Reorganization with Symlink Preservation  
**Impact**: Zero downtime, backward compatibility maintained

## Pre-Migration Checklist

- [ ] Verify existing QVF engine is working: `python -m datascience_platform.qvf --help`
- [ ] Backup current development work
- [ ] Ensure Node.js 18+ and Python 3.11+ are installed
- [ ] Install pnpm: `npm install -g pnpm`

## Migration Steps

### 1. Verify New Structure
The new QVF platform is located at:
```
/Users/umasankrudhya/Projects/ds-package/qvf-platform/
```

Key verification points:
- [ ] Symlink exists: `ls -la packages/qvf-core` (should show symlink)
- [ ] QVF core accessible: `ls packages/qvf-core/ado/` (should show existing files)
- [ ] All required directories created

### 2. Install Dependencies

#### Frontend Dependencies
```bash
cd /Users/umasankrudhya/Projects/ds-package/qvf-platform
pnpm install
```

#### Backend Dependencies  
```bash
cd apps/api
pip install -r requirements.txt
```

#### Sync Service Dependencies
```bash
cd services/ado-sync
pip install -r requirements.txt
```

### 3. Configuration Setup

#### Environment Files
Copy and configure environment variables:
```bash
# In qvf-platform root
cp .env.example .env

# In apps/web/
cp .env.example .env.local

# Edit both files with your actual values
```

#### Required Environment Variables
- `ADO_ORGANIZATION`: Your Azure DevOps organization
- `ADO_PROJECT`: Your Azure DevOps project  
- `ADO_PAT_TOKEN`: Personal Access Token for ADO API
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret for authentication

### 4. Test Development Environment

#### Start Backend API
```bash
cd apps/api
python -m uvicorn qvf_api.main:app --reload --port 8000
```
Verify: http://localhost:8000/docs should show FastAPI documentation

#### Start Frontend
```bash
# From project root
pnpm run dev:web
```
Verify: http://localhost:3006 should show QVF Platform homepage

#### Start Both Together
```bash
# From project root  
pnpm run dev
```

### 5. Verify QVF Core Integration

Test that the symlinked QVF core is accessible:
```python
# In apps/api Python environment
from packages.qvf_core.ado import work_items
from packages.qvf_core.core import qvf_scorer

# Should import without errors
```

### 6. Test API Endpoints

Using curl or Postman, test:
- [ ] Health check: `GET http://localhost:8000/health`
- [ ] API documentation: `GET http://localhost:8000/docs`
- [ ] Work items: `GET http://localhost:8000/api/v1/work-items/`
- [ ] QVF criteria: `GET http://localhost:8000/api/v1/qvf/criteria`

### 7. Verify Frontend Integration

Test frontend functionality:
- [ ] Homepage loads at http://localhost:3006
- [ ] Navigation works
- [ ] API calls work (check Network tab in DevTools)
- [ ] TypeScript compilation: `pnpm run typecheck`

## Development Workflow Changes

### Before (Old Structure)
```bash
# Direct QVF engine usage
python -m datascience_platform.qvf.ado.work_items

# Scripts in root directory
./ds-analyze file.csv
```

### After (New Structure)  
```bash
# API-based development
pnpm run dev  # Starts both frontend and backend

# QVF engine still available through symlink
python -c "from packages.qvf_core.ado import work_items"

# Existing scripts still work from main project root
cd ../.. && ./ds-analyze file.csv
```

## Code Migration Examples

### API Integration
```typescript
// Before: Direct QVF calls
import { qvfEngine } from '../datascience_platform/qvf'

// After: API calls
import { WorkItem, QVFScore } from '@qvf/shared-types'
import axios from 'axios'

const response = await axios.get<WorkItem[]>('/api/v1/work-items')
```

### Component Development
```tsx
// Before: No structured components
// Direct HTML/CSS

// After: Structured components
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
```

## Troubleshooting

### Common Issues

#### Symlink Problems
```bash
# If symlink is broken
cd packages/
rm qvf-core
ln -sf ../../src/datascience_platform/qvf qvf-core
```

#### Port Conflicts
- Frontend: Change port in `apps/web/package.json` scripts
- Backend: Use different port with `--port` flag

#### Import Errors
```python
# If Python imports fail, add to PYTHONPATH
export PYTHONPATH="/Users/umasankrudhya/Projects/ds-package:$PYTHONPATH"
```

#### TypeScript Errors
```bash
# Clear Next.js cache
rm -rf apps/web/.next
pnpm run build
```

### Verification Commands
```bash
# Check symlink
ls -la packages/qvf-core

# Test QVF engine accessibility  
python -c "import sys; sys.path.append('packages'); from qvf_core import __init__"

# Verify API
curl http://localhost:8000/health

# Test frontend build
pnpm run build
```

## Rollback Plan

If issues arise, the existing structure is completely preserved:

1. **Existing QVF Engine**: Unchanged at `src/datascience_platform/qvf/`
2. **Existing Scripts**: Still functional in project root
3. **Existing Tests**: Continue to work as before

To rollback:
```bash
# Simply use existing structure
cd /Users/umasankrudhya/Projects/ds-package/
python -m datascience_platform.qvf --help
./ds-analyze file.csv
```

## Post-Migration Tasks

### Development
- [ ] Update IDE workspace to include qvf-platform directory
- [ ] Configure debugger for both Python API and TypeScript frontend
- [ ] Set up pre-commit hooks for the monorepo
- [ ] Update documentation with new development workflow

### Team Onboarding  
- [ ] Share this migration guide with team
- [ ] Update development environment setup docs
- [ ] Create video walkthrough of new structure
- [ ] Schedule team demo of new capabilities

### Production Preparation
- [ ] Configure CI/CD pipeline for monorepo structure
- [ ] Set up Docker containers for API and frontend
- [ ] Configure database migrations
- [ ] Set up monitoring and logging

## Benefits of New Structure

### For Developers
- **Modern Stack**: Next.js 14, FastAPI, TypeScript
- **Better DX**: Hot reload, type safety, component library
- **Clear Separation**: API, frontend, and shared types clearly separated
- **Monorepo Benefits**: Shared dependencies, coordinated releases

### For Product
- **Scalability**: Modern architecture supports growth
- **Performance**: Optimized frontend and API
- **Security**: Proper authentication and validation
- **Maintainability**: Clear structure and separation of concerns

### For Operations
- **Deployment**: Container-ready structure
- **Monitoring**: Built-in health checks and structured logging
- **Configuration**: Environment-based configuration
- **Documentation**: Auto-generated API docs

## Next Steps After Migration

1. **Integrate Real Authentication**: Replace placeholder auth with real user management
2. **Connect QVF Engine**: Replace API placeholders with actual QVF core calls
3. **Build Dashboards**: Create rich visualizations using existing QVF data
4. **Add Real-time Features**: WebSocket integration for live updates
5. **Production Deployment**: Configure for your hosting environment

## Support

If you encounter issues during migration:
1. Check this troubleshooting section
2. Verify symlinks are working correctly
3. Ensure all dependencies are installed
4. Test with the verification commands provided

The new structure is designed to be completely additive - your existing QVF engine continues to work exactly as before, while providing a modern application foundation for future development.