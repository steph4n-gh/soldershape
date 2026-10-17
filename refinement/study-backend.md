# Focused study backend

`read_study` normalizes one prospective study document. It binds each lower diameter to its own selected source footprint. A caller cannot provide a replacement lower diameter or a prescribed gap. Each arm requires a separate boundary evidence declaration. The declaration can explicitly state an unverified planning assumption. It is not proof of mask geometry or wetting.

`run_study` sends two literal-rim nominal requests to the actual native solver. An optional two-pad equivalent-volume hypothesis adds two requests. It adds each pad cylinder's volume and subtracts both finished metal thicknesses from the solved height. Gravity must be off for this hypothesis. Its mesh exports are named `equivalent-domain-mm.obj` and `equivalent-domain-mm.stl`. These meshes are not physical solder-shape measurements.

The report contains three finite analytical volume samples per arm and hypothesis. The formula is independently transcribed from [Van Veen, Vandevelde and Beyne, 2004](https://imapsjmep.org/article/39820.pdf), printed page 58, Eqs. 2, 6 and 9. The unloaded spherical height is found from the volume equation. Eq. 9 supplies axial stiffness. Load divided by stiffness gives the first-order compression. SI conversion is explicit in the report. Zero offset, gravity off, finite positive stiffness and compression no greater than one percent of unloaded height are required. One percent is a conservative software policy. It is not an experimental error bound.

The default example's independent analytical nominal gaps are 223.349072, 207.519669, 178.249754 and 167.318023 micrometers. The order is Reference literal, Candidate literal, Reference two-pad and Candidate two-pad. The native engine must establish its own numbers. No native result is replaced by the formula. Numerical agreement greater than the maximum of 0.1 micrometer and 0.1 percent of native nominal gap blocks an analytical screen conclusion. Agreement is necessary for this software screen. It is insufficient for physical qualification.

The decision has no winner or fabrication-approved state. Failed native calculations take priority. Unsupported analytical inputs produce `sensitivity_unavailable`. Crossing the declared criterion or changing the revision ordering across the declared samples produces `assumption_sensitive`. `screened_samples` says only that those sampled values retain the criterion side and ordering. The reported extrema are neither continuous tolerance bounds nor probability estimates.

`bundle_study` reuses the native bundle format and raw receipts. It adds the normalized study, complete report, both footprint sources, escaped static HTML and sample CSV. All members have hashes. `replay_study` verifies the existing archive bounds and hashes. It regenerates request identity from the study and checks the stored report, conclusion, samples and readable exports before computation. It then recomputes the native and analytical calculations. It never executes archived engine commands. A numerically failed saved or fresh case cannot pass replay.

The separate study document deliberately preserves the mature single-joint editable-case parser and force-viewer workflow. The early candidate B sketch's shared parser migration was unnecessary for this isolated workflow.

## Verification

Run the fast behavior and archive controls with the following command.

```sh
python3 -m unittest tests.test_study -v
```

The 11 checks cover actual source-to-request diameter and hash binding, retained independent formula values, missing provenance, unsupported mask openings, forbidden parameter overrides, finite-sample decision policy, failed receipt preservation, numerical disagreement, readable archive content, deterministic bundle output, resealed input and conclusion changes, HTML escaping and nonexecution of archived commands.

All native responses in this fast test file are explicitly synthetic doubles. They test serialization and decision controls. They are not evidence of engine accuracy or physical agreement. Fresh actual native computation and browser acceptance are owned by the parent refinement run.

Model the Domain keeps study input and report output as separate dictionaries with one normalization boundary. Laziness Protocol keeps the old case format intact and reuses native solve and bundle tools. Prove It Works checks opened archives, regenerated requests and tampered exports rather than trusting stored verdicts.
