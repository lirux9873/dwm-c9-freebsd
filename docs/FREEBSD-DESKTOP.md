# Native FreeBSD Quickshell desktop

The native desktop is now runnable on FreeBSD 15.1 amd64/X11. It reuses the
project's Quickshell launcher, workspace model, notifications and tray, with
a FreeBSD entry point and native system provider. It does not start the Fedora
NetworkManager, BlueZ, PipeWire, systemd or package-management helpers.

## Start it on our VM

It is already installed as daniel. From the VirtualBox console, outside an
existing X session, run:

    startx "$HOME/.local/share/dwm-c9-freebsd/start-session"

The panel has an Apps button, nine workspaces, active-window title, notification
history, System controls and clock. Super+D opens the searchable application
launcher; Super+Enter opens a terminal; Super+S opens System; Super+N opens
notifications. Super+1..9 changes workspace. Super+Shift+Q logs out.

The previous desktop remains available:

    startx /usr/local/bin/dwm-c9-session

## Install from a checkout

As root, install the native profile (review the transaction first):

    packages=$(sh scripts/dwm-freebsd-packages.sh desktop)
    pkg install $packages

Then, as your regular user:

    python3 scripts/install-freebsd-desktop.py

This builds dwm and installs versioned releases beneath
~/.local/share/dwm-c9-freebsd. No root access is used by the installer.
It preserves existing native TOML settings and leaves ~/.config and the
system-installed desktop alone. The managed Quickshell tree is replaced by
each release. Do not edit generated release files; edit source and reinstall.
Log out before updating. Re-run the installer to update from your checkout.

To restore the previous binaries and shell after an update:

    python3 scripts/install-freebsd-desktop.py --rollback

Rollback preserves current user settings. It does not roll back pkg packages.
To stop using this installation, choose the original session above; no system
services or display-manager configuration need reverting.

## What works and what remains

| Feature | Native profile |
| --- | --- |
| Panel/workspaces/window title | Tested with real dwm and Quickshell on Xvfb |
| Application search and launch | Tested using installed desktop entries |
| Notifications and history | D-Bus delivery and history tested |
| Tray | Included; individual third-party tray apps not qualified |
| Volume and mute | Native FreeBSD mixer controls; availability depends on device permissions |
| Network | Read-only IPv4 interface status; no Wi-Fi editor |
| Battery and load | Native sysctl/load data; unavailable battery is reported explicitly |
| Bluetooth, brightness, suspend, lock | Not included in this profile |
| Full inherited Settings / package updates | Not included; no privileged Fedora helpers run |

The Quickshell package is quickshell-0.3.0_1 on the test VM. Qt Quick defaults
to software rendering for VirtualBox/Xvfb; QT_QUICK_BACKEND can override it.
The current panel targets one screen. Physical GPU, multimonitor, audible audio
output and laptop power hardware still require device testing.

## Troubleshooting and validation

Session log: ~/.local/share/dwm-c9-freebsd/logs/session.log.
The session refuses an already managed X display; log out before starting it.
It uses a private runtime directory and a session D-Bus when none is present.
The graphical shell and dwm stop together on logout or shell failure.

See [native validation evidence](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-QUICKSHELL-REVIEW.md).
