#!/usr/bin/env python3
"""TabBridge relay — a tiny, dependency-free tab queue.

The iOS app POSTs captured Safari tabs here; the desktop native-messaging host
pulls them and opens them in Chrome. Designed to run privately on the user's
Tailscale tailnet (bind to the tailnet IP, reach it from both Windows and Mac).

Endpoints (all require `Authorization: Bearer <token>`):

    POST /tabs    body: {"tabs": [{"url": "...", "title": "..."}], "device": "iPhone"}
                  -> enqueues the batch, returns {"queued": N}
    GET  /tabs    -> dequeues and returns all pending batches:
                     {"batches": [{"tabs": [...], "device": "...", "ts": 0}]}
    GET  /health  -> {"ok": true, "pending": N}   (no auth)

Storage is an in-memory FIFO queue — the relay is a transient hand-off, not a
database. Tabs not yet pulled are held until a desktop drains them.

Config via environment:
    TABBRIDGE_TOKEN   shared secret (required; refuses to start without it)
    TABBRIDGE_HOST    bind address (default 127.0.0.1; set to your tailnet IP)
    TABBRIDGE_PORT    bind port    (default 8765)
"""
import json
import os
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BATCHES = 1000          # backstop against unbounded growth
MAX_BODY_BYTES = 2 << 20    # 2 MiB — generous for a URL list


class Queue:
    """Thread-safe FIFO of tab batches."""

    def __init__(self):
        self._dq = deque()
        self._lock = threading.Lock()

    def put(self, batch):
        with self._lock:
            self._dq.append(batch)
            while len(self._dq) > MAX_BATCHES:
                self._dq.popleft()  # drop oldest if a desktop never drains

    def drain(self):
        with self._lock:
            items = list(self._dq)
            self._dq.clear()
        return items

    def __len__(self):
        with self._lock:
            return len(self._dq)


QUEUE = Queue()
TOKEN = os.environ.get("TABBRIDGE_TOKEN", "")


def _clean_tabs(raw):
    """Keep only well-formed http(s) tabs; coerce to {url, title}."""
    out = []
    if not isinstance(raw, list):
        return out
    for t in raw:
        if not isinstance(t, dict):
            continue
        url = str(t.get("url", "")).strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            continue
        out.append({"url": url, "title": str(t.get("title", "")).strip()})
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "TabBridgeRelay/0.1"

    # ---- helpers -------------------------------------------------------
    def _send(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _authed(self):
        expected = f"Bearer {TOKEN}"
        got = self.headers.get("Authorization", "")
        # constant-ish time compare to avoid trivial timing leaks
        ok = len(got) == len(expected)
        for a, b in zip(got, expected):
            ok &= (a == b)
        return ok and bool(TOKEN)

    def log_message(self, fmt, *args):  # quieter logging
        sys.stderr.write("[relay] %s\n" % (fmt % args))

    # ---- routes --------------------------------------------------------
    def do_GET(self):
        if self.path == "/health":
            return self._send(200, {"ok": True, "pending": len(QUEUE)})
        if self.path == "/tabs":
            if not self._authed():
                return self._send(401, {"error": "unauthorized"})
            return self._send(200, {"batches": QUEUE.drain()})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/tabs":
            return self._send(404, {"error": "not found"})
        if not self._authed():
            return self._send(401, {"error": "unauthorized"})
        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            return self._send(400, {"error": "bad length"})
        if length <= 0 or length > MAX_BODY_BYTES:
            return self._send(413, {"error": "empty or too large"})
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._send(400, {"error": "invalid json"})
        tabs = _clean_tabs(data.get("tabs"))
        if not tabs:
            return self._send(400, {"error": "no valid http(s) tabs"})
        QUEUE.put({
            "tabs": tabs,
            "device": str(data.get("device", "unknown"))[:64],
            "ts": int(time.time()),
        })
        return self._send(200, {"queued": len(tabs)})


def make_server(host=None, port=None):
    host = host or os.environ.get("TABBRIDGE_HOST", "127.0.0.1")
    port = int(port or os.environ.get("TABBRIDGE_PORT", "8765"))
    return ThreadingHTTPServer((host, port), Handler)


def main():
    if not TOKEN:
        sys.stderr.write(
            "ERROR: set TABBRIDGE_TOKEN to a shared secret before starting.\n"
        )
        return 1
    srv = make_server()
    host, port = srv.server_address
    sys.stderr.write(f"[relay] listening on http://{host}:{port}\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.stderr.write("\n[relay] shutting down\n")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
