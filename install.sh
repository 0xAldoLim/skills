#!/usr/bin/env sh
set -eu

script_parent=${0%/*}
[ "$script_parent" != "$0" ] || script_parent=.
repo_dir=$(CDPATH= cd -- "$script_parent" && pwd -P)
mode=link
replace=0
dry_run=0
harness=agents
custom_target=
for option in "$@"; do
    case "$option" in
        --copy) mode=copy ;;
        --replace) replace=1 ;;
        --dry-run) dry_run=1 ;;
        --harness=*) harness=${option#*=} ;;
        --target=*) custom_target=${option#*=} ;;
        --help|-h)
            printf '%s\n' 'usage: sh install.sh [--copy] [--replace] [--dry-run] [--harness=agents|claude|opencode|all] [--target=DIR]'
            printf '%s\n' 'Default: link each skill into ~/.agents/skills. --harness all installs into agents, claude and opencode discovery roots.'
            printf '%s\n' 'SKILLS_DIR overrides the destination. --copy includes docs/scripts/schemas/knowledge/prompts for standalone use.'
            exit 0 ;;
        --harness|--target)
            printf 'use %s=VALUE (the separate-argument form is ambiguous)\n' "$option" >&2
            exit 2 ;;
        *) printf 'unknown option: %s\n' "$option" >&2; exit 2 ;;
    esac
done

if [ -n "$custom_target" ]; then
    destinations=$custom_target
elif [ -n "${SKILLS_DIR:-}" ]; then
    destinations=$SKILLS_DIR
else
    case $harness in
        agents) destinations="${AGENTS_HOME:-$HOME/.agents}/skills" ;;
        claude) destinations="${CLAUDE_HOME:-$HOME/.claude}/skills" ;;
        opencode) destinations="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
        all)
            destinations="${AGENTS_HOME:-$HOME/.agents}/skills
${CLAUDE_HOME:-$HOME/.claude}/skills
${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
        *)
            printf 'unknown harness: %s (use agents, claude, opencode or all)\n' "$harness" >&2
            exit 2 ;;
    esac
fi

dest_file=$(mktemp "${TMPDIR:-/tmp}/ctf-skills-dest.XXXXXX")
trap 'rm -f "$dest_file"' 0 1 2 15
printf '%s\n' "$destinations" > "$dest_file"
if ! grep -q '[^[:space:]]' "$dest_file"; then
    printf '%s\n' 'no destination selected' >&2
    exit 2
fi

# Validate every destination before any mutation. A failed second destination
# must not leave the first partially installed.
while IFS= read -r destination; do
    [ -n "$destination" ] || continue
    resolved=$(realpath -m -- "$destination" 2>/dev/null || printf '%s' "$destination")
    case "$resolved" in
        "$repo_dir"|"$repo_dir/"|"$repo_dir/"*) printf 'destination must be outside the source checkout: %s\n' "$destination" >&2; exit 2 ;;
    esac
    for skill_file in "$repo_dir"/*/SKILL.md; do
        skill_dir=${skill_file%/*}
        target="$destination/${skill_dir##*/}"
        if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ] && [ "$mode" = link ]; then continue; fi
        if { [ -e "$target" ] || [ -L "$target" ]; } && [ "$replace" != 1 ]; then
            printf 'existing skill preserved: %s; use --replace for a recoverable backup\n' "$target" >&2
            exit 1
        fi
    done
    if [ "$mode" = copy ]; then
        for shared in docs scripts schemas knowledge prompts; do
            if { [ -e "$destination/$shared" ] || [ -L "$destination/$shared" ]; } && [ "$replace" != 1 ]; then
                printf 'existing shared directory preserved: %s; use --replace for a recoverable backup\n' "$destination/$shared" >&2
                exit 1
            fi
        done
    fi
done < "$dest_file"

if [ "$dry_run" = 1 ]; then
    printf 'would install skills via %s into:\n' "$mode"
    while IFS= read -r destination; do [ -n "$destination" ] || continue; printf '  %s\n' "$destination"; done < "$dest_file"
    exit 0
fi

while IFS= read -r destination; do
    [ -n "$destination" ] || continue
    mkdir -p "$destination"
    backup_dir="${destination%/}.ctf-backup-$$"
    for skill_file in "$repo_dir"/*/SKILL.md; do
        skill_dir=${skill_file%/*}
        skill_name=${skill_dir##*/}
        target="$destination/$skill_name"
        if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ] && [ "$mode" = link ]; then
            printf 'current %s at %s\n' "$skill_name" "$destination"
            continue
        fi
        if [ -e "$target" ] || [ -L "$target" ]; then
            mkdir -p "$backup_dir"
            mv -- "$target" "$backup_dir/"
        fi
        if [ "$mode" = copy ]; then cp -R -- "$skill_dir" "$destination/"; else ln -s -- "$skill_dir" "$target"; fi
    done
    if [ "$mode" = copy ]; then
        for shared in docs scripts schemas knowledge prompts; do
            [ -d "$repo_dir/$shared" ] || continue
            if [ -e "$destination/$shared" ] || [ -L "$destination/$shared" ]; then
                mkdir -p "$backup_dir"
                mv -- "$destination/$shared" "$backup_dir/"
            fi
            cp -R -- "$repo_dir/$shared" "$destination/"
        done
    fi
    printf 'installed into %s\n' "$destination"
done < "$dest_file"
printf 'CTF skills ready. Never auto-push. Verify with: python3 <bundle>/scripts/validate_skills.py\n'
