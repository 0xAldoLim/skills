#!/usr/bin/env sh
set -eu

mode=${1:-all}

case "$mode" in
  all|python|apt|brew|gems|go|manual)
    printf '%s\n' "Tool installation is intentionally category-driven."
    printf '%s\n' "Open the selected ctf-*/SKILL.md Prerequisites section and install only the tools required by the active hypothesis."
    printf '%s\n' "Requested group: $mode"
    ;;
  *)
    printf '%s\n' "usage: $0 [all|python|apt|brew|gems|go|manual]" >&2
    exit 2
    ;;
esac
