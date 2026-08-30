---
type: Playbook
title: Per-skill update mechanism
description: >-
  How per-skill updates work in this repo: the required two-channel "## Updating"
  section and metadata.version in every SKILL.md, the shared scripts/update.sh
  engine (guards, per-skill version comparison against origin/main, changelog
  delta, confirm, pull, reload reminders), the parallel plugin-marketplace
  channel, the provenance of the design (ACT act-update pattern), and the
  release steps — including scripts/bump-version.sh and the four lockstep
  repo-level version fields — that make updates detectable.
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
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/scripts/update.sh
    title: scripts/update.sh — per-skill updater (verified by local inspection)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/scripts/install.sh
    title: scripts/install.sh — symlink installer, --tool targets and --force behaviour
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/scripts/bump-version.sh
    title: scripts/bump-version.sh — lockstep bump of the four repo-level version fields
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:45:08Z
status: stable
---

# Per-skill update mechanism

Every skill in this repo carries its own update command, but the command a user
runs depends on the channel they installed through: git-clone/symlink installs
share one update engine and one git clone, while Claude Code plugin installs
update through the marketplace. This playbook describes the two-channel
contract each SKILL.md must satisfy, the exact flow of `scripts/update.sh`, why
the design looks the way it does, and what an author must do on each release so
updates are detectable on **both** channels.

## The per-skill contract

Every `skills/<name>/SKILL.md` MUST contain (CLAUDE.md binding rule 3):

1. **A `## Updating` section** in the body that covers **both install
   channels**, because the right command depends on how the skill was
   installed:

   - *git clone + symlink install* — run from the repository root:

     ```bash
     ./scripts/update.sh <skill-name>
     ```

   - *Claude Code plugin-marketplace install*:

     ```bash
     claude plugin update kengjudd@kengjudd
     ```

   The plugin cache is not a git clone (it has no `.git` directory), so
   `update.sh` cannot run there — it hits its clone guard and exits 1. A
   `## Updating` section that documents only one of the two channels sends
   half the users to a command that cannot work for them.

2. **`metadata.version`** in the frontmatter — a SemVer string, quoted
   (e.g. `version: "1.0.0"`). The Agent Skills spec has *no* standard version
   field; the only spec-legal place for a version is the free-form `metadata`
   map, which is why it lives there and nowhere else.

3. **`metadata.updated`** — the date of the last change, `"YYYY-MM-DD"`.

Example frontmatter (from `skills/creating-skills/SKILL.md`):

```yaml
metadata:
  version: "1.1.0"
  updated: "2026-08-29"
```

Skills missing `metadata.version`, or carrying an `## Updating` section that
does not document *both* channels above, are incomplete by definition. The
scaffold in `templates/skill-template/` already includes the two-channel
section and both metadata keys; keep them when creating new skills (see
/skill-authoring/best-practices.md and the `creating-skills` skill).

## The shared engine: scripts/update.sh

`scripts/update.sh` (at `/Users/keng/Coding/gitkeng/skills-kengjudd/scripts/update.sh`)
is the single implementation behind the git-clone/symlink half of every skill's
`## Updating` section. (The other half, `claude plugin update
kengjudd@kengjudd`, is handled entirely by Claude Code — see
/specs/claude-code-plugins.md.)

Usage:

```bash
./scripts/update.sh <skill-name>      # update check for one skill
./scripts/update.sh --all             # update check for every skill
./scripts/update.sh <skill-name> -y   # skip the confirmation prompt
```

Step-by-step flow:

1. **Resolve repo root** from the script's own location and `cd` there, so it
   works when invoked through a symlinked skill directory.
2. **Guard: git clone.** Requires a `.git` directory at the repo root;
   otherwise prints the clone command
   (`git clone git@github.com:gitkeng/skills-kengjudd.git`) and exits 1. This
   is exactly the guard a plugin-marketplace install trips: the plugin cache
   holds a copy of the skills with no `.git`, so those users must run
   `claude plugin update kengjudd@kengjudd` instead.
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
8. **Confirm.** If no checked skill reported an update, the script exits 0 here
   without prompting. Otherwise it prompts `Pull updates now? (git pull updates
   the whole repo) [y/N]` unless `-y/--yes` was passed; anything other than
   `y`/`Y` prints `Aborted.` and exits 0 without pulling.
9. **Pull.** `git pull origin main`.
10. **Reload reminders.** Prints how to make each agent pick up the change:
    - Claude Code (symlink install): start a new session — symlinked SKILL.md
      edits load on next use;
    - Claude Code plugin install: `claude plugin update kengjudd@kengjudd`;
    - Codex: `/skills` to refresh; other agents: restart the session.

The version-extraction helper (`skill_version`) reads only the `metadata:`
block of the frontmatter (`sed -n '/^metadata:/,/^[a-z]/p'`) and takes the
first `version:` line, stripping quotes — so `metadata.version` must be a
plain scalar on its own line for detection to work.

## Why one `git pull` but a per-skill command

All skills live in a single git clone, and `scripts/install.sh` symlinks each
`skills/<name>` directory into the agents' discovery dirs. At user scope there
are five targets — `~/.claude/skills`, `~/.agents/skills`,
`~/.config/agents/skills`, `~/.kiro/skills`, and `~/.zcode/skills` — selected by
`--tool claude|codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|zcode|all`
(`all` links into all five; an unrecognised `--tool` value is rejected with
exit 1 before anything is linked). See /agents/skill-discovery-matrix.md for
the per-agent mapping. Because the install is symlink-based, a single
`git pull` updates every installed skill in place at once — there is no
per-skill checkout to update independently.

That property depends on the link actually pointing back into the clone. When a
target name is already taken by something that is not our symlink, `install.sh`
prints `SKIP ... already exists (not ours)` and leaves it alone; `--force`
replaces a symlink outright but *moves* a real file or directory aside to
`<name>.bak.<pid>` rather than deleting it. A skipped or backed-up entry is not
symlinked, so `git pull` will not refresh it — re-run the installer before
relying on the update flow.

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
each SKILL.md so a skill-scoped answer is possible, while keeping the four
lockstep repo-level version fields + `CHANGELOG.md` for whole-repo releases.

Why this model over the alternatives (researched trade-offs):

- **git-clone + symlink + update script (chosen):** single source of truth;
  instant refresh on `git pull` (Claude Code even picks up SKILL.md edits in
  skills-dir installs live); works across many agent CLIs from one checkout;
  users can pin by simply not pulling. Costs: requires git, no automatic
  update notification (the command must be run), and symlinks break in some
  sandboxed environments.
- **Claude Code plugin marketplace:** first-class semver, scoped installs,
  background auto-update + `/reload-plugins`, namespacing — but Claude
  Code-specific, and the declared `version` *pins* the plugin: users only
  receive updates when the author bumps it (Claude Code compares the
  marketplace entry's `plugins[].version`). This repo ships it as a fully
  supported second channel via `.claude-plugin/` — which is why the four
  version bumps in the author checklist are mandatory rather than optional
  (see /specs/claude-code-plugins.md).
- **npx skills CLI (vercel-labs/skills):** cross-agent GitHub-as-registry with
  a built-in `update` command — but Node-dependent and HEAD-based (no semver;
  lockfile still experimental).
- **anthropics/skills** itself has no per-skill update mechanism at all —
  updates ride whichever distribution channel was used.

Founding rationale is recorded in /decisions/2026-08-29-repo-design.md.

## Author checklist: what makes an update detectable

Each channel has its own detector, and both are version-driven. `update.sh`
detects updates **only** by comparing `metadata.version` strings, and Claude
Code decides whether a plugin update exists **only** by comparing the
marketplace plugin entry's `version`. If you change a skill without bumping
those, every clone reports "up to date" and every plugin user receives nothing.
On every skill release you MUST (CLAUDE.md binding rule 4):

1. **Bump `metadata.version`** in the skill's SKILL.md (SemVer) and set
   `metadata.updated` to today's date. Do this by hand, in the skill you
   changed — no script touches per-skill versions.
2. **Bump all four repo-level version fields to the same SemVer string.** They
   move in lockstep and are not optional:
   - `VERSION`
   - `.claude-plugin/plugin.json` → `version`
   - `.claude-plugin/marketplace.json` → `metadata.version`
   - `.claude-plugin/marketplace.json` → `plugins[0].version` (the one Claude
     Code actually compares)

   Do not edit them by hand — run `./scripts/bump-version.sh <semver>`, which
   validates the SemVer string, writes all four, and prints the result;
   `./scripts/bump-version.sh --show` prints the current values without
   changing anything. Bump size: new skill = minor, skill content fix = patch,
   breaking layout change = major.
3. **Add a `CHANGELOG.md` entry** at the repo root (Keep a Changelog format) —
   this plus the commit messages on `skills/<name>/` is what users see as the
   pending-changes preview.
4. Capture the knowledge (OKF concept + `knowledge/log.md` entry) — required
   by the same rule, though not part of update detection.

Knowledge-only and scripts-only changes are held to the same versioning bar:
they also bump all four version fields — minor for an OKF spec-version
migration, patch otherwise — and get a `CHANGELOG.md` entry under a
`### Knowledge` or `### Tooling` heading.

Commit messages that touch `skills/<name>/` should be meaningful — they are
surfaced verbatim by step 7 of the update flow as the skill's changelog delta.
