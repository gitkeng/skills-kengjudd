# Knowledge Base Log

## 2026-08-29

- **Update** of /skill-authoring/importing-skills.md alongside the import of
  `doc2markdown` (repo v0.5.0), renamed on import from the machine-local
  `~/.claude/skills/doc-to-markdown` (deferred-inventory row U1). Two new cases
  recorded: sources with no git history (record the local path and say so —
  never invent a commit or version for `metadata.upstream`) and rename on
  import (frontmatter `name` must match the new directory, sweep the skill's
  files for the old name, and warn that the original stays installed and
  competes on description-match). Import-status table: 4 of 23 imported.
- **Extension** of `doc2markdown` in the same v0.5.0 release: the import
  landed at 1.0.0 (the source has PDF/DOCX/XLSX only), then PPTX support was
  added in the working tree before the first commit — new
  `scripts/extract_pptx.py`, pptx fidelity rules (slide headings, speaker
  notes, page furniture), pptx manifest summary keys
  (`slides_needing_ocr`, `slides_with_overlay_text`, `slides_render_unavailable`,
  …), and the Thai "แปลงสไลด์"/"พาวเวอร์พอยต์" trigger words, taking the
  skill to 1.1.0. Recorded here because the changelog entry alone would hide
  that the PPTX half of this skill is new work in this repo, not part of the
  imported source.
- **Creation** of /skill-authoring/importing-skills.md alongside the first skill
  import (repo v0.4.0): `business-rules-extraction`,
  `comprehensive-codebase-analysis`, and `codebase-analysis-report` imported from
  `gitkeng/aws-kiro-atx-lab` (`.kiro/skills/`). Records what an import actually
  requires — `metadata.upstream` provenance including a dirty source working
  tree, renumbering to 1.0.0 with the upstream number preserved only in
  metadata, the two-channel `## Updating` section, re-anchoring skill-relative
  script paths that symlink installs break, replacing Kiro-specific README
  install instructions, and keeping a bundled LICENSE that a `license:` field
  refers to. Also documents the hard v2-output data contract that makes
  `codebase-analysis-report` and `comprehensive-codebase-analysis` a pair, and
  carries an import-status table for the deferred inventory in
  /decisions/2026-08-29-repo-design.md (3 of 23 imported; the other 20 rows
  stand).
- **Update** from the final review round (repo v0.3.0), per binding rule 7:
  brought /skill-authoring/update-mechanism.md, /skill-authoring/best-practices.md
  and /decisions/2026-08-29-repo-design.md back in line with the revised
  CLAUDE.md — two-channel `## Updating` contract, unconditional lockstep bump of
  the four repo-level version fields via the new `scripts/bump-version.sh`, the
  five `install.sh` user-scope targets, and corrected `--force` / unknown-tool
  script behaviour. Removed hardcoded OKF version strings so the version lives
  only in `knowledge/index.md` and /specs/okf-spec.md. Reframed the evals
  section as upstream guidance that this repo does not require, rather than an
  implied convention it does not have.
- **Update** from the expert review of `CLAUDE.md`/`AGENTS.md` (repo v0.2.0):
  documented ZCode (Z.ai) in /agents/skill-discovery-matrix.md and
  /specs/agents-md-standard.md — it reads AGENTS.md and *only* AGENTS.md, never
  `CLAUDE.md` at runtime, which makes this repo's adapter pointer load-bearing
  rather than merely acceptable; recorded its skill-discovery roots
  (`~/.zcode/skills` primary, `~/.agents/skills` secondary) and frontmatter
  limits; added `zcode` to the documented `install.sh --tool` mapping.
  Corrected the opencode claim in both /agents/skill-discovery-matrix.md and
  /specs/agent-skills-spec.md: it recognizes five of the six spec frontmatter
  fields, silently ignoring `allowed-tools`.
- **Update** after adversarial verification against live sources: corrected the
  status of anthropics/claude-code#6235 (closed "completed" 2026-08-17, docs
  still show no native AGENTS.md support) and #50778 (closed 2026-04-19, docs
  still list no `.agents/skills` path) in /specs/agents-md-standard.md and
  /decisions/2026-08-29-repo-design.md; replaced the dead Zed rules URL with
  zed.dev/docs/ai/instructions; annotated the private ACT repo source with its
  local-clone verification path; added the missing opencode source to
  /specs/agent-skills-spec.md.
- **Creation** of the knowledge bundle (OKF 0.2) during repository initialization:
  spec summaries (agent-skills, agents-md, okf, claude-code-plugins), agent skill
  discovery matrix, skill-authoring playbooks, and the founding design decision
  record. All content researched from primary sources on this date.
