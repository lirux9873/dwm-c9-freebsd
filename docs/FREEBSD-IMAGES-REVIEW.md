# FreeBSD image builder review

## FreeBSD 15.1 disc1 correction (2026-09-29)

Base: `33a38d3` on main. The user's native run reached ISO staging and found
no `usr/freebsd-dist/base.txz`. FreeBSD's releng/15.1 release Makefile confirms
the default pkgbase disc1 layout includes MANIFEST but omits distribution
archives unless NOPKGBASE is set. The builder now validates the system image's
original base checksum against this manifest and accepts `--kernel`, verified
against the same manifest, before adding the two distributions.

Seven portable tests pass, including pkgbase and legacy-media staging, missing
kernel guidance, bad-kernel rejection, malformed/duplicate manifest rejection,
and preservation of the kernel manifest entry. The archive-list subprocess is
mocked in these staging tests; this is not a native ISO build result.
Whitespace checks pass. Built-in review remains unavailable with the same
home-directory error. Full native ISO build and boot remain unverified.

## Original implementation review

Base: `origin/main` at `dbd8e6c9b0b9a2192cb662a906f068cf7ccc0490`.
Scope: experimental minimal FreeBSD 15.1 amd64 X11/dwm artifacts.

Local validation on Windows (2026-09-28):

- Five portable tests pass: MANIFEST edits preserve other sets/selection;
  mismatched source and corrupt image rejection; no-clobber publication;
  wrong-host rejection; failed workspaces retained without publication.
- Shell wrapper and generated session pass shell syntax validation.
- Python builder help/parsing works; tests import the complete builder.
- Astro check: 17 files, no errors, warnings or hints; build: 13 pages pass.
- `git diff --check` passes.
- Independent review findings addressed: persistent application data,
  explicit Distribution Sets selection, and refusal of inherited autostart,
  autostop and theme-apply helpers. Source-tree version check added and ISO
  helper checksum recorded for provenance.
- Built-in `codex review --uncommitted` cannot start on this host because it
  reports "Could not find home directory"; independent review used instead.

Official releng/15.1 `mkisoimages.sh`, `make-manifest.sh`, `freebsd-version`
and bsdinstall sources were consulted. The workflow now runs portable builder
tests inside its FreeBSD VM in addition to the existing native core smoke.

No complete native image has been built or booted. Chroot package installation,
BIOS/UEFI boot, UFS/ZFS installation and installed-user X11 remain required
qualification gates. The PR must not be described as release-image validation.
