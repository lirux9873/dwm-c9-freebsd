#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELPER="$ROOT_DIR/scripts/dwm-terminal"
BASH_BIN="${BASH:-/usr/bin/bash}"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

mkdir -p "$work/bin" "$work/home/.config/dwm-titus"
export HOME="$work/home"
export XDG_CONFIG_HOME="$HOME/.config"

cat >"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml" <<'EOF'
[vars]
terminal = "alacritty"
EOF

cat >"$work/bin/alacritty" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$0" >"$DWM_TERMINAL_TEST_OUT"
printf '%s\n' "$@" >>"$DWM_TERMINAL_TEST_OUT"
SCRIPT
chmod +x "$work/bin/alacritty"

cat >"$work/bin/kitty" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$0" >"$DWM_TERMINAL_TEST_OUT"
printf '%s\n' "$@" >>"$DWM_TERMINAL_TEST_OUT"
SCRIPT
chmod +x "$work/bin/kitty"

DWM_TERMINAL_TEST_OUT="$work/out" \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER" --class dwm-test

grep -Fqx "$work/bin/alacritty" "$work/out"
grep -Fqx -- "--class" "$work/out"
grep -Fqx "dwm-test" "$work/out"

sed -i.bak 's/terminal = "alacritty"/terminal = "kitty"/' \
	"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml"
DWM_TERMINAL_TEST_OUT="$work/configured-out" \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER" --print-command >"$work/configured-command"
sed -i.bak 's/terminal = "kitty"/terminal = "dwmterm"/' \
	"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml"
cat >"$work/bin/dwmterm" <<'SCRIPT'
#!/bin/sh
printf '%s\n' "$0" >"$DWM_TERMINAL_TEST_OUT"
printf '%s\n' "$@" >>"$DWM_TERMINAL_TEST_OUT"
SCRIPT
chmod +x "$work/bin/dwmterm"

DWM_TERMINAL_TEST_OUT="$work/dwmterm-configured-out" \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER" --print-command >"$work/dwmterm-configured-command"
grep -Fqx dwmterm "$work/dwmterm-configured-command"
rm -f "$work/bin/dwmterm"
sed -i.bak 's/terminal = "dwmterm"/terminal = "alacritty"/' \
	"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml"

cat >>"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml" <<'EOF'
[malformed-section
terminal = "kitty"
EOF
DWM_TERMINAL_TEST_OUT="$work/section-out" \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER" --print-command >"$work/section-command"
grep -Fqx alacritty "$work/section-command"

DWM_TERMINAL_TEST_OUT="$work/default-out" PATH="$work/bin" "$BASH_BIN" "$HELPER"
grep -Fqx "$work/bin/alacritty" "$work/default-out"
DWM_TERMINAL_TEST_OUT="$work/direct-out" PATH="$work/bin" "$BASH_BIN" "$HELPER" -e sh -c "printf direct"
grep -Fqx -- "-e" "$work/direct-out"
grep -Fqx "sh" "$work/direct-out"

cat >"$work/bin/custom-term" <<'SCRIPT'
#!/bin/sh
printf 'custom\n' >"$DWM_TERMINAL_TEST_OUT"
SCRIPT
chmod +x "$work/bin/custom-term"

DWM_TERMINAL_TEST_OUT="$work/custom-out" \
	DWM_TERMINAL=custom-term \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER"

grep -Fqx "custom" "$work/custom-out"

printf '%s\n' '[vars]' 'terminal = not-quoted' \
	>"$XDG_CONFIG_HOME/dwm-titus/hotkeys.toml"
DWM_TERMINAL_TEST_OUT="$work/malformed-out" \
	PATH="$work/bin" \
	"$BASH_BIN" "$HELPER"
grep -Fqx "$work/bin/alacritty" "$work/malformed-out"

rm -f "$work/bin/alacritty" "$work/bin/kitty" "$work/bin/custom-term"

if PATH="$work/bin" "$BASH_BIN" "$HELPER" 2>"$work/err"; then
	echo "dwm-terminal succeeded without a terminal" >&2
	exit 1
fi

grep -Fq "no supported terminal emulator found" "$work/err"

grep -Eq '^[[:space:]]*terminal[[:space:]]*=[[:space:]]*"alacritty"' \
	"$ROOT_DIR/config/hotkeys.toml"
grep -Fq 'key="x",       desc="Terminal"' "$ROOT_DIR/config/hotkeys.toml"
