# Rebuild the quotation geometry

The editable native model is `model.py` with dimensions in `spec.json`. These are CadQuery source files. Neutral geometry is in `../hardware/`. Dimensions are millimeters. All interfaces marked unreleased remain unreleased after a successful build.

From the repository or extracted package root, use Python 3.13 and an isolated environment. This geometry was checked with CadQuery 2.6.1 on Apple Silicon macOS. Other platforms need their own installation and readback check.

```sh
python3.13 -m venv output/cad-env
output/cad-env/bin/python -m pip install -r force_lab/cad/requirements.txt
output/cad-env/bin/python force_lab/tools/build_cad.py
output/cad-env/bin/python force_lab/tools/verify_cad.py
```

The builder replaces generated STEP, DXF, SVG, geometry and manifest files. Preserve a revision before changing dimensions. It emits four assemblies for x/z sensing and 40/120 µm offsets, individual parts, thin-film boundary artwork and drawings. `requirements-lock.txt` records the environment used for the retained exports. It is an environment receipt, not a claim of platform-independent binary equivalence.

The verifier independently reimports every STEP, checks solid counts and validity, measures pad planes, verifies actual hole and pocket geometry, reads DXF units and island dimensions, checks the intended load path, and rejects interference. Its mass and beam calculations use declared planning material properties. They do not certify the assembled sensor, bonds, hot temperature, optical resolution or full-rim pinning.

To rebuild the printable handbook in the same environment:

```sh
output/cad-env/bin/python -m pip install -r force_lab/tools/requirements-docs.txt
output/cad-env/bin/python force_lab/tools/build_handbook.py
```

Thin-film islands and a nonwetting surround on transparent substrates define the proposed wetting boundary. The DXFs are nominal thin-film fabrication artwork. Ordinary PCB Gerbers would not define that surface process, so no unrelated PCB is added to this fixture. The original 220/270 µm PCB coupon remains a separate experiment.

The cool adapter has an internal fixture pattern and a deliberately unfinished vendor interface. The final sensor attachment, allowable moment/cross load, heater, chamber, stage and thin-film stack require a lab-approved drawing revision before machining release. Neither STEP validity nor these instructions authorize fabrication.
