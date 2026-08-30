"""Character-accurate text extraction from a PDF page.

`page.get_text("text")` is close, but Thai documents come out damaged: many
Thai fonts map the NIKHAHIT glyph (the little circle that forms the top half of
SARA AM, ำ) to U+0020 with **zero advance width**.  Plain text extraction then
yields "ท า" where the source says "ทำ" -- silently corrupting every word that
contains ำ.

So we read the page at character level, where each glyph still carries its
bounding box, and rebuild the string:

  * a zero-width space is never a real space -- it is a combining mark the font
    failed to encode.  Followed by า (U+0E32) it is a NIKHAHIT and the pair
    recomposes to ำ (U+0E33); otherwise it is dropped.
  * an explicit NIKHAHIT + SARA AA pair recomposes the same way.
  * output is NFC-normalised so Thai marks sit in canonical order.

Everything here is deterministic.  It only ever removes glyphs the font told us
have no width, or recomposes a documented Unicode equivalence -- it never
invents a character.
"""

from __future__ import annotations

import re
import unicodedata

# A glyph narrower than this is not a real advance; PDF text operators emit
# combining marks this way.
ZERO_WIDTH = 0.05

NIKHAHIT = "ํ"  # ◌ํ
SARA_AA = "า"  # า
SARA_AM = "ำ"  # ำ

THAI = re.compile("[\u0e00-\u0e7f]")


def _chars_to_string(chars) -> str:
    out: list[str] = []
    i = 0
    n = len(chars)
    while i < n:
        ch = chars[i]["c"]
        bbox = chars[i]["bbox"]
        width = bbox[2] - bbox[0]

        if ch == " " and width <= ZERO_WIDTH:
            nxt = chars[i + 1]["c"] if i + 1 < n else ""
            if nxt == SARA_AA:
                out.append(SARA_AM)
                i += 2
                continue
            i += 1  # unmapped combining mark with no width -- drop it
            continue

        out.append(ch)
        i += 1

    text = "".join(out)
    text = text.replace(NIKHAHIT + SARA_AA, SARA_AM)
    text = _decode_pua(text)
    text = unicodedata.normalize("NFC", text)
    return text


# Symbol / Wingdings / Webdings glyphs reach the text layer as U+F000 + the
# font's own byte.  Undo that offset so a checkbox or bullet shows up as some
# readable ASCII instead of a tofu box.  Which *symbol* the byte draws depends
# on the font, so the count is reported to the manifest and the page render
# stays the authority on what the glyph actually looks like.
_PUA_LOW = re.compile("[\uf000-\uf0ff]")


def _decode_pua(text: str) -> str:
    def sub(m):
        code = ord(m.group(0)) - 0xF000
        return chr(code) if 0x20 <= code <= 0x7E else ""

    return _PUA_LOW.sub(sub, text)


def pua_count(text: str) -> int:
    """Private-use glyphs seen before decoding -- a hint to check the render."""
    return len(_PUA_LOW.findall(text))


def _blocks_to_text(raw, join_blocks: str = "\n\n") -> str:
    parts: list[str] = []
    for block in raw.get("blocks", []):
        if block.get("type") != 0:
            continue
        lines = []
        for line in block.get("lines", []):
            chars = [c for span in line.get("spans", []) for c in span.get("chars", [])]
            lines.append(_chars_to_string(chars).rstrip())
        chunk = "\n".join(lines).strip()
        if chunk:
            parts.append(chunk)
    return join_blocks.join(parts)


def page_text(page) -> str:
    """Full page text, blocks separated by a blank line."""
    return _blocks_to_text(page.get_text("rawdict"))


def clip_text(page, rect) -> str:
    """Text inside a rectangle, newlines collapsed to single spaces.

    Used for table cells, where the cell's visual line breaks are layout, not
    content.
    """
    raw = page.get_text("rawdict", clip=rect)
    text = _blocks_to_text(raw, join_blocks=" ")
    return re.sub(r"\s*\n\s*", " ", text).strip()


def has_thai(text: str) -> bool:
    return bool(THAI.search(text))


# Symptom of the bug this module fixes: a Thai consonant, a space, then SARA AA.
# After repair this pattern must not appear.  Kept so the pipeline can assert it.
BROKEN_SARA_AM = re.compile("[\u0e01-\u0e2e]\\s+\u0e32")


def broken_sara_am_count(text: str) -> int:
    return len(BROKEN_SARA_AM.findall(text))


# Some Thai PDFs carry a font whose encoding collapses SARA AA (า) into SARA AM
# (ำ), so the text layer says "กำรค้ำ" where the page plainly reads "การค้า".
# Nothing deterministic can undo that -- both characters arrive as the same
# codepoint -- so the page has to be read from its render instead.
#
# The tell is the ratio of ำ to (า + ำ).  Measured over the sample corpus,
# healthy Thai documents sit at 0.139-0.154; a collapsed one reads 0.849.
SARA_AM_RATIO_LIMIT = 0.35
MIN_THAI_FOR_RATIO = 200


def thai_stats(text: str) -> dict:
    aa = text.count(SARA_AA)
    am = text.count(SARA_AM)
    total = aa + am
    return {
        "thai_chars": len(THAI.findall(text)),
        "sara_aa": aa,
        "sara_am": am,
        "sara_am_ratio": round(am / total, 4) if total else 0.0,
    }


def thai_layer_unreliable(stats: dict) -> bool:
    """True when the text layer cannot be trusted for Thai and OCR must win."""
    return (
        stats["thai_chars"] >= MIN_THAI_FOR_RATIO
        and stats["sara_am_ratio"] > SARA_AM_RATIO_LIMIT
    )
