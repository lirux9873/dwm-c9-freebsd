# Active FreeBSD tasks

## Next milestone: native installation and session lifecycle

The minimal desktop passed owner testing on UEFI/ZFS. Native package profiles
and excluded integration cleanup are implemented; see
[cleanup validation](docs/FREEBSD-DEPENDENCY-REVIEW.md).
The full desktop remains unported.

- [ ] Inventory startup/helper commands and select the next native session scope.
- [ ] Replace GNU filesystem and Linux lifecycle assumptions in session helpers.
- [ ] Add a config-preserving native installer/uninstaller for existing systems.
- [ ] Validate native desktop-file paths, fonts and display-manager/startx entry.
- [ ] Test installation, repeat installation and rollback on the snapshot VM.
- [ ] Close core gaps: swallowing, status clicks and save/rename hot reloads.

Quickshell service providers and updates/recovery follow this milestone.
Historical Fedora issue authorizations do not govern this fork.
