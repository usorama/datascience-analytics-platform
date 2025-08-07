#!/bin/bash
# validate_dod_completion.sh - BMAD Quality Gate Hook
# Ensures 100% DoD completion before story advancement

set -euo pipefail

# Configuration
CLAUDE_DIR="$(dirname "$(dirname "$0")")"
CONFIG_FILE="$CLAUDE_DIR/config/multi-agent-config.yaml"
LOG_DIR="$CLAUDE_DIR/logs/quality"

# Create log directory
mkdir -p "$LOG_DIR"

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

log_validation() {
    local level="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] validate_dod_completion: $message" >> "$LOG_DIR/dod_validation.log"
}

check_enforcement_mode() {
    if [ -f "$CONFIG_FILE" ]; then
        if grep -q "enforcement.*mandatory\|enforcement.*true" "$CONFIG_FILE" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

validate_story_dod() {
    local story_file="$1"
    
    if [ ! -f "$story_file" ]; then
        log_validation "ERROR" "Story file not found: $story_file"
        return $EXIT_FAILURE
    fi

    # Extract DoD checklist items
    local checklist_start=$(grep -n "## Definition of Done Checklist" "$story_file" | cut -d: -f1)
    if [ -z "$checklist_start" ]; then
        log_validation "ERROR" "No DoD checklist found in $story_file"
        return $EXIT_FAILURE
    fi

    # Count total and completed items
    local total_items=0
    local completed_items=0
    local line_num=$checklist_start
    
    while IFS= read -r line; do
        ((line_num++))
        
        # Stop at next section
        if [[ "$line" =~ ^##[[:space:]] && $line_num -gt $checklist_start ]]; then
            break
        fi
        
        # Count checklist items
        if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\[ ]]; then
            ((total_items++))
        elif [[ "$line" =~ ^[[:space:]]*-[[:space:]]*\[[xX]\] ]]; then
            ((total_items++))
            ((completed_items++))
        fi
    done < <(tail -n +$checklist_start "$story_file")

    if [ $total_items -eq 0 ]; then
        log_validation "ERROR" "No checklist items found in DoD section"
        return $EXIT_FAILURE
    fi

    local completion_percent=$((completed_items * 100 / total_items))
    
    log_validation "INFO" "DoD Progress: $completed_items/$total_items ($completion_percent%)"

    if [ $completion_percent -lt 100 ]; then
        log_validation "ERROR" "DoD completion is $completion_percent% - must be 100% for advancement"
        echo "❌ QUALITY GATE FAILURE: DoD Completion"
        echo "   Current: $completed_items/$total_items items completed ($completion_percent%)"
        echo "   Required: 100% completion"
        echo "   Action: Complete all DoD checklist items before advancing story status"
        return $EXIT_FAILURE
    fi

    log_validation "INFO" "DoD validation passed: 100% completion achieved"
    return $EXIT_SUCCESS
}

check_status_change() {
    local story_file="$1"
    
    # Check if status is being changed to Review or Done
    if grep -q "Status.*Review\|Status.*Done" "$story_file" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

main() {
    # Only enforce if configuration enables it
    if ! check_enforcement_mode; then
        log_validation "INFO" "DoD validation in advisory mode - skipping enforcement"
        exit $EXIT_SUCCESS
    fi

    # Get current working directory and check for story files
    local current_dir="$(pwd)"
    local story_files=()
    
    # Look for story files being modified
    while IFS= read -r -d '' file; do
        if [[ "$file" =~ story.*\.md$ ]] && check_status_change "$file"; then
            story_files+=("$file")
        fi
    done < <(find "$current_dir" -name "*.md" -type f -print0 2>/dev/null)

    # If no story files with status changes, exit successfully
    if [ ${#story_files[@]} -eq 0 ]; then
        log_validation "INFO" "No story status changes detected"
        exit $EXIT_SUCCESS
    fi

    # Validate each story file
    local validation_failed=false
    for story_file in "${story_files[@]}"; do
        log_validation "INFO" "Validating DoD for: $story_file"
        
        if ! validate_story_dod "$story_file"; then
            validation_failed=true
        fi
    done

    if [ "$validation_failed" = true ]; then
        echo ""
        echo "🚨 BMAD QUALITY GATE: DoD completion validation failed"
        echo "   All Definition of Done checklist items must be 100% complete"
        echo "   before advancing story status to Review or Done."
        echo ""
        exit $EXIT_FAILURE
    fi

    log_validation "INFO" "All story DoD validations passed"
    exit $EXIT_SUCCESS
}

# Handle script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi