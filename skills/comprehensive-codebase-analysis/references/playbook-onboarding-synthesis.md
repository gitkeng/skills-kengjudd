# Onboarding and synthesis playbook

## Onboarding

Derive commands from build files and documentation; do not execute them. Document prerequisites and file-evidenced versions, environment/configuration setup with redacted values, build, run, test, database preparation, common failure hints, and limitations. If a command is inferred, label it and say how to verify.

Map common changes to concrete locations: add/modify an endpoint, business rule, data field/migration, UI, integration, test, configuration, telemetry, and deployment. Summarize key architecture decisions, security boundaries, data ownership, generated-code rules, and risky hotspots newcomers must understand.

## Root synthesis

`project-overview.md` covers business context, stack, entry points, deployment, components, and analysis coverage. `executive-summary.md` ranks findings globally by severity and contains the re-run delta table. `reading-guide.md` routes engineering, architecture, business, security, and operations audiences. `technical-debt-report.md` ranks debt and closes with neutral modernization pathways.

`README.md` links every required Markdown and JSON artifact, each with one-line description, and displays severity badges derived from manifest counts.

Before final writing, reconcile duplicate prose findings to one manifest record, verify confidence/evidence, preserve aliases, compute deltas by canonical membership/severity, resolve traceability, and ensure all claims agree across documents.
