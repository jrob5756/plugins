---
description: Implement a feature based on an epic from a prd.
arguement-hint: [prd-link] [epic-id]
---

If you do not have a `Doc` or `Epic`, you cannot proceed. You must stop and ask for these inputs. Do not provide an example request. Just specify that the input is required.

## PRIMARY DIRECTIVE

Your goal is to implement the feature described in the `$2` epic from the `$1` document.

## WORKFLOW STEPS

Present the following steps as **trackable todos** to guide progress:

1. **PRD Review**  
    - Locate the existing PRD document that is associated with the Task List.
    - If you cannot locate the PRD you must stop and ask for assistance. You cannot proceed without the PRD.
    - Thoroughly read and understand the PRD document. Extract key goals, constraints, and success criteria to inform all subsequent steps.
    - Analyze the `$2` in relation to the PRD. Identify how the epic contributes to the overall product vision and requirements.

2. **Supporting Documentation Review**  
   - Review any additional documentation which may include a requirements document `*.req.md` or design document.
   - Supporting documents should be in the same directory as the PRD or linked within it.

3. **Codebase Review**  
   If available, read `${config:project.overview_path}` to understand the system architecture and relevant modules. 

4. **Deep Code Analysis**
   Use the `code-search/*`tools to gather insights about the codebase and identify dependencies or affected modules and coding patterns.

5. **Implementation Planning**  
   Based on the insights gathered from the PRD, requirements document, and codebase review, outline a clear plan for implementing the feature. This plan should include:
   - Specific code changes required
   - Any new tests that need to be created

6. **Implementation Execution**  
   Carry out the implementation plan, making sure to follow best practices and coding standards.

7. **Review**  
   Conduct a thorough review of the implementation to ensure it:
   - Meets all requirements outlined in the PRD and Task List
   - Is free of bugs and errors
   - Includes appropriate tests and documentation
   - Strictly follows best practices and coding standards
