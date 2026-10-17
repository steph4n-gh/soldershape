# Quote the force experiment in stages

Prepare a technical and commercial quotation for an isolated molten-solder bridge experiment. This document is a draft for the project owner to send. No request has been sent, no lab has accepted the work, and no order is authorized.

The test compares 5 and 7 nL liquid bridges between 200 µm circular wettable rims. Both rims stay horizontal. The actual hot gap is held at 150 µm. Separate specimens test 40 and 120 µm lateral offsets. A cool, nominal ±2 mN scalar force head measures lateral force first and normal force in a separate indexed configuration. The joint's orientation relative to gravity must stay unchanged.

## Return a capability matrix first

For each requirement, return accepted, conditional, or unavailable. Name the evidence, unresolved integration work, owner, estimated cost, and lead time. Distinguish equipment already commissioned in your lab from equipment that requires purchase or custom development.

| Requirement | Required quotation evidence |
| --- | --- |
| Force measurement near 10 to 150 µN in both signs | Assembled expanded uncertainty at most 2 µN, traceability, bandwidth, drift, and coverage justification |
| Custom upper carrier | Written sensor-supplier acceptance of attachment, mass, moments, cross loads, overload protection, and sensor-body temperature |
| Hot rim position | Calibrated observation of both actual wettable rims, feedback method, uncertainty, drift, and tilt |
| 120 µm offset | Coarse and fine travel plan with collision limits and local metrology |
| Stable pinned boundaries | Thin-film process, metal finish, nonwetting surround, complete contact-line observation, and rejection rules |
| Actual liquid volume | Independent mass or geometry method with liquid-density correction, transferred-material accounting, and uncertainty |
| Actual material inputs | Alloy identification and independent density and surface tension at the chosen temperature and atmosphere |
| Thermal and chemical environment | Accepted heater, purge chemistry, oxide control, local temperature mapping, and cool-sensor isolation |
| Confirmation | 48 independently prepared bridges in three blocks, retained failures, randomized volume order, and no outcome-driven input fitting |
| Data ownership and delivery | Raw logs, images, calibration certificates, scripts, edited native CAD, deviations, and complete scoring inputs |

Published resolution is not accepted as the assembled uncertainty. Public specifications for the candidate instruments do not establish hot-fixture accuracy or interface compatibility. Quote the uncertainty at the actual small forces. Do not quote only a percentage of full scale.

## Quote separate work packages

1. Quote a feasibility and interface review. Return approved or rejected mechanical interfaces, an optical-access sketch, the force and position budgets, and a stop decision. Do not buy the reference instruments for this stage.
2. Quote an assembled-carrier transfer calibration and hot no-bridge demonstration. Include the indexed axis configurations, representative moments, heat and purge controls, and raw time series. Stop before confirmation if the uncertainty gates fail.
3. Quote sacrificial process commissioning. Demonstrate stable wetting and measurable liquid volume at 40 µm before the difficult 120 µm endpoint. Establish dwell and reversal rules before confirmation.
4. Quote a prospective prediction freeze and 48 independent confirmation bridges. Keep separate prices for the lateral and normal phases. Include all failures in the disposition table.
5. Quote a separate diagnostic option for 200 µm offset and the 60 µm compressed gap. Label this work outside the confirmatory pass criteria.

List labor, custom fabrication, consumables, equipment access, outsourced metrology, software work, shipping, taxes, and contingency separately. State the currency, quote validity, assumptions, exclusions, and lead times. Stock, commercial availability, supplier approval, and actual prices are unconfirmed in this package.

## Resolve these interfaces before fabrication

The provided CAD does not establish compatibility with an Oxford head, a PI stage, or a Linkam chamber. Return final supplier-specific attachment drawings with approved load and thermal limits. Include the complete moving mass and its center of gravity. Taring does not restore sensor range. A second support at the hot carrier is prohibited unless its force contribution is independently measured and the protocol is revised.

The intended optical arrangement observes the upper rim through a transparent cap and the joint from two directions. Establish whether the full wetting boundary is visible despite the metal island and stalk. If a hidden section can depin undetected, reject the fixed-rim test or propose a separately qualified geometry.

Specify the thin-film stack, finished wettable diameter, film height, roundness, roughness, nonwetting surround, cleaning, bond material, and hot compatibility. Nominal 200 µm artwork is not the final hot boundary. The lab must propose and qualify these manufacturing details before release.

The alloy and temperature are deliberately unspecified until the lab proposes a measurable, stable process. Select them using independent material evidence. The existing example surface tension and density cannot substitute for characterization. If flux creates the liquid interface, the solder/gas model may not apply. A changed interface requires a model-scope review before confirmation.

The initial 0.1 nL volume uncertainty budget fails the difficult normal-force endpoint in local native sensitivity checks. A tighter, unmeasured candidate uses expanded volume uncertainty 0.02 nL together with 0.25 µm diameter and gap uncertainties. Quote a demonstration of the complete transferred-liquid-volume method before promising this endpoint. Readability of a balance or nominal ball diameter is insufficient. See `uncertainties.md` for the assumptions and failed budget.

For a Linkam stage, obtain explicit acceptance of any custom carrier port or optical access. Its documented electrical probes are not force probes. The manufacturer's support page permits nitrogen and argon and prohibits helium and hydrogen. Do not assume a hydrogen or formic-acid process is compatible. [Linkam stage support](https://www.linkam.co.uk/support/stages/general).

## Return a reviewable evidence package

Deliver the following files with stable specimen and calibration identifiers.

- Editable CAD and approved drawings, neutral exports, material certificates, and an as-built dimension report.
- Sensor certificates, full axis-response and moment tests, force-sign checks, before and after calibration checks, raw hot blanks, and the complete uncertainty budget.
- Alloy, temperature, atmosphere, oxide-control, liquid-density, surface-tension, and liquid-volume evidence independent of the confirmation force outcomes.
- Time-synchronized raw force, actual-rim coordinates, local temperatures, sensor-body temperature, controller commands, and unprocessed images for each bridge.
- Complete allocation and disposition records, including failed, missing, depinned, unstable, and out-of-domain specimens.
- Exact frozen inputs, independently registered manifest digest, later outcomes, analysis outputs, deviations, and a signed conclusion that states which endpoints were measurable.

If the integrated 120 µm uncertainty gate is unavailable, quote the cheapest decisive alternative. Prefer lateral-only 40 µm commissioning with the same horizontal joint over an unqualified hot two-axis system. State explicitly which endpoint remains inconclusive.
