---
name: creating-skills
description: >-
  Guide for creating, updating, and registering skills in the skills-kengjudd
  repository. Use when creating a new skill, modifying an existing skill's
  content or version, importing a skill from another project, or asking how
  skills in this repo are named, prefixed, structured, versioned, installed,
  or updated.
metadata:
  version: "1.2.0"
  updated: "2026-08-30"
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
- If the resolved path is not inside a clone of this repository (it resolves
  into `~/.claude/plugins/cache/...`, a plugin install), the repository is
  not on this machine and every workflow below dead-ends there — ask the
  user to clone `gitkeng/skills-kengjudd` and work from the clone.
- Read `<repo>/CLAUDE.md` for the repository's binding rules. Do not proceed
  from memory of an older version of the rules.
- **No guessing.** If a design question cannot be answered from this repo's
  `knowledge/` bundle or a trusted source, ask the user before deciding.

## Workflow: creating a new skill

0. **Run the spec freshness gate.** `./scripts/check-spec-versions.sh`
   (CLAUDE.md rule 5). On exit 1, migrate the knowledge base before continuing.
1. **Clarify scope.** One skill = one capability with clear triggers. If the
   idea spans several independent capabilities, split it. Then run the
   [Skill prefixes](#skill-prefixes) decision — the user is asked only when
   the repo has no plugin packaging (no `.claude-plugin/plugin.json` with a
   `name`) — before anything is scaffolded.
2. **Name it.** Lowercase `a-z0-9-`, 1-64 chars, no leading/trailing/consecutive
   hyphens. Prefer gerund form (`creating-skills`) or noun phrases
   (`pdf-processing`). The directory name and frontmatter `name` MUST match.
   The name must also be unique among skills already installed on the
   machine — check the discovery directories `install.sh` targets and
   `claude plugin list` (CLAUDE.md → "Skill naming") before settling.
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
   for Claude Code plugin discovery). This is mandatory for every skill; the
   only exception is the explicit no-plugin branch of
   [Skill prefixes](#skill-prefixes). Registration places the skill under
   the plugin's invocation prefix on the Claude Code plugin channel — the
   prefix's value comes from the plugin `name`.
9. **Capture knowledge (mandatory).** Add or update an OKF concept describing
   what was learned or decided while building the skill. Default destination:
   `knowledge/skill-authoring/<topic>.md` with `type: Playbook` — or
   `knowledge/decisions/<YYYY-MM-DD>-<topic>.md` with `type: Decision` when the
   skill encodes a lasting decision. Include `generated:` and `sources:` for
   any external claim. Then list it in `knowledge/index.md` (plain relative
   path form) and append an entry to `knowledge/log.md` under today's date.
10. **Validate.** Run the checklist in
    [references/authoring-checklist.md](references/authoring-checklist.md).
    Then install the repo so the skill is discoverable —
    `./scripts/install.sh --tool claude --project .` — and in a fresh session
    test that it triggers on its intended prompts and does NOT trigger on
    near-miss prompts.
11. **Version bookkeeping.** Run `./scripts/bump-version.sh <semver>` (new skill
    = minor bump) — it sets all four repo-level version fields. Then add a
    `CHANGELOG.md` entry under the skill's name and a row in the README
    `## Skills` table (name, version, description). Validation comes first so
    a failed trigger test never forces a second version bump.

## Workflow: updating an existing skill

0. Run `./scripts/check-spec-versions.sh` (CLAUDE.md rule 5).
1. Edit the skill's files.
2. Bump `metadata.version` (SemVer) and `metadata.updated` in its SKILL.md.
3. Run `./scripts/bump-version.sh <semver>`; add a CHANGELOG.md entry under the
   skill's name; update the skill's version in the README `## Skills` table.
4. Update the related `knowledge/` concept and `knowledge/log.md`.
5. Re-run the checklist in
   [references/authoring-checklist.md](references/authoring-checklist.md) —
   at minimum the portability gate, and repeat the trigger and anti-trigger
   tests in a fresh session whenever the `description` changed.

## Workflow: importing a skill from another project

1. Copy the skill directory into `skills/` — bring ALL its dependencies:
   `references/`, `scripts/`, `assets/`, and note external CLIs it shells out to.
2. Strip project-specific coupling (hardcoded paths, project-only conventions)
   or document it in `compatibility` frontmatter.
3. Remove build artifacts (`__pycache__/`, `.git/` of vendored repos).
4. If it has an upstream (vendored third-party skill), record the upstream URL
   in `metadata.upstream` and in its knowledge/ concept so it can be re-synced.
5. Imported skills start at `metadata.version: "1.0.0"` regardless of any
   upstream numbering; record the upstream version or commit in
   `metadata.upstream`, combined with the URL into a single string (e.g.
   `"<url> @<version-or-commit>"`) — metadata values are always strings,
   never objects. If the user asks for a different number, confirm the
   intent before deviating.
6. Then follow steps 4-11 of "creating a new skill". The
   [Skill prefixes](#skill-prefixes) decision applies to imports too — when
   the repo has no plugin packaging, ask before copying anything (step 1's
   gate is not inside the 4-11 range).

If asked to update a skill that is not in `skills/` yet, say so and offer to
import it — do not invent a version history. The deferred-import inventory of
skills from older projects (with source paths, readiness, and dependencies)
lives in `knowledge/decisions/2026-08-29-repo-design.md`.

## Skill prefixes

Claude Code namespaces plugin skills by the **plugin name**: a skill
registered in the plugin named `kengjudd` invokes as `kengjudd:<skill-name>`
on the plugin channel (`kengjudd:git-commit`). The prefix never lives in the
skill itself — directory name and frontmatter `name` stay bare `a-z0-9-`
(Agent Skills spec) — and on the git-clone/symlink channel every skill
invokes by its bare name, with no prefix, on every agent. Handle this
explicitly for **every** skill you create or import:

- **The repo already ships a plugin** — `.claude-plugin/plugin.json` with a
  `name` (this repo: `kengjudd`). Reuse it: registering the new skill in
  that plugin's `skills` array (step 8) is all it takes; the skill inherits
  the existing prefix. Never create a second plugin or a second prefix
  alongside it.
- **The repo has no plugin packaging** — ask the user *before* scaffolding,
  in words they can answer without knowing the mechanism (substitute the
  real skill name):

  > This repo has no Claude Code plugin yet. Without one, the skill invokes
  > by its bare name everywhere (`<skill-name>`). With one, it also invokes
  > namespaced on the Claude Code plugin channel — the plugin name becomes
  > the prefix (`<prefix>:<skill-name>`) — and renaming a plugin later is a
  > breaking change. Create a plugin? If yes, which name?

  The **user** picks the name — it becomes the prefix everyone types, so it
  should be short, lowercase, and owner-recognizable (this repo: `kengjudd`,
  not `skills-kengjudd`). Never derive it silently from the repository name.

  - *Yes* → create `.claude-plugin/plugin.json` with the user's name. Add
    `marketplace.json` only when distribution to other machines is wanted.
    Field formats and pitfalls: `knowledge/specs/claude-code-plugins.md`.
  - *No* → plain skills directory; the skill invokes by its bare name
    everywhere, and step 8's registration does not apply — the one
    exception to this repo's register-every-skill default (CLAUDE.md),
    taken only on the user's explicit instruction.

  Record the answer — and the plugin name, if one was created — in the
  skill's knowledge concept so later sessions don't re-ask.

Renaming a plugin later changes every skill's prefix and orphans existing
installs — a breaking change (see
`knowledge/decisions/2026-08-30-plugin-name-kengjudd.md`). Choose the name
once, early. Full decision flow, naming rationale, and sources:
`knowledge/skill-authoring/skill-prefixes.md`.

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
claude plugin update kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
