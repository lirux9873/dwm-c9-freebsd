# Active Tasks

## FreeBSD milestone 1: core preparation

This is the active work; the completed Fedora task list below is historical.

- [x] Inspect detached origin/main and create a focused branch.
- [x] Implement native process queries and core build integration.
- [x] Add a native build/process gate and document the unported boundaries.
- [x] Run the gate on FreeBSD 15.1 amd64; see docs/FREEBSD-CI-REVIEW.md.
- [x] Verify basic X11 launching, terminal hotkey, tags, close and logout in CI.
- [ ] Verify swallowing, status clicks and TOML save/rename reloads.
- [ ] Complete native validation and review before merging as a usable port.

## Fedora 0.7.2 initial updates

User authorization: implement issues #347, #344, #346 and #345 and open one
ready-for-review PR. No merge or release publication is authorized.

- [x] Inspect issues, verify clean origin/main ancestry, create codex/fedora-0.7.2.
- [x] Audit effective DNF5 settings and preserve administrator overrides.
- [x] Provision fastfetch and initial-update dependencies in both image variants.
- [x] Implement repository-gated first-login offer and visible authorized update.
- [x] Implement bounded throughput/latency measurement with trusted fallback lists.
- [x] Complete failure/retry, real prompt, Fedora installation and runtime checks.
- [x] Complete full repository gates and document image-validation limitations.
- [x] Complete independent review, fix valid findings, and prepare the validated PR.

Behavior and recovery: [INITIAL-UPDATE.md](docs/INITIAL-UPDATE.md).

Validation: [INITIAL-UPDATE-QUALIFICATION.md](docs/INITIAL-UPDATE-QUALIFICATION.md).
