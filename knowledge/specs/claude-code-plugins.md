---
type: Reference
title: Claude Code plugins — plugin.json / marketplace.json mechanics, install and update commands
description: >-
  Exact field formats for .claude-plugin/plugin.json and marketplace.json,
  the two-step marketplace install flow, version-pinning semantics, update
  commands, auto-update behavior and env flags, the local plugin cache layout,
  and schema lessons learned from the andrej-karpathy-skills model repo.
tags:
  - claude-code
  - plugins
  - marketplace
  - packaging
  - versioning
  - updates
sources:
  - resource: https://code.claude.com/docs/en/plugins
    title: Claude Code docs — Create plugins
  - resource: https://code.claude.com/docs/en/plugins-reference
    title: Claude Code docs — Plugins reference (version management)
  - resource: https://code.claude.com/docs/en/discover-plugins
    title: Claude Code docs — Discover and install plugins (marketplaces, auto-update)
  - resource: https://github.com/multica-ai/andrej-karpathy-skills
    title: multica-ai/andrej-karpathy-skills (model plugin repo)
  - resource: https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/.claude-plugin/plugin.json
    title: Live plugin.json on main (karpathy repo)
  - resource: https://raw.githubusercontent.com/multica-ai/andrej-karpathy-skills/main/.claude-plugin/marketplace.json
    title: Live marketplace.json on main (karpathy repo)
  - resource: https://api.github.com/repos/multica-ai/andrej-karpathy-skills
    title: GitHub API — karpathy repo metadata (license detection)
  - resource: file:///Users/keng/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/
    title: Local plugin cache inspection (v1.0.0 snapshot)
  - resource: https://github.com/anthropics/skills
    title: anthropics/skills (official marketplace example)
  - resource: https://github.com/obra/superpowers
    title: obra/superpowers — reference implementation of a short plugin name (skills invoke as superpowers:<skill>); verified 2026-08-30
  - resource: https://raw.githubusercontent.com/obra/superpowers/main/.claude-plugin/plugin.json
    title: Live plugin.json on main (superpowers) — "name": "superpowers"
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:45:09Z
status: stable
---

# Claude Code plugins: packaging, install, and update mechanics

How Claude Code plugins are declared (`.claude-plugin/plugin.json` +
`marketplace.json`), installed (two-step marketplace flow), versioned
(pin-by-version semantics), and updated (manual commands + background
auto-update). This repo packages itself as a plugin in `.claude-plugin/`;
see also /specs/agent-skills-spec.md for the SKILL.md format the plugin
exposes, and /skill-authoring/update-mechanism.md for this repo's own
update workflow.

## plugin.json (`.claude-plugin/plugin.json`)

Fields, as validated by Claude Code (verified against the live
andrej-karpathy-skills plugin.json plus its schema-fix commit history):

| Field | Format | Notes |
|---|---|---|
| `name` | string | Plugin name (e.g. `"andrej-karpathy-skills"`). Distinct from the marketplace name. |
| `description` | string | |
| `version` | string, SemVer | Optional but **pins the plugin** — see [Version pinning](#version-pinning-semantics). |
| `author` | **OBJECT** `{"name": "..."}` | NOT a plain string. Claude Code schema validation rejects a string here (karpathy repo commit "Fix plugin.json schema validation errors" changed string → object). |
| `license` | string | e.g. `"MIT"`. |
| `keywords` | array of strings | e.g. `["guidelines", "best-practices"]`. |
| `skills` | array of strings | Each entry points to a skill **DIRECTORY** (not the SKILL.md file) and **must carry the `./` prefix**: `["./skills/karpathy-guidelines"]`. Directory-pointing + `./` prefix is required for skill auto-discovery (karpathy PR #18 "Fix plugin skill path for Claude Code compatibility"). |

This repo's rule (CLAUDE.md): every new skill must be registered in the
`skills` array as `"./skills/<name>"`.

## marketplace.json (`.claude-plugin/marketplace.json`, alongside plugin.json)

Verified against the live karpathy marketplace.json:

| Field | Format | Notes |
|---|---|---|
| `name` | string | The **MARKETPLACE** name (e.g. `"karpathy-skills"`) — deliberately distinct from the plugin name; it is what users type after `@` on install. |
| `id` | string | Same value as `name` in the model repo. |
| `owner` | object `{"name": "..."}` | |
| `metadata` | object `{description, version}` | Marketplace-level description + SemVer version string. |
| `plugins` | array | One entry per plugin: `name`, `source` (`"./"` when the plugin root is the repo root), `description`, `version`, `author`, `keywords`, `category` (e.g. `"workflow"`). |

## Install: two-step, and what the `@` suffix means

```text
/plugin marketplace add <owner>/<repo>        # step 1: register the marketplace
/plugin install <plugin-name>@<marketplace-name>   # step 2: install the plugin
```

The `@` suffix is the **marketplace name** (marketplace.json top-level
`name`), NOT the GitHub owner/author. Examples:

- karpathy model repo: `/plugin marketplace add forrestchang/andrej-karpathy-skills`
  then `/plugin install andrej-karpathy-skills@karpathy-skills`.
- anthropics/skills: `/plugin marketplace add anthropics/skills` then
  `/plugin install document-skills@anthropic-agent-skills`.
- This repo: `/plugin marketplace add gitkeng/skills-kengjudd` then
  `/plugin install kengjudd@kengjudd` (the plugin was renamed from
  `skills-kengjudd` on 2026-08-30 so its skills invoke with the short
  `kengjudd:` prefix — see /decisions/2026-08-30-plugin-name-kengjudd.md).

`marketplace add` accepts `owner/repo`, a git URL, a local path, or a URL,
and supports ref pinning via `#ref` (branch/tag), e.g.
`/plugin marketplace add https://gitlab.com/company/plugins.git#v1.0.0`.

Installed skills surface **namespaced** as `<plugin>:<skill>`, which differs
from the bare `/skill` name of a directly-installed skill. The official docs
state the rule directly: "Plugin skills are namespaced by the plugin name"
(commit-commands provides `/commit-commands:commit`). Examples:
`andrej-karpathy-skills:karpathy-guidelines`, `superpowers:brainstorming`
(obra/superpowers names its plugin `superpowers`), and — since the
2026-08-30 rename — `kengjudd:git-commit` in this repo.

**Design consequence: the plugin `name` field is where you choose the
invocation prefix.** This repo's plugin is named `kengjudd`, shorter than the
repository name `skills-kengjudd`, precisely so plugin-channel skills invoke
with a short `kengjudd:` prefix; the repository name, clone URLs, and the
marketplace name are unaffected. The docs note that the identifier users type
(`kengjudd@kengjudd`) is the marketplace entry's `name`, which *can* differ
from plugin.json's `name` — keep the two identical here, as this repo does.

## Version pinning semantics

- plugin.json `version` is optional SemVer. Resolution precedence:
  **plugin.json `version` > marketplace-entry `version` > fallback**
  (e.g. commit SHA for git sources).
- Setting a version **pins** the plugin: per the official docs, users only
  receive updates when the author bumps the version string. Content-only
  pushes without a bump do not propagate to installed users.
  (Exception: `command`-source plugins are re-resolved once per session and
  update when the output hash changes.)
- Consequence for this repo: **every release must bump the `version` fields
  in both `.claude-plugin/plugin.json` and `marketplace.json`**, or plugin
  users silently stay on the old snapshot. The karpathy repo demonstrates
  the failure mode: it changed README/Cursor files after 1.0.0 without a
  bump; the cached 1.0.0 remains what users have (it happens to still match
  main, but only by luck).
- Alternative pinning model: the community catalog
  (anthropics/claude-plugins-community) pins each plugin to a commit SHA
  and bumps the pin via CI as authors push.

## Update commands

```bash
claude plugin update <plugin>                 # or <plugin>@<marketplace>
#   options: -s/--scope user|project|local|managed, -y/--yes
```

```text
/plugin marketplace update <marketplace-name>   # refresh the catalog
/reload-plugins                                 # reload after update
#   add --force to override the prompt-cache warning
```

Installing by qualified name (`/plugin install plugin@marketplace`)
force-refreshes that marketplace first (since Claude Code v2.1.232).

## Auto-update behavior

- After session start, Claude Code refreshes marketplaces and updates
  installed plugins **in the background** (random delay up to 10 minutes),
  then prompts `/reload-plugins`. No documented periodic re-check during
  long sessions beyond this startup pass.
- Defaults: **official Anthropic marketplaces auto-update by default;
  third-party/local marketplaces default off**.
- Env flags: `DISABLE_AUTOUPDATER=1` (turn off), `FORCE_AUTOUPDATE_PLUGINS=1`
  (force on for all).

## Local cache layout

Installed marketplace plugins are cached at:

```text
~/.claude/plugins/cache/<marketplace-name>/<plugin-name>/<plugin-version>/
```

Verified locally:
`~/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/`
contains a full repo snapshot plus a `.in_use/` directory of numeric PID
lockfiles (e.g. `80304`) marking sessions using that version.

## Skills-directory plugins (lightweight alternative)

`claude plugin init my-tool` scaffolds `~/.claude/skills/my-tool/` with its
own `.claude-plugin/plugin.json`; it loads as `my-tool@skills-dir`.
SKILL.md edits take effect **immediately in-session**; other components
need `/reload-plugins`. There is no uninstall command — delete the folder
or `claude plugin disable my-tool@skills-dir`. Useful for fast iteration
before publishing through a marketplace.

## Lessons from the karpathy model repo

The multica-ai/andrej-karpathy-skills repo (~208.5k stars as of
2026-08-29) is the reference example of minimal plugin packaging; its
commit history records the schema pitfalls:

1. **`author` must be an object.** It was initially a string and failed
   Claude Code schema validation; fixed to `{"name": "forrestchang"}`.
2. **`skills` entries must be `./`-prefixed directory paths.** Pointing at
   the SKILL.md file, or omitting `./`, breaks skill auto-discovery
   (PR #18).
3. **Missing LICENSE file is an anti-pattern.** The repo declares MIT in
   README/plugin.json/SKILL.md but ships no LICENSE file, so the GitHub API
   reports `license: null` — the license is not machine-detected. Ship a
   real LICENSE file.
4. **Marketplace name ≠ plugin name ≠ owner.** Keeping them distinct
   (`karpathy-skills` vs `andrej-karpathy-skills` vs `forrestchang`) works,
   but install docs must spell out that `@` takes the marketplace name.
5. **Bump the version on every meaningful release** (see pinning above);
   the repo has no git tags/releases — the `version` fields are the only
   release mechanism.
6. **Renamed/transferred repos keep working** via GitHub redirects: README
   install commands still use the pre-transfer path
   `forrestchang/andrej-karpathy-skills`. Prefer updating docs anyway.

## Open questions

- Whether Claude Code ever re-fetches a marketplace plugin on content-only
  changes when the plugin.json version is unchanged (not directly
  observable; docs imply no for pinned versions).
- No documented periodic marketplace re-check cadence during long sessions
  beyond the startup pass and a 30-second dedupe window for named installs.
