#!/usr/bin/env python3
"""End-to-end tests for the TabBridge relay. No third-party deps.

Run:  TABBRIDGE_TOKEN=secret python relay/test_relay.py
(the script sets a token itself if one isn't present).
"""
import json
import os
import threading
import urllib.error
import urllib.request

os.environ.setdefault("TABBRIDGE_TOKEN", "test-secret")
os.environ["TABBRIDGE_HOST"] = "127.0.0.1"
os.environ["TABBRIDGE_PORT"] = "8799"  # avoid clashing with a real relay

import relay  # noqa: E402  (import after env is set)

TOKEN = os.environ["TABBRIDGE_TOKEN"]
BASE = "http://127.0.0.1:8799"
_failures = []


def check(name, cond):
    mark = "ok  " if cond else "FAIL"
    print(f"  [{mark}] {name}")
    if not cond:
        _failures.append(name)


def req(method, path, body=None, token=TOKEN):
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main():
    srv = relay.make_server()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    print("relay tests:")
    try:
        # health (no auth)
        st, body = req("GET", "/health", token=None)
        check("health returns ok", st == 200 and body.get("ok") is True)
        check("health starts empty", body.get("pending") == 0)

        # auth is enforced
        st, _ = req("GET", "/tabs", token=None)
        check("GET /tabs without token -> 401", st == 401)
        st, _ = req("GET", "/tabs", token="wrong")
        check("GET /tabs with bad token -> 401", st == 401)

        # enqueue a batch
        st, body = req("POST", "/tabs", {
            "device": "iPhone",
            "tabs": [
                {"url": "https://example.com", "title": "Example"},
                {"url": "https://news.ycombinator.com", "title": "HN"},
            ],
        })
        check("POST valid batch -> 200", st == 200)
        check("POST reports queued=2", body.get("queued") == 2)

        # junk tabs are filtered (ftp + non-dict dropped; one https kept)
        st, body = req("POST", "/tabs", {"tabs": [
            {"url": "ftp://nope"}, "garbage", {"url": "https://ok.dev", "title": "ok"},
        ]})
        check("POST filters non-http(s) -> queued=1", st == 200 and body.get("queued") == 1)

        # empty/invalid rejected
        st, _ = req("POST", "/tabs", {"tabs": []})
        check("POST empty tabs -> 400", st == 400)

        # drain returns everything, FIFO, then empties
        st, body = req("GET", "/tabs")
        batches = body.get("batches", [])
        check("GET /tabs returns 2 batches", st == 200 and len(batches) == 2)
        check("FIFO order preserved (iPhone first)", batches and batches[0]["device"] == "iPhone")
        check("first batch has 2 tabs", batches and len(batches[0]["tabs"]) == 2)
        check("batch carries a timestamp", batches and isinstance(batches[0]["ts"], int))

        # second drain is empty (consumed)
        st, body = req("GET", "/tabs")
        check("second drain is empty", st == 200 and body.get("batches") == [])

        # 404 for unknown route
        st, _ = req("GET", "/nope", token=None)
        check("unknown route -> 404", st == 404)
    finally:
        srv.shutdown()
        srv.server_close()

    print()
    if _failures:
        print(f"FAILED: {len(_failures)} check(s): {', '.join(_failures)}")
        return 1
    print("All relay checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
