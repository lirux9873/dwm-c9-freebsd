#!/bin/sh
# Build and native-process gate for the first FreeBSD migration milestone.
set -eu

if [ "$(uname -s)" != FreeBSD ]; then
	printf '%s\n' 'This gate requires a native FreeBSD 15.1 host.' >&2
	exit 1
fi
case $(freebsd-version -u) in
15.1-*) ;;
*) printf '%s\n' 'This gate is qualified for FreeBSD 15.1 only.' >&2; exit 1 ;;
esac

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
work=$(mktemp -d "${TMPDIR:-/tmp}/c9-core.XXXXXXXX")
cleanup() {
	# Only remove the private directory allocated above, never a caller root.
	case $work in
	*/c9-core.*) rm -rf -- "$work" ;;
	esac
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

"${CC:-cc}" -std=c99 -Wall -Wextra -Werror -I"$repo" \
	"$repo/freebsd-process.c" "$repo/tests/test-freebsd-process.c" \
	-o "$work/c9-proc-test"
"$work/c9-proc-test"

mkdir "$work/source"
for file in Makefile config.mk config.def.h dwm.c drw.c drw.h \
	util.c util.h tomlparser.c tomlparser.h freebsd-process.c freebsd-process.h; do
	cp "$repo/$file" "$work/source/$file"
done
gmake -C "$work/source" CC="${CC:-cc}" clean all
ldd "$work/source/dwm"
mkdir -p "$work/stage/usr/local/bin"
install -m 755 "$work/source/dwm" "$work/stage/usr/local/bin/dwm-c9"
cmp "$work/source/dwm" "$work/stage/usr/local/bin/dwm-c9"
printf '%s\n' 'Native process tests, clean core build and manual binary staging passed.'
printf '%s\n' 'This does not test the desktop installer or an X11 session.'
