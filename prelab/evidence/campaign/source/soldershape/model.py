"""Validated millimeter inputs and KiCad footprint geometry."""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import re

PYTHON_SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class InputError(ValueError):
    pass


@dataclass(frozen=True)
class JointSpec:
    lower_diameter_mm: float
    upper_diameter_mm: float
    standoff_mm: float
    volume_mm3: float
    offset_mm: float
    surface_tension_n_m: float = 0.48
    density_g_cm3: float = 9.0
    gravity: bool = True

    def __post_init__(self):
        limits = {
            "lower_diameter_mm": (0.05, 10.0),
            "upper_diameter_mm": (0.05, 10.0),
            "standoff_mm": (0.02, 10.0),
            "volume_mm3": (0.000001, 1000.0),
            "offset_mm": (-5.0, 5.0),
            "surface_tension_n_m": (0.01, 2.0),
            "density_g_cm3": (0.1, 25.0),
        }
        for name, (low, high) in limits.items():
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise InputError(f"{name} must be a finite number.")
            if not low <= value <= high:
                raise InputError(f"{name} must be between {low} and {high}.")
        if not isinstance(self.gravity, bool):
            raise InputError("gravity must be true or false.")

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise InputError("Joint parameters must be an object.")
        allowed = set(cls.__dataclass_fields__)
        if set(data) - allowed:
            raise InputError("Unknown joint parameters: " + ", ".join(sorted(set(data) - allowed)))
        try:
            return cls(**data)
        except TypeError as error:
            raise InputError("Missing required joint parameters.") from error

    def to_dict(self):
        return asdict(self)

    @property
    def sha256(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class LoadSpec:
    lower_diameter_mm: float
    upper_diameter_mm: float
    volume_mm3: float
    offset_mm: float
    normal_load_uN: float
    surface_tension_n_m: float = 0.48
    density_g_cm3: float = 9.0
    gravity: bool = True

    def __post_init__(self):
        self.at_gap(1.0)
        load = self.normal_load_uN
        if isinstance(load, bool) or not isinstance(load, (int, float)) or not math.isfinite(load):
            raise InputError("normal_load_uN must be a finite number.")
        if not 0 <= load <= 100000:
            raise InputError("normal_load_uN must be between 0 and 100000.")

    def at_gap(self, standoff_mm):
        return JointSpec(self.lower_diameter_mm, self.upper_diameter_mm, standoff_mm,
                         self.volume_mm3, self.offset_mm, self.surface_tension_n_m,
                         self.density_g_cm3, self.gravity)

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict):
            raise InputError("Joint parameters must be an object.")
        if set(data) - set(cls.__dataclass_fields__):
            raise InputError("Unknown loaded joint parameters: " + ", ".join(sorted(set(data) - set(cls.__dataclass_fields__))))
        try:
            return cls(**data)
        except TypeError as error:
            raise InputError("Missing required loaded joint parameters.") from error

    def to_dict(self):
        return asdict(self)

    @property
    def sha256(self):
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def joint_spec_from_dict(data):
    if not isinstance(data, dict):
        raise InputError("Joint parameters must be an object.")
    if "standoff_mm" in data and "normal_load_uN" in data:
        raise InputError("Specify a wetted-plane gap or a normal load, not both.")
    return LoadSpec.from_dict(data) if "normal_load_uN" in data else JointSpec.from_dict(data)


def spherical_gap_mm(lower_diameter_mm, upper_diameter_mm, volume_mm3):
    values = (lower_diameter_mm, upper_diameter_mm, volume_mm3)
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0 for value in values):
        raise InputError("Spherical seed dimensions and volume must be finite and positive.")
    a, b = lower_diameter_mm/2, upper_diameter_mm/2
    low, high = 0.0, (6*volume_mm3/math.pi)**(1/3)
    for _ in range(80):
        height = (low + high)/2
        volume = math.pi*height*(a*a+b*b)/2 + math.pi*height**3/6
        if volume < volume_mm3:
            low = height
        else:
            high = height
    return (low + high)/2


def _number(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise InputError(f"Invalid {name} in footprint.") from error
    if not math.isfinite(result) or abs(result) > 100000:
        raise InputError(f"Invalid {name} in footprint.")
    return result


def _sexpr(source):
    token = re.compile(r'\s+|\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+')
    stack = [[]]
    end = 0
    count = 0
    for match in token.finditer(source):
        if match.start() != end:
            raise InputError("Malformed KiCad quoted string.")
        end = match.end()
        part = match.group()
        if part.isspace():
            continue
        count += 1
        if count > 150000:
            raise InputError("Footprint has too many tokens.")
        if part == "(":
            if len(stack) > 80:
                raise InputError("Footprint nesting is too deep.")
            child = []
            stack[-1].append(child)
            stack.append(child)
        elif part == ")":
            if len(stack) == 1:
                raise InputError("Unbalanced KiCad parentheses.")
            stack.pop()
        else:
            if part.startswith('"'):
                part = re.sub(r'\\(.)', r'\1', part[1:-1])
            stack[-1].append(part)
    if end != len(source) or len(stack) != 1 or len(stack[0]) != 1:
        raise InputError("Expected one complete KiCad footprint.")
    root = stack[0][0]
    if not isinstance(root, list) or len(root) < 2 or not isinstance(root[1], str) or root[0] not in ("footprint", "module"):
        raise InputError("Import a .kicad_mod footprint, not a complete PCB.")
    return root


def import_footprint(source):
    if not isinstance(source, str) or not source.strip():
        raise InputError("Choose a KiCad footprint file.")
    encoded = source.encode("utf-8")
    if len(encoded) > 2_000_000:
        raise InputError("Footprints are limited to 2 MB.")
    root = _sexpr(source)
    mask_settings = [item[1:] for item in root[2:] if isinstance(item, list) and item and item[0] == "solder_mask_margin"]
    if len(mask_settings) > 1 or mask_settings and len(mask_settings[0]) != 1:
        raise InputError("Malformed footprint solder mask margin.")
    footprint_mask = _number(mask_settings[0][0], "solder mask margin") if mask_settings else 0
    pads = []
    for item in root[2:]:
        if not isinstance(item, list) or not item or item[0] != "pad":
            continue
        if len(item) < 4 or any(not isinstance(value, str) for value in item[:4]):
            raise InputError("Malformed pad record.")
        attrs = {}
        for child in item[4:]:
            if isinstance(child, list) and child:
                if child[0] in attrs:
                    raise InputError("Duplicate pad geometry attribute.")
                attrs[child[0]] = child[1:]
        size, at = attrs.get("size"), attrs.get("at", ["0", "0"])
        if not size or len(size) != 2 or len(at) not in (2, 3):
            raise InputError("Pad size and position are required.")
        sx, sy = (_number(v, "pad size") for v in size)
        x, y = (_number(v, "pad position") for v in at[:2])
        if sx <= 0 or sy <= 0:
            raise InputError("Pad dimensions must be positive.")
        reason = None
        if item[2] != "smd" or item[3] != "circle" or abs(sx - sy) > 1e-9:
            reason = "Only circular SMD pads are supported by this model."
        elif not all(isinstance(layer, str) for layer in attrs.get("layers", [])):
            raise InputError("Malformed pad layers.")
        elif not set(attrs.get("layers", [])) & {"F.Cu", "B.Cu", "*.Cu"}:
            reason = "Select a copper pad."
        mask_margin = attrs.get("solder_mask_margin", [0])
        if len(mask_margin) != 1:
            raise InputError("Malformed pad solder mask margin.")
        declared_mask = _number(mask_margin[0], "solder mask margin") or footprint_mask
        if declared_mask < 0:
            reason = "The declared solder mask opening is smaller than the copper pad. This copper-rim model cannot solve that boundary."
        pads.append({"index": len(pads), "identifier": item[1], "x_mm": x, "y_mm": y,
                     "angle_deg": _number(at[2], "pad rotation") if len(at) == 3 else 0,
                     "shape": item[3], "size_mm": [sx, sy], "supported": reason is None,
                     "declared_mask_margin_mm": declared_mask if declared_mask != 0 else None,
                     "mask_scope": "Board-level mask settings, drawn mask geometry and final CAM are not resolved by a footprint import.",
                     "unsupported_reason": reason})
        if len(pads) > 4096:
            raise InputError("Footprints are limited to 4096 pads.")
    if not pads:
        raise InputError("The footprint contains no pads.")
    return {"name": str(root[1]), "sha256": hashlib.sha256(encoded).hexdigest(), "pads": pads}


def request_from_footprint(source, pad_index, parameters):
    footprint = import_footprint(source)
    if isinstance(pad_index, bool) or not isinstance(pad_index, int) or not 0 <= pad_index < len(footprint["pads"]):
        raise InputError("Select a valid pad.")
    pad = footprint["pads"][pad_index]
    if not pad["supported"]:
        raise InputError(pad["unsupported_reason"])
    if not isinstance(parameters, dict) or "lower_diameter_mm" in parameters:
        raise InputError("The board-pad diameter comes from the selected footprint pad.")
    spec = joint_spec_from_dict({**parameters, "lower_diameter_mm": pad["size_mm"][0]})
    return spec, {"name": footprint["name"], "sha256": footprint["sha256"], "pad": pad}


def parse_case(data):
    if not isinstance(data, dict) or set(data) != {"schema", "footprint_text", "pad_index", "parameters", "baseline"}:
        raise InputError("A case must contain schema, footprint_text, pad_index, parameters and baseline.")
    if data["schema"] != "soldershape.case.v1":
        raise InputError("Unsupported editable case format.")
    spec, _ = request_from_footprint(data["footprint_text"], data["pad_index"], data["parameters"])
    parameters = spec.to_dict()
    del parameters["lower_diameter_mm"]
    baseline = data["baseline"]
    if baseline is not None:
        if not isinstance(baseline, dict) or set(baseline) != {"upper_diameter_mm", "volume_mm3"}:
            raise InputError("A reference design contains only upper_diameter_mm and volume_mm3.")
        reference, _ = request_from_footprint(data["footprint_text"], data["pad_index"], {**parameters, **baseline})
        baseline = {key: getattr(reference, key) for key in ("upper_diameter_mm", "volume_mm3")}
    return {"schema": data["schema"], "footprint_text": data["footprint_text"], "pad_index": data["pad_index"],
            "parameters": parameters, "baseline": baseline}
