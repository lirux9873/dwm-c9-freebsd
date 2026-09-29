# FreeBSD 15.1 open task inventory

Target: FreeBSD 15.1-RELEASE amd64, X11 and native FreeBSD packages.

The supported desktop currently consists of dwm, the native Quickshell panel,
launcher, notifications, tray, basic system information, mixer volume controls,
themes and `feh` wallpaper support. The installer copies only the small helper
set declared in `scripts/install-freebsd-desktop.py`; the other inherited
scripts and settings remain porting input and are not supported on FreeBSD.

This list is ordered by dependency and user impact. A similarly named FreeBSD
package is not proof that a Linux integration can be reused. Each provider must
be checked against its native interface and tested on FreeBSD.

## P0 - define and protect the native product

- [ ] Classify every inherited script and configuration file as **port**,
  **replace**, **retain as historical reference**, or **remove**. Record the
  decision before expanding the native installer.
- [ ] Make unsupported entry points fail clearly on FreeBSD. Cover
  `install.sh`, `gmake install`, `scripts/dev-sync-install.sh`, inherited image
  helpers and any direct invocation of Linux-only desktop providers.
- [ ] Replace the inherited Fedora product contract in `SPEC.md`, the remaining
  Fedora sections of `AGENTS.md`, `CONTRIBUTING.md`, issue templates and the PR
  template with the FreeBSD support and validation contract.
- [ ] Decide the final configuration locations and migration contract. The
  current user installer intentionally uses
  `~/.local/share/dwm-c9-freebsd/config`; inherited helpers expect
  `${XDG_CONFIG_HOME:-~/.config}/dwm-titus`.
- [ ] Expand `scripts/dwm-freebsd-packages.sh` only as native components are
  accepted. For every new dependency, verify the FreeBSD 15.1 amd64 package
  name, executable path, service requirements and license.
- [ ] Add a native uninstall command and document exactly which managed files
  it removes. Preserve every user-owned TOML file, wallpaper and unrelated X11
  configuration.

## P1 - complete a daily-use desktop

### Session, startup and login

- [ ] Add config-preserving XDG autostart support and orderly shutdown without
  `/proc`, `loginctl`, or `systemctl`. Replace the relevant behavior from
  `scripts/autostart.sh`, `scripts/autostop.sh`,
  `scripts/dwm-xdg-autostart` and `config/systemd/user/`.
- [ ] Provide and test a system-wide X session entry for a FreeBSD display
  manager while retaining the working `startx` path. Test login, logout,
  repeated login and failure recovery as an unprivileged user.
- [ ] Decide whether a display manager is part of the supported package profile;
  if it is, document its `rc.conf` setup without silently enabling services.
- [ ] Add session log rotation or bounded retention so
  `~/.local/share/dwm-c9-freebsd/logs/session.log` cannot grow indefinitely.

### Hardware and quick controls

- [ ] Validate audible output and mixer selection on real FreeBSD hardware.
  Extend `dwm-freebsd-provider` beyond the single `vol` device only after the
  supported OSS, PulseAudio or PipeWire contract is chosen.
- [ ] Implement event-driven network status and Wi-Fi operations using a
  reviewed FreeBSD interface. The current provider is IPv4/read-only;
  `scripts/dwm-quickshell-network` assumes NetworkManager, `nmcli` and procfs.
- [ ] Implement native Bluetooth discovery, pairing, connection and power
  controls. Do not reuse the BlueZ/`bluetoothctl` provider without proving that
  exact service is supported on the target system.
- [ ] Implement brightness discovery and adjustment for supported FreeBSD
  hardware, including clear unsupported states for desktops and VMs.
- [ ] Implement battery state, AC state and remaining-time reporting and test
  it on a laptop. The current `hw.acpi.battery.life` value is percentage only.
- [ ] Implement lock, suspend, reboot and power-off actions with explicit user
  intent and a narrow FreeBSD authorization design. Replace logind/systemd and
  Linux power-profile assumptions from `dwm-lock*`, `power-management.sh` and
  the inherited power QML.
- [ ] Port screenshots and clipboard handling to selected native packages and
  verify region, active-monitor and full-desktop capture.

### Displays, input and core behavior

- [ ] Port display discovery, layout preview, confirmation and rollback from
  the inherited `dwm-display-*` and `dwm-settings-display*` helpers. Remove
  `/sys/class/drm` and Linux process-identity assumptions.
- [ ] Test multi-monitor panel placement, tray behavior, workspace routing,
  hot-plug and disconnect recovery on FreeBSD Xorg.
- [ ] Port keyboard, pointer, repeat-rate and cursor settings using native X11
  tools. Preserve a timed rollback for changes that can make input unusable.
- [ ] Complete end-to-end dwm tests for swallowing, status clicks, focus,
  monitor movement and save/rename hot reload of `hotkeys.toml`, `themes.toml`
  and `window-rules.toml`.
- [ ] Decide whether Picom is supported. If retained, package and test its
  startup, configuration, restart and failure behavior; otherwise remove its
  settings UI and inherited autostart paths.

### Appearance and desktop utilities

- [ ] Add a graphical wallpaper picker and fit-mode controls to the native
  System panel while retaining the tested `dwm-freebsd-appearance` CLI.
- [ ] Port or deliberately remove the inherited font, GTK theme, icon theme,
  cursor, panel-settings and application-theme writers. Preserve customized
  files and provide preview/rollback for risky appearance changes.
- [ ] Port default applications and MIME associations using native XDG tools.
- [ ] Decide which terminal, file manager, browser, media player, notification
  tools and archive utilities belong in the supported desktop profile; verify
  each native package and default binding.
- [ ] Port the status process only if dwm status text/click actions remain a
  product feature. `scripts/dwm-status` currently assumes procfs, Linux power
  supply sysfs and PulseAudio/PipeWire tools.

## P2 - port Settings and system administration

- [ ] Replace the reduced System popup with a native Settings application, one
  pane at a time. Do not install the inherited `config/quickshell/settings/`
  models until their providers are native and their unsupported states work.
- [ ] Port system information and health checks to FreeBSD interfaces such as
  `sysctl`, `procstat`, `swapinfo` and the rc service system. Remove procfs,
  pressure-stall, systemd-unit, journal and firewalld assumptions.
- [ ] Design package updates around `pkg` with a previewable transaction,
  explicit root authorization, interruption recovery and honest error states.
  Replace `dwm-desktop-update*`, `dwm-initial-update*`, DNF/RPM/PackageKit code
  and `config/dnf/`; do not enable unattended upgrades by default.
- [ ] Evaluate ZFS boot environments with `bectl` for update recovery. Keep UFS
  supported with a clearly documented reduced recovery path.
- [ ] Port hostname, timezone, time synchronization, locale and keyboard-layout
  settings using FreeBSD configuration files and rc services. Use narrow,
  root-owned helpers for privileged writes.
- [ ] Decide the FreeBSD scope for users, printers, services and repositories.
  Port only the accepted features; remove the remaining AccountsService, CUPS,
  systemd and Fedora repository UI.
- [ ] Port diagnostics so it reports FreeBSD version, ABI, packages, rc
  services, Xorg, dwm, Quickshell and the selected hardware providers without
  leaking private configuration or credentials.
- [ ] Replace the Fedora source-update/release helpers with a FreeBSD-aware,
  config-preserving application update and rollback workflow.

## P3 - installation media, release qualification and cleanup

### Images and installation

- [ ] Integrate the supported Quickshell desktop into the FreeBSD system image
  so a custom-ISO install does not require a second source checkout. Retain a
  minimal recovery session.
- [ ] Decide and document first-boot behavior, user creation, GPU setup,
  services and display-manager setup. Do not automate disk selection or enable
  services without visible user choice.
- [ ] Qualify both UEFI and BIOS installs, ZFS and UFS, clean upgrade/rollback,
  checksums, manifests and normal-user desktop startup. UEFI/ZFS VirtualBox is
  the only owner-confirmed installation path so far.
- [ ] Test Intel, AMD, NVIDIA and VirtualBox graphics separately and document
  the exact FreeBSD packages and configuration for each verified path.

### Retire inherited Fedora surfaces

- [ ] Remove or archive the Fedora Kickstarts, Anaconda branding,
  `build-dwm-fedora-*`, `scripts/image/`, `config/dnf/` and
  `config/systemd/` after any reusable behavior has a native replacement.
- [ ] Remove obsolete Fedora tests and fixtures as their native replacements
  land. Keep the FreeBSD VM workflow as the required gate and ensure CI never
  reports Linux-host execution as native validation.
- [ ] Rewrite or remove inherited Astro pages that still advertise a complete
  Fedora desktop, including Development Progress, Settings, Control Center,
  theming, installation and troubleshooting content.
- [ ] Remove remaining Steam, Flatpak, Gear Lever/AppImage and Herdr references
  from tracked documentation and evidence if complete source-tree removal is
  still the project policy. Their upstream history remains available in Git.
- [ ] Replace stale Fedora package names and comments in defaults such as
  `config.def.h`, and remove duplicate Linux-only `config/*.toml` once native
  defaults cover the accepted features.
- [ ] Finish project naming, screenshots, logos, manual pages, security policy,
  release notes and versioning for `dwm-c9-freebsd`.

### Final qualification

- [ ] Run the complete native CI gate on every supported change and keep
  focused regression tests for each ported provider.
- [ ] Measure Quickshell idle CPU/memory, repeated provider failures and session
  shutdown after the full desktop is assembled.
- [ ] Complete physical-hardware testing for audio, battery, brightness,
  suspend/resume, Wi-Fi, Bluetooth, multi-monitor and GPU acceleration.
- [ ] Publish a release checklist with FreeBSD version, architecture, package
  repository ABI, source commit, image checksums, firmware/filesystem matrix,
  known hardware gaps and rollback instructions.

## Already complete

- [x] Native FreeBSD process discovery and clean dwm build.
- [x] Basic X11 smoke: terminal, tags, close and logout.
- [x] FreeBSD package profiles and native CI VM.
- [x] Experimental FreeBSD system-image and installer-ISO builders.
- [x] Owner-tested UEFI/ZFS installation in VirtualBox.
- [x] User-owned installer with repeat install, rollback and preserved TOML.
- [x] Native Quickshell panel, launcher, tray and notifications.
- [x] Basic hostname, load, IPv4, battery percentage and mixer controls.
- [x] Four live color themes and persistent `feh` wallpaper support.

Completion means code, native package mapping, user documentation and focused
FreeBSD validation land together. Hardware-dependent work must name the tested
hardware and leave untested devices explicitly unqualified.
