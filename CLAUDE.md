# skills-kengjudd

Central, private repository of Agent Skills for multiple AI coding agents
(Claude Code primary; also Codex, Cursor, opencode, Gemini CLI, Zed, Kiro,
Kimi CLI, and others), paired with a project knowledge base in the
OKF (Open Knowledge Format) standard.

This file is the **canonical instruction set** for any agent working in this
repository. `AGENTS.md` is a thin adapter that points non-Claude agents here.

## Binding rules

1. **No guessing.** Every factual claim added to this repo must come from a
   trusted source (official docs, specs, verified local inspection) — record it
   with `sources:` in the knowledge base. If research cannot settle a question,
   ask the user before deciding. Never invent.
2. **`skills/` and `knowledge/` are disjoint and must stay that way.**
   OKF requires a `type:` frontmatter key on every knowledge document; the
   Agent Skills spec forbids unknown frontmatter keys in SKILL.md. Never place
   SKILL.md files under `knowledge/` or OKF concepts under `skills/`.
3. **Every skill carries its own update command.** Each SKILL.md must contain a
   `## Updating` section invoking `./scripts/update.sh <skill-name>` and a
   `metadata.version` (SemVer, string). Skills without these are incomplete.
4. **Every skill change produces knowledge.** Creating or updating a skill
   requires: an OKF concept added/updated under `knowledge/`, a `knowledge/log.md`
   entry, a `CHANGELOG.md` entry, a `metadata.version` bump, and a repo `VERSION`
   bump. No exceptions.
5. **Check spec freshness before KB work.** Before significant changes to
   `knowledge/`, run `./scripts/check-spec-versions.sh`. If the OKF spec has
   moved past the recorded version, update `knowledge/specs/okf-spec.md` and
   migrate the bundle first. The canonical OKF spec lives at
   `github.com/GoogleCloudPlatform/open-knowledge-format` — the copy under
   `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen snapshot; never
   cite it as current.
6. **Portability first.** Skills use only the six agentskills.io frontmatter
   fields (`name`, `description`, `license`, `compatibility`, `metadata`,
   `allowed-tools`). Claude-Code-only fields are forbidden in portable skills.

## Repository structure

```
skills/<name>/           one folder per skill (Agent Skills spec)
  SKILL.md               frontmatter + body + required "## Updating" section
  references|scripts|assets/
knowledge/               OKF 0.2 bundle (project knowledge base)
  index.md               bundle index (okf_version)
  log.md                 KB change history (newest date first)
  specs/                 spec knowledge: agent-skills, agents-md, okf, claude plugins
  agents/                per-agent skill discovery paths and constraints
  skill-authoring/       how to write good skills; how updates work
  decisions/             dated design decision records
scripts/
  install.sh             symlink skills into per-agent skill dirs (--tool ...)
  update.sh              per-skill updater (update.sh <skill-name>|--all)
  check-spec-versions.sh OKF spec freshness check
templates/skill-template/ scaffold for new skills
.claude-plugin/          plugin.json + marketplace.json (Claude Code packaging)
VERSION, CHANGELOG.md    repo-level SemVer + Keep-a-Changelog
```

## Working with skills

- **Create / update / import a skill:** invoke the `creating-skills` skill
  (`skills/creating-skills/SKILL.md`) and follow it exactly — it encodes the
  full lifecycle including registration and knowledge capture. Its checklist:
  `skills/creating-skills/references/authoring-checklist.md`.
- **Register:** every new skill must be added to `.claude-plugin/plugin.json`
  → `skills` array as `"./skills/<name>"` (`./` prefix + directory path).
- **Skill naming:** directory name == frontmatter `name`; lowercase `a-z0-9-`,
  max 64 chars; gerund or noun phrase; must be unique among the skills already
  installed on the user's machine (check `~/.claude/skills`, `~/.agents/skills`).

## Knowledge base (OKF) rules

- Bundle root is `knowledge/`; it conforms to OKF 0.2:
  - every non-reserved `.md` has YAML frontmatter with non-empty `type:`;
  - reserved names: `index.md` (listing; frontmatter only at bundle root),
    `log.md` (history, `## YYYY-MM-DD` headings, newest first);
  - recommended fields: `title`, `description`, `tags`; provenance via
    `sources:` (each entry has `resource:`), `generated: {by, at}`,
    `verified:` list; lifecycle via `status:` (draft|stable|deprecated) and
    `stale_after:`.
- `type` vocabulary used in this repo: `Spec Summary`, `Reference`, `Playbook`,
  `Decision`. Extend only with user approval.
- Actor convention: agents write `generated.by` as `<agent>/<model>`
  (e.g. `claude-code/claude-fable-5`); humans as `human:kengjudd`.
- Cross-link concepts with bundle-relative links starting with `/`
  (e.g. `/specs/okf-spec.md`).
- External facts require `sources:` with resolvable URLs. Unsourced factual
  content is a defect (rule 1).

## Versioning

- Repo: `VERSION` (SemVer) + `CHANGELOG.md` (Keep a Changelog). New skill =
  minor bump; skill content fix = patch bump; breaking layout change = major.
- Per skill: `metadata.version` + `metadata.updated` in SKILL.md frontmatter.
- Both must move together on every skill change (rule 4).

## Install & update

```bash
# clone (private repo — requires git auth)
git clone git@github.com:gitkeng/skills-kengjudd.git

# link all skills into an agent's discovery dir (user scope)
./scripts/install.sh --tool claude     # or codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|all
./scripts/install.sh --tool claude --project /path/to/project   # project scope

# per-skill update
./scripts/update.sh <skill-name>
./scripts/update.sh --all
```

Claude Code can alternatively install via the plugin marketplace:
`/plugin marketplace add gitkeng/skills-kengjudd` then
`/plugin install skills-kengjudd@kengjudd`. When releasing, bump the `version`
fields in `.claude-plugin/plugin.json` and `marketplace.json` — plugin users
only receive updates when those versions are bumped.

## For non-Claude agents

If you are reading this via `AGENTS.md`: this file is the complete rule set —
follow it as written. Where it references Claude-specific tooling (`/plugin`,
skill invocation), use your agent's equivalent; the git + scripts workflow is
agent-agnostic.
