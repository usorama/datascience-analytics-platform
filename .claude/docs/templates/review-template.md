# Code Review Report: {{component_name}}

## TEMPLATE ENFORCEMENT NOTICE
**This template structure is MANDATORY. Agents cannot produce review documents in any other format.**

## Review Overview

### Component Information
- **Component**: {{component_name}}
- **Type**: {{component_type}}
- **Author**: {{author}}
- **Reviewer**: {{reviewer}}
- **Review Date**: {{review_date}}
- **Files Reviewed**: {{file_count}} files

### Review Scope
{{#each review_scope}}
- {{scope_item}}
{{/each}}

### Overall Assessment
**Status**: {{overall_status}}
**Quality Score**: {{quality_score}}/10
**Recommendation**: {{recommendation}}

## Code Quality Analysis

### Architecture & Design
**Score**: {{architecture_score}}/10

#### Strengths
{{#each architecture_strengths}}
- {{strength}}
{{/each}}

#### Issues Found
{{#each architecture_issues}}
- **{{severity}}**: {{issue_description}}
  - **File**: {{file_location}}
  - **Fix Required**: {{fix_required}}
{{/each}}

#### Recommendations
{{#each architecture_recommendations}}
- {{recommendation}}
{{/each}}

### Code Standards Compliance
**Score**: {{standards_score}}/10

#### Compliance Check
- [ ] Follows project coding standards
- [ ] Proper naming conventions used
- [ ] Consistent indentation and formatting
- [ ] Appropriate comments and documentation
- [ ] No linter errors or warnings
- [ ] Type safety maintained (if applicable)

#### Non-Compliance Issues
{{#each standards_issues}}
- **File**: {{file_name}}
- **Issue**: {{issue_description}}
- **Severity**: {{severity}}
- **Fix**: {{suggested_fix}}
{{/each}}

### Performance Analysis
**Score**: {{performance_score}}/10

#### Performance Metrics
- **Bundle Impact**: {{bundle_impact}}
- **Runtime Performance**: {{runtime_performance}}
- **Memory Usage**: {{memory_usage}}
- **Load Time Impact**: {{load_time_impact}}

#### Performance Issues
{{#each performance_issues}}
- **Issue**: {{issue_description}}
- **Impact**: {{performance_impact}}
- **Location**: {{file_location}}
- **Suggested Fix**: {{suggested_fix}}
{{/each}}

#### Performance Recommendations
{{#each performance_recommendations}}
- {{recommendation}}
{{/each}}

## Functionality Verification

### Feature Completeness
**Score**: {{functionality_score}}/10

#### Requirements Verification
{{#each requirements}}
- **Requirement**: {{requirement_description}}
- **Status**: {{verification_status}}
- **Evidence**: {{verification_evidence}}
{{/each}}

#### Functional Issues
{{#each functional_issues}}
- **Issue**: {{issue_description}}
- **Severity**: {{severity}}
- **Steps to Reproduce**: {{reproduction_steps}}
- **Expected vs Actual**: {{expected_vs_actual}}
{{/each}}

### Testing Coverage
**Coverage Score**: {{test_coverage_score}}/10

#### Test Analysis
- [ ] Unit tests present and comprehensive
- [ ] Integration tests cover key workflows
- [ ] Edge cases properly tested
- [ ] Error handling tested
- [ ] Performance tests included (if applicable)
- [ ] All tests passing

#### Testing Gaps
{{#each testing_gaps}}
- **Gap**: {{gap_description}}
- **Priority**: {{gap_priority}}
- **Suggested Tests**: {{suggested_tests}}
{{/each}}

## Security Assessment

### Security Score
**Score**: {{security_score}}/10

#### Security Checklist
- [ ] Input validation implemented
- [ ] Output sanitization applied
- [ ] Authentication/authorization respected
- [ ] No hardcoded secrets or credentials
- [ ] Secure data handling practices
- [ ] No known security vulnerabilities
- [ ] HTTPS/secure transport used
- [ ] Error messages don't leak sensitive info

#### Security Issues
{{#each security_issues}}
- **Issue**: {{issue_description}}
- **Severity**: {{severity}}
- **Location**: {{file_location}}
- **Risk**: {{security_risk}}
- **Mitigation**: {{suggested_mitigation}}
{{/each}}

#### Security Recommendations
{{#each security_recommendations}}
- {{recommendation}}
{{/each}}

## Documentation & Maintainability

### Documentation Score
**Score**: {{documentation_score}}/10

#### Documentation Checklist
- [ ] Code is self-documenting with clear naming
- [ ] Complex logic has explanatory comments
- [ ] Public APIs have proper documentation
- [ ] README updated (if applicable)
- [ ] Change log updated
- [ ] Deployment notes provided (if applicable)

#### Documentation Issues
{{#each documentation_issues}}
- **Issue**: {{issue_description}}
- **Location**: {{file_location}}
- **Required Action**: {{required_action}}
{{/each}}

### Maintainability Assessment
**Score**: {{maintainability_score}}/10

#### Maintainability Factors
- **Code Complexity**: {{complexity_assessment}}
- **Modularity**: {{modularity_assessment}}
- **Reusability**: {{reusability_assessment}}
- **Testability**: {{testability_assessment}}

## Detailed Issue Summary

### Critical Issues (Must Fix)
{{#each critical_issues}}
- **{{issue_id}}**: {{issue_description}}
  - **File**: {{file_location}}
  - **Impact**: {{impact_description}}
  - **Fix Required**: {{fix_description}}
{{/each}}

### Major Issues (Should Fix)
{{#each major_issues}}
- **{{issue_id}}**: {{issue_description}}
  - **File**: {{file_location}}
  - **Impact**: {{impact_description}}
  - **Suggested Fix**: {{fix_description}}
{{/each}}

### Minor Issues (Nice to Fix)
{{#each minor_issues}}
- **{{issue_id}}**: {{issue_description}}
  - **File**: {{file_location}}
  - **Suggestion**: {{fix_description}}
{{/each}}

## Review Decision

### Final Recommendation
**Decision**: {{final_decision}}
**Rationale**: {{decision_rationale}}

### Pre-Merge Requirements
{{#each pre_merge_requirements}}
- [ ] {{requirement_description}}
{{/each}}

### Post-Merge Recommendations
{{#each post_merge_recommendations}}
- {{recommendation}}
{{/each}}

## Reviewer Notes

### Review Process
- **Time Spent**: {{review_time}}
- **Review Method**: {{review_method}}
- **Tools Used**: {{tools_used}}

### Additional Comments
{{additional_comments}}

### Follow-up Actions
{{#each follow_up_actions}}
- **Action**: {{action_description}}
- **Owner**: {{action_owner}}
- **Timeline**: {{action_timeline}}
{{/each}}

## TEMPLATE VALIDATION METADATA
- Template Version: 2.0
- Required Sections: 10
- Mandatory Fields: 25
- Quality Gates: 20
- Score Categories: 7

**ENFORCEMENT**: This template structure is architecturally enforced. Non-compliant outputs will be rejected.