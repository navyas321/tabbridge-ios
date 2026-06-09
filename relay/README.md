# TabBridge relay

A tiny, dependency-free tab queue (Python stdlib only). The iOS app POSTs captured Safari tabs
here; the desktop native-messaging host pulls them. Meant to run privately on your **Tailscale
tailnet** so both Windows and macOS desktops can reach it without a public server.

## Run

```bash
# pick a strong shared secret; the iOS app and desktop host must use the same one
export TABBRIDGE_TOKEN="$(python -c 'import secrets;print(secrets.token_urlsafe(32))')"
export TABBRIDGE_HOST="100.x.y.z"   # your tailnet IP (default 127.0.0.1)
export TABBRIDGE_PORT="8765"
python relay.py
```

On Windows PowerShell:

```powershell
$env:TABBRIDGE_TOKEN = "your-shared-secret"
$env:TABBRIDGE_HOST  = "100.x.y.z"
python relay.py
```

## API

| Method | Path      | Auth                       | Purpose |
|--------|-----------|----------------------------|---------|
| POST   | `/tabs`   | `Authorization: Bearer …`  | Enqueue `{"tabs":[{"url","title"}], "device":"iPhone"}` |
| GET    | `/tabs`   | `Authorization: Bearer …`  | Drain + return all pending batches |
| GET    | `/health` | none                       | `{"ok":true,"pending":N}` |

Only `http(s)` URLs are accepted; the queue is an in-memory FIFO (transient hand-off, not storage).

## Test

```bash
python test_relay.py
```
