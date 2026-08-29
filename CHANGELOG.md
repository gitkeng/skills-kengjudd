# Changelog

All notable changes to this repository are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

Per-skill versions live in each skill's `SKILL.md` under `metadata.version`.
When a skill changes, bump both the skill's `metadata.version` and this repo's `VERSION`,
and record the change here under the skill's name.

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
