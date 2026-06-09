#!/usr/bin/env python3
"""Tests for the native-messaging host's framing + dispatch. No deps.

Run:  python desktop/native-host/test_host.py
"""
import io
import struct

import tabbridge_host as h

_failures = []


def check(name, cond):
    print(f"  [{'ok  ' if cond else 'FAIL'}] {name}")
    if not cond:
        _failures.append(name)


def main():
    print("native-host tests:")

    # round-trip a message through encode -> read
    obj = {"cmd": "pull", "n": 3, "s": "héllo"}
    wire = h.encode_message(obj)
    (declared_len,) = struct.unpack("<I", wire[:4])
    check("length prefix matches payload size", declared_len == len(wire) - 4)
    back = h.read_message(io.BytesIO(wire))
    check("encode -> read round-trips (incl. unicode)", back == obj)

    # short/empty stream is clean EOF, not a crash
    check("empty stream -> None (EOF)", h.read_message(io.BytesIO(b"")) is None)
    check("truncated prefix -> None", h.read_message(io.BytesIO(b"\x02\x00")) is None)
    # header promises 10 bytes, body has 3 -> None
    truncated = struct.pack("<I", 10) + b"abc"
    check("truncated body -> None", h.read_message(io.BytesIO(truncated)) is None)

    # dispatch
    check("ping -> pong", h.handle({"cmd": "ping"}) == {"ok": True, "pong": True})
    r = h.handle({"cmd": "bogus"})
    check("unknown cmd -> ok:false", r["ok"] is False and "unknown" in r["error"])
    # pull with no relay configured fails gracefully (no env set in test)
    import os
    os.environ.pop("TABBRIDGE_RELAY", None)
    r = h.handle({"cmd": "pull"})
    check("pull without relay -> graceful error", r["ok"] is False and "RELAY" in r["error"])

    print()
    if _failures:
        print(f"FAILED: {len(_failures)} check(s): {', '.join(_failures)}")
        return 1
    print("All native-host checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
