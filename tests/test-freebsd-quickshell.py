#!/usr/bin/env python3
"""Exercise an isolated installed C9 desktop. Run under dbus-run-session."""
import argparse
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prefix", type=Path)
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    prefix = args.prefix.resolve()
    assert os.uname().sysname == "FreeBSD" and os.geteuid() != 0
    assert os.environ.get("DBUS_SESSION_BUS_ADDRESS"), "Run under dbus-run-session"
    apps = prefix / "data/applications"
    apps.mkdir(parents=True, exist_ok=True)
    entry = apps / "c9-native-test.desktop"
    if os.path.lexists(entry):
        raise RuntimeError("Use a disposable test prefix; test entry already exists")
    entry.write_text("[Desktop Entry]\nType=Application\nName=C9NativeTest\nExec=xterm -title C9NativeLaunched\n")
    env = dict(os.environ)
    processes = []
    with tempfile.TemporaryDirectory(prefix="c9-qs-test-") as directory:
        work = Path(directory)

        def run(*command):
            return subprocess.run(command, env=env, capture_output=True, text=True, timeout=8)

        def wait_for(label, predicate):
            until = time.monotonic() + 40
            while time.monotonic() < until:
                if any(p.poll() is not None for p in processes):
                    raise RuntimeError("Desktop exited while waiting for " + label)
                if predicate():
                    return
                time.sleep(.2)
            raise RuntimeError("Timeout waiting for " + label)

        def ipc(*command):
            env["XDG_RUNTIME_DIR"] = (prefix / "state/runtime-path").read_text().strip()
            return run("quickshell", "ipc", "--path", str(prefix / "config/quickshell/shell.qml"), "call", "desktop", *command)

        def visible(title):
            return run("xdotool", "search", "--onlyvisible", "--name", title).returncode == 0

        with (work / "x.log").open("w") as log:
            try:
                with (work / "display").open("w+") as fd:
                    processes.append(subprocess.Popen(["Xvfb", "-displayfd", str(fd.fileno()), "-screen", "0", "1280x800x24", "-nolisten", "tcp"], pass_fds=(fd.fileno(),), stdout=log, stderr=log))
                    wait_for("display", lambda: (work / "display").stat().st_size > 0)
                env["DISPLAY"] = ":" + (work / "display").read_text().strip()
                wait_for("X11", lambda: run("xprop", "-root").returncode == 0)
                session = subprocess.Popen([str(prefix / "start-session")], env=env, stdout=log, stderr=log, start_new_session=True)
                processes.append(session)
                wait_for("runtime", lambda: (prefix / "state/runtime-path").exists())
                wait_for("Quickshell IPC", lambda: ipc("workspace").returncode == 0)
                assert run("xdotool", "key", "--clearmodifiers", "super+2").returncode == 0
                wait_for("workspace model", lambda: ipc("workspace").stdout.strip() == "1")
                run("xdotool", "key", "--clearmodifiers", "super+1")
                run("xdotool", "key", "--clearmodifiers", "super+d")
                wait_for("launcher", lambda: visible("dwm launcher"))
                wait_for("app index", lambda: int(ipc("applicationCount").stdout.strip() or "0") > 0)
                run("xdotool", "type", "C9NativeTest")
                run("xdotool", "key", "Return")
                wait_for("application launch", lambda: visible("C9NativeLaunched"))
                run("xdotool", "key", "--clearmodifiers", "super+s")
                wait_for("native controls", lambda: visible("C9 FreeBSD controls"))
                run("xdotool", "key", "Escape")
                run("xdotool", "key", "--clearmodifiers", "super+Return")
                wait_for("terminal", lambda: visible("xterm"))
                def active_terminal_title():
                    result = ipc("activeTitle")
                    return result.returncode == 0 and result.stdout.strip() == "xterm"
                wait_for("active window title", active_terminal_title)
                # The panel must reserve real screen space, not cover clients.
                window = run("xdotool", "search", "--onlyvisible", "--class", "XTerm").stdout.splitlines()[0]
                geometry = run("xdotool", "getwindowgeometry", "--shell", window).stdout
                fields = dict(line.split("=", 1) for line in geometry.splitlines() if "=" in line)
                assert int(fields["Y"]) >= 42, geometry
                result = run("gdbus", "call", "--session", "--dest", "org.freedesktop.Notifications", "--object-path", "/org/freedesktop/Notifications", "--method", "org.freedesktop.Notifications.Notify", "C9 test", "0", "", "Native notification", "FreeBSD Quickshell integration passed", "[]", "{}", "5000")
                assert result.returncode == 0, result.stderr
                wait_for("notification history", lambda: int(ipc("notificationCount").stdout.strip() or "0") > 0)
                children = run("pgrep", "-P", str(session.pid)).stdout.splitlines()
                shell_pid = next(pid for pid in children if "quickshell" in run("ps", "-p", pid, "-o", "comm=").stdout)
                before = run("ps", "-p", shell_pid, "-o", "time=").stdout.strip()
                time.sleep(5)
                after = run("ps", "-p", shell_pid, "-o", "time=").stdout.strip()
                print("Idle Quickshell CPU time over 5s:", before, "->", after)
                if args.screenshot:
                    subprocess.run(["xwd", "-root", "-silent", "-out", str(args.screenshot)], env=env, check=True)
                run("xdotool", "key", "--clearmodifiers", "super+shift+q")
                assert session.wait(timeout=12) == 0
                print("PASS: Quickshell panel, workspace model, launcher index, controls, terminal, reserved panel area, notifications and logout")
            finally:
                entry.unlink(missing_ok=True)
                for process in reversed(processes):
                    if process.poll() is None:
                        process.terminate()
                for process in reversed(processes):
                    try:
                        process.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        process.kill()
                print((prefix / "logs/session.log").read_text()[-10000:])


if __name__ == "__main__":
    main()
