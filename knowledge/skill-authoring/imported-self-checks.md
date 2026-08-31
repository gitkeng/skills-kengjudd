---
type: Playbook
title: Self-checks inside imported skills
description: >-
  What goes wrong when a skill ships its own validation gate and is then
  imported into a repository with different rules: the gate can reject the
  provenance the new repository mandates, it can over-reach onto files that
  never reach the artifact it guards, and its test suite can encode the shape of
  the one fixture it was written against. Worked example: the
  codebase-analysis-report neutrality scanner, which rejected its own SKILL.md
  from the moment it was imported.
tags:
  - skills
  - importing
  - validation
  - testing
  - playbook
sources:
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/codebase-analysis-report/scripts/validate_report.py
    title: The neutrality scanner and its two tiers (verified by local inspection and execution 2026-08-30)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/skills/codebase-analysis-report/scripts/test_report.py
    title: Self-test suite; fixture-shape helpers (100 tests passing on four distinct fixtures 2026-08-30)
  - resource: file:///Users/keng/Coding/gitkeng/skills-kengjudd/CLAUDE.md
    title: Repository rule mandating honest metadata.upstream provenance
  - resource: https://agentskills.io/specification
    title: Agent Skills specification (metadata is a free-form string map)
generated:
  by: claude-code/claude-opus-5
  at: 2026-08-30T00:00:00Z
status: stable
---

# Self-checks inside imported skills

Some skills ship a validation gate that runs on every invocation. When such a
skill is imported, that gate arrives carrying the *source* repository's
assumptions and starts enforcing them against the *destination* repository. This
playbook records the three failure modes seen in practice so a later import does
not rediscover them. The import procedure itself is in
[importing-skills](/skill-authoring/importing-skills.md); this document covers
what happens after the import lands.

## 1. The gate can reject the provenance this repo mandates

`codebase-analysis-report` ships a vendor-neutrality scanner with a denylist
containing `aws` and `atx`. This repository's `CLAUDE.md` requires every
imported skill to record its honest source repository in `metadata.upstream` —
and that source was `gitkeng/aws-kiro-atx-lab`. The skill therefore rejected its
own `SKILL.md` from the moment it was imported, and every render failed at the
publication gate.

The rules were both right; they simply did not know about each other. The fix is
an explicit, narrow exemption in the scanner plus a sentence in the skill's own
hard rules declaring it — because an agent reading only `SKILL.md` otherwise sees
a neutrality rule contradicted by line 7 of the same file, and "fixes" it by
deleting the provenance, violating the no-invented-facts rule.

**This is not a one-off.** The sibling skill `codebase-analysis`
carried the same class of defect from the same import: its
`check_skill_frontmatter` flattened the YAML block, read `metadata.version` as a
top-level key, and failed its own `SKILL.md` against a rule that frontmatter
"must contain only name and description". Two skills, two different checks, one
cause — the source repository did not require `metadata`, and the destination
does.

**Rule of thumb.** When importing a skill that validates anything, grep its
denylists, required-key sets, and path assumptions against this repo's mandated
conventions *before* the first commit. Then run its test suite — the neutrality
failure existed from commit `dea8c66` and went unnoticed because the imported
suite was never executed.

## 2. A gate must cover only what reaches the artifact it guards

The same scanner also checked `SKILL.md`, `README.md`, and `references/*.md`.
None of those contributes a byte to the generated report, yet a hit in any of
them blocked publication. A documentation typo could stop the delivery of a
correct artifact.

Split such a check by *blast radius*:

- **Publication gate** — only files whose text reaches the artifact. Run on
  every invocation; failure blocks publishing.
- **Self-test** — authoring documentation that steers wording but ships nothing.
  Run by the test suite; failure never blocks a user's output.

Two traps when splitting:

- **Do not narrow the surviving gate by accident.** Here the wide-but-wrong doc
  scan had been masking two holes in the real gate: the chrome was matched
  against a narrower second denylist (so bare provider tokens were never checked
  against it at all), and chrome was extracted with a triple-quote regex (so
  wording in ordinary quoted literals escaped entirely). Removing the mask
  without closing the holes would have been a net regression. Walk the module's
  AST for string literals instead of pattern-matching quote styles, and keep one
  denylist.
- **Give the authoring tier a way to run.** Once the doc scan lives only in a
  test suite that requires a large external fixture, nobody editing the docs can
  check their own work. Add a `--self-check` entry point that runs both tiers
  with no fixture and no artifact.

## 3. Failure messages decide how long adjudication takes

The original message was `neutrality: SKILL.md contains branded token 'aws'`. It
named neither the line, nor the text, nor which root `SKILL.md` was relative to —
and the validated report directory has an `assets/` directory of its own, so the
paths are genuinely ambiguous. Diagnosing it took reading the scanner's source,
which the skill's own instructions try to avoid.

A gate message inside a skill should carry the file, the line, the offending
text, and — when paths are relative to something other than the obvious root —
which root. Likewise, if the workflow tells the agent to report a temp path on
failure, the code must actually retain that directory and print it; the renderer
here deleted it in a `finally` block, so the instruction was unfollowable.

## 4. Test suites encode the fixture they were written against

The imported suite hardcoded `BR-007`, `TC-008`, `CMP-001`, and asserted the
literal string `"AWS SDK"` from one finding title — while the skill's own
documentation promised that *any* completed v2 output tree is a valid fixture.
On a different, entirely valid tree the suite failed, and the workflow's gate 5
then said "do not publish".

Deriving values from the fixture at runtime is only half a fix: it converts
"assumes alias `BR-007`" into "assumes a rule with `coverage_status: covered`
exists", which still fails on a legacy repository with no tests. **Synthesize the
shape the case needs into the temp copy instead**, preserving every
cross-manifest invariant the renderer enforces (a synthesized component needs a
matching `coverage.components` entry; a synthesized finding needs its
`severity_counts` bump). Then verify against deliberately sparse fixtures — one
with no vulnerabilities, one with no tests, one with no registries populated at
all — not only the tree the skill was authored against.

## Checklist for the next import of a validating skill

1. Grep the skill's denylists and required-key sets against this repo's mandated
   conventions.
2. Run its test suite before the import commit; a suite that has never run is
   not a passing suite.
3. Classify each self-check by blast radius; keep publication gates to what
   reaches the artifact, and confirm the surviving gate was not silently
   narrowed.
4. Give authoring-tier checks a fixture-free entry point.
5. Make every gate message locate its own hit.
6. Check the suite against a sparse fixture, not just the rich one.
