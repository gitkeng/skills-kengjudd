# Report content and safe rendering

## Information architecture

The report is a single scrollable page with these in-flow sections, each with a
stable ID and sidebar anchor:

- **Overview** — coverage mode, severity cards (equal to `severity_counts`),
  top open findings, finding confidence distribution, the preserved
  `prior_manifest_loaded` flag with delta counts (a false flag is framed as the
  first recorded run), coverage limitations, and reading routes (links to the
  findings registry, the documents section, and any declared reading-guide,
  migration, or operations documents). Shows the incomplete-source banner when
  applicable.
- **Findings** — complete sortable/filterable registry: alias, severity badge,
  status, confidence, title, evidence, stable row anchors.
- **Business rules** — complete registry: alias, coverage status, confidence,
  rule text, evidence; filterable by coverage.
- **Components** — complete registry with analysis-depth coverage.
- **Tests & traceability** — test registry, BR↔TC links, and explicit untested
  rules.
- **Documents** — every declared Markdown document rendered in full, grouped by
  source category, in declaration order, inside native disclosures.
- **About this report** — source schema/version/timestamp, generation method,
  offline/privacy statement, and machine-data references.

The report does not reproduce a legacy fixed-tab design and does not author a
roadmap. Migration and operations remain source documents reachable from the
Overview reading routes and the Documents section.

## Markdown subset (standard library only)

Supported: hash-prefixed (`#`) headings (demoted by a fixed offset inside
document panels so an embedded h1 nests under the page hierarchy, clamped at
h6), paragraphs, unordered/ordered lists, blockquotes,
fenced code, pipe tables, emphasis (`**`, `*`, `__`), inline code, links, and
images. Everything else renders as escaped text.

Escaping is first-class:

- Raw HTML is always escaped as text, including angle-bracket code such as
  `Task<JsonResult>`. Source HTML is never passed through or stripped.
- Emphasis is applied only to already-escaped text using fixed tags.

## Links

- Allowed: relative, hash (`#...`), and `http(s)` targets.
- Relative/hash links render as ordinary anchors.
- `http(s)` links get `rel="noreferrer noopener"` and an explicit external-link
  label.
- Any active scheme (for example `javascript:`, `data:`) renders as inert text
  with a visible note; it is never emitted as a live `href`.

## Images

Markdown images never trigger a remote request.

- `http(s)` images (including badge services) render as labeled external links
  marked "not loaded"; no `<img>` element is emitted.
- Relative images pass the same containment checks as documents. If the target
  is a regular local file within the allowlist, it embeds as a data URL;
  otherwise it renders as a labeled placeholder.
- Allowlist: `.png`, `.jpg`/`.jpeg`, `.gif`, `.webp`, `.svg`, at most 1 MiB.
- SVG is sanitized by rejection: an SVG containing `<script>`, an inline event
  handler attribute, `<foreignObject>`, or an external `href`/`xlink:href`
  (anything not a local `#fragment`) is not embedded; a placeholder is shown
  instead. Only fully clean SVGs embed.

## Determinism

- Document and alias order follow manifest declaration order.
- Severity views sort by fixed severity rank, then alias.
- DOM IDs derive from escaped aliases/paths plus deterministic collision
  suffixes, so IDs are unique and stable across runs.
- Runs include a report timestamp and are not claimed byte-identical; tests use
  a fixed `--generated-at` for reproducibility.
