# TabBridge iOS (capture side) — not yet implemented

This is the **source** end of the pipeline: a SwiftUI container app + a **Safari Web Extension**
that reads your open Safari tabs and POSTs them to the [relay](../relay).

It is **not built yet** — it requires **macOS + Xcode** (this part can't be compiled on Windows).
The desktop + relay halves it talks to are already implemented and tested.

## Planned shape (see [../docs/PLAN.md](../docs/PLAN.md) §4)
- **Safari Web Extension** (MV3): `browser.tabs.query({})` in the background script enumerates open
  tabs → `browser.runtime.sendNativeMessage` → `SafariWebExtensionHandler` (Swift).
- **SwiftUI app**: review/select captured tabs, pick a paired desktop, **Send** → `POST /tabs` on
  the relay with the shared bearer token.
- **App Group + GRDB** for the local queue; pairing stores the relay URL + token in the Keychain.

## First spike (the make-or-break unknown)
Prove the read path: a Safari Web Extension that logs **all** open Safari tab URLs/titles on a real
device after the user grants access. The all-tabs permission UX is Safari-version-dependent — test
it before building the rest. See [../docs/FEASIBILITY.md](../docs/FEASIBILITY.md).

## Contract with the relay
POST `/tabs` with `Authorization: Bearer <token>` and body:
```json
{ "device": "iPhone", "tabs": [ { "url": "https://…", "title": "…" } ] }
```
