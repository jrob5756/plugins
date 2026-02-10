---
agent: Coder
description: Review implementation changes against PRD requirements and generate a comprehensive validation report
model: Claude Opus 4.6 (copilot)
---

## INPUTS

- `PRD` (string, required): A link to a Product Requirements Document file (e.g. `.prd.md`) that contains the requirements and implementation plan to validate against.
- `Scope` (string, required): The scope of changes to review. This can be:
  - A commit hash or range (e.g., `abc123` or `abc123..def456`)
  - A branch name (e.g., `feature/embedded-artifacts`)
  - A list of specific files that were modified
  - The string "workspace" to review all current changes in the workspace

If you do not have a `PRD` or `Scope`, you cannot proceed. You must stop and ask for these inputs. Do not provide an example request. Just specify that the inputs are required.

## PRIMARY DIRECTIVE

Conduct a comprehensive review of the implementation changes specified in `${input:Scope}` against ALL requirements, goals, and specifications defined in the `${input:PRD}` document. Generate a detailed validation report that:
- **Verifies complete implementation** of all requirements and tasks
- **Identifies gaps, deviations, or missing implementations**
- **Validates quality standards** including tests, documentation, and best practices
- **Provides actionable recommendations** for addressing any findings

## WORKFLOW STEPS

Present the following steps as **trackable todos** to guide progress:

1. **Load and Parse PRD**
   - Read the complete PRD document from `${input:PRD}`
   - Extract all requirements (REQ-, SEC-, CON-, GUD-, PAT- prefixed items)
   - Extract all EPICs and their associated tasks (ITEM- prefixed)
   - Identify success criteria, constraints, and quality standards
   - Note risk classifications and mitigation strategies

2. **Analyze Scope of Changes**
   - Identify all files modified within `${input:Scope}`
   - If scope is a branch/PR: get diff against base branch
   - If scope is commits: analyze all changes in commit range
   - If scope is "workspace": review all uncommitted changes
   - Generate a comprehensive list of all modified files and their change types (added/modified/deleted)

3. **Map Changes to PRD Requirements**
   - For each requirement in the PRD, identify corresponding implementation changes
   - For each EPIC and task, verify if the described work was completed
   - Create a traceability matrix linking PRD items to actual changes
   - Identify any changes that don't map to PRD requirements (scope creep)

4. **Deep Implementation Review**
   Use `code-search/*`tools to:
   - Verify each implemented feature matches PRD specifications exactly
   - Check that removed/deleted components listed in PRD are actually removed
   - Validate that architectural decisions align with Solution Architecture section
   - Confirm file modifications match the Files section (FILE- items)
   - Verify no unintended side effects or breaking changes

5. **Requirements Validation**
   For each requirement category:
   - **Functional Requirements (REQ-)**: Verify feature implementation completeness
   - **Security Requirements (SEC-)**: Validate security controls are in place
   - **Constraints (CON-)**: Check performance, size, compatibility limits
   - **Guidelines (GUD-)**: Verify adherence to best practices
   - **Patterns (PAT-)**: Confirm design patterns are correctly applied

6. **Quality Assurance Validation**
   - Verify all tests specified in Quality & Testing section are implemented
   - Check test coverage meets requirements
   - Validate documentation updates match Documentation section
   - Confirm build/deployment changes align with Deployment section
   - Review error handling and edge cases

7. **Gap Analysis**
   - Identify all PRD requirements NOT met by the implementation
   - List all EPIC tasks that are incomplete or missing
   - Note any deviations from specified architecture or design
   - Highlight missing tests, documentation, or validation steps
   - Flag any high-risk areas that lack proper mitigation

8. **Generate Validation Report**
   Create a comprehensive `.review.md` report with:
   - Executive summary of compliance status
   - Detailed requirement-by-requirement validation results
   - Complete list of gaps and deviations
   - Risk assessment of identified issues
   - Prioritized recommendations for remediation
   - Metrics on implementation completeness

## REVIEW CRITERIA

Evaluate implementation against these standards:

### Completeness
- ✅ All EPICs are fully implemented
- ✅ All tasks (ITEM-) are completed as specified
- ✅ All requirements (REQ-, SEC-, CON-, etc.) are satisfied
- ✅ All specified files are modified/created/deleted as planned

### Correctness
- ✅ Implementation matches PRD specifications exactly
- ✅ No logic errors or bugs introduced
- ✅ Proper error handling implemented
- ✅ Edge cases addressed

### Quality
- ✅ Code follows specified patterns and guidelines
- ✅ Tests provide adequate coverage
- ✅ Documentation is complete and accurate
- ✅ Performance meets specified constraints

### Compliance
- ✅ Security requirements are met
- ✅ Backward compatibility maintained (if required)
- ✅ Platform compatibility verified
- ✅ Deployment strategy followed

## REVIEW BEST PRACTICES

- Be **precise and specific** - reference exact file names, line numbers, and code elements
- Provide **actionable feedback** - don't just identify problems, suggest solutions
- Use **objective metrics** - quantify completeness, coverage, and compliance
- Include **positive findings** - acknowledge what was done well
- Maintain **traceability** - link every finding back to specific PRD requirements
- Be **exhaustive** - review EVERY requirement, don't skip any

## FILE NAMING CONVENTION

- Save the review report in the same directory as the PRD
- Use the naming pattern: `[prd-name].review.md`
- Example: If PRD is `embedded-artifacts.prd.md`, save as `embedded-artifacts.review.md`

## MANDATORY TEMPLATE

Mandatory template can be found [here](../templates/octane.review.template.md).
