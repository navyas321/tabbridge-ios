# TabBridge desktop (Windows / macOS)

The desktop half of the pipeline: a **Chrome MV3 extension** + a **native-messaging host**. The
host pulls queued tabs from the [relay](../relay) and the extension opens each one with
`chrome.tabs.create()`.

```
iOS Safari ──POST──▶ relay ──pull──▶ native host ──stdio──▶ Chrome extension ──open──▶ desktop Chrome
```

## Install (one-time)

### 1. Load the extension
1. Open `chrome://extensions`, enable **Developer mode**.
2. **Load unpacked** → select `desktop/chrome-extension`.
3. Copy the extension's **ID** (shown on its card).

### 2. Register the native host
1. Edit [`native-host/com.tabbridge.host.json`](native-host/com.tabbridge.host.json):
   - set `"path"` to the **absolute path** of `run-host.bat` (Windows) or `run-host.sh` (macOS),
   - put your extension ID into `allowed_origins`: `chrome-extension://<ID>/`.
2. Tell the host where the relay is (same secret as the relay):
   - **Windows:** `setx TABBRIDGE_RELAY "http://100.x.y.z:8765"` and `setx TABBRIDGE_TOKEN "…"`
   - **macOS:** export both in the host's launch environment, and `chmod +x run-host.sh`.
3. Register the host manifest:
   - **Windows:** create registry key
     `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.tabbridge.host`
     with its default value = absolute path to `com.tabbridge.host.json`.
   - **macOS:** copy `com.tabbridge.host.json` to
     `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`.

### 3. Use it
Click the TabBridge toolbar button → **Open tabs from phone**. (It also polls once a minute so tabs
can appear automatically; comment out the alarm in `background.js` for manual-only.)

## How the pieces map
- [`chrome-extension/`](chrome-extension) — `background.js` (native messaging + `chrome.tabs.create`),
  `popup.html`/`popup.js` (the "Open tabs from phone" button).
- [`native-host/`](native-host) — `tabbridge_host.py` (stdio framing + relay pull), launch wrappers,
  and the host manifest template. Tests: `test_host.py`, `test_integration.py`.

## Status
Desktop + relay halves are implemented and tested end-to-end (see `../relay` and `native-host`
tests). The **iOS** capture app ([`../ios`](../ios)) still needs to be built on macOS/Xcode.
