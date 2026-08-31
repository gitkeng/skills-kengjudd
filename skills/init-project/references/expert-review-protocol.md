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

Beyond the two standing reviewers, add domain reviewers for the technologies
and domains the user named during the interview (the `task-type-presets.md`
questions, plus any technology named in a free-text answer) — **at most
five**, however many were named. Build the roster like this:

1. Give an individual reviewer to the technologies with the largest KB
   footprint first — the ones whose concepts carry the most claims to
   check.
2. Group the remainder by **shared review surface**: technologies whose
   concepts a single reviewer can check together (same ecosystem, same
   concept, same subject). Every named knowledge *domain* gets one grouped
   pass in total, never one pass per domain.
3. Stop at five domain reviewers. A user who named eight technologies gets
   five passes, not eight — and the Phase 6 report says how they were
   grouped. **Never drop a technology silently:** every one named is
   reviewed by exactly one reviewer, alone or in a group.

Running sequentially (no subagent tool), the same cap applies: at most five
domain passes plus the two standing passes.

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

**Adjudication.** The orchestrator running this skill — not the reviewer —
decides each finding, and **accepts by default**. Reject a finding only
when it contradicts an explicit decision the user made during the interview,
breaks one of the skill's iron rules, or asserts something no source backs.
A finding that conflicts with a user decision goes back to the *user* as a
question, not into a rejection list. Everything else is applied.

- **Accepted findings against context files:** context files amended in
  place — edit `AGENTS.md` or the affected adapter directly, then re-check
  the content budget (`context-file-guidelines.md` `## Content budget`)
  before moving to the next finding.
- **Accepted findings against KB concepts:** KB concepts corrected with the
  amendment logged in `<kb>/log.md` — edit the concept file in place and add
  a new dated entry (newest first), consistent with `okf-kb-guide.md`'s log
  conventions. When a finding requires a **new** concept, create it through
  `okf-kb-guide.md` `## Creating the bundle` like any other: frontmatter,
  an `<kb>/index.md` bullet, and a `<kb>/log.md` entry. Phase 3 step 5 has
  already run, so nothing else will index it for you.
- **Rejected findings:** recorded with a one-line reason rather than
  silently dropped, and reported in Phase 6.
- **Gaps:** where a finding is accepted but cannot be applied inside this
  run's budget or knowledge, record it as a gap rather than a rejection.

## Convergence

The review loop is bounded. It runs **one full pass and one re-check, never
a third**:

1. **Pass 1** — the roster reviews the artifacts and returns findings.
   Adjudicate and apply them per `## Applying findings`.
2. **Re-check** — re-review **only what the apply step changed**, not the
   whole artifact set. Its job is to catch regressions the fixes introduced.
3. A finding raised for the first time in the re-check is applied **only if
   it is a regression from the apply step**. Anything else — a new
   observation about content that pass 1 already saw and passed — is
   recorded as a gap in the Phase 6 report and left for a future run.
4. There is no third pass. If the re-check finds a regression, fix it and
   verify that single fix directly; do not restart the loop.

On a re-run of the skill (Phase 0 detected previous output), both steps look
only at what this run wrote or changed.
