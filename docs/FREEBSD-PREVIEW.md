# A visible native desktop preview

This preview uses the installed minimal FreeBSD dwm binary and Xorg tools.
It opens a welcome terminal, top system monitor and live clock/load/disk window,
with consistent dark colors, tiling shortcuts and nine workspaces. It is not
the Quickshell panel: this fork disables the original dwm bar.

From the VM console, logged in as your regular user and outside X:

    startx /bin/sh "$HOME/dwm-freebsd-preview.sh"

The preview script has been placed at that path on the development VM. For a
new checkout, use an absolute path to scripts/dwm-freebsd-preview instead.
Requires the installed /usr/local/bin/dwm from the custom ISO, xterm, xsetroot
and xprop (provided by the native Xorg profile). No new packages are needed on
the current VM. No root access is used.

Super+Enter opens a terminal; Super+M opens top; Super+J/K changes focus;
Super+H/L resizes the master area; Super+Shift+Enter promotes a window;
Super+T/F/Space selects tile/float/monocle; Super+1..9 selects a workspace.
Super+Shift+C closes a window. Super+Shift+Q exits the preview.

Configuration and application data are temporary and removed on exit. Edits to
preview settings are not retained. Shell commands still run as your normal user
and can change your files; this is configuration isolation, not a sandbox.
Your existing desktop settings and installed binaries are preserved. To return:

    startx /usr/local/bin/dwm-c9-session

## Validation

2026-09-29, base 0ad2f02, branch codex/freebsd-desktop-preview. Tested as daniel
on the FreeBSD 15.1 VM using a separate 1280x800 Xvfb display and the installed
dwm binary. All three windows appeared, workspace switching and clean logout
passed. A screenshot was captured from that display. Test log:
/tmp/c9-preview-test.log; temporary test driver: /tmp/c9-preview-test.py.
Physical VirtualBox console launch remains the owner's next check. No full
Quickshell GUI or native general installer is claimed.

Shell syntax and git diff checks passed. Codex CLI review could not start on
Windows (home-directory error); independent source review is used instead.
ShellCheck/shfmt are unavailable. No installed binaries were changed.
Independent review completed with no actionable findings.
