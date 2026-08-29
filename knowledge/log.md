# Knowledge Base Log

## 2026-08-29

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
