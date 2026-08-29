---
type: Playbook
title: Skill authoring best practices
description: >
  Actionable playbook for writing Agent Skills that trigger correctly and work
  across agents: description writing, naming, progressive disclosure discipline,
  degrees of freedom, bundling scripts, and eval-first testing.
tags:
  - agent-skills
  - authoring
  - best-practices
  - descriptions
  - progressive-disclosure
  - evals
sources:
  - resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
    title: "Anthropic: Skill authoring best practices"
  - resource: https://agentskills.io/specification
    title: Agent Skills Specification
  - resource: https://agentskills.io
    title: Agent Skills Overview (open standard)
  - resource: https://code.claude.com/docs/en/skills
    title: "Claude Code: Extend Claude with skills"
  - resource: https://github.com/anthropics/skills
    title: anthropics/skills (GitHub)
  - resource: https://github.com/agentskills/agentskills
    title: agentskills/agentskills (GitHub, skills-ref validator)
generated:
  by: claude-code/claude-fable-5
  at: "2026-08-29T10:44:56Z"
status: stable
---

# Skill authoring best practices

How to write skills that trigger at the right moments, stay cheap in context,
and behave predictably. Distilled from Anthropic's official authoring guidance
and the agentskills.io specification. Format rules (frontmatter fields, name
constraints, directory layout) live in
[/specs/agent-skills-spec.md](/specs/agent-skills-spec.md); this document is
about writing skills *well*. The operational step-by-step version of this
playbook is the checklist at
`skills/creating-skills/references/authoring-checklist.md` (in `skills/`,
outside this knowledge bundle).

## 1. Write the description for the router, not the reader

The description is the only thing the agent sees at discovery time (~100 tokens
per skill preloaded at startup), so it alone decides whether the skill fires.

Do:

- **Third person, always.** "Processes Excel files..." — never
  "I can help you...".
- **State both the capability AND the trigger.** Include what the skill does
  and a "Use when ..." clause naming the situations that should activate it.
- **Use concrete keywords** a user's request would actually contain (file
  extensions, tool names, verbs like "convert", "extract", "deploy") so
  description matching has something to latch onto.
- Stay within the spec limit: 1–1024 characters, non-empty.

Anti-patterns:

- Vague descriptions — "Helps with documents" tells the router nothing and
  will both under-trigger and mis-trigger.
- First person or marketing voice.
- Describing implementation details instead of triggers.
- XML tags in the description (rejected by Anthropic platform validation).

## 2. Name skills as gerunds or noun phrases

- Prefer **gerund form** (`processing-pdfs`) or **noun phrases**
  (`pdf-processing`).
- Avoid vague names: `helper`, `utils`, and similar say nothing about when to
  use the skill.
- Hard constraints (from the spec, enforced by validators): 1–64 chars,
  lowercase `a-z0-9-` only, no leading/trailing/consecutive hyphens, name MUST
  equal the parent directory name, and (Anthropic platform) no `anthropic` or
  `claude` reserved words, no XML tags.
- Repo-specific: the name must also be unique among skills already installed on
  the machine — see the naming rule in the repo-root `CLAUDE.md` and check
  `~/.claude/skills`, `~/.agents/skills` before choosing.

## 3. Respect progressive disclosure — budget every level

Skills load in three stages; write for the stage each piece of content lives in:

| Level | What loads | Budget |
|---|---|---|
| 1 Discovery | `name` + `description` only, for all skills, at startup | ~100 tokens |
| 2 Activation | Full SKILL.md body, when the task matches | < 5000 tokens, **< 500 lines** |
| 3 Execution | Bundled `references/`, `scripts/`, `assets/` files | loaded/run only as needed |

Discipline that follows from this:

- **Keep SKILL.md under 500 lines.** Anything longer belongs in `references/`
  and should be pulled in only when needed.
- **Keep file references one level deep from SKILL.md.** Don't make the agent
  chase reference-to-reference chains; link every needed file directly from the
  skill body, using relative paths with forward slashes.
- **Add a table of contents to any reference file over 100 lines** so the agent
  can navigate it without reading it whole.
- Reference MCP tools as `ServerName:tool_name` so the agent can resolve them
  unambiguously.

## 4. Match degrees of freedom to task fragility

Decide, per operation, how much latitude the agent should get:

- **Low freedom — exact scripts.** For fragile or error-prone operations, write
  "run exactly this command" and provide the script. Do not describe the steps
  and hope the agent reproduces them.
- **High freedom — heuristics.** Where many approaches work (analysis, writing,
  open-ended refactoring), give principles and judgment criteria instead of
  rigid procedures.

Supporting patterns from the official guidance, useful in either mode:

- **Workflow checklists** for multi-step procedures the agent must not skip.
- **Validator feedback loops**: have the agent run a validator and iterate on
  its output rather than eyeballing correctness.
- **Template pattern**: ship a template in `assets/` and instruct the agent to
  fill it, instead of describing the desired output shape in prose.
- **Input/output examples** to pin down formats that prose under-specifies.
- **Plan–validate–execute** for batch or destructive changes: produce the full
  plan, validate it, only then execute.

## 5. Bundle deterministic operations as scripts

If an operation is deterministic — same inputs, same required output — put it
in `scripts/` as executable code and have SKILL.md invoke it, rather than
writing instructions for the agent to re-derive the operation each time.
Scripts are Level-3 content: they cost no context until executed, they don't
drift, and they remove a whole class of transcription errors. (In this repo the
mandatory `## Updating` section already follows this rule by delegating to
`./scripts/update.sh <skill-name>` — see
[/skill-authoring/update-mechanism.md](/skill-authoring/update-mechanism.md).)

## 6. Build evals BEFORE writing extensive documentation

Official guidance is explicit: create evaluations first, then write the docs to
pass them. Concretely:

- Define test cases (the skill-creator tooling uses `evals/evals.json` test
  cases run in isolated subagents, with `grading.json` for scoring and
  `benchmark.json` for with-skill vs without-skill comparison).
- Benchmark **with and without the skill** — a skill that doesn't beat the
  no-skill baseline is overhead, not help.
- **Test across model sizes.** What works for Opus may need more detail for
  Haiku; verify with every model the skill targets before calling it done.

## 7. Test triggering, not just behavior

A skill that works when manually invoked but never fires on its own is broken.
Tune the description against two prompt sets:

- **Should-trigger prompts**: realistic user requests that must activate the
  skill.
- **Should-not-trigger prompts**: adjacent requests that must NOT activate it
  (the skill-creator tooling supports exactly this should/should-not
  description tuning).

If a should-trigger prompt misses, add its concrete keywords to the
description; if a should-not prompt fires, narrow the "Use when" clause.
Iterate until both sets pass.

## 8. Validate before shipping

- Run `skills-ref validate ./my-skill` (reference validator from
  `agentskills/agentskills`).
- In Claude Code, `claude plugin validate <dir>` (v2.1.233+) also validates
  packaged skills.
- For this repo, additionally walk the full operational checklist at
  `skills/creating-skills/references/authoring-checklist.md` — it layers the
  repo's registration, versioning, and knowledge-capture requirements on top of
  the practices above.

## Related

- [/specs/agent-skills-spec.md](/specs/agent-skills-spec.md) — format rules and
  frontmatter constraints these practices assume.
- [/skill-authoring/update-mechanism.md](/skill-authoring/update-mechanism.md) —
  how per-skill updates work in this repo.
- [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md) —
  where each agent discovers skills; relevant when testing triggering per agent.
