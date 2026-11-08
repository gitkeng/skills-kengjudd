# Phase 1 — Interview: the nine topics in full

Read this when Phase 1 starts; it carries the full text of topics 1–9, which
SKILL.md summarises in one line each. The bold labels are
the ones other references refer to.

## Contents

- [1 Project identity](#1-project-identity)
- [2 Agents](#2-agents)
- [3 Task types](#3-task-types)
- [4 Gap checklists](#4-gap-checklists)
- [5 Knowledge-base folder name](#5-knowledge-base-folder-name)
- [6 Legacy knowledge folders](#6-legacy-knowledge-folders)
- [7 Karpathy guidelines opt-in](#7-karpathy-guidelines-opt-in)
- [8 Language of generated files](#8-language-of-generated-files)
- [9 Pre-existing artifacts](#9-pre-existing-artifacts)

## 1 Project identity

Ask for the project's **name** and a one-or-two
sentence **purpose**. Recommend the target directory's own name; for an
existing codebase also draft the purpose from its README per
`## Edge cases` and offer that draft. For an empty directory ask
outright. Both are required: the assets carry `<Project name>` tokens
that must not survive.

## 2 Agents

Multi-select from the fourteen agents covered in
[agent-context-matrix.md](agent-context-matrix.md)
— Claude Code, Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI,
Amp, Goose, ZCode, Antigravity, GitHub Copilot, Devin (formerly
Windsurf) — plus free text for any other agent.

## 3 Task types

Multi-select from the four presets in
[task-type-presets.md](task-type-presets.md) —
`## coding`, `## frontend`, `## project management`,
`## knowledge base` — plus free text, which goes through that file's
`## Free-text task types`: draft by analogy, confirm in one question,
at most one revision round.

## 4 Gap checklists

For every selected task type, read only its preset
section plus `## Gap rules`, and ask its items by key, one at a time,
recommendation first, until no gaps remain — including the one-level
expansion items an answer naming a technology adds. Items the user
defers join the **running gap list**, flushed to `<kb>/log.md` at Phase 3
**Skeleton, run record, gap flush** and reported in Phase 6; nothing is
written before then.

## 5 Knowledge-base folder name

Recommend `knowledge-base`, then ask.
This is `<kb>` everywhere below. Accept only a **single path segment
matching `[a-z0-9._-]+`** — no spaces, no `/`, no leading `.` alone, no
absolute path, no `..`; re-ask with the constraint stated (re-ask
bound). Check for an existing folder of that name
**case-insensitively** with the probe in
[run-lifecycle.md](run-lifecycle.md)
`## Detection signals`, because macOS and Windows treat `Docs` and
`docs` as the same directory. If the name is taken by a folder this run
must not write into, stop and ask: propose exactly one alternative
(`<chosen>-okf`) and let the user accept it or name another. Never adjust
the user's chosen name silently.

## 6 Legacy knowledge folders

When the root has depth-1 directories that
look like documentation and are not OKF bundles (`docs`, `doc`,
`documentation`, `notes`, `wiki`, `adr`, `decisions`, the folder that
collided in the previous topic, any directory named under
`coding/existing-conventions`), list them and ask which to index as
legacy from the new bundle (key `knowledge-base/legacy-folders`,
multi-select, "none" allowed; the user may add paths). A folder that
**is** an OKF bundle is offered as an external KB instead. Skip the
question when no candidate exists.

## 7 Karpathy guidelines opt-in

Ask whenever the project involves
**writing code** — the `coding` preset, the `frontend` preset, or a
confirmed code-flavored free-text checklist. It is an item of the
`## coding` checklist (`coding/karpathy-opt-in`); a run that selected
`coding` has answered it there — carry that answer forward. Ask here only
if no code-writing checklist covered it; the default is to include.
Including it never installs the upstream skill.

## 8 Language of generated files

Recommend the language the user is
writing in, then ask. Every file this run writes uses the answer
**except** the items in
[context-file-guidelines.md](context-file-guidelines.md)
`## Never translated` — chiefly the standing-rules and Karpathy blocks,
the four HTML markers, YAML keys and `type:` values, and every key or
token a later run parses. When the answer is not English, put the notice
line that section describes above each fixed block.

## 9 Pre-existing artifacts

Nothing is asked here. Every existing path
is decided once, on the Phase 3 **Write plan**, per
[context-file-guidelines.md](context-file-guidelines.md)
`## Merge semantics`; additive writes into an existing OKF bundle are
never asked about.
