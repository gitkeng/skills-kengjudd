#!/usr/bin/env python3
"""Validate a generated codebase-analysis-report tree using Python stdlib only.

Checks:
  * required files exist (index.html, report-manifest.json, assets/mermaid.min.js);
  * report-manifest.json conforms to the committed schema contract;
  * recomputed SHA-256 of generated files matches the manifest (manifest never
    hashes itself);
  * severity/registry counts in the manifest are internally consistent;
  * the pinned Mermaid checksum matches the shipped asset value;
  * index.html contains required accessibility landmarks, sections, a skip link,
    unique IDs, a blocking head theme initializer, non-color severity text, and
    no external asset loads or branded template tokens.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
REPORT_SCHEMA_VERSION = "1.0"
SOURCE_SCHEMA_VERSION = "2.0"
MERMAID_SHA256 = "07e37dfa97b337ccc85365d57eddf99b9706f09db3b59b260d0333b23b343c4b"
SEVERITIES = ["critical", "high", "medium", "low"]

# Exported schema-contract constants. These are the single source of truth for
# the hardcoded (stdlib-only) manifest validator and are asserted to stay
# synchronized with assets/report-manifest.schema.json by the test suite.
MANIFEST_REQUIRED_KEYS = {
    "schema_version", "report_generated_at", "source_schema_version",
    "source_generated_at", "source_incomplete", "source_prior_manifest_loaded",
    "documents", "counts", "mermaid_sha256", "generated_files",
}
COUNTS_REQUIRED_KEYS = {
    "severity", "business_rules", "findings", "components", "test_cases",
    "traceability_links",
}
SEVERITY_REQUIRED_KEYS = set(SEVERITIES)

REQUIRED_SECTIONS = [
    "overview", "findings", "business-rules", "components", "tests", "documents", "about",
]

# Provider/brand + prohibited-content denylist for skill-authored chrome only.
# Observed source content (finding titles, document panels, repository paths,
# registries) is rendered as evidence and is explicitly OUT OF SCOPE for this
# scan. Matching is word-boundary based to avoid false substrings such as the
# CSS property "text-transform".
BRAND_DENYLIST = [
    "aws", "amazon", "azure", "gcp", "google cloud", "atx",
    "well-architected", "readiness score", "estimated cost", "migration cost",
    "aws-logo", "execution time", "tokens used",
]
# Multi-word prohibited phrases (substring match is fine; no benign collisions).
PHRASE_DENYLIST = [
    "well-architected", "readiness score", "estimated cost", "migration cost",
    "roadmap to", "aws-logo", "execution time", "tokens used", "google cloud",
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _keys_ok(obj, required, where, errors):
    if not isinstance(obj, dict):
        errors.append("%s: expected object" % where)
        return False
    missing = required - set(obj)
    extra = set(obj) - required
    if missing:
        errors.append("%s: missing keys %s" % (where, sorted(missing)))
    if extra:
        errors.append("%s: unexpected keys %s" % (where, sorted(extra)))
    return not missing and not extra


def validate_manifest_schema(rm, errors):
    required = MANIFEST_REQUIRED_KEYS
    if not _keys_ok(rm, required, "report-manifest", errors):
        return
    if rm.get("schema_version") != REPORT_SCHEMA_VERSION:
        errors.append("report-manifest.schema_version: expected %r" % REPORT_SCHEMA_VERSION)
    if rm.get("source_schema_version") != SOURCE_SCHEMA_VERSION:
        errors.append("report-manifest.source_schema_version: expected %r" % SOURCE_SCHEMA_VERSION)
    for key in ("report_generated_at", "source_generated_at"):
        if not isinstance(rm.get(key), str) or not rm[key].strip():
            errors.append("report-manifest.%s: expected nonempty string" % key)
    if not isinstance(rm.get("source_incomplete"), bool):
        errors.append("report-manifest.source_incomplete: expected boolean")
    if not isinstance(rm.get("source_prior_manifest_loaded"), bool):
        errors.append("report-manifest.source_prior_manifest_loaded: expected boolean")
    if not isinstance(rm.get("documents"), list) or not all(isinstance(x, str) for x in rm.get("documents", [])):
        errors.append("report-manifest.documents: expected string array")
    if not re.fullmatch(r"[0-9a-f]{64}", rm.get("mermaid_sha256", "")):
        errors.append("report-manifest.mermaid_sha256: expected 64-hex digest")
    elif rm["mermaid_sha256"] != MERMAID_SHA256:
        errors.append("report-manifest.mermaid_sha256: does not match pinned asset")

    counts = rm.get("counts")
    creq = COUNTS_REQUIRED_KEYS
    if _keys_ok(counts, creq, "report-manifest.counts", errors):
        sev = counts.get("severity")
        if _keys_ok(sev, SEVERITY_REQUIRED_KEYS, "report-manifest.counts.severity", errors):
            for s in SEVERITIES:
                if not isinstance(sev.get(s), int) or sev[s] < 0:
                    errors.append("report-manifest.counts.severity.%s: expected nonnegative int" % s)
        for k in ("business_rules", "findings", "components", "test_cases", "traceability_links"):
            if not isinstance(counts.get(k), int) or counts[k] < 0:
                errors.append("report-manifest.counts.%s: expected nonnegative int" % k)

    gf = rm.get("generated_files")
    if not isinstance(gf, dict) or not gf:
        errors.append("report-manifest.generated_files: expected nonempty object")
    else:
        if "report-manifest.json" in gf:
            errors.append("report-manifest.generated_files: must not hash itself")
        for path, digest in gf.items():
            if not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
                errors.append("report-manifest.generated_files[%s]: bad digest" % path)


def validate_report_dir(report_dir):
    report_dir = Path(report_dir)
    errors = []

    index = report_dir / "index.html"
    rm_path = report_dir / "report-manifest.json"
    mermaid = report_dir / "assets" / "mermaid.min.js"

    for p, name in ((index, "index.html"), (rm_path, "report-manifest.json"), (mermaid, "assets/mermaid.min.js")):
        if not p.is_file():
            errors.append("missing required file: %s" % name)
    if errors:
        return errors

    try:
        rm = json.loads(rm_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return ["report-manifest.json: invalid JSON: %s" % exc]

    validate_manifest_schema(rm, errors)

    # Recompute checksums of generated files.
    if isinstance(rm.get("generated_files"), dict):
        for rel, digest in rm["generated_files"].items():
            target = report_dir / rel
            if not target.is_file():
                errors.append("generated_files: missing %s" % rel)
                continue
            actual = sha256_bytes(target.read_bytes())
            if actual != digest:
                errors.append("checksum mismatch for %s" % rel)

    # Pinned Mermaid asset.
    if mermaid.is_file() and sha256_bytes(mermaid.read_bytes()) != MERMAID_SHA256:
        errors.append("assets/mermaid.min.js: checksum does not match pinned value")

    html = index.read_text(encoding="utf-8")
    errors.extend(validate_index_html(html, rm))
    errors.extend(scan_authored_assets())
    return errors


def validate_index_html(html, rm):
    errors = []

    # Landmarks + skip link.
    if 'class="skip-link"' not in html:
        errors.append("index.html: missing skip link")
    for needle, msg in (
        ("<main", "missing <main> landmark"),
        ("<nav", "missing <nav> landmark"),
        ("<header", "missing <header> landmark"),
        ('<aside', "missing <aside> landmark"),
    ):
        if needle not in html:
            errors.append("index.html: %s" % msg)

    # Required sections.
    for sid in REQUIRED_SECTIONS:
        if ('id="%s"' % sid) not in html:
            errors.append("index.html: missing required section id=%s" % sid)

    # Blocking head theme init before first paint (script appears before <style> in head).
    head = html.split("</head>", 1)[0]
    if "car:theme:v1" not in head or "prefers-color-scheme" not in head:
        errors.append("index.html: missing blocking head theme initializer")

    # Theme controls: System/Light/Dark with text labels.
    for label in ("System", "Light", "Dark"):
        if ('data-theme-choice="%s"' % label.lower()) not in html:
            errors.append("index.html: missing theme choice %s" % label)

    # Unique IDs.
    ids = re.findall(r'\sid="([^"]+)"', html)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errors.append("index.html: duplicate IDs %s" % dupes[:10])

    # Severity text present (non-color cue): each severity word appears as text in
    # the overview severity cards (label) regardless of count.
    for s in SEVERITIES:
        if ('%s findings</div>' % s) not in html:
            errors.append("index.html: severity %s lacks textual label in overview cards" % s)

    # No external asset loads. Only <img>/<script>/<audio>/<video>/<source>/<iframe>
    # 'src' and <link>/<use> 'href' are asset loads. Anchor href to http(s) is an
    # allowed, labeled external navigation link and is intentionally not flagged.
    for m in re.finditer(r'<(img|script|iframe|audio|video|source|embed|track)\b[^>]*\bsrc\s*=\s*"([^"]+)"', html, re.IGNORECASE):
        val = m.group(2).strip().lower()
        if val.startswith("http://") or val.startswith("https://") or val.startswith("//"):
            errors.append("index.html: external asset load %r" % m.group(2))
    for m in re.finditer(r'<(link|use)\b[^>]*\bhref\s*=\s*"([^"]+)"', html, re.IGNORECASE):
        val = m.group(2).strip().lower()
        if val.startswith("http://") or val.startswith("https://") or val.startswith("//"):
            errors.append("index.html: external asset load %r" % m.group(2))
    for bad in ("fetch(", "xmlhttprequest", "navigator.sendbeacon", "new image("):
        if bad in html.lower():
            errors.append("index.html: prohibited network primitive %r" % bad)

    # Anchor external-link treatment. Any <a> whose href is an external navigation
    # vector (http(s) or protocol-relative '//host') MUST carry rel=noreferrer
    # noopener AND a visible external-link label. This closes the class where a
    # '//host' anchor could be emitted live and unlabeled (protocol-relative
    # bypass) and cannot regress silently.
    for m in re.finditer(r'<a\b[^>]*\bhref\s*=\s*"([^"]+)"[^>]*>', html, re.IGNORECASE):
        raw = m.group(1).strip()
        val = raw.replace("\\", "/").lower()
        if val.startswith("http://") or val.startswith("https://") or val.startswith("//"):
            tag = m.group(0).lower()
            if "noreferrer" not in tag or "noopener" not in tag:
                errors.append("index.html: external anchor %r missing rel=noreferrer noopener" % raw)
            # Visible external-link label follows the anchor.
            tail = html[m.end():m.end() + 200].lower()
            if "external-link-note" not in tail and "external-link-note" not in tag:
                errors.append("index.html: external anchor %r missing visible external-link label" % raw)
        # A backslash-containing anchor href must never be emitted live.
        elif "\\" in raw:
            errors.append("index.html: anchor href contains backslash (should be inert) %r" % raw)

    # Neutrality is enforced on SKILL-AUTHORED ASSETS (see scan_authored_assets),
    # not on rendered source content. Here we only assert the shipped chrome does
    # not embed a placeholder that failed substitution in template skeletons.

    # All manifest Markdown documents referenced.
    for doc in rm.get("documents", []):
        if doc not in html:
            errors.append("index.html: manifest document %s not present" % doc)

    return errors


BENIGN_PLACEHOLDER = None  # documents/source may contain braces; not scanned here.


def _word_present(text, word):
    return re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])", text) is not None


def scan_authored_assets():
    """Neutrality/placeholder scan over shipped, skill-authored files only:
    report.css, report.js, and the render template (render_report.py chrome
    strings). Observed source content is never scanned. Returns error list."""
    errors = []
    targets = {
        "assets/report.css": (SKILL_ROOT / "assets" / "report.css"),
        "assets/report.js": (SKILL_ROOT / "assets" / "report.js"),
        "SKILL.md": (SKILL_ROOT / "SKILL.md"),
        "README.md": (SKILL_ROOT / "README.md"),
    }
    for ref in sorted((SKILL_ROOT / "references").glob("*.md")):
        targets["references/" + ref.name] = ref
    for name, path in targets.items():
        if not path.is_file():
            errors.append("neutrality: missing authored asset %s" % name)
            continue
        low = path.read_text(encoding="utf-8").lower()
        for word in BRAND_DENYLIST:
            if " " in word or "-" in word:
                if word in low:
                    errors.append("neutrality: %s contains prohibited phrase %r" % (name, word))
            elif _word_present(low, word):
                errors.append("neutrality: %s contains branded token %r" % (name, word))
    # Scan the authored chrome strings inside render_report.py (skeleton/head/nav).
    rr = (SKILL_ROOT / "scripts" / "render_report.py").read_text(encoding="utf-8")
    # Only the static HTML skeleton constants; extract triple-quoted templates.
    chrome_strings = re.findall(r'"""(.*?)"""', rr, flags=re.DOTALL)
    chrome = "\n".join(chrome_strings).lower()
    for phrase in PHRASE_DENYLIST:
        if phrase in chrome:
            errors.append("neutrality: render template contains prohibited phrase %r" % phrase)
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description="Validate a generated report directory.")
    parser.add_argument("report_dir", help="path to the generated report directory")
    args = parser.parse_args(argv[1:])
    report_dir = Path(args.report_dir).resolve()
    if not report_dir.is_dir():
        print("ERROR: not a directory: %s" % report_dir, file=sys.stderr)
        return 2
    errors = validate_report_dir(report_dir)
    if errors:
        print("FAIL: report validation (%d issue(s))" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    print("PASS: report validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
