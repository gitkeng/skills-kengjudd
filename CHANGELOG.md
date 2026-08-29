# Changelog

All notable changes to this repository are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

Per-skill versions live in each skill's `SKILL.md` under `metadata.version`.
When a skill changes, bump both the skill's `metadata.version` and this repo's `VERSION`,
and record the change here under the skill's name.

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
