---
description: Review a PR that adds or updates an Octane scenario against the authoring guide.
arguement-hint: [pr-number]
---

## PRIMARY DIRECTIVE

Review the GitHub pull request `$ARGUMENTS` that adds or updates Octane scenario(s). Validate all scenario changes against the [Scenario Authoring Guide](docs/scenario-authoring-guide.md) and existing scenarios as reference. Produce a structured review comment and a review verdict (approve, comment, or request-changes).

## CONSTRAINTS

### GitHub Tools
Use the GH CLI (`gh`) for all GitHub interactions. Do not use MCP GitHub tools.

### Scope
Only review files under `artifacts/scenarios/` and `docs/scenarios.md`. Ignore unrelated changes but note if the PR mixes scenario changes with other code changes (which is discouraged).

### Review Standards
- Be constructive and specific — cite the authoring guide section for each finding
- Distinguish between **blocking issues** (must fix) and **suggestions** (nice to have)
- Acknowledge what the author did well before listing issues

## WORKFLOW

### Step 1: Fetch PR Details

```bash
gh pr view $ARGUMENTS --json number,title,body,author,files,headRefName,baseRefName,url
```

Also fetch the full diff:
```bash
gh pr diff $ARGUMENTS
```

### Step 2: Identify Scenario Changes

From the PR files list, identify:
- Which scenario(s) are being added or modified (directories under `artifacts/scenarios/`)
- Whether `docs/scenarios.md` was updated
- Whether any shared artifacts are referenced

### Step 3: Load Reference Materials

Read the following reference materials:
1. [Scenario Authoring Guide](docs/scenario-authoring-guide.md) — the primary review standard
2. For each changed scenario, read its full `scenario.json` and `README.md`
3. Load 2-3 existing well-structured scenarios as reference baselines:
   - `artifacts/scenarios/spec-driven-development/scenario.json`
   - `artifacts/scenarios/flaky-test-fix/scenario.json`
   - `artifacts/scenarios/test-analysis/scenario.json`
4. **Note any discrepancies between the authoring guide and established scenarios**: If the authoring guide conflicts with the conventions used by reference scenarios (e.g., frontmatter field names), use the conventions from the **reference scenarios** as the standard and note the guide discrepancy in the review as a **suggestion** to update the guide.

### Step 4: Research VS Code AI Artifact Best Practices

Search the web for current best practices on authoring AI artifacts for VS Code. Run targeted searches for each artifact type present in the PR:

1. **Prompts** (if PR includes `.prompt.md` files): Search for best practices on writing VS Code Copilot prompt files (`.prompt.md`), including frontmatter structure, instruction clarity, and prompt engineering techniques for chat participants.
2. **Agents / Chat Modes** (if PR includes `.agent.md` or `.chatmode.md` files): Search for best practices on creating VS Code Copilot custom agents and chat modes, including role definitions, tool scoping, and system prompt design.
3. **Instructions** (if PR includes `.instructions.md` files): Search for best practices on writing VS Code Copilot custom instructions files, including scoping with `applyTo` globs, instruction specificity, and layering.
4. **Skills** (if PR includes `skills/` directories): Search for best practices on creating agent skills following the [agentskills.io](https://agentskills.io) specification, including progressive disclosure, SKILL.md formatting, and resource organization.

Use findings to supplement the authoring guide when evaluating artifact quality in later steps. Note any PR artifacts that deviate from current community best practices as **suggestions** in the review.

### Step 5: Validate Scenario Metadata (`scenario.json`)

For each scenario's `scenario.json`, verify:

#### Required Fields
- [ ] `id` — present, kebab-case, matches directory name
- [ ] `name` — present, title case, descriptive
- [ ] `description` — present, max 100 characters, clear value proposition
- [ ] `category` — one of: `planning`, `development`, `quality`, `operations`
- [ ] `difficulty` — one of: `beginner`, `intermediate`, `advanced`
- [ ] `allowed_locations` — present and explicitly set. Valid values: `["workspace"]`, `["user"]`, or `["workspace", "user"]`

#### Optional Fields (if present, validate correctness)
- [ ] `tags` — array of 3-5 relevant, lowercase tags
- [ ] `version` — valid semver format
- [ ] `author` — present and non-empty
- [ ] `homepage` — valid URL if provided
- [ ] `documentation` — relative path, file exists
- [ ] `shared_artifacts` — all referenced files exist in `artifacts/shared/`
- [ ] `mcp_servers` — all listed servers exist in `artifacts/shared/mcp.json`

#### Consistency Checks
- [ ] All files referenced in `shared_artifacts` actually exist

#### `allowed_locations` Validation
- [ ] `allowed_locations` is **explicitly present** — if missing, flag as **blocking**
- [ ] Value is justified based on artifact types:
  - Scenarios with `templates/` or `config/` → should include `"workspace"`
  - Scenarios with ONLY agents/prompts/instructions/skills → should support both `["workspace", "user"]`
  - If set to only one location without justification, flag as **suggestion**

### Step 6: Validate README Documentation

For each scenario's `README.md`, verify:

- [ ] **Exists** and is non-empty
- [ ] **Structure** follows the recommended template from the authoring guide:
  - Overview/description (2-3 sentences)
  - "When to Use" section with specific use cases
  - "Prerequisites" section listing MCP servers and requirements
  - "Workflows" section with numbered steps
  - Example prompts/commands
  - Expected output descriptions
- [ ] **Accuracy** — descriptions match what the scenario actually provides
- [ ] **Completeness** — all agents, prompts, and key artifacts are documented
- [ ] **Quality** — well-written, free of typos, clear to a new user

### Step 7: Validate Artifacts

For each artifact in the scenario, verify naming conventions and structure:

#### Prompts (`.prompt.md`)
- [ ] Named `Octane.<Agent>.<Action>.prompt.md`
- [ ] **Agent name in filename matches a defined agent**: The `<Agent>` portion must correspond to:
  - A scenario-specific agent at `agents/<Agent>.agent.md`, OR
  - A shared agent in `scenario.json` → `shared_artifacts`
  - If no match, flag as **blocking**
- [ ] Contains YAML frontmatter with `agent` or `mode` field referencing the correct agent
  - The value must match the `name:` in the corresponding `.agent.md`
  - If `authors:` is used (deprecated), flag as **suggestion** to update
  - If `agent:`/`mode:` is missing entirely, flag as **suggestion**
- [ ] Has clear instruction sections
- [ ] Instructions are clear and unambiguous
- [ ] Specifies expected input and output

#### Agents (`.agent.md`)
- [ ] Named `<AgentName>.agent.md` (PascalCase)
- [ ] Defines clear role and expertise
- [ ] Lists responsibilities, guidelines, and available tools
- [ ] Specifies output format

#### Instructions (`.instructions.md`)
- [ ] Named `octane.<context>.instructions.md`
- [ ] Context-specific and actionable
- [ ] Clear do's and don'ts

#### Templates (`.md` in `templates/`)
- [ ] Named `octane.<output-type>.template.md`
- [ ] Clear section headings and descriptive placeholders
- [ ] Consistent formatting

#### Skills (`skills/`)
- [ ] Each skill has a `SKILL.md` with required YAML frontmatter (`name`, `description`)
- [ ] `name` matches directory name, 1-64 chars, lowercase/numbers/hyphens
- [ ] `description` is 1-1024 chars, explains what and when
- [ ] `SKILL.md` is under 500 lines
- [ ] Subdirectories (`scripts/`, `references/`, `assets/`) used appropriately
- [ ] **All file references in `SKILL.md` resolve to existing files**: Parse for Markdown links with relative paths. For each:
  1. Resolve the path relative to the skill directory
  2. Verify the target file exists in the PR
  3. If missing → **blocking**: "SKILL.md references `<path>` but this file does not exist"
- [ ] **No unreferenced files**: Flag files in `scripts/`, `references/`, `assets/` that aren't referenced by SKILL.md as a **suggestion** (potential dead resources)

#### Configuration (`config/octane.yaml`)
- [ ] Settings are namespaced under the scenario ID
- [ ] Sensible defaults provided
- [ ] Settings documented in README

#### Agent-Prompt Consistency (cross-artifact check)
- [ ] **Every scenario-defined agent is referenced by at least one prompt**: For each `.agent.md` in `agents/`:
  1. Extract the agent `name:` from frontmatter
  2. Check that at least one `.prompt.md` references it via `agent:`/`mode:` field or filename
  3. If unused → **suggestion**: "Agent is defined but not referenced by any prompt. Consider removing it or connecting it to prompts."
- [ ] **Every prompt references a defined agent**: For each `.prompt.md`:
  1. Extract `<Agent>` from the filename
  2. Verify a corresponding agent exists (scenario-specific or shared)
  3. If not → **blocking**: "Prompt references agent `<Agent>` but no corresponding agent file exists"

#### Model Recency (all `.prompt.md` and `.agent.md` files)
- [ ] **Check `model:` field for current model versions**: Compare against models used by reference scenarios from Step 3
  - If the new scenario uses an older model version, flag as **suggestion**: "Consider upgrading to `<current model>` — reference scenarios use this version"
  - This is a **suggestion**, not blocking — the author may have a valid reason

### Step 8: Validate docs/scenarios.md Update

- [ ] PR includes an update to `docs/scenarios.md`
- [ ] New scenario is numbered sequentially
- [ ] Entry includes link to scenario README
- [ ] All custom agents listed (scenario-specific and shared)
- [ ] Required MCP servers documented
- [ ] Sample prompts provided with descriptions

### Step 9: Cross-Reference with Existing Scenarios

- [ ] No ID conflicts with existing scenarios
- [ ] No duplicate functionality (check for overlapping tags and descriptions)
- [ ] Consistent quality level compared to existing scenarios
- [ ] Follows established patterns and conventions

#### Merge vs. Standalone Analysis

For each new scenario, actively evaluate whether it should be a **standalone scenario** or **merged into an existing one**:

1. **Load all existing `scenario.json` files** from `artifacts/scenarios/*/scenario.json`
2. **Compare tags, category, and description** against every existing scenario
3. **Flag potential overlap** if:
   - 3+ tags overlap with an existing scenario
   - Category matches AND description addresses a similar domain
   - The new scenario's workflows are a subset of an existing scenario's workflows
   - The new scenario could be added as an additional prompt/agent within an existing scenario
4. **Recommendation**: If overlap is found, explicitly state whether the scenario should:
   - Remain standalone (with justification — e.g., distinct workflow, different MCP dependencies)
   - Be merged into `<existing-scenario-id>` (with reasoning)
   - Be split — some artifacts merged, others kept as a new scenario
5. **Check for shared underlying tools/CLIs**: Search SKILL.md files, prompt instructions, and scripts for references to the same CLI tool or API (e.g., `skills-agent`). If multiple scenarios in the same PR wrap the same tool:
   - Flag as **strong merge candidate** — scenarios wrapping the same CLI should generally be one scenario with multiple prompts
   - Also check existing scenarios for the same tool
   - **Suggestion** unless 3+ scenarios in the same PR wrap the same tool → then **blocking**

This is a **suggestion-level finding** unless the overlap is so significant that two scenarios would confuse users.

### Step 10: Validate Preset Inclusion

Check whether the new scenario is appropriately included in presets (`artifacts/presets/*.json`):

1. **Load all preset files**: `all.json`, `minimal.json`, `full-dev-workflow.json`, `testing.json`, `docs.json`
2. **Check `all.json`**: Every scenario MUST be listed in `all.json`. If the new scenario is missing from `all.json`, this is a **blocking issue**.
3. **Check category-specific presets**: Based on the scenario's `category` and `tags`, evaluate whether it belongs in a themed preset:
   - `testing.json` — scenarios with category `quality` or `testing`, or tags like `testing`, `test-*`
   - `docs.json` — scenarios with category `documentation` or tags like `documentation`, `docs`
   - `full-dev-workflow.json` — scenarios that are part of an end-to-end development flow
   - `minimal.json` — foundational scenarios only (rarely should a new scenario be added here)
4. **Recommendation**: If the scenario fits a themed preset but isn't included, note it as a **suggestion**. If it's missing from `all.json`, mark as **blocking**.
5. **Consistency**: Verify the scenario ID in preset files matches the `id` in `scenario.json` exactly.

### Step 11: Determine Review Verdict

Based on findings, assign a verdict:

| Verdict | Criteria |
|---------|----------|
| **approve** | All required fields valid, README comprehensive, artifacts follow conventions, in correct presets, no blocking issues |
| **comment** | Minor suggestions only — naming nitpicks, documentation enhancements, optional fields missing, preset suggestions |
| **request-changes** | Missing required files, invalid `scenario.json` fields, broken references, missing `docs/scenarios.md` update, missing from `all.json` preset, significant quality gaps, significant unaddressed overlap with existing scenario |

### Step 12: Draft and Submit PR Review

Compose a review comment using the template below, then submit it:

```bash
gh pr review $ARGUMENTS --<verdict> --body-file /tmp/octane-scenario-review.md
```

Where `<verdict>` is `--approve`, `--comment`, or `--request-changes`.

## REVIEW COMMENT TEMPLATE

The review comment MUST follow this structure:

```markdown
## Scenario Review: `<scenario-name>`

**PR:** #<number>
**Verdict:** ✅ Approve | 💬 Comment | 🔄 Request Changes

---

### Summary

Brief 2-3 sentence summary of what the scenario does and overall quality assessment.

### What's Done Well

- Specific positive observations about the scenario
- Good practices followed
- Quality highlights

### Findings

#### Blocking Issues (must fix)

> Items that prevent approval. Each cites the relevant authoring guide section.

- **[scenario.json]** Issue description — _see Authoring Guide > Scenario Metadata Schema > Required Fields_
- **[README.md]** Issue description — _see Authoring Guide > Creating a Scenario > Step 4_

_(or "None" if no blocking issues)_

#### Suggestions (nice to have)

> Non-blocking improvements that would enhance the scenario.

- **[prompts]** Suggestion description
- **[agents]** Suggestion description

_(or "None" if no suggestions)_

### Checklist Summary

| Check | Status |
|-------|--------|
| `scenario.json` required fields | ✅ / ❌ |
| `scenario.json` optional fields | ✅ / ⚠️ / N/A |
| README structure and quality | ✅ / ❌ |
| Artifact naming conventions | ✅ / ❌ |
| Artifact content quality | ✅ / ⚠️ |
| `docs/scenarios.md` updated | ✅ / ❌ |
| Included in `all.json` preset | ✅ / ❌ |
| Correct themed presets | ✅ / ⚠️ / N/A |
| No conflicts with existing scenarios | ✅ / ❌ |
| No significant overlap / merge needed | ✅ / ⚠️ |
| Skills follow spec (if applicable) | ✅ / N/A |
| Agent-prompt cross-references | ✅ / ⚠️ |
| SKILL.md file references valid | ✅ / ❌ / N/A |
| Model versions current | ✅ / ⚠️ / N/A |
| `allowed_locations` explicitly set | ✅ / ❌ |
| Underlying tool overlap checked | ✅ / ⚠️ / N/A |

### Detailed Notes

Any additional context, questions for the author, or references to specific lines in the diff.
```

## IMPORTANT NOTES

- Always read the **actual files** from the PR branch, not just the diff, to get full context
- If the PR modifies multiple scenarios, review each one separately with its own section in the comment
- If `docs/scenarios.md` is not updated, this is always a **blocking issue**
- Be lenient on first-time contributors — provide guidance, not just criticism
- If unsure about a finding, mark it as a suggestion rather than a blocking issue 
