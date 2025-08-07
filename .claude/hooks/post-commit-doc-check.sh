#!/bin/bash
# Post-Commit Documentation Check Hook
# Flags documentation updates needed after code commits
# Usage: Called automatically by git post-commit hook

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
COMMIT_HASH="${1:-$(git rev-parse HEAD)}"
COMMIT_SHORT=$(git rev-parse --short "$COMMIT_HASH")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
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

# Verify git repository
if [[ ! -d ".git" ]]; then
    log "❌ Not a git repository" "$RED"
    exit 1
fi

log "📝 Post-commit documentation check for: $COMMIT_SHORT" "$BLUE"

# Get commit information
COMMIT_MESSAGE=$(git log -1 --format="%s" "$COMMIT_HASH")
COMMIT_AUTHOR=$(git log -1 --format="%an" "$COMMIT_HASH")
COMMIT_DATE=$(git log -1 --format="%ad" --date=short "$COMMIT_HASH")

# Get changed files in this commit
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r "$COMMIT_HASH")

log "📊 Commit details:" "$CYAN"
echo "  • Message: $COMMIT_MESSAGE"
echo "  • Author: $COMMIT_AUTHOR"
echo "  • Date: $COMMIT_DATE"
echo "  • Files changed: $(echo "$CHANGED_FILES" | wc -l | tr -d ' ')"

# Initialize tracking arrays
declare -a DOC_UPDATE_NEEDED=()
declare -a MANIFEST_UPDATE_NEEDED=()
declare -a API_DOC_UPDATE_NEEDED=()
declare -a README_UPDATE_NEEDED=()

# Check for significant code changes that need documentation updates
while IFS= read -r file; do
    if [[ -z "$file" ]]; then
        continue
    fi
    
    case "$file" in
        # API route changes
        server/src/presentation/routes/*.ts|server/src/presentation/routes/*.js)
            API_DOC_UPDATE_NEEDED+=("$file")
            log "🔌 API route changed: $file" "$YELLOW"
            ;;
        
        # Core domain/business logic changes
        server/src/domain/*.ts|server/src/core/*.ts|server/src/application/*.ts)
            DOC_UPDATE_NEEDED+=("$file")
            log "🧠 Core logic changed: $file" "$YELLOW"
            ;;
        
        # Database schema/model changes
        server/src/infrastructure/database/*.ts|server/src/models/*.ts)
            DOC_UPDATE_NEEDED+=("$file")
            log "🗄️  Database model changed: $file" "$YELLOW"
            ;;
        
        # Frontend component changes
        client/components/*.tsx|client/app/*.tsx|client/pages/*.tsx)
            DOC_UPDATE_NEEDED+=("$file")
            log "🖥️  Frontend component changed: $file" "$YELLOW"
            ;;
        
        # Package.json changes
        */package.json)
            MANIFEST_UPDATE_NEEDED+=("$file")
            log "📦 Dependencies changed: $file" "$YELLOW"
            ;;
        
        # Configuration changes
        *.config.js|*.config.ts|*.json|*.yaml|*.yml)
            if [[ "$file" != *"node_modules"* ]]; then
                DOC_UPDATE_NEEDED+=("$file")
                log "⚙️  Configuration changed: $file" "$YELLOW"
            fi
            ;;
        
        # Environment or deployment changes
        Dockerfile*|docker-compose*|*.env.example|.github/workflows/*)
            DOC_UPDATE_NEEDED+=("$file")
            log "🚀 Deployment config changed: $file" "$YELLOW"
            ;;
    esac
done <<< "$CHANGED_FILES"

# Check if documentation was updated in the same commit
DOC_FILES_UPDATED=$(echo "$CHANGED_FILES" | grep -E '\.(md|txt|rst)$' || true)
MANIFEST_FILES_UPDATED=$(echo "$CHANGED_FILES" | grep -E 'docs/manifests/.*\.json$' || true)

# Analyze impact and create recommendations
TOTAL_ISSUES=$((${#DOC_UPDATE_NEEDED[@]} + ${#MANIFEST_UPDATE_NEEDED[@]} + ${#API_DOC_UPDATE_NEEDED[@]}))

if [[ $TOTAL_ISSUES -gt 0 ]]; then
    log "⚠️  Documentation update recommendations:" "$YELLOW"
    
    # API documentation recommendations
    if [[ ${#API_DOC_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo
        log "🔌 API Documentation Updates Needed:" "$PURPLE"
        for file in "${API_DOC_UPDATE_NEEDED[@]}"; do
            echo "  • $file"
        done
        
        if [[ -z "$DOC_FILES_UPDATED" ]]; then
            echo
            echo "  📝 Recommended actions:"
            echo "    - Update API documentation in docs/api/"
            echo "    - Update OpenAPI/Swagger specs if available"
            echo "    - Review and update Postman collections"
            echo "    - Update client SDK if applicable"
        fi
    fi
    
    # General documentation recommendations
    if [[ ${#DOC_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo
        log "📚 General Documentation Updates Needed:" "$PURPLE"
        for file in "${DOC_UPDATE_NEEDED[@]}"; do
            echo "  • $file"
        done
        
        if [[ -z "$DOC_FILES_UPDATED" ]]; then
            echo
            echo "  📝 Recommended actions:"
            echo "    - Update relevant README files"
            echo "    - Review architecture documentation"
            echo "    - Update deployment guides if needed"
            echo "    - Check if CLAUDE.md needs updates"
        fi
    fi
    
    # Manifest update recommendations
    if [[ ${#MANIFEST_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo
        log "📋 Manifest Updates Needed:" "$PURPLE"
        for file in "${MANIFEST_UPDATE_NEEDED[@]}"; do
            echo "  • $file"
        done
        
        if [[ -z "$MANIFEST_FILES_UPDATED" ]]; then
            echo
            echo "  📝 Recommended actions:"
            echo "    - Run: .claude/hooks/manifest-auto-updater.sh"
            echo "    - Update setup/installation documentation"
            echo "    - Review dependency compatibility notes"
        fi
    fi
    
    # Create documentation TODO file
    TODO_FILE=".claude/hooks/doc-todos/todo-$(date +%Y%m%d-%H%M%S).md"
    mkdir -p "$(dirname "$TODO_FILE")"
    
    cat > "$TODO_FILE" << EOF
# Documentation TODO - Generated from Commit $COMMIT_SHORT

**Commit**: $COMMIT_HASH  
**Message**: $COMMIT_MESSAGE  
**Author**: $COMMIT_AUTHOR  
**Date**: $COMMIT_DATE  
**Generated**: $(date '+%Y-%m-%d %H:%M:%S')

## Changes Requiring Documentation Updates

EOF

    if [[ ${#API_DOC_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo "### API Documentation" >> "$TODO_FILE"
        for file in "${API_DOC_UPDATE_NEEDED[@]}"; do
            echo "- [ ] Review and update API docs for: \`$file\`" >> "$TODO_FILE"
        done
        echo >> "$TODO_FILE"
    fi
    
    if [[ ${#DOC_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo "### General Documentation" >> "$TODO_FILE"
        for file in "${DOC_UPDATE_NEEDED[@]}"; do
            echo "- [ ] Review documentation impact of: \`$file\`" >> "$TODO_FILE"
        done
        echo >> "$TODO_FILE"
    fi
    
    if [[ ${#MANIFEST_UPDATE_NEEDED[@]} -gt 0 ]]; then
        echo "### Manifest Updates" >> "$TODO_FILE"
        for file in "${MANIFEST_UPDATE_NEEDED[@]}"; do
            echo "- [ ] Update manifests due to: \`$file\`" >> "$TODO_FILE"
        done
        echo "- [ ] Run: \`.claude/hooks/manifest-auto-updater.sh\`" >> "$TODO_FILE"
        echo >> "$TODO_FILE"
    fi
    
    echo "## Recommended Actions" >> "$TODO_FILE"
    echo >> "$TODO_FILE"
    echo "1. **Run Documentation Currency Check**:" >> "$TODO_FILE"
    echo "   \`\`\`bash" >> "$TODO_FILE"
    echo "   .claude/hooks/documentation-currency-check.sh --verbose" >> "$TODO_FILE"
    echo "   \`\`\`" >> "$TODO_FILE"
    echo >> "$TODO_FILE"
    echo "2. **Update Manifests**:" >> "$TODO_FILE"
    echo "   \`\`\`bash" >> "$TODO_FILE"
    echo "   .claude/hooks/manifest-auto-updater.sh" >> "$TODO_FILE"
    echo "   \`\`\`" >> "$TODO_FILE"
    echo >> "$TODO_FILE"
    echo "3. **Review Critical Documentation Files**:" >> "$TODO_FILE"
    echo "   - \`CLAUDE.md\` - Project instructions" >> "$TODO_FILE"
    echo "   - \`design.md\` - UI/UX design system" >> "$TODO_FILE"
    echo "   - \`README.md\` - Project overview" >> "$TODO_FILE"
    echo "   - \`docs/api/\` - API documentation" >> "$TODO_FILE"
    echo >> "$TODO_FILE"
    echo "4. **Consider Creating/Updating**:" >> "$TODO_FILE"
    echo "   - Architecture diagrams" >> "$TODO_FILE"
    echo "   - Deployment guides" >> "$TODO_FILE"
    echo "   - Developer onboarding docs" >> "$TODO_FILE"
    echo "   - Troubleshooting guides" >> "$TODO_FILE"
    echo >> "$TODO_FILE"
    echo "---" >> "$TODO_FILE"
    echo "*This TODO was auto-generated by post-commit-doc-check.sh*" >> "$TODO_FILE"
    
    log "📋 Documentation TODO created: $TODO_FILE" "$GREEN"
    
    # Auto-run manifest updater if requested
    if [[ ${#MANIFEST_UPDATE_NEEDED[@]} -gt 0 ]]; then
        log "🔄 Auto-running manifest updater..." "$CYAN"
        if .claude/hooks/manifest-auto-updater.sh; then
            log "✅ Manifests updated automatically" "$GREEN"
        else
            log "⚠️  Manifest update failed - manual intervention needed" "$YELLOW"
        fi
    fi
    
else
    log "✅ No documentation updates needed for this commit" "$GREEN"
fi

# Check for documentation-only commits
if [[ -n "$DOC_FILES_UPDATED" && $TOTAL_ISSUES -eq 0 ]]; then
    log "📚 Documentation-only commit detected" "$GREEN"
    echo "  • Updated files: $(echo "$DOC_FILES_UPDATED" | tr '\n' ' ')"
fi

# Summary statistics
log "📊 Post-commit analysis summary:" "$BLUE"
echo "  • API changes requiring doc updates: ${#API_DOC_UPDATE_NEEDED[@]}"
echo "  • Code changes requiring doc updates: ${#DOC_UPDATE_NEEDED[@]}"
echo "  • Manifest updates needed: ${#MANIFEST_UPDATE_NEEDED[@]}"
echo "  • Documentation files updated: $(echo "$DOC_FILES_UPDATED" | wc -l | tr -d ' ')"

# Create summary log entry
LOG_DIR=".claude/hooks/doc-check-logs"
mkdir -p "$LOG_DIR"
LOG_ENTRY="$LOG_DIR/$(date +%Y%m%d).log"

echo "$(date -Iseconds) | $COMMIT_SHORT | API:${#API_DOC_UPDATE_NEEDED[@]} | DOC:${#DOC_UPDATE_NEEDED[@]} | MANIFEST:${#MANIFEST_UPDATE_NEEDED[@]} | $COMMIT_MESSAGE" >> "$LOG_ENTRY"

log "✅ Post-commit documentation check completed" "$GREEN"

exit 0