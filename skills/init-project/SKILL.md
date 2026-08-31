---
name: init-project
description: >-
  Initialize a project for one or more AI coding agents: interview the user
  (agents, task types, stack, knowledge-base folder name, Karpathy
  guidelines opt-in), research each selected agent and named technology,
  create an OKF knowledge base (default folder knowledge-base), generate a
  canonical AGENTS.md plus per-agent adapters (CLAUDE.md, GEMINI.md, ...),
  and run an adaptive expert review. Use when asked to init or set up a
  project for agents, bootstrap agent context files or a knowledge base —
  "init โปรเจกต์", "ตั้งต้นโครงการให้ agent", "สร้าง AGENTS.md/CLAUDE.md",
  "ตั้งค่า knowledge base". Not for scaffolding application code, running
  git init, the built-in `/init` slash command (writes a single CLAUDE.md
  only), or analyzing an existing codebase in depth.
license: MIT
metadata:
  version: "1.0.0"
  updated: "2026-08-31"
---

# Init Project

## Purpose

Initialize a target project so the AI coding agents the user selects can work
in it effectively. The run produces exactly two kinds of output: **context
files** (a canonical `AGENTS.md` plus the per-agent adapters that agent
actually needs) and an **OKF knowledge base** inside the project, seeded from
researched, sourced facts. It never scaffolds application code, never runs
`git init`, and never installs third-party skills — those stay out of scope
and are at most suggested in the final report.

## Iron rules

These bind every phase below. Where a reference file seems to permit
otherwise, these win.

- **Every consequential decision is asked, never assumed.** Recommendations
  are encouraged: recommend first, then ask, and wait for the answer.
- **Every factual claim written into a knowledge base carries `sources:`**
  with resolvable URLs from official/trusted origins. Nothing is written from
  memory. (A `Decision` concept recording this project's own choice has no
  external origin and needs no external source.) If research cannot settle a
  question, ask the user; if the user cannot settle it either, record it as
  an explicit gap instead of inventing an answer.
- **No bias toward any single agent.** Shared content lives only in the
  canonical `AGENTS.md`; agent-specific content lives only in that agent's
  adapter.

## Workflow

Run the six phases in order. Phase 5 starts only after Phases 3 **and** 4
have both finished, because it reviews both of their outputs.

### Phase 1 — Interview

Ask **one topic at a time** and wait for each answer before moving on.
Conduct the interview in whatever language the user is already writing in;
topic ⑦ sets the language of the *generated* files, not of this skill.

1. **Project identity.** Ask for the project's **name** and a one-or-two
   sentence **purpose** (what it does, who it is for). Recommend the target
   directory's own name as the project name; for an existing codebase also
   draft the purpose from its README per `## Edge cases` and offer that
   draft. For an empty directory there is nothing to draft from — ask
   outright rather than inventing a purpose. Both answers are required:
   `assets/agents-md-template.md` and `assets/kb-skeleton/index.md` carry
   `<Project name>` tokens that Phase 3 forbids leaving unreplaced.
2. **Agents.** Multi-select from the agents covered in
   [references/agent-context-matrix.md](references/agent-context-matrix.md),
   plus free text for any agent not listed there.
3. **Task types.** Multi-select from the four presets in
   [references/task-type-presets.md](references/task-type-presets.md) —
   `## coding`, `## frontend`, `## project management`,
   `## knowledge base` — plus free text. Any free-text task type goes
   through that file's `## Free-text task types` procedure: draft the
   checklist by analogy, show the draft, get it confirmed *before* asking
   anything from it.
4. **Gap checklists.** For every selected task type, ask its checklist items
   using the question wording in that file (translated if needed), one item
   at a time, recommendation first. Keep going until no gaps remain under
   its `## Gap rules` — including the extra items an answer naming a new
   technology adds. Items the user explicitly defers are never silently
   dropped: add each to a **running gap list** you keep for the whole run.
   `<kb>/` does not exist yet, so nothing is written to it here — Phase 3
   step 5 flushes the list into `<kb>/log.md`, and Phase 6 reports it.
5. **Knowledge-base folder name.** Recommend `knowledge-base`, then ask.
   This is `<kb>` everywhere below.
6. **Karpathy guidelines opt-in.** Only when a coding task type was
   selected. It is the last item of the `## coding` checklist, so it is
   normally already answered in ④ — carry that answer forward instead of
   asking again. Ask here only if ④ did not cover it; the question wording
   is in
   [references/task-type-presets.md](references/task-type-presets.md)
   `## coding` and the default is to include. Including it never installs
   the upstream skill.
7. **Language of generated files.** Recommend the language the user is
   writing in, then ask. Every file this run writes — `AGENTS.md`, the
   adapters, the KB concepts, and the Phase 6 report — uses the answer.
8. **Pre-existing artifacts.** Do **not** ask one global question up front.
   When a later phase encounters an artifact that already exists, stop there
   and ask merge / skip / replace for *that artifact*, per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`. Never overwrite silently.

### Phase 2 — Research

1. Read
   [references/agent-context-matrix.md](references/agent-context-matrix.md)
   **first**. Every agent it covers is already researched and sourced — use
   it as written; do not re-research it at run time.
2. For a selected agent the matrix does not cover, research it live from its
   official documentation and write up the same six fields in the matrix's
   format (context file(s) & precedence, import syntax, adapter rule, native
   init command, config locations, sources with a verification date). Decide
   its adapter rule with that file's `## Fallback rule`.
3. For every technology named during the interview, research the fields
   required by
   [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Researched-technology template` from official sources.
4. **No web access:** say so to the user before continuing, proceed with
   bundled knowledge only, and add every skipped item to the running gap
   list from Phase 1 ④ (Phase 3 step 5 flushes it to `<kb>/log.md`; Phase 6
   reports it). Never fill the hole from memory.

### Phase 3 — Create the KB (draft)

1. Run [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Version check` once for this run, before creating or changing
   anything.
2. If `<kb>/` already exists: an OKF bundle goes through that file's
   `## Migration` (propose the concrete changes, get approval, log it); a
   non-OKF docs/notes folder is left untouched and handled per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`.
3. Instantiate `assets/kb-skeleton/index.md` and `assets/kb-skeleton/log.md`
   into `<kb>/`. **Replace every `<...>` token** — `<Project name>`,
   `<Title>`, `<path>`, `<description>`, `<YYYY-MM-DD>`, the seeding
   summary. No `<...>` placeholder may survive into the target project.
4. Write the concept documents per `## Creating the bundle`: one per named
   technology using `## Researched-technology template`; concepts for the
   domains and seed sources named under the `## knowledge base` preset; one
   index concept per external KB per `## External knowledge bases`; and, if
   Karpathy was opted in, the fuller guidelines as a `Reference` concept.
5. Use only the four `type:` values in `## Type vocabulary`, and index every
   concept in `<kb>/index.md`. Write the `<kb>/log.md` entry for the seeding
   **and one entry for every gap accumulated in Phases 1–2** — this is where
   the running gap list is flushed to disk.

This is a **draft** — Phase 5 reviews and corrects it before the report.

### Phase 4 — Generate context files

1. Instantiate `assets/agents-md-template.md` as the canonical `AGENTS.md`
   at the target project root. Fill `## Project` from the interview (and,
   for an existing codebase, the light analysis described under
   `## Edge cases`); fill `## Commands` with the commands the interview's
   package-manager, test, lint, and build answers imply, deleting that
   section outright when the project has no toolchain yet and named none;
   fill `## Knowledge base` with the chosen `<kb>` folder;
   fill `## Agent notes` with one bullet per selected agent. The template's
   `## Working rules` already carries the verbatim standing-rules block from
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Standing rules block` — never re-author it; add the working-rules
   facts each preset's **Output delta** paragraph calls for around it.
2. **Karpathy block.** Opted in: keep the block between
   `<!-- karpathy:start -->` and `<!-- karpathy:end -->`. Opted out, **or
   never asked because no coding task type was selected**: delete that whole
   marked block, markers included.
3. **Adapters.** For each selected agent, look up its `**Adapter rule:**` in
   [references/agent-context-matrix.md](references/agent-context-matrix.md);
   for an agent not in the matrix, apply its `## Fallback rule` to the
   Phase 2 research.
   - `native` — write no adapter file at all. Record the agent, and the one
     quirk worth surfacing, in `## Agent notes`.
   - `import-adapter` — write that agent's own context file containing the
     `AGENTS.md` import, plus at most a couple of agent-specific notes.
   - `full-copy` — write that agent's own context file as a full copy of
     `AGENTS.md`'s content, carrying the provenance header given in
     `## Fallback rule`, and flag it in the Phase 6 report.
4. **Budget.** Respect
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Content budget` (a full-copy adapter is exempt from the adapter cap
   and inherits `AGENTS.md`'s own budget). Over budget: never trim a fact
   silently — move it into `<kb>/` and leave a pointer, deciding what goes
   where with `## Context vs KB`. Re-check the budget after every edit.
5. Any target path that already has a file goes through `## Merge semantics`
   for that artifact before it is touched.

### Phase 5 — Expert review + apply

Follow [references/expert-review-protocol.md](references/expert-review-protocol.md)
end to end, and only once Phases 3 and 4 are both complete:
`## Capability heuristic` to decide parallel subagents vs sequential persona
passes; `## Reviewer roster` to build the roster (the two standing reviewers
plus one domain reviewer per technology or domain named in the interview);
`## Checklist: prompt engineering`, `## Checklist: context engineering`, and
`## Checklist: generic domain` as the pass/fail bars; `## Applying findings`
to apply every accepted finding — context files amended in place, KB
concepts corrected and logged in `<kb>/log.md` — before Phase 6. Rejected
findings get a one-line reason, not silence.

### Phase 6 — Report

Report to the user, in the language chosen in Phase 1 ⑦:

- **Files created or modified,** by path: `AGENTS.md`, each adapter, and
  everything under `<kb>/`.
- **Every decision taken,** each traceable to the user's own approval.
- **Remaining gaps:** deferred checklist items listed by task type and item;
  a skipped or failed OKF version check; anything degraded by missing web
  access; agents research could not resolve; technologies whose concepts
  were skipped rather than invented.
- **Spec drift,** if the version check found an OKF version newer than the
  one [references/okf-kb-guide.md](references/okf-kb-guide.md) is written
  against — say that the skill itself needs a maintainer update.
- **Any full-copy adapter,** with the warning that later `AGENTS.md` edits
  will not propagate to it until this skill is re-run.
- **How to re-run:** re-running this skill is safe **where provenance
  markers are present** — inside them, `## Merge semantics` makes a re-run
  replace only the generated content. Files this skill generated whole on a
  fresh run carry no markers, so a re-run treats them like any other
  pre-existing artifact: it asks merge / skip / replace for each one.
- **Out-of-scope suggestions,** clearly labeled as suggestions: e.g.
  installing the upstream Karpathy guidelines skill, or running
  `comprehensive-codebase-analysis` for a deep pass over an existing
  codebase.

## Edge cases

- **A context file already exists** (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`,
  or any other adapter target). Ask merge / skip / replace for that one
  artifact at the moment it is encountered, then apply
  [references/context-file-guidelines.md](references/context-file-guidelines.md)
  `## Merge semantics`. Never one global answer, never a silent overwrite.
- **An existing OKF knowledge base at an older `okf_version`.** Migrate via
  [references/okf-kb-guide.md](references/okf-kb-guide.md) `## Migration`:
  write out the concrete file-by-file changes, get the user's approval, then
  apply and log them.
- **An existing codebase.** Do light analysis only — README, directory
  layout, manifest/config files — enough to fill `AGENTS.md`'s project and
  stack sections. Deep understanding is not this skill's job: point the user
  at the `comprehensive-codebase-analysis` skill instead of duplicating it.
- **No web access.** Tell the user, degrade to the bundled references, and
  add each skipped check to the running gap list — flushed to `<kb>/log.md`
  in Phase 3 step 5, reported in Phase 6. Bundled facts may be used;
  remembered facts may not.
- **An agent research cannot resolve.** Ask the user for the agent's
  official documentation or links. Record only the facts that get confirmed,
  in the matrix's format, and list everything else as a gap. If the adapter
  rule still cannot be determined, ask the user which of `native`,
  `import-adapter`, or `full-copy` applies — do not guess.

## References

- [references/agent-context-matrix.md](references/agent-context-matrix.md) —
  per-agent context files, precedence, import syntax, adapter rule, native
  init command, config locations, sources; plus the `## Fallback rule` for
  agents it does not cover.
- [references/task-type-presets.md](references/task-type-presets.md) — the
  four presets' gap checklists as ready-to-ask questions, their output
  deltas, free-text task types, and the gap/deferral rules.
- [references/okf-kb-guide.md](references/okf-kb-guide.md) — OKF version
  check, bundle creation, migration, `type:` vocabulary, the
  researched-technology concept template, external knowledge bases.
- [references/context-file-guidelines.md](references/context-file-guidelines.md)
  — content budget, context-vs-KB split, the verbatim standing-rules block,
  per-artifact merge semantics.
- [references/expert-review-protocol.md](references/expert-review-protocol.md)
  — capability heuristic, reviewer roster, the three checklists, and how
  findings are applied.

Assets instantiated into the target project: `assets/agents-md-template.md`
(canonical `AGENTS.md` skeleton), `assets/kb-skeleton/index.md` and
`assets/kb-skeleton/log.md` (OKF bundle root files).

## Updating

This skill is versioned via `metadata.version` (see frontmatter) and
distributed from the private repo `gitkeng/skills-kengjudd`. Use the command
that matches how it was installed.

**Git clone + symlink install** — run from the repository root:

```bash
./scripts/update.sh init-project
```

If this skill directory is a symlink (the normal install), resolve it with
`readlink -f <this-skill-dir>`; the repo root is two directories above the
resolved path.

The script fetches `origin/main`, compares this skill's `metadata.version`,
shows this skill's pending commits, and pulls after confirmation.

**Claude Code plugin install** — the plugin cache has no `.git`, so
`update.sh` cannot run there:

```bash
claude plugin update kengjudd@kengjudd
```

After updating, restart the agent session so the new version loads.
