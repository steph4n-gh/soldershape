# Product media and walkthrough

The PNGs are real captures of the running local application on 2026-10-16. The capture uses the UI at `79170fc` and its already computed default Board result. The 400 µm pad, 300 µm held gap, 240 µm offset and 40/56 nL volumes are hypothetical process inputs. Physical force accuracy remains unqualified.

- `board-explorer.png` shows the actual ULX3S board, selected U1/J16 pad and original native silkscreen.
- `comparison-review.png` shows the result interpretation and two computed meshes.
- `result-inputs.png` shows the selected result's force explanation and input snapshot.
- `walkthrough.mp4` is a 24-second visual walkthrough assembled from those three still captures. Each remains visible for eight seconds. It is not continuous screen recording and does not represent computation speed. It has no audio.
- `walkthrough.vtt` supplies a short caption track. The transcript below describes the same content.

## Transcript

From 0 to 8 seconds, Board explorer shows the ULX3S PCB and selects U1/J16. The other 1,176 pads supply context and are not computed. The source copper is 400 µm.

From 8 to 16 seconds, the two-volume comparison shows X/Z forces of −184.526/−181.284 µN for 40 nL and −164.385/+13.386 µN for 56 nL. The declared fixture objective requires restoration without an upward separating force. The larger volume pushes upward under these held-gap assumptions.

From 16 to 24 seconds, the expanded Candidate result lists the 56 nL volume, 300 µm held gap, 240 µm offset, material values, signed forces and exact input identity. The HTML review and evidence ZIP preserve the numerical observations for inspection and replay. Physical measurement is still required.

## Attribution

ULX3S is by EMARD and its contributors. The complete board view retains the original EMARD, RADIONA and FER silkscreen. Its [original modified MIT notice](../../board_demo/source/LICENSE.md) applies to the included board material. The board authors do not endorse SolderShape or the hypothetical comparison. Surface Evolver and the BGA force methods are by Ken Brakke. See [THIRD_PARTY.md](../../THIRD_PARTY.md).

SolderShape's original UI and accompanying documentation use the project [MIT license](../../LICENSE). Third-party content keeps its own terms. Media identities are recorded by the launch artifact checker.

## Rebuild the video

FFmpeg is optional for media editing. It is not an application dependency. From the repository root, run:

```sh
ffmpeg -f concat -safe 0 -i docs/media/walkthrough.ffconcat -t 24 -vf 'fps=24,scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b1b1f,setsar=1,format=yuv420p' -c:v libx264 -crf 20 -preset medium -movflags +faststart output/walkthrough.mp4
```

Review a rebuilt video before replacing the maintained file. Encoder versions can change its bytes. No generated image replaces the captured UI.
