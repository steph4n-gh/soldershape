# Candidate B. One browser presenter and a portable result page

## Problem

An engineer currently receives signed forces and canonical units, then has to explain them to someone else. This candidate keeps all calculation and archive code intact. One browser module turns the immutable returned result into both the visible explanation and a standalone HTML file. The existing ZIP remains the numerical evidence. This is a presentation improvement, not additional physical validation.

## Usage from the caller

Joint details gives the presenter only the response it has accepted for the current revision. It never gives it live controls or a copied Board origin note as authoritative source binding.

```js
const presentation = SolderShapeResult.joint(acceptedResponse);
presentation.render(document.getElementById('result-takeaway'), selectedIndex);
const file = await presentation.brief(selectedIndex);
SolderShapeUI.downloadFile(file, 'soldershape-result.html');
```

Board gives it the existing checked report. The report already carries the true selected source, declared held-gap objective and recorded marker.

```js
const presentation = SolderShapeResult.board(acceptedResponse);
presentation.render(document.getElementById('result-takeaway'), 1);
const file = await presentation.brief(1);
SolderShapeUI.downloadFile(file, 'soldershape-board-result.html');
```

The browser keeps the same presentation instance beside the accepted response. Clearing the response clears the instance and disables its export. Selecting a sweep row renders that row from the same snapshot. A selected row is visually emphasized in the brief, but every returned case remains present.

A colleague opens the HTML without SolderShape running. The page contains assumptions, engineering-unit inputs, force directions, statuses, exact input hashes and replay commands. A download link inside the HTML extracts the original, unmodified evidence ZIP embedded as a data URL. No script, external font, CDN or server is needed to read the page or obtain that evidence.

## Shape

The public API has two constructors because the two existing response envelopes contain materially different source provenance. Both return one narrow presentation object. A single private adapter owns each wire representation. The ordinary Joint presentation never fabricates board-source binding.

```js
SolderShapeResult.joint(response) -> Presentation
SolderShapeResult.board(response) -> Presentation

Presentation.render(element, selectedIndex) -> void
Presentation.brief(selectedIndex) -> Promise<Blob>
```

The constructors validate at the network boundary and copy the accepted result data. Internal functions operate on this domain shape.

```text
Snapshot {
  kind: 'joint' | 'board',
  cases: Case[],
  comparison: null | { status, reason?, scope, delta?, designs },
  board: null | { selection, boardSha256, calculationSourceHashes, recorded },
  evidence: { originalZipBase64, originalZipName },
  qualification: 'unqualified'
}

Case {
  role: string,
  inputSha256: string,
  sourcePad: { footprintName, padNumber, padIndex },
  boundary:
    { kind: 'held-gap', gapMm: number } |
    { kind: 'supported-load', downwardLoadUN: number, solvedGapMm: number | null,
      residualUN: number | null, toleranceUN: number | null },
  input: { lowerDiameterMm, upperDiameterMm, volumeMm3, offsetMm,
    surfaceTensionNM, densityGCm3, gravity },
  numerical:
    { kind: 'checked', forces: { xUN, zUN }, warnings: string[] } |
    { kind: 'not-converged', diagnosticForces: { xUN, zUN } | null,
      warnings: string[] } |
    { kind: 'failed', error: string },
  engine: null | { version, sourceSha256, binarySha256 }
}

Interpretation {
  headline: string,
  facts: string[],
  blockers: string[],
  inputRows: DisplayRow[],
  caseRows: DisplayRow[],
  qualification: string
}
```

`Snapshot` is private, not a new wire schema. `Interpretation` contains presentation facts rather than a second numerical result. The discriminated vertical condition prevents a held-gap fixture rule from appearing in supported-load prose. The numerical union prevents a failed row from acquiring a force through a zero fallback. Model the Domain changes these data shapes rather than adding loosely related flags.

Private functions keep the call chain short.

```js
jointSnapshot(response) -> Snapshot
boardSnapshot(response) -> Snapshot
interpret(snapshot, selectedIndex) -> Interpretation
renderDocument(snapshot, interpretation, zipSha256) -> string
```

`interpret` is pure and is the sole owner of sentence selection and unit conversion. `render` creates DOM nodes with `textContent`. `renderDocument` uses a single HTML-escaping helper for all dynamic values. Its generated document has inline CSS and no executable script. `brief` decodes the already returned ZIP once, hashes its bytes with browser Web Crypto, calls the same interpreter and produces the document Blob. It does not inspect current form fields, alter ZIP bytes or run the solver.

Canonical millimeters and cubic millimeters remain exact in JSON and requests. The presenter multiplies lengths and volumes by 1000 for µm and nL display. It shows enough precision to distinguish the actual values, plus expandable canonical inputs. A blank raw draft never enters this module. The surrounding input recap must independently render blank as unavailable rather than coercing it to zero.

## Result rules

| Situation | Required interpretation |
| --- | --- |
| Checked held-gap pair | State the held gap. Describe each lateral direction and the candidate change. Describe upward/downward signs explicitly. Use the Board's existing `screen` only when presenting a genuine Board report. |
| Checked supported-load pair | State the supported downward load, solved gaps and candidate gap difference. Show load residual and tolerance. Positive upward solder force balances the load and is not a fixture failure. |
| Zero offset | State that this point cannot establish centering response. For a supported-load pair, the gap comparison remains available. Do not print a restoring-force delta as zero. |
| Negative offset | Force opposite the offset restores alignment. Force with the offset moves away. Compute the display meaning using `-sign(offset) * Fx`, matching the existing comparison convention. |
| Signed or crossing comparison | Distinguish stronger restoration from weaker destabilization. Crossing from restoring to outward force must say the direction changed. A larger magnitude alone is not an improvement. |
| No reference | Explain the selected case and its force directions. No winner, relative claim or fabricated delta. |
| Scope warnings | Preserve all warnings and block any preference. A numerically checked surface can still exceed the model's physical scope. |
| Not converged | Diagnostic values may be shown and labeled as such. No checked comparison or preferred design. |
| Failed | Preserve the actual error and exact attempted inputs. No computed forces, gap or mesh is invented. |
| Sweep | Present the selected point's snapshot and explanation together. Include every point, including failures, in the offline page. |

Every branch retains the unresolved physical qualification. None turns the four published standoff comparisons into force validation. None turns the copied starting point of a Joint case into Board-bound evidence after edits.

## Module map

- Add `soldershape/web/result.js` as an IIFE exposing only `SolderShapeResult`. It owns response adaptation, factual interpretation, engineering-unit display, safe HTML and original-ZIP binding.
- Add one shared style block to the existing common stylesheet for the takeaway, input snapshot and brief action.
- Update `app.js` and `board.js` only at accepted-response, result selection and invalidation sites. Replace their redundant summary construction with presenter calls where the facts overlap.
- Add fixed static serving for the single script. This is the only required server edit.
- Keep `artifacts.py`, `board.py`, calculation functions, canonical parsers, archived evidence and released ZIPs unchanged.
- Use a small Node harness for pure interpreter fixtures. Browser verification remains authoritative for the download and no-server experience.

Boundary Discipline keeps response checking in the two adapters and prose rules in one pure function. Laziness Protocol avoids a ZIP library, configurable report system, PDF dependency and second numerical implementation.

## Does the brief belong inside the ZIP?

Yes, if the desired deliverable is one conventional evidence ZIP that already contains the readable explanation and hashes it in `manifest.json`. This candidate does not meet that particular acceptance check. An unchanged server archive cannot gain a manifest-bound HTML member through presentation code alone.

The embedded-original-ZIP HTML is a coherent alternative product artifact. It binds the visible explanation to the exact downloaded ZIP with an explicit SHA-256, embeds the original archive bytes and carries input hashes. The HTML itself is not covered by the archive manifest. It must say that its summary is a derived browser presentation and that the embedded ZIP is the canonical evidence. This remains weaker than a manifest-bound brief for archive-centric review.

Repacking the ZIP in JavaScript would require a new compression dependency or a custom ZIP implementation, duplicate manifest ownership in the browser, and a special Board archive handling path. That complexity is disproportionate. It also makes CLI exports miss the new capability. I reject that extension.

If a readable brief inside every new ZIP is a firm requirement, choose server-owned interpretation and artifact rendering instead. Graft this candidate's single selected-snapshot presentation, signed-force rules and engineering-unit cues into it. Do not maintain parallel Python and JavaScript prose engines.

## Verification gates

1. Use the default Board 40/56 nL pair. Board and Joint display 400 µm upper diameter, 300 µm held gap and 240 µm offset, while downloaded canonical values remain 0.4, 0.3 and 0.24. Force numbers agree exactly before display rounding.
2. Exercise checked supported-load, zero offset, negative offset, direction reversal, no reference, not-converged, model warning and failed fixtures. Assert concrete visible sentences and absent forbidden claims, rather than comparing an implementation to itself.
3. Edit an input while a response is pending. The late response must not restore either a takeaway or brief export. Navigate and restore drafts. No numerical interpretation may survive without fresh computation.
4. Download Board and Joint briefs through actual buttons. Stop or use a different browser session without the server. Open each HTML, extract its embedded ZIP and prove the ZIP SHA-256 matches the stated value and original bytes.
5. Compare every displayed input, force, solved gap, status, error and source identity against canonical ZIP members. Preserve failures. HTML-containing source names and errors must appear as text and execute nothing.
6. Run existing archive readers and numerical replay on the original embedded ZIP. Historical ZIP hashes remain unchanged. Test a seven-point response and a realistic large archive to catch Blob memory or data-URL failures.
7. Confirm that the original archive manifest does not claim to cover the HTML. If acceptance still requires that coverage, mark this candidate failed rather than weakening the requirement silently.

## Tradeoffs accepted

- We accept a browser-specific new download in exchange for leaving calculation and archive code intact.
- We accept a larger standalone HTML file in exchange for one portable artifact with original evidence attached.
- We accept that CLI-created archives receive no readable brief. This is the main reason this candidate may lose.
- We accept plain tables rather than a second offline 3D viewer. The existing native geometry remains available in the evidence.

## Alternatives considered

A server-produced brief in the existing archive covers CLI and browser equally and gives the manifest one owner. It has a deeper evidence interface but touches archive generation and source identity. It is stronger when archive portability is the actual product requirement.

A sidecar HTML without the original ZIP is smaller but leaves an engineer with two files to keep together. Hashing a missing archive does not make the numerical evidence accessible. It loses on the handoff workflow.

A browser ZIP rewrite hides substantial archive integrity policy behind a download button. It exposes special archive responsibilities to the presenter and duplicates an existing trusted owner. It loses on maintainability.

## Synthesis decision

Pending the independent judge. This candidate is competitive for immediate on-screen comprehension. It should lose if the accepted end-to-end requirement remains a readable manifest-bound brief in every newly produced evidence ZIP.

## Next implementation step

Build the pure interpretation fixture table first, then show the same accepted Board and supported-load snapshots through the presenter and generated no-script HTML before wiring downloads.
