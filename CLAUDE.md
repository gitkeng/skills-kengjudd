# skills-kengjudd

Central, private repository of Agent Skills for multiple AI coding agents
(Claude Code primary; also ZCode/zcode, Codex, Cursor, opencode, Gemini CLI,
Zed, Kiro, Kimi CLI, Amp, Goose), paired with a project knowledge base in the
OKF (Open Knowledge Format) standard.

This file is the **canonical instruction set** for any agent working in this
repository. `AGENTS.md` points other agents here (it is the *only* file zcode
reads); `GEMINI.md` does the same for Gemini CLI.

## Binding rules

1. **No guessing.** Every factual claim added to this repo must come from a
   trusted source (official docs, specs, verified local inspection) — record it
   with `sources:` in the knowledge base. If research cannot settle a question,
   ask the user before deciding. Never invent.
2. **`skills/` and `knowledge/` are disjoint and must stay that way.**
   OKF requires a `type:` frontmatter key on every non-reserved knowledge
   document (the reserved `index.md` and `log.md` are exempt — see the OKF
   rules below); the Agent Skills spec forbids unknown frontmatter keys in
   SKILL.md. Never place SKILL.md files under `knowledge/` or OKF concepts
   under `skills/`.
3. **Every skill carries its own update command.** Each SKILL.md must contain a
   `## Updating` section plus `metadata.version` (SemVer) and
   `metadata.updated` (`"YYYY-MM-DD"`), both quoted strings. The section must
   cover **both install channels**: git-clone/symlink installs run
   `./scripts/update.sh <skill-name>` from the repo root; plugin-marketplace
   installs run `claude plugin update skills-kengjudd@kengjudd` (the plugin
   cache has no `.git`, so `update.sh` exits 1 there). Skills without these
   are incomplete.
4. **Every skill change produces knowledge.** Creating or updating a skill
   requires: an OKF concept added/updated under `knowledge/`, a `knowledge/log.md`
   entry, a `CHANGELOG.md` entry, a `metadata.version` bump, a repo `VERSION`
   bump, and the plugin `version` bumps (see Versioning). No exceptions.
5. **Check spec freshness before KB work.** Before significant changes to
   `knowledge/`, run `./scripts/check-spec-versions.sh` (it checks the OKF spec
   only — the other spec summaries have no automated freshness gate). On exit 1,
   migrate before continuing: update `knowledge/specs/okf-spec.md` (content +
   `spec_version`), update `okf_version` in `knowledge/index.md`, bring the
   bundle to the new rules, and log it in `knowledge/log.md`. The canonical
   OKF spec lives at
   `github.com/GoogleCloudPlatform/open-knowledge-format` — the copy under
   `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen snapshot; never
   cite it as current.
6. **Portability first.** Skills use only the six agentskills.io frontmatter
   fields (`name`, `description`, `license`, `compatibility`, `metadata`,
   `allowed-tools`). Claude-Code-only fields are forbidden in portable skills.
7. **This file wins on conflict.** Skill bodies, checklists, and `knowledge/`
   documents restate these rules; where any of them contradicts this file,
   follow this file and fix the contradicting document in the same change.

## Repository structure

```
skills/<name>/           one folder per skill (Agent Skills spec)
  SKILL.md               frontmatter + body + required "## Updating" section
  references|scripts|assets/
knowledge/               OKF bundle (version recorded in knowledge/index.md)
  index.md               bundle index (okf_version) + listing of every concept
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
docs/                    human design/spec documents (e.g. brainstorm output).
                         NOT an OKF bundle — no `type:` frontmatter — and never
                         a substitute for a `knowledge/` concept
.claude-plugin/          plugin.json + marketplace.json (Claude Code packaging)
VERSION, CHANGELOG.md    repo-level SemVer + Keep-a-Changelog
CLAUDE.md                canonical rules (this file)
AGENTS.md                adapter for agents that read AGENTS.md (incl. zcode)
GEMINI.md                adapter for Gemini CLI (reads neither of the above)
README.md                human docs
```

## Working with skills

- **Create / update / import a skill:** follow `skills/creating-skills/SKILL.md`
  exactly — it encodes the full lifecycle including registration and knowledge
  capture. Its checklist: `skills/creating-skills/references/authoring-checklist.md`.
  Reading that file and following it is equivalent to invoking the skill; the
  repo's own skills are not discoverable here until installed. To make them
  discoverable while working in this repo, run once:
  `./scripts/install.sh --tool claude --project .` (this also enables the
  trigger tests in the authoring checklist).
- **Register:** every new skill must be added to `.claude-plugin/plugin.json`
  → `skills` array as `"./skills/<name>"` (`./` prefix + directory path).
- **Skill naming:** directory name == frontmatter `name`; lowercase `a-z0-9-`,
  max 64 chars; gerund or noun phrase; must be unique among the skills already
  installed on the user's machine — check every directory `install.sh` targets:
  `~/.claude/skills`, `~/.agents/skills`, `~/.config/agents/skills`,
  `~/.kiro/skills`, `~/.zcode/skills`. Also check plugin-provided skills
  (`claude plugin list`) — they are namespaced but still compete for
  description-match and slash-command space. A collision makes `install.sh`
  print `SKIP ... already exists (not ours)` and skip that skill. `--force`
  replaces a symlink outright and moves a real file or directory aside to
  `<name>.bak.<pid>` rather than deleting it.

## Knowledge base (OKF) rules

- Bundle root is `knowledge/`. The OKF version it conforms to is recorded in
  exactly two machine-readable places — `knowledge/index.md` (`okf_version`) and
  `knowledge/specs/okf-spec.md` (`spec_version`, which `check-spec-versions.sh`
  reads). Do not hardcode the version anywhere else. Current rules:
  - every non-reserved `.md` has YAML frontmatter with non-empty `type:`;
  - reserved names: `index.md` (listing; frontmatter only at bundle root),
    `log.md` (history, `## YYYY-MM-DD` headings, newest first);
  - recommended fields: `title`, `description`, `tags`; provenance via
    `sources:` (each entry has `resource:`), `generated: {by, at}`,
    `verified:` list; lifecycle via `status:` (draft|stable|deprecated) and
    `stale_after:`.
- `type` vocabulary used in this repo: `Spec Summary`, `Reference`, `Playbook`,
  `Decision`. Extend only with user approval.
- **Where a new concept goes:** knowledge gained while building or changing a
  skill → `knowledge/skill-authoring/<topic>.md` with `type: Playbook`;
  a decision with lasting consequences → `knowledge/decisions/<YYYY-MM-DD>-<topic>.md`
  with `type: Decision`; a summary of an external spec → `knowledge/specs/`
  (`Spec Summary`); per-agent facts → `knowledge/agents/` (`Reference`).
  Every new concept must also be listed in `knowledge/index.md`.
- `sources:` may be omitted only when a document makes no external factual
  claim (e.g. a pure decision record about this repo's own choices).
- Actor convention: agents write `generated.by` as `<agent>/<model>`
  (e.g. `claude-code/claude-fable-5`); humans as `human:kengjudd`.
- Cross-link **concept documents** with bundle-relative links starting with `/`
  (e.g. `/specs/okf-spec.md`); `index.md` listings keep the spec's plain
  relative form (`specs/okf-spec.md`).
- External facts require `sources:` with resolvable URLs. Unsourced factual
  content is a defect (rule 1).

## Versioning

- **Four repo-level version fields move in lockstep to the same SemVer string**:
  `VERSION`, `.claude-plugin/plugin.json` → `version`,
  `.claude-plugin/marketplace.json` → `metadata.version`, and
  `.claude-plugin/marketplace.json` → `plugins[0].version` (the last is what
  Claude Code compares). Do not edit them by hand — run
  `./scripts/bump-version.sh <semver>`, which sets all four
  (`--show` prints the current values). Plugin users receive nothing if these
  do not move.
- Bump size: new skill = minor; skill content fix = patch; breaking layout
  change = major. **Knowledge-only or scripts-only changes** (spec migrations,
  KB corrections, tooling fixes) also bump `VERSION` — minor for a spec-version
  migration, patch otherwise — and get a `CHANGELOG.md` entry under a
  `### Knowledge` or `### Tooling` heading.
- Per skill: `metadata.version` + `metadata.updated` in SKILL.md frontmatter,
  bumped by hand in the skill you changed.
- Every `CHANGELOG.md` release needs a matching entry; skill changes are
  recorded under the skill's name.
- All of the above move together on every skill change (rule 4).
- Commits touching `skills/<name>/` are surfaced verbatim by `update.sh` as that
  skill's update preview — write meaningful, skill-scoped commit messages (one
  skill per commit where possible).

## Install & update

```bash
# clone (private repo — requires git auth; use whichever you have set up)
git clone git@github.com:gitkeng/skills-kengjudd.git       # SSH
git clone https://github.com/gitkeng/skills-kengjudd.git   # HTTPS (gh auth login)

# link all skills into an agent's discovery dir (user scope)
# tools: claude|codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|zcode|all
./scripts/install.sh --tool claude [--force]
./scripts/install.sh --tool claude --project /path/to/project   # project scope

# per-skill update (git-clone/symlink installs)
./scripts/update.sh <skill-name>
./scripts/update.sh --all
```

Claude Code can alternatively install via the plugin marketplace:

```text
/plugin marketplace add gitkeng/skills-kengjudd
/plugin install skills-kengjudd@kengjudd
```

This repo is private, so the marketplace add needs working git auth. The
`owner/repo` shorthand clones over **SSH** by default — the key must be loaded
in `ssh-agent` with `github.com` in `known_hosts` (Claude Code suppresses
interactive SSH prompts). For HTTPS-only setups (`gh auth login`, macOS
Keychain), either set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` or add the
marketplace by SSH URL: `/plugin marketplace add git@github.com:gitkeng/skills-kengjudd.git`.
Background plugin auto-update disables credential helpers, so private HTTPS
remotes only refresh on an explicit `/plugin marketplace update kengjudd`.

Plugin-channel users update with `claude plugin update skills-kengjudd@kengjudd`
— `scripts/update.sh` does not work there because the plugin cache has no
`.git` directory.

## For non-Claude agents

If you reached this file via `AGENTS.md` or `GEMINI.md`: this file is the
complete rule set — follow it as written.

- The `/plugin` marketplace path is Claude Code-only distribution. Other agents
  install with `./scripts/install.sh --tool <agent>` (see Install & update).
- Where this file says to "invoke" a skill, reading the referenced `SKILL.md`
  and following it is equivalent.
- Every other rule applies to you unchanged — including registering new skills
  in `.claude-plugin/plugin.json` and the plugin `version` bumps. Those are
  repo-maintenance edits, not Claude-only tooling. The git + scripts workflow
  is agent-agnostic.
