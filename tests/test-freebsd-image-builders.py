#!/usr/bin/env python3
"""Portable failure-path tests; these do not claim FreeBSD boot coverage."""
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("builder", Path(__file__).resolve().parents[1] / "scripts/build-dwm-freebsd-system-image.py")
sys.dont_write_bytecode = True
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ImageTests(unittest.TestCase):
    def test_manifest_preserves_kernel_and_selection(self):
        kernel = 'kernel.txz\toldkernel\t20\tkernel\t"Kernel"\ton\n'
        text = 'base.txz\toldbase\t10\tbase\t"Base system"\ton\n' + kernel
        result = builder.replace_manifest(text, "newhash", 42)
        self.assertIn('base.txz\tnewhash\t42\tbase\t"Base system"\ton\n', result)
        self.assertTrue(result.endswith(kernel))
        for invalid in (kernel, text + text, "base.txz\tbroken"):
            with self.assertRaises(ValueError):
                builder.replace_manifest(invalid, "newhash", 42)

    def test_image_provenance_and_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base.txz"
            image = root / "system.tar.xz"
            base.write_bytes(b"official base fixture")
            image.write_bytes(b"prepared image fixture")
            manifest = image.with_name(image.name + ".json")
            metadata = {"kind": "freebsd-dwm-base", "protocol": 1,
                        "release": "15.1-RELEASE", "architecture": "amd64",
                        "profile": "minimal-x11", "source_base_sha256": builder.digest(base),
                        "sha256": builder.digest(image), "size": image.stat().st_size}
            manifest.write_text(json.dumps(metadata))
            self.assertEqual(builder.validate_system(image, base), metadata)
            base.write_bytes(b"different release")
            with self.assertRaises(ValueError):
                builder.validate_system(image, base)
            image.write_bytes(b"corrupted image")
            with self.assertRaises(ValueError):
                builder.validate_system(image, base)

    def test_publication_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            staged = root / "staged"
            output = root / "published.iso"
            staged.write_bytes(b"new image")
            output.write_bytes(b"existing image")
            with self.assertRaises(FileExistsError):
                builder.publish(staged, output, {})
            self.assertEqual(output.read_bytes(), b"existing image")
            self.assertFalse(output.with_name(output.name + ".json").exists())
            output.unlink()
            builder.publish(staged, output, {})
            with self.assertRaises(FileExistsError):
                builder.publish(staged, output, {})
            self.assertEqual(output.read_bytes(), b"new image")

    def test_host_rejection_precedes_any_build(self):
        with patch.object(builder.platform, "system", return_value="Linux"), patch.object(builder, "run") as run:
            with self.assertRaisesRegex(ValueError, "FreeBSD 15.1"):
                builder.host_check()
            run.assert_not_called()

    def test_unmount_failure_prevents_publication(self):
        # main retains the failed workspace instead of recursively deleting a
        # possibly mounted device filesystem. Test that cleanup boundary.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "base.txz"
            base.write_bytes(b"fixture")
            with patch.object(builder, "host_check"), patch.object(builder, "build_system", side_effect=OSError("umount failed")), patch.object(builder, "publish") as publish:
                with self.assertRaises(OSError):
                    builder.main(["--input", str(base), "--sha256", builder.digest(base),
                                  "--output", str(root / "system.tar.xz"), "--disposable-vm"])
                publish.assert_not_called()
            self.assertEqual(len(list(root.glob(".dwm-freebsd-*"))), 1)


if __name__ == "__main__":
    unittest.main()
