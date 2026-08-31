# Inventory playbook

Produce the evidence base used by later documents; do not create a separate inventory output.

1. Enumerate top-level and component trees, first-party files, manifests, entry points, build/test/configuration files, data stores, pipelines, infrastructure, and deployment descriptors.
2. Detect languages with `languages.md`; record counts/shares and exclusions.
3. Detect frameworks and file-evidenced versions without claiming current support status.
4. Register logical components using path/namespace canonical keys and `CMP-NNN` aliases.
5. Trace entry points to components and externally visible interfaces.
6. Identify implicit contracts: setting keys, environment variables, named connections, feature flags, file locations, ports, and secrets references.
7. Record coverage per component as fully read, sampled, or inventory only.
8. Use optional repository history only for churn; do not require it.

Feed project-overview, program-structure, metrics, operations, onboarding, and manifest coverage. Every stack/version claim includes file evidence. Distinguish first-party, generated, vendored, tests, and assets.
