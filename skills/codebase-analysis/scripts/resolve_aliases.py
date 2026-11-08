#!/usr/bin/env python3
"""Mint aliases late, after parallel phases have written their entries.

Parallel mode (see references/parallel-phases.md) lets Phases 2-7 run as
concurrent subagents. They cannot mint `BR-NNN` / `TD-NNN` / `V-NNN` /
`TC-NNN` / `CMP-NNN` aliases without colliding, so each subagent writes its
registered entries — canonical keys, no aliases — to
`<output-root>/.work/entries-<phase>.json` and refers to any entry in prose
or in `source_refs` / `traceability` with the placeholder
`{{alias:<canonical-key>}}`.

This script, run once by the orchestrator at Phase 8:

1. loads every `.work/entries-*.json` fragment and merges the five registries
   by canonical key (a key registered twice with different content is an
   error — the phases disagree and a human must pick);
2. loads `.work/prior-manifest.json` when present (the snapshot Phase 0 took
   of the previous run's manifest.json) and reuses its aliases for matching
   canonical keys, then mints the next unused number per registry for the
   rest — the same rule as references/evidence-and-identity.md;
3. rewrites every `{{alias:<key>}}` placeholder in all Markdown files under
   the output root and inside the fragments' own string fields;
4. computes `delta` (new / resolved / regressed / persisted) and
   `severity_counts`;
5. writes `.work/entries.resolved.json` for the orchestrator to merge into
   `manifest.json`, and exits 1 if any placeholder points at an unregistered
   key, so an unresolved reference can never reach the final output.

The orchestrator deletes `.work/` after `manifest.json` is written; the
validator rejects any file it does not expect.

Usage:
  python3 resolve_aliases.py <output-root> [--dry-run]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{alias:([a-z]+:[^}\s]+)\}\}")
REGISTRIES = {
    "business_rules": ("br", "BR"),
    "findings": (None, None),  # registry per entry: td -> TD, v -> V
    "components": ("cmp", "CMP"),
    "test_cases": ("tc", "TC"),
}
ALIAS_PREFIX = {"br": "BR", "td": "TD", "v": "V", "tc": "TC", "cmp": "CMP"}
SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def die(msg: str, code: int = 2) -> None:
    print(f"resolve_aliases: {msg}", file=sys.stderr)
    sys.exit(code)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"{path}: invalid JSON ({exc})")


def registry_of(section: str, entry: dict) -> str:
    if section == "findings":
        reg = entry.get("registry")
        if reg not in ("td", "v"):
            die(f"finding {entry.get('canonical_key')!r}: registry must be 'td' or 'v'")
        return reg
    return REGISTRIES[section][0]


def canonical_registry(key: str) -> str:
    return key.split(":", 1)[0]


def merge_fragments(work: Path) -> tuple[dict, list[str]]:
    merged = {s: {} for s in REGISTRIES}
    traceability: list = []
    sources: list[str] = []
    for frag_path in sorted(work.glob("entries-*.json")):
        frag = load_json(frag_path)
        sources.append(frag_path.name)
        for section in REGISTRIES:
            for entry in frag.get(section, []) or []:
                key = entry.get("canonical_key")
                if not isinstance(key, str) or not key:
                    die(f"{frag_path.name}: {section} entry without canonical_key")
                reg = registry_of(section, entry)
                if canonical_registry(key) != reg:
                    die(f"{frag_path.name}: {key} is in {section} but its key registry is {canonical_registry(key)!r}")
                if "alias" in entry and entry["alias"] not in (None, ""):
                    die(f"{frag_path.name}: {key} carries an alias; parallel phases must not mint aliases")
                entry = {k: v for k, v in entry.items() if k != "alias"}
                prev = merged[section].get(key)
                if prev is not None and prev != entry:
                    die(f"{key} registered twice with different content (see {frag_path.name}); reconcile before resolving")
                merged[section][key] = entry
        for link in frag.get("traceability", []) or []:
            if link not in traceability:
                traceability.append(link)
    merged["traceability"] = traceability
    return merged, sources


def mint(merged: dict, prior: dict | None) -> dict[str, str]:
    """canonical key -> alias, reusing prior aliases, minting above the max."""
    alias_of: dict[str, str] = {}
    max_num: dict[str, int] = {r: 0 for r in ALIAS_PREFIX}
    prior_keys: dict[str, str] = {}
    if prior:
        for section in ("business_rules", "findings", "components", "test_cases"):
            for entry in prior.get(section, []) or []:
                key, alias = entry.get("canonical_key"), entry.get("alias")
                if isinstance(key, str) and isinstance(alias, str):
                    prior_keys[key] = alias
                    m = re.fullmatch(r"([A-Z]+)-(\d+)", alias)
                    if m:
                        reg = m.group(1).lower()
                        max_num[reg] = max(max_num.get(reg, 0), int(m.group(2)))
    current_keys = [k for s in REGISTRIES for k in merged[s]]
    # 1. reuse
    for key in current_keys:
        if key in prior_keys:
            alias_of[key] = prior_keys[key]
    # 2. mint, in a stable order (sorted keys) so re-running is deterministic
    for key in sorted(k for k in current_keys if k not in alias_of):
        reg = canonical_registry(key)
        max_num[reg] += 1
        if max_num[reg] > 999:
            die(f"registry {reg} exceeded 999 aliases; the schema allows three digits")
        alias_of[key] = f"{ALIAS_PREFIX[reg]}-{max_num[reg]:03d}"
    return alias_of


def substitute(text: str, alias_of: dict[str, str], unresolved: set[str]) -> str:
    def repl(m):
        key = m.group(1)
        if key in alias_of:
            return alias_of[key]
        unresolved.add(key)
        return m.group(0)
    return PLACEHOLDER.sub(repl, text)


def walk_strings(obj, fn):
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [walk_strings(x, fn) for x in obj]
    if isinstance(obj, dict):
        return {k: walk_strings(v, fn) for k, v in obj.items()}
    return obj


def compute_delta(merged: dict, alias_of: dict, prior: dict | None) -> dict:
    """Delta over *findings* only (td/v), as the manifest validator requires:
    every delta key must be a current or prior finding, and a first run's
    `new` must list exactly the current findings."""
    cur_sev = {k: e.get("severity") for k, e in merged["findings"].items()}
    cur_keys = set(merged["findings"])
    prior_keys, prior_sev = set(), {}
    if prior:
        for e in prior.get("findings", []) or []:
            k = e.get("canonical_key")
            if isinstance(k, str):
                prior_keys.add(k)
                prior_sev[k] = e.get("severity")
    new = sorted(cur_keys - prior_keys)
    resolved = sorted(prior_keys - cur_keys)
    both = cur_keys & prior_keys
    regressed = sorted(k for k in both if k in cur_sev and k in prior_sev
                       and SEVERITY_RANK.get(cur_sev[k], -1) > SEVERITY_RANK.get(prior_sev[k], -1))
    persisted = sorted(k for k in both if k not in regressed)
    return {"prior_manifest_loaded": prior is not None, "new": new, "resolved": resolved,
            "regressed": regressed, "persisted": persisted}


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    dry = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__)
        return 2
    root = Path(args[0]).resolve()
    work = root / ".work"
    if not work.is_dir():
        die(f"{work} not found: parallel mode writes fragments there (see references/parallel-phases.md)")
    merged, sources = merge_fragments(work)
    if not sources:
        die(f"no entries-*.json fragments in {work}")
    prior_path = work / "prior-manifest.json"
    prior = load_json(prior_path) if prior_path.is_file() else None

    alias_of = mint(merged, prior)
    unresolved: set[str] = set()

    # resolve placeholders inside the fragments' own fields
    resolved_sections = {}
    for section in ("business_rules", "findings", "components", "test_cases"):
        out = []
        for key in sorted(merged[section]):
            entry = dict(merged[section][key])
            entry["alias"] = alias_of[key]
            entry = walk_strings(entry, lambda s: substitute(s, alias_of, unresolved))
            out.append(entry)
        resolved_sections[section] = out
    resolved_sections["traceability"] = walk_strings(
        merged["traceability"], lambda s: substitute(s, alias_of, unresolved))

    # rewrite Markdown under the output root
    rewritten = []
    for md in sorted(root.rglob("*.md")):
        if work in md.parents:
            continue
        text = md.read_text(encoding="utf-8")
        new_text = substitute(text, alias_of, unresolved)
        if new_text != text:
            rewritten.append(md.relative_to(root).as_posix())
            if not dry:
                md.write_text(new_text, encoding="utf-8")

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for e in resolved_sections["findings"]:
        sev = e.get("severity")
        if sev in counts:
            counts[sev] += 1

    result = {
        "sources": sources,
        "alias_of": alias_of,
        **resolved_sections,
        "severity_counts": counts,
        "delta": compute_delta(merged, alias_of, prior),
        "markdown_rewritten": rewritten,
        "unresolved_placeholders": sorted(unresolved),
    }
    if not dry:
        (work / "entries.resolved.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"fragments: {len(sources)}  entries: "
          + ", ".join(f"{s}={len(resolved_sections[s])}" for s in ("business_rules", "findings", "components", "test_cases"))
          + f"  markdown rewritten: {len(rewritten)}" + ("  (dry run)" if dry else ""))
    if unresolved:
        print("UNRESOLVED placeholders (key never registered by any phase):", file=sys.stderr)
        for key in sorted(unresolved):
            print(f"  {{{{alias:{key}}}}}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
