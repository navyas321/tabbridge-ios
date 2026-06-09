#!/usr/bin/env python3
"""Integration test: relay + native host together.

Simulates the desktop half of the pipeline:
  1. start the relay
  2. POST a tab batch (as the iOS app would)
  3. point the host at the relay and call its `pull` handler (as Chrome would)
  4. assert the host returns exactly those tabs

Run:  python desktop/native-host/test_integration.py
"""
import json
import os
import sys
import threading
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "relay"))
sys.path.insert(0, HERE)

TOKEN = "integration-secret"
PORT = "8801"
os.environ["TABBRIDGE_TOKEN"] = TOKEN
os.environ["TABBRIDGE_HOST"] = "127.0.0.1"
os.environ["TABBRIDGE_PORT"] = PORT
os.environ["TABBRIDGE_RELAY"] = f"http://127.0.0.1:{PORT}"

import relay            # noqa: E402
import tabbridge_host as host  # noqa: E402

_failures = []


def check(name, cond):
    print(f"  [{'ok  ' if cond else 'FAIL'}] {name}")
    if not cond:
        _failures.append(name)


def main():
    srv = relay.make_server()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("integration (relay + host):")
    try:
        # 1. iOS app POSTs a batch
        payload = json.dumps({
            "device": "iPhone 16",
            "tabs": [
                {"url": "https://apple.com", "title": "Apple"},
                {"url": "https://github.com/navyas321", "title": "GitHub"},
            ],
        }).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{PORT}/tabs",
            data=payload,
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            posted = json.loads(resp.read().decode())
        check("iOS POST accepted (queued=2)", posted.get("queued") == 2)

        # 2. Chrome -> host: pull
        result = host.handle({"cmd": "pull"})
        check("host pull ok", result.get("ok") is True)
        batches = result.get("batches", [])
        check("host received 1 batch", len(batches) == 1)
        urls = [t["url"] for b in batches for t in b["tabs"]]
        check("host surfaced both URLs in order",
              urls == ["https://apple.com", "https://github.com/navyas321"])
        check("device label carried through", batches and batches[0]["device"] == "iPhone 16")

        # 3. second pull is empty (relay drained)
        again = host.handle({"cmd": "pull"})
        check("second pull is empty", again.get("ok") is True and again.get("batches") == [])
    finally:
        srv.shutdown()
        srv.server_close()

    print()
    if _failures:
        print(f"FAILED: {len(_failures)} check(s): {', '.join(_failures)}")
        return 1
    print("All integration checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
