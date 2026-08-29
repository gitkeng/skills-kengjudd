# skills-kengjudd — Agent Instructions

> **The canonical instruction set for this repository is [CLAUDE.md](CLAUDE.md).
> Read that file in full before doing anything else here.**

This project is Claude Code–first, so its rules live in `CLAUDE.md` as the
single source of truth. This file exists because the AGENTS.md standard has no
import syntax — so if you are Codex, Cursor, opencode, Gemini CLI, Zed, Kiro,
Kimi CLI, zcode, or any other agent reading this: open `CLAUDE.md` now and
treat its contents as if they were written in this file.

## Minimal orientation (details in CLAUDE.md)

- `skills/<name>/` — one Agent Skill per folder (agentskills.io format); every
  SKILL.md has a required `## Updating` section and `metadata.version`.
- `knowledge/` — OKF 0.2 knowledge bundle; every document needs `type:`
  frontmatter and `sources:` for external facts. Keep it disjoint from `skills/`.
- `scripts/install.sh --tool <agent>` links skills into your agent's discovery
  directory; `scripts/update.sh <skill-name>` updates one skill.

## Three invariants you must not break

1. No guessing — unsourced factual content is a defect; ask the user when
   research cannot settle a question.
2. Never mix `skills/` and `knowledge/` subtrees (their specs have conflicting
   frontmatter rules).
3. Any skill change requires: knowledge entry + `knowledge/log.md` +
   `CHANGELOG.md` + skill `metadata.version` bump + repo `VERSION` bump.

Everything else — structure, naming, OKF rules, versioning, install/update
commands — is specified in [CLAUDE.md](CLAUDE.md).
