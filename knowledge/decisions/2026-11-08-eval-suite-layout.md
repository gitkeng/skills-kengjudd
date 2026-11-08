---
type: Decision
title: Eval suite layout — evals/ at the plugin root with synthetic fixtures
description: >-
  On 2026-11-08 the maintainer decided that this repo adopts an eval suite
  runnable by Claude Code's claude plugin eval: one case directory per skill
  and scenario under evals/ at the plugin root, fixtures synthesised under
  evals/fixtures/ (never real documents or repositories), trigger and
  anti-trigger cases graded with tool_used: Skill, and the manual
  fresh-session trigger test kept only for agents without eval tooling.
  Resolves the open question left in /skill-authoring/best-practices.md §6.
tags:
  - evals
  - testing
  - claude-code
  - plugin
  - decision
sources:
  - resource: https://code.claude.com/docs/en/plugin-evals
    title: Claude Code docs — Plugin evals (case layout prompt.md + graders, with/without arms, grader types, report.html; requires v2.1.269+)
  - resource: https://code.claude.com/docs/en/skills
    title: Claude Code docs — Skills (a tool_used: Skill grader measures description hit rate)
  - resource: https://agentskills.io/skill-creation/evaluating-skills
    title: Agent Skills — Evaluating skills (with/without comparison, token and duration deltas)
  - resource: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
    title: anthropics/skills skill-creator — evals/evals.json workflow and description optimiser (a separate, incompatible layout)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/docs/skill-quality-review-2026-11-08.md
    title: The 2026-11-08 skill quality review that proposed the suite (§4.2, §9)
generated:
  by: claude-code/claude-fable-5-1
  at: "2026-11-08T06:38:06Z"
verified:
  - by: "human:kengjudd"
    at: "2026-11-08T06:38:06Z"
status: stable
---

# Eval suite layout: `evals/` at the plugin root, synthetic fixtures

## Decision

This repo gets an eval suite that `claude plugin eval` can run. Layout:

```text
evals/
  README.md                how to run the suite, the grants it needs
  <skill>-<case>/          one directory per skill and scenario
    prompt.md              the user prompt, realistic, may be Thai; run limits
    case.yaml              only when the case needs context.scaffold_script
    scaffold.sh            seeds the empty run workspace (git repo, a .docx)
    fixtures/              the synthetic inputs and the script that made them
    graders/*.md           tool_used / regex / file_exists / llm graders
  results/                 written by the runner; ignored by git
```

Fixtures live **inside the case directory**, because that is the only place
the runner reads from: each run starts in an empty workspace, and a
`scaffold_script` named in `case.yaml` (run only with `--scaffold`) is what
puts files there. A scaffold embeds its payload (base64 for a binary) rather
than reading a path, since it runs with a minimal environment.

Rules:

1. **Fixtures are synthetic.** Never a real document, a real repository, or
   anything carrying personal or client data. A fixture is built by a script
   (kept beside it, e.g. `fixtures/make_brief.py`) from invented content and
   is small enough to read in a review.
2. **Every skill gets at least one trigger case and one anti-trigger case.**
   The trigger case asserts `tool_used: Skill` with the skill's name; the
   anti-trigger case uses a near-miss prompt (adjacent task, shared keywords)
   and asserts the skill did **not** fire. Output-shape graders are added
   where the result is mechanically checkable (git-commit, doc2markdown).
3. **Manual fresh-session trigger tests stay only as the fallback** for agents
   without eval tooling; on Claude Code the authoring checklist calls the
   runner instead.
   The anti-trigger assertion is `tool_used: Skill` with `min: 0`, `max: 0`,
   `arm: both`; a plain `tool_used: Skill` is a plugin-fired indicator the
   runner excludes from the two-arm score. Behaviour graders that only the
   skill can satisfy (e.g. "ran the bundled extractor") carry
   `arm: with-only`.
4. The suite is a repo convention, not part of any skill: it lives outside
   `skills/` so it never travels with a symlink or into another agent's
   skill directory, and `.claude-plugin/plugin.json` does not list it.

## Why

- Claude Code 2.1.269+ ships `claude plugin eval`, which runs each case
  several times with and without the plugin, grades with declarative
  grader files, and reports a score delta and an HTML report. Before this,
  the only test the repo had was a human pasting prompts into a fresh
  session, which measured nothing and was rarely repeated after the first
  release.
- The skill-creator tooling from anthropics/skills uses a different layout
  (`evals/evals.json`, `grading.json`, `benchmark.json`) that the Claude
  Code runner does not read. Picking the runner that is installed with the
  agent avoids maintaining a second harness.
- `/skill-authoring/best-practices.md` §6 explicitly deferred the layout to a
  maintainer decision; this record closes it.

## What does not change

- Skills keep the six spec frontmatter fields and no eval metadata.
- `scripts/update.sh` and `install.sh` ignore `evals/`.
- Per-skill validators (`scripts/validate_output.py`) remain the
  deterministic output gate; evals test triggering and end-to-end behaviour.

## Related

- [/skill-authoring/best-practices.md](/skill-authoring/best-practices.md) §6–§8
- [/skill-authoring/context-budgets.md](/skill-authoring/context-budgets.md)
