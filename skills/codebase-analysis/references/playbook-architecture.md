# Architecture playbook

Method anchors: C4 (https://c4model.com/), ADRs (https://adr.github.io/), and DDD bounded contexts (https://martinfowler.com/bliki/BoundedContext.html).

## System overview

Describe business purpose and C4 system context, containers/deployable units, components, and a code-level view. If a level is genuinely inapplicable, retain its heading and give an evidence-based `not applicable` justification. State deployment model, trust boundaries, external actors/systems, data stores, runtime topology, and architectural constraints. Include Mermaid v11 system and deployment views.

## Components

For every `CMP-NNN`, provide canonical key, path/namespace, responsibility, owned data, entry points, interfaces, dependencies, dependents, and evidence. Separate logical components from deployment containers.

## Dependencies

Map internal and external dependencies. For each integration state direction, sync/async, protocol or mechanism, data exchanged, authentication, timeout/retry/failure behavior, and whether messaging exists or is absent. Include a dependency graph and a failure-impact/single-point relationship where relevant.

## Patterns and decisions

Identify design patterns and anti-patterns only with code evidence. Write inferred decisions as ADR-lite records with exactly: decision, choice, rationale, evidence, confidence, and consequences. Do not invent stakeholder intent; rationale may be an explicitly labeled inference.

All documents cite file:line or path and distinguish verified topology from inferred runtime behavior.
