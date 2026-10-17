# Lab documentation report

Prepared `force_lab/README.md`, `RFQ.md`, `PROCEDURE.md`, `BOM.csv`, and `uncertainties.md` for the selected cool scalar-sensor fixture. No CAD, analysis code, templates, or PDF was edited by this owner.

The documents define a staged quote, interface acceptance, commissioning, independent inputs, a prospective freeze, 48 held-out bridges, raw evidence delivery, and stop conditions. Separate x and z specimens retain horizontal pads and downward gravity. The upper load path has no auxiliary contact or unqualified temperature lead. The procedure requires actual hot-rim registration and observable pinned boundaries.

The reference dimensions agree with `force_lab/cad/spec.json`. These include the 10 × 10 × 0.5 mm lower chip, 2 × 2 × 0.3 mm upper cap, 0.35 mm pad setback, 20 × 1 mm horizontal stalk, and 150 µm wettable-plane gap. The 0.5 µm film and bond envelopes remain unqualified manufacturing details. Sensor, stage, chamber, attachment, and chemistry interfaces block fabrication release.

The BOM has 27 rows and 10 columns. It includes 72 upper and lower specimen carriers and 72 solder charges. This is 48 confirmation bridges, 12 commissioning bridges, and 12 spares. The last two quantities are quote allowances. Actual stock, price, lead time, and supplier acceptance are unknown. The CSV distinguishes candidate commercial instruments from custom work.

The analysis owner confirmed the 48-specimen allocation and current CLI. The procedure uses independent pre-freeze hot geometry registration with a blinded force channel. It calls out the burden of registering all 48 specimens before one freeze. Reheating or remounting must preserve the frozen boundary within its declared uncertainty. A nominal cold-stage setpoint is insufficient.

Fresh native planning supplied a failed input budget and a tighter unmeasured candidate. The original 0.1 nL volume budget gives about 5.644 µN normal guard and fails the 3 µN gate. A tighter 0.02 nL volume and 0.25 µm diameter/gap candidate gives about 2.452 µN normal guard. This is numerical feasibility screening only. At example density, 0.02 nL corresponds to 0.18 µg. The XPR2U's advertised 0.15 µg typical repeatability does not establish that complete transferred-mass uncertainty. The RFQ now makes volume metrology a decisive capability demonstration.

Primary sources were checked in the metrology report and re-opened for the Oxford small-force ranges, PI positioning limits, Linkam gas restriction, Heraeus material properties, and Mettler balance specifications. The sources support candidate capability, not integrated hot accuracy or availability. No lab message, order, purchase, or fabrication release occurred.

Local checks parsed all CSV rows, confirmed the 72-charge allowance, counted all 48 allocation IDs, found six independent specimens per axis/offset/volume group, checked the key CAD dimensions, and verified the analyzer's actual CLI help. The documents contain no long-dash characters. The root owner must still render and inspect the combined PDF, verify the complete handoff package, and review the physical claims with the final code.

The original 220 versus 270 µm height coupon remains separate. The new force test matches the original 200 µm stress geometry. It does not physically validate the 400 µm ULX3S hypotheses or a complete PCB.
