#!/bin/sh
# The Python builder shares checksum, manifest and publication handling.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/build-dwm-freebsd-system-image.py" --installer "$@"
