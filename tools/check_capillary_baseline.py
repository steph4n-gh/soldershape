"""Compare an independent axisymmetric area/volume discretization with native forces.

Research only. Requires NumPy and SciPy. Equal pinned circular rims, zero offset,
fixed volume, no gravity. Native forces do not enter the independent minimization.
"""

import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from soldershape.model import JointSpec
from soldershape.solver import solve


def axisymmetric(radius, height, volume, segments):
    scaled_height = height/radius
    target = volume/radius**3
    spacing = 1/segments

    def components(interior):
        radii = np.r_[1, interior, 1]
        lower, upper = radii[:-1], radii[1:]
        difference = upper-lower
        length = np.sqrt((scaled_height*spacing)**2+difference**2)
        area = np.pi*np.sum((lower+upper)*length)
        enclosed = np.pi*scaled_height*spacing*np.sum(lower*lower+lower*upper+upper*upper)/3
        area_gradient = np.pi*((length+(lower+upper)*difference/length)[:-1]
                               +(length-(lower+upper)*difference/length)[1:])
        volume_gradient = np.pi*scaled_height*spacing*((lower+2*upper)[:-1]+(2*lower+upper)[1:])/3
        return area, enclosed, area_gradient, volume_gradient, radii, length

    start = np.ones(segments-1)*math.sqrt(target/(math.pi*scaled_height))
    result = minimize(lambda x: components(x)[0], start,
                      jac=lambda x: components(x)[2],
                      constraints=[{"type": "eq", "fun": lambda x: components(x)[1]-target,
                                    "jac": lambda x: components(x)[3]}],
                      bounds=[(.01, None)]*(segments-1), method="SLSQP",
                      options={"ftol": 1e-12, "maxiter": 1000})
    area, enclosed, area_gradient, volume_gradient, radii, length = components(result.x)
    multiplier = float(area_gradient@volume_gradient/(volume_gradient@volume_gradient))
    area_height_derivative = np.pi*np.sum((radii[:-1]+radii[1:])*scaled_height*spacing*spacing/length)
    force = -radius*(area_height_derivative-multiplier*enclosed/scaled_height)*1000
    return {"segments": segments, "success": bool(result.success), "message": result.message,
            "force_z_uN_at_gamma1": float(force), "normalized_volume_error": float(abs(enclosed/target-1)),
            "normalized_stationarity": float(np.linalg.norm(area_gradient-multiplier*volume_gradient)),
            "area_mm2": float(area*radius*radius),
            "radii_extent_mm": [float(min(radii)*radius), float(max(radii)*radius)]}


def main():
    results = []
    for name, radius, height, volume in (("thin", .32, .0351, .01181699087727595), ("ordinary", .1, .15, .006)):
        rows = [axisymmetric(radius, height, volume, count) for count in (24, 48, 96)]
        spec = JointSpec(radius*2, radius*2, height, volume, 0, 1, 9, False)
        native = solve(spec)
        difference = abs(rows[-1]["force_z_uN_at_gamma1"]/native["forces"]["z_uN"]-1)
        passed = (native["status"] == "refinement_checked" and difference < .001
                  and all(row["success"] and row["normalized_volume_error"] < 1e-8
                          and row["normalized_stationarity"] < .001 for row in rows))
        results.append({"case": name, "spec": spec.to_dict(), "independent": rows,
                        "native": {key: native[key] for key in ("status", "forces", "diagnostics")},
                        "relative_force_difference": difference, "relative_force_threshold": .001, "passed": passed})
        print(name, "relative force difference", difference, "passed", passed, flush=True)
    (ROOT / "evidence/model-repair/axisymmetric.json").write_text(json.dumps(results, indent=2)+"\n")
    return 0 if all(row["passed"] for row in results) else 1


if __name__ == "__main__":
    sys.exit(main())
