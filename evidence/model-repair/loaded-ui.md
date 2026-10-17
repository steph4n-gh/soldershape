# Supported normal load in the workbench

The vertical condition is either a prescribed gap or a supported normal load per joint. The form submits exactly one of `standoff_mm` and `normal_load_uN`. Shared material, offset and geometry inputs keep their existing fields. Editable cases keep `soldershape.case.v1` and infer the vertical condition from the parameter shape when opened.

The inactive vertical input is hidden, disabled and not required. Switching the condition invalidates results and downloads. It keeps the saved reference dimensions, so both designs recompute under the newly selected shared condition. Zero normal load is accepted by the form and retained when a case is reopened.

Loaded geometry comes from `result.equilibrium`. The exact request remains in `result.input`. A loaded request has no input gap. Before solving, the viewer asks the user to compute the gap and geometry. A failed loaded result shows no gap or mesh. The force panel shows solved gap, supported load, force-balance residual and the returned numerical tolerance. These labels make no physical accuracy claim.

Both result tables include a gap column. A comparison describes the common prescribed gap or common normal load. Under load, it displays each design's independently solved gap. Offset sweeps state that each offset requires a fresh height solve. The load help text states that package weight and load sharing require an external calculation.

## Checks performed by the UI implementation worker

These commands passed.

```sh
node --check soldershape/web/app.js
git diff --check -- soldershape/web
```

An inline Node VM harness exercised the application event handlers against a small DOM fixture. It checked these eleven behavior groups.

1. Prescribed-gap requests exclude `normal_load_uN`.
2. Loaded requests exclude `standoff_mm`, and inactive input validity is disabled.
3. A vertical-condition change preserves reference dimensions.
4. Unsolved loaded geometry is deferred.
5. Result metadata and table gap use the returned equilibrium.
6. Failed loaded points show no invented gap or geometry.
7. A loaded case reopens in load mode, including a zero load.
8. A prescribed-gap case reopens in gap mode.
9. A rejected case preserves the current inputs.
10. A response arriving after a vertical-condition change is discarded.
11. The discarded response cannot enable a stale download.

The harness printed `PASS 11 loaded-UI behavior groups`. This is a DOM fixture check. It does not establish browser layout, native computation, or physical accuracy. The root worker owns the running-browser and native-backend acceptance checks.

## Principles applied

Model the Domain shaped the mutually exclusive parameter fields and the separation of requested inputs from solved geometry. Laziness Protocol kept the existing case schema, routes and DOM rendering, with no new dependency or client-side physics calculation.
