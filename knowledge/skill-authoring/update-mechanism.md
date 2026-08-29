---
type: Playbook
title: Per-skill update mechanism
description: >-
  How per-skill updates work in this repo: the required "## Updating" section
  and metadata.version in every SKILL.md, the shared scripts/update.sh engine
  (guards, per-skill version comparison against origin/main, changelog delta,
  confirm, pull, reload reminders), the provenance of the design (ACT
  act-update pattern), and the release steps an author must perform for
  updates to be detectable.
tags:
  - skills
  - updating
  - versioning
  - scripts
  - playbook
sources:
  - resource: https://github.com/CodeWithAndreaPro/agentic-coding-toolkit
    title: Agentic Coding Toolkit (ACT) — act-update pattern (private repo — 404 unauthenticated)
  - resource: file:///Users/keng/.agentic-coding-toolkit
    title: Local ACT clone, VERSION 1.0.6 — primary verification source
  - resource: https://agentskills.io/specification
    title: Agent Skills specification (frontmatter fields, metadata map)
  - resource: https://github.com/anthropics/skills
    title: anthropics/skills (marketplace distribution reference)
  - resource: https://code.claude.com/docs/en/plugins-reference
    title: Claude Code docs — Plugins reference (version management)
  - resource: https://code.claude.com/docs/en/discover-plugins
    title: Claude Code docs — Discover and install plugins (auto-update)
  - resource: https://github.com/vercel-labs/skills
    title: vercel-labs/skills — npx skills CLI (alternative pattern)
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:45:08Z
status: stable
---

# Per-skill update mechanism

Every skill in this repo carries its own update command, but all skills share
one update engine and one git clone. This playbook describes the contract each
SKILL.md must satisfy, the exact flow of `scripts/update.sh`, why the design
looks the way it does, and what an author must do on each release so updates
are detectable.

## The per-skill contract

Every `skills/<name>/SKILL.md` MUST contain (CLAUDE.md binding rule 3):

1. **A `## Updating` section** in the body that tells the reader (human or
   agent) to run, from the repository root:

   ```bash
   ./scripts/update.sh <skill-name>
   ```

2. **`metadata.version`** in the frontmatter — a SemVer string, quoted
   (e.g. `version: "1.0.0"`). The Agent Skills spec has *no* standard version
   field; the only spec-legal place for a version is the free-form `metadata`
   map, which is why it lives there and nowhere else.

3. **`metadata.updated`** — the date of the last change, `"YYYY-MM-DD"`.

Example frontmatter (from `skills/creating-skills/SKILL.md`):

```yaml
metadata:
  version: "1.0.0"
  updated: "2026-08-29"
```

Skills missing the `## Updating` section or `metadata.version` are incomplete
by definition. The scaffold in `templates/skill-template/` already includes
both; keep them when creating new skills (see
/skill-authoring/best-practices.md and the `creating-skills` skill).

## The shared engine: scripts/update.sh

`scripts/update.sh` (at `/Users/keng/Coding/gitkeng/skills-kengjudd/scripts/update.sh`)
is the single implementation behind every skill's `## Updating` section.

Usage:

```bash
./scripts/update.sh <skill-name>      # update check for one skill
./scripts/update.sh --all             # update check for every skill
./scripts/update.sh <skill-name> -y   # skip the confirmation prompt
```

Step-by-step flow:

1. **Resolve repo root** from the script's own location and `cd` there, so it
   works when invoked through a symlinked skill directory.
2. **Guard: git clone.** Requires `.git` to exist; otherwise prints the clone
   command (`git clone git@github.com:gitkeng/skills-kengjudd.git`) and exits 1.
3. **Guard: branch.** `git branch --show-current` must be `main`; otherwise
   errors and exits.
4. **Guard: clean tree.** `git status --porcelain` must be empty; otherwise
   asks the user to commit or stash first and exits. This prevents a pull from
   colliding with local edits.
5. **Fetch without merging.** `git fetch origin main --quiet`.
6. **Per-skill version comparison.** For each requested skill, the script
   extracts `metadata.version` from the local `skills/<name>/SKILL.md` and from
   the remote copy read via
   `git show origin/main:skills/<name>/SKILL.md` — i.e. it previews the remote
   state without merging anything. Outcomes:
   - remote version empty → `"not present on origin/main (local-only skill,
     nothing to update)"`;
   - versions equal → `"up to date (version X)"`;
   - versions differ → `"update available — local X -> remote Y"` and the
     pull flag is set.
7. **Changelog delta per skill.** When an update is available it shows the
   pending commits scoped to that skill's path:
   `git log --oneline HEAD..origin/main -- "skills/<name>/"`.
8. **Confirm.** Prompts `Pull updates now? (git pull updates the whole repo)
   [y/N]` unless `-y/--yes` was passed. Anything other than `y`/`Y` aborts.
9. **Pull.** `git pull origin main`.
10. **Reload reminders.** Prints how to make each agent pick up the change:
    - Claude Code (symlink install): start a new session — symlinked SKILL.md
      edits load on next use;
    - Claude Code plugin install: `claude plugin update skills-kengjudd@kengjudd`;
    - Codex: `/skills` to refresh; other agents: restart the session.

The version-extraction helper (`skill_version`) reads only the `metadata:`
block of the frontmatter (`sed -n '/^metadata:/,/^[a-z]/p'`) and takes the
first `version:` line, stripping quotes — so `metadata.version` must be a
plain scalar on its own line for detection to work.

## Why one `git pull` but a per-skill command

All skills live in a single git clone, and `scripts/install.sh` symlinks each
`skills/<name>` directory into the agents' discovery dirs (`~/.claude/skills`,
`~/.agents/skills`, `~/.config/agents/skills`, `~/.kiro/skills` — see
/agents/skill-discovery-matrix.md). Because the install is symlink-based, a
single `git pull` updates every installed skill in place at once — there is no
per-skill checkout to update independently.

The command is still per-skill because the *decision* is per-skill: the user
invoking `## Updating` from one skill wants to know whether *that* skill
changed, what changed in it, and only then whether to pull. The script honors
that by comparing that skill's `metadata.version` against `origin/main` and
showing a `git log` delta scoped to `skills/<name>/`, while being honest in
the confirmation prompt that the pull itself is repo-wide. `--all` is the
repo-wide sweep for when you want the full picture.

## Provenance and trade-offs

The flow is adapted from the **ACT act-update pattern**
(CodeWithAndreaPro/agentic-coding-toolkit, verified locally at
`~/.agentic-coding-toolkit`, VERSION 1.0.6): guard (git clone present, on
main, clean tree) → `git fetch` → compare local vs remote version via
`git show origin/main:<file>` (preview without merging) → show changelog
delta → explicit user confirmation → `git pull` → print reload/reinstall
reminders, never auto-run installers. ACT compares a single repo-root
`VERSION` file; this repo refines that to per-skill `metadata.version` in
each SKILL.md so a skill-scoped answer is possible, while keeping the
repo-level `VERSION` + `CHANGELOG.md` for whole-repo releases.

Why this model over the alternatives (researched trade-offs):

- **git-clone + symlink + update script (chosen):** single source of truth;
  instant refresh on `git pull` (Claude Code even picks up SKILL.md edits in
  skills-dir installs live); works across many agent CLIs from one checkout;
  users can pin by simply not pulling. Costs: requires git, no automatic
  update notification (the command must be run), and symlinks break in some
  sandboxed environments.
- **Claude Code plugin marketplace:** first-class semver, scoped installs,
  background auto-update + `/reload-plugins`, namespacing — but Claude
  Code-specific, and setting `plugin.json` `version` *pins* the plugin: users
  only receive updates when the author bumps it. This repo supports it as a
  secondary channel via `.claude-plugin/` (see /specs/claude-code-plugins.md).
- **npx skills CLI (vercel-labs/skills):** cross-agent GitHub-as-registry with
  a built-in `update` command — but Node-dependent and HEAD-based (no semver;
  lockfile still experimental).
- **anthropics/skills** itself has no per-skill update mechanism at all —
  updates ride whichever distribution channel was used.

Founding rationale is recorded in /decisions/2026-08-29-repo-design.md.

## Author checklist: what makes an update detectable

`update.sh` detects updates **only** by comparing `metadata.version` strings.
If you change a skill without bumping its version, every clone will report
"up to date" and the change is invisible to the update mechanism. On every
skill release you MUST (CLAUDE.md binding rule 4):

1. **Bump `metadata.version`** in the skill's SKILL.md (SemVer) and set
   `metadata.updated` to today's date.
2. **Add a `CHANGELOG.md` entry** at the repo root (Keep a Changelog format) —
   this plus the commit messages on `skills/<name>/` is what users see as the
   pending-changes preview.
3. **Bump the repo `VERSION` file** (SemVer): new skill = minor, content fix =
   patch, breaking layout change = major.
4. Capture the knowledge (OKF concept + `knowledge/log.md` entry) — required
   by the same rule, though not part of update detection.
5. If also distributing as a Claude Code plugin: bump the `version` fields in
   `.claude-plugin/plugin.json` and `marketplace.json`, since plugin users
   only receive updates when those are bumped.

Commit messages that touch `skills/<name>/` should be meaningful — they are
surfaced verbatim by step 7 of the update flow as the skill's changelog delta.
