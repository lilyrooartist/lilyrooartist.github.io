#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python3 scripts/aol_gmail_bridge.py --env ../secrets/aol-gmail-bridge.env "$@"
