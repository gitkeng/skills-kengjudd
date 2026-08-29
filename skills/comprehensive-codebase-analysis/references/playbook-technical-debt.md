# Technical-debt playbook

Use `TD-NNN` for concrete debt findings and preserve aliases by canonical key.

## Summary

Rank debt by severity and include a debt-versus-quality-attribute impact matrix. For each finding provide title, severity, confidence, evidence, consequence, affected components, and remediation direction.

## Outdated components

Use exactly these columns:

`component | current version (file-evidenced) | last-known latest/EOL status | verify-at pointer | migration path`

Without a successful live lookup, write the status as `as of model knowledge — verify at <pointer>` and point to https://endoflife.date/ or the relevant package registry. With a live lookup, cite source and lookup date. Never infer “latest” or EOL from memory. A direct successor in the same product line is allowed; otherwise keep paths capability-based and neutral.

## Maintenance burden

Explain burden narratives with evidence and include a hotspot table covering size, estimated complexity, optional churn, coupling, knowledge concentration signals, test gaps, and operational impact.

## Remediation plan

Prioritize tiers by risk, dependency order, reversibility, and prerequisite. Every action includes linked aliases, current state, target state, effort (`small|medium|large` with assumptions), files, approach, validation, dependencies, and execution order. Auto-mark an action `resolved` on re-run only when all linked findings are in `delta.resolved`.

Close the root debt report with modernization capability pathways. Each pathway gives suitability, trade-offs, first step, and—only if examples are useful—a neutral list of at least three choices spanning at least two providers or hosted plus self-hosted. Never recommend a vendor-specific follow-on analysis.
