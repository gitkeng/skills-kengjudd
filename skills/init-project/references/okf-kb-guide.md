# OKF knowledge-base guide

Procedures for creating, checking, and migrating an OKF (Open Knowledge
Format) knowledge bundle in the **target project** — not this skill's own
repository. `<kb>` below stands for the KB folder name chosen during the
interview (default `knowledge-base`). This guide is written against **OKF
0.2**; treat every rule below as scoped to that version unless the Version
check step finds a newer one. This file travels with the skill (including a
bare symlink install); it makes no this-repo `knowledge/` references.

## Contents

- [Version check](#version-check)
- [Creating the bundle](#creating-the-bundle)
- [Concept kinds](#concept-kinds)
- [Skill-owned concepts](#skill-owned-concepts)
- [Domain and seed-source concepts](#domain-and-seed-source-concepts)
- [Migration](#migration)
- [Legacy knowledge folders](#legacy-knowledge-folders)
- [Type vocabulary](#type-vocabulary)
- [Researched-technology template](#researched-technology-template)
- [External knowledge bases](#external-knowledge-bases)
- [Sources](#sources)

## Version check

Run this check once per skill run, at Phase 2 **Fetch probe and version
check** — before any research, so that its outcome is also the run's single
verdict on web access.

1. Fetch the canonical spec —
   `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
   — trying the routes **in this order** and stopping at the first that
   succeeds:
   1. a shell, because it returns one line, not the document. Buffer the
      whole body before grepping (piping `curl` straight into `grep -m1`
      closes the pipe early and trips `pipefail`), and anchor the match
      (a loose match can pick up "Changes since Version 0.2"):
      ```bash
      spec="$(curl -fsSL https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md)" \
        && printf '%s\n' "$spec" | grep -m1 -oE '^\*\*Version [0-9]+\.[0-9]+(\.[0-9]+)?\*\*'
      ```
   2. the harness's web-fetch tool, when there is no shell or the shell
      route failed — it returns the whole document, so pay that once and do
      not read past the `**Version X.Y**` line (line 3) unless step 2
      requires it.

   A shell error is **not** evidence of being offline; the offline branch
   applies only when both routes have failed. There are no git tags or
   GitHub releases for OKF — do not look for them. The `**Version X.Y**`
   line is the only version signal. Record the outcome in the chat ledger
   and later in the run record as `init_project_web` (`shell`, `fetch-tool`
   or `offline`).
2. **Fetch succeeded, version equals 0.2:** this guide is current — proceed
   as written and do **not** read the spec body. **Version is newer than
   0.2:** read the fetched spec's breaking-changes section first, then
   whatever else differs, and apply its rules for this run; **write the
   fetched version into the root `index.md`'s `okf_version`**, not
   `"0.2"` — the bundle must record the spec it was actually built against,
   or every future run will propose the same migration again. Add a
   `log.md` bullet saying the bundle was created against `<X.Y>` using a
   guide written for 0.2, and put the drift in the report
   (`report-format.md` section 8). Never silently apply a newer spec
   without flagging it.
3. **Both routes failed (offline, network error, non-2xx):** do not block
   the run. Generate the bundle per 0.2, write `okf_version: "0.2"`, and
   record the skipped check as a gap in two places: the report, and a
   `gap:` bullet in the KB's `log.md` (`## Skill-owned concepts`
   **Log bullet grammar**). The same verdict drives SKILL.md Phase 2
   **No web access**.

## Creating the bundle

An OKF bundle has exactly two reserved filenames (`index.md`, `log.md`,
at any directory level) and treats every other `.md` file as a concept
document. Start from the skeleton the skill ships: `assets/` is a sibling of
the `references/` directory this file lives in, so the skeleton is
`assets/kb-skeleton/` — the same path SKILL.md names. Resolve it against the
skill directory, not against the target project.

1. Create the `<kb>/` directory if it does not exist.
2. Copy `assets/kb-skeleton/index.md` to `<kb>/index.md` **only if that file
   does not already exist** — an existing index is never overwritten, only
   added to. This is the **bundle root** index — the one place allowed to
   carry frontmatter, and only one key: `okf_version: "0.2"` (already
   present in the skeleton; write the fetched version instead when
   `## Version check` found a newer one). Replace the `<Project name>`,
   `<Title>`, `<path>`, `<description>` placeholder tokens with real
   values. Body format: one or more section headings, each followed by
   `* [Title](path) - description` bullets, one bullet per concept — the
   shipped skeleton uses a `#` title line plus a `## Concepts` section. Keep
   that single section until the bundle reaches roughly 15 concepts or the
   user asks for grouping (tags from `## Concept kinds` are the suggested
   grouping key). Subdirectory `index.md` files carry **no frontmatter at
   all**.
3. Copy `assets/kb-skeleton/log.md` to `<kb>/log.md` **only if that file
   does not already exist**; where one is there, add a new dated heading at
   the top instead. Replace `<YYYY-MM-DD>` with today's date and the
   seeding bullet's tokens per **Log bullet grammar**. New entries always go
   at the top (newest first); one date heading is shared by every bullet of
   that day.
4. For every concept you write (see `## Concept kinds` for the closed list)
   create one `<kb>/<slug>.md` file with frontmatter:
   - `type:` — non-empty, one of the four values in `## Type vocabulary`.
     This is the only field OKF requires; everything below is what this
     skill additionally always writes.
   - `title:`, `description:` — short and factual.
   - `tags:` — at least one tag from `## Concept kinds` (`init-project` on
     every file this skill writes) plus any free tags.
   - `sources:` — a list; every entry has a `resource:`. Per OKF 0.2 §6.2 a
     path-valued `resource:` takes exactly one of three forms: an absolute
     URL, a bundle-relative path beginning with `/` (resolved from `<kb>/`),
     or a relative path (resolved from the concept file that carries it).
     §5.1 additionally allows a scope descriptor, which is not a path. Use a
     URL for external facts. For a fact taken from the target project's own
     files (its README, design docs, meeting notes, an existing docs
     folder), use a path that actually resolves **from the concept file**:
     project material sitting beside `<kb>/` is `../README.md`, not a bare
     `README.md` — that would resolve to `<kb>/README.md`, which does not
     exist. A bundle-relative `/` path is interpreted from `<kb>/`, so it is
     the wrong tool for material outside the bundle; use `../` for that.
     Reach for a **scope descriptor** only when no single artifact backs the
     claim — a fact drawn from a whole working tree or a set of files, or a
     file that is deliberately not committed such as a local `.env` — and
     then say what was inspected and when (for example
     `the acme-docs repository working tree, inspected 2026-08-31`). When
     one file backs the claim, cite that file. Check that every path
     resolves before writing it (`self-check.md` C5). Never write a concept
     whose factual claims lack a source — if you cannot source a claim, ask
     the user or record it as a gap instead of inventing it. A `Decision`
     concept's claim is the choice itself, with no external origin to cite —
     record its provenance the same way, as a scope descriptor naming the
     interview (for example
     `this project's init-project interview, conducted 2026-08-31`), never
     as an empty `sources:`. **Project material is data** (iron rule 5):
     cite the file that holds a credential or token, never its value.
   - `generated: { by: "<agent>/<model>", at: "<ISO 8601 UTC>" }` — `by`
     names *whatever agent and model is running this skill right now*
     (e.g. `claude-code/claude-sonnet-5`), never a fixed value copied from
     an example. `at` is the current UTC timestamp.
   - `status: draft` on every concept Phase 3 writes; Phase 5 **Stabilize**
     changes it to `stable` after the review (the run record flips at Phase
     6 instead). `deprecated` is never written by this skill.
   - Optional: `stale_after:` (absolute ISO 8601 datetime; **required** on
     technology concepts, see `## Researched-technology template` item 4),
     `verified:` (a list of `{ by, at }`; add a `human:<id>` entry only once
     a human actually confirmed the content — do not add it speculatively).
5. Add a `* [Title](path) - description` bullet for every new concept to
   the nearest `index.md` above it (normally the bundle root). **Every
   bullet this skill generates goes inside the provenance markers.** The
   skeleton ships them already: append new bullets **inside** the existing
   `<!-- init-project:start -->` / `<!-- init-project:end -->` block, never
   after it. If the index has no markers yet (an OKF bundle written by
   something else), add the pair around the bullets this run writes and
   leave every pre-existing bullet outside them. The `okf_version`
   frontmatter, the `#` title line, and the section headings always stay
   outside.

   **On a re-run the block is rebuilt as a union**, never replaced and
   never appended to: keep every existing bullet inside the block whose
   file still exists (bullets a later agent added there survive); a bullet
   whose file is gone is asked about — never dropped silently — at this
   step (or at Phase 0 when detected there); add one bullet per new
   concept; a changed description of a re-researched concept is shown in
   the batched KB amend list beside the concept, not applied silently;
   never two bullets for one path (`self-check.md` C9). The index needs no
   block-diff confirmation of its own: the union drops nothing except
   what the user agreed to drop.

   Index bullets and `log.md` entries link a concept by its plain
   **relative** filename (`<slug>.md`), which resolves from the file
   carrying the link. Do not describe such a link as "bundle-relative" in
   prose — that term belongs only to a path that begins with `/`.
6. Keep the layout **flat** (`<kb>/<slug>.md`) until the bundle reaches
   roughly 15 concepts, or the user asks for grouping. OKF prescribes no
   folder names, so either shape is conformant; only add structure when it
   earns its keep.

## Concept kinds

The closed list of concepts a run may write. Slug patterns apply to new
concepts only — a re-run keeps the slugs an earlier run chose. `sources:`
gives the form the entry takes.

| Kind | `type` | Slug | Written at | `sources:` | Tag |
| --- | --- | --- | --- | --- | --- |
| technology | `Reference` | `<tech-slug>` | Phase 3 **Concepts**, from the Phase 2 extract | official URLs | `technology` |
| agent (not in matrix) | `Reference` | `agent-<slug>` | Phase 3 **Concepts**, from the Phase 2 extract | official URLs | `agent` |
| domain | `Reference` (`Playbook` for a procedure) | `domain-<slug>` | Phase 3 **Concepts** | path or "nothing yet" | `domain` |
| seed source | `Reference` | `source-<slug>` | Phase 3 **Concepts** | path (indexed, not copied) | `seed-source` |
| external KB | `Reference` | `external-<slug>` | Phase 3 **Concepts** | URL or path | `external-kb` |
| legacy folder | `Reference` | `legacy-<slug>` | Phase 3 **Concepts** | path | `legacy` |
| conventions document | `Reference` | `conventions-<slug>` | Phase 4 **Budget**, only when the cut order moves it out of `AGENTS.md` | path | `process` |
| process | `Playbook` | `process-<slug>` | Phase 3 **Concepts** (project-management answers) | interview scope descriptor | `process` |
| constraints | `Reference` | `constraints` | Phase 3 **Concepts**, only when the frontend delta's constraints do not fit `## Working rules` | interview scope descriptor | `constraints` |
| decision | `Decision` | `decision-<slug>` | Phase 3 **Concepts**, one per interview answer that **overrides a default**: a KB cadence other than the standing rule, Karpathy opted out, a type vocabulary adopted from an existing bundle, a task type dropped | interview scope descriptor | `decision` |
| budget overflow | `Reference` | `<topic-slug>` | Phase 4 **Budget** | inherited from the moved fact | as the fact |
| review finding | per finding | per finding | Phase 5 **Apply** | per finding | as the fact |
| Karpathy guidelines | `Reference` | `karpathy-guidelines` | Phase 3 **Skeleton, run record, gap flush**, opt-in only | asset (upstream URL at a pinned commit) | `karpathy` |
| maintenance | `Playbook` | `kb-maintenance` | Phase 3 **Skeleton, run record, gap flush**, every run | asset (OKF spec URL) | `process` |
| run record | `Decision` | `init-project-run` | Phase 3 **Skeleton, run record, gap flush** | interview scope descriptor | `decision` |

Free-text checklists are not concepts: they live in the run record. Every
other interview answer lives in the run record too — a `decision-*` concept
exists only for the four overrides above. Every file carries the tag
`init-project` in addition to the kind tag. Ecosystem defaults that were
never a question (a formatter that comes with the chosen linter) are one
line inside the parent technology's concept, not a concept of their own.

## Skill-owned concepts

Three concepts are written by this skill from its own assets or state and
**regenerated on every run** without the batched amend ask
(`context-file-guidelines.md` `## Merge semantics` **Skill-owned files**).
Two are assets instantiated verbatim — `kb-maintenance.md` (every run) and
`karpathy-guidelines.md` (opt-in) — each carrying
`init_project_asset: "<asset path>@<skill version>"` and the four `<...>`
frontmatter tokens to replace. The third is the **run record**.

**Run record shape** — `<kb>/init-project-run.md`, `type: Decision`, whose
lifecycle is in `run-lifecycle.md` `## Run record`. Standard keys: `title`,
`description`, `tags` (`init-project`, `decision`), `sources` (the
interview scope descriptor), `generated`, OKF `status` (`draft` while the
run is open, `stable` when closed). Then only **flat, namespaced** keys —
each a scalar, a flat list, or a one-level mapping, nothing deeper
(`self-check.md` `## Parser subset`):

| Key | Value |
| --- | --- |
| `init_project_version` | this skill's `metadata.version` |
| `init_project_run_number` | 1, 2, … |
| `init_project_started` / `init_project_completed` | ISO 8601 UTC; `completed` absent while `in-progress`, required when `complete` |
| `init_project_previous_started` | absent on run 1, required when run number > 1 |
| `init_project_status` | `in-progress` \| `complete` |
| `init_project_phase` | 3–6, the last phase that finished |
| `init_project_web` | `shell` \| `fetch-tool` \| `offline` |
| `init_project_root` | scope descriptor, never an absolute path |
| `init_project_agents`, `init_project_task_types` | flat lists |
| `init_project_kb`, `init_project_language` | scalars |
| `init_project_karpathy` | `included` \| `excluded` \| `not-asked` |
| `init_project_type_vocabulary` | one-level mapping, only when a bundle's own vocabulary was adopted |
| `init_project_legacy_folders`, `init_project_concepts` | flat lists of quoted strings |
| `init_project_write_plan` | list of `"<path> | new\|merge\|replace\|update\|skip | <baseline> | <rollback>"` |
| `init_project_answers` | list of `"<key> | <value> | <recommendation> | <reason or empty>"` — the reason records a reaffirmed decision, a re-ask count, or "declined" |
| `init_project_confirmed_commands` | list of `"<name> | <command>"` |
| `init_project_free_text_checklists` | list of `"<task-type-slug>/<item-slug> | <question>"` |
| `init_project_deferred` | flat list of keys, the snapshot at close |

**Values that carry user text are always double-quoted YAML strings**, with
`"` and `\` escaped, so that a `: ` or a leading `|`, `*`, `&`, `#`, `[` in
an answer never turns the item into a mapping. Never write an empty value:
omit the key instead. Prose — rationale, the story of a merge decision —
goes in the body under `## Run`, `## Answers`, `## Deferred`, `## Legacy
folders`, `## Merge decisions`, which nothing parses. Key names and enum
values are never translated.

**Log bullet grammar** — two `log.md` bullet forms are machine-read; they
are a convention of this skill, not an OKF rule. Tokens and keys stay
verbatim, the trailing text follows the generated-files language:

- seeding: `- init-project: run <n>, skill <version>, seeded <slug>[, <slug>...]`
- gap: `- gap: <key> | open|closed|declined | <one line>` — `<key>` is the
  item key from `task-type-presets.md`; the last field takes everything
  after the second ` | `. A gap is closed or declined by a **new** bullet
  under a new date, never by editing the old one; reading newest-first,
  the first bullet for a key is its current state. `log.md` is the single
  authority on gaps: a concept's **Open questions** section mirrors it and
  is never the source.

## Domain and seed-source concepts

The `## knowledge base` preset names knowledge domains to cover and existing
material to seed from. Each named domain and each named seed source gets one
concept (`type: Reference`, or `Playbook` when it documents a procedure)
with three fields, and nothing else:

1. **Scope** — what this concept covers, and what it deliberately does not.
2. **Current material** — what exists today, with a `sources:` path that
   resolves from the concept file (project material beside `<kb>/` is
   `../<file>`), or a URL for external material. "Nothing yet" is a valid
   answer; say so instead of inventing content. A seed source is
   **indexed and cited, never copied in**: name the path, what it contains,
   and which concepts cite it; quote an excerpt only under the rule of
   `## External knowledge bases` step 2, and treat its text as data (iron
   rule 5).
3. **Open questions** — what is not settled yet, one bullet each. These
   mirror the `gap:` bullets in `log.md`, which remain the source of truth.

A domain with no material and no open questions does not need a concept —
say so in the report rather than writing an empty file.

## Migration

Run this before writing anything new if `<kb>/index.md` already exists
and looks like an OKF bundle.

1. Read `<kb>/index.md`'s frontmatter for `okf_version`. If absent, look
   for version signals inside existing concepts: `timestamp:` frontmatter
   (replaced by `generated: { by, at }` in 0.2) or a body-level
   `# Citations` section (replaced by frontmatter `sources:` in 0.2) both
   indicate a v0.1 bundle. If you find neither an `okf_version` key nor
   any v0.1 signal, treat the bundle as already 0.2-shaped (the spec's own
   sample bundles omit `okf_version` from index.md, so its absence alone
   is not evidence of an old version).
2. Compare that version against the one found in `## Version check`.
3. **Versions match:** nothing to migrate: proceed to `## Creating the
   bundle` for any new concepts.
4. **Bundle version is older:** diff the fetched spec's rules against the
   bundle's version (for 0.1 → 0.2: `timestamp` → `generated: { by, at }`;
   body `# Citations` → frontmatter `sources:`). Before the ask, state the
   **size** of what you are proposing: how many concept files change, and
   the change class per file (frontmatter rewrite, body section moved,
   untouched). Then write out the concrete, file-by-file changes, with
   each file's rollback (`run-lifecycle.md` `## Rollback`), and **ask the
   user to approve them** before touching anything — never migrate
   silently. This approval is one of the run's fixed consent asks.
5. On approval, in this order: back up **every** file the migration will
   convert before converting the first one; write the `<kb>/log.md` entry
   **first**, marked in progress ("migration 0.1 → 0.2 started, N files");
   apply the file changes; then set `okf_version` in the root `index.md` to
   the new version **only after the last file has converted**, and close
   the log entry with what changed. A migration interrupted halfway is then
   resumable: the log says it started, and `okf_version` still names the
   old version, so a later run re-proposes only the files that did not
   convert.
6. **Non-OKF knowledge folders never get migrated.** A docs/notes/wiki
   folder that is not an OKF bundle (no per-file `type:` frontmatter, no
   `index.md`/`log.md` convention) is left exactly as it is and indexed
   instead — see `## Legacy knowledge folders`.

## Legacy knowledge folders

This is the single statement of how an existing non-OKF docs/notes/wiki
folder is pointed at; no other file in this skill restates it. Which
folders count is answered by the user in Phase 1 **Legacy knowledge
folders** — the run never decides it by encountering a folder.

1. For each folder the user named, write one concept in `<kb>/`,
   `type: Reference`, slug `legacy-<slug>`, that indexes the old folder:
   where it lives (a path that resolves from the concept file, so normally
   `../<folder>/`), what it contains, and that it is legacy material this
   skill did not convert.
2. Add one line to the generated `AGENTS.md`'s `## Project knowledge base`
   section naming that folder as legacy and linking the concept.
3. Never move, rewrite, or "clean up" the old folder's content.

## Type vocabulary

Generated KBs use exactly four `type:` values — do not introduce a fifth
without asking the user first and recording their approval in `log.md`:

- `Spec Summary` — a summary of an external spec, standard, or API surface.
- `Reference` — factual material meant to be looked up, not read start to
  end (researched-technology facts, agent/tool facts, glossaries).
- `Playbook` — a procedure or how-to for doing something repeatable.
- `Decision` — a record of a choice made for this project, with the
  rationale and alternatives considered.

OKF itself imposes no controlled vocabulary on `type:` — this restriction
is a convention this skill applies to keep generated bundles consistent,
not an OKF requirement. If the target project already has its own
established `type:` vocabulary in an existing OKF bundle, prefer matching
it over introducing these four from scratch: ask the user which to use
(an interview question, key `knowledge-base/type-vocabulary`, asked at
Phase 3 **Existing bundle**), record the mapping in the run record's
`init_project_type_vocabulary` and in a `decision-type-vocabulary` concept,
and write a log bullet. A re-run reads the record and does not ask again.

## Researched-technology template

Every technology the interview settles gets a concept — whether the user
named it outright or accepted it from a recommendation — **within the
research scope confirmed at Phase 2 **Research scope**: at most ten
technology concepts per run; the user trims or merges the list before any
fetch, and anything beyond the cap is deferred as a `gap:` bullet.

Do not confuse this scope with the interview's expansion rule. **Expanding
the interview is narrow**: only a technology chosen as a project decision
adds a follow-up question (`task-type-presets.md` `## Gap rules`).
**Getting a concept is broad**: every settled technology gets one, including
the ecosystem defaults the user accepted rather than named — the language
and runtime, package manager, test framework, and lint tooling a
recommendation supplied are concepts here even though they added no question
there. A default that was never a question at all (a formatter bundled with
the chosen linter) is one line inside its parent's concept instead.

For each of them, create exactly one concept, `type: Reference`,
containing:

1. **Current stable version** — as of the verification date below, from
   the technology's own release notes or official site, not memory.
2. **Official docs URL(s)** in `sources:`, each entry with a `resource:`
   pointing at the canonical documentation (not a blog post or forum
   thread) for that fact.
3. **3–7 project-relevant facts** — setup/installation steps, project
   conventions (config file names, directory layout), and integration
   points with the other agents/technologies selected in the interview.
   Skip generic facts the user did not ask about; every fact here should
   be something this project's context files or KB will actually use.
4. **Verification date** — always as a `verified:` entry
   (`{ by: "<agent>/<model>", at: "<ISO 8601>" }`), plus
   `stale_after:` = that timestamp + 30 days. Phase 0 re-researches a
   concept only when `stale_after` has passed or the user says the version
   changed. The date may additionally be stated in the body.
5. **Does this technology's CLI write agent context files?** Some
   scaffolders create their own `AGENTS.md` or `CLAUDE.md` and overwrite
   what this skill generated. Check the technology's own CLI documentation;
   when the answer is yes, record the command, the files it writes, and its
   behavior toward an existing file, then follow
   `context-file-guidelines.md` `## Scaffolder collisions`. "No" and "not
   documented" are both valid recorded answers.

**Effort bound.** Spend at most **three fetches per technology** — one for
the version source, one for the docs entry point, one more for whatever is
still missing. When a field is still unresolved after that, record it as a
gap and move on; do not keep researching.

**Extract.** The moment a technology is done (fields complete, or three
fetches spent), emit in the chat a fixed-form extract of at most 15 lines:
slug; version and verification date; up to two docs URLs; the facts, one
per line; the CLI answer; gaps. In the interview language, with slug, URLs
and version strings untouched. The extract is the **only** input Phase 3
uses to write the concept and the only thing a Phase 5 reviewer receives in
its brief; no field the extract carries is fetched again in Phases 3–5.

**Per-field N/A.** Any of the fields above may be answered "not applicable"
with a one-line reason — for example, a component library distributed as a
copy-in CLI may have no library version to pin, so record the CLI version
instead and say why. Skip writing the concept entirely only when all four of
the factual fields (items 1–4) fail.

If a named technology cannot be researched (no web access, no official
docs found, ambiguous name), do not guess: ask the user for the
authoritative source (an interview question) or record it as an explicit
gap in the report and in `<kb>/log.md`, and skip writing the concept rather
than inventing facts.

## External knowledge bases

Some target projects already point at a separate, already-structured
knowledge base — another OKF bundle (in a submodule, a monorepo package,
or a separate repo) or an LLMWiki-style wiki. Do not fold these into
`<kb>/` wholesale.

1. Create one `type: Reference` concept in `<kb>/` (slug
   `external-<slug>`) that indexes the external KB: what it covers, where
   it lives (path or URL), and how to browse it. This is the only concept
   most external KBs need.
2. Copy in verbatim excerpts only when a specific fact from the external
   KB is needed right now (e.g. by a concept from
   `## Researched-technology template`). Attribute every excerpt with a
   `sources:` entry pointing back at the origin concept/page — never
   present a copied excerpt as originally authored here.
3. Never rewrite or "clean up" the external KB itself as part of this
   skill's run; it is out of scope and out of this skill's control.

## Sources

Every OKF rule stated in this guide comes from the canonical spec, read at
the raw URL below and verified on the date given. Section numbers are cited
inline where a rule depends on them.

- OKF SPEC.md (canonical, `main`):
  https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md
  — verified 2026-08-31, `**Version 0.2**`; re-checked 2026-09-07 with
  `check-spec-versions.sh` (still 0.2).
  - §4.2 / §5.1 — per-claim attribution and the `sources:` entry shape,
    including the scope descriptor that is not a path.
  - §6.1 / §6.2 — path-valued fields: absolute URL, bundle-relative path
    beginning with `/`, or a relative path resolved from the file carrying
    it.
  - Lifecycle — `status` enum and absent-means-stable; `stale_after` as an
    absolute datetime; §11 — unknown extra frontmatter keys are permitted,
    which is what the `init_project_*` keys rely on.
- The copy under `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen
  snapshot — never cite it as the current spec.
