# Changelog

All notable changes to this repository are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

Per-skill versions live in each skill's `SKILL.md` under `metadata.version`.
When a skill changes, bump both the skill's `metadata.version` and this repo's `VERSION`,
and record the change here under the skill's name.

## [0.10.0] - 2026-08-31

### init-project

**Added — init-project 1.0.0.** Initializes a *target* project so the AI coding
agents the user selects can work in it: it interviews the user (project
identity, agents, task types, stack, knowledge-base folder name, Karpathy
guidelines opt-in), researches any selected agent or named technology its
bundled reference does not already cover, creates an OKF knowledge base inside
the project, generates a canonical `AGENTS.md` plus only the per-agent adapters
those agents actually need, and runs an adaptive expert review before reporting.
It never scaffolds application code, never runs `git init`, and never installs
third-party skills. Twelve agents are covered by a bundled context matrix
(Claude Code, Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp,
Goose, ZCode, Antigravity); only two of them need an adapter, and five expand no
imports at all, so the canonical file is written self-contained rather than
delegating its substance to `@` references.

**Hardened by two end-to-end runs before release.** Scenario A (empty directory)
hit a hard dead end and three contradictions: Phase 1 never asked for the
project's name or purpose although both templates require them and the skill
forbids inventing or leaving placeholders (the only path that produces them is
"read the README", which an empty directory does not have) — a `Project
identity` topic was added; the guidelines promised context files hold "the
commands an agent runs" with no template section for them — a `## Commands`
section was added; the review protocol cited `R9`, a requirement ID that exists
only in the internal plan; and the KB guide called the index body format "fixed"
in a way its own shipped skeleton contradicts. Scenario B (existing codebase,
merge into a pre-existing `AGENTS.md`) hit two more, both cases of rules that
are individually right and jointly unsatisfiable: the KB iron rule demanded a
resolvable URL for every fact while the `knowledge base` preset invites seeding
from an in-repo README that has no URL, and a user-chosen KB update cadence
contradicted the verbatim standing-rules block, producing two conflicting rules
in one generated file with no permitted remedy. The first pass at those two
fixes was itself wrong twice — it cited a source category the OKF spec does not
define (a bare relative path resolves from the concept file, i.e. inside the KB
folder, so project material needs `../`), and it reconciled one superseded
standing-rules bullet where a non-default cadence conflicts with two.

**Hardened by a four-domain expert panel.** Loop, harness, context, and prompt
engineering reviewers ran in parallel over the frozen skill; every finding was
accepted (59 applied as written, 6 adapted, none dropped), and the wave itself
introduced four contradictions that took a second round. The behavior changes:

- **Cost.** The interview's technology expansion was an unbounded rewrite
  relation — one scenario produced 9 concepts and 27 extra questions, another
  none. Expansion is now depth-1 with terminal items and fires only for
  technologies chosen as a project decision, under a 25-question ceiling with a
  cost preview and a continue/recommend/defer valve; research is bounded at 3
  fetches per technology with per-field "not applicable"; the review loop
  converges (one pass plus one re-check of only what changed) with a roster cap
  of 5 domain reviewers plus 2 standing ones, grouped by shared surface and
  named in the report. Measured: 44 questions → 18 on the same scenario.
- **Re-runs.** Provenance markers were written only when merging, so a second
  run could not recognize its own output and appended a full duplicate (82 lines
  → 164, past the file's own budget). Markers are now unconditional on every
  generated file including the KB index, which makes the re-run promise literal,
  and a new Phase 0 detects a previous run, replays the previous answers, asks
  only what changed, and re-researches only what is stale.
- **Harnesses.** New iron rule 4 — *if you cannot ask, do not write*: with no
  user channel (headless, CI, subagent) the skill emits the question list and
  stops instead of substituting defaults. The KB skeleton no longer overwrites
  an existing `index.md`/`log.md`; the OKF version check works through any fetch
  mechanism (a shell network error is not evidence of being offline); `<kb>`
  folder names are validated and checked case-insensitively; concurrent runs
  re-read before writing.
- **Correctness of output.** Before writing, the skill now checks the target for
  files that shadow or duplicate `AGENTS.md` and warns about native `/init`
  commands that would overwrite it, using the matrix's verbs verbatim — one run
  had emitted an *invented* claim about `/init` that contradicted the researched
  matrix. Scaffolder collisions (a framework CLI that writes its own agent
  context files) are surfaced too.
- **Drift and duplication.** The standing-rules block is single-sourced in the
  template (the byte-identity contract between two copies is retired) and
  cross-references anchor to bullet text rather than ordinals; merge semantics
  is stated once with pointers elsewhere; `skip` and `replace` are now defined
  alongside `merge`; the 512-line agent matrix is read one `## <agent>` section
  at a time.
- **Language and triggering.** An explicit never-translated list (standing-rules
  and Karpathy blocks, the HTML markers, YAML keys and `type:` values) resolves
  the contradiction between the language answer and the verbatim blocks. The
  description is front-loaded with "Use when" and its trigger phrases because
  some agents inject only ~250 characters of it, and it names the built-in
  `/init` as an anti-trigger. Final validation: triggers 7/7, both scenarios
  green.

### Knowledge

- New concept `knowledge/agents/agent-init-conventions.md` (`Reference`), the
  precursor research for the skill: for each of the 12 target agents, the
  instruction/context files it reads and their precedence, import syntax, native
  init command, and config file locations — every claim from official docs,
  repos, or changelogs, with ten questions parked as known gaps rather than
  guessed. It feeds the skill's bundled `references/agent-context-matrix.md`.
- New concept `knowledge/skill-authoring/init-project-lessons.md` (`Playbook`):
  what building an orchestrator-sized skill taught — canonical file plus thin
  adapters and why imports cannot carry content, bounding loops rather than only
  specifying them, the dead-end classes only an end-to-end run finds versus the
  cost/re-run/harness classes only a review panel finds, deciding a
  write-identity mechanism before the first template, verbatim-vs-language
  conflicts, and trigger wording against a built-in command.
- Fixed a stale fact in `knowledge/specs/agents-md-standard.md`: Gemini CLI's
  AGENTS.md opt-in is the nested `context.fileName`, not the flat
  `contextFileName` recorded on 2026-08-29 (verified 2026-08-31 against
  `google-gemini/gemini-cli` `docs/cli/gemini-md.md`, added as a source). No
  official changelog names the rename, so the old key's removal and any
  compatibility alias stay recorded as an open question in
  `knowledge/agents/agent-init-conventions.md`.

## [0.9.1] - 2026-08-30

### comprehensive-codebase-analysis (1.1.0 → 1.1.1)

**Fixed — the validator rejected its own SKILL.md.** `check_skill_frontmatter`
flattened the frontmatter block, so `metadata.version` was read as a top-level
key and the "only name and description" rule failed every run with
`FAIL: skill frontmatter and limits`. The `metadata` map is one of the six
portable Agent Skills fields and is where this repository requires version and
provenance to live. Same class of defect as the neutrality self-hit fixed in
0.8.0: a check inherited at import did not know the distributing repository's
rules.

- Top-level keys and the nested `metadata` map are now parsed separately.
  Top-level keys are checked against the six portable fields by name, so a
  Claude-only field such as `model:` is still rejected — and with a message that
  names the offending field instead of a blanket "must contain only name and
  description".
- `allowed-tools` remains prohibited, but now reports its own reason rather than
  being mislabelled non-portable: it *is* one of the six portable fields; this
  skill forbids tool restrictions separately.
- `metadata.version` must be SemVer and `metadata.updated` must be `YYYY-MM-DD`
  when a `metadata` map is present — previously unchecked.
- A stray indented key outside a `metadata` block is reported instead of being
  silently absorbed.

## [0.9.0] - 2026-08-30

### comprehensive-codebase-analysis (1.0.1 → 1.1.0)

**Fixed — generated Mermaid diagrams sometimes did not render.** The shipped
check was a bracket-balance matcher plus a first-token test, so it reported
`PASS: Mermaid v11 syntax` on an output tree containing three diagrams that
render nothing at all. A Mermaid parse error blanks the whole block, so each one
cost an entire diagram. All three had balanced brackets:

- a node shape attached to an edge instead of an id — `docugent -->[("MongoDB")]`
  instead of `docugent --> mongo[("MongoDB")]`;
- a `sequenceDiagram` keyword used inside a flowchart — `actor caller["…"]`,
  where an actor is an ordinary node;
- a `;` inside a sequence message, which is a statement separator and silently
  truncates the message text.

- Added a type-aware heuristic linter (6 rules, stdlib only, offline). Rules are
  keyed by diagram type because the same token differs in meaning between them:
  `loop["Per page"]` is a node in a flowchart and a block opener in a sequence
  diagram. Calibrated against mermaid 11.17.2: 26/26 agreement on a valid/invalid
  suite with **zero false positives**, so a correct diagram is never rejected.
- Every Mermaid block in the tree is now linted, not only the six files where a
  diagram is required — `architecture/dependencies.md` had never been checked
  despite a template asking for a diagram there.
- Acceptance criterion changed from "passes the shipped lint" — circular, since
  the bar was whatever the weakest tool measured — to "every Mermaid block
  renders", with the lint named as partial evidence.

**Fixed — three of the four diagram-producing phases never saw the syntax
rules.** Mermaid is written in the architecture, behavior, reference-analysis,
and operations-diagrams phases, but the guidance lived in
`playbook-diagrams.md`, which only the last of those loads. Rules moved to a new
`references/mermaid-syntax.md`, added to all four phase load lists, and expanded
to cover the constructs that actually break rendering.

**Fixed — a template example that taught the mistake.** `actor` was used as a
flowchart node id in `template-architecture.md` and `template-diagrams.md`, and
as a sequence keyword elsewhere in the same skill, while the playbook asks for
several actors in one system-context view. A node id cannot be reused, so the
agent reached for the declaration form and produced a parse error. Example ids
are now `client` and `externalUser`.

### Knowledge

- New concept `knowledge/skill-authoring/validating-generated-artifacts.md`
  (`Playbook`): why a hand-written checker drifts away from "will the consumer
  accept this", how to calibrate one against the real parser without introducing
  false positives, and how progressive disclosure starves rules that cut across
  phases.

## [0.8.0] - 2026-08-30

### codebase-analysis-report (1.0.1 → 1.1.0)

**Fixed — every render failed.** The vendor-neutrality scanner scanned this
skill's own `SKILL.md`, whose `metadata.upstream` names the repository the skill
was imported from (`gitkeng/aws-kiro-atx-lab`) as `CLAUDE.md` requires. The
substrings `aws` and `atx` matched the denylist, so the publication gate rejected
every report. Present since 0.4.0.

- Neutrality is now split by blast radius. `scan_emitted_assets()` guards
  publication and covers only what reaches `index.html` (`report.css`,
  `report.js`, the renderer's chrome). `scan_authored_docs()` covers `SKILL.md`,
  `README.md`, and `references/*.md` and runs in the test suite only — a
  documentation defect no longer blocks publishing a valid report.
- `metadata.upstream` is exempt from the scan in every YAML form it can take
  (quoted, folded `>`, literal `|`, CRLF files). `name`, `description`, body
  prose, and a top-level `upstream:` key remain in scope.
- Closed two pre-existing holes in the publication gate that the over-broad doc
  scan had been masking: the renderer's chrome was checked against a narrower
  second denylist, so the bare tokens `aws`, `amazon`, `azure`, `gcp`, and `atx`
  were never checked against it; and chrome was extracted with a triple-quote
  regex, so wording in ordinary quoted literals escaped entirely. Chrome is now
  walked via the module AST against a single denylist.
- Neutrality failures now report the file, the line number, the offending text,
  and the skill root — report directories have an `assets/` directory of their
  own, so the paths were ambiguous.
- On validation failure the renderer keeps the unpublished temp output and prints
  its path plus the command to list every error. The workflow had always
  instructed the agent to report that path, but a `finally: rmtree` deleted it
  first. Nothing is published either way.

**Added.** `python3 scripts/validate_report.py --self-check` runs both neutrality
tiers with no report directory and no fixture — the check to run after editing
the skill's own files.

**Fixed — the self-test suite could not pass on a valid fixture.** Cases
hardcoded `BR-007`, `TC-008`, `CMP-001`, and the literal `"AWS SDK"` from one
finding's title, contradicting the documented promise that any completed v2
output tree is a valid fixture. Cases now synthesize the shape they need into
their temp copy, preserving the renderer's cross-manifest invariants. Verified on
four fixtures, including trees with no vulnerabilities, with no tests, and with
no registries populated at all: 100 tests pass on each.

### Knowledge

- New concept `knowledge/skill-authoring/imported-self-checks.md` (`Playbook`):
  what goes wrong when an imported skill ships its own validation gate — it can
  reject the provenance this repo mandates, over-reach past the artifact it
  guards, and encode the shape of one fixture — plus the checklist for the next
  such import.

## [0.7.0] - 2026-08-30

**BREAKING — plugin channel only.** The Claude Code plugin is renamed
`skills-kengjudd` → `kengjudd` (`.claude-plugin/plugin.json` `name` and the
marketplace entry's `name`). Plugin skills are namespaced by the plugin name,
so every skill now invokes as `kengjudd:<skill-name>`
(e.g. `kengjudd:git-commit`) — the same short-prefix pattern obra/superpowers
uses for `superpowers:<skill>`. Nothing else moved: the GitHub repository
name, clone URLs, the marketplace name (`kengjudd`), and the git-clone +
symlink channel are all unchanged, and the symlink channel never had a prefix
to begin with. No install of the old plugin id existed on this machine at
rename time (checked `~/.claude/plugins/cache`); anyone who did install
pre-rename runs `/plugin uninstall skills-kengjudd@kengjudd`, then
`/plugin install kengjudd@kengjudd` (a qualified-name install refreshes the
marketplace first, so no separate update step is needed). Pre-1.0 SemVer:
breaking rides the minor line.

### Added

- **creating-skills 1.2.0** — the creation workflow now handles skill
  prefixes explicitly for every new skill: a repo that already ships a
  plugin (this repo: `kengjudd`) gets the skill registered there so it
  inherits `kengjudd:<skill-name>`; a repo with no plugin packaging must
  ask the user "prefix or none?" *before* scaffolding and record the
  answer in `knowledge/`. New "Skill prefixes" section in SKILL.md, a
  matching item in the authoring checklist, and the rule that the plugin
  name is chosen once, early (renaming it later is breaking). Reviewed
  before release by three domain experts (skill authoring, prompt
  engineering, context engineering — parallel subagents, 0.6.0 precedent);
  consensus and verified findings applied in one pass: the no-plugin
  branch is executable (explicit registration exception to step 8), the
  exact user-facing question is spelled out and the **user** picks the
  plugin name, imports pass through the prefix gate, the section links
  its knowledge concept, the update workflow re-runs the checklist
  (trigger tests when the description changed), validation runs before
  version bookkeeping on the create path, "Name it" checks installed-name
  uniqueness, `metadata.upstream` stays one combined string, a plugin-
  cache guard was added to "Before you start", and the description gained
  the "named, prefixed" trigger words.

### Changed

- All six skills' `## Updating` sections now point at `kengjudd@kengjudd`, as
  does every other mention of the plugin channel: CLAUDE.md, AGENTS.md,
  README.md, the authoring checklist, the skill template,
  `scripts/update.sh`'s reload reminder, and the business-rules-extraction
  README (install command + version line). Patch bumps:
  **creating-skills 1.2.0** (minor — new prefix workflow, see Added),
  **business-rules-extraction 1.0.1**,
  **comprehensive-codebase-analysis 1.0.1**, **codebase-analysis-report
  1.0.1**, **doc2markdown 1.1.1**, **git-commit 1.0.1**.
- README documents that plugin-channel skills invoke namespaced as
  `kengjudd:<skill-name>` (bilingual note in the install section).

### Knowledge

- `knowledge/decisions/2026-08-30-plugin-name-kengjudd.md` — the rename
  decision: mechanism (prefix = plugin name, sourced from the Claude Code
  docs and obra/superpowers), what deliberately did not change, and the
  migration path for pre-rename installs.
- `knowledge/specs/claude-code-plugins.md` — namespacing section rewritten
  around the verified docs quote ("Plugin skills are namespaced by the plugin
  name"), with the design consequence spelled out (the plugin `name` field is
  where you choose the invocation prefix) and obra/superpowers added as a
  source; this repo's install example updated.
- `knowledge/skill-authoring/update-mechanism.md` and
  `knowledge/skill-authoring/best-practices.md` — plugin-channel command
  updated to `kengjudd@kengjudd`.
- `knowledge/skill-authoring/skill-prefixes.md` (Playbook) — where an
  invocation prefix comes from (the plugin name, never the skill's own
  name), the reuse-or-ask flow for new skills, how to choose a plugin name,
  and why a late plugin rename is breaking.

## [0.6.0] - 2026-08-30

### Added

- **git-commit 1.0.0** — Gitmoji + Conventional Commits messages from the
  whole working tree (staged + unstaged + untracked), grouped into
  one-commit-per-concern and committed only after explicit approval.
  Promoted from the user-level slash command `/commit`
  (`~/.claude/commands/commit.md`, no git history — first command-to-skill
  conversion, recorded in `metadata.upstream`). Beyond the source command:
  full-tree survey with safety preconditions (stops on unfinished
  merge/rebase, detached HEAD, unborn branch), secrets/artifact exclusion
  before grouping, whole-path-only staging with a clean-index reset and
  per-group verification, hook-failure handling, and a closed final-state
  check. First skill authored through two-domain expert review (git expert
  + senior developer subagents; 20 findings applied in one pass).

### Knowledge

- `knowledge/skill-authoring/command-to-skill.md` — new playbook: command
  `description` is help text while a skill description is the trigger,
  `!`-injected context becomes an explicit survey step, `allowed-tools`
  syntax carries over, and scope/source-deletion are owner decisions.

## [0.5.0] - 2026-08-29

### Added

- **doc2markdown 1.1.0** — convert a PDF, DOCX, XLSX, or PPTX into faithful
  Markdown with images extracted and tables preserved, including Thai OCR
  font-corruption repair (SARA AM recomposition, SARA AA collapse detection).
  Imported at 1.0.0 from the user's machine-local
  `~/.claude/skills/doc-to-markdown` and **renamed on import** — the first
  import from a source with no git history, and the first rename
  (`metadata.upstream` records the local origin accordingly) — then extended
  in the same release to 1.1.0 with PPTX support: `extract_pptx.py` (shape
  and group reading-order via the `chOff`/`chExt` transform, run coalescing,
  full-page-picture scan vs background detection, speaker notes,
  unreadable-chart placeholders, low-res render flags), pptx rules in the
  SKILL.md body, and the "แปลงสไลด์"/"พาวเวอร์พอยต์" trigger words. Eight
  Python scripts with PEP 723 inline dependencies (`uv` on PATH),
  subagent-based page/slide transcription, and a merge-time audit
  (`missing_parts`, `broken_image_links`, `unreferenced_assets`, …).

### Knowledge

- `knowledge/skill-authoring/importing-skills.md` — extended with the two new
  cases this import surfaced: provenance for local sources with no git
  repository, and rename-on-import (frontmatter `name` must match the new
  directory; the original stays installed and competes on description-match).
  Import-status table now covers 4 of the 23 deferred skills.

## [0.4.0] - 2026-08-29

First skill import: the three codebase-analysis skills from
`gitkeng/aws-kiro-atx-lab` (`.kiro/skills/`). All three start at
`metadata.version` 1.0.0 per the import rule; their upstream repository, path,
commit, and upstream version are recorded in `metadata.upstream`.

### Added

- **business-rules-extraction 1.0.0** — static, read-only extraction of business
  rules from any codebase into domain-decomposed catalogs with line-level
  evidence, coverage accounting, and a Python validator. Imported from
  `aws-kiro-atx-lab@595f830` (upstream version 1.1.0). MIT-licensed, ships its
  own LICENSE.
- **comprehensive-codebase-analysis 1.0.0** — offline, evidence-backed
  architecture, behavior, security, tech-debt, migration, and onboarding
  analysis with a resumable phase model and machine-auditable manifest.
  Imported from `aws-kiro-atx-lab@7423a91`.
- **codebase-analysis-report 1.0.0** — renders a completed
  `comprehensive-codebase-analysis` **v2** output tree into a single offline,
  accessible HTML report (pinned local Mermaid v11). Imported from
  `aws-kiro-atx-lab@4320cce` plus the source's uncommitted working-tree changes.
  Hard input dependency on `comprehensive-codebase-analysis`, recorded in
  `metadata.requires` — the two are a pair.

### Changed

- All three imported SKILL.md files gained the required two-channel
  `## Updating` section and an explicit statement that their `scripts/` and
  `references/` paths resolve against the skill directory (`readlink -f`), not
  the analyzed repository — the copy-the-directory assumption breaks under this
  repo's symlink install.
- `README.md` is now bilingual (English then Thai in every section). Commands
  and tables are stated once and shared by both languages so the two versions
  cannot drift apart.
- `business-rules-extraction/README.md`: Kiro-specific `cp -r` install table
  replaced with `./scripts/install.sh --tool <agent>` and the plugin channel;
  version line and CI example corrected to this repo's numbering and layout.

### Knowledge

- `knowledge/skill-authoring/importing-skills.md` (Playbook) — what an import
  actually requires (provenance, renumbering, updating section, path
  re-anchoring, host-specific READMEs, bundled licenses), how to record a dirty
  source working tree, why paired skills ship together, and an import-status
  table over the 23-skill deferred inventory.

## [0.3.0] - 2026-08-29

Final expert-review round: regression fixes, two script bugs, and consolidation
of the release procedure.

### Added

- `scripts/bump-version.sh <semver>` — sets all four repo-level version fields
  in lockstep (`VERSION`, `plugin.json` `.version`, `marketplace.json`
  `.metadata.version`, `marketplace.json` `.plugins[0].version`). `--show`
  prints the current values. The previous instructions said "the `version`
  fields" without naming them, and `marketplace.json` has two.
- `CLAUDE.md`: where a new knowledge concept goes (directory + `type:` per
  kind), and a release procedure for knowledge-only and scripts-only changes.
- Authoring checklist: `knowledge/index.md` listing, README skills-table row,
  the spec-freshness gate, and the `skills-ref validate` portability gate.

### Fixed

- **`install.sh --force` could destroy real data.** It ran `rm -rf` on any
  existing path, including a real directory (the plausible case when importing
  a skill that already lives in `~/.claude/skills`). It now removes symlinks
  only and moves a real file or directory aside to `<name>.bak.<pid>`.
- **`install.sh` exited 0 on an unknown `--tool`.** `targets_for_tool` runs in
  a process substitution, so its `exit 1` killed only the subshell: a typo
  installed nothing while reporting success. The value is now validated in the
  main shell before the loop.
- `check-spec-versions.sh` matched `Version X.Y` anywhere in the spec; a
  "Changes since Version 0.2" line above the header would have reported a stale
  version as current. It now anchors to the `**Version X.Y**` declaration line
  and exits 2 if that line is absent.
- README skills table showed creating-skills at 1.0.0 after the 1.1.0 bump.
- The OKF version was hardcoded in four instruction files; it now lives only in
  `knowledge/index.md` and `knowledge/specs/okf-spec.md`.
- `templates/skill-template/` shipped two defects into every scaffolded skill:
  a `$0`-based path snippet that does not work in a SKILL.md body, and a link
  to a `references/example.md` that does not exist.
- Clone instructions offered only the SSH URL while this checkout uses HTTPS.
- KB playbooks that restated the single-channel update rule and the conditional
  plugin bump were brought back in line with CLAUDE.md (binding rule 7).

## [0.2.0] - 2026-08-29

Expert review of `CLAUDE.md` / `AGENTS.md` (three specialist lenses) plus
verification of two open facts.

### Added

- `GEMINI.md` adapter — Gemini CLI reads neither `AGENTS.md` nor `CLAUDE.md`,
  so without it a Gemini session got zero instructions.
- `install.sh --tool zcode` → `~/.zcode/skills` (ZCode's highest-precedence
  root). `--tool zcode` previously errored out.
- Binding rule 7 in `CLAUDE.md`: this file wins when a derived document
  contradicts it.
- ZCode (Z.ai) documented in the knowledge base: reads AGENTS.md only, never
  `CLAUDE.md` at runtime; skill discovery roots and frontmatter limits.

### Changed

- **creating-skills 1.0.0 → 1.1.0**: the `## Updating` section now covers both
  install channels. `./scripts/update.sh` cannot work for plugin-marketplace
  installs because the plugin cache has no `.git`; those users run
  `claude plugin update skills-kengjudd@kengjudd`. Same fix in
  `templates/skill-template/` and the authoring checklist.
- `CLAUDE.md` rule 4 and the Versioning section now include the
  `.claude-plugin/` `version` bumps — plugin users receive nothing without them.
- `CLAUDE.md` rule 2 no longer contradicts the OKF section: `index.md` and
  `log.md` are exempt from the `type:` requirement.
- Documented the private-repo auth prerequisites for
  `/plugin marketplace add` (SSH by default; `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1`
  or an SSH URL for HTTPS-only setups).
- `AGENTS.md`: fourth invariant (six-field frontmatter), zcode's
  AGENTS.md-only behavior, corrected agent list (added Amp, Goose).
- Structure diagram and README layout table now include `docs/`.
- Skill-name collision check now lists all five `install.sh` target directories.

### Fixed

- `check-spec-versions.sh` exited 56 (`curl` + `grep -m1` broke the pipe under
  `pipefail`); the spec is now buffered before matching.
- `knowledge/agents/skill-discovery-matrix.md` said opencode recognizes "six"
  spec frontmatter fields while listing five — it recognizes five and silently
  ignores `allowed-tools`.

## [0.1.0] - 2026-08-29

### Added

- Initial repository structure: `skills/`, `knowledge/` (OKF 0.2 bundle), `scripts/`, `templates/`.
- `creating-skills` skill v1.0.0 — meta-skill for creating and updating skills in this repo.
- `scripts/install.sh` — symlink skills into per-agent skill directories.
- `scripts/update.sh` — per-skill update engine (fetch → compare version → changelog → pull).
- `scripts/check-spec-versions.sh` — OKF spec version freshness check.
- `CLAUDE.md` (canonical agent instructions) and `AGENTS.md` (adapter for other agents).
- Claude Code plugin packaging (`.claude-plugin/plugin.json`, `marketplace.json`).
- Knowledge base seeded with spec summaries, agent discovery matrix, skill-authoring playbooks, and the founding design decision record.
