---
type: Playbook
title: Importing skills from other projects
description: >-
  What actually has to change when a skill written for another project is
  imported into skills-kengjudd: provenance recording in metadata.upstream,
  version renumbering from 1.0.0, the two-channel "## Updating" section, the
  skill-root path problem created by symlink installs, host-specific README
  install instructions, and paired skills with a hard input dependency. Worked
  example: the aws-kiro-atx-lab trio imported on 2026-08-29.
tags:
  - skills
  - importing
  - provenance
  - versioning
  - playbook
sources:
  - resource: https://agentskills.io/specification
    title: Agent Skills specification (six frontmatter fields; metadata is a free-form string map)
  - resource: file:///Users/keng/Coding/gitkeng/aws-kiro-atx-lab/.kiro/skills
    title: Import source — aws-kiro-atx-lab Kiro skills (verified by local inspection 2026-08-29)
  - resource: https://github.com/gitkeng/aws-kiro-atx-lab
    title: Upstream repository of the imported trio (private)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/scripts/install.sh
    title: scripts/install.sh — symlink install model that breaks skill-relative command paths
  - resource: file:///Users/keng/.claude/skills/doc-to-markdown
    title: Import source of doc2markdown — machine-local skill, no git history (verified by local inspection 2026-08-29)
generated:
  by: claude-code/claude-opus-5
  at: 2026-08-29T11:49:01Z
status: stable
---

# Importing skills from other projects

A skill authored inside another project is rarely a drop-in. This playbook
records the edits that were actually required, so a later import does not
rediscover them. The procedure itself lives in
`skills/creating-skills/SKILL.md` § "Workflow: importing a skill from another
project"; this document explains *why* each step exists and what it looked like
in practice.

## What must change on import

1. **Provenance goes in `metadata.upstream`.** The Agent Skills spec allows only
   six frontmatter keys, but `metadata` is a free-form string map — so upstream
   repository, path, commit, and the upstream's own version number all fit in
   one string there. Without it the import is unreconstructable: the source repo
   keeps evolving and nothing else in this repo records where the files came
   from.
2. **Renumber to `1.0.0`.** The upstream number describes a different release
   line with a different update channel. Carrying it over would imply an update
   history that `scripts/update.sh` cannot show (it compares versions across
   commits *of this repo*). Record the upstream number inside
   `metadata.upstream` instead. If a README repeats the version, fix it there
   too — two numbers in one skill is a defect.
3. **Add the two-channel `## Updating` section.** Imported skills never have
   one, because their original distribution channel was "copy the directory".
4. **Re-anchor skill-relative paths.** Skills written for a copy-the-directory
   install say `python3 scripts/validate_output.py`. Under this repo's symlink
   install the agent's working directory is the *analyzed* project, so that
   path resolves to the wrong place — or nowhere. Every imported skill needs an
   explicit statement that its `scripts/`, `references/`, and `assets/` paths
   are relative to the skill directory, with `readlink -f <this-skill-dir>` as
   the way to resolve it. (`comprehensive-codebase-analysis` already used
   `<skill-root>/scripts/...`, which is the pattern to prefer when authoring.)
5. **Rewrite host-specific install instructions.** A bundled `README.md` written
   for Kiro told users to `cp -r` the directory into `.kiro/skills/`. That
   contradicts this repo's installer and its update path, so it is replaced with
   `./scripts/install.sh --tool <agent>` plus the plugin channel.
6. **Keep a bundled `LICENSE`.** The repo publishes no top-level LICENSE (2026-08-29
   design decision 4), but a skill that declares `license: MIT` in frontmatter must
   keep the license file that claim refers to.

## Provenance of a dirty working tree

The import source may have uncommitted changes. Recording only the last commit
would then be false: the imported bytes are not that commit. Check
`git status --porcelain <path>` in the source repo before writing
`metadata.upstream`, and say so explicitly when the tree is dirty — the trio's
`codebase-analysis-report` was imported at `@4320cce plus uncommitted
working-tree changes`.

## Sources with no git history

Not every source is a repository. `doc2markdown` was imported from the
machine-local `~/.claude/skills/doc-to-markdown`, which has no `.git` at all —
there is no commit to cite and no upstream version to preserve. The honest
`metadata.upstream` then records the local path and says so:
`"local ~/.claude/skills/doc-to-markdown (no git repo, no upstream version;
imported 2026-08-29)"`. Do not invent a commit or a version number to fill the
field.

## Rename on import

An import may take a new name (`doc-to-markdown` → `doc2markdown`, at the
user's request). Two consequences:

- The frontmatter `name` must match the new directory — rename it in the copied
  SKILL.md, and sweep the skill's own files for the old name (a docstring in
  `scripts/_common.py` still said `doc-to-markdown`).
- The original skill usually stays installed where it was. Two skills with
  near-identical descriptions compete on description-match for the same
  triggers; tell the user, and let them decide whether to remove the original.

## Paired skills

`codebase-analysis-report` consumes a `comprehensive-codebase-analysis` **v2**
output tree (`schema_version` `2.0`) and has no other input. Importing one
without the other yields a skill that cannot run. Skills coupled by a data
contract are imported, versioned, and released together; the dependency is
recorded in `metadata.requires` on the consumer.

## Import status of the deferred inventory

`/decisions/2026-08-29-repo-design.md` lists 23 skills deferred at repository
initialization. Imported since then:

| Skill | Source | Imported | Repo release |
|-------|--------|----------|--------------|
| business-rules-extraction | aws-kiro-atx-lab | 2026-08-29 | 0.4.0 |
| comprehensive-codebase-analysis | aws-kiro-atx-lab | 2026-08-29 | 0.4.0 |
| codebase-analysis-report | aws-kiro-atx-lab | 2026-08-29 | 0.4.0 |
| doc2markdown | ~/.claude/skills (renamed from doc-to-markdown; no git history) | 2026-08-29 | 0.5.0 |

The remaining 19 rows of that inventory are still accurate as deferred
candidates. Related: /skill-authoring/best-practices.md,
/skill-authoring/update-mechanism.md.
