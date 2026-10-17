"use strict";

const $ = (id) => document.getElementById(id);
const arms = ["reference", "candidate"];
const parameterNames = ["upper_diameter_mm", "volume_mm3", "normal_load_uN", "offset_mm", "surface_tension_n_m", "density_g_cm3"];
const state = {
  token: null,
  engineReady: false,
  revision: 0,
  phase: "idle",
  response: null,
  reference: { text: "", footprint: null, padIndex: null },
  candidate: { text: "", footprint: null, padIndex: null },
};
let draftReady = false;
const draftFieldNames = [...parameterNames, "reference-evidence", "candidate-evidence", "gap-requirement", "requirement-source", "volume-fraction", "lower-metal", "upper-metal", "two-pad-evidence", "input-evidence"];

function lockSetup(locked) {
  $("study-form").inert = locked;
  document.querySelector(".file-bar").inert = locked;
}

function saveDraft() {
  if (!draftReady) return;
  SolderShapeUI.saveDraft("study", {
    fields: Object.fromEntries(draftFieldNames.map((id) => [id, $(id).value])),
    gravity: $("gravity").checked,
    twoPad: $("two-pad-enabled").checked,
    sources: Object.fromEntries(arms.map((arm) => [arm, { text: state[arm].text, padIndex: state[arm].padIndex }])),
  });
}

async function restoreDraft(draft, revision) {
  if (!draft || typeof draft.fields !== "object" || !draft.sources || arms.some((arm) => typeof draft.sources[arm]?.text !== "string")) {
    throw new Error("The saved study draft could not be read. Open a study file or load the planning example.");
  }
  const imported = await Promise.all(arms.map((arm) => draft.sources[arm].text
    ? api("/api/import", { footprint_text: draft.sources[arm].text }) : null));
  if (revision !== state.revision) return false;
  for (const [index, arm] of arms.entries()) {
    state[arm] = { ...draft.sources[arm], footprint: imported[index]?.footprint || null };
    renderArm(arm);
  }
  for (const id of draftFieldNames) {
    if (typeof draft.fields[id] === "string") $(id).value = draft.fields[id];
  }
  $("gravity").checked = draft.gravity === true;
  $("two-pad-enabled").checked = draft.twoPad === true;
  clearResult();
  updateControls();
  draftReady = true;
  return true;
}

function number(value, digits = 3) {
  return typeof value === "number" && Number.isFinite(value)
    ? new Intl.NumberFormat("en", { maximumFractionDigits: digits, minimumFractionDigits: 0 }).format(value)
    : "Unavailable";
}

function notice(message = "", error = false) {
  $("notice").textContent = message;
  $("notice").className = `notice${error ? " error" : ""}`;
  $("notice").hidden = !message;
}

async function api(path, body) {
  const options = body === undefined ? {} : {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-SolderShape-Token": state.token },
    body: JSON.stringify(body),
  };
  const response = await fetch(path, { ...options, cache: "no-store" });
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The local service did not return JSON. Check that SolderShape is running.");
  }
  if (!response.ok) throw new Error(data.error || `The local service returned HTTP ${response.status}.`);
  return data;
}

function selectedPad(arm) {
  return state[arm].footprint?.pads.find((pad) => pad.index === state[arm].padIndex);
}

function updateControls() {
  const idle = state.phase === "idle";
  const session = !!state.token;
  const supported = arms.every((arm) => selectedPad(arm)?.supported);
  $("example-button").disabled = !session || !idle;
  $("study-file").disabled = !session || !idle;
  $("save-study-button").disabled = !session || !idle || !supported;
  $("run-study-button").disabled = !session || !idle || !supported || !state.engineReady;
  $("download-study-button").disabled = !idle || !state.response?.bundle_base64;
  $("run-label").textContent = state.phase === "computing" ? "Computing native nominal cases…" : "Run pad revision study";
  for (const arm of arms) {
    $(`${arm}-file`).disabled = !session || !idle;
    $(`${arm}-pad`).disabled = !state[arm].footprint;
    $(`${arm}-inspect`).disabled = !session || !idle || !selectedPad(arm)?.supported;
  }
  const twoPad = $("two-pad-enabled").checked;
  $("two-pad-fields").hidden = !twoPad;
  for (const id of ["lower-metal", "upper-metal", "two-pad-evidence"]) {
    $(id).disabled = !twoPad;
    $(id).required = twoPad;
  }
}

function clearResult() {
  state.response = null;
  SolderShapeUI.clearDownload();
  $("decision-state").textContent = "Awaiting computation";
  $("decision-heading").textContent = "Can this comparison resolve your design question?";
  $("empty-result").hidden = false;
  $("decision-result").hidden = true;
  $("computed-results").hidden = true;
  $("nominal-body").replaceChildren();
  $("samples-body").replaceChildren();
  $("study-digest").textContent = "";
}

function invalidate() {
  const hadResult = !!state.response;
  state.revision += 1;
  clearResult();
  if (state.phase === "computing") {
    notice("Inputs changed while the study is running. Its previous inputs will not replace your changes or restore an export.");
  } else if (hadResult) {
    notice("Inputs changed. Run the study again to create a matching result and archive.");
  } else {
    notice();
  }
  updateControls();
  return state.revision;
}

function renderArm(arm) {
  const { footprint, padIndex } = state[arm];
  const pad = selectedPad(arm);
  $(`${arm}-name`).textContent = footprint?.name || "Choose a footprint";
  $(`${arm}-count`).textContent = footprint ? `${footprint.pads.length} PADS / TOP VIEW` : "NO PADS";
  $(`${arm}-diameter`).textContent = pad ? pad.supported ? `${number(pad.size_mm[0] * 1000, 2)} µm` : "Unsupported pad" : "No pad selected";
  $(`${arm}-hash`).textContent = footprint ? `Source SHA-256 ${footprint.sha256}` : "No source loaded.";
  $(`${arm}-identity`).textContent = footprint ? `Source SHA-256 ${footprint.sha256.slice(0, 16)}…` : "No footprint source loaded.";
  $(`${arm}-identity`).title = footprint?.sha256 || "";
  $(`${arm}-pad-message`).textContent = pad
    ? pad.supported ? "Copper geometry is supported. Pinning and wetting still require the evidence declaration below." : pad.unsupported_reason
    : "Circular copper SMD pads are supported.";
  $(`${arm}-pad-message`).className = `pad-message${pad && !pad.supported ? " unsupported" : ""}`;
  const select = $(`${arm}-pad`);
  select.replaceChildren();
  if (footprint) {
    for (const item of footprint.pads) {
      const option = document.createElement("option");
      option.value = String(item.index);
      option.textContent = `Pad ${item.identifier}${item.supported ? "" : " · unsupported"}`;
      select.append(option);
    }
    select.value = String(padIndex);
  } else {
    const option = document.createElement("option");
    option.textContent = "Import a footprint first";
    select.append(option);
  }
  drawArm(arm);
}

function drawArm(arm) {
  const canvas = $(`${arm}-canvas`);
  const bounds = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(bounds.width * ratio));
  canvas.height = Math.max(1, Math.round(bounds.height * ratio));
  const ctx = canvas.getContext("2d");
  ctx.scale(ratio, ratio);
  const width = bounds.width;
  const height = bounds.height;
  const pads = state[arm].footprint?.pads;
  ctx.strokeStyle = "#34495b";
  ctx.lineWidth = 0.5;
  for (let x = 12; x < width; x += 18) {
    for (let y = 12; y < height; y += 18) {
      ctx.beginPath(); ctx.moveTo(x - 1, y); ctx.lineTo(x + 1, y); ctx.stroke();
    }
  }
  if (!pads?.length) return;
  const edges = pads.map((pad) => ({ x: pad.x_mm, y: pad.y_mm, r: Math.max(...pad.size_mm) / 2 }));
  const left = Math.min(...edges.map((pad) => pad.x - pad.r));
  const right = Math.max(...edges.map((pad) => pad.x + pad.r));
  const top = Math.min(...edges.map((pad) => pad.y - pad.r));
  const bottom = Math.max(...edges.map((pad) => pad.y + pad.r));
  const scale = Math.min((width - 34) / Math.max(right - left, 0.01), (height - 43) / Math.max(bottom - top, 0.01));
  for (const pad of pads) {
    const selected = pad.index === state[arm].padIndex;
    ctx.save();
    ctx.translate(width / 2 + (pad.x_mm - (left + right) / 2) * scale, (height - 12) / 2 + (pad.y_mm - (top + bottom) / 2) * scale);
    ctx.rotate(-pad.angle_deg * Math.PI / 180);
    const rx = pad.size_mm[0] * scale / 2;
    const ry = pad.size_mm[1] * scale / 2;
    ctx.beginPath();
    if (["circle", "oval"].includes(pad.shape)) ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
    else ctx.rect(-rx, -ry, rx * 2, ry * 2);
    ctx.fillStyle = !pad.supported ? "#455361" : selected ? arm === "candidate" ? "#69c7c8" : "#e8a975" : "#685847";
    ctx.fill();
    ctx.lineWidth = selected ? 1.5 : 0.7;
    ctx.strokeStyle = selected ? "#f5e3cd" : "#9c836a";
    ctx.stroke();
    if (selected) {
      ctx.beginPath(); ctx.arc(0, 0, Math.max(rx, ry) + 4, 0, Math.PI * 2); ctx.stroke();
    }
    ctx.restore();
  }
}

function draftStudy() {
  const parameters = Object.fromEntries(parameterNames.map((name) => [name, Number($(name).value)]));
  parameters.gravity = $("gravity").checked;
  return {
    schema: "soldershape.study.v1",
    ...Object.fromEntries(arms.map((arm) => [arm, {
      footprint_text: state[arm].text,
      pad_index: state[arm].padIndex,
      boundary_evidence: $(`${arm}-evidence`).value,
    }])),
    parameters,
    requirement: { pad_face_gap_um: Number($("gap-requirement").value), source: $("requirement-source").value },
    volume_fraction: Number($("volume-fraction").value),
    two_pad: $("two-pad-enabled").checked ? {
      lower_metal_um: Number($("lower-metal").value),
      upper_metal_um: Number($("upper-metal").value),
      evidence: $("two-pad-evidence").value,
    } : null,
    input_evidence: $("input-evidence").value,
  };
}

async function applyStudy(study, revision) {
  const imported = await Promise.all(arms.map((arm) => api("/api/import", { footprint_text: study[arm].footprint_text })));
  if (revision !== state.revision) return false;
  for (const [index, arm] of arms.entries()) {
    state[arm] = { text: study[arm].footprint_text, footprint: imported[index].footprint, padIndex: study[arm].pad_index };
    $(`${arm}-evidence`).value = study[arm].boundary_evidence;
    renderArm(arm);
  }
  for (const name of parameterNames) $(name).value = study.parameters[name];
  $("gravity").checked = study.parameters.gravity;
  $("gap-requirement").value = study.requirement.pad_face_gap_um;
  $("requirement-source").value = study.requirement.source;
  $("volume-fraction").value = study.volume_fraction;
  $("input-evidence").value = study.input_evidence;
  $("two-pad-enabled").checked = study.two_pad !== null;
  $("lower-metal").value = study.two_pad?.lower_metal_um ?? 35;
  $("upper-metal").value = study.two_pad?.upper_metal_um ?? 35;
  $("two-pad-evidence").value = study.two_pad?.evidence ?? "";
  updateControls();
  draftReady = true;
  saveDraft();
  return true;
}

async function loadExample() {
  const revision = invalidate();
  state.phase = "loading";
  updateControls();
  notice("Loading the controlled coupon planning example…");
  try {
    const data = await api("/api/study/example");
    if (await applyStudy(data, revision)) {
      notice("The 220 vs 270 µm coupon example is loaded. These are artificial planning assumptions. They are not physical measurements.");
    }
  } catch (error) {
    if (revision === state.revision) notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
    saveDraft();
  }
}

async function importFootprint(arm, file) {
  if (!file) return;
  const revision = invalidate();
  state.phase = "loading";
  state[arm] = { text: "", footprint: null, padIndex: null };
  renderArm(arm);
  updateControls();
  try {
    const text = await file.text();
    const data = await api("/api/import", { footprint_text: text });
    if (revision !== state.revision) return;
    state[arm] = { text, footprint: data.footprint, padIndex: data.footprint.pads.find((pad) => pad.supported)?.index ?? data.footprint.pads[0].index };
    draftReady = true;
    $(`${arm}-evidence`).value = "";
    renderArm(arm);
    notice(`Imported ${arm} footprint. Declare its boundary evidence or planning assumption before running the study.`);
  } catch (error) {
    if (revision === state.revision) notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
    saveDraft();
  }
}

function list(id, values) {
  $(id).replaceChildren(...values.map((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    return item;
  }));
}

function tableRow(row, values) {
  const tr = document.createElement("tr");
  tr.dataset.design = row.design;
  const first = document.createElement("td");
  first.textContent = row.design;
  const mapping = document.createElement("small");
  mapping.textContent = row.mapping === "literal_rims" ? "Literal copper rims" : row.mapping === "two_pad_cylinders" ? "Two-pad cylinder hypothesis" : row.mapping;
  first.append(mapping);
  tr.append(first);
  for (const value of values) {
    const td = document.createElement("td");
    td.textContent = value;
    tr.append(td);
  }
  return tr;
}

function renderReport() {
  const report = state.response.report;
  $("decision-state").textContent = report.decision.status.replaceAll("_", " ");
  $("decision-heading").textContent = report.decision.headline;
  list("decision-reasons", report.decision.reasons);
  list("decision-actions", report.decision.next_actions);
  list("scope-list", report.scope);
  $("empty-result").hidden = true;
  $("decision-result").hidden = false;
  $("computed-results").hidden = false;
  $("nominal-body").replaceChildren(...report.nominal.map((row) => tableRow(row, [
    `${number(row.lower_diameter_mm * 1000, 2)} µm`,
    row.native_gap_um === null ? "Unavailable" : `${number(row.native_gap_um)} µm`,
    row.analytical_gap_um === null ? "Unavailable" : `${number(row.analytical_gap_um)} µm`,
    row.native_minus_analytical_um === null ? "Unavailable" : `${number(row.native_minus_analytical_um)} µm`,
    row.margin_um === null ? "Unavailable" : `${number(row.margin_um)} µm`,
    row.status.replaceAll("_", " "),
  ])));
  $("samples-body").replaceChildren(...report.samples.map((row) => {
    const tr = tableRow(row, [
      `${number(row.volume_mm3, 8)} mm³${row.volume_sample ? ` · ${row.volume_sample}` : ""}`,
      row.gap_um === null ? "Unavailable" : `${number(row.gap_um)} µm`,
      row.margin_um === null ? "Unavailable" : `${number(row.margin_um)} µm`,
      row.eligible ? "Eligible under stated policy" : row.reason || "Unavailable",
    ]);
    if (!row.eligible) tr.lastElementChild.className = "ineligible";
    return tr;
  }));
  $("study-digest").textContent = `Study SHA-256 ${report.study_sha256}`;
}

async function runStudy(event) {
  event.preventDefault();
  if (state.phase !== "idle" || !$("study-form").reportValidity()) return;
  const revision = invalidate();
  const study = draftStudy();
  state.phase = "computing";
  updateControls();
  notice("Computing the native nominal cases and the independent analytical volume screen. Keep this tab open. Editing inputs will discard this result.");
  try {
    const data = await api("/api/study", study);
    if (revision !== state.revision) {
      notice("The completed study used earlier inputs and was discarded. Run again to compute your current inputs.");
      return;
    }
    state.response = data;
    renderReport();
    notice("The study is complete. The conclusion applies to these declared inputs and finite samples. Physical qualification remains unqualified.");
    $("decision-heading").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch (error) {
    if (revision === state.revision) notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
  }
}

function download(blob, filename) {
  SolderShapeUI.downloadFile(blob, filename);
}

async function saveStudy() {
  if (state.phase !== "idle" || !$("study-form").reportValidity()) return;
  const revision = state.revision;
  state.phase = "saving";
  updateControls();
  try {
    const data = await api("/api/study/case", draftStudy());
    if (revision !== state.revision) return;
    download(new Blob([JSON.stringify(data.study, null, 2) + "\n"], { type: "application/json" }), "soldershape-study.json");
    notice("Saved the normalized editable study. Its JSON contains inputs and footprint sources. Run and download the archive to keep calculation evidence.");
  } catch (error) {
    if (revision === state.revision) notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
  }
}

async function openStudy(file) {
  if (!file) return;
  const revision = invalidate();
  state.phase = "loading";
  updateControls();
  try {
    const draft = JSON.parse(await file.text());
    const data = await api("/api/study/case", draft);
    if (await applyStudy(data.study, revision)) notice("Opened the editable study. Run it to generate current computation evidence.");
  } catch (error) {
    if (revision === state.revision) notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
  }
}

async function inspectArm(arm) {
  if (state.phase !== "idle" || !selectedPad(arm)?.supported) return;
  for (const name of parameterNames) {
    if (!$(name).reportValidity()) return;
  }
  const revision = state.revision;
  const parameters = Object.fromEntries(parameterNames.map((name) => [name, $(name).valueAsNumber]));
  parameters.gravity = $("gravity").checked;
  saveDraft();
  state.phase = "opening";
  updateControls();
  notice(`Opening the ${arm} source pad with its literal copper rims. The two-pad cylinder hypothesis is excluded.`);
  try {
    await SolderShapeUI.openCase({
      schema: "soldershape.case.v1",
      footprint_text: state[arm].text,
      pad_index: state[arm].padIndex,
      parameters,
      baseline: null,
    }, { label: `Pad comparison, ${arm} literal rims`, href: "/study" }, state.token, () => revision === state.revision);
  } catch (error) {
    notice(error.message, true);
  } finally {
    state.phase = "idle";
    updateControls();
  }
}

$("study-form").addEventListener("input", (event) => {
  if (event.target.type === "file") return;
  for (const arm of arms) {
    if (event.target.id === `${arm}-pad`) {
      state[arm].padIndex = Number(event.target.value);
      renderArm(arm);
    }
  }
  invalidate();
  saveDraft();
});
$("study-form").addEventListener("submit", runStudy);
$("example-button").addEventListener("click", loadExample);
$("save-study-button").addEventListener("click", saveStudy);
$("study-file").addEventListener("change", (event) => {
  openStudy(event.target.files[0]);
  event.target.value = "";
});
for (const arm of arms) {
  $(`${arm}-inspect`).addEventListener("click", () => inspectArm(arm));
  $(`${arm}-file`).addEventListener("change", (event) => {
    importFootprint(arm, event.target.files[0]);
    event.target.value = "";
  });
  new ResizeObserver(() => drawArm(arm)).observe($(`${arm}-canvas`));
}
$("download-study-button").addEventListener("click", () => {
  if (!state.response?.bundle_base64 || state.phase !== "idle") return;
  const decoded = atob(state.response.bundle_base64);
  download(new Blob([Uint8Array.from(decoded, (character) => character.charCodeAt(0))], { type: "application/zip" }), state.response.bundle_filename);
});

lockSetup(true);
(async () => {
  try {
    const data = await api("/api/bootstrap");
    state.token = data.token;
    const engine = data.engine;
    state.engineReady = engine.ready;
    $("engine-label").textContent = state.engineReady ? `Surface Evolver ${engine.version} · ready` : "Numerical engine unavailable";
    $("engine-state").className = `engine-state ${state.engineReady ? "ready" : "unavailable"}`;
    updateControls();
    if (state.revision === 0) {
      const saved = SolderShapeUI.readDraft("study");
      if (saved) {
        const revision = state.revision;
        state.phase = "loading";
        updateControls();
        if (await restoreDraft(saved.inputs, revision)) notice("Study inputs and both footprint sources restored in this tab. Run again for fresh evidence.");
        state.phase = "idle";
      } else {
        await loadExample();
      }
    }
    saveDraft();
    updateControls();
    if (!state.engineReady) notice(engine.error, true);
  } catch (error) {
    notice(error.message, true);
    if (!state.token) {
      $("engine-label").textContent = "Local service unavailable";
      $("engine-state").className = "engine-state unavailable";
    }
  } finally {
    state.phase = "idle";
    lockSetup(false);
    updateControls();
  }
})();
window.addEventListener("pagehide", saveDraft);
