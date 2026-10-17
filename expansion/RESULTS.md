# Matching force test and real-board workflow

This phase delivers a complete local source-to-test workflow. It does not establish physical force accuracy or customer demand. The native solver and model are unchanged from base `65b9839`. The earlier physical force-validation failures remain unresolved. No laboratory was contacted, no purchase or fabrication authorized, and no public deployment performed.

## What was selected

Four complete design candidates were compared before implementation. The real ULX3S atlas won over a new passive panel because it makes an actual routed-board pad traceable without adding unrelated CAM. A cool ±2 mN scalar sensor won as the staged measurement base. A transparent cap and horizontal silica stalk improve optical access. Separate x/z specimens preserve horizontal joint orientation and gravity. A simultaneous two-axis head remains an alternative if a lab already has demonstrated hot accuracy.

The strongest argument against the fixture is its unqualified integration. Sensor attachment, moment, transverse load, hot drift and complete contact-line visibility can still defeat it. Force range and resolution do not establish compatibility. The strongest argument against the atlas is that its useful physics is still one isolated joint with hypothetical process inputs. KiCad remains the better general board viewer. Surface Evolver supplies the underlying numerical capability.

The [independent design judgment](research/design-judgment.md) records scores, grafts and reversal conditions. [Product end-state](PRODUCT-ENDSTATE.md) defines the bounded opportunity. A reproducible operating domain and useful practitioner decisions could become defensible. Neither is established here. A language port, larger renderer or whole-board risk score would add unsupported scope.

## Outside-lab quotation handoff

The prepared archive is `output/soldershape-force-lab-r1.zip`. It has 128 members, 18,779,732 bytes and SHA-256 `0b4ee985fc0bde510385e92656bfac7c8df92e73f3be4a4e69e5770e9fa63274`. Its manifest explicitly keeps lab acceptance, fabrication release and physical validation false.

The package contains:

- Editable CadQuery model and dimension specification, four STEP assemblies and sixteen individual STEP parts.
- Thin-film DXF boundary artwork and sixteen dimensioned SVG drawings. The experiment uses transparent substrates with measured wettable islands and a nonwetting surround. Ordinary PCB Gerbers would not define that surface process. The original 220/270 µm PCB coupon remains separate and unchanged.
- A 38-page printable handbook, staged RFQ, 27-row BOM, assembly and measurement procedure, calibration and hot-blank requirements, uncertainty budgets and supplier acceptance questions.
- Forty-eight independent confirmation bridges across three preparation blocks, both axes, both offsets and both volume arms. Reversals and frames are within-specimen diagnostics. Commissioning and spares are separately budgeted.
- Blank input, material, calibration, covariance, outcome, raw time-series and hot-blank templates. No physical observations are supplied.
- Native numerical planning receipts, prospective freeze/scoring software, tamper controls, exact source snapshots and portable static verification.

All four STEP assemblies reimport with fifteen valid solids, no interference, 150 µm wet-face gap and 40/120 µm offset. Independent readback also checks actual holes, pocket and load-path adjacency. The modeled moving assembly is 40.394 mg. Its estimated worst carrier/joint moment is 7.124 µN·m. Those engineering estimates require supplier acceptance and assembled calibration. They are not hardware ratings. See [CAD evidence](../force_lab/cad/evidence/verification.json).

At the 200 µm-rim, 150 µm-gap, 120 µm-offset numerical example, the lateral difference is 10.070 µN and the 7 nL normal prediction is +7.619 µN. Twenty fresh native requests quantify local input sensitivities. The initial unmeasured allocation gives a 5.644 µN normal decision guard and fails the proposed 3 µN gate. A tighter unmeasured allocation gives 2.452 µN. It is a target for lab demonstration, not evidence of capability. A volume-only budget allows about 0.0458 nL expanded uncertainty before other input terms. Actual simultaneous tolerances must be tighter. Unresolved or out-of-domain reciprocal sensitivities are withheld.

The final planning archive has SHA-256 `928978bb11345a7167bd5a1944f89d80edbf7d819cbc147b8b27e016f25c4a1b`. The analyzer has SHA-256 `2613c2d36a4732555b6f423371066a5e80549ad81e0d8f89e200f899ec6acd02`. Gamma 0.48 N/m and density 9 g/cm³ remain uncharacterized example inputs. Independent actual-alloy, temperature, volume, rim and uncertainty measurements must precede a physical prediction freeze.

If the small endpoint cannot pass commissioning, the cheaper next test is lateral force at 40 µm. It cannot validate the small upward sign or whole-package motion. The retained 200 µm-offset scope warning and compressed 60 µm-gap numerical failure stay outside the primary confirmation population.

## Running board demonstration

Open [the running explorer](http://127.0.0.1:8768/board). The unmodified attributed ULX3S source is pinned to commit `6a92cec6b177191c5b0f80e260013a1f8ec147dd`. Native extraction and independent readback agree on 235 components, 1177 pads and 5365 track objects. All 381 eligible front circular pads match their SVG positions and radii. The complete original front silkscreen, including required logos, is retained. Two builds produced identical extraction manifests.

The selected FPGA pad U1 J16 is net SDRAM_D0, at board position [142.88, 86.6] mm, with actual 400 µm copper diameter. The board does not establish its actual wetting boundary or package/process inputs.

| Actual pad with hypothetical process | Volume | Computed Fx | Computed Fz |
| --- | ---: | ---: | ---: |
| 300 µm held gap, 240 µm offset | 40 nL | -184.526 µN | -181.284 µN |
| Same selected pad and boundary | 56 nL | -164.385 µN | +13.386 µN |
| Browser change to 160 µm offset | 40 nL | -143.028 µN | -218.095 µN |
| Same changed browser request | 56 nL | -121.104 µN | +47.477 µN |

These are fresh native calculations, not scaled old forces. More liquid reduces restoring force and changes vertical direction under this declared held-gap objective. An aligned height formula does not answer this offset-force question. The computation does not select a production volume, predict self-alignment, sum forces over the package or qualify yield.

The actual browser selected the source pad, changed offset, computed both meshes, exercised shared camera controls and downloaded the editable case and board-bound archive. Unsupported U2 selection cleared forces and disabled computation/export. Editing during a pending run discarded the late response. The actual changed-offset download is `board_demo/data/browser-comparison.zip`, SHA-256 `598e1bb2aa8b573ec8eeed8fd2cd54528c325f5ec589b07b58af8479244ff7b2`. Fresh replay reproduced both force pairs with zero difference and matching engine identity. [Replay receipt](browser-download-replay.json) and [actual screenshot](board-workflow.png) preserve the result.

## Repairs and verification

Independent review found and repaired four consequential defects. Shared input/force sources now retain signed covariance in the residual. Static planning verification regenerates all conclusions from expected raw requests. Frozen and observed transverse position plus expanded uncertainty must stay within 0.5 µm. Reversed volume ordering now produces correct wording. A common x bias cannot qualify overall force agreement merely because it cancels in a contrast. [Fresh repair verification](research/repair-verification.md) gives executable counterexamples.

An actual extracted-package test then found a host-cache portability defect. Static verification and scoring now use the recorded producer identity, with receipt consistency and registered-manifest checks, without requiring this host's engine. Fresh computations still require setup. The extracted final package passed static verification of all twenty requests, all thirty synthetic controls and actual neutral CAD readback with no `.engine` directory. Static verification explicitly reports that no native replay occurred. [Final independent verification](research/handoff-final-verification.md) closes that repair. The first failure and earlier planning records remain preserved.

The complete application suite passes 70 tests. The original coupon suite passes 34. The final force suite passes 30. These are 134 tests across three suites, not 134 physical observations. Missing package members, a false physical-validation flag and an empty resealed handoff are rejected. Every final PDF page was rendered and visually inspected. A drawing annotation overlap was repaired. [Preservation checks](preservation.json) confirm unchanged numerical files, original stress recording and both existing coupon archives.

Three redundant narrative docstrings were removed after Comment Sicko review. No suppressions, constraint encodings or unresolved comment findings remain in that inspected scope. Reviews used inherited same-family agents. They do not establish cross-model agreement.

## Exact local commands

From `/Volumes/Storage/oct16project`, run:

```sh
python3 tools/setup_engine.py
python3 -m soldershape serve --port 8768
```

An existing service is already running at that address. Stop only the service you started when restarting it. The older workbench services and user tabs were preserved.

```sh
python3 tools/verify_board.py board_demo/data/browser-comparison.zip --replay
python3 board_demo/tools/verify_native.py
python3 force_lab/tools/analyze.py verify-plan force_lab/planning/native-120
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s coupons/tests -v
python3 -m unittest discover -s force_lab/tests -v
```

Rebuild editable CAD and the handbook in an isolated environment:

```sh
python3.13 -m venv output/cad-env
output/cad-env/bin/python -m pip install -r force_lab/cad/requirements.txt -r force_lab/tools/requirements-docs.txt
output/cad-env/bin/python force_lab/tools/build_cad.py
output/cad-env/bin/python force_lab/tools/verify_cad.py
output/cad-env/bin/python force_lab/tools/build_handbook.py
python3 force_lab/tools/package_lab.py build output/soldershape-force-lab-rebuilt.zip
python3 force_lab/tools/verify_handoff.py output/soldershape-force-lab-rebuilt.zip --output output/new-extracted-check --cad-python output/cad-env/bin/python
```

Rebuilding CAD or PDF can change export metadata and package hashes. Preserve delivered revisions. Native KiCad source extraction uses the hash-pinned Docker image described in [NATIVE.md](../board_demo/NATIVE.md). The runtime app does not require Docker, CadQuery or document packages.

To prepare actual independent physical inputs, begin with `python3 force_lab/tools/analyze.py templates output/new-lab-inputs`. Complete the blanks using the lab's commissioning evidence. Follow [the lab README](../force_lab/README.md) to freeze before confirmation and register the resulting manifest digest. Blank or inadequate evidence is deliberately rejected. Do not fit material inputs to confirmation forces.

## Remaining decisive gates

The next physical gate is a lab capability response and accepted interfaces, followed by hot blanks and assembled calibration. A lab must demonstrate wetting boundaries, actual-rim feedback, volume uncertainty and sensor load limits before acquiring confirmation data. The next product gate is practitioners showing a useful decision or experiment beyond their strongest current method. Neither gate can be completed with more local visual features.

Experience First chose a real board-to-pad-to-result route. Model the Domain separated board identity, numerical requests and physical observations. Build the Lever produced deterministic extractors and repeatable artifact tools. Explain the Number withheld unresolved tolerances and preserved failed uncertainty budgets. Prove It Works required actual browser downloads, native replay, CAD readback and an engine-free extracted handoff.
