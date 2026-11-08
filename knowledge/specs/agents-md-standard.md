---
type: Spec Summary
title: AGENTS.md standard and CLAUDE.md interop
description: >
  What the AGENTS.md open standard is (and is not), which agents read it
  natively, how per-tool precedence semantics differ, when Claude Code reads
  it (natively since v2.1.277, but only without a CLAUDE.md and only in
  sessions that fetch feature flags), the official interop options, and why
  this repository inverts the usual pattern (CLAUDE.md canonical, AGENTS.md
  as thin adapter).
tags:
  - agents-md
  - claude-code
  - claude-md
  - interop
  - spec
sources:
  - resource: https://agents.md
    title: AGENTS.md official site (spec, FAQ, supported tools)
  - resource: https://github.com/agentsmd/agents.md
    title: agentsmd/agents.md spec repository (GitHub; moved from openai/agents.md, verified 2026-09-23)
  - resource: https://code.claude.com/docs/en/memory
    title: "Claude Code docs — How Claude remembers your project (AGENTS.md section: when it loads, Project instructions values, when unavailable, earlier workarounds, sharing one file; @imports, symlink, /import, /init; verified 2026-09-23)"
  - resource: https://code.claude.com/docs/en/env-vars
    title: "Claude Code docs — Environment variables (features that need feature-flag fetching, incl. AGENTS.md reading; first session after an install or upgrade; verified 2026-09-23)"
  - resource: https://code.claude.com/docs/en/commands
    title: "Claude Code docs — Commands (/init, /import; verified 2026-09-23)"
  - resource: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
    title: "Claude Code changelog — 2.1.277 \"Added AGENTS.md support\" (verified 2026-09-23)"
  - resource: https://registry.npmjs.org/@anthropic-ai/claude-code
    title: "npm registry — @anthropic-ai/claude-code publish times (2.1.277 published 2026-09-18)"
  - resource: https://github.com/anthropics/claude-code/issues/6235
    title: anthropics/claude-code issue #6235 — Support AGENTS.md (closed "completed" 2026-08-17; native reading shipped in 2.1.277)
  - resource: https://github.com/anthropics/claude-code/issues/34235
    title: anthropics/claude-code issue #34235 — support AGENTS.md as native context file alongside CLAUDE.md (open, verified 2026-09-23)
  - resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: OpenAI Codex docs — AGENTS.md configuration (locations, precedence, size limits)
  - resource: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
    title: Gemini CLI docs site — Provide context with GEMINI.md files (@file.md imports; source of the flat `contextFileName` name recorded here on 2026-08-29)
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md
    title: "gemini-cli repo docs — Context files (nested `context.fileName`, GEMINI.md hierarchy, @file.md imports; verified 2026-08-31)"
  - resource: https://github.com/google-gemini/gemini-cli/issues/12345
    title: google-gemini/gemini-cli issue #12345 — AGENTS.md by default (closed, not planned)
  - resource: https://opencode.ai/docs/rules/
    title: opencode docs — Rules (AGENTS.md, CLAUDE.md fallback, instructions config)
  - resource: https://zcode.z.ai/en/docs/agents
    title: ZCode docs — AGENTS.md (user + workspace resolution; CLAUDE.md only a one-time onboarding migration source)
  - resource: https://zed.dev/docs/ai/instructions
    title: Zed docs — Instructions (compatibility instruction files, first-match-wins)
  - resource: https://raw.githubusercontent.com/zed-industries/zed/main/docs/src/ai/rules.md
    title: Zed repo — rules.md ("Rules have been replaced by Skills and Instructions")
  - resource: https://cursor.com/docs/rules
    title: Cursor docs — Rules (AGENTS.md root and nested support)
  - resource: https://cursor.com/help/customization/rules
    title: "Cursor help — Rules (CLAUDE.md read the same way as AGENTS.md; verified 2026-09-23)"
  - resource: https://github.com/openai/codex/pull/39837
    title: "openai/codex PR #39837 — Ignore project instructions for untrusted projects (merged 2026-08-21)"
  - resource: https://github.com/google-gemini/gemini-cli/issues/28227
    title: "google-gemini/gemini-cli issue #28227 — AGENTS.md not in the default context.fileName (open, 2026-09-23)"
  - resource: https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/tools/memoryTool.ts
    title: "gemini-cli source — memoryTool.ts (context.fileName adds names to GEMINI.md)"
  - resource: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions
    title: "GitHub Docs — Copilot CLI custom instructions (AGENTS.md, CLAUDE.md, GEMINI.md merged; @ imports)"
  - resource: https://docs.devin.ai/cli/extensibility/rules
    title: "Devin docs — Rules & AGENTS.md (CLAUDE.md and others treated identically)"
  - resource: https://docs.devin.ai/desktop/changelog
    title: "Devin Desktop changelog — v3.0.12 \"Windsurf is now Devin Desktop\" (2026-06-02)"
  - resource: https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/customization/agents.md
    title: "Kimi Code docs — agents and instruction files (successor of the archived kimi-cli)"
  - resource: https://github.com/MoonshotAI/kimi-cli
    title: MoonshotAI/kimi-cli — archived Python Kimi CLI (AGENTS.md via /init)
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:44:54Z
verified:
  - by: claude-code/claude-opus-5-5
    at: "2026-09-23T07:11:13Z"
status: stable
---

# AGENTS.md standard and CLAUDE.md interop

## What AGENTS.md is

AGENTS.md is an open, tool-agnostic, plain-Markdown instruction file for
coding agents — "a README for agents." It was created collaboratively by
OpenAI Codex, Amp (Sourcegraph), Jules (Google), Cursor, and Factory, and is
now stewarded by the **Agentic AI Foundation under the Linux Foundation**.
The spec repo is `github.com/agentsmd/agents.md` (moved from
`openai/agents.md`, which now redirects; MIT-licensed, ~24.5k stars,
verified 2026-09-23); the site reports 60k+ open-source projects using the
file.

Key properties of the spec:

- **No required structure.** The FAQ states there are no mandated headings,
  fields, or syntax — "AGENTS.md is just standard Markdown."
- **No import syntax.** The standard defines no `@file` or include mechanism.
  (This asymmetry drives all the interop patterns below.)
- **Typical content** (official guidance): project overview, setup/build/test
  commands, code style, testing instructions, security considerations, and
  commit/PR conventions. Agents will attempt to run programmatic checks listed
  in the file and fix failures; treat it as living documentation.
- **Nested files** are supported for monorepos: "The closest AGENTS.md to the
  edited file wins; explicit user chat prompts override everything" (FAQ).
- Migration tip from the site for the older singular filename:
  `mv AGENT.md AGENTS.md && ln -s AGENTS.md AGENT.md`.

## Which tools read AGENTS.md natively

Listed on agents.md as supporting it (verified 2026-09-23): Codex, Jules,
Factory, Aider, goose, opencode, Zed, Warp, VS Code, Devin, Autopilot & Coded
Agents (UiPath), Junie, Amp, Cursor, RooCode, Gemini CLI, Kilo Code, Phoenix,
Semgrep, GitHub Copilot coding agent, Ona, Windsurf, Augment Code. The site
does not list Claude Code. Windsurf itself has since become Devin Desktop
(2026-06-02). Kimi Code CLI (Moonshot; successor of the archived Kimi CLI)
also reads AGENTS.md and generates it with `/init`.

Notable per-tool behavior (per-agent detail and sources:
/agents/agent-init-conventions.md):

| Tool | Behavior |
| --- | --- |
| **Codex** | Reads `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md` globally, then per-directory `AGENTS.override.md`/`AGENTS.md` from the project root down to cwd, concatenated root-down (closer files later, overriding). Capped at `project_doc_max_bytes` (32 KiB default); fallback filenames configurable via `project_doc_fallback_filenames` in `~/.codex/config.toml`. An untrusted project loads no project AGENTS.md (source, 2026-08-21). No import syntax. |
| **Cursor** | Reads AGENTS.md at project root and in subdirectories; nested files combined, nearest wins. Also reads a root CLAUDE.md "the same way it reads AGENTS.md". `.cursor/rules/*.mdc` remains for glob-scoped/manually-invoked rules. |
| **opencode** | Reads project AGENTS.md (falls back to CLAUDE.md for Claude Code compatibility) plus global `~/.config/opencode/AGENTS.md`. Explicitly "doesn't automatically parse file references in AGENTS.md" — extra files come via the `instructions` array in `opencode.json` (globs and URLs supported). |
| **Zed** | First-match-wins list: `.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`. A stray `.cursorrules` silently shadows AGENTS.md. |
| **Gemini CLI** | Does **not** read AGENTS.md by default (default context file is GEMINI.md); requires opting in via the nested `context.fileName` setting, which takes a list, **adds** to `GEMINI.md` rather than replacing it, and can include `AGENTS.md` (documented example `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`). This entry recorded the flat `contextFileName` from the docs site on 2026-08-29, consistent with Gemini CLI's move to a nested `settings.json` structure — no official changelog entry names the rename, so neither removal of the old key nor a compatibility alias is confirmed. Issue google-gemini/gemini-cli#12345 (AGENTS.md by default) was closed as not planned; the later bug report #28227 asking the same is open (2026-09-23). Supports `@file.md` imports. |
| **GitHub Copilot** | CLI, VS Code and the cloud agent all read AGENTS.md by default. The CLI merges AGENTS.md, CLAUDE.md and GEMINI.md with `.github/copilot-instructions.md` and expands `@path` in AGENTS.md and CLAUDE.md (not GEMINI.md); VS Code also reads CLAUDE.md by default; the cloud agent uses the nearest AGENTS.md. |
| **Devin** (formerly Windsurf) | Devin CLI and Devin Desktop's Devin Local read AGENTS.md automatically, and treat `AGENTS.local.md`, `AGENT.md`, `.windsurfrules` and CLAUDE.md "identically" as always-on rules. No import syntax is documented. |
| **ZCode** (Z.ai) | Reads **AGENTS.md only** — the engine's candidate-filename list is the single entry `["AGENTS.md"]` (verified in `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs`, v3.9.2). User default `~/.zcode/AGENTS.md` is injected first, then the workspace `<repo>/AGENTS.md` is searched from cwd upward to the project root and overrides it; hidden alternates `<repo>/.zcode/AGENTS.md` and `<repo>/.agents/AGENTS.md` also resolve. **CLAUDE.md is never read at runtime** — the Z.ai docs use it only during onboarding as a one-time migration source. |
| **Claude Code** | Reads AGENTS.md natively since **v2.1.277** (published 2026-09-18), but by default **only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above it**, and only in sessions that fetch feature flags — see below. |

### Precedence semantics are NOT standardized

Beyond "closest file wins," each tool implements its own merge model:

- **Claude Code** concatenates all discovered CLAUDE.md files broad-to-specific,
  and by default reads AGENTS.md only when no CLAUDE.md counts anywhere from
  the working directory up — the inverse of the opencode and Amp fallbacks
  (AGENTS.md first, CLAUDE.md only where AGENTS.md is missing).
- **Codex** concatenates root-down, later (closer) files overriding.
- **Zed** uses first-match-wins file *selection* (one file); **opencode**
  picks one filename (AGENTS.md, else CLAUDE.md) and then loads every file of
  that name from the working directory up to the worktree root.
- **Cursor** merges nested files with nearest winning.
- **GitHub Copilot CLI** merges everything it finds and "does not define a
  general precedence order"; **Devin** loads every rule file as always-on
  and documents no winner.

Do not assume instructions in a nested file behave the same across agents.

## Claude Code reads AGENTS.md — conditionally (since v2.1.277)

Until 2026-09 the Claude Code memory docs said plainly that Claude Code reads
CLAUDE.md, not AGENTS.md (last verified in that form 2026-08-29). The
tracker's most-reacted request, anthropics/claude-code **issue #6235**, was
closed as "completed" on 2026-08-17; the feature itself shipped in
**v2.1.277** (npm publish 2026-09-18), whose changelog reads: "Added
AGENTS.md support: in a project with no CLAUDE.md, Claude Code reads
AGENTS.md instead." Issue #34235 ("support AGENTS.md as a native context file
alongside CLAUDE.md") is still open (verified 2026-09-23). What the memory
docs now state (verified 2026-09-23):

- **When.** Under the default **Project instructions** value
  `claude-md-or-agents-md`, Claude reads AGENTS.md "only when you have no
  CLAUDE.md in your working directory or above it". A `CLAUDE.md`,
  `.claude/CLAUDE.md` or `CLAUDE.local.md` there counts; `~/.claude/CLAUDE.md`,
  the managed CLAUDE.md and `.claude/rules/` do not. The docs warn that
  adding a `CLAUDE.local.md` to a project that relies on AGENTS.md "stops
  Claude from reading AGENTS.md for you".
- **What.** Every `AGENTS.md` and `.claude/AGENTS.md` from the working
  directory upward at session start; a subdirectory's AGENTS.md on demand
  when Claude reads a file there. `@path` imports inside it are expanded.
  Never read: `AGENTS.local.md`, `AGENTS.override.md`, anything under
  `.agents/`.
- **Setting.** `claude-md-and-agents-md` reads both (each directory's
  CLAUDE.md first; an AGENTS.md already loaded through an import or symlink
  is skipped), `claude-md` reads CLAUDE.md only, `managed-only` loads only
  the managed CLAUDE.md and auto memory at launch. Set in `/config` or under
  `pluginConfigs` → `agents-md@builtin` in user, `--settings` or managed
  settings — ignored in project and local settings, so **a repository cannot
  change the value for its users**.
- **When unavailable** (CLAUDE.md only, and the setting is hidden): before
  v2.1.277; in sessions that do not fetch feature flags — Amazon Bedrock,
  Claude Platform on AWS, Google Cloud's Agent Platform, Microsoft Foundry, a
  Claude apps gateway, or `DISABLE_TELEMETRY` / `DO_NOT_TRACK` /
  `DISABLE_GROWTHBOOK` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set to a
  value that turns fetching off (env-vars docs); in the first session after
  an install or upgrade; with the built-in `agents-md` plugin disabled.
- **Differences from CLAUDE.md** when read through the setting:
  `InstructionsLoaded` hooks don't fire, `--add-dir` directories don't load
  their AGENTS.md, and an external `@path` import loads only if external
  imports were already approved for the project, with no prompt.

### Official interop options (from the Claude Code docs)

1. **Native reading** — nothing to add, when every session qualifies (above).
2. **Import adapter:** a CLAUDE.md containing `@AGENTS.md`, with
   Claude-specific instructions below the import. The docs prescribe it
   "when Claude isn't reading your AGENTS.md directly" — a project that also
   has a CLAUDE.md, the `claude-md` setting, or a session that can't load
   AGENTS.md — and state that "Keeping the import never makes Claude read
   AGENTS.md twice, whichever Project instructions value you use." `@file`
   imports work anywhere in CLAUDE.md, take relative or absolute paths,
   recurse up to 4 hops, are skipped inside code spans/fenced blocks, and
   load at launch.
3. **Symlink:** `ln -s AGENTS.md CLAUDE.md`. The Edit and Write tools refuse
   to write through the link (the refusal points Claude at AGENTS.md), and
   on Windows symlinks need Administrator privileges or Developer Mode and a
   clone without `core.symlinks` gets a one-line CLAUDE.md — so the docs say
   to use the import whenever anyone works on Windows.
4. **One-time migration:** `/import [codex|gemini|cursor]` (v2.1.213+;
   Cursor v2.1.265+; unavailable without feature-flag fetching) appends a
   one-time copy of instruction files such as AGENTS.md to the matching
   CLAUDE.md and carries over MCP servers, commands, subagents, and skills;
   `/init` offers it when it finds Codex or Gemini CLI configuration. Plain
   `/init` reads Cursor and Copilot rules; with `CLAUDE_CODE_NEW_INIT=1` it
   also reads AGENTS.md, `.devin/rules/`, Windsurf rules and `.clinerules`.

The docs list the earlier workarounds and what to do with each now: a
`CLAUDE.md` containing `@AGENTS.md` can stay (remove it only if it holds
nothing else *and* no session needs it); a CLAUDE.md that only tells Claude
in words to read AGENTS.md should be deleted or given an `@AGENTS.md` import;
a symlink can stay; a `SessionStart` hook that prints AGENTS.md should go, as
it would now add a second copy.

**Consequence for multi-agent repos:** the canonical-AGENTS.md +
thin-`@AGENTS.md`-CLAUDE.md pattern stays the robust one — native reading is
feature-flagged and switched off by any project CLAUDE.md or
CLAUDE.local.md, while the import works in every session and never
double-reads. Local confirmation (2026-09-23, Claude Code 2.1.280 with
`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` set in `~/.claude/settings.json`):
with only an AGENTS.md, a `claude -p` session saw no project instructions;
with a CLAUDE.md containing `@AGENTS.md` it saw them; `/import` reported it
"isn't available in this environment". The init-project skill keeps Claude
Code as an `import-adapter` for this reason
(/decisions/2026-09-23-claude-code-keeps-import-adapter.md).

## Why THIS repo inverts the usual pattern

This repository does the opposite: **CLAUDE.md is canonical** (the full
binding rule set at the repo root) and **AGENTS.md is the thin adapter**, a
short prose pointer telling non-Claude agents to read and follow CLAUDE.md.

Rationale:

- The project is **Claude Code-first** (primary agent; plugin packaging under
  `.claude-plugin/`), so the authoritative instructions live in the file the
  primary tool actually loads automatically.
- The usual direction (canonical AGENTS.md + `@AGENTS.md` in CLAUDE.md)
  exists because AGENTS.md has no import syntax — a canonical CLAUDE.md
  cannot be *imported* from AGENTS.md. But no import is needed: AGENTS.md is
  plain Markdown with no required structure, and agents reading it can follow
  a **prose pointer** ("read CLAUDE.md and follow it as written") by simply
  reading the referenced file with their file tools. CLAUDE.md's
  "For non-Claude agents" section closes the loop by mapping Claude-specific
  tooling to agent-agnostic git + scripts workflows.
- Tools that select a single rules file (Zed, opencode) find either file
  anyway — both list CLAUDE.md in their lookup chains — and tools that read
  only AGENTS.md get the pointer.
- Claude Code's native AGENTS.md reading (v2.1.277) changes nothing here:
  the root CLAUDE.md counts, so under the default setting Claude reads
  CLAUDE.md only and never the pointer; under `claude-md-and-agents-md` it
  would also read the pointer, which only repeats "read CLAUDE.md".
- **ZCode makes the adapter load-bearing, not merely acceptable.** It is a
  concrete, verified agent whose candidate-filename list is exactly
  `["AGENTS.md"]`: CLAUDE.md is never loaded automatically, and unlike Zed or
  opencode there is no CLAUDE.md fallback in its lookup chain at all. The only
  thing ZCode reads by itself is AGENTS.md, so the prose pointer in AGENTS.md
  is the *sole* mechanism that carries this repo's binding rules into a ZCode
  session — the agent follows it by reading CLAUDE.md with its own file tools.
  This is the case that turns the inverted layout from a defensible choice
  into a functional requirement: drop the pointer and ZCode gets nothing.

Full founding rationale: /decisions/2026-08-29-repo-design.md.

## Open questions

- *Resolved 2026-09-23:* what the "completed" closure of #6235 (2026-08-17)
  shipped — conditional native AGENTS.md reading in v2.1.277 (above).
  Issue #34235 remains open (verified 2026-09-23); why is not recorded here.
- Whether the Agentic AI Foundation formalizes precedence/merge semantics or
  an import syntax — currently each tool implements its own.
- Interop for the companion skills convention (`.agents/skills/` vs
  `.claude/skills/`): anthropics/claude-code#50778 was closed as "completed"
  on 2026-04-19, but as of 2026-09-23 the official Claude Code skills docs
  still list no `.agents/skills` discovery location (and the memory docs say
  nothing under `.agents/` is read as instructions), so the gap persists —
  outside the AGENTS.md file spec itself; see /agents/skill-discovery-matrix.md.

## Related documents

- /specs/agent-skills-spec.md — the Agent Skills (SKILL.md) specification
- /agents/skill-discovery-matrix.md — where each agent discovers skills
- /decisions/2026-08-29-repo-design.md — why CLAUDE.md is canonical here
- /decisions/2026-09-23-claude-code-keeps-import-adapter.md — why
  init-project still gives Claude Code a `@AGENTS.md` adapter
