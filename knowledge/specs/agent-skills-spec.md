---
type: Spec Summary
title: Agent Skills specification
description: >
  Summary of the agentskills.io Agent Skills open standard: skill directory
  layout, the exact six SKILL.md frontmatter fields and their constraints,
  the portability rule this repo enforces, three-level progressive disclosure
  with token budgets, validation tooling, and the Claude-Code-only extension
  fields that portable skills must not use.
tags:
  - agent-skills
  - skill-md
  - frontmatter
  - portability
  - progressive-disclosure
  - validation
sources:
  - resource: https://agentskills.io
    title: Agent Skills Overview (open standard)
  - resource: https://agentskills.io/specification
    title: Agent Skills Specification
  - resource: https://code.claude.com/docs/en/skills
    title: "Claude Code: Extend Claude with skills"
  - resource: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
    title: "Anthropic: Skill authoring best practices"
  - resource: https://github.com/agentskills/agentskills
    title: agentskills/agentskills (GitHub, skills-ref validator)
  - resource: https://github.com/anthropics/skills
    title: anthropics/skills (GitHub)
  - resource: https://opencode.ai/docs/skills/
    title: opencode Skills docs — spec-fields-only frontmatter
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:44:54Z
status: stable
---

# Agent Skills specification

Agent Skills is an open format for packaging procedural knowledge for AI
agents. Originally developed by Anthropic, it is now maintained as an open
standard at [agentskills.io](https://agentskills.io) (GitHub:
`agentskills/agentskills`). The format is adopted by 25+ agents, including
Claude Code, OpenAI Codex/ChatGPT, Cursor, opencode, Gemini CLI, Amp, Goose,
Kiro, Zed, and Kimi CLI. Per-agent discovery paths and quirks are catalogued
in [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md).

## Skill anatomy

A skill is a **directory** containing a required `SKILL.md` (YAML frontmatter
+ Markdown body) plus optional conventional subdirectories:

| Path | Purpose |
|---|---|
| `SKILL.md` | Required. Frontmatter + instructions body. |
| `scripts/` | Executable code the agent can run. |
| `references/` | Documentation loaded on demand. |
| `assets/` | Templates, images, data files. |

Any additional files or directories are allowed. File references from
SKILL.md should stay **one level deep** and use relative paths with forward
slashes.

## The six frontmatter fields (exact and exhaustive)

The spec defines **exactly six** fields. No others exist in the standard.

| Field | Required | Constraints |
|---|---|---|
| `name` | yes | 1–64 chars; only lowercase `a-z`, `0-9`, hyphens; no leading/trailing hyphen; no consecutive hyphens (`--`); **must match the parent directory name**. |
| `description` | yes | 1–1024 chars, non-empty; states what the skill does AND when to use it, with specific trigger keywords; written in third person. |
| `license` | no | License identifier/text. |
| `compatibility` | no | 1–500 chars if present; most skills should omit it. |
| `metadata` | no | Map of **string keys to string values** (this repo stores `version` and `updated` here per CLAUDE.md rule 3). |
| `allowed-tools` | no | **Experimental.** Space-separated string, e.g. `Bash(git:*) Bash(jq:*) Read`. Per-agent enforcement semantics (grant vs restriction) are not standardized. |

Anthropic's platform adds validation on top of the spec: `name` and
`description` cannot contain XML tags, and `name` cannot contain the
reserved words `anthropic` or `claude`.

## Portability rule (why this repo forbids extra keys)

**claude.ai skill uploads, the Skills API, and `package_skill.py` accept
ONLY the six spec fields.** Any other frontmatter key fails hard with an
`Unexpected key(s) in SKILL.md frontmatter` error. Frontmatter restricted to
the six spec fields loads unchanged in Claude Code, so there is no downside
to staying spec-pure — this is CLAUDE.md binding rule 6 ("Portability
first"). Note that opencode likewise recognizes only the spec fields.

## Claude Code extension fields — forbidden in portable skills

Claude Code extends the standard with many extra frontmatter fields:
`when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`,
`user-invocable`, `allowed-tools`/`disallowed-tools`, `model`, `effort`,
`context` (fork), `agent`, `background`, `hooks`, `paths`, `shell`. In
Claude Code all frontmatter fields are optional and `description` is only
"recommended".

Claude Code also adds body-level features the spec does not define:
argument substitution (`$ARGUMENTS`, `$ARGUMENTS[N]`/`$N`, named `$name`
args), path variables (`${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`,
`${CLAUDE_SESSION_ID}`, `${CLAUDE_PLUGIN_ROOT}`), and dynamic context
injection (`` !`command` `` lines and ```` ```! ```` blocks, executed before
Claude sees the content; a failed command aborts the invocation).

Skills in this repo must NOT use any of these: the extension frontmatter
keys break claude.ai/Skills API packaging outright (hard fail above), and
the body features silently degrade to literal text on every non-Claude
agent. Keep SKILL.md bodies plain Markdown and frontmatter to the six spec
fields.

## Progressive disclosure (3 levels)

Agents load skills in three stages to conserve context:

1. **Discovery** — only `name` + `description` (~100 tokens per skill) are
   preloaded at startup for all installed skills. This is why the
   description must carry both capability and trigger conditions.
2. **Activation** — the full SKILL.md body is loaded when a task matches.
   Recommended budget: **< 5,000 tokens / < 500 lines**.
3. **Execution** — bundled files (`scripts/`, `references/`, `assets/`) are
   loaded or executed only as needed, never eagerly.

Practical consequences: keep SKILL.md under 500 lines; move detail into
`references/` files (give files > 100 lines a table of contents); keep
references one level deep so the agent can find them from SKILL.md.
Authoring guidance that builds on this lives in
[/skill-authoring/best-practices.md](/skill-authoring/best-practices.md).

## Validation tooling

- `skills-ref validate ./my-skill` — the reference validator from the
  `agentskills/agentskills` repo (skills-ref reference library). Validates
  against the open spec; use this as the portability gate.
- `claude plugin validate <dir>` — Claude Code's own validator
  (v2.1.233+); useful when packaging this repo as a plugin (see
  [/specs/claude-code-plugins.md](/specs/claude-code-plugins.md)).

## Authoring guidance from the spec ecosystem (summary)

Official best practices (platform.claude.com):

- Descriptions in **third person** ("Processes Excel files…", never "I can
  help you…"); state capability AND triggers ("Use when…"); avoid vague
  descriptions ("Helps with documents").
- Names: prefer gerund form (`processing-pdfs`) or noun phrases
  (`pdf-processing`); avoid vague names (`helper`, `utils`).
- Match **degrees of freedom** to task fragility: low freedom (exact
  scripts, "run exactly this command") for fragile/error-prone operations;
  high freedom (heuristics) where many approaches work.
- Bundle deterministic operations as executable scripts rather than prose
  instructions; build evals **before** writing extensive documentation;
  test with all target models (what works for Opus may need more detail
  for Haiku).

## Open questions

- `allowed-tools` is marked experimental; per-agent enforcement semantics
  are not standardized.
- The spec defines only the skill directory format, **not** discovery
  locations — user-scope path conventions differ per agent
  (`~/.agents/skills` vs `~/.config/agents/skills`); see
  [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md).
