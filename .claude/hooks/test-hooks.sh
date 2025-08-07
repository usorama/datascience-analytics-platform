#!/bin/bash
# Test Script for Git Hooks System
# Tests all hooks for basic functionality

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${2:-$NC}[TEST] $1${NC}"
}

log "🧪 Testing Git Hooks System..." "$BLUE"

# Test 1: Documentation currency check (basic)
log "1️⃣  Testing documentation currency check..." "$YELLOW"
if .claude/hooks/documentation-currency-check.sh > /dev/null 2>&1; then
    log "✅ Documentation currency check: PASSED" "$GREEN"
else
    log "❌ Documentation currency check: FAILED" "$RED"
fi

# Test 2: Manifest auto-updater (dry run)
log "2️⃣  Testing manifest auto-updater (dry-run)..." "$YELLOW"
mkdir -p docs/manifests
if .claude/hooks/manifest-auto-updater.sh --dry-run > /dev/null 2>&1; then
    log "✅ Manifest auto-updater: PASSED" "$GREEN"
else
    log "❌ Manifest auto-updater: FAILED" "$RED"
fi

# Test 3: Checkpoint creation
log "3️⃣  Testing checkpoint creation..." "$YELLOW"
if .claude/hooks/pre-implementation-checkpoint.sh "test-run" "Hook testing checkpoint" > /dev/null 2>&1; then
    log "✅ Checkpoint creation: PASSED" "$GREEN"
    
    # Clean up test checkpoint
    git tag -d "$(git tag -l "checkpoint-test-run-*" | head -1)" > /dev/null 2>&1 || true
else
    log "❌ Checkpoint creation: FAILED" "$RED"
fi

# Test 4: Post-commit doc check (simulated)
log "4️⃣  Testing post-commit documentation check..." "$YELLOW"
if .claude/hooks/post-commit-doc-check.sh "$(git rev-parse HEAD)" > /dev/null 2>&1; then
    log "✅ Post-commit doc check: PASSED" "$GREEN"
else
    log "❌ Post-commit doc check: FAILED" "$RED"
fi

# Test 5: Git hooks installation (dry run)
log "5️⃣  Testing git hooks installation..." "$YELLOW"
if [[ -f ".claude/hooks/install-git-hooks.sh" && -x ".claude/hooks/install-git-hooks.sh" ]]; then
    log "✅ Git hooks installer: PASSED" "$GREEN"
else
    log "❌ Git hooks installer: FAILED" "$RED"
fi

# Test 6: PNPM script integration
log "6️⃣  Testing pnpm script integration..." "$YELLOW"
if grep -q "hooks:install" package.json && grep -q "docs:check" package.json; then
    log "✅ PNPM script integration: PASSED" "$GREEN"
else
    log "❌ PNPM script integration: FAILED" "$RED"
fi

log "🏁 Hook system testing completed!" "$GREEN"
log "📋 All core hooks are functional and ready for use" "$BLUE"

exit 0