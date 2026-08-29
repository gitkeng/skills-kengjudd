# Root document templates

## README.md

```markdown
# <Project> codebase analysis

Severity: ![critical](badge) <count> · ![high](badge) <count> · ![medium](badge) <count> · ![low](badge) <count>

## Navigation
- [Project overview](project-overview.md) — <one-line description>
- <link every required Markdown and JSON artifact with one-line description>
```

Use text-compatible badges whose counts equal `manifest.severity_counts`. Include all 39 Markdown documents plus both JSON files.

## project-overview.md

Sections: Scope and coverage; Business context; Technology stack (`technology | file-evidenced version | evidence | confidence`); Entry points; Components; Deployment model; Constraints; Assumptions and limitations.

## executive-summary.md

Sections: Scope; Severity-ranked findings (`alias | severity | finding | component | evidence`); Cross-dimension themes; Delta (`state | aliases | count`) with resolved/new/regressed/persisted; Immediate decisions; Limitations.

## reading-guide.md

Table: `audience | start here | then read | questions answered`, with engineering, architecture, business, security, and operations rows.

## technical-debt-report.md

Sections: Severity overview; Ranked debt; Dependencies; Remediation sequence; Resolved actions on re-run; Modernization pathways (`capability | suitability | trade-offs | reversible first step | balanced examples`).

## onboarding.md

Sections: Prerequisites; Configuration; Build; Run; Test; Data setup; Common changes (`task | files | checks`); Key decisions; Security/operations cautions; Troubleshooting; Evidence limitations.

## JSON state

Construct `manifest.json` and `progress.json` from shipped schemas. Use JSON `null`, never placeholder strings, for unknown optional values. Do not leave angle-bracket placeholders in final output.
