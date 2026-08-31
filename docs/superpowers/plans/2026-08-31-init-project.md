# init-project Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the portable `init-project` skill (spec:
`docs/superpowers/specs/2026-08-31-init-project-design.md`) that initializes a
target project for one or more AI coding agents — interview → research → OKF
knowledge base → canonical AGENTS.md + per-agent adapters → adaptive expert
review → report.

**Architecture:** A markdown-only Agent Skill in `skills/init-project/`: a
<500-line SKILL.md orchestrator, five reference documents (agent matrix, OKF
guide, task presets, context-file guidelines, review protocol), and three
asset templates. Build-time research lands first in this repo's
`knowledge/agents/` (precursor commit), then feeds the skill's bundled matrix.

**Tech Stack:** Agent Skills spec (agentskills.io six-field frontmatter), OKF
0.2, this repo's `creating-skills` workflow and scripts (`install.sh`,
`update.sh`, `bump-version.sh`, `check-spec-versions.sh`). No application code.

## Global Constraints

Copied from the approved spec — every task inherits all of these:

- Frontmatter: ONLY `name`, `description`, `license`, `compatibility`,
  `metadata`, `allowed-tools`; all metadata values quoted strings.
- `SKILL.md` body under 500 lines; depth goes to `references/` (linked one
  level deep); a link to a nonexistent file is a defect.
- Generated-AGENTS.md content budget: **≤ 150 lines / ≤ 10 KB**.
- Default KB folder name in target projects: **`knowledge-base`**.
- OKF canonical source: `github.com/GoogleCloudPlatform/open-knowledge-format`
  (current: 0.2). The `GoogleCloudPlatform/knowledge-catalog/okf/` copy is a
  frozen snapshot — never cite it as current.
- v1 agent list is EXACTLY these 12: Claude Code, Codex, Cursor, opencode,
  Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose, ZCode, Antigravity.
- Karpathy Guidelines inclusion = a ≤ 20-line attributed excerpt in AGENTS.md
  + a KB `Reference` concept. NEVER install the upstream skill repo.
- No code scaffolding of any kind. No third-party skill installation.
- No bias toward any single agent: shared content lives only in canonical
  AGENTS.md; agent-specific content only in that agent's adapter.
- Every external factual claim carries `sources:` with resolvable official
  URLs. If research cannot settle a question → ask the user, never assume
  (applies to the build itself, not only the skill's runtime).
- Repo versioning: new skill = **minor** bump, `0.9.1 → 0.10.0`, via
  `./scripts/bump-version.sh 0.10.0` (never edit the four version fields by
  hand).
- Commits go to `main` (established repo practice, user-approved for this
  work); skill-scoped gitmoji + Conventional Commits messages, because
  `update.sh` surfaces commits touching `skills/init-project/` verbatim as
  the update preview.
- Wherever a step says "today's date", use the real execution date
  (`date +%F`), not the plan's date.

---

### Task 1: Preflight gates

**Files:**
- No files created. Read-only checks.

**Interfaces:**
- Produces: a green light — OKF spec fresh, name `init-project` collision-free,
  clean tree. Every later task assumes these passed.

- [ ] **Step 1: Spec freshness gate (CLAUDE.md rule 5)**

Run from the repo root:

```bash
./scripts/check-spec-versions.sh
```

Expected: exit 0. If exit 1: STOP — migrate `knowledge/specs/okf-spec.md`,
`knowledge/index.md` (`okf_version`), the bundle, and `knowledge/log.md` per
CLAUDE.md rule 5 before continuing, and tell the user this happened.

- [ ] **Step 2: Name collision check**

```bash
for d in ~/.claude/skills ~/.agents/skills ~/.config/agents/skills ~/.kiro/skills ~/.zcode/skills; do
  [ -e "$d/init-project" ] && echo "COLLISION: $d/init-project"
done
claude plugin list 2>/dev/null | grep -i 'init-project'
```

Expected: no output (no collision). On collision: STOP and ask the user.

- [ ] **Step 3: Clean tree on main**

```bash
git status --porcelain && git branch --show-current
```

Expected: empty status, branch `main`.

---

### Task 2: Agent research → repo knowledge (precursor commit)

**Files:**
- Create: `knowledge/agents/agent-init-conventions.md`
- Modify: `knowledge/index.md` (add listing line), `knowledge/log.md` (add
  entry under today's date, newest first)

**Interfaces:**
- Consumes: `knowledge/agents/skill-discovery-matrix.md`,
  `knowledge/specs/agents-md-standard.md` (existing verified facts — do not
  re-research what they already cover).
- Produces: `knowledge/agents/agent-init-conventions.md`, a `type: Reference`
  OKF concept answering, **per agent, for all 12**: (a) instruction/context
  file(s) read + paths + precedence; (b) import syntax support (yes/no +
  syntax); (c) native init command (e.g. `/init`) if any; (d) config file
  locations; each with official-source URLs and a verification date. Task 4
  builds the skill's bundled matrix from this file.

- [ ] **Step 1: Enumerate the known-gap list (from the spec)**

Already verified in repo knowledge (context-file behavior): Claude Code,
Codex, Cursor, opencode, Gemini CLI, Zed, ZCode, Kimi CLI. Must research:

1. **Kiro** — context-file behavior (steering files?), init command, config paths.
2. **Amp** — context-file precedence/global-file detail beyond "reads AGENTS.md".
3. **Goose** — same as Amp (currently only a bare supported-tools listing).
4. **Antigravity** — everything: what it is (Google's agentic IDE), context
   file(s), rules/memories mechanism, init command, config paths.
5. **All 12** — native init command + config file locations (only some are
   already recorded).

- [ ] **Step 2: Research from official sources only**

Acceptable sources: official docs sites, official GitHub repos/READMEs,
vendor documentation. NOT acceptable: blog posts, forum answers, model
memory. For each claim record the URL. Any question that official sources
cannot settle → ask the user (offer a recommendation), or record it
explicitly as a known gap in the concept — never guess.

- [ ] **Step 3: Write the concept document**

`knowledge/agents/agent-init-conventions.md` frontmatter (exact shape):

```yaml
---
type: Reference
title: Per-agent init conventions (context files, init commands, config)
description: >
  For each of the 12 agents targeted by the init-project skill: which
  instruction/context files it reads (paths + precedence), import syntax,
  native init command, and config file locations. Feeds
  skills/init-project/references/agent-context-matrix.md.
tags: [agents, context-files, init, agents-md]
sources:
  - resource: <url>
    title: <title>
  # one entry per consulted source
generated:
  by: <agent>/<model>       # e.g. claude-code/claude-opus-5
  at: <ISO8601 timestamp>
status: stable
---
```

Body: one `## <Agent>` section per agent (all 12, even the eight known ones
— those cite the existing repo concepts via bundle-relative links like
`/specs/agents-md-standard.md` instead of duplicating facts), answering
(a)–(d) from the Interfaces block. Unsettled items go under a final
`## Known gaps` heading.

- [ ] **Step 4: Register in index + log**

Add to `knowledge/index.md` under the agents section (plain relative form):
`* [Per-agent init conventions](agents/agent-init-conventions.md) - context files, init commands, config locations for the 12 init-project agents`.
Add a `## <today>` entry to `knowledge/log.md` (newest first) describing the
addition.

- [ ] **Step 5: Verify OKF conformance**

```bash
head -1 knowledge/agents/agent-init-conventions.md | grep -qx -- '---' \
  && grep -q '^type: Reference' knowledge/agents/agent-init-conventions.md \
  && grep -q 'agent-init-conventions' knowledge/index.md \
  && echo OK
```

Expected: `OK`. Also manually confirm: every factual claim traceable to a
`sources:` entry; all 12 agents present
(`grep -c '^## ' knowledge/agents/agent-init-conventions.md` ≥ 13 — 12
agents + Known gaps).

- [ ] **Step 6: Commit (precursor)**

```bash
git add knowledge/
git commit -m "📚 knowledge: add per-agent init conventions reference

Research for the upcoming init-project skill: context files, precedence,
import syntax, native init commands, and config locations for its 12
target agents, from official sources. Precursor to the skill's bundled
agent-context-matrix."
```

---

### Task 3: Scaffold skill + frontmatter + Updating section

**Files:**
- Create: `skills/init-project/SKILL.md` (from template; body filled in Task 10)

**Interfaces:**
- Produces: valid six-field frontmatter and the repo-required `## Updating`
  section. Tasks 4–10 add content around it.

- [ ] **Step 1: Scaffold**

```bash
cp -R templates/skill-template skills/init-project
```

- [ ] **Step 2: Write the frontmatter (exact content)**

Replace the template frontmatter with:

```yaml
---
name: init-project
description: >-
  Initialize a project for one or more AI coding agents: interview the user
  (agents, task types, stack, knowledge-base folder name, Karpathy
  guidelines opt-in), research each selected agent and named technology,
  create an OKF knowledge base (default folder knowledge-base), generate a
  canonical AGENTS.md plus per-agent adapters (CLAUDE.md, GEMINI.md, ...),
  and run an adaptive expert review. Use when asked to init or set up a
  project for agents, bootstrap agent context files or a knowledge base —
  "init โปรเจกต์", "ตั้งต้นโครงการให้ agent", "สร้าง AGENTS.md/CLAUDE.md",
  "ตั้งค่า knowledge base". Not for scaffolding application code, running
  git init, or analyzing an existing codebase in depth.
license: MIT
metadata:
  version: "1.0.0"
  updated: "<today YYYY-MM-DD>"
---
```

- [ ] **Step 3: Fix the Updating section**

In the template's `## Updating` section replace `skill-name-here` with
`init-project`. Keep everything else verbatim (both channels: `update.sh`
and `claude plugin update kengjudd@kengjudd`). Delete the template's
comment blocks.

- [ ] **Step 4: Verify frontmatter is six-field-only and name matches**

```bash
awk '/^---$/{c++; next} c==1 && /^[a-zA-Z-]+:/{print $1}' skills/init-project/SKILL.md
```

Expected output ⊆ {`name:`, `description:`, `license:`, `metadata:`} (this
skill uses no `compatibility`/`allowed-tools`), and
`grep -q '^name: init-project$' skills/init-project/SKILL.md` passes.
Description must be ≤ 1024 chars:
`awk '/^description:/,/^license:/' skills/init-project/SKILL.md | wc -c` < 1100.

- [ ] **Step 5: Commit**

```bash
git add skills/init-project
git commit -m "✨ feat(init-project): scaffold skill with frontmatter and Updating section"
```

---

### Task 4: `references/agent-context-matrix.md`

**Files:**
- Create: `skills/init-project/references/agent-context-matrix.md`

**Interfaces:**
- Consumes: `knowledge/agents/agent-init-conventions.md` (Task 2),
  `knowledge/specs/agents-md-standard.md`.
- Produces: one row/section per agent with the columns Phase 4 of the skill
  depends on: **Context file(s) & precedence · Import syntax · Adapter rule
  (native / import-adapter / full-copy) · Native init command · Config
  locations · Sources (verified date)**. Task 10's Phase 4 logic references
  this file by relative path `references/agent-context-matrix.md`.

- [ ] **Step 1: Write the document**

Structure: short intro (how the skill uses the matrix; unknown agents →
research live from official sources, mirroring this format), then a
`## <Agent>` section per agent — all 12, each ending with a `Sources:` list
(URLs + verified date). Derive every fact from the Task 2 concept and
existing repo knowledge; copy facts, not prose. Each section states the
**adapter rule** explicitly, e.g.: Codex/Cursor/opencode/Zed/Amp/Goose/
ZCode/Kimi CLI → `native` (reads AGENTS.md); Claude Code → `import-adapter`
(`CLAUDE.md` containing `@AGENTS.md`); Gemini CLI → `import-adapter`
(`GEMINI.md` containing `@AGENTS.md`); Kiro/Antigravity → per Task 2
findings (`native`/`import-adapter`/`full-copy` + provenance header).
End with a `## Fallback rule` section: an agent with neither native
AGENTS.md reading nor imports gets a generated full copy with a provenance
header ("Generated from AGENTS.md — do not edit; regenerate instead") and a
note in the final report.

- [ ] **Step 2: Verify coverage**

```bash
for a in "Claude Code" "Codex" "Cursor" "opencode" "Gemini CLI" "Zed" "Kiro" "Kimi CLI" "Amp" "Goose" "ZCode" "Antigravity"; do
  grep -q "^## $a" skills/init-project/references/agent-context-matrix.md || echo "MISSING: $a"
done
```

Expected: no output. And `grep -c 'Sources:' ...` ≥ 12.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project/references/agent-context-matrix.md
git commit -m "✨ feat(init-project): add bundled agent context matrix (12 agents)"
```

---

### Task 5: `references/okf-kb-guide.md`

**Files:**
- Create: `skills/init-project/references/okf-kb-guide.md`

**Interfaces:**
- Produces: the KB procedures Task 10's Phase 3 references. Section names
  used by SKILL.md: `## Version check`, `## Creating the bundle`,
  `## Migration`, `## Type vocabulary`, `## Researched-technology template`,
  `## External knowledge bases`.

- [ ] **Step 1: Write the document** with exactly these sections:

1. `## Version check` — On every run fetch
   `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
   and read its `**Version X.Y**` line. Online: follow the fetched spec; if
   newer than this guide (written against **0.2**), note the drift in the
   final report so the skill itself gets updated. Offline: generate per 0.2,
   write `okf_version: "0.2"`, and record the skipped check as a gap in the
   report and the project KB.
2. `## Creating the bundle` — `<kb>/index.md` with `okf_version` frontmatter
   + `# Heading` / `* [Title](path) - description` listing; `<kb>/log.md`
   with `## YYYY-MM-DD` headings newest-first; every other `.md` is a
   concept with frontmatter: non-empty `type:`, `title`, `description`,
   `sources:` (each entry has `resource:`), `generated: {by, at}`. Use
   `assets/kb-skeleton/` as the starting point.
3. `## Migration` — if the target has an OKF KB with an older `okf_version`:
   diff the fetched spec against that version's rules, propose the concrete
   structural changes, **ask the user**, then migrate and log it in
   `<kb>/log.md`. Non-OKF knowledge folders are never migrated (coexist +
   reference; see context-file-guidelines).
4. `## Type vocabulary` — generated KBs use exactly `Spec Summary`,
   `Reference`, `Playbook`, `Decision`; extensions only with user approval.
5. `## Researched-technology template` — one concept per user-named
   technology: current stable version, official docs URL(s) in `sources:`,
   3–7 project-relevant facts (setup, conventions, integration points),
   verification date.
6. `## External knowledge bases` — index-bearing external KBs (OKF bundles,
   LLMWiki-style wikis): store an index/reference concept linking out; copy
   in only needed excerpts, attributed.

- [ ] **Step 2: Verify**

```bash
for s in "Version check" "Creating the bundle" "Migration" "Type vocabulary" "Researched-technology template" "External knowledge bases"; do
  grep -q "^## $s" skills/init-project/references/okf-kb-guide.md || echo "MISSING: $s"
done
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project/references/okf-kb-guide.md
git commit -m "✨ feat(init-project): add OKF knowledge-base guide (create, check version, migrate)"
```

---

### Task 6: `references/task-type-presets.md`

**Files:**
- Create: `skills/init-project/references/task-type-presets.md`

**Interfaces:**
- Produces: the four preset gap checklists + free-text procedure Task 10's
  Phase 1 references. Section names: `## coding`, `## frontend`,
  `## project management`, `## knowledge base`, `## Free-text task types`,
  `## Gap rules`.

- [ ] **Step 1: Write the document.** Each preset section = a checklist of
  interview questions (full question wording, one per item) + an "Output
  delta" paragraph (what this preset changes in AGENTS.md/KB). Checklists
  come verbatim from the spec:

- **coding**: language(s)/runtime · framework · package manager/build tool ·
  test framework · lint/format tooling · repo layout · CI · existing
  convention documents · Karpathy opt-in (default include).
- **frontend**: framework · component library · styling approach · design
  source (e.g. Figma) · state management · target platforms/browsers ·
  accessibility requirements.
- **project management**: methodology · tracker tool · where specs/tasks
  live in the repo · definition of done · reporting cadence.
- **knowledge base**: knowledge domains to cover · initial seed sources ·
  external KBs to reference · update cadence and ownership.
- `## Free-text task types`: draft a checklist by analogy with the presets,
  confirm it with the user before proceeding.
- `## Gap rules`: a gap = any checklist item not yet answered and not
  explicitly deferred by the user; an answer naming a new technology adds
  that technology's items; deferred items are recorded in the report and KB.

- [ ] **Step 2: Verify**

```bash
for s in "coding" "frontend" "project management" "knowledge base" "Free-text task types" "Gap rules"; do
  grep -q "^## $s" skills/init-project/references/task-type-presets.md || echo "MISSING: $s"
done
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project/references/task-type-presets.md
git commit -m "✨ feat(init-project): add task-type preset gap checklists"
```

---

### Task 7: `references/context-file-guidelines.md`

**Files:**
- Create: `skills/init-project/references/context-file-guidelines.md`

**Interfaces:**
- Produces: sections Task 10's Phases 1/4 reference: `## Content budget`,
  `## Context vs KB`, `## Standing rules block`, `## Merge semantics`.

- [ ] **Step 1: Write the document** with exactly these sections:

1. `## Content budget` — AGENTS.md ≤ 150 lines / ≤ 10 KB; adapters ≤ 10
   lines; when over budget, move detail into the KB and link it.
2. `## Context vs KB` — context files hold: identity, commands, binding
   rules, pointers into the KB. KB holds: researched facts, decisions,
   deep conventions. Anything an agent needs *every* turn → context;
   anything looked up *sometimes* → KB.
3. `## Standing rules block` — the verbatim rules text embedded into every
   generated AGENTS.md (write it here once, exact wording, so generation is
   copy-paste): read the project KB first and research externally **only
   when the KB lacks the answer**; update the KB after every completed
   piece of work; capture new knowledge into the KB; reference external
   index-bearing KBs by index + link, pulling only needed excerpts; keep
   context files updated each work cycle but never bloated; watch the OKF
   spec version (per okf-kb-guide `## Version check`).
4. `## Merge semantics` — per artifact, asked at encounter time (never one
   global answer, never silent overwrite): existing context file → preserve
   user content, append generated sections/adapter import between
   provenance markers (`<!-- init-project:start -->` /
   `<!-- init-project:end -->`); existing non-OKF knowledge folder →
   coexist (create the OKF bundle under the chosen name — adjusted if it
   collides — and reference the old folder by link); existing OKF KB →
   update in place + Migration path per okf-kb-guide.

- [ ] **Step 2: Verify**

```bash
for s in "Content budget" "Context vs KB" "Standing rules block" "Merge semantics"; do
  grep -q "^## $s" skills/init-project/references/context-file-guidelines.md || echo "MISSING: $s"
done
```

Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project/references/context-file-guidelines.md
git commit -m "✨ feat(init-project): add context-file guidelines (budget, standing rules, merge)"
```

---

### Task 8: `references/expert-review-protocol.md`

**Files:**
- Create: `skills/init-project/references/expert-review-protocol.md`

**Interfaces:**
- Produces: sections Task 10's Phase 5 references: `## Capability
  heuristic`, `## Reviewer roster`, `## Checklist: prompt engineering`,
  `## Checklist: context engineering`, `## Checklist: generic domain`,
  `## Applying findings`.

- [ ] **Step 1: Write the document** with exactly these sections:

1. `## Capability heuristic` — verbatim: "If your harness provides a
   subagent/task-spawning tool, run the reviewers below as parallel
   subagents, one per reviewer. Otherwise run the same checklists yourself
   as sequential persona passes, one reviewer at a time, announcing each
   persona. Either way the checklists and pass/fail bars are identical."
2. `## Reviewer roster` — standing (always): prompt engineering, context
   engineering. Domain: one reviewer per technology/domain named in the
   interview; no bundled checklist for it → generic domain persona
   parameterized with the technology, using the generic domain checklist.
3. `## Checklist: prompt engineering` — items: instructions are imperative
   and unambiguous; no two rules conflict; trigger/anti-trigger wording
   present; examples match the rules they illustrate; no vague qualifiers
   ("appropriately", "as needed") standing in for decisions.
4. `## Checklist: context engineering` — items: within content budget;
   every always-needed fact in context, every sometimes-needed fact in KB
   with a pointer; no duplication between AGENTS.md and adapters; adapters
   contain only agent-specific content; nothing bloats over time (rules
   reference the KB instead of restating it).
5. `## Checklist: generic domain` — items (parameterized by technology X):
   claims about X match its official docs (spot-check ≥ 3 against
   `sources:`); versions are current stable; setup/convention facts are
   actionable for this project; nothing invented (every X claim has a
   source); gaps about X are listed, not papered over.
6. `## Applying findings` — accepted findings are applied before the report
   phase: context files amended in place; KB concepts corrected with the
   amendment logged in `<kb>/log.md`. Rejected findings are recorded with a
   one-line reason. Review output is never "report-only".

- [ ] **Step 2: Verify**

```bash
grep -c '^## ' skills/init-project/references/expert-review-protocol.md
```

Expected: 6.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project/references/expert-review-protocol.md
git commit -m "✨ feat(init-project): add adaptive expert-review protocol and v1 checklists"
```

---

### Task 9: Assets — KB skeleton + AGENTS.md template (+ Karpathy excerpt)

**Files:**
- Create: `skills/init-project/assets/kb-skeleton/index.md`
- Create: `skills/init-project/assets/kb-skeleton/log.md`
- Create: `skills/init-project/assets/agents-md-template.md`

**Interfaces:**
- Consumes: `## Standing rules block` from context-file-guidelines (Task 7).
- Produces: templates Task 10's Phases 3–4 instantiate. `agents-md-template.md`
  section anchors used by the skill: `## Project`, `## Knowledge base`,
  `## Working rules`, `## Engineering guidelines (Karpathy)` (removable
  block), `## Agent notes`.

- [ ] **Step 1: Write `kb-skeleton/index.md`**

```markdown
---
okf_version: "0.2"
---

# <Project name> knowledge base

## Concepts

* [<Title>](<path>.md) - <description>
```

(Placeholder tokens `<...>` are intentional here — this is a template the
skill fills at run time; the SKILL.md instructs replacing every `<...>`.)

- [ ] **Step 2: Write `kb-skeleton/log.md`**

```markdown
# Knowledge base log

## <YYYY-MM-DD>

- Initialized by the init-project skill: <summary of seeded concepts>.
```

- [ ] **Step 3: Research the Karpathy excerpt**

Fetch `https://github.com/multica-ai/andrej-karpathy-skills` (README and the
karpathy-guidelines skill content). Distill a ≤ 20-line excerpt of its core
behavioral rules (surgical changes, avoid overcomplication, surface
assumptions, verifiable success criteria — use the actual upstream wording,
condensed, with attribution). If the repo is unreachable or its content
differs materially from this summary, STOP and ask the user before writing
anything.

- [ ] **Step 4: Write `agents-md-template.md`** with sections: `## Project`
  (name, purpose, stack — filled from interview), `## Knowledge base`
  (folder name, OKF pointer, read-first rule pointer), `## Working rules`
  (paste the Task 7 standing-rules block verbatim),
  `## Engineering guidelines (Karpathy)` (the Step 3 excerpt + attribution
  link, wrapped in `<!-- karpathy:start -->` / `<!-- karpathy:end -->` so
  opt-out = delete the block), `## Agent notes` (per-agent quirks worth
  surfacing, filled from the matrix). Template total must leave headroom:
  ≤ 120 lines so a filled file stays ≤ 150.

- [ ] **Step 5: Verify**

```bash
wc -l skills/init-project/assets/agents-md-template.md   # ≤ 120
awk '/karpathy:start/,/karpathy:end/' skills/init-project/assets/agents-md-template.md | wc -l  # ≤ 24 (20 + markers/heading)
grep -q 'okf_version' skills/init-project/assets/kb-skeleton/index.md && echo OK
```

- [ ] **Step 6: Commit**

```bash
git add skills/init-project/assets
git commit -m "✨ feat(init-project): add KB skeleton and AGENTS.md template with Karpathy excerpt"
```

---

### Task 10: SKILL.md body (orchestrator)

**Files:**
- Modify: `skills/init-project/SKILL.md` (body between frontmatter and
  `## Updating`)

**Interfaces:**
- Consumes: all five references + three assets by relative path.
- Produces: the complete runtime workflow. Structure: `## Purpose`,
  `## Iron rules`, `## Workflow` (Phases 1–6), `## Edge cases`,
  `## References`, `## Updating` (already present).

- [ ] **Step 1: Write `## Purpose`** — one paragraph: initializes a target
  project for selected AI coding agents; produces context files + an OKF KB
  only; never scaffolds code.

- [ ] **Step 2: Write `## Iron rules`** (verbatim from spec):
  every consequential decision is asked, never assumed (recommend, then
  ask); every KB claim carries `sources:` from official origins — if
  research cannot settle it, ask the user; no bias toward any agent —
  shared content only in AGENTS.md, agent-specific content only in that
  agent's adapter.

- [ ] **Step 3: Write `## Workflow`** — the six phases, each a numbered
  subsection that *references* its documents rather than restating them:

1. **Interview** — one topic at a time: agents (multi-select + free text);
   task types (presets + free text); the selected presets' gap checklists
   per `references/task-type-presets.md` until no gaps (per its
   `## Gap rules`); KB folder name (default `knowledge-base`); Karpathy
   opt-in (coding only, default include); language of generated files;
   pre-existing artifacts handled per-artifact at encounter time per
   `references/context-file-guidelines.md` `## Merge semantics`.
2. **Research** — read `references/agent-context-matrix.md` first; unknown
   agents/technologies → live research from official sources in the matrix's
   format; no web access → tell the user, use bundled knowledge, record
   gaps in the KB.
3. **Create the KB (draft)** — follow `references/okf-kb-guide.md`
   (`## Version check` → `## Creating the bundle`, seeding technology
   concepts per `## Researched-technology template`; existing older-version
   OKF KB → `## Migration`). Instantiate `assets/kb-skeleton/`, replacing
   every `<...>` token.
4. **Generate context files** — instantiate `assets/agents-md-template.md`
   (drop the karpathy block if opted out); apply each selected agent's
   adapter rule from the matrix (native / import-adapter / full-copy with
   provenance header); stay within `## Content budget`.
5. **Expert review + apply** — follow
   `references/expert-review-protocol.md` end to end (capability heuristic,
   roster from interview answers, checklists, `## Applying findings`).
6. **Report** — files created; every decision taken (all user-approved);
   remaining gaps (deferred answers, offline checks, unresearchable
   agents); how to re-run; suggestions that were out of scope (e.g.
   installing the upstream Karpathy skill).

- [ ] **Step 4: Write `## Edge cases`** — bullets from the spec: pre-existing
  files (per-artifact ask + merge semantics), older-`okf_version` KB
  (migration), existing codebase (light README/layout analysis only; point
  deep analysis to `comprehensive-codebase-analysis`), no web access
  (degrade + record), unresolvable agent (ask the user for docs; record
  confirmed facts; list the rest as gaps).

- [ ] **Step 5: Write `## References`** — links to all five reference files,
  one level deep.

- [ ] **Step 6: Verify**

```bash
wc -l skills/init-project/SKILL.md    # < 500
for f in agent-context-matrix okf-kb-guide task-type-presets context-file-guidelines expert-review-protocol; do
  grep -q "references/$f.md" skills/init-project/SKILL.md || echo "UNLINKED: $f"
  [ -f "skills/init-project/references/$f.md" ] || echo "MISSING FILE: $f"
done
```

Expected: line count < 500, no other output.

- [ ] **Step 7: Commit**

```bash
git add skills/init-project/SKILL.md
git commit -m "✨ feat(init-project): write orchestrator body (iron rules, 6 phases, edge cases)"
```

---

### Task 11: Register, install, trigger tests

**Files:**
- Modify: `.claude-plugin/plugin.json` (append `"./skills/init-project"` to
  `skills` array)

**Interfaces:**
- Produces: the skill discoverable in this repo (project scope) and
  registered on the plugin channel as `kengjudd:init-project`.

- [ ] **Step 1: Register**

Append `"./skills/init-project"` to the `skills` array in
`.claude-plugin/plugin.json`. Verify JSON validity:

```bash
python3 -m json.tool .claude-plugin/plugin.json > /dev/null && grep -q 'init-project' .claude-plugin/plugin.json && echo OK
```

- [ ] **Step 2: Install project-scope for testing**

```bash
./scripts/install.sh --tool claude --project .
ls -la .claude/skills/ | grep init-project
```

Expected: symlink `init-project` present.

- [ ] **Step 3: Trigger tests (fresh session)**

In a fresh Claude Code session in this repo, test that the skill triggers
(is selected / offered) on each positive prompt and NOT on any negative:

Positive: `ตั้งต้นโครงการนี้ให้ Claude Code กับ ZCode ใช้` ·
`init this project for my coding agents with a knowledge base` ·
`สร้าง AGENTS.md กับ knowledge base ให้โปรเจกต์นี้`.
Negative: `run git init` · `initialize a new npm package` ·
`วิเคราะห์ codebase นี้แบบละเอียด` (must hit
comprehensive-codebase-analysis instead) · `/init`.

Record pass/fail per prompt. Any failure → adjust `description` wording
only (no scope change), re-run this step, and note the change for Task 15's
knowledge capture.

- [ ] **Step 4: Run the authoring checklist**

Open `skills/creating-skills/references/authoring-checklist.md` and verify
every item against `skills/init-project/` (frontmatter, body, references
one-level-deep, Updating section, portability — no Claude-only fields).
Fix violations before proceeding.

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "✨ feat(init-project): register skill in kengjudd plugin"
```

---

### Task 12: End-to-end Scenario A (empty directory)

**Files:**
- Create (outside repo): `/tmp/init-e2e-a/` — disposable test target.

**Interfaces:**
- Consumes: the installed skill (Task 11).
- Produces: verified Scenario A outputs per the spec's acceptance criteria.

- [ ] **Step 1: Prepare target**

```bash
rm -rf /tmp/init-e2e-a && mkdir -p /tmp/init-e2e-a
```

- [ ] **Step 2: Run the skill against the target** (fresh session, following
  `skills/init-project/SKILL.md` exactly) with these scripted interview
  answers — no deviations:

agents = Claude Code, ZCode, Gemini CLI · task type = coding, naming
Next.js + shadcn · KB folder = default (`knowledge-base`) · Karpathy =
include · language = English · every other question → take the skill's
recommendation.

- [ ] **Step 3: Verify outputs**

```bash
cd /tmp/init-e2e-a
test -f AGENTS.md && test -f CLAUDE.md && test -f GEMINI.md && echo files-OK
wc -l AGENTS.md            # ≤ 150
wc -c AGENTS.md            # ≤ 10240
grep -q '@AGENTS.md' CLAUDE.md && grep -q '@AGENTS.md' GEMINI.md && echo adapters-OK
grep -q 'okf_version' knowledge-base/index.md && test -f knowledge-base/log.md && echo kb-OK
for f in $(find knowledge-base -name '*.md' ! -name index.md ! -name log.md); do
  grep -q '^type:' "$f" || echo "NO TYPE: $f"
  grep -q '^sources:' "$f" || echo "NO SOURCES: $f"
done
ls knowledge-base | grep -iE 'next|shadcn'   # researched-technology concepts exist
awk '/karpathy:start/,/karpathy:end/' AGENTS.md | wc -l   # >0 and ≤ 24
```

Expected: all OK markers, no `NO TYPE`/`NO SOURCES`, both technologies
present, and the run ended with a report listing decisions + gaps. ZCode
needs no adapter (native AGENTS.md reader) — confirm no ZCode-specific file
was generated.

- [ ] **Step 4: Fix and re-run** — any failure is a defect in the skill
  documents (not in the test): fix the skill, commit the fix
  (`🐛 fix(init-project): <what>`), wipe `/tmp/init-e2e-a`, repeat from
  Step 1 until green.

---

### Task 13: End-to-end Scenario B (existing codebase, non-coding)

**Files:**
- Create (outside repo): `/tmp/init-e2e-b/` — fixture with pre-existing files.

**Interfaces:**
- Consumes: the installed skill.
- Produces: verified Scenario B outputs, exercising merge + custom KB name +
  a non-coding preset.

- [ ] **Step 1: Prepare fixture**

```bash
rm -rf /tmp/init-e2e-b && mkdir -p /tmp/init-e2e-b
cd /tmp/init-e2e-b && git init -q
printf '# Acme docs project\n\nInternal documentation tooling.\n' > README.md
printf '# Existing agent notes\n\n- Hand-written rule: keep docs in sync.\n' > AGENTS.md
```

- [ ] **Step 2: Run the skill** with scripted answers:

agents = Codex, Kimi CLI · task type = knowledge base (domains: product
docs + release notes; seed source: the README; no external KBs; monthly
update cadence, owner = user) · KB folder = `kb` (custom) · language =
English · pre-existing `AGENTS.md` → answer **merge** when asked · every
other question → take the skill's recommendation.

- [ ] **Step 3: Verify outputs**

```bash
cd /tmp/init-e2e-b
grep -q 'Hand-written rule' AGENTS.md && echo preserved-OK      # user content kept
grep -q 'init-project:start' AGENTS.md && echo markers-OK        # generated block marked
test -d kb && grep -q 'okf_version' kb/index.md && echo kb-name-OK
test ! -e knowledge-base && echo no-default-folder-OK
test ! -e CLAUDE.md && test ! -e GEMINI.md && echo no-extra-adapters-OK  # Codex+Kimi read AGENTS.md
grep -q 'karpathy:start' AGENTS.md && echo FAIL-karpathy-present # non-coding → no Karpathy block
wc -l AGENTS.md   # ≤ 150
```

Expected: all OK markers, no `FAIL-karpathy-present` output, and the report
was produced. The interview must NOT have asked coding-preset questions
(stack, CI, Karpathy) — check the transcript.

- [ ] **Step 4: Fix and re-run** — same loop as Task 12 Step 4
  (`🐛 fix(init-project): <what>`, wipe fixture, repeat until green).

---

### Task 14: Post-build expert panel (4 domains) + apply

**Files:**
- Modify: any `skills/init-project/` file the accepted findings touch.

**Interfaces:**
- Consumes: the complete, e2e-green skill.
- Produces: the reviewed-and-improved skill the spec's acceptance requires.

- [ ] **Step 1: Dispatch four reviewers** (parallel subagents; each reads the
  whole `skills/init-project/` tree + the spec, returns structured findings
  with severity + evidence + suggestion):

1. **Prompt engineering** — instruction clarity, ambiguity, conflicting
   rules, trigger quality of the description.
2. **Context engineering** — token economy of SKILL.md vs references
   (progressive disclosure), duplication, whether generated artifacts obey
   the budget philosophy the skill preaches.
3. **Loop engineering** — the interview/gap loop and fix-rerun loops:
   termination conditions, unbounded questioning risk, deferral handling.
4. **Harness engineering** — portability across the 12 agents: capability
   heuristic realism, no Claude-only assumptions in the runtime flow,
   symlink/plugin channel behavior, offline degradation.

- [ ] **Step 2: Adjudicate and apply** — accept/reject each finding with a
  one-line reason; apply accepted ones. If any change touched trigger
  wording → re-run Task 11 Step 3; if any change touched runtime behavior →
  re-run the affected e2e scenario.

- [ ] **Step 3: Commit**

```bash
git add skills/init-project
git commit -m "♻️ refactor(init-project): apply 4-domain expert panel findings"
```

---

### Task 15: Knowledge capture + CHANGELOG + README

**Files:**
- Create: `knowledge/skill-authoring/init-project-lessons.md`
- Modify: `knowledge/index.md`, `knowledge/log.md`, `CHANGELOG.md`,
  `README.md` (Skills table)

**Interfaces:**
- Consumes: everything learned in Tasks 2–14.
- Produces: the CLAUDE.md-rule-4 artifacts.

- [ ] **Step 1: Write the Playbook concept**

`knowledge/skill-authoring/init-project-lessons.md` — frontmatter
`type: Playbook`, `title`, `description`, `tags`, `generated: {by, at}`;
`sources:` only if it makes external claims. Body: what was decided and
learned building init-project — the canonical-AGENTS.md + adapter-rule
design, the adaptive review heuristic, e2e failures and their fixes,
trigger-wording adjustments, panel findings that changed the skill. Link
related concepts (`/agents/agent-init-conventions.md`,
`/skill-authoring/best-practices.md`).

- [ ] **Step 2: Register** — add the listing line to `knowledge/index.md`
  (plain relative form) and a `## <today>` entry to `knowledge/log.md`
  covering both this concept and the skill's creation.

- [ ] **Step 3: CHANGELOG** — add a `## [0.10.0] - <today>` release with an
  `### init-project` heading: new skill, one-line summary, note the
  precursor `agent-init-conventions` knowledge under `### Knowledge`.

- [ ] **Step 4: README Skills table** — add row: `init-project` · `1.0.0` ·
  the description's first sentence.

- [ ] **Step 5: Verify + commit**

```bash
grep -q 'init-project-lessons' knowledge/index.md && grep -q '0.10.0' CHANGELOG.md && grep -q 'init-project' README.md && echo OK
git add knowledge CHANGELOG.md README.md
git commit -m "📚 knowledge(init-project): capture build lessons; changelog + README for 0.10.0"
```

---

### Task 16: Version bump + final verification

**Files:**
- Modify (via script only): `VERSION`, `.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: everything; this is the release gate.

- [ ] **Step 1: Bump all four fields**

```bash
./scripts/bump-version.sh 0.10.0
./scripts/bump-version.sh --show
```

Expected: all four values read `0.10.0`.

- [ ] **Step 2: Final sweep**

```bash
grep -q "updated: \"$(date +%F)\"" skills/init-project/SKILL.md && echo date-OK
wc -l skills/init-project/SKILL.md            # still < 500
git status --porcelain                         # only the three version files staged-able
```

Re-confirm the authoring checklist's portability gate one last time (no
non-spec frontmatter snuck in during Task 14 edits).

- [ ] **Step 3: Commit the release**

```bash
git add VERSION .claude-plugin
git commit -m "🔖 release: v0.10.0 — add init-project skill"
```

- [ ] **Step 4: Report to the user** — summary of everything shipped, the
  e2e evidence, panel findings applied, and the two install/update channels
  for trying it (`./scripts/install.sh --tool claude` /
  `claude plugin update kengjudd@kengjudd` after a marketplace update).
