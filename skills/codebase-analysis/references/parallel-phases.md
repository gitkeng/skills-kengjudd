# Parallel phases

How to run Phases 2–7 as concurrent subagents when the harness can spawn
them. Sequential mode (SKILL.md as written) stays the default and the
fallback; parallel mode changes **who writes what and when aliases are
minted**, nothing about the documents themselves.

## Contents

- [When to use it](#when-to-use-it)
- [Groups and dependencies](#groups-and-dependencies)
- [What a subagent may and may not do](#what-a-subagent-may-and-may-not-do)
- [Entry fragments](#entry-fragments)
- [Alias placeholders](#alias-placeholders)
- [Subagent brief](#subagent-brief)
- [Orchestrator steps](#orchestrator-steps)
- [Resume and failure](#resume-and-failure)

## When to use it

Use parallel mode when all of these hold:

- your harness can run several subagents at once and wait for all of them;
- Phase 1 is complete and checkpointed, so every subagent starts from the
  same inventory, component list and depth decisions;
- the repository is large enough that the phases' reading time dominates
  (each subagent re-reads the focus files — parallel mode trades tokens for
  wall-clock time).

Stay sequential for a small repository, when a prior `manifest.json` exists
and you want to review alias matches as you go, or when the harness cannot
guarantee that subagents see the same files.

## Groups and dependencies

| Group | Phases (subagents) | Needs | Produces |
| --- | --- | --- | --- |
| A | 2 Architecture, 3 Behavior, 4 Reference and analysis, 5 Debt and specialized | Phase 1 checkpoint | their documents + one entry fragment each |
| B | 6 Operations and diagrams, 7 Migration and onboarding | Group A complete (6 draws on components and behaviors; 7 links tests to `br`/`v`/`td`/`cmp` keys) | their documents + fragments |
| — | 8 Synthesize and validate | Group B complete | run by the orchestrator, never a subagent |

Each subagent loads only the references its phase lists in SKILL.md, writes
only its phase's documents, and never touches `manifest.json`,
`progress.json`, `README.md` or another phase's files.

**Assign registry ownership before dispatching.** Tell each subagent which
registries it may register — normally `cmp` to Phase 1 (already done),
`br` to Phase 3, `td` to Phase 4 for code-level debt and to Phase 5 for
dependency, security and operational debt, `v` to Phase 5, `tc` to Phase 7 —
and that anything it notices outside its registries goes into its report,
not its fragment. The first end-to-end run did this and finished with no
duplicate registrations; without it the resolver's "registered twice with
different content" error is the likely outcome.

## What a subagent may and may not do

- **May** read the repository, the Phase 1 checkpoint (`progress.json`), the
  prior snapshot `.work/prior-manifest.json`, and its own references.
- **May** register entries — business rules, findings, components it
  discovers beyond Phase 1, test cases, traceability links — in its fragment.
- **Must not mint aliases.** It knows canonical keys (per
  `references/evidence-and-identity.md`) but not which numbers are free;
  two subagents would mint the same `TD-007`. It writes
  `{{alias:<canonical-key>}}` wherever a document or a `source_refs` /
  `traceability` field needs an alias.
- **Must not** write `progress.json`; the orchestrator checkpoints each group.

## Entry fragments

`<output-root>/.work/entries-<phase-id>.json`, one per subagent, where
`<phase-id>` is the id SKILL.md's Phase 0 lists (`architecture`,
`behavior`, `reference-analysis`, `debt-specialized`, `operations-diagrams`,
`migration-onboarding`). Shape: the manifest's own record types with the
`alias` field **omitted**:

```json
{
  "phase": "behavior",
  "business_rules": [
    {"canonical_key": "br:src/orders/service.py:minimum-total:place-order",
     "rule": "An order below the minimum total is rejected.",
     "confidence": "verified",
     "evidence": [{"path": "src/orders/service.py", "line_start": 41, "line_end": 48}],
     "coverage_status": "untested"}
  ],
  "findings": [],
  "components": [],
  "test_cases": [],
  "traceability": []
}
```

`findings` carry `registry` (`td` or `v`) as in the manifest. A `test_cases`
entry's `source_refs` and a `traceability` link's two fields hold
placeholders, not aliases. The same canonical key may appear in two
fragments only with identical content; a disagreement stops resolution and
is reported.

## Alias placeholders

Grammar: `{{alias:<canonical-key>}}`, for example
`{{alias:td:src/auth/handler.cs:missing-request-token:submit}}`. Use it in
prose, tables and JSON string fields exactly where the alias would go.
`scripts/resolve_aliases.py` replaces every occurrence in every `*.md`
under the output root and in the fragments; a placeholder whose key no
fragment registered makes the script exit 1 and list the keys, so a dangling
reference cannot reach the final output. Do not invent an alias to avoid a
placeholder — that is what the sequential rule "match canonical keys before
minting" protects against.

## Subagent brief

Give every subagent this, filled in, followed by SKILL.md's
`## Non-negotiable rules` and `## Severity scale` verbatim:

> Run Phase {N} — {name} of the codebase-analysis skill for the repository
> at {repo-root}; the output root is {output-root}. Phase 1 is complete:
> read {output-root}/progress.json for the inventory, components and depth
> decisions, and {output-root}/.work/prior-manifest.json (if present) for
> the previous run's canonical keys. Load only these references from the
> skill directory {skill-dir}: {the "Load only" list of Phase N}. Write only
> these documents: {Phase N's document list}. Register every business rule,
> finding, component, test case or traceability link you create in
> {output-root}/.work/entries-{phase-id}.json in the shape of
> references/parallel-phases.md § Entry fragments, with canonical keys and
> **no aliases**; wherever a document or field needs an alias write
> `{{alias:<canonical-key>}}` instead. Do not write progress.json,
> manifest.json, README.md or any other phase's files. Report the documents
> and the fragment you wrote, and anything you could not assess.

## Orchestrator steps

1. **Phase 0.** Besides the normal steps, copy an existing `manifest.json`
   to `<output-root>/.work/prior-manifest.json` — the read-only prior
   snapshot the subagents and the resolver use.
2. **Phase 1** as written, then checkpoint.
3. **Group A.** Dispatch Phases 2–5 concurrently with the brief above. When
   all four report, check that each phase's documents exist and its fragment
   parses; checkpoint the four phases in `progress.json`.
4. **Group B.** Dispatch Phases 6–7 the same way; check; checkpoint.
5. **Phase 8.** Run
   `python3 <skill-root>/scripts/resolve_aliases.py <output-root>`. It
   merges the fragments, reuses prior aliases, mints the rest, rewrites
   every placeholder in the documents, and writes
   `.work/entries.resolved.json` with `business_rules`, `findings`,
   `components`, `test_cases`, `traceability`, `severity_counts` and
   `delta` (findings only, as the validator requires). Exit 1 means
   unresolved placeholders: fix the fragment or the document, re-run. Then build `manifest.json` from the resolved entries
   plus `coverage` and `documents` as SKILL.md's Phase 8 says, write the
   root documents and README, and **delete `<output-root>/.work/`** — the
   validator rejects unexpected files. Finish with
   `python3 <skill-root>/scripts/validate_output.py <output-root>`.

## Resume and failure

- A subagent that fails or times out leaves its phase `pending`; re-dispatch
  only that phase (its documents, if partial, are overwritten).
- If the orchestrator is interrupted inside a group, the phases already
  reported complete keep their fragments; on resume re-dispatch the missing
  ones. Never resume Phase 8 from a partial `.work/` — all six fragments
  must be present.
- A subagent may report that it could not write one of its documents (a
  harness hook or sandbox rule refused the path). Its fragment is still
  valid; the orchestrator writes that document from the content the
  subagent returned, then continues.
- A resolver error about a key "registered twice with different content"
  means two phases described the same defect differently. Keep one
  description (usually the phase that owns the registry: `br` → behavior,
  `td` → reference-analysis or debt, `v` → debt-specialized, `tc` →
  migration) and delete the other entry, then re-run the resolver.
