# {{project_name}} Product Requirements Document (PRD)

## TEMPLATE ENFORCEMENT NOTICE
**This template structure is MANDATORY. Agents cannot produce PRD documents in any other format.**

## Goals and Background Context

### Goals
{{#each goals}}
- {{goal}}
{{/each}}

**PURPOSE**: Define clear, measurable outcomes this PRD will deliver if successful.

### Background Context
{{background_context}}

**REQUIREMENT**: 1-2 paragraphs summarizing what problem this solves and why it matters.

### Change Log
| Date | Version | Description | Author |
|------|---------|-------------|---------|
| {{date}} | {{version}} | {{change_description}} | {{author}} |

## Requirements

### Functional Requirements
{{#each functional_requirements}}
{{@index}}. **FR{{@index}}**: {{requirement}}
{{/each}}

**VALIDATION REQUIREMENT**: Each requirement must be testable and traceable to acceptance criteria.

### Non-Functional Requirements  
{{#each non_functional_requirements}}
{{@index}}. **NFR{{@index}}**: {{requirement}}
{{/each}}

**VALIDATION REQUIREMENT**: Performance, security, and scalability requirements with measurable criteria.

## User Interface Design Goals

### Overall UX Vision
{{ux_vision}}

### Key Interaction Paradigms
{{interaction_paradigms}}

### Core Screens and Views
{{#each core_screens}}
- **{{screen_name}}**: {{screen_description}}
{{/each}}

### Accessibility Requirements
**Level**: {{accessibility_level}}
**Standards**: {{accessibility_standards}}

### Target Platforms
**Platforms**: {{target_platforms}}
**Device Support**: {{device_support}}

## Technical Assumptions

### Repository Structure
**Type**: {{repository_type}}
**Rationale**: {{repository_rationale}}

### Service Architecture
**Architecture**: {{service_architecture}}
**Rationale**: {{architecture_rationale}}

### Testing Requirements
**Strategy**: {{testing_strategy}}
**Coverage**: {{testing_coverage}}

### Additional Technical Assumptions
{{#each additional_assumptions}}
- {{assumption}}
{{/each}}

## Epic List

{{#each epics}}
### Epic {{epic_number}}: {{epic_title}}
**Goal**: {{epic_goal}}

{{#each stories}}
#### Story {{../epic_number}}.{{story_number}}: {{story_title}}

**As a** {{user_type}},
**I want** {{action}},
**so that** {{benefit}}.

##### Acceptance Criteria
{{#each acceptance_criteria}}
{{@index}}. {{criteria}}
{{/each}}

{{/each}}
{{/each}}

## Checklist Results Report

### PRD Completeness Validation
- [ ] All goals clearly defined and measurable
- [ ] Background context provides sufficient rationale
- [ ] Functional requirements are testable and complete
- [ ] Non-functional requirements have measurable criteria
- [ ] UI/UX goals align with target user needs
- [ ] Technical assumptions are documented and justified
- [ ] All epics deliver end-to-end value
- [ ] All stories follow proper user story format
- [ ] All acceptance criteria are testable and specific

### Quality Gates Validation
- [ ] Requirements traceability matrix complete
- [ ] Epic-story alignment verified
- [ ] Technical feasibility confirmed
- [ ] Resource requirements estimated
- [ ] Timeline and milestones defined
- [ ] Success metrics established
- [ ] Risk assessment completed

## Next Steps

### UX Expert Prompt
Review this PRD and create a comprehensive UI/UX specification that translates these requirements into specific interface designs, interaction patterns, and user experience flows.

### Architect Prompt  
Using this PRD as the foundation, design a technical architecture that can deliver all functional and non-functional requirements within the specified technical constraints and assumptions.

## TEMPLATE VALIDATION METADATA
- Template Version: 2.0
- Required Sections: 8
- Mandatory Fields: 15
- Epic Structure: Nested with stories and AC
- Quality Gates: 16

**ENFORCEMENT**: This template structure is architecturally enforced. Non-compliant outputs will be rejected.