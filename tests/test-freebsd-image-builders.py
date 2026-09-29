#!/usr/bin/env python3
"""Portable failure-path tests; these do not claim FreeBSD boot coverage."""
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SPEC = importlib.util.spec_from_file_location("builder", Path(__file__).resolve().parents[1] / "scripts/build-dwm-freebsd-system-image.py")
sys.dont_write_bytecode = True
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class ImageTests(unittest.TestCase):
    def test_pkgbase_and_legacy_media(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                dist = root / "dist"
                dist.mkdir()
                image = root / "system.tar.xz"
                image.write_bytes(b"customized base")
                kernel = root / "kernel.txz"
                kernel.write_bytes(b"official kernel")
                base_hash = "a" * 64
                original = (f'base.txz\t{base_hash}\t1\tbase\t"Base"\ton\n'
                            f'kernel.txz\t{builder.digest(kernel)}\t2\tkernel\t"Kernel"\ton\n')
                (dist / "MANIFEST").write_text(original)
                metadata = {"kind": "freebsd-dwm-base", "protocol": 1,
                            "release": "15.1-RELEASE", "architecture": "amd64",
                            "profile": "minimal-x11", "source_base_sha256": base_hash,
                            "sha256": builder.digest(image), "size": image.stat().st_size}
                image.with_name(image.name + ".json").write_text(json.dumps(metadata))
                if legacy:
                    (dist / "kernel.txz").write_bytes(kernel.read_bytes())
                else:
                    with self.assertRaisesRegex(ValueError, "--kernel"):
                        builder.stage_distributions(dist, image)
                with patch.object(builder, "run", return_value=SimpleNamespace(stdout="./\n./bin/\n")):
                    result = builder.stage_distributions(dist, image, None if legacy else kernel)
                self.assertEqual(result, metadata)
                self.assertEqual((dist / "base.txz").read_bytes(), image.read_bytes())
                self.assertEqual((dist / "kernel.txz").read_bytes(), kernel.read_bytes())
                self.assertEqual(builder.distribution_hash((dist / "MANIFEST").read_text(), "base.txz"), builder.digest(image))
                self.assertEqual((dist / "MANIFEST").read_text().splitlines()[1], original.splitlines()[1])
                # A wrong kernel must fail before writing any distribution.
                kernel.write_bytes(b"wrong kernel")
                (dist / "MANIFEST").write_text(original)
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    builder.stage_distributions(dist, image, kernel)
                self.assertEqual((dist / "MANIFEST").read_text(), original)

    def test_distribution_hash_rejects_ambiguous_or_malformed_entries(self):
        entry = 'base.txz\t' + 'a' * 64 + '\t1\tbase\t"Base"\ton\n'
        for invalid in ("", entry + entry, entry.replace('a' * 64, "bad")):
            with self.assertRaises(ValueError):
                builder.distribution_hash(invalid, "base.txz")

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
