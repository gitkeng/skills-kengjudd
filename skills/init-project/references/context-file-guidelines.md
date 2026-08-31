# Context-file guidelines

Rules for what `init-project` writes into a target project's generated
context files (canonical `AGENTS.md` and its per-agent adapters), and for
how it handles artifacts that already exist there. Phase 1 (Interview) only
*points* at `## Merge semantics` — it encounters no artifacts itself. Phase
3 (Create the KB) consults it at encounter time; Phase 4 (Generate context
files) consults it up front in its step 1, then consults `## Content
budget` while writing, `## Standing rules block` and
`## Scaffolder collisions` while assembling `## Working rules`, and
`## Context vs KB` when a fact has to move. This file travels with the skill
(including a bare symlink install); it makes no this-repo `knowledge/`
references. Sibling references — `agent-context-matrix.md`,
`okf-kb-guide.md` (its `## Migration` procedure) — are allowed and used below.

## Contents

- [Content budget](#content-budget)
- [Context vs KB](#context-vs-kb)
- [Standing rules block](#standing-rules-block)
- [Scaffolder collisions](#scaffolder-collisions)
- [Merge semantics](#merge-semantics)

## Content budget

- Canonical `AGENTS.md`: **≤ 150 lines and ≤ 10 KB**, both hard caps. The
  line cap normally binds first; the byte cap is the backstop for a file
  with unusually long lines.
- Import-adapters (e.g. `CLAUDE.md` containing `@AGENTS.md`, `GEMINI.md`
  containing `@AGENTS.md`): **≤ 10 lines** — the import line plus at most
  two short agent-specific notes below it.
- A **full-copy** adapter (`agent-context-matrix.md` `## Fallback rule`, for
  an agent with neither native `AGENTS.md` reading nor an import mechanism)
  is not an adapter in the sense above — it duplicates `AGENTS.md`'s content
  wholesale, so it inherits `AGENTS.md`'s own ≤ 150 lines / ≤ 10 KB budget
  instead of the 10-line cap.
- **On merge into a pre-existing file** (`## Merge semantics` below), every
  cap above scopes to the generated `<!-- init-project:start -->` /
  `<!-- init-project:end -->` block this skill writes, not the file as a
  whole: pre-existing user content outside the markers never counts against
  the cap and is never cut to make room.
- **Over budget:** do not trim facts silently and do not let the file grow
  past the cap. Apply this **cut order**, stopping as soon as the file fits:
  1. Per-technology detail → move into that technology's knowledge-base
     concept, leaving a one-line stack summary in the context file.
  2. Process facts (methodology, reporting cadence, ways of working) → the
     knowledge base, with a pointer.
  3. `## Agent notes` → one line per agent, nothing more.
  4. Explanatory clauses in `## Commands` → the knowledge base; keep the
     command and a short gloss.

  The standing-rules block and the Karpathy block are **never** trimmed, at
  any step. Still over budget after step 4: keep the fact, and record the
  overflow as a gap in the Phase 6 report.
- **The cap wins, but never by deletion.** When another rule says a fact
  must live in the context file and the cap says it does not fit, move
  something else out first; if nothing else qualifies, keep the fact and
  record the overflow as a Phase 6 gap. Do not cycle between the two rules.
- Re-check the budget after every edit in Phase 4 and after every accepted
  expert-review finding in Phase 5.

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
- **Versions:** the context file's stack line carries **major versions
  only** ("Next.js 16, Node.js 22"). Exact versions, their release dates,
  and their sources stay in the dated knowledge-base concept, which can be
  re-verified; an undated pin copied into `AGENTS.md` cannot.
- **Never restate a KB fact the context file also links to.** If the context
  file points at a concept, the detail lives there and only there.

## Standing rules block

The standing-rules block has exactly one home: the `## Working rules`
section of `assets/agents-md-template.md`. Copy it from the template into
every generated `AGENTS.md` unchanged. It is deliberately **not** reproduced
here — one copy cannot drift from itself. The block is self-contained: a
target project has none of this skill's own files present, so the rules name
their own canonical URL rather than pointing back at this guide.

**Never translated, never reworded.** The block is copied char-for-char in
English even when the interview chose another language for generated files,
because later runs match it literally. The same applies to the Karpathy
block, to the `init-project:*` and `karpathy:*` markers, and to YAML keys
and `type:` values in KB frontmatter. When the chosen language is not
English, add one line **in that language** immediately above each such block
saying it is quoted verbatim from this skill and must not be edited or
translated.

Two of the block's bullets state the **default** knowledge-base update
behaviour, and an interview answer can supersede them. Identify them by
their opening text, never by their position — a future edit may reorder the
block:

- the bullet beginning **"After finishing any piece of work"** fixes *when*
  the knowledge base is written;
- the bullet beginning **"When you learn something new about this project"**
  fixes *when* a new learning is captured.

Keep the block verbatim regardless; never edit it to match an interview
answer. When the interview's update-cadence/ownership answer
(`task-type-presets.md` `## knowledge base`) differs from that default,
reconcile it in the generated file's `## Project knowledge base` section
instead: record the agreed cadence and owner there, and add an explicit
override line for **every** standing bullet the answer supersedes. A cadence
answer supersedes both bullets above, so a single line is not enough:

- **Override for "After finishing any piece of work" — when the knowledge
  base is written.** State the agreed cadence and owner, and say plainly
  that the per-work-cycle default no longer applies. For example: "Update
  cadence: monthly, owned by <name>, who runs the monthly update of
  `<kb>/`. This supersedes the `## Working rules` bullet 'After finishing
  any piece of work, update the knowledge base with what changed' — do not
  write to `<kb>/` on your own schedule."
- **Override for "When you learn something new about this project" — where
  interim learnings go.** Any cadence longer than "after every piece of
  work" opens a gap between learning something and writing it down, and that
  bullet forbids losing it. Name the interim path explicitly. For example:
  "When you learn a fact one of the `<kb>/` concepts covers, or an answer to
  a gap one lists as open, say so in your final message to the owner so it
  reaches the next update." Without this line an agent must either break the
  agreed cadence or drop the learning.

Without these lines the generated file carries conflicting rules and fails
Phase 5's `## Checklist: prompt engineering` bar "No two rules conflict."
When the answer matches the default, add nothing.

## Scaffolder collisions

Some project scaffolders write their own agent context files into the
project root, replacing what this skill generated. The case this skill has
run into is `create-next-app`, which wrote both an `AGENTS.md` and a
`CLAUDE.md` into a freshly scaffolded Next.js project. Whenever the research
step flags such a CLI (`okf-kb-guide.md` `## Researched-technology template`
item 5), do two things:

- Record it in that technology's knowledge-base concept: which command
  writes which files, and what it does to a file that already exists.
- Add **one** bullet below the verbatim standing-rules block in
  `## Working rules`, naming the command, the files it writes, and the
  concept to read first — for example: "Before running `create-next-app` in
  this repo, read `<kb>/nextjs.md`: it writes its own `AGENTS.md` and
  `CLAUDE.md` over the ones here."

## Merge semantics

Every pre-existing artifact is handled **per artifact** — never one global
answer covering everything found, and never a silent overwrite. The user is
asked merge, skip, or replace for that specific artifact before it is
touched. When the ask happens depends on what the phase knows:

- **Phase 3** asks **at encounter**, because it discovers what is inside
  `<kb>/` as it goes.
- **Phase 4** asks **up front, in its step 1**, because it can list every
  path it will write before writing any of them. Collecting the answers
  first is still one ask per artifact — it is not a global question.

The three answers mean:

- **Merge** — leave the existing content exactly as it is and add the
  generated content between the provenance markers below.
- **Skip** — write nothing to that path at all, and list the skip in the
  Phase 6 report. Skipping `AGENTS.md` has a consequence to raise
  immediately: every import-adapter would then import a file this run did
  not author. Say so, and ask whether to write those adapters anyway.
- **Replace** — overwrite the path with the generated content, wrapped in
  the provenance markers. Before replacing, show what is about to be
  discarded (at minimum: the existing headings and the file's length) and
  get the user's confirmation; then write.

**Knowledge-base files: additive writes are not asked about; overwrites and
amendments are one batched ask.** Split them by what the write does, not by
where it lands:

- **Additive** — creating a new concept file, appending a bullet inside the
  index's marker block, adding a dated entry at the top of `log.md`. This
  destroys nothing, so it proceeds **without a question**, exactly as the
  existing-OKF-knowledge-base bullet below says.
- **Overwriting or amending** — replacing content in a `<kb>/` file that is
  already there: editing an existing concept, rewriting existing index
  bullets or log entries, or converting files during a migration. These are
  **never** asked one file at a time. Show them as a single list — each path
  with what will change in it — and get one answer, the way
  `okf-kb-guide.md` `## Migration` presents its changes. The user may still
  answer per file for any subset they name. Never touch a `<kb>/` file that
  was not on the list you showed.

Phase 3 invokes this before it overwrites or amends anything under `<kb>/`.

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

  These markers are written on every run, fresh files included, so a later
  run always finds them and replaces only the content between them, leaving
  everything outside untouched.
- **Existing non-OKF knowledge folder** (docs/notes/wiki content with no
  per-file `type:` frontmatter and no `index.md`/`log.md` convention):
  coexist. Create the new OKF bundle under the chosen folder name; if that
  name is already taken by this folder, Phase 1's knowledge-base-folder
  topic stops and asks the user rather than adjusting the name silently.
  Index the old folder from the new bundle per `okf-kb-guide.md`
  `## Legacy knowledge folders`. Never migrate or rewrite the old folder's
  content — see `okf-kb-guide.md` `## Migration`, which scopes migration to
  OKF bundles only.
- **Existing OKF knowledge base** (an `index.md`/`log.md` bundle, any
  `okf_version`): update in place. **Additive** writes here are the one
  artifact class that is **not** asked about, because adding new concepts
  and index/log entries alongside the existing ones destroys nothing. Any
  write that would overwrite or amend what is already in the bundle goes
  through the batched list-and-approve above first. Never overwrite an
  existing `index.md` or `log.md` with the skeleton. If its `okf_version`
  is older
  than the version found by the current run's version check, follow the
  migration path in `okf-kb-guide.md` `## Migration` — propose the concrete
  changes and get the user's approval before touching anything, then log the
  migration in `log.md`.
