#!/usr/bin/env sh
set -eu

bundle_scripts=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$bundle_scripts/install_tools.py" "$@"
