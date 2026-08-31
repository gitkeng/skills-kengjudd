---
type: Playbook
title: Lessons from building the init-project skill
description: >-
  What building an orchestrator-sized skill taught: canonical file plus thin
  adapters (and why imports cannot carry content), bounding every loop rather
  than only specifying it, the dead-end classes only an end-to-end run finds,
  the cost/re-run/harness classes only a review panel finds, marker
  idempotency, verbatim-vs-language conflicts, and trigger wording against a
  built-in command.
tags:
  - skills
  - authoring
  - orchestration
  - review
  - agents-md
  - playbook
sources:
  - resource: ../../skills/init-project/SKILL.md
    title: The skill this playbook is about (init-project 1.0.0, repo v0.10.0)
  - resource: ../../skills/init-project/references/expert-review-protocol.md
    title: Adaptive review protocol as shipped (roster cap, convergence, adjudication)
  - resource: ../../skills/init-project/references/context-file-guidelines.md
    title: Content budget, cut order, merge semantics, standing-rules pointer
generated:
  by: claude-code/claude-opus-5
  at: "2026-08-31T06:30:08Z"
status: stable
---

# Lessons from building the init-project skill

`init-project` is the largest skill in this repo: an orchestrator that
interviews the user, researches, writes an OKF knowledge base into a target
project, generates a canonical `AGENTS.md` plus per-agent adapters, and runs an
adaptive expert review — 486 lines of SKILL.md over five references and two
asset trees. It was built once, then **hardened twice**: two full end-to-end
runs against real directories, and a four-domain expert panel (loop, harness,
context, and prompt engineering) whose findings were all accepted and applied
in one wave (59 applied as written, 6 adapted, none dropped), followed by a
second round for four breakages the wave itself introduced.

This document keeps the transferable part. The per-agent facts the skill is
built on live in
[/agents/agent-init-conventions.md](/agents/agent-init-conventions.md); the
general authoring rules it obeys live in
[/skill-authoring/best-practices.md](/skill-authoring/best-practices.md).

## 1. One canonical file, thin adapters — imports cannot carry content

The design question was where the substance goes when N agents each read a
different file. The answer came from research, not preference — every per-agent
fact below is sourced in
[/agents/agent-init-conventions.md](/agents/agent-init-conventions.md):

- Only **2 of 12** target agents need an adapter at all (Claude Code and
  Gemini CLI); every other one reads `AGENTS.md` in some form.
- **5 of 12 expand no imports at all.** So a canonical file that delegates its
  substance to `@`-referenced files silently loses that substance on nearly
  half the target set.

Hence the rule the skill enforces: **imports are an adapter mechanism, not a
content-organization one — the canonical file must be self-contained**, and an
adapter contains the import line plus only what is true of that agent and false
of the others.

Generalizing: when a skill emits files for several consumers, the research
question is not "does consumer X read this file" but "does X read it *the same
way*". First-match-wins selection (in Zed a stray `.cursorrules` shadows
`AGENTS.md` entirely — see
[/specs/agents-md-standard.md](/specs/agents-md-standard.md)), concatenation,
byte caps, and import expansion all differ per agent, and each one changes what
you are allowed to write.

## 2. Ask, don't assume — then gate the ask itself

The skill's first iron rule is that every consequential decision is asked, never
assumed. The panel found the hole: that rule is **unsatisfiable in a headless
run** (`-p`, CI, a subagent with no user channel), and the natural fallback is
silent default substitution — exactly what the rule exists to prevent.

The fix became iron rule 4: *if you cannot ask, do not write*. With no user
channel, create no files, emit the full question list, and stop.

Any skill whose correctness depends on a user channel needs the same capability
gate. Interactive-only assumptions are invisible until they are not.

## 3. Bound the loops, not just the content

The loop panel's verdict on the pre-panel skill was blunt: content well
specified, **9 loops, 0 bounds**. Every "for each X, do Y" in a skill is a loop,
and prose loops have no natural terminator.

The worst one: "create a knowledge concept for each technology, and expand it
into follow-up questions" is a rewrite relation with no depth limit. One
scenario produced 9 concepts and 27 extra questions; another produced none —
same instructions. The bounds now shipped:

- expansion depth **1**, expansion items terminal (second-order technologies
  become one-line mentions, not new concepts);
- expand only technologies the user chose **as a project decision** — ecosystem
  defaults accepted from a recommendation do not expand;
- a hard **25-question ceiling** with an explicit continue / recommend-the-rest
  / defer ask, deferred items joining the gap list;
- a **cost preview** — show the number of questions before spending them;
- research effort bounded at 3 fetches per technology, with per-field "not
  applicable" allowed and a gap recorded instead of a stall;
- review **convergence**: one pass plus one re-check of only what changed, never
  a third.

Measured effect on the same scenario: **44 questions → 18**, with the same
output. Bounding a loop is not a quality trade; unbounded loops were paying for
nothing.

## 4. Adaptive review is right, but adaptive means unbounded by default

The skill picks its reviewers from what the run actually produced — the agents
selected, the knowledge subjects written — instead of a fixed roster. That is
the correct shape: a run touching two agents should not pay for six reviewers.

It is also unbounded by construction. One run spawned **11 review passes**. The
protocol now caps the roster at 5 domain reviewers plus 2 standing ones, groups
technologies by shared review surface, **names the grouping in the report**, and
never drops a technology silently.

The second half of a review protocol is adjudication, and it is easy to omit.
"Apply the accepted findings" is not executable when nothing says who accepts,
against what bar, or where a rejection goes. As shipped: the orchestrator
accepts by default and rejects only against an explicit user decision, an iron
rule, or a sourced fact; anything conflicting with a user decision goes back to
the user; every rejection is recorded with a one-line reason in the final
report.

## 5. What the end-to-end runs caught that inspection did not

Two runs (empty directory; existing codebase with merge into a pre-existing
`AGENTS.md`) produced six defects, in two classes — neither visible while
reading the documents one at a time.

**(a) Data the workflow demands but never collects.** The empty-directory run
hit a hard stop in Phase 3: the templates carry `<Project name>` and a project
purpose, the skill forbids any `<...>` placeholder surviving into the target,
and its iron rules forbid inventing one — yet **no interview topic asked for
either**. The only path that produces a name and purpose was "read the existing
README", which an empty directory does not have. Fixed by adding a Project
identity topic. Same class, smaller: a reference promised that context files
hold "the commands an agent runs directly" while the template had no section to
put them in.

**(b) Rules that are individually right and jointly unsatisfiable on one
input.** The codebase run hit two:

- The KB iron rule demanded a resolvable URL for every fact, while the
  knowledge-base preset explicitly invites seeding from an in-repo README that
  has no URL. The rule was simply too narrow — the format already allows a
  path-valued source.
- A user-chosen KB update cadence ("monthly") contradicted the verbatim
  standing-rules block, which says the KB is written *after finishing any piece
  of work*. Two conflicting rules in one generated file, failing the skill's own
  "no two rules conflict" review bar, with no remedy the skill permitted.

Plus two pure-inspection defects the runs surfaced only because someone was
looking: a dangling requirement ID (`R9`) that existed in the internal plan and
in no shipped file, and a format the guide called "fixed" that contradicted the
skeleton the same skill ships.

**The principle:** run the skill on the inputs where a required field has no
source, and where two rules meet. A run is the only thing that forces every rule
to hold *at once*, on one input.

**The second-order lesson:** a fix for a jointly-unsatisfiable pair can itself be
wrong in a way only re-checking catches. The "allow in-project sources" fix
cited a spec category that does not exist (the spec defines absolute URL,
bundle-relative `/…`, and ordinary relative path — and a bare `README.md` inside
the KB folder resolves *inside* it, not to the project README above). The
cadence fix told the generator to override "the bullet it supersedes" when a
non-default cadence conflicts with **two** bullets, leaving the second one
broken. Re-check a fix against the spec text and against every rule it touches,
not just the one that failed.

## 6. What the panel caught that the runs could not

A run proves one path. It cannot see cost, second runs, other harnesses, or
drift between duplicated rules.

- **Cost** — section 3. A loop that happens to terminate looks fine in a
  transcript.
- **Harness assumptions.** No ask channel (section 2). A version check
  hard-coded as `curl | grep`, which falsely branches to "offline" on a harness
  with a fetch tool but no shell — a shell network error is not evidence of
  being offline. Unconditional skeleton instantiation that overwrites an
  existing index and log on a partial re-run. An unvalidated folder name that
  can collide with an existing directory on a case-insensitive filesystem.
- **Duplication drift.** One standing-rules block was kept byte-identical in
  two files "by contract", and the reconciliation rules referenced its bullets
  **by ordinal** — reorder the block and the overrides silently point at the
  wrong rules. Merge semantics was stated four times and had *already* drifted
  between copies. Fix: one source of truth (the template), other sites become
  pointers, and cross-references anchor to bullet **text**, never position.
- **Unmetered reads.** A 512-line reference was loaded whole when a run needs
  one section per selected agent — 71–86% dead weight. Progressive disclosure
  works at file granularity only until a file gets big; then it needs a "read
  only the `## <agent>` section" instruction and a `## Contents` list to make
  that possible.
- **Emergent behavior is a missing instruction, not a success.** Both runs
  warned the user that an agent's native `/init` could clobber the generated
  file — good behavior that appeared in no instruction. In one run that
  emergent warning contained an *invented* claim contradicting the researched
  matrix. If a run does the right thing for a reason the skill never states,
  write the reason down; you are otherwise depending on the model's mood.
- **A large fix wave needs its own review round.** Applying ~65 changes at once
  introduced four new Important contradictions (scope of "expand", where markers
  reach, when the batched ask applies, when existence checks happen). Budget the
  second round.

## 7. Marker idempotency: a writer must recognize its own writes

Originally the skill wrapped generated content in
`<!-- init-project:start -->` / `<!-- init-project:end -->` **only when merging
into a file that already existed**. Fresh files therefore carried no markers, so
a second run could not distinguish its own previous output from the user's
content and appended a full second copy of everything — 82 lines to 164, past
the file's own 150-line budget, and toward another agent's silent 32 KiB
truncation.

Markers are now **unconditional on every generated file**, including the
knowledge-base index, which makes the skill's re-run promise literally true:
*what is between the markers is replaced in place; nothing outside them is
touched*. Two consequences follow directly:

- Markers are matched literally, so they can never be translated (section 8).
- Re-run detection becomes possible at all: a Phase 0 that finds the markers can
  show the previous answers, ask only what changed, and re-research only what is
  stale — making run 2 cheaper than run 1 instead of more expensive.

For any skill that writes into files it may write again, **decide the identity
mechanism first**. Every re-run behavior you can offer is downstream of it.

## 8. A language answer and a verbatim block contradict each other

The skill asks the user which language to write in, and separately ships blocks
that must be reproduced character for character. On a Thai run those two rules
are mutually unsatisfiable, and the same instructions produced three different
behaviors across runs.

The resolution is an explicit **never-translated list** — the standing-rules and
Karpathy blocks, the four HTML markers, YAML keys and `type:` values — with
everything else following the user's answer, plus a one-line note *in the chosen
language* above each fixed block saying it is verbatim from the skill and must
not be edited. Whenever a skill offers a language/style choice, enumerate what
the choice does not apply to; silence there is a defect, not a default.

## 9. Trigger wording: name the built-in you are not

Trigger testing (best-practices §7) showed the description matching Claude
Code's built-in `/init` slash command. One anti-trigger clause naming it — and
what it does instead (writes a single `CLAUDE.md`, no knowledge base) — fixed
it. Final tests: **7/7**, including a bare `/init` prompt where the model
correctly named the built-in rather than the skill.

The harness panel added the other half: some agents inject only ~250 characters
of a description. A description that opens with a capability blurb and ends with
its triggers shows **zero triggers** in that window. Front-load "Use when …" and
the concrete trigger phrases (English before Thai, since the truncation is by
character), put the capability blurb after, and anti-triggers last. Re-run the
trigger tests after any description rewrite — they are cheap and they are the
only evidence that a rewrite did not break discovery.

## Checklist for the next orchestrator-sized skill

1. For every consumer of a generated artifact, record *how* it reads the file,
   not just whether — then design so the weakest reader still gets everything.
2. List the skill's loops. Give each a depth limit, a ceiling, an exit, and a
   cost preview.
3. Gate the assumptions the environment can invalidate: no user channel, no
   shell, no network, a second concurrent run.
4. Decide the write-identity mechanism (markers or equivalent) before writing
   the first template, and make it unconditional.
5. State once, point everywhere. Any rule duplicated across files will drift;
   any cross-reference by position will rot.
6. Run it end to end on the input where a required field has no source, and on
   the input where two rules meet. Then re-check each fix against the spec and
   against every rule it touches.
7. Enumerate what a user's language/style choice does *not* apply to.
8. Cap and adjudicate the review: roster limit, one pass plus one re-check, an
   explicit acceptance bar, and a recorded reason for every rejection.
9. Re-run trigger and anti-trigger tests after any description change, and name
   the built-in commands the skill must not shadow.

## Related

- [/agents/agent-init-conventions.md](/agents/agent-init-conventions.md) — the
  per-agent facts (context files, precedence, imports, native init commands)
  this skill's design conclusions rest on.
- [/skill-authoring/best-practices.md](/skill-authoring/best-practices.md) —
  description writing, progressive disclosure budgets, trigger testing.
- [/skill-authoring/validating-generated-artifacts.md](/skill-authoring/validating-generated-artifacts.md)
  — the sibling failure mode: rules that never reach every phase producing the
  artifact.
- [/specs/agents-md-standard.md](/specs/agents-md-standard.md) — the standard
  the generated canonical file follows, and why per-tool precedence is not
  portable.
