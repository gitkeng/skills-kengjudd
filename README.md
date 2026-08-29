# skills-kengjudd

Private central repository of [Agent Skills](https://agentskills.io) usable
across multiple AI coding agents — Claude Code (primary), Codex, Cursor,
opencode, Gemini CLI, Zed, Kiro, Kimi CLI, and others — paired with a project
knowledge base in the [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) format.

- **Agents:** read [CLAUDE.md](CLAUDE.md) (canonical rules). [AGENTS.md](AGENTS.md) points there.
- **Humans:** this README.

## Layout

| Path | Purpose |
|---|---|
| `skills/<name>/` | One skill per folder (agentskills.io spec). Every skill has its own `## Updating` command and `metadata.version`. |
| `knowledge/` | OKF 0.2 knowledge bundle — specs, per-agent facts, authoring playbooks, decisions. |
| `scripts/` | `install.sh` (symlink into agent dirs), `update.sh` (per-skill updater), `check-spec-versions.sh` (OKF freshness). |
| `templates/skill-template/` | Scaffold for new skills. |
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
./scripts/install.sh --tool all       # all of the above

# Or per project:
./scripts/install.sh --tool claude --project /path/to/project
```

Claude Code alternative (plugin marketplace):

```
/plugin marketplace add gitkeng/skills-kengjudd
/plugin install skills-kengjudd@kengjudd
```

## Update

Each skill documents its own update command in its SKILL.md `## Updating`
section. All of them route through:

```bash
./scripts/update.sh <skill-name>   # one skill: fetch → compare version → show changes → pull
./scripts/update.sh --all          # every skill
```

## Creating a new skill

Invoke the `creating-skills` skill from any supported agent, or read
[skills/creating-skills/SKILL.md](skills/creating-skills/SKILL.md) — it covers
naming, frontmatter, structure, registration, knowledge capture, and versioning.

## Skills

| Skill | Version | Description |
|---|---|---|
| [creating-skills](skills/creating-skills/SKILL.md) | 1.0.0 | Meta-skill: create, update, and register skills in this repo. |
