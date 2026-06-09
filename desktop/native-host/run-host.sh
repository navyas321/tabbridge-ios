#!/usr/bin/env bash
# TabBridge native-messaging host launcher (macOS / Linux).
# Chrome registers THIS script as the host "path"; it hands stdio to Python.
# Set TABBRIDGE_RELAY and TABBRIDGE_TOKEN in the environment (e.g. a launchd
# plist or your shell profile) so the host can reach the relay.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$DIR/tabbridge_host.py"
