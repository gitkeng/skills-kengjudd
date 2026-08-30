#!/usr/bin/env python3
"""Validate comprehensive-codebase-analysis v2 output using Python stdlib only."""

import json
import re
import sys
from pathlib import Path

SEVERITIES = {"critical", "high", "medium", "low"}
CONFIDENCE = {"verified", "inferred", "assumption"}
CANONICAL_RE = re.compile(r"^(br|td|v|tc|cmp):[A-Za-z0-9._%/-]+:[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9._-]*$")
ALIASES = {
    "br": re.compile(r"^BR-[0-9]{3}$"),
    "td": re.compile(r"^TD-[0-9]{3}$"),
    "v": re.compile(r"^V-[0-9]{3}$"),
    "tc": re.compile(r"^TC-[0-9]{3}$"),
    "cmp": re.compile(r"^CMP-[0-9]{3}$"),
}
PHASES = [
    "inventory", "architecture", "behavior", "reference-analysis",
    "debt-specialized", "operations-diagrams", "migration-onboarding", "synthesis",
]
ROOT_FILES = [
    "README.md", "project-overview.md", "executive-summary.md", "reading-guide.md",
    "technical-debt-report.md", "onboarding.md", "manifest.json", "progress.json",
]
MARKDOWN_FILES = [
    "README.md", "project-overview.md", "executive-summary.md", "reading-guide.md",
    "technical-debt-report.md", "onboarding.md",
    "architecture/system-overview.md", "architecture/components.md",
    "architecture/dependencies.md", "architecture/patterns.md",
    "behavior/business-logic.md", "behavior/workflows.md",
    "behavior/decision-logic.md", "behavior/error-handling.md",
    "reference/program-structure.md", "reference/interfaces.md",
    "reference/data-models.md", "reference/api-reference.md", "reference/modules.md",
    "analysis/code-metrics.md", "analysis/complexity-analysis.md",
    "analysis/dependency-analysis.md", "analysis/security-patterns.md", "analysis/tech-debt.md",
    "technical-debt/summary.md", "technical-debt/outdated-components.md",
    "technical-debt/maintenance-burden.md", "technical-debt/remediation-plan.md",
    "diagrams/structural/component-diagrams.md",
    "diagrams/behavioral/sequence-diagrams.md",
    "diagrams/architecture/system-context.md",
    "migration/component-order.md", "migration/test-specifications.md",
    "migration/validation-criteria.md", "specialized/database-patterns.md",
    "specialized/security-analysis.md", "operations/build-cicd-iac.md",
    "operations/testing-observability.md",
]
REQUIRED_FILES = set(MARKDOWN_FILES + ["manifest.json", "progress.json"])
REQUIRED_DIRS = {
    "architecture", "behavior", "reference", "analysis", "technical-debt", "diagrams",
    "diagrams/structural", "diagrams/behavioral", "diagrams/architecture", "migration",
    "specialized", "operations",
}
MERMAID_FILES = {
    "diagrams/structural/component-diagrams.md",
    "diagrams/behavioral/sequence-diagrams.md",
    "diagrams/architecture/system-context.md",
    "reference/data-models.md", "behavior/workflows.md", "architecture/system-overview.md",
}
MERMAID_TYPES = {
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "C4Context", "C4Container", "C4Component",
    "C4Deployment", "architecture-beta", "block-beta", "packet-beta", "journey",
    "gantt", "pie", "mindmap", "timeline", "gitGraph", "quadrantChart", "xychart-beta",
    "sankey-beta", "requirementDiagram", "zenuml",
}


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_str(value):
    return isinstance(value, str) and bool(value.strip())


def load_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path.name}: invalid JSON: {exc}")
        return None


def exact_keys(obj, required, optional, where, errors):
    if not isinstance(obj, dict):
        errors.append(f"{where}: expected object")
        return False
    missing = required - set(obj)
    extra = set(obj) - required - optional
    if missing:
        errors.append(f"{where}: missing keys {sorted(missing)}")
    if extra:
        errors.append(f"{where}: unexpected keys {sorted(extra)}")
    return not missing and not extra


def check_skill_frontmatter(skill_root):
    errors = []
    path = skill_root / "SKILL.md"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [f"SKILL.md unreadable: {exc}"]
    if not lines or lines[0] != "---":
        return ["SKILL.md: missing opening frontmatter delimiter"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return ["SKILL.md: missing closing frontmatter delimiter"]
    fields = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"SKILL.md frontmatter: malformed line {line!r}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"}:
        errors.append("SKILL.md frontmatter must contain only name and description")
    name = fields.get("name", "")
    desc = fields.get("description", "")
    if name != "comprehensive-codebase-analysis" or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append("SKILL.md frontmatter name is invalid")
    if not desc or len(desc) > 1024:
        errors.append("SKILL.md description must contain 1..1024 characters")
    triggers = ("analy", "architecture", "debt", "legacy", "migration")
    if not all(term in desc.lower() for term in triggers):
        errors.append("SKILL.md description does not state all required trigger contexts")
    if len(lines) > 500:
        errors.append(f"SKILL.md has {len(lines)} lines; maximum is 500")
    body_words = len("\n".join(lines[end + 1:]).split())
    if body_words * 1.35 >= 5000:
        errors.append("SKILL.md body token proxy is not below 5000")
    if "allowed-tools" in fields:
        errors.append("SKILL.md uses prohibited allowed-tools frontmatter")
    return errors


def check_tree(root):
    errors = []
    for rel in sorted(REQUIRED_FILES):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"required file is empty: {rel}")
    for rel in sorted(REQUIRED_DIRS):
        if not (root / rel).is_dir():
            errors.append(f"missing required directory: {rel}/")
    if root.is_dir():
        actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        for rel in sorted(actual - REQUIRED_FILES):
            errors.append(f"unexpected output file: {rel}")
    return errors


def check_evidence(value, where, errors):
    if not isinstance(value, list) or not value:
        errors.append(f"{where}.evidence: expected nonempty array")
        return
    for i, evidence in enumerate(value):
        loc = f"{where}.evidence[{i}]"
        if not exact_keys(evidence, {"path", "line_start", "line_end"}, set(), loc, errors):
            continue
        if not is_str(evidence["path"]) or evidence["path"].startswith(("/", "./")) or "\\" in evidence["path"]:
            errors.append(f"{loc}.path: must be repo-relative with forward slashes")
        start, end = evidence["line_start"], evidence["line_end"]
        if start is not None and (not is_int(start) or start < 1):
            errors.append(f"{loc}.line_start: expected positive integer or null")
        if end is not None and (not is_int(end) or end < 1):
            errors.append(f"{loc}.line_end: expected positive integer or null")
        if (start is None) != (end is None):
            errors.append(f"{loc}: line_start and line_end must both be null or integers")
        if is_int(start) and is_int(end) and end < start:
            errors.append(f"{loc}: line_end precedes line_start")


def check_canonical(key, registry, where, errors):
    if not isinstance(key, str) or not CANONICAL_RE.fullmatch(key):
        errors.append(f"{where}.canonical_key: invalid canonical-key syntax")
    elif key.split(":", 1)[0] != registry:
        errors.append(f"{where}.canonical_key: prefix does not match registry {registry}")


def check_manifest(root):
    errors = []
    manifest = load_json(root / "manifest.json", errors)
    if manifest is None:
        return errors, None
    required = {"schema_version", "generated_at", "repository_root", "output_root", "coverage", "documents", "business_rules", "findings", "components", "test_cases", "traceability", "severity_counts", "delta"}
    if not exact_keys(manifest, required, set(), "manifest", errors):
        return errors, manifest
    if manifest["schema_version"] != "2.0":
        errors.append("manifest.schema_version: expected '2.0'")
    for key in ("generated_at", "repository_root", "output_root"):
        if not is_str(manifest[key]):
            errors.append(f"manifest.{key}: expected nonempty string")

    coverage = manifest["coverage"]
    if exact_keys(coverage, {"mode", "components", "limitations"}, set(), "manifest.coverage", errors):
        if coverage["mode"] not in {"full", "focused", "sampled"}:
            errors.append("manifest.coverage.mode: invalid enum")
        if not isinstance(coverage["limitations"], list) or not all(isinstance(x, str) for x in coverage["limitations"]):
            errors.append("manifest.coverage.limitations: expected string array")
        if not isinstance(coverage["components"], list):
            errors.append("manifest.coverage.components: expected array")
        else:
            for i, item in enumerate(coverage["components"]):
                where = f"manifest.coverage.components[{i}]"
                if exact_keys(item, {"component_alias", "depth", "files_read", "rationale"}, set(), where, errors):
                    if not ALIASES["cmp"].fullmatch(item["component_alias"] if isinstance(item["component_alias"], str) else ""):
                        errors.append(f"{where}.component_alias: invalid")
                    if item["depth"] not in {"fully-read", "sampled", "inventory-only"}:
                        errors.append(f"{where}.depth: invalid enum")
                    if not isinstance(item["files_read"], list) or not all(isinstance(x, str) for x in item["files_read"]):
                        errors.append(f"{where}.files_read: expected string array")
                    if not isinstance(item["rationale"], str):
                        errors.append(f"{where}.rationale: expected string")

    aliases = set()
    keys = set()
    alias_kind = {}
    br_coverage = {}

    documents = manifest["documents"]
    doc_paths = []
    if not isinstance(documents, list):
        errors.append("manifest.documents: expected array")
    else:
        for i, doc in enumerate(documents):
            where = f"manifest.documents[{i}]"
            if exact_keys(doc, {"path", "description", "severity_badge"}, set(), where, errors):
                if not is_str(doc["path"]):
                    errors.append(f"{where}.path: expected nonempty string")
                else:
                    doc_paths.append(doc["path"])
                if not is_str(doc["description"]):
                    errors.append(f"{where}.description: expected nonempty string")
                if doc["severity_badge"] not in SEVERITIES | {"none"}:
                    errors.append(f"{where}.severity_badge: invalid enum")
        if len(doc_paths) != len(set(doc_paths)):
            errors.append("manifest.documents: duplicate paths")
        if set(doc_paths) != REQUIRED_FILES:
            errors.append("manifest.documents: paths must equal the declared output file set")

    business_rules = manifest["business_rules"]
    if not isinstance(business_rules, list):
        errors.append("manifest.business_rules: expected array")
    else:
        for i, rule in enumerate(business_rules):
            where = f"manifest.business_rules[{i}]"
            req = {"canonical_key", "alias", "rule", "confidence", "evidence", "coverage_status"}
            if not exact_keys(rule, req, set(), where, errors):
                continue
            check_canonical(rule["canonical_key"], "br", where, errors)
            if not ALIASES["br"].fullmatch(rule["alias"] if isinstance(rule["alias"], str) else ""):
                errors.append(f"{where}.alias: invalid BR alias")
            if not is_str(rule["rule"]):
                errors.append(f"{where}.rule: expected nonempty string")
            if rule["confidence"] not in CONFIDENCE:
                errors.append(f"{where}.confidence: invalid enum")
            if rule["coverage_status"] not in {"covered", "untested"}:
                errors.append(f"{where}.coverage_status: invalid enum")
            check_evidence(rule["evidence"], where, errors)
            br_coverage[rule["alias"]] = rule["coverage_status"]
            alias_kind[rule["alias"]] = "br"
            if rule["alias"] in aliases: errors.append(f"duplicate alias: {rule['alias']}")
            if rule["canonical_key"] in keys: errors.append(f"duplicate canonical key: {rule['canonical_key']}")
            aliases.add(rule["alias"]); keys.add(rule["canonical_key"])

    findings = manifest["findings"]
    counts = {level: 0 for level in SEVERITIES}
    if not isinstance(findings, list):
        errors.append("manifest.findings: expected array")
    else:
        for i, finding in enumerate(findings):
            where = f"manifest.findings[{i}]"
            req = {"canonical_key", "alias", "registry", "title", "kind", "severity", "confidence", "status", "evidence"}
            if not exact_keys(finding, req, set(), where, errors):
                continue
            registry = finding["registry"]
            if registry not in {"td", "v"}:
                errors.append(f"{where}.registry: invalid enum")
                continue
            check_canonical(finding["canonical_key"], registry, where, errors)
            if not ALIASES[registry].fullmatch(finding["alias"] if isinstance(finding["alias"], str) else ""):
                errors.append(f"{where}.alias: does not match registry")
            if not is_str(finding["title"]) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", finding["kind"] if isinstance(finding["kind"], str) else ""):
                errors.append(f"{where}: invalid title or kind")
            if finding["severity"] not in SEVERITIES:
                errors.append(f"{where}.severity: invalid enum")
            else:
                counts[finding["severity"]] += 1
            if finding["confidence"] not in CONFIDENCE:
                errors.append(f"{where}.confidence: invalid enum")
            if finding["status"] not in {"open", "accepted", "remediated"}:
                errors.append(f"{where}.status: invalid enum")
            check_evidence(finding["evidence"], where, errors)
            alias_kind[finding["alias"]] = registry
            if finding["alias"] in aliases: errors.append(f"duplicate alias: {finding['alias']}")
            if finding["canonical_key"] in keys: errors.append(f"duplicate canonical key: {finding['canonical_key']}")
            aliases.add(finding["alias"]); keys.add(finding["canonical_key"])

    components = manifest["components"]
    component_aliases = set()
    if not isinstance(components, list):
        errors.append("manifest.components: expected array")
    else:
        for i, component in enumerate(components):
            where = f"manifest.components[{i}]"
            req = {"canonical_key", "alias", "name", "path", "namespace"}
            if not exact_keys(component, req, set(), where, errors):
                continue
            check_canonical(component["canonical_key"], "cmp", where, errors)
            if not ALIASES["cmp"].fullmatch(component["alias"] if isinstance(component["alias"], str) else ""):
                errors.append(f"{where}.alias: invalid CMP alias")
            if not is_str(component["name"]) or not is_str(component["path"]):
                errors.append(f"{where}: name and path must be nonempty strings")
            if component["namespace"] is not None and not isinstance(component["namespace"], str):
                errors.append(f"{where}.namespace: expected string or null")
            alias_kind[component["alias"]] = "cmp"; component_aliases.add(component["alias"])
            if component["alias"] in aliases: errors.append(f"duplicate alias: {component['alias']}")
            if component["canonical_key"] in keys: errors.append(f"duplicate canonical key: {component['canonical_key']}")
            aliases.add(component["alias"]); keys.add(component["canonical_key"])

    test_cases = manifest["test_cases"]
    test_aliases = set()
    if not isinstance(test_cases, list):
        errors.append("manifest.test_cases: expected array")
    else:
        for i, test in enumerate(test_cases):
            where = f"manifest.test_cases[{i}]"
            req = {"canonical_key", "alias", "category", "title", "source_refs", "status"}
            if not exact_keys(test, req, set(), where, errors):
                continue
            check_canonical(test["canonical_key"], "tc", where, errors)
            if not ALIASES["tc"].fullmatch(test["alias"] if isinstance(test["alias"], str) else ""):
                errors.append(f"{where}.alias: invalid TC alias")
            category = test["category"]
            if category not in {"behavioral", "security", "infrastructure"}:
                errors.append(f"{where}.category: invalid enum")
            if not is_str(test["title"]): errors.append(f"{where}.title: expected nonempty string")
            refs = test["source_refs"]
            if not isinstance(refs, list) or not refs:
                errors.append(f"{where}.source_refs: expected nonempty array")
            else:
                for ref in refs:
                    if ref not in aliases or alias_kind.get(ref) not in {"br", "v", "td", "cmp"}:
                        errors.append(f"{where}.source_refs: unresolved reference {ref!r}")
                    if category == "behavioral" and alias_kind.get(ref) != "br":
                        errors.append(f"{where}: behavioral tests may reference only BR aliases")
                    if category in {"security", "infrastructure"} and alias_kind.get(ref) not in {"v", "td", "cmp"}:
                        errors.append(f"{where}: security/infrastructure source must be V, TD, or CMP")
            if test["status"] not in {"specification", "existing"}:
                errors.append(f"{where}.status: invalid enum")
            if test["alias"] in aliases: errors.append(f"duplicate alias: {test['alias']}")
            if test["canonical_key"] in keys: errors.append(f"duplicate canonical key: {test['canonical_key']}")
            aliases.add(test["alias"]); keys.add(test["canonical_key"]); test_aliases.add(test["alias"])

    trace = manifest["traceability"]
    linked_brs = set()
    if not isinstance(trace, list):
        errors.append("manifest.traceability: expected array")
    else:
        seen_links = set()
        for i, link in enumerate(trace):
            where = f"manifest.traceability[{i}]"
            if exact_keys(link, {"business_rule", "test_case"}, set(), where, errors):
                pair = (link["business_rule"], link["test_case"])
                if pair in seen_links: errors.append(f"{where}: duplicate link")
                seen_links.add(pair)
                if alias_kind.get(link["business_rule"]) != "br": errors.append(f"{where}: unresolved BR")
                if link["test_case"] not in test_aliases: errors.append(f"{where}: unresolved TC")
                linked_brs.add(link["business_rule"])
    for alias, status in br_coverage.items():
        if status == "covered" and alias not in linked_brs:
            errors.append(f"business rule {alias} is covered but has no traceability link")
        if status == "untested" and alias in linked_brs:
            errors.append(f"business rule {alias} is untested but has a traceability link")

    severity_counts = manifest["severity_counts"]
    if exact_keys(severity_counts, SEVERITIES, set(), "manifest.severity_counts", errors):
        for level in SEVERITIES:
            if not is_int(severity_counts[level]) or severity_counts[level] < 0:
                errors.append(f"manifest.severity_counts.{level}: expected nonnegative integer")
            elif severity_counts[level] != counts[level]:
                errors.append(f"manifest.severity_counts.{level}: expected {counts[level]}")

    delta = manifest["delta"]
    delta_lists = {}
    if exact_keys(delta, {"prior_manifest_loaded", "new", "resolved", "regressed", "persisted"}, set(), "manifest.delta", errors):
        if not isinstance(delta["prior_manifest_loaded"], bool): errors.append("manifest.delta.prior_manifest_loaded: expected boolean")
        for state in ("new", "resolved", "regressed", "persisted"):
            values = delta[state]
            if not isinstance(values, list):
                errors.append(f"manifest.delta.{state}: expected array"); continue
            delta_lists[state] = values
            if len(values) != len(set(values)): errors.append(f"manifest.delta.{state}: duplicate key")
            for key in values:
                if not isinstance(key, str) or not CANONICAL_RE.fullmatch(key): errors.append(f"manifest.delta.{state}: invalid canonical key {key!r}")
        all_delta = [key for values in delta_lists.values() for key in values]
        if len(all_delta) != len(set(all_delta)): errors.append("manifest.delta: states overlap")
        current_finding_keys = {f.get("canonical_key") for f in findings if isinstance(f, dict)} if isinstance(findings, list) else set()
        for state in ("new", "regressed", "persisted"):
            if not set(delta_lists.get(state, [])) <= current_finding_keys:
                errors.append(f"manifest.delta.{state}: contains non-current finding key")
        if delta.get("prior_manifest_loaded") is False:
            if delta_lists.get("resolved") or delta_lists.get("regressed") or delta_lists.get("persisted"):
                errors.append("manifest.delta: first run cannot contain resolved/regressed/persisted")
            if set(delta_lists.get("new", [])) != current_finding_keys:
                errors.append("manifest.delta.new: first run must list every current finding")

    coverage_aliases = {c.get("component_alias") for c in coverage.get("components", []) if isinstance(c, dict)} if isinstance(coverage, dict) else set()
    if coverage_aliases != component_aliases:
        errors.append("manifest.coverage.components must contain every component alias exactly once")
    return errors, manifest


def check_progress(root):
    errors = []
    progress = load_json(root / "progress.json", errors)
    if progress is None: return errors
    req = {"schema_version", "run_id", "repository_root", "output_root", "status", "current_phase", "phases", "prior_manifest_loaded", "updated_at"}
    if not exact_keys(progress, req, set(), "progress", errors): return errors
    if progress["schema_version"] != "2.0": errors.append("progress.schema_version: expected '2.0'")
    for key in ("run_id", "repository_root", "output_root", "updated_at"):
        if not is_str(progress[key]): errors.append(f"progress.{key}: expected nonempty string")
    if progress["status"] != "completed": errors.append("progress.status: final output must be completed")
    if progress["current_phase"] != "completed": errors.append("progress.current_phase: final output must be completed")
    if not isinstance(progress["prior_manifest_loaded"], bool): errors.append("progress.prior_manifest_loaded: expected boolean")
    phases = progress["phases"]
    if not isinstance(phases, list) or len(phases) != len(PHASES):
        errors.append("progress.phases: expected exactly eight phases")
    else:
        ids = []
        for i, phase in enumerate(phases):
            where = f"progress.phases[{i}]"
            if exact_keys(phase, {"id", "status", "completed_at", "artifacts"}, set(), where, errors):
                ids.append(phase["id"])
                if phase["status"] != "completed": errors.append(f"{where}.status: expected completed")
                if not is_str(phase["completed_at"]): errors.append(f"{where}.completed_at: expected timestamp string")
                if not isinstance(phase["artifacts"], list) or not all(isinstance(x, str) for x in phase["artifacts"]): errors.append(f"{where}.artifacts: expected string array")
        if ids != PHASES: errors.append("progress.phases: IDs/order do not match declared phases")
    return errors


def mermaid_blocks(text):
    return re.findall(r"```mermaid[ \t]*\n(.*?)```", text, flags=re.DOTALL)


def balanced(block):
    stack = []
    pairs = {"]": "[", ")": "(", "}": "{"}
    openers = set(pairs.values())
    in_quote = False
    escaped = False
    for line in block.splitlines():
        if line.lstrip().startswith("%%"): continue
        for index, char in enumerate(line):
            if escaped: escaped = False; continue
            if char == "\\" and in_quote: escaped = True; continue
            if char == '"': in_quote = not in_quote; continue
            if in_quote: continue
            previous = line[index - 1] if index else ""
            following = line[index + 1] if index + 1 < len(line) else ""
            if char == "{" and previous and previous in "o|": continue
            if char == "}" and following and following in "o|": continue
            if char in openers: stack.append(char)
            elif char in pairs:
                if not stack or stack.pop() != pairs[char]: return False
    return not stack and not in_quote


# --------------------------------------------------------------------------- #
# Mermaid syntax rules beyond bracket balance.
#
# balanced() answers "are the brackets paired", which is not the same question
# as "will this render". Every rule below encodes a construct that Mermaid v11
# rejects outright — a parse error blanks the WHOLE block, not one line — while
# the brackets stay perfectly balanced. Rules are keyed by diagram type because
# the same token is legal in one and fatal in another: `loop["Per page"]` is an
# ordinary node in a flowchart but a block opener in a sequenceDiagram, and
# `actor` is a declaration keyword in a sequenceDiagram but only a node name in
# a flowchart.
#
# This is a heuristic, not a grammar; it cannot be complete. It is calibrated
# against the real parser to raise no false positives, so a report is never
# blocked over syntax Mermaid actually accepts.
# --------------------------------------------------------------------------- #
FLOWCHART_TYPES = {"flowchart", "graph"}
FLOWCHART_DIRECTIONS = {"TB", "TD", "BT", "RL", "LR"}
# Declaration keywords that only exist in a sequenceDiagram.
SEQUENCE_ONLY_KEYWORDS = {"actor", "participant", "autonumber", "activate", "deactivate"}
# Block openers closed by `end`, per diagram type.
SEQUENCE_BLOCK_OPENERS = {"loop", "alt", "opt", "par", "critical", "rect", "break", "box"}
# A flowchart edge, ending right where the target node id must begin.
ARROW_TAIL_RE = re.compile(r"(?:-{2,}[->ox]|-{2,}|-\.-*>?|={2,}>?|~~~)\s*(?=[\[({])")
SEQ_MESSAGE_RE = re.compile(r"^[^:]*?(?:-{1,2}>>?|-{1,2}[)x])[+-]?[^:]*:(?P<text>.*)$")


def strip_quoted(line):
    """Replace double-quoted spans with same-length filler so rules below never
    match punctuation that Mermaid treats as literal label text."""
    out, in_quote, escaped = [], False, False
    for char in line:
        if escaped:
            out.append("_"); escaped = False; continue
        if char == "\\" and in_quote:
            out.append("_"); escaped = True; continue
        if char == '"':
            in_quote = not in_quote; out.append('"'); continue
        out.append("_" if in_quote else char)
    return "".join(out)


def significant_lines(block):
    """(1-based index, line) pairs, skipping blanks and %% comment lines."""
    for number, line in enumerate(block.splitlines(), 1):
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            yield number, line


def lint_mermaid_block(block):
    """Return a list of human-readable syntax problems in one Mermaid block."""
    problems = []
    body = block.strip()
    if not body:
        return ["empty block"]
    tokens = body.split()
    diagram_type = tokens[0]
    is_flowchart = diagram_type in FLOWCHART_TYPES
    is_sequence = diagram_type == "sequenceDiagram"

    # R6 — flowchart direction must be one Mermaid knows.
    if is_flowchart and len(tokens) > 1:
        direction = tokens[1].rstrip(";")
        if direction not in FLOWCHART_DIRECTIONS and not direction.startswith("%%"):
            problems.append(
                f"line 1: {diagram_type} direction {direction!r} is not one of "
                + "/".join(sorted(FLOWCHART_DIRECTIONS))
            )

    depth = 0
    for number, raw in significant_lines(block):
        line = strip_quoted(raw)
        stripped = line.strip()
        first = stripped.split()[0] if stripped.split() else ""

        # R1 — a shape token belongs to a node id; it may not follow an edge.
        if is_flowchart and ARROW_TAIL_RE.search(line):
            problems.append(
                f"line {number}: edge is followed by a node shape with no node id "
                f"(write `--> id[\"label\"]`, not `-->[\"label\"]`)"
            )

        # R2 — sequenceDiagram declaration keywords are fatal inside a flowchart.
        if is_flowchart and first in SEQUENCE_ONLY_KEYWORDS and len(stripped.split()) > 1:
            problems.append(
                f"line {number}: {first!r} is a sequenceDiagram keyword and cannot "
                f"declare a node in a {diagram_type} (drop it and write the node alone)"
            )

        # R3 — `;` ends a statement; a sequence message is not quoted, so a `;`
        # inside the message text truncates it and orphans the remainder.
        if is_sequence:
            match = SEQ_MESSAGE_RE.match(line)
            if match and ";" in match.group("text").rstrip().rstrip(";"):
                problems.append(
                    f"line {number}: ';' inside a sequence message ends the statement "
                    f"and orphans the rest of the text (use ',' instead)"
                )

        # R4 — block openers must be closed by `end`.
        if is_flowchart and first == "subgraph":
            depth += 1
        elif is_sequence and first in SEQUENCE_BLOCK_OPENERS:
            depth += 1
        elif first == "end" and (is_flowchart or is_sequence):
            depth -= 1
            if depth < 0:
                problems.append(f"line {number}: `end` without a matching block opener")
                depth = 0

        # R5 — flowchart edge labels are delimited by a pair of pipes.
        if is_flowchart and stripped.count("|") % 2:
            problems.append(f"line {number}: odd number of '|' — an edge label is not closed")

    if depth > 0:
        problems.append(f"{depth} unclosed block(s): every subgraph/loop/alt/opt needs an `end`")
    return problems


def lint_block(rel, index, block, errors):
    tokens = block.strip().split()
    diagram_type = tokens[0] if tokens else ""
    if diagram_type not in MERMAID_TYPES:
        errors.append(f"{rel} block {index}: invalid Mermaid v11 first token {diagram_type!r}")
    if not balanced(block):
        errors.append(f"{rel} block {index}: unbalanced brackets or quotes")
    for problem in lint_mermaid_block(block):
        errors.append(f"{rel} block {index}: {problem}")
    return diagram_type


def check_mermaid(root):
    errors = []
    types_by_file = {}
    for rel in sorted(MERMAID_FILES):
        text = (root / rel).read_text(encoding="utf-8")
        blocks = mermaid_blocks(text)
        if not blocks:
            errors.append(f"{rel}: required Mermaid fenced block missing"); continue
        types_by_file[rel] = []
        for index, block in enumerate(blocks, 1):
            types_by_file[rel].append(lint_block(rel, index, block, errors))
    # MERMAID_FILES lists where a diagram is REQUIRED. Diagrams also appear
    # wherever a template asks for one (architecture/dependencies.md among
    # them), and a broken diagram is just as broken there — so every Mermaid
    # block in the tree is linted, while only these files must contain one.
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel in MERMAID_FILES:
            continue
        for index, block in enumerate(mermaid_blocks(path.read_text(encoding="utf-8")), 1):
            lint_block(rel, index, block, errors)
    if "erDiagram" not in types_by_file.get("reference/data-models.md", []): errors.append("reference/data-models.md: erDiagram required")
    if "flowchart" not in types_by_file.get("behavior/workflows.md", []): errors.append("behavior/workflows.md: flowchart required")
    structural = types_by_file.get("diagrams/structural/component-diagrams.md", [])
    if "flowchart" not in structural and "C4Component" not in structural: errors.append("structural diagrams: component diagram required")
    if not ({"classDiagram", "flowchart"} & set(structural)): errors.append("structural diagrams: class/package diagram required")
    behavioral = types_by_file.get("diagrams/behavioral/sequence-diagrams.md", [])
    if behavioral.count("sequenceDiagram") < 2: errors.append("behavioral diagrams: at least two sequenceDiagram blocks required")
    if not ({"stateDiagram", "stateDiagram-v2", "flowchart"} & set(behavioral)): errors.append("behavioral diagrams: lifecycle state/activity diagram required")
    return errors


def check_behavior_banners(root):
    errors = []
    for rel in ("behavior/business-logic.md", "behavior/workflows.md", "behavior/decision-logic.md", "behavior/error-handling.md"):
        first = "\n".join((root / rel).read_text(encoding="utf-8").splitlines()[:8])
        if not re.search(r"^>\s*Confidence:\s*(high|medium|low)\s+(?:—|-)\s+\S", first, flags=re.MULTILINE | re.IGNORECASE):
            errors.append(f"{rel}: calibrated high/medium/low confidence banner missing near top")
    return errors


def check_readme(root, manifest):
    errors = []
    text = (root / "README.md").read_text(encoding="utf-8")
    links = {}
    for match in re.finditer(r"^\s*[-*]\s+\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)\s*(?:[-—:]\s*)(.*)$", text, flags=re.MULTILINE):
        links[match.group(1)] = match.group(2).strip()
    for rel in sorted(REQUIRED_FILES - {"README.md"}):
        if rel not in links: errors.append(f"README.md: missing navigation link to {rel}")
        elif not links[rel]: errors.append(f"README.md: link to {rel} lacks one-line description")
    if manifest:
        counts = manifest.get("severity_counts", {})
        for level in sorted(SEVERITIES):
            count = counts.get(level)
            patterns = [rf"{level}\D{{0,20}}{count}\b", rf"\b{count}\D{{0,20}}{level}"]
            if is_int(count) and not any(re.search(p, text, re.IGNORECASE) for p in patterns):
                errors.append(f"README.md: does not display manifest {level} count {count}")
    return errors


def main(argv):
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print("Usage: validate_output.py <output-root>", file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"ERROR: output root is not a directory: {root}", file=sys.stderr)
        return 2
    skill_root = Path(__file__).resolve().parent.parent
    checks = []
    checks.append(("skill frontmatter and limits", check_skill_frontmatter(skill_root)))
    tree_errors = check_tree(root)
    checks.append(("declared output tree", tree_errors))
    if tree_errors:
        for name, errors in checks:
            print(("PASS" if not errors else "FAIL") + f": {name}")
            for error in errors: print(f"  - {error}")
        return 1
    manifest_errors, manifest = check_manifest(root)
    checks.append(("manifest structure and references", manifest_errors))
    checks.append(("progress structure", check_progress(root)))
    checks.append(("Mermaid v11 syntax", check_mermaid(root)))
    checks.append(("behavior confidence banners", check_behavior_banners(root)))
    checks.append(("README navigation and badges", check_readme(root, manifest)))
    failed = 0
    for name, errors in checks:
        if errors:
            failed += 1
            print(f"FAIL: {name}")
            for error in errors: print(f"  - {error}")
        else:
            print(f"PASS: {name}")
    print(f"Validation {'failed' if failed else 'passed'}: {failed} failing check group(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
