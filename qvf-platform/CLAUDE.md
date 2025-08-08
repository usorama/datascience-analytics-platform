# QVF Platform - Application Structure

## Overview
**ARCHITECTURE STATUS**: Monorepo structure created but minimally implemented. QVF backend remains in traditional Python package structure.

**Created**: August 8, 2025  
**Architecture**: Planned monorepo with symlinked core engine preservation  
**Current Reality**: Structure exists, implementation incomplete (~10% complete)
**Purpose**: Intended scalable application structure for QVF enterprise deployment

## ⚠️ **CRITICAL: REALITY VS PLAN**

### **Current State Assessment (August 8, 2025)**
- **Directory Structure**: ✅ Created (monorepo folders exist)
- **API Implementation**: ⚠️ Minimal (310 lines of Python, basic FastAPI setup)
- **Web Implementation**: ❌ Skeletal (66 lines of TypeScript, no functional components)
- **Shared Types**: ⚠️ Basic structure only
- **Database**: ❌ Not implemented
- **Authentication**: ❌ Not implemented

### **Functional QVF Backend Location**
- **Active Development**: `/src/datascience_platform/qvf/` (9,852 lines of code)
- **ADO Integration**: Fully implemented with test suite
- **QVF Scoring**: Core algorithms complete
- **AI Integration**: Ollama manager and semantic analysis ready

### **Architecture Decision Required**
**Before frontend development can proceed, team must decide**:
1. **Complete monorepo migration** (move backend to qvf-platform/apps/api/) - 40+ SP effort
2. **Keep hybrid approach** (backend in datascience_platform, frontend in qvf-platform) - 0 SP effort
3. **Abandon monorepo** (build frontend in datascience_platform/qvf/ui/) - minimal effort

## Project Structure
```
qvf-platform/
├── apps/                           # Application layer
│   ├── api/                        # FastAPI backend
│   │   ├── src/qvf_api/           # API source code
│   │   │   ├── main.py            # FastAPI app entry
│   │   │   ├── routers/           # API route handlers
│   │   │   ├── services/          # Business logic layer
│   │   │   ├── models/            # Database models
│   │   │   └── config.py          # Configuration settings
│   │   ├── requirements.txt       # Python dependencies
│   │   └── pyproject.toml         # Modern Python packaging
│   └── web/                       # Next.js 14 frontend
│       ├── src/                   # Source code
│       │   ├── app/               # Next.js app router
│       │   ├── components/        # React components
│       │   └── lib/               # Utilities and helpers
│       └── package.json           # Node.js dependencies
├── packages/                       # Shared packages
│   ├── qvf-core -> ../../src/     # Symlink to existing QVF engine
│   └── shared-types/              # TypeScript type definitions
├── services/                       # Microservices
│   └── ado-sync/                  # Azure DevOps sync service
└── package.json                   # Monorepo root configuration
```

## Core Design Principles

### 1. **Preservation Strategy**
- **Symlink Architecture**: `packages/qvf-core` symlinks to existing QVF engine
- **No Code Duplication**: Existing QVF logic remains in original location
- **Backward Compatibility**: All existing scripts and imports continue working

### 2. **Modern Application Architecture**
- **API-First**: FastAPI backend with OpenAPI documentation
- **Type Safety**: Shared TypeScript types across frontend and backend
- **Component-Based**: React components with Shadcn/UI design system
- **Monorepo Management**: PNPM workspaces for efficient dependency management

### 3. **Enterprise Standards**
- **Port Configuration**: Web app on port 3006 (per project standards)
- **Environment Configuration**: Proper .env handling and settings management
- **Security**: JWT authentication, CORS configuration, input validation
- **Testing**: Comprehensive test structure for all components

## Technology Stack

### Frontend (Next.js 14)
- **Framework**: Next.js 14 with App Router
- **UI Library**: Shadcn/UI components with Tailwind CSS v4
- **State Management**: TanStack Query for server state
- **Type Safety**: TypeScript with strict mode
- **Styling**: Tailwind CSS with CSS variables for theming

### Backend (FastAPI)
- **API Framework**: FastAPI with automatic OpenAPI docs
- **Authentication**: JWT with OAuth2 password flow
- **Database**: SQLAlchemy with Alembic migrations
- **Validation**: Pydantic models for request/response validation
- **CORS**: Configured for frontend integration

### Shared Infrastructure
- **Types**: Shared TypeScript definitions in `@qvf/shared-types`
- **Core Engine**: Symlinked QVF engine for scoring and analysis
- **Sync Service**: Dedicated ADO sync service for work item updates

## Development Workflow

### ⚠️ **CURRENT LIMITATIONS**
**These commands are defined but not fully functional until architecture decision is made.**

### Installation
```bash
# Install monorepo dependencies (basic structure only)
pnpm install

# Install Python API dependencies (minimal FastAPI setup)
pnpm run install:api

# NOTE: Functional QVF backend is in /src/datascience_platform/qvf/
cd ../
pip install -e .
```

### Development Commands
```bash
# ❌ NOT FUNCTIONAL - requires implementation
pnpm run dev

# ❌ MINIMAL - basic web structure only
pnpm run dev:web    # Next.js on port 3006 (skeleton only)

# ⚠️ MINIMAL - basic FastAPI setup
pnpm run dev:api    # FastAPI on port 8000 (not connected to QVF backend)

# ✅ WORKING QVF BACKEND
cd ../src/datascience_platform/qvf/
python -m qvf --help
```

### API Development
```bash
cd apps/api
python -m uvicorn qvf_api.main:app --reload
# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

## Integration Points

### QVF Core Integration
```python
# In API services, import from symlinked core
from qvf_core.ado import WorkItemsClient
from qvf_core.core import QVFScorer
from qvf_core.ai import SemanticAnalyzer
```

### Type Safety
```typescript
// Shared types available in both frontend and API
import { WorkItem, QVFScore } from '@qvf/shared-types'
```

### API Endpoints
- **Authentication**: `/api/v1/auth/` - JWT authentication
- **QVF Scoring**: `/api/v1/qvf/` - QVF calculation endpoints
- **Work Items**: `/api/v1/work-items/` - Work item CRUD operations

## Migration Instructions

### For Developers
1. **Existing Code**: No changes required to existing QVF engine code
2. **New Development**: Use the structured app format for new features
3. **API Integration**: Use FastAPI endpoints instead of direct QVF calls
4. **Frontend Development**: Build React components in apps/web/src/components/

### For Deployment
1. **Database Setup**: Configure PostgreSQL/SQLite connection in API config
2. **Environment Variables**: Set up .env files for each application
3. **Build Process**: Use pnpm build for frontend, Docker for API
4. **Load Balancer**: Configure nginx to route /api/* to FastAPI backend

## Configuration

### Environment Variables
```bash
# API Configuration (.env in apps/api/)
DATABASE_URL=postgresql://user:pass@localhost/qvf
SECRET_KEY=your-jwt-secret
ADO_ORGANIZATION=your-org
ADO_PROJECT=your-project
ADO_PAT_TOKEN=your-token

# Web Configuration (.env.local in apps/web/)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Port Configuration
- **Frontend**: 3006 (per project requirements)
- **API**: 8000 (FastAPI default)
- **Sync Service**: 8001 (if needed)

## Security Considerations

### Authentication Flow
1. Login via `/api/v1/auth/token` with credentials
2. Receive JWT access token
3. Include token in Authorization header for protected endpoints
4. Token validation on all protected routes

### Data Protection
- Input validation on all API endpoints
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in React components
- CORS properly configured for frontend domain

## Performance Optimizations

### Frontend
- Next.js App Router for optimal loading
- Component lazy loading where appropriate
- Image optimization with Next.js Image component
- CSS-in-JS with Tailwind for minimal bundle size

### Backend
- FastAPI async/await for concurrent request handling
- Database connection pooling
- Response caching for expensive QVF calculations
- Background tasks for long-running operations

## Monitoring and Debugging

### Development Tools
- FastAPI automatic OpenAPI documentation
- Next.js development server with hot reload
- TypeScript strict mode for compile-time error detection
- Shared types prevent API/frontend mismatches

### Production Monitoring
- Structured logging in both frontend and backend
- Error tracking integration points
- Performance monitoring hooks
- Health check endpoints

## Next Steps

### Immediate Tasks
1. Set up development environment with pnpm install
2. Configure database connection for API
3. Set up authentication flow with real user management
4. Integrate actual QVF core engine calls
5. Build production deployment configuration

### Future Enhancements
- Real-time updates via WebSocket connections
- Advanced dashboard visualizations
- Multi-tenant support for different teams
- Automated testing pipeline integration
- Container orchestration with Docker Compose

## Support and Documentation

### API Documentation
- Interactive docs available at `/docs` when API is running
- Schema definitions in shared-types package
- Example requests and responses in router files

### Component Library
- Storybook integration for component development
- Design system documentation
- Accessibility guidelines and testing

This structure provides a modern, scalable foundation for QVF Platform development while preserving all existing functionality and maintaining enterprise-grade standards.