#!/usr/bin/env python3
"""Comprehensive self-test for the codebase-analysis-report skill.

Python standard library only. Uses temporary directories exclusively; creates no
authoring evidence in the shipped skill. The required --fixture points at any
valid, completed v2 analysis output tree (typically the analysis root being
reported); derived mutation fixtures are built in temp directories.

Run:  python3 test_report.py --fixture PATH
Exit: 0 when all tests pass, 1 otherwise.
"""

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render_report as R
import validate_report as V

# No default fixture: the suite requires --fixture pointing at any valid,
# completed v2 output tree (typically the analysis root being reported). A
# hard-coded authoring path would be authoring state inside the shipped skill.
FIXTURE = None
FIXED_TS = "2026-08-29T00:00:00Z"


def copy_fixture(dst):
    shutil.copytree(FIXTURE, dst)
    for p in Path(dst).rglob("*"):
        if p.is_file():
            os.chmod(p, 0o644)
    return Path(dst)


def load_manifest(root):
    return json.loads((root / "manifest.json").read_text())


def write_manifest(root, manifest):
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def render(source, output, **kw):
    argv = ["render_report.py", "--source", str(source), "--output", str(output),
            "--generated-at", FIXED_TS]
    if kw.get("replace"):
        argv.append("--replace")
    if kw.get("allow_incomplete"):
        argv.append("--allow-incomplete")
    buf_out, buf_err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = R.main(argv)
    return code, buf_out.getvalue(), buf_err.getvalue()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="car-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def fresh_source(self):
        src = self.tmp / ("src-%d" % id(self))
        if src.exists():
            shutil.rmtree(src)
        return copy_fixture(src)

    def read_index(self, out):
        return (Path(out) / "index.html").read_text(encoding="utf-8")

    # ------------------------------------------------------------------ #
    # Fixture-shape helpers.
    #
    # The accepted fixture is ANY valid, completed v2 output tree, so no test may
    # assume a particular alias — or even that a registry is populated. A repo
    # with no vulnerabilities has no V finding; a legacy repo with no tests has
    # no covered rule and possibly no traceability at all. Both are valid input
    # that must render. Each helper therefore returns the entry a test needs,
    # synthesizing it into the temp manifest when the fixture lacks it, keeping
    # every cross-manifest invariant the renderer enforces intact.
    # ------------------------------------------------------------------ #
    def ensure_rule(self, m):
        if not m["business_rules"]:
            m["business_rules"].append({
                "canonical_key": "br:synthetic/rule.go:synthesized-rule:suite",
                "alias": "BR-900",
                "rule": "Synthesized by the test suite because the fixture has none.",
                "confidence": "low",
                "evidence": [],
                "coverage_status": "untested",
            })
        return m["business_rules"][0]

    def ensure_finding(self, m):
        if not m["findings"]:
            m["findings"].append({
                "canonical_key": "td:synthetic/debt.go:synthesized-finding:suite",
                "alias": "TD-900",
                "registry": "td",
                "title": "Synthesized by the test suite because the fixture has none.",
                "kind": "technical-debt",
                "severity": "low",
                "confidence": "low",
                "status": "open",
                "evidence": [],
            })
            m["severity_counts"]["low"] = m["severity_counts"].get("low", 0) + 1
        return m["findings"][0]

    def ensure_component(self, m):
        if not m["components"]:
            m["components"].append({
                "canonical_key": "cmp:synthetic:synthesized-component:suite",
                "alias": "CMP-900",
                "name": "Synthesized component",
                "path": "synthetic/",
                "namespace": None,
            })
            # coverage.components must equal the components alias set exactly.
            m["coverage"].setdefault("components", []).append({
                "component_alias": "CMP-900",
                "depth": "not-read",
                "files_read": [],
                "rationale": "synthesized by the test suite",
            })
        return m["components"][0]

    def ensure_test_case(self, m, category="behavioral"):
        for tc in m["test_cases"]:
            if tc.get("category") == category:
                return tc
        if not m["test_cases"]:
            m["test_cases"].append({
                "canonical_key": "tc:synthetic/test.go:synthesized-case:suite",
                "alias": "TC-900",
                "category": "behavioral",
                "title": "Synthesized by the test suite because the fixture has none.",
                "source_refs": [self.ensure_rule(m)["alias"]],
                "status": "specification",
            })
        tc = m["test_cases"][0]
        # Re-category the first case and give it refs its new category permits.
        tc["category"] = category
        tc["source_refs"] = [
            self.ensure_rule(m)["alias"] if category == "behavioral"
            else self.ensure_component(m)["alias"]
        ]
        return tc

    def ensure_covered_rule(self, m):
        """Alias of a business rule that is `covered` and linked, synthesizing
        that state when the fixture carries no covered rule."""
        for r in m["business_rules"]:
            if r.get("coverage_status") == "covered":
                return r["alias"]
        rule = self.ensure_rule(m)
        tc = self.ensure_test_case(m)
        rule["coverage_status"] = "covered"
        m["traceability"].append({"business_rule": rule["alias"], "test_case": tc["alias"]})
        return rule["alias"]

    def ensure_traceability_link(self, m):
        if not m["traceability"]:
            self.ensure_covered_rule(m)
        return m["traceability"][0]


# --------------------------------------------------------------------------- #
class TestContract(Base):
    def test_valid_baseline_renders_and_validates(self):
        src = self.fresh_source()
        out = self.tmp / "out"
        code, o, e = render(src, out)
        self.assertEqual(code, 0, e)
        self.assertEqual(V.validate_report_dir(out), [])

    def test_both_schema_versions_required(self):
        src = self.fresh_source()
        m = load_manifest(src)
        m["schema_version"] = "3.0"
        write_manifest(src, m)
        code, o, e = render(src, self.tmp / "o1")
        self.assertEqual(code, 1)
        self.assertIn("unsupported-contract", e)

    def test_progress_schema_version_required(self):
        src = self.fresh_source()
        pj = json.loads((src / "progress.json").read_text())
        pj["schema_version"] = "1.0"
        (src / "progress.json").write_text(json.dumps(pj))
        code, o, e = render(src, self.tmp / "o2")
        self.assertEqual(code, 1)
        self.assertIn("unsupported-contract", e)

    def test_unknown_manifest_key_fails_closed(self):
        src = self.fresh_source()
        m = load_manifest(src)
        m["surprise"] = 1
        write_manifest(src, m)
        code, o, e = render(src, self.tmp / "o3")
        self.assertEqual(code, 1)
        self.assertIn("unknown manifest keys", e)

    def test_completion_predicate_phase_status(self):
        src = self.fresh_source()
        pj = json.loads((src / "progress.json").read_text())
        pj["phases"][3]["status"] = "in-progress"
        (src / "progress.json").write_text(json.dumps(pj))
        # Not allowed without flag.
        code, o, e = render(src, self.tmp / "o4")
        self.assertEqual(code, 1)
        self.assertIn("incomplete", e)

    def test_incomplete_allowed_shows_banner(self):
        src = self.fresh_source()
        pj = json.loads((src / "progress.json").read_text())
        pj["status"] = "in-progress"
        pj["current_phase"] = "synthesis"
        (src / "progress.json").write_text(json.dumps(pj))
        out = self.tmp / "o5"
        code, o, e = render(src, out, allow_incomplete=True)
        self.assertEqual(code, 0, e)
        html = self.read_index(out)
        self.assertIn("warning-banner", html)
        self.assertIn("incomplete", html.lower())

    def test_count_mismatch_fails(self):
        src = self.fresh_source()
        m = load_manifest(src)
        m["severity_counts"]["high"] = 99
        write_manifest(src, m)
        code, o, e = render(src, self.tmp / "o6")
        self.assertEqual(code, 1)
        self.assertIn("count-mismatch", e)

    def test_coverage_disagreement_fails(self):
        src = self.fresh_source()
        m = load_manifest(src)
        # Mark a covered rule as untested while a link still exists.
        br = self.ensure_covered_rule(m)
        for r in m["business_rules"]:
            if r["alias"] == br:
                r["coverage_status"] = "untested"
        write_manifest(src, m)
        code, o, e = render(src, self.tmp / "o7")
        self.assertEqual(code, 1)
        self.assertIn("coverage-disagreement", e)


# --------------------------------------------------------------------------- #
class TestDocuments(Base):
    def test_json_excluded_md_included_once(self):
        src = self.fresh_source()
        out = self.tmp / "out"
        self.assertEqual(render(src, out)[0], 0)
        html = self.read_index(out)
        m = load_manifest(src)
        md = [d["path"] for d in m["documents"] if d["path"].endswith(".md")]
        for path in md:
            # Each md doc appears as an article header exactly once.
            count = html.count('>%s <span class="badge"' % path)
            self.assertEqual(count, 1, "doc %s appears %d times" % (path, count))
        # JSON files are not rendered as Markdown articles.
        self.assertNotIn('>manifest.json <span class="badge"', html)
        # But they are referenced in About as source data.
        self.assertIn("<code>manifest.json</code>", html)


# --------------------------------------------------------------------------- #
class TestCoverageModes(Base):
    def _set_mode(self, src, mode):
        m = load_manifest(src)
        m["coverage"]["mode"] = mode
        write_manifest(src, m)

    def test_full_focused_sampled(self):
        for mode in ("full", "focused", "sampled"):
            src = self.tmp / ("src-" + mode)
            copy_fixture(src)
            self._set_mode(src, mode)
            out = self.tmp / ("out-" + mode)
            code, o, e = render(src, out)
            self.assertEqual(code, 0, e)
            self.assertIn(mode, self.read_index(out))

    def test_untested_rule_and_nonempty_delta(self):
        # The shape under test (an untested rule; four non-empty delta states) is
        # synthesized in temp rather than assumed of the fixture, because any
        # completed v2 tree is an accepted fixture.
        src = self.fresh_source()
        m = load_manifest(src)
        br = self.ensure_covered_rule(m)
        # Convert it to untested: drop its traceability links, flip the status.
        # Its test cases stay declared; source_refs still resolve to a live BR.
        m["traceability"] = [t for t in m["traceability"] if t["business_rule"] != br]
        for r in m["business_rules"]:
            if r["alias"] == br:
                r["coverage_status"] = "untested"
        # Non-empty delta states. Delta entries are canonical keys; resolved keys
        # need not be current findings, so they are free-form.
        key = self.ensure_finding(m)["canonical_key"]
        m["delta"] = {
            "prior_manifest_loaded": True,
            "new": [key],
            "persisted": ["td:still/here:synthetic-persisted:test"],
            "regressed": ["v:back/again:synthetic-regressed:test"],
            "resolved": ["v:gone/in/this/run:synthetic-resolved:test"],
        }
        write_manifest(src, m)
        out = self.tmp / "out"
        code, o, e = render(src, out)
        self.assertEqual(code, 0, e)
        html = self.read_index(out)
        # Untested rule listed.
        self.assertRegex(html, r"(?s)Untested business rules.*" + re.escape(br))
        # Every delta state carries its synthesized count.
        for state in ("new", "resolved", "regressed", "persisted"):
            self.assertIn('<tr><td>%s</td><td data-sort="1">1</td></tr>' % state, html)


# --------------------------------------------------------------------------- #
class TestContentSafety(Base):
    def render_md(self, md):
        ids = R.IdFactory()
        return R.render_markdown(FIXTURE, md, ids)

    def test_raw_html_escaped(self):
        out = self.render_md("A generic `Task<JsonResult>` and <script>alert(1)</script> text.")
        self.assertNotIn("<script>alert", out)
        self.assertIn("&lt;script&gt;", out)
        self.assertIn("Task&lt;JsonResult&gt;", out)

    def test_active_scheme_link_inert(self):
        out = self.render_md("[click](javascript:alert(1))")
        self.assertNotIn("href=\"javascript:", out)
        self.assertIn("inert link", out)

    def test_external_link_rel(self):
        out = self.render_md("[site](https://example.com)")
        self.assertIn('rel="noreferrer noopener"', out)
        self.assertIn("external link", out)

    def test_protocol_relative_link_treated_external(self):
        # B1 regression: '//host' is NOT a safe relative link. It must be
        # classified external and emitted with rel + visible external label,
        # never as a live/unlabeled anchor.
        self.assertEqual(R.classify_link("//evil.com/x"), ("external", "//evil.com/x"))
        out = self.render_md("See [external](//cdn.evil.example/track) here.")
        # It must carry external treatment.
        self.assertIn('rel="noreferrer noopener"', out)
        self.assertIn("external link", out)
        # And must NOT be a bare, un-labeled safe anchor.
        self.assertNotIn('<a href="//cdn.evil.example/track">external</a>', out)

    def test_protocol_relative_image_no_loading_element(self):
        # B1 regression: '//host' image must not become a network-loading <img>.
        out = self.render_md("![x](//evil.com/a.png)")
        self.assertNotIn("<img", out)
        self.assertIn("not loaded", out)

    def test_backslash_link_inert(self):
        # B1 regression: UNC-style backslash hrefs are neutralized (inert).
        self.assertEqual(R.classify_link("\\\\server\\share")[0], "inert")
        out = self.render_md("[unc](\\\\server\\share)")
        self.assertNotIn('href="\\\\server\\share"', out)
        self.assertNotIn('href="//server/share"', out)
        self.assertIn("inert link", out)

    def test_backslash_slash_not_safe(self):
        # '/\evil.com' normalizes to '//evil.com' and must not be safe.
        self.assertNotEqual(R.classify_link("/\\evil.com")[0], "safe")

    def test_safe_relative_links_still_safe(self):
        # Genuine relative/hash links remain live in-report anchors.
        for href in ("#findings", "./page.html", "../up.html", "/root/rel.html", "sub/rel.html"):
            self.assertEqual(R.classify_link(href)[0], "safe", href)

    def test_remote_image_no_loading_element(self):
        out = self.render_md("![badge](https://img.shields.io/x.svg)")
        self.assertNotIn("<img", out)
        self.assertIn("not loaded", out)

    def test_relative_image_containment_and_embed(self):
        # Create a tiny local PNG within a temp source; embed as data URL.
        src = self.tmp / "imgsrc"
        src.mkdir()
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
            "890000000a49444154789c6360000002000100" "0d0a2db4" "0000000049454e44ae426082"
        )
        (src / "pic.png").write_bytes(png)
        ids = R.IdFactory()
        out = R.render_markdown(src, "![p](pic.png)", ids)
        self.assertIn("data:image/png;base64", out)
        # Traversal image rejected.
        out2 = R.render_markdown(src, "![p](../secret.png)", R.IdFactory())
        self.assertIn("image", out2.lower())
        self.assertNotIn("data:image", out2)

    def test_oversize_image_placeholder(self):
        src = self.tmp / "bigimg"
        src.mkdir()
        (src / "big.png").write_bytes(b"\x89PNG" + b"0" * (R.IMAGE_MAX_BYTES + 10))
        out = R.render_markdown(src, "![b](big.png)", R.IdFactory())
        self.assertIn("too large", out)

    def test_svg_sanitize_script_rejected(self):
        src = self.tmp / "svgsrc"
        src.mkdir()
        (src / "bad.svg").write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"><script>x()</script></svg>')
        out = R.render_markdown(src, "![s](bad.svg)", R.IdFactory())
        self.assertIn("unsafe SVG omitted", out)
        (src / "evt.svg").write_bytes(b'<svg onload="x()"></svg>')
        out2 = R.render_markdown(src, "![s](evt.svg)", R.IdFactory())
        self.assertIn("unsafe SVG omitted", out2)
        (src / "ext.svg").write_bytes(b'<svg><image href="http://evil/x.png"/></svg>')
        out3 = R.render_markdown(src, "![s](ext.svg)", R.IdFactory())
        self.assertIn("unsafe SVG omitted", out3)
        # Clean SVG embeds.
        (src / "ok.svg").write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>')
        out4 = R.render_markdown(src, "![s](ok.svg)", R.IdFactory())
        self.assertIn("data:image/svg+xml;base64", out4)

    def test_symlink_escape_rejected(self):
        src = self.tmp / "linksrc"
        src.mkdir()
        secret = self.tmp / "secret.txt"
        secret.write_text("top secret")
        link = src / "link.md"
        try:
            os.symlink(secret, link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unsupported")
        with self.assertRaises(R.ReportError):
            R.contained_path(src, "link.md")

    def test_undecodable_document_clean_error(self):
        # Round-2 NEW-1: an invalid-UTF-8 declared document raises a clean
        # ReportError (user-facing message), not a raw UnicodeDecodeError.
        src = self.fresh_source()
        m = load_manifest(src)
        first_md = next(d["path"] for d in m["documents"] if d["path"].endswith(".md"))
        (src / first_md).write_bytes(b"\xff\xfe\x00broken")
        code, o, e = render(src, self.tmp / "out-undecodable")
        self.assertEqual(code, 1)
        self.assertIn("unreadable document", e)
        self.assertNotIn("Traceback", e)

    def test_special_file_rejected(self):
        src = self.tmp / "specialsrc"
        src.mkdir()
        (src / "sub").mkdir()
        with self.assertRaises(R.ReportError):
            R.contained_path(src, "sub")  # directory, not regular file


# --------------------------------------------------------------------------- #
class TestMermaid(Base):
    def test_all_accepted_types_safe(self):
        for t in sorted(R.MERMAID_TYPES):
            safe, reason = R.classify_mermaid(t + "\n  A --> B")
            self.assertTrue(safe, "%s flagged: %s" % (t, reason))

    def test_unsupported_type_source_only(self):
        safe, reason = R.classify_mermaid("bogusDiagram\n A-->B")
        self.assertFalse(safe)

    def test_directive_source_only(self):
        safe, reason = R.classify_mermaid('%%{init: {"theme":"dark"}}%%\nflowchart LR\n A-->B')
        self.assertFalse(safe)
        self.assertIn("directive", reason)

    def test_raw_html_source_only(self):
        safe, reason = R.classify_mermaid('flowchart LR\n A["<b>bold</b>"]-->B')
        self.assertFalse(safe)

    def test_stereotypes_and_generics_stay_safe(self):
        # M-1 regression: idiomatic Mermaid angle brackets are not HTML.
        cases = [
            "stateDiagram-v2\n  state f <<fork>>\n  [*] --> f",
            "classDiagram\n  <<interface>> Shape\n  Shape : +area()",
            "classDiagram\n  class Runner {\n    +Task<JsonResult> Run()\n  }",
        ]
        for src in cases:
            safe, reason = R.classify_mermaid(src)
            self.assertTrue(safe, "%r flagged: %s" % (src.splitlines()[1], reason))

    def test_html_element_names_rejected_even_unterminated(self):
        # M-2 regression: real HTML tag names are rejected with or without a
        # closing '>', including in arrowless diagram types.
        cases = [
            'flowchart LR\n A["<img src=x onerror=alert(1)>"] --> B',
            'mindmap\n  root\n    "<img src=https://evil.example/t.png"',
            'pie\n  "<img src=https://evil.example/t.png" : 42',
            'timeline\n  2020 : <img src=https://evil.example/x.png',
            'flowchart LR\n A["<script>x()</script>"]-->B',
        ]
        for src in cases:
            safe, reason = R.classify_mermaid(src)
            self.assertFalse(safe, "%r accepted" % src)
            self.assertIn("HTML", reason)

    def test_edge_aware_balance(self):
        # Mermaid state edges use o{ }o and |{ }| forms; must be treated balanced.
        self.assertTrue(R.mermaid_balanced('stateDiagram-v2\n A --> B'))
        self.assertFalse(R.mermaid_balanced('flowchart LR\n A[unbalanced'))
        # Quoted bracket should not unbalance.
        self.assertTrue(R.mermaid_balanced('flowchart LR\n A["a ] b"]-->B'))

    def test_source_only_does_not_abort_report(self):
        ids = R.IdFactory()
        html = R.render_markdown(FIXTURE,
                                 "```mermaid\nbogus\nA-->B\n```\n\nAfter.", ids)
        self.assertIn("shown as source", html)
        self.assertIn("After.", html)

    def test_safe_block_has_strict_markers(self):
        ids = R.IdFactory()
        html = R.render_mermaid_block("flowchart LR\n A-->B", ids)
        self.assertIn('data-mermaid-safe="true"', html)
        self.assertIn("mermaid-source", html)  # static fallback present

    def test_pinned_checksum(self):
        actual = R.sha256_file(R.ASSETS_DIR / "mermaid.min.js")
        self.assertEqual(actual, R.MERMAID_SHA256)
        self.assertEqual(V.MERMAID_SHA256, R.MERMAID_SHA256)


# --------------------------------------------------------------------------- #
class TestInteractionAndA11y(Base):
    def setUp(self):
        super().setUp()
        self.out = self.tmp / "out"
        code, o, e = render(self.fresh_source(), self.out)
        self.assertEqual(code, 0, e)
        self.html = self.read_index(self.out)

    def test_anchor_nav_with_aria_current(self):
        self.assertIn('href="#overview"', self.html)
        self.assertIn('aria-current="true"', self.html)

    def test_native_disclosure_buttons(self):
        self.assertIn('class="disclosure-toggle"', self.html)
        self.assertIn('aria-expanded="true"', self.html)
        self.assertIn('aria-controls=', self.html)
        self.assertNotIn('role="button"', self.html)  # no div-as-button

    def test_sortable_aria_sort(self):
        self.assertIn('aria-sort="none"', self.html)
        self.assertIn('class="sort-btn"', self.html)

    def test_filter_live_status(self):
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn("data-filter-for=", self.html)

    def test_theme_controls_labeled(self):
        for label in ("System", "Light", "Dark"):
            self.assertIn(">%s<" % label, self.html)
        self.assertIn('role="status"', self.html)

    def test_blocking_head_theme_init(self):
        head = self.html.split("</head>", 1)[0]
        self.assertIn("car:theme:v1", head)
        self.assertIn("prefers-color-scheme", head)
        # script appears before the stylesheet -> before first paint
        self.assertLess(head.index("<script>"), head.index("<style>"))

    def test_landmarks_and_skip_link(self):
        for needle in ("<main", "<nav", "<header", "<aside", "skip-link"):
            self.assertIn(needle, self.html)

    def test_table_captions(self):
        self.assertIn("<caption>", self.html)

    def test_heading_hierarchy(self):
        # UX-F1 regression: exactly one page h1; heading levels never jump by
        # more than one when descending (decreases are always allowed).
        levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])[\s>]", self.html)]
        self.assertTrue(levels, "no headings found")
        self.assertEqual(levels[0], 1, "document must start with h1")
        self.assertEqual(levels.count(1), 1, "exactly one h1 expected")
        for prev, cur in zip(levels, levels[1:]):
            self.assertLessEqual(cur - prev, 1,
                                 "heading skip: h%d followed by h%d" % (prev, cur))

    def test_tables_have_scroll_regions(self):
        # UX-F3 regression: every table sits inside a focusable scroll region.
        tables = len(re.findall(r"<table[\s>]", self.html))
        regions = len(re.findall(r'class="table-scroll" role="region" tabindex="0"', self.html))
        self.assertEqual(tables, regions)

    def test_no_external_assets(self):
        # validator already checks; assert here directly on img/script src.
        for m in re.finditer(r'<(img|script)\b[^>]*\bsrc="([^"]+)"', self.html):
            self.assertFalse(m.group(2).lower().startswith(("http://", "https://", "//")),
                             "external asset: %s" % m.group(2))


# --------------------------------------------------------------------------- #
class TestThemeJs(Base):
    def test_js_theme_contract(self):
        js = (R.ASSETS_DIR / "report.js").read_text()
        self.assertIn('"car:theme:v1"', js)
        self.assertIn("matchMedia", js)
        self.assertIn("try", js)                 # storage exceptions caught
        self.assertIn("addEventListener", js)    # OS-change listener
        self.assertIn("securityLevel", js)
        self.assertIn('"strict"', js)

    def test_css_reduced_motion_and_print(self):
        css = (R.ASSETS_DIR / "report.css").read_text()
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("@media print", css)
        self.assertIn("data-theme=\"dark\"", css)

    def test_print_override_beats_dark_theme_specificity(self):
        # SC-1 regression: the @media print token override must include the
        # :root[data-theme="dark"] selector, or dark-mode printing emits
        # near-white text (media queries do not change cascade specificity).
        css = (R.ASSETS_DIR / "report.css").read_text()
        print_block = css.split("@media print", 1)[1]
        first_rule = print_block[:print_block.index("}")]
        self.assertIn(':root[data-theme="dark"]', first_rule)
        # Light values reasserted for text and severity tokens.
        self.assertIn("--fg: #000000", first_rule)
        self.assertIn("--sev-critical-fg: #7f1d1d", first_rule)
        # Filtered-out rows become visible in print.
        self.assertIn("tr[hidden]", print_block)

    def test_js_htmllabels_disabled(self):
        js = (R.ASSETS_DIR / "report.js").read_text()
        self.assertIn("htmlLabels: false", js)

    def test_js_failure_label_distinct(self):
        js = (R.ASSETS_DIR / "report.js").read_text()
        self.assertIn("could not be rendered", js)


# --------------------------------------------------------------------------- #
class TestContrast(Base):
    """Programmatic WCAG contrast for token pairs in both themes."""

    @staticmethod
    def _lum(hexstr):
        hexstr = hexstr.lstrip("#")
        r, g, b = (int(hexstr[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
        def lin(c):
            return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        R_, G_, B_ = lin(r), lin(g), lin(b)
        return 0.2126 * R_ + 0.7152 * G_ + 0.0722 * B_

    @classmethod
    def _ratio(cls, a, b):
        la, lb = cls._lum(a), cls._lum(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    def _tokens(self, theme):
        css = (R.ASSETS_DIR / "report.css").read_text()
        if theme == "light":
            block = css.split(":root {", 1)[1].split("}", 1)[0]
        else:
            block = css.split(':root[data-theme="dark"] {', 1)[1].split("}", 1)[0]
        tokens = {}
        for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", block):
            tokens[m.group(1)] = m.group(2)
        return tokens

    def test_body_text_contrast(self):
        for theme in ("light", "dark"):
            t = self._tokens(theme)
            ratio = self._ratio(t["fg"], t["bg"])
            self.assertGreaterEqual(ratio, 4.5, "%s fg/bg = %.2f" % (theme, ratio))
            muted = self._ratio(t["fg-muted"], t["bg"])
            self.assertGreaterEqual(muted, 4.5, "%s fg-muted/bg = %.2f" % (theme, muted))

    def test_ui_border_and_focus_contrast(self):
        for theme in ("light", "dark"):
            t = self._tokens(theme)
            self.assertGreaterEqual(self._ratio(t["border-strong"], t["bg"]), 3.0,
                                    "%s border-strong" % theme)
            self.assertGreaterEqual(self._ratio(t["focus"], t["bg"]), 3.0, "%s focus" % theme)

    def test_severity_badge_contrast(self):
        for theme in ("light", "dark"):
            t = self._tokens(theme)
            for sev in ("critical", "high", "medium", "low", "none"):
                ratio = self._ratio(t["sev-%s-fg" % sev], t["sev-%s-bg" % sev])
                self.assertGreaterEqual(ratio, 4.5, "%s %s badge = %.2f" % (theme, sev, ratio))


# --------------------------------------------------------------------------- #
class TestIntegrityMutations(Base):
    def setUp(self):
        super().setUp()
        self.out = self.tmp / "out"
        self.assertEqual(render(self.fresh_source(), self.out)[0], 0)

    def test_baseline_valid(self):
        self.assertEqual(V.validate_report_dir(self.out), [])

    def test_index_checksum_mutation_fails(self):
        idx = self.out / "index.html"
        idx.write_text(idx.read_text() + "<!-- tamper -->")
        errs = V.validate_report_dir(self.out)
        self.assertTrue(any("checksum mismatch for index.html" in e for e in errs))

    def test_removed_document_fails(self):
        rm = json.loads((self.out / "report-manifest.json").read_text())
        html = (self.out / "index.html").read_text()
        # Remove a document reference by editing html then re-hashing to isolate the
        # documents check: instead, drop a doc from manifest and ensure mismatch.
        rm["documents"].append("architecture/nonexistent.md")
        (self.out / "report-manifest.json").write_text(json.dumps(rm))
        errs = V.validate_report_dir(self.out)
        self.assertTrue(any("not present" in e for e in errs))

    def test_manifest_hashes_itself_fails(self):
        rm = json.loads((self.out / "report-manifest.json").read_text())
        rm["generated_files"]["report-manifest.json"] = "0" * 64
        (self.out / "report-manifest.json").write_text(json.dumps(rm))
        errs = V.validate_report_dir(self.out)
        self.assertTrue(any("must not hash itself" in e for e in errs))

    def test_mermaid_checksum_mutation_fails(self):
        (self.out / "assets" / "mermaid.min.js").write_bytes(b"tampered")
        errs = V.validate_report_dir(self.out)
        self.assertTrue(any("mermaid" in e.lower() for e in errs))


# --------------------------------------------------------------------------- #
class TestPublication(Base):
    def test_collision_refusal(self):
        src = self.fresh_source()
        out = self.tmp / "out"
        self.assertEqual(render(src, out)[0], 0)
        code, o, e = render(src, out)  # no --replace
        self.assertEqual(code, 1)
        self.assertIn("output-collision", e)

    def test_replace_backup_restore(self):
        src = self.fresh_source()
        out = self.tmp / "out"
        self.assertEqual(render(src, out)[0], 0)
        marker = out / "MARKER.txt"
        marker.write_text("old")
        code, o, e = render(src, out, replace=True)
        self.assertEqual(code, 0, e)
        # Old output replaced (marker gone), no leftover temp/backup siblings.
        self.assertFalse(marker.exists())
        leftovers = [p.name for p in out.parent.iterdir()
                     if p.name.startswith(".out.")]
        self.assertEqual(leftovers, [])

    def test_temp_on_same_filesystem(self):
        # The temp sibling shares the destination parent (same filesystem).
        dest = self.tmp / "sub" / "report"
        sib = R.unique_sibling(dest, "tmp")
        self.assertEqual(sib.parent, dest.parent)

    def test_replace_restore_on_rename_failure(self):
        # SC-2 regression: when the temp->dest rename fails after the old
        # output was moved to backup, the prior output must be restored intact.
        dest = self.tmp / "dest"
        dest.mkdir()
        (dest / "index.html").write_text("old-report")
        temp = self.tmp / ".dest.tmp"
        temp.mkdir()
        (temp / "index.html").write_text("new-report")
        real_rename = R.os.rename

        def flaky(a, b):
            if Path(a) == temp:
                raise OSError("simulated rename failure")
            return real_rename(a, b)

        R.os.rename = flaky
        try:
            with self.assertRaises(R.ReportError) as cm:
                R.publish(temp, dest, allow_replace=True)
        finally:
            R.os.rename = real_rename
        self.assertIn("restored prior output", str(cm.exception))
        self.assertEqual((dest / "index.html").read_text(), "old-report")
        # No backup residue; the temp dir is left for the caller's cleanup.
        residue = [p.name for p in self.tmp.iterdir() if ".backup" in p.name]
        self.assertEqual(residue, [])

    def test_replace_final_validation_restores_backup(self):
        # SC-3: the backup is removed only after the published destination
        # passes final validation; an invalid publish restores the prior output.
        dest = self.tmp / "dest"
        dest.mkdir()
        (dest / "index.html").write_text("old-report")
        temp = self.tmp / ".dest.tmp"
        temp.mkdir()
        (temp / "garbage.txt").write_text("not a report")  # fails validation
        with self.assertRaises(R.ReportError) as cm:
            R.publish(temp, dest, allow_replace=True)
        self.assertIn("final validation", str(cm.exception))
        self.assertEqual((dest / "index.html").read_text(), "old-report")
        residue = [p.name for p in self.tmp.iterdir() if ".backup" in p.name]
        self.assertEqual(residue, [])


# --------------------------------------------------------------------------- #
class TestNeutrality(Base):
    def test_emitted_assets_neutral(self):
        self.assertEqual(V.scan_emitted_assets(), [])

    def test_authored_docs_neutral(self):
        self.assertEqual(V.scan_authored_docs(), [])

    def skill_copy_with_branded_doc(self):
        """A working copy of the skill whose references/ carry a branded phrase.
        Returns the copy root; V.SKILL_ROOT is repointed at it for the test."""
        root = self.tmp / "skill-copy"
        shutil.copytree(R.SKILL_ROOT, root, symlinks=True)
        ref = root / "references" / "validation.md"
        ref.write_text(ref.read_text(encoding="utf-8")
                       + "\n\nThis report follows the AWS Well-Architected review.\n",
                       encoding="utf-8")
        original = V.SKILL_ROOT
        V.SKILL_ROOT = root
        self.addCleanup(lambda: setattr(V, "SKILL_ROOT", original))
        return root

    def test_publication_gate_ignores_authored_docs(self):
        # Behavioral, not structural: a branded phrase in references/ must be
        # caught by scan_authored_docs and must NOT block a render, because those
        # files contribute no byte to index.html.
        self.skill_copy_with_branded_doc()
        self.assertTrue(any("well-architected" in e for e in V.scan_authored_docs()))
        self.assertEqual(V.scan_emitted_assets(), [])
        out = self.tmp / "out"
        code, o, e = render(self.fresh_source(), out)
        self.assertEqual(code, 0, e)
        self.assertEqual(V.validate_report_dir(out), [])

    def test_emitted_chrome_scanned_outside_triple_quotes(self):
        # Authored wording in an ordinary quoted literal is emitted into the
        # report just like a triple-quoted skeleton, so the publication gate must
        # see it. Guards the AST-based chrome scan against a regex regression.
        root = self.tmp / "skill-chrome"
        shutil.copytree(R.SKILL_ROOT, root, symlinks=True)
        rr = root / "scripts" / "render_report.py"
        src = rr.read_text(encoding="utf-8")
        anchor = '"<p>Prior manifest loaded: <strong>yes</strong>.</p>"'
        self.assertIn(anchor, src)
        rr.write_text(src.replace(anchor, '"<p>AWS readiness score pending.</p>"'),
                      encoding="utf-8")
        original = V.SKILL_ROOT
        V.SKILL_ROOT = root
        self.addCleanup(lambda: setattr(V, "SKILL_ROOT", original))
        errs = V.scan_emitted_assets()
        self.assertTrue(any("'aws'" in e for e in errs), errs)
        self.assertTrue(any("readiness score" in e for e in errs), errs)
        # The message locates the hit precisely enough to act on.
        self.assertTrue(any(re.search(r"render_report\.py:\d+ contains", e) for e in errs), errs)

    def test_upstream_provenance_exempt(self):
        # metadata.upstream records the honest source repository and may carry a
        # brand name; name/description in the same frontmatter stay in scope.
        # Every YAML form the value can legally take must be exempt, or the
        # self-hit returns the first time someone reformats the frontmatter.
        exempt = {
            "double-quoted": '---\nname: x\nmetadata:\n  upstream: "gitkeng/aws-atx-lab @abc"\n---\n\nbody\n',
            "folded": '---\nname: x\nmetadata:\n  upstream: >-\n    gitkeng/aws-atx-lab\n    @abc\n---\n\nbody\n',
            "literal": '---\nname: x\nmetadata:\n  upstream: |\n    gitkeng/aws-atx-lab\n---\n\nbody\n',
            "crlf": '---\r\nname: x\r\nmetadata:\r\n  upstream: "gitkeng/aws-atx-lab"\r\n---\r\n\r\nbody\r\n',
        }
        for label, doc in exempt.items():
            errs = []
            V._scan_text("SKILL.md", V._strip_provenance(doc), errs)
            self.assertEqual(errs, [], "%s form leaked" % label)
        # Not exempt: description, body prose, and a top-level upstream key.
        scanned = {
            "description": '---\nname: x\ndescription: built for AWS\n---\n\nbody\n',
            "body": '---\nname: x\n---\n\nsee upstream: gitkeng/aws-lab\n',
            "top-level": '---\nupstream: gitkeng/aws-lab\n---\n\nbody\n',
        }
        for label, doc in scanned.items():
            errs = []
            V._scan_text("SKILL.md", V._strip_provenance(doc), errs)
            self.assertTrue(any("'aws'" in e for e in errs), "%s not scanned" % label)

    def test_denylist_catches_injection(self):
        # Simulate a branded token in a copied asset within temp; scan that copy.
        css = (R.ASSETS_DIR / "report.css").read_text()
        self.assertNotIn("aws", css.lower().replace("always", ""))  # sanity
        # Direct denylist behavior check.
        self.assertTrue(V._word_present("built for aws customers", "aws"))
        self.assertFalse(V._word_present("awssome typo", "aws"))

    def test_error_message_locates_the_hit(self):
        # The failure a user sees must name the file, the line, and the text, so
        # it can be adjudicated without reading this scanner's source.
        errs = []
        V._scan_text("SKILL.md", "ok\nbuilt for AWS customers\n", errs)
        self.assertEqual(
            errs, ["neutrality: SKILL.md:2 contains branded token 'aws' "
                   "in: built for AWS customers"])

    def test_self_check_needs_no_report_dir(self):
        # Authoring loop: neutrality must be checkable without a v2 fixture.
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = V.main(["validate_report.py", "--self-check"])
        self.assertEqual(code, 0, buf.getvalue())
        self.assertIn("PASS: skill self-check", buf.getvalue())

    def test_source_provider_names_pass_through(self):
        # A provider name in a finding title is observed evidence and must reach
        # the output unchanged: the denylist governs skill-authored chrome only.
        # The branded title is injected rather than assumed of the fixture.
        marker = "AWS SDK client left on an unsupported major version"
        src = self.fresh_source()
        m = load_manifest(src)
        self.ensure_finding(m)["title"] = marker
        write_manifest(src, m)
        out = self.tmp / "out"
        code, o, e = render(src, out)
        self.assertEqual(code, 0, e)
        self.assertIn(marker, self.read_index(out))


# --------------------------------------------------------------------------- #
class TestOverviewCounts(Base):
    def test_severity_cards_match_manifest(self):
        src = self.fresh_source()
        out = self.tmp / "out"
        self.assertEqual(render(src, out)[0], 0)
        html = self.read_index(out)
        m = load_manifest(src)
        for sev in ("critical", "high", "medium", "low"):
            n = m["severity_counts"][sev]
            self.assertRegex(
                html,
                r'<div class="metric">%d</div>\s*<div class="label">%s findings</div>' % (n, sev),
                "severity card %s=%d not found" % (sev, n),
            )

    def test_prior_manifest_flag_surfaced(self):
        # BA-F1: delta.prior_manifest_loaded is preserved in the Overview delta
        # block and recorded in report-manifest.json; false is framed as the
        # first recorded run instead of "since prior run" counts.
        src = self.fresh_source()
        m = load_manifest(src)
        m["delta"]["prior_manifest_loaded"] = False
        write_manifest(src, m)
        out = self.tmp / "out-prior-false"
        self.assertEqual(render(src, out)[0], 0)
        html = self.read_index(out)
        self.assertIn("first recorded", html)
        rm = json.loads((out / "report-manifest.json").read_text())
        self.assertIs(rm["source_prior_manifest_loaded"], False)

        m["delta"]["prior_manifest_loaded"] = True
        write_manifest(src, m)
        out2 = self.tmp / "out-prior-true"
        self.assertEqual(render(src, out2)[0], 0)
        html2 = self.read_index(out2)
        self.assertIn("Prior manifest loaded: <strong>yes</strong>", html2)
        rm2 = json.loads((out2 / "report-manifest.json").read_text())
        self.assertIs(rm2["source_prior_manifest_loaded"], True)

    def test_reading_routes_present(self):
        # BA-F2/PE-F6: Overview offers reading routes to registries and documents.
        src = self.fresh_source()
        out = self.tmp / "out-routes"
        self.assertEqual(render(src, out)[0], 0)
        html = self.read_index(out)
        self.assertIn("Reading routes", html)
        self.assertIn('href="#findings"', html)
        self.assertIn('href="#documents"', html)


# --------------------------------------------------------------------------- #
class TestEvidenceFormatter(Base):
    """R1: shared evidence formatter — line_start+line_end -> :N-M, only start
    -> :N, both null -> path only. Applies to findings and business rules."""

    def test_formatter_both_lines(self):
        self.assertEqual(
            R.format_evidence({"path": "a/b.cs", "line_start": 10, "line_end": 20}),
            "a/b.cs:10-20",
        )

    def test_formatter_only_start(self):
        self.assertEqual(
            R.format_evidence({"path": "a/b.cs", "line_start": 42, "line_end": None}),
            "a/b.cs:42",
        )

    def test_formatter_both_null(self):
        self.assertEqual(
            R.format_evidence({"path": "a/b.cs", "line_start": None, "line_end": None}),
            "a/b.cs",
        )

    def test_formatter_missing_lines_is_path_only(self):
        self.assertEqual(R.format_evidence({"path": "a/b.cs"}), "a/b.cs")

    def test_formatter_escapes_path(self):
        # HTML-escape the path so evidence text can never inject markup.
        out = R.format_evidence({"path": "a/<b>.cs", "line_start": 1, "line_end": 2})
        self.assertNotIn("<b>", out)
        self.assertIn("&lt;b&gt;", out)

    def test_formatter_list_joins(self):
        recs = [
            {"path": "a.cs", "line_start": 1, "line_end": 2},
            {"path": "b.cs", "line_start": 3, "line_end": None},
            {"path": "c.cs", "line_start": None, "line_end": None},
        ]
        self.assertEqual(R.format_evidence_list(recs), "a.cs:1-2; b.cs:3; c.cs")

    def _mutate_and_render(self, mutate):
        src = self.fresh_source()
        m = load_manifest(src)
        mutate(m)
        write_manifest(src, m)
        out = self.tmp / ("out-%d" % id(mutate))
        code, o, e = render(src, out)
        self.assertEqual(code, 0, e)
        return self.read_index(out)

    def test_mixed_null_evidence_in_findings_and_rules(self):
        # Give one rule only-start evidence and one finding both-null evidence,
        # then assert the rendered evidence cells follow the contract exactly and
        # never emit the old ":N-None" defect. Whichever rule/finding the fixture
        # happens to declare first will do; a repo with no vulnerabilities still
        # has findings in the td registry, and an empty registry is synthesized.
        def mutate(m):
            self.ensure_rule(m)["evidence"] = [
                {"path": "Controllers/RideController.cs",
                 "line_start": 61, "line_end": None}]
            self.ensure_finding(m)["evidence"] = [
                {"path": "Controllers/RideController.cs",
                 "line_start": None, "line_end": None}]
        html = self._mutate_and_render(mutate)
        self.assertNotIn("-None", html)
        self.assertNotIn(":None", html)
        # Only-start business rule renders as path:N (no range).
        self.assertIn("Controllers/RideController.cs:61</code>", html)
        # Both-null finding renders path only (no trailing colon).
        self.assertIn("Controllers/RideController.cs</code>", html)


# --------------------------------------------------------------------------- #
class TestInputContractMappings(Base):
    """R2: normative input-contract mappings enforced by validate_source, with
    semantics mirrored from the upstream comprehensive-codebase-analysis
    validator (coverage/component alias equality; traceability + source_refs
    resolution with category semantics). All negatives must fail closed."""

    def _render_mutated(self, mutate, output="out"):
        src = self.fresh_source()
        m = load_manifest(src)
        mutate(m)
        write_manifest(src, m)
        return render(src, self.tmp / output)

    def test_coverage_alias_missing_fails_closed(self):
        # Drop a coverage.components entry so the set no longer equals components.
        def mutate(m):
            self.ensure_component(m)  # guarantees at least one entry to drop
            m["coverage"]["components"] = m["coverage"]["components"][:-1]
        code, o, e = self._render_mutated(mutate, "cov1")
        self.assertEqual(code, 1)
        self.assertIn("coverage-mapping", e)

    def test_coverage_alias_extra_fails_closed(self):
        # Add an extra coverage.components alias not present in components.
        def mutate(m):
            m["coverage"]["components"].append({
                "component_alias": "CMP-999", "depth": "inventory-only",
                "files_read": ["x"], "rationale": "phantom",
            })
        code, o, e = self._render_mutated(mutate, "cov2")
        self.assertEqual(code, 1)
        self.assertIn("coverage-mapping", e)

    def test_baseline_coverage_alias_equality_holds(self):
        # Sanity: unmodified baseline passes the alias-equality check (renders 0).
        src = self.fresh_source()
        code, o, e = render(src, self.tmp / "cov-ok")
        self.assertEqual(code, 0, e)

    def test_traceability_unresolved_br_fails_closed(self):
        def mutate(m):
            # Append a link to a non-existent BR alias. This does not disturb any
            # real BR's covered/untested invariant, so the traceability-mapping
            # check is the one that must fire (fail closed).
            m["traceability"].append({
                "business_rule": "BR-999",  # unresolved on purpose
                "test_case": self.ensure_test_case(m)["alias"]})
        code, o, e = self._render_mutated(mutate, "tr1")
        self.assertEqual(code, 1)
        self.assertIn("traceability-mapping", e)

    def test_traceability_br_ref_to_nonbr_fails_closed(self):
        def mutate(m):
            # A finding alias is not a business rule; must fail closed. Both
            # aliases resolve, so the failure can only come from the kind check —
            # a hardcoded alias would have failed for the wrong reason. Appended
            # so the BR coverage cross-check is not perturbed first.
            m["traceability"].append({
                "business_rule": self.ensure_finding(m)["alias"],
                "test_case": self.ensure_test_case(m)["alias"]})
        code, o, e = self._render_mutated(mutate, "tr2")
        self.assertEqual(code, 1)
        self.assertIn("traceability-mapping", e)

    def test_traceability_unresolved_tc_fails_closed(self):
        def mutate(m):
            self.ensure_traceability_link(m)["test_case"] = "TC-999"
        code, o, e = self._render_mutated(mutate, "tr3")
        self.assertEqual(code, 1)
        self.assertIn("traceability-mapping", e)

    def test_source_ref_unresolved_fails_closed(self):
        def mutate(m):
            self.ensure_test_case(m)["source_refs"] = ["BR-999"]
        code, o, e = self._render_mutated(mutate, "sr1")
        self.assertEqual(code, 1)
        self.assertIn("source-ref-mapping", e)

    def test_behavioral_source_ref_must_be_br(self):
        # A behavioral case pointing at a finding must fail closed. The finding
        # alias resolves, so only the kind check can produce the failure.
        def mutate(m):
            self.ensure_test_case(m, "behavioral")["source_refs"] = [
                self.ensure_finding(m)["alias"]]
        code, o, e = self._render_mutated(mutate, "sr2")
        self.assertEqual(code, 1)
        self.assertIn("source-ref-mapping", e)

    def test_security_source_ref_must_be_v_td_cmp(self):
        # A security test case pointing at a BR must fail closed. The security
        # category is synthesized so the check is exercised on any fixture.
        def mutate(m):
            self.ensure_test_case(m, "security")["source_refs"] = [
                self.ensure_rule(m)["alias"]]
        code, o, e = self._render_mutated(mutate, "sr3")
        self.assertEqual(code, 1)
        self.assertIn("source-ref-mapping", e)

    def test_security_source_ref_component_allowed(self):
        # A CMP alias is a valid security/infrastructure source (upstream
        # semantics). Only source_refs change, so the BR covered/linked
        # invariants stay intact (they are driven by traceability, not by
        # source_refs).
        def mutate(m):
            self.ensure_test_case(m, "security")["source_refs"] = [
                self.ensure_component(m)["alias"]]
        code, o, e = self._render_mutated(mutate, "sr4")
        self.assertEqual(code, 0, e)

    def test_empty_source_refs_fails_closed(self):
        def mutate(m):
            self.ensure_test_case(m)["source_refs"] = []
        code, o, e = self._render_mutated(mutate, "sr5")
        self.assertEqual(code, 1)
        self.assertIn("source-ref-mapping", e)


# --------------------------------------------------------------------------- #
class TestSchemaSynchronization(Base):
    """R3: the hardcoded stdlib validator's top-level/counts/severity required
    and property sets, and its const versions, must stay synchronized with
    assets/report-manifest.schema.json. Load the schema and assert equality."""

    def setUp(self):
        super().setUp()
        schema_path = R.SKILL_ROOT / "assets" / "report-manifest.schema.json"
        self.schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def test_top_level_required_and_properties_match(self):
        self.assertEqual(set(self.schema["required"]), V.MANIFEST_REQUIRED_KEYS)
        self.assertEqual(set(self.schema["properties"]), V.MANIFEST_REQUIRED_KEYS)
        self.assertFalse(self.schema.get("additionalProperties", True))

    def test_counts_required_and_properties_match(self):
        counts = self.schema["properties"]["counts"]
        self.assertEqual(set(counts["required"]), V.COUNTS_REQUIRED_KEYS)
        self.assertEqual(set(counts["properties"]), V.COUNTS_REQUIRED_KEYS)
        self.assertFalse(counts.get("additionalProperties", True))

    def test_severity_required_and_properties_match(self):
        sev = self.schema["properties"]["counts"]["properties"]["severity"]
        self.assertEqual(set(sev["required"]), V.SEVERITY_REQUIRED_KEYS)
        self.assertEqual(set(sev["properties"]), V.SEVERITY_REQUIRED_KEYS)
        self.assertEqual(set(sev["properties"]), set(V.SEVERITIES))
        self.assertFalse(sev.get("additionalProperties", True))

    def test_const_versions_match(self):
        self.assertEqual(
            self.schema["properties"]["schema_version"]["const"], V.REPORT_SCHEMA_VERSION
        )
        self.assertEqual(
            self.schema["properties"]["source_schema_version"]["const"],
            V.SOURCE_SCHEMA_VERSION,
        )

    def test_mermaid_digest_pattern_and_render_validate_agree(self):
        # The schema's digest pattern is 64 lowercase hex; the pinned constant must
        # satisfy it, and render/validate constants must agree with each other.
        pattern = self.schema["properties"]["mermaid_sha256"]["pattern"]
        self.assertRegex(V.MERMAID_SHA256, pattern)
        self.assertEqual(V.MERMAID_SHA256, R.MERMAID_SHA256)
        self.assertEqual(V.REPORT_SCHEMA_VERSION, R.REPORT_SCHEMA_VERSION)
        self.assertEqual(V.SOURCE_SCHEMA_VERSION, R.SOURCE_SCHEMA_VERSION)


def main():
    global FIXTURE
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fixture", required=True,
        help="path to any valid, completed v2 analysis output tree "
             "(typically the analysis root being reported)")
    args, remaining = parser.parse_known_args()
    FIXTURE = Path(args.fixture).resolve()
    if not (FIXTURE / "manifest.json").is_file():
        print("ERROR: fixture not found or missing manifest.json: %s" % FIXTURE, file=sys.stderr)
        return 2
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
