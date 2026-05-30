# CLAUDE.md — TabBridge (iOS)

Advisory context for agents. Load-bearing rules belong in CI/hooks, not here (prose is followed ~70% of the time — fine for style, not safety).

## What this is
iOS app + Safari Web Extension that moves open tabs between Safari and Chrome. **Read the asymmetry in `docs/PLAN.md` §2 before proposing any "sync" feature — true bidirectional auto-sync is IMPOSSIBLE on iOS and must never be claimed.**

## Ground truth (do not re-litigate)
- Chrome iOS: no extensions, no tab-read API. `googlechrome-x-callback://` is write-only.
- Safari tabs are readable only from the extension **background** script, only for granted origins.
- Chrome→Safari capture is manual (Share Extension, one tab).
- All tab URLs stay **on-device / user-iCloud**. Never send URLs to any server.

## Workflow
- Explore → Plan → Implement → Commit for non-trivial changes.
- One feature per branch; build clean (`xcodebuild` 0 errors) before handing off.
- Model policy: Sonnet default; Opus for multi-target architecture or native↔extension bridge debugging.
- Verify on a real device or simulator — the `tabs.query` all-tabs grant behavior is version-dependent; test it, don't assume.
