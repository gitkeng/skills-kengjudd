#!/usr/bin/env python3
"""Validate init-project output (or the skill itself) using Python 3.9 stdlib only.

Modes (see references/self-check.md):
  validate_output.py <target-root> --kb <kb-folder> [--plan <record>]   checks C1-C9
  validate_output.py --detect <target-root>                              Phase 0 state
  validate_output.py --probe-folder <target-root> <name>                 case-insensitive collision probe
  validate_output.py --self                                              maintainer gate on the skill

Prints failures only, one per line: <file>:<line>: <check>: <message>.
Exit 0 = pass, 1 = failures, 2 = usage or I/O error. Never touches the network.
"""

import argparse
import datetime as _dt
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
START = "<!-- init-project:start -->"
END = "<!-- init-project:end -->"
K_START = "<!-- karpathy:start -->"
K_END = "<!-- karpathy:end -->"
FULL_COPY_HEADER = "<!-- Generated from AGENTS.md — do not edit; regenerate instead -->"
ALLOWED_COMMENTS = {START, END, K_START, K_END, FULL_COPY_HEADER}
TYPE_VOCAB = {"Spec Summary", "Reference", "Playbook", "Decision"}
STATUS_ENUM = {"draft", "stable", "deprecated"}
RESERVED = {"index.md", "log.md"}
SKIP_DIRS = {".git", "node_modules", ".init-project-backup"}
CONTEXT_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})$")
TOKEN_RE = re.compile(r"<[^!>\n][^>\n]*>")
INDEX_BULLET_RE = re.compile(r"^\s*[*-]\s+\[[^\]]*\]\(([^)]+)\)")
LOG_SEED_RE = re.compile(r"^- (Initialized by the init-project skill:|init-project: run )")
RUN_KEYS_REQUIRED = [
    "init_project_version", "init_project_run_number", "init_project_started",
    "init_project_status", "init_project_phase", "init_project_web", "init_project_root",
    "init_project_agents", "init_project_task_types", "init_project_kb",
    "init_project_language", "init_project_karpathy", "init_project_write_plan",
    "init_project_answers",
]

failures = []


def fail(path, line, check, msg):
    failures.append(f"{path}:{line}: {check}: {msg}")


def read(path):
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")


# ---------------------------------------------------------------- frontmatter
class SubsetError(Exception):
    pass


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(v) >= 2 and v[0] == "'" and v[-1] == "'":
        return v[1:-1]
    return v


def parse_inline_map(v):
    v = v.strip()
    if not (v.startswith("{") and v.endswith("}")):
        raise SubsetError("inline mapping expected")
    out = {}
    for part in v[1:-1].split(","):
        if not part.strip():
            continue
        if ":" not in part:
            raise SubsetError("inline mapping item without ':'")
        k, val = part.split(":", 1)
        out[k.strip()] = unquote(val)
    return out


def parse_frontmatter(text):
    """Return (dict, end_line) or raise SubsetError. dict is None when no frontmatter."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise SubsetError("unterminated frontmatter")
    data = {}
    i = 1
    while i < end:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line.startswith(" "):
            raise SubsetError(f"unexpected indented line {i + 1}")
        m = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if not m:
            raise SubsetError(f"unparseable line {i + 1}")
        key, rest = m.group(1), m.group(2)
        if rest.strip():
            if rest.strip().startswith("{"):
                data[key] = parse_inline_map(rest)
            elif rest.strip().startswith("[") or rest.strip().startswith("&") or rest.strip().startswith("|") or rest.strip().startswith(">"):
                raise SubsetError(f"unsupported scalar form at line {i + 1}")
            else:
                data[key] = unquote(rest)
            i += 1
            continue
        # block: list or one-level mapping
        i += 1
        items = None
        mapping = None
        while i < end and (lines[i].startswith(" ") or not lines[i].strip()):
            l = lines[i]
            if not l.strip():
                i += 1
                continue
            s = l.strip()
            if s.startswith("- "):
                if mapping is not None:
                    raise SubsetError(f"list item inside mapping at line {i + 1}")
                items = items if items is not None else []
                body = s[2:]
                if body.startswith('"') or body.startswith("'"):
                    items.append(unquote(body))
                    i += 1
                    continue
                mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", body)
                if mm and not body.startswith("http"):
                    entry = {mm.group(1): unquote(mm.group(2))}
                    indent = len(l) - len(l.lstrip())
                    i += 1
                    while i < end and lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) > indent:
                        m2 = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", lines[i])
                        if not m2:
                            raise SubsetError(f"nested item outside subset at line {i + 1}")
                        entry[m2.group(1)] = unquote(m2.group(2))
                        i += 1
                    items.append(entry)
                    continue
                items.append(unquote(body))
                i += 1
                continue
            mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", s)
            if mm:
                if items is not None:
                    raise SubsetError(f"mapping line inside list at line {i + 1}")
                mapping = mapping if mapping is not None else {}
                if mm.group(2).strip() == "" or mm.group(2).strip().startswith(("{", "[", "-")):
                    raise SubsetError(f"nesting deeper than one level at line {i + 1}")
                mapping[mm.group(1)] = unquote(mm.group(2))
                i += 1
                continue
            raise SubsetError(f"unparseable block line {i + 1}")
        data[key] = items if items is not None else (mapping if mapping is not None else "")
    return data, end + 1


# ---------------------------------------------------------------- helpers
def marker_form(text):
    """Return 'well-formed' | 'unmarked' | 'malformed: <why>'."""
    starts = ends = ks = ke = 0
    in_fence = False
    order = []
    for ln in text.split("\n"):
        if ln.strip().startswith("```"):
            in_fence = not in_fence
            continue
        s = ln.strip()
        if s in (START, END, K_START, K_END):
            if in_fence:
                return "malformed: marker inside a code fence"
            if s != ln.rstrip():
                return "malformed: marker not alone on its line"
            order.append(s)
            starts += s == START
            ends += s == END
            ks += s == K_START
            ke += s == K_END
        elif START in ln or END in ln or K_START in ln or K_END in ln:
            return "malformed: marker not alone on its line"
    if starts == ends == ks == ke == 0:
        return "unmarked"
    if starts != 1 or ends != 1:
        return f"malformed: {starts} start / {ends} end markers"
    if order.index(START) > order.index(END):
        return "malformed: end before start"
    if ks or ke:
        if ks != 1 or ke != 1:
            return f"malformed: {ks} karpathy start / {ke} end markers"
        if not (order.index(START) < order.index(K_START) < order.index(K_END) < order.index(END)):
            return "malformed: karpathy pair not nested inside the init-project pair"
    return "well-formed"


def block_of(text):
    """Lines inside the init-project pair (exclusive) and the 1-based line of START."""
    lines = text.split("\n")
    try:
        a = lines.index(START)
        b = lines.index(END)
    except ValueError:
        return None, 0
    return lines[a + 1:b], a + 1


VERBATIM_ASSETS = {"kb-maintenance.md", "karpathy-guidelines.md"}


def frontmatter_text(txt):
    """The frontmatter block of txt (including the fences), or '' when absent."""
    m = re.match(r"^---\n.*?\n---\n", txt, re.S)
    return m.group(0) if m else ""


def asset_tokens():
    toks = set()
    for p in sorted((SKILL_DIR / "assets").rglob("*.md")):
        txt = read(p)
        if p.name in VERBATIM_ASSETS:
            txt = frontmatter_text(txt)  # their bodies are instantiated verbatim
        # strip HTML comments so tokens inside authoring comments are not counted
        txt = re.sub(r"<!--.*?-->", "", txt, flags=re.S)
        toks.update(TOKEN_RE.findall(txt))
    return toks


def latest_standing_block():
    hist = read(SKILL_DIR / "references" / "standing-rules-history.md")
    m = re.search(r"^## (\d+\.\d+\.\d+)\n.*?```markdown\n(.*?)```", hist, re.S | re.M)
    if not m:
        return None, None
    return m.group(1), m.group(2)


def template_standing_block():
    tpl = read(SKILL_DIR / "assets" / "agents-md-template.md")
    m = re.search(r"^## Working rules\n\n(.*?)\n\n<!-- karpathy:start -->", tpl, re.S | re.M)
    return m.group(1) + "\n" if m else None


def iso_ok(v):
    return isinstance(v, str) and bool(ISO_RE.match(v.strip()))


# ---------------------------------------------------------------- checks
def check_context_file(path, kind):
    text = read(path)
    form = marker_form(text)
    if form != "well-formed":
        fail(path, 1, "C1", form)
        return
    block, start_line = block_of(text)
    tokens = asset_tokens()
    lower_tokens = {t.lower() for t in tokens}
    for i, ln in enumerate(block, start=start_line + 1):
        for tok in TOKEN_RE.findall(ln):
            if tok.lower() in lower_tokens:
                fail(path, i, "C2", f"placeholder survived: {tok}")
            else:
                print(f"{path}:{i}: C2: warning: unlisted <...> text: {tok}", file=sys.stderr)
    for i, ln in enumerate(text.split("\n"), start=1):
        for c in re.findall(r"<!--.*?-->", ln):
            if c not in ALLOWED_COMMENTS:
                fail(path, i, "C2", f"comment other than the markers: {c[:60]}")
    nbytes = len("\n".join(block).encode("utf-8"))
    nlines = len(block)
    if kind == "canonical" or kind == "full-copy":
        if nlines > 150:
            fail(path, start_line, "C3", f"block is {nlines} lines (cap 150)")
        if nbytes > 10240:
            fail(path, start_line, "C3", f"block is {nbytes} bytes (cap 10240)")
    elif kind == "adapter":
        if nlines > 10:
            fail(path, start_line, "C3", f"block is {nlines} lines (cap 10)")
        if nbytes > 1024:
            fail(path, start_line, "C3", f"block is {nbytes} bytes (cap 1024)")
        imports = [ln for ln in block if ln.strip().startswith("@")]
        if not imports:
            fail(path, start_line, "C8", "no @import line inside the block")
        for ln in imports:
            target = ln.strip()[1:].split()[0]
            if not (Path(path).parent / target).exists():
                fail(path, start_line, "C8", f"import target missing: {target}")
    if kind == "canonical":
        _, blk = latest_standing_block()
        if blk and blk not in text:
            fail(path, start_line, "C6", "current standing-rules block is not a contiguous substring")


def check_concept(path, kb, vocab, tech_only=False):
    text = read(path)
    try:
        fm, _ = parse_frontmatter(text)
    except SubsetError as e:
        print(f"{path}:1: C4: skipped: outside parser subset ({e})", file=sys.stderr)
        return None
    if fm is None:
        fail(path, 1, "C4", "no frontmatter")
        return None
    t = fm.get("type")
    if not t:
        fail(path, 1, "C4", "empty or missing type")
    elif t not in vocab:
        fail(path, 1, "C4", f"type {t!r} not in vocabulary {sorted(vocab)}")
    srcs = fm.get("sources")
    if isinstance(srcs, list):
        for s in srcs:
            if not isinstance(s, dict) or not s.get("resource"):
                fail(path, 1, "C4", "sources entry without resource")
            elif not str(s["resource"]).startswith(("http://", "https://")) and (" " not in str(s["resource"])):
                res = str(s["resource"])
                base = kb if res.startswith("/") else Path(path).parent
                target = (Path(base) / res.lstrip("/")) if res.startswith("/") else (base / res)
                if not target.exists():
                    fail(path, 1, "C5", f"sources path does not resolve: {res}")
    gen = fm.get("generated")
    if not isinstance(gen, dict) or not gen.get("by") or not gen.get("at"):
        fail(path, 1, "C4", "generated.by / generated.at missing")
    elif not iso_ok(gen["at"]):
        fail(path, 1, "C4", f"generated.at not ISO 8601 with offset: {gen['at']}")
    if "status" in fm and fm["status"] not in STATUS_ENUM:
        fail(path, 1, "C4", f"status {fm['status']!r} not in {sorted(STATUS_ENUM)}")
    if "stale_after" in fm and not iso_ok(fm["stale_after"]):
        fail(path, 1, "C4", f"stale_after not ISO 8601 with offset: {fm['stale_after']}")
    tags = fm.get("tags") or []
    if "technology" in tags:
        if "verified" not in fm:
            fail(path, 1, "C4", "technology concept without verified:")
        if "stale_after" not in fm:
            fail(path, 1, "C4", "technology concept without stale_after:")
    for k, v in fm.items():
        if v == "" or v == [] or v == {}:
            fail(path, 1, "C4", f"empty value for {k}")
    # C2 for tokens the assets carry; a verbatim asset is checked in its frontmatter only
    scan = frontmatter_text(text) if fm.get("init_project_asset") else text
    body = scan.split("\n")
    tokens = {t.lower() for t in asset_tokens()}
    for i, ln in enumerate(body, start=1):
        for tok in TOKEN_RE.findall(ln):
            if tok.lower() in tokens:
                fail(path, i, "C2", f"placeholder survived: {tok}")
    return fm


def check_run_record(path, kb):
    fm = check_concept(path, kb, TYPE_VOCAB)
    if fm is None:
        return
    for k in RUN_KEYS_REQUIRED:
        if k not in fm:
            fail(path, 1, "C7", f"missing key {k}")
    status = fm.get("init_project_status")
    if status == "in-progress" and "init_project_completed" in fm:
        fail(path, 1, "C7", "init_project_completed present while in-progress")
    if status == "complete" and "init_project_completed" not in fm:
        fail(path, 1, "C7", "init_project_completed missing while complete")
    try:
        n = int(fm.get("init_project_run_number", "1"))
    except ValueError:
        n = 1
        fail(path, 1, "C7", "init_project_run_number not an integer")
    if n > 1 and "init_project_previous_started" not in fm:
        fail(path, 1, "C7", "init_project_previous_started missing on run > 1")
    if n == 1 and "init_project_previous_started" in fm:
        fail(path, 1, "C7", "init_project_previous_started present on run 1")
    raw = read(path)
    for key in ("init_project_write_plan", "init_project_answers", "init_project_confirmed_commands",
                "init_project_free_text_checklists", "init_project_legacy_folders", "init_project_concepts"):
        m = re.search(rf"^{key}:\n((?:  - .*\n)+)", raw, re.M)
        if m:
            for ln in m.group(1).splitlines():
                if not ln.strip()[2:].startswith('"'):
                    fail(path, 1, "C7", f"{key} item not a double-quoted string: {ln.strip()[:40]}")


def check_index(kb):
    idx = kb / "index.md"
    if not idx.exists():
        fail(idx, 1, "C9", "index.md missing")
        return
    text = read(idx)
    form = marker_form(text)
    if form != "well-formed":
        fail(idx, 1, "C1", form)
        return
    block, start_line = block_of(text)
    seen = {}
    for i, ln in enumerate(block, start=start_line + 1):
        m = INDEX_BULLET_RE.match(ln)
        if not m:
            continue
        target = m.group(1)
        if target in seen:
            fail(idx, i, "C9", f"duplicate bullet for {target} (first at line {seen[target]})")
        seen[target] = i
        if not (kb / target).exists():
            fail(idx, i, "C9", f"bullet target missing: {target} (ask at the union, do not drop)")
        for tok in TOKEN_RE.findall(ln):
            fail(idx, i, "C2", f"placeholder survived: {tok}")


def plan_paths(record_path):
    if not record_path:
        return None
    raw = read(record_path)
    m = re.search(r"^init_project_write_plan:\n((?:  - .*\n)+)", raw, re.M)
    if not m:
        return None
    out = []
    for ln in m.group(1).splitlines():
        item = unquote(ln.strip()[2:])
        out.append(item.split("|")[0].strip())
    return out


def validate_target(root, kb_name, record):
    root = Path(root).resolve()
    kb = root / kb_name
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2
    vocab = set(TYPE_VOCAB)
    rec = kb / "init-project-run.md"
    if kb.exists() and rec.exists():
        try:
            fm, _ = parse_frontmatter(read(rec))
            extra = fm.get("init_project_type_vocabulary") if fm else None
            if isinstance(extra, dict):
                vocab |= set(extra.values())
        except SubsetError:
            pass
    chosen = plan_paths(record) if record else None
    # context files
    agents = root / "AGENTS.md"
    if agents.exists():
        check_context_file(agents, "canonical")
    for name in ("CLAUDE.md", "GEMINI.md"):
        p = root / name
        if p.exists():
            kind = "full-copy" if FULL_COPY_HEADER in read(p) else "adapter"
            check_context_file(p, kind)
    # kb
    if kb.exists():
        check_index(kb)
        cutoff = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=24)
        for p in sorted(kb.glob("*.md")):
            if p.name in RESERVED:
                continue
            rel = str(p.relative_to(root))
            if chosen is not None:
                if rel not in chosen and p.name != "init-project-run.md":
                    continue
            else:
                try:
                    fm, _ = parse_frontmatter(read(p))
                    at = (fm or {}).get("generated", {}).get("at") if isinstance((fm or {}).get("generated"), dict) else None
                    if at and iso_ok(at):
                        ts = _dt.datetime.fromisoformat(at.replace("Z", "+00:00"))
                        if ts < cutoff:
                            continue
                except SubsetError:
                    pass
            if p.name == "init-project-run.md":
                check_run_record(p, kb)
            else:
                check_concept(p, kb, vocab)
        if not rec.exists():
            fail(rec, 1, "C7", "run record missing while <kb>/ exists")
    return 1 if failures else 0


# ---------------------------------------------------------------- --detect
def detect(root):
    root = Path(root).resolve()
    sig = {}
    for name in CONTEXT_FILES:
        p = root / name
        if p.exists():
            form = marker_form(read(p))
            if form != "unmarked":
                sig[f"a:{name}"] = form
    kbs = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in SKIP_DIRS:
            continue
        idx = d / "index.md"
        if idx.exists():
            txt = read(idx)
            if txt.startswith("---") and "okf_version:" in txt.split("---")[1] and marker_form(txt) == "well-formed":
                kbs.append(d)
    record = None
    for d in kbs:
        sig[f"b:{d.name}"] = "index with okf_version and markers"
        log = d / "log.md"
        if log.exists() and any(LOG_SEED_RE.match(ln) for ln in read(log).split("\n")):
            sig[f"c:{d.name}"] = "log bullet"
        r = d / "init-project-run.md"
        if r.exists():
            sig[f"d:{d.name}"] = "run record"
            try:
                record, _ = parse_frontmatter(read(r))
            except SubsetError:
                record = {}
    state = "fresh"
    a = any(k.startswith("a:") for k in sig)
    malformed = [k for k, v in sig.items() if k.startswith("a:") and v.startswith("malformed")]
    if malformed:
        state = "foreign"
    elif record is not None:
        st = record.get("init_project_status")
        skill_v = None
        m = re.search(r'version:\s*"([^"]+)"', read(SKILL_DIR / "SKILL.md"))
        skill_v = m.group(1) if m else None
        rv = record.get("init_project_version")
        if rv and skill_v and tuple(int(x) for x in rv.split(".")) > tuple(int(x) for x in skill_v.split(".")):
            state = "newer output"
        elif st == "in-progress":
            state = "half-finished"
        elif st == "complete":
            state = "re-run"
        else:
            state = "foreign"
    elif a and any(k.startswith("c:") for k in sig):
        state = "re-run"
    elif a or kbs:
        state = "partial"
    print(f"state: {state}")
    for k, v in sig.items():
        print(f"signal {k}: {v}")
    return 0


def probe_folder(root, name):
    root = Path(root).resolve()
    for entry in os.listdir(root):
        if entry.lower() == name.lower():
            print(entry)
            return 1
    return 0


# ---------------------------------------------------------------- --self
def self_check():
    skill = read(SKILL_DIR / "SKILL.md")
    refs = {p.name: read(p) for p in sorted((SKILL_DIR / "references").glob("*.md"))}
    headings = {n: {ln[3:].strip() for ln in t.split("\n") if ln.startswith("## ")} for n, t in refs.items()}
    all_texts = {"SKILL.md": skill}
    all_texts.update({f"references/{n}": t for n, t in refs.items()})
    # anchors: [x](references/f.md) `## S`  and  `f.md` `## S`
    link_re = re.compile(r"\[[^\]]*\]\(references/([a-z0-9-]+\.md)\)\s*`## ([^`]+)`")
    plain_re = re.compile(r"`([a-z0-9-]+\.md)`(?:'s)?\s+`## ([^`]+)`")
    for fname, text in all_texts.items():
        for i, ln in enumerate(text.split("\n"), start=1):
            for m in list(link_re.finditer(ln)) + list(plain_re.finditer(ln)):
                f, sec = m.group(1), m.group(2)
                if f not in headings:
                    if f in ("SKILL.md",):
                        continue
                    fail(SKILL_DIR / fname, i, "self", f"unknown reference file {f}")
                elif sec not in headings[f]:
                    fail(SKILL_DIR / fname, i, "self", f"anchor `## {sec}` not in {f}")
    # phase labels
    labels = {}
    phase = None
    for ln in skill.split("\n"):
        m = re.match(r"^### Phase (\d) ", ln)
        if m:
            phase = m.group(1)
        m = re.match(r"^\d+\. \*\*([^*]+?)\.?\*\*", ln)
        if m and phase is not None:
            labels.setdefault(phase, set()).add(m.group(1).rstrip("."))
    for fname, text in all_texts.items():
        for i, ln in enumerate(text.split("\n"), start=1):
            for m in re.finditer(r"Phase (\d) \*\*([^*]+?)\*\*", ln):
                ph, lab = m.group(1), m.group(2).rstrip(".")
                if lab not in labels.get(ph, set()):
                    fail(SKILL_DIR / fname, i, "self", f"Phase {ph} **{lab}** is not a labelled step")
    # size
    n_lines = skill.count("\n") + (0 if skill.endswith("\n") else 1)
    n_bytes = len(skill.encode("utf-8"))
    if n_lines > 440:
        fail(SKILL_DIR / "SKILL.md", 1, "self", f"{n_lines} lines (cap 440)")
    if n_bytes > 25600:
        fail(SKILL_DIR / "SKILL.md", 1, "self", f"{n_bytes} bytes (cap 25600)")
    # contents
    for n, t in refs.items():
        if t.count("\n") > 100 and "## Contents" not in t:
            fail(SKILL_DIR / "references" / n, 1, "self", "reference over 100 lines without ## Contents")
    # standing block
    ver, blk = latest_standing_block()
    tpl = template_standing_block()
    if blk is None or tpl is None:
        fail(SKILL_DIR / "references" / "standing-rules-history.md", 1, "self", "cannot locate the standing block")
    elif blk != tpl:
        fail(SKILL_DIR / "references" / "standing-rules-history.md", 1, "self",
             f"latest section ({ver}) differs from the template's ## Working rules block")
    # asset versions
    m = re.search(r'^  version:\s*"([^"]+)"', skill, re.M)
    skill_v = m.group(1) if m else None
    for p in sorted((SKILL_DIR / "assets").rglob("*.md")):
        mm = re.search(r'^init_project_asset:\s*"[^@"]+@([^"]+)"', read(p), re.M)
        if mm and mm.group(1) != skill_v:
            fail(p, 1, "self", f"init_project_asset version {mm.group(1)} != SKILL.md {skill_v}")
    print("asset token list: " + ", ".join(sorted(asset_tokens())))
    return 1 if failures else 0


# ---------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?")
    ap.add_argument("--kb")
    ap.add_argument("--plan")
    ap.add_argument("--detect", metavar="ROOT")
    ap.add_argument("--probe-folder", nargs=2, metavar=("ROOT", "NAME"))
    ap.add_argument("--self", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.self:
            code = self_check()
        elif a.detect:
            code = detect(a.detect)
        elif a.probe_folder:
            code = probe_folder(*a.probe_folder)
        elif a.root and a.kb:
            code = validate_target(a.root, a.kb, a.plan)
        else:
            ap.print_usage()
            return 2
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for f in failures:
        print(f)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
