# Experimental FreeBSD 15.1 image builders

These builders target **FreeBSD 15.1-RELEASE amd64**, with a minimal native Xorg,
dwm, xterm and D-Bus session. They do not include the separately installed native Quickshell desktop,
Linux service helpers, optional application stores or gaming integrations.
They are development tools, not qualified release images.

## How the two builders fit together

`scripts/build-dwm-freebsd-system-image.py` starts with an official `base.txz`,
installs native packages in a temporary chroot, compiles the committed dwm
checkout and produces a customized base filesystem `.tar.xz` with a JSON
manifest. It is not a bootable disk image: the installer supplies the kernel,
partitions, bootloader, network configuration, passwords and users.

`scripts/build-dwm-freebsd-installer-iso.sh` adds the customized base distribution
to the matching official disc1 ISO, refreshes its installer manifest, and rebuilds
the ISO with FreeBSD's `release/amd64/mkisoimages.sh`. That upstream tool prepares
BIOS and UEFI boot structures. Bootability still requires testing both firmware
paths. The standard interactive FreeBSD installer is retained; there is no
automatic disk selection or partition erasure script.

## Builder requirements

Use a **disposable FreeBSD 15.1 amd64 VM**, with root access, Internet access,
and at least 30 GB free workspace. The privileged chroot is not a security
sandbox. Package installation scripts execute there. Never run this on your
daily desktop. No host disk device is selected or formatted by these builders.

Install host tools:

```sh
pkg install python3 git
git clone -b releng/15.1 --depth 1 https://git.FreeBSD.org/src.git /usr/src
git clone https://github.com/lirux9873/dwm-c9-freebsd.git
cd dwm-c9-freebsd
```

The ISO builder requires the complete matching source tree, because
`mkisoimages.sh` sources other release/boot helper files. FreeBSD base supplies
`tar`, `makefs`, `mkimg`, `etdump`, `mount`, `umount`, `chroot` and the compiler.

Download the official FreeBSD 15.1 amd64 **disc1 ISO**, its CHECKSUM.SHA256 file,
and the matching `base.txz` and `kernel.txz` with their distribution MANIFEST. Use the
[official download page](https://www.freebsd.org/where/) and
[FreeBSD verification instructions](https://docs.freebsd.org/en/books/handbook/bsdinstall/).
Supply the exact trusted SHA256 values below. A hash you compute from an
untrusted download is not source authentication.

## Build the base filesystem

Run as root in the disposable VM. Replace the placeholders with real paths
and checksum values; the output and its adjacent `.json` must not exist.

```sh
python3 scripts/build-dwm-freebsd-system-image.py \
  --disposable-vm \
  --input /build/base.txz \
  --sha256 BASE_TXZ_SHA256_FROM_OFFICIAL_MANIFEST \
  --output /build/dwm-freebsd-15.1.tar.xz
```

Only `git archive HEAD` is compiled: commit intentional source changes first.
Untracked files, credentials, local configuration and uncommitted edits are not
copied from the checkout. The output manifest records the commit, installed
package versions, source checksum and final artifact checksum. Package
repositories can change, so builds are not claimed to be byte-reproducible.

## Build the installer ISO

FreeBSD 15.1 disc1 normally carries pkgbase packages, not the legacy base/kernel
archives. The builder uses the checksums in the ISO's distribution MANIFEST to
verify the existing system image's original base and the supplied kernel:

```sh
fetch -o /build/kernel.txz https://download.freebsd.org/releases/amd64/15.1-RELEASE/kernel.txz
```

```sh
sh scripts/build-dwm-freebsd-installer-iso.sh \
  --disposable-vm \
  --input /build/FreeBSD-15.1-RELEASE-amd64-disc1.iso \
  --sha256 DISC1_SHA256_FROM_OFFICIAL_CHECKSUM_FILE \
  --system-image /build/dwm-freebsd-15.1.tar.xz \
  --kernel /build/kernel.txz \
  --freebsd-src /usr/src \
  --output /build/dwm-freebsd-15.1.iso
```

The builder verifies that the root filesystem was prepared from the exact
`base.txz` identified by the ISO's MANIFEST. The kernel must match that manifest
too. Older media already containing `kernel.txz` can omit `--kernel`.
If an older builder failed with `missing usr/freebsd-dist/base.txz`, update
the builder and rerun only the ISO step with `--kernel`; the completed system
image and its JSON manifest can be reused. Keep each generated artifact with its adjacent
JSON manifest. Existing output files are never replaced. Failed builds retain
their workspace for diagnosis. If an unmount failed, detach that workspace's
devfs mount before removing anything; destroying the disposable VM is also a
safe cleanup option. Successful builds remove their temporary workspace.

## Install and start the minimal desktop

Test first in a fresh VM with an empty virtual disk. Boot the ISO and use the
normal interactive installer, choosing **Distribution Sets**, including both
base and kernel sets. Do not choose **Packages (Tech Preview)**: that path
bypasses the modified base archive and would install without dwm. Create a
regular user, set passwords, finish installation and reboot from the installed
disk. Configure Xorg and the GPU as described in the
[FreeBSD X11 handbook](https://docs.freebsd.org/en/books/handbook/x11/).

As the regular user:

```sh
startx /usr/local/bin/dwm-c9-session
```

The session seeds missing TOML files without replacing existing configuration.
Super+Return opens xterm, Super+1 through Super+9 changes tags,
Super+Shift+C closes a window and Super+Shift+Q logs out. Application data stays
in the user's persistent XDG data directory. The session refuses to start if
inherited autostart/autostop/theme-apply helpers are present, leaving those files untouched.
It does not install a display manager, configure GPU drivers, enable automatic
login or replace a user's `.xinitrc`.

## Continue to the Quickshell desktop

Once the minimal session works, follow the [step-by-step native desktop guide](https://lirux9873.github.io/dwm-c9-freebsd/desktop.html)
to clone the source, install native packages and build the user-owned Quickshell
session. No second ISO build is required.

## Validation boundary

Portable tests cover checksum/provenance rejection, distribution-manifest
updates, exclusive output publication, host rejection and failed-workspace
retention. Run `python3 tests/test-freebsd-image-builders.py`.

The owner reports successful image creation, UEFI/ZFS VM installation, basic
X11/dwm keyboard checks and startup after reboot. See
[manual VM evidence](FREEBSD-VM-VALIDATION.md) for scope and missing identifiers.
BIOS, UFS and physical hardware remain unverified. Before release qualification, record
both firmware boot/install results, output SHA256 values, package manifest,
normal-user terminal/tag/logout tests and source-tree revision.

References: [FreeBSD bsdinstall](https://man.freebsd.org/bsdinstall(8)),
[FreeBSD 15.1 ISO builder](https://github.com/freebsd/freebsd-src/blob/releng/15.1/release/amd64/mkisoimages.sh),
[distribution manifest format](https://github.com/freebsd/freebsd-src/blob/releng/15.1/release/scripts/make-manifest.sh).
