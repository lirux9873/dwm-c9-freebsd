#!/bin/bash
# Runs only inside the disposable factory installer target, never on the host.
set -euo pipefail
[[ ${1:-} == --factory-target && -f /etc/dwm-titus-factory-target ]]
[[ $(id -u) == 0 && $(getent passwd imagebuilder | cut -d: -f6) == /home/imagebuilder ]]
# shellcheck disable=SC1091
source /etc/os-release
[[ $ID == fedora && $VERSION_ID == 44 ]]
variant=$(cat /etc/dwm-titus-factory-target)
[[ $variant == standard || $variant == nvidia ]]
source_dir=/home/imagebuilder/.local/share/dwm-titus
install -d /usr/share/dwm-titus-image /usr/local/share/fonts/dwm-titus
cp -a "$source_dir"/. /usr/share/dwm-titus-image/
# Refresh only the official Fedora PackageKit packages. A release-only backport
# cannot be identified by an unprivileged client on the default procfs policy.
dnf --repo=fedora --repo=updates upgrade -y PackageKit PackageKit-glib libdnf5
python3 /usr/share/dwm-titus-image/scripts/image/check-packagekit.py
bash /usr/share/dwm-titus-image/scripts/image/install-tools.sh
# Fedora intentionally hides sxiv. Override that desktop ID system-wide so
# it is discoverable without modifying the RPM-owned entry or its MIME list.
install -d /usr/local/share/applications
sed 's/^NoDisplay=true$/NoDisplay=false/' /usr/share/applications/sxiv.desktop \
	>/usr/local/share/applications/sxiv.desktop
desktop-file-validate /usr/local/share/applications/sxiv.desktop
update-desktop-database /usr/local/share/applications
cp -a /home/imagebuilder/.local/share/fonts/. /usr/local/share/fonts/dwm-titus/
# User configuration is generated offline for the real account at installation.
fc-cache -f
rpm -qa --qf '%{NAME}-%{EPOCHNUM}:%{VERSION}-%{RELEASE}.%{ARCH}\n' | sort >/usr/share/dwm-titus-image/rpm-manifest.txt
printf 'protocol=1\nvariant=%s\nfedora=44\narchitecture=x86_64\n' "$variant" >/etc/dwm-titus-image
[[ -x /usr/local/bin/dwm && -f /usr/share/xsessions/dwm.desktop ]]
printf 'DWM_FACTORY_PREPARED\n'
