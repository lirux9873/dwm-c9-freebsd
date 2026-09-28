#!/usr/bin/env python3
"""Build experimental FreeBSD 15.1 amd64 minimal-dwm installation artifacts.

Run as root in a disposable FreeBSD VM. No physical disks are opened. A chroot
is used for package installation and compilation, not as a security sandbox.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
RELEASE = "15.1-RELEASE"
PACKAGES = ["gmake", "pkgconf", "libinotify", "libX11", "libXft", "libXinerama",
            "libXrender", "libxcb", "xcb-util", "imlib2", "freetype2", "fontconfig",
            "xorg", "xterm", "dbus", "noto-sans-mono", "noto-emoji"]
HOTKEYS = '''[vars]
keys = [
  { mod="SUPER", key="Return", func="spawn", exec=["xterm"] },
  { mod="SUPER SHIFT", key="c", func="killclient" },
  { mod="SUPER SHIFT", key="q", func="quit" },
]
tag_keys = [
  { key="1", tag=0 }, { key="2", tag=1 }, { key="3", tag=2 },
  { key="4", tag=3 }, { key="5", tag=4 }, { key="6", tag=5 },
  { key="7", tag=6 }, { key="8", tag=7 }, { key="9", tag=8 },
]
'''
SESSION = '''#!/bin/sh
set -eu
if [ "$(id -u)" -eq 0 ]; then
  echo "Run the X11 session as a regular user." >&2
  exit 1
fi
config=${XDG_CONFIG_HOME:-$HOME/.config}/dwm-titus
mkdir -p "$config"
for name in hotkeys.toml themes.toml window-rules.toml; do
  if [ ! -e "$config/$name" ]; then
    cp -n "/usr/local/share/dwm-c9-freebsd/$name" "$config/$name"
  fi
done
# Keep application data persistent. Refuse inherited session helpers rather
# than running unported Linux scripts or changing the user's files.
export XDG_DATA_HOME=${XDG_DATA_HOME:-$HOME/.local/share}
case "$XDG_DATA_HOME" in /*) ;; *) echo "XDG_DATA_HOME must be absolute" >&2; exit 1;; esac
mkdir -p "$XDG_DATA_HOME/dwm-titus"
for name in scripts/autostart.sh scripts/autostop.sh scripts/theme-apply.sh; do
  if [ -e "$XDG_DATA_HOME/dwm-titus/$name" ]; then
    echo "Review and move the inherited $name before using this minimal session." >&2
    exit 1
  fi
done
exec dbus-run-session -- /usr/local/bin/dwm
'''


def run(*args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verified(path, expected):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise ValueError("Supply a SHA256 from the official FreeBSD CHECKSUM file")
    if digest(path) != expected.lower():
        raise ValueError(f"SHA256 mismatch: {path}")


def host_check():
    if platform.system() != "FreeBSD" or platform.machine() != "amd64":
        raise ValueError("Requires a FreeBSD 15.1 amd64 builder VM")
    version = run("freebsd-version", "-u", capture_output=True, text=True).stdout.strip()
    if not re.fullmatch(r"15\.1-RELEASE(?:-p\d+)?", version):
        raise ValueError(f"Unsupported builder userland: {version}")
    if os.geteuid() != 0:
        raise ValueError("Run as root inside a disposable builder VM")


def publish(staged, output, metadata):
    """Publish with exclusive hard links, never replacing existing artifacts."""
    metadata.update(sha256=digest(staged), size=staged.stat().st_size)
    manifest = output.with_name(output.name + ".json")
    staged_manifest = staged.with_name(staged.name + ".json")
    staged_manifest.write_text(json.dumps(metadata, indent=2) + "\n")
    os.link(staged_manifest, manifest)
    try:
        os.link(staged, output)
    except BaseException:
        manifest.unlink()
        raise


def write(root, name, content, mode=0o644):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(mode)


def build_system(args, work):
    root = work / "root"
    root.mkdir()
    run("tar", "-xpf", args.input, "-C", root)
    # Never execute an archive whose claimed version is incompatible.
    version = (root / "bin/freebsd-version").read_text()
    if not re.search(r'USERLAND_VERSION=[\'\"]15\.1-RELEASE(?:-p\d+)?[\'\"]', version):
        raise ValueError("Input must be the official FreeBSD 15.1 base.txz")
    source = root / "usr/local/src/dwm-c9-freebsd"
    source.mkdir(parents=True)
    snapshot = work / "source.tar"
    with snapshot.open("wb") as stream:
        run("git", "-C", REPO, "archive", "HEAD", stdout=stream)
    run("tar", "-xf", snapshot, "-C", source)
    commit = run("git", "-C", REPO, "rev-parse", "HEAD", capture_output=True, text=True).stdout.strip()
    resolver = root / "etc/resolv.conf"
    resolver.unlink(missing_ok=True)
    shutil.copyfile("/etc/resolv.conf", resolver)
    # Mount only in the new work tree; cleanup must never traverse mounted devfs.
    run("mount", "-t", "devfs", "devfs", root / "dev")
    mounted = True
    try:
        env = {"PATH": "/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin",
               "HOME": "/root", "ASSUME_ALWAYS_YES": "yes", "LC_ALL": "C"}

        def inside(*command, **kwargs):
            return run("chroot", root, *command, env=env, **kwargs)

        inside("/usr/sbin/pkg", "bootstrap", "-y")
        inside("/usr/local/sbin/pkg", "install", "-y", *PACKAGES)
        inside("/usr/local/bin/gmake", "-C", "/usr/local/src/dwm-c9-freebsd", "CC=cc", "clean", "all")
        inside("/usr/bin/install", "-m", "755", "/usr/local/src/dwm-c9-freebsd/dwm", "/usr/local/bin/dwm")
        package_versions = inside("/usr/local/sbin/pkg", "query", "%n-%v", capture_output=True, text=True).stdout.splitlines()
        inside("/usr/local/sbin/pkg", "clean", "-ay")
    finally:
        # If unmount fails, leave the entire work tree for operator recovery.
        run("umount", root / "dev")
        mounted = False
    assert not mounted
    resolver.unlink(missing_ok=True)
    defaults = root / "usr/local/share/dwm-c9-freebsd"
    defaults.mkdir(parents=True)
    for name in ("themes.toml", "window-rules.toml"):
        shutil.copyfile(source / "config" / name, defaults / name)
    write(root, "usr/local/share/dwm-c9-freebsd/hotkeys.toml", HOTKEYS)
    write(root, "usr/local/bin/dwm-c9-session", SESSION, 0o755)
    write(root, "usr/local/share/xsessions/dwm-c9.desktop", "[Desktop Entry]\nName=dwm-c9-freebsd\nType=Application\nExec=/usr/local/bin/dwm-c9-session\n")
    write(root, "usr/local/share/dwm-c9-freebsd/xinitrc.example", "exec /usr/local/bin/dwm-c9-session\n")
    write(root, "usr/local/share/dwm-c9-freebsd/IMAGE-README", "Experimental minimal X11/dwm image. As a regular user run:\nstartx /usr/local/bin/dwm-c9-session\nSuper+Return: terminal; Super+Shift+Q: logout. GPU setup is hardware-specific.\n")
    shutil.rmtree(source)
    staged = work / "system.tar.xz"
    run("tar", "-cJpf", staged, "-C", root, ".")
    return staged, {"kind": "freebsd-dwm-base", "protocol": 1, "release": RELEASE,
                    "architecture": "amd64", "profile": "minimal-x11", "source_base_sha256": args.sha256.lower(),
                    "git_commit": commit, "packages": package_versions,
                    "qualification": "experimental; boot and installation not qualified"}


def validate_system(image, base):
    metadata = json.loads(image.with_name(image.name + ".json").read_text())
    for key, value in {"kind": "freebsd-dwm-base", "protocol": 1, "release": RELEASE,
                       "architecture": "amd64", "profile": "minimal-x11"}.items():
        if metadata.get(key) != value:
            raise ValueError(f"System image manifest mismatch: {key}")
    verified(image, metadata["sha256"])
    if metadata["size"] != image.stat().st_size or metadata["source_base_sha256"] != digest(base):
        raise ValueError("System image must use exactly this ISO's base.txz")
    return metadata


def replace_manifest(text, sha256, count):
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.split("\t")[0] == "base.txz"]
    if len(matches) != 1:
        raise ValueError("Expected exactly one base.txz entry in MANIFEST")
    fields = lines[matches[0]].split("\t")
    if len(fields) < 6:
        raise ValueError("Invalid FreeBSD distribution MANIFEST")
    fields[1:3] = [sha256, str(count)]
    lines[matches[0]] = "\t".join(fields)
    return "\n".join(lines) + "\n"


def build_iso(args, work):
    release_info = (args.freebsd_src / "sys/conf/newvers.sh").read_text()
    if not re.search(r'^REVISION="15\.1"', release_info, re.MULTILINE):
        raise ValueError("--freebsd-src must be a matching FreeBSD 15.1 source tree")
    media = work / "media"
    media.mkdir()
    run("tar", "-xpf", args.input, "-C", media)
    for name in ("boot/cdboot", "boot/loader.efi", "boot/pmbr", "usr/freebsd-dist/base.txz",
                 "usr/freebsd-dist/kernel.txz", "usr/freebsd-dist/MANIFEST"):
        if not (media / name).is_file():
            raise ValueError(f"Requires a FreeBSD amd64 disc1 ISO; missing {name}")
    if (media / "etc/installerconfig").exists():
        raise ValueError("Refusing media with a pre-existing unattended installer")
    dist = media / "usr/freebsd-dist"
    metadata = validate_system(args.system_image, dist / "base.txz")
    shutil.copyfile(args.system_image, dist / "base.txz")
    listing = run("tar", "-tf", dist / "base.txz", capture_output=True, text=True).stdout
    manifest = dist / "MANIFEST"
    manifest.write_text(replace_manifest(manifest.read_text(), digest(dist / "base.txz"), len(listing.splitlines())))
    shutil.copyfile(args.system_image.with_name(args.system_image.name + ".json"), media / "DWM-IMAGE.json")
    write(media, "DWM-README.txt", "FreeBSD 15.1 amd64 with experimental minimal dwm.\nChoose Distribution Sets (NOT Packages/Tech Preview) in the interactive installer.\nInclude the base and kernel sets. The package-based path does not install dwm.\nAfter installation log in as a regular user and run:\nstartx /usr/local/bin/dwm-c9-session\nNo unattended partitioning or default password is configured.\n")
    staged = work / "installer.iso"
    # Use the complete releng/15.1 source tree: this script sources sibling tools.
    script = args.freebsd_src / "release/amd64/mkisoimages.sh"
    run("sh", script, "-b", "C9_151_AMD64", staged, media)
    return staged, {"kind": "freebsd-dwm-installer", "protocol": 1, "release": RELEASE,
                    "architecture": "amd64", "profile": "minimal-x11", "source_iso_sha256": args.sha256.lower(),
                    "system_sha256": metadata["sha256"], "git_commit": metadata["git_commit"],
                    "mkisoimages_sha256": digest(script),
                    "qualification": "experimental; BIOS/UEFI boot and installation not qualified"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installer", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--input", type=Path, required=True, help="Official base.txz (or disc1 ISO in installer mode)")
    parser.add_argument("--sha256", required=True, help="Trusted SHA256 for --input from official release checksums")
    parser.add_argument("--output", type=Path, required=True, help="New .tar.xz (or .iso); adjacent .json is also created")
    parser.add_argument("--disposable-vm", action="store_true", help="Acknowledge this is a disposable FreeBSD builder VM")
    parser.add_argument("--system-image", type=Path, help="Installer mode: root filesystem and adjacent JSON manifest")
    parser.add_argument("--freebsd-src", type=Path, help="Installer mode: complete matching releng/15.1 source tree")
    args = parser.parse_args(argv)
    if not args.disposable_vm:
        parser.error("--disposable-vm is required; package scripts execute in a privileged chroot")
    if args.installer != bool(args.system_image and args.freebsd_src):
        parser.error("Installer mode requires --system-image and --freebsd-src")
    if not args.installer and (args.system_image or args.freebsd_src):
        parser.error("--system-image and --freebsd-src are installer-only")
    args.input = args.input.resolve(strict=True)
    args.output = args.output.absolute()
    suffix = ".iso" if args.installer else ".tar.xz"
    if not args.output.name.endswith(suffix):
        parser.error(f"Output must end with {suffix}")
    for path in (args.output, args.output.with_name(args.output.name + ".json")):
        if path.exists() or path.is_symlink():
            parser.error(f"Output already exists: {path}")
    host_check()
    verified(args.input, args.sha256)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=".dwm-freebsd-", dir=args.output.parent))
    # Keep failed workspaces for inspection, especially if a mount cannot detach.
    try:
        staged, metadata = (build_iso if args.installer else build_system)(args, work)
        publish(staged, args.output, metadata)
    except BaseException:
        print(f"Build failed; retained workspace (check mounts before cleanup): {work}", file=sys.stderr)
        raise
    run("chflags", "-R", "noschg", work)
    shutil.rmtree(work)
    print(f"Created experimental artifact: {args.output}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
