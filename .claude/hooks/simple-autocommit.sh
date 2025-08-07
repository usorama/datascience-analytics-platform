#!/bin/bash
# simple-autocommit.sh - Simplified auto-commit script

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
CONFIG_FILE="${PROJECT_DIR}/.claude/config/autocommit-config.json"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Check if git repository
if [[ ! -d ".git" ]]; then
    echo "Not a git repository, skipping auto-commit"
    exit 0
fi

# Check for changes
if [[ -z "$(git status --porcelain)" ]]; then
    echo "No changes detected, skipping auto-commit"
    exit 0
fi

# Load configuration
ENABLED=true
if [[ -f "$CONFIG_FILE" ]]; then
    # Try to find available Python version
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Python not found, assuming enabled=true"
        ENABLED=true
    fi
    
    if [[ -n "${PYTHON_CMD:-}" ]]; then
        ENABLED=$($PYTHON_CMD -c "import json; print(json.load(open('$CONFIG_FILE')).get('enabled', True))" 2>/dev/null || echo "true")
    fi
fi

if [[ "$ENABLED" != "True" ]]; then
    echo "Auto-commit disabled"
    exit 0
fi

# Generate commit message
TASK_TYPE="${1:-Task}"
TASK_DESC="${2:-Development progress}"
COMMIT_MSG="✅ $TASK_TYPE Complete: $TASK_DESC"

# Add Claude signature
COMMIT_MSG="$COMMIT_MSG

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Create backup branch
BACKUP_BRANCH="autocommit-backup-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP_BRANCH" 2>/dev/null || true

# Stage and commit (skip hooks for auto-commits)
git add -A
git commit -m "$COMMIT_MSG" --no-verify

# Create tag
TAG_NAME="completion-$(date +%Y%m%d-%H%M%S)"
git tag -a "$TAG_NAME" -m "Task completion: $TASK_TYPE" 2>/dev/null || true

echo "✅ Auto-commit created: $(git rev-parse --short HEAD)"
echo "📍 Backup branch: $BACKUP_BRANCH"
echo "🏷️  Tag: $TAG_NAME"

exit 0