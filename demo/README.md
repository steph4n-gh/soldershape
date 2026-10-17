# Inspect the misalignment stress demo

Open a local, recorded comparison of two solder volumes under a held gap. Inspect actual native meshes, test the model limits, and export inputs for fresh computation.

1. From the repository root, start the local server.

   ```sh
   python3 -m soldershape serve --port 8765
   ```

2. Open http://127.0.0.1:8765/demo. The first view compares 5 and 7 nL at 120 micrometers of offset. The smaller volume restores more strongly and pulls downward. The larger volume pushes upward at the prescribed 150 micrometer gap. These are conditional computed forces.
3. Orbit either exact mesh to rotate both views. Use Mesh edges, the arrow keys, plus and minus, or Reset view. The camera changes the view only.
4. Select **40 µm offset**, **200 µm limit**, or **60 µm gap failure**. These are separate recorded equilibria. At 200 micrometers, the larger-volume result has a substrate-plane warning. The compressed control has no checked equilibrium. Both block the comparison.
5. Choose **Download all native evidence**. Verify the actual downloaded file from the repository root.

   ```sh
   python3 tools/verify_demo.py /path/to/evidence.zip
   ```

6. Choose **Save selected editable comparison**. Open **Joint workbench**, choose **Open case**, and select the downloaded JSON. Run **Compare reference and candidate** to compute afresh. The compressed control exports a single case. Use **Solve joint** for it.

Recorded inspection works without the native engine. To recompute, first build the pinned engine and then run the native replay.

```sh
python3 tools/setup_engine.py
python3 tools/verify_demo.py demo/data/stress-cases.zip --replay
```

The verifier distinguishes six numerical successes from the deliberately retained Hessian failure. `recording_verified=true` means the recorded behavior reproduced. It does not mean every case solved or that physical accuracy passed. The generic application replay command reports the retained failed case as a failure. Use the dedicated command above for this recording.

To regenerate every retained case from fresh native computation, run the following commands. The builder replaces the canonical recording, so preserve a copy first if you need the previous byte identity.

```sh
python3 tools/build_demo.py
python3 tools/build_demo.py --verify
python3 tools/verify_demo.py --replay
python3 -m unittest tests.test_demo -v
```

There is no cached-recording builder. Source files must match the imported numerical code before and after native work. Archived scripts are evidence and never execute during replay. Native logs can change the archive digest on regeneration even when forces agree.

The [results and limits](RESULTS.md) explain the decision, verification and remaining uncertainty. [protocol.json](protocol.json) contains every prescribed input. The 36-pad KiCad footprint supplies context for the highlighted joint. It is not a newly fabricated board or a coupled package calculation.
