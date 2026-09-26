# Documentation publication review

Base: `origin/main` at `f27d436`. Scope: GitHub Pages publication for
`https://lirux9873.github.io/dwm-c9-freebsd/`.

Validation on Windows, 2026-09-26:

- Locked dependencies installed with `npm ci`.
- `astro check`: 17 files, zero errors, warnings or hints.
- `astro build`: all 13 static pages built successfully.
- Generated HTML audit: all local links, images/assets and fragment targets
  resolve; canonical URLs contain the repository prefix exactly once.
- Home page imports the FreeBSD guide; inherited reference pages carry one
  migration notice. No generated CNAME remains.
- `git diff --check`: passed.
- Independent source review: initial duplicate links/notices were corrected;
  follow-up review reports no remaining actionable findings.
- `codex review --uncommitted` could not start on this host: "Could not find
  home directory". Independent agent review supplied source review coverage.

The change does not modify the window manager. Native desktop tests are not
repeated for this documentation-only boundary. Hosted deployment and the live
site are checked after publication; their outcome is recorded in the PR.
