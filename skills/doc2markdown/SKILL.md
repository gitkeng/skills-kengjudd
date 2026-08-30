---
name: doc2markdown
description: Convert a PDF, DOCX, XLSX, or PPTX into faithful Markdown, with images extracted and tables preserved. Use when asked to convert, extract, transcribe, read into markdown, or "make a .md out of" a document — including Thai documents, scans needing OCR, slide decks, RFPs, TORs, meeting minutes, and cost breakdown spreadsheets. Triggers on .pdf/.docx/.xlsx/.pptx paths and on "แปลงเอกสาร", "อ่านไฟล์เป็น markdown", "ถอดเอกสาร", "แปลงสไลด์", "พาวเวอร์พอยต์".
metadata:
  version: "1.1.1"
  updated: "2026-08-30"
  upstream: "local ~/.claude/skills/doc-to-markdown (no git repo, no upstream version; imported 2026-08-29)"
---

# Document to Markdown

Convert a source document into one Markdown file that a reader can trust: same
words, same tables, same figures, same order.

The hard parts are already solved deterministically by the scripts in
`scripts/`. Your job is the part that needs eyes — reading page renders,
deciding heading levels, placing figures — and then checking the result.

**Never transcribe a document by reading it yourself from scratch.** Run the
extractor first. It repairs Thai text that every naive extraction corrupts (see
"Why the scripts exist"), and it hands you page images, table grids, and saved
figures that you would otherwise have to reconstruct by guesswork.

## Requirements

`uv` must be on PATH. The scripts declare their own dependencies inline
(PEP 723), so `uv run scripts/probe.py …` installs what it needs on first run.
Nothing to set up.

All `scripts/` paths in this skill are relative to the **skill directory**, not
the working directory. If this skill is installed as a symlink, resolve its real
location first (`readlink -f <this-skill-dir>`) and run the scripts from there,
e.g. `uv run <skill-dir>/scripts/probe.py …`.

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

## Step 2 — Extract

Pick the extractor by kind. All four write `<work>/manifest.json`.

```bash
uv run scripts/extract_pdf.py  "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_docx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_xlsx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
uv run scripts/extract_pptx.py "<file>" --work "<work>" --assets "<out_dir>/assets"
```

Then read `manifest.json` and let its `summary` decide how much work is needed:

- `pages_needing_ocr` — those pages have no usable text layer. They must be
  transcribed from `pages/pNNN.png`, not from the `.txt`.
- `thai_text_layer_unreliable: true` — the font collapsed า into ำ across the
  whole document. **Every** page must be read from its render; the `.txt` files
  are unusable no matter how clean they look.
- `pages_to_read_image` — pages where the render is worth the tokens (tables,
  figures, odd symbol glyphs). Pages not in this list can be transcribed from
  their `.txt` alone.
- `repeated_assets` — a logo or letterhead repeating on most pages. Link it
  once at first occurrence, not on every page.
- `sheets_with_uncached_formulas` — that workbook was never opened in Excel, so
  cells show `=SUM(...)` instead of a number. Say so in the output; do not
  invent totals.
- `sheets_with_hidden_data`, `skipped_sheets` — hidden rows/columns were
  extracted anyway; hidden *sheets* were not. Mention both to the user.
- `slides_needing_ocr` (pptx) — those slides are one full-page picture (or a
  background image fill) with no usable text or structured content. They must
  be transcribed from `slides/sNNN.png`, the slide's own picture normalised as
  its render — exactly like a scanned PDF page.
- `slides_with_overlay_text` (pptx) — OCR slides that still have a few text
  boxes on top of the picture. **The render does not contain that text** (it is
  the embedded picture only, not a rasterised slide); the transcription brief
  must say to carry the draft's text into the part.
- `slides_with_little_text` (pptx) — slides with under 40 chars that are NOT
  OCR slides (no full-page picture). Whatever their content is, it needs eyes:
  review them from the draft and, when in doubt, the figure files.
- `slides_render_unavailable` (pptx) — full-page-image slides whose picture is
  in a format neither Pillow nor LibreOffice could convert (e.g. EMF/WMF
  without LibreOffice). The sanctioned part content is the `## Slide N`
  heading plus one italic line: `*This slide is a single image in a format
  that could not be converted; it was not transcribed.*` Then tell the user.
- `slides_low_res_render` (pptx) — OCR slides whose render is under 1200 px on
  the long side; transcription confidence is limited, say so in the report.
- `slides_with_unreadable_charts` (pptx) — the chart's cached data could not be
  read, and slides are never rendered whole (no PowerPoint/LibreOffice
  dependency in this skill). The draft carries an italic placeholder line;
  keep it in the part and tell the user which slide's chart is missing.
- `slides_with_background_image` (pptx) — a full-bleed picture sits *under*
  real content. It is saved as an asset flagged `background: true` and linked
  at the end of the draft. Read the image: if it carries content (an annotated
  infographic), transcribe that content; if it is wallpaper, remove the link.
- `slides_with_notes` (pptx) — these slides have speaker notes; fidelity
  rule 10 applies. On OCR slides the notes live only in the draft — the render
  cannot show them — so the transcription brief must carry them over verbatim.
- `furniture_dropped` (pptx) — text boxes whose whole content was the slide's
  own number, dropped as page furniture. Listed so the drop is never silent.

## Step 3 — Write the parts

One Markdown file per unit, into `<work>/parts/`. The names matter — `merge.py`
sorts them naturally and checks the count against the manifest:

| Kind | One part per | File name |
| --- | --- | --- |
| pdf | page | `parts/p001.md`, `parts/p002.md`, … |
| docx | chunk in `manifest.chunks` | `parts/c01.md`, … |
| xlsx | entry in `manifest.sheets[].parts` | `parts/s01_p01.md`, … |
| pptx | slide | `parts/s001.md`, `parts/s002.md`, … |

**DOCX, XLSX, and PPTX are already drafted.** `chunks/cNN.md`,
`sheets/sNN_pNN.md`, and `slides/sNNN.md` are real Markdown, produced
deterministically. Read each draft against its `.txt` counterpart, fix what
needs judgement (heading levels, figure placement, a header band the guess got
wrong), and save to `parts/`. If a draft is already right, copy it across
unchanged — do not rewrite for style.

**PPTX exception: OCR slides have no text draft.** A slide flagged `needs_ocr`
is one full-page picture; its `slides/sNNN.md` holds at most overlaid text and
the speaker-notes blockquote. Those slides are transcribed from
`slides/sNNN.png` by subagents. **Batch only the slide numbers in
`summary.slides_needing_ocr`** — probe's `batches` span *all* slides, which is
wrong for pptx; group the flagged numbers into ranges of `batch-size` yourself.
Dispatch one subagent per range, concurrently, with this brief, filled in:

> Transcribe slides {list} of {source} into Markdown.
> For each slide write `{work}/parts/s{NNN}.md` (zero-padded to 3).
> Per slide, `{work}/manifest.json` has the entry under `slides`:
> - `image_file` — the slide's render. **Read it.** It is the embedded
>   full-page picture only — not a rasterised slide — so it is the authority
>   for everything visible *in the picture*, and nothing else.
> - `chars` and `overlay_text` — when true, text boxes sit on top of the
>   picture and are NOT in the render. Carry the text from the slide's
>   `text_file` into the part, placed where it sits on the slide.
> - If the slide's `draft_file` contains a `> **Speaker notes:**` blockquote,
>   append it verbatim at the end of the part (rule 10) — the render cannot
>   show notes.
> - There are no pre-built `tables[]` files for slides. Build any table visible
>   in the render as a Markdown table yourself, following rule 5. If the render
>   is mostly a diagram or flowchart, transcribe every node's label as a nested
>   bullet list mirroring the visual hierarchy, and add a one-line italic
>   description of the layout.
> Follow the fidelity rules below. Write nothing outside `parts/`.

Then include the fidelity rules verbatim in the brief.

**PDF needs transcription.** Dispatch one subagent per batch from
`probe.batches`. Batches are independent, so send them in a single message and
let them run concurrently. Give each subagent this brief, filled in:

> Transcribe pages {start}–{end} of {source} into Markdown.
> For each page write `{work}/parts/p{NNN}.md` (zero-padded to 3).
> Per page, `{work}/manifest.json` has the entry under `pages`:
> - `text_file` — the repaired text layer. Use it as the source of the words.
> - `image_file` — the page render. **Read it** when `read_image` is true, and
>   treat it as authoritative when `needs_ocr` or `text_suspect` is true: in
>   that case the text layer is corrupt and you transcribe from the image.
> - `tables[].file` — a pre-built Markdown table for each table on the page.
>   Check it against the render, fix cells the ruling-line detection got wrong,
>   and paste it in. Do not rebuild a table from the raw text.
> - `assets[]` — each has a ready-made `md` link. Place it where the figure sits
>   on the page. Skip any entry where `first_occurrence` is false.
> Follow the fidelity rules below. Write nothing outside `parts/`.

Then include the fidelity rules verbatim in the brief.

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
where the file is, how many pages/sheets, what was OCR'd, what was skipped
(hidden sheets, unreadable spots), and anything you had to judge rather than
read.

## Why the scripts exist

Don't route around them; each encodes a failure you will otherwise hit.

- **Thai SARA AM.** Many Thai PDF fonts map the NIKHAHIT glyph to a zero-width
  space, so plain extraction turns `ทำ` into `ท า` — silently, in every word
  with ำ. `pdf_text.py` rebuilds the string at glyph level and recomposes it.
- **Thai SARA AA collapse.** Some fonts encode า and ำ as the same codepoint,
  so the text layer reads `กำรค้ำ` for `การค้า`. Nothing can undo that, which is
  why the extractor detects it by ratio and forces the whole document to OCR.
- **DOCX body order.** Iterating `document.paragraphs` then `document.tables`
  reorders the entire document. `extract_docx.py` walks the XML body in order.
- **XLSX merged cells.** openpyxl reports a merged value once and `None` for the
  rest, so a group label vanishes from every row but the first.
  `extract_xlsx.py` spreads it — except across a full-width banner row, where
  spreading is noise.
- **Repeated figures.** The same logo on 40 pages is one asset, not 40.
  Extraction hashes the bytes and reports which pages each figure appears on.
- **PPTX shape order.** `slide.shapes` iterates in z-order (creation order),
  not reading order. `extract_pptx.py` sorts by visual position — title first,
  then top-to-bottom, left-to-right.
- **PPTX groups.** Shapes inside a group report positions in the group's child
  coordinate system, not slide coordinates; using them raw scrambles reading
  order. The extractor applies the `chOff`/`chExt` transform when recursing.
- **PPTX full-page pictures.** A slide that is one full-bleed image with real
  text on top is a *background* (decoration, not saved); with no text it is a
  *scan* (saved as the slide's render and transcribed by OCR). Confusing the
  two either loses a slide's only content or fills the output with wallpaper.
- **PPTX runs.** PowerPoint splits runs mid-word, so per-run markdown markers
  produce `**1.** **Import**` and empty `****` pairs. The extractor coalesces
  adjacent same-style runs and never inserts spaces between them (Thai words
  would break).

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh doc2markdown
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
