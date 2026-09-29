# Native dependency cleanup validation

Date: 2026-09-29. Base: d825768 (main). Reviewed branch:
codex/freebsd-native-packages. This record accompanies the cleanup commit;
its Git history identifies the exact published tree.

## Scope

The minimal image and native CI use scripts/dwm-freebsd-packages.sh.
All 22 distinct package names across image/test/host were found using
`pkg rquery -U %n PACKAGE` against the test VM's existing catalogue.
This confirms catalogue availability, not a newly executed package transaction.
Existing VM packages, installed binaries and user configuration were not changed.

Excluded optional integrations were removed from active install paths, helpers,
defaults, tests and site guides. Historical release/evidence records remain.
General FreeBSD installation and Quickshell service providers remain unported.

## Native checks

FreeBSD 15.1-RELEASE amd64, user daniel. Tests ran in an isolated copy at
/tmp/c9-native-cleanup.PciNtNal/source, based on d825768 plus the cleanup patch.

- python3 tests/test-freebsd-packages.py: 2 tests passed.
- python3 tests/test-freebsd-image-builders.py: 7 tests passed. The retained-workspace
  diagnostic is expected output from the failure-path test.
- env DWM_FREEBSD_X11_SMOKE=1 sh tests/test-freebsd-core.sh: process tests,
  clean build, binary staging and X11 launch/terminal/tags/close/logout passed.
- bash tests/test-dwm-terminal.sh: passed after making test sed usage portable.
- bash tests/test-webapp-launch.sh: passed after providing Bash in its isolated PATH.
- env DWM_TEST_LAUNCHER_LIST_ONLY=1 bash tests/test-quickshell-launcher.sh:
  desktop-entry discovery passed. This explicitly omits managed session launch.

The two existing strict-prototype compiler warnings and nonfatal XKEYBOARD
warnings remain. A previous readiness timeout did not recur in this run; its
cause remains unknown.

## Other checks and review

Astro check: 18 files, zero errors/warnings/hints. Static build: 14 pages.
Changed shell syntax and git diff --check passed. Independent code and docs
reviews completed; missing helper installation, stale documentation and an
unrelated deletion were corrected before final review.

Built-in Codex CLI review is unavailable on the authoring Windows host
(`Could not find home directory`); independent source review is used instead.
ShellCheck, shfmt and configured Quickshell QML lint/runtime tooling are not
available in this environment. The full inherited Fedora suite and fresh
Fedora image builds were not run. No new FreeBSD ISO was built for this change.

The full launcher regression test still fails at theme-environment propagation
on FreeBSD and Windows: the inherited session helper uses GNU stat assumptions.
Desktop-entry discovery passes separately; no full launcher/session or
Quickshell runtime validation is claimed. Terminal and webapp tests previously
failed on FreeBSD due to test harness GNU sed/PATH assumptions, now corrected.
