#!/bin/bash
# Git Hooks Installation Script
# Installs checkpoint and documentation hooks into git hooks directory
# Usage: ./install-git-hooks.sh [--force]

set -euo pipefail

# Configuration
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
FORCE_INSTALL=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE_INSTALL=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--force]"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log "🔧 Installing git hooks for documentation and checkpoint management..." "$BLUE"

# Backup existing hooks
backup_hook() {
    local hook_name="$1"
    local hook_path=".git/hooks/$hook_name"
    
    if [[ -f "$hook_path" && "$FORCE_INSTALL" == "false" ]]; then
        if [[ ! -f "$hook_path.backup" ]]; then
            cp "$hook_path" "$hook_path.backup"
            log "📦 Backed up existing $hook_name hook" "$YELLOW"
        fi
    fi
}

# Install pre-commit hook enhancement
install_pre_commit_hook() {
    local hook_path=".git/hooks/pre-commit"
    backup_hook "pre-commit"
    
    cat > "$hook_path" << 'EOF'
#!/bin/bash
# Enhanced Pre-Commit Hook with Documentation Currency Check
# Combines existing pre-commit logic with documentation validation

set -euo pipefail

PROJECT_DIR="$(git rev-parse --show-toplevel)"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[PRE-COMMIT] $1${NC}"
}

# Run existing BMAD pre-commit check if it exists
if [[ -f ".bmad-core/hooks/pre-commit-completion-check.sh" ]]; then
    log "🔍 Running BMAD completion check..." "$YELLOW"
    .bmad-core/hooks/pre-commit-completion-check.sh
    bmad_result=$?
else
    bmad_result=0
fi

# Run existing backed up pre-commit hook if it exists
if [[ -f ".git/hooks/pre-commit.backup" ]]; then
    log "🔍 Running existing pre-commit checks..." "$YELLOW"
    .git/hooks/pre-commit.backup
    existing_result=$?
else
    existing_result=0
fi

# Run documentation currency check
if [[ -f ".claude/hooks/documentation-currency-check.sh" ]]; then
    log "📚 Running documentation currency check..." "$YELLOW"
    .claude/hooks/documentation-currency-check.sh
    doc_result=$?
    
    if [[ $doc_result -ne 0 ]]; then
        log "⚠️  Documentation issues found. Run with --fix to auto-repair:" "$YELLOW"
        echo "    .claude/hooks/documentation-currency-check.sh --fix"
        echo ""
        log "Or commit anyway with: git commit --no-verify" "$YELLOW"
    fi
else
    doc_result=0
fi

# Exit with failure if any check failed
if [[ $bmad_result -ne 0 || $existing_result -ne 0 || $doc_result -ne 0 ]]; then
    log "❌ Pre-commit checks failed" "$RED"
    exit 1
fi

log "✅ All pre-commit checks passed" "$GREEN"
exit 0
EOF
    
    chmod +x "$hook_path"
    log "✅ Enhanced pre-commit hook installed" "$GREEN"
}

# Install post-commit hook
install_post_commit_hook() {
    local hook_path=".git/hooks/post-commit"
    backup_hook "post-commit"
    
    cat > "$hook_path" << 'EOF'
#!/bin/bash
# Post-Commit Hook with Documentation Check
# Automatically checks for documentation updates needed after commits

set -euo pipefail

PROJECT_DIR="$(git rev-parse --show-toplevel)"
cd "$PROJECT_DIR"

# Run post-commit documentation check
if [[ -f ".claude/hooks/post-commit-doc-check.sh" ]]; then
    .claude/hooks/post-commit-doc-check.sh
fi

# Run existing post-commit logic if backed up version exists
if [[ -f ".git/hooks/post-commit.backup" ]]; then
    .git/hooks/post-commit.backup
fi

exit 0
EOF
    
    chmod +x "$hook_path"
    log "✅ Post-commit documentation check hook installed" "$GREEN"
}

# Install pre-push hook with checkpoint creation
install_pre_push_hook() {
    local hook_path=".git/hooks/pre-push"
    backup_hook "pre-push"
    
    cat > "$hook_path" << 'EOF'
#!/bin/bash
# Pre-Push Hook with Checkpoint Creation
# Creates checkpoint before pushing to remote

set -euo pipefail

PROJECT_DIR="$(git rev-parse --show-toplevel)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[PRE-PUSH] $1${NC}"
}

# Get push information
remote="$1"
url="$2"

# Create pre-push checkpoint
if [[ -f ".claude/hooks/pre-implementation-checkpoint.sh" ]]; then
    log "📍 Creating pre-push checkpoint..." "$YELLOW"
    .claude/hooks/pre-implementation-checkpoint.sh "push-to-$remote" "Pre-push checkpoint before pushing to $remote"
fi

# Run existing pre-push logic if backed up version exists
if [[ -f ".git/hooks/pre-push.backup" ]]; then
    .git/hooks/pre-push.backup "$@"
    existing_result=$?
else
    existing_result=0
fi

# Update manifests before push
if [[ -f ".claude/hooks/manifest-auto-updater.sh" ]]; then
    log "📋 Updating manifests before push..." "$YELLOW"
    .claude/hooks/manifest-auto-updater.sh
fi

log "✅ Pre-push checks completed" "$GREEN"
exit $existing_result
EOF
    
    chmod +x "$hook_path"
    log "✅ Pre-push checkpoint hook installed" "$GREEN"
}

# Install post-merge hook
install_post_merge_hook() {
    local hook_path=".git/hooks/post-merge"
    backup_hook "post-merge"
    
    cat > "$hook_path" << 'EOF'
#!/bin/bash
# Post-Merge Hook with Documentation Update
# Updates manifests and checks documentation after merges

set -euo pipefail

PROJECT_DIR="$(git rev-parse --show-toplevel)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[POST-MERGE] $1${NC}"
}

# Update manifests after merge
if [[ -f ".claude/hooks/manifest-auto-updater.sh" ]]; then
    log "📋 Updating manifests after merge..." "$YELLOW"
    .claude/hooks/manifest-auto-updater.sh --force
fi

# Run documentation currency check
if [[ -f ".claude/hooks/documentation-currency-check.sh" ]]; then
    log "📚 Checking documentation currency after merge..." "$YELLOW"
    .claude/hooks/documentation-currency-check.sh --verbose || true
fi

# Run existing post-merge logic if backed up version exists
if [[ -f ".git/hooks/post-merge.backup" ]]; then
    .git/hooks/post-merge.backup "$@"
fi

log "✅ Post-merge tasks completed" "$GREEN"
exit 0
EOF
    
    chmod +x "$hook_path"
    log "✅ Post-merge documentation hook installed" "$GREEN"
}

# Install all hooks
install_pre_commit_hook
install_post_commit_hook
install_pre_push_hook
install_post_merge_hook

# Create hook management script
cat > ".claude/hooks/manage-git-hooks.sh" << 'EOF'
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
EOF

chmod +x ".claude/hooks/manage-git-hooks.sh"
log "🛠️  Git hooks management script created" "$GREEN"

log "✅ Git hooks installation completed successfully!" "$GREEN"
echo
echo "📋 Installed hooks:"
echo "  • pre-commit: Documentation currency check + existing checks"
echo "  • post-commit: Automatic documentation update flagging"
echo "  • pre-push: Checkpoint creation + manifest updates"
echo "  • post-merge: Manifest updates + documentation checks"
echo
echo "🛠️  Management commands:"
echo "  • Check status: .claude/hooks/manage-git-hooks.sh status"
echo "  • Disable hooks: .claude/hooks/manage-git-hooks.sh disable"
echo "  • Re-enable hooks: .claude/hooks/manage-git-hooks.sh enable"
echo
echo "💡 To bypass hooks temporarily: git commit --no-verify"

exit 0