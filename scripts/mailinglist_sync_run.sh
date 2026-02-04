#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Activate venv
source .venv-mailingsync/bin/activate

python scripts/mailinglist_sync.py --config mailinglist_sync_config.json
