---
okf_version: "0.2"
---

# skills-kengjudd Knowledge Base

Project knowledge bundle in OKF format. Canonical spec:
[open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format).

# Specs

* [Agent Skills specification](specs/agent-skills-spec.md) - SKILL.md format, frontmatter fields, constraints, progressive disclosure
* [AGENTS.md standard](specs/agents-md-standard.md) - the open agent-instruction file standard and CLAUDE.md interop
* [OKF specification](specs/okf-spec.md) - Open Knowledge Format rules this bundle follows, and how to check for spec updates
* [Claude Code plugins](specs/claude-code-plugins.md) - plugin.json / marketplace.json mechanics, install and update commands

# Agents

* [Skill discovery matrix](agents/skill-discovery-matrix.md) - where each supported agent discovers skills, per scope

# Skill authoring

* [Best practices](skill-authoring/best-practices.md) - how to write skills that trigger correctly and work across agents
* [Update mechanism](skill-authoring/update-mechanism.md) - how per-skill updates work in this repo
* [Importing skills](skill-authoring/importing-skills.md) - what must change when a skill is imported from another project, and the import status of the deferred inventory
* [Command to skill](skill-authoring/command-to-skill.md) - what must change when a slash command is promoted into a portable skill
* [Skill prefixes](skill-authoring/skill-prefixes.md) - where an invocation prefix comes from (the plugin name, never the skill name), and the reuse-or-ask flow when creating skills
* [Self-checks inside imported skills](skill-authoring/imported-self-checks.md) - when an imported skill's own validation gate rejects this repo's mandated provenance, over-reaches past the artifact it guards, or encodes one fixture's shape
* [Validating generated artifacts](skill-authoring/validating-generated-artifacts.md) - why a hand-written checker drifts from "will the consumer accept this", how to calibrate it against the real parser, and how progressive disclosure starves cross-cutting rules

# Decisions

* [2026-08-30 plugin name kengjudd](decisions/2026-08-30-plugin-name-kengjudd.md) - plugin renamed skills-kengjudd → kengjudd so skills invoke as kengjudd:<skill>; mechanism, unchanged parts, migration
* [2026-08-29 repository design](decisions/2026-08-29-repo-design.md) - founding decisions, spec-conflict rationale, deferred imports inventory
