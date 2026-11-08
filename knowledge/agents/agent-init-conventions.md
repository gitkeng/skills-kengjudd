---
type: Reference
title: Per-agent init conventions (context files, init commands, config)
description: >
  For each of the 14 agents targeted by the init-project skill: which
  instruction/context files it reads (paths + precedence), whether it also
  loads another agent's file (CLAUDE.md, GEMINI.md), import syntax, native
  init command and what it does to an existing AGENTS.md, and config file
  locations. Re-verified 2026-09-23. Feeds
  skills/init-project/references/agent-context-matrix.md.
tags: [agents, context-files, init, agents-md]
sources:
  - resource: https://code.claude.com/docs/en/memory
    title: "Claude Code docs — memory (CLAUDE.md locations, @imports, the AGENTS.md section, /init, /import)"
  - resource: https://code.claude.com/docs/en/commands
    title: "Claude Code docs — commands (/init, /import)"
  - resource: https://code.claude.com/docs/en/env-vars
    title: "Claude Code docs — features that need feature-flag fetching; first session after an install or upgrade"
  - resource: https://code.claude.com/docs/en/settings
    title: "Claude Code docs — settings scopes and precedence"
  - resource: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
    title: "Claude Code changelog — 2.1.277 AGENTS.md support"
  - resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: "OpenAI Codex docs — AGENTS.md"
  - resource: https://learn.chatgpt.com/docs/config-file/config-basic
    title: "OpenAI Codex docs — config file basics (precedence incl. cloud-managed defaults)"
  - resource: https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs
    title: "openai/codex — agents_md.rs (project root markers, untrusted projects, truncation)"
  - resource: https://github.com/openai/codex/pull/39837
    title: "openai/codex PR #39837 — Ignore project instructions for untrusted projects (merged 2026-08-21)"
  - resource: https://github.com/openai/codex/blob/main/codex-rs/tui/src/slash_command.rs
    title: "openai/codex — slash_command.rs (/init description)"
  - resource: https://github.com/openai/codex/blob/main/codex-rs/tui/assets/prompt_for_init_command.md
    title: "openai/codex — /init prompt (never overwrites an existing AGENTS.md)"
  - resource: https://github.com/openai/codex/issues/21932
    title: "openai/codex issue #21932 — let /init update an existing AGENTS.md (open)"
  - resource: https://cursor.com/docs/rules
    title: "Cursor docs — rules (AGENTS.md root and nested, .mdc rules, application order)"
  - resource: https://cursor.com/help/customization/rules
    title: "Cursor help — rules (CLAUDE.md read like AGENTS.md; ~/.cursor/rules; .cursorrules legacy)"
  - resource: https://cursor.com/docs/cli/using
    title: "Cursor docs — using the CLI (root AGENTS.md and CLAUDE.md)"
  - resource: https://cursor.com/docs/cli/reference/configuration
    title: "Cursor docs — CLI configuration"
  - resource: https://cursor.com/docs/cli/reference/parameters
    title: "Cursor docs — CLI parameters (generate-rule)"
  - resource: https://cursor.com/docs/cli/mcp
    title: "Cursor docs — CLI MCP (project → global → nested)"
  - resource: https://opencode.ai/docs/rules/
    title: "opencode docs — rules"
  - resource: https://opencode.ai/docs/config/
    title: "opencode docs — config"
  - resource: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/session/instruction.ts
    title: "anomalyco/opencode — instruction.ts (lookup order)"
  - resource: https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/command/index.ts
    title: "anomalyco/opencode — command/index.ts and /init template"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md
    title: "gemini-cli docs — context files"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/memoryTool.ts
    title: "gemini-cli source — memoryTool.ts (default filename; context.fileName adds names)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/memport.md
    title: "gemini-cli docs — memory import processor"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/commands/init.ts
    title: "gemini-cli source — init.ts (existing GEMINI.md left unchanged)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/configuration.md
    title: "gemini-cli docs — configuration reference"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/trusted-folders.md
    title: "gemini-cli docs — trusted folders"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/changelogs/latest.md
    title: "gemini-cli changelog — v0.60.0"
  - resource: https://github.com/google-gemini/gemini-cli/issues/28227
    title: "gemini-cli issue #28227 — AGENTS.md not in the default context.fileName (open)"
  - resource: https://zed.dev/docs/ai/instructions
    title: "Zed docs — instructions"
  - resource: https://github.com/zed-industries/zed/blob/main/docs/src/configuring-zed.md
    title: "Zed docs source — configuring Zed (published page now redirects)"
  - resource: https://kiro.dev/docs/steering/
    title: "Kiro docs — steering"
  - resource: https://kiro.dev/docs/custom-agents/configuration-reference/
    title: "Kiro docs — custom agent configuration reference (default resources inherited)"
  - resource: https://kiro.dev/docs/cli/v3/new-features/
    title: "Kiro docs — CLI v3 new features"
  - resource: https://kiro.dev/docs/configuration/
    title: "Kiro docs — configuration scopes"
  - resource: https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/customization/agents.md
    title: "Kimi Code docs — agents and instruction files"
  - resource: https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core-v2/src/agent/profile/context.ts
    title: "Kimi Code source — context.ts (AGENTS.md load order)"
  - resource: https://github.com/MoonshotAI/kimi-code/blob/main/packages/agent-core-v2/src/features/sessionInit/profile/init.md
    title: "Kimi Code source — /init prompt"
  - resource: https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/configuration/overrides.md
    title: "Kimi Code docs — overrides (no project-level config)"
  - resource: https://github.com/MoonshotAI/kimi-cli
    title: "MoonshotAI/kimi-cli (archived; 1.52.0 installs Kimi Code)"
  - resource: https://ampcode.com/docs/customize/agents-md
    title: "Amp docs — AGENTS.md"
  - resource: https://ampcode.com/docs/cli/settings
    title: "Amp docs — CLI settings"
  - resource: https://goose-docs.ai/docs/guides/context-engineering/using-goosehints/
    title: "goose docs — using goosehints (@ includes, nested hints)"
  - resource: https://goose-docs.ai/docs/guides/environment-variables/
    title: "goose docs — environment variables (CONTEXT_FILE_NAMES default)"
  - resource: https://goose-docs.ai/docs/guides/config-files/
    title: "goose docs — config files"
  - resource: https://github.com/aaif-goose/goose
    title: "aaif-goose/goose (moved from block/goose; AAIF at the Linux Foundation)"
  - resource: https://zcode.z.ai/en/docs/agents
    title: "ZCode docs — AGENTS.md"
  - resource: https://zcode.z.ai/en/docs/subagents
    title: "ZCode docs — subagents (injectAgentsMd)"
  - resource: https://zcode.z.ai/en/docs/commands
    title: "ZCode docs — commands"
  - resource: https://zcode.z.ai/en/docs/mcp-services
    title: "ZCode docs — MCP servers"
  - resource: file:///Applications/ZCode.app/Contents/Resources/glm/zcode.cjs
    title: "Local inspection — ZCode 3.14.3 engine (built-in /init, AGENTS.md lookup), 2026-09-23"
  - resource: https://antigravity.google/docs/rules-workflows/
    title: "Antigravity docs — rules"
  - resource: https://antigravity.google/docs/cli/gcli-migration/
    title: "Antigravity docs — migration from Gemini CLI"
  - resource: https://antigravity.google/docs/cli/best-practices/
    title: "Antigravity docs — CLI best practices"
  - resource: https://antigravity.google/docs/migration/workflows-to-skills/
    title: "Antigravity docs — workflows to skills (retired 2026-11-01)"
  - resource: https://antigravity.google/changelog
    title: "Antigravity changelog (IDE v1.20.5; 2.0 v2.11.0, v2.12.0)"
  - resource: https://antigravity.google/docs/slash-commands/
    title: "Antigravity docs — slash commands"
  - resource: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
    title: "GitHub Docs — custom instructions for Copilot CLI"
  - resource: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
    title: "GitHub Docs — Copilot CLI command reference"
  - resource: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference
    title: "GitHub Docs — Copilot CLI configuration directory"
  - resource: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
    title: "GitHub Docs — repository custom instructions (cloud agent)"
  - resource: https://code.visualstudio.com/docs/agents/reference/ai-settings
    title: "VS Code docs — AI settings reference"
  - resource: https://github.com/microsoft/vscode/blob/main/extensions/copilot/assets/prompts/skills/init/SKILL.md
    title: "microsoft/vscode — built-in init skill"
  - resource: https://docs.devin.ai/cli/extensibility/rules
    title: "Devin docs — rules & AGENTS.md"
  - resource: https://docs.devin.ai/cli/reference/configuration/read-config-from
    title: "Devin docs — configuration import (read_config_from defaults)"
  - resource: https://docs.devin.ai/cli/reference/configuration/global-vs-local
    title: "Devin docs — configuration precedence"
  - resource: https://docs.devin.ai/desktop/changelog
    title: "Devin Desktop changelog (Windsurf renamed 2026-06-02; Cascade removed 2026-09-08)"
  - resource: https://docs.devin.ai/desktop/devin-local
    title: "Devin docs — Devin Local (shares the Devin CLI harness)"
generated:
  by: claude-code/claude-opus-5-5
  at: "2026-09-23T07:11:13Z"
status: stable
stale_after: "2026-10-23"
---

# Per-agent init conventions

What each of the 14 agents in the `init-project` target list actually loads
at session start, how it merges those files, whether it also loads another
agent's file, whether it can import other files, whether it can generate its
own context file, and where its configuration lives. Every section answers
the same four questions:

- **(a) Instruction/context files** — filenames, paths, precedence/merge model
- **(b) Import syntax** — yes/no, and the exact syntax
- **(c) Native init command** — a built-in command that writes the context
  file, and what it does to an `AGENTS.md` that already exists
- **(d) Config file locations** — where the agent's own settings live

The skill's copy of these facts, with a source line per fact, is
`skills/init-project/references/agent-context-matrix.md`; this document
keeps the same facts in comparison form plus what only local inspection
showed. The AGENTS.md standard itself is in
[/specs/agents-md-standard.md](/specs/agents-md-standard.md), skill
discovery paths in
[/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md).
Unresolved questions are in [Known gaps](#known-gaps) — none of them are
guessed.

All URL-backed facts below were re-verified **2026-09-23**; the previous
pass was 2026-08-31, and what changed between them is logged in
[/log.md](/log.md). Facts from source code are marked *(source)*, facts
from the installed app *(local inspection)*.

## Claude Code

- **(a)** `CLAUDE.md`, and `AGENTS.md` only when no `CLAUDE.md` counts. Load
  order, broadest to most specific: managed policy
  (`/Library/Application Support/ClaudeCode/CLAUDE.md` on macOS,
  `/etc/claude-code/CLAUDE.md` on Linux/WSL,
  `C:\Program Files\ClaudeCode\CLAUDE.md` on Windows) → user
  `~/.claude/CLAUDE.md` → project `./CLAUDE.md` **or** `./.claude/CLAUDE.md` →
  local `./CLAUDE.local.md`; concatenated root-down, subdirectory files on
  demand; `.claude/rules/*.md` and `~/.claude/rules/` at launch or per
  `paths:` glob. **Native AGENTS.md since v2.1.277** (npm publish
  2026-09-18): under the default **Project instructions** value
  (`claude-md-or-agents-md`) every `AGENTS.md` and `.claude/AGENTS.md` from
  the working directory up is read *only when* no `CLAUDE.md`,
  `.claude/CLAUDE.md` or `CLAUDE.local.md` exists there; the setting lives in
  user, `--settings` or managed settings only. Unavailable before 2.1.277,
  without feature-flag fetching (Bedrock, Google Cloud's Agent Platform,
  Foundry, Claude Platform on AWS, a Claude apps gateway, telemetry/traffic
  opt-outs), in the first session after an install or upgrade, or with the
  built-in `agents-md` plugin disabled. Full detail:
  [/specs/agents-md-standard.md](/specs/agents-md-standard.md).
- **(b)** **Yes** — `@path/to/import`; relative to the importing file,
  absolute allowed, four hops deep, skipped inside code, expanded at launch;
  also expanded inside an `AGENTS.md` read natively.
- **(c)** **Yes** — `/init` "Initialize project with a `CLAUDE.md` guide";
  an existing CLAUDE.md gets suggested improvements, not an overwrite. When
  it finds Codex or Gemini CLI configuration it offers `/import`, which
  appends a one-time copy of `AGENTS.md` to `CLAUDE.md` — beside an
  `@AGENTS.md` import that copy repeats the content and goes stale.
  `/import` needs feature-flag fetching; on this maintainer's machine it
  reported "/import isn't available in this environment" (2026-09-23).
- **(d)** Settings precedence, highest first: managed → `--settings` →
  `.claude/settings.local.json` → `.claude/settings.json` →
  `~/.claude/settings.json`. Auto memory at
  `~/.claude/projects/<project>/memory/` (`autoMemoryDirectory` relocates it).
- **Local check, 2026-09-23** (Claude Code 2.1.280,
  `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set): with only an `AGENTS.md`,
  `claude -p` saw no project instructions; with a `CLAUDE.md` containing
  `@AGENTS.md` it did. See
  [/decisions/2026-09-23-claude-code-keeps-import-adapter.md](/decisions/2026-09-23-claude-code-keeps-import-adapter.md).

## Codex

- **(a)** `AGENTS.md`. Global `~/.codex/AGENTS.override.md` or
  `~/.codex/AGENTS.md`, then per-directory `AGENTS.override.md`/`AGENTS.md`
  from the project root (nearest parent with a `project_root_markers` entry,
  default `.git`) down to the working directory, concatenated root-down;
  nothing below the working directory. **An untrusted project loads no
  project `AGENTS.md`** *(source; PR #39837, merged 2026-08-21 — the docs do
  not say so)*. Project files share `project_doc_max_bytes` (32 KiB); empty
  files are skipped and the file crossing the limit is truncated with only a
  log message *(source)*. Fallback names via `project_doc_fallback_filenames`.
- **(b)** **No** import mechanism.
- **(c)** **Yes** — `/init` "create an AGENTS.md file with instructions for
  Codex"; its prompt forbids overwriting or modifying an existing
  `AGENTS.md` (a model instruction, not a code check). Issue #21932 (update
  an existing file) is still open.
- **(d)** `config.toml`, highest first: CLI flags/`--config` → project
  `.codex/config.toml` (trusted projects only) → profile files → user
  `~/.codex/config.toml` → cloud-managed defaults for the signed-in
  workspace → system `/etc/codex/config.toml` → built-in defaults; managed
  machines may add `requirements.toml`; `CODEX_HOME` relocates `~/.codex`.

## Cursor

- **(a)** `AGENTS.md` at the root and in subdirectories, combined, nearest
  wins. **Also reads a root `CLAUDE.md` "the same way it reads `AGENTS.md`"**,
  always applied; the CLI reads root `AGENTS.md` and `CLAUDE.md`.
  `.cursor/rules/*.mdc` (`alwaysApply`, `description`, `globs`; plain `.md`
  ignored); `.cursorrules` is legacy. User Rules in the UI (synced) or
  `~/.cursor/rules` (local); Team Rules in the dashboard. Order: Team →
  Project → User.
- **(b)** `@filename` inside `.mdc` rules; inside `AGENTS.md`/`CLAUDE.md`
  not documented.
- **(c)** **No `/init`**, no AGENTS.md generator; rule generators only
  (`/create-rule`, CLI `agent generate-rule`, palette **New Cursor Rule**).
- **(d)** `~/.cursor/cli-config.json` (`CURSOR_CONFIG_DIR`,
  `$XDG_CONFIG_HOME/cursor/` on Linux/BSD); per-project permissions only, in
  `.cursor/cli.json`; MCP `.cursor/mcp.json` and `~/.cursor/mcp.json`
  (project → global → nested).

## opencode

- **(a)** `AGENTS.md`, falling back to `CLAUDE.md` (and a deprecated
  `CONTEXT.md`), plus `~/.config/opencode/AGENTS.md` and, unless disabled,
  `~/.claude/CLAUDE.md`. Docs: "The first matching file wins in each
  category." *(source)* From the working directory up to the worktree root
  it takes the first filename found anywhere on the path and loads every
  file of that name — so `CLAUDE.md` only when no `AGENTS.md` exists on the
  path. Subdirectory files attach when the agent reads files there.
- **(b)** **No** — "doesn't automatically parse file references"; the
  `instructions` array in `opencode.json` adds paths, globs, URLs.
- **(c)** **Yes** — `/init` ("guided AGENTS.md setup"): "Create or update
  `AGENTS.md` for this repository." — edits an existing file.
- **(d)** Merged, lowest to highest: remote `.well-known/opencode` → global
  `~/.config/opencode/opencode.json` → `OPENCODE_CONFIG` → project
  `opencode.json` → `.opencode/` → `OPENCODE_CONFIG_CONTENT` → managed files
  → macOS managed preferences; `OPENCODE_CONFIG_DIR` loads after the global
  and `.opencode` directories; TUI settings in `tui.json`.

## Gemini CLI

- **(a)** `GEMINI.md` by default; `context.fileName` **adds** names in front
  of `GEMINI.md` and can include `AGENTS.md`. Not read by default: #12345
  closed not planned (2026-05-08), #28227 open, nothing merged. Global
  `~/.gemini/GEMINI.md`, workspace directories and parents, plus
  just-in-time scanning up to a trusted root; all concatenated.
- **(b)** **Yes** — `@file.md` (relative or absolute; a bare `@AGENTS.md`
  passes validation); ignored inside code spans and blocks.
- **(c)** **Yes** — `/init` "Analyzes the project and creates a tailored
  GEMINI.md file"; with a `GEMINI.md` present it stops: "No changes were
  made." `/memory show|list|reload` (alias `refresh`).
- **(d)** Four `settings.json` layers: system defaults → user → workspace →
  system overrides; `GEMINI_CLI_SYSTEM_SETTINGS_PATH`,
  `GEMINI_CLI_SYSTEM_DEFAULTS_PATH`, `GEMINI_CLI_HOME`. Since v0.60.0
  (2026-09-15) the system files are skipped unless securely owned. A
  project `.gemini/settings.json` is not loaded from an untrusted folder
  while folder trust is on.

## Zed

- **(a)** First-match-wins list: `.rules`, `.cursorrules`, `.windsurfrules`,
  `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`, `AGENTS.md`,
  `CLAUDE.md`, `GEMINI.md` — a stray `.cursorrules` shadows `AGENTS.md`.
  Personal `~/.config/zed/AGENTS.md`; project overrides personal. The list
  governs the Zed Agent only; External Agents and Terminal Threads "may read
  their own native instruction files directly".
- **(b)** **No** import mechanism *(source: loaded as plain text)*.
- **(c)** **None documented.**
- **(d)** `~/.config/zed/settings.json` (Linux also
  `$XDG_CONFIG_HOME/zed/`), `%APPDATA%\Zed\settings.json`; `.zed/settings.json`
  (also in subdirectories); `keymap.json`. The published
  `zed.dev/docs/configuring-zed` now redirects to the all-settings
  reference, which omits these paths — cite the docs source file.

## Kiro

- **(a)** Steering: `.kiro/steering/*.md` and `~/.kiro/steering/`; the three
  foundation files; inclusion `always` / `fileMatch` / `manual` / `auto`.
  `AGENTS.md` is supported, "always included", no inclusion modes. Scopes
  merge; Agent > Project > Global. **Two official contradictions:** custom
  agents do not auto-include steering (steering page) vs. inherit steering,
  skills and `AGENTS.md` by default unless
  `chat.disableInheritingDefaultResources` (configuration reference); no
  inclusion modes on the CLI (steering page) vs. front-matter inclusion
  modes in the opt-in CLI v3. Configuration Sync can load cloud steering
  into new local CLI sessions.
- **(b)** **Yes, in steering** — `#[[file:relative/path]]`.
- **(c)** **No slash command**; the IDE's **Generate Steering Docs** button
  writes the foundation files, not `AGENTS.md`.
- **(d)** `~/.kiro/` (`settings/mcp.json`, `settings/permissions.yaml`,
  `settings/cli.json`, `agents/`, `steering/`, `skills/`, `hooks/`,
  `powers/`) and `.kiro/` (plus `.kiro/settings/cli.json` overrides);
  project permissions per user at
  `~/.kiro/workspace-roots/<hash>/permissions.yaml`; deny wins at any
  scope; `KIRO_HOME`; `/config` in V3 sessions.

## Kimi CLI

Now **Kimi Code CLI** (`MoonshotAI/kimi-code`). The Python `kimi-cli`
repository is archived; its 1.52.0 (2026-09-22) makes a bare `kimi` install
Kimi Code, and its README says existing installations "will stop working".

- **(a)** `AGENTS.md`: global `$KIMI_CODE_HOME/AGENTS.md` (default
  `~/.kimi-code/AGENTS.md`), cross-tool `~/.agents/AGENTS.md`, project
  `.kimi-code/AGENTS.md` or `AGENTS.md`. *(source)* Read in that order,
  project files per directory from the git root down to the working
  directory (lowercase `agents.md` accepted), all joined, a warning above a
  recommended 32 KiB total; no `CLAUDE.md`, `GEMINI.md` or `.kimi/AGENTS.md`.
- **(b)** **Not documented**; *(source)* text is inserted as-is.
- **(c)** **Yes** — `/init` "Analyze the current codebase and generate
  `AGENTS.md`"; *(source)* its prompt writes the root file "replacing the
  file's previous content" after carrying forward what is still accurate —
  it rewrites an existing `AGENTS.md`.
- **(d)** One user-level `~/.kimi-code/config.toml` (+ `tui.toml`); "no
  project-level config file mechanism"; `KIMI_CODE_HOME` relocates it; MCP
  in `~/.kimi-code/mcp.json` or a project `.kimi-code/mcp.json`. `~/.kimi/`
  belongs to the archived CLI and is read only to migrate.

## Amp

- **(a)** `AGENTS.md` in the working directory and parents up to `$HOME`,
  subtree files on access, `$HOME/.config/amp/AGENTS.md`,
  `$HOME/.config/AGENTS.md`, system-wide files, a personal Global AGENTS.md
  in the web app, and a workspace-wide Global AGENTS.md set by admins
  (included before personal and repository guidance). `AGENT.md` or
  `CLAUDE.md` only where a directory has no `AGENTS.md`.
- **(b)** **Yes** — `@`-mentions (relative, absolute, `@~/`, globs); a
  mentioned file with `globs` frontmatter loads only after a matching file
  is read.
- **(c)** **None documented**; Amp "offers to generate an `AGENTS.md` file
  for you if none exists"; `agents-md list` shows what is loaded.
- **(d)** `~/.config/amp/settings.json(c)`, workspace `.amp/settings.json(c)`
  (overrides user), `--settings-file`, managed `managed-settings.json`
  per OS, and for Enterprise a server-side managed document the local file
  outranks; keys prefixed `amp.`.

## Goose

Moved from `block/goose` to `aaif-goose/goose` (Agentic AI Foundation, Linux
Foundation); docs at `goose-docs.ai`.

- **(a)** `AGENTS.md` and `.goosehints` at each level, from the working
  directory up to the repository root, nested ones on access; global
  `~/.config/goose/.goosehints`, local beats global. `CONTEXT_FILE_NAMES`
  sets the list; its default order is stated both ways
  (`["AGENTS.md", ".goosehints"]` in the hints guide,
  `[".goosehints", "AGENTS.md"]` in the environment-variables reference).
- **(b)** **Yes** — `@` "Automatically includes the file content"; plain
  paths are read on demand. *Correction:* recorded as "No" until 2026-09-23.
- **(c)** **None** (`goose term init` prints a shell script).
- **(d)** `~/.config/goose/config.yaml` and siblings
  (`%APPDATA%\Block\goose\config\` on Windows); environment variables beat
  the config file, which beats defaults.

## ZCode

- **(a)** `AGENTS.md` only: `~/.zcode/AGENTS.md` then the workspace
  `AGENTS.md`, no merging across levels, no child scan, no rule selection by
  task; subagents inject both since v3.7.1 (`injectAgentsMd: false` opts
  out). `CLAUDE.md` is a one-time onboarding source only. *(local
  inspection, 3.14.3)* The candidate list is exactly `["AGENTS.md"]`; the
  workspace file is the first found walking up from the working directory
  to the git root; each file is read up to 100 KiB.
- **(b)** **No** — explicitly.
- **(c)** **Yes, undocumented.** The commands page still lists `/goal` and
  `/compact` only; *(local inspection, 3.14.3)* the engine ships `/init`
  ("Create or update workspace AGENTS.md instructions.", `/init [notes]`),
  whose prompt edits an existing root `AGENTS.md` "instead of replacing it
  wholesale", creates one when absent, never writes `~/.zcode/AGENTS.md`,
  and stops if `.zcode/AGENTS.md` or `.agents/AGENTS.md` exists.
- **(d)** `~/.zcode/v2/config.json` (providers), `~/.zcode/cli/config.json`
  (`mcp.servers`), workspace `.zcode/config.json`, `.agents/mcp.json` as a
  fallback only; a user MCP server beats a project one of the same name.

## Antigravity

- **(a)** `GEMINI.md` and `AGENTS.md` in the active directory (migration
  page; CLI best practices); the IDE added `AGENTS.md` in v1.20.5
  (2026-03-09). Global `~/.gemini/GEMINI.md` on every product, plus
  `~/.gemini/antigravity-cli/rules/` on the CLI. Rules in `.agents/rules`
  (12,000 characters each, four activation modes). Workflows are IDE-only
  and retire on 2026-11-01. `AGENTS.md`-vs-`GEMINI.md` precedence and
  nested discovery are not documented.
- **(b)** **Yes** — `@path/to/file` inside `AGENTS.md` and rule files
  (2.0 changelog v2.11.0 only).
- **(c)** **None** (`/learn` distills rules or skills; `/boost` and
  `/migrate-workflows` are new).
- **(d)** `~/.gemini/config/` (`config.json`, `mcp_config.json`, agents),
  workspace `.agents/` (MCP, agents, skills), CLI
  `~/.gemini/antigravity-cli/settings.json`; `~/.gemini/settings.json` is
  legacy Gemini CLI.

## GitHub Copilot

- **(a)** `AGENTS.md` by default on every surface. **CLI:** merges
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`,
  `.github/instructions/**/*.instructions.md` and user files, with no
  general precedence (identical duplicates removed). **VS Code** (Local
  harness): root `AGENTS.md` (`chat.useAgentsMdFile` true), nested only with
  `chat.useNestedAgentsMdFiles`, `CLAUDE.md` (`chat.useClaudeMdFile` true),
  `.github/copilot-instructions.md`, `*.instructions.md`. **Cloud agent:**
  `**/AGENTS.md`, nearest wins; a root `CLAUDE.md` or `GEMINI.md`
  "alternatively". Personal > repository > organization on GitHub.com, all
  provided.
- **(b)** **CLI:** `@relative/path` in `AGENTS.md`, `CLAUDE.md`,
  `copilot-instructions.md` — not in `GEMINI.md`. **VS Code:** Markdown
  links, auto-added only with `chat.includeReferencedInstructions`. Cloud
  agent: not documented.
- **(c)** **CLI:** `copilot init` / `/init` write or update
  `.github/copilot-instructions.md`. **VS Code:** `/init`; its built-in skill
  prefers `AGENTS.md` and updates an existing one. **Cloud agent:** an
  onboarding prompt opens a PR adding `.github/copilot-instructions.md`.
- **(d)** CLI `~/.copilot` (`COPILOT_HOME`), `.github/copilot/settings.json`
  and `.local.json`, MCP in `~/.copilot/mcp-config.json`, `.mcp.json`,
  `.github/mcp.json`; VS Code `settings.json`/`.vscode/settings.json`,
  `.vscode/mcp.json`; cloud agent `copilot-setup-steps.yml` and repository
  settings.

## Devin

Formerly **Windsurf**: renamed Devin Desktop on 2026-06-02; its Cascade agent
was removed on 2026-09-08, leaving Devin Local, which shares the Devin CLI
harness.

- **(a)** `AGENTS.md` read automatically; `AGENTS.local.md`, `AGENT.md`,
  `.windsurfrules` and `CLAUDE.md` are "treated identically" as always-on
  rules; nested files on access; global `~/.config/devin/AGENTS.md` and
  `~/.claude/CLAUDE.md`; `.devin/rules/`, `.windsurf/rules/`,
  `.cursor/rules/`. No documented winner on conflict. 32 KiB cap per
  always-on file. `read_config_from.agents_standard` / `.claude` (default
  true) switch families off.
- **(b)** **Not documented.**
- **(c)** **None documented** (`devin rules list|show|paths`).
- **(d)** `~/.config/devin/config.json`, `.devin/config.json`,
  `.devin/config.local.json`; Organization/Team > session > local > project
  > user; MCP in `mcp_config.json` files.

## Cross-cutting summary

| Agent | Reads AGENTS.md natively | Also loads another agent's file | Import syntax | Native init command → effect on an existing AGENTS.md |
|---|---|---|---|---|
| Claude Code | Yes, conditionally (no CLAUDE.md; feature flag) | — | `@path` (4 hops) | `/init` writes CLAUDE.md; offers `/import`, which copies AGENTS.md into CLAUDE.md |
| Codex | Yes (trusted projects) | — | No | `/init` refuses to touch it (prompt-level) |
| Cursor | Yes | root `CLAUDE.md` | `@file` in `.mdc` only | none |
| opencode | Yes | `CLAUDE.md` only without AGENTS.md | No | `/init` updates it |
| Gemini CLI | Only via `context.fileName` | — | `@file.md` | `/init` writes GEMINI.md; no-op if one exists |
| Zed | Yes (first match) | only without AGENTS.md | No | none |
| Kiro | Yes (always-included steering) | — | `#[[file:…]]` in steering | none (IDE button writes steering) |
| Kimi CLI (Kimi Code) | Yes | — | Not documented | `/init` rewrites it |
| Amp | Yes | `CLAUDE.md` only without AGENTS.md | `@path`, `@~/`, globs | none (offers one if missing) |
| Goose | Yes (with `.goosehints`) | — | `@path` | none |
| ZCode | Yes (only AGENTS.md) | — | No (explicitly) | `/init` edits it (undocumented, 3.14.3) |
| Antigravity | Yes (with GEMINI.md) | root `GEMINI.md` | `@path/to/file` | none |
| GitHub Copilot | Yes | `CLAUDE.md`, `GEMINI.md` | CLI `@path`; VS Code links | CLI writes copilot-instructions.md; VS Code `/init` updates it |
| Devin | Yes | `CLAUDE.md` | Not documented | none |

What this means for `init-project`:

- **Only Claude Code and Gemini CLI get an import adapter** — Gemini CLI
  because it does not read `AGENTS.md` by default, Claude Code because its
  native reading is conditional where the import is not.
- **Adapters are read by other agents.** Cursor, GitHub Copilot and Devin
  load a root `CLAUDE.md`; Antigravity and Copilot load a root `GEMINI.md`.
  Adapter notes therefore carry their agent's name (the template does it),
  and Copilot CLI, which expands `@AGENTS.md` inside `CLAUDE.md`, loads
  `AGENTS.md` twice when Claude Code is also selected.
- **The canonical file must be self-contained.** Codex, opencode, Zed and
  ZCode expand no imports; Cursor, Kimi Code, Kiro (outside its steering
  syntax) and Devin document none for `AGENTS.md`; VS Code Copilot follows
  links only with a setting that is off by default. An `AGENTS.md` that
  delegates substance to `@`-referenced files loses it on four agents for
  certain and on up to five more.
- **Four init commands rewrite or edit `AGENTS.md`** — opencode, Kimi Code,
  ZCode and VS Code Copilot — so their "do not run `/init` here" note
  matters; Codex's refuses by prompt, the others write a different file.

## Known gaps

Unresolved from official sources as of 2026-09-23 — not assumptions:

- **Antigravity:** `AGENTS.md`-vs-`GEMINI.md` precedence; nested or parent
  `AGENTS.md` discovery; whether `@` imports work inside `AGENTS.md` on the
  CLI and IDE (only the 2.0 changelog says so); `/learn` names
  `.antigravity/rules.md` as a target while the Rules page uses
  `.agents/rules/`.
- **Gemini CLI:** whether a file both imported by `GEMINI.md` and listed in
  `context.fileName` loads once; when the flat `contextFileName` became
  `context.fileName` (no changelog entry names the rename).
- **Cursor and Devin:** whether `@AGENTS.md` inside a `CLAUDE.md` is
  expanded — which decides whether the Claude Code adapter makes them load
  `AGENTS.md` twice.
- **GitHub Copilot:** the Copilot harness in VS Code documents no discovery
  rules; the CLI pages disagree on discovery scope ("standard locations" vs
  "Git root and cwd") and on absolute import paths; the cloud agent's
  handling of root plus nested `AGENTS.md`, and of `AGENTS.md` next to
  `CLAUDE.md`/`GEMINI.md`, is not stated.
- **Devin:** rule order and conflict resolution (same directory, root vs
  nested, global vs project); whether the 32 KiB cap still holds after the
  later "tighter injection limits".
- **Goose:** the default `CONTEXT_FILE_NAMES` order (the docs disagree) and
  which of `AGENTS.md`/`.goosehints` wins in one directory.
- **Kiro:** the two contradictions in (a) — custom-agent steering
  inheritance and CLI inclusion modes.
- **ZCode:** `/init` is found only by local inspection; no official page or
  changelog entry names it or the release that added it. The split between
  its two user config files has no documented rule.
- **Codex:** the untrusted-project rule exists only in source and the
  merged PR, not in the docs.
- **Zed, Amp, Cursor, Devin, Antigravity, Kiro:** absence of an
  `AGENTS.md` generator is "not documented", not confirmed.

## Related documents

- [/specs/agents-md-standard.md](/specs/agents-md-standard.md) — the
  AGENTS.md standard, per-tool behavior, and Claude Code's conditional
  native reading
- [/decisions/2026-09-23-claude-code-keeps-import-adapter.md](/decisions/2026-09-23-claude-code-keeps-import-adapter.md)
  — why Claude Code still gets a `@AGENTS.md` adapter
- [/agents/skill-discovery-matrix.md](/agents/skill-discovery-matrix.md) —
  where the same agents discover Agent Skills
- [/specs/agent-skills-spec.md](/specs/agent-skills-spec.md) — the SKILL.md
  format
