# Agent context matrix

This file is consulted by `init-project` Phase 4 (generate per-agent context
files) to decide, for each agent the user selected, how a canonical
`AGENTS.md` reaches that agent: read directly (`native`), pulled in through
the agent's own import mechanism (`import-adapter`), or copied wholesale
because the agent has neither (`full-copy`). It travels with this skill
(including into a bare symlink install), so every fact below is restated with
its own external source and verification date rather than pointing at this
repository's private knowledge base.

Twelve agents are covered: Claude Code, Codex, Cursor, opencode, Gemini CLI,
Zed, Kiro, Kimi CLI, Amp, Goose, ZCode, Antigravity. For any other agent,
research it live from its official documentation before deciding the adapter
rule — mirror this file's six fields (context file(s) & precedence, import
syntax, adapter rule, native init command, config locations, sources with
verified date) and use the `## Fallback rule` decision procedure at the end
of this file.

## Contents

- [Claude Code](#claude-code)
- [Codex](#codex)
- [Cursor](#cursor)
- [opencode](#opencode)
- [Gemini CLI](#gemini-cli)
- [Zed](#zed)
- [Kiro](#kiro)
- [Kimi CLI](#kimi-cli)
- [Amp](#amp)
- [Goose](#goose)
- [ZCode](#zcode)
- [Antigravity](#antigravity)
- [Fallback rule](#fallback-rule)

## Claude Code

- **Context file(s) & precedence:** `CLAUDE.md`, never `AGENTS.md`. Broadest
  to most specific: managed policy
  (`/Library/Application Support/ClaudeCode/CLAUDE.md` macOS,
  `/etc/claude-code/CLAUDE.md` Linux/WSL,
  `C:\Program Files\ClaudeCode\CLAUDE.md` Windows) → user
  `~/.claude/CLAUDE.md` → project `./CLAUDE.md` **or** `./.claude/CLAUDE.md`
  → local `./CLAUDE.local.md`. All discovered files are **concatenated**
  (not overridden), broad to specific; within a directory `CLAUDE.local.md`
  is appended after `CLAUDE.md`. Subdirectory files load on demand when
  Claude reads files there. `.claude/rules/*.md` (project, recursive) and
  `~/.claude/rules/` (user) load at launch, or only for matching files when
  they carry `paths:` frontmatter globs.
- **Import syntax:** Yes — `@path/to/import`. Relative paths resolve against
  the file containing the import; absolute paths allowed; recursive to a
  maximum depth of 4 hops; parsing skips code spans and fenced blocks;
  imported files expand at launch.
- **Adapter rule:** `import-adapter` — the canonical `AGENTS.md` reaches
  Claude Code through a `CLAUDE.md` containing `@AGENTS.md` (the official
  interop pattern; Claude-specific additions can follow below the import).
- **Native init command:** Yes — `/init` generates a starting CLAUDE.md from
  codebase analysis (suggests improvements instead of overwriting if one
  already exists) and also reads Cursor rules (`.cursor/rules/`,
  `.cursorrules`) and `.github/copilot-instructions.md`. With
  `CLAUDE_CODE_NEW_INIT=1` it becomes an interactive multi-phase flow that
  additionally reads `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/` or
  `.windsurfrules`, and `.clinerules`. Separately, `/import` (v2.1.213+)
  appends a one-time copy of a supported agent's instruction file into the
  matching CLAUDE.md.
- **Config locations:** Settings precedence, highest first: managed
  (`managed-settings.json`, MDM, or the claude.ai console) →
  `claude --settings` → `.claude/settings.local.json` →
  `.claude/settings.json` → `~/.claude/settings.json`. Auto memory lives at
  `~/.claude/projects/<project>/memory/` (relocatable via
  `autoMemoryDirectory`).

Sources:
- Claude Code docs — Memory: https://code.claude.com/docs/en/memory (verified 2026-08-31)
- Claude Code docs — Settings: https://code.claude.com/docs/en/settings (verified 2026-08-31)
- Claude Code docs — Memory (AGENTS.md non-support statement, "Claude Code reads CLAUDE.md, not AGENTS.md"): https://code.claude.com/docs/en/memory (re-verified 2026-08-29)

## Codex

- **Context file(s) & precedence:** `AGENTS.md`. Global scope:
  `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`; then per-directory
  `AGENTS.override.md`/`AGENTS.md` from the git root down to the current
  directory, **concatenated root-down with closer files later (overriding)**.
  Discovery **stops at the current directory** — subdirectories below it are
  never scanned. Capped at `project_doc_max_bytes` (32 KiB default); Codex
  **skips empty files and stops adding files once the combined size reaches
  the limit**, so a truncated tail is silent. Fallback filenames are
  configurable via `project_doc_fallback_filenames` in `~/.codex/config.toml`.
- **Import syntax:** No — no `@import`/include mechanism is documented for
  Codex instruction files.
- **Adapter rule:** `native` — Codex reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** Yes — `/init`, described verbatim in the CLI
  source as "create an AGENTS.md file with instructions for Codex." Open
  feature request `openai/codex#21932` asks for `/init` to also update an
  existing AGENTS.md — not shipped as of the verification date below.
- **Config locations:** `config.toml`, precedence highest first: CLI flags
  and `--config` overrides → project `.codex/config.toml` (git root down to
  cwd, trusted projects only) → profile files
  `~/.codex/<profile>.config.toml` → user `~/.codex/config.toml` → system
  `/etc/codex/config.toml` (Unix) → built-in defaults. Managed machines may
  add an organization `requirements.toml`. `CODEX_HOME` relocates the
  `~/.codex` directory.

Sources:
- OpenAI Codex docs — AGENTS.md: https://learn.chatgpt.com/docs/agent-configuration/agents-md (verified 2026-08-29; discovery-stops-at-cwd and silent-truncation details verified 2026-08-31)
- OpenAI Codex docs — Config file basics: https://learn.chatgpt.com/docs/config-file/config-basic (verified 2026-08-31)
- OpenAI Codex docs — Developer commands: https://learn.chatgpt.com/docs/developer-commands (verified 2026-08-31)
- openai/codex — slash_command.rs (verbatim `/init` description): https://github.com/openai/codex/blob/main/codex-rs/tui/src/slash_command.rs (verified 2026-08-31)
- openai/codex issue #21932: https://github.com/openai/codex/issues/21932 (verified 2026-08-31)

## Cursor

- **Context file(s) & precedence:** Reads `AGENTS.md` at the project root
  and in subdirectories; nested files are **combined, nearest wins**.
  `.cursor/rules/*.mdc` coexists for glob-scoped/manually-invoked rules,
  with frontmatter keys `alwaysApply`, `description`, `globs`. **User Rules
  and Team Rules are configured through the Cursor UI and dashboard, not
  repo files**, so an init flow cannot write them. Documented application
  order: **Team Rules → Project Rules → User Rules**.
- **Import syntax:** Yes, inside `.mdc` rules — "Use `@filename.ts` to
  include files in your rule's context." Whether the same expansion applies
  inside `AGENTS.md` itself is **not documented**.
- **Adapter rule:** `native` — Cursor reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** **No `/init`.** The documented generator is
  `/create-rule` in Agent chat, which writes a rule file with proper
  frontmatter into `.cursor/rules` — not an `AGENTS.md` generator. The
  Cursor CLI slash-command reference lists no `/init` and no AGENTS.md
  generator. This is "not documented," not confirmed absent.
- **Config locations:** CLI settings `~/.cursor/cli-config.json` (global;
  only permissions can be set per project, at `<project>/.cursor/cli.json`).
  MCP servers at `.cursor/mcp.json` (project) and `~/.cursor/mcp.json`
  (global), with project → global → nested precedence. Rules at
  `.cursor/rules/`.

Sources:
- Cursor docs — Rules: https://cursor.com/docs/rules (verified 2026-08-29 for AGENTS.md root/nested support; `.mdc` frontmatter keys, Team/Project/User order verified 2026-08-31)
- Cursor docs — CLI configuration: https://cursor.com/docs/cli/reference/configuration (verified 2026-08-31)
- Cursor docs — CLI slash commands: https://cursor.com/docs/cli/reference/slash-commands (verified 2026-08-31)
- Cursor docs — CLI MCP: https://cursor.com/docs/cli/mcp (verified 2026-08-31)

## opencode

- **Context file(s) & precedence:** Reads project `AGENTS.md`, falling back
  to `CLAUDE.md` for Claude Code compatibility, plus the global
  `~/.config/opencode/AGENTS.md`. The local lookup **walks up from the
  current directory** (not just the project root); the search is
  **first-match-wins per level**; there is a fourth step —
  `~/.claude/CLAUDE.md` as a Claude Code compatibility fallback, unless
  disabled.
- **Import syntax:** No — "opencode doesn't automatically parse file
  references" in `AGENTS.md`. Additional files are pulled in through the
  `instructions` array in `opencode.json`, which accepts local paths, glob
  patterns, and remote URLs (5-second fetch timeout).
- **Adapter rule:** `native` — opencode reads `AGENTS.md` directly; no
  adapter file is needed.
- **Native init command:** Yes — `/init` generates or updates `AGENTS.md`
  by scanning the repository and asking targeted questions.
- **Config locations:** Config files are **merged**, not replaced, lowest
  to highest: remote `.well-known/opencode` → global
  `~/.config/opencode/opencode.json` → custom path from `OPENCODE_CONFIG`
  → project `opencode.json` → `.opencode/` directories → inline
  `OPENCODE_CONFIG_CONTENT` → managed files
  (`/Library/Application Support/opencode/` macOS, `/etc/opencode/` Linux,
  `%ProgramData%\opencode` Windows) → macOS managed preferences (highest,
  non-overridable). `.jsonc` is accepted everywhere `.json` is.

Sources:
- opencode docs — Rules: https://opencode.ai/docs/rules/ (verified 2026-08-29 for AGENTS.md/CLAUDE.md fallback and no-auto-parse; upward-walk and first-match-wins detail verified 2026-08-31)
- opencode docs — Config: https://opencode.ai/docs/config/ (verified 2026-08-31)

## Gemini CLI

- **Context file(s) & precedence:** Default context filename is
  `GEMINI.md`; the `context.fileName` setting takes a list and **can
  include `AGENTS.md`** (documented example:
  `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`). Gemini CLI does **not** read
  `AGENTS.md` by default, and the request to make that the default was
  closed as not planned (issue #12345, cited below) — so treat the
  `GEMINI.md` adapter, not a default-`AGENTS.md` change, as the supported
  path. Hierarchy: global `~/.gemini/GEMINI.md`, then
  configured workspace directories and their parents, plus just-in-time
  scanning — when a tool touches a file or directory, the CLI scans that
  directory and its ancestors. All found files are **concatenated** and
  sent with every prompt.
- **Import syntax:** Yes — `@file.md`, supporting relative
  (`@./components/x.md`) and absolute paths.
- **Adapter rule:** `import-adapter` — the canonical `AGENTS.md` reaches
  Gemini CLI through a `GEMINI.md` containing `@AGENTS.md`. This is the
  zero-configuration path; the alternative of setting `context.fileName` to
  include `AGENTS.md` also works but requires per-project configuration.
- **Native init command:** Yes — `/init`, described verbatim in the source
  as "Analyzes the project and creates a tailored GEMINI.md file"; it
  writes an empty `GEMINI.md` in the target directory and then populates it
  from project analysis (writes `GEMINI.md`, not `AGENTS.md`). `/memory
  show` and `/memory reload` inspect and re-scan context files.
- **Config locations:** Four `settings.json` files, precedence lowest to
  highest: system defaults (`system-defaults.json`) → user
  `~/.gemini/settings.json` → workspace `<project>/.gemini/settings.json` →
  system overrides (`/etc/gemini-cli/settings.json` Linux,
  `C:\ProgramData\gemini-cli\settings.json` Windows,
  `/Library/Application Support/GeminiCli/settings.json` macOS) — the
  system overrides file has the final say. `GEMINI_CLI_SYSTEM_SETTINGS_PATH`
  overrides the system path; `GEMINI_CLI_HOME` relocates `.gemini`. Arrays
  and objects merge rather than replace.

Sources:
- gemini-cli docs — Context files: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md (verified 2026-08-31)
- gemini-cli source — initCommand.ts: https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/commands/initCommand.ts (verified 2026-08-31)
- gemini-cli docs — Settings: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md (verified 2026-08-31)
- gemini-cli docs — Enterprise: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md (verified 2026-08-31)
- google-gemini/gemini-cli issue #12345 ("AGENTS.md by default", closed not planned): https://github.com/google-gemini/gemini-cli/issues/12345 (verified 2026-08-29)

## Zed

- **Context file(s) & precedence:** Project instructions use a
  **first-match-wins** list: `.rules`, `.cursorrules`, `.windsurfrules`,
  `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`,
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` — a stray `.cursorrules` silently
  shadows `AGENTS.md`. Zed also has a **personal** instruction file at
  `~/.config/zed/AGENTS.md` (`%APPDATA%\Zed\AGENTS.md` on Windows) applying
  across all projects; **project instructions override personal
  instructions when they conflict**.
- **Import syntax:** No — no file-reference or import mechanism is
  documented for instruction files.
- **Adapter rule:** `native` — Zed reads `AGENTS.md` directly (as one entry
  in its first-match-wins list); no adapter file is needed. Caution: if a
  higher-priority file such as `.cursorrules` exists, it shadows
  `AGENTS.md` entirely rather than merging with it.
- **Native init command:** **None documented.** The instructions docs tell
  the user to create or edit the file manually; no generator command
  appears in them. This is "not documented," not confirmed absent.
- **Config locations:** User settings `~/.config/zed/settings.json` (macOS
  and Linux), `%APPDATA%\Zed\settings.json` (Windows); project settings
  `.zed/settings.json`; key bindings in `keymap.json`.

Sources:
- Zed docs — Instructions: https://zed.dev/docs/ai/instructions (verified 2026-08-29 for the first-match-wins list and shadowing hazard; personal-file/precedence detail verified 2026-08-31)
- Zed docs — Configuring Zed: https://zed.dev/docs/configuring-zed (verified 2026-08-31)

## Kiro

- **Context file(s) & precedence:** Kiro's native mechanism is **steering
  files**: workspace `.kiro/steering/*.md` and global `~/.kiro/steering/`.
  Three foundation files (`product.md`, `tech.md`, `structure.md`) are
  included in every interaction by default. Inclusion is controlled by YAML
  frontmatter — `inclusion: always`, `inclusion: fileMatch` with
  `fileMatchPattern`, `inclusion: manual` (invoked as
  `#steering-file-name`), or `inclusion: auto` with `name`/`description`.
  **`AGENTS.md` is supported** as a steering directive source: same
  markdown, but it does **not** support inclusion modes and is **always
  included**; place it in `~/.kiro/steering/` or the workspace root, with
  discovery in subdirectories. Custom agents do **not** auto-include
  steering — they must list `file://.kiro/steering/**/*.md` in their
  `resources` field. Kiro CLI does not support inclusion modes, loading
  everything in `.kiro/steering/`. Steering and skills **merge** across
  scopes rather than replacing; precedence is **Agent > Project > Global**.
- **Import syntax:** Yes — `#[[file:relative/path/to/file.ext]]` embeds a
  live workspace file inside a steering document (e.g.
  `#[[file:api/openapi.yaml]]`).
- **Adapter rule:** `native` — Kiro reads `AGENTS.md` directly as a
  steering source; no adapter file is needed.
- **Native init command:** **No slash command.** The IDE has a **Generate
  Steering Docs** button (Steering section) that creates the three
  foundation files in `.kiro/steering/` — it does not generate `AGENTS.md`
  itself.
- **Config locations:** Global scope under `~/.kiro/`:
  `settings/mcp.json`, `settings/permissions.yaml`, `settings/cli.json`,
  `agents/`, `steering/`, `skills/`, `hooks/`, `powers/`. Project scope
  under `.kiro/`: `settings/mcp.json`, `agents/`, `steering/`, `skills/`,
  `hooks/`, `specs/`. The **Agent > Project > Global** precedence recorded
  above has one exception: for permissions, a **deny wins at any scope**.
  `KIRO_HOME` redirects the global `~/.kiro` directory.

Sources:
- Kiro docs — Steering: https://kiro.dev/docs/steering/ (verified 2026-08-31)
- Kiro docs — Configuration scopes: https://kiro.dev/docs/configuration/ (verified 2026-08-31)
- Kiro docs — MCP configuration: https://kiro.dev/docs/mcp/configuration/ (verified 2026-08-31)

## Kimi CLI

- **Context file(s) & precedence:** Reads `AGENTS.md`. The agent template
  variable `${KIMI_AGENTS_MD}` is documented as "Merged `AGENTS.md` content
  from project root to working directory (including `.kimi/AGENTS.md`)" —
  the merge spans project root down to cwd and includes a
  `.kimi/AGENTS.md`.
- **Import syntax:** **Not documented** — no `@file`/import expansion for
  `AGENTS.md` appears in the official docs (absence of documentation, not
  documented absence).
- **Adapter rule:** `native` — Kimi CLI reads `AGENTS.md` directly; no
  adapter file is needed.
- **Native init command:** Yes — `/init`, verbatim: "Analyze the current
  project and generate an `AGENTS.md` file." It runs a temporary
  sub-session to examine the codebase and write the file.
- **Config locations:** **Two config homes exist across product
  generations, unreconciled by a single official page.** The
  `MoonshotAI/kimi-cli` docs put configuration and runtime data under
  `~/.kimi/`: `~/.kimi/config.toml` is the main configuration file
  (auto-created on first run; a legacy `~/.kimi/config.json` is migrated to
  TOML with a `config.json.bak` backup; overrides via `--config-file <path>`
  and inline `--config '<json>'`); runtime data at `~/.kimi/` (`kimi.json`,
  `mcp.json`, `credentials/`, `sessions/`, `plans/`, `user-history/`,
  `logs/`), relocatable via `KIMI_SHARE_DIR` (which explicitly does **not**
  move the Agent Skills search paths). Separately, the kimi.com **Kimi
  Code** docs use `$KIMI_CODE_HOME` (default `~/.kimi-code/`) for skill
  roots plus `extra_skill_dirs` in `config.toml`. Which home applies
  depends on the build (Kimi Code CLI is documented as evolving into Kimi
  Code); do not treat either as "the" Kimi CLI config location without
  checking the build in use.

Sources:
- kimi-cli docs — Slash commands: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/reference/slash-commands.md (verified 2026-08-31)
- kimi-cli docs — Config files: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/config-files.md (verified 2026-08-31)
- kimi-cli docs — Data locations: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/configuration/data-locations.md (verified 2026-08-31)
- kimi-cli docs — Agents and subagents: https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/customization/agents.md (verified 2026-08-31)
- Kimi Code CLI docs — Agent Skills: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/skills.html (verified 2026-08-31)

## Amp

- **Context file(s) & precedence:** Reads `AGENTS.md` from the widest set
  of locations recorded here: the current working directory (or editor
  workspace roots) **and parent directories up to `$HOME`**; subtree
  `AGENTS.md` files, included when the agent accesses files in those
  directories; user config `$HOME/.config/amp/AGENTS.md` and
  `$HOME/.config/AGENTS.md`; and system-wide `/etc/ampcode/AGENTS.md`,
  `/Library/Application Support/ampcode/AGENTS.md`,
  `%ProgramData%\ampcode\AGENTS.md`. Fallback, verbatim: "If no
  `AGENTS.md` exists in a directory, but a file named `AGENT.md` (without
  an `S`) or `CLAUDE.md` does exist, that file will be included."
- **Import syntax:** Yes — `@`-mentions inside `AGENTS.md` support relative
  paths, absolute paths, `@~/some/path`, and globs such as `@doc/*.md`;
  `@`-mentions inside code blocks are ignored.
- **Adapter rule:** `native` — Amp reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** **None documented.** `agents-md list` in the
  command palette shows which `AGENTS.md` files Amp is currently using, but
  no command generates one. This is "not documented," not confirmed
  absent.
- **Config locations:** User settings `~/.config/amp/settings.json` or
  `.jsonc` (`%USERPROFILE%\.config\amp\...` on Windows); workspace
  `.amp/settings.json`/`.jsonc`, resolved to the nearest match searching
  upward to the repository root; `--settings-file <path>` for a custom
  file; enterprise managed settings at
  `/Library/Application Support/ampcode/managed-settings.json` (macOS),
  `/etc/ampcode/managed-settings.json` (Linux),
  `%ProgramData%\ampcode\managed-settings.json` (Windows). **Workspace
  settings override user settings**; all keys use the `amp.` prefix.

Sources:
- Amp docs — AGENTS.md: https://ampcode.com/docs/customize/agents-md (verified 2026-08-31)
- Amp docs — CLI configuration: https://ampcode.com/docs/cli/settings (verified 2026-08-31)
- Amp docs — CLI getting started: https://ampcode.com/docs/cli (verified 2026-08-31)

## Goose

- **Context file(s) & precedence:** Default context filenames are **both**
  `AGENTS.md` and `.goosehints`: "By default, goose looks for both
  `AGENTS.md` and `.goosehints` at each level." Files load from the working
  directory **up to the repository root**, and goose additionally
  discovers hint files in nested subdirectories when it works there. Global
  hints live at `~/.config/goose/.goosehints` and apply to every session;
  when global and local conflict, **local wins**. The filename list is
  configurable with the `CONTEXT_FILE_NAMES` environment variable (a JSON
  array, default `["AGENTS.md", ".goosehints"]`). Ordering between
  `AGENTS.md` and `.goosehints` at the same level when they contradict each
  other is **not documented**.
- **Import syntax:** No — no import expansion. The docs' guidance is to
  reference other files by path (e.g. `/docs/style.md`) so goose reads them
  with its own tools.
- **Adapter rule:** `native` — Goose reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** **None.** The CLI command list contains no
  context-file generator; the similarly named `goose term init <SHELL>`
  only prints a shell integration script.
- **Config locations:** macOS/Linux: `~/.config/goose/config.yaml`
  (provider, model, extensions, general settings), `permission.yaml`,
  `secrets.yaml`, `permissions/tool_permissions.json`, `prompts/`. Windows:
  the same tree under `%APPDATA%\Block\goose\config\`.

Sources:
- goose docs — Using goosehints: https://github.com/block/goose/blob/main/documentation/docs/guides/context-engineering/using-goosehints.md (verified 2026-08-31)
- goose docs — Config files: https://github.com/block/goose/blob/main/documentation/docs/guides/config-files.md (verified 2026-08-31)
- goose docs — CLI commands: https://github.com/block/goose/blob/main/documentation/docs/guides/goose-cli-commands.md (verified 2026-08-31)

## ZCode

- **Context file(s) & precedence:** `AGENTS.md` and only `AGENTS.md`, from
  exactly two sources: the user global `~/.zcode/AGENTS.md` and the current
  workspace `AGENTS.md`. Verbatim: "When both sources exist, ZCode appends
  the user global instructions first, then the workspace instructions." It
  does **not** merge multiple `AGENTS.md` files across directory levels, does
  **not** scan child directories, and does **not** choose rule files
  automatically by task type. `CLAUDE.md` is a **one-time onboarding
  migration source only**, never read at runtime.
- **Import syntax:** No — `@import`/`@include` expansion is explicitly not
  performed. ZCode is the load-bearing case for a canonical `AGENTS.md`
  that carries its own content rather than delegating to imports, since it
  expands none.
- **Adapter rule:** `native` — ZCode reads `AGENTS.md` directly (the only
  file it reads by itself); no adapter file is needed, and none is possible
  since ZCode has no import mechanism to adapt through.
- **Native init command:** **None.** ZCode Agent ships two built-in slash
  commands, `/goal` and `/compact`; there is no `/init` and no documented
  `AGENTS.md` generator.
- **Config locations:** **Configuration is split across two user-scope
  files, and no official page states the general rule for which keys belong
  in which** — so neither is safe to treat as "the" ZCode config; check the
  key you need before writing. `~/.zcode/v2/config.json` holds
  model/provider connection settings, while `~/.zcode/cli/config.json`
  is the user-scope file for the `mcp.servers` key. Workspace equivalent:
  `<project root>/.zcode/config.json`. Custom commands are `.md` files under
  `~/.zcode/commands` (user) or the project directory (workspace).
  `.agents/mcp.json` (standard `mcpServers` shape) is a fallback only, used
  solely when no MCP server is configured in a `.zcode` config file at the
  same scope.

Sources:
- ZCode docs — AGENTS.md: https://zcode.z.ai/en/docs/agents (verified 2026-08-31)
- ZCode docs — Commands: https://zcode.z.ai/en/docs/commands (verified 2026-08-31)
- ZCode docs — Configuration: https://zcode.z.ai/en/docs/configuration (verified 2026-08-31)
- ZCode docs — MCP servers: https://zcode.z.ai/en/docs/mcp-services (verified 2026-08-31)

## Antigravity

Google's agentic IDE (an AI agent platform operating within defined
projects, with an IDE surface and a TUI, the Antigravity CLI).

- **Context file(s) & precedence:** Workspace context: the agent "continues
  to parse and enforce rule constraints defined inside your active
  directory's `GEMINI.md` and `AGENTS.md` files" — **both** filenames are
  read. Global context: "The agent automatically consults and enforces your
  global constraints located at `~/.gemini/GEMINI.md`." Separately,
  Antigravity's own **Rules** are markdown files under the workspace
  `.agents/rules` folder (backward-compatible with `.agent/rules`), capped
  at **12,000 characters each**, with four activation modes: Manual
  (`@`-mention), Always On, Model Decision, and Glob. Workflows use the same
  format, invoked as `/workflow-name`. **Precedence between `AGENTS.md` and
  `GEMINI.md` is not documented**, nor is whether nested/parent `AGENTS.md`
  files are discovered beyond "your active directory's" — neither an
  upward walk nor a subtree scan is stated. The official changelog entry
  naming `AGENTS.md` support is v2.11.0 (2026-08-26), describing `@path`
  inlining *within* `AGENTS.md`; no official entry establishes the version
  at which Antigravity began reading `AGENTS.md` at all.
- **Import syntax:** Yes — `@path/to/file` references and inlines external
  files "within `AGENTS.md` and custom rule files" (changelog v2.11.0,
  2026-08-26). A relative path resolves against the rules file's location;
  an absolute form such as `@/path/to/file.md` resolves to
  `/path/to/file.md` first and falls back to `workspace/path/to/file.md`.
- **Adapter rule:** `native` — Antigravity reads `AGENTS.md` directly in
  the active workspace directory (alongside `GEMINI.md`); no adapter file
  is needed. Caveat: because AGENTS.md-vs-GEMINI.md precedence is
  undocumented, do not assume which file wins if both exist and conflict.
- **Native init command:** **None.** Documented built-in slash commands are
  `/teamwork-preview`, `/goal`, `/plan`, `/grill-me`, `/learn`, `/schedule`,
  `/browser`, `/btw` (plus CLI-side `/agents`, `/codesearch`, `/credits`,
  `/diff`, `/permissions`, `/resume`, `/statusline`, `/title`, `/usage`,
  `/voice`) — no `/init` or context-file generator. The closest mechanism
  is `/learn`, which "distills session feedback and corrections into
  persistent Rules or Skills." This is "not documented," not confirmed
  absent.
- **Config locations:** `~/.gemini/config/` holds `config.json`. Global MCP
  servers at `~/.gemini/config/mcp_config.json`; workspace MCP at
  `.agents/mcp_config.json`. Global custom agents at
  `~/.gemini/config/agents/<agent_name>/agent.md`; workspace agents at
  `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md`. Workspace
  skills at `.agents/skills/` (backward compat `.agent/skills/`); global
  CLI skills at `~/.gemini/antigravity-cli/skills/`. Since v2.11.0
  Antigravity also discovers custom skills, agents, and rules declared in
  `skills.json`, `agents.json`, and `rules.json` files inside project
  subdirectories. `~/.gemini/settings.json` is legacy Gemini CLI
  configuration.

Sources:
- Antigravity docs — Rules and Workflows: https://antigravity.google/docs/rules-workflows/ (verified 2026-08-31)
- Antigravity docs — Migration: https://antigravity.google/docs/cli/gcli-migration/ (verified 2026-08-31)
- Antigravity changelog: https://antigravity.google/changelog (verified 2026-08-31)
- Antigravity docs — Slash commands: https://antigravity.google/docs/slash-commands/ (verified 2026-08-31)
- Antigravity docs — Getting started: https://antigravity.google/docs/getting-started (verified 2026-08-31)

## Fallback rule

Use this decision procedure for any agent not covered by the 12 sections
above, after researching it live from its official documentation:

1. If the agent reads `AGENTS.md` directly at session start (or a
   configurable context-file list that can include it, with no import step
   required) → **`native`**. No adapter file is needed.
2. Else, if the agent's own native context file supports importing or
   including another file (an `@path` mention or similar include
   mechanism) → **`import-adapter`**. Create the agent's native file
   containing an import of `AGENTS.md`, with any agent-specific additions
   below the import.
3. Else — the agent has neither native `AGENTS.md` reading nor an import
   mechanism — → **`full-copy`**. Generate the agent's native context file
   as a full copy of `AGENTS.md`'s content, with this provenance header at
   the top of the generated file:

   ```
   <!-- Generated from AGENTS.md — do not edit; regenerate instead -->
   ```

   Note in the skill's final report to the user that this agent received a
   generated full copy rather than a live adapter, so edits to `AGENTS.md`
   will not propagate automatically and the file must be regenerated by
   re-running this skill (or manually) after any change.

None of the 12 agents in this matrix need the `full-copy` rule as of
2026-08-31 — Kiro and Antigravity, the two agents that looked like
candidates for it, both turned out to read `AGENTS.md` natively (see their
sections above). Keep this rule for agents outside the current v1 target
list.
