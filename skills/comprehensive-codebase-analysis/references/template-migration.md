# Migration templates

## component-order.md

`order | CMP-ID | files | prerequisite | compatibility/data concern | reason | validation | rollback boundary | stream`

Follow with a critical-path list and parallel-workstream table.

## test-specifications.md

### TC-NNN — <observable behavior>
- Canonical key: `tc:<path>:<kind>:<symbol-or-ordinal>`
- Category: behavioral | security | infrastructure
- Source aliases: BR-NNN or V-NNN/TD-NNN/CMP-NNN
- Setup/fixtures: <state>
- Stimulus: <action>
- Expected result: <measurable observation>
- Edge/error result: <measurable observation>
- Evidence: `path:line`
- Status: specification | existing

## validation-criteria.md

`criterion | linked aliases | validation method | measurable pass condition | required evidence/data | stage | owner role`.

Include applicable functional parity, security, data integrity, performance baseline, rollback, and operational-readiness criteria. Never use “works” as a pass condition.
