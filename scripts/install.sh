#!/usr/bin/env bash
# Install skills-kengjudd skills into an agent's skill directory via symlinks.
#
# Usage:
#   ./scripts/install.sh --tool <claude|codex|cursor|opencode|gemini|zed|goose|kimi|amp|kiro|zcode|all> [--project <dir>] [--force]
#
# Default scope is user-level (home directory). Pass --project <dir> to link into
# that project's skill directories instead.
#
# Target directory per tool (user scope), based on each agent's documented
# discovery paths (see knowledge/agents/skill-discovery-matrix.md):
#   claude                              -> ~/.claude/skills
#   codex|cursor|opencode|gemini|zed|goose -> ~/.agents/skills   (universal convention)
#   kimi|amp                            -> ~/.config/agents/skills
#   kiro                                -> ~/.kiro/skills
#   zcode                               -> ~/.zcode/skills       (ZCode's highest-precedence root)
#   all                                 -> all five directories above
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

TOOL=""
PROJECT_DIR=""
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)    TOOL="$2"; shift 2 ;;
    --project) PROJECT_DIR="$2"; shift 2 ;;
    --force)   FORCE=1; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$TOOL" ]]; then
  echo "Error: --tool is required. See --help." >&2
  exit 1
fi

targets_for_tool() {
  local base_claude base_agents base_config_agents base_kiro base_zcode
  if [[ -n "$PROJECT_DIR" ]]; then
    base_claude="$PROJECT_DIR/.claude/skills"
    base_agents="$PROJECT_DIR/.agents/skills"
    base_config_agents="$PROJECT_DIR/.agents/skills"
    base_kiro="$PROJECT_DIR/.kiro/skills"
    base_zcode="$PROJECT_DIR/.zcode/skills"
  else
    base_claude="$HOME/.claude/skills"
    base_agents="$HOME/.agents/skills"
    base_config_agents="$HOME/.config/agents/skills"
    base_kiro="$HOME/.kiro/skills"
    base_zcode="$HOME/.zcode/skills"
  fi
  case "$1" in
    claude) echo "$base_claude" ;;
    codex|cursor|opencode|gemini|zed|goose) echo "$base_agents" ;;
    kimi|amp) echo "$base_config_agents" ;;
    kiro) echo "$base_kiro" ;;
    zcode) echo "$base_zcode" ;;
    all) printf '%s\n' "$base_claude" "$base_agents" "$base_config_agents" "$base_kiro" "$base_zcode" | sort -u ;;
    *) echo "Error: unknown tool '$1'" >&2; exit 1 ;;
  esac
}

linked=0 skipped=0
while IFS= read -r target_dir; do
  mkdir -p "$target_dir"
  for skill_path in "$SKILLS_DIR"/*/; do
    skill_name="$(basename "$skill_path")"
    link="$target_dir/$skill_name"
    src="$SKILLS_DIR/$skill_name"
    if [[ -L "$link" && "$(readlink "$link")" == "$src" ]]; then
      skipped=$((skipped + 1))
      continue
    fi
    if [[ -e "$link" || -L "$link" ]]; then
      if [[ "$FORCE" -eq 1 ]]; then
        rm -rf "$link"
      else
        echo "SKIP  $link already exists (not ours). Use --force to replace." >&2
        skipped=$((skipped + 1))
        continue
      fi
    fi
    ln -s "$src" "$link"
    echo "LINK  $link -> $src"
    linked=$((linked + 1))
  done
done < <(targets_for_tool "$TOOL")

echo "Done: $linked linked, $skipped skipped."
echo "Reminder: restart or reload your agent session so newly linked skills are discovered."
