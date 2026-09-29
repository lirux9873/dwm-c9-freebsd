# FreeBSD image builder review

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
