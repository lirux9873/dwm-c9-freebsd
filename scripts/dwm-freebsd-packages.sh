#!/bin/sh
# Native FreeBSD package names. Listing a profile never installs anything.
set -eu
packages() {
    case "$1" in
    build)
        printf '%s\n' gmake pkgconf libinotify libX11 libXft libXinerama libXrender \
            libxcb xcb-util imlib2 freetype2 fontconfig
        ;;
    runtime)
        printf '%s\n' xorg xterm dbus noto-sans-mono noto-emoji
        ;;
    test)
        packages build
        printf '%s\n' python3 xorg-vfbserver xterm xdotool xprop noto-sans-mono noto-emoji
        ;;
    desktop)
        packages build
        packages runtime
        printf '%s\n' quickshell python3 bash xdotool xprop glib feh
        ;;
    image)
        packages build
        packages runtime
        printf '%s\n' git
        ;;
    host)
        packages build
        printf '%s\n' git python3
        ;;
    *) printf 'Unknown FreeBSD package profile: %s\n' "$1" >&2; return 1 ;;
    esac
}
if [ "$#" -ne 1 ]; then
    printf 'Usage: %s build|runtime|test|image|host|desktop\n' "$0" >&2
    exit 2
fi
# Capture before sorting so an invalid profile cannot be masked by a pipeline.
list=$(packages "$1")
printf '%s\n' "$list" | LC_ALL=C sort -u
