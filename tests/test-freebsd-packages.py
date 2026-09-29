#!/usr/bin/env python3
"""Check native package profile contracts without installing packages."""
import os
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/dwm-freebsd-packages.sh"


class Profiles(unittest.TestCase):
    def run_profile(self, *args):
        return subprocess.run([os.environ.get("DWM_TEST_SH", "sh"), str(SCRIPT), *args],
                              capture_output=True, text=True)

    def test_profiles(self):
        profiles = {}
        for name in ("build", "runtime", "test", "image", "host"):
            result = self.run_profile(name)
            self.assertEqual(result.returncode, 0, result.stderr)
            packages = result.stdout.splitlines()
            self.assertEqual(packages, sorted(set(packages)))
            self.assertTrue(packages)
            for package in packages:
                self.assertRegex(package, r"^[A-Za-z0-9][A-Za-z0-9_+.-]*$")
            profiles[name] = set(packages)
        self.assertLessEqual(profiles["build"] | profiles["runtime"], profiles["image"])
        self.assertIn("git", profiles["image"])
        self.assertLessEqual({"python3", "xorg-vfbserver", "xdotool", "xprop"}, profiles["test"])
        self.assertLessEqual(profiles["build"] | {"git", "python3"}, profiles["host"])

    def test_invalid_profile_fails_without_output(self):
        for args in ((), ("full",), ("build", "runtime"), ("--help",)):
            result = self.run_profile(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(result.stdout)


if __name__ == "__main__":
    unittest.main()
