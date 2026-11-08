# Skill Authoring Checklist

Operational checklist for skills in skills-kengjudd. Deeper rationale and
sources live in the repo knowledge base: `knowledge/skill-authoring/best-practices.md`.

## Frontmatter

- [ ] `name` equals the directory name; lowercase `a-z0-9-`; 1-64 chars; no
      leading/trailing/consecutive hyphens; does not contain "anthropic" or "claude";
      unique among skills already installed on the machine (check the
      directories `install.sh` targets and `claude plugin list`).
- [ ] `description` is 1-1024 chars (aim for 300-600), third person, states
      BOTH what the skill does and when to use it, and contains the concrete
      trigger words a user would type (Thai included). The trigger is complete
      within the **first 240 characters** — ZCode shows ~250, Kimi 240, Codex
      shortens first; "Not for …" exclusions come last. No XML tags.
- [ ] Only spec fields used: `name`, `description`, `license`, `compatibility`,
      `metadata`, `allowed-tools`. Nothing else. `allowed-tools`, when present,
      is a space-separated string (`Bash(git status:*) Read`), not a YAML list.
- [ ] `metadata.version` and `metadata.updated` present; all metadata values
      are quoted strings.

## Description quality tests

Draft the description early (it clarifies scope), then **rewrite it after the
body is finished** — the body is what tells you what the skill actually does.
Check the final version:

- Would the skill trigger on the 3-5 prompts it is built for? List them.
- Would it stay silent on near-miss prompts that belong to other skills?
- Does it avoid vague phrasing ("helps with documents") in favor of concrete
  nouns and verbs ("Converts PDF, DOCX, XLSX into Markdown...")?
- Is it written in third person ("Guides...", not "I can help you...")?

## Body structure

- [ ] Under 500 lines and under ~5,000 tokens (≈20 KB of English); depth
      moved to `references/`, organised by variant so one run loads one file.
- [ ] Rules that must hold for the whole task (iron rules, stop conditions,
      the reference table) sit in the first ~5,000 tokens — Claude Code
      re-attaches only that much after context compaction.
- [ ] References linked one level deep from SKILL.md, relative paths,
      forward slashes.
- [ ] Reference files longer than ~100 lines start with a table of contents.
- [ ] Degrees of freedom match the task:
      - fragile/destructive operations → exact commands or a script in `scripts/`
        ("run exactly this");
      - open-ended tasks → principles and heuristics.
- [ ] Deterministic, repeatable operations are shipped as executable scripts
      in `scripts/`, not as prose instructions.
- [ ] Workflows with more than ~3 steps are numbered checklists.
- [ ] `## Updating` section present in the template's short form (two
      commands, one reload sentence), names this skill in the
      `./scripts/update.sh <skill-name>` command, AND gives the plugin-channel
      alternative `claude plugin update kengjudd@kengjudd` (the plugin
      cache has no `.git`, so `update.sh` fails there).

## Repo integration

- [ ] Registered in `.claude-plugin/plugin.json` `skills` array as
      `"./skills/<skill-name>"`.
- [ ] Prefix handled per the **Skill prefixes** rule in SKILL.md: the repo
      already ships a plugin (here `kengjudd`) → the skill is registered
      there and inherits `kengjudd:<skill-name>`; no plugin packaging → the
      user was asked *before* creation whether they want a prefix, and the
      answer — and the plugin name, if one was created — is recorded in
      `knowledge/`.
- [ ] `knowledge/` concept added/updated with `type:`, `sources:`, `generated:`.
- [ ] `knowledge/log.md` entry appended under today's date.
- [ ] New/changed concept listed in `knowledge/index.md` under the right
      `# Section`, using the plain relative path form.
- [ ] `./scripts/bump-version.sh <semver>` run (sets all four repo-level version
      fields; verify with `--show`). Plugin users receive nothing otherwise.
- [ ] `CHANGELOG.md` entry added under the skill's name.
- [ ] README `## Skills` table row added, or its version cell updated.
- [ ] `./scripts/check-spec-versions.sh` was run before the KB edits (rule 5).

## Testing before calling it done

- [ ] Portability gate: `skills-ref validate ./skills/<name>` (and
      `claude plugin validate .` when packaging changed).
- [ ] Eval cases exist under `<repo>/evals/<skill-name>-<case>/` — at least one
      trigger case (`tool_used: Skill`) and one near-miss anti-trigger case,
      fixtures synthetic only (`knowledge/decisions/2026-11-08-eval-suite-layout.md`).
- [ ] On Claude Code: `claude plugin eval . --case '<skill-name>-*'` passes;
      read `evals/results/.../report.html` for tokens and duration with vs
      without the skill.
- [ ] On agents without eval tooling (fallback): link the repo into that
      agent's discovery directory (`./scripts/install.sh --tool <agent>
      --project .`), start a fresh session, paste each intended prompt (should
      trigger) and each near-miss prompt (should not). Use one install channel
      per machine — with the `kengjudd` plugin also enabled every skill is
      listed twice.
- [ ] Walk the workflow end-to-end once as written — every command runs, every
      referenced file exists.
- [ ] If the skill will be used by weaker/smaller models, test with them too;
      what works for a large model may need more explicit steps for a small one.
