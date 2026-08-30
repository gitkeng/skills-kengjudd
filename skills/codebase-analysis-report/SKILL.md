---
name: codebase-analysis-report
description: Generate a portable, offline, accessible HTML report from a comprehensive-codebase-analysis v2 output tree. Use to visualize evidence-backed findings, business rules, components, test traceability, coverage, migration analysis, operations, and Mermaid diagrams without choosing a vendor platform.
metadata:
  version: "1.0.1"
  updated: "2026-08-30"
  upstream: "gitkeng/aws-kiro-atx-lab .kiro/skills/codebase-analysis-report @4320cce plus uncommitted working-tree changes as of 2026-08-29"
  requires: "comprehensive-codebase-analysis v2 output tree as input"
---

# Codebase analysis report

Turn a completed `comprehensive-codebase-analysis` v2 output tree into a single,
self-contained HTML report that works from `file://`, needs no network, and
faithfully preserves evidence, confidence, coverage, and traceability. The
deterministic renderer owns HTML structure, escaping, counts, theme behavior,
and validation. Do not infer new findings, severities, scores, costs, or
provider recommendations; the manifest is the source of truth.

Command and reference paths below are relative to this skill's own directory.
When the skill is installed as a symlink, resolve it first
(`readlink -f <this-skill-dir>`) and prefix every `scripts/` and `references/`
path with the resolved directory.

## Hard rules

- Read only a user-selected analysis root. Write only under a separately
  resolved output root.
- Never execute analyzed code, install packages, use a CDN, or fetch remotely.
- Treat all Markdown/JSON as untrusted: escape everything, sanitize links and
  images, render Mermaid strictly with an always-visible source fallback.
- The skill's own UI, defaults, and wording stay vendor-neutral. Provider names
  appear only when present in the source as observed evidence.
- Publish only output that passed validation. Never silently overwrite.

## Workflow (gates)

Gates 2–6 are enforced by `scripts/render_report.py`,
`scripts/validate_report.py`, and `scripts/test_report.py`: run the commands
rather than reading source documents into context. Read source files only to adjudicate a reported
validation failure.

1. **Resolve roots.** If the analysis root or the output root is absent, ask
   the user; never infer the analysis root from the working directory. State
   each resolved path before writing. If the output root already exists, stop
   and ask the user to approve replacement; only after the user approves, re-run
   with `--replace` (prior output is backed up and restored on failure).
   → load `references/input-contract.md`.
2. **Preflight the source.** Require `manifest.json` and `progress.json` at
   schema `2.0`; require completion unless the user approves an incomplete run
   (which shows a persistent banner). Fail closed on unknown versions/keys.
   → `references/input-contract.md`.
3. **Read declared inputs** with strict path containment (reject `..`, absolute
   paths, symlink escapes, non-regular files; rules in
   `references/input-contract.md` § Path safety). Render Markdown only for `.md`
   documents; expose `manifest.json`/`progress.json` in About.
   → `references/input-contract.md`, `references/report-content.md`.
4. **Render** into a unique temp sibling of the destination.
   → `references/report-content.md`; load `references/ux-accessibility.md` and
   `references/mermaid-security.md` only when investigating theme,
   accessibility, or diagram behavior.
5. **Validate** the temp output and run the self-test suite
   (`test_report.py --fixture <analysis-root>`; any completed v2 output tree is
   a valid fixture — typically the analysis root being reported. For a
   user-approved incomplete source, pass another completed v2 tree if one is
   available; otherwise skip the suite, rely on `validate_report.py`, and say
   so in the final report). On any
   validation or test failure, do not publish; report the failing check and the
   temp path to the user.
   → `references/validation.md`.
6. **Publish** by rename. When replacing, back up the prior output, move the
   validated temp into place, and restore the backup if publication fails.
   → `references/validation.md`.
7. **Report** the exact output path, source status, counts, validation result,
   and limitations.

## Commands

```sh
# Render (announce the resolved output path before running):
python3 scripts/render_report.py --source <analysis-root> --output <report-dir> [--replace] [--allow-incomplete]

# Validate a generated report independently:
python3 scripts/validate_report.py <report-dir>

# Run the full self-test suite (uses temp dirs only; the fixture is any
# completed v2 output tree, typically the analysis root being reported):
python3 scripts/test_report.py --fixture <v2-output-tree>
```

Use `--generated-at <ISO8601>` only for reproducible fixtures.

## Load references on demand

Keep context lean. Read a reference only when its phase applies:

- `references/input-contract.md` — normative field-to-view map and enums (the
  single contract shared by workflow and scripts).
- `references/report-content.md` — information architecture, Markdown subset,
  link/image safety, and section derivation.
- `references/ux-accessibility.md` — theme model, keyboard/ARIA contract, and
  print/reduced-motion rules.
- `references/mermaid-security.md` — accepted diagram types, strict rendering,
  and source-only fallback policy.
- `references/validation.md` — report-manifest integrity, publication
  semantics, and the test matrix.

## Shipped assets

`assets/report.css` and `assets/report.js` are the neutral component design,
inlined into `index.html` at render time. `assets/mermaid.min.js` is a local,
version-pinned Mermaid v11 runtime (SHA-256 recorded in the scripts and tests).
`assets/report-manifest.schema.json` defines the report integrity manifest.

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh codebase-analysis-report
```

If this skill directory is a symlink (the normal install), resolve it with
`readlink -f <this-skill-dir>`; the repo root is two directories above the
resolved path.

The script fetches `origin/main`, compares this skill's `metadata.version`,
shows this skill's pending commits, and pulls after confirmation.

**Claude Code plugin install** — the plugin cache has no `.git`, so
`update.sh` cannot run there:

```bash
claude plugin update kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
