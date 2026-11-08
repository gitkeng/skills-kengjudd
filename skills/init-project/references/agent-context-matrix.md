# Agent context matrix

This file is consulted by `init-project` Phase 4 (generate per-agent context
files) to decide, for each agent the user selected, how a canonical
`AGENTS.md` reaches that agent: read directly (`native`), pulled in through
the agent's own import mechanism (`import-adapter`), or copied wholesale
because the agent has neither (`full-copy`). It travels with this skill
(including into a bare symlink install), so every fact below is restated with
its own external source and verification date rather than pointing at this
repository's private knowledge base.

Fourteen agents are covered: Claude Code, Codex, Cursor, opencode, Gemini
CLI, Zed, Kiro, Kimi CLI, Amp, Goose, ZCode, Antigravity, GitHub Copilot,
Devin (formerly Windsurf). For any other agent, research it live from its
official documentation before deciding the adapter rule — mirror this file's
six fields (context file(s) & precedence, import syntax, adapter rule, native
init command, config locations, sources with verified date) and use the
`## Fallback rule` decision procedure at the end of this file.

**Adapters are read by more than their own agent.** A root `CLAUDE.md` is
also loaded, alongside `AGENTS.md`, by Cursor, GitHub Copilot and Devin; a
root `GEMINI.md` by Antigravity and GitHub Copilot. So an import adapter's
notes reach those agents too — the adapter template labels each note with
its agent's name — and an agent that expands the adapter's `@AGENTS.md`
(GitHub Copilot CLI does) loads `AGENTS.md` twice. opencode, Amp and Zed
read `CLAUDE.md` only where no `AGENTS.md` is found, so they never see an
adapter. Each agent's section below gives its own case.

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
- [GitHub Copilot](#github-copilot)
- [Devin](#devin)
- [Fallback rule](#fallback-rule)

## Claude Code

- **Context file(s) & precedence:** `CLAUDE.md`; `AGENTS.md` only when no
  `CLAUDE.md` counts (below). Broadest to most specific: managed policy
  (`/Library/Application Support/ClaudeCode/CLAUDE.md` macOS,
  `/etc/claude-code/CLAUDE.md` Linux/WSL,
  `C:\Program Files\ClaudeCode\CLAUDE.md` Windows) → user
  `~/.claude/CLAUDE.md` → project `./CLAUDE.md` **or** `./.claude/CLAUDE.md`
  → local `./CLAUDE.local.md`. All discovered files are **concatenated**
  (not overridden), broad to specific; within a directory `CLAUDE.local.md`
  is appended after `CLAUDE.md`. Subdirectory files load on demand when
  Claude reads files there. `.claude/rules/*.md` (project, recursive) and
  `~/.claude/rules/` (user) load at launch, or only for matching files when
  they carry `paths:` frontmatter globs. **Native `AGENTS.md`** (v2.1.277,
  published 2026-09-18): under the default **Project instructions** value
  `claude-md-or-agents-md`, Claude reads every `AGENTS.md` and
  `.claude/AGENTS.md` in the working directory and above it **only when no
  `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists there** —
  `~/.claude/CLAUDE.md`, the managed `CLAUDE.md` and `.claude/rules/` do not
  count, so a `CLAUDE.local.md` alone switches `AGENTS.md` off. A
  subdirectory's `AGENTS.md` loads on demand; `AGENTS.local.md`,
  `AGENTS.override.md` and anything under `.agents/` are never read. Other
  values: `claude-md-and-agents-md` (both, each directory's `CLAUDE.md`
  first; an `AGENTS.md` already loaded through an import or symlink is not
  read twice), `claude-md`, `managed-only` — set in `/config`, or under
  `pluginConfigs` → `agents-md@builtin` in user, `--settings` or managed
  settings (ignored in project and local settings). **Unavailable** —
  `CLAUDE.md` only — before v2.1.277; without feature-flag fetching (Amazon
  Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, Claude Platform
  on AWS, a Claude apps gateway, or `DISABLE_TELEMETRY`, `DO_NOT_TRACK`,
  `DISABLE_GROWTHBOOK` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set to
  a value that turns fetching off); in the first session after an install
  or upgrade; or with the built-in `agents-md` plugin disabled.
- **Import syntax:** Yes — `@path/to/import`. Relative paths resolve against
  the file containing the import; absolute paths allowed; recursive to a
  maximum depth of 4 hops; parsing skips code spans and fenced blocks;
  imported files expand at launch. Also expanded inside an `AGENTS.md`
  Claude reads natively.
- **Adapter rule:** `import-adapter` — a `CLAUDE.md` containing `@AGENTS.md`,
  the documented pattern for sessions where Claude "isn't reading your
  `AGENTS.md` directly" (Claude-specific additions follow below the import).
  Kept although native reading exists, because native reading is
  conditional — the unavailable list above, and any project `CLAUDE.md` or
  `CLAUDE.local.md` switches it off — while the import works in every
  session, and "Keeping the import never makes Claude read `AGENTS.md`
  twice, whichever **Project instructions** value you use." The documented
  symlink alternative (`ln -s AGENTS.md CLAUDE.md`) is not used: on Windows
  it needs Administrator privileges or Developer Mode, and a clone without
  `core.symlinks` checks it out as a one-line `CLAUDE.md`. Cursor, GitHub
  Copilot and Devin also load a root `CLAUDE.md`, so this adapter's notes
  reach them (each note carries the agent's name) and GitHub Copilot CLI,
  which expands the import, loads `AGENTS.md` a second time.
- **Native init command:** Yes — `/init`, verbatim: "Initialize project with
  a `CLAUDE.md` guide." It generates a starting CLAUDE.md from codebase
  analysis; if one already exists it "suggests improvements rather than
  overwriting it". It reads Cursor rules (`.cursor/rules/`, `.cursorrules`)
  and `.github/copilot-instructions.md`; with `CLAUDE_CODE_NEW_INIT=1` it
  becomes an interactive flow (CLAUDE.md files, skills, hooks) that also
  reads `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/` or `.windsurfrules`,
  and `.clinerules`. "If `/init` finds OpenAI Codex or Google Gemini CLI
  configuration, it offers to carry it over with `/import`" — and
  `/import [codex|gemini|cursor]` (v2.1.213+, Cursor v2.1.265+; unavailable
  without feature-flag fetching) "appends a one-time copy of instruction
  files such as `AGENTS.md` to the matching `CLAUDE.md`": beside an
  `@AGENTS.md` import, that copy repeats the imported content and goes
  stale.
- **Config locations:** Settings precedence, highest first: managed
  (`managed-settings.json`, MDM, or the claude.ai console) →
  `claude --settings` → `.claude/settings.local.json` →
  `.claude/settings.json` → `~/.claude/settings.json`. Auto memory lives at
  `~/.claude/projects/<project>/memory/` (relocatable via
  `autoMemoryDirectory`).

Sources:
- Claude Code docs — Memory (CLAUDE.md locations, imports, the `AGENTS.md` section: when it loads, **Project instructions** values, when support is unavailable, earlier workarounds, sharing one file): https://code.claude.com/docs/en/memory (verified 2026-09-23)
- Claude Code docs — Commands (`/init`, `/import`): https://code.claude.com/docs/en/commands (verified 2026-09-23)
- Claude Code docs — Environment variables (features that need feature-flag fetching; first session after an install or upgrade): https://code.claude.com/docs/en/env-vars (verified 2026-09-23)
- Claude Code docs — Settings: https://code.claude.com/docs/en/settings (verified 2026-09-23)
- Claude Code changelog, 2.1.277 ("Added AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead"): https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md (verified 2026-09-23); publish date from the npm registry: https://registry.npmjs.org/@anthropic-ai/claude-code (verified 2026-09-23)

## Codex

- **Context file(s) & precedence:** `AGENTS.md`. Global scope:
  `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`; then per-directory
  `AGENTS.override.md`/`AGENTS.md` from the project root (the nearest parent
  holding a `project_root_markers` entry, default `.git`) down to the current
  directory, **concatenated root-down with closer files later (overriding)**.
  Discovery **stops at the current directory** — subdirectories below it are
  never scanned. **An untrusted project loads no project `AGENTS.md`** —
  only the global file (source: PR "Ignore project instructions for
  untrusted projects", merged 2026-08-21; the docs do not say so). Capped at
  `project_doc_max_bytes` (32 KiB default); Codex **skips empty files and
  truncates at the limit**, so a truncated tail is silent. Fallback
  filenames are configurable via `project_doc_fallback_filenames` in
  `~/.codex/config.toml`.
- **Import syntax:** No — no `@import`/include mechanism is documented for
  Codex instruction files.
- **Adapter rule:** `native` — Codex reads `AGENTS.md` directly; no adapter
  file is needed. In an untrusted project it reads none until the user
  trusts the project.
- **Native init command:** Yes — `/init`, described verbatim in the CLI
  source as "create an AGENTS.md file with instructions for Codex." Its
  prompt says: "Before writing, check whether AGENTS.md already exists in
  the current working directory. If it does, do not overwrite or modify
  it." — a model instruction, not a code check. Feature request
  `openai/codex#21932` (let `/init` update an existing AGENTS.md) is still
  open.
- **Config locations:** `config.toml`, precedence highest first: CLI flags
  and `--config` overrides → project `.codex/config.toml` (git root down to
  cwd, trusted projects only) → profile files
  `~/.codex/<profile>.config.toml` → user `~/.codex/config.toml` →
  cloud-managed `config.toml` defaults for the signed-in workspace → system
  `/etc/codex/config.toml` (Unix) → built-in defaults. Managed machines may
  add an organization `requirements.toml`. `CODEX_HOME` relocates the
  `~/.codex` directory.

Sources:
- OpenAI Codex docs — AGENTS.md: https://learn.chatgpt.com/docs/agent-configuration/agents-md (verified 2026-09-23)
- OpenAI Codex docs — Config file basics: https://learn.chatgpt.com/docs/config-file/config-basic (verified 2026-09-23)
- OpenAI Codex docs — Developer commands: https://learn.chatgpt.com/docs/developer-commands (verified 2026-09-23)
- openai/codex — agents_md.rs (project root markers; untrusted projects skip project files): https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs (verified 2026-09-23)
- openai/codex PR #39837 ("Ignore project instructions for untrusted projects", merged 2026-08-21): https://github.com/openai/codex/pull/39837 (verified 2026-09-23)
- openai/codex — slash_command.rs (verbatim `/init` description): https://github.com/openai/codex/blob/main/codex-rs/tui/src/slash_command.rs (verified 2026-09-23)
- openai/codex — `/init` prompt: https://github.com/openai/codex/blob/main/codex-rs/tui/assets/prompt_for_init_command.md (verified 2026-09-23)
- openai/codex issue #21932 (open): https://github.com/openai/codex/issues/21932 (verified 2026-09-23)

## Cursor

- **Context file(s) & precedence:** Reads `AGENTS.md` at the project root
  and in subdirectories; nested files are **combined, nearest wins**. It
  also "reads `CLAUDE.md` files the same way it reads `AGENTS.md`": a root
  `CLAUDE.md` is always applied, whatever its `alwaysApply`; the CLI reads
  `AGENTS.md` and `CLAUDE.md` at the project root. `.cursor/rules/*.mdc`
  coexists for glob-scoped/manually-invoked rules, with frontmatter keys
  `alwaysApply`, `description`, `globs` (a plain `.md` there is ignored);
  `.cursorrules` is legacy and will be deprecated. **User Rules** are set in
  the UI (synced to the account) or as files in `~/.cursor/rules` (local);
  **Team Rules** in the dashboard — an init flow writes neither. Documented
  application order: **Team Rules → Project Rules → User Rules**.
- **Import syntax:** Yes, inside `.mdc` rules — "Use `@filename.ts` to
  include files in your rule's context." Whether the same expansion applies
  inside `AGENTS.md` or `CLAUDE.md` is **not documented**.
- **Adapter rule:** `native` — Cursor reads `AGENTS.md` directly; no adapter
  file is needed. When Claude Code is also selected, Cursor loads its
  `CLAUDE.md` adapter too.
- **Native init command:** **No `/init`** and no `AGENTS.md` generator. The
  documented generators write rules into `.cursor/rules`: `/create-rule` in
  Agent chat, the CLI's `agent generate-rule` (alias `rule`), and **New
  Cursor Rule** in the command palette. This is "not documented," not
  confirmed absent.
- **Config locations:** CLI settings `~/.cursor/cli-config.json`
  (`$env:USERPROFILE\.cursor\cli-config.json` on Windows;
  `CURSOR_CONFIG_DIR` overrides the directory, and Linux/BSD use
  `$XDG_CONFIG_HOME/cursor/cli-config.json`); only permissions can be set
  per project, at `<project>/.cursor/cli.json`. MCP servers at
  `.cursor/mcp.json` (project) and `~/.cursor/mcp.json` (global), with
  project → global → nested precedence. Rules at `.cursor/rules/`; user
  rule files at `~/.cursor/rules`.

Sources:
- Cursor docs — Rules: https://cursor.com/docs/rules (verified 2026-09-23)
- Cursor help — Rules (CLAUDE.md read like AGENTS.md; `~/.cursor/rules`; `.cursorrules` legacy): https://cursor.com/help/customization/rules (verified 2026-09-23)
- Cursor docs — Using the CLI (root `AGENTS.md` and `CLAUDE.md`): https://cursor.com/docs/cli/using (verified 2026-09-23)
- Cursor docs — CLI configuration: https://cursor.com/docs/cli/reference/configuration (verified 2026-09-23)
- Cursor docs — CLI parameters (`generate-rule`): https://cursor.com/docs/cli/reference/parameters (verified 2026-09-23)
- Cursor docs — CLI slash commands: https://cursor.com/docs/cli/reference/slash-commands (verified 2026-09-23)
- Cursor docs — MCP (file locations): https://cursor.com/docs/mcp (verified 2026-09-23)
- Cursor docs — CLI MCP (project → global → nested precedence): https://cursor.com/docs/cli/mcp (verified 2026-09-23)

## opencode

- **Context file(s) & precedence:** Reads project `AGENTS.md`, falling back
  to `CLAUDE.md` for Claude Code compatibility, plus the global
  `~/.config/opencode/AGENTS.md` and, unless disabled, `~/.claude/CLAUDE.md`
  as a Claude Code compatibility fallback. The docs: "The first matching
  file wins in each category." The source walks from the current directory
  up to the worktree root, takes the first filename found anywhere on that
  path (`AGENTS.md`, then `CLAUDE.md`, then a deprecated `CONTEXT.md`) and
  loads every file of that name on the path — so `CLAUDE.md` is used only
  when no `AGENTS.md` exists there. Instruction files in subdirectories are
  attached when the agent reads files in them.
- **Import syntax:** No — "opencode doesn't automatically parse file
  references" in `AGENTS.md`. Additional files are pulled in through the
  `instructions` array in `opencode.json`, which accepts local paths, glob
  patterns, and remote URLs (5-second fetch timeout).
- **Adapter rule:** `native` — opencode reads `AGENTS.md` directly; no
  adapter file is needed.
- **Native init command:** Yes — `/init` ("guided AGENTS.md setup" in the
  source) generates or updates `AGENTS.md` by scanning the repository and
  asking targeted questions; its template begins "Create or update
  `AGENTS.md` for this repository." — so it edits this run's `AGENTS.md`.
- **Config locations:** Config files are **merged**, not replaced, lowest
  to highest: remote `.well-known/opencode` → global
  `~/.config/opencode/opencode.json` → custom path from `OPENCODE_CONFIG`
  → project `opencode.json` → `.opencode/` directories → inline
  `OPENCODE_CONFIG_CONTENT` → managed files
  (`/Library/Application Support/opencode/` macOS, `/etc/opencode/` Linux,
  `%ProgramData%\opencode` Windows) → macOS managed preferences (highest,
  non-overridable). `.jsonc` is accepted everywhere `.json` is. An
  `OPENCODE_CONFIG_DIR` directory loads after the global and `.opencode`
  directories and "can override" them; TUI settings live in a separate
  `tui.json`.

Sources:
- opencode docs — Rules: https://opencode.ai/docs/rules/ (verified 2026-09-23)
- opencode docs — Config: https://opencode.ai/docs/config/ (verified 2026-09-23)
- anomalyco/opencode (formerly sst/opencode) — instruction.ts (lookup order, `CONTEXT.md` deprecated, subdirectory files): https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/instruction.ts (verified 2026-09-23)
- anomalyco/opencode — command/index.ts and the `/init` template: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/command/index.ts (verified 2026-09-23)

## Gemini CLI

- **Context file(s) & precedence:** Default context filename is
  `GEMINI.md`; the `context.fileName` setting takes a list and **can
  include `AGENTS.md`** (documented example:
  `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`). The setting **adds** names
  in front of `GEMINI.md` rather than replacing it ("Adds one or more
  filenames to the current context filenames"). Gemini CLI does **not** read
  `AGENTS.md` by default: the request to make that the default was closed
  as not planned (#12345, 2026-05-08), a later bug report asking the same
  (#28227) is open, and no change has merged (verified 2026-09-23) — so
  treat the `GEMINI.md` adapter, not a default-`AGENTS.md` change, as the
  supported path. Hierarchy: global `~/.gemini/GEMINI.md`, then
  configured workspace directories and their parents, plus just-in-time
  scanning — when a tool touches a file or directory, the CLI scans that
  directory and its ancestors up to a trusted root. All found files are
  **concatenated** and sent with every prompt.
- **Import syntax:** Yes — `@file.md`, supporting relative
  (`@./components/x.md`) and absolute paths; a bare `@AGENTS.md` passes the
  import validation. `@` imports inside code spans and fenced blocks are
  ignored, so the adapter's import line must not sit in backticks.
- **Adapter rule:** `import-adapter` — the canonical `AGENTS.md` reaches
  Gemini CLI through a `GEMINI.md` containing `@AGENTS.md`. This is the
  zero-configuration path. The alternative, adding `AGENTS.md` to
  `context.fileName`, needs per-project configuration in
  `.gemini/settings.json` — a file Gemini CLI does not load from a folder
  that is untrusted while folder trust is on. Do not use both: whether a
  file that is imported and also listed is loaded once is not documented.
  Antigravity and GitHub Copilot also load a root `GEMINI.md`, so this
  adapter's notes reach them (each note carries the agent's name); Copilot
  CLI does not expand `@` inside `GEMINI.md`.
- **Native init command:** Yes — `/init`, described verbatim in the source
  as "Analyzes the project and creates a tailored GEMINI.md file"; it
  writes an empty `GEMINI.md` in the target directory and then populates it
  from project analysis (writes `GEMINI.md`, not `AGENTS.md`). When a
  `GEMINI.md` already exists it stops: "A GEMINI.md file already exists in
  this directory. No changes were made." `/memory show`, `/memory list` and
  `/memory reload` (alias `refresh`) inspect and re-scan context files.
- **Config locations:** Four `settings.json` files, precedence lowest to
  highest: system defaults (`system-defaults.json`) → user
  `~/.gemini/settings.json` → workspace `<project>/.gemini/settings.json` →
  system overrides (`/etc/gemini-cli/settings.json` Linux,
  `C:\ProgramData\gemini-cli\settings.json` Windows,
  `/Library/Application Support/GeminiCli/settings.json` macOS) — the
  system overrides file has the final say. `GEMINI_CLI_SYSTEM_SETTINGS_PATH`
  and `GEMINI_CLI_SYSTEM_DEFAULTS_PATH` override the two system paths;
  `GEMINI_CLI_HOME` relocates `.gemini`. Arrays and objects merge rather
  than replace. Since v0.60.0 (2026-09-15) the two system-wide files are
  skipped, with a warning, unless their ownership and permissions pass a
  strict check.

Sources:
- gemini-cli docs — Context files: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md (verified 2026-09-23)
- gemini-cli source — memoryTool.ts (`DEFAULT_CONTEXT_FILENAME`, `context.fileName` adds names): https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/memoryTool.ts (verified 2026-09-23)
- gemini-cli docs — Memory import processor (`@` imports, code regions ignored): https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/memport.md (verified 2026-09-23)
- gemini-cli source — memoryImportProcessor.ts (import path validation): https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/utils/memoryImportProcessor.ts (verified 2026-09-23)
- gemini-cli source — initCommand.ts: https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/ui/commands/initCommand.ts (verified 2026-09-23)
- gemini-cli source — init.ts (existing `GEMINI.md` left unchanged): https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/commands/init.ts (verified 2026-09-23)
- gemini-cli docs — Commands (`/memory` subcommands): https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/commands.md (verified 2026-09-23)
- gemini-cli docs — Settings: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/settings.md (verified 2026-09-23)
- gemini-cli docs — Configuration reference (system-defaults paths, `GEMINI_CLI_SYSTEM_DEFAULTS_PATH`, `GEMINI_CLI_HOME`): https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md (verified 2026-09-23)
- gemini-cli docs — Enterprise: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/enterprise.md (verified 2026-09-23)
- gemini-cli docs — Trusted folders (project `.gemini/settings.json` not loaded when untrusted): https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/trusted-folders.md (verified 2026-09-23)
- gemini-cli changelog — v0.60.0 (strict system-config ownership checks, #29115): https://github.com/google-gemini/gemini-cli/blob/main/docs/changelogs/latest.md (verified 2026-09-23)
- google-gemini/gemini-cli issue #12345 ("AGENTS.md by default", closed not planned 2026-05-08): https://github.com/google-gemini/gemini-cli/issues/12345 (verified 2026-09-23)
- google-gemini/gemini-cli issue #28227 (AGENTS.md not in the default `context.fileName` list, open): https://github.com/google-gemini/gemini-cli/issues/28227 (verified 2026-09-23)

## Zed

- **Context file(s) & precedence:** Project instructions use a
  **first-match-wins** list: `.rules`, `.cursorrules`, `.windsurfrules`,
  `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`,
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` — a stray `.cursorrules` silently
  shadows `AGENTS.md`. Zed also has a **personal** instruction file at
  `~/.config/zed/AGENTS.md` (`%APPDATA%\Zed\AGENTS.md` on Windows) applying
  across all projects; **project instructions override personal
  instructions when they conflict**. The list applies to the Zed Agent
  only: External Agents and Terminal Threads inside Zed "may read their own
  native instruction files directly".
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
  and Linux; Linux also honors `$XDG_CONFIG_HOME/zed/settings.json`),
  `%APPDATA%\Zed\settings.json` (Windows); project settings
  `.zed/settings.json` (also allowed in subdirectories), layered default →
  user → project; key bindings in `keymap.json`.

Sources:
- Zed docs — Instructions: https://zed.dev/docs/ai/instructions (verified 2026-09-23)
- Zed docs source — Configuring Zed (the published `zed.dev/docs/configuring-zed` now redirects to the all-settings reference, which omits these paths): https://github.com/zed-industries/zed/blob/main/docs/src/configuring-zed.md (verified 2026-09-23)
- Zed docs — Key bindings (`keymap.json`): https://zed.dev/docs/key-bindings (verified 2026-09-23)

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
  discovery in subdirectories. Steering and skills **merge** across scopes
  rather than replacing; precedence is **Agent > Project > Global**. Two
  official pages contradict each other, so neither claim is safe alone:
  the steering page says custom agents do **not** auto-include steering
  (list `file://.kiro/steering/**/*.md` in `resources`), while the custom
  agent configuration reference says they inherit steering files, skills
  and `AGENTS.md` by default unless `chat.disableInheritingDefaultResources`
  is set; and the steering page says Kiro CLI supports no inclusion modes,
  while the opt-in CLI v3 (`kiro-cli --v3`) supports front-matter inclusion
  modes. Steering uploaded through Configuration Sync also loads into new
  local CLI sessions when the user enables that option.
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
  `hooks/`, `specs/`; workspace CLI overrides in `.kiro/settings/cli.json`;
  project-scope permissions live per user outside the repo, at
  `~/.kiro/workspace-roots/<hash>/permissions.yaml`. The **Agent > Project >
  Global** precedence recorded above has one exception: for permissions, a
  **deny wins at any scope**. `KIRO_HOME` redirects the global `~/.kiro`
  directory. In a V3 session `/config` shows the configuration in use.

Sources:
- Kiro docs — Steering: https://kiro.dev/docs/steering/ (verified 2026-09-23)
- Kiro docs — Custom agent configuration reference (default resources inherited): https://kiro.dev/docs/custom-agents/configuration-reference/ (verified 2026-09-23)
- Kiro docs — CLI v3 new features (inclusion modes): https://kiro.dev/docs/cli/v3/new-features/ (verified 2026-09-23)
- Kiro docs — Configuration scopes (Configuration Sync, workspace-roots permissions, `/config`): https://kiro.dev/docs/configuration/ (verified 2026-09-23)
- Kiro docs — Slash commands (workspace `.kiro/settings/cli.json`; no `/init`): https://kiro.dev/docs/reference/slash-commands/ (verified 2026-09-23)
- Kiro docs — MCP configuration: https://kiro.dev/docs/mcp/configuration/ (verified 2026-09-23)

## Kimi CLI

Moonshot AI's terminal agent is now **Kimi Code CLI**
(`MoonshotAI/kimi-code`). The Python `MoonshotAI/kimi-cli` repository is
archived ("no longer maintained"; existing installations "will stop
working"), and its release 1.52.0 (2026-09-22) turns a bare `kimi` into the
Kimi Code installer; `~/.kimi/` is read only to migrate from it. The fields
below describe Kimi Code.

- **Context file(s) & precedence:** Reads `AGENTS.md`. Global
  Kimi-specific instructions at `$KIMI_CODE_HOME/AGENTS.md` (default
  `~/.kimi-code/AGENTS.md`); generic cross-tool instructions at
  `~/.agents/AGENTS.md`; project instructions in `.kimi-code/AGENTS.md` or
  `AGENTS.md` under the project tree. The source reads them in that order —
  project files in each directory from the git root down to the working
  directory, lowercase `agents.md` also accepted — and joins them all,
  warning above a recommended 32 KiB total. It does not read `CLAUDE.md`,
  `GEMINI.md` or the old `.kimi/AGENTS.md`.
- **Import syntax:** **Not documented** — no `@file`/import expansion for
  `AGENTS.md` appears in the official docs (absence of documentation, not
  documented absence).
- **Adapter rule:** `native` — Kimi Code reads `AGENTS.md` directly; no
  adapter file is needed.
- **Native init command:** Yes — `/init`, verbatim: "Analyze the current
  codebase and generate `AGENTS.md`". Its prompt writes the root
  `AGENTS.md` "replacing the file's previous content", after reading an
  existing one and carrying forward whatever is still accurate — so it
  rewrites this run's `AGENTS.md`.
- **Config locations:** One user-level `~/.kimi-code/config.toml` (terminal
  UI preferences in a companion `tui.toml`); "The CLI currently reads a
  single user-level config file and has no project-level config file
  mechanism." `KIMI_CODE_HOME` relocates the whole data directory,
  including the global `AGENTS.md`; generic `~/.agents/` files stay in the
  real home. MCP servers are declared in `~/.kimi-code/mcp.json` or a
  project-local `.kimi-code/mcp.json`, not in `config.toml`.

Sources:
- kimi-code docs — Agents (instruction files, `~/.agents/AGENTS.md`): https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/customization/agents.md (verified 2026-09-23)
- kimi-code source — context.ts (load order, 32 KiB recommendation): https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core-v2/src/agent/profile/context.ts (verified 2026-09-23)
- kimi-code docs — Slash commands (`/init`): https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/reference/slash-commands.md (verified 2026-09-23)
- kimi-code source — `/init` prompt: https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core-v2/src/features/sessionInit/profile/init.md (verified 2026-09-23)
- kimi-code docs — Config files: https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/configuration/config-files.md (verified 2026-09-23)
- kimi-code docs — Overrides (no project-level config): https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/configuration/overrides.md (verified 2026-09-23)
- MoonshotAI/kimi-cli README and CHANGELOG (archived; 1.52.0 installs Kimi Code): https://github.com/MoonshotAI/kimi-cli (verified 2026-09-23)

## Amp

- **Context file(s) & precedence:** Reads `AGENTS.md` from the widest set
  of locations recorded here: the current working directory (or editor
  workspace roots) **and parent directories up to `$HOME`**; subtree
  `AGENTS.md` files, included when the agent accesses files in those
  directories; user config `$HOME/.config/amp/AGENTS.md` and
  `$HOME/.config/AGENTS.md`; and system-wide `/etc/ampcode/AGENTS.md`,
  `/Library/Application Support/ampcode/AGENTS.md`,
  `%ProgramData%\ampcode\AGENTS.md`. A personal **Global AGENTS.md** can
  also be edited in the web app (Settings → Advanced), and workspace admins
  can set a workspace-wide one that Amp includes before personal and
  repository guidance. Fallback, verbatim: "If no `AGENTS.md` exists in a
  directory, but a file named `AGENT.md` (without an `S`) or `CLAUDE.md`
  does exist, that file will be included."
- **Import syntax:** Yes — `@`-mentions inside `AGENTS.md` support relative
  paths, absolute paths, `@~/some/path`, and globs such as `@doc/*.md`;
  `@`-mentions inside code blocks are ignored. An @-mentioned file with
  `globs` frontmatter is included only once Amp has read a matching file.
- **Adapter rule:** `native` — Amp reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** **None documented.** "Amp offers to generate an
  `AGENTS.md` file for you if none exists" — an offer, not a command, and
  only where the file is missing. `agents-md list` in the command palette
  shows which `AGENTS.md` files Amp is currently using. This is "not
  documented," not confirmed absent.
- **Config locations:** User settings `~/.config/amp/settings.json` or
  `.jsonc` (`%USERPROFILE%\.config\amp\...` on Windows); workspace
  `.amp/settings.json`/`.jsonc`, resolved to the nearest match searching
  upward to the repository root; `--settings-file <path>` for a custom
  file; enterprise managed settings at
  `/Library/Application Support/ampcode/managed-settings.json` (macOS),
  `/etc/ampcode/managed-settings.json` (Linux),
  `%ProgramData%\ampcode\managed-settings.json` (Windows), plus — for
  Enterprise — a server-side managed-settings document in Workspace
  Settings, which the local managed file takes precedence over. **Workspace
  settings override user settings**; all keys use the `amp.` prefix.

Sources:
- Amp docs — AGENTS.md: https://ampcode.com/docs/customize/agents-md (verified 2026-09-23)
- Amp docs — CLI configuration: https://ampcode.com/docs/cli/settings (verified 2026-09-23)

## Goose

Goose moved from `block/goose` to `aaif-goose/goose` ("goose is part of the
Agentic AI Foundation (AAIF) at the Linux Foundation"); its docs are at
`goose-docs.ai`.

- **Context file(s) & precedence:** Default context filenames are **both**
  `AGENTS.md` and `.goosehints`: "By default, goose looks for both
  `AGENTS.md` and `.goosehints` at each level." Files load from the working
  directory **up to the repository root**, and goose additionally
  discovers hint files in nested subdirectories when it works there. Global
  hints live at `~/.config/goose/.goosehints` and apply to every session;
  when global and local conflict, **local wins**. The filename list is
  configurable with the `CONTEXT_FILE_NAMES` environment variable (a JSON
  array); its default order differs between official pages — the hints
  guide gives `["AGENTS.md", ".goosehints"]`, the environment-variables
  reference `[".goosehints", "AGENTS.md"]` — and which of the two wins when
  they contradict at the same level is **not documented**.
- **Import syntax:** Yes — an `@` reference "Automatically includes the
  file content in goose's immediate context"; a plain path without `@` only
  points goose at a file to read when needed. (Recorded as "No" until
  2026-09-23; the docs have described `@` since at least 2025-12.)
- **Adapter rule:** `native` — Goose reads `AGENTS.md` directly; no adapter
  file is needed.
- **Native init command:** **None.** The CLI command list contains no
  context-file generator; the similarly named `goose term init <SHELL>`
  only prints a shell integration script.
- **Config locations:** macOS/Linux: `~/.config/goose/config.yaml`
  (provider, model, extensions, general settings), `permission.yaml`,
  `secrets.yaml`, `permissions/tool_permissions.json`, `prompts/`. Windows:
  the same tree under `%APPDATA%\Block\goose\config\`. Precedence:
  environment variables, then config file settings, then defaults.

Sources:
- goose docs — Using goosehints: https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/ (verified 2026-09-23)
- goose docs — Environment variables (`CONTEXT_FILE_NAMES` default): https://goose-docs.ai/docs/guides/environment-variables/ (verified 2026-09-23)
- goose docs — Config files: https://goose-docs.ai/docs/guides/config-files/ (verified 2026-09-23)
- goose docs — CLI commands: https://goose-docs.ai/docs/guides/goose-cli-commands/ (verified 2026-09-23)
- aaif-goose/goose repository (AAIF membership; the docs sources above live under `documentation/docs/guides/`): https://github.com/aaif-goose/goose (verified 2026-09-23)

## ZCode

- **Context file(s) & precedence:** `AGENTS.md` and only `AGENTS.md`, from
  exactly two sources: the user global `~/.zcode/AGENTS.md` and the current
  workspace `AGENTS.md`. Verbatim: "When both sources exist, ZCode appends
  the user global instructions first, then the workspace instructions." It
  does **not** merge multiple `AGENTS.md` files across directory levels, does
  **not** scan child directories, and does **not** choose rule files
  automatically by task type. Since v3.7.1 subagents inject both files too
  (`injectAgentsMd: false` in a subagent's frontmatter opts out).
  `CLAUDE.md` is a **one-time onboarding
  migration source only**, never read at runtime.
- **Import syntax:** No — `@import`/`@include` expansion is explicitly not
  performed. ZCode is the load-bearing case for a canonical `AGENTS.md`
  that carries its own content rather than delegating to imports, since it
  expands none.
- **Adapter rule:** `native` — ZCode reads `AGENTS.md` directly (the only
  file it reads by itself); no adapter file is needed, and none is possible
  since ZCode has no import mechanism to adapt through.
- **Native init command:** **Yes, undocumented.** The commands page still
  lists two built-ins, `/goal` and `/compact`, but local inspection of the
  installed ZCode 3.14.3 (2026-09-23) finds a built-in `/init` — summary
  "Create or update workspace AGENTS.md instructions.", usage
  `/init [notes]`. Its prompt edits an existing workspace-root `AGENTS.md`
  "instead of replacing it wholesale", creates one when absent, never
  writes `~/.zcode/AGENTS.md`, and stops if `.zcode/AGENTS.md` or
  `.agents/AGENTS.md` exists — so it edits this run's `AGENTS.md`.
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
  same scope. When a project and the user define an MCP server of the same
  name, the user's wins — "a project can never override your
  configuration".

Sources:
- ZCode docs — AGENTS.md: https://zcode.z.ai/en/docs/agents (verified 2026-09-23)
- ZCode docs — Subagents (`injectAgentsMd`, since v3.7.1): https://zcode.z.ai/en/docs/subagents (verified 2026-09-23)
- ZCode docs — Commands: https://zcode.z.ai/en/docs/commands (verified 2026-09-23)
- ZCode docs — Configuration: https://zcode.z.ai/en/docs/configuration (verified 2026-09-23)
- ZCode docs — MCP servers: https://zcode.z.ai/en/docs/mcp-services (verified 2026-09-23)
- Local inspection — ZCode 3.14.3 app bundle, `Contents/Resources/glm/zcode.cjs` (built-in command list and `/init` prompt; not a public URL): 2026-09-23

## Antigravity

Google's agentic development platform, documented per product: the
Antigravity 2.0 desktop app, the Antigravity CLI, and the Antigravity IDE.
Its changelog has one tab per product — cite the tab with the version.

- **Context file(s) & precedence:** Workspace context: the agent "continues
  to parse and enforce rule constraints defined inside your active
  directory's `GEMINI.md` and `AGENTS.md` files" — **both** filenames are
  read; the CLI best-practices page likewise tells users to create
  `GEMINI.md` or `AGENTS.md` at the workspace root, parsed at startup. The
  IDE began reading `AGENTS.md` in v1.20.5 (2026-03-09): "Added support for
  reading rules from AGENTS.md in addition to GEMINI.md." Global context:
  `~/.gemini/GEMINI.md` on every product ("The agent automatically consults
  and enforces your global constraints"); the CLI also reads global rules
  from `~/.gemini/antigravity-cli/rules/`. Separately, Antigravity's own
  **Rules** are markdown files under the workspace `.agents/rules` folder
  (backward-compatible with `.agent/rules`), capped at **12,000 characters
  each**, with four activation modes: Manual (`@`-mention), Always On,
  Model Decision, and Glob. Workflows are now IDE-only, deprecated, and
  retired on 2026-11-01 in favor of Agent Skills (`/migrate-workflows`).
  **Precedence between `AGENTS.md` and `GEMINI.md` is not documented**, nor
  is whether nested/parent `AGENTS.md` files are discovered beyond "your
  active directory's" — neither an upward walk nor a subtree scan is stated.
- **Import syntax:** Yes — `@path/to/file` references and inlines external
  files "within `AGENTS.md` and custom rule files" (2.0 changelog tab,
  v2.11.0, 2026-08-26; no CLI or IDE entry says the same). A relative path
  resolves against the rules file's location; an absolute form such as
  `@/path/to/file.md` resolves to `/path/to/file.md` first and falls back to
  the same path under the workspace root.
- **Adapter rule:** `native` — Antigravity reads `AGENTS.md` directly in
  the active workspace directory (alongside `GEMINI.md`); no adapter file
  is needed. Caveat: because AGENTS.md-vs-GEMINI.md precedence is
  undocumented, do not assume which file wins if both exist and conflict —
  and when Gemini CLI is also selected, Antigravity loads its `GEMINI.md`
  adapter too.
- **Native init command:** **None.** No `/init` or context-file generator
  appears among the documented built-in slash commands (the catalog added
  `/boost`, 2.0 v2.12.0, and `/migrate-workflows`) or in the CLI reference.
  The closest mechanism is `/learn`, which "distills session feedback and
  corrections into persistent Rules or Skills." This is "not documented,"
  not confirmed absent.
- **Config locations:** `~/.gemini/config/` holds `config.json`. Global MCP
  servers at `~/.gemini/config/mcp_config.json`; workspace MCP at
  `.agents/mcp_config.json`. Global custom agents at
  `~/.gemini/config/agents/<agent_name>/agent.md`; workspace agents at
  `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md`. Workspace
  skills at `.agents/skills/` (backward compat `.agent/skills/`); global
  CLI skills at `~/.gemini/antigravity-cli/skills/`. CLI settings at
  `~/.gemini/antigravity-cli/settings.json`. Since
  v2.11.0 Antigravity also discovers custom skills, agents, and rules
  declared in `skills.json`, `agents.json`, and `rules.json` files inside
  project subdirectories. `~/.gemini/settings.json` is legacy Gemini CLI
  configuration.

Sources:
- Antigravity docs — Rules (per-product global/workspace rule paths): https://antigravity.google/docs/rules-workflows/ (verified 2026-09-23)
- Antigravity docs — Migration from Gemini CLI: https://antigravity.google/docs/cli/gcli-migration/ (verified 2026-09-23)
- Antigravity docs — CLI best practices (`GEMINI.md` or `AGENTS.md` at the workspace root): https://antigravity.google/docs/cli/best-practices/ (verified 2026-09-23)
- Antigravity docs — Workflows (IDE; deprecated): https://antigravity.google/docs/ide/workflows/ (verified 2026-09-23)
- Antigravity docs — Workflows to Skills migration (retired 2026-11-01): https://antigravity.google/docs/migration/workflows-to-skills/ (verified 2026-09-23)
- Antigravity changelog (IDE tab v1.20.5; 2.0 tab v2.11.0, v2.12.0): https://antigravity.google/changelog (verified 2026-09-23)
- Antigravity docs — Slash commands: https://antigravity.google/docs/slash-commands/ (verified 2026-09-23)
- Antigravity docs — Settings (CLI `settings.json`): https://antigravity.google/docs/settings/ (verified 2026-09-23)

## GitHub Copilot

Three surfaces read instructions differently: **Copilot CLI**, **Copilot in
VS Code**, and the **Copilot cloud agent** on github.com (formerly "coding
agent"; the old URLs redirect).

- **Context file(s) & precedence:** `AGENTS.md` is read by default on all
  three. **CLI:** loads "simultaneously (all are merged)" `AGENTS.md`,
  `CLAUDE.md` (also `.claude/CLAUDE.md`), `GEMINI.md`,
  `.github/copilot-instructions.md` and
  `.github/instructions/**/*.instructions.md` (applied where `applyTo`
  matches), plus `$HOME/.copilot/copilot-instructions.md`,
  `$HOME/.copilot/instructions/` and `COPILOT_CUSTOM_INSTRUCTIONS_DIRS`. The
  how-to page finds repository files at the repository root, the working
  directory, the directories between, and those in the path of a file being
  worked on; the reference table says "In Git root and cwd". It removes
  duplicate copies of identical files but "does not define a general
  precedence order". **VS Code** (the Local agent harness, still the
  default): `AGENTS.md` at each workspace-folder root
  (`chat.useAgentsMdFile`, default `true`), nested ones only with the
  experimental `chat.useNestedAgentsMdFiles` (default `false`); also
  `.github/copilot-instructions.md`, `CLAUDE.md` files
  (`chat.useClaudeMdFile`, default `true`) and `*.instructions.md` in
  `.github/instructions` or `.claude/rules`. A subfolder opened alone finds
  the repository root's files only with
  `chat.useCustomizationsInParentRepositories`. The Local agent "will be
  removed in a future release"; the newer Copilot harness does not document
  its discovery rules. **Cloud agent:** `**/AGENTS.md` ("the nearest
  `AGENTS.md` file in the directory tree will take precedence"),
  `.github/copilot-instructions.md`,
  `.github/instructions/**/*.instructions.md`, and "Alternatively ... a
  single `CLAUDE.md` or `GEMINI.md` file stored in the root". On GitHub.com
  personal instructions rank above repository ones and those above
  organization ones, but "all sets of relevant instructions are provided".
- **Import syntax:** **CLI:** yes — "In `.github/copilot-instructions.md`,
  `AGENTS.md`, or `CLAUDE.md`, use `@` followed by a relative path to
  include another file" (recursive; referenced files stay inside the
  repository); "File references are not expanded in `GEMINI.md` or
  `*.instructions.md` files". **VS Code:** Markdown links, resolved against
  the instructions file, added automatically only with
  `chat.includeReferencedInstructions` (default `false`). **Cloud agent:**
  not documented.
- **Adapter rule:** `native` — a root `AGENTS.md` reaches all three
  surfaces; no adapter file is needed. Do not also write
  `.github/copilot-instructions.md`: every surface loads both. When Claude
  Code or Gemini CLI is also selected, their adapters reach Copilot too —
  the CLI and VS Code load `CLAUDE.md`, the CLI `GEMINI.md` — and the CLI
  expands the `@AGENTS.md` inside `CLAUDE.md`, so it loads `AGENTS.md`
  twice (its de-duplication covers identical copies only).
- **Native init command:** **CLI:** `copilot init` ("Initialize Copilot
  custom instructions for this repository.") and `/init` write or update
  `.github/copilot-instructions.md`, not `AGENTS.md`; "If the file already
  exists, Copilot suggests improvements which you can choose to apply or
  reject." **VS Code:** `/init` — "Generate or update workspace
  instructions in a local agent session." Its built-in `init` skill says
  "Prefer AGENTS.md over `.github/copilot-instructions.md`. If the user
  already has one of these files, update it instead of creating a new one."
  — so it edits this run's `AGENTS.md`. **Cloud agent:** no command; an
  onboarding prompt has Copilot open a draft pull request that writes
  `.github/copilot-instructions.md`.
- **Config locations:** **CLI:** `~/.copilot` (`COPILOT_HOME` replaces the
  whole path) holds `settings.json` and `mcp-config.json`; repository
  settings in `.github/copilot/settings.json`, personal overrides in
  `.github/copilot/settings.local.json`; project MCP servers in `.mcp.json`
  or `.github/mcp.json` take precedence over user-level ones of the same
  name. **VS Code:** user `settings.json` and workspace
  `.vscode/settings.json`; MCP in `.vscode/mcp.json`. **Cloud agent:**
  `.github/workflows/copilot-setup-steps.yml` (a single
  `copilot-setup-steps` job; it runs only from the default branch) and
  repository **Settings → Copilot** (MCP servers, cloud agent settings).

Sources:
- GitHub Docs — Adding custom instructions for Copilot CLI (locations, merging, `@` imports): https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions (verified 2026-09-23)
- GitHub Docs — Copilot CLI command reference (merged locations, `copilot init` and `/init`, settings files): https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference (verified 2026-09-23)
- GitHub Docs — Copilot CLI configuration directory (`~/.copilot`, `COPILOT_HOME`, `mcp-config.json`): https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference (verified 2026-09-23)
- GitHub Docs — Adding repository custom instructions (cloud agent: nearest `AGENTS.md`, root `CLAUDE.md`/`GEMINI.md`, generation PR): https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions (verified 2026-09-23)
- GitHub Docs — About customizing Copilot responses (personal > repository > organization): https://docs.github.com/en/copilot/concepts/prompting/response-customization (verified 2026-09-23)
- GitHub Docs — Customize the cloud agent environment (`copilot-setup-steps.yml`): https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment (verified 2026-09-23)
- VS Code docs — AI settings reference (`chat.useAgentsMdFile`, `chat.useNestedAgentsMdFiles`, `chat.useClaudeMdFile`, `chat.includeReferencedInstructions`, `chat.useCustomizationsInParentRepositories`; Local agent removal): https://code.visualstudio.com/docs/agents/reference/ai-settings (verified 2026-09-23)
- VS Code docs — Custom instructions: https://code.visualstudio.com/docs/agent-customization/custom-instructions (verified 2026-09-23)
- VS Code docs — AI features cheat sheet (`/init`): https://code.visualstudio.com/docs/agents/reference/ai-features-cheat-sheet (verified 2026-09-23)
- microsoft/vscode — built-in `init` skill: https://github.com/microsoft/vscode/blob/main/extensions/copilot/assets/prompts/skills/init/SKILL.md (verified 2026-09-23)

## Devin

Cognition's agent, formerly **Windsurf**: "Windsurf is now Devin Desktop"
(Devin Desktop changelog v3.0.12, 2026-06-02), and v3.9.19 (2026-09-08):
"Cascade has been removed. Devin Local is now the only agent available in
Devin Desktop." Devin Local is "our next-generation agent harness shared
with Devin CLI" and "reads `AGENTS.md` through the Devin CLI rules system",
so one entry covers **Devin CLI** and **Devin Desktop**; the cloud Devin
also reads `AGENTS.md`. Official docs moved to `docs.devin.ai`
(`docs.windsurf.com` redirects there).

- **Context file(s) & precedence:** "Devin CLI reads this file
  automatically" — `AGENTS.md` at the project root. It also reads
  `AGENTS.local.md` (personal, gitignored), `AGENT.md`, `.windsurfrules`
  and `CLAUDE.md`: "All of these are treated identically — their contents
  are loaded as always-on rules." Root files load at session start;
  subdirectory ones load when the agent accesses files there (nested and
  lowercase `agents.md` files since CLI v3000.4.16). Global rules:
  `~/.config/devin/AGENTS.md` (`%APPDATA%\devin\AGENTS.md` on Windows,
  `AGENT.md` also accepted) and `~/.claude/CLAUDE.md`, loaded together with
  project rules. Rule directories are read too: `.devin/rules/*.md` and
  `.devin/global_rules.md` (preferred over their `.windsurf/`
  equivalents), `.windsurf/rules/` and `.cursor/rules/`. Which file wins
  when rules conflict — same directory, root vs nested, global vs project —
  is not documented. Each always-on rule file is capped at 32 KiB and
  truncated with a hint (CLI changelog). Setting
  `read_config_from.agents_standard` or `read_config_from.claude` (both
  default `true`) to `false` stops the `AGENTS.md` family or `CLAUDE.md`
  loading — the `claude` key also drops Claude Code skills, commands and
  MCP servers.
- **Import syntax:** **Not documented** — no `@path` or include syntax for
  rule files appears in the docs; "Controlling Imports" there means which
  other tools' formats are read. Whether an `@AGENTS.md` inside a
  `CLAUDE.md` is expanded or loaded as literal text is not documented.
- **Adapter rule:** `native` — Devin reads `AGENTS.md` directly; no adapter
  file is needed. When Claude Code is also selected, Devin loads its
  `CLAUDE.md` adapter too, as another always-on rule.
- **Native init command:** **None documented.** The CLI command reference
  lists no `/init`; `devin rules` only lists, shows and locates rules
  (`list`, `show <name>`, `paths`). This is "not documented," not
  confirmed absent.
- **Config locations:** User `~/.config/devin/config.json`
  (`%APPDATA%\devin\config.json`); project `.devin/config.json` ("Only
  `permissions`, `read_config_from`, and `hooks`") and a git-excluded
  `.devin/config.local.json`. Precedence, highest first: Organization/Team
  Settings (cannot be overridden) → session grants →
  `.devin/config.local.json` → `.devin/config.json` → user; a nested
  `.devin/` in a subdirectory beats its ancestors. MCP servers in
  `~/.config/devin/mcp_config.json`, `.devin/mcp_config.json` and
  `.devin/mcp_config.local.json` (moved out of `config.json` in CLI
  v3000.3.22). Devin Desktop keeps editor settings in its own `User/`
  folder under `~/Library/Application Support/Devin/`, `%APPDATA%\Devin\`
  or `~/.config/Devin/`.

Sources:
- Devin docs — Rules & AGENTS.md (file list, "treated identically", global rules, `.devin/` rules, other tools' rules): https://docs.devin.ai/cli/extensibility/rules (verified 2026-09-23)
- Devin docs — Configuration import (`read_config_from` keys and defaults): https://docs.devin.ai/cli/reference/configuration/read-config-from (verified 2026-09-23)
- Devin docs — Configuration precedence: https://docs.devin.ai/cli/reference/configuration/global-vs-local (verified 2026-09-23)
- Devin docs — Commands & flags (no `/init`; `devin rules`): https://docs.devin.ai/cli/reference/commands (verified 2026-09-23)
- Devin CLI changelog (stable) — v3000.4.16 nested `AGENTS.md`; 32 KiB rule cap; v3000.3.22 MCP files: https://docs.devin.ai/cli/changelog/stable (verified 2026-09-23)
- Devin docs — Devin Local (harness shared with Devin CLI; rules and `AGENTS.md`): https://docs.devin.ai/desktop/devin-local (verified 2026-09-23)
- Devin docs — AGENTS.md in Devin Desktop ("through the Devin CLI rules system"): https://docs.devin.ai/desktop/cascade/agents-md (verified 2026-09-23)
- Devin Desktop changelog (v3.0.12 rename; v3.9.19 Cascade removed): https://docs.devin.ai/desktop/changelog (verified 2026-09-23)
- Devin Desktop FAQ (editor settings paths): https://docs.devin.ai/desktop/devin-desktop-faq (verified 2026-09-23)
- Devin docs — AGENTS.md for the cloud Devin: https://docs.devin.ai/onboard-devin/agents-md (verified 2026-09-23)

## Fallback rule

Use this decision procedure for any agent not covered by the 14 sections
above, after researching it live from its official documentation — at most
**four fetches per agent** (the docs entry point, the context-file page,
the configuration page, one more for whatever is still missing); a field
still unresolved after that is recorded as "not documented" in the format
above, and if the adapter rule itself is still undecidable the run asks the
user (SKILL.md `## Edge cases`, "An agent research cannot resolve"):

1. If the agent reads `AGENTS.md` directly at session start in its default
   configuration → **`native`**. No adapter file is needed. Two limits: a
   configurable context-file list counts only when its default already
   includes `AGENTS.md` (Gemini CLI's does not); and when that direct
   reading is switched off by conditions the agent's own native file is not
   subject to — a feature flag, a provider, the mere presence of that native
   file (Claude Code) — use step 2 whenever the agent's own file can import,
   because an import reaches the agent in every session. A condition that
   blocks every project file alike (Codex ignores all project instructions
   in an untrusted project) does not count.
2. Else, if the agent's own native context file supports importing or
   including another file (an `@path` mention or similar include
   mechanism) → **`import-adapter`**. Instantiate
   `assets/adapter-template.md` as the agent's native file: the import
   line uses that agent's documented syntax verbatim, with any
   agent-specific additions below the import, each labeled with the
   agent's name.
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

None of the 14 agents in this matrix need the `full-copy` rule as of
2026-09-23 — Kiro and Antigravity, the two agents that looked like
candidates for it, both turned out to read `AGENTS.md` natively (see their
sections above). Keep this rule for agents outside the current target
list.
