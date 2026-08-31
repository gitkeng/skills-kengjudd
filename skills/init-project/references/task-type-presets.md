# Task-type preset gap checklists

This file is consulted by `init-project` Phase 1 (Interview) once the user has
named one or more task types for the project. Each of the four preset
sections below (`coding`, `frontend`, `project management`, `knowledge base`)
is a checklist: every item is written out as a full, ready-to-ask question the
agent running this skill can put to the user verbatim (or adapt to the
interview's chosen language), one topic per question. Ask items one at a
time. Wherever a sensible default exists, state the recommendation first and
then ask — never assume it silently (the skill's iron rule: recommend, then
ask). Each preset section closes with an **Output delta** paragraph
describing what that preset's answers change in the generated `AGENTS.md` and
in the project knowledge base. `## Free-text task types` covers task types the
user names that are not one of the four presets. `## Gap rules` defines when
an item counts as an open gap, how naming a new technology grows a checklist,
and how deferred items are tracked — these rules apply to every preset and to
confirmed free-text checklists alike.

## Contents

- [coding](#coding)
- [frontend](#frontend)
- [project management](#project-management)
- [knowledge base](#knowledge-base)
- [Free-text task types](#free-text-task-types)
- [Gap rules](#gap-rules)

## coding

- **Language(s) and runtime.** "Which programming language(s), and which
  runtime or language version, will this project use (for example:
  TypeScript on Node.js 22, Python 3.12, Go 1.23)? If more than one, name
  each and where it applies (e.g. backend vs. frontend)." No universal
  default; if the user knows the language but not the version, recommend
  that language's current LTS or stable release.
- **Framework.** "Is there an application framework this project is built
  on, or will be built on (for example Next.js, Django, Spring Boot,
  Express)? If none yet, that's a valid answer." No universal default; if a
  framework is genuinely needed for the stated language and use case,
  recommend the ecosystem's current, most common choice and let the user
  confirm or pick another.
- **Package manager / build tool.** "Which package manager or build tool
  does, or will, this project use to install dependencies and build (for
  example npm/pnpm/yarn, pip/uv/poetry, Cargo, Maven/Gradle)?" Recommend the
  tool most idiomatic for the chosen language/framework (e.g. pnpm for a new
  Next.js project, uv for a new Python project) if the user has no
  preference.
- **Test framework.** "Which test framework will this project use (for
  example Jest or Vitest, pytest, JUnit, `go test`)?" Recommend the
  ecosystem-standard test framework for the chosen language if the user has
  none in mind.
- **Lint/format tooling.** "Which linting and code-formatting tools should
  this project enforce (for example ESLint plus Prettier, Ruff,
  golangci-lint)?" Recommend the ecosystem-standard combination for the
  chosen language if the user has no preference.
- **Repo layout.** "How is, or should, the repository be laid out — for
  example a single package at the root, a monorepo with multiple
  packages/workspaces, or a specific source/test directory convention?"
  Recommend a single-package layout for a new, small project, and a monorepo
  only if the user already described multiple deployable components.
- **CI.** "Does this project use, or should it use, a continuous-integration
  pipeline (for example GitHub Actions, GitLab CI, CircleCI), and if so,
  what does it currently run (tests, lint, build, deploy)?" Recommend adding
  a minimal pipeline that runs the chosen test and lint tools if none exists
  yet.
- **Existing convention documents.** "Are there existing documents this
  project already follows for coding conventions or architecture (a style
  guide, an ADR log, a CONTRIBUTING.md, an existing AGENTS.md or CLAUDE.md)?
  If yes, where do they live?" No default — this item exists so the skill
  reads and respects what already exists instead of duplicating or
  contradicting it.
- **Karpathy guidelines opt-in.** "This skill can include a short,
  attributed excerpt of the Karpathy engineering guidelines — behavioral
  rules that push against overcomplicating changes, favor surgical edits,
  ask the agent to surface its assumptions, and require verifiable success
  criteria — as a clearly marked, removable block in the generated
  AGENTS.md, plus a fuller reference copy in the knowledge base. The default
  is to include it. Keep the default, or opt out?" Default: include.
  Declining removes the marked Karpathy guidelines block from the generated
  AGENTS.md entirely, and the KB skips the corresponding reference concept.
  **Gating:** this is the interview's single Karpathy question for any
  project that involves **writing code**. When `frontend`, or a confirmed
  code-flavored free-text checklist, is selected without `coding`, ask this
  same item once there instead. Never ask it twice. When no code-writing
  task type is selected at all it is never asked, and Phase 4 deletes the
  marked block from the generated AGENTS.md.

**Output delta:** the coding preset's answers populate `AGENTS.md`'s project
stack description (language/runtime, framework, package manager/build tool,
test framework, lint/format tooling) and drive one knowledge-base concept per
named technology, seeded per `okf-kb-guide.md`'s `## Researched-technology
template`. Repo layout and CI answers are folded into the same stack
description; where CI already exists, note whether it already gates lint,
test, and build so later reports can point back to it. Existing convention
documents are read and cross-referenced rather than duplicated — link them
from the generated working-rules section instead of restating their content.
The Karpathy opt-in controls exactly one thing: whether the generated
AGENTS.md keeps or drops its marked Karpathy guidelines block; opting in also
adds the fuller guidelines as a knowledge-base reference concept, opting out
skips both.

## frontend

- **Framework.** "Which frontend framework does, or will, this project use
  (for example React, Vue, Svelte, SwiftUI, Flutter)?" If the coding
  preset's framework answer already names a full-stack framework (e.g.
  Next.js), confirm whether that answer already covers the frontend or a
  separate frontend-only framework applies.
- **Component library.** "Is there a UI component library this project uses
  or should use (for example shadcn/ui, Material UI, Chakra UI, Flutter's
  Material widgets)? If none, that's a valid answer." No universal default;
  recommend one only when the named framework has an obvious idiomatic
  pairing (e.g. shadcn/ui for a new React/Next.js project).
- **Styling approach.** "How is, or will, styling be done — for example
  Tailwind CSS, CSS Modules, styled-components, or a design-token system?"
  Recommend Tailwind CSS as a common current default for a new web project
  if the user has no preference and the framework supports it.
- **Design source.** "Is there a design source of truth for this project's
  UI (for example a Figma file, a design-system document, hand-sketched
  mockups)? If yes, where can the skill find it (a link or file path)?" No
  default — "none yet" is a valid answer.
- **State management.** "Does, or should, this project use a dedicated
  state-management approach (for example Redux, Zustand, React Context,
  Riverpod, Vuex), or is local component state enough?" Recommend starting
  with the framework's built-in state primitives and no separate library for
  a new, small project, escalating only if the user expects complex shared
  state.
- **Target platforms/browsers.** "Which platforms or browsers must this
  project support (for example the latest evergreen desktop and mobile
  browsers, a specific minimum browser version, native iOS/Android, a
  specific OS)?" Recommend the current two latest versions of major
  evergreen browsers as a reasonable default for a new web project if the
  user has no specific requirement.
- **Accessibility requirements.** "Does this project have specific
  accessibility requirements or a compliance target (for example WCAG 2.1
  AA, a legal requirement, or none formal but best-effort)?" Recommend a
  best-effort WCAG 2.1 AA baseline if the user has no formal requirement.

**Output delta:** frontend answers extend `AGENTS.md`'s project stack
description with the frontend framework, component library, styling
approach, and state-management choice, and drive one knowledge-base concept
per named frontend technology (framework, component library, design tool)
per the researched-technology template. The design-source answer also
shapes Phase 5's expert-review roster — a design/Figma-flavored domain
reviewer is only added when a design source was actually named. Target
platform/browser and accessibility answers are recorded as explicit
constraints (in the working-rules section or a project-constraints note)
because they change what "done" means for UI work, not just what stack is
used.

## project management

- **Methodology.** "What project-management methodology does this team
  follow (for example Scrum, Kanban, ad hoc/none)?" Recommend a lightweight
  Kanban-style flow if the user has no formal methodology and the project is
  small.
- **Tracker tool.** "Which issue or task tracker does this project use, if
  any (for example GitHub Issues, Jira, Linear, a plain markdown TODO
  file)?" No universal default; if none exists, recommend a plain markdown
  task list inside the repo as the lowest-friction option.
- **Where specs/tasks live in the repo.** "Where in the repository do specs,
  plans, or task breakdowns live, or where should they live (for example
  `docs/`, `.github/ISSUE_TEMPLATE/`, a dedicated `specs/` or `tasks/`
  folder)?" Recommend a `docs/` or `specs/` folder at the repo root if
  nothing exists yet.
- **Definition of done.** "What counts as 'done' for a unit of work on this
  project (for example: tests pass and code is reviewed; tests pass and
  it's deployed; PM sign-off; docs updated)?" Recommend "tests pass, lint
  passes, and the change is reviewed" as a baseline if the user has none
  defined.
- **Reporting cadence.** "How often, and to whom, does progress get reported
  (for example a daily standup note, a weekly summary, none needed)?" No
  default — "none" is a valid answer for a small or solo project.

**Output delta:** the tracker location, where specs/tasks live, and the
definition of done are written into `AGENTS.md`'s working-rules section so
any agent knows where to file work and what "complete" means. Methodology
and reporting cadence change less often than code but are still useful to
look up later, so they typically become a knowledge-base concept documenting
the team's process rather than being baked into `AGENTS.md` itself. A
concrete tracker product (e.g. Jira, Linear) is treated like any other named
technology: it gets a knowledge-base reference concept via the
researched-technology template once its role and docs are known.

## knowledge base

- **Knowledge domains to cover.** "Which knowledge domains or topics should
  this project's knowledge base cover (for example: business rules,
  architecture decisions, API contracts, deployment runbooks, a glossary of
  domain terms)?" No default — this is project-specific; if the user is
  unsure, recommend starting with whatever domains already surfaced
  elsewhere in this interview (named technologies, architecture, team
  process) and expanding later.
- **Initial seed sources.** "What existing material should seed the
  knowledge base (for example an existing README, a wiki, design docs,
  meeting notes), or is there nothing yet?" No default; "nothing yet" is a
  valid answer for a brand-new project.
- **External KBs to reference.** "Does this project already have, or use, a
  separate, already-structured knowledge base elsewhere (another OKF
  bundle, a wiki, a Confluence space) that this knowledge base should index
  and link to rather than duplicate?" No default; "none" is a valid answer.
- **Update cadence and ownership.** "How often should the knowledge base be
  updated, and who — or what process — is responsible for keeping it
  current (for example: after every completed task, weekly, 'agents update
  it automatically after each work session')?" Recommend "agents update it
  after every completed piece of work" as the default, matching this
  skill's own standing rule for generated context files.

**Output delta:** knowledge domains and initial seed sources directly
determine which concepts get pre-seeded into the knowledge base during
Phase 3, beyond the technology concepts every preset can add. External KBs
named here are recorded as index/reference concepts per
`okf-kb-guide.md`'s `## External knowledge bases`, not copied in full.
Update cadence and ownership are written into `AGENTS.md`'s
`## Project knowledge base` section as the standing instruction agents
follow afterward — by default,
read the knowledge base first and update it after every completed piece of
work. When the answer differs from that default it contradicts the verbatim
standing-rules block, so write it with the explicit override line described
in `context-file-guidelines.md` `## Standing rules block` rather than
editing the block.

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
   ready-to-ask question per item, one topic per question, with a sensible
   recommendation stated wherever one exists. Add items the presets don't
   cover only when they are clearly implied by the task type itself (for
   example, a "data engineering" task type might add "which data
   pipeline/orchestration tool, if any?").
3. **Present the full draft to the user before asking any item from it**,
   explicitly labeled as a draft, and invite the user to add, remove, or
   reword items. Do not start interviewing against a free-text checklist
   the user has not seen and confirmed.
4. **Once confirmed** (with or without edits), the checklist becomes that
   task type's working checklist and follows `## Gap rules` exactly like a
   named preset's checklist — the same gap, deferral, and
   new-technology-expansion behavior applies.
5. **Record the confirmed checklist** in the skill's final report, and in
   the project knowledge base if the task type reflects a durable, recurring
   part of the project's work, so a future run of the skill does not have
   to redraft it from scratch.

## Gap rules

A **gap** is any checklist item — from a preset above, or from a confirmed
free-text checklist — that has not yet been answered and has not been
explicitly deferred by the user. Keep asking (one gap at a time,
recommendation first, per the iron rule) until, for every task type the user
selected, no gaps remain — subject to the preview and ceiling below.

### Cost preview and question ceiling

Before asking the first checklist item, count what the selected task types
imply — the preset items plus the items technology expansion will add — and
tell the user that number. Then offer three ways forward:

1. answer them one at a time;
2. take your recommendation for every item, with corrections afterwards;
3. defer a named subset to the gap list now.

**Hard ceiling: 25 questions per run**, counting every question this skill
puts to the user, not only checklist items. On reaching it, stop and ask
whether to continue, take recommendations for what remains, or defer it.
Everything deferred at the ceiling joins the running gap list and is treated
exactly like any other deferral below.

### Technology expansion — depth 1 only

An answer that names a technology can add an item to the checklist, but only
within both of these limits:

- **Only project decisions expand.** A technology expands when the user
  chose it *as a project decision* — their answer to the framework,
  component-library, styling, state-management, design-source, tracker, or
  CI question, or a technology they volunteered in free text. A technology
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

- **Role.** "What role does <technology> play in this project (for example:
  the frontend framework, the CI runner, the primary datastore)?"

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
"not applicable"). Deferred items:

- are never silently dropped — they are recorded in the skill's final report
  to the user, listed by task type and item; and
- are also recorded in the project knowledge base (a `log.md` entry, or a
  note within the relevant concept) so a future run of the skill, or a human
  reading the knowledge base, can see what was left open and why.

Deferring is not the same as declining forever: a deferred item can be
answered later in the same session if the user brings it up, or on a future
run of the skill.
