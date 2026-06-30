#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_dir="$repo_root/skills/easy-boss"
target_dir="${CODEX_HOME:-$HOME/.codex}/skills/easy-boss"

if [[ ! -d "$source_dir" ]]; then
  echo "Skill source not found: $source_dir" >&2
  exit 1
fi

mkdir -p "$(dirname "$target_dir")"
rm -rf "$target_dir"
cp -R "$source_dir" "$target_dir"

echo "Installed Easy Boss to: $target_dir"
echo 'Restart Codex or open a new conversation, then use: $easy-boss'
