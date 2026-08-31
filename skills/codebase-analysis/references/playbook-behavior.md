# Behavior playbook

Method anchor: DDD bounded contexts (https://martinfowler.com/bliki/BoundedContext.html).

Open each behavior document with `> Confidence: <high|medium|low> — <basis and coverage>.` Use `high` only when all material paths were read directly, `medium` when some behavior is inferred or sampled, and `low` when key dynamic/runtime evidence is unavailable. Individual claims still use `verified`, `inferred`, or `assumption`.

## Business logic

Organize by business capability or user journey, never controller/class/function headings. Explain rules in plain language. Register each rule as `BR-NNN` with a content-derived canonical key. Always include a nonempty glossary. Define every domain or code-derived term used in the behavior documents that a non-specialist reader may not know; each entry contains a plain-language definition and the corresponding code identifier when one exists.

End with the exact traceability schema:

`BR-ID | rule (plain language) | source file:line | covering TC-IDs | coverage status`

Coverage is `covered` when at least one `TC-NNN` specification is linked and `untested` only when no test specification exists; never leave it blank. Record every BR-to-TC mapping in manifest `traceability`, including specifications whose implementation status is not `existing`.

## Workflows

For each key journey, state actor, trigger, code entry point, preconditions, numbered steps, state/data effects, external interactions, success, and failures. Render Mermaid v11 flowcharts anchored to entry-point evidence.

## Decision logic

For every material branch point, write a decision tree or language-neutral pseudocode that covers conditions, precedence, defaults, side effects, and fall-through/error branches. Cite the branch lines.

## Error handling

Catalog handlers by boundary, exception/status, response, logging, retry/recovery, and evidence. Add a missing-handling gap table and recovery-pattern summary. Any latent null, race, swallowed error, unsafe default, or impossible state becomes a manifest finding with severity, not a prose aside.
