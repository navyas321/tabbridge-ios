# Dependencies & License Map — tabbridge-ios

**Proprietary** (private). No third-party copyleft code. Verified 2026-05-30; updated 2026-06-09 for
the iOS Safari → desktop Chrome direction.

**iOS side**
- Apple system frameworks (SwiftUI, SafariServices, CloudKit, App Groups) — no license concern.
- GRDB (if adopted for the App Group store) — MIT ✅.

**Desktop side (Windows / macOS)**
- Chrome **Native Messaging** — built-in Chrome mechanism, no code dependency.
- Native-messaging host + relay puller (Go or Rust) — std-lib / permissive deps only (MIT/BSD/Apache).

**Transport**
- Self-hosted **relay** on the user's Tailscale tailnet (Go/Node, single binary) — permissive deps only.
- CloudKit (`CKSyncEngine`) — Apple framework, Mac-only optional path.

**Discipline:** **No code copied from vibemis (GPL-3.0)** or any copyleft source. Keep deps
MIT/BSD/Apache; never vendor GPL/AGPL code into this proprietary app.
