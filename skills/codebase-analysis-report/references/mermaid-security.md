# Mermaid compatibility and security

## Accepted diagram types

The renderer accepts the same type superset as the source validator:

`flowchart`, `graph`, `sequenceDiagram`, `classDiagram`, `stateDiagram`,
`stateDiagram-v2`, `erDiagram`, `C4Context`, `C4Container`, `C4Component`,
`C4Deployment`, `architecture-beta`, `block-beta`, `packet-beta`, `journey`,
`gantt`, `pie`, `mindmap`, `timeline`, `gitGraph`, `quadrantChart`,
`xychart-beta`, `sankey-beta`, `requirementDiagram`, `zenuml`.

## Classification

A fenced `mermaid` block is **safe** for runtime rendering only when all hold:

- it contains no init/config directive (`%%{init ...}%%`, `%%{config ...}%%`);
- its first token is an accepted diagram type;
- it contains no raw HTML tag. Detection matches real HTML element names
  (terminated or unterminated tag-opens), so idiomatic Mermaid such as UML
  stereotypes (`<<fork>>`, `<<interface>>`) and generic type names
  (`Task<JsonResult>`) stays renderable;
- its brackets/quotes are balanced under quote-, escape-, comment-, and
  Mermaid-edge-aware rules (matching the source validator: `%%` comment lines
  skipped, `"..."` spans ignored, backslash escapes honored, and `o{`/`|{` and
  `}o`/`}|` edge forms treated as balanced).

Any block that is unsupported, malformed, contains raw HTML, or contains a
directive is preserved as an **escaped source-only fallback** and does not abort
the rest of a valid report.

## Rendering behavior

- Escaped source is present in the static DOM and stays visible without
  JavaScript and in print.
- Safe diagrams carry `data-mermaid-safe="true"`. The deferred script
  initializes Mermaid with `securityLevel: "strict"`, a neutral theme,
  deterministic IDs, and `htmlLabels: false` (labels render as SVG text, never
  live HTML), and renders eagerly so print and off-screen sections are not
  blank.
- JavaScript reveals rendered output only after Mermaid succeeds. A rendering
  failure leaves the source and a readable failure label.

## Local asset

`assets/mermaid.min.js` is a generic, offline Mermaid v11 runtime copied from
the shared bundle. It is version-pinned by SHA-256; the same digest is embedded
in `render_report.py` and `validate_report.py` and asserted by the test suite
and the report-manifest. It is a runtime, not a branded UI asset. No CDN or
network fetch is ever used.
