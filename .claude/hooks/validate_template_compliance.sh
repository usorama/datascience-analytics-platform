#!/bin/bash
# Template Compliance Validation Hook
# Executed via Claude Code PreToolUse hook to enforce template compliance

set -e

# Configuration
CONFIG_FILE=".claude/config/multi-agent-config.yaml"
TEMPLATE_DIR=".claude/docs/templates"
LOG_FILE=".claude/logs/quality/template_compliance.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log_validation() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log_validation "HOOK EXECUTED: Template compliance validation started"

# Check if validation is enabled
if [ ! -f "$CONFIG_FILE" ]; then
    log_validation "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 0  # Don't block if config missing
fi

# Get the tool being executed and target file from environment or arguments
TOOL_NAME="${CLAUDE_TOOL_NAME:-$1}"
TARGET_FILE="${CLAUDE_TOOL_FILE:-$2}"

log_validation "VALIDATION: Checking template compliance for tool:$TOOL_NAME file:$TARGET_FILE"

# Only validate document creation/editing tools for story files
case "$TOOL_NAME" in
    "Write"|"Edit"|"MultiEdit")
        case "$TARGET_FILE" in
            *"/stories/"*.md)
                log_validation "VALIDATING: Story template compliance for $TARGET_FILE"
                
                if [ -f "$TARGET_FILE" ]; then
                    # Check required sections
                    MISSING_SECTIONS=()
                    REQUIRED_SECTIONS=("Status" "Story" "Acceptance Criteria" "Tasks / Subtasks" "Dev Notes" "Evidence Collection" "File List" "Change Log" "MANDATORY QUALITY GATES CHECKLIST")
                    
                    for section in "${REQUIRED_SECTIONS[@]}"; do
                        if ! grep -q "^## $section\|^### $section" "$TARGET_FILE"; then
                            MISSING_SECTIONS+=("$section")
                        fi
                    done
                    
                    # Check for template validation metadata
                    if ! grep -q "TEMPLATE VALIDATION METADATA" "$TARGET_FILE"; then
                        MISSING_SECTIONS+=("Template Metadata")
                    fi
                    
                    # Fail if any sections are missing
                    if [ ${#MISSING_SECTIONS[@]} -gt 0 ]; then
                        log_validation "ERROR: Template compliance violation in $TARGET_FILE"
                        log_validation "ERROR: Missing required sections: ${MISSING_SECTIONS[*]}"
                        echo "TEMPLATE COMPLIANCE VIOLATION:"
                        echo "File: $TARGET_FILE"
                        echo "Missing sections: ${MISSING_SECTIONS[*]}"
                        echo ""
                        echo "REQUIRED ACTION: Use the correct template structure"
                        echo "Template compliance is MANDATORY and cannot be bypassed."
                        exit 1
                    fi
                    
                    log_validation "SUCCESS: Template compliance validated for $TARGET_FILE"
                fi
                ;;
            *)
                log_validation "INFO: File $TARGET_FILE not subject to template validation"
                ;;
        esac
        ;;
    *)
        log_validation "INFO: Tool $TOOL_NAME not subject to template validation"
        ;;
esac

log_validation "SUCCESS: Template compliance validation completed"
exit 0