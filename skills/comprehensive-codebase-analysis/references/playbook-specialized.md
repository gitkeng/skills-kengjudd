# Specialized analysis playbook

Security source: OWASP Top 10:2025 (https://owasp.org/Top10/2025/). Inventory formats may align with SPDX (https://spdx.dev/about/overview/) or CycloneDX (https://cyclonedx.org/specification/overview/).

## Database patterns

Document stores, connection/configuration evidence, ORM mappings, entity relationships, migrations, transactions, query patterns, ownership, and schema concerns. Produce inferred DDL with `inferred` labels. Map representative ORM queries to likely SQL and label dialect/translation uncertainty. Cover keys, constraints, indexes, nullability, precision, cascade behavior, concurrency, N+1/unbounded access, seed data, and migration rollback.

## Security analysis

Organize findings in this published OWASP Top 10:2025 order: A01 Broken Access Control; A02 Security Misconfiguration; A03 Software Supply Chain Failures; A04 Cryptographic Failures; A05 Injection; A06 Insecure Design; A07 Authentication Failures; A08 Software or Data Integrity Failures; A09 Security Logging and Alerting Failures; A10 Mishandling of Exceptional Conditions. Include categories with no finding and cite https://owasp.org/Top10/2025/.

Register each concrete vulnerability as `V-NNN` with canonical key, CWE, severity, confidence, impact, exploit preconditions, `file:line`, remediation, and a concrete minimal fix snippet adapted to the observed language. Do not include weaponized exploit instructions.

Build per-endpoint access-control and request-forgery matrices or cross-link the analysis matrix. Distinguish remediated controls from open vulnerabilities.

Scan source/configuration and available history only when local tooling permits for secret patterns. Redact values to type plus final four characters at most; do not copy credentials into output.

Create an SBOM-style inventory with component, file-evidenced version, supplier when evidenced, license or `unknown`, source manifest, direct/transitive/unknown scope, and confidence. Do not claim vulnerability status without an evidence source/date.
