# Input contract (normative)

This is the single field-to-view map shared by the workflow and the scripts. It
binds to the real `comprehensive-codebase-analysis` v2 keys and enums. Unknown
schema versions or keys fail closed with an unsupported-contract message. The
new skill has no runtime dependency on the sibling analyzer; if its validator is
discoverable it may be run as optional corroboration only.

## Versions and completion

- Both `manifest.json.schema_version` and `progress.json.schema_version` must
  equal `2.0`.
- The source is **complete** only when all hold:
  - `progress.status == "completed"`,
  - `progress.current_phase == "completed"`,
  - `progress.phases` has exactly the eight declared IDs, in order:
    `inventory, architecture, behavior, reference-analysis, debt-specialized,
    operations-diagrams, migration-onboarding, synthesis`,
  - every `phases[].status == "completed"`.
- An incomplete source renders only with explicit approval and a persistent
  warning banner.

## Coverage

- `coverage.mode` in `full | focused | sampled`.
- `coverage.components[]` each has `component_alias` (`CMP-000`), `depth`
  (`fully-read | sampled | inventory-only`), `files_read[]`, `rationale`.
- `coverage.limitations[]` are strings shown verbatim.
- The set of `component_alias` equals the set of `components[].alias`.

## Documents

- `documents[]` each has `path`, `description`, `severity_badge`
  (`critical|high|medium|low|none`). Declaration order is preserved.
- Render only `.md` entries as Markdown. Expose `manifest.json` and
  `progress.json` in About as source-data references, never as Markdown.

## Findings

- `findings[]`: `registry` (`td|v`), `alias` (`TD-000`/`V-000`), `title`,
  `kind`, `severity` (`critical|high|medium|low`), `confidence`
  (`verified|inferred|assumption`), `status` (`open|accepted|remediated`),
  `evidence[]` (`path`, `line_start`, `line_end`; lines may be null in pairs).
- `severity_counts` must equal the computed per-severity finding counts. A
  mismatch is a count error, not a model judgment.
- "Top findings" means `status == "open"`, ordered by severity rank
  (`critical<high<medium<low`) then alias.
- Confidence distributions are computed from the current manifest records.

## Business rules

- `business_rules[]`: `alias` (`BR-000`), `rule`, `confidence`, `evidence[]`,
  `coverage_status` (`covered|untested`).
- Trust `coverage_status` as displayed status and cross-check it against
  `traceability[]`: `covered` requires at least one BR link; `untested` requires
  none. A disagreement is an input-validation error.

## Components

- `components[]`: `alias` (`CMP-000`), `name`, `path`, `namespace` (string or
  null). Show analysis depth from the matching `coverage.components[]` entry.

## Tests and traceability

- `test_cases[]`: `alias` (`TC-000`), `category`
  (`behavioral|security|infrastructure`), `title`, `status`
  (`specification|existing`), `source_refs[]`.
- BR↔TC links come from `traceability[]`. V/TD/CMP linkage comes from
  `test_cases[].source_refs`.
- "Untested rules" are business rules whose `coverage_status == "untested"`.

## Delta

- `delta` preserves `prior_manifest_loaded`, `new`, `resolved`, `regressed`,
  `persisted` exactly. Overview shows the counts of each state.

## Path safety

- Document and image paths must be relative POSIX paths: no NUL, no drive
  prefix, no absolute root, no `..` segment. Resolve each path and any symlink
  target strictly and require it to stay under the resolved input root. Reject
  non-regular files and escapes.
