"use strict";

(() => {
  const pages = [["/board", "Board explorer"], ["/", "Joint details"], ["/study", "Pad comparison"], ["/demo", "Worked example"], ["/lab", "Physical test"]];
  const page = location.pathname === "/index.html" ? "/" : location.pathname;
  const prefix = "soldershape.ui.v1.";
  const limit = 4_600_000;
  const transferKey = prefix + "case";
  let storageWarning = false;
  let downloadURL = null;
  function clearDownload() {
    document.getElementById("workspace-download")?.remove();
    if (downloadURL) URL.revokeObjectURL(downloadURL);
    downloadURL = null;
  }
  function downloadFile(value, filename) {
    clearDownload();
    const panel = document.createElement("div"); panel.id = "workspace-download"; panel.className = "workspace-download";
    panel.setAttribute("role", "status");
    const label = document.createElement("span"); label.textContent = "Your file is ready. ";
    const link = document.createElement("a"); link.download = filename; link.textContent = `Download ${filename} ↓`;
    if (value instanceof Blob) { downloadURL = URL.createObjectURL(value); link.href = downloadURL; }
    else link.href = value;
    panel.append(label, link); document.querySelector(".workspace-purpose").after(panel);
    link.click();
  }
  function warn(message) {
    let notice = document.getElementById("workspace-notice");
    if (!notice) {
      notice = document.createElement("p"); notice.id = "workspace-notice";
      notice.className = "workspace-notice"; notice.setAttribute("role", "status");
      document.querySelector("main").prepend(notice);
    }
    notice.textContent = message;
  }
  function storageFailure() {
    if (!storageWarning) warn("Browser draft storage is unavailable or full. Keep this page open and use Save editable case or Save editable study before leaving. Direct case handoff needs browser storage.");
    storageWarning = true;
  }
  function write(key, value) {
    try {
      const json = JSON.stringify(value);
      if (new TextEncoder().encode(json).length > limit) throw new Error("Draft too large");
      sessionStorage.setItem(key, json); return true;
    } catch { storageFailure(); return false; }
  }
  function read(key) {
    try {
      const json = sessionStorage.getItem(key);
      if (!json) return null;
      if (new TextEncoder().encode(json).length > limit) throw new Error("Draft too large");
      return JSON.parse(json);
    } catch { storageFailure(); return null; }
  }
  function discardDraft(name) {
    try { sessionStorage.removeItem(prefix + name); } catch { storageFailure(); }
  }
  function saveDraft(name, inputs, sourceIdentity = null) {
    return write(prefix + name, { version: 1, page: name, savedAt: new Date().toISOString(), inputs, sourceIdentity });
  }
  function readDraft(name) {
    const draft = read(prefix + name);
    if (!draft) return null;
    if (draft.version !== 1 || draft.page !== name || !draft.inputs || typeof draft.inputs !== "object") {
      warn("This browser draft could not be read. Open your saved editable file to recover portable inputs."); return null;
    }
    return draft;
  }
  async function checkedCase(value, token) {
    const response = await fetch("/api/case", { method: "POST", headers: { "Content-Type": "application/json", "X-SolderShape-Token": token }, body: JSON.stringify(value) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The case could not be opened.");
    return data;
  }
  async function openCase(value, origin, token, isCurrent = () => true) {
    const data = await checkedCase(value, token);
    if (!isCurrent()) throw new Error("Inputs changed while opening. Open the current case again.");
    const label = typeof origin?.label === "string" ? origin.label.slice(0, 240) : "Another SolderShape tool";
    const href = pages.some(([path]) => path === origin?.href) ? origin.href : "/board";
    if (!write(transferKey, { version: 1, createdAt: Date.now(), case: data.case, origin: { label, href } })) throw new Error("Could not transfer the case. Save the editable case and open it in Joint details instead.");
    location.assign("/?open=case");
  }
  async function receiveCase(token) {
    if (new URLSearchParams(location.search).get("open") !== "case") return null;
    const transfer = read(transferKey);
    if (!transfer || transfer.version !== 1 || !Number.isFinite(transfer.createdAt) || Date.now() - transfer.createdAt > 7_200_000 || transfer.createdAt > Date.now() + 60_000) throw new Error("The case handoff is missing or expired. Return to its source and open it again, or use a saved editable case.");
    const data = await checkedCase(transfer.case, token);
    const origin = transfer.origin;
    if (!origin || typeof origin.label !== "string" || !pages.some(([path]) => path === origin.href)) throw new Error("The case handoff has invalid source context.");
    return { ...data, origin };
  }
  function consumeCase() {
    try { sessionStorage.removeItem(transferKey); } catch { storageFailure(); }
    history.replaceState(null, "", "/");
  }
  const oldHeader = document.querySelector("body > header");
  const engine = document.getElementById("engine-state");
  const header = document.createElement("header"); header.className = "workspace-header";
  const skip = document.createElement("a"); skip.href = "#main-content"; skip.className = "skip-link"; skip.textContent = "Skip to content";
  const brand = document.createElement("a"); brand.href = "/board"; brand.className = "workspace-brand"; brand.textContent = "SolderShape"; brand.setAttribute("aria-label", "SolderShape home");
  const nav = document.createElement("nav"); nav.setAttribute("aria-label", "SolderShape tools");
  for (const [href, label] of pages) {
    const link = document.createElement("a"); link.href = href; link.textContent = label;
    if (href === page) link.setAttribute("aria-current", "page"); nav.append(link);
  }
  header.append(skip, brand, nav);
  if (engine) header.append(engine);
  else {
    const mode = document.createElement("span"); mode.className = "workspace-mode";
    if (page === "/board") mode.id = "workspace-engine";
    mode.textContent = page === "/demo" ? "Recorded calculation" : page === "/lab" ? "Quote-ready test plan" : "Local computation"; header.append(mode);
  }
  if (oldHeader) oldHeader.replaceWith(header); else document.body.prepend(header);
  const main = document.querySelector("main"); main.id = "main-content"; main.tabIndex = -1;
  const promise = document.createElement("div"); promise.className = "workspace-purpose";
  const purpose = document.createElement("p"); purpose.textContent = "Compare one solder joint. Keep the evidence. Plan the test.";
  const scope = document.createElement("span"); scope.textContent = "Physical force accuracy unqualified";
  promise.append(purpose, scope); main.prepend(promise);
  const footer = document.createElement("div"); footer.className = "workspace-next";
  const note = document.createElement("p"); note.textContent = "Inputs stay in this browser tab across navigation. Save an editable file for a durable copy. Restored inputs need a fresh computation.";
  const lab = document.createElement("a"); lab.href = page === "/lab" ? "/board" : "/lab"; lab.textContent = page === "/lab" ? "Return to Board explorer →" : "Prepare a physical test →";
  footer.append(note, lab); main.append(footer);
  // A browser's page cache must not revive numerical evidence as current after navigation.
  window.addEventListener("pageshow", (event) => { if (event.persisted) location.reload(); });
  window.SolderShapeUI = Object.freeze({ saveDraft, readDraft, discardDraft, warn, openCase, receiveCase, consumeCase, downloadFile, clearDownload });
})();
