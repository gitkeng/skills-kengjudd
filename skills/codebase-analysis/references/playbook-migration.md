# Migration playbook

Migration remains target-platform-neutral: describe capabilities and dependencies, not an assumed host. A direct runtime/framework successor is allowed when supported by evidence.

## Component order

Sequence changes at file/component level. For each step include component alias, files, prerequisite, reason, data/API compatibility, rollback boundary, and validation. Show the critical path and independent parallel workstreams. Place characterization and observability work before behavior-changing migration.

## Characterization tests

Use preserved `TC-NNN` aliases. Each specification includes canonical key, source alias, the source rule/finding in plain language, purpose, setup/fixtures, stimulus, expected observable result, edge/error case, and evidence. Plain-language text states actor, condition or trigger, and observable outcome in complete sentences, with code-only terms defined or omitted.

- Behavioral tests reference a `BR-NNN`.
- Security/infrastructure tests reference a `V-NNN`, `TD-NNN`, or `CMP-NNN`.
- Every `BR-NNN` links to at least one test specification and is `covered`, or has no test specification and is explicitly `untested` in manifest and behavior traceability.
- Record every linked BR/TC pair in manifest `traceability`; a `specification` TC counts as traceability coverage even though it is not an implemented test.

Do not claim that a test exists unless a test file is observed; these are specifications when not implemented.

## Validation criteria

For every migration criterion provide linked components/findings/tests, validation method, measurable pass condition, evidence/data needed, stage, and owner role (not a named person). Avoid vague conditions such as “works” or “improves.” Include functional parity, security, data integrity, performance baseline, rollback, and operational readiness where applicable.
