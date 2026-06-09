# tabbridge-ios — Integrations (mostly dev-time)

Curated 2026-05-30. Honest framing: a native SwiftUI app + Safari Web Extension has **almost no runtime MCP/connector layer** — Apple frameworks are SDKs, not MCPs. The value below is **dev-time** build/test/ship acceleration.

## Dev-time MCPs / tools (build, test, ship)

| Name | Helps with | Official/community | Priority |
|------|-----------|--------------------|----------|
| **XcodeBuildMCP** (Sentry) | Anchor tool: ~82 tools — build/test/run, simulator, device deploy, LLDB, UI automation, log capture, SwiftPM. Headless via `xcodebuild`. | official-ish | **P0** |
| **apple-docs-mcp** | live Apple Developer docs (SwiftUI/SafariServices/UIKit) + WWDC + API refs in-prompt | community | **P0** |
| **safari-web-extension-converter** (`xcrun`) | convert Chrome/MV3 extension → Safari Web Extension Xcode project. ⚠️ Safari MV3 lacks `webRequest` — verify API parity. | **Official (Apple)** | **P0** |
| **fastlane** | release pipeline: `match` (signing), `gym` (build), `pilot`/`deliver` (TestFlight + App Store) on ASC API | official OSS | **P0** |
| **GitHub Actions `macos-26` runners** | hosted Xcode build/test/sign (GA Feb 2026); pair with fastlane | Official (GitHub) | **P0** |
| **ios-simulator-mcp** | lighter sim-only MCP (tap/swipe/type/screenshot) | community | P1 |
| **Playwright** | test the extension's web parts (popup/options/content) in Chromium+WebKit (WebKit ≈ Safari, not identical) | Official (MS) | P1 |
| **web-ext** (Mozilla) | `web-ext lint` validates manifest/permissions/MV3 before Safari conversion | Official | P1 |
| **GitHub MCP Server** | repos/issues/PRs/releases/Actions from an agent | Official | P1 |
| **Context7** | version-specific docs for the JS/TS side (Playwright, web-ext, MV3) | community | P1 |
| **App Store Connect MCP / TestFlight Feedback MCP** | conversational build/TestFlight/review ops; pull beta crash+screenshot feedback | community | P2 |
| **XcodeDocsMCP** | offline installed-SDK symbol docs | community | P2 |
| **Chrome extension tooling** (`web-ext` lint, Vite/CRXJS, `chrome.runtime` reload) | build/package the **desktop Chrome MV3 extension** (the write side) | community/official | **P0** |
| **Go/Rust cross-compile + signing** (`goreleaser` / `cargo`, signtool/codesign) | build the **native-messaging host** for Windows + macOS and register it (registry / abs-path manifest) | official OSS | P1 |

## Runtime connectors / APIs

The shipped runtime is a real cross-device pipeline now (not just iOS):

| Name | Use | Notes |
|------|-----|-------|
| **Safari Web Extension** (`browser.tabs` + native messaging + App Group) | **read** open Safari tabs on iOS (the source) | MV3 parity gaps (no `webRequest`); all-tabs grant UX is version-dependent |
| **Self-hosted relay (Tailscale tailnet)** | move the tab list iOS → desktop privately (iOS POST, desktop pull) | primary transport; cross-platform (Win **and** Mac); no public server |
| **CloudKit / CKSyncEngine** | optional **Mac-only** transport alternative | Apple-account-bound; does **not** reach Windows |
| **Chrome Native Messaging** | desktop host ↔ Chrome extension over stdio | Win: registry-registered host; macOS: abs-path manifest |
| **Chrome `chrome.tabs.create()`** (desktop) | **open** the tabs in desktop Chrome (the destination) | unrestricted on desktop — no `x-callback`, no stepper |

**Bottom line:** P0 dev tools = XcodeBuildMCP + apple-docs-mcp + safari-web-extension-converter +
fastlane + `macos-26` runners + Chrome-extension tooling. Runtime pipeline = **Safari read (iOS)
→ tailnet relay → Native Messaging host → `chrome.tabs.create()` (desktop)**.
