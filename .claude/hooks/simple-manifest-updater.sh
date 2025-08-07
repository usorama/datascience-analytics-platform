#!/bin/bash
# Simple Manifest Auto-Updater Hook
# Creates basic project manifests without complex JSON manipulation

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
MANIFEST_DIR="docs/manifests"
TIMESTAMP=$(date -Iseconds)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[$(date '+%H:%M:%S')] $1${NC}"
}

cd "$PROJECT_DIR" || exit 1

# Create manifest directory
mkdir -p "$MANIFEST_DIR"

log "📋 Generating project manifests..." "$BLUE"

# 1. File Structure Manifest
cat > "$MANIFEST_DIR/file-structure.json" << EOF
{
  "generated": "$TIMESTAMP",
  "generator": "simple-manifest-updater.sh",
  "project_structure": {
    "frontend": {
      "root": "client/",
      "key_directories": [
$(find client -type d -not -path "*/node_modules/*" -not -path "*/.next/*" 2>/dev/null | head -20 | sed 's/^/        "/' | sed 's/$/"/' | paste -sd,)
      ],
      "component_files": [
$(find client -name "*.tsx" -not -path "*/node_modules/*" 2>/dev/null | head -10 | sed 's/^/        "/' | sed 's/$/"/' | paste -sd,)
      ]
    },
    "backend": {
      "root": "server/",
      "key_directories": [
$(find server -type d -not -path "*/node_modules/*" -not -path "*/dist/*" 2>/dev/null | head -20 | sed 's/^/        "/' | sed 's/$/"/' | paste -sd,)
      ],
      "source_files": [
$(find server -name "*.ts" -not -path "*/node_modules/*" 2>/dev/null | head -10 | sed 's/^/        "/' | sed 's/$/"/' | paste -sd,)
      ]
    }
  },
  "statistics": {
    "total_directories": $(find . -type d -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' '),
    "typescript_files": $(find . -name "*.ts" -o -name "*.tsx" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' '),
    "markdown_files": $(find . -name "*.md" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
  }
}
EOF

# 2. API Endpoints Manifest
cat > "$MANIFEST_DIR/api-endpoints.json" << EOF
{
  "generated": "$TIMESTAMP",
  "generator": "simple-manifest-updater.sh",
  "api_structure": {
    "route_files": [
$(find server/src -name "*routes*.ts" -o -name "*routes*.js" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ],
    "middleware_files": [
$(find server/src -path "*/middleware/*" -name "*.ts" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ],
    "controller_files": [
$(find server/src -path "*controller*" -name "*.ts" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ]
  },
  "summary": {
    "total_route_files": $(find server/src -name "*routes*.ts" -o -name "*routes*.js" 2>/dev/null | wc -l | tr -d ' '),
    "total_middleware": $(find server/src -path "*/middleware/*" -name "*.ts" 2>/dev/null | wc -l | tr -d ' ')
  }
}
EOF

# 3. Dependencies Manifest
cat > "$MANIFEST_DIR/dependencies.json" << EOF
{
  "generated": "$TIMESTAMP",
  "generator": "simple-manifest-updater.sh",
  "package_files": {
    "root": $(if [[ -f "package.json" ]]; then echo '"package.json"'; else echo "null"; fi),
    "client": $(if [[ -f "client/package.json" ]]; then echo '"client/package.json"'; else echo "null"; fi),
    "server": $(if [[ -f "server/package.json" ]]; then echo '"server/package.json"'; else echo "null"; fi)
  },
  "package_manager": "$(if [[ -f "pnpm-lock.yaml" ]]; then echo "pnpm"; elif [[ -f "yarn.lock" ]]; then echo "yarn"; else echo "npm"; fi)",
  "workspace_count": $(find . -name "package.json" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
}
EOF

# 4. Documentation Manifest
cat > "$MANIFEST_DIR/documentation.json" << EOF
{
  "generated": "$TIMESTAMP",
  "generator": "simple-manifest-updater.sh",
  "documentation_files": {
    "root_docs": [
$(find . -maxdepth 1 -name "*.md" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ],
    "docs_directory": [
$(find docs -name "*.md" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ],
    "readme_files": [
$(find . -name "README.md" -not -path "*/node_modules/*" 2>/dev/null | sed 's/^/      "/' | sed 's/$/"/' | paste -sd,)
    ]
  },
  "summary": {
    "total_markdown_files": $(find . -name "*.md" -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' '),
    "documentation_coverage": "$(if [[ -f "CLAUDE.md" && -f "design.md" && -f "README.md" ]]; then echo "complete"; else echo "partial"; fi)"
  }
}
EOF

# 5. Index Manifest
cat > "$MANIFEST_DIR/index.json" << EOF
{
  "generated": "$TIMESTAMP",
  "generator": "simple-manifest-updater.sh",
  "manifests": {
    "file_structure": "file-structure.json",
    "api_endpoints": "api-endpoints.json", 
    "dependencies": "dependencies.json",
    "documentation": "documentation.json"
  },
  "project_info": {
    "name": "Virtual Tutor AI",
    "last_manifest_update": "$TIMESTAMP",
    "git_commit": "$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
  }
}
EOF

log "✅ Generated manifests:" "$GREEN"
echo "  • file-structure.json - Project directory structure"
echo "  • api-endpoints.json - Backend API organization"
echo "  • dependencies.json - Package management info"
echo "  • documentation.json - Documentation inventory"
echo "  • index.json - Manifest index and metadata"

log "📁 Manifests saved to: $MANIFEST_DIR" "$BLUE"

exit 0