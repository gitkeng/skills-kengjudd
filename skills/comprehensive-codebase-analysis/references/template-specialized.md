# Specialized templates

## database-patterns.md

Sections: Store/configuration inventory; Entity-to-store mapping; Relationships and ownership; Transaction patterns; ORM query to inferred SQL mapping; Inferred DDL; Schema concerns; Migration/recovery.

ORM mapping: `source operation | inferred SQL/dialect | parameters | transaction | risk/concern | evidence | confidence`.

Fence inferred DDL as SQL and label it `inferred`; include PK/FK/nullability/index assumptions explicitly.

## security-analysis.md

Start with scope, coverage, and redaction method. Create a section for each OWASP Top 10:2025 category in published order.

Vulnerability registry:

`V-ID | canonical key | OWASP category | CWE | severity | impact | exploit preconditions | evidence | confidence | remediation`

Each open vulnerability includes a minimal language-appropriate fix snippet and verification step. Remediated controls belong in a separate posture table, not the open registry.

Secrets scan: `location | secret type | redacted indicator | status | evidence`; never include a full value.

SBOM inventory: `component | version | supplier (if evidenced) | license/unknown | source manifest | direct/transitive/unknown | confidence`.
