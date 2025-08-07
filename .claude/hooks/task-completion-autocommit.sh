#!/bin/bash
# task-completion-autocommit.sh - Automated git commits on task completion
# Triggers when BMAD validation confirms story/task completion

set -euo pipefail

# Configuration
CLAUDE_DIR="$(dirname "$(dirname "$0)")"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
LOG_DIR="$CLAUDE_DIR/logs/autocommit"
CONFIG_FILE="$CLAUDE_DIR/config/autocommit-config.json"

# Create required directories
mkdir -p "$LOG_DIR"

# Default configuration
DEFAULT_CONFIG='{
  "enabled": true,
  "auto_push": false,
  "commit_message_template": "✅ Task Complete: {task_description}",
  "tag_completions": true,
  "require_dod_validation": true,
  "require_evidence_validation": true,
  "safety_backup": true
}'

# Initialize config if not exists
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "$DEFAULT_CONFIG" > "$CONFIG_FILE"
fi

# Load configuration
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        cat "$CONFIG_FILE" | python3 -c "import sys, json; config=json.load(sys.stdin); print(json.dumps(config))"
    else
        echo "$DEFAULT_CONFIG"
    fi
}

log_message() {
    local level="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] task-completion-autocommit: $message" | tee -a "$LOG_DIR/autocommit.log"
}

# Change to project directory
cd "$PROJECT_DIR" || {
    log_message "ERROR" "Cannot change to project directory: $PROJECT_DIR"
    exit 1
}

# Check if git repository
if [[ ! -d ".git" ]]; then
    log_message "INFO" "Not a git repository, skipping auto-commit"
    exit 0
fi

# Load configuration
CONFIG=$(load_config)
ENABLED=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('enabled', True))")

if [[ "$ENABLED" != "True" ]]; then
    log_message "INFO" "Auto-commit disabled in configuration"
    exit 0
fi

# Function to detect task completion
detect_task_completion() {
    local completion_indicators=()
    
    # Check for DoD completion validation
    if [[ -f "$LOG_DIR/../quality/dod_validation.log" ]]; then
        if tail -10 "$LOG_DIR/../quality/dod_validation.log" | grep -q "DoD validation PASSED"; then
            completion_indicators+=("dod_validated")
        fi
    fi
    
    # Check for evidence validation
    if [[ -f "$LOG_DIR/../quality/evidence_validation.log" ]]; then
        if tail -10 "$LOG_DIR/../quality/evidence_validation.log" | grep -q "Evidence validation PASSED"; then
            completion_indicators+=("evidence_validated")
        fi
    fi
    
    # Check for story completion markers in recent files
    if find . -name "*.md" -mtime -1 -exec grep -l "Story.*Complete\|✅.*Complete\|COMPLETED" {} \; | head -1 > /dev/null; then
        completion_indicators+=("story_marked_complete")
    fi
    
    # Check for significant commit activity (multiple files changed)
    local changed_files=$(git status --porcelain | wc -l)
    if [[ $changed_files -gt 5 ]]; then
        completion_indicators+=("significant_changes")
    fi
    
    echo "${completion_indicators[@]}"
}

# Function to generate commit message
generate_commit_message() {
    local task_type="$1"
    local task_description="$2"
    local completion_indicators="$3"
    
    local template=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('commit_message_template', '✅ Task Complete: {task_description}'))")
    
    # Extract task description from recent activity
    if [[ -z "$task_description" ]]; then
        # Try to extract from recent commit messages or file changes
        task_description=$(git log --oneline -5 | grep -E "feat|fix|docs|style|refactor|test" | head -1 | cut -d' ' -f2- || echo "Development milestone")
    fi
    
    # Generate contextual commit message
    local commit_msg="✅ ${task_type}: ${task_description}"
    
    # Add validation context
    if [[ "$completion_indicators" =~ "dod_validated" ]]; then
        commit_msg="$commit_msg - DoD Validated"
    fi
    
    if [[ "$completion_indicators" =~ "evidence_validated" ]]; then
        commit_msg="$commit_msg - Evidence Confirmed"
    fi
    
    # Add Claude Code signature
    commit_msg=$(printf "%s\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>" "$commit_msg")
    
    echo "$commit_msg"
}

# Function to create safety backup
create_safety_backup() {
    local backup_branch="autocommit-backup-$(date +%Y%m%d-%H%M%S)"
    git branch "$backup_branch" 2>/dev/null || true
    log_message "INFO" "Safety backup created: $backup_branch"
}

# Function to perform auto-commit
perform_auto_commit() {
    local task_type="$1"
    local task_description="$2"
    local completion_indicators="$3"
    
    # Check if there are changes to commit
    if [[ -z "$(git status --porcelain)" ]]; then
        log_message "INFO" "No changes detected, skipping auto-commit"
        return 0
    fi
    
    # Create safety backup if enabled
    local safety_backup=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('safety_backup', True))")
    if [[ "$safety_backup" == "True" ]]; then
        create_safety_backup
    fi
    
    # Generate commit message
    local commit_message=$(generate_commit_message "$task_type" "$task_description" "$completion_indicators")
    
    # Stage all changes
    git add -A
    
    # Create commit with message
    git commit -m "$commit_message"
    
    local commit_hash=$(git rev-parse --short HEAD)
    log_message "SUCCESS" "Auto-commit created: $commit_hash"
    
    # Create tag if enabled
    local tag_completions=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tag_completions', True))")
    if [[ "$tag_completions" == "True" ]]; then
        local tag_name="completion-$(date +%Y%m%d-%H%M%S)"
        git tag -a "$tag_name" -m "Task completion: $task_type" 2>/dev/null || true
        log_message "INFO" "Completion tag created: $tag_name"
    fi
    
    # Auto-push if enabled
    local auto_push=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('auto_push', False))")
    if [[ "$auto_push" == "True" ]] && git remote get-url origin >/dev/null 2>&1; then
        git push origin "$(git branch --show-current)" 2>/dev/null || {
            log_message "WARNING" "Auto-push failed, commit remains local"
        }
        git push --tags 2>/dev/null || true
    fi
    
    return 0
}

# Main execution logic
main() {
    local task_type="${1:-Task}"
    local task_description="${2:-Development milestone}"
    
    log_message "INFO" "Starting task completion auto-commit check"
    
    # Detect task completion indicators
    local completion_indicators
    completion_indicators=$(detect_task_completion)
    
    if [[ -n "$completion_indicators" ]]; then
        log_message "INFO" "Task completion detected: $completion_indicators"
        
        # Verify requirements if enabled
        local require_dod=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('require_dod_validation', True))")
        local require_evidence=$(echo "$CONFIG" | python3 -c "import sys, json; print(json.load(sys.stdin).get('require_evidence_validation', True))")
        
        local validation_passed=true
        
        if [[ "$require_dod" == "True" ]] && [[ ! "$completion_indicators" =~ "dod_validated" ]]; then
            log_message "WARNING" "DoD validation required but not detected"
            validation_passed=false
        fi
        
        if [[ "$require_evidence" == "True" ]] && [[ ! "$completion_indicators" =~ "evidence_validated" ]]; then
            log_message "WARNING" "Evidence validation required but not detected"
            validation_passed=false
        fi
        
        if [[ "$validation_passed" == "true" ]]; then
            perform_auto_commit "$task_type" "$task_description" "$completion_indicators"
        else
            log_message "INFO" "Validation requirements not met, skipping auto-commit"
        fi
    else
        log_message "INFO" "No task completion indicators detected"
    fi
}

# Command line argument parsing
if [[ $# -gt 0 ]]; then
    case "$1" in
        --enable)
            CONFIG_PATH="$CONFIG_FILE" python3 << 'EOF'
import os, json
config_file = os.environ['CONFIG_PATH']
with open(config_file, 'r') as f:
    config = json.load(f)
config['enabled'] = True
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
EOF
            log_message "INFO" "Auto-commit enabled"
            ;;
        --disable)
            CONFIG_PATH="$CONFIG_FILE" python3 << 'EOF'
import os, json
config_file = os.environ['CONFIG_PATH']
with open(config_file, 'r') as f:
    config = json.load(f)
config['enabled'] = False
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
EOF
            log_message "INFO" "Auto-commit disabled"
            ;;
        --config)
            echo "Current configuration:"
            cat "$CONFIG_FILE" | python3 -m json.tool
            ;;
        --force)
            main "Manual" "Forced completion"
            ;;
        --help)
            echo "Usage: $0 [--enable|--disable|--config|--force|--help] [task_type] [task_description]"
            echo "  --enable    Enable auto-commit"
            echo "  --disable   Disable auto-commit"
            echo "  --config    Show current configuration"
            echo "  --force     Force auto-commit regardless of validation"
            echo "  --help      Show this help"
            exit 0
            ;;
        *)
            main "$1" "$2"
            ;;
    esac
else
    main
fi

exit 0