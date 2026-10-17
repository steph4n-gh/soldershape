"""Verify the pre-lab evidence without executing archived code or native scripts."""

import gzip
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prelab.campaign import accepted, read, sha, verify as verify_campaign
from prelab.replay import validate_fresh
from prelab.rigid_cap import build_report

EVIDENCE = ROOT / "prelab/evidence"


def baseline_check():
    fresh = read(EVIDENCE / "baseline/plan.json")
    archived = read(ROOT / "coupons/evidence/planning/plan.json")
    rows = []
    for left, right in zip(fresh["caps"], archived["caps"], strict=True):
        if left["cap_id"] != right["cap_id"]:
            raise ValueError("Baseline arm changed.")
        for a, b in zip(left["models"], right["models"], strict=True):
            if (a["request"], a["mapping"], a["gravity"]) != (b["request"], b["mapping"], b["gravity"]):
                raise ValueError("Fresh baseline request differs from historical input.")
            with gzip.open(EVIDENCE / "baseline" / a["receipt"], "rt") as stream:
                result = json.load(stream)
            validate_fresh({**result, "producer_engine": result["engine"]}, a["request"], a["request_sha256"],
                           read(EVIDENCE / "campaign/manifest.json")["engine"])
            if not accepted(result):
                raise ValueError("Fresh baseline request failed numerical gates.")
            correction = 70 if a["mapping"] == "two_pad_cylinders" else 0
            gap = result["equilibrium"]["standoff_mm"] * 1000 - correction
            difference = gap - b["predicted_pad_face_gap_um"]
            if abs(difference) > .001 or abs(gap - a["predicted_pad_face_gap_um"]) > 1e-10:
                raise ValueError("Fresh baseline value differs from archived prediction.")
            rows.append({"arm": left["cap_id"], "mapping": a["mapping"], "gravity": a["gravity"], "gap_difference_um": difference})
    if len(rows) != 6 or sum(row["gravity"] for row in rows) != 2:
        raise ValueError("All six baseline cases, including two real-liquid gravity controls, are required.")
    return rows


def replay_check():
    campaign = EVIDENCE / "campaign"
    directory = EVIDENCE / "replay-final"
    report = read(directory / "report.json")
    manifest = read(campaign / "manifest.json")
    table = read(campaign / "plan.json")
    if (report["replay_code_sha256"] != sha((ROOT / "prelab/replay.py").read_bytes())
            or report["campaign_manifest_sha256"] != sha((campaign / "manifest.json").read_bytes())
            or report["source_sha256"] != manifest["source_sha256"] or report["engine"] != manifest["engine"]):
        raise ValueError("Replay source identity differs.")
    expected = {row["request_sha256"] for row in table["rows"] if row["scenario"] in
                ("nominal", "opposed-requested-endpoints", "opposed-wider-volume")}
    expected.add(table["negative_control"])
    if {row["request_sha256"] for row in report["requests"]} != expected or len(report["requests"]) != len(expected):
        raise ValueError("Replay case accounting differs.")
    if set(report["receipt_sha256"]) != {key + ".json.gz" for key in expected}:
        raise ValueError("Replay receipt inventory differs.")
    for row in report["requests"]:
        key = row["request_sha256"]
        path = directory / (key + ".json.gz")
        if sha(path.read_bytes()) != report["receipt_sha256"][path.name]:
            raise ValueError("Replay receipt hash differs.")
        with gzip.open(path, "rt") as stream:
            fresh = json.load(stream)
        with gzip.open(campaign / "receipts" / path.name, "rt") as stream:
            original = json.load(stream)
        validate_fresh(fresh, table["jobs"][key], key, manifest["engine"])
        if accepted(original):
            if not accepted(fresh):
                raise ValueError("Accepted replay case failed.")
            gap = 1000 * (fresh["equilibrium"]["standoff_mm"] - original["equilibrium"]["standoff_mm"])
            forces = {axis: fresh["forces"][axis] - original["forces"][axis] for axis in ("x_uN", "z_uN")}
            if (gap != row["gap_difference_um"] or forces != row["force_difference_uN"]
                    or abs(gap) > .01 or max(map(abs, forces.values())) > .01):
                raise ValueError("Replay numerical comparison differs.")
        elif accepted(fresh) or not row["expected_rejection"]:
            raise ValueError("Failed control was omitted or relabeled.")
        if not row["passed"]:
            raise ValueError("Replay row did not pass its numerical check.")
    return len(expected)


def archive_metadata(archive, inventory):
    if sha(archive.read_bytes()) != inventory["archive_sha256"]:
        raise ValueError("Finite-pad archive hash differs.")
    metadata, seen = {}, set()
    with tarfile.open(archive, mode="r|gz") as files:
        for item in files:
            name = item.name
            if (name in seen or name not in inventory["files"] or not item.isfile()
                    or Path(name).is_absolute() or ".." in Path(name).parts):
                raise ValueError("Finite-pad archive has an unexpected or unsafe member.")
            seen.add(name)
            stream = files.extractfile(item)
            if name in ("summary.json", "report.json", "PROJECT-LICENSE.txt") or name.endswith("/result.json") or name.startswith("adapter-snapshots/"):
                content = stream.read()
                digest = sha(content)
                metadata[name] = content
            else:
                digest = hashlib.file_digest(stream, "sha256").hexdigest()
            if digest != inventory["files"][name]:
                raise ValueError("Finite-pad member hash differs: " + name)
    if seen != set(inventory["files"]):
        raise ValueError("Finite-pad archive is missing members.")
    if metadata.get("PROJECT-LICENSE.txt") != (ROOT / "LICENSE").read_bytes():
        raise ValueError("Source-containing evidence archive lacks the exact project notice.")
    return metadata


def finite_check():
    inventory = read(EVIDENCE / "finite-manifest.json")
    metadata = archive_metadata(EVIDENCE / "finite-pilot.tar.gz", inventory)
    summary = read(EVIDENCE / "finite-summary.json")
    if metadata["summary.json"] != (EVIDENCE / "finite-summary.json").read_bytes():
        raise ValueError("Finite-pad summary is not the archived original.")
    for attempt in summary["attempts"]:
        content = metadata[attempt["result"]]
        if sha(content) != attempt["result_sha256"]:
            raise ValueError("A failed or successful finite-pad attempt changed.")
        if sha(metadata[attempt["adapter_snapshot"]]) != attempt["adapter_sha256"]:
            raise ValueError("Finite-pad adapter snapshot differs.")
        result = json.loads(content)
        if any(result.get(key) != attempt.get(key) for key in
               ("status", "physical_eligibility", "accepted_face_gap_mm")):
            raise ValueError("Finite-pad attempt summary differs from its result.")
    for row in summary["fresh_relaxed_energy_checks"]:
        reactions = []
        for step in (.0005, .00025):
            pair = []
            for direction in ("minus", "plus"):
                name = f"{row['source']}/levels3-step{step:.9f}-{direction}/result.json"
                value = json.loads(metadata[name])
                if not value["physical_eligibility"] or not value["numeric_gates_passed"]:
                    raise ValueError("Energy-check geometry failed eligibility.")
                pair.append(value)
            reactions.extend(-50*(b["energy_erg"]-a["energy_erg"])/step
                             for a, b in zip(pair[0]["levels"][-2:], pair[1]["levels"][-2:], strict=True))
        residual = max(abs(value-row["target_uN"]) for value in reactions)
        spread = max(reactions)-min(reactions)
        if (abs(residual-row["maximum_load_residual_uN"]) > 1e-9
                or abs(spread-row["spread_uN"]) > 1e-9):
            raise ValueError("Finite energy derivatives do not reproduce summary.")
    control = json.loads(metadata["v5-penetrating-control-fixed/result.json"])
    if (control["physical_eligibility"] or not control["interface"]["intrusion_detected"]
            or not control["interface"]["active_new_contact"] or control["status"] != "not_converged"):
        raise ValueError("The failed penetrating control was relabeled.")
    if summary["attempted_isolated_jobs"] != len(summary["attempts"]):
        raise ValueError("Finite-pad attempt accounting differs.")
    if not all(row["passed"] and row["maximum_load_residual_uN"] < .01 for row in summary["fresh_relaxed_energy_checks"]):
        raise ValueError("Nominal fixed-wetting energy checks did not pass.")
    return {"retained_isolated_attempts": len(summary["attempts"]),
            "full_wetting_maximum_load_residual_uN": max(row["maximum_load_residual_uN"] for row in summary["fresh_relaxed_energy_checks"]),
            "active_contact_qualified": False, "continuous_clearance_certified": False}


def finite_confirmation_check():
    inventory = read(EVIDENCE / "finite-confirmation.tar.gz.manifest.json")
    metadata = archive_metadata(EVIDENCE / "finite-confirmation.tar.gz", inventory)
    report = json.loads(metadata["report.json"])
    for name, digest in report["source_sha256"].items():
        if sha((ROOT / name).read_bytes()) != digest:
            raise ValueError("Finite confirmation source differs.")
    expected = read(ROOT / "prelab/finite-controls.json")["jobs"]
    if set(report["centers"]) != set(expected):
        raise ValueError("Finite confirmation controls differ.")
    for name, row in report["centers"].items():
        result = json.loads(metadata[name + "/result.json"])
        if row != {key: result.get(key) for key in row}:
            raise ValueError("Finite confirmation result differs from its summary.")
        if "penetrating" not in name and (not row["physical_eligibility"] or not row["numeric_gates_passed"]):
            raise ValueError("Nominal finite confirmation failed.")
        if "penetrating" in name and row["physical_eligibility"]:
            raise ValueError("Penetrating finite confirmation was accepted.")
    for arm, result in report["energy_checks"].items():
        if result["status"] != "reaction_checked" or result["maximum_load_residual_uN"] >= .01:
            raise ValueError("Finite confirmation energy check failed.")
        for check in result["checks"]:
            step = check["delta_mm"]
            pair = [json.loads(metadata[f"{arm}-energy/levels3-step{step:.9f}-{direction}/result.json"])
                    for direction in ("minus", "plus")]
            reaction = -50*(pair[1]["energy_erg"]-pair[0]["energy_erg"])/step
            if abs(reaction-check["reaction_uN"]) > 1e-9:
                raise ValueError("Finite confirmation reaction differs from raw energies.")
    return {"fixed_controls": len(expected), "relaxed_energy_checks": len(report["energy_checks"]), "passed": True}


def verify_all():
    campaign = verify_campaign(EVIDENCE / "campaign")
    baseline = baseline_check()
    replayed = replay_check()
    rigid = build_report()
    if rigid != read(EVIDENCE / "rigid-cap.json"):
        raise ValueError("Rigid-cap values differ from recomputed mechanics.")
    finite = finite_check()
    confirmation = finite_confirmation_check()
    return {"passed": True, "campaign": campaign, "fresh_baseline_cases": len(baseline),
            "verification_code_sha256": sha(Path(__file__).read_bytes()),
            "baseline_maximum_gap_difference_um": max(abs(row["gap_difference_um"]) for row in baseline),
            "identity_checked_fresh_replays": replayed, "rigid_cap_cases": rigid["analytical_cap_cases"],
            "finite_pad": finite, "finite_confirmation": confirmation, "physical_qualification": "unqualified",
            "scope": "File integrity, trusted-source recomputation and numerical evidence. Not a trusted timestamp or physical validation."}


if __name__ == "__main__":
    print(json.dumps(verify_all(), indent=2))
