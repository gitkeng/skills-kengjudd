---
type: Playbook
title: Skill invocation prefixes (plugin packaging)
description: >-
  Where a skill's invocation prefix comes from and where it cannot come
  from: Claude Code namespaces plugin skills by the plugin name, so the
  prefix is decided by the name field in .claude-plugin/plugin.json — never
  by the skill's own name (spec-limited to a-z0-9-) and never present on
  git-clone/symlink installs. Carries the reuse-or-ask decision flow that
  creating-skills follows for every new skill, how to choose a plugin name
  when creating one, and why a late plugin rename is breaking.
tags:
  - skills
  - prefixes
  - plugins
  - packaging
  - claude-code
  - playbook
sources:
  - resource: https://code.claude.com/docs/en/discover-plugins
    title: Claude Code docs — Discover and install plugins ("Plugin skills are namespaced by the plugin name")
  - resource: https://agentskills.io/specification
    title: Agent Skills specification (skill name constraints — lowercase a-z0-9-, must equal directory name)
  - resource: https://github.com/obra/superpowers
    title: obra/superpowers — plugin named "superpowers" so its skills invoke as superpowers:<skill> (verified 2026-08-30)
  - resource: https://code.claude.com/docs/en/skills
    title: Claude Code docs — Extend Claude with skills (directly-installed skills invoke by bare name)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/.claude-plugin/plugin.json
    title: This repo's plugin manifest (name: kengjudd — the prefix source; verified by local inspection)
generated:
  by: claude-code/glm-5.3
  at: 2026-08-30T04:58:13Z
status: stable
---

# Skill invocation prefixes

`kengjudd:git-commit` is not a skill name — it is a **namespaced
invocation**. This playbook records where that prefix comes from, where it
cannot come from, and the decision flow `creating-skills` runs for every new
skill.

## Where a prefix comes from

Exactly one place: **the plugin name**. The Claude Code docs state the rule
directly — "Plugin skills are namespaced by the plugin name" — so a skill
registered in a plugin named `kengjudd` invokes as `kengjudd:<skill-name>`
on the plugin channel. obra/superpowers is the reference: its plugin is
named `superpowers`, so its skills invoke as `superpowers:brainstorming`,
`superpowers:writing-skills`, and so on. The plugin `name` field is where
you choose the prefix users will type (mechanics and field formats:
/specs/claude-code-plugins.md).

## Where it cannot come from

- **The skill itself.** The Agent Skills spec limits a skill's `name` (and
  its directory) to lowercase `a-z0-9-` with no colons, and `name` must
  equal the directory name. A prefix can never be encoded in the skill.
- **The git-clone/symlink channel.** Skills installed by
  `scripts/install.sh` (or any skills-dir install) are personal skills: they
  invoke by their bare name on every agent, no prefix anywhere. That is
  platform behavior, not an option this repo can toggle.
- **The marketplace name.** `kengjudd@kengjudd` names the marketplace after
  the `@`; the prefix users invoke with comes from the plugin `name`. (Keep
  the two identical anyway — see /specs/claude-code-plugins.md.)

## The decision flow for every new skill

`creating-skills` applies this before scaffolding anything:

1. **Does the repo ship a plugin?** Look for `.claude-plugin/plugin.json`
   with a `name`.
2. **Yes → reuse it.** Registering the new skill in that plugin's `skills`
   array is all it takes; the skill inherits the existing prefix. One repo,
   one plugin, one prefix — never create a second plugin alongside the
   first. (This repo: plugin `kengjudd` → every skill is
   `kengjudd:<skill-name>` on the plugin channel.)
3. **No → ask the user** — with the exact question worded so a user who does
   not know the mechanism can answer (the normative wording lives in
   `skills/creating-skills/SKILL.md` § Skill prefixes); the **user**, never
   the agent, picks the plugin name when the answer is yes.
   - *Yes* → create `.claude-plugin/plugin.json` with the user's name
     (choosing well: below), and add `marketplace.json` only when
     distribution to other machines is wanted.
   - *No* → plain skills directory; bare-name invocation everywhere, and
     plugin registration is skipped — the one exception to the repo's
     register-every-skill default, taken only on the user's explicit
     instruction.
   - Record the answer — and the chosen plugin name, if one was created —
     in the skill's knowledge concept so later sessions don't re-ask.

## Choosing a plugin name when there is no plugin yet

The plugin name **is** the prefix users type, so optimize for typing:
short, lowercase, owner-recognizable. It does not need to match the
repository name — this repo is `skills-kengjudd` and the plugin is
`kengjudd`, chosen precisely so invocations stay short. Repository name,
plugin name, and marketplace name are three separate namespaces
(/specs/claude-code-plugins.md § marketplace).

## Renaming later is breaking

A plugin rename changes every skill's prefix at once and strands installed
users on an orphaned id that no longer resolves in the marketplace. This
repo did it once, knowingly, before anyone had installed the plugin —
see /decisions/2026-08-30-plugin-name-kengjudd.md for the migration
commands. Default: choose the name once, early, and keep it.

## Related

- /specs/claude-code-plugins.md — plugin.json / marketplace.json field
  formats, install and update commands, version pinning.
- /skill-authoring/best-practices.md — naming rules for the skill itself
  (which prefix rules are orthogonal to).
- /skill-authoring/update-mechanism.md — the two update channels behind
  the two install channels.
