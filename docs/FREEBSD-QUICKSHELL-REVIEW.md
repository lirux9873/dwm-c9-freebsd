# Native Quickshell validation

2026-09-29. Base 48f34eb; branch codex/freebsd-quickshell-desktop.
FreeBSD 15.1-RELEASE amd64, quickshell-0.3.0_1, Qt 6.11.1, unprivileged daniel.
Source/test workspace: /tmp/c9-quickshell.dB1tuNMd/source.
Final installed prefix: /home/daniel/.local/share/dwm-c9-freebsd.

## Architecture and results

The native entry point reuses core, state, launcher, notifications and panel
components. Linux-only service models are not imported by this entry point.
Native provider uses mixer, ifconfig, sysctl and getloadavg without privilege
escalation. Desktop packages were checked against the VM's pkg catalogue.

The source built successfully, with two pre-existing strict-prototype warnings.
`tests/test-freebsd-installer.py` passed real installation, repeat installation,
custom TOML and dangling-symlink preservation, rollback and unmanaged-directory
refusal. Independent review found the dangling-symlink issue; it was corrected
with lexists and covered before deployment. Final source review was clean.

`dbus-run-session -- python3 tests/test-freebsd-quickshell.py PREFIX` passed
against both a temporary installation and the final installed user prefix:
workspace hotkey/state, indexed app search and launch, native controls window,
terminal, active title, panel reservation, notification delivery/history and
clean logout. Actual app windows were launched in a separate Xvfb display.
The final five-second idle sample increased Quickshell CPU time from 0:00.89
to 0:00.90 (about 0.2% of one CPU); this is a measurement, not a test threshold.
Screenshots were captured and visually checked. Native mixer snapshot reported
volume 75%; setting that same volume succeeded and retained it.

A missing _NET_WM_NAME exposed a shared title-fallback bug, fixed to accept only
actual property values before falling back to WM_NAME. Native window-list
properties also use the X11 window-id representation. Event-driven xprop
watching remains in place; controls sample only while open.

## Lint and limits

Native qmllint uses /usr/local/lib/qt6/qml and generated qs module maps. Fixed
relative symlink targets and GNU-only import extraction in the lint helper.
Two type-metadata warnings remain: PanelWindow marked uncreatable and unresolved
QProcess::ExitStatus. Both types execute in the passing real Quickshell test;
no clean static-lint claim is made. Log: /tmp/c9-quickshell.dB1tuNMd/qmllint-final.log.
Session log: PREFIX/logs/session.log. A nonfatal FileView warning occurred.
Xterm XIO messages occur when the test X server shuts down after logout.

Built-in Codex CLI review cannot locate its home directory on Windows;
independent source review was used. ShellCheck/shfmt unavailable.
The owner subsequently confirmed the VirtualBox console session works.
Third-party tray apps, audible sound,
laptop power devices and multiple monitors are not validated. No fresh ISO,
Linux runtime suite, privileged updater or full inherited Settings was tested.

Additional gates passed: package profiles (2), session boundaries (4), image
builder tests (7), full launcher helper regression, changed shell syntax and
git diff checks. Astro check: 19 files, zero diagnostics; build: 15 pages.
Final review tightened the active-title test to require successful IPC and the
expected xterm title; the installed-desktop test passed again.
