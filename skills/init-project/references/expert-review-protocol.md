# Expert review protocol

This file is consulted by `init-project` Phase 5 (Expert review), after
Phase 4 has generated the canonical `AGENTS.md` plus its per-agent adapters
and Phase 3 has drafted the project knowledge base (`<kb>/`) concepts.
Reviewers check and improve two concrete artifacts: the generated
`AGENTS.md` + adapters, against `context-file-guidelines.md`'s budget and
rules, and the Phase 3 KB draft concepts, against `okf-kb-guide.md`'s
frontmatter/sourcing requirements. This file travels with the skill
(including a bare symlink install); it makes no this-repo `knowledge/`
references. Sibling references — `context-file-guidelines.md`,
`okf-kb-guide.md`, `agent-context-matrix.md`, `task-type-presets.md` — are
allowed and used below.

## Capability heuristic

If your harness provides a subagent/task-spawning tool, run the reviewers
below as parallel subagents, one per reviewer. Otherwise run the same
checklists yourself as sequential persona passes, one reviewer at a time,
announcing each persona. Either way the checklists and pass/fail bars are
identical.

## Reviewer roster

Two standing reviewers run on every project, regardless of stack:

- **Prompt engineering** — reviews the instructional wording of the
  generated `AGENTS.md` and its adapters (the `## Working rules` section,
  the standing rules block, and any adapter-specific notes) using `##
  Checklist: prompt engineering`.
- **Context engineering** — reviews the same artifacts for structure and
  budget compliance against `context-file-guidelines.md`, using `##
  Checklist: context engineering`.

Beyond the two standing reviewers, add one **domain reviewer per technology
or domain the user named during the interview** (the `task-type-presets.md`
questions, plus any free-text technology named per R9). For example, a user
who named Next.js, shadcn, and Figma during the interview gets three domain
reviewers — one per technology — in addition to the two standing reviewers.

- If a bundled checklist exists for that technology or domain, the reviewer
  uses it.
- If no bundled checklist exists for it — v1 ships none beyond the two
  standing checklists, so this is the common case — instantiate a **generic
  domain persona** parameterized with that technology (e.g. "generic domain
  reviewer for Next.js") and have it run `## Checklist: generic domain` with
  X bound to that technology's name.

Every domain reviewer (bundled or generic) reviews the Phase 3 KB draft
concept(s) written for its technology, checking them against
`okf-kb-guide.md`'s frontmatter and sourcing requirements. Reviewing the
context files themselves is the two standing reviewers' job, not the domain
reviewers'.

## Checklist: prompt engineering

- Instructions are imperative and unambiguous.
- No two rules conflict.
- Trigger/anti-trigger wording is present.
- Examples match the rules they illustrate.
- No vague qualifiers ("appropriately", "as needed") standing in for
  decisions.

## Checklist: context engineering

- Within content budget (`context-file-guidelines.md` `## Content budget`).
- Every always-needed fact is in context; every sometimes-needed fact is in
  the KB with a pointer left in the context file
  (`context-file-guidelines.md` `## Context vs KB`).
- No duplication between `AGENTS.md` and adapters.
- Adapters contain only agent-specific content.
- Nothing bloats over time: rules reference the KB instead of restating it.

## Checklist: generic domain

Parameterized by technology X — the domain reviewer's assigned technology:

- Claims about X match its official docs (spot-check ≥ 3 against
  `sources:`).
- Versions are current stable.
- Setup/convention facts are actionable for this project.
- Nothing invented (every X claim has a source).
- Gaps about X are listed, not papered over.

## Applying findings

Review output is never "report-only": accepted findings are applied before
the report phase (Phase 6), not deferred to it or merely written down.

- **Accepted findings against context files:** context files amended in
  place — edit `AGENTS.md` or the affected adapter directly, then re-check
  the content budget (`context-file-guidelines.md` `## Content budget`)
  before moving to the next finding.
- **Accepted findings against KB concepts:** KB concepts corrected with the
  amendment logged in `<kb>/log.md` — edit the concept file in place and add
  a new dated entry (newest first), consistent with `okf-kb-guide.md`'s log
  conventions.
- **Rejected findings:** recorded with a one-line reason rather than
  silently dropped.
