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

Write the description last, after the body. Then check:

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
- [ ] `## Updating` section present and names this skill in the
      `./scripts/update.sh <skill-name>` command.

## Repo integration

- [ ] Registered in `.claude-plugin/plugin.json` `skills` array as
      `"./skills/<skill-name>"`.
- [ ] `knowledge/` concept added/updated with `type:`, `sources:`, `generated:`.
- [ ] `knowledge/log.md` entry appended under today's date.
- [ ] `CHANGELOG.md` entry added; repo `VERSION` bumped (SemVer).

## Testing before calling it done

- [ ] Trigger test: paste each intended prompt into a fresh session; the skill
      should activate from its description alone.
- [ ] Anti-trigger test: near-miss prompts should NOT activate it.
- [ ] Walk the workflow end-to-end once as written — every command runs, every
      referenced file exists.
- [ ] If the skill will be used by weaker/smaller models, test with them too;
      what works for a large model may need more explicit steps for a small one.
