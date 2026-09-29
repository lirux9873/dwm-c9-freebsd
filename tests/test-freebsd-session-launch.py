#!/usr/bin/env python3
"""Native launcher boundaries; all files live in a private temporary directory."""
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

LAUNCHER = Path(__file__).resolve().parents[1] / "scripts/dwm-session-launch"


@unittest.skipUnless(platform.system() == "FreeBSD", "requires native FreeBSD")
class SessionLaunch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "config/dwm-titus"
        self.config.mkdir(parents=True)
        self.runtime = self.root / "runtime"
        self.runtime.mkdir()
        self.lock = self.runtime / "dwm-theme-apply.lock"
        self.theme = self.config / "theme-env.sh"
        self.theme.write_text("export QT_QPA_PLATFORMTHEME=gtk3\n"
                              "export XCURSOR_THEME=Test-Cursor\n"
                              "export XCURSOR_SIZE=32\n")
        self.env = dict(os.environ, HOME=str(self.root),
                        XDG_CONFIG_HOME=str(self.config.parent),
                        XDG_RUNTIME_DIR=str(self.runtime), XCURSOR_THEME="Parent")
        self.env.pop("XDG_DATA_DIRS", None)

    def launch(self, code=None):
        code = code or "import os,json,sys; print(json.dumps([os.environ['XCURSOR_THEME'],os.environ['XDG_DATA_DIRS'],sys.argv[1:]]))"
        return subprocess.run(["sh", str(LAUNCHER), sys.executable, "-c", code,
                               "argument with spaces", "literal;$()"],
                              env=self.env, capture_output=True, text=True, timeout=5)

    def test_environment_arguments_and_native_data_dirs(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), ["Test-Cursor",
                         "/usr/local/share:/usr/share",
                         ["argument with spaces", "literal;$()"]])
        self.env["XDG_DATA_DIRS"] = "/custom/share:/usr/local/share"
        self.assertEqual(json.loads(self.launch().stdout)[1], self.env["XDG_DATA_DIRS"])

    def test_lock_released_before_exec_and_exit_status(self):
        result = self.launch("import os,fcntl,sys; "
                             "f=open(os.environ['XDG_RUNTIME_DIR']+'/dwm-theme-apply.lock','a'); "
                             "fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB); sys.exit(37)")
        self.assertEqual(result.returncode, 37, result.stderr)

    def test_unsafe_lock_does_not_modify_target_or_block_launch(self):
        target = self.root / "target"
        for kind in ("dangling", "symlink", "hardlink"):
            with self.subTest(kind=kind):
                if kind != "dangling":
                    target.write_text("preserve me")
                if kind == "hardlink":
                    os.link(target, self.lock)
                else:
                    self.lock.symlink_to(target)
                result = self.launch()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0], "Parent")
                if kind == "dangling":
                    self.assertFalse(target.exists())
                else:
                    self.assertEqual(target.read_text(), "preserve me")
                self.lock.unlink()

    def test_unsafe_theme_records_are_not_loaded(self):
        original = self.root / "original"
        self.theme.rename(original)
        for kind in ("symlink", "hardlink", "oversized"):
            with self.subTest(kind=kind):
                if kind == "symlink":
                    self.theme.symlink_to(original)
                elif kind == "hardlink":
                    os.link(original, self.theme)
                else:
                    self.theme.write_text(original.read_text() + "\n" * 4096)
                result = self.launch()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)[0], "Parent")
                self.theme.unlink()


if __name__ == "__main__":
    unittest.main()
