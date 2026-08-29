# Analysis templates

## code-metrics.md

State method and exclusions. Tables: language/file/LOC estimates; component size; quality indicators; internal/external dependency counts.

## complexity-analysis.md

`symbol | path:line | decisions | M=decisions+1 | NIST boundary status | optional churn | centrality | test signal | confidence`

State that 10 is the simple-structure boundary and that results are estimates. Add heuristic duplication and maintainability sections with methods.

## dependency-analysis.md

`component | Ca | Ce | I=Ce/(Ca+Ce) | estimate basis | evidence`; use `n/a` for zero denominator.

Failure table: `dependency/component | failure mode | blast radius | single point? | mitigation | evidence | confidence`.

## security-patterns.md

Access-control matrix: `endpoint | verb | authentication | role/policy/ownership | evidence | gap`.

Request-forgery matrix: `state-changing endpoint | credential mode | token/control | evidence | gap`.

## tech-debt.md

`TD-ID | canonical key | concrete defect | severity | quality impact | remediation direction | evidence | confidence`.
