# Knowledge Base Log

## 2026-08-31

- **init-project 1.0.0** (repo v0.10.0) — the repo's first orchestrator-sized
  skill: it interviews the user, researches, writes an OKF knowledge base into a
  *target* project, generates a canonical `AGENTS.md` plus only the per-agent
  adapters that agent actually needs, and runs an adaptive expert review.
  Built on the per-agent research below, then hardened twice. **Two end-to-end
  runs** (empty directory; existing codebase with a merge) found six defects in
  two classes: data the workflow demands but never collects (the templates
  require a project name and purpose; no interview topic asked, and the only
  path that produces one is "read the README", which an empty directory lacks),
  and rules that are individually right but jointly unsatisfiable on one input
  (URL-only sources vs. a preset that seeds from an in-repo README; a
  user-chosen KB cadence vs. a verbatim standing-rules block that fixes the
  cadence — two conflicting rules in one generated file, failing the skill's own
  review bar). A **four-domain expert panel** (loop, harness, context, prompt
  engineering, parallel read-only reviewers) then found what a run cannot see:
  nine unbounded loops, an iron rule that is unsatisfiable headlessly, a
  skeleton write that overwrites an existing index and log on re-run, a
  standing-rules block duplicated byte-identically with cross-references by
  *ordinal*, a 512-line reference loaded whole for one section, and markers
  written only on merge so a second run duplicated everything. All findings
  accepted; 59 applied as written, 6 adapted, none dropped — and the wave itself
  introduced four contradictions needing a second round. Post-fix validation:
  triggers 7/7, both scenarios green, interview cost 44 questions → 18 with the
  same output.

- **Creation** of /skill-authoring/init-project-lessons.md (`Playbook`)
  alongside that skill: the transferable half — imports are an adapter
  mechanism and never a content-organization one (5 of 12 agents expand no
  imports at all, so a canonical file that delegates its substance loses it);
  every "for each X" is a loop needing a depth, a ceiling, an exit, and a cost
  preview shown before it is spent; adaptive reviewer rosters need a cap and a
  named adjudicator with a recorded reason per rejection; a skill that writes
  files it may write again must decide its **write-identity mechanism first**
  (unconditional markers, not merge-only ones) because every re-run behavior is
  downstream of it; a language choice must enumerate what it does *not* apply to
  (verbatim blocks, markers, YAML keys); and a description must name the
  built-in command it is not — trigger testing caught this skill matching the
  built-in `/init`, and some agents show only ~250 characters, so triggers go
  first. Also records what only a run finds vs. what only a panel finds, and
  that emergent good behavior is a missing instruction rather than a success.

- **Correction** in /specs/agents-md-standard.md, closing the follow-up owed
  below: the Gemini CLI opt-in setting is the nested `context.fileName`, not the
  flat `contextFileName` recorded there on 2026-08-29 — verified against
  `google-gemini/gemini-cli` `docs/cli/gemini-md.md` on 2026-08-31, with the
  repo-docs URL added as a source and the docs-site entry re-titled to say which
  name it backs. The setting takes a list and can include `AGENTS.md`. No
  official changelog entry names the rename, so the old key's removal and any
  compatibility alias remain unconfirmed; the known gap in
  /agents/agent-init-conventions.md was rewritten from "a live conflict inside
  this bundle" (with an action item) to that narrower open question.

- **Per-agent init conventions** — new `Reference` concept
  `/agents/agent-init-conventions.md`, the research foundation for the upcoming
  `init-project` skill. For all 12 target agents (Claude Code, Codex, Cursor,
  opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose, ZCode, Antigravity) it
  records the instruction/context files read and their precedence, import
  syntax, native init command, and config file locations — every claim from
  official docs, official repos, or vendor changelogs. Four agents had no
  context-file coverage in this bundle before: **Kiro** (steering files under
  `.kiro/steering/`, with `AGENTS.md` accepted as an always-included steering
  source and `#[[file:…]]` embeds), **Amp** (the widest AGENTS.md search of the
  twelve — cwd up to `$HOME`, subtrees on access, two user paths, three system
  paths, `AGENT.md`/`CLAUDE.md` fallback, `@`-mentions with globs), **Goose**
  (`["AGENTS.md", ".goosehints"]` at every level, overridable via
  `CONTEXT_FILE_NAMES`), and **Antigravity** (Google's agentic IDE: reads
  workspace `GEMINI.md` *and* `AGENTS.md`, global `~/.gemini/GEMINI.md`, rules
  under `.agents/rules` capped at 12,000 chars, `@path/to/file` inlining since
  v2.11.0).

- **Two findings that change how the skill must be built.** First, only **two**
  of the twelve need an import adapter — Claude Code (`CLAUDE.md` with
  `@AGENTS.md`) and Gemini CLI (`GEMINI.md` with `@AGENTS.md`, since it reads
  AGENTS.md only when `context.fileName` is configured); every other agent reads
  `AGENTS.md` in some form, including Kiro and Antigravity, whose behavior was
  unknown when the spec was written. Second, **five agents expand no imports at
  all** (ZCode explicitly, plus Codex, opencode, Zed, Goose), so a canonical
  AGENTS.md that delegates its substance to `@`-referenced files silently loses
  that substance on nearly half the target set. Imports are an adapter
  mechanism, not a content-organization one — the generated file must be
  self-contained.

- **Follow-up owed to `/specs/agents-md-standard.md`.** That concept records the
  Gemini CLI opt-in setting as flat `contextFileName` (verified 2026-08-29); the
  current Gemini CLI docs give the nested `context.fileName`, matching the
  documented move of `settings.json` to a nested structure. The new concept
  records the verified name and flags the divergence as a known gap; the older
  concept was deliberately left untouched because it sits outside the change
  that surfaced this, and should be corrected in its own edit.

- **Ten questions parked as known gaps rather than guessed**, notably
  Antigravity's AGENTS.md-vs-GEMINI.md precedence and the version at which it
  began reading AGENTS.md (third-party guides state one; no official entry
  does), Cursor's `@filename` expansion inside AGENTS.md as opposed to `.mdc`
  rules, Kimi CLI's two config homes (`~/.kimi/` in the repo docs vs
  `$KIMI_CODE_HOME` default `~/.kimi-code/` on kimi.com), and ZCode's split
  between `~/.zcode/v2/config.json` (provider settings) and
  `~/.zcode/cli/config.json` (`mcp.servers`, and the per-skill `enable: false`
  this bundle recorded from engine inspection) with no documented rule for which
  keys belong where. Several entries are "not documented" rather than
  "confirmed absent" — for missing init commands (Zed, Amp, Antigravity) the
  distinction is stated explicitly so a later reader does not upgrade silence
  into a fact.

## 2026-08-30

- **comprehensive-codebase-analysis 1.1.1** — the skill's validator rejected its
  own `SKILL.md`: `check_skill_frontmatter` flattened the frontmatter block, so
  `metadata.version` counted as a top-level key and the "only name and
  description" rule failed on every run. **Third instance of the same class in
  two days** (after the neutrality self-hit in codebase-analysis-report 1.1.0):
  a check inherited at import enforcing the source repository's conventions
  against a destination that mandates different ones. Fixed by parsing the
  nested `metadata` map separately, checking top-level keys against the six
  portable Agent Skills fields by name, and adding SemVer/date checks on
  `metadata.version` and `metadata.updated`, which had never been validated.
  Confirms the checklist in `/skill-authoring/imported-self-checks.md` — grep an
  imported skill's checks against this repo's mandated conventions *before* the
  import commit — and that the cost of skipping it is one silent broken gate per
  imported skill.

- **comprehensive-codebase-analysis 1.1.0** — Mermaid diagrams the skill
  produced sometimes failed to render. Root cause: the shipped check was a
  bracket-balance matcher plus a first-token test, so it reported
  `PASS: Mermaid v11 syntax` on a real output tree carrying three diagrams that
  render nothing. All three had balanced brackets — a node shape attached to an
  edge instead of an id (`docugent -->[("MongoDB")]`), a `sequenceDiagram`
  keyword used in a flowchart (`actor caller["…"]`), and a `;` inside a sequence
  message, which is a statement separator and truncates the text. A Mermaid
  parse error blanks the entire block, so each cost a whole diagram. Added a
  type-aware heuristic linter (6 rules, stdlib only, offline), extended the scan
  from the six files where a diagram is *required* to every Mermaid block in the
  tree (`architecture/dependencies.md` had never been checked despite a template
  asking for a diagram there), and rewrote the acceptance criterion from "passes
  the shipped lint" — circular — to "every Mermaid block renders", with the lint
  named as partial evidence. Verified against mermaid 11.17.2 as oracle: 26/26
  agreement, **zero false positives**, all 6 offending lines caught, silent on
  the skill's own 11 template blocks; applying the suggested fixes to a copy of
  the failing tree made 14/14 blocks parse.
  Concept: `/skill-authoring/validating-generated-artifacts.md`.

- **Progressive disclosure starves cross-cutting rules** — found while fixing
  the above, and not reported by the expert review. Four phases write Mermaid
  (architecture, behavior, reference-analysis, operations-diagrams) but the
  syntax guidance sat in `playbook-diagrams.md`, which only the last of them
  loads; three phases never saw it, and the first real bug came from one of
  those three. `Load only <files>` is what keeps context lean and is exactly
  what hides a concern spanning phases. Extracted the rules into
  `references/mermaid-syntax.md` and added it to all four phase load lists.
  Also fixed the example that taught the mistake: templates used `actor` as a
  flowchart node id in one place and as a sequence keyword in another, while the
  playbook asked for several actors in one view — a node id cannot be reused, so
  the agent reached for the declaration form and produced a parse error.

- **Review round** on the Mermaid defect: one domain expert (Mermaid v11),
  scoped explicitly to Mermaid-related files at the user's instruction. The
  expert disclosed on its own that it had read a vendored `mermaid.min.js` from
  a sibling skill to use as a parser oracle, which exceeded the scope it was
  given — disclosed to the user rather than buried. Its diagnosis matched an
  independent parser run done here with the npm `mermaid` package; the
  cross-phase loading gap above was found outside the review and verified
  directly. Reinforces: give a scoped reviewer the scope in writing, and expect
  to verify its factual claims yourself.

- **codebase-analysis-report 1.1.0** — repaired an imported self-check that
  rejected the skill itself. The vendor-neutrality scanner (inherited from
  `aws-kiro-atx-lab` at import, repo v0.4.0) scanned this skill's own
  `SKILL.md`, whose `metadata.upstream` names the source repository as
  `CLAUDE.md` requires — so `aws`/`atx` matched the denylist and every render
  failed at the publication gate. Present since commit `dea8c66`; unnoticed
  because the imported test suite had never been run (it failed 31 of 94 for the
  same reason). Split the scan by blast radius — `scan_emitted_assets()` guards
  publication (only what reaches `index.html`), `scan_authored_docs()` runs in
  the suite — and exempted `metadata.upstream` in every YAML form while keeping
  `name`/`description` in scope. Removing the doc scan from the gate exposed two
  pre-existing holes in the surviving gate, both closed: chrome was matched
  against a narrower second denylist (bare provider tokens never checked against
  it) and extracted by a triple-quote regex (wording in ordinary literals
  escaped); chrome is now walked via AST against a single denylist. Also: gate
  messages now carry file, line, text, and skill root; the renderer retains and
  prints the unpublished temp directory on validation failure, which SKILL.md
  gate 5 had always instructed but a `finally: rmtree` made impossible; and a
  new `validate_report.py --self-check` runs both tiers with no fixture, so
  documentation edits are checkable in the authoring loop. Separately, the suite
  hardcoded `BR-007`/`TC-008`/`CMP-001`/`"AWS SDK"` while the skill promised
  "any completed v2 output tree is a valid fixture"; cases now synthesize the
  shape they need into the temp copy, preserving the renderer's cross-manifest
  invariants. Verified: 100 tests pass on four fixtures, including trees with no
  vulnerabilities, with no tests, and with no registries populated at all.
  Concept: `/skill-authoring/imported-self-checks.md`.

- **Review round** on the codebase-analysis-report neutrality fix, on a frozen
  working tree: three-domain expert review (prompt engineering, context
  engineering, business analysis — parallel subagents), following the 0.7.0
  precedent. Six findings overlapped across two or more reviewers and were
  applied. Two were raised by a single reviewer and applied only after
  independent verification by execution: the publication-gate holes (proved by
  planting a branded literal outside a triple-quoted string and observing the
  gate return no error) and the unfollowable temp-path instruction (proved by
  reading the `finally` block). One reviewer claim was checked and confirmed by
  running the exemption against folded, literal, and CRLF frontmatter forms —
  all three leaked before the fix. Reinforces the standing rule: overlapping
  findings are a truth signal, single-reviewer findings need verification
  against the files or a run before they are acted on.

- **Review round** on the creating-skills 1.2.0 prefix work, before its
  first commit: three-domain expert review (skill authoring, prompt
  engineering, context engineering — parallel subagents on a frozen
  draft), mirroring the 0.6.0 two-domain precedent. Overlapping findings
  treated as truth signal; single-reviewer findings verified against the
  files before applying; one prompt-engineering suggestion (reduce the
  checklist prefix item to a bare pointer) rejected 2:1 — both other
  reviewers wanted the checklist self-contained. Applied: the no-plugin
  branch is now executable (step 8 declares registration mandatory with
  the no-plugin branch as its one exception); the exact user-facing
  question is spelled out as a quotable block that explains the mechanism
  (the old "do you want prefixed invocation?" presupposed the
  plugin-name-is-the-prefix mechanism) and the **user** picks the plugin
  name (never derived silently from the repo name); the import workflow is
  routed through the prefix gate ("steps 4-11" skipped step 1, and import
  step 1 *is* the copying); the SKILL.md section now links
  /skill-authoring/skill-prefixes.md as its canonical expansion (the flow
  lived in three places with no declared source of truth) and the concept
  points back for the normative question wording; the update workflow
  re-runs the checklist with trigger/anti-trigger tests whenever the
  description changed (it was the only path that never validated); the
  create workflow validates *before* version bookkeeping (a failed
  trigger test after the bump would force a second bump across all four
  repo-level fields); "Name it" and the checklist gained the
  installed-name uniqueness check CLAUDE.md mandates; `metadata.upstream`
  is recorded as one combined string (steps 4-5 wrote two values into one
  string-only key); and "Before you start" guards against the skill being
  loaded from the plugin cache with no clone on the machine. Description
  trigger words extended with "named, prefixed".
- **Creation** of /skill-authoring/skill-prefixes.md alongside
  **creating-skills 1.2.0** (repo v0.7.0): the skill-creation workflow now
  handles invocation prefixes explicitly for every new skill — a repo that
  already ships a plugin reuses it (registration in
  `.claude-plugin/plugin.json` makes the skill inherit
  `kengjudd:<skill-name>`), and a repo with no plugin packaging must ask the
  user "prefix or none?" *before* scaffolding, recording the answer in the
  knowledge base. The playbook records where a prefix can and cannot come
  from (the plugin name only; the skill's own `name` is spec-limited to
  `a-z0-9-`, and symlink/skills-dir installs have no prefix on any agent),
  how to choose a plugin name when creating one (it is the prefix users
  type, and need not match the repository name), and that renaming a plugin
  later is breaking (links /decisions/2026-08-30-plugin-name-kengjudd.md).
  The authoring checklist gained the matching prefix check, and
  /skill-authoring/best-practices.md §2 cross-links the playbook.
- **Creation** of /decisions/2026-08-30-plugin-name-kengjudd.md alongside the
  plugin rename in repo v0.7.0: the Claude Code plugin shipped from this repo
  was renamed `skills-kengjudd` → `kengjudd` (plugin.json `name` +
  marketplace `plugins[0].name`) so plugin-channel skills invoke with a short
  prefix — `kengjudd:git-commit` — mirroring obra/superpowers
  (`superpowers:<skill>`). Mechanism recorded with sources: the official docs
  state "Plugin skills are namespaced by the plugin name". Also recorded:
  what deliberately did not change (GitHub repo name, clone URLs, marketplace
  name `kengjudd`, and the symlink channel, where personal skills have no
  prefix on any agent — platform behavior, since the Agent Skills spec allows
  only `a-z0-9-` in a skill's own name), and the one-time migration for
  pre-rename installs (uninstall old id, then qualified install of
  `kengjudd@kengjudd`, which refreshes the marketplace by itself).
  /specs/claude-code-plugins.md gained the namespaced-by-plugin-name rule
  with the superpowers sources, and the `kengjudd@kengjudd` command was
  swept through /skill-authoring/update-mechanism.md,
  /skill-authoring/best-practices.md, and the live-guidance passages of
  /decisions/2026-08-29-repo-design.md (its two plugin-channel command
  references state current mechanics, not 2026-08-29 history, so binding
  rule 7 applies).
- **Creation** of /skill-authoring/command-to-skill.md alongside the
  promotion of the `/commit` slash command (`~/.claude/commands/commit.md`)
  into the `git-commit` skill (repo v0.6.0). Recorded: a command's
  `description` is help text for humans while a skill's description is the
  model-matched trigger; `!`-injected command context must become an explicit
  survey step the agent runs; `allowed-tools` permission syntax carries over
  verbatim; and both the scope widening (staged-only → whole working tree)
  and deleting the source command afterwards are owner decisions to ask
  about, not defaults. This was also the first skill authored through
  two-domain expert review (git expert + senior developer subagents on a
  frozen draft; 20 findings applied in a single pass; overlapping findings
  from the independent reviewers treated as a truth signal, single-reviewer
  claims verified against real git behaviour before applying).

## 2026-08-29

- **Update** of /skill-authoring/importing-skills.md alongside the import of
  `doc2markdown` (repo v0.5.0), renamed on import from the machine-local
  `~/.claude/skills/doc-to-markdown` (deferred-inventory row U1). Two new cases
  recorded: sources with no git history (record the local path and say so —
  never invent a commit or version for `metadata.upstream`) and rename on
  import (frontmatter `name` must match the new directory, sweep the skill's
  files for the old name, and warn that the original stays installed and
  competes on description-match). Import-status table: 4 of 23 imported.
- **Extension** of `doc2markdown` in the same v0.5.0 release: the import
  landed at 1.0.0 (the source has PDF/DOCX/XLSX only), then PPTX support was
  added in the working tree before the first commit — new
  `scripts/extract_pptx.py`, pptx fidelity rules (slide headings, speaker
  notes, page furniture), pptx manifest summary keys
  (`slides_needing_ocr`, `slides_with_overlay_text`, `slides_render_unavailable`,
  …), and the Thai "แปลงสไลด์"/"พาวเวอร์พอยต์" trigger words, taking the
  skill to 1.1.0. Recorded here because the changelog entry alone would hide
  that the PPTX half of this skill is new work in this repo, not part of the
  imported source.
- **Creation** of /skill-authoring/importing-skills.md alongside the first skill
  import (repo v0.4.0): `business-rules-extraction`,
  `comprehensive-codebase-analysis`, and `codebase-analysis-report` imported from
  `gitkeng/aws-kiro-atx-lab` (`.kiro/skills/`). Records what an import actually
  requires — `metadata.upstream` provenance including a dirty source working
  tree, renumbering to 1.0.0 with the upstream number preserved only in
  metadata, the two-channel `## Updating` section, re-anchoring skill-relative
  script paths that symlink installs break, replacing Kiro-specific README
  install instructions, and keeping a bundled LICENSE that a `license:` field
  refers to. Also documents the hard v2-output data contract that makes
  `codebase-analysis-report` and `comprehensive-codebase-analysis` a pair, and
  carries an import-status table for the deferred inventory in
  /decisions/2026-08-29-repo-design.md (3 of 23 imported; the other 20 rows
  stand).
- **Update** from the final review round (repo v0.3.0), per binding rule 7:
  brought /skill-authoring/update-mechanism.md, /skill-authoring/best-practices.md
  and /decisions/2026-08-29-repo-design.md back in line with the revised
  CLAUDE.md — two-channel `## Updating` contract, unconditional lockstep bump of
  the four repo-level version fields via the new `scripts/bump-version.sh`, the
  five `install.sh` user-scope targets, and corrected `--force` / unknown-tool
  script behaviour. Removed hardcoded OKF version strings so the version lives
  only in `knowledge/index.md` and /specs/okf-spec.md. Reframed the evals
  section as upstream guidance that this repo does not require, rather than an
  implied convention it does not have.
- **Update** from the expert review of `CLAUDE.md`/`AGENTS.md` (repo v0.2.0):
  documented ZCode (Z.ai) in /agents/skill-discovery-matrix.md and
  /specs/agents-md-standard.md — it reads AGENTS.md and *only* AGENTS.md, never
  `CLAUDE.md` at runtime, which makes this repo's adapter pointer load-bearing
  rather than merely acceptable; recorded its skill-discovery roots
  (`~/.zcode/skills` primary, `~/.agents/skills` secondary) and frontmatter
  limits; added `zcode` to the documented `install.sh --tool` mapping.
  Corrected the opencode claim in both /agents/skill-discovery-matrix.md and
  /specs/agent-skills-spec.md: it recognizes five of the six spec frontmatter
  fields, silently ignoring `allowed-tools`.
- **Update** after adversarial verification against live sources: corrected the
  status of anthropics/claude-code#6235 (closed "completed" 2026-08-17, docs
  still show no native AGENTS.md support) and #50778 (closed 2026-04-19, docs
  still list no `.agents/skills` path) in /specs/agents-md-standard.md and
  /decisions/2026-08-29-repo-design.md; replaced the dead Zed rules URL with
  zed.dev/docs/ai/instructions; annotated the private ACT repo source with its
  local-clone verification path; added the missing opencode source to
  /specs/agent-skills-spec.md.
- **Creation** of the knowledge bundle (OKF 0.2) during repository initialization:
  spec summaries (agent-skills, agents-md, okf, claude-code-plugins), agent skill
  discovery matrix, skill-authoring playbooks, and the founding design decision
  record. All content researched from primary sources on this date.
