#!/usr/bin/env python3
"""Exercise native theme and wallpaper state in a private directory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / "scripts/dwm-freebsd-appearance"


@unittest.skipUnless(sys.platform.startswith("freebsd"), "requires native FreeBSD")
class Appearance(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="c9-appearance-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / "config/dwm-titus"
        self.config.mkdir(parents=True)
        shutil.copyfile(REPO / "config/freebsd/themes.toml", self.config / "themes.toml")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.log = self.root / "commands.log"
        for command in ("xsetroot", "feh", "xterm"):
            path = self.bin / command
            path.write_text("#!/bin/sh\nprintf '%s' '" + command + "' >>\"$C9_APPEARANCE_LOG\"\nprintf ' <%s>' \"$@\" >>\"$C9_APPEARANCE_LOG\"\nprintf '\\n' >>\"$C9_APPEARANCE_LOG\"\n")
            path.chmod(0o700)
        self.env = dict(os.environ, XDG_CONFIG_HOME=str(self.root / "config"),
                        DISPLAY=":test", C9_APPEARANCE_LOG=str(self.log),
                        PATH=str(self.bin) + os.pathsep + os.environ["PATH"])

    def invoke(self, *arguments):
        return subprocess.run([sys.executable, str(HELPER), *arguments], env=self.env,
                              capture_output=True, text=True, timeout=5)

    def test_theme_switch_and_terminal_palette(self):
        result = self.invoke("themes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ["nord", "dracula", "gruvbox", "tokyonight"])
        result = self.invoke("theme", "dracula")
        self.assertEqual(result.returncode, 0, result.stderr)
        palette = json.loads((self.config / "native-theme.json").read_text())
        self.assertEqual(palette["name"], "dracula")
        self.assertEqual(palette["colors"]["accent"], "#BD93F9")
        self.assertIn('theme = "dracula"', (self.config / "themes.toml").read_text())
        result = self.invoke("terminal", "-T", "argument with spaces")
        self.assertEqual(result.returncode, 0, result.stderr)
        terminal_log = self.log.read_text().splitlines()[-1]
        self.assertTrue(terminal_log.startswith("xterm "))
        self.assertIn("<-bg> <#282A36>", terminal_log)

    def test_wallpaper_persists_and_rejects_bad_input(self):
        image = self.root / "wall paper.png"
        image.write_bytes(b"test fixture")
        result = self.invoke("wallpaper", str(image), "max")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.config / "wallpaper.conf").read_text(),
                         "path=" + str(image) + "\nfit=max\n")
        self.assertIn("feh <--no-fehbg> <--bg-max> <" + str(image) + ">", self.log.read_text())
        bad = self.root / "not-image.txt"
        bad.write_text("no")
        result = self.invoke("wallpaper", str(bad))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.config / "wallpaper.conf").read_text(),
                         "path=" + str(image) + "\nfit=max\n")
        image.unlink()
        result = self.invoke("apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("saved wallpaper skipped", result.stderr)
        self.assertEqual(self.invoke("clear-wallpaper").returncode, 0)
        self.assertFalse((self.config / "wallpaper.conf").exists())


if __name__ == "__main__":
    unittest.main()
