#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_DIR/../secrets/aol-gmail-bridge.env"
SOURCE_STATE_FILE="$REPO_DIR/../secrets/aol-gmail-bridge-state.json"
RUNTIME_DIR="$HOME/Library/Application Support/LilyRoo/AOLGmailBridge"
RUNTIME_ENV="$RUNTIME_DIR/aol-gmail-bridge.env"
RUNTIME_STATE="$RUNTIME_DIR/aol-gmail-bridge-state.json"
LOG_FILE="$RUNTIME_DIR/aol-gmail-bridge.log"
RUNNER="$RUNTIME_DIR/aol-gmail-bridge-launchd-runner.sh"
BRIDGE="$RUNTIME_DIR/aol_gmail_bridge.py"
PLIST="$HOME/Library/LaunchAgents/com.lilyroo.aol-gmail-bridge.plist"
LABEL="com.lilyroo.aol-gmail-bridge"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if ! grep -q '^AOL_APP_PASSWORD=.\+' "$ENV_FILE" || ! grep -q '^GMAIL_APP_PASSWORD=.\+' "$ENV_FILE"; then
  echo "Add AOL_APP_PASSWORD and GMAIL_APP_PASSWORD to $ENV_FILE before installing launchd." >&2
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$RUNTIME_DIR"
chmod 600 "$ENV_FILE"
touch "$LOG_FILE"
chmod 600 "$LOG_FILE"
cp "$REPO_DIR/scripts/aol_gmail_bridge.py" "$BRIDGE"
chmod 700 "$BRIDGE"

grep -v '^STATE_PATH=' "$ENV_FILE" > "$RUNTIME_ENV"
printf 'STATE_PATH=%s\n' "$RUNTIME_STATE" >> "$RUNTIME_ENV"
chmod 600 "$RUNTIME_ENV"

if [[ -f "$SOURCE_STATE_FILE" && ! -f "$RUNTIME_STATE" ]]; then
  cp "$SOURCE_STATE_FILE" "$RUNTIME_STATE"
  chmod 600 "$RUNTIME_STATE"
fi

cat > "$RUNNER" <<RUNNER
#!/usr/bin/env bash
set -euo pipefail

while true; do
  date -u +"[%Y-%m-%dT%H:%M:%SZ] AOL Gmail bridge run"
  python3 "$BRIDGE" --env "$RUNTIME_ENV" || true
  sleep 300
done
RUNNER
chmod 700 "$RUNNER"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$RUNNER</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>StandardOutPath</key>
  <string>$LOG_FILE</string>
  <key>StandardErrorPath</key>
  <string>$LOG_FILE</string>
</dict>
</plist>
PLIST

chmod 600 "$PLIST"
launchctl bootout "gui/$(id -u)" "$PLIST" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
launchctl enable "gui/$(id -u)/$LABEL"
launchctl kickstart -k "gui/$(id -u)/$LABEL"

echo "Installed $LABEL"
echo "Log: $LOG_FILE"
