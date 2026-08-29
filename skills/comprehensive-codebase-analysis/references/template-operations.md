# Operations templates

## build-cicd-iac.md

Sections: Build inventory; Pipeline/IaC detection matrix; Detected pipeline flows; Deployment/runtime topology; Container posture; File-observable supply-chain posture; Gaps and limitations.

Detection matrix: `format/tool | detection patterns | detected paths | status | evidence`. Include every format mandated by the operations playbook, even when not detected.

Pipeline table: `file | trigger | stages/jobs | build/test | artifacts | environment/target | secret references | rollback/health | evidence`.

Supply-chain table: `control | observed configuration | gap | severity | evidence | locally assessable?`.

## testing-observability.md

Test table: `framework/suite | type | location | command evidence | count/signal | coverage signal | component/capability gap`.

Telemetry inventory: `signal (traces/metrics/logs) | framework/library | instrumentation points | propagation/correlation | exporter/sink | sensitive-data control | evidence | gap`.

Include non-OTel loggers and error middleware under logs. Add health/readiness, alert/rule, dashboard, and runbook inventories. State that missing local files do not prove missing host-side configuration.
