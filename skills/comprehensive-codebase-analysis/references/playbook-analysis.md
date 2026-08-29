# Analysis and metrics playbook

Sources: McCabe/NIST SP 500-235 (https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication500-235.pdf); Martin, “OO Design Quality Metrics: An Analysis of Dependencies” (1994); ISO/IEC 25010:2023 explainer (https://www.sonarsource.com/resources/library/iso-iec-25010-explained/).

## Metrics

Report file/component source size, method/type counts where observable, test signals, quality indicators, and internal/external dependency counts. State exclusions and whether measured or estimated.

Estimate cyclomatic complexity as `M = decisions + 1` per function/method using a documented language convention. Use 10 as the NIST SP 500-235 simple-structure boundary; report values above 10 as review hotspots, not automatic defects.

For each component estimate afferent coupling `Ca`, efferent coupling `Ce`, and instability `I = Ce/(Ca+Ce)`; use `I = n/a` when both are zero. Label coupling and instability estimates. Label duplication and maintainability estimates heuristic and explain the heuristic.

## Complexity hotspots

Rank by complexity, size, optional churn, centrality, security boundary, and test gaps. Cite every hotspot.

## Dependency analysis

Map dependency direction, version evidence, criticality, cycles, and replaceability. Include a failure-impact and single-point-of-failure table with component/dependency, failure mode, blast radius, existing mitigation, evidence, and confidence.

## Security patterns

For every endpoint where applicable, create access-control and request-forgery-protection matrices with route/action, verb, authentication, role/policy/ownership, token protection, evidence, and gap. Distinguish authentication from authorization.

## Debt assessment

Turn only located quality defects into manifest findings. Relate impacts to applicable ISO/IEC 25010 quality characteristics without inventing certification claims.
