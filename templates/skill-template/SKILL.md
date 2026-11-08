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
- The "## Updating

Versioned by `metadata.version`; source: private repo `gitkeng/skills-kengjudd`.

- Git clone + symlink install (from the repo root; `readlink -f` a symlinked
  skill dir to find it): `./scripts/update.sh skill-name-here`
- Claude Code plugin install (`update.sh` cannot run in the plugin cache, which
  has no `.git`): `claude plugin update kengjudd@kengjudd`

Then reload skills or restart the session (Claude Code: `/reload-skills`).
