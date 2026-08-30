#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pymupdf>=1.24", "openpyxl>=3.1", "python-docx>=1.1", "python-pptx>=1.0"]
# ///
"""Inspect a source document and report what the extraction pipeline is facing.

Answers the questions the orchestrator needs before dispatching any subagent:
how many pages / sheets, does every page carry a usable text layer, is the text
layer garbled, how many images are embedded, how should the work be batched.

    uv run probe.py <file> [--batch-size 5]

Prints JSON on stdout.  Never writes anything.
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

import _common as C

# A page with fewer real characters than this is treated as having no usable
# text layer -- typically a scan, or a page that is one big picture.
MIN_CHARS_FOR_TEXT_LAYER = 40

# Above this fraction of private-use / replacement glyphs the text layer
# decodes to nonsense (broken ToUnicode CMap) and must not be trusted.
MAX_GARBLED_RATIO = 0.05


def probe_pdf(path: Path) -> dict:
    import pymupdf

    doc = pymupdf.open(path)
    pages = []
    needs_ocr = []
    suspect = []
    xrefs = set()

    for pno in range(doc.page_count):
        page = doc[pno]
        text = page.get_text("text") or ""
        stripped = "".join(text.split())
        garbled = C.garbled_ratio(text)

        images = page.get_images(full=True)
        for img in images:
            xrefs.add(img[0])

        page_area = abs(page.rect.width * page.rect.height) or 1.0
        covered = 0.0
        for img in images:
            for rect in page.get_image_rects(img[0]) or []:
                covered = max(covered, abs(rect.width * rect.height) / page_area)

        has_text = len(stripped) >= MIN_CHARS_FOR_TEXT_LAYER
        is_garbled = garbled > MAX_GARBLED_RATIO

        if not has_text:
            needs_ocr.append(pno + 1)
        elif is_garbled:
            suspect.append(pno + 1)

        pages.append(
            {
                "page": pno + 1,
                "chars": len(stripped),
                "has_text_layer": has_text,
                "garbled_ratio": round(garbled, 4),
                "text_suspect": is_garbled,
                "image_count": len(images),
                "max_image_page_coverage": round(covered, 3),
                "looks_scanned": (not has_text) and covered > 0.5,
            }
        )

    total = doc.page_count
    doc.close()
    return {
        "pages": total,
        "distinct_embedded_images": len(xrefs),
        "pages_needing_ocr": needs_ocr,
        "pages_with_suspect_text": suspect,
        "fully_scanned": len(needs_ocr) == total and total > 0,
        "page_info": pages,
    }


def probe_docx(path: Path) -> dict:
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    document = docx.Document(str(path))
    body = document.element.body

    paragraphs = tables = chars = headings = 0
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            para = Paragraph(child, document)
            paragraphs += 1
            chars += len(para.text)
            if (para.style.name or "").lower().startswith("heading"):
                headings += 1
        elif tag == "tbl":
            table = Table(child, document)
            tables += 1
            for row in table.rows:
                for cell_ in row.cells:
                    chars += len(cell_.text)

    with zipfile.ZipFile(path) as zf:
        media = [n for n in zf.namelist() if n.startswith("word/media/")]

    return {
        "paragraphs": paragraphs,
        "headings": headings,
        "tables": tables,
        "text_chars": chars,
        "media_files": len(media),
        "media_names": sorted(media),
    }


def probe_xlsx(path: Path) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(path, data_only=True, read_only=False)
    sheets = []
    for index, ws in enumerate(wb.worksheets, start=1):
        images = len(getattr(ws, "_images", []) or [])
        charts = len(getattr(ws, "_charts", []) or [])
        sheets.append(
            {
                "index": index,
                "name": ws.title,
                "state": ws.sheet_state,
                "max_row": ws.max_row or 0,
                "max_column": ws.max_column or 0,
                "merged_ranges": len(ws.merged_cells.ranges),
                "images": images,
                "charts": charts,
            }
        )
    wb.close()
    return {"sheet_count": len(sheets), "sheets": sheets}


def probe_pptx(path: Path) -> dict:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    prs = Presentation(str(path))
    area = ((prs.slide_width or 1) * (prs.slide_height or 1)) or 1
    slides = []
    needs_ocr = []
    for sno, slide in enumerate(prs.slides, start=1):
        chars = tables = charts = pictures = 0
        full_bleed = False
        for shape, _l, _t, w, h in C.iter_shapes(slide.shapes):
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                pictures += 1
                if (w * h) / area >= 0.85:
                    full_bleed = True
            elif getattr(shape, "has_table", False):
                tables += 1
            elif getattr(shape, "has_chart", False):
                charts += 1
            if getattr(shape, "has_text_frame", False) and shape.has_text_frame:
                chars += len("".join(shape.text_frame.text.split()))
        ocr = full_bleed and chars < MIN_CHARS_FOR_TEXT_LAYER
        if ocr:
            needs_ocr.append(sno)
        slides.append(
            {
                "slide": sno,
                "chars": chars,
                "pictures": pictures,
                "tables": tables,
                "charts": charts,
                "full_bleed_image": full_bleed,
                "needs_ocr": ocr,
            }
        )
    return {
        "slide_count": len(slides),
        "slides_needing_ocr": needs_ocr,
        "fully_image_based": len(needs_ocr) == len(slides) and len(slides) > 0,
        "slide_info": slides,
    }


KINDS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".xlsx": "xlsx",
    ".xlsm": "xlsx",
    ".pptx": "pptx",
}

UNSUPPORTED = {
    ".doc": "legacy .doc (OLE2) needs LibreOffice to convert; not installed",
    ".xls": "legacy .xls (BIFF) needs LibreOffice or xlrd<2; convert to .xlsx first",
    ".ppt": "legacy .ppt (OLE2); save it as .pptx first",
}


def batches(count: int, size: int) -> list[dict]:
    out = []
    for start in range(1, count + 1, size):
        end = min(start + size - 1, count)
        out.append({"index": len(out) + 1, "start": start, "end": end})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--batch-size", type=int, default=5)
    args = ap.parse_args()

    path = Path(args.file).expanduser()
    if not path.exists():
        C.emit({"ok": False, "error": f"file not found: {path}"})
        return 1

    suffix = path.suffix.lower()
    if suffix in UNSUPPORTED:
        C.emit({"ok": False, "error": UNSUPPORTED[suffix], "path": str(path)})
        return 2

    kind = KINDS.get(suffix)
    if kind is None:
        C.emit({"ok": False, "error": f"unsupported extension: {suffix}", "path": str(path)})
        return 2

    result = {
        "ok": True,
        "path": str(path.resolve()),
        "base": C.base_name(path),
        "kind": kind,
        "size_bytes": path.stat().st_size,
    }

    try:
        if kind == "pdf":
            info = probe_pdf(path)
            result["units"] = info["pages"]
            result["unit_name"] = "page"
            result["batches"] = batches(info["pages"], args.batch_size)
        elif kind == "docx":
            info = probe_docx(path)
            result["units"] = 1
            result["unit_name"] = "document"
        elif kind == "pptx":
            info = probe_pptx(path)
            result["units"] = info["slide_count"]
            result["unit_name"] = "slide"
            result["batches"] = batches(info["slide_count"], args.batch_size)
        else:
            info = probe_xlsx(path)
            result["units"] = info["sheet_count"]
            result["unit_name"] = "sheet"
        result[kind] = info
    except Exception as exc:  # surface the real reason, do not pretend success
        C.emit({"ok": False, "error": f"{type(exc).__name__}: {exc}", "path": str(path)})
        return 3

    C.emit(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
