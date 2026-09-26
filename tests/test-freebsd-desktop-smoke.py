#!/usr/bin/env python3
"""Exercise the native dwm core in Xvfb without unported session helpers."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

REPO = Path(__file__).resolve().parents[1]


def main():
    if not sys.platform.startswith("freebsd"):
        raise RuntimeError("This smoke test requires FreeBSD")
    if os.geteuid() == 0:
        raise RuntimeError("Run the desktop smoke test as an unprivileged user")
    if len(sys.argv) != 2:
        raise RuntimeError("Usage: test-freebsd-desktop-smoke.py /path/to/dwm")
    binary = Path(sys.argv[1]).resolve(strict=True)
    for command in ("Xvfb", "xterm", "xdotool", "xprop"):
        if not shutil.which(command):
            raise RuntimeError(f"Missing command: {command}")

    def interrupted(signum, _frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    with tempfile.TemporaryDirectory(prefix="c9-x11-") as directory:
        work = Path(directory)
        config = work / "config/dwm-titus"
        config.mkdir(parents=True)
        (work / "data/dwm-titus").mkdir(parents=True)
        (work / "runtime").mkdir(mode=0o700)
        for name in ("themes.toml", "window-rules.toml"):
            shutil.copyfile(REPO / "config" / name, config / name)
        (config / "hotkeys.toml").write_text('''[vars]
keys = [
  { mod="SUPER", key="Return", func="spawn", exec=["xterm", "-title", "C9SmokeTerminal"] },
  { mod="SUPER SHIFT", key="c", func="killclient" },
  { mod="SUPER SHIFT", key="q", func="quit" },
]
tag_keys = [
  { key="1", tag=0 },
  { key="2", tag=1 },
]
''', encoding="utf-8")
        env = {**os.environ, "HOME": str(work), "XDG_CONFIG_HOME": str(work / "config"),
               "XDG_DATA_HOME": str(work / "data"), "XDG_DATA_DIRS": "/usr/local/share",
               "XDG_STATE_HOME": str(work / "state"), "XDG_CACHE_HOME": str(work / "cache"),
               "XDG_RUNTIME_DIR": str(work / "runtime")}
        env.pop("DBUS_SESSION_BUS_ADDRESS", None)
        processes = []
        with (work / "desktop.log").open("w+") as log:
            def start(args, **kwargs):
                process = subprocess.Popen(args, env=env, stdout=log, stderr=log,
                                           start_new_session=True, **kwargs)
                processes.append(process)
                return process

            def run(*args):
                return subprocess.run(args, env=env, capture_output=True, text=True, timeout=3)

            def checked(*args):
                result = run(*args)
                if result.returncode:
                    raise RuntimeError(f"Command failed: {args}: {result.stderr}")
                return result

            def wait_for(label, predicate):
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError(f"Desktop process exited while waiting for {label}")
                    if predicate():
                        return
                    time.sleep(0.1)
                raise RuntimeError(f"Timed out waiting for {label}")

            def desktop_is(number):
                result = run("xprop", "-root", "_NET_CURRENT_DESKTOP")
                return result.returncode == 0 and result.stdout.rsplit("=", 1)[-1].strip() == str(number)

            try:
                with (work / "display").open("w+") as display_file:
                    start(["Xvfb", "-displayfd", str(display_file.fileno()), "-screen", "0",
                           "1024x768x24", "-nolisten", "tcp"], pass_fds=(display_file.fileno(),))
                    wait_for("Xvfb display", lambda: (work / "display").stat().st_size > 0)
                    env["DISPLAY"] = ":" + (work / "display").read_text().strip()
                wait_for("X11 readiness", lambda: run("xprop", "-root").returncode == 0)
                wm = start([str(binary)])
                wait_for("dwm readiness", lambda: desktop_is(0))
                checked("xdotool", "key", "--clearmodifiers", "super+Return")
                wait_for("terminal launch", lambda: run("xdotool", "search", "--onlyvisible",
                                                        "--name", "^C9SmokeTerminal$").returncode == 0)
                checked("xdotool", "key", "--clearmodifiers", "super+2")
                wait_for("second tag", lambda: desktop_is(1))
                checked("xdotool", "key", "--clearmodifiers", "super+1")
                wait_for("first tag", lambda: desktop_is(0))
                checked("xdotool", "key", "--clearmodifiers", "super+shift+c")
                wait_for("terminal close", lambda: run("xdotool", "search", "--name",
                                                       "^C9SmokeTerminal$").returncode == 1)
                checked("xdotool", "key", "--clearmodifiers", "super+shift+q")
                if wm.wait(timeout=5) != 0:
                    raise RuntimeError("dwm exited unsuccessfully")
                print("FreeBSD X11 smoke passed: launch, terminal, tags, close and logout")
            finally:
                for process in reversed(processes):
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=3)
                log.seek(0)
                print(log.read(), end="")


if __name__ == "__main__":
    main()
