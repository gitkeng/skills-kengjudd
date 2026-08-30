---
title: Converting a slash command into a skill
description: >-
  What must change when a Claude Code slash command (~/.claude/commands/*.md)
  is promoted into a portable Agent Skill — frontmatter, context gathering,
  description purpose, and scope decisions.
type: Playbook
tags:
  - skill-authoring
  - slash-commands
  - imports
status: stable
sources:
  - resource: file:///Users/keng/.claude/commands/commit.md
    title: Source of git-commit — a user-level Claude Code slash command (verified by local inspection 2026-08-30)
generated:
  by: claude-code/glm-5.3
  at: 2026-08-30
---

# Converting a slash command into a skill

Recorded while promoting the `/commit` slash command
(`~/.claude/commands/commit.md`) into the `git-commit` skill (repo v0.6.0).
A slash command and a skill look similar — markdown plus frontmatter — but
they are invoked differently, and the conversion must account for that.

## What carries over, what must change

- **Frontmatter**: a command carries `description` (help text) and
  optionally `allowed-tools` (Claude Code permission syntax, e.g.
  `Bash(git status:*)`). The `allowed-tools` syntax carries over verbatim
  into a skill. The `description` does **not**: for a command it explains
  the command to a human browsing `/help`; for a skill it is the *trigger*
  the model matches against the user's request. Rewrite it: third person,
  what it does + when to use it, concrete words a user would type.
- **Add the missing skill fields**: `name` (must equal the directory) and
  `metadata` (`version`, `updated`, optionally `upstream`). Commands have
  neither.
- **Context gathering**: commands can inject live output at invocation time
  with `!`command`` frontmatter lines. Skills have no such mechanism — every
  `!`-injection becomes an explicit **Step 1 "run these first"** instruction
  the agent executes itself. If the source command relies on injected
  context, the skill must reproduce it as commands, or the agent will
  improvise.
- **A command is explicit; a skill is discovered.** Users type `/commit`
  deliberately; a skill is chosen by description-match. After conversion the
  description carries the entire targeting burden — write near-miss fences
  ("Not for pushing, rebasing, …") that a command never needed.

## Decisions to ask the owner about

The conversion is a natural moment to revisit scope, because the source
command encodes private habits, not reviewed design. For `/commit`:

- Scope: the command looked at staged changes only; the owner chose to widen
  the skill to the whole working tree (staged + unstaged + untracked).
- The original command's fate: like `doc-to-markdown` before it
  (see /skill-authoring/importing-skills.md), the owner chose to delete the
  source after the skill shipped, so the skill becomes the single home.
  Ask — do not decide.

## Expert review of a converted skill

Two-domain subagent review (git expert + senior developer) surfaced 15+
real defects the first draft missed — mostly git states the prose never
considered (mid-merge, pre-staged index, hook failures, unborn branch) and
footer/trailer mechanics. What made it work:

- Tell each reviewer which decisions are **settled owner choices they must
  not challenge** (style, name, scope) — otherwise reviews burn rounds
  relitigating them.
- Overlapping findings from independent reviewers (both flagged the
  pre-staged index sweep and the `-m` footer mechanics) are a strong truth
  signal; findings from a single reviewer still get verified against real
  git behaviour before applying.
- Run reviewers concurrently on a frozen file; apply everything in one edit
  afterwards — editing mid-review hands later reviewers a moving target.

Related: /skill-authoring/importing-skills.md,
/skill-authoring/best-practices.md.
