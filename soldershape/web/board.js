"use strict";

const $ = (id) => document.getElementById(id);
const SVG_NS = "http://www.w3.org/2000/svg";
const state = { context: null, component: null, padIndex: null, draft: null, revision: 0, phase: "loading", pending: null, response: null, bundleUrl: null, token: null, engineReady: false, caseAction: null, padHits: [] };
const fields = [
  ["upper-diameter", "upper_diameter_mm", 1000], ["held-gap", "standoff_mm", 1000],
  ["offset", "offset_mm", 1000], ["candidate-volume", "volume_mm3", 1000],
  ["surface-tension", "surface_tension_n_m", 1], ["density", "density_g_cm3", 1],
];
const initialCamera = { yaw: -.58, elevation: .4, zoom: 1 };
const camera = { ...initialCamera, drag: null };
const modelCanvases = [$("reference-canvas"), $("candidate-canvas")];
let framePending = false;

function number(value, digits = 3) {
  return Number.isFinite(value) ? value.toLocaleString("en-US", { maximumFractionDigits: digits, useGrouping: false }) : "Unavailable";
}
function signed(value, digits = 3) { return Number.isFinite(value) ? `${value > 0 ? "+" : ""}${number(value, digits)}` : "Unavailable"; }
function component() { return state.context?.components.find((item) => item.uuid === state.component) || null; }
function pad() { return component()?.pads.find((item) => item.index === state.padIndex) || null; }
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function spec(record) { return record?.equilibrium || record?.input; }
function setList(element, values) {
  element.replaceChildren(...values.map((value) => { const item = document.createElement("li"); item.textContent = value; return item; }));
}
function notice(message, kind = "") { $("run-notice").textContent = message; $("run-notice").className = kind; }
function sourceIdentity() {
  return { board_sha256: state.context.source.board_sha256, extractor_sha256: state.context.extraction.extractor_sha256 };
}
function saveDraft() {
  if (!state.context || !state.draft) return;
  const values = Object.fromEntries([...fields.map(([id]) => id), "reference-volume"].map((id) => [id, $(id).value]));
  window.SolderShapeUI.saveDraft("board", { component_uuid: state.component, pad_index: state.padIndex, search: $("component-search").value, values, gravity: $("gravity").checked }, sourceIdentity());
}
function restoreDraft() {
  const saved = window.SolderShapeUI.readDraft("board");
  if (!saved) return false;
  const identity = sourceIdentity(), inputs = saved.inputs;
  const selected = state.context.components.find((item) => item.uuid === inputs?.component_uuid);
  const matchesSource = saved.sourceIdentity?.board_sha256 === identity.board_sha256 && saved.sourceIdentity?.extractor_sha256 === identity.extractor_sha256;
  const ids = [...fields.map(([id]) => id), "reference-volume"];
  const validSelection = selected && (selected.pads.some((item) => item.index === inputs.pad_index) || inputs.pad_index === null && !selected.pads.length);
  const validInputs = typeof inputs?.search === "string" && typeof inputs?.gravity === "boolean" && ids.every((id) => typeof inputs?.values?.[id] === "string");
  if (!matchesSource || !validSelection || !validInputs) {
    window.SolderShapeUI.warn("The saved board inputs no longer match this source board or extraction. The initial comparison is shown instead. Save the previous raw draft below before replacing it.");
    SolderShapeUI.downloadFile(new Blob([JSON.stringify(saved, null, 2) + "\n"], { type: "application/json" }), "soldershape-unmatched-board-draft.json");
    return false;
  }
  state.component = selected.uuid;
  state.padIndex = inputs.pad_index;
  $("component-search").value = inputs.search;
  for (const id of ids) $(id).value = inputs.values[id];
  $("gravity").checked = inputs.gravity;
  readDraft();
  return true;
}
function svgElement(name, attributes = {}) {
  const element = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, String(value));
  return element;
}
async function api(url, body) {
  const response = await fetch(url, body ? { method: "POST", headers: { "Content-Type": "application/json", "X-SolderShape-Token": state.token }, body: JSON.stringify(body) } : { cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed with status ${response.status}.`);
  return data;
}
function clearResponse() {
  SolderShapeUI.clearDownload();
  state.response = null;
  if (state.bundleUrl) URL.revokeObjectURL(state.bundleUrl);
  state.bundleUrl = null;
}
function invalidate() {
  state.revision += 1;
  state.phase = "draft";
  clearResponse();
  renderResults();
  updateCompute();
  saveDraft();
  if (state.pending !== null) notice("Inputs changed. The pending computation will be discarded.", "working");
  else notice(pad()?.supported ? "Inputs changed. Compute this selected joint to obtain current forces and exports." : "This selection is inspect-only. Choose a supported circular front pad.");
  scheduleDraw();
}
function updateCompute() {
  const valid = !!state.token && !!pad()?.supported && $("comparison-form").checkValidity();
  $("compute-button").disabled = !valid || !state.engineReady || state.pending !== null || !!state.caseAction;
  $("compute-button").textContent = state.pending !== null ? "Native engine running…" : state.engineReady ? "Compute selected comparison ↗" : "Numerical engine unavailable";
  $("inspect-joint").disabled = !valid || !!state.caseAction;
  $("case-download").disabled = !valid || !!state.caseAction;
  $("inspect-joint").textContent = state.caseAction === "inspect" ? "Opening joint details…" : "Inspect this joint";
  $("case-download").textContent = state.caseAction === "save" ? "Preparing editable case…" : "Save editable case";
}
function readDraft() {
  for (const [id, key, scale] of fields) state.draft.parameters[key] = $(id).valueAsNumber / scale;
  state.draft.parameters.gravity = $("gravity").checked;
  state.draft.baseline.volume_mm3 = $("reference-volume").valueAsNumber / 1000;
  state.draft.baseline.upper_diameter_mm = state.draft.parameters.upper_diameter_mm;
}
function boardRequest() {
  readDraft();
  return { schema: "soldershape.board-request.v1", board_sha256: state.context.source.board_sha256, reference: component().reference, pad_index: state.padIndex, parameters: clone(state.draft.parameters), baseline: clone(state.draft.baseline) };
}
function renderComponentOptions() {
  const query = $("component-search").value.trim().toLowerCase();
  const selected = component();
  const matches = state.context.components.filter((item) => `${item.reference} ${item.value}`.toLowerCase().includes(query));
  const visible = selected && !matches.includes(selected) ? [selected, ...matches] : matches;
  $("component-select").replaceChildren(...visible.map((item) => {
    const option = document.createElement("option");
    option.value = item.uuid;
    option.textContent = `${item.reference} · ${item.value || "No value"}${item.side === "back" ? " · back" : ""}`;
    return option;
  }));
  $("component-select").value = state.component;
}
function selectComponent(uuid, chosenPad = null) {
  state.component = uuid;
  const selected = component();
  if (!selected) return;
  const nextPad = selected.pads.find((item) => item.index === chosenPad) || selected.pads.find((item) => item.supported) || selected.pads[0];
  state.padIndex = nextPad?.index ?? null;
  invalidate();
  renderSelection();
}
function renderSelection() {
  const selected = component(), selectedPad = pad();
  renderComponentOptions();
  $("pad-select").replaceChildren(...selected.pads.map((item) => {
    const option = document.createElement("option"); option.value = item.index;
    option.textContent = `${item.identifier || "Unnumbered"} · ${item.net || "No net"}${item.supported ? "" : " · inspect only"}`;
    return option;
  }));
  if (!selected.pads.length) { const option = document.createElement("option"); option.textContent = "No source pads"; $("pad-select").append(option); }
  $("pad-select").value = state.padIndex ?? "";
  $("pad-select").disabled = !selected.pads.length;
  $("selected-heading").textContent = `${selected.reference}${selectedPad ? ` / pad ${selectedPad.identifier || "unnumbered"}` : " / graphic"}`;
  $("selection-status").textContent = selectedPad?.supported ? "Circular front pad" : "Inspect only";
  $("selection-status").className = `status-pill${selectedPad?.supported ? "" : " warn"}`;
  $("pad-net").textContent = selectedPad?.net || "No assigned net";
  $("pad-copper").textContent = selectedPad ? `${number(selectedPad.size_mm[0] * 1000, 1)} × ${number(selectedPad.size_mm[1] * 1000, 1)} µm · ${selectedPad.shape}` : "No pad geometry";
  $("pad-position").textContent = selectedPad ? `${number(selectedPad.board_xy_mm[0])}, ${number(selectedPad.board_xy_mm[1])} mm` : `${number(selected.board_position_mm[0])}, ${number(selected.board_position_mm[1])} mm`;
  $("pad-axis").textContent = `(${signed(selected.local_x_board[0], 4)}, ${signed(selected.local_x_board[1], 4)}) · ${number(selected.rotation_deg, 1)}°`;
  $("selection-scope").textContent = selectedPad?.supported ? "Copper geometry supports a circular-boundary hypothesis. The actual wettable rim, mask opening and process conditions remain unmeasured. Only this selected joint can be computed." : selectedPad?.unsupported_reason || "This source graphic has no solder pad to compute. Its original board artwork remains visible.";
  $("selection-scope").className = `selection-scope${selectedPad?.supported ? "" : " warn"}`;
  renderBoardOverlay();
  updateCompute();
  scheduleDraw();
}
function renderBoardOverlay() {
  const svg = $("board-overlay"), selected = component(), selectedPad = pad();
  const bounds = state.context.svg.bounds_mm;
  svg.setAttribute("viewBox", bounds.join(" "));
  const shapes = [];
  const components = [...state.context.components.filter((item) => item.uuid !== selected.uuid), selected];
  for (const item of components) {
    const [x, y, width, height] = item.bounds_mm;
    const rect = svgElement("rect", { x, y, width: Math.max(width, .7), height: Math.max(height, .7), rx: .15, class: `component-hit${item.uuid === selected.uuid ? " selected" : ""}` });
    const title = svgElement("title"); title.textContent = `${item.reference} · ${item.value || "Source graphic"}`; rect.append(title);
    rect.addEventListener("click", () => selectComponent(item.uuid));
    shapes.push(rect);
  }
  if (selectedPad) {
    const [x, y] = selectedPad.board_xy_mm, direction = selected.local_x_board;
    const end = [x + direction[0] * 5, y + direction[1] * 5];
    shapes.push(svgElement("circle", { cx: x, cy: y, r: .65, class: "selection-cross" }));
    shapes.push(svgElement("path", { d: `M ${x - 1} ${y} H ${x + 1} M ${x} ${y - 1} V ${y + 1}`, class: "selection-cross" }));
    const arrowLeft = [end[0] - direction[0] * .8 - direction[1] * .4, end[1] - direction[1] * .8 + direction[0] * .4];
    const arrowRight = [end[0] - direction[0] * .8 + direction[1] * .4, end[1] - direction[1] * .8 - direction[0] * .4];
    shapes.push(svgElement("path", { d: `M ${x} ${y} L ${end[0]} ${end[1]} M ${arrowLeft[0]} ${arrowLeft[1]} L ${end[0]} ${end[1]} L ${arrowRight[0]} ${arrowRight[1]}`, class: "axis-line" }));
    const label = svgElement("text", { x: end[0] + .5, y: end[1] - .5, class: "axis-label" }); label.textContent = "+X"; shapes.push(label);
  }
  svg.replaceChildren(...shapes);
  $("scale-bar").style.width = `${$("board-graphic").getBoundingClientRect().width * 10 / bounds[2]}px`;
}
function renderRecord(role, record) {
  const geometry = spec(record);
  $(role + "-title").textContent = geometry ? `${number(geometry.volume_mm3 * 1000, 2)} nL liquid solder` : `${role === "reference" ? "Reference" : "Candidate"} liquid volume`;
  const status = !record ? "Awaiting computation" : record.status === "failed" ? "Native solver failed" : record.model_warnings?.length ? "Outside model scope" : record.status === "refinement_checked" ? "Refinement checked" : "Numerical checks failed";
  $(role + "-status").textContent = status;
  $(role + "-status").className = `status-pill${!record || record.status === "refinement_checked" && !record.model_warnings?.length ? "" : record.status === "failed" ? " failed" : " warn"}`;
  for (const axis of ["x", "z"]) { const element = $(`${role}-force-${axis}`); element.textContent = signed(record?.forces?.[axis + "_uN"]); element.className = Number.isFinite(record?.forces?.[axis + "_uN"]) ? "" : "empty"; }
  $(role + "-empty").hidden = !!record?.mesh;
  $(role + "-empty").querySelector("strong").textContent = record ? "No checked geometry for this point" : "Compute the selected joint";
  $(role + "-empty").querySelector("p").textContent = record?.error || "Only a native result can supply this geometry.";
  $(role + "-mesh").textContent = record?.mesh ? `${record.mesh.triangles.length.toLocaleString()} triangles · ${number(geometry.standoff_mm * 1000, 1)} µm held gap · ${signed(geometry.offset_mm * 1000, 1)} µm offset` : "No current mesh";
  const warnings = record ? [...(record.diagnostics?.warnings || []), ...(record.model_warnings || []), ...(record.error ? [record.error] : [])] : [];
  setList($(role + "-warnings"), warnings); $(role + "-warnings").hidden = !warnings.length;
}
function renderResults() {
  const report = state.response?.report;
  renderRecord("reference", report?.results[0]); renderRecord("candidate", report?.results[1]);
  $("computed-badge").textContent = report?.results.some((item) => item.mesh) ? "1 selected joint computed · neighbors unsolved" : "0 joints computed in this view";
  $("result-origin").textContent = report ? report.recorded ? "Verified native recording" : "Fresh native computation" : "No current computation";
  $("bundle-download").disabled = !state.bundleUrl;
  const screen = report?.screen;
  const labels = { conditional_comparison: "CONDITIONAL FORCE COMPARISON", outside_model_scope: "COMPARISON BLOCKED BY MODEL SCOPE", numerical_failure: "COMPARISON BLOCKED BY NUMERICAL FAILURE" };
  $("screen-panel").className = `screen-panel${screen?.status === "outside_model_scope" ? " warn" : screen?.status === "numerical_failure" ? " failed" : ""}`;
  $("screen-status").textContent = screen ? labels[screen.status] || "CONDITIONAL FORCE COMPARISON" : "DECLARED FIXTURE OBJECTIVE";
  $("screen-headline").textContent = screen?.headline || "Seek lateral restoration without an upward separating force.";
  setList($("screen-details"), screen?.details || ["The gap remains held by an external fixture. No assembly motion is simulated."]);
  $("result-identity").textContent = report ? `${report.selection.reference} / pad ${report.selection.pad_identifier || "unnumbered"} · net ${report.selection.pad_net || "unassigned"} · exact source board SHA-256 ${report.selection.board_sha256}` : "Inspect or save valid inputs now. Board-bound numerical evidence requires a current computation.";
  updateCompute();
  for (const canvas of modelCanvases) { const ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height); }
  scheduleDraw();
}
function acceptResponse(response, revision) {
  if (revision !== state.revision) return false;
  const selection = response.report?.selection;
  if (!selection || selection.reference !== component().reference || selection.pad_index !== state.padIndex || selection.board_sha256 !== state.context.source.board_sha256) throw new Error("The response does not match the selected source pad.");
  if (!Array.isArray(response.report.results) || response.report.results.length !== 2) throw new Error("The engine did not return the two requested cases.");
  const bytes = Uint8Array.from(atob(response.bundle_base64), (character) => character.charCodeAt(0));
  clearResponse();
  state.response = response;
  state.bundleUrl = URL.createObjectURL(new Blob([bytes], { type: "application/zip" }));
  state.phase = "ready";
  renderResults();
  return true;
}
async function compute(event) {
  event.preventDefault();
  if (!state.engineReady || !pad()?.supported || state.pending !== null || state.caseAction || !$("comparison-form").reportValidity()) return;
  const request = boardRequest();
  saveDraft();
  state.revision += 1;
  const revision = state.revision;
  state.pending = revision;
  state.phase = "computing";
  clearResponse(); renderResults(); updateCompute();
  notice("Running two native equilibria and refinement checks. You can edit inputs; edited results will be discarded.", "working");
  try {
    const response = await api("/api/board/compare", request);
    if (acceptResponse(response, revision)) notice("Native computation complete. Inspect both force directions and the scope checks. Physical accuracy remains unqualified.");
  } catch (error) { if (revision === state.revision) { state.phase = "draft"; notice(`Computation unavailable. ${error.message}`, "error"); } }
  finally { if (state.pending === revision) state.pending = null; updateCompute(); if (revision !== state.revision) notice("Inputs changed. The previous response was discarded. Compute the current selection."); }
}
async function exportCase(action) {
  if (!state.token || !pad()?.supported || state.caseAction || !$("comparison-form").reportValidity()) return;
  const revision = state.revision;
  const request = boardRequest();
  saveDraft();
  state.caseAction = action;
  updateCompute();
  try {
    const response = await api("/api/board/case", request);
    if (revision !== state.revision) { notice("Inputs changed. The previous editable case was discarded. Try the current selection."); return; }
    if (action === "inspect") {
      const label = `Board explorer · ${response.selection.reference} / pad ${response.selection.pad_identifier || "unnumbered"}`;
      await window.SolderShapeUI.openCase(response.case, { label, href: "/board" }, state.token, () => revision === state.revision);
    } else {
      const blob = new Blob([JSON.stringify(response.case, null, 2) + "\n"], { type: "application/json" });
      download(blob, `soldershape-${response.selection.reference}-pad-${response.selection.pad_identifier || "unnumbered"}.json`);
      notice("Current editable inputs saved. The case needs fresh computation in Joint details.");
    }
  } catch (error) { notice(`Editable case unavailable. ${error.message}`, "error"); }
  finally { state.caseAction = null; updateCompute(); }
}
function canvasContext(canvas) {
  const bounds = canvas.getBoundingClientRect(), ratio = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(bounds.width * ratio) || canvas.height !== Math.round(bounds.height * ratio)) { canvas.width = Math.round(bounds.width * ratio); canvas.height = Math.round(bounds.height * ratio); }
  const ctx = canvas.getContext("2d"); ctx.setTransform(ratio, 0, 0, ratio, 0, 0); ctx.clearRect(0, 0, bounds.width, bounds.height);
  return { ctx, width: bounds.width, height: bounds.height };
}
function drawPads() {
  const { ctx, width, height } = canvasContext($("pad-canvas")), selected = component(), selectedPad = pad();
  state.padHits = [];
  if (!selected?.pads.length || !width || !height) return;
  const pads = selected.pads;
  const left = Math.min(...pads.map((item) => item.local_xy_mm[0] - item.size_mm[0] / 2));
  const right = Math.max(...pads.map((item) => item.local_xy_mm[0] + item.size_mm[0] / 2));
  const top = Math.min(...pads.map((item) => item.local_xy_mm[1] - item.size_mm[1] / 2));
  const bottom = Math.max(...pads.map((item) => item.local_xy_mm[1] + item.size_mm[1] / 2));
  const scale = Math.min((width - 52) / Math.max(right - left, .5), (height - 54) / Math.max(bottom - top, .5));
  const project = (x, y) => [width / 2 + (x - (left + right) / 2) * scale, (height - 18) / 2 + (y - (top + bottom) / 2) * scale];
  ctx.fillStyle = "#25404a";
  for (let x = 10; x < width; x += 18) for (let y = 10; y < height; y += 18) ctx.fillRect(x, y, 1, 1);
  for (const item of pads) {
    const [x, y] = project(...item.local_xy_mm), active = item.index === state.padIndex;
    ctx.beginPath();
    if (["circle", "oval"].includes(item.shape)) ctx.ellipse(x, y, item.size_mm[0] * scale / 2, item.size_mm[1] * scale / 2, 0, 0, Math.PI * 2);
    else ctx.rect(x - item.size_mm[0] * scale / 2, y - item.size_mm[1] * scale / 2, item.size_mm[0] * scale, item.size_mm[1] * scale);
    ctx.fillStyle = active ? "#f0b27c" : item.supported ? "#9a7454" : "#425d63"; ctx.fill();
    ctx.strokeStyle = active ? "#ffe5c4" : item.supported ? "#bd9674" : "#6e868a"; ctx.lineWidth = active ? 1.6 : .7; ctx.stroke();
    state.padHits.push({ index: item.index, x, y, radius: Math.max(item.size_mm[0], item.size_mm[1]) * scale / 2 });
  }
  if (selectedPad) {
    const [x, y] = project(...selectedPad.local_xy_mm);
    ctx.beginPath(); ctx.arc(x, y, Math.max(selectedPad.size_mm[0] * scale / 2 + 3, 5), 0, Math.PI * 2); ctx.strokeStyle = "#78d5cc"; ctx.lineWidth = 1; ctx.stroke();
    ctx.fillStyle = "#e4cfb5"; ctx.font = "9px ui-monospace,monospace"; ctx.textAlign = "left"; ctx.fillText(`PAD ${selectedPad.identifier || "UNNUMBERED"}`, 12, 17);
  }
  const barWidth = Math.min(width * .18, 50), barMm = barWidth / scale;
  ctx.strokeStyle = "#779aa6"; ctx.beginPath(); ctx.moveTo(width - barWidth - 14, height - 16); ctx.lineTo(width - 14, height - 16); ctx.stroke();
  ctx.fillStyle = "#8babb6"; ctx.font = "8px ui-monospace,monospace"; ctx.textAlign = "right"; ctx.fillText(`${number(barMm, 2)} mm`, width - 14, height - 23);
}
function pairView(records) {
  const specs = records.map(spec), center = [specs[0].offset_mm / 2, 0, Math.max(...specs.map((item) => item.standoff_mm)) / 2];
  let extent = Math.max(...specs.map((item) => Math.max(item.standoff_mm, item.lower_diameter_mm, item.upper_diameter_mm, Math.abs(item.offset_mm) + (item.lower_diameter_mm + item.upper_diameter_mm) / 2)));
  for (const record of records) for (const point of record.mesh?.vertices_mm || []) extent = Math.max(extent, ...point.map((coordinate, index) => Math.abs(coordinate - center[index]) * 2));
  const sizes = modelCanvases.map((canvas) => canvas.getBoundingClientRect());
  const scale = Math.min(...sizes.map((size) => Math.min(size.width * .7, size.height * .7))) / extent * camera.zoom;
  return { center, extent, scale };
}
function drawModel(canvas, record, view) {
  const { ctx, width, height } = canvasContext(canvas);
  if (!record?.mesh || !width || !height) return;
  const geometry = spec(record), cy = Math.cos(camera.yaw), sy = Math.sin(camera.yaw), ce = Math.cos(camera.elevation), se = Math.sin(camera.elevation);
  const project = (point) => { const [x, y, z] = point.map((value, index) => value - view.center[index]); return [width / 2 + (cy * x - sy * y) * view.scale, height * .52 + (se * (sy * x + cy * y) - ce * z) * view.scale, ce * (sy * x + cy * y) + se * z]; };
  const line = (a, b, color, weight = 1) => { const start = project(a), end = project(b); ctx.beginPath(); ctx.moveTo(start[0], start[1]); ctx.lineTo(end[0], end[1]); ctx.strokeStyle = color; ctx.lineWidth = weight; ctx.stroke(); };
  const ground = -view.extent * .08;
  for (let index = -4; index <= 4; index += 1) { const position = index * view.extent / 4; line([-view.extent + view.center[0], position, ground], [view.extent + view.center[0], position, ground], "#54819027", .7); line([position + view.center[0], -view.extent, ground], [position + view.center[0], view.extent, ground], "#54819027", .7); }
  window.SolderMesh.drawSurface(ctx, record.mesh, project, geometry.standoff_mm, $("mesh-edges").checked);
  for (const rim of [{ x: 0, z: 0, radius: geometry.lower_diameter_mm / 2, color: "#f0b27c" }, { x: geometry.offset_mm, z: geometry.standoff_mm, radius: geometry.upper_diameter_mm / 2, color: "#78d5cc" }]) {
    ctx.beginPath(); for (let index = 0; index <= 96; index += 1) { const angle = index * Math.PI * 2 / 96, point = project([rim.x + Math.cos(angle) * rim.radius, Math.sin(angle) * rim.radius, rim.z]); if (!index) ctx.moveTo(point[0], point[1]); else ctx.lineTo(point[0], point[1]); } ctx.strokeStyle = rim.color; ctx.lineWidth = 1.5; ctx.stroke();
  }
  const origin = [geometry.offset_mm, 0, geometry.standoff_mm];
  for (const arrow of [{ axis: "X", vector: [Math.sign(record.forces.x_uN), 0, 0], color: "#f0b27c" }, { axis: "Z", vector: [0, 0, Math.sign(record.forces.z_uN)], color: "#78d5cc" }]) {
    if (arrow.vector.every((value) => value === 0)) continue;
    const endPoint = origin.map((value, index) => value + arrow.vector[index] * view.extent * .22), start = project(origin), end = project(endPoint), angle = Math.atan2(end[1] - start[1], end[0] - start[0]);
    line(origin, endPoint, arrow.color, 1.6); ctx.beginPath(); ctx.moveTo(end[0] - 6 * Math.cos(angle - .45), end[1] - 6 * Math.sin(angle - .45)); ctx.lineTo(end[0], end[1]); ctx.lineTo(end[0] - 6 * Math.cos(angle + .45), end[1] - 6 * Math.sin(angle + .45)); ctx.strokeStyle = arrow.color; ctx.stroke(); ctx.fillStyle = arrow.color; ctx.font = "9px ui-monospace,monospace"; ctx.textAlign = "center"; ctx.fillText(arrow.axis, end[0] + Math.cos(angle) * 11, end[1] + Math.sin(angle) * 11 + 3);
  }
  const barWidth = .1 * view.scale; ctx.beginPath(); ctx.moveTo(19, height - 27); ctx.lineTo(19 + barWidth, height - 27); ctx.strokeStyle = "#88a7b7"; ctx.lineWidth = 1; ctx.stroke(); ctx.fillStyle = "#8cabb8"; ctx.font = "8px ui-monospace,monospace"; ctx.textAlign = "left"; ctx.fillText("100 µm", 19, height - 35);
}
function scheduleDraw() {
  if (framePending || !state.context) return;
  framePending = true;
  requestAnimationFrame(() => { framePending = false; drawPads(); const records = state.response?.report.results; if (records) { const view = pairView(records); drawModel(modelCanvases[0], records[0], view); drawModel(modelCanvases[1], records[1], view); } });
}
function download(url, filename) { SolderShapeUI.downloadFile(url, filename); }
$("comparison-form").addEventListener("submit", compute);
for (const input of $("comparison-form").querySelectorAll("input")) input.addEventListener("input", () => { readDraft(); invalidate(); });
$("component-search").addEventListener("input", () => { renderComponentOptions(); saveDraft(); });
$("component-select").addEventListener("change", () => selectComponent($("component-select").value));
$("pad-select").addEventListener("change", () => { state.padIndex = Number($("pad-select").value); invalidate(); renderSelection(); });
$("pad-canvas").addEventListener("click", (event) => { const bounds = event.currentTarget.getBoundingClientRect(), x = event.clientX - bounds.left, y = event.clientY - bounds.top; const hit = state.padHits.map((item) => ({ ...item, distance: Math.hypot(item.x - x, item.y - y) })).sort((a, b) => a.distance - b.distance)[0]; if (hit && hit.distance <= Math.max(hit.radius + 4, 7)) { state.padIndex = hit.index; invalidate(); renderSelection(); } });
$("pad-canvas").addEventListener("keydown", (event) => { if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(event.key) || !pad()) return; event.preventDefault(); const direction = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[event.key], origin = pad().local_xy_mm; const candidates = component().pads.map((item) => { const dx = item.local_xy_mm[0] - origin[0], dy = item.local_xy_mm[1] - origin[1]; return { item, forward: dx * direction[0] + dy * direction[1], sideways: Math.abs(dx * direction[1] - dy * direction[0]), distance: Math.hypot(dx, dy) }; }).filter((item) => item.forward > 1e-6).sort((a, b) => a.sideways - b.sideways || a.distance - b.distance); if (candidates.length) { state.padIndex = candidates[0].item.index; invalidate(); renderSelection(); } });
for (const canvas of modelCanvases) {
  canvas.addEventListener("pointerdown", (event) => { if (event.button !== 0) return; camera.drag = { x: event.clientX, y: event.clientY, id: event.pointerId }; canvas.setPointerCapture(event.pointerId); canvas.classList.add("dragging"); });
  canvas.addEventListener("pointermove", (event) => { if (!camera.drag || camera.drag.id !== event.pointerId) return; camera.yaw += (event.clientX - camera.drag.x) * .008; camera.elevation = Math.max(-1.2, Math.min(1.2, camera.elevation + (event.clientY - camera.drag.y) * .006)); camera.drag.x = event.clientX; camera.drag.y = event.clientY; scheduleDraw(); });
  const end = () => { camera.drag = null; canvas.classList.remove("dragging"); }; for (const eventName of ["pointerup", "pointercancel", "lostpointercapture"]) canvas.addEventListener(eventName, end);
  canvas.addEventListener("wheel", (event) => { event.preventDefault(); camera.zoom = Math.max(.55, Math.min(2.7, camera.zoom * Math.exp(-event.deltaY * .001))); scheduleDraw(); }, { passive: false });
  canvas.addEventListener("keydown", (event) => { if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "=", "-", "Home"].includes(event.key)) return; event.preventDefault(); if (event.key === "Home") Object.assign(camera, initialCamera); if (event.key === "ArrowLeft") camera.yaw -= .1; if (event.key === "ArrowRight") camera.yaw += .1; if (event.key === "ArrowUp") camera.elevation = Math.min(1.2, camera.elevation + .1); if (event.key === "ArrowDown") camera.elevation = Math.max(-1.2, camera.elevation - .1); if (["+", "="].includes(event.key)) camera.zoom = Math.min(2.7, camera.zoom * 1.1); if (event.key === "-") camera.zoom = Math.max(.55, camera.zoom / 1.1); scheduleDraw(); });
}
$("reset-view").addEventListener("click", () => { Object.assign(camera, initialCamera); scheduleDraw(); });
$("mesh-edges").addEventListener("change", scheduleDraw);
$("bundle-download").addEventListener("click", () => { if (state.bundleUrl) download(state.bundleUrl, state.response.bundle_filename || "soldershape-board-evidence.zip"); });
$("case-download").addEventListener("click", () => exportCase("save"));
$("inspect-joint").addEventListener("click", () => exportCase("inspect"));
window.addEventListener("pagehide", saveDraft);
window.addEventListener("resize", () => { if (state.context) renderBoardOverlay(); scheduleDraw(); });
async function load() {
  try {
    const [bootstrap, data] = await Promise.all([api("/api/bootstrap"), api("/api/board")]);
    state.token = bootstrap.token; state.engineReady = !!bootstrap.engine.ready; state.context = data.context; state.draft = clone(data.default_request);
    for (const [id, key, scale] of fields) $(id).value = number(state.draft.parameters[key] * scale, 8);
    $("reference-volume").value = number(state.draft.baseline.volume_mm3 * 1000, 8); $("gravity").checked = state.draft.parameters.gravity;
    const initial = state.context.components.find((item) => item.reference === state.draft.reference && item.pads.some((item) => item.index === state.draft.pad_index)) || state.context.components.find((item) => item.pads.some((pad) => pad.supported));
    state.component = initial.uuid; state.padIndex = state.draft.pad_index;
    if (!initial.pads.some((item) => item.index === state.padIndex)) state.padIndex = initial.pads.find((item) => item.supported)?.index ?? initial.pads[0]?.index ?? null;
    const restored = restoreDraft();
    state.phase = "draft";
    $("component-count").textContent = `${state.context.components.length} actual components`;
    $("pad-count").textContent = `${state.context.components.reduce((count, item) => count + item.pads.length, 0).toLocaleString()} actual pads`;
    $("board-size").textContent = `${number(state.context.bounds_mm[2], 2)} × ${number(state.context.bounds_mm[3], 2)} mm`;
    $("board-digest").textContent = `Source commit ${state.context.source.commit} · Board SHA-256 ${state.context.source.board_sha256}`;
    $("extraction-digest").textContent = `Native KiCad ${state.context.extraction.kicad_version} · Extractor SHA-256 ${state.context.extraction.extractor_sha256}`;
    $("source-link").href = `${state.context.source.repository.replace(/\/$/, "")}/tree/${state.context.source.commit}`;
    document.getElementById("workspace-engine").textContent = state.engineReady ? `Surface Evolver ${bootstrap.engine.version} · ready` : "Numerical engine unavailable";
    $("engine-notice").hidden = state.engineReady;
    $("engine-notice").textContent = bootstrap.engine.error || "The numerical engine is unavailable. You can still inspect and save editable inputs.";
    $("explorer").hidden = false; $("load-notice").hidden = true;
    renderSelection(); renderResults();
    notice(restored ? "Board inputs restored in this tab. Prior forces were cleared. Inspect or compute the current joint." : "The source pad is selected. Inspect its editable inputs or compute fresh forces for these hypothetical process inputs.");
    const revision = state.revision;
    if (data.recorded_preview && !restored) {
      try { const recorded = await api("/api/board/recorded"); if (acceptResponse(recorded, revision)) notice("Verified recording of the initial hypothesis. Use Compute selected comparison for fresh native results."); }
      catch (error) { if (revision === state.revision && !state.response && state.pending === null) notice(`Initial recording unavailable. Fresh computation remains available. ${error.message}`); }
    }
  } catch (error) { $("load-notice").hidden = false; $("load-notice").className = "notice error"; $("load-notice").textContent = `The board extraction is unavailable. ${error.message}`; $("explorer").hidden = true; }
}
load();
