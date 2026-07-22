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

# Append-only compatibility layer: copy category references, generated indexes,
# learned entries, and Codex UI metadata without deleting local-only files.
for skill_dir in "$REPO_DIR"/*; do
    [ -d "$skill_dir" ] || continue
    [ -f "$skill_dir/SKILL.md" ] || continue

    skill_name=$(basename "$skill_dir")
    target_dir="$SKILLS_DIR/$skill_name"
    cp -R "$skill_dir"/. "$target_dir"/
done

printf 'supporting references and invocation metadata installed\n'
