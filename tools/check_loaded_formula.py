"""Compare retained aligned predictions with Van Veen et al. 2004 Eq. 9.

The loaded spring correction is evaluated independently of native forces.
Source: https://imapsjmep.org/article/39820.pdf, printed page 58.
"""

import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.model import spherical_gap_mm


def main():
    campaign = json.loads((ROOT / "evidence/model-repair/loaded-physical-results.json").read_text())
    rows = []
    for row in campaign["rows"]:
        if row["mapping"] != "published" or row["input"]["offset_mm"] != 0 or row["input"]["gravity"]:
            continue
        spec = row["input"]
        p, q = spec["upper_diameter_mm"]/2, spec["lower_diameter_mm"]/2
        height = spherical_gap_mm(2*q, 2*p, spec["volume_mm3"])
        j = (height*height+p*p+q*q)/(p*p+q*q)
        u = p*q/(p*p+q*q)
        stiffness = spec["surface_tension_n_m"]*(4*math.pi/5)*j*(j*(j+4)+10*u*u)/(j*j-4*u*u)**1.5
        predicted = 1000*(height-.034)-spec["normal_load_uN"]/stiffness
        rows.append({"id": row["id"], "scenario": row["scenario"], "gamma_N_m": spec["surface_tension_n_m"],
                     "stiffness_N_m": stiffness, "analytical_rim_um": predicted,
                     "native_rim_um": row["predicted_rim_um"], "measured_rim_um": row["measured_rim_um"],
                     "native_minus_analytical_um": row["predicted_rim_um"]-predicted})
    nominal = [row for row in rows if row["scenario"] == "primary" and row["gamma_N_m"] == .48]
    assert len(nominal) == 4, "All four nominal physical rows are required."
    report = {"source": "https://imapsjmep.org/article/39820.pdf", "equation": 9,
              "scope": "Aligned small-load spring approximation, same paper copper-volume mapping. Not process qualification.",
              "nominal_mean_absolute_error_um": sum(abs(row["analytical_rim_um"]-row["measured_rim_um"]) for row in nominal)/4,
              "nominal_max_native_difference_um": max(abs(row["native_minus_analytical_um"]) for row in nominal), "rows": rows}
    (ROOT / "evidence/model-repair/loaded-formula.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
