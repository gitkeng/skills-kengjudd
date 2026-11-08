# Phase 4 — Generate context files: the seven steps in full

Read this when Phase 4 starts; it carries the full text of steps 1–7, which
SKILL.md summarises in one line each. The bold labels are the ones
other references refer to.

## Contents

- [1 Baseline and block diff](#1-baseline-and-block-diff)
- [2 Canonical file](#2-canonical-file)
- [3 Markers](#3-markers)
- [4 Karpathy block](#4-karpathy-block)
- [5 Adapters](#5-adapters)
- [6 Budget](#6-budget)
- [7 Self-check](#7-self-check)

## 1 Baseline and block diff

Re-read every context-file target on the
plan immediately before writing. For every **marked** file compute the
in-block lines the regenerated block would drop, compare the standing
block against
[standing-rules-history.md](standing-rules-history.md),
and put the whole set to the user as **one** confirmation per
`## Merge semantics` **Marked files**. A marker or log entry this run did
not write, found now, is the *foreign* state: stop. Never write a
context file before this answer.

## 2 Canonical file

Instantiate `assets/agents-md-template.md` as
`AGENTS.md` at the root. Fill `## Project` from the interview (and the
light analysis of `## Edge cases` for an existing codebase);
`## Commands` from the commands confirmed under `coding/commands` only,
deleting lines the project has no command for and the whole section
when it has none; `## Project knowledge base` with `<kb>`, plus one line
per legacy folder linking its concept; `## Agent notes` per **Adapters**.
Copy the template's `## Working rules` block unchanged — the single
source of the standing-rules block,
[context-file-guidelines.md](context-file-guidelines.md)
`## Standing rules block` — and add the facts each preset's **Output
delta** calls for, the convention-document pointers, and any
`## Scaffolder collisions` bullet **below the verbatim block, as
additional bullets, never interleaved with it**.

## 3 Markers

Everything this skill writes into `AGENTS.md` and every
adapter sits between `<!-- init-project:start -->` and
`<!-- init-project:end -->`, on a fresh run exactly as on a merge; only
the file's H1 stays outside. Keep the template's pair, add no second
pair, let `karpathy:*` nest inside
([run-lifecycle.md](run-lifecycle.md)
`## Marker forms`). This is what lets a re-run regenerate instead of
duplicate.

## 4 Karpathy block

Opted in: keep the block between its markers. Opted
out, or never asked because no code-writing task type was selected:
delete the whole marked block, markers included.

## 5 Adapters

For each selected agent take its **Adapter rule** from the
Phase 2 extract. Before writing for a `native` agent, check the root for
files that shadow or duplicate `AGENTS.md` using that agent's
**Context file(s) & precedence** field (Zed's first-match-wins list,
Goose's `.goosehints`, the `GEMINI.md` Antigravity also reads); every hit
is a row on the write plan, never a silent write.
- `native` — no adapter file. Record the agent in `## Agent notes`.
- `import-adapter` — instantiate `assets/adapter-template.md` as that
  agent's own file: the import line verbatim from the extract, at most
  two notes true of that agent and false of the others, the notice line
  on a non-English run. Do not restate that `AGENTS.md` is canonical.
- `full-copy` — that agent's own file as a full copy of `AGENTS.md`'s
  content with the provenance header from `## Fallback rule`; flagged in
  the report.

`## Agent notes` carries one bullet per selected agent, an imperative
constraint for the agents that read the file later; for a `native` agent
it names the single quirk from the closed list in the template's
comment, with any init command copied **verbatim** from the extract's
**Native init command** field, never paraphrased. At most one further
bullet may carry a cross-agent warning; anything else belongs in `<kb>/`.

## 6 Budget

Respect
[context-file-guidelines.md](context-file-guidelines.md)
`## Content budget` in both units (a full-copy adapter inherits
`AGENTS.md`'s caps). Over budget: never trim a fact silently — follow
that section's **cut order**, moving detail into `<kb>/` as a concept of
`## Concept kinds` (a delta row on the plan; frontmatter, index bullet,
log bullet), deciding what goes where with `## Context vs KB`. Re-check
after every edit.

## 7 Self-check

Run `scripts/validate_output.py <root> --kb <kb> --plan
<kb>/init-project-run.md` ([self-check.md](self-check.md))
— markers, placeholders, budget, frontmatter, links, standing block,
adapter import, index. Fix and re-run within its `## Fix loop` bound;
report what survives as a gap. Without `python3`, walk the checklist by
hand and say so.
