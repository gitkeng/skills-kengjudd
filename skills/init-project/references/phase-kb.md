# Phase 3 — Create the KB (draft): the five steps in full

Read this when Phase 3 starts; it carries the full text of steps 1–5, which
SKILL.md summarises in one line each. The bold labels are the ones other
references refer to.

## Contents

- [1 Existing bundle](#1-existing-bundle)
- [2 Write plan](#2-write-plan)
- [3 Skeleton, run record, gap flush](#3-skeleton-run-record-gap-flush)
- [4 Concepts](#4-concepts)
- [5 Index and log](#5-index-and-log)

## 1 Existing bundle

If `<kb>/` exists and is an OKF bundle, go through
[okf-kb-guide.md](okf-kb-guide.md) `## Migration`
(size, file-by-file changes, one approval) and its `## Type vocabulary`
question when the bundle has its own vocabulary. Legacy folders come
from the interview, never from encountering a folder here.

## 2 Write plan

Show the one table of every path Phases 3–4 will touch,
per [run-lifecycle.md](run-lifecycle.md)
`## Write plan` — action, baseline, rollback per row — and get one
answer. Merge / skip / replace, marked files, skill-owned files and
additive writes are decided there per
[context-file-guidelines.md](context-file-guidelines.md)
`## Merge semantics`. Nothing is written before this answer; nothing off
the plan is ever written.

## 3 Skeleton, run record, gap flush

Create `<kb>/` if needed;
instantiate `assets/kb-skeleton/index.md` and `log.md` **only where
absent** (never overwrite an existing index or log — add to it);
instantiate `assets/kb-skeleton/kb-maintenance.md` every run and
`karpathy-guidelines.md` on opt-in; write `<kb>/init-project-run.md`
with every answer and the confirmed plan
(`## Run record`; shape in the OKF guide's `## Skill-owned concepts`);
and flush the running gap list as `gap:` bullets under today's heading
using that section's **Log bullet grammar**. Replace every `<...>`
token in every file you instantiate; the `init-project:*` markers are not
placeholders.

## 4 Concepts

Write every concept the run owes per
[okf-kb-guide.md](okf-kb-guide.md)
`## Concept kinds` — technology (from the extracts), agent, domain and
seed source, external KB, legacy folder, process, constraints, and one
`decision-*` concept per interview answer that overrides a default — each
with `status: draft`, the frontmatter of `## Creating the bundle` step 4,
and only the four `type:` values of `## Type vocabulary`.

## 5 Index and log

Add one bullet per concept inside the index's marker
block per `## Creating the bundle` step 5 (on a re-run, the **union**),
write the seeding bullet, then run `scripts/validate_output.py` checks
C2, C4, C5 and C9 ([self-check.md](self-check.md)).
