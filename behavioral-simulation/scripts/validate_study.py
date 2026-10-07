#!/usr/bin/env python3
"""Validate hard epistemic contracts for a Behavioral Simulation workspace."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

from _common import (
    CORRECTNESS_UNITS,
    EVIDENCE_TYPES,
    GRADE_INDEX,
    GRADES,
    MODES,
    PHASES,
    SCHEMA_VERSION,
    read_json,
)
from calculate_metrics import compute

EID = re.compile(r"^E[0-9]{3,}$")
RID = re.compile(r"^R[0-9]{3,}$")
VID = re.compile(r"^V[0-9]{3,}$")

REQUIRED_FILES = [
    "input.json",
    "simulation-state.json",
    "evidence-ledger.json",
    "runs.json",
    "validations.json",
    "calibration.json",
]


def nonempty(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def load_workspace(root: Path, errors: list[str]) -> dict[str, Any]:
    out = {}
    for name in REQUIRED_FILES:
        path = root / name
        if not path.exists():
            errors.append(f"missing {name}")
            continue
        try:
            out[name] = read_json(path)
        except Exception as exc:
            errors.append(f"{name} is not valid JSON: {exc}")
    return out


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    inp = data.get("input.json", {})
    state = data.get("simulation-state.json", {})
    evidence = data.get("evidence-ledger.json", {})
    runs = data.get("runs.json", {})
    vals = data.get("validations.json", {})
    cal = data.get("calibration.json", {})

    for name, doc in data.items():
        if isinstance(doc, dict) and doc.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{name} schema_version must be {SCHEMA_VERSION}")

    for field in ["decision", "population", "scenario", "outcome_space"]:
        if not nonempty(inp.get(field)):
            errors.append(f"input.json requires {field}")
    if inp.get("mode") not in MODES:
        errors.append("input.json invalid mode")
    if inp.get("target_grade") not in GRADES:
        errors.append("input.json invalid target_grade")

    if state.get("phase") not in PHASES:
        errors.append("simulation-state invalid phase")
    if state.get("mode") not in MODES or state.get("mode") != inp.get("mode"):
        errors.append("mode drift between input and state")
    if state.get("current_grade") not in GRADES or state.get("target_grade") not in GRADES:
        errors.append("state invalid evidence grade")
    if state.get("primary_correctness_unit") not in CORRECTNESS_UNITS:
        errors.append("state invalid primary_correctness_unit")

    eids: set[str] = set()
    observed_human = []
    validation_evidence_ids = set()
    grounding_evidence_ids = set()
    for i, row in enumerate(evidence.get("entries", []) if isinstance(evidence, dict) else []):
        owner = f"evidence[{i}]"
        eid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(eid, str) or not EID.match(eid) or eid in eids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        eids.add(eid)
        et = row.get("evidence_type")
        if et not in EVIDENCE_TYPES:
            errors.append(f"{owner} invalid evidence_type")
        use = row.get("use")
        if use not in {"GROUNDING","TRAINING","VALIDATION","CALIBRATION","CONTEXT","SCENARIO"}:
            errors.append(f"{owner} invalid use")
        if row.get("held_out") is True and use not in {"VALIDATION","CALIBRATION"}:
            errors.append(f"{owner} held_out evidence must be validation/calibration use")
        if et == "SIMULATED_ESTIMATE" and use in {"GROUNDING","TRAINING"} and state.get("current_grade") != "L0_ROLEPLAY":
            errors.append(f"{owner} synthetic output cannot substitute for real grounding at graded levels")
        if et == "OBSERVED_HUMAN":
            observed_human.append(row)
        if use in {"GROUNDING","TRAINING"}:
            grounding_evidence_ids.add(eid)
        if use == "VALIDATION" and row.get("held_out") is True:
            validation_evidence_ids.add(eid)

    overlap = grounding_evidence_ids & validation_evidence_ids
    if overlap:
        errors.append(f"holdout leakage: evidence used for grounding/training and held-out validation: {sorted(overlap)}")

    rids: set[str] = set()
    for i, row in enumerate(runs.get("entries", []) if isinstance(runs, dict) else []):
        owner = f"runs[{i}]"
        rid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(rid, str) or not RID.match(rid) or rid in rids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        rids.add(rid)
        if not nonempty(row.get("model")) or not nonempty(row.get("model_version")):
            errors.append(f"{owner} requires model and model_version")
        for eid in row.get("evidence_ids", []):
            if eid not in eids:
                errors.append(f"{owner} references unknown evidence {eid}")

    vids: set[str] = set()
    held_validations = []
    for i, row in enumerate(vals.get("entries", []) if isinstance(vals, dict) else []):
        owner = f"validations[{i}]"
        vid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(vid, str) or not VID.match(vid) or vid in vids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        vids.add(vid)
        if row.get("run_id") not in rids:
            errors.append(f"{owner} references unknown run")
        if row.get("held_out") is True:
            held_validations.append(row)
        try:
            expected = compute(row)
            actual = row.get("computed_error")
            if expected is not None:
                if actual is None or not math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-9):
                    errors.append(f"{owner} metric drift: recompute {row.get('metric')}")
        except Exception as exc:
            errors.append(f"{owner} metric invalid: {exc}")

    grade = state.get("current_grade")
    gi = GRADE_INDEX.get(grade, -1)

    if gi >= GRADE_INDEX["L1_PERSON_GROUNDED"] and not observed_human:
        errors.append(f"{grade} requires real OBSERVED_HUMAN grounding")

    if gi >= GRADE_INDEX["L2_POPULATION_GROUNDED"]:
        if state.get("population_design", {}).get("status") != "DEFINED":
            errors.append(f"{grade} requires a defined population design")

    if gi < GRADE_INDEX["L2_POPULATION_GROUNDED"] and state.get("mode") == "POPULATION_PREDICTION":
        if state.get("endpoint") in {"USE_WITH_CAUTION","DECISION_SUPPORT"}:
            errors.append("population prediction below L2 cannot be promoted beyond EXPLORE/TEST_REAL_WORLD")

    if gi >= GRADE_INDEX["L3_HELD_OUT_VALIDATED"]:
        if not held_validations:
            errors.append(f"{grade} requires held-out real-outcome validation")
        if not state.get("validation", {}).get("metric_predeclared"):
            errors.append(f"{grade} requires predeclared validation metric")
        if not state.get("model_config", {}).get("frozen_for_validation"):
            errors.append(f"{grade} requires model/config frozen for validation")

    if gi >= GRADE_INDEX["L4_DECISION_CALIBRATED"]:
        if cal.get("status") != "VALID":
            errors.append("L4 requires calibration.json status VALID")
        if cal.get("decision_threshold") is None or not nonempty(cal.get("decision_metric")):
            errors.append("L4 requires decision metric and threshold")
        if not cal.get("validation_ids"):
            errors.append("L4 requires calibration validation_ids")
        for vid in cal.get("validation_ids", []):
            if vid not in vids:
                errors.append(f"calibration references unknown validation {vid}")
        metrics = cal.get("error_prediction_metrics", {})
        if not isinstance(metrics, dict) or not metrics:
            errors.append("L4 requires out-of-sample error-prediction metrics")
        if not cal.get("buckets"):
            errors.append("L4 requires empirically evaluated confidence/error buckets")
        freshness = cal.get("freshness", {})
        if freshness.get("drift_status") not in {"OK","MONITOR","STALE"}:
            errors.append("L4 requires explicit drift_status")
        if freshness.get("drift_status") == "STALE":
            errors.append("L4 calibration is stale")

    if state.get("primary_correctness_unit") == "PLAUSIBILITY_ONLY" and gi >= GRADE_INDEX["L3_HELD_OUT_VALIDATED"]:
        errors.append("plausibility/believability alone cannot establish L3/L4 predictive validity")

    if rids and state.get("model_config", {}).get("status") != "DEFINED":
        errors.append("recorded runs require defined model_config in state")

    if state.get("endpoint") == "DECISION_SUPPORT" and grade != "L4_DECISION_CALIBRATED":
        errors.append("DECISION_SUPPORT endpoint requires L4_DECISION_CALIBRATED")

    if state.get("mode") == "MULTI_AGENT_DYNAMICS" and rids:
        if state.get("stress_tests", {}).get("multi_agent_failures") == "NOT_RUN" and state.get("endpoint") in {"USE_WITH_CAUTION","DECISION_SUPPORT"}:
            errors.append("multi-agent predictive use requires explicit failure-mode stress testing")

    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workspace")
    args = p.parse_args()
    root = Path(args.workspace)
    errors: list[str] = []
    data = load_workspace(root, errors)
    errors.extend(validate(data))
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
