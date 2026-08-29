---
type: Spec Summary
title: AGENTS.md standard and CLAUDE.md interop
description: >
  What the AGENTS.md open standard is (and is not), which agents read it
  natively, how per-tool precedence semantics differ, why Claude Code does not
  read it, the official interop options, and why this repository inverts the
  usual pattern (CLAUDE.md canonical, AGENTS.md as thin adapter).
tags:
  - agents-md
  - claude-code
  - claude-md
  - interop
  - spec
sources:
  - resource: https://agents.md
    title: AGENTS.md official site (spec, FAQ, supported tools)
  - resource: https://github.com/openai/agents.md
    title: openai/agents.md spec repository (GitHub)
  - resource: https://code.claude.com/docs/en/memory
    title: Claude Code docs — How Claude remembers your project (AGENTS.md section, @imports, symlink, /import, /init)
  - resource: https://github.com/anthropics/claude-code/issues/6235
    title: anthropics/claude-code issue #6235 — Support AGENTS.md (closed "completed" 2026-08-17; docs still show no native support)
  - resource: https://github.com/anthropics/claude-code/issues/34235
    title: anthropics/claude-code issue #34235 — support AGENTS.md as native context file
  - resource: https://learn.chatgpt.com/docs/agent-configuration/agents-md
    title: OpenAI Codex docs — AGENTS.md configuration (locations, precedence, size limits)
  - resource: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
    title: Gemini CLI docs — Provide context with GEMINI.md files (contextFileName, @file.md imports)
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
  - resource: https://github.com/MoonshotAI/kimi-cli
    title: MoonshotAI/kimi-cli — Kimi Code CLI (AGENTS.md via /init)
  - resource: https://gist.github.com/yurukusa/d36197848911f025add142abefcde685
    title: "Gist: Does Claude Code read AGENTS.md? Sync patterns for the #6235 cluster"
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:44:54Z
status: stable
---

# AGENTS.md standard and CLAUDE.md interop

## What AGENTS.md is

AGENTS.md is an open, tool-agnostic, plain-Markdown instruction file for
coding agents — "a README for agents." It was created collaboratively by
OpenAI Codex, Amp (Sourcegraph), Jules (Google), Cursor, and Factory, and is
now stewarded by the **Agentic AI Foundation under the Linux Foundation**.
The spec repo is `github.com/openai/agents.md` (MIT-licensed, ~24k stars);
the site reports 60,000+ open-source projects using the file.

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

Listed on agents.md as supporting it: Codex, Jules, Factory, Aider, goose,
opencode, Zed, Warp, VS Code, Devin, Junie, Amp, Cursor, RooCode, Gemini CLI,
Kilo Code, Phoenix, Semgrep, GitHub Copilot coding agent, Ona, Windsurf,
Augment Code. Kimi CLI (Moonshot) also generates and reads AGENTS.md via its
`/init` command.

Notable per-tool behavior:

| Tool | Behavior |
| --- | --- |
| **Codex** | Reads `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md` globally, then per-directory `AGENTS.override.md`/`AGENTS.md` from git root down to cwd, concatenated root-down (closer files later, overriding). Capped at `project_doc_max_bytes` (32 KiB default); fallback filenames configurable via `project_doc_fallback_filenames` in `~/.codex/config.toml`. No import syntax. |
| **Cursor** | Reads AGENTS.md at project root and in subdirectories; nested files combined, nearest wins. `.cursor/rules/*.mdc` remains for glob-scoped/manually-invoked rules. |
| **opencode** | Reads project AGENTS.md (falls back to CLAUDE.md for Claude Code compatibility) plus global `~/.config/opencode/AGENTS.md`. Explicitly "doesn't automatically parse file references in AGENTS.md" — extra files come via the `instructions` array in `opencode.json` (globs and URLs supported). |
| **Zed** | First-match-wins list: `.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.github/copilot-instructions.md`, `AGENT.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`. A stray `.cursorrules` silently shadows AGENTS.md. |
| **Gemini CLI** | Does **not** read AGENTS.md by default (default context file is GEMINI.md); requires opting in via the `contextFileName` setting. Issue google-gemini/gemini-cli#12345 requesting it by default was closed as not planned. Gemini CLI's context files are the only non-Claude ones with `@file.md` import syntax. |
| **ZCode** (Z.ai) | Reads **AGENTS.md only** — the engine's candidate-filename list is the single entry `["AGENTS.md"]` (verified in `/Applications/ZCode.app/Contents/Resources/glm/zcode.cjs`, v3.9.2). User default `~/.zcode/AGENTS.md` is injected first, then the workspace `<repo>/AGENTS.md` is searched from cwd upward to the project root and overrides it; hidden alternates `<repo>/.zcode/AGENTS.md` and `<repo>/.agents/AGENTS.md` also resolve. **CLAUDE.md is never read at runtime** — the Z.ai docs use it only during onboarding as a one-time migration source. |
| **Claude Code** | Does **not** read AGENTS.md at all — see below. |

### Precedence semantics are NOT standardized

Beyond "closest file wins," each tool implements its own merge model:

- **Claude Code** concatenates all discovered CLAUDE.md files broad-to-specific.
- **Codex** concatenates root-down, later (closer) files overriding.
- **Zed** and **opencode** use first-match-wins file *selection* (one file).
- **Cursor** merges nested files with nearest winning.

Do not assume instructions in a nested file behave the same across agents.

## Claude Code does not read AGENTS.md

The official Claude Code memory docs (code.claude.com/docs/en/memory) state
plainly: "Claude Code reads CLAUDE.md, not AGENTS.md." Native support was the
tracker's most-reacted feature request — anthropics/claude-code
**issue #6235**, 6,500+ reactions — which was **closed as "completed" on
2026-08-17**; yet the memory docs still state Claude Code reads CLAUDE.md,
not AGENTS.md (re-verified 2026-08-29), so no native AGENTS.md reading has
shipped. Successor issue #34235 remains open (verified 2026-08-29).

### Official interop options (from the Claude Code docs)

1. **Import adapter:** create a CLAUDE.md containing `@AGENTS.md` — Claude
   Code's `@file` import pulls the file in, and Claude-specific instructions
   can be appended below the import. `@file` imports work anywhere in
   CLAUDE.md, take relative or absolute paths, recurse up to 4 hops, are
   skipped inside code spans/fenced blocks, and load at launch.
2. **Symlink:** `ln -s AGENTS.md CLAUDE.md`. On Windows, symlinks need
   Administrator privileges or Developer Mode, so the docs prefer option 1
   there.
3. **One-time migration:** `/import` (Claude Code v2.1.213+) appends a copy
   of AGENTS.md into CLAUDE.md and carries over MCP servers, commands,
   subagents, and skills. Also, `/init` with `CLAUDE_CODE_NEW_INIT=1` reads
   AGENTS.md (plus `.devin/rules/`, Windsurf rules, and `.clinerules`) when
   generating CLAUDE.md; plain `/init` already reads Cursor and Copilot rules.

The docs' recommended *sync* pattern for multi-agent repos is AGENTS.md as
the canonical source of truth with CLAUDE.md as a thin `@AGENTS.md` adapter —
because the import capability exists only on the Claude side (Codex defines
no import syntax; opencode does not auto-parse `@` references; only Gemini
CLI supports `@file.md` imports, and it doesn't read AGENTS.md by default
anyway).

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

- What the "completed" closure of #6235 (2026-08-17) actually shipped — the
  official docs still show no native AGENTS.md reading as of 2026-08-29;
  successor issue #34235 remains open.
- Whether the Agentic AI Foundation formalizes precedence/merge semantics or
  an import syntax — currently each tool implements its own.
- Interop for the companion skills convention (`.agents/skills/` vs
  `.claude/skills/`): anthropics/claude-code#50778 was closed as "completed"
  on 2026-04-19, but as of 2026-08-29 the official Claude Code skills docs
  still list no `.agents/skills` discovery location, so the gap persists —
  outside the AGENTS.md file spec itself; see /agents/skill-discovery-matrix.md.

## Related documents

- /specs/agent-skills-spec.md — the Agent Skills (SKILL.md) specification
- /agents/skill-discovery-matrix.md — where each agent discovers skills
- /decisions/2026-08-29-repo-design.md — why CLAUDE.md is canonical here
