# Product media and walkthrough

Six JPEGs capture the actual application on 2026-10-17 at source commit `3644c08bbf0ef1976bc634bba323779055583e6b`. Both gaps were freshly computed through the normal Board controls. The walkthrough uses actual ULX3S U1/J16 copper. Its 400 µm upper wetting diameter, 300 and 330 µm held gaps, +240 µm offset, 40/56 nL liquid volumes and material values are hypothetical process inputs. Physical force accuracy remains unqualified.

The [capture manifest](capture-manifest.json) identifies the six frames. [Browser observations](../../launch_sync/evidence/capture-observations.json) retain visible forces, inputs, result origin, URLs and capture times. Screenshot bytes use their native JPEG format. The original board silkscreen is preserved.

| Time | Capture | Visible step |
| --- | --- | --- |
| 0 to 6 seconds | `board-explorer.jpg` | Actual board and selected U1/J16 copper. Other joints remain unsolved. |
| 6 to 12 seconds | `process-assumptions.jpg` | Declared upper pad, gap, offset, volumes and material inputs. |
| 12 to 18 seconds | `comparison-review.jpg` | At 300 µm, only 40 nL meets the declared numerical fixture rule. |
| 18 to 24 seconds | `changed-gap.jpg` | At 330 µm, both volumes meet that rule. Only held gap changed. |
| 24 to 30 seconds | `result-inputs.jpg` | Expanded current candidate inputs, signed forces and exact input identity. |
| 30 to 36 seconds | `lab-handoff.jpg` | Matching board question and required lab measurements. The 200 µm kit needs adaptation. |

`walkthrough.mp4` is a 36-second sequence assembled from these six actual still captures. Each stays visible for six seconds. It has no audio. It is not continuous screen recording and its editorial timing does not measure solver speed. [Captions](walkthrough.vtt) and the [full transcript](../../website/dist/transcript.html) describe the same sequence.

## Attribution

ULX3S is by EMARD and its contributors. The complete board view retains the original EMARD, RADIONA and FER silkscreen. Its [original modified MIT notice](../../board_demo/source/LICENSE.md) applies to the included board material. The board authors do not endorse SolderShape or this hypothetical comparison. Surface Evolver and the BGA force methods are by Ken Brakke. See [THIRD_PARTY.md](../../THIRD_PARTY.md).

SolderShape's original UI and accompanying documentation use the project [MIT license](../../LICENSE). Third-party content keeps its own terms. The launch asset checker records every served media file's identity.

## Rebuild the video

FFmpeg is optional for media editing. It is not an application dependency. From the repository root, run:

```sh
ffmpeg -f concat -safe 0 -i docs/media/walkthrough.ffconcat -t 36 -vf 'fps=24,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0b1b1f,setsar=1,format=yuv420p' -c:v libx264 -crf 20 -preset medium -movflags +faststart output/walkthrough-new.mp4
```

Inspect a rebuilt video before replacing the maintained file. Encoder versions can change its bytes. No generated image replaces the captured UI. Old captures remain in Git history.
