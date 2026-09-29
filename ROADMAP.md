# FreeBSD migration roadmap

Target: FreeBSD 15.1 amd64, X11, native applications. The full desktop port
remains the goal; bootable media is only one component.

| Area | Status | Remaining work |
| --- | --- | --- |
| Core/process interfaces | Native CI passes | Swallowing, status clicks, TOML reload tests |
| Minimal desktop and images | Owner UEFI/ZFS VM tests pass | Exact artifact evidence; BIOS/UFS and physical hardware unverified |
| Dependencies and excluded apps | Next milestone | Shared native pkg profile; remove excluded integrations |
| Installer and session | Minimal image only | Existing-system install/uninstall, config preservation, display manager, lifecycle |
| Quickshell services | Not ported | Audio, network, Bluetooth, brightness, power, storage and displays |
| Updates and recovery | Not ported | Native package operations and privilege boundaries |
| Documentation and release | Partial | Replace Fedora guides; qualify complete desktop |

Implement dependencies/cleanup first, then native installation/session,
Quickshell provider groups, updates/recovery and full release qualification.
Keep the working minimal session available throughout. Close remaining core
runtime coverage gaps alongside these milestones.

Do not activate inherited Fedora installers or automatic updaters on FreeBSD.
See TASKS.md, docs/FREEBSD.md and docs/FREEBSD-VM-VALIDATION.md. Historical
Fedora plans remain in Git history and do not govern this fork.
