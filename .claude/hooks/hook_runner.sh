#!/bin/bash
# Universal Hook Runner - Automatically finds project root and executes hooks
# Usage: hook_runner.sh <hook_script> [arguments...]

set -euo pipefail

HOOK_SCRIPT="$1"
shift # Remove first argument, leaving the rest as hook arguments

# Function to find project root by looking for common project markers
find_project_root() {
    local current_dir="$PWD"

    # Start from current directory and walk up the tree
    while [[ "$current_dir" != "/" ]]; do
        # Check for common project markers
        if [[ -f "$current_dir/.claude/settings.json" ]] || \
           [[ -f "$current_dir/package.json" ]] || \
           [[ -f "$current_dir/.git/config" ]] || \
           [[ -f "$current_dir/requirements.txt" ]] || \
           [[ -f "$current_dir/Cargo.toml" ]] || \
           [[ -f "$current_dir/go.mod" ]]; then
            echo "$current_dir"
            return 0
        fi
        current_dir=$(dirname "$current_dir")
    done

    # Fallback: return current directory if no project root found
    echo "$PWD"
    return 1
}

# Find the project root
PROJECT_ROOT=$(find_project_root)

# Change to project root and execute the hook
cd "$PROJECT_ROOT"

# Execute the hook script with the provided arguments
if [[ -f ".claude/hooks/$HOOK_SCRIPT" ]]; then
    python3 ".claude/hooks/$HOOK_SCRIPT" "$@"
else
    echo "Error: Hook script .claude/hooks/$HOOK_SCRIPT not found in $PROJECT_ROOT" >&2
    exit 1
fi
