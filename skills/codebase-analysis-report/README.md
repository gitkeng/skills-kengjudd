# codebase-analysis-report

Generate a portable, offline, accessible HTML report from a
`comprehensive-codebase-analysis` **v2** output tree. The report visualizes
evidence-backed findings, business rules, components, test traceability,
coverage, and Mermaid diagrams — without adopting any vendor platform.

## What it produces

A single directory you can open directly in a browser:

```text
<output>/
├── index.html            # self-contained: inlined CSS/JS, escaped content
├── report-manifest.json  # integrity + provenance (schema, counts, checksums)
└── assets/
    └── mermaid.min.js    # local, version-pinned Mermaid v11 runtime
```

`index.html` works from `file://`, loads no external scripts/styles/fonts/
images, is keyboard-operable, printable, and understandable without color.

## Design principles

- **Contract-driven.** The v2 `manifest.json` is the source of truth. The skill
  never invents findings, severities, scores, costs, or recommendations.
- **Safe by construction.** Markdown/JSON are untrusted: all text is escaped,
  links and images are sanitized, and Mermaid renders strictly with an
  always-visible source fallback. No analyzed code runs; nothing is fetched.
- **Vendor-neutral.** The UI, defaults, and wording are capability-first.
  Provider names appear only when present in the source as observed evidence.
- **Deterministic.** Ordering and IDs are stable; a report is validated before
  it is ever published.

## Usage

```sh
# 1) Render (state the resolved output path before running):
python3 scripts/render_report.py --source <analysis-root> --output <report-dir>

#    Replace an existing report — only after the user approves replacement
#    (prior output is backed up and restored on failure):
python3 scripts/render_report.py --source <analysis-root> --output <report-dir> --replace

#    Render an incomplete source (adds a persistent warning banner):
python3 scripts/render_report.py --source <analysis-root> --output <report-dir> --allow-incomplete

# 2) Validate a generated report independently:
python3 scripts/validate_report.py <report-dir>

# 3) Run the self-test suite (temp directories only):
python3 scripts/test_report.py --fixture <v2-output-tree>
```

Requires Python 3 (standard library only). No installs, no network.

## Layout

- `SKILL.md` — concise phased workflow and gates.
- `references/` — standalone, phase-specific detail:
  - `input-contract.md` — normative field-to-view map and enums.
  - `report-content.md` — information architecture and safe rendering.
  - `ux-accessibility.md` — theme, keyboard/ARIA, print/reduced-motion.
  - `mermaid-security.md` — accepted types, strict rendering, fallback.
  - `validation.md` — integrity manifest, publication, test matrix.
- `scripts/` — `render_report.py`, `validate_report.py`, `test_report.py`.
- `assets/` — `report.css`, `report.js`, `report-manifest.schema.json`,
  `mermaid.min.js`.

## Compatibility and safety notes

- Input must be v2 (`schema_version` `2.0`) output of the current
  `comprehensive-codebase-analysis` skill. Legacy provider-specific output is
  not an input target.
- Publication is one-shot (temp → validate → publish). Unvalidated output is
  never intentionally published; multi-step replacement is not claimed
  transactionally atomic.
- Mermaid directives (`%%{init}%%`) are treated as intentional source-only
  fallback rather than rendered, to preserve strict security.
