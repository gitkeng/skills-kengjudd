# Operations playbook

## Build, delivery, and infrastructure

Inventory build commands and prerequisites from files. Use this minimum detection map, then extend it for repository-specific formats:

| Format | File-observable patterns |
|---|---|
| GitHub Actions | `.github/workflows/*.yml`, `.github/workflows/*.yaml` |
| GitLab CI | `.gitlab-ci.yml`, included pipeline YAML |
| Jenkins | `Jenkinsfile`, files named `Jenkinsfile*` |
| Azure Pipelines | `azure-pipelines.yml`, pipeline YAML references |
| CircleCI | `.circleci/config.yml` |
| Bitbucket Pipelines | `bitbucket-pipelines.yml` |
| Tekton/Argo | YAML kinds for pipeline/task/workflow resources |
| CloudFormation/CDK/SAM/buildspec | template markers, CDK manifests/source, `samconfig*`, `buildspec*.yml` |
| Bicep/ARM | `*.bicep`, deployment-template JSON schema/markers |
| Cloud Build | `cloudbuild.yaml`, `cloudbuild.yml` |
| Terraform/OpenTofu | `*.tf`, `*.tf.json`, lock files |
| Pulumi | `Pulumi*.yaml`, project source references |
| Kubernetes/Helm | resource `apiVersion`/`kind`, `Chart.yaml`, chart templates |
| Dockerfile/Compose | `Dockerfile*`, `compose*.yml`, `docker-compose*.yml` |
| Ansible | playbooks, inventories, roles, collections |
| Chef/Puppet | recipes/cookbooks and manifests/modules |

For each detected file, map triggers, stages, tests, artifacts, environments, approvals visible in code, secrets references, deployment targets, rollback/health checks, and evidence. State absent formats as `not detected`, not as proof they are unused externally.

Assess supply-chain posture from files only: lock/pinning, build provenance configuration, dependency update/scanning configuration, SAST/lint, workflow token permissions, third-party action/plugin pinning, artifact integrity/signing configuration, committed binaries, license/security policy, and dangerous script interpolation. For committed binaries, record path, type, source/provenance evidence, reproducibility, integrity verification, and whether first-party source can rebuild them; derive severity from executable risk and missing provenance rather than file count. Host-side controls remain `not assessable from local checkout` without repository evidence.

## Testing and observability

Inventory test frameworks, suites, commands, fixture/data strategy, coverage configuration/reports, and gaps by component/capability. When no test framework or suite is observed, record a repository-wide `total absence` gap before component gaps. Do not invent coverage percentages.

Classify telemetry using OpenTelemetry signal taxonomy (https://opentelemetry.io/docs/concepts/signals/): traces, metrics, and logs. Include non-OpenTelemetry libraries and framework loggers in the appropriate signal, plus error-reporting/diagnostic middleware. For each signal record framework, instrumentation point, propagation/correlation, exporter/sink configuration, sensitive-data risk, evidence, and gap. Inventory route names such as health/ready, framework health registrations, container `HEALTHCHECK`, orchestration liveness/readiness/startup probes, alert/rule files, dashboards, and runbooks when present.
