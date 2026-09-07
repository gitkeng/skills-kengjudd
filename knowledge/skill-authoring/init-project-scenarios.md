---
type: Playbook
title: init-project release scenarios and pre-release gate
description: >-
  The closed set of end-to-end scenarios a release of the init-project skill
  is walked through, what each one must produce, and the maintainer gate
  (`validate_output.py --self`) that must exit 0 before the skill version is
  bumped.
tags:
  - skills
  - authoring
  - testing
  - init-project
  - playbook
sources:
  - resource: ../../skills/init-project/SKILL.md
    title: The skill under test (init-project 1.1.0, repo v0.13.0)
  - resource: ../../skills/init-project/references/self-check.md
    title: The checks and the --self gate the scenarios rely on
  - resource: ../../skills/init-project/references/run-lifecycle.md
    title: Phase 0 states, headless gate and rollback the scenarios exercise
  - resource: ../../docs/init-project-expert-review-2026-09-06.md
    title: Proposal R-34 of the 2026-09-06 expert review, which asked for this file
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-09-07T04:30:00Z"
status: stable
---

# init-project release scenarios and pre-release gate

Two end-to-end runs and one review panel hardened init-project 1.0.0
([/skill-authoring/init-project-lessons.md](/skill-authoring/init-project-lessons.md)
§5–6), but none of those runs was written down as something that can be
repeated. This file is the repeatable form. A scenario is an **input** plus
the **expected artifacts**, checked with the skill's own validator rather
than by reading; a release runs the gate and the scenarios its change class
requires, and records the result in [/log.md](/log.md).

## The gate

From the repository root:

```bash
python3 skills/init-project/scripts/validate_output.py --self
```

Exit 0 is required before `metadata.version` moves. It checks that every
`## Section` anchor and every `Phase N **Label**` reference resolves, that
SKILL.md is within 440 lines and 25,600 bytes, that every reference over
100 lines has a `## Contents`, that the latest section of
`standing-rules-history.md` equals the template's block byte for byte, and
that every asset's `init_project_asset` version equals the skill version.
It also prints the placeholder token list the validator derives from the
assets — read it once per release to confirm no authoring comment leaked a
token.

## Scenarios

Each scenario is run on Claude Code (the harness the skill is developed
on); a run on another harness is recorded as a gap, not assumed. The
validator command after each run is
`python3 <skill>/scripts/validate_output.py <root> --kb <kb> --plan <kb>/init-project-run.md`
and must exit 0 unless the scenario says otherwise.

| # | Input | Expected artifacts | Required when |
| --- | --- | --- | --- |
| A | empty directory; task types `coding` + `frontend`; two agents (Claude Code, Codex); Thai as the generated-files language | `AGENTS.md` with a well-formed pair, Thai prose, the English standing and Karpathy blocks each preceded by a Thai notice line, byte cap respected; `CLAUDE.md` from the adapter template; `<kb>/` with `index.md`, `log.md`, `kb-maintenance.md`, `karpathy-guidelines.md`, `init-project-run.md` (`status: complete`), one concept per technology in scope with `verified`/`stale_after`; validator exit 0 | every release |
| B | existing codebase with an unmarked `AGENTS.md`, a `docs/` folder and a `.env` | the write plan lists `AGENTS.md` as merge/skip/replace with a rollback and `docs/` came from the legacy-folders question; on merge the old content sits outside the pair untouched; a `legacy-docs` concept; no value from `.env` anywhere under `<kb>/`; validator exit 0 | a release touching merge semantics, the write plan, rollback or iron rule 5 |
| C | the output of A, run again after changing one answer | Phase 0 reports *re-run* and lists the recorded answers by key; only the changed answer and open gaps are asked; the index block is a union (no duplicate bullet, earlier bullets kept); the block diff shows nothing dropped; `init_project_run_number: 2` with `init_project_previous_started`; validator exit 0 | every release |
| D | output written by skill 1.0.0 (produce it from `git show baae7e5:skills/init-project/…` into a scratch skill directory and run scenario A with it) | Phase 0 reports *re-run* from the 1.0.0 log bullet with no record; the standing block matches history section `1.0.0` and is regenerated; the report says "standing rules updated from 1.0.0 to 1.1.0"; a record is created; validator exit 0 | a release changing the standing-rules block, markers or detection |
| E | `claude -p "init this project for Claude Code"` in an empty directory | **zero** files created (`git status` or `ls -A` unchanged); the last message is either the Phase 1 topic list with "the run stopped because it could not ask", or the target-root consent ask left unanswered — the model cannot see the `-p` flag, so the ask itself is the probe and the turn ends there | every release |

## Recording a run

Add one bullet per scenario under the release's date in [/log.md](/log.md):
scenario letter, harness, validator exit code, and any gap. A scenario that
could not be run is recorded as *not run* with the reason — it is never
reported as passed by reading the files.

## Related

- [/skill-authoring/init-project-lessons.md](/skill-authoring/init-project-lessons.md)
  — why the runs exist and what they caught.
- [/skill-authoring/validating-generated-artifacts.md](/skill-authoring/validating-generated-artifacts.md)
  — calibrating a checker against the real consumer.
