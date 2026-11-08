# PDF — manifest flags, parts, transcription brief

Read this only when `probe.py` reported `kind: pdf`.

## Contents

- [Manifest flags](#manifest-flags)
- [Parts](#parts)
- [Transcription brief](#transcription-brief)
- [Why the PDF scripts exist](#why-the-pdf-scripts-exist)

## Manifest flags

After `extract_pdf.py`, read `manifest.json` → `summary`:

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

## Parts

One part per page: `parts/p001.md`, `parts/p002.md`, … (zero-padded to 3).
`merge.py` sorts them naturally and checks the count against the manifest.

## Transcription brief

PDF pages are transcribed by subagents, one per batch from `probe.batches`.
Batches are independent, so send them in a single message and let them run
concurrently. Give each subagent this brief, filled in, **followed by the
Fidelity rules from SKILL.md verbatim**:

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

## Why the PDF scripts exist

- **Thai SARA AM.** Many Thai PDF fonts map the NIKHAHIT glyph to a zero-width
  space, so plain extraction turns `ทำ` into `ท า` — silently, in every word
  with ำ; others leave the decomposed pair `ํ` + `า`. `pdf_text.py` rebuilds
  the string at glyph level and recomposes both forms, including a pair the
  PDF split across a line break (`ขอกํ` / `าหนด`), since SARA AA never
  starts a line on its own (1.2.1).
- **Thai SARA AA collapse.** Some fonts encode า and ำ as the same codepoint,
  so the text layer reads `กำรค้ำ` for `การค้า`. Nothing can undo that, which is
  why the extractor detects it by ratio and forces the whole document to OCR.
- **Repeated figures.** The same logo on 40 pages is one asset, not 40.
  Extraction hashes the bytes and reports which pages each figure appears on.
