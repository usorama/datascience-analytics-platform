#!/bin/bash
# Rollback script for checkpoint: checkpoint-test-run-20250805-165605
# Generated: 2025-08-05 16:56:07

set -euo pipefail

echo "🔄 Rolling back to checkpoint: checkpoint-test-run-20250805-165605"
echo "⚠️  This will reset your working directory to the checkpoint state."
echo "   Current changes will be lost unless committed or stashed."
echo

read -p "Continue with rollback? (yes/no): " confirm
if [[ $confirm != "yes" ]]; then
    echo "Rollback cancelled."
    exit 0
fi

# Check if checkpoint tag exists
if ! git tag | grep -q "^checkpoint-test-run-20250805-165605$"; then
    echo "❌ Checkpoint tag 'checkpoint-test-run-20250805-165605' not found."
    exit 1
fi

# Perform rollback
echo "🔄 Resetting to checkpoint..."
git reset --hard "checkpoint-test-run-20250805-165605"

# Restore stashed changes if they exist
if [[ -f ".claude/hooks/.last-stash-20250805-165605" ]]; then
    stash_msg=$(cat ".claude/hooks/.last-stash-20250805-165605")
    echo "🔄 Checking for stashed changes..."
    
    # Find the stash entry
    if git stash list | grep -q "$stash_msg"; then
        echo "📦 Restoring stashed changes: $stash_msg"
        git stash pop
        rm ".claude/hooks/.last-stash-20250805-165605"
    fi
fi

echo "✅ Rollback complete. Repository reset to checkpoint: checkpoint-test-run-20250805-165605"
echo "📍 Current state: $(git branch --show-current) @ $(git rev-parse --short HEAD)"
