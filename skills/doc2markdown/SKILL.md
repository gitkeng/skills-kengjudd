---
name: doc2markdown
description: >-
  Convert a PDF, DOCX, XLSX, or PPTX into faithful Markdown with images
  extracted and tables preserved. Use when asked to convert, extract,
  transcribe, or read a document into markdown — "แปลงเอกสาร", "อ่านไฟล์เป็น
  markdown", "ถอดเอกสาร" — or when a .pdf/.docx/.xlsx/.pptx path appears.
  Handles Thai documents, scans needing OCR, slide decks ("แปลงสไลด์",
  "พาวเวอร์พอยต์"), RFPs, TORs, meeting minutes, and cost breakdown
  spreadsheets.
metadata:
  version: "1.2.1"
  updated: "2026-11-08"
  upstream: "local ~/.claude/skills/doc-to-markdown (no git repo, no upstream version; imported 2026-08-29)"
---

# Document to Markdown

Convert a source document into one Markdown file that a reader can trust: same
words, same tables, same figures, same order.

The hard parts are already solved deterministically by the scripts in
`scripts/`. Your job is the part that needs eyes — reading page renders,
deciding heading levels, placing figures — and then checking the result.

**Never transcribe a document by reading it yourself from scratch.** Run the
extractor first. It repairs Thai text that every naive extraction corrupts,
keeps the document's real order, and hands you page images, table grids, and
saved figures that you would otherwise have to reconstruct by guesswork. The
per-kind reference explains which failure each script prevents.

## Requirements

`uv` must be on PATH. The scripts declare their own dependencies inline
(PEP 723), so `uv run scripts/probe.py …` installs what it needs on first run.
Nothing to set up.

All `scripts/` and `references/` paths in this skill are relative to the
**skill directory**, not the working directory. If this skill is installed as
a symlink, resolve its real location first (`readlink -f <this-skill-dir>`)
and run the scripts from there, e.g. `uv run <skill-dir>/scripts/probe.py …`.

## Layout

Decide these two directories up front and keep them fixed for the whole run:

```
<out_dir>/
  <base>.md              ← the deliverable
  assets/                ← extracted figures; MUST sit beside the .md
    <base>_01.png
<out_dir>/.dtm/<base>/   ← scratch; safe to delete when done
  manifest.json          ← what the extractor found (read this, it drives everything)
  pages/ chunks/ sheets/ slides/
  tables/
  parts/                 ← one Markdown file per unit; you write these
```

`assets/` must be a sibling of the `.md`, or the relative image links break —
`merge.py` verifies this and will tell you.

Default `<out_dir>` to the source file's own directory unless the user says
otherwise. Default `<base>` to the source file's stem.

## Step 1 — Probe

```bash
uv run scripts/probe.py "<file>" --batch-size 5
```

Read the JSON. It tells you the kind, the unit count (pages / sheets /
document), whether any page lacks a text layer, and how to batch the work.
If `ok` is false, stop and report the reason — do not fall back to guessing.

Legacy `.doc` / `.xls` / `.ppt` are rejected by design. Ask the user to save as
`.docx` / `.xlsx` / `.pptx`; converting them silently is not something this
skill does.

**Then read exactly one reference for the kind probe reported** — it holds
that kind's manifest flags, part naming, review procedure or subagent brief,
and the reasons behind its script:

| `kind` | Read |
| --- | --- |
| `pdf` | [references/pdf.md](references/pdf.md) |
| `docx`, `xlsx` | [references/docx-xlsx.md](references/docx-xlsx.md) |
| `pptx` | [references/pptx.md](references/pptx.md) |

## Step 2 — Extract

Pick the extractor by kind. All four write `<work>/manifest.json`.

```bash
uv run scripts/extract_pdf.py  "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_docx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_xlsx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_pptx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
```

Then read `manifest.json` and let its `summary` flags decide how much work is
needed — the kind's reference lists every flag and what to do about it. Two
are universal: a flag naming pages or slides that **need OCR** means those
units are transcribed from their render, never from the `.txt`; and
`repeated_assets` means a recurring logo is linked once, not on every page.

## Step 3 — Write the parts

One Markdown file per unit, into `<work>/parts/`, named as the kind's reference
says — `merge.py` sorts them naturally and checks the count against the
manifest.

- **DOCX, XLSX, PPTX are already drafted** (`chunks/`, `sheets/`, `slides/`
  hold real Markdown). Read each draft against its `.txt`, fix what needs
  judgement (heading levels, figure placement, a header band the guess got
  wrong), and save to `parts/`. If a draft is already right, copy it across
  unchanged — do not rewrite for style.
- **PDF pages and OCR slides need transcription** from their renders. When
  your harness can spawn subagents, dispatch one per batch concurrently with
  the brief in the kind's reference, followed by the Fidelity rules below
  verbatim; otherwise transcribe batch by batch yourself under the same
  brief.

## Fidelity rules

These are the contract. Everything here is about not quietly changing the
document.

1. **Transcribe, do not summarise.** Every sentence, table row, and list item in
   the source appears in the output. No condensing, no "…and so on", no
   improving the wording.
2. **Do not translate.** Thai stays Thai, English stays English, mixed stays
   mixed.
3. **Never invent.** If a character is genuinely unreadable, write
   `[unreadable]` — `merge.py` flags it so the user finds out. Making a
   plausible-looking value up is the one unrecoverable failure here.
4. **Headings** map to `#`…`######` by the document's own hierarchy. Do not
   promote a bold run to a heading unless it plainly is one.
5. **Tables** stay tables. Merged header cells fold into one row joined with
   ` / `. A cell's internal line breaks become `<br>`. A literal `|` inside a
   cell is escaped `\|`. Every row has the same column count as its header.
6. **Slide headings (pptx).** If a slide shows a visible title, it becomes the
   part's `##` heading. If the slide has no title, start the part with
   `## Slide N` — a structural marker, not invented content. Never compose a
   title the slide does not show.
7. **Figures** get their manifest `md` link at the position they appear. Add a
   one-line italic caption underneath describing what it shows — a chart nobody
   can read is worth less than a sentence saying what it plots.
8. **Page furniture** — running headers, footers, page numbers, slide numbers —
   is dropped, not transcribed once per page. Text boxes and callouts are kept,
   as blockquotes.
9. **No page markers** in the body. Do not write `--- page 4 ---`; the parts are
   about to be joined into one continuous document. (The `## Slide N` marker of
   rule 6 is the allowed exception — slides are discrete units, not pages of
   continuous prose.)
10. **Speaker notes (pptx)** are source content. Keep them as a blockquote at
    the end of the slide's part: `> **Speaker notes:** …` with every
    continuation line also prefixed `> ` (the extractor already formats it
    this way). If a slide has none, write nothing.
11. **Nothing outside `parts/`.** Do not touch the source file, the assets, or
    the final `.md`.

## Step 4 — Merge and verify

```bash
uv run scripts/merge.py --work "<work>" --out "<out_dir>/<base>.md" \
  --title "<document title>" --strict
```

It joins the parts, fixes only whitespace, and audits. Read `problems`:

- `missing_parts` / `empty_parts` — a subagent failed. Re-run that batch.
- `broken_image_links` — a link points at a file that is not there. Usually a
  hand-typed path; use the manifest's `md` string instead.
- `unreferenced_assets` — a figure was extracted and nobody placed it. Find
  where it belongs and add it. This is the failure you cannot see by reading
  the output, so never wave it through.
- `malformed_table_rows` — a row's column count disagrees with its header.
  Fix the row; do not fix the header to match a broken row.
- `placeholders_left` — a TODO or `[unreadable]` survived. Resolve it or tell
  the user explicitly which part of the document could not be read.
- `repeated_boundary_lines` — the same line opens or closes most parts: page
  furniture that leaked in. Remove it from the parts and merge again.

Re-run `merge.py` after fixing until `ok` is true. Then report to the user:
where the file is, how many pages/sheets/slides, what was OCR'd, what was
skipped (hidden sheets, unreadable spots), and anything you had to judge
rather than read.

## Updating

Versioned by `metadata.version`; source: private repo `gitkeng/skills-kengjudd`.

- Git clone + symlink install (from the repo root; `readlink -f` a symlinked
  skill dir to find it): `./scripts/update.sh doc2markdown`
- Claude Code plugin install (`update.sh` cannot run in the plugin cache, which
  has no `.git`): `claude plugin update kengjudd@kengjudd`

Then reload skills or restart the session (Claude Code: `/reload-skills`).
