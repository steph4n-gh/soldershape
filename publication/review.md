# Publication source review

The publication diff against `e689643` passes source review. Launch approval remains conditional on successful hosted CI, the actual prerelease and an anonymous check of the deployed Site. Those external operations were still pending when this review ran.

The review covered the 14 changed maintained files, the existing Actions workflow and the new publication workflow and status page. No application solver, source-board bytes, recorded numerical archive or served media changed. This is a same-model independent review under the configured inherit-parent policy.

## Findings and corrections

Two stale statements in `launch/READINESS.md` were reported to root and corrected during review. The current-status link now points to `publication/RESULTS.md`, while `launch_sync/RESULTS.md` remains the preceding local qualification. The CI description now links the Actions workflow and reserves exact run status for the publication receipt. It no longer states that hosted CI has never run.

No remaining source blocker was found. The new release links deliberately target `v0.4.0-preview.1`. They must resolve before the Site is deployed. The changelog describes the completed publication, so its CI and release claims require the same final external gate.

## Direct checks

- GitHub API readback confirmed `steph4n-gh/soldershape`, public visibility, enabled issues and the `main` default branch. Private vulnerability reporting returned `enabled: true`.
- Every local destination in the five changed HTML pages exists. Their new GitHub source, release and private-reporting URLs use the verified repository identity. All maintained footers have removed source-pending copy.
- Setup instructions use the existing pinned engine builder and the actual `soldershape serve` command. Replay instructions retain the two nested native archive paths and the existing `tools/verify_board.py --replay` interface.
- An independent `python3 decision_walkthrough/verify.py` run passed. Only `standoff_mm` differs between the retained cases. The 300 micrometre candidate has positive Z force and fails the declared held-gap rule. Both 330 micrometre cases meet that numerical rule. Physical qualification remains `unqualified`.
- All maintained claims retain the isolated-joint limit, hypothetical process inputs, unresolved physical force validation, the separate height coupon and the adaptation required for the 400 micrometre force test. No production or full-board simulation claim was added.
- The builder's parsed Python structure is identical to the baseline after normalizing the two status strings. Its manifest and receipt now use `research_preview_candidate`. Historical receipts retain their original status and remain unchanged.
- `git diff --check e689643` passed. The diff contains no numerical source or retained evidence change.

## Comment Sicko result

The changed executable scope contains two status-string replacements and no added comments. The five changed HTML pages contain no HTML comments. The existing workflow and builder contain no scoped suppression or constraint comment requiring action.

Deleted comments 0. Restored comments 0. Flags 0. Reruns 0. Architect sketch not needed. Root-cause fixes not needed. Encoding offers 0. Encodings 0. Unenforced constraints 0. Historical source notices and evidence were left intact.

## Remaining launch gates

Root must record a successful hosted workflow for the exact public release commit, verify the complete release asset and hashes, and confirm the deployed Site without an owner session or bypass credential. The source review does not substitute for those checks. The research preview still has no qualified physical force accuracy or native-platform qualification beyond its recorded Apple Silicon macOS checks.

Prove It Works shaped this review by requiring API readback and an independent retained-case verifier run. No public operation or product edit was performed by the reviewer.
