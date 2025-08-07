#!/bin/bash
# Hook System Health Check Script
# Verifies all hooks are properly configured and working

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
HOOKS_DIR="$PROJECT_DIR/.claude/hooks"
CONFIG_DIR="$PROJECT_DIR/.claude/config"
LOGS_DIR="$PROJECT_DIR/.claude/logs"

echo "======================================"
echo "  Claude Hook System Health Check"
echo "  Date: $(date)"
echo "======================================"
echo ""

# Check Python availability
echo "1. Python Environment Check:"
if command -v python3.12 &> /dev/null; then
    echo "   ✅ Python 3.12 found: $(which python3.12)"
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    echo "   ⚠️  Python 3.12 not found, using Python 3: $(which python3)"
    PYTHON_CMD="python3"
else
    echo "   ❌ Python not found! Hooks will not work."
    exit 1
fi

# Check hook files exist
echo ""
echo "2. Hook Files Check:"
if [[ -f "$HOOKS_DIR/task-completion-detector.py" ]]; then
    echo "   ✅ task-completion-detector.py exists"
else
    echo "   ❌ task-completion-detector.py missing!"
fi

if [[ -f "$HOOKS_DIR/simple-autocommit.sh" ]]; then
    echo "   ✅ simple-autocommit.sh exists"
else
    echo "   ❌ simple-autocommit.sh missing!"
fi

# Check hook configuration
echo ""
echo "3. Hook Configuration:"
if [[ -f "$CONFIG_DIR/autocommit-config.json" ]]; then
    ENABLED=$($PYTHON_CMD -c "import json; print(json.load(open('$CONFIG_DIR/autocommit-config.json')).get('enabled', True))" 2>/dev/null || echo "unknown")
    echo "   ✅ Configuration file exists"
    echo "   📋 Auto-commit enabled: $ENABLED"
else
    echo "   ⚠️  Configuration file missing (using defaults)"
fi

# Check completion history
echo ""
echo "4. Completion History:"
if [[ -f "$CONFIG_DIR/completion_history.json" ]]; then
    COUNT=$($PYTHON_CMD -c "import json; print(len(json.load(open('$CONFIG_DIR/completion_history.json'))))" 2>/dev/null || echo "0")
    echo "   📊 Tracked completions: $COUNT"
else
    echo "   📊 No completion history (fresh start)"
fi

# Check logs
echo ""
echo "5. Recent Hook Activity:"
if [[ -f "$LOGS_DIR/task_completion.log" ]]; then
    echo "   📝 Last 5 log entries:"
    tail -5 "$LOGS_DIR/task_completion.log" | sed 's/^/      /'
else
    echo "   📝 No logs yet"
fi

# Test hook execution
echo ""
echo "6. Hook Execution Test:"
echo "   Running test detection..."
OUTPUT=$($PYTHON_CMD "$HOOKS_DIR/task-completion-detector.py" --test 2>&1 || true)
if [[ $? -eq 0 ]]; then
    echo "   ✅ Hook execution successful"
    echo "$OUTPUT" | grep -E "Detected events:|Completion type:" | sed 's/^/      /'
else
    echo "   ❌ Hook execution failed!"
    echo "$OUTPUT" | head -5 | sed 's/^/      /'
fi

# Check git status
echo ""
echo "7. Git Repository Status:"
if [[ -d ".git" ]]; then
    echo "   ✅ Git repository detected"
    CHANGES=$(git status --porcelain | wc -l | tr -d ' ')
    echo "   📊 Uncommitted changes: $CHANGES files"
else
    echo "   ❌ Not a git repository!"
fi

echo ""
echo "======================================"
echo "  Health Check Complete"
echo "======================================"