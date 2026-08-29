# Technical-debt templates

## summary.md

Severity-ranked findings table and debt-versus-quality-attribute matrix: `TD-ID | severity | reliability | security | maintainability | performance | portability | evidence`.

## outdated-components.md

Use exactly:

`component | current version (file-evidenced) | last-known latest/EOL status | verify-at pointer | migration path`

Write `as of model knowledge — verify at <pointer>` unless a live source and date are cited.

## maintenance-burden.md

Narratives per component plus hotspot table: `component | size | complexity estimate | optional churn | coupling | tests | burden | evidence`.

## remediation-plan.md

`order/tier | action | linked aliases | current | target | effort+assumptions | files | approach | validation | dependencies | delta status`.

Explain critical path and parallel actions. On re-run, mark `resolved` only when every linked finding is resolved; otherwise use `open` or `partial`.
