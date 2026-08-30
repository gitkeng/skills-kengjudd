#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.24"]
# ///
"""Deterministically pull everything a subagent needs out of a PDF.

Per page it writes the repaired text layer, a rendered PNG for visual reference
and OCR, and any table structure PyMuPDF can find (cell text re-read through
pdf_text so Thai survives).  Embedded figures are saved once each into the
assets folder in document order, and the manifest hands back a ready-made
markdown image link so nobody has to hand-build a URL-encoded path.

    uv run extract_pdf.py <file.pdf> --work <workdir> --assets <assetsdir> [--base NAME]

Writes <workdir>/manifest.json and prints a summary of it on stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from urllib.parse import quote

import _common as C
import pdf_text as T

MIN_CHARS_FOR_TEXT_LAYER = 40
MAX_GARBLED_RATIO = 0.05

# An image covering this much of a page that has no text layer is the page
# itself (a scan), not a figure inside the document.
PAGE_SCAN_COVERAGE = 0.85


def render_page(page, dpi: int, max_px: int, out_path: Path) -> dict:
    """Rasterise one page, capped so the PNG stays cheap for a model to read."""
    import pymupdf

    zoom = dpi / 72.0
    longest = max(page.rect.width, page.rect.height) * zoom
    if longest > max_px:
        zoom *= max_px / longest

    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(out_path)
    return {"width": pix.width, "height": pix.height, "dpi": round(zoom * 72, 1)}


def extract_page_tables(page, work: Path, pno: int) -> list[dict]:
    """Table candidates for one page, cell text re-read with Thai repair.

    PyMuPDF finds the ruling lines; we do not trust its own cell text because
    it goes through the plain extractor that mangles SARA AM.
    """
    import pymupdf

    try:
        finder = page.find_tables()
    except Exception as exc:
        print(f"[warn] p{pno}: find_tables failed: {exc}", file=sys.stderr)
        return []

    entries = []
    for tindex, table in enumerate(finder.tables, start=1):
        grid = []
        header = getattr(table, "header", None)
        if header is not None and getattr(header, "external", False):
            grid.append([n or "" for n in (header.names or [])])

        for row in table.rows:
            grid.append(
                [
                    "" if bbox is None else T.clip_text(page, pymupdf.Rect(bbox))
                    for bbox in row.cells
                ]
            )

        grid = C.trim_grid(grid)
        if len(grid) < 2:
            continue

        rel = f"tables/p{pno:03d}_t{tindex:02d}.md"
        C.write_text(work / rel, C.to_md_table(grid, header_rows=1) + "\n")
        entries.append(
            {
                "index": tindex,
                "file": rel,
                "rows": len(grid),
                "cols": max(len(r) for r in grid),
                "bbox": [round(v, 1) for v in table.bbox],
            }
        )
    return entries


def collect_images(doc, assets_dir: Path, base: str, min_px: int, scanned: set[int]):
    """Save each distinct embedded figure once, numbered in document order.

    Identical bytes reused across pages (a header logo) collapse to a single
    asset that records every page it appears on, so the markdown can link it at
    its first occurrence instead of repeating it on every page.
    """
    by_hash: dict[str, dict] = {}
    order: list[str] = []

    for pno in range(doc.page_count):
        page = doc[pno]
        page_area = abs(page.rect.width * page.rect.height) or 1.0

        placed = []
        for img in page.get_images(full=True):
            xref = img[0]
            rects = page.get_image_rects(xref) or []
            top = min((r.y0 for r in rects), default=0.0)
            left = min((r.x0 for r in rects), default=0.0)
            coverage = max((abs(r.width * r.height) / page_area for r in rects), default=0.0)
            placed.append((top, left, xref, coverage))
        placed.sort(key=lambda t: (round(t[0], 1), round(t[1], 1)))

        for _top, _left, xref, coverage in placed:
            try:
                raw = doc.extract_image(xref)
            except Exception:
                continue
            if not raw or not raw.get("image"):
                continue
            if raw.get("width", 0) < min_px or raw.get("height", 0) < min_px:
                continue
            if coverage >= PAGE_SCAN_COVERAGE and (pno + 1) in scanned:
                continue  # this image *is* the scanned page, not a figure

            digest = hashlib.sha1(raw["image"]).hexdigest()
            entry = by_hash.get(digest)
            if entry is None:
                entry = {
                    "ext": (raw.get("ext") or "png").lower(),
                    "bytes": raw["image"],
                    "width": raw.get("width"),
                    "height": raw.get("height"),
                    "pages": [],
                }
                by_hash[digest] = entry
                order.append(digest)
            if (pno + 1) not in entry["pages"]:
                entry["pages"].append(pno + 1)

    known_ext = {"png", "jpg", "jpeg", "gif", "bmp", "webp", "tiff"}
    assets = []
    repeat_threshold = max(3, int(doc.page_count * 0.5))
    if order:
        assets_dir.mkdir(parents=True, exist_ok=True)

    for index, digest in enumerate(order, start=1):
        entry = by_hash[digest]
        ext = entry["ext"] if entry["ext"] in known_ext else "png"
        name = f"{base}_{index:02d}.{ext}"
        (assets_dir / name).write_bytes(entry["bytes"])
        rel = f"{assets_dir.name}/{name}"
        assets.append(
            {
                "index": index,
                "file": name,
                "rel_path": rel,
                "md": f"![]({quote(rel)})",
                "width": entry["width"],
                "height": entry["height"],
                "pages": entry["pages"],
                "first_page": entry["pages"][0] if entry["pages"] else None,
                "repeated": len(entry["pages"]) >= repeat_threshold,
            }
        )
    return assets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--work", required=True, help="scratch dir for page dumps")
    ap.add_argument("--assets", required=True, help="assets dir for extracted figures")
    ap.add_argument("--base", default=None, help="output base name (default: file stem)")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--ocr-dpi", type=int, default=220, help="dpi for pages with no text layer")
    ap.add_argument("--max-px", type=int, default=1800, help="cap on rendered longest side")
    ap.add_argument("--min-image-px", type=int, default=80, help="ignore figures smaller than this")
    ap.add_argument("--no-tables", action="store_true")
    args = ap.parse_args()

    import pymupdf

    path = Path(args.file).expanduser()
    if not path.exists():
        C.emit({"ok": False, "error": f"file not found: {path}"})
        return 1

    base = args.base or C.base_name(path)
    work = Path(args.work).expanduser()
    assets_dir = Path(args.assets).expanduser()
    doc = pymupdf.open(path)

    pages = []
    scanned: set[int] = set()

    for pno in range(doc.page_count):
        page = doc[pno]
        plain = page.get_text("text") or ""       # pre-repair, for diagnostics only
        text = T.page_text(page)                  # repaired: this is what agents read
        stripped = "".join(text.split())

        garbled = C.garbled_ratio(plain)
        has_text = len(stripped) >= MIN_CHARS_FOR_TEXT_LAYER
        suspect = garbled > MAX_GARBLED_RATIO
        if not has_text or suspect:
            scanned.add(pno + 1)

        txt_rel = f"pages/p{pno + 1:03d}.txt"
        C.write_text(work / txt_rel, text)

        png_rel = f"pages/p{pno + 1:03d}.png"
        render = render_page(
            page,
            args.ocr_dpi if (pno + 1) in scanned else args.dpi,
            args.max_px,
            work / png_rel,
        )

        tables = [] if args.no_tables else extract_page_tables(page, work, pno + 1)

        pages.append(
            {
                "page": pno + 1,
                "text_file": txt_rel,
                "image_file": png_rel,
                "chars": len(stripped),
                "has_text_layer": has_text,
                "text_suspect": suspect,
                "garbled_ratio": round(garbled, 4),
                "symbol_glyphs": T.pua_count(plain),
                "repaired_sara_am": T.broken_sara_am_count(plain) - T.broken_sara_am_count(text),
                "needs_ocr": (pno + 1) in scanned,
                "render": render,
                "tables": tables,
                "assets": [],
            }
        )

    # Figures are identified against the *layout* scan set: a page that is one
    # big image.  Thai encoding trouble, decided next, must not feed into this.
    assets = collect_images(doc, assets_dir, base, args.min_image_px, set(scanned))
    page_count = doc.page_count
    doc.close()

    # Document-level Thai integrity.  If the font collapsed า into ำ, every
    # page must be transcribed from its render -- the text layer lies.
    thai = T.thai_stats("".join((work / p["text_file"]).read_text("utf-8") for p in pages))
    thai_broken = T.thai_layer_unreliable(thai)
    if thai_broken:
        print(
            f"[warn] Thai text layer unreliable (sara-am ratio {thai['sara_am_ratio']}): "
            "forcing every page to OCR from its render",
            file=sys.stderr,
        )
        for p in pages:
            p["needs_ocr"] = True
            p["text_suspect"] = True
            scanned.add(p["page"])

    by_page = {p["page"]: p for p in pages}
    for asset in assets:
        for pno in asset["pages"]:
            if pno in by_page:
                by_page[pno]["assets"].append(
                    {
                        "file": asset["file"],
                        "md": asset["md"],
                        "first_occurrence": pno == asset["first_page"],
                        "repeated": asset["repeated"],
                    }
                )

    # Reading the render costs tokens.  Only recommend it where the layout
    # actually needs eyes: OCR pages, tables, figures, odd symbol glyphs.
    for p in pages:
        p["read_image"] = bool(
            p["needs_ocr"] or p["text_suspect"] or p["tables"] or p["assets"] or p["symbol_glyphs"]
        )

    manifest = {
        "ok": True,
        "kind": "pdf",
        "source": str(path.resolve()),
        "base": base,
        "work_dir": str(work.resolve()),
        "assets_dir": str(assets_dir.resolve()),
        "assets_dir_name": assets_dir.name,
        "page_count": page_count,
        "assets": assets,
        "thai": thai | {"text_layer_unreliable": thai_broken},
        "pages": pages,
        "summary": {
            "pages_needing_ocr": sorted(scanned),
            "thai_text_layer_unreliable": thai_broken,
            "asset_count": len(assets),
            "repeated_assets": [a["file"] for a in assets if a["repeated"]],
            "pages_with_tables": [p["page"] for p in pages if p["tables"]],
            "pages_to_read_image": [p["page"] for p in pages if p["read_image"]],
            "sara_am_repairs": sum(p["repaired_sara_am"] for p in pages),
        },
    }
    C.write_json(work / "manifest.json", manifest)

    summary = {k: v for k, v in manifest.items() if k != "pages"}
    summary["pages"] = f"{page_count} entries in manifest.json"
    C.emit(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
