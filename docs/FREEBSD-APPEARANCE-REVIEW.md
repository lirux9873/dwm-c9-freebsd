# FreeBSD appearance validation

Review boundary: native theme switching and persistent wallpaper support for
the FreeBSD 15.1 X11 desktop.

- Base: `origin/main` at `9b38034`
- Branch: `codex/freebsd-themes-wallpaper`
- Native package catalogue: `feh 3.12.2` resolves for FreeBSD 15.1 amd64.
- `python3 tests/test-freebsd-packages.py`: 2 tests passed on FreeBSD.
- `python3 tests/test-freebsd-appearance.py`: 2 tests passed on FreeBSD,
  including theme selection, terminal colors, wallpaper arguments, persistence,
  removal and a missing saved image.
- `python3 tests/test-freebsd-installer.py`: passed on FreeBSD, including legacy
  theme migration and preservation of user configuration.
- `python3 tests/test-freebsd-quickshell.py`: passed in a nested native X11
  session, including a live switch to the Dracula palette through Quickshell
  IPC. Quickshell used 0.01 CPU seconds over the five-second idle sample.
- `astro check`: 19 files checked with no errors, warnings or hints.
- `astro build`: 15 pages built successfully.
- Shell syntax and `git diff --check`: passed.
- Independent review found a stale-wallpaper startup failure. The helper now
  keeps the theme background when a saved image is unavailable, and the
  regression test covers that path. Re-review found no remaining code or
  security issues.

The VM did not yet have the real `feh` package installed. The appearance test
uses a recording executable to verify the exact argument vector, and the
graphical test uses a harmless stand-in. Displaying a real image remains a
short manual check after installing `feh`.

The built-in `codex review --uncommitted` command could not start on the
Windows host because it reported `Could not find home directory`. The
independent source review above was completed instead.
