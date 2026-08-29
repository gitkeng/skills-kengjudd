#!/usr/bin/env bash
# Per-skill updater for skills-kengjudd.
#
# Usage:
#   ./scripts/update.sh <skill-name>     # update check for one skill
#   ./scripts/update.sh --all            # update check for every skill
#   ./scripts/update.sh <skill-name> -y  # skip the confirmation prompt
#
# Flow (adapted from the ACT act-update pattern):
#   1. Verify this is a git clone on branch main with a clean working tree.
#   2. git fetch origin main.
#   3. Compare the skill's local metadata.version against origin/main.
#   4. Show the skill's pending commits (changelog delta) and ask for confirmation.
#   5. git pull, then print reload reminders.
#
# Note: git pull updates the whole repository (all skills share one clone);
# the per-skill version comparison determines whether THIS skill has changes.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

SKILL=""
ALL=0
YES=0
for arg in "$@"; do
  case "$arg" in
    --all) ALL=1 ;;
    -y|--yes) YES=1 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) SKILL="$arg" ;;
  esac
done

if [[ "$ALL" -eq 0 && -z "$SKILL" ]]; then
  echo "Error: pass a skill name or --all. See --help." >&2
  exit 1
fi

if [[ ! -d .git ]]; then
  echo "Error: $REPO_ROOT is not a git clone. Clone it first:" >&2
  echo "  git clone git@github.com:gitkeng/skills-kengjudd.git" >&2
  exit 1
fi

branch="$(git branch --show-current)"
if [[ "$branch" != "main" ]]; then
  echo "Error: on branch '$branch', expected 'main'. Switch back before updating." >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Error: working tree is not clean. Commit or stash changes before updating." >&2
  exit 1
fi

echo "Fetching origin/main..."
git fetch origin main --quiet

# Extract metadata.version from a SKILL.md given as stdin.
skill_version() {
  sed -n '/^metadata:/,/^[a-z]/p' | grep -m1 'version:' | sed 's/.*version:[[:space:]]*"\{0,1\}//; s/"\{0,1\}[[:space:]]*$//' || true
}

check_one() {
  local name="$1"
  local skill_md="skills/$name/SKILL.md"
  if [[ ! -f "$skill_md" ]]; then
    echo "Error: skill '$name' not found at $skill_md" >&2
    return 1
  fi
  local local_v remote_v
  local_v="$(skill_version < "$skill_md")"
  remote_v="$(git show "origin/main:$skill_md" 2>/dev/null | skill_version)"
  if [[ -z "$remote_v" ]]; then
    echo "$name: not present on origin/main (local-only skill, nothing to update)."
    return 0
  fi
  if [[ "$local_v" == "$remote_v" ]]; then
    echo "$name: up to date (version $local_v)."
    return 0
  fi
  echo "$name: update available — local $local_v -> remote $remote_v"
  echo "Pending changes for this skill:"
  git log --oneline HEAD..origin/main -- "skills/$name/" | sed 's/^/  /'
  NEEDS_PULL=1
}

NEEDS_PULL=0
if [[ "$ALL" -eq 1 ]]; then
  for skill_path in skills/*/; do
    check_one "$(basename "$skill_path")"
  done
else
  check_one "$SKILL"
fi

if [[ "$NEEDS_PULL" -eq 0 ]]; then
  exit 0
fi

if [[ "$YES" -ne 1 ]]; then
  printf 'Pull updates now? (git pull updates the whole repo) [y/N] '
  read -r answer
  [[ "$answer" == "y" || "$answer" == "Y" ]] || { echo "Aborted."; exit 0; }
fi

git pull origin main
echo ""
echo "Updated. Reload reminders:"
echo "  - Claude Code: start a new session (symlinked SKILL.md edits load on next use)."
echo "  - Claude Code plugin install: run 'claude plugin update skills-kengjudd@kengjudd'."
echo "  - Codex: run /skills to refresh. Other agents: restart the session."
