#!/usr/bin/env bash
# Install receipt-compresser as a launchd LaunchAgent (starts at login, restarts on crash).
# Usage: ./install.sh [WATCH_DIR] [SAVE_DIR]
#        ./install.sh --uninstall
set -euo pipefail

LABEL="com.receipt-compresser"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

if [[ "${1:-}" == "--uninstall" ]]; then
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Uninstalled $LABEL"
    exit 0
fi

WATCH_DIR="${1:-$HOME/Pictures/Receipts}"
SAVE_DIR="${2:-$WATCH_DIR/Compressed}"

# Create a venv inside the project and install dependencies
if [[ ! -x "$PROJECT_DIR/.venv/bin/python" ]]; then
    python3 -m venv "$PROJECT_DIR/.venv"
fi
"$PROJECT_DIR/.venv/bin/pip" install -q -r "$PROJECT_DIR/requirements.txt"

mkdir -p "$WATCH_DIR" "$SAVE_DIR" "$HOME/Library/LaunchAgents" "$HOME/Library/Logs"

sed -e "s|__PYTHON__|$PROJECT_DIR/.venv/bin/python|g" \
    -e "s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    -e "s|__WATCH_DIR__|$WATCH_DIR|g" \
    -e "s|__SAVE_DIR__|$SAVE_DIR|g" \
    -e "s|__HOME__|$HOME|g" \
    "$PROJECT_DIR/launchd/$LABEL.plist.template" > "$PLIST"

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"

echo "Installed and started $LABEL"
echo "  watching: $WATCH_DIR"
echo "  saving:   $SAVE_DIR"
echo "  logs:     $HOME/Library/Logs/receipt-compresser.log"
