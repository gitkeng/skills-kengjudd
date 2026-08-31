---
name: init-project
description: >-
  Use when asked to init or set up a project for AI coding agents, bootstrap
  agent context files, or start a project knowledge base — "init this
  project for Claude Code", "set up AGENTS.md", "generate CLAUDE.md /
  GEMINI.md", "init โปรเจกต์", "ตั้งต้นโครงการให้ agent",
  "สร้าง AGENTS.md/CLAUDE.md", "ตั้งค่า knowledge base". Interviews the user
  (agents, task types, stack, knowledge-base folder name, Karpathy
  guidelines opt-in), researches any selected agent or named technology not
  already covered by its bundled reference, creates an OKF knowledge base
  (default folder knowledge-base), generates a canonical AGENTS.md plus
  per-agent adapters, and runs an adaptive expert review. Not for
  scaffolding application code, running git init, the built-in `/init` slash
  command (writes a single CLAUDE.md only), or analyzing an existing
  codebase in depth.
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
- **If you cannot ask, do not write.** The rule above assumes a live user
  channel. When this run has no way to put a question to a human — a
  headless or non-interactive invocation (`-p`, `exec`, a CI job), or a
  subagent with no path back to the user — create and modify **no files at
  all**. Emit the full Phase 1 question list, say the run stopped because it
  could not ask, and stop. Never substitute a default for an unanswered
  question.
- **Every factual claim written into a knowledge base carries `sources:`.**
  An **external** fact cites a resolvable URL from an official/trusted
  origin. A fact taken from the target project's own material — a README,
  design docs, meeting notes, an existing docs folder, i.e. the seed sources
  the `knowledge base` preset asks for — cites that file by a path that
  actually resolves **from the concept file that carries it**; the three
  path forms OKF accepts, their resolution bases, and the check to run
  before writing one are in
  [references/okf-kb-guide.md](references/okf-kb-guide.md)
  `## Creating the bundle` step 4. Nothing is written from memory. (A
  `Decision` concept recording this project's own choice has no external
  origin and needs no external source.) If research cannot settle a
  question, ask the user; if the user cannot settle it either, record it as
  an explicit gap instead of inventing an answer.
- **No bias toward any single agent.** Shared content lives only in the
  canonical `AGENTS.md`; agent-specific content lives only in that agent's
  adapter.

## Workflow

Run Phase 0 first, then Phases 1–6 in order. Phase 5 starts only after
Phases 3 **and** 4 have both finished, because it reviews both of their
outputs.

### Phase 0 — Detect a previous run

Before asking anything, look for evidence that this skill already ran here:
`<!-- init-project:start -->` markers in `AGENTS.md` or any adapter, an
`index.md` carrying `okf_version` in a knowledge-base-shaped folder, and an
`init-project` entry in that bundle's `log.md`.

- **No evidence:** this is a fresh run — continue to Phase 1 as written.
- **Evidence found:** say so, then make the re-run cheaper than run 1:
  1. Show the previous answers you can recover (project identity, agents,
     task types, `<kb>` folder, language, Karpathy state) as a list, and ask
     **only what changed** plus every gap the previous run left in
     `<kb>/log.md`.
  2. Re-research an existing technology concept only when its `verified:`
     date is more than 30 days old, its `stale_after:` has passed, or the
     user says the version changed. Otherwise keep it and skip Phase 2 for
     that technology.
  3. Phase 5 reviews only what this run writes or changes.
- **Foreign markers** — a provenance marker or log entry this skill did not
  write, or a run that looks half-finished — stop and tell the user before
  writing anything.

### Phase 1 — Interview

Ask **one topic at a time** and wait for each answer before moving on.
Conduct the interview in whatever language the user is already writing in;
the **Language of generated files** topic sets the language of the
*generated* files, not of this skill.

**Show the cost before you spend it.** As soon as the task types are known,
count the checklist items you are about to ask — including the items each
named technology adds — and tell the user that number before asking them.
Offer three ways forward: one question at a time, your recommendation for
all of them with corrections afterwards, or defer a named subset to the gap
list. **Hard ceiling: 25 questions in one run**, all topics included. On
reaching it, stop and ask whether to continue, take recommendations for the
rest, or defer the rest; everything deferred joins the running gap list.

1. **Project identity.** Ask for the project's **name** and a one-or-two
   sentence **purpose** (what it does, who it is for). Recommend the target
   directory's own name as the project name; for an existing codebase also
   draft the purpose from its README per `## Edge cases` and offer that
   draft. For an empty directory there is nothing to draft from — ask
   outright rather than inventing a purpose. Both answers are required:
   `assets/agents-md-template.md` and `assets/kb-skeleton/index.md` carry
   `<Project name>` tokens that Phase 3 forbids leaving unreplaced.
2. **Agents.** Multi-select from the twelve agents covered in
   [references/agent-context-matrix.md](references/agent-context-matrix.md)
   — Claude Code, Codex, Cursor, opencode, Gemini CLI, Zed, Kiro, Kimi CLI,
   Amp, Goose, ZCode, Antigravity — plus free text for any other agent.
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
   its `## Gap rules` — including the items an answer naming a new
   technology adds, which expand **one level only** under that file's
   expansion rule. Items the user explicitly defers are never silently
   dropped: add each to a **running gap list** you keep for the whole run.
   `<kb>/` does not exist yet, so nothing is written to it here — Phase 3
   step 5 flushes the list into `<kb>/log.md`, and Phase 6 reports it.
5. **Knowledge-base folder name.** Recommend `knowledge-base`, then ask.
   This is `<kb>` everywhere below. Accept only a **single path segment
   matching `[a-z0-9._-]+`** — no spaces, no `/`, no leading `.` alone, no
   absolute path, no `..`; re-ask with the constraint stated if the answer
   does not match. Check for an existing folder of that name
   **case-insensitively**, because macOS and Windows filesystems treat
   `Docs` and `docs` as the same directory. If the name is already taken by
   a folder this run must not write into, stop and ask: propose exactly one
   alternative (`<chosen>-okf`) and let the user accept it or name another.
   Never adjust the user's chosen name silently.
6. **Karpathy guidelines opt-in.** Ask whenever the project involves
   **writing code** — the `coding` preset, the `frontend` preset, or a
   confirmed free-text checklist for a code-flavored task type. It is the
   last item of the `## coding` checklist, so a run that selected `coding`
   has normally answered it there — carry that answer forward instead of
   asking again. Ask here only if no code-writing checklist covered it; the
   question wording is in
   [references/task-type-presets.md](references/task-type-presets.md)
   `## coding` and the default is to include. Including it never installs
   the upstream skill.
7. **Language of generated files.** Recommend the language the user is
   writing in, then ask. Every file this run writes — `AGENTS.md`, the
   adapters, the KB concepts, and the Phase 6 report — uses the answer,
   **except** three things that are never translated and never reworded:
   (a) the standing-rules block and the Karpathy block, copied char-for-char
   in English; (b) the four HTML markers `init-project:start`,
   `init-project:end`, `karpathy:start`, `karpathy:end`, which later runs
   match literally; (c) YAML keys and `type:` values in KB frontmatter. When
   the answer is not English, put one line **in the chosen language**
   immediately above each fixed block saying that it is quoted verbatim from
   this skill and must not be edited or translated. The same rule is
   restated in
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Standing rules block`.
8. **Pre-existing artifacts.** There is never one global question covering
   everything found, and never a silent overwrite — but the two later phases
   time their asks differently, because they know different things. **Phase
   3** asks when it encounters an artifact, since it discovers `<kb>/`'s
   contents as it goes. **Phase 4** asks for all of its targets up front in
   its step 1, because it knows its complete target list before it writes a
   byte. Both ask merge / skip / replace per artifact, per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`, which defines all three answers. **One exception:**
   additive writes into an existing OKF knowledge base — new concepts and
   index/log entries added alongside what is there — destroy nothing and are
   not asked about; an overwrite or amendment inside that bundle still goes
   through the batched ask in that same section. An older
   `okf_version` still goes through
   [references/okf-kb-guide.md](references/okf-kb-guide.md) `## Migration`
   and its own approval.

### Phase 2 — Research

1. Read [references/agent-context-matrix.md](references/agent-context-matrix.md)
   **first, and selectively**: read only the `## <agent>` section of each
   selected agent (its `## Contents` lists every section by name), plus
   `## Fallback rule` only when a selected agent is not listed there. Every
   agent it covers is already researched and sourced — use it as written; do
   not re-research it at run time and do not read sections for agents this
   run did not select.
2. For a selected agent the matrix does not cover, research it live from its
   official documentation and write up the same six fields in the matrix's
   format (context file(s) & precedence, import syntax, adapter rule, native
   init command, config locations, sources with a verification date). Decide
   its adapter rule with that file's `## Fallback rule`.
3. For every technology named during the interview, research the fields
   required by
   [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Researched-technology template` from official sources, within that
   section's **Effort bound** and its **Per-field N/A** rule.
4. **No web access:** say so to the user before continuing, proceed with
   bundled knowledge only, and add every skipped item to the running gap
   list from Phase 1 topic 4 (Phase 3 step 5 flushes it to `<kb>/log.md`;
   Phase 6 reports it). Never fill the hole from memory. "No web access"
   means every fetch route your harness offers has failed — see
   `## Version check` in the OKF guide for what counts.

### Phase 3 — Create the KB (draft)

1. Run [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Version check` once for this run, before creating or changing
   anything.
2. If `<kb>/` already exists: an OKF bundle goes through that file's
   `## Migration` (propose the concrete changes, get approval, log it); a
   non-OKF docs/notes folder is left untouched and handled per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`.
3. Create `<kb>/` if it does not exist, then instantiate
   `assets/kb-skeleton/index.md` and `assets/kb-skeleton/log.md`
   **only for the files that are not already there**. Where `<kb>/index.md`
   or `<kb>/log.md` already exists, never overwrite it: leave it in place
   and add to it (a new concept bullet, a new dated entry at the top) per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`, whose existing-OKF-bundle branch updates in place.
   **Additive writes anywhere under `<kb>/` proceed without a question;
   before overwriting or amending any `<kb>/` file that already exists, show
   the batched list from that same section and get one answer.**
   In every file you do instantiate, **replace every `<...>` token** —
   `<Project name>`, `<Title>`, `<path>`, `<description>`, `<YYYY-MM-DD>`,
   the seeding summary. No `<...>` placeholder may survive into the target
   project. The skeleton's `init-project:*` markers are not placeholders —
   keep them exactly where they are.
4. Write the concept documents per `## Creating the bundle`: one per named
   technology using `## Researched-technology template`; one per domain and
   per seed source named under the `## knowledge base` preset, using
   `## Domain and seed-source concepts`; one index concept per external KB
   per `## External knowledge bases`; and, if Karpathy was opted in, the
   fuller guidelines as a `Reference` concept.
5. Use only the four `type:` values in `## Type vocabulary`, and index every
   concept in `<kb>/index.md`, putting the bullets this run generates inside
   that file's `<!-- init-project:start -->` / `<!-- init-project:end -->`
   block per `## Creating the bundle` step 5. Write the
   `<kb>/log.md` entry for the seeding **and one entry for every gap
   accumulated in Phases 1–2** — this is where the running gap list is
   flushed to disk. Gap entries are bullets under the same date heading, not
   a heading each.

This is a **draft** — Phase 5 reviews and corrects it before the report.

### Phase 4 — Generate context files

1. **Check what already exists, before writing anything.** List every path
   this phase will write — `AGENTS.md`, plus one adapter per selected agent
   whose rule is not `native` — and for each path that already has a file,
   ask merge / skip / replace for that artifact **now**, per
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Merge semantics`. Carry the answers into the steps below; never write
   to a path whose answer you do not have.
2. Instantiate `assets/agents-md-template.md` as the canonical `AGENTS.md`
   at the target project root. Fill `## Project` from the interview (and,
   for an existing codebase, the light analysis described under
   `## Edge cases`); fill `## Commands` with the commands the interview's
   package-manager, test, lint, and build answers imply, deleting that
   section outright when the project has no toolchain yet and named none;
   fill `## Project knowledge base` with the chosen `<kb>` folder;
   fill `## Agent notes` per step 5. The template's `## Working rules`
   carries the **single source** of the standing-rules block —
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Standing rules block` points at the template rather than repeating
   it. Copy the template's block unchanged; never re-author, reorder, or
   translate it. Add the working-rules facts each preset's **Output delta**
   paragraph calls for, plus any bullet that guideline's
   `## Scaffolder collisions` requires, **immediately below the verbatim
   block, as additional bullets, never interleaved with it**.
3. **Provenance markers — always.** Everything this skill writes into
   `AGENTS.md` and into every adapter goes between
   `<!-- init-project:start -->` and `<!-- init-project:end -->`, on a fresh
   run exactly as on a merge; only the file's H1 stays outside them. The
   template already ships the pair around its body — keep them, do not add a
   second pair, and let the `karpathy:*` markers nest inside. An adapter you
   author from scratch gets the same wrapping. The `<kb>/index.md` bullets
   Phase 3 step 5 wrote are already wrapped by the skeleton per
   [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Creating the bundle` step 5. This is what makes a re-run replace
   instead of duplicate — without it, run 2 appends a second copy of
   everything.
4. **Karpathy block.** Opted in: keep the block between
   `<!-- karpathy:start -->` and `<!-- karpathy:end -->`. Opted out, **or
   never asked because no code-writing task type was selected**: delete that
   whole marked block, markers included.
5. **Adapters.** For each selected agent, look up its `**Adapter rule:**` in
   [references/agent-context-matrix.md](references/agent-context-matrix.md);
   for an agent not in the matrix, apply its `## Fallback rule` to the
   Phase 2 research. Before writing for a `native` agent, check the target
   directory for files that shadow or duplicate `AGENTS.md`, using that
   agent's **Context file(s) & precedence** field: Zed's first-match-wins
   list (`.rules`, `.cursorrules`, `.windsurfrules`, `.clinerules`,
   `.github/copilot-instructions.md`, `AGENT.md` each shadow `AGENTS.md`
   entirely), Goose's competing `.goosehints`, and — when both Antigravity
   and Gemini CLI are selected — the `GEMINI.md` adapter that Antigravity
   also reads alongside `AGENTS.md` with undocumented precedence. Report
   every hit and ask the user what to do before writing.
   - `native` — write no adapter file at all. Record the agent in
     `## Agent notes`.
   - `import-adapter` — write that agent's own context file containing the
     `AGENTS.md` import, plus **only** notes that are true of that agent and
     false of the others (at most two). Do not restate that `AGENTS.md` is
     canonical — the import line already says so.
   - `full-copy` — write that agent's own context file as a full copy of
     `AGENTS.md`'s content, carrying the provenance header given in
     `## Fallback rule`, and flag it in the Phase 6 report.

   **`## Agent notes`** carries one bullet per selected agent, each written
   as an imperative constraint for the agents that will read the file later,
   not as bookkeeping about this run. Every bullet names the adapter kind;
   for a `native` agent it also names the single behavior-changing quirk,
   taken from this closed list: (i) which file the agent reads, and whether
   it reads `AGENTS.md` at all; (ii) a native init command that would
   overwrite what this run wrote — written as "do not run `<command>` here",
   with the command and its create-versus-update behavior copied
   **verbatim from that agent's Native init command field**, never
   paraphrased or inferred; (iii) an import-expansion limit (for example
   "Do not add `@` imports — ZCode does not expand them"). For an
   `import-adapter` or `full-copy` agent the quirk goes in that agent's own
   file instead. At most one further bullet may carry a cross-agent warning;
   anything else belongs in `<kb>/`.
6. **Budget.** Respect
   [references/context-file-guidelines.md](references/context-file-guidelines.md)
   `## Content budget` (a full-copy adapter is exempt from the adapter cap
   and inherits `AGENTS.md`'s own budget). Over budget: never trim a fact
   silently — follow that section's **cut order**, moving the detail into
   `<kb>/` and leaving a pointer, deciding what goes where with
   `## Context vs KB`. A concept created here is a new concept even though
   Phase 3 step 5 has already run: give it frontmatter, an `<kb>/index.md`
   bullet, and a `<kb>/log.md` entry per
   [references/okf-kb-guide.md](references/okf-kb-guide.md)
   `## Creating the bundle`. Re-check the budget after every edit.
7. **Placeholder sweep — last step of this phase.** Grep the generated
   `AGENTS.md` and every adapter for `<`. No `<...>` token and no authoring
   comment may survive into the target project; the only comments allowed in
   the output are the `init-project:*` and `karpathy:*` markers. Delete
   everything else the template carried, including comments naming this
   skill's own `references/` files.

### Phase 5 — Expert review + apply

Follow [references/expert-review-protocol.md](references/expert-review-protocol.md)
end to end, and only once Phases 3 and 4 are both complete:

1. **Mode.** Apply `## Capability heuristic` — parallel subagents when your
   harness spawns them, otherwise sequential persona passes.
2. **Roster.** Build it with `## Reviewer roster`: the two standing
   reviewers plus **at most five** domain reviewers, grouped by shared
   review surface as that section describes. On a re-run, review only what
   this run wrote or changed.
3. **Checklists.** Use `## Checklist: prompt engineering`,
   `## Checklist: context engineering`, and `## Checklist: generic domain`
   as the pass/fail bars.
4. **Apply.** Follow `## Applying findings` — context files amended in
   place, KB concepts corrected and logged in `<kb>/log.md`. You are the
   adjudicator: accept by default and reject only for the reasons that
   section allows, giving every rejection a one-line reason.
5. **Converge.** Follow `## Convergence`: one review pass, then one
   re-check of only what changed, and never a third.

### Phase 6 — Report

Report to the user, in the language chosen in Phase 1 topic 7:

- **Files created or modified,** by path: `AGENTS.md`, each adapter, and
  everything under `<kb>/`.
- **Every decision taken,** each traceable to the user's own approval.
- **Remaining gaps:** deferred checklist items listed by task type and item;
  anything deferred at the 25-question ceiling; a skipped or failed OKF
  version check; anything degraded by missing web access; agents research
  could not resolve; technologies whose concepts were skipped rather than
  invented; any fact that could not be kept within the content budget.
- **Expert review:** which reviewers ran, how domain reviewers were grouped
  when the roster was capped, that accepted findings were applied, and every
  rejected finding with its one-line reason.
- **Where to change each agent's settings:** one line per selected agent
  naming its config location, taken from that agent's **Config locations**
  field in the matrix (or from the Phase 2 research for an agent the matrix
  does not cover).
- **Spec drift,** if the version check found an OKF version newer than the
  one [references/okf-kb-guide.md](references/okf-kb-guide.md) is written
  against — say that the skill itself needs a maintainer update.
- **Any full-copy adapter,** with the warning that later `AGENTS.md` edits
  will not propagate to it until this skill is re-run.
- **Any agent whose own init command could overwrite this output,** named
  with the "do not run it here" warning from `## Agent notes`.
- **How to re-run:** re-running this skill is safe. Everything it writes
  sits between `<!-- init-project:start -->` and `<!-- init-project:end -->`
  markers; a re-run replaces only what is between them and never touches
  anything outside them.
- **Out-of-scope suggestions,** clearly labeled as suggestions: e.g.
  installing the upstream Karpathy guidelines skill, or running
  `comprehensive-codebase-analysis` for a deep pass over an existing
  codebase.

## Edge cases

- **A context file already exists** → Phase 1 topic 8 and Phase 4 step 1.
- **An agent's own init command would overwrite this run's output.** The
  behavior differs per agent and must be quoted from the matrix, not
  paraphrased: Codex's `/init` creates an `AGENTS.md`; Kimi CLI's `/init`
  generates an `AGENTS.md`; Gemini CLI's `/init` writes a `GEMINI.md`;
  opencode's `/init` generates **or updates** `AGENTS.md`; Claude Code's
  `/init` suggests improvements instead of overwriting when a `CLAUDE.md`
  already exists. Warn the user in Phase 6 and record the "do not run
  `<command>` here" note per Phase 4 step 5. Never assert init behavior the
  matrix does not state.
- **Another run is writing at the same time.** Re-read every target file
  immediately before writing it, not only when you first listed it. If you
  find a provenance marker or `log.md` entry this run did not write, stop
  and tell the user instead of merging blind.
- **An existing OKF knowledge base at an older `okf_version`.** Migrate via
  [references/okf-kb-guide.md](references/okf-kb-guide.md) `## Migration`:
  write out the concrete file-by-file changes, get the user's approval, then
  apply and log them.
- **An existing codebase.** Do light analysis only — README, directory
  layout, manifest/config files — enough to fill `AGENTS.md`'s project and
  stack sections. Deep understanding is not this skill's job: point the user
  at the `comprehensive-codebase-analysis` skill instead of duplicating it.
- **No web access.** Only after every fetch route your harness offers has
  failed (a shell error alone is not proof — see
  [references/okf-kb-guide.md](references/okf-kb-guide.md)
  `## Version check`): tell the user, degrade to the bundled references, and
  add each skipped check to the running gap list — flushed to `<kb>/log.md`
  in Phase 3 step 5, reported in Phase 6. Bundled facts may be used;
  remembered facts may not.
- **An agent research cannot resolve.** Ask the user for the agent's
  official documentation or links. Record only the facts that get confirmed,
  in the matrix's format, and list everything else as a gap. If the adapter
  rule still cannot be determined, ask the user which of `native`,
  `import-adapter`, or `full-copy` applies — do not guess.

## References

| File | What it answers |
| --- | --- |
| [agent-context-matrix.md](references/agent-context-matrix.md) | Per-agent context files & precedence, import syntax, adapter rule, native init command, config locations, sources; `## Fallback rule` for agents it does not cover. |
| [task-type-presets.md](references/task-type-presets.md) | The four presets' gap checklists as ready-to-ask questions, their output deltas, free-text task types, gap/deferral/expansion rules. |
| [okf-kb-guide.md](references/okf-kb-guide.md) | OKF version check, bundle creation, migration, `type:` vocabulary, researched-technology and domain concept templates, external KBs. |
| [context-file-guidelines.md](references/context-file-guidelines.md) | Content budget and cut order, context-vs-KB split, the standing-rules block, scaffolder collisions, merge semantics. |
| [expert-review-protocol.md](references/expert-review-protocol.md) | Capability heuristic, reviewer roster and cap, the three checklists, applying findings, convergence. |

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
