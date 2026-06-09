#!/usr/bin/env python3
"""TabBridge native-messaging host (desktop).

Chrome launches this process and talks to it over stdin/stdout using the
native-messaging framing: each message is a 4-byte little-endian length prefix
followed by that many bytes of UTF-8 JSON.

The desktop Chrome extension sends `{"cmd": "pull"}`; this host fetches pending
tab batches from the relay (GET /tabs) and returns them, so the extension can
open each URL via chrome.tabs.create(). `{"cmd": "ping"}` -> {"ok": true}.

Config via environment (set in the host's launch context):
    TABBRIDGE_RELAY   relay base URL, e.g. http://100.x.y.z:8765  (required for pull)
    TABBRIDGE_TOKEN   shared secret matching the relay
"""
import json
import os
import struct
import sys
import urllib.request


# ---- native-messaging framing (pure, unit-tested) ----------------------
def encode_message(obj):
    """Serialize obj to the native-messaging wire format (len prefix + JSON)."""
    data = json.dumps(obj, separators=(",", ":")).encode("utf-8")
    return struct.pack("<I", len(data)) + data


def read_message(stream):
    """Read one framed message from a binary stream; None at clean EOF."""
    raw_len = stream.read(4)
    if len(raw_len) < 4:
        return None  # EOF — Chrome closed the pipe
    (length,) = struct.unpack("<I", raw_len)
    payload = stream.read(length)
    if len(payload) < length:
        return None
    return json.loads(payload.decode("utf-8"))


def write_message(stream, obj):
    stream.write(encode_message(obj))
    stream.flush()


# ---- relay client ------------------------------------------------------
def pull_from_relay():
    base = os.environ.get("TABBRIDGE_RELAY", "").rstrip("/")
    token = os.environ.get("TABBRIDGE_TOKEN", "")
    if not base:
        return {"ok": False, "error": "TABBRIDGE_RELAY not set"}
    req = urllib.request.Request(
        base + "/tabs",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return {"ok": True, "batches": body.get("batches", [])}
    except Exception as e:  # noqa: BLE001 — report any failure back to the extension
        return {"ok": False, "error": str(e)}


def handle(msg):
    cmd = (msg or {}).get("cmd")
    if cmd == "ping":
        return {"ok": True, "pong": True}
    if cmd == "pull":
        return pull_from_relay()
    return {"ok": False, "error": f"unknown cmd: {cmd!r}"}


def main():
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        msg = read_message(stdin)
        if msg is None:
            break
        write_message(stdout, handle(msg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
