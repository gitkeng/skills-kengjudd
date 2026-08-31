# init-project Skill — Design

**Date:** 2026-08-31
**Status:** Approved by user (Kongsak) on 2026-08-31
**Scope:** One new portable skill, `init-project`, plus the knowledge capture and
version bookkeeping that CLAUDE.md rule 4 requires. No code scaffolding features.

## Purpose

A skill that initializes a target project for one or more AI coding agents:
it interviews the user, researches what each selected agent needs, creates an
OKF knowledge base, generates per-agent context files from a canonical
AGENTS.md, and runs an adaptive expert review over everything it produced.
It creates **context + knowledge base only** — it never scaffolds application
code (that belongs to stack-specific tools and skills).

## User decisions (2026-08-31)

1. **Name:** `init-project`. The user first asked for `init`; renamed after the
   collision with Claude Code's built-in `/init` was raised. The verb-phrase
   form deviates from the repo's gerund/noun-phrase preference; it follows the
   existing `git-commit` precedent and was the recommended, user-approved
   option. Plugin-channel invocation: `kengjudd:init-project`.
2. **Scope:** context files + OKF knowledge base only. No `create-next-app`,
   `flutter create`, or any code scaffolding.
3. **Default KB folder in target projects:** `knowledge-base` (the
   "knowledge-based" spelling in the original request was confirmed as a typo).
   The user can override the name at init time.
4. **Expert review mechanism:** adaptive — spawn parallel expert subagents when
   the harness supports them; otherwise run sequential persona passes over the
   same checklists, so results are comparable on every agent.
5. **Approach:** bundled research (approach A). Per-agent knowledge ships in
   the skill's `references/` and is refreshed later through the normal
   `creating-skills` update workflow, not re-researched on every run.
6. **OKF source:** the canonical repo
   `github.com/GoogleCloudPlatform/open-knowledge-format` (current: 0.2). The
   `knowledge-catalog/okf/` URL in the original request is a frozen snapshot
   and is never cited as current (matches CLAUDE.md rule 5).

## Requirements (from the user's request, consolidated)

R1. Build the skill by following this repo's `creating-skills` workflow.
R2. At run time, ask which agents to initialize for (e.g. Claude Code, ZCode,
    Antigravity, Kimi CLI); multi-select; free-text entry for agents not listed.
R3. Per-agent init knowledge is gathered up front and bundled; unknown agents
    are researched at run time from official sources.
R4. Ask the task type(s) — presets: coding, project management, knowledge
    base, frontend — plus free-text entry.
R5. Per task type, keep asking follow-up questions until the preset's gap
    checklist (see Interview) has no unanswered items.
R6. Every initialized project gets a knowledge base; default folder
    `knowledge-base`, user-overridable.
R7. KB uses the OKF format; the skill checks the canonical spec version on
    every run. New KBs are created at the latest reachable version; an
    existing OKF KB at an older `okf_version` is migrated to the latest
    structure (with the user's confirmation, logged in the KB's `log.md`).
R8. For coding projects, offer Karpathy Guidelines
    (`github.com/multica-ai/andrej-karpathy-skills`) — default include,
    user may decline; asked during the interview. "Include" means a fixed
    excerpt in AGENTS.md plus a KB reference concept (see Phase 4); it never
    installs the upstream skill (out of scope; the final report may suggest it).
R9. When the user names concrete technologies (e.g. Next.js, shadcn, Figma
    MCP), research them during init and store the findings in the project KB,
    one concept per technology meeting the minimum template in
    `okf-kb-guide.md`: current stable version, official docs URL(s) under
    `sources:`, 3–7 project-relevant facts (setup, conventions, integration
    points), and a verification date.
R10–R13. Standing rules embedded into the generated context files:
    read the project KB first and research externally **only when the KB lacks
    the answer**; update the KB after every completed piece of work; capture
    new knowledge discovered while working into the project KB; reference
    external index-bearing knowledge bases (the user's examples: OKF bundles,
    LLMWiki-style wikis) by index + link, pulling in only needed excerpts;
    keep context files updated each work cycle but never bloated.
R14. Generated context files are reviewed **and improved** by experts — prompt
    engineering and context engineering always, plus domain reviewers derived
    from the interview answers (one reviewer per named technology or domain,
    e.g. Next.js, frontend design, Figma). Findings are applied before the
    report phase, not just reported.
R15. During init, necessary decisions are never made silently — recommend,
    then ask the user.
R16. All KB content — in target projects and in this repo — comes from trusted
    sources; nothing invented. Target-project KB writes pass the Phase 5
    source-quality review.
R17–R18 (meta). The skill itself is built step by step, without bias toward
    any single agent; during the build, unresolved questions are asked to the
    user before deciding — never assumed; the repo's own KB additions need
    trusted sources and an expert review pass; after the build, experts in
    prompt engineering, context engineering, loop engineering, and harness
    engineering review and improve the skill.

## Design

### Skill identity

- `skills/init-project/`, frontmatter `name: init-project`,
  `metadata.version: "1.0.0"`, `metadata.updated: "<build date>"`.
- Only the six agentskills.io frontmatter fields; fully portable.
- Description written as the trigger, in English with Thai trigger phrases
  ("init โปรเจกต์", "ตั้งต้นโครงการให้ agent", "สร้าง AGENTS.md/CLAUDE.md",
  "ตั้งค่า knowledge base"), stating both what it does and when to use it.
- Registered in `.claude-plugin/plugin.json` → `skills`.

### File structure

```
skills/init-project/
  SKILL.md                        orchestrator, <500 lines: iron rules + 6 phases
  references/
    agent-context-matrix.md       per agent: context file(s) read, import syntax,
                                  precedence, native init command, config paths,
                                  sources + verification date
    okf-kb-guide.md               creating an OKF bundle in a target project;
                                  version check + migration procedure; the fixed
                                  type: vocabulary; researched-technology
                                  concept template
    context-file-guidelines.md    content budget (AGENTS.md ≤ 150 lines / 10 KB
                                  excluding tables the matrix requires),
                                  anti-bloat rules, what belongs in context
                                  files vs the KB, merge semantics per artifact
    expert-review-protocol.md     adaptive review protocol + the v1 checklists
    task-type-presets.md          the four presets' gap checklists + output deltas
  assets/
    kb-skeleton/                  index.md and log.md templates for target KBs
    agents-md-template.md         canonical AGENTS.md skeleton
```

### Iron rules (apply across all phases)

- Every consequential decision is asked, never assumed; recommendations are
  allowed and encouraged (R15).
- Every factual claim written into a KB carries `sources:` with resolvable
  URLs from official/trusted origins (R16). If research cannot settle a
  question, the skill asks the user.
- No bias toward any single agent: shared content lives in the canonical
  AGENTS.md; agent-specific content only in that agent's adapter.

### Runtime workflow — six phases

1. **Interview.** One topic at a time: ① agents (multi-select + free text);
   ② task type(s) (presets + free text); ③ the selected presets' gap
   checklists, asked until every item is answered or explicitly deferred by
   the user (deferred items are recorded as gaps in the report and KB) —
   a user answer that names a new technology adds that technology's items to
   the checklist; ④ KB folder name (default `knowledge-base`); ⑤ Karpathy
   guidelines opt-in for coding projects (default: include); ⑥ language of
   the generated files; ⑦ pre-existing artifacts are handled **per artifact
   at encounter time** (merge / skip / replace — never one global answer,
   never a silent overwrite; semantics below).

   Preset gap checklists (v1; full question wording in
   `task-type-presets.md`):
   - *coding*: language(s)/runtime, framework, package manager/build tool,
     test framework, lint/format tooling, repo layout, CI, existing
     convention documents, Karpathy opt-in.
   - *frontend*: framework, component library, styling approach, design
     source (e.g. Figma), state management, target platforms/browsers,
     accessibility requirements.
   - *project management*: methodology, tracker tool, where specs/tasks live
     in the repo, definition of done, reporting cadence.
   - *knowledge base*: knowledge domains to cover, initial seed sources,
     external KBs to reference, update cadence and ownership.
   - *free-text task types*: the skill drafts a checklist by analogy with the
     presets and confirms it with the user before proceeding.
2. **Research.** Read `references/agent-context-matrix.md` first. Agents or
   technologies not covered → research live from official sources. If the
   harness has no web access: tell the user, proceed with bundled knowledge
   only, and record the gaps in the project KB.
3. **Create the KB (draft).** Fetch the canonical OKF SPEC.md and read its
   version line. Online: follow the fetched (latest) spec; if it is newer
   than the bundled `okf-kb-guide.md`, note the drift in the report so the
   skill itself gets updated. Offline: generate per the bundled spec version,
   write that `okf_version`, and record the skipped check as a gap. Create
   `<kb>/index.md` (with `okf_version`), `<kb>/log.md`, and seed concept
   documents from the stack research (each with `type:`, `sources:`,
   `generated:`). Generated KBs reuse this repo's `type:` vocabulary
   (`Spec Summary`, `Reference`, `Playbook`, `Decision`); extensions need
   user approval. If the target already has an OKF KB at an older
   `okf_version`, propose and (on confirmation) perform the structure
   migration, logged in `log.md`. External KBs are referenced by index +
   link; only needed excerpts are copied in.
4. **Generate context files.** AGENTS.md is canonical (Linux Foundation
   standard). Adapter rules, driven entirely by the matrix:
   - native AGENTS.md readers (per current knowledge: Codex, Cursor,
     opencode, Zed, Amp, Goose, ZCode, Kimi CLI) → no adapter;
   - import-capable non-readers → thin import adapter (Claude Code →
     `CLAUDE.md` containing `@AGENTS.md`; Gemini CLI → `GEMINI.md`
     containing `@AGENTS.md`);
   - agents with neither native reading nor imports → a generated full copy
     with a provenance header stating it is derived from AGENTS.md and must
     be regenerated, plus a note in the report.
   The standing rules (R10–R13) and — when opted in — a fixed excerpt
   (≤ 20 lines, attributed with a link) of the Karpathy guidelines are
   embedded in AGENTS.md within the content budget; the full guidelines
   become a KB `Reference` concept. Merge semantics for pre-existing files:
   context file → preserve the user's content, add the generated sections /
   adapter import with provenance markers; non-OKF knowledge folder →
   coexist — create the OKF bundle under the chosen (or adjusted) name and
   reference the old folder by link, never migrate its content.
5. **Expert review (adaptive) + apply.** Capability heuristic written into
   the skill: *if your harness provides a subagent/task-spawning tool, run
   the reviewers as parallel subagents; otherwise run the same checklists as
   sequential persona passes.* Standing reviewers (always): prompt
   engineering, context engineering. Domain reviewers: one per technology or
   domain named in the interview; when no bundled checklist matches, a
   generic domain-expert persona parameterized with that technology uses the
   generic domain checklist. The v1 bundled checklists: the two standing
   domains + one generic domain checklist (technology-parameterized).
   Reviewers cover both the context files and the Phase 3 KB drafts
   (source quality per R16); accepted findings are **applied** — context
   files amended, KB concepts corrected with amendments logged in
   `<kb>/log.md` — before Phase 6.
6. **Report.** Files created, decisions taken (all user-approved), remaining
   gaps (deferred answers, offline checks, unresearchable agents), and how
   to re-run or update later.

### Bundled agent knowledge

Exactly these 12 agents in v1 of `agent-context-matrix.md`: Claude Code,
Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose, ZCode,
Antigravity. Context-file behavior for eight of them (Claude Code, Codex,
Cursor, opencode, Gemini CLI, Zed, ZCode, Kimi CLI) is already verified in
this repo's `knowledge/specs/agents-md-standard.md` and `knowledge/agents/`.
Build-time research (with sources) must cover the rest: **Kiro, Amp, and
Goose context-file behavior; everything about Antigravity; and native init
commands + config file locations for all twelve.** The same research lands in
this repo's `knowledge/agents/` (CLAUDE.md rule 4) — it may land as a
precursor commit before the skill itself — so the skill reference and the
repo KB stay two views of one body of knowledge.

### Edge cases

- Pre-existing CLAUDE.md / AGENTS.md / KB folder → per-artifact ask (merge,
  skip, or replace) with the Phase 4 merge semantics; never overwrite
  silently.
- Existing OKF KB at an older `okf_version` → migration path (Phase 3).
- Existing codebase → light analysis (README, layout) to fill AGENTS.md
  sections; deep analysis is delegated to `comprehensive-codebase-analysis`,
  not duplicated.
- No web access → degrade gracefully (Phases 2–3).
- Unknown agent that research cannot resolve → ask the user for docs/links;
  record whatever is confirmed, list the rest as gaps.

### Out of scope (v1)

- Code scaffolding of any kind.
- Monorepo / nested AGENTS.md layouts.
- Migrating the *content* of existing non-OKF knowledge folders (they are
  referenced, not converted; see Phase 4 merge semantics).
- Installing third-party skills (including the Karpathy skills repo).

## Build process (meta)

1. Follow `skills/creating-skills/SKILL.md` end to end: spec freshness gate,
   scaffold from template, six-field frontmatter, `## Updating` section,
   registration in `plugin.json`, knowledge capture, validation, version
   bookkeeping (new skill = minor repo bump).
2. Research pass for the agent matrix (see Bundled agent knowledge for the
   exact gap list) with sources, feeding both `references/` and
   `knowledge/agents/`.
3. During the build, unresolved questions go to the user before any decision
   — never assumed (recommendations welcome).
4. Post-build expert panel over the skill itself: prompt engineering, context
   engineering, loop engineering, harness engineering — findings are applied,
   not just reported.
5. Knowledge capture: a `type: Playbook` concept under
   `knowledge/skill-authoring/` for what was learned, plus `knowledge/index.md`
   listing and `knowledge/log.md` entry; `CHANGELOG.md` and README skills
   table updated.

## Acceptance criteria

- Authoring checklist in `creating-skills` passes; frontmatter is
  six-field-only and spec-valid.
- Trigger tests: fires on intended prompts (Thai + English); does not fire on
  near-misses (e.g. plain `/init`, "initialize a git repo").
- Two scripted end-to-end test runs (fixed interview answers, so results are
  reproducible):
  - **Scenario A — empty directory:** agents = Claude Code + ZCode +
    Gemini CLI; task type = coding (Next.js + shadcn named); KB folder =
    default; Karpathy = include; language = English.
  - **Scenario B — small existing codebase:** agents = Codex + Kimi CLI;
    task type = knowledge base (non-coding); KB folder = custom name;
    Karpathy not applicable.
  Each run must produce: an OKF-valid KB (reserved files correct, every
  concept has `type:` + `sources:`, researched technologies meet the R9
  template), AGENTS.md within the stated content budget, correct adapters
  for the selected agents, and a final report listing decisions and gaps.
- Expert panel (4 domains) has reviewed the skill and its findings are
  incorporated.
- All four repo version fields bumped via `bump-version.sh`; CHANGELOG, README
  table, knowledge concept, index, and log entries present.
