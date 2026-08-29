#!/usr/bin/env python3
"""Render a portable, offline, accessible HTML report from a
comprehensive-codebase-analysis v2 output tree.

Python standard library only. No network, no external dependencies, no CDNs.

Pipeline: resolve roots -> preflight validate source (fail closed) -> read all
declared documents with strict path containment -> render into a unique temp
sibling of the destination -> validate temp output -> publish by rename, with
backup/restore when replacing an existing destination.

Content-integrity rules (see references/):
  * All source text is HTML-escaped; raw HTML is never passed through.
  * Links allow only relative/hash and http(s); active schemes become inert text.
  * Images: only contained local raster/vector files within the allowlist embed;
    remote/badge images render as labeled non-loading external links.
  * Mermaid: strict validation; safe diagrams render at runtime with
    securityLevel 'strict'; unsafe/malformed diagrams stay source-only.
  * Counts/registries are derived from manifest.json; nothing is inferred.
"""

import argparse
import base64
import hashlib
import html
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = SKILL_ROOT / "assets"

REPORT_SCHEMA_VERSION = "1.0"
SOURCE_SCHEMA_VERSION = "2.0"

# Pinned Mermaid v11 asset checksum. Verified against the shipped copy at build
# time; tests recompute and compare this value.
MERMAID_SHA256 = "07e37dfa97b337ccc85365d57eddf99b9706f09db3b59b260d0333b23b343c4b"

PHASES = [
    "inventory", "architecture", "behavior", "reference-analysis",
    "debt-specialized", "operations-diagrams", "migration-onboarding", "synthesis",
]

SEVERITIES = ["critical", "high", "medium", "low"]
SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "none": 4}

MERMAID_TYPES = {
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "C4Context", "C4Container", "C4Component",
    "C4Deployment", "architecture-beta", "block-beta", "packet-beta", "journey",
    "gantt", "pie", "mindmap", "timeline", "gitGraph", "quadrantChart", "xychart-beta",
    "sankey-beta", "requirementDiagram", "zenuml",
}

# Local image allowlist (Round-1 amendment): raster + SVG, <= 1 MiB.
IMAGE_MAX_BYTES = 1024 * 1024
IMAGE_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

# Categories used to group documents in the Documents section, matched by path prefix.
DOC_CATEGORIES = [
    ("architecture/", "Architecture"),
    ("behavior/", "Behavior"),
    ("reference/", "Reference"),
    ("analysis/", "Analysis"),
    ("technical-debt/", "Technical debt"),
    ("diagrams/", "Diagrams"),
    ("migration/", "Migration"),
    ("specialized/", "Specialized"),
    ("operations/", "Operations"),
]


class ReportError(Exception):
    """Fatal, user-facing error that aborts rendering without publishing."""


# --------------------------------------------------------------------------- #
# Source contract loading and validation (fail closed)
# --------------------------------------------------------------------------- #

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ReportError("unsupported-contract: missing %s" % path.name)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReportError("unsupported-contract: cannot parse %s: %s" % (path.name, exc))


def validate_source(source_root, allow_incomplete):
    """Self-contained preflight. Returns (manifest, progress, incomplete_flag).

    Fails closed on unknown schema versions/keys. Does not modify the source.
    """
    manifest = load_json(source_root / "manifest.json")
    progress = load_json(source_root / "progress.json")

    if not isinstance(manifest, dict) or manifest.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise ReportError("unsupported-contract: manifest.schema_version must be '2.0'")
    if not isinstance(progress, dict) or progress.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise ReportError("unsupported-contract: progress.schema_version must be '2.0'")

    required_manifest = {
        "schema_version", "generated_at", "repository_root", "output_root", "coverage",
        "documents", "business_rules", "findings", "components", "test_cases",
        "traceability", "severity_counts", "delta",
    }
    unknown = set(manifest) - required_manifest
    if unknown:
        raise ReportError("unsupported-contract: unknown manifest keys %s" % sorted(unknown))
    missing = required_manifest - set(manifest)
    if missing:
        raise ReportError("unsupported-contract: missing manifest keys %s" % sorted(missing))

    # Completion predicate.
    complete = (
        progress.get("status") == "completed"
        and progress.get("current_phase") == "completed"
        and isinstance(progress.get("phases"), list)
        and [p.get("id") for p in progress["phases"]] == PHASES
        and all(p.get("status") == "completed" for p in progress["phases"])
    )
    incomplete = not complete
    if incomplete and not allow_incomplete:
        raise ReportError(
            "source is incomplete (progress not fully completed); "
            "rerun with --allow-incomplete to render with a persistent warning banner"
        )

    # Coverage integrity.
    coverage = manifest["coverage"]
    if not isinstance(coverage, dict) or coverage.get("mode") not in {"full", "focused", "sampled"}:
        raise ReportError("unsupported-contract: coverage.mode invalid")

    # Severity counts must match findings.
    counts = {level: 0 for level in SEVERITIES}
    for finding in manifest["findings"]:
        sev = finding.get("severity")
        if sev in counts:
            counts[sev] += 1
    declared = manifest["severity_counts"]
    for level in SEVERITIES:
        if declared.get(level) != counts[level]:
            raise ReportError(
                "count-mismatch: severity_counts.%s=%r but findings imply %d"
                % (level, declared.get(level), counts[level])
            )

    # BR coverage_status cross-check against traceability (input-validation error).
    linked = {t.get("business_rule") for t in manifest["traceability"] if isinstance(t, dict)}
    for rule in manifest["business_rules"]:
        alias, status = rule.get("alias"), rule.get("coverage_status")
        if status == "covered" and alias not in linked:
            raise ReportError("coverage-disagreement: %s is covered but has no traceability link" % alias)
        if status == "untested" and alias in linked:
            raise ReportError("coverage-disagreement: %s is untested but has a traceability link" % alias)

    # Documents must be a nonempty list; JSON entries are excluded from Markdown rendering.
    if not isinstance(manifest["documents"], list) or not manifest["documents"]:
        raise ReportError("unsupported-contract: documents must be a nonempty array")

    # ------------------------------------------------------------------ #
    # Normative input-contract mappings (mirror the upstream validator's
    # alias/category semantics; see comprehensive-codebase-analysis
    # scripts/validate_output.py and references/input-contract.md). These are
    # fail-closed cross-reference checks over the alias graph.
    # ------------------------------------------------------------------ #
    # Build an alias -> kind map across business rules, findings, components.
    # Kinds: 'br' (business rule), 'v'/'td' (finding registries), 'cmp' (component).
    alias_kind = {}
    for rule in manifest["business_rules"]:
        if isinstance(rule, dict) and isinstance(rule.get("alias"), str):
            alias_kind[rule["alias"]] = "br"
    for finding in manifest["findings"]:
        if isinstance(finding, dict) and isinstance(finding.get("alias"), str):
            reg = finding.get("registry")
            # Finding aliases map to their registry kind ('v' or 'td'); an unknown
            # registry is left unmapped so source_refs pointing at it fail closed.
            if reg in {"v", "td"}:
                alias_kind[finding["alias"]] = reg
    component_alias_set = set()
    for component in manifest["components"]:
        if isinstance(component, dict) and isinstance(component.get("alias"), str):
            alias_kind[component["alias"]] = "cmp"
            component_alias_set.add(component["alias"])
    test_alias_set = {
        tc.get("alias") for tc in manifest["test_cases"]
        if isinstance(tc, dict) and isinstance(tc.get("alias"), str)
    }

    # coverage.components component_alias set must equal the components alias set,
    # exactly (no missing, no extra). This is normative in the input contract.
    coverage_alias_set = {
        c.get("component_alias") for c in coverage.get("components", [])
        if isinstance(c, dict) and isinstance(c.get("component_alias"), str)
    }
    if coverage_alias_set != component_alias_set:
        only_cov = sorted(coverage_alias_set - component_alias_set)
        only_cmp = sorted(component_alias_set - coverage_alias_set)
        raise ReportError(
            "coverage-mapping: coverage.components component_alias set must equal "
            "the components alias set exactly (coverage-only=%s, components-only=%s)"
            % (only_cov, only_cmp)
        )

    # Every traceability reference must resolve: business_rule -> a BR alias,
    # test_case -> a declared test-case alias.
    for i, link in enumerate(manifest["traceability"]):
        if not isinstance(link, dict):
            raise ReportError("traceability-mapping: traceability[%d] is not an object" % i)
        br_ref = link.get("business_rule")
        tc_ref = link.get("test_case")
        if alias_kind.get(br_ref) != "br":
            raise ReportError(
                "traceability-mapping: traceability[%d] business_rule %r does not "
                "resolve to a business rule" % (i, br_ref)
            )
        if tc_ref not in test_alias_set:
            raise ReportError(
                "traceability-mapping: traceability[%d] test_case %r does not "
                "resolve to a declared test case" % (i, tc_ref)
            )

    # Every test_case.source_refs alias must resolve to a business rule, finding,
    # or component, with category semantics consistent with the upstream validator:
    #   * behavioral               -> references only BR aliases
    #   * security | infrastructure-> references only V, TD, or CMP aliases
    for i, tc in enumerate(manifest["test_cases"]):
        if not isinstance(tc, dict):
            raise ReportError("source-ref-mapping: test_cases[%d] is not an object" % i)
        category = tc.get("category")
        refs = tc.get("source_refs")
        if not isinstance(refs, list) or not refs:
            raise ReportError(
                "source-ref-mapping: test_cases[%d].source_refs must be a nonempty array" % i
            )
        for ref in refs:
            kind = alias_kind.get(ref)
            if kind not in {"br", "v", "td", "cmp"}:
                raise ReportError(
                    "source-ref-mapping: test_cases[%d].source_refs %r does not "
                    "resolve to a business rule, finding, or component" % (i, ref)
                )
            if category == "behavioral" and kind != "br":
                raise ReportError(
                    "source-ref-mapping: test_cases[%d] is behavioral but source_ref "
                    "%r resolves to %s (behavioral tests may reference only BR aliases)"
                    % (i, ref, kind)
                )
            if category in {"security", "infrastructure"} and kind not in {"v", "td", "cmp"}:
                raise ReportError(
                    "source-ref-mapping: test_cases[%d] is %s but source_ref %r resolves "
                    "to %s (security/infrastructure sources must be V, TD, or CMP)"
                    % (i, category, ref, kind)
                )

    return manifest, progress, incomplete


# --------------------------------------------------------------------------- #
# Path containment
# --------------------------------------------------------------------------- #

def contained_path(source_root, rel_path):
    """Resolve rel_path under source_root with strict containment.

    Rejects NUL, absolute/drive-prefixed paths, '..' segments, symlink escapes,
    and non-regular files. Returns the resolved Path or raises ReportError.
    """
    if not isinstance(rel_path, str) or not rel_path:
        raise ReportError("path-containment: empty path")
    if "\x00" in rel_path:
        raise ReportError("path-containment: NUL in path %r" % rel_path)
    posix = rel_path.replace("\\", "/")
    if posix.startswith("/") or re.match(r"^[A-Za-z]:", posix):
        raise ReportError("path-containment: absolute/drive path rejected %r" % rel_path)
    parts = posix.split("/")
    if any(part == ".." for part in parts):
        raise ReportError("path-containment: parent traversal rejected %r" % rel_path)

    base = source_root.resolve()
    target = (base / posix).resolve()  # resolves symlinks
    try:
        target.relative_to(base)
    except ValueError:
        raise ReportError("path-containment: escapes source root %r" % rel_path)
    if not target.exists():
        raise ReportError("path-containment: missing file %r" % rel_path)
    if not target.is_file():
        raise ReportError("path-containment: not a regular file %r" % rel_path)
    return target


# --------------------------------------------------------------------------- #
# Deterministic IDs
# --------------------------------------------------------------------------- #

class IdFactory:
    def __init__(self):
        self._seen = {}

    def make(self, raw):
        base = re.sub(r"[^a-z0-9]+", "-", str(raw).lower()).strip("-") or "id"
        n = self._seen.get(base, 0)
        self._seen[base] = n + 1
        return base if n == 0 else "%s-%d" % (base, n + 1)


def esc(text):
    return html.escape("" if text is None else str(text), quote=True)


def format_evidence(evidence):
    """Format a single evidence record's location string, HTML-escaped.

    Line-range contract (see references/input-contract.md; lines may be null in
    pairs per the upstream validator):
      * line_start and line_end both present -> "path:N-M"
      * only line_start present (line_end null) -> "path:N"
      * both null (or absent) -> "path"
    Only line_start is treated as authoritative for the leading ":N"; line_end
    extends it to a range when present.
    """
    if not isinstance(evidence, dict):
        return esc(evidence)
    path = esc(evidence.get("path"))
    start = evidence.get("line_start")
    end = evidence.get("line_end")
    if start is None:
        return path
    if end is None:
        return "%s:%s" % (path, esc(start))
    return "%s:%s-%s" % (path, esc(start), esc(end))


def format_evidence_list(records):
    """Join a list of evidence records with '; ' using format_evidence."""
    return "; ".join(format_evidence(e) for e in (records or []))


# --------------------------------------------------------------------------- #
# Link and image safety
# --------------------------------------------------------------------------- #

def classify_link(href):
    """Return (kind, value). kind in {'safe', 'external', 'inert'}.

    Contract (PLAN.md §7, references/report-content.md): only relative/hash and
    explicit http(s) links are permitted. Everything else is neutralized.

    Safe (rendered as a live in-report/relative anchor): '#'-fragments and
    clearly-relative POSIX paths ('/', './', '../', or bare relative), but NEVER
    a protocol-relative '//host' form and NEVER a backslash-containing path.
    External (rendered with rel=noreferrer noopener + visible external label):
    explicit http:// / https://, and protocol-relative '//host' (network-capable
    navigation vectors must be labeled, not silently trusted).
    Inert (neutralized, non-navigating text): active schemes (javascript:, data:,
    mailto:, vbscript:, ...) and backslash-containing UNC-style paths.
    """
    h = (href or "").strip()
    if not h:
        return ("inert", href)

    # Normalize backslashes for classification so odd forms like '\\server\share'
    # and '/\evil.com' cannot masquerade as safe relative paths.
    h2 = h.replace("\\", "/")

    # Backslash-containing hrefs (UNC-style, e.g. \\server\share) are neutralized.
    if "\\" in h:
        return ("inert", h)

    low2 = h2.lower()

    # Protocol-relative URL ('//host/...') is a network-capable external vector.
    if h2.startswith("//"):
        return ("external", h)

    # Explicit http(s) is external.
    if low2.startswith("http://") or low2.startswith("https://"):
        return ("external", h)

    # In-report fragment.
    if h2.startswith("#"):
        return ("safe", h)

    # Clearly-relative POSIX paths (single leading slash, not '//').
    if h2.startswith("/") or h2.startswith("./") or h2.startswith("../"):
        return ("safe", h)

    # Bare relative path without scheme, without leading slash, without '//'.
    if ":" not in h2.split("/")[0]:
        return ("safe", h)

    return ("inert", h)  # active scheme (javascript:, data:, mailto:, etc.)


def render_link(href, text_html):
    kind, value = classify_link(href)
    if kind == "safe":
        return '<a href="%s">%s</a>' % (esc(value), text_html)
    if kind == "external":
        return ('<a href="%s" rel="noreferrer noopener">%s</a>'
                '<span class="external-link-note"> (external link)</span>'
                % (esc(value), text_html))
    # inert
    return '%s <span class="external-link-note">(inert link: %s)</span>' % (text_html, esc(value))


def render_image(source_root, src, alt):
    """Render a Markdown image. Local contained images within the allowlist embed
    as data URLs; everything else becomes a labeled, non-loading link/placeholder.
    Never emits a remote-loading <img>.
    """
    kind, value = classify_link(src)
    alt_html = esc(alt)
    if kind == "external":
        return ('<a href="%s" rel="noreferrer noopener">%s</a>'
                '<span class="external-link-note"> (external image, not loaded)</span>'
                % (esc(value), alt_html or esc(value)))
    if kind == "inert":
        return '<span class="md-image-placeholder">image omitted: %s</span>' % (alt_html or esc(value))
    # safe/relative -> attempt contained embed
    try:
        target = contained_path(source_root, value)
    except ReportError:
        return '<span class="md-image-placeholder">image unavailable: %s</span>' % (alt_html or esc(value))
    ext = target.suffix.lower()
    if ext not in IMAGE_MIME:
        return '<span class="md-image-placeholder">unsupported image type: %s</span>' % esc(value)
    try:
        data = target.read_bytes()
    except OSError:
        return '<span class="md-image-placeholder">image unreadable: %s</span>' % esc(value)
    if len(data) > IMAGE_MAX_BYTES:
        return '<span class="md-image-placeholder">image too large: %s</span>' % esc(value)
    if ext == ".svg":
        embedded = sanitize_svg(data)
        if embedded is None:
            return '<span class="md-image-placeholder">unsafe SVG omitted: %s</span>' % esc(value)
        b64 = base64.b64encode(embedded).decode("ascii")
    else:
        b64 = base64.b64encode(data).decode("ascii")
    return '<img class="md-image" alt="%s" src="data:%s;base64,%s">' % (alt_html, IMAGE_MIME[ext], b64)


def sanitize_svg(data):
    """Return sanitized SVG bytes or None if it must be rejected.

    Rejects (does not attempt to clean) any SVG containing <script>, event
    handler attributes, <foreignObject>, or external href/xlink:href references.
    """
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError:
        return None
    low = text.lower()
    if "<script" in low or "<foreignobject" in low:
        return None
    if re.search(r"\son\w+\s*=", text, re.IGNORECASE):
        return None
    # external href / xlink:href referencing anything other than a local fragment
    for m in re.finditer(r'(?:xlink:href|href)\s*=\s*"([^"]*)"', text, re.IGNORECASE):
        val = m.group(1).strip().lower()
        if val and not val.startswith("#"):
            return None
    return text.encode("utf-8")


# --------------------------------------------------------------------------- #
# Inline Markdown (bounded subset, escape-first)
# --------------------------------------------------------------------------- #

def render_inline(source_root, text):
    """Render inline Markdown from already-*unescaped* source text.

    Strategy: tokenize into code spans / images / links first (so their content
    is handled explicitly), escape everything else, then apply emphasis on the
    escaped stream. Raw HTML angle brackets are escaped, never passed through.
    """
    out = []
    i = 0
    n = len(text)
    pattern = re.compile(
        r"`([^`]+)`"                                  # 1: inline code
        r"|!\[([^\]]*)\]\(([^)]*)\)"                  # 2 alt, 3 src (image)
        r"|\[([^\]]*)\]\(([^)]*)\)"                   # 4 text, 5 href (link)
    )
    while i < n:
        m = pattern.search(text, i)
        if not m:
            out.append(apply_emphasis(esc(text[i:])))
            break
        if m.start() > i:
            out.append(apply_emphasis(esc(text[i:m.start()])))
        if m.group(1) is not None:
            out.append("<code>%s</code>" % esc(m.group(1)))
        elif m.group(2) is not None or (m.group(3) is not None and text[m.start()] == "!"):
            out.append(render_image(source_root, m.group(3), m.group(2)))
        else:
            inner = apply_emphasis(esc(m.group(4)))
            out.append(render_link(m.group(5), inner))
        i = m.end()
    return "".join(out)


def apply_emphasis(escaped_text):
    """Apply bold/italic on already-HTML-escaped text. Safe because ** and * are
    not affected by escaping and we only insert fixed tags."""
    escaped_text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped_text)
    escaped_text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped_text)
    escaped_text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", escaped_text)
    return escaped_text


# --------------------------------------------------------------------------- #
# Mermaid validation (mirrors source validator semantics)
# --------------------------------------------------------------------------- #

def mermaid_balanced(block):
    """Quote/escape/comment/edge-aware bracket balance (matches source validator)."""
    stack = []
    pairs = {"]": "[", ")": "(", "}": "{"}
    openers = set(pairs.values())
    in_quote = False
    escaped = False
    for line in block.splitlines():
        if line.lstrip().startswith("%%"):
            continue
        for index, char in enumerate(line):
            if escaped:
                escaped = False
                continue
            if char == "\\" and in_quote:
                escaped = True
                continue
            if char == '"':
                in_quote = not in_quote
                continue
            if in_quote:
                continue
            previous = line[index - 1] if index else ""
            following = line[index + 1] if index + 1 < len(line) else ""
            if char == "{" and previous and previous in "o|":
                continue
            if char == "}" and following and following in "o|":
                continue
            if char in openers:
                stack.append(char)
            elif char in pairs:
                if not stack or stack.pop() != pairs[char]:
                    return False
    return not stack and not in_quote


# HTML element names whose presence in diagram source disqualifies runtime
# rendering. Matching by real element name (rather than any <word> span) keeps
# idiomatic Mermaid safe: UML stereotypes (<<fork>>, <<interface>>) and generic
# type names (Task<JsonResult>) are not HTML. Unterminated tag-opens are caught
# too, so classification never depends on a later ">". The runtime additionally
# disables htmlLabels, so label text can never become live HTML.
HTML_TAG_NAMES = frozenset("""
a abbr address area article aside audio b base bdi bdo blockquote body br
button canvas caption cite code col colgroup data datalist dd del details dfn
dialog div dl dt em embed fieldset figcaption figure footer foreignobject form
h1 h2 h3 h4 h5 h6 head header hgroup hr html i iframe img input ins kbd label
legend li link main map mark math menu meta meter nav noscript object ol
optgroup option output p param picture pre progress q rp rt ruby s samp script
section select slot small source span strong style sub summary sup svg table
tbody td template textarea tfoot th thead time title tr track u ul use var
video wbr xmp
""".split())


def classify_mermaid(block):
    """Return (safe: bool, reason: str). A diagram is source-only when unsupported,
    malformed, contains raw HTML tags, or contains an init/config directive."""
    tokens = block.strip().split()
    diagram_type = tokens[0] if tokens else ""
    # Directives that weaken security are treated as source-only fallback. Check
    # first so a leading %%{init}%% directive is reported accurately even though
    # it displaces the diagram-type token.
    if re.search(r"%%\{\s*init", block) or re.search(r"%%\{\s*config", block):
        return (False, "configuration directive present")
    if diagram_type not in MERMAID_TYPES:
        return (False, "unsupported diagram type")
    # Raw HTML tags disqualify runtime rendering. Mask stereotype spans first,
    # then reject any tag-open (terminated or not) naming a real HTML element.
    probe = re.sub(r"<<[^<>]*>>", "", block)
    for m in re.finditer(r"</?\s*([a-zA-Z][a-zA-Z0-9-]*)", probe):
        if m.group(1).lower() in HTML_TAG_NAMES:
            return (False, "raw HTML tag present")
    if not mermaid_balanced(block):
        return (False, "unbalanced brackets or quotes")
    return (True, "")


# --------------------------------------------------------------------------- #
# Block Markdown
# --------------------------------------------------------------------------- #

def render_markdown(source_root, text, ids, heading_offset=0):
    """Render a bounded Markdown subset to safe HTML.

    heading_offset demotes embedded document headings (clamped at h6) so a
    document's h1 nests correctly under the surrounding page hierarchy."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i = 0
    n = len(lines)
    last_heading = [""]  # nearest preceding heading text, for table region labels

    def flush_paragraph(buf):
        if buf:
            out.append("<p>%s</p>" % render_inline(source_root, " ".join(buf).strip()))
            buf.clear()

    para = []
    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Fenced code / mermaid
        fence = re.match(r"^```([A-Za-z0-9_-]*)\s*$", stripped)
        if fence:
            flush_paragraph(para)
            lang = fence.group(1)
            body = []
            i += 1
            while i < n and not re.match(r"^```\s*$", lines[i].strip()):
                body.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            code = "\n".join(body)
            if lang == "mermaid":
                out.append(render_mermaid_block(code, ids))
            else:
                out.append("<pre><code>%s</code></pre>" % esc(code))
            continue

        if not stripped:
            flush_paragraph(para)
            i += 1
            continue

        # Headings (demoted by heading_offset, clamped at h6)
        h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if h:
            flush_paragraph(para)
            level = min(6, len(h.group(1)) + heading_offset)
            last_heading[0] = h.group(2)
            out.append("<h%d>%s</h%d>" % (level, render_inline(source_root, h.group(2)), level))
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            flush_paragraph(para)
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>"
                       % render_inline(source_root, " ".join(q.strip() for q in quote)))
            continue

        # Table (pipe with a separator row)
        if "|" in line and i + 1 < n and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]) and "-" in lines[i + 1]:
            flush_paragraph(para)
            i = render_table(source_root, lines, i, out, last_heading[0])
            continue

        # Lists (unordered / ordered)
        if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph(para)
            i = render_list(source_root, lines, i, out)
            continue

        para.append(stripped)
        i += 1

    flush_paragraph(para)
    return "\n".join(out)


def render_list(source_root, lines, i, out):
    n = len(lines)
    ordered = bool(re.match(r"^\s*\d+\.\s+", lines[i]))
    tag = "ol" if ordered else "ul"
    items = []
    while i < n:
        m = re.match(r"^\s*(?:[-*+]|\d+\.)\s+(.*)$", lines[i])
        if not m:
            if lines[i].strip() == "":
                # allow a single blank line inside a list only if next is a list item
                if i + 1 < n and re.match(r"^\s*(?:[-*+]|\d+\.)\s+", lines[i + 1]):
                    i += 1
                    continue
            break
        items.append(render_inline(source_root, m.group(1)))
        i += 1
    out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % it for it in items), tag))
    return i


def render_table(source_root, lines, i, out, context_heading=""):
    n = len(lines)

    def cells(row):
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]

    header = cells(lines[i])
    i += 2  # skip header + separator
    body_rows = []
    while i < n and "|" in lines[i] and lines[i].strip():
        body_rows.append(cells(lines[i]))
        i += 1
    thead = "".join("<th scope=\"col\">%s</th>" % render_inline(source_root, c) for c in header)
    tbody = ""
    for row in body_rows:
        tds = "".join("<td>%s</td>" % render_inline(source_root, c) for c in row)
        tbody += "<tr>%s</tr>" % tds
    label = ("Table: %s" % context_heading) if context_heading else "Table"
    out.append(
        '<div class="table-scroll" role="region" tabindex="0" aria-label="%s">'
        '<table aria-label="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
        % (esc(label), esc(label), thead, tbody)
    )
    return i


def render_mermaid_block(code, ids):
    safe, reason = classify_mermaid(code)
    diag_id = ids.make("diagram")
    src_id = ids.make(diag_id + "-source")
    escaped = esc(code)
    if safe:
        label = "Diagram (interactive rendering requires JavaScript; source shown below)."
        rendered = '<div class="mermaid-rendered" hidden aria-hidden="true"></div>'
        source_block = (
            '<details class="mermaid-source disclosure" open>'
            '<summary>Diagram source</summary>'
            '<pre id="%s"><code>%s</code></pre>'
            '</details>' % (src_id, escaped)
        )
        return (
            '<figure class="diagram" data-mermaid-safe="true">'
            '<figcaption class="diagram-fallback-label">%s</figcaption>'
            '%s%s</figure>' % (esc(label), rendered, source_block)
        )
    label = "Diagram shown as source (%s)." % esc(reason)
    return (
        '<figure class="diagram" data-mermaid-safe="false">'
        '<figcaption class="diagram-fallback-label">%s</figcaption>'
        '<pre class="mermaid-source" id="%s"><code>%s</code></pre>'
        '</figure>' % (label, src_id, escaped)
    )


# --------------------------------------------------------------------------- #
# HTML sections built from structured manifest data
# --------------------------------------------------------------------------- #

def badge(sev):
    return '<span class="badge" data-sev="%s">%s</span>' % (esc(sev), esc(sev))


def section_overview(manifest, incomplete, ids):
    coverage = manifest["coverage"]
    counts = manifest["severity_counts"]
    findings = manifest["findings"]
    rules = manifest["business_rules"]

    cards = "".join(
        '<div class="card"><div class="metric">%d</div>'
        '<div class="label">%s findings</div></div>' % (counts.get(s, 0), s)
        for s in SEVERITIES
    )

    # Confidence distribution computed from current records.
    conf = {"verified": 0, "inferred": 0, "assumption": 0}
    for f in findings:
        if f.get("confidence") in conf:
            conf[f["confidence"]] += 1
    conf_rows = "".join(
        "<tr><td>%s</td><td data-sort=\"%d\">%d</td></tr>" % (esc(k), v, v)
        for k, v in conf.items()
    )

    # Top open findings: status open, ordered by severity then alias.
    open_findings = sorted(
        [f for f in findings if f.get("status") == "open"],
        key=lambda f: (SEVERITY_RANK.get(f.get("severity"), 9), f.get("alias", "")),
    )
    top_rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(f.get("alias")), badge(f.get("severity")), render_inline_plain(f.get("title")))
        for f in open_findings[:10]
    ) or "<tr><td colspan=\"3\">No open findings.</td></tr>"

    delta = manifest["delta"]
    delta_rows = "".join(
        "<tr><td>%s</td><td data-sort=\"%d\">%d</td></tr>" % (esc(state), len(delta.get(state, [])), len(delta.get(state, [])))
        for state in ("new", "resolved", "regressed", "persisted")
    )
    # prior_manifest_loaded is preserved exactly; when false the "since prior
    # run" framing would mislead, so say this is the first recorded run.
    if delta.get("prior_manifest_loaded"):
        prior_html = "<p>Prior manifest loaded: <strong>yes</strong>.</p>"
    else:
        prior_html = ("<p>Prior manifest loaded: <strong>no</strong> &mdash; first recorded "
                      "analysis run; delta states reflect this run only.</p>")

    limitations = "".join("<li>%s</li>" % esc(x) for x in coverage.get("limitations", [])) or "<li>None recorded.</li>"

    # Reading routes: stable section anchors plus direct links to the reading
    # guide and migration/operations source documents when the source declares them.
    routes = ['<li><a href="#findings">Complete findings registry</a></li>',
              '<li><a href="#documents">Full analysis documents</a></li>']
    for d in manifest["documents"]:
        p = str(d.get("path", ""))
        if p.endswith(".md") and ("reading-guide" in p or p.startswith("migration/") or p.startswith("operations/")):
            anchor = "doc-" + (re.sub(r"[^a-z0-9]+", "-", p[:-3].replace("/", "-").lower()).strip("-") or "id")
            routes.append('<li><a href="#%s"><code>%s</code></a></li>' % (esc(anchor), esc(p)))
    routes_html = "".join(routes)

    banner = ""
    if incomplete:
        banner = ('<div class="warning-banner" role="alert">Source analysis is incomplete. '
                  'Counts and registries reflect a partial run and may change.</div>')

    return """
<section id="overview" class="report-section" aria-labelledby="overview-h">
  <h2 id="overview-h">Overview</h2>
  {banner}
  <p>Coverage mode: <strong>{mode}</strong>. Repository: <code>{repo}</code>.</p>
  <h3>Severity counts</h3>
  <div class="card-grid">{cards}</div>
  <h3>Top open findings</h3>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Top open findings">
  <table><caption>Open findings ordered by severity then alias</caption>
    <thead><tr><th scope="col">Alias</th><th scope="col">Severity</th><th scope="col">Title</th></tr></thead>
    <tbody>{top_rows}</tbody></table></div>
  <h3>Confidence distribution (findings)</h3>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Confidence distribution">
  <table><caption>Finding confidence distribution</caption>
    <thead><tr><th scope="col">Confidence</th><th scope="col">Count</th></tr></thead>
    <tbody>{conf_rows}</tbody></table></div>
  <h3>Delta since prior run</h3>
  {prior_html}
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Delta state counts">
  <table><caption>Delta state counts</caption>
    <thead><tr><th scope="col">State</th><th scope="col">Count</th></tr></thead>
    <tbody>{delta_rows}</tbody></table></div>
  <h3>Coverage limitations</h3>
  <ul>{limitations}</ul>
  <h3>Reading routes</h3>
  <ul>{routes_html}</ul>
</section>
""".format(banner=banner, mode=esc(coverage.get("mode")), repo=esc(manifest.get("repository_root")),
           cards=cards, top_rows=top_rows, conf_rows=conf_rows, delta_rows=delta_rows,
           prior_html=prior_html, limitations=limitations, routes_html=routes_html)


def render_inline_plain(text):
    """Escape plain text (titles etc.) without Markdown interpretation."""
    return esc(text)


def section_findings(manifest):
    findings = sorted(
        manifest["findings"],
        key=lambda f: (SEVERITY_RANK.get(f.get("severity"), 9), f.get("alias", "")),
    )
    rows = []
    for f in findings:
        ev = format_evidence_list(f.get("evidence", []))
        rows.append(
            '<tr data-severity="%s" data-status="%s" data-registry="%s" id="finding-%s">'
            '<td>%s</td><td data-sort="%d">%s</td><td>%s</td><td>%s</td><td>%s</td><td><code>%s</code></td></tr>'
            % (esc(f.get("severity")), esc(f.get("status")), esc(f.get("registry")), esc(f.get("alias")),
               esc(f.get("alias")), SEVERITY_RANK.get(f.get("severity"), 9), badge(f.get("severity")),
               esc(f.get("status")), esc(f.get("confidence")), render_inline_plain(f.get("title")), ev)
        )
    body = "".join(rows) or "<tr><td colspan=\"6\">No findings.</td></tr>"
    return """
<section id="findings" class="report-section" aria-labelledby="findings-h">
  <h2 id="findings-h">Findings</h2>
  <div class="filter-bar">
    <label for="finding-sev-filter">Filter by severity</label>
    <select id="finding-sev-filter" data-filter-for="findings-table" data-filter-attr="severity" data-filter-status="findings-filter-status">
      <option value="all">All severities</option>
      <option value="critical">Critical</option>
      <option value="high">High</option>
      <option value="medium">Medium</option>
      <option value="low">Low</option>
    </select>
    <span id="findings-filter-status" class="filter-status" aria-live="polite"></span>
  </div>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Complete findings registry">
  <table id="findings-table" data-sortable><caption>Complete findings registry</caption>
    <thead><tr>
      <th scope="col"><button type="button" class="sort-btn">Alias</button></th>
      <th scope="col" data-type="severity" aria-sort="none"><button type="button" class="sort-btn">Severity</button></th>
      <th scope="col"><button type="button" class="sort-btn">Status</button></th>
      <th scope="col"><button type="button" class="sort-btn">Confidence</button></th>
      <th scope="col">Title</th>
      <th scope="col">Evidence</th>
    </tr></thead>
    <tbody>{body}</tbody></table></div>
</section>
""".format(body=body)


def section_business_rules(manifest):
    rows = []
    for r in manifest["business_rules"]:
        ev = format_evidence_list(r.get("evidence", []))
        rows.append(
            '<tr data-coverage="%s" id="rule-%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><code>%s</code></td></tr>'
            % (esc(r.get("coverage_status")), esc(r.get("alias")), esc(r.get("alias")),
               esc(r.get("coverage_status")), esc(r.get("confidence")), render_inline_plain(r.get("rule")), ev)
        )
    body = "".join(rows) or "<tr><td colspan=\"5\">No business rules.</td></tr>"
    return """
<section id="business-rules" class="report-section" aria-labelledby="br-h">
  <h2 id="br-h">Business rules</h2>
  <div class="filter-bar">
    <label for="br-cov-filter">Filter by coverage</label>
    <select id="br-cov-filter" data-filter-for="br-table" data-filter-attr="coverage" data-filter-status="br-filter-status">
      <option value="all">All</option>
      <option value="covered">Covered</option>
      <option value="untested">Untested</option>
    </select>
    <span id="br-filter-status" class="filter-status" aria-live="polite"></span>
  </div>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Complete business rule registry">
  <table id="br-table" data-sortable><caption>Complete business rule registry</caption>
    <thead><tr>
      <th scope="col"><button type="button" class="sort-btn">Alias</button></th>
      <th scope="col"><button type="button" class="sort-btn">Coverage</button></th>
      <th scope="col"><button type="button" class="sort-btn">Confidence</button></th>
      <th scope="col">Rule</th>
      <th scope="col">Evidence</th>
    </tr></thead>
    <tbody>{body}</tbody></table></div>
</section>
""".format(body=body)


def section_components(manifest):
    depth_by_alias = {
        c.get("component_alias"): c.get("depth")
        for c in manifest["coverage"].get("components", [])
    }
    rows = []
    for c in manifest["components"]:
        rows.append(
            '<tr id="component-%s"><td>%s</td><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td></tr>'
            % (esc(c.get("alias")), esc(c.get("alias")), esc(c.get("name")), esc(c.get("path")),
               esc(c.get("namespace") if c.get("namespace") is not None else "\u2014"),
               esc(depth_by_alias.get(c.get("alias"), "\u2014")))
        )
    body = "".join(rows) or "<tr><td colspan=\"5\">No components.</td></tr>"
    return """
<section id="components" class="report-section" aria-labelledby="cmp-h">
  <h2 id="cmp-h">Components</h2>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Complete component registry">
  <table id="cmp-table" data-sortable><caption>Complete component registry with analysis depth</caption>
    <thead><tr>
      <th scope="col"><button type="button" class="sort-btn">Alias</button></th>
      <th scope="col"><button type="button" class="sort-btn">Name</button></th>
      <th scope="col">Path</th>
      <th scope="col">Namespace</th>
      <th scope="col"><button type="button" class="sort-btn">Analysis depth</button></th>
    </tr></thead>
    <tbody>{body}</tbody></table></div>
</section>
""".format(body=body)


def section_tests(manifest):
    linked_brs = {t.get("business_rule") for t in manifest["traceability"]}
    test_rows = []
    for tc in manifest["test_cases"]:
        refs = ", ".join(esc(r) for r in tc.get("source_refs", []))
        test_rows.append(
            '<tr id="test-%s"><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (esc(tc.get("alias")), esc(tc.get("alias")), esc(tc.get("category")),
               esc(tc.get("status")), render_inline_plain(tc.get("title")), refs)
        )
    tbody = "".join(test_rows) or "<tr><td colspan=\"5\">No test cases.</td></tr>"

    trace_rows = "".join(
        "<tr><td>%s</td><td>%s</td></tr>" % (esc(t.get("business_rule")), esc(t.get("test_case")))
        for t in manifest["traceability"]
    ) or "<tr><td colspan=\"2\">No links.</td></tr>"

    untested = [r.get("alias") for r in manifest["business_rules"] if r.get("coverage_status") == "untested"]
    untested_html = "".join("<li>%s</li>" % esc(a) for a in untested) or "<li>None: all rules are covered.</li>"

    return """
<section id="tests" class="report-section" aria-labelledby="tests-h">
  <h2 id="tests-h">Tests &amp; traceability</h2>
  <h3>Test specifications and existing tests</h3>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Test case registry">
  <table id="tc-table" data-sortable><caption>Test case registry</caption>
    <thead><tr>
      <th scope="col"><button type="button" class="sort-btn">Alias</button></th>
      <th scope="col"><button type="button" class="sort-btn">Category</button></th>
      <th scope="col"><button type="button" class="sort-btn">Status</button></th>
      <th scope="col">Title</th>
      <th scope="col">Source refs</th>
    </tr></thead>
    <tbody>{tbody}</tbody></table></div>
  <h3>Business rule &#8596; test case links</h3>
  <div class="table-scroll" role="region" tabindex="0" aria-label="Table: Traceability links">
  <table><caption>Traceability links</caption>
    <thead><tr><th scope="col">Business rule</th><th scope="col">Test case</th></tr></thead>
    <tbody>{trace_rows}</tbody></table></div>
  <h3>Untested business rules</h3>
  <ul>{untested_html}</ul>
</section>
""".format(tbody=tbody, trace_rows=trace_rows, untested_html=untested_html)


def section_documents(source_root, manifest, ids):
    """Render every declared Markdown document in full, grouped by category.
    JSON entries are excluded from Markdown rendering (surfaced in About)."""
    md_docs = [d for d in manifest["documents"] if str(d.get("path", "")).endswith(".md")]

    def category_of(path):
        for prefix, label in DOC_CATEGORIES:
            if path.startswith(prefix):
                return label
        return "Overview documents"

    grouped = {}
    order = []
    for doc in md_docs:
        path = doc["path"]
        cat = category_of(path)
        if cat not in grouped:
            grouped[cat] = []
            order.append(cat)
        grouped[cat].append(doc)

    blocks = []
    for cat in order:
        blocks.append('<h3>%s</h3>' % esc(cat))
        for doc in grouped[cat]:
            path = doc["path"]
            target = contained_path(source_root, path)
            try:
                text = target.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                raise ReportError("unreadable document: %s (%s)" % (path, exc))
            anchor = "doc-" + ids.make(path.replace("/", "-").replace(".md", ""))
            panel_id = anchor + "-panel"
            # Embedded document headings are demoted so a doc h1 nests as h5
            # under the h4 disclosure title (page h1 > section h2 > category h3).
            rendered = render_markdown(source_root, text, ids, heading_offset=4)
            blocks.append(
                '<article class="disclosure" id="%s">'
                '<h4 style="margin:0"><button type="button" class="disclosure-toggle" '
                'aria-expanded="true" aria-controls="%s">%s %s</button></h4>'
                '<div class="disclosure-panel" id="%s">'
                '<p class="filter-status">%s</p>%s</div></article>'
                % (anchor, panel_id, esc(path), badge(doc.get("severity_badge", "none")),
                   panel_id, esc(doc.get("description", "")), rendered)
            )

    return """
<section id="documents" class="report-section" aria-labelledby="docs-h">
  <h2 id="docs-h">Documents</h2>
  <p>Every declared Markdown document is rendered below in source order. Machine
  data files are referenced in About this report.</p>
  {blocks}
</section>
""".format(blocks="\n".join(blocks))


def section_about(manifest, progress, incomplete):
    json_docs = [d["path"] for d in manifest["documents"] if not str(d.get("path", "")).endswith(".md")]
    json_html = "".join("<li><code>%s</code></li>" % esc(p) for p in json_docs) or "<li>None</li>"
    return """
<section id="about" class="report-section" aria-labelledby="about-h">
  <h2 id="about-h">About this report</h2>
  <ul>
    <li>Source schema version: <strong>{ssv}</strong></li>
    <li>Source generated at: <strong>{sga}</strong></li>
    <li>Source completion: <strong>{completion}</strong></li>
    <li>Generation method: deterministic offline render (Python standard library); no code executed, no network access.</li>
    <li>Privacy/offline: this report loads no external scripts, styles, fonts, images, or trackers. Mermaid runs from a local, version-pinned asset.</li>
  </ul>
  <h3>Source data references</h3>
  <ul>{json_html}</ul>
</section>
""".format(ssv=esc(manifest.get("schema_version")), sga=esc(manifest.get("generated_at")),
           completion=("incomplete" if incomplete else "completed"), json_html=json_html)


# --------------------------------------------------------------------------- #
# Page assembly
# --------------------------------------------------------------------------- #

THEME_HEAD_SCRIPT = """
(function(){try{var k="car:theme:v1";var p;try{p=localStorage.getItem(k);}catch(e){p=null;}
if(p!=="light"&&p!=="dark"&&p!=="system"){p="system";}
var d=(p==="dark")||(p==="system"&&window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches);
var t=d?"dark":"light";var r=document.documentElement;r.setAttribute("data-theme",t);r.style.colorScheme=t;}catch(e){}})();
"""


def build_html(source_root, manifest, progress, incomplete, css, js):
    ids = IdFactory()
    nav = [
        ("overview", "Overview"),
        ("findings", "Findings"),
        ("business-rules", "Business rules"),
        ("components", "Components"),
        ("tests", "Tests & traceability"),
        ("documents", "Documents"),
        ("about", "About this report"),
    ]
    nav_html = "".join(
        '<li><a href="#%s"%s>%s</a></li>' % (sid, (' aria-current="true"' if i == 0 else ""), esc(label))
        for i, (sid, label) in enumerate(nav)
    )

    sections = [
        section_overview(manifest, incomplete, ids),
        section_findings(manifest),
        section_business_rules(manifest),
        section_components(manifest),
        section_tests(manifest),
        section_documents(source_root, manifest, ids),
        section_about(manifest, progress, incomplete),
    ]

    return """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Codebase analysis report</title>
<script>{head_script}</script>
<style>{css}</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>
<div class="layout">
<aside class="sidebar" aria-label="Report sections">
  <p class="nav-heading">Sections</p>
  <nav aria-label="Report navigation"><ul>{nav_html}</ul></nav>
</aside>
<div class="main">
  <header class="toolbar">
    <h1 class="title">Codebase analysis report</h1>
    <div class="theme-control" role="group" aria-label="Theme">
      <button type="button" data-theme-choice="system" aria-pressed="true">System</button>
      <button type="button" data-theme-choice="light" aria-pressed="false">Light</button>
      <button type="button" data-theme-choice="dark" aria-pressed="false">Dark</button>
    </div>
    <span id="theme-status" class="visually-hidden" role="status" aria-live="polite">Theme: System</span>
  </header>
  <main id="main-content" class="content">
    {sections}
  </main>
</div>
</div>
<script src="assets/mermaid.min.js"></script>
<script>{js}</script>
</body>
</html>
""".format(head_script=THEME_HEAD_SCRIPT.strip(), css=css, nav_html=nav_html,
           sections="\n".join(sections), js=js)


# --------------------------------------------------------------------------- #
# Report manifest and integrity
# --------------------------------------------------------------------------- #

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def build_report_manifest(manifest, incomplete, generated_at, index_bytes, mermaid_sha):
    md_docs = [d["path"] for d in manifest["documents"] if str(d.get("path", "")).endswith(".md")]
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "report_generated_at": generated_at,
        "source_schema_version": SOURCE_SCHEMA_VERSION,
        "source_generated_at": manifest.get("generated_at"),
        "source_incomplete": incomplete,
        "source_prior_manifest_loaded": bool(manifest["delta"].get("prior_manifest_loaded")),
        "documents": md_docs,
        "counts": {
            "severity": {s: manifest["severity_counts"].get(s, 0) for s in SEVERITIES},
            "business_rules": len(manifest["business_rules"]),
            "findings": len(manifest["findings"]),
            "components": len(manifest["components"]),
            "test_cases": len(manifest["test_cases"]),
            "traceability_links": len(manifest["traceability"]),
        },
        "mermaid_sha256": mermaid_sha,
        "generated_files": {
            "index.html": sha256_bytes(index_bytes),
            "assets/mermaid.min.js": mermaid_sha,
        },
    }


# --------------------------------------------------------------------------- #
# Publication (temp -> validate -> rename, with backup/restore)
# --------------------------------------------------------------------------- #

def unique_sibling(dest, suffix):
    parent = dest.parent
    base = dest.name
    n = 0
    while True:
        candidate = parent / (".%s.%s%s" % (base, suffix, "" if n == 0 else "-%d" % n))
        if not candidate.exists():
            return candidate
        n += 1


def write_report_tree(temp_dir, index_html, report_manifest):
    (temp_dir / "assets").mkdir(parents=True, exist_ok=True)
    index_path = temp_dir / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    shutil.copy2(ASSETS_DIR / "mermaid.min.js", temp_dir / "assets" / "mermaid.min.js")
    (temp_dir / "report-manifest.json").write_text(
        json.dumps(report_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return index_path


def publish(temp_dir, dest, allow_replace):
    """Publish validated temp output to dest. Never intentionally publishes
    unvalidated output. Not claimed transactionally atomic across the backup step."""
    if dest.exists():
        if not allow_replace:
            raise ReportError(
                "output-collision: destination %s already exists; ask the user to approve "
                "replacement, then rerun with --replace (existing output is backed up)" % dest
            )
        backup = unique_sibling(dest, "backup")
        os.rename(str(dest), str(backup))
        try:
            os.rename(str(temp_dir), str(dest))
        except OSError:
            os.rename(str(backup), str(dest))  # restore
            raise ReportError("publish failed; restored prior output at %s" % dest)
        # Remove the backup only after the published destination re-validates.
        from validate_report import validate_report_dir  # local import; same dir
        errors = validate_report_dir(dest)
        if errors:
            failed = unique_sibling(dest, "failed")
            os.rename(str(dest), str(failed))
            os.rename(str(backup), str(dest))
            raise ReportError(
                "published output failed final validation; restored prior output at %s "
                "(failed output kept at %s)" % (dest, failed)
            )
        shutil.rmtree(str(backup), ignore_errors=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.rename(str(temp_dir), str(dest))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv):
    parser = argparse.ArgumentParser(description="Render an offline HTML report from a v2 analysis tree.")
    parser.add_argument("--source", required=True, help="analysis output root (contains manifest.json)")
    parser.add_argument("--output", required=True, help="report destination directory (resolved, announced)")
    parser.add_argument("--replace", action="store_true", help="replace an existing destination (with backup/restore)")
    parser.add_argument("--allow-incomplete", action="store_true", help="render an incomplete source with a warning banner")
    parser.add_argument("--generated-at", default=None, help="fixed report timestamp for reproducible fixtures")
    args = parser.parse_args(argv[1:])

    source_root = Path(args.source).resolve()
    dest = Path(args.output).resolve()
    if not source_root.is_dir():
        print("ERROR: source root is not a directory: %s" % source_root, file=sys.stderr)
        return 2

    print("Resolved source: %s" % source_root)
    print("Resolved output: %s" % dest)

    try:
        manifest, progress, incomplete = validate_source(source_root, args.allow_incomplete)
        css = (ASSETS_DIR / "report.css").read_text(encoding="utf-8")
        js = (ASSETS_DIR / "report.js").read_text(encoding="utf-8")

        mermaid_sha = sha256_file(ASSETS_DIR / "mermaid.min.js")
        if mermaid_sha != MERMAID_SHA256:
            raise ReportError("integrity: pinned Mermaid asset checksum mismatch")

        generated_at = args.generated_at or _now_iso()
        index_html = build_html(source_root, manifest, progress, incomplete, css, js)
        index_bytes = index_html.encode("utf-8")
        report_manifest = build_report_manifest(manifest, incomplete, generated_at, index_bytes, mermaid_sha)

        temp_dir = unique_sibling(dest, "tmp")
        temp_dir.mkdir(parents=True, exist_ok=False)
        try:
            write_report_tree(temp_dir, index_html, report_manifest)
            # Validate temp output before publishing.
            from validate_report import validate_report_dir  # local import; same dir
            errors = validate_report_dir(temp_dir)
            if errors:
                raise ReportError("temp report failed validation: %s" % "; ".join(errors[:5]))
            publish(temp_dir, dest, args.replace)
        finally:
            if temp_dir.exists():
                shutil.rmtree(str(temp_dir), ignore_errors=True)
    except ReportError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 1

    print("Report published: %s" % dest)
    print("Source status: %s" % ("incomplete" if incomplete else "completed"))
    print("Severity counts: %s" % manifest["severity_counts"])
    print("Validation: passed")
    return 0


def _now_iso():
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv))
