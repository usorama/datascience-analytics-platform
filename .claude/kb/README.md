# Claude Code Automation Knowledge Base

This directory contains knowledge documents (KDs) for troubleshooting, fixes, and system insights.

## Document Index

### Bug Fixes & Troubleshooting
- **[KD-2025-01-23-001](./argparse-error-fix-2025-01-23.md)** - Claude Hook Argparse Error Fix
  - **Issue:** Sporadic `unrecognized arguments: --v3` errors
  - **Solution:** Robust argument parsing with graceful unknown argument handling
  - **Impact:** Restored development velocity, improved system reliability
  - **Status:** ✅ Resolved

- **[KD-2025-01-23-002](./hook-working-directory-fix-2025-01-23.md)** - Claude Hook Working Directory Fix
  - **Issue:** Hooks failing with "No such file or directory" from subdirectories
  - **Solution:** Absolute paths in hook commands for working directory independence
  - **Impact:** Restored hook functionality across all project contexts
  - **Status:** ✅ Resolved

### Security & Audits
- **[KD-2025-01-23-003](./claude-folder-security-audit-2025-01-23.md)** - Claude Folder Security Audit
  - **Scope:** Comprehensive security review of `.claude/` folder (58 files, 1,114 lines of code)
  - **Rating:** B+ (Good) - No critical vulnerabilities found
  - **Key Findings:** 4 medium risks, excellent security fundamentals, well-architected safety layers
  - **Recommendations:** Hash function improvements, log rotation, permission hardening
  - **Status:** ✅ Complete - Next review in 6 months

## Document Standards

### Naming Convention
- Format: `{issue-type}-{date}-{sequence}.md`
- Example: `argparse-error-fix-2025-01-23.md`

### Required Sections
1. **Problem Statement** - Clear description of the issue
2. **Investigation Process** - Step-by-step analysis
3. **Root Cause Analysis** - Primary and secondary causes
4. **Solution Implementation** - Code changes and fixes
5. **Testing & Validation** - Test cases and results
6. **Prevention Measures** - How to avoid similar issues
7. **Files Modified** - Complete list of changed files
8. **Lessons Learned** - Technical and process insights
9. **Future Recommendations** - Next steps and improvements

### Document Types
- **Bug Fix**: Issues that caused system failures or errors
- **Enhancement**: Improvements to existing functionality
- **Investigation**: Research and analysis documents
- **Process**: Workflow and methodology documentation
- **Security Audit**: Comprehensive security and risk assessments

## Quick Reference

### Common Issues
- **Argument Parsing Errors**: See KD-2025-01-23-001
- **Hook Configuration Mismatches**: See KD-2025-01-23-001
- **Working Directory Issues**: See KD-2025-01-23-002
- **Hook Execution Failures**: See KD-2025-01-23-002
- **Security Concerns**: See KD-2025-01-23-003
- **Code Quality Issues**: See KD-2025-01-23-003

### Best Practices
- Always use `parse_known_args()` for argument parsing
- Use absolute paths for hook commands in settings.json
- Implement graceful error handling with fallback behavior
- Document configuration-implementation dependencies
- Test hooks from multiple working directories
- Add comprehensive test coverage for argument combinations
- Use cryptographic hash functions for security-sensitive operations
- Implement log rotation and retention policies
- Set restrictive file permissions (600) for sensitive files
- Use specific permission patterns instead of broad wildcards

### Security Guidelines
- **Hash Functions**: Use `hashlib.sha256()` instead of built-in `hash()`
- **File Permissions**: Create log files with 600 permissions
- **Configuration**: Avoid hardcoded absolute paths, use environment variables
- **Permissions**: Use specific command patterns, avoid broad wildcards like `Bash(*:*)`
- **Subprocess**: Never use `os.system()`, prefer `subprocess.run()` with timeouts
- **Input Validation**: Always validate and sanitize user inputs
- **Error Handling**: Implement secure defaults in error conditions

---

*Last Updated: January 23, 2025*
*Security Audit: January 23, 2025 - Next Review: July 2025*
