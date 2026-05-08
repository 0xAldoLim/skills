#!/usr/bin/env sh
set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
AGENTS_HOME=${AGENTS_HOME:-"$HOME/.agents"}
SKILLS_DIR=${SKILLS_DIR:-"$AGENTS_HOME/skills"}

mkdir -p "$SKILLS_DIR"

for skill_file in "$REPO_DIR"/*/SKILL.md; do
    [ -f "$skill_file" ] || continue

    skill_name=$(basename "$(dirname "$skill_file")")
    target_dir="$SKILLS_DIR/$skill_name"

    mkdir -p "$target_dir"
    cp "$skill_file" "$target_dir/SKILL.md"
    printf 'installed %s\n' "$skill_name"
done

printf 'skills installed to %s\n' "$SKILLS_DIR"
