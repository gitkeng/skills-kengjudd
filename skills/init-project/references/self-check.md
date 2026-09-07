# Self-check

The normative list of checks a run's output must pass, each with its pass
condition and the phase that runs it. `scripts/validate_output.py`
implements every check below in Python 3.9 standard library only; a harness
without `python3` walks this list by hand and says so in the report. The
script prints **failures only** — `<file>:<line>: <check>: <message>` — and
exits 0 (pass), 1 (at least one failure) or 2 (usage or I/O error). It never
touches the network. This file travels with the skill (including a bare
symlink install); it makes no this-repo `knowledge/` references.

## Contents

- [Invocation](#invocation)
- [Parser subset](#parser-subset)
- [Checks](#checks)
- [Fix loop](#fix-loop)
- [Skill self-check (--self)](#skill-self-check---self)

## Invocation

```bash
python3 <skill-dir>/scripts/validate_output.py <target-root> --kb <kb-folder> [--plan <kb>/init-project-run.md]
```

`<skill-dir>` is the directory containing this skill's SKILL.md as the
harness loaded it. With `--plan`, the script limits checks C2, C4 and C9 to
the paths listed in the record's `init_project_write_plan` (files this run
wrote); without it, every `.md` under `<kb>/` whose `generated.at` falls in
the last 24 hours is treated as this run's. Other modes:
`--detect <root>` (prints the Phase 0 state and signals, see
`run-lifecycle.md`), `--probe-folder <root> <name>` (case-insensitive
collision probe), `--self` (below).

## Parser subset

The script reads YAML frontmatter with its own reader, which accepts
exactly this subset — the shape everything this skill writes conforms to:

- top-level `key: scalar` (plain, single- or double-quoted; double quotes
  escape `\"` and `\\`), or a block scalar (`>-`, `>`, `|`, `|-`) whose
  indented lines are joined — the form the skill's own `description:`
  fields use;
- `key:` followed by a flat list of scalars (`- item`), where an item that
  starts with `"` is always a scalar and an item of the form `- k: v` opens
  a one-level mapping (further `  k2: v2` lines belong to it);
- `key:` followed by a one-level mapping (`  k: v`), including the inline
  form `key: { k: v, k2: v2 }`;
- no deeper nesting, no anchors or aliases.

A file outside the subset is reported once as
`skipped: outside parser subset` and is **not** a failure — user-authored
concepts may use any YAML the OKF spec allows.

## Checks

| ID | Scope | Pass condition | Runs at |
| --- | --- | --- | --- |
| C1 marker form | every context file the run wrote; `<kb>/index.md` | well-formed per `run-lifecycle.md` `## Marker forms` (one `init-project` pair, on their own lines, outside fences; Karpathy pair, if any, nested and single) | Phase 4 **Self-check**, Phase 5 after apply |
| C2 placeholders | every file the run wrote | no token from the **asset token list** survives (case-insensitive match is a failure; any other `<...>` is a warning); no `<!--` other than the four markers and the full-copy header `<!-- Generated from AGENTS.md — do not edit; regenerate instead -->` | Phase 3 **Index and log**, Phase 4 **Self-check** |
| C3 budget | `AGENTS.md`; each adapter | inside the `init-project` block: `AGENTS.md` ≤ 150 lines and ≤ 10,240 bytes; import-adapter ≤ 10 lines and ≤ 1,024 bytes; full-copy inherits `AGENTS.md`'s caps; both units reported | Phase 4 **Budget**, **Self-check**, Phase 5 |
| C4 frontmatter | every non-reserved `.md` the run wrote under `<kb>/` | parses in the subset; `type` non-empty and in the vocabulary (the four values, or the record's `init_project_type_vocabulary`); every `sources[]` entry has `resource`; `generated.by` and `generated.at` present, `at` ISO 8601 with offset; `status` in `draft|stable|deprecated` when present; `stale_after` ISO 8601 with offset when present; a concept tagged `technology` has `verified` and `stale_after`; run record implications: `init_project_completed` absent while `in-progress` and present when `complete`, `init_project_previous_started` present iff `init_project_run_number` > 1, no empty values | Phase 3 **Index and log**, Phase 5 |
| C5 links | `<kb>/index.md` bullets; path-valued `sources.resource` in files the run wrote | every relative path resolves from the file that carries it; bundle-relative `/` paths resolve from `<kb>/`; URLs are not fetched | Phase 3 **Index and log**, Phase 5 |
| C6 standing block | `AGENTS.md` | the current block from `references/standing-rules-history.md` (latest section) is a contiguous substring after line-ending normalization only | Phase 4 **Self-check** |
| C7 run record | `<kb>/init-project-run.md` | exists when `<kb>/` exists; keys listed in `okf-kb-guide.md` `## Skill-owned concepts`; values carrying user text are double-quoted strings; C4 implications hold | Phase 3, Phase 6 |
| C8 adapter import | each import-adapter | inside its block, the import line names a file that exists at the path the import syntax resolves to | Phase 4 **Self-check** |
| C9 index | `<kb>/index.md` | inside the block, no two bullets share a path; every bullet's target exists (a missing target is reported for the union ask, not silently dropped) | Phase 3 **Index and log**, Phase 6 |

**Asset token list.** C2's list is generated from the skill's own assets —
every `<...>` token found in `assets/` that is not an HTML comment — so it
cannot drift from the templates; `--self` prints it. Files instantiated
from `kb-maintenance.md` and `karpathy-guidelines.md` carry tokens only in
their frontmatter; their bodies are exempt from the `<...>` warning.

## Fix loop

Phase 4 **Self-check** runs the script once. Every failure is fixed and
the script re-run **at most twice more** in the run (an attempt bound per
run, not per failure). Anything still failing after the third run is
recorded as a gap in the report under **Self-check**, with the failure line
verbatim, and the run continues to Phase 5 — it never skips the review and
never loops further. Phase 5's apply step re-runs the script once after the
last accepted finding; a failure there is a regression the re-check fixes
directly.

## Skill self-check (--self)

`python3 scripts/validate_output.py --self` runs from the skill directory
and checks the skill, not a target. It is the maintainer's pre-release
gate and must exit 0 before `metadata.version` is bumped:

- every `## Section` anchor SKILL.md and the references cite — a markdown
  link to a reference file, or a reference file name in a code span, each
  followed by the section name in a code span — resolves to a heading in
  that file;
- every `Phase N **Label**` reference resolves to a labelled step in
  SKILL.md's Phase N;
- SKILL.md ≤ 440 lines and ≤ 25,600 bytes;
- every reference longer than 100 lines starts with `## Contents`;
- the latest section of `references/standing-rules-history.md` equals the
  template's `## Working rules` block byte for byte;
- every asset that carries `init_project_asset:` names the same version as
  SKILL.md's `metadata.version`;
- the asset token list can be generated and is printed.
