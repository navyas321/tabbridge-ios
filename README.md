# TabBridge

**Send your open Safari tabs from iPhone/iPad straight into Chrome on your Windows PC or Mac.**

You're reading on your phone, you've got a stack of Safari tabs, and you want them open in Chrome
on your desktop — without emailing yourself links or fishing through iCloud. TabBridge captures
your open Safari tabs on iOS and opens them as real tabs in desktop Chrome.

> **Direction (v1):** **iOS Safari → desktop Chrome (Windows / macOS).** One-way push is the
> product. (Desktop Chrome → iOS Safari is a natural later addition — see [docs/PLAN.md](docs/PLAN.md) §9.)

## Why this direction is the feasible one

The hard wall on iOS is *reading Chrome's tabs* — Chrome on iOS has no extensions and no tab API.
TabBridge sidesteps that entirely by **never touching Chrome on iOS**:

- ✅ **Read all open Safari tabs on iOS** — Safari Web Extension, `browser.tabs.query({})` (with your permission).
- ✅ **Open them in desktop Chrome** — a desktop Chrome extension calls `chrome.tabs.create()`. On
  Windows/macOS the extensions API is *unrestricted* — no `x-callback` hacks, no "tap to continue" stepper.
- ✅ **Private transport** — tab list travels iOS → desktop over a **self-hosted relay on your
  Tailscale tailnet** (or CloudKit for Mac-only). Nothing posted to a third-party server.

The only genuinely version-sensitive unknown is the iOS Safari "read all tabs" permission grant —
everything downstream is well-trodden API.

## Code & status

```
iOS Safari ──POST──▶ relay ──pull──▶ native host ──stdio──▶ Chrome extension ──open──▶ desktop Chrome
```

| Component | Path | Status |
|-----------|------|--------|
| Relay (tab queue, Python stdlib) | [`relay/`](relay) | ✅ implemented + tested |
| Native-messaging host (Python) | [`desktop/native-host/`](desktop/native-host) | ✅ implemented + tested |
| Chrome MV3 extension (opens the tabs) | [`desktop/chrome-extension/`](desktop/chrome-extension) | ✅ implemented (load unpacked) |
| iOS app + Safari Web Extension (capture) | [`ios/`](ios) | ⏳ planned — needs macOS/Xcode |

The **desktop + relay halves run and are tested end-to-end today** (`python run_tests.py`). The iOS
capture side is the remaining build — see [`ios/README.md`](ios/README.md). Desktop setup is in
[`desktop/README.md`](desktop/README.md).

**Designation:** personal tool, with a clear path to a desktop-anchored product.

See the full architecture, verified feasibility, transport options, and `claude.ai/design` UX
prompts in **[docs/PLAN.md](docs/PLAN.md)** and **[docs/FEASIBILITY.md](docs/FEASIBILITY.md)**.
