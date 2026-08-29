# Report integrity, publication, and testing

## Report manifest

Every published report includes `report-manifest.json`, validated against
`assets/report-manifest.schema.json`. It records its own `schema_version`, the
consumed source schema/version and timestamps, the incomplete-source flag, the
included Markdown document paths, registry/severity counts, the pinned Mermaid
SHA-256, and SHA-256 for `index.html` and copied assets. It never hashes itself.

`validate_report.py` checks this schema directly, recomputes all checksums and
counts, confirms the pinned Mermaid digest, and asserts the generated HTML:

- required sections, landmarks, and a skip link exist;
- IDs are unique;
- theme controls (System/Light/Dark) and a blocking head initializer are
  present;
- severity labels appear as text in the overview cards (non-color cue);
- no external asset loads (`<img>`/`<script>`/`<link>` etc. to `http(s)`/`//`)
  and no network primitives (`fetch`, `XMLHttpRequest`, `sendBeacon`, `new
  Image`);
- every manifest Markdown document is present.

Neutrality is enforced on skill-authored assets only (`report.css`,
`report.js`, and the render template chrome), with word-boundary matching so
CSS properties like `text-transform` are not false positives. Observed source
content (finding titles, document panels, repository paths) passes through
unchanged.

## Publication semantics

Rendering is one-shot and intentionally non-resumable: render into a unique temp
sibling of the destination → validate the temp output → publish. It does not
create a report-generation `progress.json`.

- The temp directory is a sibling of the destination so renames stay on one
  filesystem.
- With no existing destination, publish by directory rename.
- With explicit `--replace` (only after the user approves replacement): rename
  the old directory to a unique backup, rename the validated temp into place,
  restore the backup if publication fails, and remove the backup only after the
  published destination passes final validation (a failed final validation
  restores the backup and keeps the failed output aside for inspection).
- Without `--replace`, an existing destination is refused
  (`output-collision`).
- This is not claimed transactionally atomic across the backup step; the claim
  is only that unvalidated output is never intentionally published.

## Test matrix (`scripts/test_report.py`, temp dirs only)

Covers, at minimum:

- both v2 schema versions, the exact completion predicate and phase set/status,
  unknown keys/version fail-closed, incomplete approval and banner;
- JSON excluded from Markdown; every declared Markdown included exactly once;
- full/focused/sampled coverage; covered and untested rules; coverage
  disagreement rejection; non-empty new/resolved/regressed delta;
- raw HTML and angle-bracket escaping; active-link neutralization; remote
  images produce no loading element; relative-image containment; oversize
  placeholder; SVG script/event/external-ref rejection and clean-SVG embed;
  symlink/traversal/special-file rejection;
- the complete accepted Mermaid type list; directive/HTML source-only fallback;
  edge/quote-aware balance; strict security markers; static and no-JS fallback;
  pinned checksum;
- anchor navigation with `aria-current`; native disclosures with
  `aria-expanded`; `aria-sort`; filter and theme live status; landmarks; skip
  link; captions;
- blocking head theme init before paint; System default; valid persistence;
  invalid/storage-exception fallback; OS-change listener; reduced-motion; light
  print override;
- programmatic contrast for body/UI/focus and severity badge token pairs in both
  themes at the stated AA ratios;
- report-manifest schema; count/checksum recomputation; self-hash rejection;
  mutation failures (tampered index, removed document, corrupted Mermaid);
- output-collision refusal; approved backup/publish/restore; temp sibling on the
  same filesystem;
- authored-asset neutrality scan; source provider-name passthrough; overview
  severity cards equal to manifest counts; absence of external scripts/styles/
  fonts/images/network calls.

## Acceptance fixture

The test suite accepts any valid, completed v2 output tree via `--fixture`
(typically the analysis root being reported). Never place test input or output
inside the shipped skill. When the sibling analyzer's validator is available,
its result on the fixture may be recorded separately from this skill's
self-contained preflight.
