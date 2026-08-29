# skills-kengjudd — Repository Design

**Date:** 2026-08-29
**Status:** Approved by user (Kongsak) on 2026-08-29
**Scope:** Initial repository structure only. No skills imported from old projects yet.

## Purpose

A private, central repository of Agent Skills usable across many AI coding agents
(Claude Code primary; also Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI, etc.),
with a project knowledge base following the OKF spec.

## User decisions (2026-08-29)

1. **Distribution:** Hybrid — git clone to a fixed path + `install.sh` symlinks into
   per-agent skill directories, **plus** a Claude Code plugin marketplace
   (`.claude-plugin/plugin.json` + `marketplace.json`).
2. **Update model:** Every skill carries its **own** update command — a required
   `## Updating` section in each SKILL.md plus per-skill `metadata.version`.
   Shared implementation lives in `scripts/update.sh <skill-name>`.
3. **Old skills:** Not imported now. Initial scaffold only.
4. **Visibility/license:** Private repo, no LICENSE file.

## Key research findings that shaped the design

- **OKF spec moved.** `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen snapshot;
  canonical home is `github.com/GoogleCloudPlatform/open-knowledge-format` (SPEC.md,
  currently **Version 0.2**). Version is declared in a `**Version X.Y**` line near the
  top of SPEC.md; the repo has no tags/releases.
- **Cross-spec conflict.** OKF requires frontmatter `type:` on every non-reserved `.md`;
  the Agent Skills spec (agentskills.io) allows only six frontmatter fields
  (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) and
  claude.ai upload hard-fails on unknown keys. Therefore `skills/` and `knowledge/`
  must be disjoint subtrees.
- **AGENTS.md has no import syntax**; only Claude Code supports `@file` imports.
  Since this project is Claude Code–first, CLAUDE.md is canonical and AGENTS.md is a
  thin adapter that tells other agents to read CLAUDE.md.
- **Proven update pattern** (ACT, verified locally): git clone to fixed path, symlink
  into agent dirs, `VERSION` + `CHANGELOG.md`, fetch → compare → show changelog →
  confirm → pull → print reload reminders. Adapted here to per-skill granularity.
- The model repo (multica-ai/andrej-karpathy-skills) shows the plugin/marketplace file
  formats but also anti-patterns to avoid (no LICENSE file; three hand-synced copies
  of the same content).

## Repository structure

```
skills-kengjudd/
├── CLAUDE.md                    # canonical agent instructions (Claude Code primary)
├── AGENTS.md                    # thin adapter → points agents to CLAUDE.md
├── README.md                    # human docs: install / update / structure
├── VERSION                      # repo-level semver
├── CHANGELOG.md                 # Keep a Changelog format
├── .claude-plugin/
│   ├── plugin.json              # Claude Code plugin; skills listed explicitly with ./ prefix
│   └── marketplace.json         # marketplace "kengjudd"
├── skills/<skill-name>/         # one folder per skill, Agent Skills spec
│   ├── SKILL.md                 # 6 std frontmatter fields; metadata.version; "## Updating" section
│   └── references|scripts|assets/
├── knowledge/                   # OKF 0.2 bundle — strictly separate from skills/
│   ├── index.md                 # okf_version: "0.2"
│   ├── log.md
│   ├── specs/                   # spec knowledge: agent-skills, agents-md, okf, claude-code plugins
│   ├── agents/                  # per-agent discovery paths & constraints
│   ├── skill-authoring/         # how to write good skills; update mechanism
│   └── decisions/               # design decisions (dated)
├── scripts/
│   ├── install.sh               # symlink skills into per-agent dirs (--tool ...)
│   ├── update.sh                # per-skill updater engine (update.sh <skill-name>|--all)
│   └── check-spec-versions.sh   # compare recorded OKF version vs canonical SPEC.md
└── templates/skill-template/    # skeleton for new skills (incl. Updating section)
```

## Mechanisms

- **Per-skill update:** each SKILL.md has `metadata: {version: ...}` and a `## Updating`
  section instructing to run `scripts/update.sh <skill-name>` from the repo root
  (resolve root via the skill dir symlink). The script: verify git clone → clean tree,
  branch main → `git fetch` → compare local vs `origin/main` skill version → show that
  skill's changelog delta → confirm → `git pull` → print per-agent reload reminders.
  A `git pull` updates the whole repo; the per-skill version comparison is what makes
  the command per-skill.
- **OKF freshness:** `check-spec-versions.sh` fetches canonical SPEC.md and compares
  the `**Version X.Y**` line against the version recorded in `knowledge/specs/okf-spec.md`.
  CLAUDE.md requires running it before significant KB changes.
- **Knowledge capture rule:** every skill create/update must add or update an OKF
  concept (frontmatter `type:` + `sources:` + `generated:`) and a `knowledge/log.md` entry.
- **Initial skill:** `creating-skills` — meta-skill guiding creation of new skills per
  this repo's conventions; serves as the reference implementation of the format.

## Quality gates

- Expert review of CLAUDE.md + AGENTS.md, max 3 rounds (user requirement).
- KB conformance check: every non-reserved `.md` under `knowledge/` has parseable
  frontmatter with non-empty `type`.
- All factual content in `knowledge/` must carry `sources:` — no unsourced claims
  (user requirement: no guessing).

## Out of scope (deferred)

- Importing skills from old projects (presales, dify, flutter, aws-kiro-atx-lab, ...).
  The inventory with dependency analysis is preserved in the KB decision record for
  when the user wants it.
- Publishing, CI validation pipeline, `skills-ref` integration.
