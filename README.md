# skills-kengjudd

Private central repository of [Agent Skills](https://agentskills.io) usable
across multiple AI coding agents — Claude Code (primary), ZCode (Z.ai), Codex,
Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose — paired with a
project knowledge base in the [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) format.

- **Agents:** read [CLAUDE.md](CLAUDE.md) (canonical rules).
  [AGENTS.md](AGENTS.md) and [GEMINI.md](GEMINI.md) point there.
- **Humans:** this README.

## Layout

| Path | Purpose |
|---|---|
| `skills/<name>/` | One skill per folder (agentskills.io spec). Every skill has its own `## Updating` command and `metadata.version`. |
| `knowledge/` | OKF 0.2 knowledge bundle — specs, per-agent facts, authoring playbooks, decisions. |
| `scripts/` | `install.sh` (symlink into agent dirs), `update.sh` (per-skill updater), `check-spec-versions.sh` (OKF freshness). |
| `templates/skill-template/` | Scaffold for new skills. |
| `docs/` | Human design/spec documents. Not an OKF bundle and not a substitute for a `knowledge/` concept. |
| `.claude-plugin/` | Claude Code plugin + marketplace packaging. |

## Install

```bash
git clone git@github.com:gitkeng/skills-kengjudd.git
cd skills-kengjudd

# Link every skill into an agent's skill directory (user scope):
./scripts/install.sh --tool claude    # ~/.claude/skills
./scripts/install.sh --tool codex     # ~/.agents/skills (also cursor|opencode|gemini|zed|goose)
./scripts/install.sh --tool kimi      # ~/.config/agents/skills (also amp)
./scripts/install.sh --tool kiro      # ~/.kiro/skills
./scripts/install.sh --tool zcode     # ~/.zcode/skills
./scripts/install.sh --tool all       # all of the above

# Or per project:
./scripts/install.sh --tool claude --project /path/to/project
```

Claude Code alternative (plugin marketplace):

```text
/plugin marketplace add gitkeng/skills-kengjudd
/plugin install skills-kengjudd@kengjudd
```

Because the repo is private, the marketplace add needs working git auth. The
`owner/repo` shorthand clones over SSH by default; for HTTPS-only setups set
`CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` or add it by SSH URL
(`/plugin marketplace add git@github.com:gitkeng/skills-kengjudd.git`).

## Update

Each skill documents its own update command in its SKILL.md `## Updating`
section, for both install channels:

```bash
# git clone + symlink installs
./scripts/update.sh <skill-name>   # one skill: fetch → compare version → show changes → pull
./scripts/update.sh --all          # every skill
```

```bash
# Claude Code plugin installs (the plugin cache has no .git)
claude plugin update skills-kengjudd@kengjudd
```

## Creating a new skill

Invoke the `creating-skills` skill from any supported agent, or read
[skills/creating-skills/SKILL.md](skills/creating-skills/SKILL.md) — it covers
naming, frontmatter, structure, registration, knowledge capture, and versioning.

## Skills

| Skill | Version | Description |
|---|---|---|
| [creating-skills](skills/creating-skills/SKILL.md) | 1.0.0 | Meta-skill: create, update, and register skills in this repo. |
