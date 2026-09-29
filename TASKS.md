# Active FreeBSD tasks

## Next milestone: native dependencies and integration cleanup

The minimal desktop passed owner testing on UEFI/ZFS. The full desktop remains
unported. See ROADMAP.md and docs/FREEBSD-VM-VALIDATION.md.

- [ ] Inventory commands in startup, hotkeys, settings and helpers.
- [ ] Share one native pkg dependency profile between installation and images.
- [ ] Remove Steam/gaming, Flatpak, Gear Lever/AppImage and Herdr from active
  code, configuration, dependencies, tests and documentation.
- [ ] Remove their shortcuts, launch actions and settings delegates.
- [ ] Verify remaining native packages and explicitly unsupported capabilities.
- [ ] Run native package resolution and core/X11 checks; complete review.

Historical Fedora issue tasks and authorizations remain in Git history and
are not requirements of this detached fork.
