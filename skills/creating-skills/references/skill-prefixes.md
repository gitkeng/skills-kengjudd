# Skill prefixes — where an invocation prefix comes from


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
