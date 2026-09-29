# Rebuild the native FreeBSD Quickshell desktop

This is the complete sequence to reproduce our working FreeBSD 15.1 amd64/X11
installation. The owner has confirmed the graphical session works in the
VirtualBox VM installed from the custom ISO (UEFI/ZFS). Automated checks also
cover a separate Xvfb display. Hardware-specific features have the limits below.

The tested desktop implementation is commit
`e1f9423c1fc76cb211088b3828fae992373c5196`, merged into main by PR #11.
Package repositories evolve: these steps reproduce the installation method,
not a byte-identical image or an exact set of package versions.

## 1. Obtain the working FreeBSD base

To rebuild the ISO as well, first follow
[the complete image-builder guide](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-IMAGES.md)
in a disposable FreeBSD 15.1 builder VM. It covers trusted input checksums,
base filesystem creation, the matching kernel, ISO creation and installation.
Keep both generated artifacts with their JSON manifests.

Install that ISO into a fresh VirtualBox VM, using the documented Distribution
Sets path. Our tested installation uses UEFI and ZFS. Create a regular desktop
user during installation, configure networking, reboot and verify the minimal
session from the VM console as that user:

```sh
startx /usr/local/bin/dwm-c9-session
```

Super+Enter opens a terminal; Super+Shift+Q logs out. Take a VM snapshot once
this works. Continue below after logout. The custom ISO contains the minimal
desktop, not Quickshell: the following steps add the graphical shell.

An existing FreeBSD 15.1 amd64 installation can also use the source installer,
but first configure a working Xorg environment for its GPU. See the
[FreeBSD X11 handbook](https://docs.freebsd.org/en/books/handbook/x11/).
That alternative does not automatically provide the original dwm-c9-session
fallback command. The complete path tested here starts from our custom ISO.

## 2. Install Git and clone as your regular user

As root in FreeBSD (not in Windows), ensure Git is installed:

```sh
pkg install git
```

Then log in as your regular desktop user. Do not use a root-owned image-builder
checkout for these steps:

```sh
cd "$HOME"
git clone https://github.com/lirux9873/dwm-c9-freebsd.git
cd dwm-c9-freebsd
git rev-parse HEAD
pwd
```

If you already have a clean checkout, use `git switch main` and
`git pull --ff-only` instead of cloning again. Preserve local edits first.
For the exact tested source, optionally run:

```sh
git switch --detach e1f9423c1fc76cb211088b3828fae992373c5196
```

Record the commit and the absolute checkout directory printed by `pwd`.

## 3. Install the native dependency profile as root

Open a root shell. Start POSIX sh so the following syntax works regardless of
the root account's default shell. Replace `/home/YOUR_USER/dwm-c9-freebsd`
with the exact checkout path from step 2:

```sh
sh
cd /home/YOUR_USER/dwm-c9-freebsd
pkg update
packages=$(sh scripts/dwm-freebsd-packages.sh desktop)
pkg install -n $packages
```

Review the proposed transaction, then install it in the same shell:

```sh
pkg install $packages
```

This includes the compiler's library dependencies, Xorg/xterm, D-Bus, fonts,
Quickshell, Python, Bash, feh, xdotool, xprop and GLib. FreeBSD base supplies Clang.
Do not substitute Linux packages. If pkg cannot find quickshell for your ABI,
stop and resolve the repository mismatch rather than installing another ABI.

Leave the root login and return to your regular user for every remaining step.
No sudo or doas configuration is required by this guide.

## 4. Build and install the desktop as your regular user

```sh
cd "$HOME/dwm-c9-freebsd"
freebsd-version -u
id -un
python3 scripts/install-freebsd-desktop.py
```

The version must be FreeBSD 15.1-RELEASE (including supported patch suffixes),
and `id -un` must not report root. The installer builds dwm with GNU make and
installs the native shell under `~/.local/share/dwm-c9-freebsd`.
Its successful output includes `Installed:` and a `startx` command.

The installation contains:

- `releases/`: versioned dwm, helpers and Quickshell code;
- `current`: the selected release;
- `config/dwm-titus/`: persistent, editable native TOML settings;
- `data/`, `cache/`, `state/`: native-session application data;
- `logs/session.log`: startup/runtime diagnostics;
- `start-session`: the entry point used below.

Existing TOML files are preserved. The installer leaves the system desktop and
normal `~/.config` settings alone. Quickshell code in releases is managed;
change source and reinstall instead of editing generated release files.
Do not run the inherited `install.sh`, `gmake install` or source-sync installer.

## 5. Start and verify the graphical shell

From the VirtualBox console as the regular user, outside an existing X session
(not from SSH):

```sh
startx "$HOME/.local/share/dwm-c9-freebsd/start-session"
```

You should see a top panel with Apps, nine workspaces, the active-window title,
Notifications, System and a clock. Check:

1. Super+Enter opens a terminal.
2. Super+D opens the searchable application launcher; search for XTerm and launch it.
3. Super+2 and Super+1 switch workspaces; clicking workspace buttons also works.
4. Super+S opens native volume/system controls; Super+N opens notification history.
5. Super+Shift+C closes a window; Super+Shift+Q logs out.
6. Run the same startx command again to verify a second session starts cleanly.

Super is the Windows key. Do not overwrite `.xinitrc`; the explicit command
selects this session. No automatic login or display manager is configured.

## Themes and wallpaper

The native desktop ships Nord, Dracula, Gruvbox and Tokyo Night palettes.
Open **System** with Super+S and click a theme name. The choice is saved in
`config/dwm-titus/themes.toml` below the installation directory. dwm and the
Quickshell panel update immediately; newly opened terminals use the palette too.

FreeBSD provides `feh` as a native package, and the desktop dependency profile
installs it. To set a wallpaper, use an absolute or home-relative image path
while the graphical session is running:

```sh
dwm-freebsd-appearance wallpaper "$HOME/Pictures/backgrounds/my-wallpaper.jpg" fill
```

Supported modes are `fill`, `max`, `scale`, `center` and `tile`. The selection
is stored in the native desktop configuration and reapplied at every login.
To remove it and return to the active theme's solid background:

```sh
dwm-freebsd-appearance clear-wallpaper
```

List or select themes from a terminal with:

```sh
dwm-freebsd-appearance themes
dwm-freebsd-appearance theme dracula
```

The helper accepts regular local JPG, PNG, WebP and BMP files. It does not
download images. Existing custom `themes.toml` files are preserved on update;
the exact original one-theme native default is migrated to the new palette set.

## 6. Update, roll back or use the original desktop

Log out before updating. As your regular user in a clean checkout:

```sh
cd "$HOME/dwm-c9-freebsd"
git switch main
git pull --ff-only
python3 scripts/install-freebsd-desktop.py
```

If the package profile changed, repeat step 3 first. A new release is built;
your native TOML edits remain. If an update fails before activation, the current
release stays selected. To restore the previous release after an update:

```sh
python3 scripts/install-freebsd-desktop.py --rollback
```

Rollback requires a previous successful installation, preserves current user
settings and does not downgrade pkg packages. On the custom-ISO installation,
the original minimal desktop remains available at any time after logout:

```sh
startx /usr/local/bin/dwm-c9-session
```

## 7. Optional developer regression checks

Normal use does not require these tests. For a development checkout, install
the additional test packages as root using the same POSIX-shell approach:

```sh
sh
cd /home/YOUR_USER/dwm-c9-freebsd
packages=$(sh scripts/dwm-freebsd-packages.sh test)
pkg install $packages
```

Then, as your regular user:

```sh
cd "$HOME/dwm-c9-freebsd"
python3 tests/test-freebsd-packages.py
python3 tests/test-freebsd-session-launch.py
env DWM_FREEBSD_X11_SMOKE=1 sh tests/test-freebsd-core.sh
python3 tests/test-freebsd-installer.py
```

For the Quickshell integration test, use a separate disposable prefix. These
commands assume POSIX sh; run `sh` first if your login shell is csh/tcsh:

```sh
work=$(mktemp -d /tmp/c9-desktop-validation.XXXXXXXX)
python3 scripts/install-freebsd-desktop.py --prefix "$work/desktop"
dbus-run-session -- python3 tests/test-freebsd-quickshell.py "$work/desktop"
printf 'Retained test files: %s\n' "$work"
```

The test uses Xvfb, launches applications, sends a test notification, checks the
panel reservation and logs out. Keep its output for a bug report. The installed
desktop in your home directory is not the test target.

## What works and what remains

| Feature | Native profile |
| --- | --- |
| Panel/workspaces/window title | Tested with real dwm and Quickshell on Xvfb |
| Application search and launch | Tested using installed desktop entries |
| Notifications and history | D-Bus delivery and history tested |
| Tray | Included; individual third-party tray apps not qualified |
| Volume and mute | Native FreeBSD mixer controls; availability depends on device permissions |
| Network | Read-only IPv4 interface status; no Wi-Fi editor |
| Battery and load | Native sysctl/load data; unavailable battery is reported explicitly |
| Bluetooth, brightness, suspend, lock | Not included in this profile |
| Themes and wallpaper | Four live palettes; persistent local wallpaper through native feh |
| Full inherited Settings / package updates | Not included; no privileged Fedora helpers run |

The Quickshell package is quickshell-0.3.0_1 on the test VM. Qt Quick defaults
to software rendering for VirtualBox/Xvfb; QT_QUICK_BACKEND can override it.
The current panel targets one screen. VirtualBox console startup is owner-confirmed. Physical GPU, multimonitor,
audible audio output and laptop power hardware still require device testing.

## Troubleshooting and validation

Session log: ~/.local/share/dwm-c9-freebsd/logs/session.log.
The session refuses an already managed X display; log out before starting it.
It uses a private runtime directory and a session D-Bus when none is present.
The graphical shell and dwm stop together on logout or shell failure.

See [native validation evidence](https://github.com/lirux9873/dwm-c9-freebsd/blob/main/docs/FREEBSD-QUICKSHELL-REVIEW.md).
