# Context-file guidelines

Rules for what `init-project` writes into a target project's generated
context files (canonical `AGENTS.md` and its per-agent adapters), and for
how it handles artifacts that already exist there. Phase 1 (Interview)
consults `## Merge semantics` when a pre-existing artifact is found; Phase 4
(Generate context files) consults all four sections — budget while writing,
the copy-paste standing rules block while assembling `## Working rules`, and
merge semantics again when writing to a target that already has files. This
file travels with the skill (including a bare symlink install); it makes no
this-repo `knowledge/` references. Sibling references — `agent-context-matrix.md`,
`okf-kb-guide.md` (its `## Migration` procedure) — are allowed and used below.

## Contents

- [Content budget](#content-budget)
- [Context vs KB](#context-vs-kb)
- [Standing rules block](#standing-rules-block)
- [Merge semantics](#merge-semantics)

## Content budget

- Canonical `AGENTS.md`: **≤ 150 lines and ≤ 10 KB**, both hard caps.
- Import-adapters (e.g. `CLAUDE.md` containing `@AGENTS.md`, `GEMINI.md`
  containing `@AGENTS.md`): **≤ 10 lines** — the import line plus at most a
  couple of short agent-specific notes below it.
- A **full-copy** adapter (`agent-context-matrix.md` `## Fallback rule`, for
  an agent with neither native `AGENTS.md` reading nor an import mechanism)
  is not an adapter in the sense above — it duplicates `AGENTS.md`'s content
  wholesale, so it inherits `AGENTS.md`'s own ≤ 150 lines / ≤ 10 KB budget
  instead of the 10-line cap.
- **Over budget:** do not trim facts silently and do not let the file grow
  past the cap. Move the detail into the project knowledge base as a concept
  (or into an existing one) and replace it in the context file with a short
  pointer/link. Re-check the budget after every edit in Phase 4 and after
  every accepted expert-review finding in Phase 5.

## Context vs KB

- **Context files hold:** project identity (name, purpose, stack), the
  commands an agent runs directly, binding rules the agent must follow on
  every turn, and pointers into the knowledge base for anything deeper.
- **Knowledge base holds:** researched facts (technology versions, official
  doc links, setup/convention details), recorded decisions with rationale,
  and deep or rarely-needed conventions.
- **Heuristic:** if an agent needs the fact on *every* turn to work
  correctly, it belongs in the context file. If the fact is only looked up
  *sometimes* — when working on a specific technology, revisiting a past
  decision, or investigating something unusual — it belongs in the KB with a
  pointer left in the context file instead of the fact itself.

## Standing rules block

The following block is the exact, verbatim text embedded into every
generated `AGENTS.md`'s `## Working rules` section (see
`assets/agents-md-template.md`). It is written once here so every future
generation is copy-paste, not re-authored. It is self-contained: a target
project has none of this skill's own files present, so the rules name their
own canonical URL rather than pointing back at this guide.

```markdown
- Read this project's knowledge base first, and research externally only
  when the knowledge base does not already have the answer.
- After finishing any piece of work, update the knowledge base with what
  changed.
- When you learn something new about this project while working, capture it
  in the knowledge base — don't let it evaporate at the end of the session.
- When a knowledge source outside this repository has its own index (an OKF
  bundle, an LLMWiki, or similar), reference it by index + link and pull in
  only the excerpts you need — never copy it wholesale.
- Keep this file and its adapters current every work cycle, but never let
  them bloat: once a detail stops being something you need on every turn,
  move it into the knowledge base and link it from here instead.
- Watch the OKF spec version: fetch
  `https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md`
  and read its `**Version X.Y**` line before knowledge-base work. When that
  version is newer than the `okf_version` recorded in the knowledge base's
  index, propose a migration to the user — never migrate silently and never
  ignore the drift.
```

Two of the block's bullets state the **default** knowledge-base update
behaviour: bullet 2 fixes *when* the knowledge base is written ("After
finishing any piece of work"), and bullet 3 fixes *when* a new learning is
captured ("don't let it evaporate at the end of the session"). Keep the
block verbatim regardless; never edit it to match an interview answer. When
the interview's update-cadence/ownership answer (`task-type-presets.md`
`## knowledge base`) differs from that default, reconcile it in
`## Knowledge base` instead: record the agreed cadence and owner there, and
add an explicit override line for **every** standing bullet the answer
supersedes. A cadence answer supersedes at least bullets 2 and 3, so a
single line is not enough:

- **Bullet 2 — when the knowledge base is written.** State the agreed
  cadence and owner, and say plainly that the per-work-cycle default no
  longer applies. For example: "Update cadence: monthly, owned by <name>,
  who runs the monthly update of `<kb>/`. This supersedes the
  `## Working rules` bullet 'After finishing any piece of work, update the
  knowledge base with what changed' — do not write to `<kb>/` on your own
  schedule."
- **Bullet 3 — where interim learnings go.** Any cadence longer than "after
  every piece of work" opens a gap between learning something and writing it
  down, and bullet 3 forbids losing it. Name the interim path explicitly.
  For example: "When you learn a fact one of the `<kb>/` concepts covers, or
  an answer to a gap one lists as open, say so in your final message to the
  owner so it reaches the next update." Without this line an agent must
  either break the agreed cadence or drop the learning.

Without these lines the generated file carries conflicting rules and fails
Phase 5's `## Checklist: prompt engineering` bar "No two rules conflict."
When the answer matches the default, add nothing.

## Merge semantics

Every pre-existing artifact is handled **per artifact, at the moment it is
encountered** — never one global answer covering everything found, and
never a silent overwrite. The user is asked merge, skip, or replace for
that specific artifact before it is touched.

- **Existing context file** (e.g. an `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`
  already present at the target path) and the user chooses merge: preserve
  the existing user-authored content exactly as it is, and append the
  generated sections (or, for an import-adapter, the `@AGENTS.md` import
  line plus any agent-specific notes) between provenance markers:

  ```markdown
  <!-- init-project:start -->
  ...generated content...
  <!-- init-project:end -->
  ```

  A later run that finds these markers already present replaces only the
  content between them, leaving everything outside untouched.
- **Existing non-OKF knowledge folder** (docs/notes/wiki content with no
  per-file `type:` frontmatter and no `index.md`/`log.md` convention):
  coexist. Create the new OKF bundle under the chosen folder name (adjusted
  to a non-colliding name if the chosen name is already taken by this
  folder) and add a concept or note in it that links to the old folder by
  path. Never migrate or rewrite the old folder's content — see
  `okf-kb-guide.md` `## Migration`, which scopes migration to OKF bundles
  only.
- **Existing OKF knowledge base** (an `index.md`/`log.md` bundle, any
  `okf_version`): update in place. Add new concepts and index/log entries
  alongside the existing ones. If its `okf_version` is older than the
  version found by the current run's version check, follow the migration
  path in `okf-kb-guide.md` `## Migration` — propose the concrete changes
  and get the user's approval before touching anything, then log the
  migration in `log.md`.
