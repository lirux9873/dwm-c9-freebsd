# dwm-c9-freebsd

A native FreeBSD 15.1 amd64/X11 port of the dwm-titus desktop. The minimal
window-manager session and a native Quickshell profile now run on FreeBSD.
[Start the graphical desktop](docs/FREEBSD-DESKTOP.md); hardware-specific services
and the full inherited Settings application remain outside this profile.

- [Documentation](https://lirux9873.github.io/dwm-c9-freebsd/)
- [Try the visible desktop preview](docs/FREEBSD-PREVIEW.md)
- [Test VM setup](docs/FREEBSD-TEST-HOST.md)
- [Native package profiles](docs/FREEBSD-DEPENDENCIES.md)
- [Image builders](docs/FREEBSD-IMAGES.md)
- [Roadmap](ROADMAP.md) and [active tasks](TASKS.md)

## Current validation

Native process tests, clean builds and basic X11 tests pass. The owner has
installed our custom ISO in a UEFI/ZFS VirtualBox VM and verified terminal
launch, tag switching, window closing, logout and startup after reboot.
See [the validation record](docs/FREEBSD-VM-VALIDATION.md).

## Build and test

Use the commands in the test-host guide as a regular user. Package
administration runs separately as root. The POSIX package profile helper lists
native package names and never installs anything by itself.

Do not run the inherited install.sh, gmake install or source synchronization
installer on FreeBSD. Use scripts/install-freebsd-desktop.py for the separate user installation.
Privileged system management and updates remain migration work.

## Configuration and migration

Existing user configuration and installed applications are not removed by this
source cleanup. Newly generated native images use the reduced minimal package
profile. The default hotkeys no longer include the removed gaming shortcut;
existing installations need a reviewed configuration migration later.

The config directory retains the inherited full-desktop configuration as
porting input. Its presence does not mean that Linux service helpers are
supported on FreeBSD. Historical Fedora builders remain reference code and
must not be used as FreeBSD installers.

## Attribution

Based on [ChrisTitusTech/dwm-titus](https://github.com/ChrisTitusTech/dwm-titus)
and [suckless dwm](https://dwm.suckless.org/). See LICENSE for terms and
CHANGELOG.md for the recorded project history.
