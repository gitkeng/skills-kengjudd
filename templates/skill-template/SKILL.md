---
name: skill-name-here
description: >-
  What this skill does, in third person, followed by when to use it.
  Use when <concrete trigger phrases users would actually type>.
metadata:
  version: "1.0.0"
  updated: "YYYY-MM-DD"
---

# Skill Title Here

<!--
Template rules (delete this comment block when done):
- `name` MUST equal the skill's directory name: lowercase a-z, 0-9, hyphens;
  1-64 chars; no leading/trailing/consecutive hyphens.
- Frontmatter may ONLY use the six Agent Skills spec fields: name, description,
  license, compatibility, metadata, allowed-tools. metadata values must be strings.
- Keep this file under 500 lines; move detail into references/ (one level deep).
- Write the description in third person with explicit "Use when..." triggers.
- The "## Updating" section below is REQUIRED for every skill in this repo.
-->

## Purpose

One short paragraph: what problem this skill solves and what the output is.

## Workflow

1. Step one.
2. Step two.
3. Step three.

## References

- [references/example.md](references/example.md) — load only when needed.

## Updating

This skill is versioned via `metadata.version` (currently see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`.

To update this skill to the latest version, run from the repository root:

```bash
./scripts/update.sh skill-name-here
```

If this skill directory is a symlink (the normal install), find the repo root with:

```bash
dirname "$(dirname "$(readlink -f "$(dirname "$0")")")"
```

or simply run the script from the clone location (default: where you cloned
`git@github.com:gitkeng/skills-kengjudd.git`). The script fetches `origin/main`,
compares this skill's `metadata.version`, shows this skill's pending commits,
and pulls after confirmation.
