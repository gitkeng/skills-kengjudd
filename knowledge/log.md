# Knowledge Base Log

## 2026-08-30

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
