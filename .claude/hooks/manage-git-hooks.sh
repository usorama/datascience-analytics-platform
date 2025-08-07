#!/bin/bash
# Git Hooks Management Script
# Usage: ./manage-git-hooks.sh [enable|disable|status|reinstall]

set -euo pipefail

PROJECT_DIR="$(git rev-parse --show-toplevel)"
cd "$PROJECT_DIR"

case "${1:-status}" in
    enable)
        .claude/hooks/install-git-hooks.sh
        echo "✅ Git hooks enabled"
        ;;
    disable)
        for hook in pre-commit post-commit pre-push post-merge; do
            if [[ -f ".git/hooks/$hook.backup" ]]; then
                mv ".git/hooks/$hook.backup" ".git/hooks/$hook"
                echo "🔄 Restored original $hook hook"
            else
                rm -f ".git/hooks/$hook"
                echo "🗑️  Removed $hook hook"
            fi
        done
        echo "❌ Git hooks disabled"
        ;;
    status)
        echo "📊 Git Hooks Status:"
        for hook in pre-commit post-commit pre-push post-merge; do
            if [[ -f ".git/hooks/$hook" ]]; then
                echo "  ✅ $hook: installed"
                if [[ -f ".git/hooks/$hook.backup" ]]; then
                    echo "     (backup available)"
                fi
            else
                echo "  ❌ $hook: not installed"
            fi
        done
        ;;
    reinstall)
        .claude/hooks/install-git-hooks.sh --force
        echo "🔄 Git hooks reinstalled"
        ;;
    *)
        echo "Usage: $0 [enable|disable|status|reinstall]"
        exit 1
        ;;
esac
