# Solder-volume comparison at a prescribed gap

Choose the tested nominal volume with the largest minimum lateral restoring force, among candidates that have no upward axial force and stay inside the pad pitch cell at every tested volume scenario.

This is a conditional volume-screening example. The separating-load rule and the volume tolerance are declared assumptions.

| Nominal volume, mm³ | Restoring force range, µN | Axial force range, µN | Minimum cell clearance, mm | Eligible in tested scenarios |
| --- | --- | --- | --- | --- |
| 0.005 | 19.401 to 20.489 | -161.879 to -88.049 | 0.07602 | True |
| 0.006 | 17.959 to 20.457 | -96.600 to 9.549 | 0.06263 | False |
| 0.007 | 13.733 to 18.880 | -16.903 to 98.124 | 0.05058 | False |

Positive axial force separates the pads. Negative axial force pulls the pads together. Lateral force is reported as a positive restoring magnitude at the positive imposed offset.

The declared rule selects less-0.005. Every tested scenario for this candidate passes the numerical checks and satisfies the nonseparating-load and pitch-cell constraints.

The volume-equivalent sheared cylinder selects more-0.007. Its force calculation does not enforce the fixed pad radius. Compare its axial-force signs with the solved pinned-rim shapes before using it for volume selection.

The sheared-cylinder approximation has a volume-dependent effective radius. It does not preserve the fixed wetted rim. Its predicted forces are useful as a cheap competing calculation, but the changed radius makes its failure informative about the boundary condition.

The numerical status checks refinement, equilibrium stationarity, volume conservation, and export topology. It does not establish physical accuracy for the chosen alloy, temperature, and flux.

Declared illustrative +/-10 percent volume sensitivity. It is not a measured process capability or probability distribution. Five samples do not certify every point in the interval.

Pinned, fully wetted circular rims. Prescribed wetted-plane gap and lateral offset. One isolated joint. Conditional forces at the supplied surface tension. The pitch cell check is a geometric envelope screen, not solder-bridge validation. The physical comparison uses a different pad diameter and gap, so its results do not qualify this design geometry.

The volume scenarios come from the workbench demonstration input. The footprint filename includes a nominal ball diameter, but this example does not establish the component's actual solder volume or recommend changing its ball specification.

A different separating-load requirement can select a different volume. These results do not predict free assembly height, placement yield, or alignment time.

Reproduce the run with the source and engine identity in `comparison.json`.

```sh
python3 tools/compare_designs.py --solver-sha256 07b45f912cadedc9ae69313820a46a40248459696bbe70d9b769fea287deeb98
```
