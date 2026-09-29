#!/bin/bash
# Required image tools, downloaded and verified only in the disposable factory.
set -euo pipefail
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
[[ $(id -u) == 0 && -f /etc/dwm-titus-factory-target && $(uname -m) == x86_64 ]]
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
starship_version=1.26.0
starship_sha=b7c232b0e8249d8e55a40beb79c5c43a7d370f3f9408bd215deb0170daeaadf3
printf 'Downloading required Starship %s (SHA-256 verified)\n' "$starship_version"
curl --fail --location --silent --show-error --retry 3 --connect-timeout 10 --max-time 120 \
	"https://github.com/starship/starship/releases/download/v$starship_version/starship-x86_64-unknown-linux-musl.tar.gz" \
	-o "$work/starship.tar.gz"
printf '%s  %s\n' "$starship_sha" "$work/starship.tar.gz" | sha256sum --check --status
tar -xzf "$work/starship.tar.gz" -C "$work" starship
install -o root -g root -m 0755 "$work/starship" /usr/local/bin/starship
install -d /usr/local/share/doc/starship
install -m 0644 /usr/share/dwm-titus-image/docs/licenses/starship-LICENSE /usr/local/share/doc/starship/LICENSE
starship --version
sha256sum /usr/local/bin/starship >/usr/share/dwm-titus-image/tool-sha256.txt
