# FEASIBILITY — read this before re-litigating the design

Written down so we don't re-argue the asymmetry. All points verification-confirmed (2025-2026).

## What is IMPOSSIBLE on iOS (non-jailbroken)
- **Read Chrome's open or synced tabs.** Chrome iOS has no extensions and no read API/URL scheme. Its Google-account sync store is inside Chrome's private sandbox container — unreadable by other apps. (It *is* readable on **desktop** via the Sync LevelDB — that's the commercial pivot, not an iOS path.)
- **Read iCloud Tabs / observe Handoff** from a third-party app. `NSUserActivity`/Handoff is same-app continuation only; iCloud Tabs live in Safari's private CloudKit scope.
- Therefore **true bidirectional, live, automatic open-tab sync is impossible.** Don't promise it.

## What IS possible
- **Read all open Safari tabs** from a Safari Web Extension **background** script via `browser.tabs.query({})` (needs the `tabs` permission; verify the exact all-sites grant UX against the target Safari version — bare `tabs` may now suffice; avoid the scary `<all_urls>` prompt if you can).
- **Push a URL into Chrome** via `googlechrome-x-callback://x-callback-url/open/?url=…&create-new-tab=true` (write-only). Multi-tab push chains on `x-success`; opening Chrome backgrounds our app, so reliability depends on Chrome returning focus → ship a **"tap to continue" stepper** as the robust fallback, and fall back to plain `https` open if `x-success` stops firing.
- **Capture one Chrome tab → our queue** via a Share Extension (one page at a time, user-initiated).
- **Open a URL in Safari** via `tabs.create` or `UIApplication.open(https://…)`.

## Net product shape
Asymmetric bridge: **Safari = auto-read**, **Chrome = manual-capture + push target**. Keep all data on-device / user-iCloud, never POST URLs to a server (App Review). The honesty about the asymmetry is the product's credibility.
