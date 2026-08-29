# Changelog

All notable changes to this repository are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [SemVer](https://semver.org/).

Per-skill versions live in each skill's `SKILL.md` under `metadata.version`.
When a skill changes, bump both the skill's `metadata.version` and this repo's `VERSION`,
and record the change here under the skill's name.

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
