#!/usr/bin/env python3
"""Native installation, upgrade and rollback in a disposable user prefix."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

if not sys.platform.startswith("freebsd") or os.geteuid() == 0:
    raise SystemExit("Run as a regular user on FreeBSD")
source = Path(__file__).resolve().parents[1] / "scripts/install-freebsd-desktop.py"
spec = importlib.util.spec_from_file_location("installer", source)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
with tempfile.TemporaryDirectory(prefix="c9-install-test-") as directory:
    root = Path(directory)
    prefix = root / "desktop"
    installer.install(prefix)
    first = (prefix / "current").resolve()
    theme = prefix / "config/dwm-titus/themes.toml"
    custom = theme.read_text() + "\n# keep my configuration\n"
    theme.write_text(custom)
    hotkeys = prefix / "config/dwm-titus/hotkeys.toml"
    hotkeys.unlink()
    hotkeys.symlink_to(root / "must-not-create")
    installer.install(prefix)
    assert (prefix / "current").resolve() != first
    assert theme.read_text() == custom
    assert hotkeys.is_symlink() and not (root / "must-not-create").exists()
    installer.rollback(prefix)
    assert (prefix / "current").resolve() == first
    assert theme.read_text() == custom
    theme.write_text(installer.LEGACY_NATIVE_THEMES)
    installer.install(prefix)
    assert 'theme = "nord"' in theme.read_text()
    assert "[theme.dracula]" in theme.read_text()
    unmanaged = root / "unmanaged"
    unmanaged.mkdir()
    try:
        installer.install(unmanaged)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Unmanaged directory accepted")
print("PASS: native install, upgrade, config/link preservation and rollback")
