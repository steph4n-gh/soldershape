"use strict";

const $ = (id) => document.getElementById(id);
const form = $("joint-form");
const parameterNames = ["upper_diameter_mm", "volume_mm3", "offset_mm", "surface_tension_n_m", "density_g_cm3"];
const state = {
  token: null,
  engineReady: false,
  revision: 0,
  footprintText: "",
  footprint: null,
  padIndex: null,
  baseline: null,
  importing: false,
  caseAction: null,
  pending: null,
  response: null,
  resultIndex: -1,
};
const camera = { yaw: -0.57, elevation: 0.39, zoom: 1, drag: null };
const colors = { copper: "#e8a975", teal: "#69c7c8", muted: "#8da3b7", grid: "#2a3c4d" };
let footprintHitAreas = [];
let chartHitAreas = [];
let framePending = false;

function number(value, digits = 3) {
  if (!Number.isFinite(value)) return "—";
  if (value === 0) return "0";
  if (Math.abs(value) >= 10000 || Math.abs(value) < 0.0001) return value.toExponential(3);
  if (Math.abs(value) < 10 ** -digits) return String(Number(value.toPrecision(3)));
  return value.toFixed(digits).replace(/\.?0+$/, "");
}

function percent(value) {
  if (!Number.isFinite(value)) return "—";
  if (value === 0) return "0%";
  return `${Number((Math.abs(value) * 100).toPrecision(3))}%`;
}

function pad() {
  return state.footprint?.pads.find((item) => item.index === state.padIndex) || null;
}

function selectedResult() {
  return state.response?.results[state.resultIndex] || null;
}

function resultSpec(result) {
  return result?.equilibrium || result?.input || null;
}

function loadMode() {
  return $("load_mode").value === "load";
}

function updateLoadMode() {
  const loaded = loadMode();
  $("gap-field").hidden = loaded;
  $("standoff_mm").disabled = loaded;
  $("standoff_mm").required = !loaded;
  $("load-field").hidden = !loaded;
  $("load-help").hidden = !loaded;
  $("normal_load_uN").disabled = !loaded;
  $("normal_load_uN").required = loaded;
  $("reference-help").textContent = `Stores upper pad diameter and solder volume. Comparison recomputes both designs using the current board pad, ${loaded ? "normal load" : "gap"}, offset, and material.`;
  $("geometry-help").textContent = loaded
    ? "Enter liquid solder volume, excluding pad metal. The solved gap separates the two wetted pad planes. The curved surface can extend beyond those planes."
    : "Enter liquid solder volume, excluding pad metal. The gap is the separation of the two wetted pad planes. The curved surface can extend beyond those planes.";
}

function freeze(value) {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value)) freeze(child);
  }
  return value;
}

function notice(message = "", kind = "") {
  $("notice").textContent = message;
  $("notice").className = `notice ${kind}`;
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

function clearComputed() {
  state.response = null;
  state.resultIndex = -1;
  renderResults();
}

function invalidate() {
  const hadResult = !!state.response;
  state.revision += 1;
  clearComputed();
  if (state.pending) notice("Inputs changed while computation runs. Its response will be discarded.", "working");
  else if (hadResult) notice("Inputs changed. Solve again to update the geometry and downloads.");
  else notice();
  updateControls();
  scheduleDraw();
}

function readParameters() {
  const parameters = {};
  for (const name of parameterNames) parameters[name] = $(name).valueAsNumber;
  const verticalCondition = loadMode() ? "normal_load_uN" : "standoff_mm";
  parameters[verticalCondition] = $(verticalCondition).valueAsNumber;
  parameters.gravity = $("gravity").checked;
  return parameters;
}

function editableCase(parameters = readParameters()) {
  return {
    schema: "soldershape.case.v1",
    footprint_text: state.footprintText,
    pad_index: state.padIndex,
    parameters,
    baseline: state.baseline,
  };
}

function previewSpec() {
  const selected = pad();
  if (!selected?.supported || loadMode()) return null;
  const parameters = readParameters();
  if (!Object.values(parameters).every((value) => typeof value === "boolean" || Number.isFinite(value))) return null;
  return { ...parameters, lower_diameter_mm: selected.size_mm[0] };
}

function updateControls() {
  const hasInputs = !!state.token && !!pad()?.supported && !state.importing && !state.caseAction;
  const canCompute = hasInputs && state.engineReady && !state.pending;
  $("solve-button").disabled = !canCompute;
  $("sweep-button").disabled = !canCompute;
  $("compare-button").disabled = !canCompute || !state.baseline;
  $("compare-button").textContent = state.pending === "compare" ? "Computing both designs…" : "Compare reference and candidate";
  $("reference-button").disabled = !hasInputs;
  $("clear-reference-button").hidden = !state.baseline;
  $("clear-reference-button").disabled = !!state.caseAction;
  $("reference-values").textContent = state.baseline
    ? `Upper pad Ø ${number(state.baseline.upper_diameter_mm, 5)} mm · solder ${number(state.baseline.volume_mm3, 6)} mm³`
    : "No reference saved.";
  $("save-case-button").disabled = !hasInputs;
  $("save-case-button").textContent = state.caseAction === "save" ? "Saving case…" : "Save editable case";
  $("case-file").disabled = !state.token || state.importing || !!state.caseAction;
  $("solve-label").textContent = state.pending === "solve" ? "Solving joint…" : "Solve joint";
  $("sweep-button").replaceChildren(document.createTextNode(state.pending === "sweep" ? "Computing sweep…" : "Run offset sweep"));
  const count = document.createElement("span");
  count.className = "button-detail";
  count.textContent = "5 points";
  $("sweep-button").append(count);
  $("download-button").disabled = !state.response?.bundle_base64 || !!state.pending || !!state.caseAction;
  $("pad-select").disabled = !state.footprint || state.importing || !!state.caseAction;
  $("example-button").disabled = !state.token || state.importing || !!state.caseAction;
  $("footprint-file").disabled = !state.token || state.importing || !!state.caseAction;
  const offset = Math.abs($("offset_mm").valueAsNumber);
  $("sweep-note").textContent = Number.isFinite(offset)
    ? offset > 0
      ? `Five independent solves between −${number(offset, 5)} and +${number(offset, 5)} mm${loadMode() ? ", each with a gap solved under the current normal load" : " at the current prescribed gap"}.`
      : "Set a nonzero lateral offset to define the sweep range."
    : "The lateral offset sets the sweep range.";
}

function renderFootprint() {
  const footprint = state.footprint;
  $("footprint-name").textContent = footprint ? footprint.name : state.importing ? "Reading footprint…" : "Choose a footprint";
  $("pad-count").textContent = footprint ? `${footprint.pads.length} PADS / TOP VIEW` : "NO PADS";
  const selected = pad();
  $("lower-diameter").textContent = selected
    ? selected.supported ? `${number(selected.size_mm[0], 5)} mm` : `${number(selected.size_mm[0])} × ${number(selected.size_mm[1])} mm`
    : "—";
  let pitch = Infinity;
  if (selected) {
    for (const other of footprint.pads) {
      if (other.index !== selected.index) pitch = Math.min(pitch, Math.hypot(other.x_mm - selected.x_mm, other.y_mm - selected.y_mm));
    }
  }
  $("pad-pitch").textContent = Number.isFinite(pitch) ? `${number(pitch, 5)} mm` : "—";
  $("pad-message").textContent = selected
    ? selected.supported ? "Board diameter comes from this copper pad. Its edge is a pinned, fully wetted boundary." : selected.unsupported_reason
    : "Circular copper SMD pads are supported.";
  $("pad-message").className = `pad-message${selected && !selected.supported ? " unsupported" : ""}`;
  scheduleDraw();
}

function populatePads() {
  const select = $("pad-select");
  select.replaceChildren();
  if (!state.footprint) {
    const option = document.createElement("option");
    option.textContent = "Import a footprint first";
    select.append(option);
  } else {
    for (const item of state.footprint.pads) {
      const option = document.createElement("option");
      option.value = String(item.index);
      option.textContent = `Pad ${item.identifier}${item.supported ? "" : " · unsupported"}`;
      select.append(option);
    }
    select.value = String(state.padIndex);
  }
}

async function importText(text, revision) {
  try {
    const data = await api("/api/import", { footprint_text: text });
    if (revision !== state.revision) return;
    state.footprintText = text;
    state.footprint = data.footprint;
    state.padIndex = data.footprint.pads.find((item) => item.supported)?.index ?? data.footprint.pads[0].index;
    populatePads();
    notice();
  } catch (error) {
    if (revision === state.revision) notice(error.message, "error");
  } finally {
    state.importing = false;
    populatePads();
    renderFootprint();
    updateControls();
  }
}

function beginImport() {
  invalidate();
  state.importing = true;
  state.baseline = null;
  state.footprintText = "";
  state.footprint = null;
  state.padIndex = null;
  populatePads();
  renderFootprint();
  updateControls();
  return state.revision;
}

async function bootstrap() {
  const data = await api("/api/bootstrap");
  state.token = data.token;
  const engine = data.engine || {};
  state.engineReady = data.engine_ready ?? engine.ready ?? engine.available ?? !!engine.version;
  const label = state.engineReady ? `Surface Evolver ${engine.version || ""} · ready`.replace(/\s+·/, " ·") : "Engine unavailable";
  $("engine-label").textContent = label;
  $("engine-state").className = `engine-state ${state.engineReady ? "ready" : "unavailable"}`;
  if (!state.engineReady) notice(engine.error || data.engine_error || "The numerical engine is unavailable. Run the setup command shown in the project README.", "error");
  updateControls();
  return data;
}

async function compute(kind) {
  if (state.pending || state.caseAction || !state.engineReady || !pad()?.supported) return;
  if (!form.reportValidity()) return;
  const parameters = readParameters();
  const body = kind === "compare" ? editableCase(parameters) : {
    footprint_text: state.footprintText, pad_index: state.padIndex, parameters, baseline: state.baseline,
  };
  if (kind === "compare" && !state.baseline) return;
  if (kind === "sweep") {
    const magnitude = Math.abs(parameters.offset_mm);
    if (magnitude === 0) {
      notice("Set a nonzero lateral offset before running the sweep.", "error");
      $("offset_mm").focus();
      return;
    }
    body.offsets_mm = [-1, -0.5, 0, 0.5, 1].map((factor) => Number((factor * magnitude).toPrecision(12)));
  }
  const revision = state.revision;
  state.pending = kind;
  clearComputed();
  updateControls();
  const progress = {
    solve: "Computing the equilibrium and checking mesh refinement. This may take a minute.",
    sweep: "Computing five independent equilibria. Each point includes a mesh refinement check. This may take a few minutes.",
    compare: "Recomputing the reference and candidate with the current shared conditions. Each design includes a mesh refinement check.",
  };
  notice(progress[kind], "working");
  try {
    const response = await api(`/api/${kind}`, body);
    if (revision !== state.revision) {
      notice("Inputs changed. The obsolete computation was discarded. Solve again with the current inputs.");
      return;
    }
    if (!Array.isArray(response.results) || !response.results.length) throw new Error("The engine returned no computation results.");
    state.response = freeze(response);
    state.resultIndex = response.results.findIndex((result) => result.status !== "failed" && result.mesh);
    if (state.resultIndex < 0) state.resultIndex = 0;
    renderResults();
    const failures = response.results.filter((result) => result.status === "failed").length;
    const unchecked = response.results.filter((result) => result.status === "not_converged").length;
    if (failures || unchecked) notice(`${response.results.length} point${response.results.length === 1 ? "" : "s"} returned. ${failures} failed; ${unchecked} did not pass the numerical checks. Inspect each row before interpreting its forces.`, "working");
    else if (response.comparison?.status === "inconclusive") notice(response.comparison.reason || "The comparison is inconclusive. Inspect its numerical evidence.", "working");
    else notice("Computation complete. Inspect the numerical checks and download the reproducible results. Physical accuracy remains unqualified.");
  } catch (error) {
    if (revision === state.revision) notice(error.message, "error");
  } finally {
    state.pending = null;
    updateControls();
    scheduleDraw();
  }
}

function statusLabel(status) {
  return { refinement_checked: "Numerically checked", not_converged: "Not converged", failed: "Failed" }[status] || "Awaiting computation";
}

function statusClass(status) {
  return { refinement_checked: "good", not_converged: "warn", failed: "failed" }[status] || "";
}

function tableCell(row, text, className = "") {
  const cell = document.createElement("td");
  cell.textContent = text;
  cell.className = className;
  row.append(cell);
  return cell;
}

function selectResult(index) {
  if (!state.response || index < 0 || index >= state.response.results.length) return;
  state.resultIndex = index;
  renderResults();
}

function renderResults() {
  const result = selectedResult();
  const spec = resultSpec(result);
  const loaded = Number.isFinite(result?.input?.normal_load_uN);
  const hasMesh = !!result?.mesh;
  const diagnostics = result?.diagnostics || {};
  const comparison = state.response?.comparison;
  const comparisonChecked = !!comparison && comparison.status === "compared"
    && state.response.results.length === 2
    && state.response.results.every((item) => item.status === "refinement_checked"
      && Number.isFinite(item.input?.offset_mm) && (item.input.offset_mm !== 0 || Number.isFinite(item.input?.normal_load_uN))
      && Number.isFinite(item.forces?.x_uN) && Number.isFinite(item.forces?.z_uN));
  $("force-heading").textContent = comparison && result?.design ? `${result.design} force on the upper pad` : "Force on the upper pad";
  $("force-x").textContent = number(result?.forces?.x_uN);
  $("force-z").textContent = number(result?.forces?.z_uN);
  $("result-status").textContent = statusLabel(result?.status);
  $("result-status").className = `result-status ${statusClass(result?.status)}`;
  $("check-force").textContent = percent(diagnostics.force_change_relative);
  $("check-volume").textContent = percent(diagnostics.volume_relative_error);
  $("check-eigenvalues").textContent = Number.isFinite(diagnostics.negative_eigenvalues) ? String(diagnostics.negative_eigenvalues) : "—";
  $("check-closed").textContent = result?.mesh_checks ? result.mesh_checks.closed ? "Yes" : "No" : "—";
  $("check-closed").className = result?.mesh_checks ? result.mesh_checks.closed ? "good" : "warn" : "";
  $("check-mesh-volume").textContent = percent(diagnostics.mesh_volume_error_relative);
  $("check-eigenvalues").className = Number.isFinite(diagnostics.negative_eigenvalues) ? diagnostics.negative_eigenvalues === 0 ? "good" : "warn" : "";
  $("load-equilibrium").hidden = !loaded;
  $("solved-gap").textContent = Number.isFinite(spec?.standoff_mm) ? `${number(spec.standoff_mm, 6)} mm` : "—";
  $("supported-load").textContent = loaded ? `${number(result.input.normal_load_uN)} µN` : "—";
  $("load-residual").textContent = Number.isFinite(result?.load_balance?.residual_uN) ? `${number(result.load_balance.residual_uN, 6)} µN` : "—";
  $("load-balance-note").textContent = result?.status === "failed"
    ? "No equilibrium gap is available for this failed point."
    : `Residual is the upward solder force minus the prescribed downward load.${Number.isFinite(result?.load_balance?.tolerance_uN) ? ` Numerical tolerance ${number(result.load_balance.tolerance_uN, 6)} µN.` : ""} A numerical balance does not establish physical accuracy.`;
  const numericalWarnings = result?.status === "failed" ? [result.error || "This point failed. No computed geometry is available."] : diagnostics.warnings || [];
  const warnings = [...numericalWarnings, ...(result?.model_warnings || [])];
  const warningList = $("result-warnings");
  warningList.replaceChildren();
  warningList.hidden = !warnings.length;
  for (const warning of warnings) {
    const item = document.createElement("li");
    item.textContent = warning;
    warningList.append(item);
  }
  const levelsBody = $("levels-body");
  levelsBody.replaceChildren();
  for (const level of result?.levels || []) {
    const row = document.createElement("tr");
    tableCell(row, String(level.level));
    tableCell(row, String(level.facets));
    tableCell(row, number(level.force_x_uN));
    tableCell(row, number(level.force_z_uN));
    tableCell(row, percent(level.volume_relative_error));
    levelsBody.append(row);
  }
  if (!levelsBody.children.length) {
    const row = document.createElement("tr");
    tableCell(row, result?.status === "failed" ? "No completed numerical levels." : "No computed result.").colSpan = 5;
    levelsBody.append(row);
  }
  $("engine-provenance").textContent = result?.engine
    ? `Surface Evolver ${result.engine.version}. Source SHA-256 ${result.engine.source_sha256}. Binary SHA-256 ${result.engine.binary_sha256}.`
    : "The result bundle records the exact model, engine identity, and raw output.";
  $("input-digest").textContent = result?.input_sha256 ? `Input SHA-256 ${result.input_sha256}` : "";
  $("model-caption").textContent = hasMesh
    ? `${result.design ? `${result.design} · ` : ""}computed mesh · gap ${number(spec?.standoff_mm, 5)} mm · offset ${number(spec?.offset_mm, 5)} mm · ${statusLabel(result.status).toLowerCase()}`
    : result?.status === "failed" ? "Failed point. No computed mesh is available." : loadMode() ? "Solve to compute the gap and geometry." : "Boundary preview. Solve to compute the joint.";
  $("mesh-summary").textContent = hasMesh
    ? `${result.mesh.vertices_mm.length.toLocaleString()} vertices · ${result.mesh.triangles.length.toLocaleString()} triangles · pinned pad boundaries`
    : "Circular, fully wetted, pinned boundaries";
  $("empty-model").hidden = !!previewSpec() || hasMesh;
  $("sweep-heading").textContent = comparison ? "Reference and candidate" : "Offset response";
  $("chart-wrap").hidden = !!comparison;
  $("chart-legend").hidden = !!comparison;
  $("comparison-summary").hidden = !comparison;
  if (comparison) {
    const delta = comparison.delta || {};
    const signed = (value, digits = 3) => Number.isFinite(value) ? `${value > 0 ? "+" : ""}${number(value, digits)}` : "—";
    $("comparison-delta").textContent = comparisonChecked
      ? `Candidate minus reference: solder volume ${signed(delta.volume_mm3, 6)} mm³ (${signed(delta.volume_percent, 2)}%); gap ${signed(delta.gap_mm, 6)} mm; restoring force ${signed(delta.restoring_force_uN)} µN; vertical force ${signed(delta.vertical_force_uN)} µN.`
      : `Comparison inconclusive. ${comparison.reason || "Both designs must pass the numerical checks at a nonzero offset before comparing forces."}`;
    $("comparison-scope").textContent = `${comparison.scope || `Both designs use the current board pad, ${loaded ? "normal load" : "gap"}, offset, and material.`} A larger restoring force means a stronger force toward alignment under these conditions. This does not select a manufacturing design.`;
  }
  const head = $("results-head");
  head.replaceChildren();
  const headers = comparison
    ? ["Design", "Upper pad · mm", "Volume · mm³", "Gap · mm", "X force · µN", "Z force · µN", "Numerical status", "View geometry"]
    : ["Offset · mm", "Gap · mm", "X force · µN", "Z force · µN", "Numerical status", "View geometry"];
  for (const label of headers) {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = label;
    head.append(cell);
  }
  const sweepBody = $("sweep-body");
  sweepBody.replaceChildren();
  if (state.response) {
    state.response.results.forEach((item, index) => {
      const geometry = resultSpec(item);
      const row = document.createElement("tr");
      row.className = `result-row${index === state.resultIndex ? " selected" : ""}`;
      if (comparison) {
        tableCell(row, item.design || comparison.designs?.[index]?.role || `Design ${index + 1}`);
        tableCell(row, number(geometry?.upper_diameter_mm, 5));
        tableCell(row, number(geometry?.volume_mm3, 6));
      } else tableCell(row, number(geometry?.offset_mm, 5));
      tableCell(row, number(geometry?.standoff_mm, 6));
      tableCell(row, number(item.forces?.x_uN));
      tableCell(row, number(item.forces?.z_uN));
      const status = tableCell(row, statusLabel(item.status), `row-status ${statusClass(item.status)}`);
      if (item.error) status.title = item.error;
      const action = tableCell(row, "");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "view-row";
      button.textContent = index === state.resultIndex ? "Selected" : "View";
      button.setAttribute("aria-label", comparison ? `View ${item.design || `design ${index + 1}`} result` : `View result at offset ${number(item.input?.offset_mm, 5)} millimeters`);
      button.setAttribute("aria-pressed", String(index === state.resultIndex));
      action.append(button);
      row.addEventListener("click", () => selectResult(index));
      sweepBody.append(row);
    });
    const gapDescription = state.response.results.map((item, index) => {
      const geometry = resultSpec(item);
      const gap = Number.isFinite(geometry?.standoff_mm) ? `${number(geometry.standoff_mm, 6)} mm` : "unavailable";
      return `${item.design || comparison?.designs?.[index]?.role || `Design ${index + 1}`} gap ${gap}.`;
    }).join(" ");
    const condition = loaded
      ? `under normal load ${number(result.input.normal_load_uN)} µN per joint at offset ${number(spec?.offset_mm, 5)} mm. ${gapDescription}`
      : `at gap ${number(spec?.standoff_mm, 5)} mm and offset ${number(spec?.offset_mm, 5)} mm.`;
    $("sweep-description").textContent = comparison
      ? `Both designs freshly computed ${condition} Select a design to inspect its mesh.`
      : `${state.response.results.length} independently computed point${state.response.results.length === 1 ? ". Run a sweep to compare offsets." : `s at the current ${loaded ? "normal load, each with its own solved gap" : "prescribed gap"}. Select a row to inspect its mesh.`}`;
  } else {
    const row = document.createElement("tr");
    row.className = "placeholder-row";
    tableCell(row, "Computed points will appear here.").colSpan = headers.length;
    sweepBody.append(row);
    $("sweep-description").textContent = loadMode()
      ? "Compare five offsets under the current normal load. The gap is solved at each offset."
      : "Compare independent equilibria at five offsets with the current prescribed gap.";
  }
  updateControls();
  scheduleDraw();
}

function canvasContext(canvas) {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const ratio = window.devicePixelRatio || 1;
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
  }
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, width, height);
  return { context, width, height };
}

function scheduleDraw() {
  if (framePending) return;
  framePending = true;
  requestAnimationFrame(() => {
    framePending = false;
    drawFootprint();
    drawModel();
    drawChart();
  });
}

function drawFootprint() {
  const { context: ctx, width, height } = canvasContext($("footprint-canvas"));
  footprintHitAreas = [];
  ctx.strokeStyle = "#26394a";
  ctx.lineWidth = 0.5;
  for (let x = 12; x < width; x += 17) {
    for (let y = 12; y < height; y += 17) {
      ctx.beginPath();
      ctx.moveTo(x - 1, y);
      ctx.lineTo(x + 1, y);
      ctx.moveTo(x, y - 1);
      ctx.lineTo(x, y + 1);
      ctx.stroke();
    }
  }
  if (!state.footprint) return;
  const pads = state.footprint.pads;
  const xMin = Math.min(...pads.map((item) => item.x_mm - Math.max(...item.size_mm) / 2));
  const xMax = Math.max(...pads.map((item) => item.x_mm + Math.max(...item.size_mm) / 2));
  const yMin = Math.min(...pads.map((item) => item.y_mm - Math.max(...item.size_mm) / 2));
  const yMax = Math.max(...pads.map((item) => item.y_mm + Math.max(...item.size_mm) / 2));
  const scale = Math.min((width - 46) / Math.max(xMax - xMin, 0.01), (height - 55) / Math.max(yMax - yMin, 0.01));
  const centerX = (xMin + xMax) / 2;
  const centerY = (yMin + yMax) / 2;
  for (const item of pads) {
    const x = width / 2 + (item.x_mm - centerX) * scale;
    const y = (height - 14) / 2 + (item.y_mm - centerY) * scale;
    const rx = item.size_mm[0] * scale / 2;
    const ry = item.size_mm[1] * scale / 2;
    const selected = item.index === state.padIndex;
    footprintHitAreas.push({ x, y, radius: Math.max(7, rx, ry), index: item.index });
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(-item.angle_deg * Math.PI / 180);
    ctx.beginPath();
    if (item.shape === "circle" || item.shape === "oval") ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI * 2);
    else ctx.rect(-rx, -ry, rx * 2, ry * 2);
    ctx.fillStyle = selected ? "#e8a975" : item.supported ? "#8e684d" : "#3a4553";
    ctx.fill();
    ctx.lineWidth = selected ? 1.5 : 1;
    ctx.strokeStyle = selected ? "#ffdec1" : item.supported ? "#bc8d67" : "#7b8490";
    if (!item.supported) ctx.setLineDash([3, 2]);
    ctx.stroke();
    if (selected) {
      ctx.setLineDash([]);
      ctx.beginPath();
      ctx.arc(0, 0, Math.max(rx, ry) + 4, 0, Math.PI * 2);
      ctx.strokeStyle = "#e8a97570";
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    ctx.restore();
    if (Math.min(rx, ry) >= 7) {
      ctx.font = `${Math.min(11, Math.max(8, rx * 0.6))}px ui-monospace, monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillStyle = selected ? "#3b2b20" : "#e8c6a8";
      ctx.fillText(item.identifier, x, y, Math.max(rx * 1.7, 12));
    }
  }
}

function drawModel() {
  const { context: ctx, width, height } = canvasContext($("model-canvas"));
  const result = selectedResult();
  const geometry = result ? resultSpec(result) : previewSpec();
  const spec = Number.isFinite(geometry?.standoff_mm) ? geometry : null;
  const emptyModel = $("empty-model");
  emptyModel.hidden = !!spec;
  if (!spec) {
    const selected = pad();
    emptyModel.querySelector("strong").textContent = result?.status === "failed" ? "No computed geometry" : selected ? selected.supported ? loadMode() ? "Solve to compute the gap and geometry" : "Complete the joint parameters" : "Select a circular copper pad" : "Start with a board pad";
    emptyModel.querySelector("span:last-child").textContent = result?.status === "failed" ? "Inspect the failure evidence before changing the inputs." : selected ? selected.supported ? loadMode() ? "The supported load determines the equilibrium gap." : "Enter valid dimensions to preview the boundaries." : selected.unsupported_reason : "Import a footprint or load the example.";
  }
  if (!spec || width < 1 || height < 1) return;
  const lowerRadius = spec.lower_diameter_mm / 2;
  const upperRadius = spec.upper_diameter_mm / 2;
  const extent = Math.max(spec.standoff_mm, spec.lower_diameter_mm, spec.upper_diameter_mm, Math.abs(spec.offset_mm) + lowerRadius + upperRadius, 0.001);
  const scale = Math.min(width * 0.65, height * 0.69) / extent * camera.zoom;
  const center = [spec.offset_mm / 2, 0, spec.standoff_mm / 2];
  const cy = Math.cos(camera.yaw), sy = Math.sin(camera.yaw);
  const ce = Math.cos(camera.elevation), se = Math.sin(camera.elevation);
  function rotate(point) {
    const x = point[0] - center[0], y = point[1] - center[1], z = point[2] - center[2];
    return [cy * x - sy * y, se * (sy * x + cy * y) - ce * z, ce * (sy * x + cy * y) + se * z];
  }
  function project(point) {
    const rotated = rotate(point);
    return [width / 2 + rotated[0] * scale, height * 0.53 + rotated[1] * scale, rotated[2]];
  }
  function line(a, b, color, lineWidth = 1) {
    const start = project(a), end = project(b);
    ctx.beginPath();
    ctx.moveTo(start[0], start[1]);
    ctx.lineTo(end[0], end[1]);
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.stroke();
  }
  const gridExtent = extent * 1.2;
  for (let i = -5; i <= 5; i += 1) {
    const t = i * gridExtent / 5;
    line([-gridExtent + center[0], t, -extent * 0.09], [gridExtent + center[0], t, -extent * 0.09], "#35506935", 0.7);
    line([t + center[0], -gridExtent, -extent * 0.09], [t + center[0], gridExtent, -extent * 0.09], "#35506935", 0.7);
  }
  const mesh = result?.mesh;
  if (mesh) {
    const projected = mesh.vertices_mm.map(project);
    const faces = mesh.triangles.map((triangle) => {
      const points = triangle.map((index) => projected[index]);
      const vertices = triangle.map((index) => mesh.vertices_mm[index]);
      const a = vertices[0], b = vertices[1], c = vertices[2];
      const ux = b[0] - a[0], uy = b[1] - a[1], uz = b[2] - a[2];
      const vx = c[0] - a[0], vy = c[1] - a[1], vz = c[2] - a[2];
      const normal = [uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx];
      const magnitude = Math.hypot(...normal) || 1;
      const light = Math.max(0, (normal[0] * -0.35 + normal[1] * -0.4 + normal[2] * 0.85) / magnitude);
      const shade = 0.62 + 0.38 * light;
      const flatCap = Math.abs(a[2] - b[2]) < 1e-9 && Math.abs(a[2] - c[2]) < 1e-9 && (Math.abs(a[2]) < 1e-8 || Math.abs(a[2] - spec.standoff_mm) < 1e-8);
      const base = flatCap ? [198, 139, 91] : [173, 199, 214];
      return { points, depth: (points[0][2] + points[1][2] + points[2][2]) / 3, color: `rgb(${base.map((component) => Math.round(component * shade)).join(",")})` };
    });
    faces.sort((a, b) => a.depth - b.depth);
    const edges = $("mesh-edges").checked;
    for (const face of faces) {
      ctx.beginPath();
      ctx.moveTo(face.points[0][0], face.points[0][1]);
      ctx.lineTo(face.points[1][0], face.points[1][1]);
      ctx.lineTo(face.points[2][0], face.points[2][1]);
      ctx.closePath();
      ctx.fillStyle = face.color;
      ctx.fill();
      ctx.strokeStyle = edges ? "#213e5270" : face.color;
      ctx.lineWidth = edges ? 0.5 : 0.45;
      ctx.stroke();
    }
  } else {
    ctx.setLineDash([4, 5]);
    line([0, 0, 0], [spec.offset_mm, 0, spec.standoff_mm], "#9ab1c45c", 1);
    ctx.setLineDash([]);
  }
  function boundary(x, z, radius) {
    ctx.beginPath();
    for (let i = 0; i <= 96; i += 1) {
      const angle = i * Math.PI * 2 / 96;
      const p = project([x + Math.cos(angle) * radius, Math.sin(angle) * radius, z]);
      if (i === 0) ctx.moveTo(p[0], p[1]);
      else ctx.lineTo(p[0], p[1]);
    }
    if (!mesh) {
      ctx.fillStyle = "#d9976120";
      ctx.fill();
    }
    ctx.strokeStyle = colors.copper;
    ctx.lineWidth = mesh ? 1.8 : 1.5;
    ctx.stroke();
  }
  boundary(0, 0, lowerRadius);
  boundary(spec.offset_mm, spec.standoff_mm, upperRadius);
  if (camera.zoom < 1.5) {
    const anchorX = width > 500 ? width * 0.77 : width * 0.76;
    for (const entry of [{ point: [spec.offset_mm + upperRadius, 0, spec.standoff_mm], label: "UPPER PAD", detail: `Ø ${number(spec.upper_diameter_mm, 4)} mm` }, { point: [lowerRadius, 0, 0], label: "BOARD PAD", detail: `Ø ${number(spec.lower_diameter_mm, 4)} mm` }]) {
      const p = project(entry.point);
      const labelY = p[1] + (entry.label === "UPPER PAD" ? -27 : 22);
      ctx.beginPath();
      ctx.moveTo(p[0] + 5, p[1]);
      ctx.lineTo(anchorX - 10, labelY);
      ctx.lineTo(anchorX, labelY);
      ctx.strokeStyle = "#7b96ad65";
      ctx.lineWidth = 0.8;
      ctx.stroke();
      ctx.textAlign = "left";
      ctx.font = "8px ui-monospace, monospace";
      ctx.fillStyle = "#8ea7bb";
      ctx.fillText(entry.label, anchorX + 4, labelY - 4);
      ctx.fillStyle = "#c7d5df";
      ctx.font = "9px ui-monospace, monospace";
      ctx.fillText(entry.detail, anchorX + 4, labelY + 10);
    }
  }
  const axisOrigin = [38, height - 43];
  const axisLength = 24;
  for (const axis of [{ vector: [1, 0, 0], label: "X", color: colors.copper }, { vector: [0, 1, 0], label: "Y", color: "#6e8dad" }, { vector: [0, 0, 1], label: "Z", color: colors.teal }]) {
    const [x, y, z] = axis.vector;
    const px = (cy * x - sy * y) * axisLength;
    const py = (se * (sy * x + cy * y) - ce * z) * axisLength;
    ctx.beginPath();
    ctx.moveTo(...axisOrigin);
    ctx.lineTo(axisOrigin[0] + px, axisOrigin[1] + py);
    ctx.strokeStyle = axis.color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = axis.color;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.font = "9px ui-monospace, monospace";
    ctx.fillText(axis.label, axisOrigin[0] + px * 1.27, axisOrigin[1] + py * 1.27);
  }
  const target = 65 / scale;
  const power = 10 ** Math.floor(Math.log10(target));
  const barMm = [1, 2, 5, 10].map((value) => value * power).find((value) => value >= target) || power;
  const barWidth = barMm * scale;
  const barX = width - barWidth - 24;
  const barY = height - 47;
  ctx.beginPath();
  ctx.moveTo(barX, barY - 3);
  ctx.lineTo(barX, barY + 3);
  ctx.moveTo(barX, barY);
  ctx.lineTo(barX + barWidth, barY);
  ctx.moveTo(barX + barWidth, barY - 3);
  ctx.lineTo(barX + barWidth, barY + 3);
  ctx.strokeStyle = "#718ba1";
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = "#8fa6ba";
  ctx.font = "8px ui-monospace, monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "bottom";
  ctx.fillText(`${number(barMm, 5)} mm`, barX + barWidth / 2, barY - 6);
}

function drawChart() {
  if (state.response?.comparison) { chartHitAreas = []; return; }
  const { context: ctx, width, height } = canvasContext($("force-chart"));
  const results = state.response?.results || [];
  const points = results.map((result, index) => ({ result, index })).filter(({ result }) => Number.isFinite(result.input?.offset_mm));
  const goodPoints = points.filter(({ result }) => Number.isFinite(result.forces?.x_uN) && Number.isFinite(result.forces?.z_uN));
  chartHitAreas = [];
  $("empty-chart").hidden = goodPoints.length > 0;
  const left = 61, right = width - 24, top = 30, bottom = height - 40;
  if (right <= left) return;
  let xmin = Math.min(...points.map(({ result }) => result.input.offset_mm));
  let xmax = Math.max(...points.map(({ result }) => result.input.offset_mm));
  if (!Number.isFinite(xmin)) { xmin = -0.02; xmax = 0.02; }
  if (xmin === xmax) { const delta = Math.max(Math.abs(xmin) * 0.3, 0.01); xmin -= delta; xmax += delta; }
  let ymin = Math.min(0, ...goodPoints.flatMap(({ result }) => [result.forces.x_uN, result.forces.z_uN]));
  let ymax = Math.max(0, ...goodPoints.flatMap(({ result }) => [result.forces.x_uN, result.forces.z_uN]));
  const range = Math.max(ymax - ymin, 1);
  ymin -= range * 0.12;
  ymax += range * 0.12;
  const xScale = (value) => left + (value - xmin) / (xmax - xmin) * (right - left);
  const yScale = (value) => bottom - (value - ymin) / (ymax - ymin) * (bottom - top);
  ctx.font = "8px ui-monospace, monospace";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= 4; i += 1) {
    const y = top + (bottom - top) * i / 4;
    ctx.strokeStyle = "#2b405255";
    ctx.lineWidth = 0.7;
    ctx.beginPath();
    ctx.moveTo(left, y);
    ctx.lineTo(right, y);
    ctx.stroke();
    ctx.fillStyle = "#7790a6";
    ctx.textAlign = "right";
    ctx.fillText(goodPoints.length ? number(ymax - (ymax - ymin) * i / 4, 1) : "", left - 10, y);
    const x = left + (right - left) * i / 4;
    ctx.textAlign = "center";
    ctx.fillText(number(xmin + (xmax - xmin) * i / 4, 4), x, bottom + 15);
  }
  ctx.fillStyle = "#8da3b7";
  ctx.textAlign = "left";
  ctx.fillText("µN", left - 28, top - 14);
  ctx.textAlign = "right";
  ctx.fillText("OFFSET · mm", right, height - 8);
  if (!goodPoints.length) return;
  ctx.strokeStyle = "#7a91a680";
  ctx.setLineDash([3, 4]);
  ctx.beginPath();
  ctx.moveTo(left, yScale(0));
  ctx.lineTo(right, yScale(0));
  ctx.stroke();
  ctx.setLineDash([]);
  const ordered = [...points].sort((a, b) => a.result.input.offset_mm - b.result.input.offset_mm);
  for (const series of [{ key: "x_uN", color: colors.copper }, { key: "z_uN", color: colors.teal }]) {
    ctx.beginPath();
    let connected = false;
    for (const { result } of ordered) {
      const value = result.forces?.[series.key];
      if (!Number.isFinite(value)) { connected = false; continue; }
      const x = xScale(result.input.offset_mm), y = yScale(value);
      if (connected) ctx.lineTo(x, y);
      else ctx.moveTo(x, y);
      connected = true;
    }
    ctx.strokeStyle = series.color;
    ctx.lineWidth = 1.7;
    ctx.stroke();
    for (const { result, index } of goodPoints) {
      const x = xScale(result.input.offset_mm), y = yScale(result.forces[series.key]);
      ctx.beginPath();
      ctx.arc(x, y, index === state.resultIndex ? 4.4 : 3.1, 0, Math.PI * 2);
      ctx.fillStyle = series.color;
      ctx.fill();
      ctx.strokeStyle = "#17222f";
      ctx.lineWidth = 1.7;
      ctx.stroke();
      if (index === state.resultIndex) {
        ctx.beginPath();
        ctx.arc(x, y, 7, 0, Math.PI * 2);
        ctx.strokeStyle = `${series.color}88`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
      chartHitAreas.push({ x, y, index });
    }
  }
}

function resetView() {
  camera.yaw = -0.57;
  camera.elevation = 0.39;
  camera.zoom = 1;
  scheduleDraw();
}

$("footprint-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const revision = beginImport();
  try {
    if (file.size > 2000000) throw new Error("Footprints are limited to 2 MB.");
    const text = await file.text();
    if (revision !== state.revision) { state.importing = false; updateControls(); return; }
    await importText(text, revision);
  } catch (error) {
    state.importing = false;
    if (revision === state.revision) notice(error.message, "error");
    renderFootprint();
    updateControls();
  }
  event.target.value = "";
});

$("example-button").addEventListener("click", async () => {
  const revision = beginImport();
  try {
    const data = await bootstrap();
    if (revision === state.revision) await importText(data.example.text, revision);
    else { state.importing = false; updateControls(); }
  } catch (error) {
    state.importing = false;
    if (revision === state.revision) notice(error.message, "error");
    renderFootprint();
    updateControls();
  }
});

function choosePad(index) {
  if (index === state.padIndex) return;
  invalidate();
  state.padIndex = index;
  state.baseline = null;
  $("pad-select").value = String(index);
  renderFootprint();
  updateControls();
}

$("pad-select").addEventListener("change", (event) => choosePad(Number(event.target.value)));
$("footprint-canvas").addEventListener("click", (event) => {
  if (state.importing || state.caseAction) return;
  const rect = event.currentTarget.getBoundingClientRect();
  const x = event.clientX - rect.left, y = event.clientY - rect.top;
  const match = footprintHitAreas.filter((area) => Math.hypot(area.x - x, area.y - y) <= area.radius).sort((a, b) => Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y))[0];
  if (match) choosePad(match.index);
});

for (const name of [...parameterNames, "standoff_mm", "normal_load_uN", "gravity"]) {
  $(name).addEventListener("input", invalidate);
}
$("load_mode").addEventListener("change", () => {
  updateLoadMode();
  invalidate();
});
form.addEventListener("submit", (event) => { event.preventDefault(); compute("solve"); });
$("sweep-button").addEventListener("click", () => compute("sweep"));
$("compare-button").addEventListener("click", () => compute("compare"));
$("reference-button").addEventListener("click", () => {
  if (!pad()?.supported || !form.reportValidity()) return;
  const parameters = readParameters();
  state.baseline = freeze({ upper_diameter_mm: parameters.upper_diameter_mm, volume_mm3: parameters.volume_mm3 });
  invalidate();
  notice("Reference dimensions saved. Change the upper pad diameter or solder volume, then compare. Both designs will use the current shared conditions.");
});
$("clear-reference-button").addEventListener("click", () => {
  state.baseline = null;
  invalidate();
});

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}

$("save-case-button").addEventListener("click", async () => {
  if (state.caseAction || !pad()?.supported || !form.reportValidity()) return;
  const revision = state.revision;
  const draft = editableCase();
  state.caseAction = "save";
  updateControls();
  try {
    const data = await api("/api/case", draft);
    if (revision !== state.revision) {
      notice("Inputs changed before the case was saved. Save again with the current inputs.");
      return;
    }
    downloadBlob(new Blob([`${JSON.stringify(data.case, null, 2)}\n`], { type: "application/json" }), "soldershape-editable-case.json");
    notice("Editable case saved. It contains the footprint, selected pad, parameters, and reference dimensions. Open it to resume and recompute.");
  } catch (error) {
    if (revision === state.revision) notice(`The case could not be saved. ${error.message}`, "error");
  } finally {
    state.caseAction = null;
    updateControls();
  }
});

$("case-file").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file || state.caseAction) return;
  const revision = state.revision;
  state.caseAction = "open";
  updateControls();
  notice("Checking the editable case before opening it…", "working");
  try {
    if (file.size > 2100000) throw new Error("Editable cases are limited to 2.1 MB.");
    let draft;
    try { draft = JSON.parse(await file.text()); }
    catch { throw new Error("Choose a SolderShape editable case JSON file."); }
    const data = await api("/api/case", draft);
    if (revision !== state.revision) {
      notice("The current inputs changed while the file was checked. The case was not opened.");
      return;
    }
    invalidate();
    state.footprintText = data.case.footprint_text;
    state.footprint = data.footprint;
    state.padIndex = data.case.pad_index;
    state.baseline = data.case.baseline ? freeze({ ...data.case.baseline }) : null;
    for (const name of parameterNames) $(name).value = String(data.case.parameters[name]);
    const verticalCondition = Number.isFinite(data.case.parameters.normal_load_uN) ? "normal_load_uN" : "standoff_mm";
    $("load_mode").value = verticalCondition === "normal_load_uN" ? "load" : "gap";
    $(verticalCondition).value = String(data.case.parameters[verticalCondition]);
    updateLoadMode();
    $("gravity").checked = data.case.parameters.gravity;
    populatePads();
    renderFootprint();
    renderResults();
    resetView();
    notice("Editable case opened. These are saved inputs. Solve or compare to compute fresh forces and exports.");
  } catch (error) {
    if (revision === state.revision) notice(`Case not opened. Your current inputs and results are unchanged. ${error.message}`, "error");
  } finally {
    event.target.value = "";
    state.caseAction = null;
    updateControls();
  }
});
$("mesh-edges").addEventListener("change", scheduleDraw);
$("reset-view").addEventListener("click", resetView);

const modelCanvas = $("model-canvas");
modelCanvas.addEventListener("pointerdown", (event) => {
  if (event.button !== 0) return;
  camera.drag = { x: event.clientX, y: event.clientY, yaw: camera.yaw, elevation: camera.elevation };
  modelCanvas.setPointerCapture(event.pointerId);
  modelCanvas.classList.add("dragging");
});
modelCanvas.addEventListener("pointermove", (event) => {
  if (!camera.drag) return;
  camera.yaw = camera.drag.yaw + (event.clientX - camera.drag.x) * 0.008;
  camera.elevation = Math.max(0.06, Math.min(1.48, camera.drag.elevation + (event.clientY - camera.drag.y) * 0.006));
  scheduleDraw();
});
function endDrag() { camera.drag = null; modelCanvas.classList.remove("dragging"); }
modelCanvas.addEventListener("pointerup", endDrag);
modelCanvas.addEventListener("pointercancel", endDrag);
modelCanvas.addEventListener("lostpointercapture", endDrag);
modelCanvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  camera.zoom = Math.max(0.45, Math.min(3.5, camera.zoom * Math.exp(-event.deltaY * 0.001)));
  scheduleDraw();
}, { passive: false });
modelCanvas.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") camera.yaw -= 0.1;
  else if (event.key === "ArrowRight") camera.yaw += 0.1;
  else if (event.key === "ArrowUp") camera.elevation = Math.min(1.48, camera.elevation + 0.1);
  else if (event.key === "ArrowDown") camera.elevation = Math.max(0.06, camera.elevation - 0.1);
  else if (event.key === "+" || event.key === "=") camera.zoom = Math.min(3.5, camera.zoom * 1.15);
  else if (event.key === "-") camera.zoom = Math.max(0.45, camera.zoom / 1.15);
  else if (event.key === "Home") resetView();
  else return;
  event.preventDefault();
  scheduleDraw();
});

$("force-chart").addEventListener("click", (event) => {
  const rect = event.currentTarget.getBoundingClientRect();
  const x = event.clientX - rect.left, y = event.clientY - rect.top;
  const match = chartHitAreas.filter((area) => Math.hypot(area.x - x, area.y - y) < 14).sort((a, b) => Math.hypot(a.x - x, a.y - y) - Math.hypot(b.x - x, b.y - y))[0];
  if (match) selectResult(match.index);
});

$("download-button").addEventListener("click", () => {
  const response = state.response;
  if (!response?.bundle_base64 || state.pending) return;
  try {
    const binary = atob(response.bundle_base64);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    downloadBlob(new Blob([bytes], { type: "application/zip" }), response.bundle_filename || "soldershape-case.zip");
  } catch (error) {
    notice(`The case could not be downloaded. ${error.message}`, "error");
  }
});

const resizeObserver = new ResizeObserver(scheduleDraw);
for (const id of ["footprint-canvas", "model-canvas", "force-chart"]) resizeObserver.observe($(id));
updateLoadMode();
renderResults();
bootstrap().then((data) => {
  if (state.revision === 0 && data.example?.text) {
    const revision = beginImport();
    return importText(data.example.text, revision);
  }
}).catch((error) => {
  $("engine-state").className = "engine-state unavailable";
  $("engine-label").textContent = "Local service unavailable";
  notice(error.message, "error");
});
