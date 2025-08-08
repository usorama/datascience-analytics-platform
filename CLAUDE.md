# CLAUDE.md - DataScience Platform

## CRITICAL: Protected Directories
**NEVER delete/modify**: `.claude/` (222 files) and `.bmad-core/` (83 files) - essential for Claude Code multi-agent toolkit

## Project Overview
Production-ready ML analytics platform with GPU acceleration, enterprise Agile metrics, and TypeScript/React dashboard generation.

## QVF Platform Architecture (NEW)
**Status**: Architecture redesign in progress - transitioning to modern application structure

The QVF system is being restructured as a **production-ready application platform** with:
- **Monorepo Architecture**: Clear separation between apps, packages, and services
- **Modern Stack**: FastAPI backend + Next.js 14 frontend + PostgreSQL database
- **Type Safety**: End-to-end TypeScript integration with OpenAPI code generation
- **Scalable Design**: Industry-standard patterns supporting team collaboration

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

## QVF Development (Active)
- **Scope**: 270 story points = ~6 days with Claude Code
- **Tracking**: `docs/bmad/qvf-progress.md`, sprint plans in `docs/bmad/`
- **Foundation**: Leverages existing AHP engine (80% complete)
- **SAFe Agent**: Ollama LLM, ChromaDB vectors, RL coaching
- **Architecture**: Modern application platform (see ADR-001)

### Migration Status
- ✅ **Architecture Design**: Complete monorepo structure designed
- ✅ **Technology Stack**: FastAPI + Next.js + PostgreSQL selected
- ✅ **API Design**: REST endpoints and data models defined
- ⏳ **Implementation**: Ready to begin development phases
- ⏳ **Data Migration**: Scripts and procedures planned

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