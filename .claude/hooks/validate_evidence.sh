#!/bin/bash
# validate_evidence.sh - BMAD Quality Gate Hook
# Validates that concrete evidence is provided for all claims

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
    echo "$(date '+%Y-%m-%d %H:%M:%S') [$level] validate_evidence: $message" >> "$LOG_DIR/evidence_validation.log"
}

check_enforcement_mode() {
    if [ -f "$CONFIG_FILE" ]; then
        if grep -q "enforcement.*mandatory\|enforcement.*true" "$CONFIG_FILE" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

validate_evidence_quality() {
    local story_file="$1"
    local evidence_failures=()
    
    if [ ! -f "$story_file" ]; then
        log_validation "ERROR" "Story file not found: $story_file"
        return $EXIT_FAILURE
    fi

    # Required evidence patterns
    local required_evidence=(
        "Test Results.*Evidence"
        "Build Output.*Evidence" 
        "Functionality Demo.*Evidence"
        "Code Review.*Evidence"
    )

    # Evidence quality patterns (what constitutes valid evidence)
    local valid_evidence_patterns=(
        "test.*pass\|success\|✓"
        "build.*success\|complete\|✓"
        "screenshot\|demo\|video\|recording"
        "review.*complete\|approved\|✓"
        "log.*output\|result\|trace"
        "commit.*hash\|sha\|id"
        "url.*http\|https"
        "file.*path\|location"
    )

    # Check for evidence sections
    for requirement in "${required_evidence[@]}"; do
        if ! grep -qi "$requirement" "$story_file"; then
            evidence_failures+=("Missing evidence section: $requirement")
            continue
        fi

        # Extract evidence section content
        local evidence_section=$(sed -n "/### $requirement/,/^### /p" "$story_file" | head -n -1)
        
        if [ -z "$evidence_section" ]; then
            evidence_failures+=("Empty evidence section: $requirement")
            continue
        fi

        # Check if evidence section contains valid evidence patterns
        local has_valid_evidence=false
        for pattern in "${valid_evidence_patterns[@]}"; do
            if echo "$evidence_section" | grep -qi "$pattern"; then
                has_valid_evidence=true
                break
            fi
        done

        if [ "$has_valid_evidence" = false ]; then
            evidence_failures+=("Insufficient evidence in section: $requirement")
        fi
    done

    # Check for placeholder evidence
    local placeholder_patterns=(
        "TODO"
        "TBD"
        "placeholder"
        "example"
        "sample"
        "dummy"
        "mock"
        "\[insert\]"
        "\[add\]"
        "\[provide\]"
    )

    for pattern in "${placeholder_patterns[@]}"; do
        if grep -qi "$pattern" "$story_file"; then
            evidence_failures+=("Placeholder evidence detected: $pattern")
        fi
    done

    # Report evidence validation results
    if [ ${#evidence_failures[@]} -gt 0 ]; then
        log_validation "ERROR" "Evidence validation failed for $story_file"
        echo "❌ QUALITY GATE FAILURE: Evidence Validation"
        echo "   The following evidence issues were found:"
        for failure in "${evidence_failures[@]}"; do
            echo "   • $failure"
        done
        echo ""
        echo "   Required Evidence Standards:"
        echo "   • Test Results: Include actual test output, pass/fail status"
        echo "   • Build Output: Include build logs, success confirmation"
        echo "   • Functionality Demo: Include screenshots, videos, or recordings"
        echo "   • Code Review: Include review completion, approval status"
        echo ""
        echo "   Valid Evidence Formats:"
        echo "   • Log outputs and traces"
        echo "   • Commit hashes and references"
        echo "   • URLs to deployments or demos"
        echo "   • File paths to artifacts"
        echo "   • Screenshots and recordings"
        echo ""
        return $EXIT_FAILURE
    fi

    log_validation "INFO" "Evidence validation passed for $story_file"
    return $EXIT_SUCCESS
}

check_completion_status() {
    local story_file="$1"
    
    # Check if story is marked as complete or for review
    if grep -q "Status.*Review\|Status.*Done\|Status.*Complete" "$story_file" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

main() {
    # Only enforce if configuration enables it
    if ! check_enforcement_mode; then
        log_validation "INFO" "Evidence validation in advisory mode - skipping enforcement"
        exit $EXIT_SUCCESS
    fi

    # Get current working directory and check for story files
    local current_dir="$(pwd)"
    local story_files=()
    
    # Look for story files being marked as complete
    while IFS= read -r -d '' file; do
        if [[ "$file" =~ story.*\.md$ ]] && check_completion_status "$file"; then
            story_files+=("$file")
        fi
    done < <(find "$current_dir" -name "*.md" -type f -print0 2>/dev/null)

    # If no completed story files, exit successfully
    if [ ${#story_files[@]} -eq 0 ]; then
        log_validation "INFO" "No completed stories detected for evidence validation"
        exit $EXIT_SUCCESS
    fi

    # Validate evidence for each completed story
    local validation_failed=false
    for story_file in "${story_files[@]}"; do
        log_validation "INFO" "Validating evidence for: $story_file"
        
        if ! validate_evidence_quality "$story_file"; then
            validation_failed=true
        fi
    done

    if [ "$validation_failed" = true ]; then
        echo ""
        echo "🚨 BMAD QUALITY GATE: Evidence validation failed"
        echo "   All claims must be backed by concrete, verifiable evidence"
        echo "   before marking stories as complete."
        echo ""
        exit $EXIT_FAILURE
    fi

    log_validation "INFO" "All evidence validations passed"
    exit $EXIT_SUCCESS
}

# Handle script execution
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi