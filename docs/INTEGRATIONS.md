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
| **plyvel + protobuf** (desktop companion, later) | read Chrome **Sync Data LevelDB** (`sessions-dt*` → `SessionSpecifics` protos). Copy the dir first (Chrome holds a lock). | community/ref | P2 |

## Runtime connectors / APIs (deliberately short)

| Name | Use | Notes |
|------|-----|-------|
| **CloudKit / CKSyncEngine** | cross-device tab-state sync (iOS app ↔ later desktop companion) | Apple-account-bound; `CKSyncEngine` (iOS 17+) is the modern path |
| **`googlechrome-x-callback://`** | the one real runtime bridge: open URL in Chrome (`open?url=…&create-new-tab&x-success=…`) + bounce back | one-way push; iOS sandbox limits |
| **Safari → only `http(s)://`** | no Safari-specific scheme exists; the **Safari Web Extension** (`browser.tabs` + native messaging + App Group) is the Safari-side runtime | MV3 parity gaps (no `webRequest`) |

**Bottom line:** P0 = XcodeBuildMCP + apple-docs-mcp + safari-web-extension-converter + fastlane + `macos-26` runners. The shipped app's only real runtime integrations are **CloudKit** (sync) and **`googlechrome-x-callback://`** (push to Chrome); the Safari side is the extension itself.
