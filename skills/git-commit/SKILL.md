---
name: git-commit
description: >-
  Create a Gitmoji + Conventional Commits commit message by analyzing the
  whole working tree — staged, unstaged, and untracked changes — group
  unrelated changes into separate commits, and commit each only after the
  user approves. Use when asked to commit, write or improve a commit
  message, prepare a commit, split changes into commits, or in Thai
  "คอมมิตให้หน่อย", "ทำ commit", "เขียน commit message". Emits emoji-prefixed
  types (✨ feat:, 🐛 fix:, ♻️ refactor:, 📝 docs:, …) with a why-focused body.
  Not for pushing, rebasing, or explaining git itself; amends only the
  message of the most recent commit on request.
metadata:
  version: "1.0.1"
  updated: "2026-08-30"
  upstream: "local ~/.claude/commands/commit.md (slash command /commit, no git repo, no upstream version; imported 2026-08-30)"
allowed-tools:
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git add:*)
  - Bash(git reset:*)
  - Bash(git commit:*)
  - Bash(git log:*)
---

# Git Commit

Turn the current working tree into well-scoped commits the repository will
still be able to read in a year: emoji + conventional type, imperative
subject under 72 characters, body that explains **why**.

Covers everything pending — staged, unstaged, and untracked — and never
commits without showing the proposal and getting an explicit go-ahead.

## Step 1 — Survey the changes

Run these first; they are the only source of truth:

```bash
git status --porcelain=v1 -b -uall  # branch, every staged/unstaged/untracked file
git diff --stat HEAD                # magnitude of tracked changes
git diff HEAD                       # full content of tracked changes (staged + unstaged)
```

Check the state before interpreting anything:

- **Unfinished operation**: if plain `git status` reports unmerged paths, or
  "You are currently merging / cherry-picking / reverting / rebasing", or the
  porcelain output shows any `UU`, `AA`, `DD`, `AU`, `UA`, `DU`, `UD` entry —
  stop and tell the user to resolve first. This skill never concludes a
  merge or rebase; committing in those states creates unintended merge
  commits with two parents.
- **Detached HEAD**: if the branch line reads `## HEAD (no branch)`, tell
  the user and ask whether to commit anyway before proposing anything.
- **No commits yet**: if the branch line reads `## No commits yet`, both
  `git diff HEAD` commands fail — skip them; everything is untracked and
  `git status` plus reading the files covers it.

Then the content:

- The whole tree is the **default** scope. If the user names a narrower
  scope (only the staged part, a specific path), honor it and say so in the
  proposal.
- Untracked files appear only in `git status` (the `-uall` flag keeps
  untracked directories from collapsing into a single `dir/` entry) — list
  them and read their content before deciding what they are. If one is
  binary or very large (by extension or size), do not read it — ask the
  user what it is and whether it belongs in a commit.
- For a submodule change, `git diff HEAD` shows only the gitlink bump, not
  the inner content — say so in the proposal and ask what the bump contains
  before assigning a type.
- If the porcelain output shows anything already staged (non-blank,
  non-`?` first column), note it explicitly in the proposal so it can never
  ride silently into a commit (see Step 5).

If the working tree is completely clean, say so and stop — do not invent
work or touch history.

## Step 2 — Group into commits

One commit = one concern. From the diff, sort the changes into groups:

- Changes that serve the same purpose go in **one** commit (a fix plus its
  test plus its changelog line belong together).
- Unrelated purposes are **separate** commits, even if they were made in the
  same editing session (a refactor and an unrelated typo fix do not mix).
- Not every change must be committed. Flag obvious secrets (`.env`,
  `*.pem`, credentials), build artifacts, and scratch files in the proposal
  and leave them out unless the user says otherwise.
- If one file's changes span two groups, say so explicitly and either
  propose them as one commit or let the user stage the split themselves —
  this skill stages whole paths only and never guesses hunk boundaries
  inside a file.
- When in doubt, propose the split and let the user decide — grouping is a
  judgement call, and the user knows context the diff does not show.

## Step 3 — Pick a type per commit

**Primary types** — cover ~95% of commits:

| Emoji | Type | When to use | SemVer |
|---|---|---|---|
| ✨ | `feat:` | New feature or capability for the end user | MINOR |
| 🐛 | `fix:` | Bug fix for the end user | PATCH |
| ♻️ | `refactor:` | Code restructuring without changing external behavior | — |
| 📝 | `docs:` | Documentation only (README, JSDoc, comments, guides) | — |
| 🎨 | `style:` | Code style: whitespace, formatting, semicolons, linting — no logic change | — |
| ✅ | `test:` | Adding, updating, or fixing tests — no production code change | — |
| ⚡️ | `perf:` | Performance improvement without changing functionality | PATCH |

**Infrastructure & maintenance types:**

| Emoji | Type | When to use | SemVer |
|---|---|---|---|
| 🏗️ | `build:` | Build system or external dependencies (npm, go.mod, pip, webpack, docker) | — |
| 👷 | `ci:` | CI/CD configuration and scripts (GitHub Actions, GitLab CI, Jenkins) | — |
| 🔧 | `chore:` | Maintenance that doesn't modify src or test (.gitignore, tooling, scripts) | — |
| ⏪️ | `revert:` | Revert a previous commit | varies |

**Breaking changes:** append `!` after the type for incompatible API or
behavioral changes → MAJOR bump, e.g. `✨ feat(auth)!: …`.

**Type selection guide:**

1. Changes what the user/consumer can do? → `feat` (new) or `fix` (corrected)
2. Only makes code faster? → `perf`
3. Restructures code without behavior change? → `refactor`
4. Only touches formatting/whitespace/linting? → `style`
5. Only touches tests? → `test`
6. Only touches documentation? → `docs`
7. Changes build tooling or dependencies? → `build`
8. Changes CI/CD pipelines? → `ci`
9. Undoes a previous commit? → `revert`
10. Everything else → `chore`

Priority: **purpose over object** — refactoring a test file is `refactor`,
not `test`.

## Step 4 — Write the message

Format:

```
<emoji> <type>[optional scope][!]: <concise description>

[optional body explaining WHY]

[optional footer: Refs: #123, Fixes: #456, BREAKING CHANGE: ...]
```

Rules:

- Present tense, imperative mood ("add", not "added").
- Subject line under 72 characters, not capitalized after the colon, no
  trailing period.
- The body explains **why** something changed, not just what — the diff
  already says what.
- Wrap the body at 72 characters per line.
- Use a scope when the project is large enough to need one: `fix(auth):`,
  `feat(api):`.
- Footer for issue references and breaking changes. Footers only work as
  the final paragraph — keep them in the dedicated footer block, never
  merged into the body.

Examples:

```
✨ feat(api): add retry logic for failed upstream calls

Intermittent network errors cause silent data loss during sync.
Exponential backoff with 3 retries handles transient failures
without overwhelming the upstream service.

Refs: #234
```

```
🐛 fix: correct off-by-one in pagination offset

Users on the last page see a duplicate of the final item
because the offset calculation doesn't account for zero-indexing.

Fixes: #891
```

```
🏗️ build: bump Go version to 1.22 in go.mod
```

```
✨ feat(auth)!: replace cookie sessions with JWT tokens

BREAKING CHANGE: all clients must send Authorization header
instead of relying on session cookies.
```

## Step 5 — Propose, confirm, then commit

Present to the user, for each planned commit:

1. A short summary of the changes it contains (files + intent).
2. The full proposed message.
3. If the changes span multiple unrelated concerns, the proposed split.
4. Anything deliberately left out (secrets, artifacts, scratch files) and
   anything already staged before this run.

**Never auto-commit.** Wait for explicit approval. If the user amends the
message or the split, follow their version. To reword the most recent
commit instead of creating a new one, propose `git commit --amend` under
this same approval rule.

On approval:

**Re-check first.** Immediately before the first `git add`, re-run
`git status --porcelain=v1 -b -uall`. If the file list no longer matches the
approved plan, stop and re-propose — never stage by a stale plan.

**Reset unless committing staged-as-is.** If the plan rebuilds the index
(the default whole-tree or split flow), run `git reset` first (mixed reset,
working tree untouched) so the index starts from a known state and nothing
pre-staged can leak into the wrong commit. Skip the reset only when the
approved plan is literally "commit exactly what is already staged".

Then build each commit exactly as proposed:

```bash
git add <the files of this group only>   # never -A / . when splitting
git diff --cached --name-only            # must list exactly this group's files
git commit -m "<subject>" -m "<body>" -m "<footer>"   # one -m per paragraph; omit absent ones
```

Stage per group by explicit path. `git add -A` before a split sequence
mixes groups and defeats Step 2.

**Check every commit's exit status.** If `git commit` fails (e.g. a
pre-commit hook rejected it), no new commit exists — do not report a hash.
Stop, re-run `git status --porcelain=v1 -b -uall`, and report which commits
landed and which remain; never blindly retry. If a hook modified files,
show the user what changed before staging anything further.

**Verify while going.** After each commit, check `git log -1 --stat` shows
exactly the promised files.

**Close the loop.** After the final commit, run `git status --porcelain=v1 -b`
once more: the tree should be clean or contain only files deliberately left
out. Report the new commit hashes and anything left behind, with the reason.

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh git-commit
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
