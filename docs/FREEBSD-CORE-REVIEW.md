# FreeBSD core preparation: review evidence

This records the initial preparation review. Subsequent native build/process
and basic X11 results are recorded in [FREEBSD-CI-REVIEW.md](FREEBSD-CI-REVIEW.md).

Base: `origin/main`, commit `e5bbddc0c7261951d351d9a7c502a9952fc0b624`.
Branch: `codex/freebsd-core-foundation`.
Authoring environment: Windows/PowerShell with Git Bash; no FreeBSD test host.

## Scope

Core GNU make integration, native process/executable queries, XCB RES process
lookup, status-process discovery and spawn handling. A new native process/build
gate and migration documentation accompany the code. The inherited full desktop
installer is blocked on FreeBSD. This is not a completed desktop port.

## Checks

- `bash -n tests/test-freebsd-core.sh`: passed on Git Bash.
- Invoking the native gate on Git Bash: refused the non-FreeBSD host as expected.
- `git diff --check`: passed; Git reports local CRLF conversion notices only.
- Native `sh tests/test-freebsd-core.sh`: not run; requires FreeBSD 15.1.
- FreeBSD compiler, linker, process sysctls and binary staging: not run.
- X11, XCB RES, terminal swallowing, libinotify save/rename reloads, status
  signaling, launch-helper fallback and logout: not run.
- Inherited full Fedora regression suite: not run; its platform-specific
  behavior is not the FreeBSD qualification gate.

An independent source review found a misplaced child-PID declaration and a
status-bar session mismatch caused by autostart's setsid. Both were corrected:
the PID declaration is in spawn, and native discovery accepts the recorded
autostart session as well as dwm's own session while verifying UID and name.
The Codex review CLI was also attempted but could not start because its runtime
could not locate a home directory. The independent review agent supplies source
review; this is not a substitute for the missing native execution evidence.
The final independent follow-up review found no remaining actionable defects
in the scoped code and tests. It also confirmed that native execution remains
unverified. No compilation or runtime pass is inferred from this review.

No native results are reused from the upstream repository. Do not merge or
describe this as a validated FreeBSD desktop until the native checks pass.
