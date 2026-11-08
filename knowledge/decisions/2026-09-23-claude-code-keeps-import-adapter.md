---
type: Decision
title: init-project keeps Claude Code as an import-adapter after native AGENTS.md support
description: >-
  Claude Code 2.1.277 (published 2026-09-18) reads AGENTS.md natively, but
  only when no CLAUDE.md or CLAUDE.local.md exists from the working
  directory up, and only in sessions that fetch feature flags. On
  2026-09-23 the maintainer decided that init-project keeps generating a
  CLAUDE.md containing @AGENTS.md for Claude Code, with the facts and the
  rationale behind it rewritten, and that the matrix's Fallback rule
  prefers an import adapter whenever direct reading is conditional. The
  same session extended the matrix to fourteen agents (GitHub Copilot,
  Devin), which /log.md records.
tags:
  - init-project
  - claude-code
  - agents-md
  - adapter
  - decision
sources:
  - resource: https://code.claude.com/docs/en/memory
    title: "Claude Code docs — AGENTS.md section: when Claude reads it, Project instructions values, when support is unavailable, removing earlier workarounds, sharing one file (verified 2026-09-23)"
  - resource: https://code.claude.com/docs/en/env-vars
    title: "Claude Code docs — Features that need feature-flag fetching (AGENTS.md reading, /import); first session after an install or upgrade (verified 2026-09-23)"
  - resource: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
    title: "Claude Code changelog — 2.1.277 \"Added AGENTS.md support\" (verified 2026-09-23)"
  - resource: https://registry.npmjs.org/@anthropic-ai/claude-code
    title: "npm registry — 2.1.277 published 2026-09-18T16:22:26Z"
  - resource: ../../skills/init-project/references/agent-context-matrix.md
    title: The matrix the decision changes (Claude Code section, Fallback rule)
generated:
  by: claude-code/claude-opus-5-5
  at: "2026-09-23T06:51:10Z"
status: stable
---

# init-project keeps Claude Code as an import-adapter

## Context

Until v2.1.277 Claude Code read `CLAUDE.md` only, so `init-project` reached
it through an import adapter: a `CLAUDE.md` containing `@AGENTS.md`. From
v2.1.277 (npm publish 2026-09-18) the official memory docs say Claude reads
`AGENTS.md` itself — but under three conditions
([/specs/agents-md-standard.md](/specs/agents-md-standard.md) has the full
set):

1. **Only without a CLAUDE.md.** Under the default **Project instructions**
   value, any `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the
   working directory or above it makes Claude read the CLAUDE.md files
   instead. The docs warn that a `CLAUDE.local.md` alone "stops Claude from
   reading `AGENTS.md` for you".
2. **Only with feature-flag fetching.** Amazon Bedrock, Google Cloud's Agent
   Platform, Microsoft Foundry, Claude Platform on AWS, a Claude apps
   gateway, and the telemetry/traffic opt-out variables all turn it off; so
   does the first session after an install or upgrade, and a version below
   2.1.277.
3. **Only the user can change the setting.** It is honored in user,
   `--settings` and managed settings and ignored in project settings, so a
   generated repository cannot switch it for its users.

The docs keep the import as the documented pattern "when Claude isn't
reading your `AGENTS.md` directly" and state that "Keeping the import never
makes Claude read `AGENTS.md` twice, whichever **Project instructions** value
you use."

## Options considered

- **Keep `import-adapter`** — one ≤ 10-line `CLAUDE.md`; works in every
  session; no double read.
- **Switch to `native`** — no `CLAUDE.md`; but Claude silently runs without
  project instructions in every session where condition 2 fails, and the
  first time anyone adds a `CLAUDE.md` or `CLAUDE.local.md`.
- **Ask at run time** — one more interview question against the 25-question
  ceiling, to choose native only when every session qualifies.

## Decision

Kongsak chose **keep `import-adapter`** (2026-09-23). The matrix's Claude
Code section now records native reading, its conditions and the reason the
adapter stays. `## Fallback rule` step 1 now reads "in its default
configuration and in every session", and step 2 names the conditional case
explicitly — before this, a literal reading of step 1 classified both Claude
Code (conditional native reading) and Gemini CLI (a configurable file list)
as `native`, contradicting their own sections.

## Evidence from this machine

On 2026-09-23, Claude Code 2.1.280 on the maintainer's machine had
`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set in `~/.claude/settings.json` —
one of the variables that turn feature-flag fetching off. In a scratch
repository holding only an `AGENTS.md` with a codeword, `claude -p` with all
tools disabled answered that no project instructions mentioned one; after
adding a `CLAUDE.md` containing `@AGENTS.md`, the same prompt returned the
codeword. `/import` in the same environment reported "/import isn't
available in this environment." Switching to `native` would have left this
maintainer's own sessions without instructions.

## Consequences

- The adapter keeps its shape and `scripts/validate_output.py` is
  unchanged (check C8 still finds the import line). What changed is who
  else reads it: Cursor, GitHub Copilot and Devin load a root `CLAUDE.md`
  too, so `assets/adapter-template.md` now labels each note line with the
  agent's name, and when Claude Code and Copilot are both selected Copilot
  CLI expands the import and loads `AGENTS.md` twice — a cost of this
  decision found by the same day's research after the choice was made, and
  reported to the maintainer with the release rather than decided for them.
- `/init` now "offers to carry over" Codex or Gemini CLI configuration with
  `/import`, which appends a one-time copy of `AGENTS.md` to `CLAUDE.md`;
  beside the `@AGENTS.md` import that copy repeats the content and goes
  stale. The matrix records it so a run can put a "do not run `/import`
  here" note in the Claude Code adapter.
- SKILL.md no longer restates each agent's init-command behavior in
  `## Edge cases`; it points at the extract's **Native init command** field,
  because that restatement is exactly the kind of duplicate that went stale
  here.

## Revisit when

- Claude Code reads `AGENTS.md` without feature-flag gating, or lets a
  project setting choose `claude-md-and-agents-md` — then `native` would be
  as robust as the import and would save a file.
- The docs stop describing the import as never double-reading.
