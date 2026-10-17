# Software corrections after the first lab handoff

The original R1 coupon geometry and physical experiment remain unchanged. The first handoff archive is historical output. Use the separately named refined archive for the corrected analysis tools. No physical observations or laboratory capability have been added.

The analysis now takes an authoritative immutable snapshot of incoming CSV, metadata, experiment and allocation. It validates, predicts and archives those same bytes. Previously a worksheet edit between validation and copying could produce an internally inconsistent completed freeze. The corrected code also normalizes archived numeric-string metadata during scoring instead of crashing.

A gross input-uncertainty screen now blocks model agreement when the already retained analytical sensitivity exceeds the declared five micrometer error budget. Measured clearance and observed process comparisons remain separate. Passing that coarse screen does not propagate native uncertainty or qualify physical accuracy.

The regression suite now includes source-file changes, code/specification/allocation changes, numeric-string scoring and excessive uncertainty. Original before-fix reports and numerical receipts remain historical evidence. Re-run the supplied tests against the corrected source before using it.

The final repair also checks every archived input against its original snapshot before completing a freeze. Scoring parses and hashes the same outcome bytes, and consumes the verified prediction snapshot. Calculation modules capture source identities when imported. A long-lived process rejects changed source until restarted. Hashes provide integrity and provenance evidence, not authentication or physical validation.

```sh
python3 -m unittest discover -s coupons/tests -v
```

Existing completed freezes remain tied to their source hashes. Do not rewrite an old freeze or its code hashes to make a new scorer accept it. Preserve the old record and produce a separately labeled prospective revision when appropriate.
