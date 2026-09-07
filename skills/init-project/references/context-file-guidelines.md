# Context-file guidelines

Rules for what `init-project` writes into a target project's generated
context files (canonical `AGENTS.md` and its per-agent adapters), and for
how it handles artifacts that already exist there. Phase 1 (Interview) only
*points* at `## Merge semantics` — it encounters no artifacts itself. Phase
3 (Create the KB) applies it through the write plan; Phase 4 (Generate
context files) applies it at **Baseline and block diff**, then consults
`## Content budget` while writing, `## Standing rules block` and
`## Scaffolder collisions` while assembling `## Working rules`,
`## Never translated` on every non-English run, and `## Context vs KB`
when a fact has to move. This file travels with the skill (including a
bare symlink install); it makes no this-repo `knowledge/` references.
Sibling references — `agent-context-matrix.md`, `okf-kb-guide.md`,
`run-lifecycle.md` — are allowed and used below.

## Contents

- [Content budget](#content-budget)
- [Context vs KB](#context-vs-kb)
- [Standing rules block](#standing-rules-block)
- [Never translated](#never-translated)
- [Scaffolder collisions](#scaffolder-collisions)
- [Merge semantics](#merge-semantics)

## Content budget

- Canonical `AGENTS.md`: **≤ 150 lines and ≤ 10 KB (10,240 bytes)**, both
  hard caps. For English the line cap normally binds first and the byte cap
  is the backstop for unusually long lines. **For scripts UTF-8 encodes in
  three bytes per character (Thai, most of CJK) the byte cap binds first**:
  budget in bytes from the start and expect roughly 3,400 characters at
  most — less, because the standing-rules and Karpathy blocks are always
  English and already use part of the budget — not 150 lines.
- Import-adapters (e.g. `CLAUDE.md` containing `@AGENTS.md`, `GEMINI.md`
  containing `@AGENTS.md`): **≤ 10 lines and ≤ 1 KB** — the import line
  plus at most two short agent-specific notes below it
  (`assets/adapter-template.md`).
- A **full-copy** adapter (`agent-context-matrix.md` `## Fallback rule`, for
  an agent with neither native `AGENTS.md` reading nor an import mechanism)
  is not an adapter in the sense above — it duplicates `AGENTS.md`'s content
  wholesale, so it inherits `AGENTS.md`'s own budget instead of the
  adapter cap.
- **Every cap scopes to the generated `<!-- init-project:start -->` /
  `<!-- init-project:end -->` block** this skill writes, not the file as a
  whole: pre-existing user content outside the markers never counts against
  the cap and is never cut to make room. Lines the user chose to keep in a
  block diff (`## Merge semantics` **Marked files**) count.
- **Over budget:** do not trim facts silently and do not let the file grow
  past the cap. Apply this **cut order**, stopping as soon as the file fits:
  1. Per-technology detail → move into that technology's knowledge-base
     concept, leaving a one-line stack summary in the context file.
  2. Process facts (methodology, reporting cadence, ways of working,
     convention documents) → the knowledge base, with a pointer.
  3. `## Agent notes` → one line per agent, nothing more.
  4. Explanatory clauses in `## Commands` → the knowledge base; keep the
     command and a short gloss.

  The standing-rules block and the Karpathy block are **never** trimmed, at
  any step. Still over budget after step 4: keep the fact, and record the
  overflow as a gap in the report.
- **The cap wins, but never by deletion.** When another rule says a fact
  must live in the context file and the cap says it does not fit, move
  something else out first; if nothing else qualifies, keep the fact and
  record the overflow as a report gap. Do not cycle between the two rules.
- Re-check the budget after every edit in Phase 4 and after every accepted
  expert-review finding in Phase 5; `scripts/validate_output.py` check C3
  asserts both units.

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

The standing-rules block has exactly one authoring home: the
`## Working rules` section of `assets/agents-md-template.md`. Copy it from
the template into every generated `AGENTS.md` unchanged. It is deliberately
**not** reproduced here — one copy cannot drift from itself. The one other
copy that exists, `standing-rules-history.md`, is a checked archive of every
shipped version (its latest section must equal the template byte for byte),
which is how Phase 4 **Baseline and block diff** tells an older block of
its own from a block the user edited. The block is self-contained: a target
project has none of this skill's own files present, so the rules name the
`kb-maintenance.md` file inside the project's knowledge base rather than
pointing back at this guide.

The block is never translated or reworded — see `## Never translated`.

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
instead: record the agreed cadence and owner there, add an explicit
override line for **every** standing bullet the answer supersedes, and
write a `decision-kb-cadence` concept (`okf-kb-guide.md`
`## Concept kinds`). A cadence answer supersedes both bullets above, so a
single line is not enough:

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

## Never translated

The single home of everything the **Language of generated files** answer
does not apply to. Every file this run writes uses the chosen language
**except**:

- (a) the standing-rules block and the Karpathy block, copied char-for-char
  in English, because later runs match them literally;
- (b) the four HTML markers `init-project:start`, `init-project:end`,
  `karpathy:start`, `karpathy:end`;
- (c) YAML keys and `type:` values in KB frontmatter;
- (d) anything quoted verbatim from `agent-context-matrix.md`: a native init
  command, a file name, an import syntax such as `@AGENTS.md`;
- (e) the run record's keys and enum values, the log-bullet tokens
  `init-project:`, `gap:`, `open`, `closed`, `declined`, and every item key
  (`coding/test-framework`, …) — these are what a later run parses;
- (f) files instantiated verbatim from an asset: `karpathy-guidelines.md`
  and `kb-maintenance.md` (English, with a notice line on a non-English
  run, so that a re-run can regenerate them without translating);
- (g) the backup directory name `.init-project-backup`.

When the chosen language is not English, put one line **in that language**
immediately above each fixed block (a) and at the top of each file in (f)
saying it is quoted verbatim from this skill and must not be edited or
translated. Reviewer briefs (`expert-review-protocol.md` `## Reviewer
brief`) carry this list; a finding that proposes changing anything on it
is invalid.

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
answer covering everything found, and never a silent overwrite. All of it
is decided on the **write plan** (`run-lifecycle.md` `## Write plan`), one
table the user answers once before Phase 3 writes its first file; no phase
asks "at encounter". What a path gets depends on what it is:

- an **unmarked** context-file path that exists → merge / skip / replace,
  defined below;
- a **marked** context-file path (a well-formed `init-project` pair,
  `run-lifecycle.md` `## Marker forms`) → this skill's own output: the
  block diff, below, never merge / skip / replace;
- a **skill-owned** file under `<kb>/` → regenerated, below;
- any other `<kb>/` write → additive or amend, below.

**Merge / skip / replace** (unmarked context files only):

- **Merge** — leave the existing content exactly as it is and add the
  generated content between the provenance markers, after the existing
  content.
- **Skip** — write nothing to that path at all, and list the skip in the
  report. Skipping `AGENTS.md` has a consequence to raise immediately:
  every import-adapter would then import a file this run did not author.
  Say so, and ask whether to write those adapters anyway (an interview
  question).
- **Replace** — overwrite the path with the generated content, wrapped in
  the provenance markers. Before replacing, show what is about to be
  discarded (at minimum: the existing headings and the file's length), get
  the user's confirmation on the plan, and back the file up per
  `run-lifecycle.md` `## Rollback`; then write.

**Marked files** (`AGENTS.md`, adapters, `<kb>/index.md` with a well-formed
pair): a re-run regenerates the block and leaves everything outside it
untouched. Because a consumer may have edited inside the block, Phase 4
**Baseline and block diff** collects, across **every** marked context file,
the in-block lines the regenerated blocks would drop, and shows them in
one message with one answer, answerable per line group: **keep** (the
line goes back into the regenerated block in its original section; a
section the template no longer has becomes an extra bullet below the
verbatim standing-rules block; or it moves into `<kb>/` with a pointer —
kept lines count against `## Content budget` and trigger the cut order
before writing), or **drop**. Lines inside the standing-rules block and the
Karpathy block are shown for information only and always regenerated
verbatim (`standing-rules-history.md` says how a differing block is
reported). Never write a block until that answer arrives. The index is
the exception that needs no diff: its block is rebuilt as a union
(`okf-kb-guide.md` `## Creating the bundle` step 5). A marked path is
excluded from a run only by striking it from the write plan; once the plan
is confirmed, the block diff is the only remaining question for it.

**Skill-owned files** (`<kb>/init-project-run.md`, and every file whose
frontmatter carries `init_project_asset`): listed on the plan as `update`
and regenerated without the batched amend ask. A file at one of those
paths **without** the key is not the skill's: it goes through the batched
amend list like any other existing concept. A skill-owned file the user
edited is shown as a differing row on the plan for information and still
regenerated — `kb-maintenance.md` tells consumers to write their own
concept instead of editing these.

**Knowledge-base files: additive writes are not asked about; overwrites and
amendments are one batched ask.** Split them by what the write does, not by
where it lands:

- **Additive** — creating a new concept file, appending a bullet inside the
  index's marker block, adding a dated entry at the top of `log.md`. This
  destroys nothing, so it proceeds **without a question**; the plan shows
  these rows for completeness.
- **Overwriting or amending** — replacing content in a `<kb>/` file that is
  already there: editing an existing concept, rewriting an existing index
  bullet's description, or converting files during a migration. These are
  **never** asked one file at a time. Show them as a single list — each path
  with what will change in it — and get one answer, the way
  `okf-kb-guide.md` `## Migration` presents its changes. The user may still
  answer per file for any subset they name. Never touch a `<kb>/` file that
  was not on the list you showed. This batched list is one of the run's
  fixed post-plan consent turns (`task-type-presets.md` `### Cost preview
  and question ceiling`).

**Existing non-OKF knowledge folder** (docs/notes/wiki content with no
per-file `type:` frontmatter and no `index.md`/`log.md` convention):
coexist. Create the new OKF bundle under the chosen folder name; if that
name is already taken by such a folder, Phase 1's knowledge-base-folder
topic stops and asks the user rather than adjusting the name silently, and
Phase 1 **Legacy knowledge folders** asks which folders to index from the
new bundle per `okf-kb-guide.md` `## Legacy knowledge folders`. Never
migrate or rewrite the old folder's content — `okf-kb-guide.md`
`## Migration` scopes migration to OKF bundles only.

**Existing OKF knowledge base** (an `index.md`/`log.md` bundle, any
`okf_version`): update in place, never overwrite an existing `index.md` or
`log.md` with the skeleton. If its `okf_version` is older than the version
found by the current run's version check, follow `okf-kb-guide.md`
`## Migration` — propose the concrete changes and get the user's approval
before touching anything, then log the migration in `log.md`.
