# Prepare and use the FreeBSD test VM

This guide follows the setup completed during the migration. It uses the
VirtualBox VM installed from our custom ISO as the test host. Commands specify
whether they run on Windows, as root in FreeBSD, or as a regular FreeBSD user.
The existing working desktop is kept while new changes are built and tested.

## Current verified state

| Step | Evidence and status |
| --- | --- |
| Custom ISO installation | Owner reports successful UEFI/ZFS installation |
| Basic dwm session | Owner reports terminal, tags, close, logout and startup after reboot all pass |
| System identity | SSH verified FreeBSD 15.1-RELEASE amd64 |
| Build dependencies below | SSH verified installed |
| Git | Initially missing; subsequently installed and verified as 2.54.0 |
| SSH public-key access | Verified from Windows over IPv4, localhost port 2244 |
| VirtualBox recovery snapshot | Recommended; creation not yet confirmed |
| Regular-user source checkout and local core gate | Instructions supplied; completion not yet confirmed on this VM |

Existing hosted CI results are separate from running the core gate on this VM.
No new local test result is implied by the installed dependencies.

## 1. Preserve the working VM

Before migration changes, take a VirtualBox snapshot of the working installation.
Give it a descriptive name such as `FreeBSD-15.1-minimal-dwm-working`.
Record the ISO checksum, source commit and VM settings when available.
The initial image test used UEFI and ZFS; BIOS, UFS and physical hardware have
not been covered by that report.

## 2. Install build dependencies as root in FreeBSD

```sh
pkg install git gmake pkgconf libinotify \
  libX11 libXft libXinerama libXrender libxcb xcb-util \
  imlib2 freetype2 fontconfig
```

The custom image already includes most of these. Git was the missing package
on our test VM and was installed separately with `pkg install git`.
FreeBSD base supplies the Clang compiler as `cc`.

For the current VM this step is complete; do not repeat it merely to proceed
with the source checkout. Keep package administration separate from builds.

## 3. Optional SSH access from Windows

Our working endpoint is VirtualBox port forwarding on `127.0.0.1:2244` to the
guest SSH service. An IPv6 connection to localhost failed, so use `ssh -4`.
If creating the forwarding rule, bind it to the host loopback address and
forward TCP host port 2244 to guest port 22.

In the following PowerShell commands, replace `vmuser` with your regular
FreeBSD username. First verify password access and check the server fingerprint
against the VM console before accepting a new host key:

```powershell
ssh -4 -p 2244 vmuser@localhost
```

Create a dedicated key in Windows PowerShell only if you do not already have it:

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\freebsd-c9"
```

Do not overwrite an existing key. If the key has a passphrase, load it into
your configured Windows SSH agent for noninteractive connections. Install only
the public key, once, entering the VM password locally when prompted:

```powershell
Get-Content "$env:USERPROFILE\.ssh\freebsd-c9.pub" |
  ssh -4 -p 2244 vmuser@localhost 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'
```

Verify key authentication without a password prompt:

```powershell
ssh -4 -i "$env:USERPROFILE\.ssh\freebsd-c9" -o BatchMode=yes -o StrictHostKeyChecking=yes -p 2244 vmuser@localhost 'git --version; freebsd-version -kru; uname -m'
```

This step is complete for our current VM. Passwords and private keys must not
be committed to the repository. SSH access is as a regular user; package or
system changes still need a separate privileged operation.

## 4. Create a regular-user checkout

In FreeBSD, log in as the regular user, not root. For a new checkout:

```sh
cd ~
git clone https://github.com/lirux9873/dwm-c9-freebsd.git
cd dwm-c9-freebsd
```

If the checkout already exists under that user's home directory:

```sh
cd ~/dwm-c9-freebsd
git status --short
git branch --show-current
```

If there are local changes, preserve them before switching branches. To test
the merged baseline with a clean checkout:

```sh
git switch main
git pull --ff-only
```

For a specific migration branch, use its explicit review instructions instead.
Do not reuse a root-owned image-builder checkout for regular-user development.

## 5. Run the native core gate as the regular user

```sh
freebsd-version -kru
git rev-parse HEAD
sh tests/test-freebsd-core.sh
```

The gate checks native process handling, performs a clean dwm build and stages
the binary in a private temporary directory. It does not install over the
working desktop and removes its temporary directory when finished.
Keep the output, tested commit and FreeBSD version when reporting a result.
This local gate has not yet been confirmed on our VM.

For an optional inspectable build in the checkout:

```sh
gmake CC=cc clean all
ldd ./dwm
```

Do not run `install.sh`, `gmake install` or `scripts/dev-sync-install.sh` on
FreeBSD. Those general installation paths are still unported.

## 6. Continue desktop validation separately

The installed minimal session starts as the regular user with:

```sh
startx /usr/local/bin/dwm-c9-session
```

Use this from the VM console outside an existing X session, not from the SSH
connection. It starts the installed binary, not the new checkout build.
For automated testing of a newly built binary in a separate Xvfb display, see
the X11 gate in the [FreeBSD guide](https://lirux9873.github.io/dwm-c9-freebsd/install.html#validation-status).

Next migration milestone: shared native dependencies and removal of excluded
integrations. Follow the repository TASKS.md and ROADMAP.md; a working minimal
session does not mean the Quickshell services or complete installer are ported.
