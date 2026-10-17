# Public research preview review

The deployed research preview passes this scoped review. No publication blocker was found in the public-file verifier, its completed receipt, the release evidence, or the maintained launch copy. This is an independent review under the configured inherit-parent model policy. It is not a physical-model qualification.

## Public-file proof

`verify_public_site.py` requests every maintained static file without an Authorization header or cookie jar. The completed `evidence/public-files.json` receipt covers 108 files. I independently recomputed every local canonical SHA-256 and compared the complete path set with that receipt. All 108 match the current source.

Seven HTML responses contain one Cloudflare managed JS-detection script. The remaining 101 responses match their canonical bytes directly. For HTML, the verifier removes a script only after its entire normalized byte sequence matches the pinned SHA-256. Only the provider ray identifier and timestamp values vary. The rest of the response must then match the complete canonical file exactly. It does not strip arbitrary scripts, tags, whitespace, text, or attributes.

I ran seven independent in-memory controls against the actual verifier and current `index.html`. Canonical bytes, the known provider insertion, and changed provider ray/timestamp values passed. A changed application heading, changed provider code, an unrelated script, and two provider insertions all failed. These controls made no network request and changed no product file. They support the narrow normalization rule. They do not authenticate Cloudflare or prove that its injected JavaScript is harmless.

Anonymous reachability is established for the explicit `SolderShape-publication-check/1.0` User-Agent used in the receipt. Root also reports ordinary browser checks separately. The default Python User-Agent receives Cloudflare error 1010. The final publication report must retain this client restriction. A successful custom-User-Agent check does not prove universal HTTP-client access. The verifier follows redirects and does not record each final URL. The separate root-page HTTP receipt records the expected requested and final custom-domain URL. The verifier uses Python assertions and must be run without `-O`.

## Release and copy

The reviewed receipts identify release source `ecac5fc41c136a878d2f34ed6673d54d5e0a341f`, successful main and tag CI, 1,502 matching package members, fresh native numerical replay with zero force difference, four matching GitHub server asset digests, and an anonymous full-package download with the same SHA-256. The release is a published prerelease rather than a draft. GitHub private vulnerability reporting is recorded as enabled.

The Site receipt identifies saved version 3 and source commit `e00393660155e4bebd364c5e238c49c6ae50ec53`. The final public deployment receipt reports success for that version. The access receipt reports `public`. The initially unsuccessful access attempt remains in the evidence rather than being overwritten.

The maintained launch pages, README, security policy, and release notes consistently describe a local research workbench. They link the actual public repository, prerelease, and private reporting form. Their comparison retains the 300 and 330 micrometre hypotheses, exact force signs, isolated-joint scope, six actual still captures, and 36-second editorial video duration. The pages preserve the unresolved physical force discrepancies, the separate 220 versus 270 micrometre height coupon, and the adaptation required to use the 200 micrometre force fixture for the 400 micrometre Board question. I found no stale source-pending statement or added production-accuracy claim on those maintained surfaces.

`publication/RESULTS.md` still describes publication as in progress at review time. Root owns its final update. This is a documentation closeout item, not an unresolved deployment failure. The earlier source review correctly labels its CI and deployment checks as pending at the time it ran.

## Comment Sicko result

The new verifier has no inline comments, suppression directives, workaround comments, or constraint comments. Its module docstring states the proof scope. Deletions 0. Restored comments 0. Flags 0. Reruns 0. Architect sketch not needed. Root-cause fixes not needed. Encoding offers 0. Encodings 0. Unenforced constraints 0.

## Limits

This review inspected the completed 108-file network receipt rather than issuing another 108 requests. It did not repeat browser interaction, mobile layout, video playback, or the full release download. Root is recording those checks separately. It did not change a public setting, deploy, mutate a candidate, edit source, or rerun an asset generator.

Prove It Works shaped the review by requiring current canonical hash comparison and negative controls against the real normalization code. Physical force accuracy and unexercised native platforms remain unqualified.
