// TabBridge popup — asks the service worker to pull + open queued tabs.
const btn = document.getElementById("open");
const status = document.getElementById("status");

function setStatus(text, isError = false) {
  status.textContent = text;
  status.className = isError ? "err" : "";
}

btn.addEventListener("click", () => {
  btn.disabled = true;
  setStatus("Checking your phone’s queue…");
  chrome.runtime.sendMessage({ cmd: "pullAndOpen" }, (res) => {
    btn.disabled = false;
    const err = chrome.runtime.lastError;
    if (err) return setStatus(err.message, true);
    if (!res || !res.ok) return setStatus((res && res.error) || "Failed", true);
    if (res.opened > 0) {
      setStatus(`Opened ${res.opened} tab${res.opened === 1 ? "" : "s"}.`);
    } else {
      setStatus("No new tabs waiting.");
    }
  });
});
