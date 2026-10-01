#!/usr/bin/env sh
set -eu

script_parent=${0%/*}
[ "$script_parent" != "$0" ] || script_parent=.
repo_dir=$(CDPATH= cd -- "$script_parent" && pwd -P)
skills_dir=${SKILLS_DIR:-"${AGENTS_HOME:-$HOME/.agents}/skills"}
mode=link
replace=0
dry_run=0
for option in "$@"; do
    case "$option" in
        --copy) mode=copy ;;
        --replace) replace=1 ;;
        --dry-run) dry_run=1 ;;
        --help|-h) printf '%s\n' 'usage: sh install.sh [--copy] [--replace] [--dry-run]' 'Default: link each skill to this complete checkout. --replace backs up existing directories/links.'; exit 0 ;;
        *) printf 'unknown option: %s\n' "$option" >&2; exit 2 ;;
    esac
done
# Inspect the complete plan before any mutation; conflicts cannot leave a partial install.
resolved_destination=$(realpath -m -- "$skills_dir")
case "$resolved_destination" in
    "$repo_dir"|"$repo_dir/"|"$repo_dir/"*) printf '%s\n' 'destination must be outside the source checkout' >&2; exit 2 ;;
esac
for skill_file in "$repo_dir"/*/SKILL.md; do
    skill_dir=${skill_file%/*}
    target="$skills_dir/${skill_dir##*/}"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ] && [ "$mode" = link ]; then continue; fi
    if { [ -e "$target" ] || [ -L "$target" ]; } && [ "$replace" != 1 ]; then
        printf 'existing skill preserved: %s; use --replace for a recoverable backup\n' "$target" >&2; exit 1
    fi
done
if [ "$mode" = copy ]; then
    for shared in docs scripts schemas knowledge prompts; do
        if { [ -e "$skills_dir/$shared" ] || [ -L "$skills_dir/$shared" ]; } && [ "$replace" != 1 ]; then
            printf 'existing shared directory preserved: %s\n' "$skills_dir/$shared" >&2; exit 1
        fi
    done
fi
if [ "$dry_run" = 1 ]; then
    printf 'would install skills via %s into %s\n' "$mode" "$skills_dir"
    exit 0
fi
mkdir -p "$skills_dir"
backup_dir="${skills_dir%/}.ctf-backup-$$"
set --
for skill_file in "$repo_dir"/*/SKILL.md; do
    skill_dir=${skill_file%/*}
    target="$skills_dir/${skill_dir##*/}"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ] && [ "$mode" = link ]; then continue; fi
    if [ -e "$target" ] || [ -L "$target" ]; then set -- "$@" "$target"; fi
done
if [ "$mode" = copy ]; then
    for shared in docs scripts schemas knowledge prompts; do
        if [ -e "$skills_dir/$shared" ] || [ -L "$skills_dir/$shared" ]; then set -- "$@" "$skills_dir/$shared"; fi
    done
fi
if [ "$#" -gt 0 ]; then
    mkdir -p "$backup_dir"
    mv -- "$@" "$backup_dir/"
fi
set --
for skill_file in "$repo_dir"/*/SKILL.md; do
    skill_dir=${skill_file%/*}
    skill_name=${skill_dir##*/}
    target="$skills_dir/$skill_name"
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$skill_dir" ] && [ "$mode" = link ]; then
        printf 'current %s\n' "$skill_name"
        continue
    fi
    set -- "$@" "$skill_dir"
done
if [ "$mode" = copy ]; then
    for shared in docs scripts schemas knowledge prompts; do
        [ -d "$repo_dir/$shared" ] || continue
        set -- "$@" "$repo_dir/$shared"
    done
fi
if [ "$#" -gt 0 ]; then
    if [ "$mode" = copy ]; then cp -R -- "$@" "$skills_dir/"; else ln -s -- "$@" "$skills_dir/"; fi
fi
printf 'Complete skill bundle installed at %s. Never auto-push.\n' "$skills_dir"
