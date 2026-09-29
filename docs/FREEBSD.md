# dwm-c9-freebsd: FreeBSD 15.1 migration

Repository: [lirux9873/dwm-c9-freebsd](https://github.com/lirux9873/dwm-c9-freebsd).
Initial baseline: `e5bbddc0c7261951d351d9a7c502a9952fc0b624`.
Target: FreeBSD 15.1-RELEASE amd64, X11, native applications.

This is a port in progress. The first change set addresses the C window manager
and its build dependencies. The inherited full desktop installer, session
helpers, QML system providers and Fedora image pipeline are not a FreeBSD port.
Do not run `install.sh`, `gmake install`, or `scripts/dev-sync-install.sh` to
install this snapshot on FreeBSD. `gmake install` now refuses that platform.

## Implemented in the first change set

- GNU make detects FreeBSD and links the native `libinotify` package, keeping
  BSD process declarations visible. Local dependencies use `LOCALBASE`, which
  defaults to `/usr/local`, independently of the installation `PREFIX`.
- `getparentprocess()` uses `KERN_PROC_PID` through `sysctl` on FreeBSD.
- XCB RES local-client PID discovery is enabled on FreeBSD. Combined with the
  parent-process query, this supplies the missing native pieces for swallowing;
  actual Xorg support and runtime behavior still need testing.
- Executable discovery uses `KERN_PROC_PATHNAME` instead of `/proc/self/exe`.
- Status-process discovery uses base `pgrep`, then validates native process
  identity and user, accepting either dwm's session or its recorded autostart
  session. It does not parse Linux procfs.
- Application spawning uses a valid PID result pointer and reports failures.
- A native test gate exercises process ancestry, session separation, missing
  processes, executable paths, buffer limits, a clean core build and manual
  binary staging. It does not modify a live desktop.

`libinotify` is a native compatibility library backed by FreeBSD event facilities,
not a Linux binary dependency. A future kqueue implementation is optional;
matching save/rename hot-reload behavior must be tested either way.

## Prepare a FreeBSD test host

For the complete sequence, including completed steps, Windows SSH access and
the next regular-user test, follow [Test VM setup](https://lirux9873.github.io/dwm-c9-freebsd/test-host.html).
Our current custom-ISO VM already has the build dependencies and Git installed;
its SSH key access is verified. Continue with the regular-user checkout and
core gate rather than reinstalling the VM.

For experimental installation media with a minimal native X11/dwm session, see
[the FreeBSD image builders](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-IMAGES.md).
These builders require a disposable FreeBSD VM. Owner-reported UEFI/ZFS
installation tests pass; full release qualification remains pending. They do
not use the inherited Fedora installer.

Install a FreeBSD 15.1 VM or machine before treating this as a usable desktop.
As root, install the build dependencies:

```sh
pkg install git gmake pkgconf libinotify \
  libX11 libXft libXinerama libXrender libxcb xcb-util \
  imlib2 freetype2 fontconfig
```

Base `cc` supplies Clang. Query the target repository if any package is missing;
do not force packages for another FreeBSD ABI. Package definitions were checked
against the official [FreeBSD ports index](https://download.freebsd.org/ports/index/).
Install Xorg, the appropriate GPU driver and an X11 terminal separately for
runtime validation; see the [FreeBSD X11 handbook](https://docs.freebsd.org/en/books/handbook/x11/).

As the regular user:

```sh
git clone https://github.com/lirux9873/dwm-c9-freebsd.git
cd dwm-c9-freebsd
sh tests/test-freebsd-core.sh
```

The default branch contains the port. Save the test output and `freebsd-version -kru` when reporting results. The gate builds in a
private temporary directory and cleans that directory on exit.

For an inspectable local build:

```sh
gmake CC=cc clean all
ldd ./dwm
```

The Makefile creates `config.h` only if it is absent. This produces a binary;
it does not install a native desktop or provide a complete session. For the
initial X11 trial, use isolated XDG configuration/data directories and native
hotkeys from the earlier installation guide. Do not copy the inherited
autostart scripts into those data directories. Do not install the inherited
`dwm-session-launch` helper yet; it still contains GNU `stat` and updater
assumptions. With no adjacent launcher helper, dwm launches applications directly.

## Remaining migration work

1. Finish core runtime validation: swallowing, status clicks, focus and
   hot-reload saves/renames. Native build/process/basic X11 tests already pass.
2. Extend the shared native package profiles as additional desktop components
   are ported. The minimal image and CI now share a profile helper; see
   [native dependencies](https://lirux9873.github.io/dwm-c9-freebsd/dependencies.html).
3. Supply native startup/shutdown, config-preserving installation, fonts and
   desktop-file paths; remove the active Linux-specific service lifecycle.
4. Adapt the Quickshell providers for audio, networking, Bluetooth, brightness,
   power, input and display hotplug. Native package availability does not imply
   compatible service APIs.
5. Replace package updates, privilege helpers and recovery with FreeBSD-aware
   operations. Keep automatic updates inactive until that design is validated.
6. Replace inherited CI/release/image workflows and finish branding and docs.

The previously removed optional applications are outside this fork's target
scope. Their integrations have been removed from active helpers, defaults,
install paths and site guides. Historical release records are retained.

## Validation status

The owner reports successful custom ISO creation, UEFI/ZFS VM installation,
terminal/tag/close/logout checks and dwm startup after reboot. See
[manual VM evidence](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-VM-VALIDATION.md).
This validates the minimal session, not the complete desktop.


The `Desktop smoke` Actions job now boots a FreeBSD 15.1 amd64 VM with the
pinned `vmactions/freebsd-vm` action. GitHub's Ubuntu host only orchestrates the
VM; package installation uses `pkg`, and compilation and tests run inside
FreeBSD. The job runs on pull requests, pushes to main and manual dispatch.

The VM creates an unprivileged `dwmci` user, runs the native process/build gate,
then exercises dwm in Xvfb: terminal spawning through a hotkey, tag changes,
closing a client and clean logout. It uses isolated configuration with no
inherited autostart helpers. This replaces the Fedora-specific managed-shell
smoke, not the still-pending Quickshell or physical-hardware qualification.
To reproduce the X11 gate locally, install `python3 xorg-vfbserver xterm xdotool
xprop noto-sans-mono noto-emoji` in addition to the build dependencies, then run
`env DWM_FREEBSD_X11_SMOKE=1 sh tests/test-freebsd-core.sh` as a regular user.

The authoring host is Windows; native validation is now available through CI.
[Run 36231369609](https://github.com/lirux9873/dwm-c9-freebsd/actions/runs/36231369609)
passed on FreeBSD 15.1-RELEASE-p3 amd64: package installation, native process
tests, clean build, manual binary staging and basic X11 smoke. See
[the CI evidence](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-CI-REVIEW.md) for the exact tested commit and limits.
Swallowing end-to-end, status clicks, save/rename hot reloads, the full Quickshell
session, physical GPU drivers and audio remain unverified. The inherited full
Fedora regression suite has not been run for this change.

Native API references:

- [FreeBSD 15.1 process structures](https://github.com/freebsd/freebsd-src/blob/releng/15.1/sys/sys/user.h)
- [FreeBSD 15.1 process sysctl implementation](https://github.com/freebsd/freebsd-src/blob/releng/15.1/sys/kern/kern_proc.c)
- [FreeBSD libinotify port](https://cgit.freebsd.org/ports/tree/devel/libinotify)
