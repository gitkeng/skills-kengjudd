# Skill Authoring Checklist

Operational checklist for skills in skills-kengjudd. Deeper rationale and
sources live in the repo knowledge base: `knowledge/skill-authoring/best-practices.md`.

## Frontmatter

- [ ] `name` equals the directory name; lowercase `a-z0-9-`; 1-64 chars; no
      leading/trailing/consecutive hyphens; does not contain "anthropic" or "claude".
- [ ] `description` is 1-1024 chars, third person, states BOTH what the skill
      does and when to use it, and contains the concrete trigger words a user
      would type. No XML tags.
- [ ] Only spec fields used: `name`, `description`, `license`, `compatibility`,
      `metadata`, `allowed-tools`. Nothing else.
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

- [ ] Under 500 lines (~5,000 tokens); depth moved to `references/`.
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
- [ ] `## Updating` section present, names this skill in the
      `./scripts/update.sh <skill-name>` command, AND gives the plugin-channel
      alternative `claude plugin update skills-kengjudd@kengjudd` (the plugin
      cache has no `.git`, so `update.sh` fails there).

## Repo integration

- [ ] Registered in `.claude-plugin/plugin.json` `skills` array as
      `"./skills/<skill-name>"`.
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

Prerequisite: a skill that is not linked into a discovery directory cannot be
trigger-tested. Run `./scripts/install.sh --tool claude --project .` (or
`--tool <your agent>`) and start a fresh session first.

- [ ] Portability gate: `skills-ref validate ./skills/<name>` (and
      `claude plugin validate .` when packaging changed).
- [ ] Trigger test: paste each intended prompt into a fresh session; the skill
      should activate from its description alone.
- [ ] Anti-trigger test: near-miss prompts should NOT activate it.
- [ ] Walk the workflow end-to-end once as written — every command runs, every
      referenced file exists.
- [ ] If the skill will be used by weaker/smaller models, test with them too;
      what works for a large model may need more explicit steps for a small one.
