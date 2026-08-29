---
type: Spec Summary
title: OKF (Open Knowledge Format) specification
description: >
  Summary of the OKF 0.2 spec that governs this repo's knowledge/ bundle:
  structure, frontmatter fields, trust and lifecycle model, linking,
  conformance rules, v0.1->v0.2 changes, and the exact procedure for
  detecting spec updates.
spec_version: "0.2"
tags:
  - okf
  - knowledge-format
  - spec
  - frontmatter
  - conformance
sources:
  - resource: https://github.com/GoogleCloudPlatform/open-knowledge-format
    title: Canonical OKF repository
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md
    title: OKF SPEC.md (canonical, raw)
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/SPEC.md
    title: OKF SPEC.md (frozen snapshot, raw)
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/README.md
    title: okf/README.md (deprecation notice + OKF overview)
  - resource: https://api.github.com/repos/GoogleCloudPlatform/open-knowledge-format/commits?path=SPEC.md
    title: SPEC.md commit history API (update checking)
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/acme_retail/index.md
    title: Example acme_retail bundle index.md
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/acme_retail/tables/orders.md
    title: Example acme_retail table concept
  - resource: https://raw.githubusercontent.com/GoogleCloudPlatform/knowledge-catalog/main/okf/bundles/acme_retail/computations/revenue-ytd.md
    title: Example acme_retail Attested Computation
generated:
  by: claude-code/claude-fable-5
  at: 2026-08-29T10:44:59Z
status: stable
---

# OKF (Open Knowledge Format) specification

OKF is a Google Cloud Platform spec for representing knowledge as a directory
of markdown files with YAML frontmatter — no schema registry, no central
authority, no required tooling. This repo's `knowledge/` directory is an OKF
bundle and must conform to the rules below.

## Canonical location and version

- **Canonical repo:** `github.com/GoogleCloudPlatform/open-knowledge-format`,
  with `SPEC.md` at the repo root on default branch `main`.
- **Deprecated snapshot:** the copy under
  `GoogleCloudPlatform/knowledge-catalog/okf/` is a **frozen, unmaintained
  snapshot** (its README says to stop using it). It was byte-identical to the
  canonical SPEC.md as of 2026-08-29, but never cite it as current.
- **Current version: 0.2**, declared as `**Version 0.2**` on line 3 of
  SPEC.md. §12 also states "This document specifies OKF version 0.2" and
  defines a `<major>.<minor>` scheme: minor = backward-compatible additions,
  major = breaking. The repo has **no git tags and no GitHub releases** — the
  SPEC.md version line is the only version source. SPEC.md last changed
  2026-08-21 (commit `0b87c52c6e`).

## Bundle structure

- Unit of distribution is a **Knowledge Bundle**: an arbitrary directory tree
  of `.md` files. OKF prescribes **no folder names**; producers organize
  freely (`references/` for mirrored external material / executor skills /
  attester code is a naming convention, not a requirement).
- Exactly two filenames are **reserved at any level**:
  - `index.md` — directory listing;
  - `log.md` — update history.
- **Every other `.md` file is a concept document.** A concept's ID is its
  bundle path minus `.md` (e.g. this file's ID is `specs/okf-spec`).

### index.md

- Optional at any directory level.
- Contains **no frontmatter**, except the bundle-root `index.md`, which MAY
  carry `okf_version: "0.2"` (this repo's root index does; the spec's own
  sample bundles do not, so consumers cannot rely on its presence).
- Body format: `# Section Heading` followed by
  `* [Title](path) - description` bullets.

### log.md

- Optional at any level; `## YYYY-MM-DD` (ISO 8601) date headings, **newest
  first**. Leading bold verbs (`**Update**`, `**Creation**`,
  `**Deprecation**`) are convention, not requirement.
- The spec is silent on log.md frontmatter (one sample bundle adds
  `type: Log`); treat that as a tolerated producer extension.

## Frontmatter fields

### Required

- `type` — the **only always-required field**. Any non-empty string;
  uncontrolled vocabulary (spec examples: "BigQuery Table", "Metric",
  "Playbook", "Attested Computation"). A concept with just `type` is fully
  conformant. This repo restricts itself to `Spec Summary`, `Reference`,
  `Playbook`, `Decision` (see `/index.md` and CLAUDE.md).

### Recommended

- `title`, `description`, `resource` (canonical URI of the underlying asset),
  `tags` (YAML list).

### Provenance: `sources`

- List of entries; per-entry `resource` is **required**; optional `id`,
  `title`, plus credibility signals `author`, `usage_count`, `last_modified`.
- Sibling key `usage_window: { from, to }` frames usage counts.
- Body text may attribute individual claims via markdown footnotes whose
  label matches a `sources[].id` (e.g. `[^ga4-schema]`).

### Trust: `generated` and `verified`

- `generated: { by, at }` — `by` is required within the mapping; `at` is an
  ISO 8601 datetime.
- `verified` — a list of `{ by, at }` entries; consumers MUST treat a bare
  mapping as a one-element list.
- **Trust tiers derived from `verified`:**
  - absent → *unverified*;
  - only non-human actors → *machine-confirmed*;
  - any `human:<id>` actor → *human-reviewed*.

### Actor conventions (§7)

- Agents/tools: `<producer>/<version>` (e.g. `reference_agent/gemini-2.5-pro`;
  this repo uses `claude-code/claude-fable-5`).
- Humans: `human:<id>` (this repo: `human:kengjudd`).
- Automated processes: `process:<id>`.

### Lifecycle

- `status`: `draft` | `stable` | `deprecated`; absent means `stable`.
- `stale_after`: **absolute** ISO 8601 datetime; the document is stale when
  now >= `stale_after`.
- All timestamp-valued keys are ISO 8601 datetimes with explicit UTC offset
  (e.g. `2026-06-30T14:00:00Z`).

### Attested Computation extras

Concepts of type "Attested Computation" additionally carry:

- `runtime` (**required**; e.g. bigquery, postgres, dbt, python, Looker);
- `parameters`: list of `{ name, type, required }`;
- `computation` (optional file path);
- `executor: { resource, receipt }`;
- `attester: { resource }`.

Example: `bundles/acme_retail/computations/revenue-ytd.md` — `runtime:
bigquery`, `parameters: [{name: year, type: integer, required: true}]`,
`executor: {resource: skills/run-on-bq.md, receipt: [job_id, executed_sql,
result]}`, `attester: {resource: attesters/sql_equality.py}`.

## Body and linking

- **No required body sections.** Conventional headings: `# Schema`,
  `# Examples`, `# Computation`.
- Linking uses standard markdown links. Bundle-relative form starting with
  `/` is **recommended** (e.g. `/specs/agent-skills-spec.md`); relative form
  (`./other.md`) is also allowed. Links are untyped edges — semantics come
  from surrounding prose. Consumers MUST tolerate broken links.

## Conformance (§11)

A bundle conforms iff:

1. every non-reserved `.md` has parseable YAML frontmatter;
2. every frontmatter has a non-empty `type`;
3. reserved filenames (`index.md`, `log.md`) follow §8/§9.

Consumers **MUST NOT** reject a bundle for: missing optional fields, unknown
`type` values, unknown extra frontmatter keys, broken links, or a missing
`index.md`.

## v0.1 → v0.2 breaking changes

- `timestamp` was replaced by `generated: { by, at }`.
- The body-level `# Citations` list was replaced by frontmatter `sources`.
- Consumers MAY fall back to the legacy forms when reading v0.1 documents.

## Checking for spec updates (programmatic)

There are **no git tags or GitHub releases** — do not look for them. The only
version signals are:

1. **Version line:** fetch
   `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
   and parse the `**Version X.Y**` line near the top (line 3), e.g.
   `curl -fsSL <url> | grep -m1 -o 'Version [0-9]\+\.[0-9]\+'`.
2. **Change detection:** the GitHub commits API filtered to the spec file —
   `https://api.github.com/repos/GoogleCloudPlatform/open-knowledge-format/commits?path=SPEC.md`.

This repo automates check 1 via `scripts/check-spec-versions.sh`, which
compares the canonical `**Version X.Y**` line against the `spec_version:`
key in this file's frontmatter (grepped as `^spec_version:`). Exit codes:
0 = up to date, 1 = drift, 2 = error. The deprecated knowledge-catalog raw
URL still resolves but must not be used for checks.

### When drift is detected

Before any further work on `knowledge/` (CLAUDE.md rule 5):

1. Read the new canonical SPEC.md.
2. Update this document — content **and** the `spec_version:` frontmatter
   key — and migrate the whole `knowledge/` bundle to the new rules
   (including `okf_version` in the root `/index.md`).
3. Record the migration in `/log.md` (and repo `CHANGELOG.md` per repo
   versioning rules).

## How this repo applies OKF

- Bundle root: `knowledge/`; root `/index.md` carries `okf_version: "0.2"`;
  history in `/log.md`.
- Every concept carries `type`, `title`, `description`, `tags`, `sources`
  (external facts require resolvable URLs), `generated`, `status`.
- Related spec docs: `/specs/agent-skills-spec.md` (skills side of the
  skills/knowledge split), `/specs/agents-md-standard.md`,
  `/specs/claude-code-plugins.md`; founding rationale in
  `/decisions/2026-08-29-repo-design.md`.
