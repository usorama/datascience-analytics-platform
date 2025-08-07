#!/bin/bash
# Pre-Implementation Checkpoint Hook
# Creates named checkpoints before major code changes to enable easy rollback
# Usage: ./pre-implementation-checkpoint.sh [operation-name] [description]

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
OPERATION="${1:-manual}"
DESCRIPTION="${2:-Pre-implementation checkpoint}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CHECKPOINT_TAG="checkpoint-${OPERATION}-${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
    log "❌ Not a git repository. Checkpoints require git." "$RED"
    exit 1
fi

# Check for uncommitted changes
if [[ -n "$(git status --porcelain)" ]]; then
    log "⚠️  Uncommitted changes detected. Stashing before checkpoint..." "$YELLOW"
    
    # Create a descriptive stash
    stash_message="Pre-checkpoint stash for ${OPERATION} at ${TIMESTAMP}"
    git stash push -m "$stash_message" --include-untracked
    
    if [[ $? -eq 0 ]]; then
        log "✅ Changes stashed: $stash_message" "$GREEN"
        echo "$stash_message" > ".claude/hooks/.last-stash-${TIMESTAMP}"
    else
        log "❌ Failed to stash changes" "$RED"
        exit 1
    fi
fi

# Get current branch and commit
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse HEAD)
CURRENT_COMMIT_SHORT=$(git rev-parse --short HEAD)

# Create checkpoint tag with detailed information
CHECKPOINT_MESSAGE="Checkpoint: ${DESCRIPTION}

Operation: ${OPERATION}
Branch: ${CURRENT_BRANCH}
Commit: ${CURRENT_COMMIT_SHORT}
Created: $(date '+%Y-%m-%d %H:%M:%S')
Agent: ${AGENT_NAME:-manual}

This checkpoint enables rollback to state before ${OPERATION} implementation.
To rollback: git reset --hard ${CHECKPOINT_TAG}"

# Create the checkpoint tag
git tag -a "$CHECKPOINT_TAG" -m "$CHECKPOINT_MESSAGE"

if [[ $? -eq 0 ]]; then
    log "✅ Checkpoint created: $CHECKPOINT_TAG" "$GREEN"
    log "📍 Current state: $CURRENT_BRANCH @ $CURRENT_COMMIT_SHORT" "$BLUE"
    
    # Store checkpoint metadata
    CHECKPOINT_META="{
  \"tag\": \"$CHECKPOINT_TAG\",
  \"operation\": \"$OPERATION\",
  \"description\": \"$DESCRIPTION\",
  \"branch\": \"$CURRENT_BRANCH\",
  \"commit\": \"$CURRENT_COMMIT\",
  \"timestamp\": \"$(date -Iseconds)\",
  \"agent\": \"${AGENT_NAME:-manual}\"
}"
    
    echo "$CHECKPOINT_META" > ".claude/hooks/.checkpoint-${TIMESTAMP}.json"
    
    # Add to checkpoint history
    echo "$(date -Iseconds) | $CHECKPOINT_TAG | $OPERATION | $DESCRIPTION" >> ".claude/hooks/checkpoint-history.log"
    
    # Create rollback script
    ROLLBACK_SCRIPT=".claude/hooks/rollback-to-${CHECKPOINT_TAG}.sh"
    cat > "$ROLLBACK_SCRIPT" << EOF
#!/bin/bash
# Rollback script for checkpoint: $CHECKPOINT_TAG
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

set -euo pipefail

echo "🔄 Rolling back to checkpoint: $CHECKPOINT_TAG"
echo "⚠️  This will reset your working directory to the checkpoint state."
echo "   Current changes will be lost unless committed or stashed."
echo

read -p "Continue with rollback? (yes/no): " confirm
if [[ \$confirm != "yes" ]]; then
    echo "Rollback cancelled."
    exit 0
fi

# Check if checkpoint tag exists
if ! git tag | grep -q "^$CHECKPOINT_TAG\$"; then
    echo "❌ Checkpoint tag '$CHECKPOINT_TAG' not found."
    exit 1
fi

# Perform rollback
echo "🔄 Resetting to checkpoint..."
git reset --hard "$CHECKPOINT_TAG"

# Restore stashed changes if they exist
if [[ -f ".claude/hooks/.last-stash-${TIMESTAMP}" ]]; then
    stash_msg=\$(cat ".claude/hooks/.last-stash-${TIMESTAMP}")
    echo "🔄 Checking for stashed changes..."
    
    # Find the stash entry
    if git stash list | grep -q "\$stash_msg"; then
        echo "📦 Restoring stashed changes: \$stash_msg"
        git stash pop
        rm ".claude/hooks/.last-stash-${TIMESTAMP}"
    fi
fi

echo "✅ Rollback complete. Repository reset to checkpoint: $CHECKPOINT_TAG"
echo "📍 Current state: \$(git branch --show-current) @ \$(git rev-parse --short HEAD)"
EOF
    
    chmod +x "$ROLLBACK_SCRIPT"
    log "🔄 Rollback script created: $ROLLBACK_SCRIPT" "$BLUE"
    
else
    log "❌ Failed to create checkpoint tag" "$RED"
    exit 1
fi

# Show recent checkpoints
log "📋 Recent checkpoints:" "$BLUE"
git tag -l "checkpoint-*" --sort=-version:refname | head -5 | while read -r tag; do
    if [[ -n "$tag" ]]; then
        tag_date=$(git log -1 --format=%ai "$tag" 2>/dev/null || echo "unknown")
        echo "  • $tag ($tag_date)"
    fi
done

# Cleanup old checkpoint metadata (keep last 20)
find ".claude/hooks" -name ".checkpoint-*.json" -type f | sort -r | tail -n +21 | xargs rm -f 2>/dev/null || true

log "🎯 Ready for implementation of: $OPERATION" "$GREEN"
echo
echo "💡 To rollback later:"
echo "   git reset --hard $CHECKPOINT_TAG"
echo "   # or run: $ROLLBACK_SCRIPT"
echo

exit 0