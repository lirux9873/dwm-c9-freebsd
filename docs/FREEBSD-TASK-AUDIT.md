# FreeBSD open-task audit

Review boundary: documentation-only inventory of work remaining after the
native Quickshell, themes and wallpaper milestones.

- Base: `codex/freebsd-themes-wallpaper` at `fc87c73` (pending PR #13).
- Branch: `codex/freebsd-open-tasks`.
- Inspected the installed helper set, native provider/session/installer,
  package profiles, FreeBSD image documentation, roadmap and native desktop
  boundary.
- Searched scripts, configuration, tests, workflows and project documents for
  Fedora, DNF/RPM, systemd, procfs/sysfs, NetworkManager, BlueZ, Linux audio,
  power and excluded-application assumptions. The keyword pass surfaced 146
  files outside historical evidence; matches were treated as audit leads, not
  automatic port requirements.
- Grouped work by supported-path safety, daily desktop features, Settings and
  administration, images/release qualification, and inherited-code cleanup.
- `ASTRO_TELEMETRY_DISABLED=1 npm run check`: 20 files, no diagnostics.
- `ASTRO_TELEMETRY_DISABLED=1 npm run build`: 16 pages built, including
  `open-tasks.html`.
- `git diff --check`: passed.

The built-in `codex review --uncommitted` command could not start on the
Windows host because it reported `Could not find home directory`. The change
does not alter runtime code.
