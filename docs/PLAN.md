# TabBridge — Plan

_Originally scoped as Safari↔Chrome **on the same iOS device**. **Corrected 2026-06-09** to the
real goal: **push open Safari tabs from iOS to Chrome on a Windows PC or Mac.** Re-researched and
adversarially verified. Verification notes are marked ⚠️._

## 1. TL;DR
Capture the user's open **Safari tabs on iOS** (Safari Web Extension) and **open them as real tabs
in desktop Chrome** on Windows/macOS, via a **desktop Chrome extension + native-messaging host**.
The tab list travels iOS → desktop over a **private self-hosted relay on the user's Tailscale
tailnet** (CloudKit is an optional Mac-only path). This direction deliberately **avoids reading
Chrome on iOS** — the one thing iOS makes impossible — so every step is on supported API.

## 2. Why the direction changed (and why it's stronger)
The previous plan tried to move tabs **between Safari and Chrome on the same iPhone**. That ran
straight into iOS's hard wall: **Chrome on iOS has no extensions and no readable tab API**, forcing
an awkward write-only `googlechrome-x-callback://` push and a "tap to continue" stepper.

Targeting **desktop Chrome** removes that wall:
- Desktop Chrome has the **full `chrome.tabs` API** — `chrome.tabs.create({url})` opens tabs with
  no per-gesture limit and no callback gymnastics. *(This was already noted in the old plan as the
  "desktop-only readable path" / commercial pivot — it's now the core product.)*
- We only ever **read Safari** (fully supported on iOS) and **write Chrome** (fully supported on
  desktop). Nothing depends on the impossible iOS-Chrome read.

## 3. Feasibility — verified hard constraints (2026)
- ✅ **Read all open Safari tabs on iOS**: Safari Web Extension **background** script,
  `browser.tabs.query({})`, with the `tabs` permission. ⚠️ The exact "Allow on Every Website" grant
  UX is Safari-version-dependent — bare `tabs` *should* now surface an all-sites grant; avoid the
  scarier `<all_urls>` prompt if possible. **This is still the one make-or-break unknown — spike it first.**
- ✅ **Open tabs in desktop Chrome**: `chrome.tabs.create({url, active})` from a desktop Chrome
  (MV3) extension. Unrestricted on Windows/macOS/Linux. *Confirmed.*
- ✅ **Feed the desktop extension from a local agent**: Chrome **Native Messaging** — extension
  ↔ a native host process over stdio. Windows registers the host via a registry key
  (`HKCU\Software\Google\Chrome\NativeMessagingHosts\<name>` → manifest path); macOS/Linux use an
  absolute-path JSON manifest in the NativeMessagingHosts dir. `connectNative` for a persistent
  pull, `sendNativeMessage` for one-shots. *Confirmed — [Chrome docs](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging).*
- ✅ **Transport iOS → desktop (cross-platform)**: a **self-hosted relay** the iOS app POSTs to and
  the desktop agent reads from. Running it on the user's **Tailscale tailnet** gives private,
  authenticated connectivity to **both Windows and Mac** with no public server and no third-party
  data custody. (Prior art for the pattern: [xBrowserSync](https://www.xbrowsersync.org/) self-hosts open-tab/bookmark sync.)
- ⚠️ **CloudKit (`CKSyncEngine`)** syncs iOS↔**macOS** natively but **does not reach Windows** (no
  CloudKit on Windows). Use it only as a Mac-only convenience path, not the primary transport.
- ❌ **iCloud Tabs / Handoff** still expose **no third-party read API** — but this is now irrelevant,
  since we read Safari through our own extension rather than scraping iCloud.

**Verdict:** **iOS Safari → desktop Chrome push is fully feasible on supported APIs.** The only real
risk is the iOS Safari all-tabs permission UX; the desktop and transport halves are routine.

## 4. Recommended architecture
Three cooperating pieces:

**(A) iOS app + Safari Web Extension**
- Safari Web Extension (MV3, non-persistent background): `browser.tabs.query({})` enumerates open
  tabs → `browser.runtime.sendNativeMessage` → `SafariWebExtensionHandler` (Swift) → App Group store.
- SwiftUI container app: review/select captured tabs, "Send to desktop", history, consent, settings.

**(B) Transport — private relay (primary) / CloudKit (Mac-only, optional)**
- **Relay:** a tiny HTTPS service (e.g. a small Go/Node binary) the user runs on their **tailnet**
  — likely co-located with the desktop or on an always-on host. iOS `POST /tabs` (JSON: list of
  `{url, title, ts}`), desktop `GET /tabs` (long-poll or pull). Auth via a shared device token;
  TLS provided by Tailscale. Payload is just URLs + titles, queued and consumed.
- **CloudKit (`CKSyncEngine`) private DB:** zero-infra option for **Mac** desktops only.

**(C) Desktop Chrome extension + native-messaging host (Windows/macOS)**
- Native host (small native app/agent): pulls the tab list from the relay (or watches CloudKit on
  Mac) and forwards it to the extension over native messaging.
- Chrome MV3 extension: receives the list and calls `chrome.tabs.create({url})` for each — opening
  them in a chosen window, optionally grouped. A toolbar popup shows "N tabs incoming → Open all".

**Data:** iOS App Group (GRDB/SQLite) for the local queue; relay holds only an in-flight queue; no
long-term server storage. **URLs + titles only.**

## 5. Tech stack
Swift 6 / SwiftUI · Safari Web Extension (MV3, TS background) · `SafariWebExtensionHandler` ·
App Groups + GRDB · **Tailscale-hosted relay (Go or Node, ~one file)** · optional CloudKit
(`CKSyncEngine`) · **desktop Chrome MV3 extension** + **Native Messaging host** (Go/Rust/Node;
Windows registry-registered, macOS abs-path manifest) · GitHub Actions (`xcodebuild`/fastlane for
iOS TestFlight; cross-compile the host for Win/Mac).

## 6. UX — design these in claude.ai/design
Screens: (1) **Onboarding/Permission Primer** — explain the one-time Safari all-tabs grant + how to
pair a desktop (scan a code / enter a tailnet address + token); (2) **Captured Tabs** (home) —
open Safari tabs with multi-select and a prominent **"Send to <desktop name>"**; (3) **Devices** —
paired desktops, online/offline, last-synced; (4) **Settings** — transport (Tailnet relay /
CloudKit), consent, clear-data, privacy explainer; (5) **Safari extension popup** — "Capture N open
tabs." Plus the **desktop Chrome popup** — "N tabs from iPhone → Open all / Open in new window."

**Prompt for claude.ai/design:**
> Design a clean, trustworthy utility called TabBridge that sends open Safari tabs from an iPhone to
> Chrome on a desktop PC/Mac. iOS screens: an onboarding screen explaining a one-time "allow reading
> your Safari tabs" grant and a desktop-pairing step (scan a code or enter an address + token); a
> captured-tabs list with multi-select and a prominent "Send to <desktop>" button; a Devices screen
> showing paired desktops with online/offline status; a privacy-forward settings screen with a
> transport choice (private tailnet relay vs iCloud, Mac only). Also design the desktop Chrome
> extension popup: "12 tabs from iPhone — Open all / Open in new window." Visual tone: native, SF
> Symbols, neutral with one accent color, privacy-reassuring, no dark patterns. Light + dark, plus an
> empty state for the captured-tabs list.

## 7. Positioning
- **Designation:** personal tool. The honest pitch — read Safari on iOS, open desktop Chrome over
  your own private relay — has no asterisk and needs no third-party server.
- **License:** Apache-2.0 (see [LICENSE](../LICENSE) / [NOTICE](../NOTICE)). Permissive, with an
  explicit patent grant; the "TabBridge" name is not licensed.
- **Self-hosting:** the relay is designed to run on the user's own Tailscale tailnet — one
  always-on tailnet service can carry it alongside other personal services.

## 8. Repo scaffold (target)
```
ios/
  TabBridge.xcodeproj           # App + SafariWebExtension targets
  App/                          # SwiftUI: TabBridgeApp, CapturedTabsView, DevicesView, OnboardingView, SettingsView
  App/Store/                    # AppGroupStore (GRDB), Transport (RelayClient / CloudKitSync)
  SafariWebExtension/           # manifest.json (mv3), background.ts, popup, SafariWebExtensionHandler.swift
  Shared/                       # Models (CapturedTab), AppGroupID
desktop/
  chrome-extension/             # MV3: background.ts (connectNative), popup ("N tabs → Open all")
  native-host/                  # relay puller + native-messaging host (Go/Rust); win + mac manifests/installers
relay/                          # tiny HTTPS queue service for the tailnet (Go/Node, single binary)
ci/                             # GitHub Actions: iOS TestFlight + cross-compiled host builds
docs/PLAN.md, docs/FEASIBILITY.md
```

## 9. First milestones
1. **Spike 1 — prove the iOS read path:** Safari Web Extension that logs ALL open Safari tab
   URLs/titles on a real device after granting access. *(Make-or-break unknown — do it first.)*
2. **Spike 2 — desktop open path:** a desktop Chrome extension that, given a hardcoded list, opens
   every URL via `chrome.tabs.create()`. (Trivial; proves the easy half.)
3. **Spike 3 — native-messaging host:** desktop host feeds the extension a list over native
   messaging; register it on Windows (registry) and macOS (manifest).
4. **Spike 4 — relay end-to-end:** stand up the tailnet relay; iOS `POST /tabs`, desktop host
   `GET /tabs` → opens them in Chrome. One real iPhone-to-desktop hop.
5. **Milestone 5 — pairing + consent UX** (from claude.ai/design): device pairing, permission
   primer, privacy label; TestFlight + signed desktop host installers via CI.

## 10. Open questions (decide before heavy build)
1. **Transport default:** ship the **tailnet relay** first (cross-platform, fits your stack), with
   CloudKit as a Mac-only zero-setup alternative — agreed? Or CloudKit-first for Mac users?
2. **Windows desktop priority:** Windows is the main reason for the relay (no CloudKit). Confirm
   Windows is a first-class target, not just Mac.
3. **Reverse direction (desktop Chrome → iOS Safari):** worth adding? It's now *feasible* (desktop
   reads Chrome via `chrome.tabs.query`, iOS Safari opens via `tabs.create`) — unlike the old
   iOS-Chrome-read dead end. Scope for v2?
4. **Send model:** manual "select tabs → send" only, or auto-send rules (e.g. "send all on
   shake / on tapping the share sheet")?
5. **Hosted relay:** offer a managed relay for non-Tailscale users (the paid tier), or self-host only?

## 11. Key references
- [Chrome `chrome.tabs` API](https://developer.chrome.com/docs/extensions/reference/api/tabs) ·
  [Native Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging) ·
  [Native Messaging (MDN)](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Native_messaging)
- [Safari Web Extensions — Apple](https://developer.apple.com/documentation/safariservices/safari-web-extensions) ·
  [Managing extension permissions](https://developer.apple.com/documentation/safariservices/managing-safari-web-extension-permissions) ·
  [`tabs.query` granted-only — Apple Forums](https://developer.apple.com/forums/thread/660646)
- [Syncing Safari web extensions across devices — Apple](https://developer.apple.com/documentation/safariservices/syncing-safari-web-extensions-across-devices-and-platforms) ·
  [CKSyncEngine](https://developer.apple.com/documentation/cloudkit/cksyncengine)
- [xBrowserSync (self-hosted tab/bookmark sync, prior art)](https://www.xbrowsersync.org/) ·
  [Tailscale](https://tailscale.com/)
