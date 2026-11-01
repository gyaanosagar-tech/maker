#!/usr/bin/env bash
# Install the skills maker depends on, at pinned SHAs.
# They are NOT vendored into maker: openmontage is AGPLv3 and would relicense
# the whole repo. Clone at runtime, call by subprocess, ship nothing.
set -euo pipefail
SK=${SKILLS_DIR:-$PWD/skills}
mkdir -p "$SK"

clone_at () {  # url dir sha
  local url=$1 dir=$2 sha=$3
  if [ -d "$SK/$dir" ]; then
    # already present (vendored in this repo, or restored from cache)
    if git -C "$SK/$dir" rev-parse --git-dir >/dev/null 2>&1; then
      git -C "$SK/$dir" fetch -q origin >/dev/null 2>&1 || true
      git -C "$SK/$dir" checkout -q "$sha" 2>/dev/null || true
    fi
    echo "  $dir present (reusing)"
    return 0
  fi
  git clone -q "$url" "$SK/$dir"
  git -C "$SK/$dir" fetch -q --depth 1 origin "$sha" 2>/dev/null || git -C "$SK/$dir" fetch -q origin
  git -C "$SK/$dir" checkout -q "$sha"
  echo "  $dir @ ${sha:0:8}"
}

echo "== skills =="
clone_at https://github.com/Leonxlnx/earshot.git                 earshot      "${EARSHOT_SHA:-main}"
echo "  (hyperframes + openmontage installed only when a job needs them)"
