---
type: Playbook
title: Parallelising a phase-based skill — late alias minting with placeholders
description: >
  How to let the phases of a long, phase-structured skill (codebase-analysis
  is the example) run as concurrent subagents without breaking stable
  identifiers: subagents register entries by canonical key and write
  {{alias:<key>}} placeholders, one deterministic script mints aliases and
  substitutes them at synthesis, fragments live in a .work/ directory the
  validator never sees, and the orchestrator alone writes the checkpoint
  file. Also the trade-off (tokens for wall-clock) and what is still
  untested.
tags:
  - skill-authoring
  - parallelism
  - subagents
  - codebase-analysis
  - identifiers
sources:
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/codebase-analysis/references/parallel-phases.md
    title: The protocol as shipped in codebase-analysis 2.1.0
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/codebase-analysis/scripts/resolve_aliases.py
    title: The resolver (tested on synthetic fragments 2026-11-08)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/codebase-analysis/references/evidence-and-identity.md
    title: The sequential alias rule the resolver reproduces
  - resource: https://code.claude.com/docs/en/skills
    title: Claude Code docs — Skills (context: fork is Claude-Code-only, so the portable form is prose plus a script)
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-11-08T07:18:00Z"
status: stable
---

# Parallelising a phase-based skill

## Contents

- [The problem](#the-problem)
- [The pattern](#the-pattern)
- [Why not the obvious alternatives](#why-not-the-obvious-alternatives)
- [What it costs](#what-it-costs)
- [What is verified and what is not](#what-is-verified-and-what-is-not)

## The problem

`codebase-analysis` runs eight phases in one context; Phases 2–7 each load a
different reference set and write disjoint documents, so they look
parallelisable. Two things stop a naive fan-out: the phases **mint stable
aliases** (`BR-NNN`, `TD-NNN`, `V-NNN`, `TC-NNN`, `CMP-NNN`) by taking the
next free number, and they **checkpoint** one shared `progress.json`. Two
subagents minting concurrently produce the same `TD-007`; two writing the
checkpoint race.

## The pattern

1. **Group by dependency, not by phase number.** Phases 2–5 only need Phase
   1's inventory; Phases 6–7 need the documents of 2–5. Two groups, each a
   concurrent dispatch, the orchestrator waits between them.
2. **Subagents register, never mint.** Each writes
   `.work/entries-<phase>.json` with its entries keyed by the canonical key
   the skill already defines, `alias` omitted, and writes
   `{{alias:<canonical-key>}}` wherever prose or a field needs an alias.
3. **One deterministic resolver at synthesis.** `resolve_aliases.py` merges
   fragments (a key registered twice with different content is an error,
   not a silent pick), reuses the prior manifest's aliases for matching keys,
   mints the rest in sorted-key order (so re-running is reproducible),
   substitutes every placeholder in every Markdown file, computes delta and
   severity counts, and exits 1 on any placeholder whose key nobody
   registered — a dangling reference cannot reach the output.
4. **Orchestrator-only side effects.** Only the orchestrator writes
   `progress.json` (after each group), `manifest.json`, `README.md`, and
   deletes `.work/` before the validator runs, because the validator
   rejects unexpected files.
5. **Portable phrasing.** The mode is prose ("when your harness can spawn
   concurrent subagents…") plus a script, not Claude Code's `context: fork`
   frontmatter, so the skill stays within the six spec fields.

## Why not the obvious alternatives

- *Alias ranges per subagent* (Phase 4 gets TD-001…, Phase 5 TD-501…) break
  the skill's own rule "never renumber gaps / next unused number" and make
  the prior-manifest match meaningless.
- *Letting one registry belong to one phase* fails in practice: debt
  findings (`td`) arise in both the reference-analysis and the debt
  phases.
- *Minting in the orchestrator and handing numbers out* would need a
  round-trip per entry while subagents are still discovering entries.

## What it costs

Each subagent re-reads the focus files, so parallel mode spends roughly
one more full read of the repository per group member in exchange for
wall-clock time. The skill says so and keeps sequential mode the default
for small repositories or when a human wants to watch alias matches.

## What is verified and what is not

- Verified (2026-11-08): the resolver on synthetic fragments — alias reuse
  across a prior manifest, minting above the prior maximum, placeholder
  substitution in documents and in `source_refs` / `traceability`, delta
  with a regressed severity, exit 1 on an unregistered key, exit 2 on a
  conflicting duplicate.
- Verified (2026-11-08, later the same day): one end-to-end parallel run
  through `claude plugin eval` on a synthetic 14-file service — 6 subagents,
  resolver and validator ran, `.work/` removed, no placeholder left, 8/8
  graders, 20 minutes, ≈$8.78 (`evals/codebase-analysis-parallel-smoke`).
  It exposed a validator parser gap (block-scalar description) and a delta
  scope bug in the resolver, both fixed in 2.1.1, and taught two protocol
  rules: assign registry ownership per subagent before dispatch, and let the
  orchestrator write a document a subagent was refused.
- **Still open:** a run on a real repository with a prior manifest (alias
  reuse across runs has only the synthetic resolver test), and the token
  cost of parallel versus sequential on the same repository.
