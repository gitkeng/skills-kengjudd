---
name: init-project
description: >-
  Initialize a project for one or more AI coding agents: interview the user
  (agents, task types, stack, knowledge-base folder name, Karpathy
  guidelines opt-in), research each selected agent and named technology,
  create an OKF knowledge base (default folder knowledge-base), generate a
  canonical AGENTS.md plus per-agent adapters (CLAUDE.md, GEMINI.md, ...),
  and run an adaptive expert review. Use when asked to init or set up a
  project for agents, bootstrap agent context files or a knowledge base —
  "init โปรเจกต์", "ตั้งต้นโครงการให้ agent", "สร้าง AGENTS.md/CLAUDE.md",
  "ตั้งค่า knowledge base". Not for scaffolding application code, running
  git init, or analyzing an existing codebase in depth.
license: MIT
metadata:
  version: "1.0.0"
  updated: "2026-08-31"
---

# Skill Title Here

## Purpose

One short paragraph: what problem this skill solves and what the output is.

## Workflow

1. Step one.
2. Step two.
3. Step three.

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh init-project
```

If this skill directory is a symlink (the normal install), resolve it with
`readlink -f <this-skill-dir>`; the repo root is two directories above the
resolved path.

The script fetches `origin/main`, compares this skill's `metadata.version`,
shows this skill's pending commits, and pulls after confirmation.

**Claude Code plugin install** — the plugin cache has no `.git`, so
`update.sh` cannot run there:

```bash
claude plugin update kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
