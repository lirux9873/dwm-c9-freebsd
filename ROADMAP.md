# FreeBSD migration roadmap

The FreeBSD 15.1 migration supersedes the inherited release plan below.

1. Core build and native process interfaces; validate in a FreeBSD VM.
2. Reduced dependency profiles and removal of unwanted optional integrations.
3. Native installer and X11 session lifecycle, preserving user configuration.
4. Quickshell system-provider adaptation and hardware validation.
5. Native update/recovery design, CI, documentation and release qualification.

See [FREEBSD.md](docs/FREEBSD.md) for the current code and test boundary.
No milestone is complete until its native acceptance checks pass.

## Historical Fedora 0.7.2 plan

## Current scope

Address issues #347, #344, #346 and #345 in one ready-for-review PR, as requested
on 2026-09-24. Version 0.7.2 covers the initial Fedora image update workflow,
DNF defaults and mirror measurement, and offline fastfetch provisioning.
Merge, tag publication, release assets and live deployment are outside this PR.

## Implementation and qualification

1. Audit effective Fedora 44 DNF5 configuration and provision conservative,
   interactive defaults without replacing administrator overrides.
2. Include fastfetch and mirror-measurement runtime dependencies in both images.
3. Offer the initial update after repository access, measure trusted mirrors,
   authorize a visible transaction, preserve retry, and persist only success.
4. Validate ordering, mirror fallback and security, actual DNF prompts, clean
   Fedora build/staged installation, image invariants and desktop behavior.
5. Run repository gates and independent review, document exact image-validation
   limits, and publish a ready-for-review PR against main.

Prior desktop-update work is documented in [DESKTOP-UPDATES.md](docs/DESKTOP-UPDATES.md)
and PR #318. Preserve earlier qualification in
[P8-QUALIFICATION.md](docs/P8-QUALIFICATION.md).

Exit: all four issue behaviors are implemented; validation evidence distinguishes
focused/container/runtime checks from full offline image qualification. Do not
claim a released or hardware-qualified image from static checks alone.
