# SolderShape introduction site

This is a buildless static introduction, recorded comparison, local setup guide and evidence download. It does not accept boards, run native computations or connect to the local service. The public source is https://github.com/steph4n-gh/soldershape.

`dist` is the maintained site source. `.openai/hosting.json` contains the registered Sites identity. Preserve that exact ID. Never create a second site for this checkout. The source helper runs in `output/launch-site`, an ignored publishing mirror with its own Git history. The application repository retains the canonical static source.

Prepare attributed assets from the actual captures and two immutable recorded Board archives.

```sh
python3 tools/prepare_launch_assets.py --receipt launch_sync/evidence/media-inventory.json
python3 -m http.server 8770 --bind 127.0.0.1 --directory website/dist
```

The preview address is `http://127.0.0.1:8770`. Choose an unused port if needed. Stop the owned preview server after QA. No package installation or build is required.

The Sites source helper opens and pushes the separate source repository, then packages exactly that pushed commit. Use the Sites plugin and its stored project ID for publication. Pass short-lived credentials only through its helper's hidden stdin. Do not put credentials in command arguments, files, shell history or this repository. The owner authorized public launch. Preserve the current public audience on future routine updates.

After editing `dist`, copy the complete canonical `dist` into the existing `output/launch-site/dist` before saving through the helper. The `.openai/hosting.json` identity must match. Verify the actual site links, recorded toggle, video, download and narrow layout before packaging. `launch/site-receipt.json` records the earlier deployment and DNS outcome. The later saved source version is identified separately under `launch_sync/evidence`. A save is not a deployment or audience change.

The example download is an outer notice-bearing wrapper. It contains both byte-identical native ZIPs and their exact extracted review members under `gap-300` and `gap-330`. Extract the outer wrapper before opening either HTML review. `launch_sync/evidence/media-inventory.json` records every served asset identity. `media/walkthrough.json` selects saved native rows rather than calculating forces in the browser. The six real captures and captioned 36-second still sequence follow the same decision.
