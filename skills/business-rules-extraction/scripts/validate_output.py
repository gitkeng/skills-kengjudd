#!/usr/bin/env python3
"""Validate business-rules-extraction output against shipped schemas and structural rules.

CLI: python3 scripts/validate_output.py <output-dir> [--repo <analyzed-repo-root>] [--format text|json]
Exit codes: 0 = pass, 1 = validation failure, 2 = usage/IO error.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Minimal JSON Schema subset interpreter
# Supports: required, type, enum, pattern, minItems, properties, items traversal
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _check_type(value, type_spec):
    """Check if value matches a JSON Schema type or type-array."""
    if isinstance(type_spec, list):
        return any(_check_type(value, t) for t in type_spec)
    expected = _TYPE_MAP.get(type_spec)
    if expected is None:
        return True  # unknown type — skip
    return isinstance(value, expected)


def validate_schema(data, schema, path="$"):
    """Validate data against a JSON Schema subset. Returns list of error strings."""
    errors = []
    if not isinstance(schema, dict):
        return errors

    # type
    if "type" in schema:
        if not _check_type(data, schema["type"]):
            errors.append(f"{path}: expected type {schema['type']}, got {type(data).__name__}")
            return errors  # cannot validate further if type is wrong

    # enum
    if "enum" in schema:
        if data not in schema["enum"]:
            errors.append(f"{path}: value {data!r} not in enum {schema['enum']}")

    # pattern
    if "pattern" in schema and isinstance(data, str):
        if not re.search(schema["pattern"], data):
            errors.append(f"{path}: '{data}' does not match pattern {schema['pattern']}")

    # minItems
    if "minItems" in schema and isinstance(data, list):
        if len(data) < schema["minItems"]:
            errors.append(f"{path}: array has {len(data)} items, minimum is {schema['minItems']}")

    # required
    if "required" in schema and isinstance(data, dict):
        for field in schema["required"]:
            if field not in data:
                errors.append(f"{path}: missing required field '{field}'")

    # properties
    if "properties" in schema and isinstance(data, dict):
        for prop, prop_schema in schema["properties"].items():
            if prop in data:
                errors.extend(validate_schema(data[prop], prop_schema, f"{path}.{prop}"))

    # items
    if "items" in schema and isinstance(data, list):
        for i, item in enumerate(data):
            errors.extend(validate_schema(item, schema["items"], f"{path}[{i}]"))

    return errors


# ---------------------------------------------------------------------------
# Finding accumulator
# ---------------------------------------------------------------------------

class Findings:
    def __init__(self):
        self.errors = []  # (check_class: int, message: str)

    def add(self, check_class, message):
        self.errors.append((check_class, message))

    @property
    def passed(self):
        return len(self.errors) == 0

    def summary(self, fmt="text"):
        if fmt == "json":
            return json.dumps({
                "passed": self.passed,
                "total_errors": len(self.errors),
                "errors": [{"class": c, "message": m} for c, m in self.errors],
            }, indent=2)
        lines = []
        if self.passed:
            lines.append("PASSED — all checks passed.")
        else:
            lines.append(f"FAILED — {len(self.errors)} error(s) found:")
            for c, m in self.errors:
                lines.append(f"  [class {c}] {m}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_forward_slash(p):
    """Normalize any path-like to a forward-slash string."""
    return str(p).replace("\\", "/")


def _path_is_within(child, parent):
    """Check child path is contained within parent (Python 3.8 compatible).

    Uses os.path.commonpath for robust containment — handles symlinks,
    redundant separators, and case-folding on case-insensitive file systems
    better than naive string prefix matching.
    """
    try:
        child_resolved = os.path.realpath(str(child))
        parent_resolved = os.path.realpath(str(parent))
    except (OSError, ValueError):
        return False
    # os.path.commonpath raises ValueError if paths are on different drives (Windows)
    try:
        common = os.path.commonpath([child_resolved, parent_resolved])
    except ValueError:
        return False
    return os.path.normcase(common) == os.path.normcase(parent_resolved)


def _is_safe_repo_relative_path(path_str):
    """Validate a path string is a safe repo-relative POSIX path.

    Rejects:
    - Empty/whitespace-only strings
    - Paths containing backslashes
    - Absolute paths (leading '/')
    - Windows drive-letter paths (e.g. 'C:...')
    - Segments that are empty, '.', or '..' (traversal)

    Returns (True, "") on success or (False, reason) on failure.
    """
    if not path_str or not path_str.strip():
        return False, "path is empty"
    if "\\" in path_str:
        return False, "path contains backslash"
    if path_str.startswith("/"):
        return False, "path is absolute (starts with /)"
    # Drive-letter check: e.g. C: or C:/
    if len(path_str) >= 2 and path_str[1] == ":" and path_str[0].isalpha():
        return False, "path contains drive letter"
    # Check each segment
    segments = path_str.split("/")
    for seg in segments:
        if seg == "":
            return False, "path contains empty segment (double slash)"
        if seg == ".":
            return False, "path contains '.' segment"
        if seg == "..":
            return False, "path contains '..' segment (traversal)"
    return True, ""


def read_json(path, findings, check_class):
    """Read and parse a JSON file. Returns parsed data or None on failure."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return json.loads(text)
    except json.JSONDecodeError as e:
        findings.add(check_class, f"Invalid JSON in {path}: {e}")
        return None
    except OSError as e:
        findings.add(check_class, f"Cannot read {path}: {e}")
        return None


def read_text_tolerant(path):
    """Read file text with encoding error tolerance. Returns text or None."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _is_stub_content(text):
    """Return True if text is whitespace-only or an obvious placeholder stub."""
    stripped = text.strip()
    if not stripped:
        return True
    # Obvious placeholder patterns
    lower = stripped.lower()
    if lower in ("todo", "tbd", "placeholder", "# todo", "# tbd", "# placeholder",
                 "coming soon", "not yet implemented"):
        return True
    return False


# ---------------------------------------------------------------------------
# Schema loading
# ---------------------------------------------------------------------------

def load_schema(script_dir, name):
    """Load a shipped schema file relative to the script location."""
    schema_path = script_dir.parent / "assets" / name
    if not schema_path.exists():
        return None
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Check implementations
# ---------------------------------------------------------------------------

def check_1_schemas(output_dir, manifest, all_rules, manifest_schema, rules_schema, findings):
    """Class 1: manifest.json and every rules.json validate against shipped schemas."""
    if manifest_schema and manifest is not None:
        errs = validate_schema(manifest, manifest_schema)
        for e in errs:
            findings.add(1, f"manifest.json schema: {e}")
    elif manifest_schema is None:
        findings.add(1, "Cannot load manifest.schema.json")

    if rules_schema:
        for domain_slug, rules_data in all_rules.items():
            errs = validate_schema(rules_data, rules_schema)
            for e in errs:
                findings.add(1, f"domains/{domain_slug}/rules.json schema: {e}")
    elif rules_schema is None:
        findings.add(1, "Cannot load rules.schema.json")


def check_2_entity_ownership(manifest, findings):
    """Class 2: every inventoried entity appears exactly once as domain-owned or shared.

    Uses manifest.entity_inventory as the authoritative list. An empty inventory is
    valid (repos with no persistent entities) but means ANY entity declared in
    owned_entities or shared_entities is rejected as unknown.

    Rejects: orphan entities, duplicate ownership without shared declaration,
    entities declared shared but not owned, unknown entities in domain ownership.
    """
    if manifest is None:
        return

    # Collect entities owned by domains
    domain_entities = {}  # entity -> list of owning domain slugs
    for domain in manifest.get("domains", []):
        slug = domain.get("slug", "?")
        for entity in domain.get("owned_entities", []):
            domain_entities.setdefault(entity, []).append(slug)

    shared_entities = manifest.get("shared_entities", [])
    shared_set = set()
    for se in shared_entities:
        entity = se.get("entity", "")
        shared_set.add(entity)
        owning = se.get("owning_domains", [])
        if not owning:
            findings.add(2, f"Shared entity '{entity}' has empty owning_domains")

    # Check for duplicate domain ownership without shared declaration
    for entity, owners in domain_entities.items():
        if len(owners) > 1 and entity not in shared_set:
            findings.add(2, f"Entity '{entity}' owned by multiple domains {owners} but not marked shared")

    # Check shared entities are actually owned by their declared domains
    for se in shared_entities:
        entity = se.get("entity", "")
        owning = se.get("owning_domains", [])
        for d in owning:
            domain_has_it = False
            for dom in manifest.get("domains", []):
                if dom.get("slug") == d and entity in dom.get("owned_entities", []):
                    domain_has_it = True
                    break
            if not domain_has_it:
                findings.add(2, f"Shared entity '{entity}' declares owning_domain '{d}' but that domain does not list it in owned_entities")

    # entity_inventory is authoritative (may be empty for no-entity repos)
    inventory = manifest.get("entity_inventory")
    if inventory is None:
        # Field is missing entirely — schema check will catch this separately
        return

    inventory_set = set(inventory)

    # Check no duplicates in inventory itself
    if len(inventory) != len(inventory_set):
        seen = set()
        for e in inventory:
            if e in seen:
                findings.add(2, f"Duplicate entity '{e}' in entity_inventory")
            seen.add(e)

    # Every inventory entity must be owned or shared
    all_owned = set(domain_entities.keys())
    for entity in inventory_set:
        if entity not in all_owned and entity not in shared_set:
            findings.add(2, f"Entity '{entity}' in inventory but not owned by any domain or marked shared (orphan)")

    # Every owned/shared entity must be in inventory (no unknown entities)
    # This applies even when inventory is empty — empty means "no entities exist"
    for entity in all_owned:
        if entity not in inventory_set:
            findings.add(2, f"Entity '{entity}' owned by domain but not in entity_inventory (unknown entity)")
    for entity in shared_set:
        if entity not in inventory_set:
            findings.add(2, f"Shared entity '{entity}' not in entity_inventory (unknown entity)")

    # Optionally require at least one domain if there are entities
    domains = manifest.get("domains", [])
    if inventory_set and not domains:
        findings.add(2, "entity_inventory is non-empty but no domains are declared")


def check_3_rule_ids(all_rules, findings):
    """Class 3: rule IDs match pattern and are globally unique."""
    id_pattern = re.compile(r"^BR-[a-z0-9-]+-[0-9]{3}$")
    seen_ids = {}
    for domain_slug, rules_data in all_rules.items():
        for rule in rules_data.get("rules", []):
            rid = rule.get("id", "")
            if not id_pattern.match(rid):
                findings.add(3, f"Rule ID '{rid}' in domain '{domain_slug}' does not match pattern")
            if rid in seen_ids:
                findings.add(3, f"Duplicate rule ID '{rid}' in domains '{seen_ids[rid]}' and '{domain_slug}'")
            else:
                seen_ids[rid] = domain_slug


def check_4_rule_shape(all_rules, findings):
    """Class 4: required fields, valid enums, nonempty evidence, category iff non-fact."""
    for domain_slug, rules_data in all_rules.items():
        for rule in rules_data.get("rules", []):
            rid = rule.get("id", "?")
            # evidence nonempty
            evidence = rule.get("evidence", [])
            if not evidence:
                findings.add(4, f"Rule '{rid}': evidence array is empty")
            # acceptance_criteria nonempty
            ac = rule.get("acceptance_criteria", [])
            if not ac:
                findings.add(4, f"Rule '{rid}': acceptance_criteria array is empty")
            # business_context nonempty
            bc = rule.get("business_context", [])
            if not bc:
                findings.add(4, f"Rule '{rid}': business_context array is empty")
            # category logic
            rule_type = rule.get("rule_type", "")
            category = rule.get("category")
            if rule_type == "fact":
                if category is not None:
                    findings.add(4, f"Rule '{rid}': fact-type rule must not have a category (got '{category}')")
            else:
                if category is None or category == "":
                    findings.add(4, f"Rule '{rid}': non-fact rule must have a category")


def check_5_rule_links(all_rules, findings):
    """Class 5: all links resolve; conflict links are bidirectional."""
    all_ids = set()
    for rules_data in all_rules.values():
        for rule in rules_data.get("rules", []):
            all_ids.add(rule.get("id", ""))

    conflict_map = {}  # id -> set of conflict targets
    for rules_data in all_rules.values():
        for rule in rules_data.get("rules", []):
            rid = rule.get("id", "")
            rels = rule.get("relationships", {})
            for link_type in ("related_rule_ids", "duplicate_rule_ids", "conflicting_rule_ids"):
                for target in rels.get(link_type, []):
                    if target not in all_ids:
                        findings.add(5, f"Rule '{rid}': {link_type} references '{target}' which does not exist")
            conflicts = set(rels.get("conflicting_rule_ids", []))
            if conflicts:
                conflict_map[rid] = conflicts

    # bidirectional check
    for rid, targets in conflict_map.items():
        for target in targets:
            if target in conflict_map:
                if rid not in conflict_map[target]:
                    findings.add(5, f"Conflict link not bidirectional: '{rid}' -> '{target}' but '{target}' does not link back")
            else:
                findings.add(5, f"Conflict link not bidirectional: '{rid}' -> '{target}' but '{target}' has no conflict link back")


def check_6_business_context(output_dir, all_rules, findings):
    """Class 6: every rule has >= 1 business-context anchor; declared file and anchor exist."""
    for rules_data in all_rules.values():
        for rule in rules_data.get("rules", []):
            rid = rule.get("id", "?")
            ctx = rule.get("business_context", [])
            if not ctx:
                findings.add(6, f"Rule '{rid}': no business_context anchors")
                continue
            for bc in ctx:
                bc_file = bc.get("file", "")
                bc_anchor = bc.get("anchor", "")
                # Validate path safety
                safe, reason = _is_safe_repo_relative_path(bc_file)
                if not safe:
                    findings.add(6, f"Rule '{rid}': business_context file path '{bc_file}' is invalid — {reason}")
                    continue
                # Verify file exists in output tree
                target_path = output_dir / bc_file.replace("/", os.sep)
                if not target_path.exists():
                    findings.add(6, f"Rule '{rid}': business_context file '{bc_file}' does not exist in output")
                    continue
                # Verify anchor exists in the file
                if bc_anchor:
                    text = read_text_tolerant(target_path)
                    if text is not None and bc_anchor not in text:
                        findings.add(6, f"Rule '{rid}': anchor '{bc_anchor}' not found in '{bc_file}'")


def check_7_coverage(output_dir, manifest, repo_root, findings):
    """Class 7: coverage completeness, totals, repo accounting, path validity.

    Validates:
    - coverage.json is valid JSON with required structure
    - total_files == len(files)
    - total_files == analyzed + excluded
    - actual file status counts match declared totals
    - all paths are relative forward-slash (no backslash, no absolute)
    - no duplicate paths
    - exclusions carry reason class and detail
    - valid status values
    - manifest total_source_files == coverage analyzed
    - with --repo: every repo file accounted for; repo root must exist
    - monorepo scoping respected

    Note: coverage.json structure is validated comprehensively here rather than
    through a separate schema file. The deliverable layout specifies two schema
    assets (manifest.schema.json and rules.schema.json); coverage validation is
    the responsibility of this check class.
    """
    coverage_path = output_dir / "coverage.json"
    coverage = read_json(coverage_path, findings, 7)
    if coverage is None:
        return

    totals = coverage.get("totals", {})
    files = coverage.get("files", [])

    # total_files == len(files)
    total_files = totals.get("total_files", 0)
    if total_files != len(files):
        findings.add(7, f"Coverage: totals.total_files ({total_files}) != len(files) ({len(files)})")

    # totals reconcile
    analyzed = totals.get("analyzed", 0)
    excluded = totals.get("excluded", 0)
    if total_files != analyzed + excluded:
        findings.add(7, f"Coverage totals: total_files ({total_files}) != analyzed ({analyzed}) + excluded ({excluded})")

    # actual file count matches declared
    actual_analyzed = sum(1 for f in files if f.get("status") == "analyzed")
    actual_excluded = sum(1 for f in files if f.get("status") == "excluded")
    if actual_analyzed != analyzed:
        findings.add(7, f"Coverage: declared analyzed={analyzed} but counted {actual_analyzed}")
    if actual_excluded != excluded:
        findings.add(7, f"Coverage: declared excluded={excluded} but counted {actual_excluded}")

    # Path validity: relative, forward-slash, no duplicates, safe segments
    seen_paths = set()
    valid_statuses = {"analyzed", "excluded"}
    for f in files:
        fpath = f.get("path", "")
        # Use reusable path safety check
        safe, reason = _is_safe_repo_relative_path(fpath)
        if not safe:
            findings.add(7, f"Coverage: path '{fpath}' is invalid — {reason}")
        # No duplicates
        if fpath in seen_paths:
            findings.add(7, f"Coverage: duplicate path '{fpath}'")
        seen_paths.add(fpath)
        # Valid status
        status = f.get("status", "")
        if status not in valid_statuses:
            findings.add(7, f"Coverage: path '{fpath}' has invalid status '{status}'")

    # Exclusions must have reason class
    for f in files:
        if f.get("status") == "excluded":
            reason = f.get("exclusion_reason")
            if not reason or not reason.get("class"):
                findings.add(7, f"Coverage: excluded file '{f.get('path', '?')}' has no exclusion reason class")

    # manifest total_source_files reconcile
    if manifest:
        manifest_total = manifest.get("project", {}).get("total_source_files", 0)
        if manifest_total != analyzed:
            findings.add(7, f"Manifest total_source_files ({manifest_total}) != coverage analyzed ({analyzed})")

    # with --repo: check every repo file is accounted for
    if repo_root:
        repo_path = Path(repo_root)
        if not repo_path.exists():
            findings.add(7, f"Repo root '{repo_root}' does not exist")
            return

        # Determine effective scope root for monorepo
        scope_root = repo_path
        if manifest:
            mono_scope = manifest.get("project", {}).get("monorepo_scope")
            if mono_scope:
                # Validate monorepo_scope as safe relative path
                safe, reason = _is_safe_repo_relative_path(mono_scope)
                if not safe:
                    findings.add(7, f"Monorepo scope '{mono_scope}' is invalid — {reason}")
                    return
                scope_root = repo_path / mono_scope.replace("/", os.sep)
                # Verify resolved scope stays under repo root
                if not _path_is_within(scope_root, repo_path):
                    findings.add(7, f"Monorepo scope '{mono_scope}' resolves outside repository root")
                    return
                if not scope_root.exists():
                    findings.add(7, f"Monorepo scope '{mono_scope}' does not exist under repo root")
                    return

        for root, _dirs, filenames in os.walk(scope_root):
            for fname in filenames:
                fpath = Path(root) / fname
                if fpath.is_file():
                    rel = to_forward_slash(fpath.relative_to(repo_path))
                    if rel not in seen_paths:
                        findings.add(7, f"File '{rel}' in repo not accounted for in coverage.json")


def check_8_evidence(output_dir, all_rules, repo_root, findings):
    """Class 8: with --repo, evidence path exists within repo, line range valid, snippet found."""
    if not repo_root:
        return
    repo_path = Path(repo_root)
    if not repo_path.exists():
        findings.add(8, f"Repo root '{repo_root}' does not exist")
        return

    for rules_data in all_rules.values():
        for rule in rules_data.get("rules", []):
            rid = rule.get("id", "?")
            for ev in rule.get("evidence", []):
                ev_file = ev.get("file", "")
                # Validate path is safe repo-relative
                safe, reason = _is_safe_repo_relative_path(ev_file)
                if not safe:
                    findings.add(8, f"Rule '{rid}': evidence path '{ev_file}' is invalid — {reason}")
                    continue

                full_path = repo_path / ev_file
                # Path containment check (Python 3.8 compatible)
                if not _path_is_within(full_path, repo_path):
                    findings.add(8, f"Rule '{rid}': evidence path '{ev_file}' escapes repository root")
                    continue

                if not full_path.exists():
                    findings.add(8, f"Rule '{rid}': evidence file '{ev_file}' does not exist")
                    continue
                line_start = ev.get("line_start", 0)
                line_end = ev.get("line_end", 0)
                if line_start < 1 or line_end < line_start:
                    findings.add(8, f"Rule '{rid}': invalid line range {line_start}-{line_end} in '{ev_file}'")
                    continue
                text = read_text_tolerant(full_path)
                if text is None:
                    findings.add(8, f"Rule '{rid}': cannot read evidence file '{ev_file}'")
                    continue
                lines = text.splitlines()
                if line_end > len(lines):
                    findings.add(8, f"Rule '{rid}': line_end {line_end} exceeds file length {len(lines)} in '{ev_file}'")
                    continue
                # snippet containment (whitespace tolerant)
                snippet = ev.get("snippet", "")
                if snippet:
                    range_text = "\n".join(lines[line_start - 1:line_end])
                    norm_range = re.sub(r"\s+", " ", range_text).strip()
                    norm_snippet = re.sub(r"\s+", " ", snippet).strip()
                    if norm_snippet not in norm_range:
                        findings.add(8, f"Rule '{rid}': snippet not found in lines {line_start}-{line_end} of '{ev_file}'")


def check_9_counts(manifest, all_rules, findings):
    """Class 9: per-domain rule counts in manifest match rules.json."""
    if manifest is None:
        return
    for domain in manifest.get("domains", []):
        slug = domain.get("slug", "?")
        declared = domain.get("rule_count", 0)
        if slug in all_rules:
            actual = len(all_rules[slug].get("rules", []))
            if declared != actual:
                findings.add(9, f"Domain '{slug}': manifest declares {declared} rules but rules.json has {actual}")
        else:
            if declared > 0:
                findings.add(9, f"Domain '{slug}': manifest declares {declared} rules but no rules.json found")


def check_10_no_stubs(output_dir, manifest, findings):
    """Class 10: all mandatory output files exist, are non-empty, and contain real content.

    Checks every file required by the output contract:
    - Top-level: 00-index.md, manifest.json, coverage.json, coverage-report.md,
      glossary.md, open-questions.md, review-workbook.csv
    - Per-domain: rules.json, business-rules.md, overview.md, features.md,
      workflows.md, validations.md, integrations.md, open-questions.md, diagrams.md
    """
    required_top = [
        "00-index.md", "manifest.json", "coverage.json", "coverage-report.md",
        "glossary.md", "open-questions.md", "review-workbook.csv"
    ]
    for fname in required_top:
        fpath = output_dir / fname
        if not fpath.exists():
            findings.add(10, f"Required file '{fname}' is missing")
        else:
            text = read_text_tolerant(fpath)
            if text is None:
                findings.add(10, f"Required file '{fname}' cannot be read")
            elif _is_stub_content(text):
                findings.add(10, f"Required file '{fname}' is empty or contains only placeholder content")

    if manifest:
        for domain in manifest.get("domains", []):
            slug = domain.get("slug", "?")
            domain_dir = output_dir / "domains" / slug
            required_domain = [
                "rules.json", "business-rules.md", "overview.md", "features.md",
                "workflows.md", "validations.md", "integrations.md",
                "open-questions.md", "diagrams.md"
            ]
            for fname in required_domain:
                fpath = domain_dir / fname
                if not fpath.exists():
                    findings.add(10, f"Domain '{slug}': required file '{fname}' is missing")
                else:
                    text = read_text_tolerant(fpath)
                    if text is None:
                        findings.add(10, f"Domain '{slug}': required file '{fname}' cannot be read")
                    elif _is_stub_content(text):
                        findings.add(10, f"Domain '{slug}': required file '{fname}' is empty or stub content")


# ---------------------------------------------------------------------------
# Mermaid syntax rules (check class 11)
#
# Ported from the sibling skill comprehensive-codebase-analysis, where the rules
# were calibrated against mermaid 11.17.2 as an oracle (26/26 agreement, zero
# false positives).
#
# A Mermaid parse error blanks the WHOLE block and renders an error box in its
# place, so one bad line costs an entire diagram. Bracket balance is necessary
# but nowhere near sufficient: every rule below encodes a construct that Mermaid
# v11 rejects outright while the brackets stay perfectly paired. Rules are keyed
# by diagram type because the same token is legal in one type and fatal in
# another: `loop["Per page"]` is an ordinary node in a flowchart but a block
# opener in a sequenceDiagram, and `actor` declares a participant in a
# sequenceDiagram but is only a node name in a flowchart.
#
# This is a heuristic, not a grammar; it cannot be complete. It is calibrated to
# raise no false positives, so extraction output is never blocked over syntax
# Mermaid actually accepts.
# ---------------------------------------------------------------------------

MERMAID_TYPES = {
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram",
    "stateDiagram-v2", "erDiagram", "C4Context", "C4Container", "C4Component",
    "C4Deployment", "architecture-beta", "block-beta", "packet-beta", "journey",
    "gantt", "pie", "mindmap", "timeline", "gitGraph", "quadrantChart", "xychart-beta",
    "sankey-beta", "requirementDiagram", "zenuml",
}
FLOWCHART_TYPES = {"flowchart", "graph"}
FLOWCHART_DIRECTIONS = {"TB", "TD", "BT", "RL", "LR"}
# Declaration keywords that only exist in a sequenceDiagram.
SEQUENCE_ONLY_KEYWORDS = {"actor", "participant", "autonumber", "activate", "deactivate"}
# Block openers closed by `end`, per diagram type.
SEQUENCE_BLOCK_OPENERS = {"loop", "alt", "opt", "par", "critical", "rect", "break", "box"}
# A flowchart edge, ending right where the target node id must begin.
ARROW_TAIL_RE = re.compile(r"(?:-{2,}[->ox]|-{2,}|-\.-*>?|={2,}>?|~~~)\s*(?=[\[({])")
SEQ_MESSAGE_RE = re.compile(r"^[^:]*?(?:-{1,2}>>?|-{1,2}[)x])[+-]?[^:]*:(?P<text>.*)$")

# The three diagram kinds every domain's diagrams.md must carry, per
# references/output-templates.md § domains/<slug>/diagrams.md.
SEQUENCE_DIAGRAM_TYPES = {"sequenceDiagram"}
COMPONENT_DIAGRAM_TYPES = {
    "flowchart", "graph", "classDiagram", "C4Component", "C4Container", "C4Context",
}
WORKFLOW_DIAGRAM_TYPES = {"flowchart", "graph", "stateDiagram", "stateDiagram-v2"}
REQUIRED_DIAGRAM_SLOTS = (
    ("sequence", SEQUENCE_DIAGRAM_TYPES),
    ("component", COMPONENT_DIAGRAM_TYPES),
    ("workflow/state", WORKFLOW_DIAGRAM_TYPES),
)


def _mermaid_blocks(text):
    """Return the body of every ```mermaid fenced block in a markdown document."""
    return re.findall(r"```mermaid[ \t]*\n(.*?)```", text, flags=re.DOTALL)


def _mermaid_balanced(block):
    """Check [], (), {} and quotes pair up outside quoted label text."""
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
            # `-o{` / `-|{` style edge decorations are not brackets.
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


def _strip_quoted_spans(line):
    """Replace double-quoted spans with same-length filler so the rules below
    never match punctuation that Mermaid treats as literal label text."""
    out, in_quote, escaped = [], False, False
    for char in line:
        if escaped:
            out.append("_")
            escaped = False
            continue
        if char == "\\" and in_quote:
            out.append("_")
            escaped = True
            continue
        if char == '"':
            in_quote = not in_quote
            out.append('"')
            continue
        out.append("_" if in_quote else char)
    return "".join(out)


def _significant_lines(block):
    """Yield (1-based index, line) pairs, skipping blanks and %% comment lines."""
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

    if diagram_type not in MERMAID_TYPES:
        problems.append(f"line 1: {diagram_type!r} is not a Mermaid v11 diagram type")
    if not _mermaid_balanced(block):
        problems.append("unbalanced brackets or quotes")

    # R6 — flowchart direction must be one Mermaid knows.
    if is_flowchart and len(tokens) > 1:
        direction = tokens[1].rstrip(";")
        if direction not in FLOWCHART_DIRECTIONS and not direction.startswith("%%"):
            problems.append(
                f"line 1: {diagram_type} direction {direction!r} is not one of "
                + "/".join(sorted(FLOWCHART_DIRECTIONS))
            )

    depth = 0
    for number, raw in _significant_lines(block):
        line = _strip_quoted_spans(raw)
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


def _unmatched_diagram_slots(block_types):
    """Return the required diagram slots that no *distinct* block can fill.

    Three required diagrams means three blocks. The type sets overlap — a
    `flowchart` is an acceptable component diagram *and* an acceptable workflow
    diagram — so a domain with one sequence diagram and one flowchart must not
    satisfy both the component and the workflow slot with that single flowchart.
    Each block therefore counts for at most one slot.

    This is a maximum bipartite matching between slots and blocks (Kuhn's
    algorithm). Slots are tried in the declared order and blocks in document
    order, so which flowchart ends up counted as the component and which as the
    workflow is deterministic — and irrelevant, since only the unfilled slots
    are reported.
    """
    slot_types = dict(REQUIRED_DIAGRAM_SLOTS)
    assigned = {}  # block index -> slot label

    def augment(label, seen):
        for index, diagram_type in enumerate(block_types):
            if index in seen or diagram_type not in slot_types[label]:
                continue
            seen.add(index)
            holder = assigned.get(index)
            if holder is None or augment(holder, seen):
                assigned[index] = label
                return True
        return False

    return [label for label, _ in REQUIRED_DIAGRAM_SLOTS if not augment(label, set())]


def check_11_mermaid(output_dir, manifest, findings):
    """Class 11: every Mermaid block in the output renders; required diagrams exist.

    Lints EVERY ```mermaid block found anywhere under the output directory — not
    only the per-domain `diagrams.md` files where a diagram is mandatory. A
    broken diagram in `workflows.md` or `overview.md` is just as broken, and
    "where the artifact must exist" is a smaller set than "where it must be
    valid". Only the output tree is read; the skill's own files are never
    scanned.

    Also verifies each declared domain's `diagrams.md` carries the three
    mandated diagrams — sequence, component, and workflow/state — as three
    distinct blocks: the type sets overlap, so one flowchart may fill the
    component slot or the workflow slot, never both.
    """
    types_by_file = {}
    for path in sorted(output_dir.rglob("*.md")):
        if not path.is_file():
            continue
        text = read_text_tolerant(path)
        if text is None:
            continue
        rel = to_forward_slash(path.relative_to(output_dir))
        for index, block in enumerate(_mermaid_blocks(text), 1):
            tokens = block.strip().split()
            types_by_file.setdefault(rel, []).append(tokens[0] if tokens else "")
            for problem in lint_mermaid_block(block):
                findings.add(11, f"{rel} block {index}: {problem}")

    if manifest is None:
        return
    for domain in manifest.get("domains", []):
        slug = domain.get("slug", "?")
        rel = f"domains/{slug}/diagrams.md"
        if not (output_dir / "domains" / slug / "diagrams.md").exists():
            continue  # class 10 reports the missing file
        block_types = types_by_file.get(rel, [])
        if not block_types:
            findings.add(11, f"Domain '{slug}': diagrams.md contains no Mermaid block")
            continue
        slot_types = dict(REQUIRED_DIAGRAM_SLOTS)
        for label in _unmatched_diagram_slots(block_types):
            findings.add(
                11,
                f"Domain '{slug}': diagrams.md has no {label} diagram of its own — the "
                f"three required diagrams need three separate blocks and each block "
                f"counts for only one (expected a block of type "
                f"{', '.join(sorted(slot_types[label]))})",
            )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate business-rules-extraction output."
    )
    parser.add_argument("output_dir", help="Path to the extraction output directory")
    parser.add_argument("--repo", default=None, help="Path to the analyzed repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.is_dir():
        print(f"Error: '{args.output_dir}' is not a directory", file=sys.stderr)
        sys.exit(2)

    findings = Findings()

    # Locate schemas
    script_dir = Path(__file__).resolve().parent
    manifest_schema = load_schema(script_dir, "manifest.schema.json")
    rules_schema = load_schema(script_dir, "rules.schema.json")

    # Load manifest
    manifest = read_json(output_dir / "manifest.json", findings, 1)

    # Load all rules.json files
    all_rules = {}
    domains_dir = output_dir / "domains"
    if domains_dir.is_dir():
        for domain_path in sorted(domains_dir.iterdir()):
            if domain_path.is_dir():
                rules_path = domain_path / "rules.json"
                if rules_path.exists():
                    data = read_json(rules_path, findings, 1)
                    if data is not None:
                        all_rules[domain_path.name] = data

    # Run all checks
    check_1_schemas(output_dir, manifest, all_rules, manifest_schema, rules_schema, findings)
    check_2_entity_ownership(manifest, findings)
    check_3_rule_ids(all_rules, findings)
    check_4_rule_shape(all_rules, findings)
    check_5_rule_links(all_rules, findings)
    check_6_business_context(output_dir, all_rules, findings)
    check_7_coverage(output_dir, manifest, args.repo, findings)
    check_8_evidence(output_dir, all_rules, args.repo, findings)
    check_9_counts(manifest, all_rules, findings)
    check_10_no_stubs(output_dir, manifest, findings)
    check_11_mermaid(output_dir, manifest, findings)

    print(findings.summary(args.format))
    sys.exit(0 if findings.passed else 1)


if __name__ == "__main__":
    main()
