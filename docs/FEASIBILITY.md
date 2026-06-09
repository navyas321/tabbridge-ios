# FEASIBILITY — read this before re-litigating the design

**Direction: iOS Safari → desktop Chrome (Windows / macOS).** Corrected 2026-06-09 from the old
"same-device Safari↔Chrome on iOS" framing. All points verification-confirmed (2025–2026).

## The key insight
The thing iOS makes **impossible** is *reading Chrome's tabs on the phone*. We never do that.
TabBridge **reads Safari on iOS** (supported) and **writes Chrome on the desktop** (supported).
By moving the Chrome side to the desktop, every step lands on a well-supported API.

## What IS possible (the whole pipeline)
- **Read all open Safari tabs on iOS** — Safari Web Extension **background** script,
  `browser.tabs.query({})`, with the `tabs` permission. ⚠️ Verify the all-sites grant UX against the
  target Safari version (bare `tabs` may now suffice; avoid the scary `<all_urls>` prompt if you can).
  **This is the one make-or-break unknown — spike it first.**
- **Open tabs in desktop Chrome** — desktop Chrome MV3 extension, `chrome.tabs.create({url})`.
  Unrestricted on Windows/macOS/Linux: no per-gesture limit, no `x-callback`, no stepper.
- **Feed the desktop extension locally** — Chrome **Native Messaging** connects the extension to a
  native host over stdio. Windows: registry key → manifest path. macOS/Linux: absolute-path JSON
  manifest. *Confirmed.*
- **Move the list iOS → desktop privately** — a **self-hosted relay on the user's Tailscale
  tailnet** (iOS POSTs, desktop pulls). Cross-platform (Windows **and** Mac), no public server, no
  third-party data custody. CloudKit (`CKSyncEngine`) is an optional **Mac-only** alternative.

## What is IMPOSSIBLE / irrelevant on iOS
- **Read Chrome's open or synced tabs on iOS** — no extensions, no read API; sync store is in
  Chrome's private sandbox. *We don't need it — Chrome is read on the desktop, not the phone.*
- **CloudKit on Windows** — doesn't exist; that's why the **relay** is the primary transport.
- **Read iCloud Tabs / observe Handoff** from a third-party app — no API. *Irrelevant: we read
  Safari through our own extension, not via iCloud.*

## Net product shape
**One-way push, all on supported API:** Safari (read, iOS) → private relay (tailnet) → native host
→ Chrome (write, desktop). The only version-sensitive risk is the iOS Safari all-tabs permission
grant. URLs + titles only; nothing posted to a third-party server. A reverse path (desktop Chrome →
iOS Safari) is feasible as a v2 — desktop reads Chrome via `chrome.tabs.query`, iOS Safari opens via
`tabs.create`.
