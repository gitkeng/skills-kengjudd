---
type: Decision
title: "2026-08-29 repository design decisions"
description: >
  Founding decisions for skills-kengjudd (hybrid distribution, per-skill update
  commands, no initial skill imports, private repo without LICENSE), the
  spec-conflict rationale behind the repository layout, and the preserved
  inventory of 23 old skills deferred for later import.
tags:
  - decision
  - repository-design
  - distribution
  - update-mechanism
  - skill-imports
sources:
  - resource: "file:///Users/keng/Coding/gitkeng/skills-kengjudd/docs/superpowers/specs/2026-08-29-skills-kengjudd-design.md"
    title: "Approved design document (2026-08-29)"
  - resource: "https://github.com/GoogleCloudPlatform/open-knowledge-format"
    title: "OKF canonical spec repository (SPEC.md — version declared in-file)"
  - resource: "https://agentskills.io/specification"
    title: "Agent Skills specification (six-field frontmatter rule)"
  - resource: "https://code.claude.com/docs/en/plugins"
    title: "Claude Code docs — Create plugins"
  - resource: "https://code.claude.com/docs/en/plugins-reference"
    title: "Claude Code docs — Plugins reference (version management)"
  - resource: "https://code.claude.com/docs/en/discover-plugins"
    title: "Claude Code docs — Discover and install plugins"
  - resource: "https://github.com/anthropics/skills"
    title: "anthropics/skills (marketplace distribution precedent)"
  - resource: "https://github.com/CodeWithAndreaPro/agentic-coding-toolkit"
    title: "ACT — clone+symlink+update pattern (private repo — 404 unauthenticated)"
  - resource: "file:///Users/keng/.agentic-coding-toolkit"
    title: "Local ACT clone, VERSION 1.0.6 — primary verification source"
  - resource: "https://github.com/vercel-labs/skills"
    title: "npx skills CLI (distribution option not chosen)"
  - resource: "https://github.com/obra/superpowers"
    title: "obra/superpowers (pure-marketplace precedent)"
  - resource: "https://github.com/multica-ai/andrej-karpathy-skills"
    title: "Model repo for plugin/marketplace files (and anti-patterns)"
  - resource: "https://github.com/flutter/flutter"
    title: "Upstream owner of the nine flutter .agents/skills"
  - resource: "https://github.com/Astro-Han/karpathy-llm-wiki"
    title: "Upstream of the vendored karpathy-llm-wiki skill"
  - resource: "https://skills.sh/"
    title: "skills.sh ecosystem (distributes find-skills)"
  - resource: "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills"
    title: "GitHub Copilot Agent Skills docs (left unfetched — open question)"
  - resource: "file:///Users/keng/Coding/presales/.claude/skills"
    title: "Inventory source: presales workspace skills"
  - resource: "file:///Users/keng/Coding/dify/.agents/skills"
    title: "Inventory source: Dify repo skills"
  - resource: "file:///Users/keng/Coding/flutter/.agents/skills"
    title: "Inventory source: flutter/flutter clone skills (unmodified upstream)"
  - resource: "file:///Users/keng/Coding/gitkeng/aws-kiro-atx-lab/.kiro/skills"
    title: "Inventory source: aws-kiro-atx-lab Kiro skills"
  - resource: "file:///Users/keng/Coding/finoniq/finoniq2brain/.claude/skills"
    title: "Inventory source: finoniq2brain skills"
  - resource: "file:///Users/keng/Coding/finoniq/finoweb/.claude/skills"
    title: "Inventory source: finoweb skills"
  - resource: "file:///Users/keng/.claude/skills"
    title: "Inventory source: user-global Claude skills"
  - resource: "file:///Users/keng/.agents/skills"
    title: "Inventory source: user-global agentskills.io skills"
generated:
  by: "claude-code/claude-fable-5"
  at: "2026-08-29T10:45:06Z"
verified:
  - by: "human:kengjudd"
    at: "2026-08-29T10:45:06Z"
status: stable
---

# 2026-08-29 Repository design decisions

Founding decision record for this repository. The full approved design lives at
`docs/superpowers/specs/2026-08-29-skills-kengjudd-design.md`; this document
captures the decisions, why they were made, and the deferred-import inventory
so a future session can act without re-scanning the source projects.

## Decisions (approved by the user, 2026-08-29)

1. **Distribution: hybrid.** Git clone to a fixed path + `scripts/install.sh`
   symlinks into per-agent skill directories, **plus** a Claude Code plugin
   marketplace (`.claude-plugin/plugin.json` + `marketplace.json`,
   marketplace name `kengjudd`). See /specs/claude-code-plugins.md and
   /agents/skill-discovery-matrix.md.
2. **Update model: per-skill update commands.** Every SKILL.md carries a
   required `## Updating` section and a `metadata.version` (SemVer string).
   The shared implementation is `scripts/update.sh <skill-name>` (also
   `--all`), following the ACT flow: verify clone → clean tree on main →
   `git fetch` → compare local vs `origin/main` skill version → show changelog
   delta → confirm → `git pull` → print per-agent reload reminders. That script
   serves the git-clone/symlink channel only; plugin-marketplace installs
   update with `claude plugin update skills-kengjudd@kengjudd`, since the
   plugin cache has no `.git` and `update.sh` exits 1 there. CLAUDE.md rule 3
   requires each `## Updating` section to name **both**. Mechanism details:
   /skill-authoring/update-mechanism.md.
3. **No import of old skills at initialization.** Initial scaffold only; the
   sole initial skill is `creating-skills` (the format's reference
   implementation). The old-skill inventory is preserved below for a future
   import session.
4. **Private repo, no LICENSE file.** Visibility is private (install requires
   git auth); no LICENSE is published. Consequence: `raw.githubusercontent`
   unauthenticated install/update patterns are unavailable by design.

## Rationale

### `skills/` vs `knowledge/`: the spec conflict forces disjoint subtrees

OKF requires every non-reserved `.md` in a bundle to carry YAML
frontmatter with a non-empty `type:` key (/specs/okf-spec.md — that document's
`spec_version`, mirrored by `okf_version` in the bundle index, is the only
place the version this repo targets is recorded). The Agent
Skills spec allows exactly six SKILL.md frontmatter fields (`name`,
`description`, `license`, `compatibility`, `metadata`, `allowed-tools`), and
claude.ai upload / Skills API packaging hard-fails on unknown keys
(/specs/agent-skills-spec.md). A SKILL.md therefore cannot conform to both
specs at once, so the OKF bundle root (`knowledge/`) and the skill folders
(`skills/`) are **disjoint subtrees** — CLAUDE.md binding rule 2. A related
terminology trap: OKF example bundles use `skills/` directories for markdown
"executor skill" concept docs, a completely different artifact from Agent
Skills folders; the two must never be conflated under one path.

### CLAUDE.md canonical, AGENTS.md thin adapter

The AGENTS.md standard has no import syntax; only Claude Code supports
`@file` imports (/specs/agents-md-standard.md). "Reference each other" is
therefore only mechanically possible one way. Since this project is Claude
Code–first, CLAUDE.md is the canonical instruction set and AGENTS.md is a
prose adapter that points non-Claude agents at CLAUDE.md. A literal mutual
`@import` was rejected: circular-import dedup behavior in Claude Code was
never verified, and the adapter pattern makes the question moot here.

### OKF canonical repo correction

The copy at `GoogleCloudPlatform/knowledge-catalog/okf/` is a **frozen
snapshot** — never cite it as current. The canonical home is
`github.com/GoogleCloudPlatform/open-knowledge-format` (SPEC.md at repo root,
which declares its version on a `**Version X.Y**` line; the repo has no
tags/releases, so that line is the only version source).
`scripts/check-spec-versions.sh` compares it against the `spec_version`
recorded in /specs/okf-spec.md and must run before significant KB changes
(CLAUDE.md rule 5). The match is anchored to the start of the declaration line
so a "Changes since Version X.Y" mention elsewhere in the document cannot be
read as current; exit 1 means drift, and exit 2 means the check could not run
(no `spec_version` in the KB, or no `**Version X.Y**` line in the fetched
spec — read the spec by hand before trusting the KB). The version this repo
targets is not restated here or anywhere else: it lives only in
/specs/okf-spec.md (`spec_version`) and the bundle index (`okf_version`).

### Why per-skill updates work despite no native mechanism

The research critic correctly noted that no researched distribution channel
provides per-skill versioning natively (SKILL.md has no standard version
field, and the verified ACT pattern uses ONE central update skill + a repo
VERSION). The user nevertheless chose per-skill commands; the resolution is
that `metadata.version` (the free-form `metadata` map is spec-legal) supplies
the per-skill version source, while `git pull` still updates the whole repo —
the per-skill version comparison in `scripts/update.sh` is what makes the
command per-skill. Marketplace caveat (verified from Claude Code docs):
plugin.json `version` pins the plugin; **users only receive marketplace
updates when that version is bumped**, so every release must move all four
repo-level version fields together — `VERSION`, `plugin.json` `.version`,
`marketplace.json` `.metadata.version`, and `marketplace.json`
`.plugins[0].version` (the one Claude Code compares). `./scripts/bump-version.sh
<semver>` sets all four; `--show` prints the current values.

## Deferred: old-skill imports

Decision 3 defers all imports. The complete inventory (23 skills, verified by
local inspection on 2026-08-29) is preserved here so an import session can
prioritize and act without re-scanning. Full path of each skill =
*source root* + `/` + *skill name*.

Source roots:

| Key | Root |
|-----|------|
| P  | `/Users/keng/Coding/presales/.claude/skills` |
| D  | `/Users/keng/Coding/dify/.agents/skills` |
| F  | `/Users/keng/Coding/flutter/.agents/skills` |
| K  | `/Users/keng/Coding/gitkeng/aws-kiro-atx-lab/.kiro/skills` |
| N1 | `/Users/keng/Coding/finoniq/finoniq2brain/.claude/skills` |
| N2 | `/Users/keng/Coding/finoniq/finoweb/.claude/skills` |
| U1 | `/Users/keng/.claude/skills` |
| U2 | `/Users/keng/.agents/skills` |

Readiness legend: **strong** = strong candidate, near drop-in;
**genericize** = reusable core but project coupling must be stripped;
**project** = project-specific, little generic value; **upstream** = unmodified
copy owned by an upstream repo (prefer cloning upstream over importing);
**vendored** = third-party-distributed skill (track upstream or freeze
deliberately).

| Skill | Src | Description | Readiness | Key dependencies |
|-------|-----|-------------|-----------|------------------|
| business-rules-extraction | K | Statically extract, document, verify business rules from any codebase with line-level evidence | strong | `scripts/validate_output.py` (python3), 2 JSON schemas, 5 references + 15 language playbooks; MIT, self-contained |
| comprehensive-codebase-analysis | K | Offline, evidence-backed architecture/security/tech-debt analysis of any repo, resumable | strong | `scripts/validate_output.py`, 2 schemas, 36 reference files, optional git/cloc, Mermaid v11; anchor of the Kiro trio |
| codebase-analysis-report | K | Portable offline accessible HTML report from comprehensive-codebase-analysis v2 output | strong | 3 Python scripts, pinned Mermaid v11 assets (SHA-256), 4 references; **hard input dep on comprehensive-codebase-analysis — import as a pair** |
| doc-to-markdown | U1 | Convert PDF/DOCX/XLSX to faithful Markdown incl. Thai OCR font-corruption repair | strong | 7 Python scripts (PEP 723 inline deps), `uv` on PATH, transcription subagents; strip `scripts/__pycache__` on import; referenced by requirement-to-module |
| frontend-testing | D | Generate Vitest + React Testing Library tests (incremental one-file workflow, AAA/black-box) | genericize | 6 references, 3 test templates, pnpm test CLIs, Dify `web/docs/test.md`; workflow + templates reusable for any Vitest+RTL project |
| backend-code-review | D | Checklist-based backend (.py) review for quality/security/maintainability | genericize | 4 rule references (Dify api/ layout, SQLAlchemy conventions), git; General Review Rules + output templates are generic |
| frontend-code-review | D | Checklist-based frontend (.tsx/.ts/.js) review, pending-change or file-targeted | genericize | 3 references (Dify React conventions), git; matched pair with backend-code-review — could be unified |
| component-refactoring | D | Refactor high-complexity React components (hook extraction, splitting, lookup tables) | genericize | Dify `pnpm analyze-component`/`refactor-component` CLIs, 3 references, skills frontend-testing + frontend-query-mutation; patterns generic once tooling stripped |
| requirement-to-module | P | Analyze TOR/RFP docs into Application Modules breakdown (.xlsx + .md, draw.io diagram); Thai frontmatter | genericize (heavy) | `scripts/build_outputs.py` (python3+openpyxl), doc-to-markdown skill, drawio plugin, presales `.memory/` KB + playbooks, 3+5 parallel subagents |
| frontend-query-mutation | D | Dify TanStack Query + oRPC contract-first query/mutation patterns | project | 2 references, `agents/openai.yaml`, Dify `web/contract`/`web/service` paths; entirely Dify-specific |
| analysis-report | K | AWS Transform (ATX) analysis + HTML5 assessment report, AWS/Kiro sales framing | project | Mermaid v11 reference, comprehensive-codebase-analysis output, templates *outside* the skill folder, node; AWS-branded variant of codebase-analysis-report |
| analyze-github-flake | F | Bucket flutter/flutter flaky-test issues into failure types | upstream | gh (auth), curl, dart, LUCI buildbucket API |
| dart-log-failure-parser | F | Parse failures from Dart/Flutter test logs; pure prompt knowledge | upstream | none (no scripts/references/CLIs) |
| find-release | F | Find lowest Dart/Flutter release containing a commit SHA | upstream | dart, `find_release.dart` inside the Flutter engine checkout (cannot run standalone) |
| flutter-cherry-pick | F | Land a formal cherry-pick of a merged flutter PR to stable/beta | upstream | `scripts/flutter_cp.dart`, dart/git/gh, in-repo PR template; must run from flutter repo root |
| flutter-pr-checks-finder | F | Find failing PR checks and their LUCI raw log URLs | upstream | gh or GitHub API, curl, LUCI; relative links into the flutter checkout; valuable builder→step mapping knowledge |
| rebuilding-flutter-tool | F | Rebuild the Flutter tool/CLI via helper script | upstream | `scripts/rebuild.dart`, dart, hardcoded repo-root-relative path |
| shepherd-prs | F | Shepherd/update/land own + approved third-party flutter PRs | upstream | `scripts/shepherd.dart`, dart, gh (workflow scope), autosubmit label; side-effectful |
| updating-android-sdk | F | Upgrade Flutter's Android SDK dep and upload CIPD packages | upstream | cipd (depot_tools), sdkmanager, in-repo files, Google/Flutter-infra write permissions — unusable externally |
| upgrade-browser | F | Upgrade Chrome/Firefox versions in Flutter Web Engine/Framework CI | upstream | `scripts/fetch_versions.dart`, dart, felt, in-repo CI files, CIPD upload perms |
| karpathy-llm-wiki | N1 | Personal LLM knowledge base with raw/ (immutable) + wiki/ (compiled) dirs | vendored | 4 templates; full git clone of Astro-Han/karpathy-llm-wiki (MIT) — strip `.git/` or track as vendored upstream |
| reui | N2 | Find/install/use ReUI registry components, examples, blocks, Motion Icons in shadcn projects | vendored | ReUI MCP server (account/license), shadcn CLI, `REUI_LICENSE_KEY`, 9 rules files; self-updating via MCP version beacon — a frozen central copy will drift |
| find-skills | U2 | Discover and install agent skills via `npx skills` and skills.sh | vendored | npx skills CLI, skills.sh; stock skills.sh single-file skill, trivial to import |

Import-session notes:

- The nine **F** skills are byte-identical to the official flutter/flutter
  repo (`git status` clean in the clone). Importing upstream-owned skills into
  a central repo duplicates what a plain clone already provides — default
  position: do not import; clone flutter instead.
- `codebase-analysis-report` + `comprehensive-codebase-analysis` must move
  together; `analysis-report` is their AWS-branded sibling and likely stays
  behind.
- Any import must follow the `creating-skills` lifecycle (CLAUDE.md rules 3–4):
  add an `## Updating` section covering both install channels
  (`./scripts/update.sh <skill-name>` and
  `claude plugin update skills-kengjudd@kengjudd`) plus `metadata.version`,
  register in `.claude-plugin/plugin.json`, capture knowledge, and bump all
  four repo-level version fields with `./scripts/bump-version.sh <semver>`.
  Names must not collide with the 40+ `act-*` and other skills already
  installed on the machine: check every directory `install.sh` targets and the
  plugin-provided skills, per the **Skill naming** rule in the repo-root
  `CLAUDE.md` (authoritative list — do not keep a copy here).

## Open questions inherited from the research critic

Still relevant after the 2026-08-29 decisions:

- **GitHub Copilot / VS Code discovery path unverified** (`.github/skills` vs
  `.agents/skills`) — the docs page was deliberately left unfetched. Needed
  before adding Copilot as an `install.sh --tool` target. Source:
  docs.github.com/en/copilot/concepts/agents/about-agent-skills.
- **Amp's exact SKILL.md frontmatter support unverified** — primary docs
  404'd/redirected during research; only discovery paths were confirmed.
- **Marketplace re-fetch on unbumped versions**: researchers disagreed on
  certainty; the docs quote ("users only receive updates when you bump it")
  is authoritative but should be verified empirically with a scratch
  marketplace before relying on marketplace-only users staying current.
- **anthropics/claude-code#50778** (native `.agents/skills` support in Claude
  Code): closed as "completed" on 2026-04-19, but as of 2026-08-29 the
  official Claude Code skills docs still list no `.agents/skills` discovery
  location — if native support ever ships in the docs, one universal
  `.agents/skills` dir could replace per-agent symlinking in `install.sh`.
- **Per-agent enforcement of `allowed-tools`** (experimental field) —
  unverified; matters if a future skill (e.g. an imported `reui`) restricts
  tools.
- **Tolerance of an extra `type:` key in SKILL.md** across agents — largely
  moot given the disjoint-subtree decision (claude.ai upload is a known
  hard-fail; Claude Code tolerates extras; others unverified).

Resolved by the design (no longer open): circular `@import` behavior
(mooted by the prose-only AGENTS.md adapter) and the vercel-labs/skills
lockfile format (the `npx skills` distribution path was not chosen).
