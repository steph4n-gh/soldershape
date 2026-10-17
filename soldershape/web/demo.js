"use strict";

const $ = (id) => document.getElementById(id);
const state = { experiment: null, sampleId: "offset-120" };
const initialCamera = { yaw: -0.58, elevation: 0.4, zoom: 1 };
const camera = { ...initialCamera, drag: null };
const canvases = [$("reference-canvas"), $("candidate-canvas")];
let framePending = false;

function number(value, digits = 3) {
  return Number.isFinite(value) ? value.toFixed(digits).replace(/\.?0+$/, "") : "Unavailable";
}

function signed(value) {
  return Number.isFinite(value) ? `${value > 0 ? "+" : ""}${number(value)}` : "Unavailable";
}

function selectedSample() {
  return state.experiment.samples.find((sample) => sample.id === state.sampleId);
}

function resultGeometry(record) {
  return record.equilibrium || record.input;
}

function resultPresentation(record) {
  if (record.status === "failed") return { label: "Native solver failed", className: "failed" };
  if (record.model_warnings.length) return { label: "Outside model scope", className: "warn" };
  if (record.status === "refinement_checked") return { label: "Refinement checked", className: "" };
  return { label: "Numerical checks failed", className: "warn" };
}

function setList(element, messages) {
  element.replaceChildren(...messages.map((message) => {
    const item = document.createElement("li");
    item.textContent = message;
    return item;
  }));
}

function renderRecord(role, record, control) {
  const spec = resultGeometry(record);
  const status = resultPresentation(record);
  $(`${role}-role`).textContent = control ? role === "reference" ? "GAP CONTROL / REFERENCE" : "GAP CONTROL / COMPRESSED" : role.toUpperCase();
  $(`${role}-heading`).textContent = control ? `${number(spec.standoff_mm * 1000, 1)} µm held gap` : `${number(spec.volume_mm3 * 1000, 1)} nL solder`;
  $(`${role}-status`).textContent = status.label;
  $(`${role}-status`).className = `numerical-status ${status.className}`;
  for (const axis of ["x", "z"]) {
    const element = $(`${role}-force-${axis}`);
    element.textContent = signed(record.forces?.[`${axis}_uN`]);
    element.classList.toggle("unavailable", !record.forces);
  }
  $(`${role}-conditions`).textContent = control
    ? `${number(spec.volume_mm3 * 1000, 1)} nL · +${number(spec.offset_mm * 1000, 1)} µm offset`
    : `${number(spec.standoff_mm * 1000, 1)} µm held gap · +${number(spec.offset_mm * 1000, 1)} µm offset`;
  $(`${role}-geometry`).textContent = `${number(spec.standoff_mm * 1000, 1)} µm HELD GAP · +${number(spec.offset_mm * 1000, 1)} µm OFFSET · ${record.mesh ? "RECORDED MESH" : "FAILED REQUEST"}`;
  $(`${role}-mesh`).textContent = record.mesh ? `${record.mesh.triangles.length.toLocaleString()} triangles` : "No mesh exported";
  $(`${role}-empty`).hidden = !!record.mesh;
  $(`${role}-empty`).querySelector("p").textContent = record.error || "";
  const messages = record.status === "failed" ? [record.error] : [...record.diagnostics.warnings, ...record.model_warnings];
  setList($(`${role}-warnings`), messages);
  $(`${role}-warnings`).hidden = !messages.length;
}

function renderSelected() {
  const sample = selectedSample();
  const referenceGap = number(resultGeometry(sample.reference).standoff_mm * 1000, 1);
  const candidateGap = number(resultGeometry(sample.candidate).standoff_mm * 1000, 1);
  const gapCondition = sample.kind === "compression_control"
    ? `Gap control at ${referenceGap} versus ${candidateGap} µm, with the same solder volume.`
    : `Gap held at ${referenceGap} µm.`;
  $("demo-title").textContent = `One isolated joint. ${gapCondition} Seek lateral restoration without upward separation.`;
  for (const button of document.querySelectorAll(".sample-buttons button")) {
    button.setAttribute("aria-pressed", String(button.dataset.sample === sample.id));
  }
  renderRecord("reference", sample.reference, sample.kind === "compression_control");
  renderRecord("candidate", sample.candidate, sample.kind === "compression_control");
  const screens = {
    conditional_comparison: { label: "CONDITIONAL FORCE COMPARISON", className: "", mark: "↔" },
    outside_model_scope: { label: "COMPARISON BLOCKED BY MODEL SCOPE", className: "warn", mark: "!" },
    numerical_failure: { label: "COMPARISON BLOCKED BY NUMERICAL FAILURE", className: "failed", mark: "!" },
  };
  const screen = screens[sample.screen.status];
  $("screen-panel").className = `screen-panel ${screen.className}`;
  $("screen-status").textContent = screen.label;
  $("screen-mark").textContent = screen.mark;
  $("screen-headline").textContent = sample.screen.headline;
  setList($("screen-details"), sample.screen.details);
  for (const row of $("native-cases").rows) {
    row.classList.toggle("selected", [sample.reference.input_sha256, sample.candidate.input_sha256].includes(row.dataset.input));
  }
  $("editable-case").textContent = sample.kind === "compression_control" ? "Save compressed editable case" : "Save selected editable comparison";
  scheduleDraw();
}

function renderCases() {
  const cases = new Map();
  for (const sample of state.experiment.samples) {
    for (const record of [sample.reference, sample.candidate]) cases.set(record.input_sha256, record);
  }
  for (const record of cases.values()) {
    const spec = resultGeometry(record);
    const row = document.createElement("tr");
    row.dataset.input = record.input_sha256;
    const status = resultPresentation(record);
    const label = record.status === "failed" ? "Compressed control" : `${number(spec.volume_mm3 * 1000, 1)} nL at ${number(spec.offset_mm * 1000, 1)} µm`;
    const values = [label, number(spec.volume_mm3 * 1000, 1), `+${number(spec.offset_mm * 1000, 1)}`, number(spec.standoff_mm * 1000, 1), signed(record.forces?.x_uN), signed(record.forces?.z_uN), status.label];
    for (const [index, value] of values.entries()) {
      const cell = document.createElement("td");
      cell.textContent = value;
      if (index === values.length - 1) cell.className = `status-cell ${status.className}`;
      row.append(cell);
    }
    row.title = `Input SHA-256 ${record.input_sha256}`;
    $("native-cases").append(row);
  }
}

function renderExperiment() {
  const experiment = state.experiment;
  document.title = `${experiment.title} | SolderShape`;
  $("demo-question").textContent = experiment.question;
  for (const sample of experiment.samples) {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.sample = sample.id;
    button.textContent = sample.label;
    button.setAttribute("aria-pressed", "false");
    button.addEventListener("click", () => {
      state.sampleId = sample.id;
      renderSelected();
    });
    $(sample.kind === "volume_comparison" ? "offset-buttons" : "control-buttons").append(button);
  }
  const pad = experiment.footprint.pads.find((item) => item.index === experiment.selected_pad_index);
  $("pitch-label").textContent = `${number(experiment.pitch_mm * 1000, 1)} µm pitch`;
  $("footprint-note").textContent = `${experiment.footprint.name}. Pad ${pad.identifier} has ${number(pad.size_mm[0] * 1000, 1)} µm diameter. Only the highlighted joint is modeled. Neighbor pads are geometric context. Their joints and interactions are not computed.`;
  $("footprint-digest").textContent = `Footprint SHA-256 ${experiment.footprint.sha256}`;
  $("baseline-note").textContent = experiment.baseline;
  setList($("assumptions"), experiment.assumptions);
  $("evidence-download").href = experiment.archive.url;
  $("archive-digest").textContent = `${experiment.archive.case_count} recorded cases · Native archive SHA-256 ${experiment.archive.sha256}`;
  renderCases();
  $("experiment").hidden = false;
  $("load-notice").hidden = true;
  renderSelected();
}

function canvasContext(canvas) {
  const bounds = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  const pixelWidth = Math.round(bounds.width * ratio);
  const pixelHeight = Math.round(bounds.height * ratio);
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }
  const context = canvas.getContext("2d");
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  context.clearRect(0, 0, bounds.width, bounds.height);
  return { context, width: bounds.width, height: bounds.height };
}

function pairView(sample) {
  const records = [sample.reference, sample.candidate];
  const specs = records.map(resultGeometry);
  const center = [specs[0].offset_mm / 2, 0, Math.max(...specs.map((spec) => spec.standoff_mm)) / 2];
  let extent = Math.max(...specs.map((spec) => Math.max(spec.standoff_mm, spec.lower_diameter_mm, spec.upper_diameter_mm, Math.abs(spec.offset_mm) + (spec.lower_diameter_mm + spec.upper_diameter_mm) / 2)));
  for (const record of records) {
    if (!record.mesh) continue;
    for (const point of record.mesh.vertices_mm) {
      extent = Math.max(extent, ...point.map((coordinate, index) => Math.abs(coordinate - center[index]) * 2));
    }
  }
  const sizes = canvases.map((canvas) => canvas.getBoundingClientRect());
  const scale = Math.min(...sizes.map((size) => Math.min(size.width * .69, size.height * .7))) / extent * camera.zoom;
  return { center, extent, scale };
}

function drawModel(canvas, record, view) {
  const { context: ctx, width, height } = canvasContext(canvas);
  if (!record.mesh || !width || !height) return;
  const spec = resultGeometry(record);
  const cy = Math.cos(camera.yaw), sy = Math.sin(camera.yaw);
  const ce = Math.cos(camera.elevation), se = Math.sin(camera.elevation);
  function project(point) {
    const x = point[0] - view.center[0], y = point[1] - view.center[1], z = point[2] - view.center[2];
    return [width / 2 + (cy * x - sy * y) * view.scale, height * .53 + (se * (sy * x + cy * y) - ce * z) * view.scale, ce * (sy * x + cy * y) + se * z];
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
  const ground = -view.extent * .09;
  for (let index = -4; index <= 4; index += 1) {
    const position = index * view.extent / 4;
    line([-view.extent + view.center[0], position, ground], [view.extent + view.center[0], position, ground], "#4a75922a", .7);
    line([position + view.center[0], -view.extent, ground], [position + view.center[0], view.extent, ground], "#4a75922a", .7);
  }
  window.SolderMesh.drawSurface(ctx, record.mesh, project, spec.standoff_mm, $("mesh-edges").checked);
  for (const boundary of [{ x: 0, z: 0, radius: spec.lower_diameter_mm / 2, color: "#edb382" }, { x: spec.offset_mm, z: spec.standoff_mm, radius: spec.upper_diameter_mm / 2, color: "#7ccfd0" }]) {
    ctx.beginPath();
    for (let index = 0; index <= 96; index += 1) {
      const angle = index * Math.PI * 2 / 96;
      const point = project([boundary.x + Math.cos(angle) * boundary.radius, Math.sin(angle) * boundary.radius, boundary.z]);
      if (index === 0) ctx.moveTo(point[0], point[1]);
      else ctx.lineTo(point[0], point[1]);
    }
    ctx.strokeStyle = boundary.color;
    ctx.lineWidth = 1.6;
    ctx.stroke();
  }
  const origin = [spec.offset_mm, 0, spec.standoff_mm];
  for (const arrow of [{ axis: "X", vector: [Math.sign(record.forces.x_uN), 0, 0], color: "#edb382" }, { axis: "Z", vector: [0, 0, Math.sign(record.forces.z_uN)], color: "#7ccfd0" }]) {
    const start = project(origin);
    const end = project(origin.map((value, index) => value + arrow.vector[index] * view.extent * .22));
    const angle = Math.atan2(end[1] - start[1], end[0] - start[0]);
    line(origin, origin.map((value, index) => value + arrow.vector[index] * view.extent * .22), arrow.color, 1.7);
    ctx.beginPath();
    ctx.moveTo(end[0], end[1]);
    ctx.lineTo(end[0] - 6 * Math.cos(angle - .45), end[1] - 6 * Math.sin(angle - .45));
    ctx.moveTo(end[0], end[1]);
    ctx.lineTo(end[0] - 6 * Math.cos(angle + .45), end[1] - 6 * Math.sin(angle + .45));
    ctx.strokeStyle = arrow.color;
    ctx.stroke();
    ctx.fillStyle = arrow.color;
    ctx.font = "9px ui-monospace, monospace";
    ctx.textAlign = "center";
    ctx.fillText(arrow.axis, end[0] + Math.cos(angle) * 11, end[1] + Math.sin(angle) * 11 + 3);
  }
  const barMm = .1;
  const barX = 20, barY = height - 35, barWidth = barMm * view.scale;
  ctx.beginPath();
  ctx.moveTo(barX, barY - 3);
  ctx.lineTo(barX, barY + 3);
  ctx.moveTo(barX, barY);
  ctx.lineTo(barX + barWidth, barY);
  ctx.moveTo(barX + barWidth, barY - 3);
  ctx.lineTo(barX + barWidth, barY + 3);
  ctx.strokeStyle = "#88a7bd";
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = "#8ca9bd";
  ctx.font = "8px ui-monospace, monospace";
  ctx.textAlign = "left";
  ctx.fillText("100 µm", barX, barY - 8);
  ctx.fillStyle = "#7893a9";
  ctx.font = "7px ui-monospace, monospace";
  ctx.fillText("FORCE ARROWS SHOW DIRECTION ONLY", 20, height - 13);
}

function drawFootprint(sample) {
  const { context: ctx, width, height } = canvasContext($("footprint-canvas"));
  const experiment = state.experiment;
  const pads = experiment.footprint.pads;
  const selected = pads.find((pad) => pad.index === experiment.selected_pad_index);
  const spec = resultGeometry(sample.reference);
  const xMin = Math.min(...pads.map((pad) => pad.x_mm - pad.size_mm[0] / 2));
  const xMax = Math.max(...pads.map((pad) => pad.x_mm + pad.size_mm[0] / 2), selected.x_mm + spec.offset_mm + spec.upper_diameter_mm / 2);
  const yMin = Math.min(...pads.map((pad) => pad.y_mm - pad.size_mm[1] / 2));
  const yMax = Math.max(...pads.map((pad) => pad.y_mm + pad.size_mm[1] / 2));
  const scale = Math.min((width - 82) / (xMax - xMin), (height - 61) / (yMax - yMin));
  const project = (x, y) => [width / 2 + (x - (xMin + xMax) / 2) * scale, (height - 20) / 2 + (y - (yMin + yMax) / 2) * scale];
  ctx.fillStyle = "#294457";
  for (let x = 12; x < width; x += 18) {
    for (let y = 12; y < height; y += 18) ctx.fillRect(x, y, 1, 1);
  }
  for (const pad of pads) {
    const point = project(pad.x_mm, pad.y_mm);
    ctx.save();
    ctx.translate(...point);
    ctx.rotate(-pad.angle_deg * Math.PI / 180);
    ctx.beginPath();
    if (pad.shape === "circle" || pad.shape === "oval") ctx.ellipse(0, 0, pad.size_mm[0] * scale / 2, pad.size_mm[1] * scale / 2, 0, 0, Math.PI * 2);
    else ctx.rect(-pad.size_mm[0] * scale / 2, -pad.size_mm[1] * scale / 2, pad.size_mm[0] * scale, pad.size_mm[1] * scale);
    ctx.fillStyle = pad.index === selected.index ? "#edb382" : "#775c48";
    ctx.fill();
    ctx.strokeStyle = pad.index === selected.index ? "#ffe0c4" : "#ad8664";
    ctx.lineWidth = pad.index === selected.index ? 1.5 : .8;
    ctx.stroke();
    ctx.restore();
  }
  const board = project(selected.x_mm, selected.y_mm);
  const upper = project(selected.x_mm + spec.offset_mm, selected.y_mm);
  ctx.beginPath();
  ctx.arc(upper[0], upper[1], spec.upper_diameter_mm / 2 * scale, 0, Math.PI * 2);
  ctx.strokeStyle = "#7ccfd0";
  ctx.lineWidth = 1.8;
  ctx.stroke();
  const labelY = Math.max(24, board[1] - selected.size_mm[1] / 2 * scale - 17);
  ctx.beginPath();
  ctx.moveTo(board[0], labelY + 3);
  ctx.lineTo(board[0], labelY + 8);
  ctx.moveTo(board[0], labelY + 5);
  ctx.lineTo(upper[0], labelY + 5);
  ctx.moveTo(upper[0], labelY + 3);
  ctx.lineTo(upper[0], labelY + 8);
  ctx.strokeStyle = "#9ac7cf";
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.fillStyle = "#a7d7db";
  ctx.font = "9px ui-monospace, monospace";
  ctx.textAlign = "center";
  ctx.fillText(`+${number(spec.offset_mm * 1000, 1)} µm`, (board[0] + upper[0]) / 2, labelY - 3);
}

function scheduleDraw() {
  if (framePending || !state.experiment) return;
  framePending = true;
  requestAnimationFrame(() => {
    framePending = false;
    const sample = selectedSample();
    const view = pairView(sample);
    drawModel(canvases[0], sample.reference, view);
    drawModel(canvases[1], sample.candidate, view);
    drawFootprint(sample);
  });
}

for (const canvas of canvases) {
  canvas.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    camera.drag = { x: event.clientX, y: event.clientY, pointerId: event.pointerId };
    canvas.setPointerCapture(event.pointerId);
    canvas.classList.add("dragging");
  });
  canvas.addEventListener("pointermove", (event) => {
    if (!camera.drag || event.pointerId !== camera.drag.pointerId) return;
    camera.yaw += (event.clientX - camera.drag.x) * .008;
    camera.elevation = Math.max(-1.2, Math.min(1.2, camera.elevation + (event.clientY - camera.drag.y) * .006));
    camera.drag.x = event.clientX;
    camera.drag.y = event.clientY;
    scheduleDraw();
  });
  const endDrag = () => {
    camera.drag = null;
    canvas.classList.remove("dragging");
  };
  canvas.addEventListener("pointerup", endDrag);
  canvas.addEventListener("pointercancel", endDrag);
  canvas.addEventListener("lostpointercapture", endDrag);
  canvas.addEventListener("wheel", (event) => {
    event.preventDefault();
    camera.zoom = Math.max(.55, Math.min(2.7, camera.zoom * Math.exp(-event.deltaY * .001)));
    scheduleDraw();
  }, { passive: false });
  canvas.addEventListener("keydown", (event) => {
    if (!["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "+", "=", "-", "Home"].includes(event.key)) return;
    event.preventDefault();
    if (event.key === "Home") Object.assign(camera, initialCamera);
    if (event.key === "ArrowLeft") camera.yaw -= .1;
    if (event.key === "ArrowRight") camera.yaw += .1;
    if (event.key === "ArrowUp") camera.elevation = Math.min(1.2, camera.elevation + .1);
    if (event.key === "ArrowDown") camera.elevation = Math.max(-1.2, camera.elevation - .1);
    if (event.key === "+" || event.key === "=") camera.zoom = Math.min(2.7, camera.zoom * 1.1);
    if (event.key === "-") camera.zoom = Math.max(.55, camera.zoom / 1.1);
    scheduleDraw();
  });
}

$("reset-view").addEventListener("click", () => {
  Object.assign(camera, initialCamera);
  scheduleDraw();
});
$("mesh-edges").addEventListener("change", scheduleDraw);
$("editable-case").addEventListener("click", () => {
  const sample = selectedSample();
  const blob = new Blob([`${JSON.stringify(sample.editable_case, null, 2)}\n`], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `soldershape-extreme-${sample.id}.json`;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
window.addEventListener("resize", scheduleDraw);

async function loadExperiment() {
  try {
    const response = await fetch("/api/demo", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error);
    state.experiment = data;
    renderExperiment();
  } catch (error) {
    $("experiment").hidden = true;
    $("load-notice").hidden = false;
    $("load-notice").className = "load-notice error";
    $("load-notice").textContent = `The recorded experiment is unavailable. ${error.message}`;
  }
}

loadExperiment();
