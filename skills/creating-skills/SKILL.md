---
name: creating-skills
description: >-
  Guide for creating, updating, and registering skills in the skills-kengjudd
  repository. Use when creating a new skill, modifying an existing skill's
  content or version, importing a skill from another project, or asking how
  skills in this repo are structured, versioned, installed, or updated.
metadata:
  version: "1.1.0"
  updated: "2026-08-29"
---

# Creating Skills in skills-kengjudd

## Purpose

This is the meta-skill of the skills-kengjudd repository. It walks through the
full lifecycle of a skill — design, authoring, registration, knowledge capture,
and versioning — so that every skill in the repo stays consistent, works across
multiple agents, and always carries its own update command.

## Before you start

- Locate the repository root. If this skill directory is a symlink (the normal
  install), resolve it: `readlink -f <this-skill-dir>` points into
  `<repo>/skills/creating-skills`. All paths below are relative to `<repo>`.
- Read `<repo>/CLAUDE.md` for the repository's binding rules. Do not proceed
  from memory of an older version of the rules.
- **No guessing.** If a design question cannot be answered from this repo's
  `knowledge/` bundle or a trusted source, ask the user before deciding.

## Workflow: creating a new skill

1. **Clarify scope.** One skill = one capability with clear triggers. If the
   idea spans several independent capabilities, split it.
2. **Name it.** Lowercase `a-z0-9-`, 1-64 chars, no leading/trailing/consecutive
   hyphens. Prefer gerund form (`creating-skills`) or noun phrases
   (`pdf-processing`). The directory name and frontmatter `name` MUST match.
3. **Scaffold from the template.**
   ```bash
   cp -R templates/skill-template skills/<skill-name>
   ```
4. **Write the frontmatter.** Only the six Agent Skills spec fields are allowed
   (`name`, `description`, `license`, `compatibility`, `metadata`,
   `allowed-tools`) — anything else breaks claude.ai upload compatibility.
   Set `metadata.version: "1.0.0"` and `metadata.updated` to today (all
   metadata values must be strings).
5. **Write the description carefully** — it is the trigger. Third person, state
   what the skill does AND when to use it, include the concrete words a user
   would type. Details: [references/authoring-checklist.md](references/authoring-checklist.md).
6. **Write the body.** Under 500 lines; put depth in `references/` (linked one
   level deep), executable helpers in `scripts/`, templates/data in `assets/`.
   Match "degrees of freedom" to the task: exact commands for fragile
   operations, heuristics for open-ended ones.
7. **Keep the required `## Updating` section** from the template, with the
   skill's own name in the `./scripts/update.sh <skill-name>` command.
8. **Register the skill** in `.claude-plugin/plugin.json` → `skills` array as
   `"./skills/<skill-name>"` (the `./` prefix and directory path are required
   for Claude Code plugin discovery).
9. **Capture knowledge (mandatory).** Add or update an OKF concept under
   `knowledge/` describing what was learned or decided while building the
   skill (frontmatter `type:`, `sources:` for external claims, `generated:`),
   and append an entry to `knowledge/log.md` under today's date.
10. **Version bookkeeping.** Add a `CHANGELOG.md` entry under the skill's name,
    bump the repo `VERSION` (SemVer: new skill = minor bump), and bump the
    `version` field in both `.claude-plugin/plugin.json` and
    `.claude-plugin/marketplace.json` — plugin-channel users only receive
    updates when those move.
11. **Validate.** Run the checklist in
    [references/authoring-checklist.md](references/authoring-checklist.md),
    then test that the skill triggers on its intended prompts and does NOT
    trigger on near-miss prompts.

## Workflow: updating an existing skill

1. Edit the skill's files.
2. Bump `metadata.version` (SemVer) and `metadata.updated` in its SKILL.md.
3. Add a CHANGELOG.md entry under the skill's name; bump repo `VERSION` and the
   `version` field in both `.claude-plugin/` JSON files.
4. Update the related `knowledge/` concept and `knowledge/log.md`.

## Workflow: importing a skill from another project

1. Copy the skill directory into `skills/` — bring ALL its dependencies:
   `references/`, `scripts/`, `assets/`, and note external CLIs it shells out to.
2. Strip project-specific coupling (hardcoded paths, project-only conventions)
   or document it in `compatibility` frontmatter.
3. Remove build artifacts (`__pycache__/`, `.git/` of vendored repos).
4. If it has an upstream (vendored third-party skill), record the upstream URL
   in `metadata.upstream` and in its knowledge/ concept so it can be re-synced.
5. Then follow steps 4-11 of "creating a new skill".

## Multi-agent compatibility rules

- Stay within the agentskills.io spec so the skill works on Claude Code, Codex,
  Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, and others. Per-agent
  discovery paths: `knowledge/agents/skill-discovery-matrix.md`.
- Do not use Claude-Code-only frontmatter (e.g. `disable-model-invocation`,
  `context`, `hooks`) in skills meant to be portable.
- Reference files inside the skill directory only (they travel with the
  symlink); repo-level files must be addressed via the repo root as shown in
  "Before you start".

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh creating-skills
```

The script verifies the clone (branch `main`, clean tree), fetches
`origin/main`, compares this skill's `metadata.version` against the remote,
shows this skill's pending commits, and pulls after confirmation.

**Claude Code plugin install** — the plugin cache has no `.git`, so
`update.sh` cannot run there:

```bash
claude plugin update skills-kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
