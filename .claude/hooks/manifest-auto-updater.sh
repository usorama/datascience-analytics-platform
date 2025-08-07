#!/bin/bash
# Manifest Auto-Updater Hook
# Automatically updates project manifests when code structure changes
# Usage: ./manifest-auto-updater.sh [--dry-run] [--force]

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
DRY_RUN=false
FORCE_UPDATE=false
MANIFEST_DIR="docs/manifests"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--force]"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${2:-$NC}[$(date '+%H:%M:%S')] $1${NC}"
}

# Change to project directory
cd "$PROJECT_DIR" || {
    log "❌ Failed to change to project directory: $PROJECT_DIR" "$RED"
    exit 1
}

# Create manifest directory if it doesn't exist
if [[ ! -d "$MANIFEST_DIR" ]]; then
    if [[ "$DRY_RUN" == "false" ]]; then
        mkdir -p "$MANIFEST_DIR"
        log "📁 Created manifest directory: $MANIFEST_DIR" "$GREEN"
    else
        log "📁 Would create manifest directory: $MANIFEST_DIR" "$YELLOW"
    fi
fi

log "🔄 Starting manifest auto-update..." "$BLUE"

# Function to generate file structure manifest
generate_file_structure_manifest() {
    local output_file="$1"
    local temp_file=$(mktemp)
    
    cat > "$temp_file" << EOF
{
  "generated": "$(date -Iseconds)",
  "generator": "manifest-auto-updater.sh",
  "project_root": "$(pwd)",
  "structure": {
EOF

    # Generate frontend structure
    if [[ -d "client" ]]; then
        echo '    "frontend": {' >> "$temp_file"
        echo '      "root": "client/",' >> "$temp_file"
        echo '      "directories": [' >> "$temp_file"
        
        find client -type d -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/dist/*" | sort | while read -r dir; do
            echo "        \"$dir\"," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '      ],' >> "$temp_file"
        echo '      "key_files": [' >> "$temp_file"
        
        # Find key frontend files
        find client -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.json" \) -not -path "*/node_modules/*" | head -20 | sort | while read -r file; do
            echo "        \"$file\"," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '      ]' >> "$temp_file"
        echo '    },' >> "$temp_file"
    fi

    # Generate backend structure
    if [[ -d "server" ]]; then
        echo '    "backend": {' >> "$temp_file"
        echo '      "root": "server/",' >> "$temp_file"
        echo '      "directories": [' >> "$temp_file"
        
        find server -type d -not -path "*/node_modules/*" -not -path "*/dist/*" | sort | while read -r dir; do
            echo "        \"$dir\"," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '      ],' >> "$temp_file"
        echo '      "key_files": [' >> "$temp_file"
        
        # Find key backend files
        find server -type f \( -name "*.ts" -o -name "*.js" -o -name "*.json" \) -not -path "*/node_modules/*" | head -20 | sort | while read -r file; do
            echo "        \"$file\"," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '      ]' >> "$temp_file"
        echo '    },' >> "$temp_file"
    fi

    # Generate documentation structure
    if [[ -d "docs" ]]; then
        echo '    "documentation": {' >> "$temp_file"
        echo '      "root": "docs/",' >> "$temp_file"
        echo '      "files": [' >> "$temp_file"
        
        find docs -type f -name "*.md" | sort | while read -r file; do
            echo "        \"$file\"," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '      ]' >> "$temp_file"
        echo '    }' >> "$temp_file"
    fi

    # Close structure object
    sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
    
    cat >> "$temp_file" << EOF
  },
  "statistics": {
    "total_directories": $(find . -type d -not -path "*/node_modules/*" -not -path "*/.git/*" | wc -l | tr -d ' '),
    "total_files": $(find . -type f -not -path "*/node_modules/*" -not -path "*/.git/*" | wc -l | tr -d ' '),
    "typescript_files": $(find . -name "*.ts" -o -name "*.tsx" -not -path "*/node_modules/*" | wc -l | tr -d ' '),
    "javascript_files": $(find . -name "*.js" -o -name "*.jsx" -not -path "*/node_modules/*" | wc -l | tr -d ' '),
    "markdown_files": $(find . -name "*.md" -not -path "*/node_modules/*" | wc -l | tr -d ' ')
  }
}
EOF

    if [[ "$DRY_RUN" == "false" ]]; then
        mv "$temp_file" "$output_file"
        log "📄 Updated file structure manifest: $output_file" "$GREEN"
    else
        log "📄 Would update file structure manifest: $output_file" "$YELLOW"
        rm "$temp_file"
    fi
}

# Function to generate API manifest
generate_api_manifest() {
    local output_file="$1"
    local temp_file=$(mktemp)
    
    cat > "$temp_file" << EOF
{
  "generated": "$(date -Iseconds)",
  "generator": "manifest-auto-updater.sh",
  "api_version": "v1",
  "endpoints": {
EOF

    # Scan for route files
    if [[ -d "server/src/presentation/routes" ]]; then
        echo '    "routes": [' >> "$temp_file"
        
        find server/src/presentation/routes -name "*.ts" -o -name "*.js" | while read -r route_file; do
            # Extract route information
            route_name=$(basename "$route_file" | sed 's/\.[^.]*$//')
            
            # Try to extract HTTP methods from the file
            methods=$(grep -E "(router\.(get|post|put|delete|patch))" "$route_file" | sed -E 's/.*router\.([^(]+).*/\1/' | sort -u | tr '\n' ',' | sed 's/,$//')
            
            if [[ -n "$methods" ]]; then
                echo "      {" >> "$temp_file"
                echo "        \"file\": \"$route_file\"," >> "$temp_file"
                echo "        \"name\": \"$route_name\"," >> "$temp_file"
                echo "        \"methods\": \"$methods\"" >> "$temp_file"
                echo "      }," >> "$temp_file"
            fi
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '    ],' >> "$temp_file"
    fi

    # Add middleware information
    if [[ -d "server/src/middleware" ]]; then
        echo '    "middleware": [' >> "$temp_file"
        
        find server/src/middleware -name "*.ts" -o -name "*.js" | while read -r middleware_file; do
            middleware_name=$(basename "$middleware_file" | sed 's/\.[^.]*$//')
            echo "      {" >> "$temp_file"
            echo "        \"file\": \"$middleware_file\"," >> "$temp_file"
            echo "        \"name\": \"$middleware_name\"" >> "$temp_file"
            echo "      }," >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '    ],' >> "$temp_file"
    fi

    # Remove trailing comma from endpoints
    sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
    
    cat >> "$temp_file" << EOF
  },
  "dependencies": {
EOF

    # Extract API dependencies from package.json
    if [[ -f "server/package.json" ]]; then
        echo '    "runtime": [' >> "$temp_file"
        
        # Extract key API-related dependencies
        grep -E '"(express|fastify|koa|socket\.io|cors|helmet|morgan)"' server/package.json | while read -r dep; do
            echo "      $dep" >> "$temp_file"
        done
        
        # Remove trailing comma
        sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
        
        echo '    ]' >> "$temp_file"
    fi

    echo '  }' >> "$temp_file"
    echo '}' >> "$temp_file"

    if [[ "$DRY_RUN" == "false" ]]; then
        mv "$temp_file" "$output_file"
        log "🔌 Updated API manifest: $output_file" "$GREEN"
    else
        log "🔌 Would update API manifest: $output_file" "$YELLOW"
        rm "$temp_file"
    fi
}

# Function to generate dependencies manifest
generate_dependencies_manifest() {
    local output_file="$1"
    local temp_file=$(mktemp)
    
    cat > "$temp_file" << EOF
{
  "generated": "$(date -Iseconds)",
  "generator": "manifest-auto-updater.sh",
  "workspaces": {
EOF

    # Root dependencies
    if [[ -f "package.json" ]]; then
        echo '    "root": {' >> "$temp_file"
        echo '      "package_file": "package.json",' >> "$temp_file"
        echo '      "dependencies": {' >> "$temp_file"
        
        if grep -q '"dependencies"' package.json; then
            echo '        "production": [' >> "$temp_file"
            sed -n '/"dependencies":/,/}/p' package.json | grep '"' | grep -v '"dependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ],' >> "$temp_file"
        fi
        
        if grep -q '"devDependencies"' package.json; then
            echo '        "development": [' >> "$temp_file"
            sed -n '/"devDependencies":/,/}/p' package.json | grep '"' | grep -v '"devDependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ]' >> "$temp_file"
        fi
        
        echo '      }' >> "$temp_file"
        echo '    },' >> "$temp_file"
    fi

    # Client dependencies
    if [[ -f "client/package.json" ]]; then
        echo '    "client": {' >> "$temp_file"
        echo '      "package_file": "client/package.json",' >> "$temp_file"
        echo '      "dependencies": {' >> "$temp_file"
        
        if grep -q '"dependencies"' client/package.json; then
            echo '        "production": [' >> "$temp_file"
            sed -n '/"dependencies":/,/}/p' client/package.json | grep '"' | grep -v '"dependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ],' >> "$temp_file"
        fi
        
        if grep -q '"devDependencies"' client/package.json; then
            echo '        "development": [' >> "$temp_file"
            sed -n '/"devDependencies":/,/}/p' client/package.json | grep '"' | grep -v '"devDependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ]' >> "$temp_file"
        fi
        
        echo '      }' >> "$temp_file"
        echo '    },' >> "$temp_file"
    fi

    # Server dependencies
    if [[ -f "server/package.json" ]]; then
        echo '    "server": {' >> "$temp_file"
        echo '      "package_file": "server/package.json",' >> "$temp_file"
        echo '      "dependencies": {' >> "$temp_file"
        
        if grep -q '"dependencies"' server/package.json; then
            echo '        "production": [' >> "$temp_file"
            sed -n '/"dependencies":/,/}/p' server/package.json | grep '"' | grep -v '"dependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ],' >> "$temp_file"
        fi
        
        if grep -q '"devDependencies"' server/package.json; then
            echo '        "development": [' >> "$temp_file"
            sed -n '/"devDependencies":/,/}/p' server/package.json | grep '"' | grep -v '"devDependencies"' | grep -v '}' | while read -r dep; do
                echo "          $dep" >> "$temp_file"
            done
            sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
            echo '        ]' >> "$temp_file"
        fi
        
        echo '      }' >> "$temp_file"
        echo '    }' >> "$temp_file"
    fi

    # Remove trailing comma
    sed -i.bak '$ s/,$//' "$temp_file" && rm "${temp_file}.bak"
    
    echo '  },' >> "$temp_file"
    
    # Add summary statistics
    echo '  "summary": {' >> "$temp_file"
    echo "    \"total_workspaces\": $(find . -name "package.json" -not -path "*/node_modules/*" | wc -l | tr -d ' ')," >> "$temp_file"
    echo "    \"total_dependencies\": $(cat package.json client/package.json server/package.json 2>/dev/null | grep -c '\".*\":' | tr -d ' ')," >> "$temp_file"
    echo "    \"package_manager\": \"$(if [[ -f "pnpm-lock.yaml" ]]; then echo "pnpm"; elif [[ -f "yarn.lock" ]]; then echo "yarn"; else echo "npm"; fi)\"" >> "$temp_file"
    echo '  }' >> "$temp_file"
    echo '}' >> "$temp_file"

    if [[ "$DRY_RUN" == "false" ]]; then
        mv "$temp_file" "$output_file"
        log "📦 Updated dependencies manifest: $output_file" "$GREEN"
    else
        log "📦 Would update dependencies manifest: $output_file" "$YELLOW"
        rm "$temp_file"
    fi
}

# Function to check if manifests need updating
needs_update() {
    local manifest_file="$1"
    local source_pattern="$2"
    
    if [[ ! -f "$manifest_file" || "$FORCE_UPDATE" == "true" ]]; then
        return 0  # Needs update
    fi
    
    # Get last modification time of manifest
    local manifest_mtime
    if [[ "$OSTYPE" == "darwin"* ]]; then
        manifest_mtime=$(stat -f %m "$manifest_file")
    else
        manifest_mtime=$(stat -c %Y "$manifest_file")
    fi
    
    # Check if any source files are newer
    while IFS= read -r -d '' file; do
        local file_mtime
        if [[ "$OSTYPE" == "darwin"* ]]; then
            file_mtime=$(stat -f %m "$file")
        else
            file_mtime=$(stat -c %Y "$file")
        fi
        
        if [[ $file_mtime -gt $manifest_mtime ]]; then
            return 0  # Needs update
        fi
    done < <(find . -path "$source_pattern" -type f -print0 2>/dev/null)
    
    return 1  # No update needed
}

# Update file structure manifest
STRUCTURE_MANIFEST="$MANIFEST_DIR/file-structure.json"
if needs_update "$STRUCTURE_MANIFEST" "*" || [[ "$FORCE_UPDATE" == "true" ]]; then
    generate_file_structure_manifest "$STRUCTURE_MANIFEST"
else
    log "📄 File structure manifest is up to date" "$GREEN"
fi

# Update API manifest
API_MANIFEST="$MANIFEST_DIR/api-endpoints.json"
if needs_update "$API_MANIFEST" "server/src/presentation/routes/*" || [[ "$FORCE_UPDATE" == "true" ]]; then
    generate_api_manifest "$API_MANIFEST"
else
    log "🔌 API manifest is up to date" "$GREEN"
fi

# Update dependencies manifest
DEPS_MANIFEST="$MANIFEST_DIR/dependencies.json"
if needs_update "$DEPS_MANIFEST" "*/package.json" || [[ "$FORCE_UPDATE" == "true" ]]; then
    generate_dependencies_manifest "$DEPS_MANIFEST"
else
    log "📦 Dependencies manifest is up to date" "$GREEN"
fi

# Create manifest index
INDEX_FILE="$MANIFEST_DIR/index.json"
if [[ "$DRY_RUN" == "false" ]]; then
    cat > "$INDEX_FILE" << EOF
{
  "generated": "$(date -Iseconds)",
  "manifests": {
    "file_structure": "file-structure.json",
    "api_endpoints": "api-endpoints.json",
    "dependencies": "dependencies.json"
  },
  "description": "Auto-generated project manifests",
  "last_update": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
    log "📋 Updated manifest index: $INDEX_FILE" "$GREEN"
else
    log "📋 Would update manifest index: $INDEX_FILE" "$YELLOW"
fi

log "✅ Manifest auto-update completed" "$GREEN"

if [[ "$DRY_RUN" == "true" ]]; then
    log "🔍 Dry run mode - no files were modified" "$CYAN"
fi

exit 0