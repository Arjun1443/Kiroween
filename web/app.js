"use strict";
const byId = id => document.getElementById(id);
const urls = byId("urls");
const status = byId("status");
const form = byId("restore-form");
const libraryStatus = byId("library-status");
const demoUrl = "https://fieldnotes.example/urban-moths";
const key = "tombstone.library.v1";
let library = [];
try {
  library = JSON.parse(localStorage.getItem(key) || "[]");
  if (!Array.isArray(library)) library = [];
} catch { library = []; }

function element(tag, value, parent, className) {
  const node = document.createElement(tag);
  if (value) node.textContent = value;
  if (className) node.className = className;
  parent.append(node);
  return node;
}

function sourceLink(parent, card, label) {
  const link = element("a", label, parent);
  const target = new URL(card.source, location.origin);
  if (target.origin === "https://web.archive.org" ||
      (target.origin === location.origin && target.pathname === "/sample.html")) {
    link.href = target.href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
  }
}

const states = {
  restored: "Restored", partial: "Capture found · text unavailable",
  missing: "No snapshot found", unavailable: "Archive lookup unavailable",
  blocked: "Address blocked", error: "Search failed"
};

function updateLibrary(items, message) {
  try {
    localStorage.setItem(key, JSON.stringify(items));
  } catch {
    libraryStatus.textContent = "Browser storage is unavailable or full.";
    return false;
  }
  library = items;
  renderLibrary();
  libraryStatus.textContent = message;
  return true;
}

function showCard(parent, card, saved = false) {
  const box = element("article", "", parent, "result");
  element("div", (card.demo ? "Offline sample · " : "") + states[card.state], box, "badge");
  element("h3", card.title || card.url, box);
  element("p", card.url + " · Origin " + (card.health || "unchecked"), box, "meta");
  if (card.error) element("p", card.error, box);
  if (!card.source) return;
  element("p", "Captured " + card.captured + " · Published " + (card.published || "unknown") +
    (card.author ? " · " + card.author : ""), box, "meta");
  sourceLink(box, card, card.demo ? "Open sample source ↗" : "Open archived capture ↗");
  if (card.highlights.length) {
    element("h4", "Source highlights", box);
    for (const id of card.highlights) {
      const evidence = card.evidence.find(item => item.id === id);
      const quote = element("blockquote", evidence.quote, box);
      element("br", "", quote);
      sourceLink(quote, card, "Source [" + id + "]");
    }
    const details = element("details", "", box);
    element("summary", "View all " + card.evidence.length + " evidence excerpts", details);
    for (const item of card.evidence) element("p", "[" + item.id + "] " + item.quote, details);
  }
  const actions = element("div", "", box, "actions");
  const action = element("button", saved ? "Remove card" : "Save card", actions);
  action.type = "button";
  action.onclick = () => {
    const others = library.filter(item => item.url !== card.url);
    if (saved) updateLibrary(others, "Card removed.");
    else if (updateLibrary([card, ...others], "Card saved to your library.")) {
      action.textContent = "Saved";
      action.disabled = true;
      status.textContent = "Card saved to your library.";
    } else status.textContent = libraryStatus.textContent;
  };
}

function matchingCards() {
  const query = byId("search").value.trim().toLowerCase();
  return library.filter(card => [card.title, card.url, card.author, ...card.evidence.map(e => e.quote)]
    .join(" ").toLowerCase().includes(query));
}

function renderLibrary() {
  const cards = byId("cards");
  const matches = matchingCards();
  cards.replaceChildren();
  byId("count").textContent = library.length;
  byId("export").disabled = matches.length === 0;
  libraryStatus.textContent = matches.length ? matches.length + " matching cards." :
    library.length ? "No matching cards." : "Restore a page and save its card to start your library.";
  for (const card of matches) showCard(cards, card, true);
}

let running = false;
form.onsubmit = async event => {
  event.preventDefault();
  if (running) return;
  const batch = [...new Set(urls.value.split(/\s+/).filter(Boolean))];
  if (!batch.length || batch.length > 5) {
    status.textContent = "Enter between 1 and 5 URLs.";
    return;
  }
  running = true;
  form.querySelector("button").disabled = byId("demo").disabled = true;
  const results = byId("results");
  results.replaceChildren();
  try {
    for (const [index, url] of batch.entries()) {
      status.textContent = "Searching archives for link " + (index + 1) + " of " + batch.length + "…";
      try {
        const response = await fetch("/api/restore", {
          method: "POST", headers: {"Content-Type": "application/json"},
          body: JSON.stringify({url}), signal: AbortSignal.timeout(35000)
        });
        const card = await response.json();
        if (!response.ok) throw new Error(card.error);
        showCard(results, card);
      } catch (error) {
        showCard(results, {url, state: "error", error: error.message || "Search timed out."});
      }
    }
    status.textContent = "Finished checking " + batch.length + (batch.length === 1 ? " link." : " links.");
  } finally {
    running = false;
    form.querySelector("button").disabled = byId("demo").disabled = false;
  }
};

byId("demo").onclick = () => {
  urls.value = demoUrl;
  form.requestSubmit();
};
byId("import").onchange = async event => {
  const file = event.target.files[0];
  event.target.value = "";
  if (!file) return;
  if (file.size > 2_000_000) {
    status.textContent = "Choose a bookmark file smaller than 2 MB.";
    return;
  }
  try {
    const content = await file.text();
    // Read only link attributes as text. Imported markup is never parsed into the document.
    const candidates = /\.html?$/i.test(file.name)
      ? [...content.matchAll(/\bhref\s*=\s*["'](https?:\/\/[^"']+)["']/gi)]
        .map(match => match[1].replaceAll("&amp;", "&"))
      : content.match(/https?:\/\/[^\s,"'<>]+/gi) || [];
    const links = [...new Set(candidates)];
    if (links.length) urls.value = links.slice(0, 5).join("\n");
    status.textContent = !links.length ? "No HTTP links found." : links.length > 5
      ? "Loaded the first 5 of " + links.length + " links. Review them before searching."
      : "Review the imported URLs before searching.";
  } catch {
    status.textContent = "Could not read the bookmark file.";
  }
};
byId("search").oninput = renderLibrary;
byId("export").onclick = () => {
  const escape = value => String(value).replace(/[\\<>\[\]*_`#]/g, "\\$&").replace(/[\r\n]/g, " ");
  const markdown = matchingCards().map(card => [
    "## " + escape(card.title),
    "Original: " + escape(card.url),
    "Captured: " + escape(card.captured),
    "Published: " + escape(card.published || "Unknown"),
    "Source: " + (card.demo ? "Bundled fictional sample (docs/sample.html)" : escape(card.source)),
    ...card.evidence.map(item => "> [" + item.id + "] " + escape(item.quote))
  ].join("\n\n")).join("\n\n---\n\n");
  const download = document.createElement("a");
  const objectUrl = URL.createObjectURL(new Blob([markdown + "\n"], {type: "text/markdown"}));
  download.href = objectUrl;
  download.download = "tombstone-library.md";
  download.click();
  setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
};

const initialUrl = new URLSearchParams(location.search).get("url");
if (initialUrl) {
  urls.value = initialUrl;
  history.replaceState(null, "", location.pathname);
}
renderLibrary();
