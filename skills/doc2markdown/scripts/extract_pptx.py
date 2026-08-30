#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["python-pptx>=1.0", "Pillow>=10"]
# ///
"""Turn a .pptx into one markdown draft per slide, plus its images.

Slides are self-contained units, so this mirrors the PDF pipeline (one part
per slide) rather than the DOCX chunker.  Two slide kinds matter:

  * normal slides -- the draft is real markdown produced here (text boxes in
    visual reading order, tables as grids with merged cells blanked, charts as
    data tables, SmartArt text from diagram data parts, figures as ready-made
    links); a reviewing agent fixes judgement calls only.
  * full-page-image slides -- one picture (or a background image fill) covers
    the slide and there is no usable text or structured content.  The picture
    is normalised into slides/sNNN.png and the slide is flagged needs_ocr,
    exactly like a scanned PDF page: a subagent transcribes from that render,
    never from memory.  Text boxes overlaid on the picture are NOT in the
    render; the manifest flags them (overlay_text) so nobody drops them.

    uv run extract_pptx.py <file.pptx> --work <workdir> --assets <assetsdir> [--base NAME]

Writes <workdir>/manifest.json and prints a summary of it on stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

import _common as C

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
DGM = "{http://schemas.openxmlformats.org/drawingml/2006/diagram}"

# A slide with fewer real characters than this has no usable text -- typically
# one big exported image (a "scan" of a slide).
MIN_CHARS_FOR_TEXT = 40

# A picture covering this much of the slide is the slide itself (or its
# background), not a figure inside it.
FULL_BLEED_COVERAGE = 0.85

# Renders are capped/flagged around these sizes: above the cap a model cannot
# eat the bytes, below the floor OCR of slide-sized text gets unreliable.
RENDER_MAX_PX = 2000
RENDER_LOW_RES_PX = 1200

# Image formats a model can actually read; anything else is converted to PNG.
READABLE_EXT = {"png", "jpg", "jpeg", "gif", "webp"}


# --------------------------------------------------------------------------
# image normalisation
# --------------------------------------------------------------------------


def _normalise_image(blob: bytes, out_path: Path, max_px: int) -> dict | None:
    """Flatten alpha onto white, cap the longest side, save as PNG.

    Always re-encodes: the file is named .png, so writing JPEG bytes into it
    would be the silent lie this module exists to prevent.  Returns the render
    info dict, or None when Pillow cannot decode the format (EMF/WMF).
    """
    try:
        import io

        from PIL import Image

        image = Image.open(io.BytesIO(blob))
        image.load()
        if image.mode != "RGB":
            rgba = image.convert("RGBA")
            flat = Image.new("RGB", rgba.size, (255, 255, 255))
            flat.paste(rgba, mask=rgba.split()[-1])
            image = flat
        width, height = image.size
        low_res = max(width, height) < RENDER_LOW_RES_PX
        longest = max(width, height)
        if longest > max_px:
            scale = max_px / longest
            image = image.resize(
                (max(1, round(width * scale)), max(1, round(height * scale))),
                Image.LANCZOS,
            )
            width, height = image.size
        out_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(out_path, "PNG")
        return {"width": width, "height": height, "low_res": low_res}
    except Exception:
        return None


def _render_via_soffice(blob: bytes, ext: str, out_path: Path, max_px: int) -> dict | None:
    """Last resort for EMF/WMF: LibreOffice converts what Pillow cannot."""
    import shutil
    import subprocess
    import tempfile

    soffice = shutil.which("soffice")
    if not soffice:
        return None
    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / f"render_input.{ext or 'bin'}"
        src.write_bytes(blob)
        try:
            subprocess.run(
                [soffice, "--headless", "--convert-to", "png", "--outdir", td, str(src)],
                check=True,
                capture_output=True,
                timeout=60,
            )
            produced = src.with_suffix(".png")
            if produced.exists():
                return _normalise_image(produced.read_bytes(), out_path, max_px)
        except Exception:
            return None
    return None


def save_render(blob: bytes, ext: str, out_path: Path, max_px: int = RENDER_MAX_PX) -> dict | None:
    """Save a full-page picture as the slide's OCR render.

    Returns the render info dict, or None when neither Pillow nor LibreOffice
    could convert the bytes -- the caller flags render_unavailable so nobody
    pretends the slide can be transcribed.
    """
    info = _normalise_image(blob, out_path, max_px)
    if info is None:
        info = _render_via_soffice(blob, ext, out_path, max_px)
    if info is None:
        print(f"[warn] render conversion failed ({ext})", file=sys.stderr)
    return info


# --------------------------------------------------------------------------
# images
# --------------------------------------------------------------------------


class ImageBank:
    """Saves each distinct picture once, numbered by first appearance.

    Identical bytes reused across slides (a logo) collapse to a single asset
    that records every slide it appears on.
    """

    def __init__(self, assets_dir: Path, base: str, min_bytes: int):
        self.assets_dir = assets_dir
        self.base = base
        self.min_bytes = min_bytes
        self.by_digest: dict[str, dict] = {}
        self.saved: list[dict] = []

    def add(self, blob: bytes, ext: str, slide: int, background: bool = False) -> dict | None:
        if not blob or len(blob) < self.min_bytes:
            return None
        digest = hashlib.sha1(blob).hexdigest()
        entry = self.by_digest.get(digest)
        if entry is None:
            ext = (ext or "png").lower()
            if ext == "jpeg":
                ext = "jpg"
            data = blob
            unreadable = False
            if ext not in READABLE_EXT:
                converted = self._to_png(blob)
                if converted is not None:
                    data, ext = converted, "png"
                else:
                    # Keep the original bytes and extension -- a wrong
                    # extension on unchanged bytes would be a silent lie --
                    # but flag the asset so nobody expects it to render.
                    unreadable = True
            index = len(self.saved) + 1
            name = f"{self.base}_{index:02d}.{ext}"
            self.assets_dir.mkdir(parents=True, exist_ok=True)
            (self.assets_dir / name).write_bytes(data)
            rel = f"{self.assets_dir.name}/{name}"
            entry = {
                "index": index,
                "file": name,
                "rel_path": rel,
                "md": f"![]({quote(rel)})",
                "bytes": len(blob),
                "slides": [],
                "background": background,
                "unreadable_format": unreadable,
            }
            self.by_digest[digest] = entry
            self.saved.append(entry)
        if slide not in entry["slides"]:
            entry["slides"].append(slide)
        if background:
            entry["background"] = True
        return entry

    @staticmethod
    def _to_png(blob: bytes) -> bytes | None:
        try:
            import io

            from PIL import Image

            out = io.BytesIO()
            Image.open(io.BytesIO(blob)).save(out, "PNG")
            return out.getvalue()
        except Exception:
            return None


# --------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------


def is_title(shape) -> bool:
    if not shape.is_placeholder:
        return False
    try:
        from pptx.enum.shapes import PP_PLACEHOLDER

        return shape.placeholder_format.type in (
            PP_PLACEHOLDER.TITLE,
            PP_PLACEHOLDER.CENTER_TITLE,
        )
    except Exception:
        return False


def para_has_bullet(para) -> bool:
    """buNone kills inheritance, so check it first; buChar/buAutoNum say bullet;
    an indented level without buNone is a bullet by list-style default."""
    ppr = para._p.find(A + "pPr")
    if ppr is not None:
        if ppr.find(A + "buNone") is not None:
            return False
        if ppr.find(A + "buChar") is not None or ppr.find(A + "buAutoNum") is not None:
            return True
    return para.level > 0


def render_paragraph(para) -> str:
    # Coalesce consecutive runs with the same bold state first: PowerPoint
    # splits runs mid-word, and wrapping each run separately yields
    # "**1.** **Import**" or empty "****" pairs -- both are broken markdown.
    # Never add spaces between runs: Thai runs split mid-word and a spurious
    # space corrupts the word.
    segments: list[list] = []  # [text, bold]
    for run in para.runs:
        text = run.text or ""
        if not text:
            continue
        try:
            bold = bool(run.font.bold)
        except Exception:
            bold = False
        if segments and segments[-1][1] == bold:
            segments[-1][0] += text
        else:
            segments.append([text, bold])

    parts = []
    for text, bold in segments:
        stripped = text.strip()
        if bold and stripped:
            lead = text[: len(text) - len(text.lstrip())]
            trail = text[len(text.rstrip()) :]
            parts.append(f"{lead}**{stripped}**{trail}")
        else:
            parts.append(text)
    body = "".join(parts).strip()
    if not body:
        body = (para.text or "").strip()
    if not body:
        return ""
    if para_has_bullet(para):
        return f"{'  ' * min(para.level, 4)}- {body}"
    return body


def text_block(shape) -> tuple[str, str]:
    """(markdown, plain) for one text frame, paragraphs in order."""
    md_lines, plain_lines = [], []
    for para in shape.text_frame.paragraphs:
        md = render_paragraph(para)
        if not md:
            continue
        md_lines.append(md)
        plain_lines.append(para.text.strip())
    return "\n".join(md_lines), "\n".join(plain_lines)


# --------------------------------------------------------------------------
# tables / charts / diagrams
# --------------------------------------------------------------------------


def table_grid(table) -> list[list[str]]:
    """Grid with merged-cell continuations blanked instead of duplicated."""
    grid = []
    seen: set[int] = set()
    for row in table.rows:
        out_row = []
        for c in row.cells:
            key = id(c._tc)
            if key in seen:
                out_row.append("")
            else:
                seen.add(key)
                out_row.append(c.text.strip())
        grid.append(out_row)
    return grid


def chart_markdown(chart) -> tuple[str, str]:
    """(markdown, plain) best-effort data readout of a chart.

    Reads the cached plot data only -- categories and series values as they
    stand in the file.  Raises nothing; the caller catches and flags
    charts_unreadable instead of dropping the chart silently.
    """
    title = ""
    if chart.has_title:
        title = chart.chart_title.text_frame.text.strip()

    lines = []
    plain = [title] if title else []
    for plot in chart.plots:
        categories = [str(c) for c in plot.categories]
        rows = []
        for series in plot.series:
            values = ["" if v is None else str(v) for v in series.values]
            rows.append([str(series.name or ""), *values])
        if categories and rows:
            header = [["", *categories]]
            grid = C.trim_grid(header + rows)
            lines.append(C.to_md_table(grid, header_rows=1))
            plain.extend(" ".join(str(v) for v in r) for r in grid)
    md = "\n\n".join(l for l in ([f"**{title}**"] if title else []) + lines)
    return md, "\n".join(plain)


def diagram_texts(shape, slide_part) -> list[str]:
    """Text nodes of a SmartArt diagram.

    python-pptx does not model diagrams; the words live in the diagram data
    part (ppt/diagrams/dataN.xml) that the graphicFrame references via
    dgm:relIds.  Reading the a:t nodes recovers the labels without inventing
    any structure.
    """
    texts = []
    for relids in shape._element.iter(DGM + "relIds"):
        rid = relids.get(R + "dm")
        if not rid:
            continue
        try:
            part = slide_part.related_parts[rid]
            root = ET.fromstring(part.blob)
        except Exception:
            continue
        for t in root.iter(A + "t"):
            if t.text and t.text.strip():
                texts.append(t.text.strip())
    return texts


def is_diagram(shape) -> bool:
    for gd in shape._element.iter(A + "graphicData"):
        if DGM.strip("{}") in (gd.get("uri") or ""):
            return True
    return False


def background_fill_image(slide) -> tuple[bytes, str] | None:
    """(blob, ext) of a picture set as the slide's background fill, if any.

    Canva/Google Slides exports put the whole slide design in
    cSld/bg/bgPr/blipFill; it never appears in slide.shapes, so a slide that is
    100% background image would otherwise look like an empty slide.
    """
    from pptx.oxml.ns import qn

    cSld = slide._element.find(qn("p:cSld"))
    if cSld is None:
        return None
    bg = cSld.find(qn("p:bg"))
    if bg is None:
        return None
    for blip in bg.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if not rid:
            continue
        try:
            part = slide.part.related_parts[rid]
        except Exception:
            return None
        ext = Path(str(part.partname)).suffix.lower().lstrip(".") or "png"
        return part.blob, ext
    return None


# --------------------------------------------------------------------------
# slides
# --------------------------------------------------------------------------


def extract_slide(slide, sno: int, slide_w: int, slide_h: int, bank: ImageBank,
                  work: Path, min_image_bytes: int) -> tuple[dict, str, str]:
    """Build (manifest entry, draft markdown, plain text) for one slide."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    slide_area = (slide_w or 1) * (slide_h or 1)
    placed = []  # (top, left, kind, payload) in slide coordinates
    full_bleed = None  # (blob, ext) of the largest picture covering the slide
    plain_all: list[str] = []
    furniture: list[str] = []  # dropped page-number text boxes, for the manifest
    tables = charts = diagrams = charts_unreadable = 0

    for shape, left, top, width, height in C.iter_shapes(slide.shapes):
        coverage = (width * height) / slide_area if slide_area else 0.0

        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            try:
                blob, ext = shape.image.blob, shape.image.ext
            except Exception:
                placed.append((top, left, "note", "[image could not be read]"))
                continue
            if coverage >= FULL_BLEED_COVERAGE:
                if len(blob) >= min_image_bytes and (
                    full_bleed is None or len(blob) > len(full_bleed[0])
                ):
                    full_bleed = (blob, ext)
                # Tiny full-bleed pictures are solid-color decoration; they are
                # neither render candidates nor figures.
                continue  # background-or-scan is decided after the text count
            entry = bank.add(blob, ext, sno)
            if entry:
                placed.append((top, left, "image", entry))
            continue

        if getattr(shape, "has_table", False):
            grid = C.trim_grid(table_grid(shape.table))
            if grid:
                md = C.to_md_table(grid, header_rows=1)
                plain = "\n".join(" ".join(str(v or "") for v in row) for row in grid)
                placed.append((top, left, "table", {"md": md, "plain": plain}))
                tables += 1
            continue

        if getattr(shape, "has_chart", False):
            try:
                md, plain = chart_markdown(shape.chart)
                placed.append((top, left, "chart", {"md": md, "plain": plain}))
                charts += 1
            except Exception as exc:
                print(f"[warn] s{sno}: chart unreadable: {exc}", file=sys.stderr)
                placed.append(
                    (top, left, "chart_unreadable",
                     "*[A chart on this slide could not be read from the file.]*")
                )
                charts_unreadable += 1
            continue

        if is_diagram(shape):
            texts = diagram_texts(shape, slide.part)
            if texts:
                md = "\n".join(f"- {t}" for t in texts)
                placed.append((top, left, "diagram", {"md": md, "plain": "\n".join(texts)}))
                diagrams += 1
            continue

        if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
            md, plain = text_block(shape)
            if not md.strip():
                continue
            if plain.strip() == str(sno):
                # A text box whose whole content is the slide's own number is
                # a page number -- furniture, dropped like PDF page numbers.
                # Recorded in the manifest so the drop is never silent.
                furniture.append(plain.strip())
                continue
            kind = "title" if is_title(shape) else "text"
            placed.append((top, left, kind, {"md": md, "plain": plain}))
            plain_all.append(plain)

    text_chars = sum(len("".join(p.split())) for p in plain_all)

    bg_fill = background_fill_image(slide)
    image_source = full_bleed or bg_fill
    # Structured content (table/chart/diagram) means the slide is NOT a scan,
    # even with a full-bleed picture and almost no text: the render would not
    # contain that content, and "transcribe from the image" would drop it.
    needs_ocr = (
        image_source is not None
        and text_chars < MIN_CHARS_FOR_TEXT
        and not (tables or charts or diagrams)
    )
    overlay_text = bool(needs_ocr and text_chars > 0)
    background_entry = None
    if image_source is not None and not needs_ocr:
        # A full-bleed picture under real content: maybe wallpaper, maybe a
        # content-carrying infographic.  Save it flagged; the reviewer decides
        # from the actual image, so nothing is dropped silently.
        background_entry = bank.add(image_source[0], image_source[1], sno, background=True)
    little_text = bool(not needs_ocr and text_chars < MIN_CHARS_FOR_TEXT)

    # Reading order: title first, then top-to-bottom, left-to-right.  The
    # rounding (~0.01 inch at 914400 EMU/inch) keeps near-aligned neighbours in
    # creation order instead of shuffling them over sub-pixel jitter.
    placed.sort(key=lambda item: (item[2] != "title", round(item[1], -4), round(item[0], -4)))

    md_parts, plain_parts = [], []
    slide_assets = []
    for _top, _left, kind, payload in placed:
        if kind == "title":
            md_parts.append(f"## {payload['md']}")
            plain_parts.append(payload["plain"])
        elif kind in ("text", "table", "chart", "diagram"):
            md_parts.append(payload["md"])
            plain_parts.append(payload["plain"])
        elif kind == "chart_unreadable":
            md_parts.append(payload)
        elif kind == "image":
            slide_assets.append(payload)
            md_parts.append(payload["md"])
        elif kind == "note":
            md_parts.append(f"**{payload}**")

    if background_entry is not None:
        slide_assets.append(background_entry)
        md_parts.append(background_entry["md"])

    notes = ""
    if slide.has_notes_slide:
        notes = slide.notes_slide.notes_text_frame.text.strip()
    if notes:
        quoted = "\n".join(
            f"> {line}" if line.strip() else ">" for line in notes.split("\n")
        )
        md_parts.append(f"> **Speaker notes:**\n{quoted}")

    render = None
    image_file = None
    if needs_ocr:
        blob, ext = image_source
        image_file = f"slides/s{sno:03d}.png"
        render = save_render(blob, ext, work / image_file)

    entry = {
        "slide": sno,
        "draft_file": f"slides/s{sno:03d}.md",
        "text_file": f"slides/s{sno:03d}.txt",
        "chars": text_chars,
        "title": next((p[3]["plain"] for p in placed if p[2] == "title"), None),
        "needs_ocr": needs_ocr,
        "overlay_text": overlay_text,
        "little_text": little_text,
        "image_file": image_file,
        "render": render,
        "render_unavailable": bool(needs_ocr and render is None),
        "background_image": background_entry is not None,
        "tables": tables,
        "charts": charts,
        "charts_unreadable": charts_unreadable,
        "diagrams": diagrams,
        "notes_chars": len(notes),
        "furniture_dropped": furniture,
        "assets": slide_assets,
        "read_image": bool(needs_ocr and render is not None),
    }
    return entry, "\n\n".join(md_parts), "\n".join(plain_parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--work", required=True, help="scratch dir for slide dumps")
    ap.add_argument("--assets", required=True, help="assets dir for extracted figures")
    ap.add_argument("--base", default=None, help="output base name (default: file stem)")
    ap.add_argument("--min-image-bytes", type=int, default=3000)
    args = ap.parse_args()

    from pptx import Presentation

    path = Path(args.file).expanduser()
    if not path.exists():
        C.emit({"ok": False, "error": f"file not found: {path}"})
        return 1
    if path.suffix.lower() != ".pptx":
        C.emit({"ok": False, "error": "only .pptx is supported; save .ppt as .pptx first"})
        return 2

    base = args.base or C.base_name(path)
    work = Path(args.work).expanduser()
    assets_dir = Path(args.assets).expanduser()

    prs = Presentation(str(path))
    bank = ImageBank(assets_dir, base, args.min_image_bytes)

    slides = []
    for sno, slide in enumerate(prs.slides, start=1):
        entry, draft, plain = extract_slide(
            slide, sno, prs.slide_width, prs.slide_height, bank, work,
            args.min_image_bytes,
        )
        C.write_text(work / entry["draft_file"], draft + "\n")
        C.write_text(work / entry["text_file"], plain + "\n")
        slides.append(entry)

    slide_count = len(slides)
    repeat_threshold = max(3, int(slide_count * 0.5))
    assets = []
    for entry in bank.saved:
        entry["first_slide"] = entry["slides"][0] if entry["slides"] else None
        entry["repeated"] = len(entry["slides"]) >= repeat_threshold
        assets.append(entry)
    # Per-slide asset lists must be copies: the bank entries are shared dicts,
    # and a first_occurrence written into the shared dict is last-writer-wins,
    # which tells the transcription brief to skip the figure everywhere.
    for entry in slides:
        entry["assets"] = [
            {
                "file": a["file"],
                "md": a["md"],
                "background": a.get("background", False),
                "unreadable_format": a.get("unreadable_format", False),
                "repeated": a.get("repeated", False),
                "first_occurrence": a.get("first_slide") == entry["slide"],
            }
            for a in entry["assets"]
        ]

    manifest = {
        "ok": True,
        "kind": "pptx",
        "source": str(path.resolve()),
        "base": base,
        "work_dir": str(work.resolve()),
        "assets_dir": str(assets_dir.resolve()),
        "assets_dir_name": assets_dir.name,
        "slide_count": slide_count,
        "assets": assets,
        "slides": slides,
        "summary": {
            "slides_needing_ocr": [s["slide"] for s in slides if s["needs_ocr"]],
            "slides_with_overlay_text": [
                s["slide"] for s in slides if s["overlay_text"]
            ],
            "slides_with_little_text": [s["slide"] for s in slides if s["little_text"]],
            "slides_render_unavailable": [
                s["slide"] for s in slides if s["render_unavailable"]
            ],
            "slides_low_res_render": [
                s["slide"] for s in slides if (s["render"] or {}).get("low_res")
            ],
            "slides_with_tables": [s["slide"] for s in slides if s["tables"]],
            "slides_with_charts": [s["slide"] for s in slides if s["charts"]],
            "slides_with_unreadable_charts": [
                s["slide"] for s in slides if s["charts_unreadable"]
            ],
            "slides_with_diagrams": [s["slide"] for s in slides if s["diagrams"]],
            "slides_with_notes": [s["slide"] for s in slides if s["notes_chars"]],
            "slides_with_background_image": [
                s["slide"] for s in slides if s["background_image"]
            ],
            "asset_count": len(assets),
            "assets_unreadable_format": [
                a["file"] for a in assets if a["unreadable_format"]
            ],
            "repeated_assets": [a["file"] for a in assets if a["repeated"]],
            "slides_to_read_image": [s["slide"] for s in slides if s["read_image"]],
        },
    }
    C.write_json(work / "manifest.json", manifest)

    summary = {k: v for k, v in manifest.items() if k not in ("slides", "assets")}
    summary["slides"] = f"{slide_count} entries in manifest.json"
    C.emit(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
