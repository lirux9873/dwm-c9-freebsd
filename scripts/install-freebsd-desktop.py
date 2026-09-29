#!/usr/bin/env python3
"""Build and install the native desktop in a dedicated user-owned directory."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
CORE = "Makefile config.mk config.def.h dwm.c drw.c drw.h util.c util.h tomlparser.c tomlparser.h freebsd-process.c freebsd-process.h".split()
HELPERS = "dwm-c9-terminal dwm-freebsd-session dwm-freebsd-provider dwm-c9-shell-control dwm-quickshell-state dwm-quickshell-launcher dwm-session-launch dwm-terminal".split()


def install(prefix):
    if not sys.platform.startswith("freebsd") or os.geteuid() == 0:
        raise RuntimeError("Run as your regular user on FreeBSD 15.1")
    version = subprocess.check_output(["freebsd-version", "-u"], text=True).strip()
    if not version.startswith("15.1-RELEASE"):
        raise RuntimeError("Requires FreeBSD 15.1-RELEASE")
    for command in ("gmake", "cc", "quickshell", "xterm", "xprop", "xdotool", "dbus-run-session", "bash", "xsetroot"):
        if not shutil.which(command):
            raise RuntimeError("Missing dependency: " + command)
    prefix = prefix.expanduser().absolute()
    if prefix.is_symlink():
        raise RuntimeError("Installation prefix must not be a symlink")
    marker = prefix / ".c9-managed"
    runtime_record = prefix / "state/runtime-path"
    if runtime_record.is_file() and Path(runtime_record.read_text().strip()).is_dir():
        raise RuntimeError("Log out of the C9 session before updating it")
    current_path = prefix / "current"
    if os.path.lexists(current_path) and not current_path.is_symlink():
        raise RuntimeError("Refusing unmanaged current release entry")
    if prefix.exists() and not marker.is_file():
        raise RuntimeError("Refusing an existing unmanaged directory: " + str(prefix))
    prefix.mkdir(parents=True, exist_ok=True)
    marker.touch()
    releases = prefix / "releases"
    releases.mkdir(exist_ok=True)
    config = prefix / "config"
    (config / "dwm-titus").mkdir(parents=True, exist_ok=True)
    qml_link = config / "quickshell"
    if os.path.lexists(qml_link) and (not qml_link.is_symlink() or os.readlink(qml_link) != str(prefix / "current/quickshell")):
        raise RuntimeError("Refusing to replace unmanaged Quickshell configuration")
    with tempfile.TemporaryDirectory(prefix="c9-build-") as temporary:
        build = Path(temporary)
        for name in CORE:
            shutil.copyfile(REPO / name, build / name)
        template = build / "config.def.h"
        template.write_text(template.read_text().replace("MesloLGS Nerd Font Mono", "Noto Sans Mono"))
        subprocess.run(["gmake", "-C", str(build), "CC=cc", "clean", "all"], check=True)
        release = Path(tempfile.mkdtemp(prefix=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-"), dir=releases))
        (release / "bin").mkdir()
        shutil.copy2(build / "dwm", release / "bin/dwm")
        for name in HELPERS:
            shutil.copyfile(REPO / "scripts" / name, release / "bin" / name)
            (release / "bin" / name).chmod(0o755)
        shutil.copytree(REPO / "config/quickshell", release / "quickshell")
        shutil.copyfile(release / "quickshell/freebsd.qml", release / "quickshell/shell.qml")
    # Only create defaults that are absent. User TOML edits survive upgrades.
    for name in ("hotkeys.toml", "themes.toml", "window-rules.toml"):
        target = config / "dwm-titus" / name
        if not os.path.lexists(target):
            shutil.copyfile(REPO / "config/freebsd" / name, target)
    if not qml_link.is_symlink():
        qml_link.symlink_to(prefix / "current/quickshell")
    current = prefix / "current"
    previous = os.readlink(current) if current.is_symlink() else None
    if previous:
        (prefix / "previous-release.txt").write_text(previous + "\n")
    pending = prefix / (".current-" + str(os.getpid()))
    pending.symlink_to(release)
    os.replace(pending, current)
    wrapper = prefix / "start-session"
    wrapper.write_text('#!/bin/sh\nset -eu\nDWM_C9_HOME=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)\nexport DWM_C9_HOME\nexec "$DWM_C9_HOME/current/bin/dwm-freebsd-session"\n')
    wrapper.chmod(0o755)
    print("Installed:", release)
    print('From the VM console: startx "' + str(wrapper) + '"')
    print("Log:", prefix / "logs/session.log")
    print("Existing system desktop and user settings outside this directory are unchanged.")


def rollback(prefix):
    prefix = prefix.expanduser().absolute()
    if not (prefix / ".c9-managed").is_file():
        raise RuntimeError("Not a managed C9 installation")
    record = prefix / "state/runtime-path"
    if record.is_file() and Path(record.read_text().strip()).is_dir():
        raise RuntimeError("Log out of the C9 session before rollback")
    previous = Path((prefix / "previous-release.txt").read_text().strip()).resolve(strict=True)
    if previous.parent != (prefix / "releases").resolve() or not (previous / "bin/dwm").is_file():
        raise RuntimeError("Invalid previous release")
    pending = prefix / (".rollback-" + str(os.getpid()))
    pending.symlink_to(previous)
    os.replace(pending, prefix / "current")
    print("Restored:", previous)
    print("User settings were preserved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path, default=Path.home() / ".local/share/dwm-c9-freebsd")
    parser.add_argument("--rollback", action="store_true", help="Restore the previous installed release; preserve settings")
    args = parser.parse_args()
    try:
        if args.rollback:
            rollback(args.prefix)
        else:
            install(args.prefix)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
