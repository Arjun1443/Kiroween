"use strict";
document.getElementById("open").onclick = async () => {
  const status = document.getElementById("status");
  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    if (!/^https?:\/\//.test(tab?.url || "")) {
      status.textContent = "Open a web page first.";
      return;
    }
    const desk = new URL("http://127.0.0.1:8000/");
    desk.searchParams.set("url", tab.url);
    await chrome.tabs.create({url: desk.href});
  } catch {
    status.textContent = "Could not access the current tab.";
  }
};
