# OKF knowledge-base guide

Procedures for creating, checking, and migrating an OKF (Open Knowledge
Format) knowledge bundle in the **target project** — not this skill's own
repository. `<kb>` below stands for the KB folder name chosen during the
interview (default `knowledge-base`). This guide is written against **OKF
0.2**; treat every rule below as scoped to that version unless the Version
check step finds a newer one.

## Contents

- [Version check](#version-check)
- [Creating the bundle](#creating-the-bundle)
- [Domain and seed-source concepts](#domain-and-seed-source-concepts)
- [Migration](#migration)
- [Legacy knowledge folders](#legacy-knowledge-folders)
- [Type vocabulary](#type-vocabulary)
- [Researched-technology template](#researched-technology-template)
- [External knowledge bases](#external-knowledge-bases)
- [Sources](#sources)

## Version check

Run this check once per skill run, before creating or migrating anything.

1. Fetch the canonical spec —
   `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
   — **by whatever means your harness provides**: a web-fetch tool, an HTTP
   client, or a shell command such as
   ```bash
   curl -fsSL https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md \
     | grep -m1 -o 'Version [0-9]\+\.[0-9]\+'
   ```
   A shell error is **not** evidence of being offline. If the shell has no
   network — or there is no shell — try the harness's fetch tool before
   concluding anything; the offline branch applies only when every route
   available to you has failed. There are no git tags or GitHub releases for
   OKF — do not look for them. The `**Version X.Y**` line (line 3 of
   SPEC.md) is the only version signal.
2. **Fetch succeeded:** read the fetched SPEC.md and follow *it*, not just
   this guide, for anything that differs. If the fetched version equals
   0.2, this guide is current — proceed as written. If it is newer than
   0.2, apply the fetched spec's rules for this run; **write the fetched
   version into the root `index.md`'s `okf_version`**, not `"0.2"` — the
   bundle must record the spec it was actually built against, or every
   future run will propose the same migration again. Add a `log.md` entry
   saying the bundle was created against `<X.Y>` using a guide written for
   0.2, and add a line to the skill's final report: "OKF spec is now
   `<X.Y>`; `references/okf-kb-guide.md` is written against 0.2 and needs a
   maintainer update." Never silently apply a newer spec without flagging
   it — this guide is what future runs will use if nobody updates it.
3. **Fetch failed on every available route (offline, network error,
   non-2xx):** do not block the run. Generate the bundle per 0.2 as
   described below, write
   `okf_version: "0.2"` into the root `index.md`, and record the skipped
   check as a gap in two places: the skill's final report to the user, and
   a `log.md` entry in the KB being created (so a later run — or a human
   reading the KB — can see the check was skipped).

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
   added to (`context-file-guidelines.md` `## Merge semantics`). This is the
   **bundle root** index — it is the one place allowed to carry
   frontmatter, and only one key: `okf_version: "0.2"` (already present in
   the skeleton; write the fetched version instead when `## Version check`
   found a newer one). Replace the `<Project name>`, `<Title>`, `<path>`,
   `<description>` placeholder tokens with real values. Body format: one
   or more section headings, each followed by
   `* [Title](path) - description` bullets, one bullet per concept — the
   shipped skeleton uses a `#` title line plus a `## Concepts` section. Keep
   that single section until the bundle reaches roughly 15 concepts or the
   user asks for grouping. If you later create subdirectories with their
   own `index.md`, those carry **no frontmatter at all** — only the bundle
   root index may carry `okf_version`.
3. Copy `assets/kb-skeleton/log.md` to `<kb>/log.md` **only if that file
   does not already exist**; where one is there, add a new dated entry at
   the top instead. Replace the `<YYYY-MM-DD>` and summary placeholders with
   today's date and a one-line description of what was seeded. New entries
   always go at the top (newest first).
4. For every concept you write (researched technology, agent fact, design
   decision, anything else) create one `<kb>/<slug>.md` file with
   frontmatter:
   - `type:` — non-empty, one of the four values in `## Type vocabulary`.
     This is the only field OKF requires; everything below is what this
     skill additionally always writes.
   - `title:`, `description:` — short and factual.
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
     claim — a fact drawn from a whole working tree or a set of files — and
     then say what was inspected and when (for example
     `the acme-docs repository working tree, inspected 2026-08-31`). When
     one file backs the claim, cite that file. Check that every path
     resolves before writing it. Never write a concept whose factual claims
     lack a source — if you cannot source a claim, ask the user or record it
     as a gap instead of inventing it.
   - `generated: { by: "<agent>/<model>", at: "<ISO 8601 UTC>" }` — `by`
     names *whatever agent and model is running this skill right now*
     (e.g. `claude-code/claude-sonnet-5`), never a fixed value copied from
     an example. `at` is the current UTC timestamp.
   - Optional: `tags:` (a YAML list), `status:` (`draft` | `stable` |
     `deprecated`; omitted means `stable`), `stale_after:` (absolute ISO
     8601 datetime), `verified:` (a list of `{ by, at }`; add a
     `human:<id>` entry only once a human actually confirmed the content —
     do not add it speculatively).
5. Add a `* [Title](path) - description` bullet for every new concept to
   the nearest `index.md` above it (normally the bundle root). Index bullets
   and `log.md` entries link a concept by its plain **relative** filename
   (`<slug>.md`), which resolves from the file carrying the link. Do not
   describe such a link as "bundle-relative" in prose — that term belongs
   only to a path that begins with `/`.
6. Keep the layout **flat** (`<kb>/<slug>.md`) until the bundle reaches
   roughly 15 concepts, or the user asks for grouping. OKF prescribes no
   folder names, so either shape is conformant; only add structure when it
   earns its keep.

## Domain and seed-source concepts

The `## knowledge base` preset names knowledge domains to cover and existing
material to seed from. Each named domain and each named seed source gets one
concept (`type: Reference`, or `Playbook` when it documents a procedure)
with three fields, and nothing else:

1. **Scope** — what this concept covers, and what it deliberately does not.
2. **Current material** — what exists today, with a `sources:` path that
   resolves from the concept file (project material beside `<kb>/` is
   `../<file>`), or a URL for external material. "Nothing yet" is a valid
   answer; say so instead of inventing content.
3. **Open questions** — what is not settled yet, one bullet each. These are
   the same gaps the final report lists, recorded where the next reader of
   the knowledge base will find them.

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
   untouched). Then write out the concrete, file-by-file changes and **ask
   the user to approve them** before touching anything — never migrate
   silently.
5. On approval, in this order: write the `<kb>/log.md` entry **first**,
   marked in progress ("migration 0.1 → 0.2 started, N files"); apply the
   file changes; then set `okf_version` in the root `index.md` to the new
   version **only after the last file has converted**, and close the log
   entry with what changed. A migration interrupted halfway is then
   resumable: the log says it started, and `okf_version` still names the old
   version, so a later run re-proposes only the files that did not convert.
6. **Non-OKF knowledge folders never get migrated.** If the target
   project has an existing docs/notes/wiki folder that is not an OKF
   bundle (no per-file `type:` frontmatter, no `index.md`/`log.md`
   convention), leave it exactly as it is. Let it coexist with the new
   `<kb>/` bundle and index it instead — see `## Legacy knowledge folders`.

## Legacy knowledge folders

This is the single statement of how an existing non-OKF docs/notes/wiki
folder is pointed at; no other file in this skill restates it.

1. Write one concept in `<kb>/`, `type: Reference`, that indexes the old
   folder: where it lives (a path that resolves from the concept file, so
   normally `../<folder>/`), what it contains, and that it is legacy
   material this skill did not convert.
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
it over introducing these four from scratch; ask the user which to use.

## Researched-technology template

For every technology named as a **project decision** during the interview —
the ones `task-type-presets.md` `## Gap rules` expands — create exactly one
concept, `type: Reference`, containing:

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
4. **Verification date** — the date you actually checked the source,
   either as a `verified:` entry (`{ by: "<agent>/<model>", at: "<ISO
   8601>" }`) or stated in the body text next to the fact it backs.
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

**Per-field N/A.** Any of the fields above may be answered "not applicable"
with a one-line reason — for example, a component library distributed as a
copy-in CLI may have no library version to pin, so record the CLI version
instead and say why. Skip writing the concept entirely only when all four of
the factual fields (items 1–4) fail.

If a named technology cannot be researched (no web access, no official
docs found, ambiguous name), do not guess: ask the user for the
authoritative source or record it as an explicit gap in the report and in
`<kb>/log.md`, and skip writing the concept rather than inventing facts.

## External knowledge bases

Some target projects already point at a separate, already-structured
knowledge base — another OKF bundle (in a submodule, a monorepo package,
or a separate repo) or an LLMWiki-style wiki. Do not fold these into
`<kb>/` wholesale.

1. Create one `type: Reference` concept in `<kb>/` that indexes the
   external KB: what it covers, where it lives (path or URL), and how to
   browse it. This is the only concept most external KBs need.
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
  — verified 2026-08-31, `**Version 0.2**`.
  - §4.2 / §5.1 — per-claim attribution and the `sources:` entry shape,
    including the scope descriptor that is not a path.
  - §6.1 / §6.2 — path-valued fields: absolute URL, bundle-relative path
    beginning with `/`, or a relative path resolved from the file carrying
    it.
- The copy under `GoogleCloudPlatform/knowledge-catalog/okf/` is a frozen
  snapshot — never cite it as the current spec.
