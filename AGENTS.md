# skills-kengjudd — Agent Instructions

> **The canonical instruction set for this repository is [CLAUDE.md](CLAUDE.md).
> Read that file in full before doing anything else here.**

This project is Claude Code–first, so its rules live in `CLAUDE.md` as the
single source of truth. This file exists because the AGENTS.md standard has no
import syntax — so if you are zcode, Codex, Cursor, opencode, Zed, Kiro,
Kimi CLI, Amp, Goose, or any other agent reading this: open `CLAUDE.md` now and
treat its contents as if they were written in this file. (Gemini CLI reads
neither file by default — it is routed through `GEMINI.md`.)

**zcode (ZCode, Z.ai's GLM agent) reads only `AGENTS.md` — it never loads
`CLAUDE.md` at runtime.** For zcode this pointer is not a convenience, it is
the entire mechanism: open `CLAUDE.md` and read it in full before acting.
zcode also injects `~/.zcode/AGENTS.md` before this file, so anything here
overrides your personal defaults for this repo.

## Minimal orientation (details in CLAUDE.md)

- `skills/<name>/` — one Agent Skill per folder (agentskills.io format); every
  SKILL.md has a required `## Updating` section and `metadata.version`.
- `knowledge/` — OKF 0.2 knowledge bundle; every document needs `type:`
  frontmatter and `sources:` for external facts. Keep it disjoint from `skills/`.
- `scripts/install.sh --tool <agent>` links skills into your agent's discovery
  directory. Accepted values: `claude|codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|zcode|all`.
  If your agent is not listed, symlink `skills/<name>/` into its own discovery
  directory manually (`.agents/skills/` is the de facto convention).
- `scripts/update.sh <skill-name>` updates one skill (git-clone installs only;
  Claude Code plugin installs use `claude plugin update skills-kengjudd@kengjudd`).

## Four invariants you must not break

1. No guessing — unsourced factual content is a defect; ask the user when
   research cannot settle a question.
2. Never mix `skills/` and `knowledge/` subtrees (their specs have conflicting
   frontmatter rules).
3. Any skill change requires: knowledge entry + `knowledge/log.md` +
   `CHANGELOG.md` + skill `metadata.version` bump + repo `VERSION` bump +
   `.claude-plugin/` `version` bumps.
4. SKILL.md frontmatter uses ONLY the six agentskills.io spec fields (`name`,
   `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) —
   any other key breaks skill packaging outright.

Everything else — structure, naming, OKF rules, versioning, install/update
commands — is specified in [CLAUDE.md](CLAUDE.md).
