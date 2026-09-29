# Native FreeBSD dependency profiles

The source of truth is scripts/dwm-freebsd-packages.sh. Run it with one
profile name to list packages, without installing or changing anything:

    sh scripts/dwm-freebsd-packages.sh host

| Profile | Purpose |
| --- | --- |
| build | C compiler dependencies: GNU make, pkgconf, X11/XCB, fonts, image and file-change notification libraries |
| runtime | Minimal Xorg, xterm, D-Bus and fonts |
| test | Build profile plus Python, Xvfb, xdotool, xprop, terminal and fonts |
| image | Build + runtime + Git for subsequent regular-user development |
| host | Build + Git + Python for a development checkout |

FreeBSD base supplies cc, sh, tar and core system tools. No Linux ABI packages
are used. The image builder reads the profile from its committed source snapshot;
CI reads the same helper in the VM repository. The existing image on your VM
does not change when this file changes.

## Package mapping for the supported minimal profile

| Capability | FreeBSD packages |
| --- | --- |
| Build tools | gmake, pkgconf |
| Xlib and font rendering | libX11, libXft, libXinerama, libXrender |
| XCB and resource queries | libxcb, xcb-util |
| Images and fonts | imlib2, freetype2, fontconfig |
| File change notifications | libinotify (native compatibility library) |
| X11 session | xorg, xterm |
| Session bus | dbus |
| Font coverage | noto-sans-mono, noto-emoji |
| Development checkout | git, python3 |
| Automated virtual display | xorg-vfbserver, xdotool, xprop |

To inspect package resolution without installing packages, use pkg's dry-run
mode against a current catalogue. In a FreeBSD root shell:

    packages=$(sh scripts/dwm-freebsd-packages.sh host)
    pkg install -n $packages

The helper rejects unknown profile names. Review the package transaction before
removing -n. A package catalogue refresh may be necessary on a newly provisioned
host. No packages need uninstalling from the working test VM for this cleanup.

## Full desktop still to port

| Component | Remaining platform work |
| --- | --- |
| Quickshell panel/settings | Native package/API compatibility and end-to-end QML session validation |
| Audio | Replace ALSA/PipeWire-specific helper assumptions with supported native controls |
| Networking and Bluetooth | Replace NetworkManager/BlueZ integration with reviewed FreeBSD providers |
| Power, lock and brightness | Replace logind/systemd service and device assumptions |
| Updates and system management | Replace DNF/RPM/PackageKit paths and privileged helpers |
| General installation | Native rc/session lifecycle, configuration preservation and display-manager support |

These are not advertised as supported dependencies merely because a similarly
named FreeBSD package exists. Their native interfaces must be implemented and
tested before adding a full desktop profile.

The excluded optional integrations have been removed from active helpers,
install paths, defaults and site guides. Historical release evidence and
changelog entries are retained as records, not installation instructions.
