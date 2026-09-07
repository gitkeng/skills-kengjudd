# Task-type preset gap checklists

This file is consulted by `init-project` Phase 1 (Interview) once the user has
named one or more task types for the project. Each of the four preset
sections below (`coding`, `frontend`, `project management`, `knowledge base`)
is a checklist: every item is written out as a full, ready-to-ask question the
agent running this skill can put to the user verbatim (or adapt to the
interview's chosen language), one topic per question. Ask items one at a
time. Wherever a sensible default exists, state the recommendation first and
then ask — never assume it silently (the skill's iron rule: recommend, then
ask). Read only the sections of the presets the user selected, plus
`## Gap rules` and, when needed, `## Free-text task types`.

**Item keys.** Every item carries a stable key `<preset>/<slug>` in
brackets after its title — `[coding/test-framework]`. Keys are
`[a-z0-9-]` on both sides, never change when a question's wording changes,
and are never translated: they are what the interview turn shows, what
option 2 lists, what the run record, the `gap:` log bullets and a re-run's
Phase 0 use to refer to the same item. Expansion items are keyed
`<technology-slug>/role`; a confirmed free-text checklist's items are keyed
`<task-type-slug>/<item-slug>`.

Each preset section closes with an **Output delta** paragraph describing what
that preset's answers change in the generated `AGENTS.md` and in the project
knowledge base. `## Free-text task types` covers task types the user names
that are not one of the four presets. `## Gap rules` defines when an item
counts as an open gap, how naming a new technology grows a checklist, how
deferred items are tracked, and how many times anything may be re-asked —
these rules apply to every preset and to confirmed free-text checklists
alike.

## Contents

- [coding](#coding)
- [frontend](#frontend)
- [project management](#project-management)
- [knowledge base](#knowledge-base)
- [Free-text task types](#free-text-task-types)
- [Gap rules](#gap-rules)

## coding

- **Language(s) and runtime** `[coding/language-runtime]`. "Which
  programming language(s), and which runtime or language version, will this
  project use (for example: TypeScript on Node.js 22, Python 3.12, Go
  1.23)? If more than one, name each and where it applies (e.g. backend vs.
  frontend)." No universal default; if the user knows the language but not
  the version, recommend that language's current LTS or stable release.
- **Framework** `[coding/framework]`. "Is there an application framework
  this project is built on, or will be built on (for example Next.js,
  Django, Spring Boot, Express)? If none yet, that's a valid answer." No
  universal default; if a framework is genuinely needed for the stated
  language and use case, recommend the ecosystem's current, most common
  choice and let the user confirm or pick another.
- **Package manager / build tool** `[coding/package-manager]`. "Which
  package manager or build tool does, or will, this project use to install
  dependencies, run the project locally (the dev/run command), and build
  (for example npm/pnpm/yarn, pip/uv/poetry, Cargo, Maven/Gradle)?"
  Recommend the tool most idiomatic for the chosen language/framework (e.g.
  pnpm for a new Next.js project, uv for a new Python project) if the user
  has no preference.
- **Test framework** `[coding/test-framework]`. "Which test framework will
  this project use (for example Jest or Vitest, pytest, JUnit, `go
  test`)?" Recommend the ecosystem-standard test framework for the chosen
  language if the user has none in mind.
- **Lint/format tooling** `[coding/lint-format]`. "Which linting and
  code-formatting tools should this project enforce (for example ESLint plus
  Prettier, Ruff, golangci-lint)?" Recommend the ecosystem-standard
  combination for the chosen language if the user has no preference.
- **Repo layout** `[coding/repo-layout]`. "How is, or should, the
  repository be laid out — for example a single package at the root, a
  monorepo with multiple packages/workspaces, or a specific source/test
  directory convention?" Recommend a single-package layout for a new, small
  project, and a monorepo only if the user already described multiple
  deployable components.
- **CI** `[coding/ci]`. "Does this project use, or should it use, a
  continuous-integration pipeline (for example GitHub Actions, GitLab CI,
  CircleCI), and if so, what does it currently run (tests, lint, build,
  deploy)?" Recommend adding a minimal pipeline that runs the chosen test
  and lint tools if none exists yet.
- **Existing convention documents** `[coding/existing-conventions]`. "Are
  there existing documents this project already follows for coding
  conventions or architecture (a style guide, an ADR log, a
  CONTRIBUTING.md, an existing AGENTS.md or CLAUDE.md)? If yes, where do
  they live?" No default — this item exists so the skill reads and respects
  what already exists instead of duplicating or contradicting it. A
  directory named here seeds the Phase 1 **Legacy knowledge folders**
  candidate list; a context file named at a path other than the root is
  shown on the write plan as *existing, not a target*.
- **Commands** `[coding/commands]`. Ask after every tool item above is
  answered: "These are the commands I will write into `AGENTS.md` —
  install: `<…>`, dev: `<…>`, test: `<…>`, lint: `<…>`, build: `<…>`.
  Confirm, correct any of them, or say which the project has no command
  for." Recommend the commands the tool answers imply; for an existing
  codebase, read them from the manifest's scripts (`package.json`,
  `Makefile`, `pyproject.toml`, …) and offer those. One question, five
  values; a command the user says does not exist is deleted from
  `## Commands`. Phase 4 writes only what was confirmed here.
- **Karpathy guidelines opt-in** `[coding/karpathy-opt-in]`. "This skill
  can include a short, attributed excerpt of the Karpathy engineering
  guidelines — behavioral rules that push against overcomplicating changes,
  favor surgical edits, ask the agent to surface its assumptions, and
  require verifiable success criteria — as a clearly marked, removable
  block in the generated AGENTS.md, plus the full guidelines as a reference
  concept in the knowledge base. The default is to include it. Keep the
  default, or opt out?" Default: include. Declining removes the marked
  Karpathy guidelines block from the generated AGENTS.md entirely, and the
  KB skips the corresponding reference concept. **Gating:** this is the
  interview's single Karpathy question for any project that involves
  **writing code**. When `frontend`, or a confirmed code-flavored free-text
  checklist, is selected without `coding`, ask this same item (same key)
  once there instead. Never ask it twice. When no code-writing task type is
  selected at all it is never asked, and Phase 4 deletes the marked block
  from the generated AGENTS.md.

**Output delta:** the coding preset's answers populate `AGENTS.md`'s project
stack description (language/runtime, framework, package manager/build tool,
test framework, lint/format tooling), its `## Commands` section (from the
confirmed commands only), and drive one knowledge-base concept per named
technology, seeded per `okf-kb-guide.md`'s `## Researched-technology
template`. Repo layout and CI answers are folded into the same stack
description; where CI already exists, note whether it already gates lint,
test, and build so later reports can point back to it. Existing convention
documents are read and cross-referenced rather than duplicated — link them
from the generated working-rules section instead of restating their content
(moved to a `conventions-<slug>` concept only when the cut order forces it).
The Karpathy opt-in controls exactly one thing: whether the generated
AGENTS.md keeps or drops its marked Karpathy guidelines block; opting in also
instantiates the full guidelines as a knowledge-base reference concept from
the skill's asset, opting out skips both.

## frontend

- **Framework** `[frontend/framework]`. "Which frontend framework does, or
  will, this project use (for example React, Vue, Svelte, SwiftUI,
  Flutter)?" If the coding preset's framework answer already names a
  full-stack framework (e.g. Next.js), confirm whether that answer already
  covers the frontend or a separate frontend-only framework applies.
- **Component library** `[frontend/component-library]`. "Is there a UI
  component library this project uses or should use (for example shadcn/ui,
  Material UI, Chakra UI, Flutter's Material widgets)? If none, that's a
  valid answer." No universal default; recommend one only when the named
  framework has an obvious idiomatic pairing (e.g. shadcn/ui for a new
  React/Next.js project).
- **Styling approach** `[frontend/styling]`. "How is, or will, styling be
  done — for example Tailwind CSS, CSS Modules, styled-components, or a
  design-token system?" Recommend Tailwind CSS as a common current default
  for a new web project if the user has no preference and the framework
  supports it.
- **Design source** `[frontend/design-source]`. "Is there a design source
  of truth for this project's UI (for example a Figma file, a design-system
  document, hand-sketched mockups)? If yes, where can the skill find it (a
  link or file path)?" No default — "none yet" is a valid answer.
- **State management** `[frontend/state-management]`. "Does, or should,
  this project use a dedicated state-management approach (for example
  Redux, Zustand, React Context, Riverpod, Vuex), or is local component
  state enough?" Recommend starting with the framework's built-in state
  primitives and no separate library for a new, small project, escalating
  only if the user expects complex shared state.
- **Target platforms/browsers** `[frontend/target-platforms]`. "Which
  platforms or browsers must this project support (for example the latest
  evergreen desktop and mobile browsers, a specific minimum browser
  version, native iOS/Android, a specific OS)?" Recommend the current two
  latest versions of major evergreen browsers as a reasonable default for a
  new web project if the user has no specific requirement.
- **Accessibility requirements** `[frontend/accessibility]`. "Does this
  project have specific accessibility requirements or a compliance target
  (for example WCAG 2.1 AA, a legal requirement, or none formal but
  best-effort)?" Recommend a best-effort WCAG 2.1 AA baseline if the user
  has no formal requirement.

**Output delta:** frontend answers extend `AGENTS.md`'s project stack
description with the frontend framework, component library, styling
approach, and state-management choice, and drive one knowledge-base concept
per named frontend technology (framework, component library, design tool)
per the researched-technology template. The design-source answer also
shapes Phase 5's expert-review roster — a design/Figma-flavored domain
reviewer is only added when a design source was actually named. Target
platform/browser and accessibility answers are recorded as explicit
constraints (a bullet below the standing-rules block, or the `constraints`
concept of `okf-kb-guide.md` `## Concept kinds` when they do not fit)
because they change what "done" means for UI work, not just what stack is
used.

## project management

- **Methodology** `[project-management/methodology]`. "What
  project-management methodology does this team follow (for example Scrum,
  Kanban, ad hoc/none)?" Recommend a lightweight Kanban-style flow if the
  user has no formal methodology and the project is small.
- **Tracker tool** `[project-management/tracker]`. "Which issue or task
  tracker does this project use, if any (for example GitHub Issues, Jira,
  Linear, a plain markdown TODO file)?" No universal default; if none
  exists, recommend a plain markdown task list inside the repo as the
  lowest-friction option.
- **Where specs/tasks live in the repo** `[project-management/specs-location]`.
  "Where in the repository do specs, plans, or task breakdowns live, or
  where should they live (for example `docs/`, `.github/ISSUE_TEMPLATE/`, a
  dedicated `specs/` or `tasks/` folder)?" Recommend a `docs/` or `specs/`
  folder at the repo root if nothing exists yet.
- **Definition of done** `[project-management/definition-of-done]`. "What
  counts as 'done' for a unit of work on this project (for example: tests
  pass and code is reviewed; tests pass and it's deployed; PM sign-off;
  docs updated)?" Recommend "tests pass, lint passes, and the change is
  reviewed" as a baseline if the user has none defined.
- **Reporting cadence** `[project-management/reporting-cadence]`. "How
  often, and to whom, does progress get reported (for example a daily
  standup note, a weekly summary, none needed)?" No default — "none" is a
  valid answer for a small or solo project.

**Output delta:** the tracker location, where specs/tasks live, and the
definition of done are written into `AGENTS.md`'s working-rules section so
any agent knows where to file work and what "complete" means. Methodology
and reporting cadence change less often than code but are still useful to
look up later, so they become the `process-<slug>` concept of
`okf-kb-guide.md` `## Concept kinds` rather than being baked into
`AGENTS.md` itself. A concrete tracker product (e.g. Jira, Linear) is
treated like any other named technology: it gets a knowledge-base reference
concept via the researched-technology template once its role and docs are
known.

## knowledge base

- **Knowledge domains to cover** `[knowledge-base/domains]`. "Which
  knowledge domains or topics should this project's knowledge base cover
  (for example: business rules, architecture decisions, API contracts,
  deployment runbooks, a glossary of domain terms)?" No default — this is
  project-specific; if the user is unsure, recommend starting with whatever
  domains already surfaced elsewhere in this interview (named technologies,
  architecture, team process) and expanding later.
- **Initial seed sources** `[knowledge-base/seed-sources]`. "What existing
  material should seed the knowledge base — indexed and cited, not copied
  in — (for example an existing README, a wiki, design docs, meeting
  notes), or is there nothing yet?" No default; "nothing yet" is a valid
  answer for a brand-new project.
- **External KBs to reference** `[knowledge-base/external-kbs]`. "Does this
  project already have, or use, a separate, already-structured knowledge
  base elsewhere (another OKF bundle, a wiki, a Confluence space) that this
  knowledge base should index and link to rather than duplicate?" No
  default; "none" is a valid answer.
- **Update cadence and ownership** `[knowledge-base/update-cadence]`. "How
  often should the knowledge base be updated, and who — or what process —
  is responsible for keeping it current (for example: after every completed
  task, weekly, 'agents update it automatically after each work
  session')?" Recommend "agents update it after every completed piece of
  work" as the default, matching this skill's own standing rule for
  generated context files.

Two further keys are asked outside this checklist and count like its
items: `[knowledge-base/legacy-folders]` (Phase 1 **Legacy knowledge
folders**) and `[knowledge-base/type-vocabulary]` (Phase 3 **Existing
bundle**, `okf-kb-guide.md` `## Type vocabulary`).

**Output delta:** knowledge domains and initial seed sources directly
determine which concepts get pre-seeded into the knowledge base during
Phase 3, beyond the technology concepts every preset can add. External KBs
named here are recorded as index/reference concepts per
`okf-kb-guide.md`'s `## External knowledge bases`, not copied in full.
Update cadence and ownership are written into `AGENTS.md`'s
`## Project knowledge base` section as the standing instruction agents
follow afterward — by default, read the knowledge base first and update it
after every completed piece of work. When the answer differs from that
default it contradicts the verbatim standing-rules block, so write it with
the explicit override lines described in `context-file-guidelines.md`
`## Standing rules block` rather than editing the block, and record a
`decision-kb-cadence` concept.

## Free-text task types

When the user names a task type that is not one of the four presets above,
the skill does not leave it unstructured — it builds a checklist for it by
analogy, then confirms that checklist with the user before using it:

1. **Identify the closest preset(s) by topic overlap.** A task type close to
   software work borrows the shape of `## coding` (or `## frontend` for
   UI-heavy work); a task type close to process or planning work borrows
   `## project management`; a task type centered on documentation or
   research borrows `## knowledge base`. A task type that spans more than
   one of these may borrow items from more than one preset.
2. **Draft a checklist in the same shape as the sections above** — one full,
   ready-to-ask question per item, one topic per question, each with a key
   `<task-type-slug>/<item-slug>`, with a sensible recommendation stated
   wherever one exists. Add items the presets don't cover only when they
   are clearly implied by the task type itself (for example, a "data
   engineering" task type might add "which data pipeline/orchestration
   tool, if any?").
3. **Confirm the draft in one question** (it counts as one interview
   question) before asking any item from it, explicitly labeled as a draft,
   with three options: *accept as drafted*; *accept with these edits* —
   additions, removals and rewordings given in that same reply; *drop this
   task type* (no checklist, no output delta; recorded in the run record so
   a re-run does not re-ask). Edits are applied and the revised draft shown
   once more for a second confirmation (one more question). Further edits
   after that are recorded as gaps, never a third round. Do not start
   interviewing against a free-text checklist the user has not confirmed.
4. **Once confirmed** (with or without edits), the checklist becomes that
   task type's working checklist and follows `## Gap rules` exactly like a
   named preset's checklist — the same gap, deferral, expansion and re-ask
   behavior applies.
5. **Record the confirmed checklist** in the run record
   (`init_project_free_text_checklists`) — always, so a future run of the
   skill does not redraft it — and point at it from the report.

## Gap rules

A **gap** is any checklist item — from a preset above, or from a confirmed
free-text checklist — that has not yet been answered and has not been
explicitly deferred by the user. Keep asking (one gap at a time,
recommendation first, per the iron rule) until, for every task type the user
selected, no gaps remain — subject to the preview, ceiling and re-ask bound
below.

### Cost preview and question ceiling

**Interview turn format.** Every interview question is put as
`[<n>/25] <key> — <question> Recommendation: <value>. Options: <a> / <b> / other.`
in the interview language, key untranslated; `Options:` is omitted when
the answer is free text or a multi-select from a list already shown, and
consent asks carry no counter.

Before asking the first checklist item, tell the user three numbers: the
interview questions already spent (the Phase 1 topics), the number the
selected task types add — preset items plus the expansion items already
known, stated as "at least N" when expansions are not yet known — and how
many remain under the ceiling. When an expansion later adds an item, say so
in one line ("+1 from Next.js: role") instead of restating the preview.
Then offer three ways forward:

1. answer them one at a time;
2. take your recommendation for every item — shown as one keyed list
   `key — recommendation` in a single message, which counts as **one**
   question; corrections that follow reference keys and are replies, not
   questions;
3. defer a named subset (by key) to the gap list now.

**Hard ceiling: 25 interview questions per run.** The ceiling counts
interview questions only: the Phase 1 topics, checklist items, expansion
items, re-asks, the commands confirmation, the legacy-folders question, the
type-vocabulary question, the research-scope question, and Phase 0's
what-changed, re-research and open-gaps questions on a re-run. Every other
question a rule of this skill requires — a research dead end, an agent
research cannot resolve, a technology that cannot be researched, a pinned
version, a folder-name collision, the skip-`AGENTS.md` consequence — is an
interview question too and counts.

**Consent asks are outside the ceiling** and are never resolved by the
ceiling's recommend-the-rest or defer exits: they are always asked and
always answered before the write they gate. They are a closed set: the
target-root confirmation, the write plan (which carries merge / skip /
replace, shadow-file answers, the backup directory and each rollback), and
after the plan at most **four** further consent turns in a run — one
block-diff confirmation covering every marked context file (Phase 4), one
batched KB amend list (Phase 3 or Phase 5), one batched ask carrying at most
three user-conflict findings (Phase 5), and one migration approval (Phase
3). No other consent ask exists.

On reaching the ceiling, stop and ask whether to continue, take
recommendations for what remains, or defer it; the ceiling ask itself does
not count. After *continue*, the interview ends when the finite checklist is
exhausted — say how many items remain. Everything deferred at the ceiling
joins the running gap list and is treated exactly like any other deferral
below. The ceiling restarts at 0 on every run, re-runs included.

### Re-ask bound

Any question may be re-asked at most **twice** (three asks in total), each
counting toward the ceiling. An **ambiguous** answer — one that matches no
option and is not a deferral — gets one re-ask that shows the option set
before it counts as the second ask. After the third ask without a usable
answer the item becomes *deferred* with the reason "no usable answer after
3 asks" recorded in its `gap:` bullet and in the run record's reason
field — except for an item the run cannot proceed without (the project
name, the `<kb>` folder name), where the run stops without writing
anything and says why (iron rule 2). A re-run does not re-ask an item the
record marks this way unless the user brings it up.

### Technology expansion — depth 1 only

An answer that names a technology can add an item to the checklist, but only
within both of these limits:

- **Only project decisions expand.** A technology expands when the user
  chose it *as a project decision* — their answer to the framework,
  component-library, styling, state-management, design-source, tracker, or
  CI question, or a technology they volunteered in free text. **This holds
  regardless of who first proposed it:** an enumerated question's answer
  expands whether the user named the technology unprompted or accepted the
  agent's recommendation for that same question — both count as the user's
  project decision once confirmed. A technology
  that merely came along with a recommendation the user accepted — the
  ecosystem's default bundler, a transitive dependency, a peer library the
  framework ships with — does **not** expand. It still gets a knowledge-base
  concept: expansion scope is narrow, concept scope is broad (see
  `okf-kb-guide.md` `## Researched-technology template`).
- **Expansion is one level deep, and expansion items are terminal.** The
  items an expansion adds never expand again. A second-order technology
  named while answering them becomes a one-line mention inside the parent
  technology's knowledge-base concept, or a gap — never its own checklist
  branch.

The expansion adds exactly one item:

- **Role** `[<technology-slug>/role]`. "What role does <technology> play in
  this project (for example: the frontend framework, the CI runner, the
  primary datastore)?"

Do **not** ask for the technology's version or its docs URL — Phase 2
settles both from official sources. Ask about a version only when the
project pins one that differs from current stable, when research cannot
disambiguate which release is meant, or when there is no version to pin and
the user has to say so.

This item is a gap like any other until answered. Once answered, each
expanded technology's answer set feeds one knowledge-base concept per
`okf-kb-guide.md`'s `## Researched-technology template`.

An item becomes **deferred**, not a gap, only when the user explicitly says
to skip or postpone it (for example: "we don't know yet," "decide later,"
"not applicable"), or under the re-ask bound above. Deferred items:

- are never silently dropped — they are recorded in the report to the
  user, listed by task type and key; and
- are also recorded in the project knowledge base as a `gap:` bullet in
  `log.md` (`okf-kb-guide.md` `## Skill-owned concepts` **Log bullet
  grammar**), which is the single authority on what was left open and why.

Deferring is not the same as declining forever: a deferred item can be
answered later in the same session if the user brings it up, or on a future
run of the skill.
