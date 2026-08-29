# Automation Playbook — Bash / PowerShell

Standalone reference for extracting business rules from shell automation scripts.
Do NOT execute, source, dot-source, or import any discovered script.

---

## 1 Detection & Identification

| Pattern | Indicates |
|---------|-----------|
| `#!/bin/bash`, `#!/usr/bin/env bash` | Bash script |
| `#!/bin/sh` | POSIX sh subset |
| `#!/usr/bin/env pwsh`, `.ps1` extension | PowerShell Core / Windows PowerShell |

**Module & dot-source declarations:**
- Bash: `source helpers.sh`, `. ./lib/common.sh`
- PowerShell: `Import-Module`, `using module`, `. .\Helpers.ps1`

Treat each sourced/imported unit as a dependency boundary. Record but never resolve by execution.

---

## 2 Sourced Functions & Dependencies

- Map every `source`/`.`/`Import-Module`/`using module` to a dependency graph node.
- Functions in sourced files may contain validation rules invisible in the caller; flag unresolved sources (e.g., `source "$LIB_DIR/utils.sh"`) as **expansion-uncertain**.

---

## 3 Parameter Validation

### Bash
```text
while getopts "e:r:" opt; do
  case $opt in
    e) ENVIRONMENT="$OPTARG" ;;
    r) REGION="$OPTARG" ;;
    *) usage; exit 1 ;;
  esac
done
[[ "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]] || die "Invalid environment"
```
Extract: allowed values, required vs optional, defaults, early-exit on violation.

### PowerShell
```text
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateSet('dev','staging','prod')][string]$Environment,
    [ValidateRange(1,100)][int]$Replicas = 3
)
```
Extract: `Mandatory`, `ValidateSet/Range/Pattern/Script`, defaults, `ParameterSetName` groupings.

---

## 4 Environment & Configuration

| Mechanism | Example | Rule signal |
|-----------|---------|-------------|
| Env var with fallback | `DB_HOST="${DB_HOST:-localhost}"` | Default reveals expectation |
| Dotenv loading | `set -a; source .env; set +a` | Config boundary (do not source) |
| PowerShell `$env:` | `$env:APP_TIER` | Runtime config dependency |
| Config file parse | `jq '.timeout' config.json` | Thresholds, feature flags |

Record every env var read and its guard/default as a potential rule.

---

## 5 Exit-Code / Pipeline / Job / Scheduler Workflows

**Exit codes as policy:** Map each non-zero exit to its triggering condition — each is an encoded rule. **Pipeline/CI context:** CI variables (`GITHUB_REF`, `BUILD_NUMBER`) signal deployment-gate rules. Conditional steps encode promotion policy. Cron headers and `Register-ScheduledJob -Trigger` encode timing constraints.

---

## 6 Shell Conditions/Case & PowerShell Switch/Objects

### Bash `case`
```text
case "$ACTION" in
  deploy)   require_approval; run_deploy ;;
  rollback) check_window; run_rollback ;;
  *)        echo "Unknown action"; exit 1 ;;
esac
```
Each branch: action → precondition → outcome = one rule.

### PowerShell `switch`
```text
switch ($Status) {
    'Approved' { Start-Deployment }
    'Pending'  { Send-Reminder }
    default    { Write-Error "Unhandled: $Status"; exit 1 }
}
```
Extract: enumerated states, transitions, default/fallthrough handling.

### PowerShell object pipeline
```text
Get-Service | Where-Object { $_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic' }
```
`Where-Object` encodes the business condition; downstream action encodes response policy.

---

## 7 Expansion Uncertainty

Flag but do not resolve:
- `"$DYNAMIC_PATH/config"` — runtime-dependent path.
- `$(command)` / backtick substitution — result unknown statically.
- PowerShell `$($obj.Method())` — return unknown without execution.
- Here-docs with embedded variables — partial template, partial rule.
Label these **expansion-uncertain** and preserve the raw expression.

---

## 8 Platform Copies

When parallel scripts exist (e.g., `deploy.sh` + `deploy.ps1`):
- Compare for semantic equivalence; divergence indicates platform-specific rules.
- Record shared rules once; annotate deviations separately.
- Treat both as authoritative unless documentation designates one canonical.

---

## 9 Plumbing vs Stakeholder Policy

| Layer | Examples | Rule type |
|-------|----------|-----------|
| **Plumbing** | `scp`, `rsync`, `Copy-Item`, `Start-Process`, `systemctl` | Mechanics |
| **Policy** | Approval gates, promotion order, change windows, rollback criteria | Business rules |

Extract policy as first-class rules. Record plumbing only when it enforces a policy constraint.

---

## 10 Snippet Citation and Secret Safety

Every rule evidence entry still requires an exact verbatim snippet.

1. Prefer an enforcement line/range containing variable references but no literal credential, token, key, or connection string.
2. Cite definition/configuration evidence only when its value is non-secret and supplies business meaning.
3. Never alter, mask, truncate, or replace text inside a snippet claimed as verbatim.
4. If no non-secret verbatim range can support the statement, do not create a BR record from that location. Record a coverage/security open question without copying the secret value.

## 11 Merge / Conflict Policy

- Register shell and PowerShell enforcement sites independently, including platform-specific copies.
- All four dimensions (subject, condition, threshold, outcome) identical: merge into one rule with every evidence entry.
- Any dimension differs: keep separate rules with bidirectional `conflicting_rule_ids`, `needs_review`, and an open question.
- Script order or specificity may explain which branch runs, but must not be used to hide or resolve contradictory policy.
- Source-control conflict regions are unanalyzable coverage findings, not business-conflict records.

## 12 Evidence Layer Mapping

| Artifact | `layer` value |
|---|---|
| Functions, parameter guards, case/switch decisions, calculations | `code` |
| Embedded query text or command-built queries | `sql` |
| Schema/constraint declarations invoked by scripts | `db_constraint` |
| Scheduler definitions, timed jobs, exit-code job sequencing | `batch` |
| Multi-step approval/promotion/rollback flow and pipeline state | `workflow` |
| Interactive prompt/form validation with stakeholder-visible effects | `ui` |
| Environment variables, module data, non-secret policy configuration | `config` |
| Declarative policy maps or decision tables | `rules_engine` |

## 13 Extraction Checklist

- [ ] Detect interpreters, modules, sourced files, functions, entry points, and schedulers without executing them.
- [ ] Extract parameter validation, defaults, guards, exit-code gates, and stakeholder-visible schedules.
- [ ] Trace variables from non-secret definitions through uses and outcomes.
- [ ] Flag dynamic expansion uncertainty and lower confidence.
- [ ] Compare Bash/PowerShell/platform copies with the four-dimension policy.
- [ ] Exclude file/process/deployment plumbing unless it enforces stakeholder policy.
- [ ] Preserve exact non-secret snippets and never expose or fabricate secret values.
- [ ] Assign every evidence entry one canonical `layer` value.
