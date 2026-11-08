# DOCX and XLSX — manifest flags, parts, review procedure

Read this only when `probe.py` reported `kind: docx` or `kind: xlsx`.

## Contents

- [Manifest flags](#manifest-flags)
- [Parts](#parts)
- [Review procedure](#review-procedure)
- [Why the DOCX and XLSX scripts exist](#why-the-docx-and-xlsx-scripts-exist)

## Manifest flags

After the extractor, read `manifest.json` → `summary`:

- `repeated_assets` — a logo or letterhead repeating across the document.
  Link it once at first occurrence.
- `sheets_with_uncached_formulas` (xlsx) — that workbook was never opened in
  Excel, so cells show `=SUM(...)` instead of a number. Say so in the output;
  do not invent totals.
- `sheets_with_hidden_data`, `skipped_sheets` (xlsx) — hidden rows/columns
  were extracted anyway; hidden *sheets* were not. Mention both to the user.

## Parts

| Kind | One part per | File name |
| --- | --- | --- |
| docx | chunk in `manifest.chunks` | `parts/c01.md`, `parts/c02.md`, … |
| xlsx | entry in `manifest.sheets[].parts` | `parts/s01_p01.md`, … |

## Review procedure

Both kinds are **already drafted**: `chunks/cNN.md` and `sheets/sNN_pNN.md`
are real Markdown, produced deterministically. Read each draft against its
`.txt` counterpart, fix what needs judgement — heading levels, figure
placement, a header band the guess got wrong — and save to `parts/`. If a
draft is already right, copy it across unchanged; do not rewrite for style.
No subagents are needed for these kinds.

## Why the DOCX and XLSX scripts exist

- **DOCX body order.** Iterating `document.paragraphs` then `document.tables`
  reorders the entire document. `extract_docx.py` walks the XML body in order.
- **DOCX list styles.** Word attaches list numbering to the *style* ("List
  Bullet", "List Number") as often as to the paragraph, so a paragraph-only
  check turns every such item into a plain paragraph. The extractor follows
  the style chain (added 1.2.0).
- **DOCX merged cells.** Continuations of a merged cell are blanked, not
  duplicated; the cell identity is its XPath, because lxml recycles proxy
  object ids and `id()` blanked unrelated cells (fixed 1.2.0).
- **XLSX merged cells.** openpyxl reports a merged value once and `None` for the
  rest, so a group label vanishes from every row but the first.
  `extract_xlsx.py` spreads it — except across a full-width banner row, where
  spreading is noise.
