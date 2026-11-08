# PPTX — manifest flags, parts, OCR-slide brief

Read this only when `probe.py` reported `kind: pptx`.

## Contents

- [Manifest flags](#manifest-flags)
- [Parts](#parts)
- [OCR slides: subagent brief](#ocr-slides-subagent-brief)
- [Why the PPTX script exists](#why-the-pptx-script-exists)

## Manifest flags

After `extract_pptx.py`, read `manifest.json` → `summary`:

- `slides_needing_ocr` — those slides are one full-page picture (or a
  background image fill) with no usable text or structured content. They must
  be transcribed from `slides/sNNN.png`, the slide's own picture normalised as
  its render — exactly like a scanned PDF page.
- `slides_with_overlay_text` — OCR slides that still have a few text boxes on
  top of the picture. **The render does not contain that text** (it is the
  embedded picture only, not a rasterised slide); the transcription brief must
  say to carry the draft's text into the part.
- `slides_with_little_text` — slides with under 40 chars that are NOT OCR
  slides (no full-page picture). Whatever their content is, it needs eyes:
  review them from the draft and, when in doubt, the figure files.
- `slides_render_unavailable` — full-page-image slides whose picture is in a
  format neither Pillow nor LibreOffice could convert (e.g. EMF/WMF without
  LibreOffice). The sanctioned part content is the `## Slide N` heading plus
  one italic line: `*This slide is a single image in a format that could not
  be converted; it was not transcribed.*` Then tell the user.
- `slides_low_res_render` — OCR slides whose render is under 1200 px on the
  long side; transcription confidence is limited, say so in the report.
- `slides_with_unreadable_charts` — the chart's cached data could not be read,
  and slides are never rendered whole (no PowerPoint/LibreOffice dependency).
  The draft carries an italic placeholder line; keep it in the part and tell
  the user which slide's chart is missing.
- `slides_with_background_image` — a full-bleed picture sits *under* real
  content. It is saved as an asset flagged `background: true` and linked at
  the end of the draft. Read the image: if it carries content (an annotated
  infographic), transcribe that content; if it is wallpaper, remove the link.
- `slides_with_notes` — these slides have speaker notes; fidelity rule 10
  applies. On OCR slides the notes live only in the draft — the render cannot
  show them — so the transcription brief must carry them over verbatim.
- `furniture_dropped` — text boxes whose whole content was the slide's own
  number, dropped as page furniture. Listed so the drop is never silent.
- `repeated_assets` — a logo repeating on most slides. Link it once.

## Parts

One part per slide: `parts/s001.md`, `parts/s002.md`, … (zero-padded to 3).

Slides are **already drafted** in `slides/sNNN.md`. Review each draft against
its `.txt`, fix judgement calls, copy to `parts/` — except OCR slides, below.

## OCR slides: subagent brief

A slide flagged `needs_ocr` has no text draft: its `slides/sNNN.md` holds at
most overlaid text and the speaker-notes blockquote. Those slides are
transcribed from `slides/sNNN.png` by subagents. **Batch only the slide numbers
in `summary.slides_needing_ocr`** — probe's `batches` span *all* slides, which
is wrong for pptx; group the flagged numbers into ranges of `batch-size`
yourself. Dispatch one subagent per range, concurrently, with this brief,
filled in, **followed by the Fidelity rules from SKILL.md verbatim**:

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

## Why the PPTX script exists

- **Shape order.** `slide.shapes` iterates in z-order (creation order), not
  reading order. `extract_pptx.py` sorts by visual position — title first,
  then top-to-bottom, left-to-right.
- **Groups.** Shapes inside a group report positions in the group's child
  coordinate system, not slide coordinates; using them raw scrambles reading
  order. The extractor applies the `chOff`/`chExt` transform when recursing.
- **Full-page pictures.** A slide that is one full-bleed image with real text
  on top is a *background* (decoration, not saved); with no text it is a
  *scan* (saved as the slide's render and transcribed by OCR). Confusing the
  two either loses a slide's only content or fills the output with wallpaper.
- **Runs.** PowerPoint splits runs mid-word, so per-run markdown markers
  produce `**1.** **Import**` and empty `****` pairs. The extractor coalesces
  adjacent same-style runs and never inserts spaces between them (Thai words
  would break).
