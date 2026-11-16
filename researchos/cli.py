"""Dependency-free experiment validation, evidence capture and toy model runner."""
import argparse
import hashlib
import json
import math
import platform
import re
import sys
from pathlib import Path


class ValidationError(ValueError):
    pass


def read_json(path):
    def reject(value):
        raise ValidationError(f"non-finite JSON constant: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def number(value, name, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValidationError(f"{name} must be a finite number")
    if positive and value <= 0:
        raise ValidationError(f"{name} must be positive")
    return value


def validate(record):
    if not isinstance(record, dict):
        raise ValidationError("record must be an object")
    required = {"schema_version", "id", "title", "hypothesis", "owner", "data_kind", "application", "model", "evidence"}
    if required - record.keys():
        raise ValidationError(f"missing fields: {sorted(required - record.keys())}")
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        raise ValidationError("schema_version must be 1")
    if not isinstance(record["id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", record["id"]):
        raise ValidationError("id must be a safe lowercase identifier of at most 80 characters")
    for key in ("title", "hypothesis", "owner"):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValidationError(f"{key} must be a nonempty string")
    if record["data_kind"] not in ("synthetic", "simulation", "experimental"):
        raise ValidationError("invalid data_kind")
    if record["application"] not in ("qubits", "photon-detectors", "signal-processing"):
        raise ValidationError("invalid application")
    model = record["model"]
    if not isinstance(model, dict) or model.get("name") != "bcs-gap-toy-v1":
        raise ValidationError("supported model: bcs-gap-toy-v1")
    for key in ("critical_temperature_K", "baseline_critical_temperature_K"):
        number(model.get(key), key, positive=True)
    temps = model.get("temperatures_K")
    if not isinstance(temps, list) or not temps or len(temps) > 10000:
        raise ValidationError("temperatures_K must contain 1 to 10000 values")
    for temp in temps:
        if number(temp, "temperature") < 0:
            raise ValidationError("temperature must be nonnegative")
    if not isinstance(record["evidence"], list):
        raise ValidationError("evidence must be a list")
    paths = set()
    for item in record["evidence"]:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not item["path"]:
            raise ValidationError("evidence requires a nonempty path")
        if item["path"] in paths:
            raise ValidationError("duplicate evidence path")
        paths.add(item["path"])
        if not isinstance(item.get("sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", item["sha256"]):
            raise ValidationError("evidence requires a lowercase sha256 digest")
    if record["data_kind"] == "experimental" and not record["evidence"]:
        raise ValidationError("experimental records require evidence")
    return record


def digest(data):
    return hashlib.sha256(data).hexdigest()


def evidence_bytes(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root):
        raise ValidationError("evidence must remain inside the record directory")
    return path.read_bytes()


def verify_evidence(record, root):
    for item in record["evidence"]:
        if digest(evidence_bytes(root, item["path"])) != item["sha256"]:
            raise ValidationError(f"evidence checksum mismatch: {item['path']}")


def gap_meV(temp, tc):
    """Weak-coupling BCS interpolation; no metamaterial predictive validity."""
    zero = 1.764 * 0.08617333262 * tc
    if temp == 0:
        return zero
    if temp >= tc:
        return 0.0
    return zero * math.tanh(1.74 * math.sqrt(tc / temp - 1))


def run(path, output):
    path = Path(path)
    raw = path.read_bytes()
    record = validate(read_json(path))
    verify_evidence(record, path.parent)
    model = record["model"]
    tc = model["critical_temperature_K"]
    baseline = model["baseline_critical_temperature_K"]
    rows = [{"temperature_K": t, "candidate_gap_meV": gap_meV(t, tc),
             "baseline_gap_meV": gap_meV(t, baseline)} for t in model["temperatures_K"]]
    if any(not math.isfinite(v) for row in rows for v in row.values()):
        raise ValidationError("model produced a non-finite result")
    result = {"experiment": record, "input_sha256": digest(raw),
              "python_version": platform.python_version(), "runner_version": "0.1.0",
              "model_output_kind": "synthetic-illustration", "results": rows,
              "limitations": "Toy weak-coupling BCS interpolation. Assumed Tc values are inputs, not predictions. No device performance, metamaterial enhancement, or experimental validation is established."}
    # Exclusive creation prevents accidental replacement of previous evidence bundles.
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    return result


def report(bundle):
    record = validate(bundle["experiment"])
    lines = [f"# {record['id']}", "", record["title"], "",
             f"Input data kind: {record['data_kind']}",
             "Model output: synthetic illustration", "", bundle["limitations"], "",
             f"Input SHA-256: `{bundle['input_sha256']}`", "",
             "| Temperature (K) | Candidate gap (meV) | Baseline gap (meV) |",
             "| --- | --- | --- |"]
    for row in bundle["results"]:
        lines.append(f"| {row['temperature_K']:g} | {row['candidate_gap_meV']:.6g} | {row['baseline_gap_meV']:.6g} |")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ("validate", "run", "hash", "report"):
        p = sub.add_parser(cmd)
        p.add_argument("path", type=Path)
        if cmd == "run":
            p.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            print(digest(args.path.read_bytes()))
        elif args.command == "validate":
            verify_evidence(validate(read_json(args.path)), args.path.parent)
            print("Valid record; declared evidence checksums verified.")
        elif args.command == "run":
            run(args.path, args.output)
            print(f"Created {args.output}")
        else:
            print(report(read_json(args.path)), end="")
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0
