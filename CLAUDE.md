# CLAUDE.md — TabBridge (iOS)

Advisory context for agents. Load-bearing rules belong in CI/hooks, not here (prose is followed ~70% of the time — fine for style, not safety).

## What this is
iOS app + Safari Web Extension that **sends open Safari tabs from iOS to Chrome on a Windows PC or
Mac** (one-way push). Pipeline: read Safari on iOS → private relay (Tailscale tailnet) → desktop
native-messaging host → desktop Chrome extension opens them. **Read `docs/PLAN.md` §2–3 and
`docs/FEASIBILITY.md` before re-scoping.** The direction was corrected 2026-06-09 away from the old
"same-device Safari↔Chrome on iOS" framing.

## Ground truth (do not re-litigate)
- We **read Safari on iOS** (supported) and **write Chrome on the desktop** (supported). We never
  read Chrome on iOS — that's the impossible part, and we don't depend on it.
- Safari tabs are readable only from the extension **background** script (`browser.tabs.query({})`),
  for granted origins; the all-tabs grant UX is Safari-version-dependent — spike it first.
- Desktop side: Chrome MV3 extension + **Native Messaging** host; `chrome.tabs.create()` is
  unrestricted on desktop (no `x-callback`, no stepper).
- Transport: **self-hosted relay on the tailnet** (cross-platform, primary). CloudKit is Mac-only.
  Payload is **URLs + titles only**; do not hand tab data to any third-party server.

## Workflow
- Explore → Plan → Implement → Commit for non-trivial changes.
- One feature per branch; build clean (`xcodebuild` 0 errors) before handing off.
- Model policy: Sonnet default; Opus for multi-target architecture or native↔extension bridge debugging.
- Verify on a real device or simulator — the `tabs.query` all-tabs grant behavior is version-dependent; test it, don't assume.

## Working agreement
- **Commit identity:** author as `navyas321 <15525026+navyas321@users.noreply.github.com>` (NOT `nandnalahoti`).
- **Explore → Plan → Implement → Commit** for non-trivial changes; if you can describe the exact diff in one sentence, just do it.
- One feature per branch, one PR at a time. **Self-verify** (build green) before any hand-off.
- **Stop and ask** before destructive commands (force-push, hard reset, branch delete) or anything irreversible/outward-facing.
- Secrets never committed (`.env`, keys, provisioning profiles) — keep them git-ignored.
