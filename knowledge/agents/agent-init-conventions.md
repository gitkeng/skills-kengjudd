---
type: Reference
title: Per-agent init conventions (context files, init commands, config)
description: >
  For each of the 12 agents targeted by the init-project skill: which
  instruction/context files it reads (paths + precedence), import syntax,
  native init command, and config file locations. Feeds
  skills/init-project/references/agent-context-matrix.md.
tags: [agents, context-files, init, agents-md]
sources:
  - resource: https://code.claude.com/docs/en/memory
    title: "Claude Code docs — How Claude remembers your project (CLAUDE.md locations, @imports, /init, /import, auto memory)"
  - resource: https://code.claude.com/docs/en/settings
    title: "Claude Code docs — Settings (five settings scopes and their precedence)"
  - resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: "OpenAI Codex docs — AGENTS.md (global/project locations, override files, merge order, project_doc_max_bytes)"
  - resource: https://learn.chatgpt.com/docs/config-file/config-basic
    title: "OpenAI Codex docs — Config file basics (config.toml precedence, project/user/system scopes)"
  - resource: https://learn.chatgpt.com/docs/developer-commands
    title: "OpenAI Codex docs — Developer commands (built-in slash commands, incl. /init)"
  - resource: https://github.com/openai/codex/blob/main/codex-rs/tui/src/slash_command.rs
    title: "openai/codex — slash_command.rs (verbatim /init description)"
  - resource: https://github.com/openai/codex/issues/21932
    title: "openai/codex issue #21932 — Allow /init to update an existing AGENTS.md (open feature request)"
  - resource: https://cursor.com/docs/rules
    title: "Cursor docs — Rules (AGENTS.md nested support, .mdc project rules, @file references, /create-rule)"
  - resource: https://cursor.com/docs/cli/reference/configuration
    title: "Cursor docs — CLI configuration (cli-config.json, project .cursor/cli.json)"
  - resource: https://cursor.com/docs/cli/reference/slash-commands
    title: "Cursor docs — CLI slash commands (no /init)"
  - resource: https://cursor.com/docs/cli/mcp
    title: "Cursor docs — CLI MCP (.cursor/mcp.json, ~/.cursor/mcp.json)"
  - resource: https://opencode.ai/docs/rules/
    title: "opencode docs — Rules (AGENTS.md, CLAUDE.md fallback, instructions array, /init)"
  - resource: https://opencode.ai/docs/config/
    title: "opencode docs — Config (opencode.json locations, merge order, managed config)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md
    title: "gemini-cli docs — Context files (GEMINI.md hierarchy, context.fileName, @file.md imports)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/commands/initCommand.ts
    title: "gemini-cli source — initCommand.ts (verbatim /init description)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md
    title: "gemini-cli docs — Settings (user and workspace settings.json)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md
    title: "gemini-cli docs — Enterprise (system settings paths, four-file precedence)"
  - resource: https://zed.dev/docs/ai/instructions
    title: "Zed docs — Instructions (first-match-wins file list, ~/.config/zed/AGENTS.md)"
  - resource: https://zed.dev/docs/configuring-zed
    title: "Zed docs — Configuring Zed (settings.json locations, .zed/settings.json)"
  - resource: https://kiro.dev/docs/steering/
    title: "Kiro docs — Steering (.kiro/steering, inclusion modes, #[[file:...]], AGENTS.md support)"
  - resource: https://kiro.dev/docs/configuration/
    title: "Kiro docs — Configuration scopes (global/project paths, KIRO_HOME, precedence)"
  - resource: https://kiro.dev/docs/mcp/configuration/
    title: "Kiro docs — MCP configuration (mcp.json workspace and user paths)"
  - resource: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/reference/slash-commands.md
    title: "kimi-cli docs — Slash commands (verbatim /init description)"
  - resource: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/config-files.md
    title: "kimi-cli docs — Config files (~/.kimi/config.toml, --config-file, legacy JSON migration)"
  - resource: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/data-locations.md
    title: "kimi-cli docs — Data locations (~/.kimi tree, KIMI_SHARE_DIR)"
  - resource: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/agents.md
    title: "kimi-cli docs — Agents and subagents (${KIMI_AGENTS_MD} merge scope)"
  - resource: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html
    title: "Kimi Code CLI docs — Agent Skills ($KIMI_CODE_HOME, ~/.kimi-code, extra_skill_dirs)"
  - resource: https://ampcode.com/docs/customize/agents-md
    title: "Amp docs — AGENTS.md (search locations, AGENT.md/CLAUDE.md fallback, @-mentions, agents-md list)"
  - resource: https://ampcode.com/docs/cli/settings
    title: "Amp docs — CLI configuration (user/workspace/managed settings paths, precedence)"
  - resource: https://ampcode.com/docs/cli
    title: "Amp docs — CLI getting started (documented CLI surface; no init command)"
  - resource: https://github.com/block/goose/blob/main/documentation/docs/guides/context-engineering/using-goosehints.md
    title: "goose docs — Using goosehints (AGENTS.md + .goosehints defaults, CONTEXT_FILE_NAMES, global hints)"
  - resource: https://github.com/block/goose/blob/main/documentation/docs/guides/config-files.md
    title: "goose docs — Config files (config.yaml, permission.yaml, secrets.yaml paths)"
  - resource: https://github.com/block/goose/blob/main/documentation/docs/guides/goose-cli-commands.md
    title: "goose docs — CLI commands (full command and slash-command list; term init)"
  - resource: https://zcode.z.ai/en/docs/agents
    title: "ZCode docs — AGENTS.md (two sources only, no @import expansion, no child-dir scan)"
  - resource: https://zcode.z.ai/en/docs/commands
    title: "ZCode docs — Commands (/goal and /compact only; custom command paths)"
  - resource: https://zcode.z.ai/en/docs/configuration
    title: "ZCode docs — Configuration (~/.zcode/v2/config.json provider options)"
  - resource: https://zcode.z.ai/en/docs/mcp-services
    title: "ZCode docs — MCP servers (~/.zcode/cli/config.json, workspace .zcode/config.json, .agents/mcp.json fallback, enable:false)"
  - resource: https://antigravity.google/docs/rules-workflows/
    title: "Antigravity docs — Rules and Workflows (~/.gemini/GEMINI.md, .agents/rules, 12k char limit, @filename)"
  - resource: https://antigravity.google/docs/cli/gcli-migration/
    title: "Antigravity docs — Migration (GEMINI.md and AGENTS.md parsed in the active directory; config paths)"
  - resource: https://antigravity.google/changelog
    title: "Antigravity changelog — v2.11.0 (2026-08-26) @path inlining in AGENTS.md; v2.3.1 ~/.gemini/config/config.json"
  - resource: https://antigravity.google/docs/slash-commands/
    title: "Antigravity docs — Slash commands (built-in command list; no /init)"
  - resource: https://antigravity.google/docs/getting-started
    title: "Antigravity docs — Getting started (product description, docs navigation)"
generated:
  by: claude-code/claude-opus-5
  at: "2026-08-31T02:50:48Z"
status: stable
---

# Per-agent init conventions

What each of the 12 agents in the `init-project` v1 target list actually loads
at session start, how it merges those files, whether it can import other files,
whether it can generate its own context file, and where its configuration
lives. Every section answers the same four questions:

- **(a) Instruction/context files** — filenames, paths, precedence/merge model
- **(b) Import syntax** — yes/no, and the exact syntax
- **(c) Native init command** — a built-in command that writes the context file
- **(d) Config file locations** — where the agent's own settings live

Facts already recorded in this bundle are cited, not restated: see
[/specs/agents-md-standard.md](/specs/agents-md-standard.md) for the AGENTS.md
standard and per-tool context-file behavior, and
[/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md) for
skill discovery paths. Unresolved questions are in
[Known gaps](#known-gaps) — none of them are guessed.

All URL-backed facts below were verified **2026-08-31**.

## Claude Code

- **(a)** Reads `CLAUDE.md`, never `AGENTS.md`. Load order, broadest to most
  specific: managed policy
  (`/Library/Application Support/ClaudeCode/CLAUDE.md` on macOS,
  `/etc/claude-code/CLAUDE.md` on Linux/WSL,
  `C:\Program Files\ClaudeCode\CLAUDE.md` on Windows) → user
  `~/.claude/CLAUDE.md` → project `./CLAUDE.md` **or** `./.claude/CLAUDE.md` →
  local `./CLAUDE.local.md`. All discovered files are **concatenated**, not
  overridden, ordered filesystem-root-down; within a directory
  `CLAUDE.local.md` is appended after `CLAUDE.md`. Files in subdirectories load
  on demand when Claude reads files there. Additionally `.claude/rules/*.md`
  (project, recursive) and `~/.claude/rules/` (user) load at launch, or only
  for matching files when they carry `paths:` frontmatter globs.
- **(b)** **Yes** — `@path/to/import`. Relative paths resolve against the file
  containing the import; absolute paths allowed; recursive to a **maximum depth
  of four hops**; parsing skips code spans and fenced blocks; imported files
  are expanded at launch. This is the mechanism behind the official
  `CLAUDE.md` → `@AGENTS.md` adapter pattern.
- **(c)** **Yes** — `/init` generates a starting CLAUDE.md from codebase
  analysis; if a CLAUDE.md already exists it suggests improvements rather than
  overwriting. Plain `/init` also reads Cursor rules (`.cursor/rules/`,
  `.cursorrules`) and `.github/copilot-instructions.md`. With
  `CLAUDE_CODE_NEW_INIT=1` it becomes an interactive multi-phase flow and also
  reads `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/` or `.windsurfrules`,
  and `.clinerules`. Separately, `/import` (v2.1.213+) appends a one-time copy
  of a supported agent's instruction file into the matching CLAUDE.md.
- **(d)** Settings precedence, highest first: managed
  (`managed-settings.json`, MDM, or the claude.ai console) → `claude --settings`
  → `.claude/settings.local.json` → `.claude/settings.json` →
  `~/.claude/settings.json`. Auto memory lives at
  `~/.claude/projects/<project>/memory/` (relocatable with
  `autoMemoryDirectory`).
- Sources: [memory docs](https://code.claude.com/docs/en/memory),
  [settings docs](https://code.claude.com/docs/en/settings);
  background in [/specs/agents-md-standard.md](/specs/agents-md-standard.md).

## Codex

- **(a)** Reads `AGENTS.md`. The global/project override chain, the root-down
  concatenation order, and the `project_doc_max_bytes` /
  `project_doc_fallback_filenames` settings are already recorded in the Codex
  row of [/specs/agents-md-standard.md](/specs/agents-md-standard.md#which-tools-read-agentsmd-natively)
  — not restated here. Two details that row does not cover: **discovery stops
  at the current directory** (subdirectories below it are never scanned), and
  Codex **skips empty files and stops adding files** once the combined size
  reaches the limit, so a truncated tail is silent.
- **(b)** **No** — no `@import`/include mechanism is documented for Codex
  instruction files.
- **(c)** **Yes** — `/init`, described verbatim in the CLI source as
  "create an AGENTS.md file with instructions for Codex". Open feature request
  openai/codex#21932 asks for it to also update an existing AGENTS.md.
- **(d)** `config.toml`, precedence highest first: CLI flags and `--config`
  overrides → project `.codex/config.toml` (git root down to cwd, trusted
  projects only) → profile files `~/.codex/<profile>.config.toml` → user
  `~/.codex/config.toml` → system `/etc/codex/config.toml` (Unix) → built-in
  defaults. Managed machines may add an organization `requirements.toml`.
  `CODEX_HOME` relocates the `~/.codex` directory.
- Sources: [/specs/agents-md-standard.md](/specs/agents-md-standard.md) for (a);
  [AGENTS.md docs](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
  [config basics](https://learn.chatgpt.com/docs/config-file/config-basic),
  [developer commands](https://learn.chatgpt.com/docs/developer-commands),
  [slash_command.rs](https://github.com/openai/codex/blob/main/codex-rs/tui/src/slash_command.rs),
  [issue #21932](https://github.com/openai/codex/issues/21932).

## Cursor

- **(a)** Reads `AGENTS.md` at the project root and in subdirectories, nearest
  winning — see the Cursor row of
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md#which-tools-read-agentsmd-natively),
  which also covers the coexisting `.cursor/rules/*.mdc` format. New here: those
  `.mdc` project rules take frontmatter keys `alwaysApply`, `description`,
  `globs`; **User Rules and Team Rules are configured through the Cursor UI and
  dashboard, not repo files**, so an init flow cannot write them; and the
  documented application order is **Team Rules → Project Rules → User Rules**.
- **(b)** **Yes, inside rules** — "Use `@filename.ts` to include files in your
  rule's context." Whether the same expansion applies inside `AGENTS.md` is not
  documented (see Known gaps).
- **(c)** **No `/init`.** The documented generator is `/create-rule` in Agent
  chat, which writes a rule file with proper frontmatter into `.cursor/rules`.
  The Cursor CLI slash-command reference lists no `/init` and no AGENTS.md
  generator.
- **(d)** CLI settings `~/.cursor/cli-config.json` (global; only permissions can
  be set per project, at `<project>/.cursor/cli.json`). MCP servers at
  `.cursor/mcp.json` (project) and `~/.cursor/mcp.json` (global), with
  project → global → nested precedence. Rules at `.cursor/rules/`.
- Sources: [/specs/agents-md-standard.md](/specs/agents-md-standard.md) for (a);
  [Rules](https://cursor.com/docs/rules),
  [CLI configuration](https://cursor.com/docs/cli/reference/configuration),
  [CLI slash commands](https://cursor.com/docs/cli/reference/slash-commands),
  [CLI MCP](https://cursor.com/docs/cli/mcp).

## opencode

- **(a)** Reads `AGENTS.md` with a `CLAUDE.md` fallback, plus the global
  `~/.config/opencode/AGENTS.md` — see the opencode row of
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md#which-tools-read-agentsmd-natively).
  New here: the local lookup **walks up from the current directory** rather than
  checking only the project root, the search is **first-match-wins per level**,
  and there is a fourth step — `~/.claude/CLAUDE.md` as a Claude Code
  compatibility fallback, unless disabled.
- **(b)** **No** — "opencode doesn't automatically parse file references" in
  AGENTS.md. Additional files are pulled in through the `instructions` array in
  `opencode.json`, which accepts local paths, glob patterns, and remote URLs
  (5-second fetch timeout).
- **(c)** **Yes** — `/init` generates or updates `AGENTS.md` by scanning the
  repository and asking targeted questions.
- **(d)** Config files are **merged**, not replaced, in this order (lowest to
  highest): remote `.well-known/opencode` → global
  `~/.config/opencode/opencode.json` → custom path from `OPENCODE_CONFIG` →
  project `opencode.json` → `.opencode/` directories → inline
  `OPENCODE_CONFIG_CONTENT` → managed files
  (`/Library/Application Support/opencode/` macOS, `/etc/opencode/` Linux,
  `%ProgramData%\opencode` Windows) → macOS managed preferences (highest,
  non-overridable). `.jsonc` is accepted everywhere `.json` is.
- Sources: [/specs/agents-md-standard.md](/specs/agents-md-standard.md) for (a);
  [Rules](https://opencode.ai/docs/rules/),
  [Config](https://opencode.ai/docs/config/).

## Gemini CLI

- **(a)** Default context filename is `GEMINI.md`; the `context.fileName`
  setting takes a list and **can include `AGENTS.md`** (documented example:
  `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`). **Name change, reconciled
  2026-08-31:** the older flat `contextFileName` (recorded on 2026-08-29 from
  the docs site) has been replaced by this nested name in
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md); the change
  matches Gemini CLI's move to a nested `settings.json` structure, though no
  official changelog entry names the rename (see Known gaps). Hierarchy: global
  `~/.gemini/GEMINI.md`, then configured workspace directories and their
  parents, plus just-in-time scanning — when a tool touches a file or
  directory, the CLI scans that directory and its ancestors. All found files
  are **concatenated** and sent with every prompt. Gemini CLI does not read
  AGENTS.md by default (see [/specs/agents-md-standard.md](/specs/agents-md-standard.md)).
- **(b)** **Yes** — `@file.md`, supporting relative (`@./components/x.md`) and
  absolute paths.
- **(c)** **Yes** — `/init`, described verbatim in the source as "Analyzes the
  project and creates a tailored GEMINI.md file"; it writes an empty
  `GEMINI.md` in the target directory and then populates it from project
  analysis. `/memory show` and `/memory reload` inspect and re-scan context
  files.
- **(d)** Four `settings.json` files, precedence lowest to highest: system
  defaults (`system-defaults.json`) → user `~/.gemini/settings.json` →
  workspace `<project>/.gemini/settings.json` → system overrides
  (`/etc/gemini-cli/settings.json` Linux,
  `C:\ProgramData\gemini-cli\settings.json` Windows,
  `/Library/Application Support/GeminiCli/settings.json` macOS) — the system
  overrides file has the final say. `GEMINI_CLI_SYSTEM_SETTINGS_PATH` overrides
  the system path; `GEMINI_CLI_HOME` relocates the `.gemini` directory. Arrays
  and objects merge rather than replace.
- Sources: [context files](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md),
  [initCommand.ts](https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/commands/initCommand.ts),
  [settings](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md),
  [enterprise](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md).

## Zed

- **(a)** Project instructions use a **first-match-wins** list whose exact
  order — and the shadowing hazard where a stray `.cursorrules` hides
  `AGENTS.md` — is already recorded in the Zed row of
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md#which-tools-read-agentsmd-natively).
  New here: Zed also has a **personal** instruction file at
  `~/.config/zed/AGENTS.md` (`%APPDATA%\Zed\AGENTS.md` on Windows) applying
  across all projects, and **project instructions override personal
  instructions when they conflict**.
- **(b)** **No** — no file-reference or import mechanism is documented for
  instruction files.
- **(c)** **None documented.** The instructions docs tell the user to create or
  edit the file manually; no generator command appears in them.
- **(d)** User settings `~/.config/zed/settings.json` (macOS and Linux),
  `%APPDATA%\Zed\settings.json` (Windows); project settings
  `.zed/settings.json`; key bindings in `keymap.json`.
- Sources: [/specs/agents-md-standard.md](/specs/agents-md-standard.md) for the
  (a) filename list; [Instructions](https://zed.dev/docs/ai/instructions),
  [Configuring Zed](https://zed.dev/docs/configuring-zed).

## Kiro

- **(a)** Kiro's native mechanism is **steering files**: workspace
  `.kiro/steering/*.md` and global `~/.kiro/steering/`. Three foundation files
  (`product.md`, `tech.md`, `structure.md`) are included in every interaction
  by default. Inclusion is controlled by YAML frontmatter — `inclusion: always`,
  `inclusion: fileMatch` with `fileMatchPattern`, `inclusion: manual` (invoked
  as `#steering-file-name`), or `inclusion: auto` with `name`/`description`.
  **`AGENTS.md` is supported** as a steering directive source: same markdown,
  but it does **not** support inclusion modes and is **always included**; place
  it in `~/.kiro/steering/` or the workspace root, with discovery in
  subdirectories. Two caveats: custom agents do **not** auto-include steering —
  they must list `file://.kiro/steering/**/*.md` in their `resources` field —
  and Kiro CLI does not support inclusion modes, loading everything in
  `.kiro/steering/`. Steering and skills **merge** across scopes rather than
  replacing.
- **(b)** **Yes** — `#[[file:relative/path/to/file.ext]]` embeds a live
  workspace file inside a steering document (e.g. `#[[file:api/openapi.yaml]]`).
- **(c)** **No slash command.** The IDE has a **Generate Steering Docs** button
  (Steering section) that creates the three foundation files in
  `.kiro/steering/`.
- **(d)** Global scope under `~/.kiro/`: `settings/mcp.json`,
  `settings/permissions.yaml`, `settings/cli.json`, `agents/`, `steering/`,
  `skills/`, `hooks/`, `powers/`. Project scope under `.kiro/`:
  `settings/mcp.json`, `agents/`, `steering/`, `skills/`, `hooks/`, `specs/`.
  Precedence is **Agent > Project > Global** (permissions are the exception:
  deny wins at any scope). `KIRO_HOME` redirects the global `~/.kiro`
  directory. Discovery paths for skills: see
  [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md).
- Sources: [Steering](https://kiro.dev/docs/steering/),
  [Configuration scopes](https://kiro.dev/docs/configuration/),
  [MCP configuration](https://kiro.dev/docs/mcp/configuration/).

## Kimi CLI

- **(a)** Reads `AGENTS.md`. The agent template variable `${KIMI_AGENTS_MD}` is
  documented as "Merged `AGENTS.md` content from project root to working
  directory (including `.kimi/AGENTS.md`)" — so the merge spans project root
  down to cwd and includes a `.kimi/AGENTS.md`. Cross-tool AGENTS.md discovery
  beyond that is covered in
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md).
- **(b)** **Not documented** — no `@file`/import expansion for AGENTS.md
  appears in the official docs (see Known gaps).
- **(c)** **Yes** — `/init`, verbatim: "Analyze the current project and
  generate an `AGENTS.md` file." It runs a temporary sub-session to examine the
  codebase and write the file; the getting-started guide frames it as the fix
  for a project that has no AGENTS.md yet.
- **(d)** `~/.kimi/config.toml` is the main configuration file, auto-created on
  first run; a legacy `~/.kimi/config.json` is migrated to TOML with a
  `config.json.bak` backup. Overrides: `--config-file <path>` and inline
  `--config '<json>'`. Runtime data lives under `~/.kimi/` (`kimi.json`,
  `mcp.json`, `credentials/`, `sessions/`, `plans/`, `user-history/`, `logs/`);
  `KIMI_SHARE_DIR` relocates that runtime data but explicitly **not** the Agent
  Skills search paths. The Kimi Code build documents a separate home,
  `$KIMI_CODE_HOME` (default `~/.kimi-code/`), for skills roots plus
  `extra_skill_dirs` in `config.toml` — see Known gaps for the two path
  families.
- Sources: [slash commands](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/reference/slash-commands.md),
  [config files](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/config-files.md),
  [data locations](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/data-locations.md),
  [agents](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/agents.md),
  [Kimi Code skills](https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html).

## Amp

- **(a)** Reads `AGENTS.md` from the widest set of locations of any agent here:
  the current working directory (or editor workspace roots) **and parent
  directories up to `$HOME`**; subtree `AGENTS.md` files, included when the
  agent accesses files in those directories; user config
  `$HOME/.config/amp/AGENTS.md` and `$HOME/.config/AGENTS.md`; and system-wide
  `/etc/ampcode/AGENTS.md`, `/Library/Application Support/ampcode/AGENTS.md`,
  `%ProgramData%\ampcode\AGENTS.md`. Fallback, verbatim: "If no `AGENTS.md`
  exists in a directory, but a file named `AGENT.md` (without an `S`) or
  `CLAUDE.md` does exist, that file will be included."
- **(b)** **Yes** — `@`-mentions inside AGENTS.md support relative paths,
  absolute paths, `@~/some/path`, and globs such as `@doc/*.md`; `@`-mentions
  inside code blocks are ignored.
- **(c)** **None documented.** `agents-md list` in the command palette shows
  which AGENTS.md files Amp is currently using, but no command generates one.
- **(d)** User settings `~/.config/amp/settings.json` or `.jsonc`
  (`%USERPROFILE%\.config\amp\...` on Windows); workspace
  `.amp/settings.json`/`.jsonc`, resolved to the nearest match searching upward
  to the repository root; `--settings-file <path>` for a custom file;
  enterprise managed settings at
  `/Library/Application Support/ampcode/managed-settings.json` (macOS),
  `/etc/ampcode/managed-settings.json` (Linux),
  `%ProgramData%\ampcode\managed-settings.json` (Windows). **Workspace settings
  override user settings**; all keys use the `amp.` prefix.
- Sources: [AGENTS.md](https://ampcode.com/docs/customize/agents-md),
  [CLI configuration](https://ampcode.com/docs/cli/settings),
  [CLI docs](https://ampcode.com/docs/cli).

## Goose

- **(a)** Default context filenames are **both** `AGENTS.md` and `.goosehints`:
  "By default, goose looks for both `AGENTS.md` and `.goosehints` at each
  level." Files load from the working directory **up to the repository root**,
  and goose additionally discovers hint files in nested subdirectories when it
  works there. Global hints live at `~/.config/goose/.goosehints` and apply to
  every session; when global and local conflict, **local wins**. The filename
  list is configurable with the `CONTEXT_FILE_NAMES` environment variable, a
  JSON array whose default is `["AGENTS.md", ".goosehints"]` (documented
  examples reuse other tools' files, e.g.
  `["CLAUDE.md", ".goosehints", "project_rules.txt"]`).
- **(b)** **No** — no import expansion. The docs' guidance is to reference other
  files by path (e.g. `/docs/style.md`) so goose reads them with its own tools.
- **(c)** **None.** The CLI command list contains no context-file generator;
  the similarly named `goose term init <SHELL>` only prints a shell integration
  script.
- **(d)** macOS/Linux: `~/.config/goose/config.yaml` (provider, model,
  extensions, general settings), `permission.yaml`, `secrets.yaml`,
  `permissions/tool_permissions.json`, `prompts/`. Windows: the same tree under
  `%APPDATA%\Block\goose\config\`.
- Sources: [using goosehints](https://github.com/block/goose/blob/main/documentation/docs/guides/context-engineering/using-goosehints.md),
  [config files](https://github.com/block/goose/blob/main/documentation/docs/guides/config-files.md),
  [CLI commands](https://github.com/block/goose/blob/main/documentation/docs/guides/goose-cli-commands.md).

## ZCode

- **(a)** `AGENTS.md` and only `AGENTS.md`, from exactly two sources: the user
  global `~/.zcode/AGENTS.md` and the current workspace `AGENTS.md`. Verbatim:
  "When both sources exist, ZCode appends the user global instructions first,
  then the workspace instructions." The docs are equally explicit about what it
  does not do: "It does not merge multiple `AGENTS.md` files across directory
  levels. It also does not scan child directories, expand `@import` /
  `@include`, or choose rule files automatically by task type." `CLAUDE.md` is
  a **one-time onboarding migration source only**, never read at runtime —
  engine-level confirmation and the hidden workspace alternates
  (`.zcode/AGENTS.md`, `.agents/AGENTS.md`) are recorded in
  [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md).
- **(b)** **No** — `@import`/`@include` expansion is explicitly not performed.
  This makes ZCode the load-bearing case for a canonical AGENTS.md carrying its
  own content (rationale in [/specs/agents-md-standard.md](/specs/agents-md-standard.md)).
- **(c)** **None.** ZCode Agent ships two built-in slash commands, `/goal` and
  `/compact`; there is no `/init` and no documented AGENTS.md generator.
- **(d)** Two distinct user-scope files, not one: `~/.zcode/v2/config.json`
  holds model/provider connection settings (a provider's `options` recognizes
  only `apiKey`, `baseURL`, `apiKeyRequired`, `headers`), while
  `~/.zcode/cli/config.json` is the user-scope file for the `mcp.servers` key —
  the same file this bundle already recorded for per-skill `enable: false`.
  Workspace equivalent: `<project root>/.zcode/config.json`. Custom commands are
  `.md` files under `~/.zcode/commands` (user) or the project directory
  (workspace). `.agents/mcp.json` (standard `mcpServers` shape) is a **fallback
  only**: "as long as any MCP server is read from a `.zcode` config file, the
  `.agents/mcp.json` in the same scope is skipped entirely" — no merging.
  Disabling a server writes `"enable": false` into its config object; absent the
  field, a server counts as enabled.
- Sources: [AGENTS.md](https://zcode.z.ai/en/docs/agents),
  [Commands](https://zcode.z.ai/en/docs/commands),
  [Configuration](https://zcode.z.ai/en/docs/configuration),
  [MCP servers](https://zcode.z.ai/en/docs/mcp-services).

## Antigravity

Google's agentic IDE ("an AI agent platform that operates within defined
projects to access folders and repositories"; agents work in local mode or in
isolated git worktrees). It ships both an IDE surface and a TUI, the
Antigravity CLI.

- **(a)** Workspace context: the agent "continues to parse and enforce rule
  constraints defined inside your active directory's `GEMINI.md` and
  `AGENTS.md` files" — so **both** filenames are read. Global context: "The
  agent automatically consults and enforces your global constraints located at
  `~/.gemini/GEMINI.md`." Separately, Antigravity's own **Rules** are markdown
  files under the workspace `.agents/rules` folder (with backward compatibility
  for `.agent/rules`), capped at **12,000 characters each**, with four
  activation modes: Manual (`@`-mention), Always On, Model Decision (chosen from
  a natural-language description), and Glob (file patterns such as
  `src/**/*.ts`). Workflows are the same format, invoked as `/workflow-name`,
  with the same 12,000-character limit. Precedence between AGENTS.md and
  GEMINI.md is not documented (see Known gaps).
- **(b)** **Yes** — `@path/to/file` references and inlines external files
  "within `AGENTS.md` and custom rule files" (changelog v2.11.0, 2026-08-26).
  A relative path resolves against the location of the rules file; an absolute
  form such as `@/path/to/file.md` resolves to `/path/to/file.md` first and
  falls back to `workspace/path/to/file.md`.
- **(c)** **None.** The documented built-in slash commands are
  `/teamwork-preview`, `/goal`, `/plan`, `/grill-me`, `/learn`, `/schedule`,
  `/browser`, `/btw` (plus CLI-side `/agents`, `/codesearch`, `/credits`,
  `/diff`, `/permissions`, `/resume`, `/statusline`, `/title`, `/usage`,
  `/voice`) — no `/init` or context-file generator. The closest mechanism is
  `/learn`, which "distills session feedback and corrections into persistent
  Rules or Skills". Onboarding offers a one-time import of existing Gemini CLI
  extensions, skills, and settings.
- **(d)** `~/.gemini/config/` holds `config.json` (a malformed one blocked
  startup in the v2.3.1 fix). Global MCP servers at
  `~/.gemini/config/mcp_config.json`; workspace MCP at `.agents/mcp_config.json`.
  Global custom agents at `~/.gemini/config/agents/<agent_name>/agent.md`;
  workspace agents at `.agents/agents/<name>.md` or
  `.agents/agents/<name>/agent.md`. Workspace skills at `.agents/skills/`
  (backward compat `.agent/skills/`); global CLI skills at
  `~/.gemini/antigravity-cli/skills/`. Since v2.11.0 Antigravity also discovers
  custom skills, agents, and rules declared in `skills.json`, `agents.json`, and
  `rules.json` files inside project subdirectories. `~/.gemini/settings.json` is
  named as legacy Gemini CLI configuration.
- Sources: [Rules and Workflows](https://antigravity.google/docs/rules-workflows/),
  [Migration](https://antigravity.google/docs/cli/gcli-migration/),
  [Changelog](https://antigravity.google/changelog),
  [Slash commands](https://antigravity.google/docs/slash-commands/),
  [Getting started](https://antigravity.google/docs/getting-started).

## Cross-cutting summary

For the `init-project` skill, the operative question is how a canonical
`AGENTS.md` reaches each agent. Three classes emerge:

| Agent | Reads AGENTS.md natively | Import syntax | Native init command |
|---|---|---|---|
| Claude Code | No (`CLAUDE.md`) | `@path` (4 hops) | `/init`, `/import` |
| Codex | Yes | No | `/init` |
| Cursor | Yes | `@filename` in rules | `/create-rule` only |
| opencode | Yes (`CLAUDE.md` fallback) | No (`instructions` array) | `/init` |
| Gemini CLI | Only via `context.fileName` | `@file.md` | `/init` (writes GEMINI.md) |
| Zed | Yes (first-match-wins list) | No | None |
| Kiro | Yes (always-included steering) | `#[[file:...]]` in steering | IDE button only |
| Kimi CLI | Yes | Not documented | `/init` |
| Amp | Yes (+ `AGENT.md`/`CLAUDE.md` fallback) | `@path`, `@~/…`, globs | None |
| Goose | Yes (with `.goosehints`) | No | None |
| ZCode | Yes (only AGENTS.md) | No (explicitly) | None |
| Antigravity | Yes (with `GEMINI.md`) | `@path/to/file` | None |

Two consequences worth carrying into the skill:

- **Only Claude Code and Gemini CLI need an import adapter** (`CLAUDE.md` with
  `@AGENTS.md`; `GEMINI.md` with `@AGENTS.md`) — every other agent here reads
  `AGENTS.md` itself, in some form. Gemini CLI is the borderline case: it reads
  `AGENTS.md` only if `context.fileName` is configured to include it, so the
  adapter is the zero-configuration path.
- **The canonical file must be self-contained.** ZCode, Codex, opencode, Zed,
  and Goose expand no imports at all, so an `AGENTS.md` that delegates its
  substance to `@`-referenced files loses that substance on five of twelve
  agents. Imports are an adapter mechanism, not a content-organization one.

## Known gaps

Recorded per CLAUDE.md rule 1 — these are unresolved from official sources as
of 2026-08-31, not assumptions:

- **Antigravity, AGENTS.md vs GEMINI.md precedence.** The migration docs say
  both are parsed in the active directory and that `~/.gemini/GEMINI.md`
  supplies global constraints, but no official page states which wins on
  conflict, or how workspace files combine with `.agents/rules`. The
  `rules-workflows` page does not mention `AGENTS.md` at all.
- **Antigravity, when AGENTS.md support landed.** The changelog entry that
  names `AGENTS.md` is v2.11.0 (2026-08-26), and it describes `@path` inlining
  *within* AGENTS.md rather than the introduction of AGENTS.md reading. No
  official entry establishes the version at which Antigravity began reading
  AGENTS.md. (Third-party guides give a version number; not usable per rule 1.)
- **Antigravity, whether nested/parent AGENTS.md files are discovered.** The
  docs say "your active directory's" files — neither an upward walk nor a
  subtree scan is documented.
- **Gemini CLI, when `contextFileName` became `context.fileName`.** Both this
  document and [/specs/agents-md-standard.md](/specs/agents-md-standard.md) now
  record the nested `context.fileName`, verified against
  `docs/cli/gemini-md.md` on 2026-08-31 (the bundle-internal conflict with the
  flat `contextFileName`, recorded 2026-08-29, was resolved on 2026-08-31). The
  most likely explanation is the documented migration of `settings.json` to a
  nested structure, but no official changelog entry naming the rename was
  found, so neither the old name's removal nor a compatibility alias is
  confirmed — a config written against the flat key may or may not still work.
- **Cursor, `@filename` inside AGENTS.md.** The `@filename.ts` include is
  documented for `.mdc` rules; whether Cursor expands it inside `AGENTS.md` is
  not stated.
- **Kimi CLI, import syntax.** No `@file`/include mechanism for AGENTS.md
  appears in the official docs. Absence of documentation, not documented
  absence.
- **Kimi CLI, two config homes.** The `MoonshotAI/kimi-cli` docs put
  configuration and runtime data in `~/.kimi/` (`config.toml`), while the
  kimi.com Kimi Code docs use `$KIMI_CODE_HOME`, default `~/.kimi-code/`, for
  skill roots. Which applies depends on the build (Kimi Code CLI is documented
  as evolving into Kimi Code), and no single official page reconciles the two.
- **ZCode, the split between its two user-scope config files.** Official docs
  use `~/.zcode/v2/config.json` for provider/model connection settings and
  `~/.zcode/cli/config.json` for `mcp.servers`; this bundle separately recorded
  `~/.zcode/cli/config.json` for per-skill `enable: false` from local engine
  inspection ([/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md)).
  No page states the general rule for which keys belong in which file, so
  neither is safe to treat as "the" ZCode config.
- **Goose, ordering between `AGENTS.md` and `.goosehints` at the same level.**
  Both are loaded at each level and local beats global, but the docs do not say
  which of the two filenames wins if they contradict each other in one
  directory.
- **Zed and Amp, absence of a generator command.** Neither vendor documents a
  command that writes an instructions file, and neither states that none
  exists. These are "not documented" rather than "confirmed absent" — the same
  caveat applies to Antigravity's `/init` and to Cursor's AGENTS.md generation.

## Related documents

- [/specs/agents-md-standard.md](/specs/agents-md-standard.md) — the AGENTS.md
  standard, per-tool context-file behavior, and why Claude Code needs an
  import adapter
- [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md) —
  where the same agents discover Agent Skills
- [/specs/agent-skills-spec.md](/specs/agent-skills-spec.md) — the SKILL.md
  format
