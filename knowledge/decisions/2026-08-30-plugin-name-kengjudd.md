---
type: Decision
title: Plugin renamed to kengjudd for a short skill prefix
description: >-
  Why the Claude Code plugin shipped from this repo was renamed
  skills-kengjudd to kengjudd on 2026-08-30: plugin skills are namespaced by
  the plugin name, so the rename makes every skill invoke as
  kengjudd:<skill-name> on the plugin channel (the pattern obra/superpowers
  uses for superpowers:<skill>). Records the mechanism, what deliberately did
  not change, and the one-time migration for pre-rename plugin installs.
tags:
  - plugin
  - claude-code
  - naming
  - distribution
  - decision
sources:
  - resource: https://code.claude.com/docs/en/discover-plugins
    title: Claude Code docs — Discover and install plugins ("Plugin skills are namespaced by the plugin name"; /plugin uninstall; qualified-name installs refresh the marketplace first)
  - resource: https://github.com/obra/superpowers
    title: obra/superpowers — reference implementation of a short plugin name (skills invoke as superpowers:<skill>), verified 2026-08-30
  - resource: https://raw.githubusercontent.com/obra/superpowers/main/.claude-plugin/plugin.json
    title: Live plugin.json on main (superpowers) — "name": "superpowers"
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/.claude-plugin/plugin.json
    title: This repo's plugin manifest (name: kengjudd, verified by local inspection)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/.claude-plugin/marketplace.json
    title: This repo's marketplace manifest (marketplace name kengjudd, plugins[0].name kengjudd)
generated:
  by: claude-code/glm-5.3
  at: 2026-08-30T04:50:28Z
status: stable
---

# Plugin renamed to `kengjudd` (short skill prefix)

## Decision

On 2026-08-30 the Claude Code plugin packaged in this repository was renamed
from `skills-kengjudd` to `kengjudd`, in both places that declare it:
`.claude-plugin/plugin.json` → `name`, and `.claude-plugin/marketplace.json`
→ `plugins[0].name`. The marketplace name stays `kengjudd`, so the install
command becomes `/plugin install kengjudd@kengjudd`.

## Why

Claude Code namespaces plugin skills by the **plugin name** — the official
docs state it directly: "Plugin skills are namespaced by the plugin name."
With the plugin named after the repository, every skill invoked through the
plugin channel carried the long prefix `skills-kengjudd:<skill-name>`.
Renaming only the plugin makes the same skills invoke as
`kengjudd:<skill-name>` (e.g. `kengjudd:git-commit`) while nothing about the
repository or the other install channel changes. obra/superpowers is the
reference for this pattern: its plugin is named `superpowers`, so its skills
invoke as `superpowers:brainstorming`, `superpowers:writing-skills`, and so
on — the plugin name is chosen for the prefix, independently of the repo
name.

## What did not change (deliberately)

- **The GitHub repository name** `gitkeng/skills-kengjudd`, all clone URLs,
  and every path in `scripts/install.sh` / `scripts/update.sh` that refers to
  the repository. The plugin identity and the repository identity are
  separate namespaces.
- **The marketplace name** `kengjudd` (marketplace.json top-level `name` /
  `id`) — existing `/plugin marketplace add` registrations keep working; only
  the plugin entry inside the catalog was renamed.
- **The git-clone/symlink channel.** Skills installed by
  `./scripts/install.sh` are personal skills and have **no prefix at all** on
  any agent — that is platform behavior (the Agent Skills spec forbids
  anything but `a-z0-9-` in a skill's own `name`), not something this repo
  can opt into. The prefix exists only on the Claude Code plugin channel.
- **Skill directory names and frontmatter `name` values.** A prefix can never
  come from the skill side.

## Migration for pre-rename plugin installs

Anyone who installed the plugin before the rename holds an orphaned
`skills-kengjudd@kengjudd` whose update command no longer resolves (the
marketplace entry it names no longer exists). One-time fix:

```text
/plugin uninstall skills-kengjudd@kengjudd
/plugin install kengjudd@kengjudd
```

No separate marketplace refresh is needed: installing by qualified name
refreshes that marketplace before the lookup. At rename time no install of
the old plugin id existed on this machine (checked
`~/.claude/plugins/cache`), so the break was theoretical here.

## Release

Repo v0.7.0 (minor — SemVer 0.y.z carries breaking changes on the minor
line; the repo is pre-1.0). Because every SKILL.md's `## Updating` section
quotes the plugin-channel command, all six skills took a patch bump with the
corrected `kengjudd@kengjudd` string; the same string was swept through
CLAUDE.md, AGENTS.md, README.md, the authoring checklist, the skill template,
`scripts/update.sh`'s reload reminder, the business-rules-extraction README,
and the knowledge base (/specs/claude-code-plugins.md,
/skill-authoring/update-mechanism.md, /skill-authoring/best-practices.md).
