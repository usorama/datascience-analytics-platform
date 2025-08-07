# Story Template v2.0 - Mandatory Structure

## TEMPLATE ENFORCEMENT NOTICE
**This template structure is MANDATORY. Agents cannot produce story documents in any other format.**

## Story {{epic_number}}.{{story_number}}: {{story_title}}

### Status
**Current Status**: {{status}}
**Valid States**: Draft, Approved, InProgress, Review, Done

**STATUS CHANGE RULES:**
- Draft → Approved: Requires validation by PO/SM
- Approved → InProgress: Automatic when dev agent starts work
- InProgress → Review: Requires 100% DoD checklist completion
- Review → Done: Requires verification agent approval

### Story
**As a** {{user_role}},
**I want** {{desired_action}},
**so that** {{business_benefit}}.

### Acceptance Criteria
{{#each acceptance_criteria}}
{{@index}}. {{criterion}}
{{/each}}

**VALIDATION REQUIREMENT**: Each AC must be testable and verifiable with concrete evidence.

### Tasks / Subtasks
{{#each tasks}}
- [ ] {{task_name}} (AC: {{associated_acceptance_criteria}})
{{#each subtasks}}
  - [ ] {{subtask_name}}
{{/each}}
{{/each}}

**COMPLETION REQUIREMENT**: ALL tasks and subtasks must be marked [x] before status can change to Review.

### Dev Notes
**PURPOSE**: Provide complete implementation context so dev agent never needs to read external architecture docs.

#### Technical Context
{{extracted_architecture_info}}

#### Previous Story Insights
{{previous_story_learnings}}

#### Implementation Guidelines
{{specific_implementation_guidance}}

#### Testing Requirements
{{testing_standards_and_requirements}}

**SOURCE REQUIREMENT**: Every technical detail must include source reference [Source: architecture/filename.md#section]

### Evidence Collection (MANDATORY)
**REQUIREMENT**: Concrete evidence must be provided for all claims before status can advance to Review.

#### Test Results
- [ ] Test execution logs showing 100% pass rate
- [ ] Build output showing zero errors/warnings
- [ ] Performance metrics (if applicable)

#### Functionality Demonstration  
- [ ] Screenshots or detailed description of working functionality
- [ ] Each acceptance criterion verified with evidence
- [ ] Edge cases tested and documented

#### Quality Validation
- [ ] Code review checklist completed
- [ ] Security validation performed
- [ ] Performance requirements met

### File List
**REQUIREMENT**: List ALL files created, modified, or affected during implementation.

#### Files Created
{{#each created_files}}
- {{file_path}} - {{description}}
{{/each}}

#### Files Modified
{{#each modified_files}}
- {{file_path}} - {{changes_description}}
{{/each}}

#### Files Affected
{{#each affected_files}}
- {{file_path}} - {{impact_description}}
{{/each}}

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| {{date}} | {{version}} | {{change_description}} | {{author}} |

### Dev Agent Record
**FILLED BY DEV AGENT DURING IMPLEMENTATION**

#### Agent Model Used
{{agent_model_name_version}}

#### Implementation Approach
{{implementation_strategy_used}}  

#### Challenges Encountered
{{challenges_and_solutions}}

#### Completion Notes
{{completion_summary_and_handoff_notes}}

### QA Results
**FILLED BY VERIFICATION AGENT**

#### Review Status
**Status**: APPROVED / REJECTED
**Reviewer**: {{verification_agent_name}}
**Date**: {{review_date}}

#### Quality Assessment
{{quality_score_and_analysis}}

#### Issues Found
{{#each issues_found}}
- {{issue_description}} - {{severity}} - {{resolution_required}}
{{/each}}

#### Approval Decision
{{approval_rationale_or_rejection_reasons}}

## MANDATORY QUALITY GATES CHECKLIST

**CRITICAL**: This checklist must be 100% complete before story can advance to Review status.

### Requirements Compliance
- [ ] All functional requirements implemented
- [ ] All acceptance criteria met and verified
- [ ] All tasks and subtasks completed [x]

### Code Quality Standards
- [ ] Code follows project coding standards
- [ ] No linter errors or warnings introduced
- [ ] Proper error handling implemented
- [ ] Security best practices followed

### Testing Requirements
- [ ] All unit tests implemented and passing
- [ ] Integration tests implemented (if required)
- [ ] Manual testing completed and documented
- [ ] Test coverage meets project standards

### Evidence Collection
- [ ] Test execution logs captured
- [ ] Build output captured showing success
- [ ] Functionality demonstration provided
- [ ] All evidence ready for verification

### Documentation
- [ ] File List complete and accurate
- [ ] Dev Notes provide complete context
- [ ] Change Log updated appropriately
- [ ] Implementation decisions documented

### Quality Validation
- [ ] No known bugs or issues remaining
- [ ] Performance requirements met
- [ ] Security requirements satisfied
- [ ] Integration with existing code validated

## TEMPLATE VALIDATION METADATA
- Template Version: 2.0
- Required Sections: 12
- Mandatory Fields: 23
- Quality Gates: 18
- Evidence Requirements: 4

**ENFORCEMENT**: This template structure is architecturally enforced. Non-compliant outputs will be rejected.