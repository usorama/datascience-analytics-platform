#!/bin/bash
# Post-tool-use hook for automatic checkpoint creation
# Triggers after Write, MultiEdit, or other significant operations

# Hook configuration from Claude Code
TOOL_NAME="${TOOL_NAME:-unknown}"
AGENT_NAME="${AGENT_NAME:-unknown}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Check if this is a git repository
if [[ ! -d ".git" ]]; then
    echo "Not a git repository, skipping checkpoint"
    exit 0
fi

# Tools that trigger checkpoint creation
CHECKPOINT_TOOLS=("Write" "MultiEdit" "NotebookEdit")

# Check if current tool should trigger checkpoint
should_checkpoint=false
for tool in "${CHECKPOINT_TOOLS[@]}"; do
    if [[ "$TOOL_NAME" == "$tool" ]]; then
        should_checkpoint=true
        break
    fi
done

if [[ "$should_checkpoint" == "true" ]]; then
    # Check if there are changes to commit
    if [[ -n "$(git status --porcelain)" ]]; then
        
        # Create meaningful commit message
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        commit_message="🔄 Auto-checkpoint: ${TOOL_NAME} by ${AGENT_NAME} at ${timestamp}"
        
        # Add all changes and commit
        git add -A
        git commit -m "$commit_message" --quiet
        
        # Create tag for significant operations
        if [[ "$AGENT_NAME" != "unknown" && "$AGENT_NAME" != "" ]]; then
            tag_name="checkpoint-$(date +%Y%m%d-%H%M%S)"
            git tag -a "$tag_name" -m "Agent checkpoint: $AGENT_NAME" --quiet
        fi
        
        current_commit=$(git rev-parse --short HEAD)
        echo "✅ Checkpoint created: $current_commit - $TOOL_NAME by $AGENT_NAME"
    else
        echo "No changes detected, skipping checkpoint"
    fi
else
    echo "Tool $TOOL_NAME does not require checkpoint"
fi

exit 0