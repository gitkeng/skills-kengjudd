---
type: Playbook
title: Validating artifacts a skill generates
description: >-
  When a skill emits an artifact that some other tool must parse — Mermaid,
  JSON, SQL, a config file — a hand-written checker measures what is easy to
  measure, not what decides success. Three failure modes seen in practice: a
  balance check standing in for a parser, acceptance criteria defined as
  "passes our lint", and syntax rules living in a reference that most producing
  phases never load. Worked example: Mermaid in comprehensive-codebase-analysis,
  then ported to business-rules-extraction.
tags:
  - skills
  - validation
  - mermaid
  - testing
  - playbook
sources:
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/comprehensive-codebase-analysis/scripts/validate_output.py
    title: The Mermaid checker before and after (verified by execution against the real parser 2026-08-30)
  - resource: https://mermaid.js.org/
    title: Mermaid documentation — diagram grammars and v11 syntax
  - resource: file:///Users/keng/Coding/finoniq/docugent/codebase-analysis
    title: Real v2 output tree with three unrenderable diagrams that the checker passed (local inspection 2026-08-30)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/business-rules-extraction/scripts/validate_output.py
    title: The same linter ported as check class 11 (calibrated by execution against mermaid 11.17.2, 2026-08-31)
generated:
  by: claude-code/claude-opus-5
  at: 2026-08-30T00:00:00Z
status: stable
---

# Validating artifacts a skill generates

A skill that writes Mermaid, JSON, SQL, YAML, or any other language for a
downstream tool needs to answer one question: *will the consumer accept this?*
Hand-written checkers reliably drift into answering an easier question instead.
This playbook records how that drift looked and what fixed it. Related:
[imported-self-checks](/skill-authoring/imported-self-checks.md), which covers gates inherited at import time.

## 1. A balance check is not a parser

`comprehensive-codebase-analysis` validated Mermaid with `balanced()` — a
bracket matcher — plus a first-token check. It reported `PASS: Mermaid v11
syntax` on an output tree with **three diagrams that render nothing at all**.
Every one had perfectly balanced brackets:

| Written | Why it is fatal |
| --- | --- |
| `docugent -->[("MongoDB")]` | Shapes attach to a node id; there is no anonymous node. After an arrow the parser wants an id and gets `CYLINDERSTART`. |
| `actor caller["Upstream"]` in a `flowchart` | `actor` is a `sequenceDiagram` keyword. In a flowchart an actor is just a node. |
| `H->>H: merge groups; mark skipped` | Sequence message text is unquoted, so `;` is a statement separator: it truncates the message and orphans the rest. |

Note the shape of these bugs: they are **cross-cutting context errors**, not
malformed tokens. A checker built on counting delimiters cannot see any of them,
because delimiters are not what is wrong.

Two rules follow.

**Calibrate against the real parser, not against intuition.** Build a suite of
valid and invalid samples, run the genuine consumer over it, and compare. Doing
this surfaced three constructs a first draft rejected wrongly — `loop["Per page"]`
(an ordinary node in a flowchart, a block opener in a sequence diagram), the
`end note` of a `stateDiagram`, and `<|..` in a `classDiagram`. Shipping that
draft would have blocked correct work. The corrected rules key off the diagram
type and score 26/26 against the parser with zero false positives.

**Prefer false negatives to false positives.** A heuristic that misses a bug
costs one broken diagram. A heuristic that rejects valid output blocks the whole
deliverable and teaches everyone to distrust the gate.

## 2. Do not define acceptance as "passes our lint"

The skill's acceptance criterion read *"Every required Mermaid artifact passes
the shipped lint."* That is circular: the bar is whatever the weakest available
tool happens to measure, so the criterion moves down whenever the tool is weak.
It also tells the agent that satisfying the checker is the goal.

State the real property, then name the tool as partial evidence for it — *"every
Mermaid block renders; the lint catches common fatal mistakes but is a
heuristic, not a parser, so passing it is necessary, not sufficient."*

## 3. Rules must reach every phase that produces the artifact

The syntax guidance lived in `playbook-diagrams.md`, loaded only by the
operations-and-diagrams phase. But four phases write Mermaid — architecture,
behavior, reference-analysis, and diagrams. **Three of them never saw the rules
at all**, and the first real bug was written by one of those three.

This is a hazard specific to progressive disclosure: `Load only <these files>`
is what keeps context lean, and it silently starves any concern that cuts across
phases. When guidance applies to more than one phase, extract it into its own
small reference and add it to every producing phase, rather than leaving it
inside the reference of whichever phase happens to own the topic.

Then check the reverse direction too: the checker only inspected the six files
where a diagram was *required*, while templates asked for diagrams elsewhere —
so `architecture/dependencies.md` was never validated. "Where the artifact must
exist" and "where the artifact must be valid" are different sets; the second is
usually "anywhere it appears".

## 4. Look for the example that taught the mistake

The templates were all valid — verified by parsing every one. But
`template-architecture.md` and `template-diagrams.md` used `actor` as a **node
id** in flowcharts, while `template-diagrams.md` used `actor` as a **keyword**
in sequence diagrams, and the playbook asked for several actors in one
system-context view. A node id cannot be reused, so an agent needing two actors
naturally reached for the declaration form it had seen elsewhere in the same
skill — which is a parse error.

An example that is individually correct can still be a trap when it collides
with a keyword. Choose demonstration identifiers that are not reserved anywhere
in the target language.

## 2026-08-31 — ported to `business-rules-extraction`

The same gap existed one skill over: `business-rules-extraction` mandates three
Mermaid diagrams per domain and had **no Mermaid check at all**, no syntax
reference, and no rendering criterion. The v0.9.0 work transferred whole — the
linter as check class 11, `references/mermaid-syntax.md`, the `actor` hazard
note in the templates, and acceptance restated as "every block renders".

Three things the port confirmed or corrected:

- **A ported heuristic still needs its own calibration run.** Re-running the
  20-block fixture through mermaid 11.17.2 reproduced 20/20 agreement with zero
  false positives — including the three traps that broke the original draft. The
  rules survived transplant intact, but the cost of *assuming* that is a broken
  gate in a second skill, which is exactly how the two imported-self-check
  defects reached production (see [imported-self-checks](/skill-authoring/imported-self-checks.md)).
- **The heuristic has a documented blind spot.** `;` inside a `sequenceDiagram`
  message is fatal *even when quoted* — verified against the parser. The lint
  masks quoted spans before its rules run, so it is silent on that form. This is
  the intended trade (a missed case costs one diagram; a false positive blocks
  the deliverable), but a blind spot the tool cannot see must be written where
  the *author* will: the ported `references/mermaid-syntax.md` states it
  explicitly instead of leaving it implicit in the code. The sibling skill's
  copy does not yet say so.
- **"Never scan the skill's own files" is cheapest as a structural property.**
  The 0.9.1 defect existed because the sibling validator judges its own
  `SKILL.md`. This validator takes one output directory on the command line and
  reads nothing else, so the whole failure class is absent by construction —
  worth preserving deliberately when adding checks, not just avoided once.

## Checklist

1. Identify the real consumer of the artifact and what it rejects.
2. Build a valid/invalid suite and calibrate the checker against that consumer;
   record the false-positive count and drive it to zero.
3. Write acceptance criteria as a property of the artifact, never as "passes
   our checker".
4. Validate the artifact everywhere it appears, not only where it is required.
5. Route cross-cutting syntax rules to every phase that produces the artifact.
6. Audit templates for identifiers that collide with the target language's
   keywords.
7. When a sibling skill emits the same artifact, port the checker *and* re-run
   the calibration there — a transplanted heuristic is unverified until it has
   faced the real consumer in its new home. Record what it still cannot see.
