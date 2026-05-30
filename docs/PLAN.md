# TabBridge — Plan

_Researched + adversarially verified 2026-05-30. Verification corrections are marked ⚠️._

## 1. TL;DR
Build a SwiftUI app + Safari Web Extension that treats **Safari as the only fully-readable side**: read open Safari tabs → store in an App Group → push them into Chrome via `googlechrome-x-callback://`. Chrome→Safari is a manual Share-Extension capture. The honest framing ("Safari auto-read, Chrome manual") *is* the product's credibility.

## 2. Feasibility — verified hard constraints
- **Chrome on iOS has no extensions** and no public API/URL scheme to **read** its open or synced tabs. `googlechrome-x-callback://` is **write-only** (open URL, `create-new-tab`, `x-success`). *Confirmed.*
- **Chrome's Google-account tab sync** store lives inside Chrome's **private sandbox container** on iOS — unreadable by other apps. The readable LevelDB path is **desktop-only**. *Confirmed — and this is the seed of the commercial pivot.*
- **iCloud Tabs / Handoff (NSUserActivity)** have **no third-party read API**; Handoff is same-app continuation only. *Confirmed.*
- **Safari Web Extension `tabs.query()` on iOS** returns url/title only for granted origins, and **only from the background script**. To see *all* tabs you need the `tabs` permission and the user to grant all-sites access. ⚠️ *Verify the exact permission at build time*: an Apple engineer stated bare `tabs` *should* suffice and the missing "Always Allow on Every Website" button for tab managers was logged as a Safari bug. Requesting `<all_urls>` is the scarier prompt → more drop-off; test whether `tabs` alone now surfaces an all-sites grant first.
- **Share Extension from Chrome** yields only the **one** currently-shared page, never a tab list. *Confirmed.*
- ⚠️ **Batch push to Chrome**: the original "one external URL per user gesture" framing is over-simplified. Real mechanism: opening Chrome **backgrounds your app**, so you chain the next URL when Chrome fires `x-success` back to TabBridge. Chaining *can* be automated; the **"Pushing X of Y — tap to continue" stepper is a deliberate fallback** for when the round-trip is slow/unreliable across iOS/Chrome versions. Add a graceful fallback to plain `https` open.
- ⚠️ **App Store review**: treat approval as a **manageable risk, not a guarantee**. Keep all URLs **on-device / user-iCloud only**, never POST to your own server, ship a clear consent flow + privacy nutrition label.

**Verdict:** true bidirectional live auto-sync is **impossible** on iOS. The "asymmetric bridge with a shared queue" is the correct ceiling and survives scrutiny.

## 3. Recommended architecture
Three Xcode targets in one app:
- **(A) SwiftUI container app** — the hub: unified queue, history, settings, consent. Owns the App Group store.
- **(B) Safari Web Extension** (MV3, non-persistent background): `browser.tabs.query({})` to enumerate, `browser.tabs.create({url})` to open; bridges to native via `browser.runtime.sendNativeMessage` → `SafariWebExtensionHandler`.
- **(C) Share Extension** — capture a shared URL (from Chrome or anywhere) into the queue.

**Data:** App Group (`group.com.you.tabbridge`) with GRDB/SQLite; optional **CloudKit private DB** (`CKSyncEngine`) for the user's own cross-device queue — the *only* sanctioned sync surface.
**Outbound to Chrome:** `UIApplication.open(googlechrome-x-callback://…&create-new-tab=true&x-success=…)`, chained. `LSApplicationQueriesSchemes = [googlechrome]`.
**Outbound to Safari:** `tabs.create` or `UIApplication.open(https://…)`.
**No backend for v1.**

## 4. Tech stack
Swift 6 / SwiftUI · Safari Web Extension (MV3, TS background) · `SafariWebExtensionHandler` native bridge · App Groups + GRDB · CloudKit (`CKSyncEngine`, optional) · `googlechrome-x-callback://` · Share Extension (`public.url`) · GitHub Actions + `xcodebuild`/fastlane for TestFlight.

## 5. UX — design these in claude.ai/design
Screens: (1) **Onboarding/Permission Primer** — honest asymmetry explainer + the Safari all-sites walkthrough; (2) **Unified Queue** (home) — captured tabs with source badges (Safari/Chrome/Shared), multi-select, "Open in Safari"/"Open in Chrome"; (3) **Batch Pusher** — "Pushing 3 of 8 to Chrome — tap to continue" stepper; (4) **Settings** — consent toggles, CloudKit on/off, clear-data, privacy explainer; (5) **Safari extension popup** — "Capture N open tabs."

**Prompt for claude.ai/design:**
> Design a clean, trustworthy iOS utility called TabBridge that moves open browser tabs between Safari and Chrome. Screens: an onboarding screen honestly explaining Safari tabs are read automatically but Chrome tabs must be shared manually; a unified tab-queue list with source badges and Open-in-Safari/Open-in-Chrome actions; a step-by-step batch-push card ("Pushing X of Y to Chrome, tap to continue"); a privacy-forward settings screen with on-device/iCloud sync toggles; and a Safari extension popup that says "Capture N open tabs." Visual tone: native iOS, SF Symbols, neutral with one accent color, privacy-reassuring, no dark patterns. Provide light + dark and an empty-state for the queue.

## 6. Commercialization
- **Designation:** **personal tool** now. The honest ceiling (no silent Chrome read, manual Chrome→Safari, scary Safari permission) makes a standalone iOS product weak — the demo always carries an asterisk.
- **License:** **proprietary** while private; **MIT** if you later open the app + extension.
- **The actually-sellable evolution:** a **desktop-anchored hub** — a Mac/Windows companion (where Chrome's sync LevelDB and full WebExtension tabs API *are* readable) + the iOS Safari extension + CloudKit, marketed as "your tabs, every browser, every device." That's where a real Chrome **read** path exists. Freemium (free: send-tab; paid: cross-device queue + history). License then: dual-license or BSL-1.1 if you add a hosted relay.

## 7. Repo scaffold (target)
```
TabBridge.xcodeproj            # 3 targets: App, SafariWebExtension, ShareExtension
App/                           # SwiftUI: TabBridgeApp, QueueView, OnboardingView, BatchPushView, SettingsView
App/Store/                     # AppGroupStore (GRDB), CloudKitSync (CKSyncEngine)
App/Bridge/                    # ChromeOpener (x-callback builder), SafariOpener
SafariWebExtension/            # manifest.json (mv3), background.ts, popup, SafariWebExtensionHandler.swift
ShareExtension/                # ShareViewController.swift
Shared/                        # Models (CapturedTab), AppGroupID, Info.plist (LSApplicationQueriesSchemes=[googlechrome])
ci/                            # GitHub Actions xcodebuild + fastlane (TestFlight)
docs/PLAN.md, docs/FEASIBILITY.md
```

## 8. First milestones
1. **Spike 1 — prove the read path:** Safari Web Extension that calls `browser.tabs.query({})` and logs ALL open tab URLs/titles on iOS after granting access. (This is the make-or-break unknown — do it first.)
2. **Spike 2 — native bridge:** get the captured list from `background.ts` into SwiftUI via the App Group; render in `QueueView`.
3. **Spike 3 — Chrome push:** open one URL, chain a second via `x-success` back into TabBridge; build the `BatchPushView` stepper + `https` fallback.
4. **Milestone 4 — Share Extension** to capture the current Chrome tab (Chrome→Safari direction).
5. **Milestone 5 — Onboarding + consent UX** (from claude.ai/design), privacy label, optional CloudKit queue; TestFlight via CI.

## 9. Open questions (decide before heavy build)
1. Real goal: **"one-click move my Safari session into Chrome"** (very doable) or **"always in sync both ways"** (impossible on iOS)? This decides the whole product.
2. iOS-only, or build toward the **desktop-anchored** sellable version (real Chrome read path)?
3. Add **iPhone↔Mac Safari↔Safari** real sync (Mac extension + CloudKit)? Stronger story than the Chrome side.
4. Personal tool only, or App Store distribution (forces the privacy/consent UX investment)?
5. Is Chrome→Safari being **manual-share-only forever** acceptable?

## 10. Key references
- [Safari Web Extensions — Apple](https://developer.apple.com/documentation/safariservices/safari-web-extensions) · [Managing extension permissions](https://developer.apple.com/documentation/safariservices/managing-safari-web-extension-permissions) · [tabs.query granted-only — Apple Forums](https://developer.apple.com/forums/thread/660646)
- [Opening links in Chrome iOS (x-callback) — Chromium](https://chromium.googlesource.com/chromium/src/+/master/docs/ios/opening_links.md) · [x-callback params](https://github.com/ChristinWhite/iosWorkflows/blob/master/google-chrome.md)
- [Chrome iOS has no extensions (Kagi Orion)](https://help.kagi.com/orion/browser-extensions/ios-ipados-extensions.html) · [Reading Chrome desktop synced tabs (LevelDB)](https://davidbieber.com/snippets/2021-01-01-programmatically-accessing-chromes-tabs-from-other-devices-data/)
- [App Review Guidelines (5.1 privacy)](https://developer.apple.com/app-store/review/guidelines/)
