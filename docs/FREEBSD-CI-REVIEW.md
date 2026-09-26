# FreeBSD Desktop smoke workflow evidence

Base: `b73ae5c` (main after the core-preparation PR).
Branch: `codex/freebsd-desktop-smoke`.

The job keeps its `Desktop smoke` name. Ubuntu supplies only the GitHub-hosted
VM launcher; `pkg`, compilation, the native process gate and the X11 smoke run
inside FreeBSD 15.1 amd64. The VM action is pinned to the verified v1.5.7
revision `4469451fe39bee80be4066836c5170362e9349f3`. Its action inputs and 15.1
definition were inspected before use.

Local checks on Windows:

- Git Bash `bash -n tests/test-freebsd-core.sh`: passed.
- Python AST parsing of `tests/test-freebsd-desktop-smoke.py`: passed.
- `git diff --check`: passed.
- Independent source review of workflow, gate and smoke: no actionable findings.
- YAML parser unavailable locally; GitHub accepted and executed the workflow.
- The Codex review CLI was unavailable in this task's environment (home-directory
  initialization failure during the preceding core review); independent source
  review was performed by a review agent.

## Hosted result

[Run 36231369609](https://github.com/lirux9873/dwm-c9-freebsd/actions/runs/36231369609)
passed for code commit `f3591cb239899483fa7ee37c54bd359c95eeefe1` on
2026-09-26. The guest reported FreeBSD **15.1-RELEASE-p3**, amd64.
Package resolution, native process tests, clean core build, manual binary
staging and the unprivileged X11 smoke all passed. Clang reported two existing
non-prototype declaration warnings for `getstatusbarpid`; there were no build
errors. Subsequent documentation-only changes reuse this code validation.

The workflow intentionally replaces
the inherited Fedora/Quickshell smoke with native core coverage: spawning a
terminal through a hotkey, tag changes, client closing and normal logout under
Xvfb as an unprivileged user. Full Quickshell services, physical GPUs, audio and
the desktop installer remain outside this gate.
