# SolderShape introduction site

This is a buildless static introduction, recorded comparison, local setup guide and evidence download. It does not accept boards, run native computations or connect to the local service. Source publication remains a separate release step.

`dist` is the maintained site source. `.openai/hosting.json` contains the registered Sites identity. Preserve that exact ID. Never create a second site for this checkout. The source helper runs in `output/launch-site`, an ignored publishing mirror with its own Git history. The application repository retains the canonical static source.

Prepare attributed assets from the actual captures and immutable recorded Board archive.

```sh
python3 tools/prepare_launch_assets.py
python3 -m http.server 8770 --bind 127.0.0.1 --directory website/dist
```

The preview address is `http://127.0.0.1:8770`. Choose an unused port if needed. Stop the owned preview server after QA. No package installation or build is required.

The Sites source helper opens and pushes the separate source repository, then packages exactly that pushed commit. Use the Sites plugin and its stored project ID for publication. Pass short-lived credentials only through its helper's hidden stdin. Do not put credentials in command arguments, files, shell history or this repository. Keep the site's existing audience. Public access is an owner decision.

After editing `dist`, copy the complete canonical `dist` into the existing `output/launch-site/dist` before saving through the helper. The `.openai/hosting.json` identity must match. Verify the actual site links, recorded toggle, video, download and narrow layout before packaging. `launch/site-receipt.json` records the selected deployment and DNS outcome.

The example download is an outer notice-bearing wrapper. Its inner ZIP remains byte-identical to the earlier numerical record. The standalone HTML explains which links require extracting that inner evidence. `launch/media-inventory.json` records every served asset identity.
