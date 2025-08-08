# CLAUDE.md - DataScience Platform

## CRITICAL: Protected Directories
**NEVER delete/modify**: `.claude/` (222 files) and `.bmad-core/` (83 files) - essential for Claude Code multi-agent toolkit

## Automation Status (Redesigned: 2025-08-08)
✅ **Global Hook Architecture**: Universal orchestrators in `~/.claude/hooks/`
✅ **Project-Agnostic**: Uses `$CLAUDE_PROJECT_DIR` environment variable
✅ **Documentation Updates**: Global hook checks for project-specific `documentation_updater.py`
✅ **Git Checkpoints**: Global hook checks for project-specific `task-completion-detector.py`
✅ **No More Errors**: Graceful fallback when project scripts don't exist

## Project Overview
Production-ready ML analytics platform with GPU acceleration, enterprise Agile metrics, and TypeScript/React dashboard generation.

## QVF Platform Architecture Status
**Status**: ⚠️ **Architecture Decision Required** - Major gap between documentation and reality identified

**Current Reality Assessment (August 8, 2025)**:
- **Traditional Backend**: `/src/datascience_platform/qvf/` (9,852 lines, 75% complete, production-ready ADO integration)
- **Monorepo Structure**: `/qvf-platform/` (created but minimal implementation, ~10% complete)
- **Critical Gap**: Documentation claimed completion vs actual skeleton implementation

**Architecture Decision Required Before Frontend Development**:
- **Option 1**: Complete monorepo migration (40+ SP effort, 6+ days)
- **Option 2**: Hybrid approach (preserve backend, build frontend in monorepo, minimal effort)
- **Option 3**: Traditional approach (build frontend in existing package structure)

### Planned Structure
```
qvf-platform/
├── apps/
│   ├── api/          # FastAPI backend application
│   └── web/          # Next.js frontend application
├── packages/
│   ├── qvf-core/     # Existing QVF engine (preserved)
│   ├── shared-types/ # Shared TypeScript/Python types
│   └── database/     # Database models and migrations
└── services/
    └── ado-sync/     # ADO integration service
```

See `docs/architecture/adr/001-qvf-platform-architecture.md` for complete architectural decisions.

## Essential Commands
```bash
# CLI Tools (executable scripts)
./dsplatform --help                    # Main CLI
./ds-analyze <file.csv>                # Quick analysis
./ds-dashboard <file.csv>              # Generate dashboard

# Installation
pip install -e .
pip install -r requirements-nlp.txt    # GPU features

# Validation
python3 scripts/verify_installation.py
python3 scripts/performance_benchmark.py
```

## Core Modules
- **ado/**: 25+ Agile metrics, semantic alignment, QVF framework
- **nlp/**: GPU-accelerated embeddings (MPS/CUDA/CPU), FAISS vectors
- **dashboard/**: TypeScript/React generation with SSR
- **mle_star/**: ML pipeline optimization with ablation
- **ml/**: AutoGluon integration, statistical analysis
- **etl/**: Multi-format data processing

## Production Standards
- **Code**: Type hints, >90% test coverage, comprehensive error handling
- **Performance**: Auto GPU detection, 90%+ cache hit rate, batch processing
- **Testing**: `pytest tests/ --cov=src`, component-specific scripts in `scripts/`
- **Quality**: `black`, `isort`, `flake8`, `mypy` for all code

## QVF Development Status
- **Total Scope**: 470 story points
- **Completed**: 125 SP (26.6%) - QVF backend core and monorepo structure created
- **Remaining**: 345 SP - Architecture decision required before frontend development can proceed
- **Tracking**: `docs/bmad/qvf-progress.md`, `docs/bmad/qvf-project-status-reality-assessment.md`
- **Foundation**: QVF backend 75% complete with production-ready ADO integration
- **Critical Blocker**: Frontend development blocked pending architecture decision

### Current Implementation Status
- ✅ **Architecture Design**: Monorepo structure created
- ⚠️ **Backend Implementation**: 75% complete in traditional structure (`/src/datascience_platform/qvf/`)
- ❌ **API Integration**: Minimal FastAPI setup, not connected to QVF backend
- ❌ **Frontend Implementation**: Skeleton only, no functional components
- ⚠️ **Technology Stack**: Planned but not implemented
- ⚠️ **Database Layer**: Not implemented in either structure

## Working QVF Backend Location

**Primary Development Location**: `/src/datascience_platform/qvf/`
- **Lines of Code**: 9,852 across 45 Python files
- **ADO Integration**: Fully implemented with comprehensive test suite
- **QVF Scoring**: Core algorithms complete and tested
- **AI Integration**: Ollama manager and semantic analysis ready
- **Status**: 75% complete, production-ready for ADO integration

**Usage**:
```bash
# Working QVF CLI
python -m src.datascience_platform.qvf --help

# ADO Integration Testing
python src/datascience_platform/qvf/ado/tests/run_integration_tests.py
```

## Critical Rules
1. **Read before write**: Always examine existing code patterns
2. **Production only**: No experimental code, TODOs, or placeholders
3. **Test everything**: Run quality gates before declaring complete
4. **Preserve structure**: Don't modify protected directories or config files
5. **Codebase context**: This project is largely developed and currently in improvement.  Check what's there before creating anything new.
6. **Guiding Principle**: No duplication of any kind, what-so-ever.  If you see something that is similar, ask if it can be refactored to use the existing code or make that decision yourself with full project context.
7. **Documentation Rules**: Always keep all planning and progress documentation up-to-date.  This is a critical part of the project and should be maintained at all times.

## Module Usage Examples
```python
from datascience_platform.ado import ADOAnalyzer
from datascience_platform.nlp import SemanticEmbedder
from datascience_platform.dashboard.generative import DashboardGenerator

embedder = SemanticEmbedder(device="auto")  # GPU auto-detection
analyzer = ADOAnalyzer(config_path="production.yaml")
generator = DashboardGenerator(theme="enterprise")
```

## References
- **Current Architecture**: `docs/bmad/technical-architecture-qvf.md`
- **New Architecture**: `docs/architecture/adr/001-qvf-platform-architecture.md` 
- **Module docs**: Each module has CLAUDE.md with specifics
- **Examples**: `examples/` directory with working demos
- **Testing**: `scripts/test_*.py` for component validation

### Architecture Documentation
- **ADR-001**: QVF Platform Application Architecture (monorepo design)
- **API Design**: REST endpoints, data models, authentication
- **Migration Plan**: 4-phase transition from current to new structure
- **Technology Stack**: FastAPI, Next.js, PostgreSQL, Redis decisions
- **Database Schema**: Personal metrics, QVF sessions, user management

**NOTE**: This is a production system. All changes must meet enterprise standards with full testing and documentation.