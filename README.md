# TabBridge (iOS)

Move your open browser tabs **between Safari and Chrome on iOS** — the thing that genuinely doesn't exist, because iOS makes true auto-sync impossible. TabBridge does the most that the sandbox actually permits, honestly.

> **What's real (and why no one ships it):**
> - ✅ **Read all your open Safari tabs** (Safari Web Extension, with your permission).
> - ✅ **Push them into Chrome**, one chained tap at a time, via `googlechrome-x-callback://`.
> - ⚠️ **Chrome → Safari is manual**: Chrome on iOS exposes no tab list, so you *share* a tab into TabBridge.
> - ❌ **No silent, always-on, bidirectional sync** is possible on iOS. Anyone promising that is lying. See [docs/PLAN.md](docs/PLAN.md).

**Status:** scaffold / planning. **Designation:** personal tool (commercial only as a desktop-anchored product later). **License:** proprietary for now.

See the full plan, verified feasibility, architecture, and `claude.ai/design` UX prompts in **[docs/PLAN.md](docs/PLAN.md)**.
