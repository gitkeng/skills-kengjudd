---
type: Reference
title: Skill discovery matrix
description: >
  Where each supported AI coding agent (Claude Code, Codex, Cursor, opencode,
  Gemini CLI, Zed, Kiro, Kimi CLI, Amp, Goose, ZCode) discovers Agent Skills,
  per scope, plus the universal path conventions and how this repo's
  scripts/install.sh maps --tool values to target directories.
tags:
  - agent-skills
  - discovery-paths
  - install
  - claude-code
  - codex
  - cursor
  - opencode
  - gemini-cli
  - zed
  - kiro
  - kimi-cli
  - amp
  - goose
  - zcode
sources:
  - resource: https://agentskills.io
    title: Agent Skills Overview (open standard)
  - resource: https://agentskills.io/specification
    title: Agent Skills Specification
  - resource: https://code.claude.com/docs/en/skills
    title: "Claude Code: Extend Claude with skills"
  - resource: https://developers.openai.com/codex/skills/
    title: OpenAI Codex Skills docs
  - resource: https://cursor.com/docs/context/skills
    title: Cursor Skills docs
  - resource: https://opencode.ai/docs/skills/
    title: opencode Skills docs
  - resource: https://geminicli.com/docs/cli/skills/
    title: Gemini CLI Skills docs
  - resource: https://ampcode.com/news/agent-skills
    title: "Amp: Agent Skills announcement"
  - resource: https://kiro.dev/docs/skills/
    title: Kiro Skills docs
  - resource: https://goose-docs.ai/docs/guides/context-engineering/using-skills/
    title: "Goose: Using Skills (mirror of official docs)"
  - resource: https://zed.dev/docs/ai/skills
    title: "Zed: Agent Skills docs"
  - resource: https://github.com/zed-industries/zed/tree/main/crates/agent_skills
    title: Zed agent_skills crate (discovery implementation)
  - resource: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
    title: "Kimi Code CLI: Agent Skills docs"
  - resource: https://github.com/MoonshotAI/kimi-cli/blob/main/AGENTS.md
    title: MoonshotAI kimi-cli AGENTS.md (skill registration)
  - resource: https://zcode.z.ai/en/docs
    title: "ZCode (Z.ai): Agentic Development Environment overview"
  - resource: https://zcode.z.ai/en/docs/skill
    title: "ZCode: Skills docs (discovery roots, frontmatter limits)"
  - resource: https://zcode.z.ai/en/docs/agents
    title: "ZCode: AGENTS.md docs (CLAUDE.md not read at runtime)"
  - resource: file:///Applications/ZCode.app/Contents/Resources/glm/zcode.cjs
    title: ZCode 3.9.2 bundled agent engine (local, inspected)
  - resource: file:///Users/keng/.zcode/
    title: Local ZCode user config dir (v2/setting.json, skills root)
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:45:34Z
status: stable
---

# Skill discovery matrix

Per-agent discovery paths for Agent Skills (the SKILL.md format — see
[/specs/agent-skills-spec.md](/specs/agent-skills-spec.md)). The spec itself
defines only the skill **directory format**, not discovery locations; every
path below is agent-specific behavior documented by that agent. This matrix is
the authority behind `scripts/install.sh` — the script's `--tool` mapping
(documented below) must stay in sync with this file.

In every path, a skill lives at `<dir>/<skill-name>/SKILL.md`.

## Per-agent discovery

### Claude Code

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.claude/skills/` — loaded from cwd and every parent up to repo root; nested `.claude/skills` in subdirs load lazily when Claude touches files there (namespaced `subdir:skill`); also `.claude/skills/` of any `--add-dir` directory | `~/.claude/skills/` (personal); `~/.claude/skills/synced/` for claude.ai-synced skills (via `CLAUDE_CODE_SYNC_SKILLS=1` in a `-p` run); enterprise via managed settings dir (e.g. `/etc/claude-code/.claude/skills/` on Linux); plugins at `<plugin>/skills/<name>/` | Automatic by description match, or explicit `/skill-name`. For personal/project skills the **directory name** (not frontmatter `name`) is the command; plugin skills are `/plugin-name:skill-name` | Symlinked skill dirs are followed. Precedence: enterprise > personal > project; skills override same-name `.claude/commands` files. Supports many extension frontmatter fields beyond the six-spec set — those are forbidden in this repo's portable skills (CLAUDE.md rule 6). Plugin packaging: see [/specs/claude-code-plugins.md](/specs/claude-code-plugins.md) |

### OpenAI Codex

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `$CWD/.agents/skills/`, then parent dirs' `.agents/skills/` up to `$REPO_ROOT/.agents/skills/` | `~/.agents/skills/` (user); `/etc/codex/skills/` (admin); plus bundled system skills | `$skill-name` or `/skills` in CLI/IDE; `@skill-name` in ChatGPT; implicit matching on description | Follows symlinks. Priority order: CWD → parents → user → admin → bundled. Optional `agents/openai.yaml` adds UI/invocation metadata (`allow_implicit_invocation`); disable per-skill in `~/.codex/config.toml` `[[skills.config]]` blocks |

### Cursor

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.cursor/skills/` and `.agents/skills/`; legacy compat `.claude/skills/` and `.codex/skills/` | `~/.cursor/skills/` and `~/.agents/skills/`; legacy compat `~/.claude/skills/` and `~/.codex/skills/` | Automatic model invocation (opt out per skill with `disable-model-invocation` frontmatter) | Supports frontmatter `name`, `description`, `paths` (globs), `disable-model-invocation`, `icon`, `color`, `metadata`. Cloud/remote agents get only project-level skills |

### opencode

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.opencode/skills/`, `.claude/skills/`, `.agents/skills/` — walking up to the git worktree root | `~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.agents/skills/` | Loaded via a native skill tool | Recognizes only **five** of the six spec frontmatter fields — `name`, `description`, `license`, `compatibility`, `metadata`. `allowed-tools` is **not** documented as recognized, and the docs state unknown frontmatter fields are silently ignored. Per-skill permissions (allow/deny/ask) configurable in `opencode.json` |

### Gemini CLI

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| Workspace: `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` | Via an `activate_skill` tool with user confirmation; managed with `/skills list\|link\|enable\|disable\|reload` and `gemini skills install <git-url> --consent` | Precedence (lowest → highest): built-in < extension skills < user < workspace; within a tier the `.agents` alias wins |

### Zed

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.agents/skills/` | `~/.agents/skills/` | Slash-command invocation; built-in `/create-skill` skill | Native Agent Skills since ~Jan 2026 (replaced the Rules Library). Discovery is exactly one level deep (`<root>/<skill-name>/SKILL.md`, no recursion/nesting). Deliberately does **not** scan other tools' paths — symlink into `~/.agents/skills/` instead (symlinks supported). Live-reloads on file changes; project skills load only from trusted worktrees |

### Kiro

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.kiro/skills/` (workspace) | `~/.kiro/skills/` | Loaded by the agent; custom agents must list `skill://.kiro/skills/*/SKILL.md` in their `resources` field | Exactly two discovery locations — no `.agents/skills` or `.claude/skills` compat. Workspace wins on name conflict. Spec-compliant frontmatter (name must match folder, max 64 chars; description max 1024) |

### Kimi CLI (Kimi Code)

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.agents/skills/` | `$KIMI_CODE_HOME/skills/` (default `~/.kimi-code/skills/`); `~/.config/agents/skills/` | `/skill:<name>` | Layered priority: Project > User > Extra > Built-in. Both `name` and `description` are mandatory in directory-form SKILL.md (parse fails otherwise). Adds nonstandard "flow skills" (`type: flow` frontmatter with embedded Mermaid/D2 workflows, invoked `/flow:<name>`) |

### Amp

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.agents/skills/` (default install target); compat `.claude/skills/` | `~/.config/agents/skills/` and `~/.config/amp/skills/`; compat `~/.claude/skills/` | Install via `amp skill add owner/repo`; explicit invocation syntax not documented in verified sources | Precedence: project overrides user overrides built-in. Exact frontmatter field support unconfirmed (see Known gaps) |

### Goose

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.goose/skills/`, `.agents/skills/` (recommended), `.claude/skills/` | `~/.config/goose/skills/`, `~/.agents/skills/`, `~/.claude/skills/` | `/skills` session command; `goose skills list` CLI | Skills platform extension enabled by default |

### ZCode (Z.ai)

| Project-scope path(s) | User-scope path(s) | Invocation style | Notes |
|---|---|---|---|
| `.zcode/skills/` then `.agents/skills/` — searched from cwd up to the git worktree root, **deeper directories win**; plus enabled plugin roots | `~/.zcode/skills/` (primary), then `~/.agents/skills/` (secondary); explicitly configured roots outrank both | `$<skill-name>` in the composer, plus model-driven auto-invocation | Not a PATH binary and not Zed: ZCode is Z.ai (Zhipu AI)'s Electron **Agentic Development Environment** for the GLM family (`/Applications/ZCode.app`, bundle id `dev.zcode.app`, v3.9.2), with a bundled agent engine at `Contents/Resources/glm/zcode.cjs`. Full root precedence: configured roots > `~/.zcode/skills` > `~/.agents/skills` > workspace `.zcode/skills` > workspace `.agents/skills` > plugin roots; within a level `.zcode` is scanned before `.agents`. **Skill identity is the file path**, so same-named skills at different roots are all discovered but only the first loads — the rest are silently shadowed. Discovery is exactly one level deep (`<root>/<name>/SKILL.md`); dot-directories (except `.system`) and `node_modules` are skipped; **symlinks are followed** (the loader treats `isDirectory() \|\| isSymbolicLink()` as a directory), so this repo's symlink install works unchanged. Frontmatter: `name` and `description` both mandatory (missing either drops the skill), `description` over 1024 chars drops the skill, ~250 chars of it get injected into context, and the body is truncated at 100 KB. Disable a single skill by absolute path with `enable: false` in `~/.zcode/cli/config.json` or workspace `.zcode/config.json`. **Instruction file is `AGENTS.md` and only `AGENTS.md`** — the engine's candidate filename list is the single-element `["AGENTS.md"]`: user default `~/.zcode/AGENTS.md` is injected first, then a workspace `<repo>/AGENTS.md` found from cwd upward overrides it (hidden alternates `<repo>/.zcode/AGENTS.md` and `<repo>/.agents/AGENTS.md`). `CLAUDE.md` is **never read at runtime**; Z.ai docs describe it only as a one-time onboarding migration source |

## Universal conventions

- **De facto cross-agent convention:** `.agents/skills/` at project level;
  `~/.agents/skills/` or `~/.config/agents/skills/` at user level. There is
  **no single normative user-scope path** — the Agent Skills spec defines only
  the skill directory format, not discovery locations, and agents split
  between the two user-level variants:
  - `~/.agents/skills/`: Codex, Cursor, opencode, Gemini CLI, Zed, Goose, and
    ZCode — though for ZCode it is only the **secondary** root; its primary
    user root is `~/.zcode/skills/`, which outranks it.
  - `~/.config/agents/skills/`: Amp, Kimi CLI.
- **`.claude/skills/` compat** is widespread (Cursor, opencode, Amp, Goose
  read it) but not universal (Zed, Kiro, and ZCode do not).
- **Outliers:** Kiro reads only its own `.kiro/skills` / `~/.kiro/skills`;
  Zed reads only the `.agents/skills` convention and expects symlinks for
  everything else; ZCode leads with its own `.zcode/skills` roots and only
  falls back to `.agents/skills`.
- **Instruction-file loading is not the same as skill discovery.** ZCode reads
  `AGENTS.md` and *only* `AGENTS.md` — `CLAUDE.md` is never read at runtime
  (Z.ai treats it purely as a one-time onboarding migration source). That is
  exactly why this repo's root `AGENTS.md` must point at `CLAUDE.md`: it is
  the only file an agent like ZCode will ever load.
- **Symlinks** are explicitly supported where documented (Claude Code, Codex,
  Zed, ZCode), which is why this repo installs by symlink.

## How this repo installs: `scripts/install.sh` mapping

`./scripts/install.sh --tool <tool> [--project <dir>] [--force]` symlinks
every `skills/<name>/` directory into the target dir(s). Accepted `--tool`
values are `claude`, `codex`, `cursor`, `opencode`, `gemini`, `zed`, `goose`,
`kimi`, `amp`, `kiro`, `zcode`, `all`. Default scope is user-level (`$HOME`);
`--project <dir>` switches to project scope. The exact `--tool` → target
mapping (mirrors `targets_for_tool()` in the script):

| `--tool` value | User-scope target (default) | Project-scope target (`--project <dir>`) |
|---|---|---|
| `claude` | `~/.claude/skills` | `<dir>/.claude/skills` |
| `codex`, `cursor`, `opencode`, `gemini`, `zed`, `goose` | `~/.agents/skills` | `<dir>/.agents/skills` |
| `kimi`, `amp` | `~/.config/agents/skills` | `<dir>/.agents/skills` |
| `kiro` | `~/.kiro/skills` | `<dir>/.kiro/skills` |
| `zcode` | `~/.zcode/skills` | `<dir>/.zcode/skills` |
| `all` | All five user dirs above, deduplicated | All project dirs above, deduplicated (`.claude/skills`, `.agents/skills`, `.kiro/skills`, `.zcode/skills` — the kimi/amp entry collapses into `.agents/skills`) |

Rationale for the collapsed mapping: agents that read `~/.agents/skills`
share one symlink farm; Kimi and Amp use `~/.config/agents/skills` at user
scope but the universal `.agents/skills` at project scope; Claude Code, Kiro,
and ZCode need their own dirs because they do not read the universal paths, or
do not read them first (Claude Code's canonical personal dir is
`~/.claude/skills`; Kiro reads nothing else; ZCode does read `~/.agents/skills`
as a fallback, but `~/.zcode/skills` is its highest-precedence non-configured
root, so installing there avoids being shadowed by a same-named skill).

Script behavior worth knowing:

- Idempotent: a link already pointing at this repo's skill is skipped.
- An existing file/dir/foreign link at the target is **not** replaced unless
  `--force` is passed (it prints `SKIP ... Use --force to replace.`).
- After linking, restart or reload the agent session — skills are discovered
  at startup (Zed being the live-reload exception).

## Known gaps

Recorded honestly per repo rule 1 (no guessing); resolve by fetching the
primary docs before relying on these points:

- **GitHub Copilot / VS Code**: listed as an adopter on agentskills.io, but
  its discovery paths were not verified (whether it uses `.github/skills` vs
  `.agents/skills` — `docs.github.com/en/copilot/concepts/agents/about-agent-skills`
  would settle it). It is therefore absent from the matrix and from
  `install.sh`.
- **Amp frontmatter support**: exact supported fields could not be confirmed
  from primary docs (`ampcode.com/manual` redirected; `ampcode.com/docs/skills`
  returned 404 at research time). Discovery paths above come from the
  official announcement (`ampcode.com/news/agent-skills`) plus secondary
  guides.
- **`allowed-tools` semantics**: the spec marks the field experimental
  ("support may vary between agent implementations"); whether it acts as a
  permission grant or a restriction is not standardized per agent. Confirmed
  data point: opencode does not document it at all and silently ignores it.
- **User-scope path convention**: no normative answer exists
  (`~/.agents/skills` vs `~/.config/agents/skills`); this repo handles the
  split via the `install.sh` mapping above.

## Related

- [/specs/agent-skills-spec.md](/specs/agent-skills-spec.md) — the SKILL.md
  format these paths discover
- [/specs/claude-code-plugins.md](/specs/claude-code-plugins.md) — the
  alternative plugin-marketplace install path for Claude Code
- [/skill-authoring/best-practices.md](/skill-authoring/best-practices.md) —
  writing skills that work across all the agents in this matrix
