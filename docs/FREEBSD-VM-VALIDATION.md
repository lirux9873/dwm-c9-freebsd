# Owner-reported minimal desktop validation

Recorded 2026-09-29 from the migration conversation. This is manual
user-reported evidence, not an automated log.

Configuration: custom FreeBSD 15.1 ISO, VM, UEFI firmware, ZFS filesystem,
minimal X11/dwm profile.

The owner confirmed successful ISO creation, installation and dwm startup,
plus all requested checks:

- Super+Return opens xterm.
- Super+1 and Super+2 switch tags.
- Super+Shift+C closes the focused window.
- Super+Shift+Q exits dwm.
- After reboot, startx /usr/local/bin/dwm-c9-session works again.

Exact ISO checksum, builder commit, installed patch level, package manifest,
hypervisor version and logs were not supplied and are not inferred.

BIOS, UFS, physical hardware, swallowing, status clicks, TOML hot reload and
the full Quickshell desktop remain unverified by this report.
