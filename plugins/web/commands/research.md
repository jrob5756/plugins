---
description: Research a question by dispatching multiple focused subagents in parallel, then synthesizing their findings into a single response.
---

## PRIMARY DIRECTIVE

Deeply research the user's request by dispatching 3–5 parallel subagents, each focused on a distinct research angle, then synthesize their findings into a single authoritative response.

<workflow>

### Step 1: Understand the Request

Before doing any research, analyze the user's request:

- Restate the core question or goal in one sentence.
- Identify the **key dimensions** that need to be researched (e.g., concepts, comparisons, best practices, current state, examples, trade-offs, caveats).
- Decide on **3–5 focused research angles** — one per subagent — that together will give complete coverage. Each angle must be meaningfully different so subagents do not duplicate work.

Present this plan as a short bulleted list so the user can see what will be researched before work begins.

### Step 2: Parallel Research

Use between **3 and 5 subagents** depending on the complexity of the topic:
- Simple, focused questions → 3 subagents
- Broad, multi-faceted topics → 5 subagents

<use_parallel_tool_calls>
Dispatch all subagents simultaneously in a single batch — research subagents have no dependencies on each other. Make all independent runSubagent calls in parallel rather than sequentially.
</use_parallel_tool_calls>

Each subagent receives a focused research question derived from Step 1. Use the `web-searcher` agent for each subagent call, with the following prompt template:

<subagent_prompt_template>
You are a focused research assistant. Your only job is to answer the following research question as accurately and concisely as possible.

<research_question>
[angle]
</research_question>

<instructions>
- Search the web using multiple engines for broad coverage.
- Fetch full content from the most promising results using WebFetch.
- Return factual findings relevant to the question, with inline source URLs for every key claim.
- Prefer official sources (documentation, official blogs) over community content.
- Note content freshness — mention if information may be outdated.
- If initial results aren't relevant, try alternative keywords or phrasings.
- Focus on reporting what the sources say; state uncertainty explicitly when information is unavailable or conflicting.
</instructions>
</subagent_prompt_template>

### Step 3: Synthesize and Respond

After all subagents complete, combine their findings into a single, well-structured response:

1. **Reconcile conflicts** — if subagents return contradictory information, note the discrepancy and explain which source is more authoritative and why.
2. **Eliminate redundancy** — merge overlapping findings into unified statements.
3. **Structure clearly** — use headings, bullet points, tables, or code blocks as appropriate for the topic.
4. **Cite sources** — every key claim must link to a source URL returned by a subagent.
5. **Surface gaps** — if research was inconclusive on any angle, state that explicitly rather than speculating.

</workflow>

<constraints>

- Ground every claim in subagent-returned evidence; explicitly state when information is unavailable or inconclusive.
- Dispatch all subagents in parallel — sequential dispatch defeats the purpose of this workflow.
- Present only synthesized findings in the final response; omit raw subagent output.
- Keep the final response focused on the user's question; include tangential findings only when directly relevant.
- When Microsoft or Azure documentation is relevant, prefer `ms-learn/*` tools over general web search.

</constraints>

<research_angle_guide>

Use these categories as inspiration when decomposing a topic into subagent assignments:

| Angle | Description |
|-------|-------------|
| Conceptual | What is it? Core definitions, history, how it works. |
| Comparative | How does it compare to alternatives? Trade-offs? |
| Best Practices | Official recommendations, community conventions, pitfalls. |
| Current State | Latest version, recent changes, known issues, roadmap. |
| Examples | Real-world usage examples, tutorials, code samples. |
| Caveats | Limitations, edge cases, gotchas, security concerns. |

Choose the angles most relevant to the user's specific request.

</research_angle_guide>

