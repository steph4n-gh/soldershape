# Product refinement design brief

The first intended user is a PCB packaging or assembly process engineer working with a test lab. The job is to compare a proposed lower-pad or solder-volume revision, identify assumptions that reverse a minimum pad-face-gap decision, and hand a reproducible case to a colleague or lab. Demand and willingness to pay are unproven. No current moat is claimed.

The current browser reference stores only upper diameter and volume, so it cannot compare the actual 220 versus 270 micrometer lower-pad study. It also presents numerical results without a decision criterion or input sensitivity review. The native solver adds no demonstrated accuracy over the published analytical formula for aligned small-load heights. Physical applicability remains conditional and geometry mapping can reverse a 185 micrometer outcome.

Design one complete narrow browser-and-export workflow. Compare structurally distinct choices before implementation. It must support different lower pad diameters with traceability to an imported footprint, honest uncertainty or assumption sensitivity, an explicit required pad-face gap, and an actionable inconclusive state. Use the existing native solver for actual case geometry. The analytical baseline can screen bounded aligned, lightly loaded assumptions but cannot become a qualified physical interval. Avoid a second general simulation system, material catalog, login or engine port. Preserve existing editable cases through one import migration boundary.

Require acceptance checks that exercise a real 220 versus 270 micrometer comparison, an assumption-induced threshold reversal, rejection of a mask-defined circular boundary falsely treated as a copper rim, stale result clearing, and an export another user can inspect or replay. Prefer a small data shape that owns the decision and assumptions over duplicated policy in browser and service.

Each candidate writes caller usage first, types/signatures/module ownership, proposed minimal changes, acceptance cases, tradeoffs and rejected alternatives. Do not implement production code yet.
