#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Assemble the per-part markdown into one document, and audit the result.

The subagents write one markdown file per batch of pages / chunks / sheets.
This script is what turns those into the deliverable.  It does no rewriting of
content -- joining and whitespace only -- because every edit it made silently
would be an edit nobody reviewed.  What it does instead is *check*:

  * every part the manifest expects exists and is not empty
  * every ![](...) link resolves to a file that is actually on disk
  * every extracted asset got referenced somewhere (a figure quietly dropped by
    a subagent is the failure mode you cannot see in the output)
  * every markdown table row has the same number of columns as its header
  * nothing that looks like an unfinished placeholder survived

    uv run merge.py --work <workdir> --out <file.md> [--parts <dir>] [--title T] [--strict]

Prints a JSON report.  With --strict, exits non-zero when anything failed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

import _common as C

IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")

# Things a subagent leaves behind when it could not read something.  Better to
# fail loudly here than to ship a document with a hole in it.
PLACEHOLDER = re.compile(
    r"(?i)\b(TODO|TBD|FIXME|XXX|lorem ipsum|\[unreadable\]|\[illegible\]|\[cannot read\])\b"
)

TABLE_LINE = re.compile(r"^\s*\|.*\|\s*$")
SEPARATOR_LINE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def natural_key(path: Path):
    """Sort p2.md before p10.md."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.name)]


def expected_parts(manifest: dict) -> int | None:
    """How many parts the extractor said this document should produce."""
    kind = manifest.get("kind")
    if kind == "pdf":
        return manifest.get("page_count")
    if kind == "docx":
        return len(manifest.get("chunks") or []) or None
    if kind == "xlsx":
        return sum(len(s.get("parts") or []) for s in manifest.get("sheets") or []) or None
    if kind == "pptx":
        return manifest.get("slide_count")
    return None


# --------------------------------------------------------------------------
# whitespace
# --------------------------------------------------------------------------


def normalise(text: str) -> str:
    """Trailing space, blank-line runs, and the blank lines block elements need.

    A table or heading glued to the paragraph above it does not render as a
    table or a heading, and that is exactly what happens when two parts are
    concatenated.  Nothing else about the text is touched.
    """
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]

    out: list[str] = []
    for line in lines:
        is_block = line.startswith("#") or bool(TABLE_LINE.match(line))
        prev = out[-1] if out else ""
        prev_is_table = bool(TABLE_LINE.match(prev))
        prev_is_heading = prev.startswith("#")

        if is_block and prev.strip():
            same_table = bool(TABLE_LINE.match(line)) and prev_is_table
            if not same_table:
                out.append("")
        elif prev_is_table and line.strip() and not TABLE_LINE.match(line):
            out.append("")
        elif prev_is_heading and line.strip():
            out.append("")

        out.append(line)

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def boundary_repeats(parts: list[tuple[str, str]]) -> list[str]:
    """Lines every part starts or ends with -- page furniture that leaked in."""
    if len(parts) < 3:
        return []

    def edge(text: str, last: bool) -> str:
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        if not lines:
            return ""
        return lines[-1] if last else lines[0]

    repeats = []
    for last in (False, True):
        edges = [edge(body, last) for _name, body in parts]
        edges = [e for e in edges if e and len(e) < 200]
        if len(edges) < len(parts) - 1:
            continue
        for candidate in set(edges):
            if edges.count(candidate) >= max(3, int(len(parts) * 0.6)):
                repeats.append(candidate)
    return sorted(set(repeats))


# --------------------------------------------------------------------------
# audits
# --------------------------------------------------------------------------


def check_images(text: str, out_dir: Path) -> tuple[list[str], list[str]]:
    """(referenced relative paths, links that resolve to nothing)."""
    referenced, broken = [], []
    for raw in IMAGE_LINK.findall(text):
        target = raw.strip().strip("<>")
        if urlparse(target).scheme in ("http", "https", "data"):
            continue
        rel = unquote(target)
        referenced.append(rel)
        if not (out_dir / rel).exists():
            broken.append(rel)
    return referenced, broken


def check_tables(text: str) -> list[dict]:
    """Rows whose column count does not match their header row."""
    problems = []
    lines = text.split("\n")
    index = 0
    while index < len(lines):
        if not TABLE_LINE.match(lines[index]):
            index += 1
            continue

        start = index
        block = []
        while index < len(lines) and TABLE_LINE.match(lines[index]):
            block.append(lines[index])
            index += 1

        if len(block) < 2:
            continue

        def width(line: str) -> int:
            # Strip exactly one leading and one trailing pipe -- .strip("|")
            # would eat the empty first cell of a row like "|  |  |".
            # A pipe escaped by _common.cell is content, not a column break.
            inner = line.strip()
            if inner.startswith("|"):
                inner = inner[1:]
            if inner.endswith("|"):
                inner = inner[:-1]
            return len(re.split(r"(?<!\\)\|", inner))

        header_width = width(block[0])
        for offset, line in enumerate(block):
            if offset == 1 and SEPARATOR_LINE.match(line):
                continue
            if width(line) != header_width:
                problems.append(
                    {
                        "line": start + offset + 1,
                        "expected_columns": header_width,
                        "found_columns": width(line),
                        "text": line.strip()[:120],
                    }
                )
    return problems


def check_placeholders(text: str) -> list[dict]:
    out = []
    for number, line in enumerate(text.split("\n"), start=1):
        match = PLACEHOLDER.search(line)
        if match:
            out.append({"line": number, "match": match.group(0), "text": line.strip()[:120]})
    return out


# --------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="extractor work dir (holds manifest.json)")
    ap.add_argument("--out", required=True, help="final markdown file to write")
    ap.add_argument("--parts", default=None, help="dir of part files (default: <work>/parts)")
    ap.add_argument("--title", default=None, help="H1 to put at the top")
    ap.add_argument("--strict", action="store_true", help="exit non-zero on any problem")
    args = ap.parse_args()

    work = Path(args.work).expanduser()
    parts_dir = Path(args.parts).expanduser() if args.parts else work / "parts"
    out_path = Path(args.out).expanduser()

    manifest = {}
    manifest_path = work / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text("utf-8"))
        except Exception as exc:
            print(f"[warn] manifest unreadable: {exc}", file=sys.stderr)

    if not parts_dir.is_dir():
        C.emit({"ok": False, "error": f"parts dir not found: {parts_dir}"})
        return 1

    files = sorted((p for p in parts_dir.glob("*.md") if p.is_file()), key=natural_key)
    if not files:
        C.emit({"ok": False, "error": f"no .md parts in {parts_dir}"})
        return 1

    parts: list[tuple[str, str]] = []
    empty: list[str] = []
    for path in files:
        body = path.read_text("utf-8").strip()
        if not body:
            empty.append(path.name)
            continue
        parts.append((path.name, body))

    if not parts:
        C.emit({"ok": False, "error": "every part file is empty", "empty_parts": empty})
        return 1

    pieces = []
    if args.title:
        pieces.append(f"# {args.title}")
    pieces.extend(body for _name, body in parts)
    text = normalise("\n\n".join(pieces))

    C.write_text(out_path, text)

    out_dir = out_path.resolve().parent
    referenced, broken = check_images(text, out_dir)
    referenced_files = {Path(r).name for r in referenced}
    unused = [
        a["file"]
        for a in (manifest.get("assets") or [])
        if a.get("file") and a["file"] not in referenced_files
    ]

    want = expected_parts(manifest)
    table_problems = check_tables(text)
    placeholders = check_placeholders(text)
    furniture = boundary_repeats(parts)

    problems = {
        "missing_parts": (
            max(0, want - len(files)) if isinstance(want, int) else None
        ),
        "empty_parts": empty,
        "broken_image_links": broken,
        "unreferenced_assets": unused,
        "malformed_table_rows": table_problems,
        "placeholders_left": placeholders,
        "repeated_boundary_lines": furniture,
    }

    failed = bool(
        empty
        or broken
        or unused
        or table_problems
        or placeholders
        or (isinstance(want, int) and len(files) < want)
    )

    report = {
        "ok": not failed,
        "out": str(out_path.resolve()),
        "kind": manifest.get("kind"),
        "parts_dir": str(parts_dir.resolve()),
        "parts_used": [name for name, _ in parts],
        "parts_expected": want,
        "chars": len(text),
        "lines": text.count("\n") + 1,
        "tables": sum(1 for line in text.split("\n") if SEPARATOR_LINE.match(line)),
        "images_referenced": len(referenced),
        "problems": problems,
    }
    C.emit(report)
    return 1 if (failed and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
