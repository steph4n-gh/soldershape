# Outside-lab physical coupon package

Experiment `SS-C220-C270-R1` compares 220 and 270 micrometer board pads under the same twenty-joint cap. This is a package for a laboratory quote and staged feasibility study. No hardware has been ordered or measured. Fabrication release requires accepted DFM and methods. The supplied files describe unit boards. The fabricator must engineer and return its production panel.

Start with [LAB_RFQ.md](LAB_RFQ.md). Send the complete archive to a prospective assembly and metrology laboratory. Ask for separate prices for DFM, hardware and materials, profiling, the three-run pilot, confirmation, and optional hot-state measurement. The lab must demonstrate the measurement capability before confirmation. The prepared RFQ has not been sent.

## Hardware and sampling

Order 12 carrier boards, 48 custom cap boards, and at least 1,200 accepted Sn63Pb37 spheres after screening. [BOM.csv](BOM.csv) specifies every material and service. Exact 320 micrometer sphere supply, screening yield, minimum order, costs, and lead time require quotes. No substitution is preapproved.

Each 40 by 40 mm carrier contains two mirrored pairs of C220 and C270 sites. Each cap is 3 by 3 by 0.8 mm, with twenty 280 micrometer mating pads at 0.5 mm pitch. Isolated copper islands and a shared mask opening avoid exposed traces changing the wetting boundary. Both sides have finite finished metal thickness. Measure them instead of transferring the old paper's one-pad correction.

Use three pilot carriers in three runs, six confirmation carriers in three further runs, one profile carrier, and two spare carriers. Confirmation contains 24 attempted caps, 12 pairs, and three run blocks. The twenty joints under one cap are dependent. [allocation.csv](allocation.csv) fixes specimen identities, paired sites, cap and sphere-kit IDs, carrier rotation, and placement order using seed 220270.

The practical outcome is the cooled minimum gap between finished pad faces. The 185 micrometer threshold is a study criterion. Mask-to-cap underbody clearance is a separate measurement. Cold geometry can support a process-specific pad comparison. It cannot alone validate molten equilibrium, restoring force, fatigue, or production yield.

## Files to use

| File or directory | Purpose |
| --- | --- |
| `hardware/carrier.kicad_pcb` and `cap.kicad_pcb` | Editable KiCad 10 unit boards, with embedded footprints and project settings. |
| `fabrication/carrier/` and `fabrication/cap/` | Actual Gerber layers, drill files, and Gerber jobs exported by KiCad. |
| `experiment.json` | Controlled dimensions, sampling, metrology gates, and fixed model hypotheses. |
| `PROCUREMENT.md`, `BOM.csv`, `LAB_RFQ.md` | Material specifications, capability sources, and staged quote request. |
| `PROCEDURE.md` | Assembly, incoming measurements, pilot gates, prediction freeze, held-out measurement, and returns. |
| `data/` | Blank confirmatory input, material metadata, and outcome templates. |
| `tools/analyze.py` | Prospective native calculations and guarded scoring. |
| `evidence/` | Actual DRC, export verification, native planning receipts, and independent reviews. |
| `research/` | Competing designs, supplier research, selection rationale, and analysis limits. |

There is no electrical schematic because the isolated pads form no circuit. These files cannot establish electrical continuity or reliability. Both boards require CNC routing and clean singulation before cap mass measurement. Do not V-score the caps. The lab must confirm at least 0.2 mm finished pad-copper clearance to the routed edge and the target pad-diameter tolerance of plus or minus 5 micrometers.

## Reproduce the files and numerical check

Run from the project or archive root. Python 3.12 or newer is sufficient for the coupon scripts. Docker is required only to rebuild CAD. Native modeling additionally requires a C compiler, `make`, and the existing Surface Evolver setup. No Rust or WASM port is needed.

```sh
python3 coupons/tools/verify_boards.py
python3 -m unittest discover -s coupons/tests -v
docker pull --platform linux/amd64 kicad/kicad@sha256:18693567392b80da435f9fa952ce3a3e534c66eb5a6033f5b9c80aa3b19dd3ec
python3 coupons/tools/build_boards.py
python3 tools/setup_engine.py
python3 coupons/tools/analyze.py plan --output output/coupon-planning-new
```

The printable guide is `output/pdf/soldershape-lab-handoff.pdf` in the project and archive root. To regenerate it, use Python with `reportlab` installed and run `python3 coupons/tools/make_lab_pdf.py`. This optional document dependency is not needed for CAD verification, model calculations, data collection, or scoring.

```sh
python3 coupons/tools/package_lab.py --output output/soldershape-coupon-r1.zip
python3 coupons/tools/package_lab.py --verify output/soldershape-coupon-r1.zip
```

The archive includes every coupon source file, the actual manufacturing outputs, the printable guide, the minimal existing solver source, its upstream setup script, and a SHA-256 manifest. It excludes the engine binary and upstream source archives. Build the engine from its pinned source only when running native calculations. After extraction, all paths and commands use the archive root.

The pinned official KiCad image reports version 10.0.6. Its CAD generation runs with networking disabled. Rebuilding preserves dimensions and seeded allocation. KiCad UUIDs and export timestamps can change. The independent verifier reads actual Gerber flashes, mask regions, outlines, drill coordinates, and DRC output. Its negative controls deliberately alter pad size, mask opening, and opposite-side copper.

The six retained native planning requests passed their numerical and load-balance checks. Under the explicitly artificial planning inputs, literal-rim gaps are 223.32 and 207.52 micrometers. The fixed two-pad-cylinder approximation gives 178.20 and 167.31 micrometers. The discrepancy is the experiment's central geometry question. These values are not lab predictions. They assume a 14 mg cap, 35 micrometer finished metal at each end, and liquid volume equal to the solid sphere volume. Actual finish, mass, density, surface tension, and thermal geometry remain unmeasured.

## Run the laboratory workflow

```sh
python3 coupons/tools/analyze.py templates --output lab-data
python3 coupons/tools/analyze.py freeze --inputs lab-data/inputs.csv --metadata lab-data/metadata.json --output lab-data/frozen
python3 coupons/tools/analyze.py score --freeze lab-data/frozen --outcomes lab-data/outcomes.csv --output lab-data/report.json
```

Fill incoming inputs and metadata from evidence after pilot qualification and before confirmatory outcomes. The blank freeze intentionally fails. Archive the completed freeze before collecting held-out heights. It contains source and input hashes, the fixed primary and secondary predictions, and actual native receipts. Missing observations remain missing. Scoring keeps all 24 attempts and all three run effects.

The lab should return its raw local-joint measurements, scans, sections, calibration and uncertainty reports, thermal traces, mass logs, certificates, failure records, and remaining parts. The requester or modeling coordinator can run the freeze and scoring commands. The measurement lab need not operate the solver if it returns the required incoming data before confirmation.

The base metrology quote must demonstrate local expanded gap uncertainty at or below 2 micrometers and paired-difference uncertainty at or below 3 micrometers. Small voxels alone do not demonstrate that accuracy. If the pilot cannot resolve the anticipated 6 micrometer comparison, revise or stop before confirmation. No successful build, numerical agreement, or synthetic test result substitutes for these physical gates.
