# Run lifecycle

How one run of `init-project` finds out what is already there, records its
own state, plans its writes, and can be resumed or rolled back. Phase 0
(Detect a previous run) reads `## Target root`, `## Detection signals`,
`## Marker forms` and `## Phase 0 states`; Phase 3 (Create the KB) reads
`## Write plan` and `## Run record`; Phase 4 reads `## Rollback`; every
phase may consult `## Resume`, `## Headless gate` and `## Chat ledger`. The
**shape** of the run record (its frontmatter keys) lives in
`okf-kb-guide.md` `## Skill-owned concepts`; this file owns only its
lifecycle. Merge, skip and replace are defined once, in
`context-file-guidelines.md` `## Merge semantics`, and are not restated
here. This file travels with the skill (including a bare symlink install);
it makes no this-repo `knowledge/` references.

## Contents

- [Target root](#target-root)
- [Detection signals](#detection-signals)
- [Marker forms](#marker-forms)
- [Phase 0 states](#phase-0-states)
- [Run record](#run-record)
- [Write plan](#write-plan)
- [Resume](#resume)
- [Rollback](#rollback)
- [Headless gate](#headless-gate)
- [Chat ledger](#chat-ledger)

## Target root

The first thing a run does is confirm **where** it will write. Show the
absolute path of the directory that will be the target — the working
directory by default; when it sits inside a git working tree, also show the
git root (`git rev-parse --show-toplevel`; without a shell, show only the
working directory) and recommend that root — say whether it is empty or how
many entries it has, and ask the user to confirm it or name another path.
This is a **consent ask**: it is outside the question ceiling
(`task-type-presets.md` `### Cost preview and question ceiling`) and is
never answered by recommendation. Refuse `/` and the home directory by
asking for a more specific path (a re-ask under `## Gap rules`
**Re-ask bound**). Every detection below runs on the confirmed root only.
The run record stores the root as a scope descriptor ("the repository root
containing this knowledge base"), never as an absolute path, because a
knowledge base moves with its repository.

This ask is also the run's **channel probe**: on a harness that ends the
turn at a question, no user turn in reply means the run is headless — see
`## Headless gate`.

## Detection signals

Search **depth 1** from the confirmed root only — this skill always writes
`<kb>/` and the context files at the root — and skip `.git`,
`node_modules` and `.init-project-backup` by name (other dot-directories
are not skipped: `.kb` is a legal `<kb>` name). The signals are a closed
list; nothing else counts as evidence of a previous run:

- **(a)** a line `<!-- init-project:start -->` in `AGENTS.md`, `CLAUDE.md`
  or `GEMINI.md` at the root, or in any adapter path the matrix names for
  an agent the run record or `AGENTS.md` `## Agent notes` lists;
- **(b)** a directory whose `index.md` has frontmatter carrying
  `okf_version:` **and** a body carrying a well-formed marker pair;
- **(c)** in that same directory, a `log.md` bullet beginning
  `- Initialized by the init-project skill:` (the 1.0.0 form) or
  `- init-project: run` (the current form, `okf-kb-guide.md`
  `## Skill-owned concepts`);
- **(d)** in that same directory, `init-project-run.md` (the run record).

Signal (b) alone — an OKF bundle without (a), (c) or (d) — is somebody
else's bundle, not evidence. When `python3` is available,
`scripts/validate_output.py --detect <root>` prints the state from
`## Phase 0 states` and the signals it found; otherwise read the files by
hand against this list.

**Probes.** Two checks the interview relies on, stated as something you can
run:

- *Folder collision, case-insensitively* (Phase 1 **Knowledge-base folder
  name**): list the root's entries and compare `lower(entry)` with
  `lower(<chosen>)`. Shell: `ls -1A <root> | grep -ixF '<chosen>'` (a hit
  prints the real name); or
  `scripts/validate_output.py --probe-folder <root> <chosen>` (exit 0 free,
  exit 1 taken, real name printed). Without a shell, use the harness's
  directory-listing tool and compare yourself.
- *User channel*: the target-root consent ask above. Its observable result
  is whether a user turn follows.

## Marker forms

A file is **well-formed** when it contains exactly one line
`<!-- init-project:start -->` followed later by exactly one line
`<!-- init-project:end -->`, each on its own line and outside any code
fence; a `karpathy:start` / `karpathy:end` pair, if present, sits inside
that pair and appears once. A file with no marker at all is **unmarked**.
Anything else — a single marker, `end` before `start`, more than one pair,
a Karpathy pair outside the block or on its own, a marker inside a fence —
is **malformed**. Consequences: well-formed → the block is this skill's own
output (`context-file-guidelines.md` `## Merge semantics` **Marked
files**); unmarked → merge / skip / replace on the write plan; malformed →
Phase 0 state *foreign*, unless the write plan already says `replace` for
that path (replace discards the whole file, so its shape does not matter).
`<kb>/index.md` follows the same definition. `scripts/validate_output.py`
check C1 asserts well-formed on every file a run writes.

## Phase 0 states

Decide the state in this order, reading the run record **first** when one
exists — the record is the arbiter; markers and index are fallback
signals. The table is closed: a run is always in exactly one state.

| State | Condition | Action |
| --- | --- | --- |
| fresh | no record, no signal (a), no signal (b) with markers | Phase 1 as written |
| re-run | record with `init_project_status: complete`; or no record but well-formed markers plus a 1.0.0 log bullet (output of skill 1.0.0) | show `init_project_answers` (or what the artifacts let you recover), ask only what changed plus every open gap |
| half-finished | record with `init_project_status: in-progress` | `## Resume` |
| newer output | record whose `init_project_version` is newer than this skill's `metadata.version` | stop; tell the user to update the skill first |
| partial | signal (a) without any KB signal, or KB signals without (a), and no record | say which part was found; offer *treat as re-run* (the write plan recreates the missing part) or *stop* |
| dangling index bullet | an index bullet inside the block whose target file no longer exists | asked at the index union (`okf-kb-guide.md` `## Creating the bundle` step 5), never dropped silently |
| foreign | a malformed marker, a log bullet in neither form, or a marker or entry found during the re-read before a write that this run did not make | stop; write nothing; report the file and line |

The concurrent-run edge case (a marker or log entry appearing between the
write plan and the write) is the *foreign* state detected late.

## Run record

The record is one concept, `<kb>/init-project-run.md`, `type: Decision`,
whose keys are listed in `okf-kb-guide.md` `## Skill-owned concepts`. Its
lifecycle:

1. **Created** at Phase 3 **Skeleton, run record, gap flush** — the first
   moment `<kb>/` exists, after every interview answer and after the write
   plan was confirmed. The plan names `init-project-run.md` itself, so the
   record's first write is consented like every other path. It carries the
   confirmed plan, every answer, every confirmed command and free-text
   checklist, and `init_project_status: in-progress`.
2. **Updated** whenever the plan gains a delta, at the end of Phases 3, 4
   and 5 (`init_project_phase` advances), and at Phase 6
   **Gap flush and close**, which sets `init_project_completed`,
   `init_project_status: complete`, `init_project_deferred` (the snapshot at
   close) and flips OKF `status` to `stable`. Writing the record is never an
   amendment that asks — it is skill-owned (`## Merge semantics`
   **Skill-owned files**).
3. **On a re-run** the record is rewritten in place (`update` on the plan);
   the previous run's answers are replaced, and the run's log bullet
   summarizes what changed.

The record is indexed inside the index's marker block like any concept, has
no `stale_after`, and its `status` flips at Phase 6 (an exception to the
Phase 5 flip other concepts get).

## Write plan

Before Phase 3 writes its first file, the run shows **one table** of every
path Phases 3 and 4 will touch and gets **one answer** (a consent ask,
outside the ceiling; the user may amend any row in that same reply). One
row per path:

| Column | Values |
| --- | --- |
| path | relative to the root |
| action | `new` · `merge` · `replace` · `update` · `skip` |
| baseline | *absent* · *N lines, unmarked* · *N lines, marked* · *skill-owned (asset@version / record)* |
| rollback | `git checkout -- <path>` · `.init-project-backup/<ts>/<path>` · *delete (new file)* · *none (additive)* |

Rows come from the interview and Phase 2: `<kb>/index.md`, `<kb>/log.md`,
one row per concept slug (`okf-kb-guide.md` `## Concept kinds`),
`init-project-run.md`, every instantiated asset, `AGENTS.md`, one adapter
per selected agent whose rule is not `native`. Additive rows (`new` under
`<kb>/`) are shown for completeness but are not what the consent is about —
additive KB writes never ask. Marked context files never get
merge/skip/replace: they get the block diff (`## Merge semantics`
**Marked files**). A path discovered later — a concept created by the Phase
4 cut order or by a review finding — joins the plan as a one-line delta:
announced, not re-asked, when it is `new` under `<kb>/`; asked otherwise. A
skill-owned path is excluded from a run only by striking it from this
plan. The confirmed plan is written into the run record and is the only
authority Phases 3–4 write from.

Phase 4 **Baseline and block diff** re-reads every context-file target
(the second read: the first was for this plan), computes the block diff for
marked files, and asks its single confirmation before any context file is
written.

## Resume

- **Before Phase 3** nothing is on disk. A run interrupted there starts
  over; research extracts still present in the conversation
  (`## Chat ledger`) may be reused, nothing else needs recovery.
- **From Phase 3 on** the record carries `init_project_phase` and
  `init_project_status: in-progress`. Phase 0 state *half-finished* offers
  two options: **resume** from the recorded phase, or **start over** (an
  ordinary re-run over partial output, through a new write plan).
- **Idempotency.** Phases 3 and 4 can be re-executed from the recorded plan:
  every target is re-read immediately before it is written, the index is
  rebuilt as a union, and block diffs are computed from the file as it is
  now, so repeating a phase applies the same plan to the current state.
  Phase 5 resumed = a fresh review pass over what this run wrote (the pass
  is bounded anyway; applied findings are not recovered). Phase 6 reads
  everything it reports from the record.
- A resume asks no interview question again (the answers are in the
  record) but re-confirms the write plan as its one consent ask.
- Migration keeps its own resumability (`okf-kb-guide.md` `## Migration`
  step 5).

## Rollback

Two layers, both stated in the write plan so the consent covers them:

1. **Show before replace** — unchanged: the Replace answer in
   `## Merge semantics` shows what will be discarded before it is written.
2. **Backup before write**, for every `replace`, every `update` of an
   existing file, and every migration:
   - if the root is a git working tree **and** the path is tracked **and**
     clean (`git status --porcelain -- <path>` prints nothing), rollback is
     `git checkout -- <path>` and the plan says so;
   - otherwise (untracked, dirty, no git, or no shell to ask git) copy the
     file to `<root>/.init-project-backup/<UTC timestamp>/<relative path>`
     **before** writing, and the plan names that copy. A migration copies
     **every** file it will convert before converting the first one.
   - a brand-new path needs no backup: rollback is deleting it.

The backup directory is skipped by `## Detection signals`, is never written
inside the markers, and is never deleted by this skill — the Phase 6 report
lists every rollback per path and suggests removing the directory once the
user is satisfied.

## Headless gate

Iron rule 2 — *if you cannot ask, do not write* — needs a way to know. Treat
the run as headless when any of these holds: the harness invocation is
non-interactive (`-p`, `exec`, `--print` or that harness's equivalent, a CI
job); the run is executing inside a task or subagent tool (a subagent
system prompt, or no user turn at all in the conversation); or no user turn
follows the target-root ask on a harness that ends the turn at a question.

Then: create and modify **no files**; emit, as the result of the turn (the
final message, or the subagent's return value — never a file), the eight
Phase 1 topics by name with the sentence "checklist items follow from the
task types chosen; see task-type-presets.md", and say the run stopped
because it could not ask. Do not promise that a human sees it: in a
subagent the emission reaches only the caller. The test for this gate is
scenario E in the maintainer's scenario playbook: run headless on an empty
directory, expect zero files and the topic list.

## Chat ledger

Until `<kb>/` exists (end of Phase 2), the run's state lives in the
conversation. To survive compaction, re-emit the same fields the run record
will carry — answers by key, deferred keys, legacy folders, selected agents
and task types, language, Karpathy state, web verdict — **at the end of
Phase 1 and at the end of Phase 2**, at most 60 lines, in the interview
language with keys and enum values untranslated. Research extracts
(`okf-kb-guide.md` `## Researched-technology template` **Extract**) and
agent extracts (SKILL.md Phase 2 **Agent matrix**) are emitted once when
each item completes and are referenced by slug in the re-emission, never
repeated. From Phase 3 on, the record replaces the ledger.
