#!/bin/bash
# Pre-tool-use hook for safety checks and MCP integration validation
# Triggers before Write, MultiEdit, or other potentially risky operations

# Hook configuration from Claude Code  
TOOL_NAME="${TOOL_NAME:-unknown}"
AGENT_NAME="${AGENT_NAME:-unknown}"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Tools that require safety checks
RISKY_TOOLS=("Write" "MultiEdit" "Bash" "NotebookEdit")

# Check if current tool requires safety checks
needs_safety_check=false
for tool in "${RISKY_TOOLS[@]}"; do
    if [[ "$TOOL_NAME" == "$tool" ]]; then
        needs_safety_check=true
        break
    fi
done

if [[ "$needs_safety_check" == "true" ]]; then
    
    # 1. Check if git repository exists
    if [[ -d ".git" ]]; then
        # Create pre-operation checkpoint if there are uncommitted changes
        if [[ -n "$(git status --porcelain)" ]]; then
            timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            pre_commit_message="🛡️ Pre-operation checkpoint: Before ${TOOL_NAME} by ${AGENT_NAME} at ${timestamp}"
            
            git add -A
            git commit -m "$pre_commit_message" --quiet
            
            current_commit=$(git rev-parse --short HEAD)
            echo "🛡️ Pre-operation checkpoint created: $current_commit"
        fi
    else
        echo "⚠️ Warning: Not a git repository. Consider initializing git for safety."
    fi
    
    # 2. Check for Context7 MCP availability (for technical agents)
    TECHNICAL_AGENTS=("frontend-developer" "backend-architect" "ai-engineer" "mobile-app-builder")
    is_technical_agent=false
    
    for agent in "${TECHNICAL_AGENTS[@]}"; do
        if [[ "$AGENT_NAME" == "$agent" ]]; then
            is_technical_agent=true
            break
        fi
    done
    
    if [[ "$is_technical_agent" == "true" ]]; then
        # Check if Context7 is available (simplified check)
        if command -v claude >/dev/null 2>&1; then
            # Validate MCP servers are accessible
            echo "📚 MCP Check: Context7 integration available for $AGENT_NAME"
            echo "💡 Reminder: Use 'use context7' in prompts for current documentation"
        else
            echo "⚠️ Warning: MCP servers may not be available. Ensure Context7 is configured."
        fi
    fi
    
    # 3. Check for dangerous operations
    if [[ "$TOOL_NAME" == "Bash" ]]; then
        echo "⚠️ Bash execution detected. Ensure commands are safe and non-destructive."
        
        # Check for common dangerous patterns (basic safety)
        if [[ "$*" =~ rm[[:space:]]+-rf|sudo[[:space:]]+rm|>>[[:space:]]/dev|dd[[:space:]]+if ]]; then
            echo "🚨 DANGER: Potentially destructive command detected!"
            echo "Command: $*"
            echo "Consider creating a checkpoint before proceeding."
            # Don't block, but warn strongly
        fi
    fi
    
    # 4. Check disk space for large operations
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [[ "$available_space" -lt 1048576 ]]; then  # Less than 1GB
        echo "⚠️ Warning: Low disk space ($(echo $available_space | awk '{print $1/1024/1024 "GB"}'))"
        echo "Consider cleaning up before large operations."
    fi
    
    # 5. Validate project context
    if [[ -f "package.json" ]]; then
        echo "📦 Node.js project detected"
    elif [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
        echo "🐍 Python project detected"  
    elif [[ -f "Cargo.toml" ]]; then
        echo "🦀 Rust project detected"
    elif [[ -f "go.mod" ]]; then
        echo "🐹 Go project detected"
    fi
    
    echo "✅ Pre-operation safety check completed for $TOOL_NAME"
    
else
    echo "No safety check required for $TOOL_NAME"
fi

# Always allow operation to proceed (return 0)
exit 0