// TabBridge desktop extension — service worker.
//
// Talks to the native-messaging host `com.tabbridge.host`, which pulls pending
// tab batches from the relay. Each tab URL is opened with chrome.tabs.create().
//
// Flow: popup (or the periodic alarm) -> pullAndOpen() -> sendNativeMessage
//       {cmd:"pull"} -> host returns {batches:[{tabs:[{url,title}]}]} -> open.

const HOST = "com.tabbridge.host";

// Promisified one-shot native message (MV3-friendly).
function nativeSend(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendNativeMessage(HOST, message, (response) => {
      const err = chrome.runtime.lastError;
      if (err) reject(new Error(err.message));
      else resolve(response);
    });
  });
}

// Pull queued batches and open every tab. Returns a summary for the popup.
async function pullAndOpen({ background = false } = {}) {
  let res;
  try {
    res = await nativeSend({ cmd: "pull" });
  } catch (e) {
    return { ok: false, error: `native host unreachable: ${e.message}`, opened: 0 };
  }
  if (!res || res.ok === false) {
    return { ok: false, error: (res && res.error) || "unknown host error", opened: 0 };
  }

  const batches = res.batches || [];
  const tabs = batches.flatMap((b) => b.tabs || []);
  let opened = 0;
  for (const t of tabs) {
    if (typeof t.url === "string" && /^https?:\/\//.test(t.url)) {
      // active:false so a big batch doesn't yank focus around
      chrome.tabs.create({ url: t.url, active: false });
      opened += 1;
    }
  }

  if (opened > 0) {
    notify(`Opened ${opened} tab${opened === 1 ? "" : "s"} from your phone`);
  } else if (!background) {
    notify("No new tabs waiting");
  }
  return { ok: true, opened, batches: batches.length };
}

function notify(message) {
  // Notifications are best-effort; ignore if the API is unavailable.
  try {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon128.png",
      title: "TabBridge",
      message,
    });
  } catch (_) {
    /* no-op */
  }
}

// Popup asks the worker to do the pull (keeps native messaging in one place).
chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg && msg.cmd === "pullAndOpen") {
    pullAndOpen({ background: false }).then(sendResponse);
    return true; // async response
  }
  return false;
});

// Optional: poll every minute so tabs show up without opening the popup.
// (Auto-open is opt-in; comment the alarm out for manual-only.)
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create("poll", { periodInMinutes: 1 });
});
chrome.alarms?.onAlarm.addListener((a) => {
  if (a.name === "poll") pullAndOpen({ background: true });
});
