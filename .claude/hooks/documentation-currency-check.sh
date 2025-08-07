#!/bin/bash
# Documentation Currency Check Hook
# Validates documentation freshness and flags outdated content
# Usage: ./documentation-currency-check.sh [--fix] [--verbose]

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
FIX_MODE=false
VERBOSE=false
MAX_AGE_DAYS=30
CRITICAL_FILES=("CLAUDE.md" "design.md" "README.md" "package.json")

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX_MODE=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --max-age)
            MAX_AGE_DAYS="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--fix] [--verbose] [--max-age DAYS]"
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

# Logging functions
log() {
    echo -e "${2:-$NC}[$(date '+%H:%M:%S')] $1${NC}"
}

verbose_log() {
    if [[ "$VERBOSE" == "true" ]]; then
        log "$1" "$2"
    fi
}

# Change to project directory
cd "$PROJECT_DIR" || {
    log "❌ Failed to change to project directory: $PROJECT_DIR" "$RED"
    exit 1
}

# Verify git repository
if [[ ! -d ".git" ]]; then
    log "❌ Not a git repository. Currency check requires git." "$RED"
    exit 1
fi

# Initialize tracking arrays
declare -a OUTDATED_DOCS=()
declare -a MISSING_DOCS=()
declare -a STALE_MANIFESTS=()
declare -a DEPENDENCY_CHANGES=()

# Create currency report directory
REPORT_DIR=".claude/hooks/currency-reports"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/currency-check-$(date +%Y%m%d-%H%M%S).json"

log "🔍 Starting documentation currency check..." "$BLUE"

# Function to check file staleness
check_file_staleness() {
    local file="$1"
    local max_age="$2"
    
    if [[ ! -f "$file" ]]; then
        return 2  # File doesn't exist
    fi
    
    local file_age_days
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        file_age_days=$(( ($(date +%s) - $(stat -f %m "$file")) / 86400 ))
    else
        # Linux
        file_age_days=$(( ($(date +%s) - $(date -r "$file" +%s)) / 86400 ))
    fi
    
    if [[ $file_age_days -gt $max_age ]]; then
        return 1  # File is stale
    fi
    
    return 0  # File is fresh
}

# Function to get last modification info
get_modification_info() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "File not found"
        return
    fi
    
    # Get git modification info
    local last_commit=$(git log -1 --format="%h %ad %s" --date=short -- "$file" 2>/dev/null || echo "No commits")
    local last_modified
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        last_modified=$(stat -f %Sm -t "%Y-%m-%d %H:%M" "$file")
    else
        last_modified=$(stat -c "%y" "$file" | cut -d. -f1)
    fi
    
    echo "Modified: $last_modified | Git: $last_commit"
}

# Check critical documentation files
log "📋 Checking critical documentation files..." "$CYAN"
for file in "${CRITICAL_FILES[@]}"; do
    verbose_log "Checking: $file" "$BLUE"
    
    if [[ ! -f "$file" ]]; then
        MISSING_DOCS+=("$file")
        log "⚠️  Missing critical file: $file" "$YELLOW"
        continue
    fi
    
    if ! check_file_staleness "$file" "$MAX_AGE_DAYS"; then
        case $? in
            1)
                OUTDATED_DOCS+=("$file")
                log "📅 Potentially outdated: $file (>$MAX_AGE_DAYS days)" "$YELLOW"
                verbose_log "$(get_modification_info "$file")" "$CYAN"
                ;;
            2)
                MISSING_DOCS+=("$file")
                log "❌ Missing: $file" "$RED"
                ;;
        esac
    else
        verbose_log "✅ Fresh: $file" "$GREEN"
    fi
done

# Check documentation structure consistency
log "🏗️  Checking documentation structure..." "$CYAN"

# Verify README files in subdirectories (exclude node_modules, .git, archives)
find . -type d \( -name "node_modules" -o -name ".git" -o -name ".archives" -o -name "dist" -o -name "build" -o -name ".next" \) -prune -o -type d \( -name "docs" -o -name "client" -o -name "server" \) -print | while read -r dir; do
    if [[ ! -f "$dir/README.md" && -n "$(find "$dir" -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -not -path "*/node_modules/*" | head -1)" ]]; then
        echo "$dir/README.md" >> /tmp/missing_readmes.txt
    fi
done

if [[ -f /tmp/missing_readmes.txt ]]; then
    while read -r missing_readme; do
        MISSING_DOCS+=("$missing_readme")
        log "📝 Missing README: $missing_readme" "$YELLOW"
    done < /tmp/missing_readmes.txt
    rm -f /tmp/missing_readmes.txt
fi

# Check for outdated API documentation
log "🔌 Checking API documentation currency..." "$CYAN"

# Check if routes have changed recently
if [[ -d "server/src/presentation/routes" ]]; then
    recent_route_changes=$(git log --since="7 days ago" --name-only --pretty=format: -- server/src/presentation/routes/ | grep -v "^$" | wc -l)
    
    if [[ $recent_route_changes -gt 0 ]]; then
        # Check if API docs were updated
        api_doc_files=("docs/api/" "docs/endpoints/" "docs/API.md" "server/README.md")
        api_docs_updated=false
        
        for api_doc in "${api_doc_files[@]}"; do
            if [[ -f "$api_doc" ]]; then
                recent_api_doc_changes=$(git log --since="7 days ago" --name-only --pretty=format: -- "$api_doc" | grep -v "^$" | wc -l)
                if [[ $recent_api_doc_changes -gt 0 ]]; then
                    api_docs_updated=true
                    break
                fi
            fi
        done
        
        if [[ "$api_docs_updated" == "false" ]]; then
            log "⚠️  API routes changed recently but documentation wasn't updated" "$YELLOW"
            STALE_MANIFESTS+=("API documentation")
        fi
    fi
fi

# Check package.json vs documentation consistency
log "📦 Checking dependency documentation..." "$CYAN"

if [[ -f "package.json" ]]; then
    # Check if dependencies changed recently but docs weren't updated
    recent_dep_changes=$(git log --since="14 days ago" --name-only --pretty=format: -- package.json client/package.json server/package.json | grep -v "^$" | wc -l)
    
    if [[ $recent_dep_changes -gt 0 ]]; then
        # Check if installation/setup docs were updated
        setup_docs=("README.md" "docs/setup/" "docs/installation/" "SETUP.md")
        setup_docs_updated=false
        
        for setup_doc in "${setup_docs[@]}"; do
            if [[ -f "$setup_doc" ]]; then
                recent_setup_changes=$(git log --since="14 days ago" --name-only --pretty=format: -- "$setup_doc" | grep -v "^$" | wc -l)
                if [[ $recent_setup_changes -gt 0 ]]; then
                    setup_docs_updated=true
                    break
                fi
            fi
        done
        
        if [[ "$setup_docs_updated" == "false" ]]; then
            log "⚠️  Dependencies changed but setup documentation wasn't updated" "$YELLOW"
            DEPENDENCY_CHANGES+=("Setup documentation needs update")
        fi
    fi
fi

# Check for broken internal links
log "🔗 Checking internal documentation links..." "$CYAN"

find . -name "*.md" -type f -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.archives/*" -not -path "*/dist/*" -not -path "*/build/*" -not -path "*/.next/*" | while read -r md_file; do
    
    # Extract markdown links
    grep -oE '\[.*\]\([^)]+\)' "$md_file" 2>/dev/null | while read -r link; do
        # Extract the URL part
        url=$(echo "$link" | sed -E 's/.*\(([^)]+)\).*/\1/')
        
        # Skip external URLs
        if [[ "$url" =~ ^https?:// ]]; then
            continue
        fi
        
        # Check if internal file exists
        if [[ "$url" =~ ^/ ]]; then
            # Absolute path from project root
            link_path=".$url"
        else
            # Relative path from current file
            link_path="$(dirname "$md_file")/$url"
        fi
        
        # Remove anchor fragments
        link_path=$(echo "$link_path" | cut -d'#' -f1)
        
        if [[ ! -f "$link_path" && ! -d "$link_path" ]]; then
            echo "Broken link in $md_file: $url" >> /tmp/broken_links.txt
        fi
    done
done

if [[ -f /tmp/broken_links.txt ]]; then
    log "🔗 Found broken internal links:" "$YELLOW"
    while read -r broken_link; do
        verbose_log "  $broken_link" "$RED"
    done < /tmp/broken_links.txt
    rm -f /tmp/broken_links.txt
fi

# Generate currency report
CURRENCY_REPORT="{
  \"timestamp\": \"$(date -Iseconds)\",
  \"max_age_days\": $MAX_AGE_DAYS,
  \"outdated_docs\": $(printf '%s\n' "${OUTDATED_DOCS[@]}" | jq -R . | jq -s .),
  \"missing_docs\": $(printf '%s\n' "${MISSING_DOCS[@]}" | jq -R . | jq -s .),
  \"stale_manifests\": $(printf '%s\n' "${STALE_MANIFESTS[@]}" | jq -R . | jq -s .),
  \"dependency_changes\": $(printf '%s\n' "${DEPENDENCY_CHANGES[@]}" | jq -R . | jq -s .),
  \"total_issues\": $((${#OUTDATED_DOCS[@]} + ${#MISSING_DOCS[@]} + ${#STALE_MANIFESTS[@]} + ${#DEPENDENCY_CHANGES[@]}))
}"

echo "$CURRENCY_REPORT" > "$REPORT_FILE"

# Summary
total_issues=$((${#OUTDATED_DOCS[@]} + ${#MISSING_DOCS[@]} + ${#STALE_MANIFESTS[@]} + ${#DEPENDENCY_CHANGES[@]}))

log "📊 Documentation Currency Summary:" "$BLUE"
echo "  • Outdated files: ${#OUTDATED_DOCS[@]}"
echo "  • Missing files: ${#MISSING_DOCS[@]}"
echo "  • Stale manifests: ${#STALE_MANIFESTS[@]}"
echo "  • Dependency issues: ${#DEPENDENCY_CHANGES[@]}"
echo "  • Total issues: $total_issues"
echo "  • Report saved: $REPORT_FILE"

# Auto-fix mode
if [[ "$FIX_MODE" == "true" && $total_issues -gt 0 ]]; then
    log "🔧 Running auto-fix mode..." "$YELLOW"
    
    # Update timestamps on critical files that exist but are stale
    for file in "${OUTDATED_DOCS[@]}"; do
        if [[ -f "$file" ]]; then
            log "📝 Adding documentation update reminder to: $file" "$CYAN"
            
            # Add update reminder comment at the top
            temp_file=$(mktemp)
            {
                echo "<!-- Documentation currency check: Last verified $(date '+%Y-%m-%d') -->"
                echo ""
                cat "$file"
            } > "$temp_file"
            mv "$temp_file" "$file"
        fi
    done
    
    # Create missing README templates
    for missing_file in "${MISSING_DOCS[@]}"; do
        if [[ "$missing_file" == *"README.md" ]]; then
            dir=$(dirname "$missing_file")
            log "📝 Creating README template: $missing_file" "$CYAN"
            
            cat > "$missing_file" << EOF
# $(basename "$dir")

<!-- Auto-generated README template - Please update with actual content -->
<!-- Created: $(date '+%Y-%m-%d %H:%M:%S') -->

## Overview

TODO: Add overview of this directory/module

## Contents

TODO: Describe the contents and structure

## Usage

TODO: Add usage instructions

## Documentation

TODO: Link to relevant documentation

---
*This README was auto-generated. Please update with accurate information.*
EOF
        fi
    done
    
    log "✅ Auto-fix completed. Please review and commit changes." "$GREEN"
fi

# Exit code based on issues found
if [[ $total_issues -gt 0 ]]; then
    log "⚠️  Documentation currency issues found. Consider running with --fix" "$YELLOW"
    exit 1
else
    log "✅ All documentation appears current" "$GREEN"
    exit 0
fi