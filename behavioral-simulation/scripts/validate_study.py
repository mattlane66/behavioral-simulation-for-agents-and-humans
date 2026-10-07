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
from _schema import validate_file_against_schema

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

SCHEMA_FILES = {
    "input.json": "input.schema.json",
    "simulation-state.json": "simulation-state.schema.json",
    "evidence-ledger.json": "evidence-ledger.schema.json",
    "runs.json": "runs.schema.json",
    "validations.json": "validations.schema.json",
    "calibration.json": "calibration.schema.json",
}


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

    schema_root = Path(__file__).resolve().parents[1] / "schemas"
    for name, schema_name in SCHEMA_FILES.items():
        if name in data:
            errors.extend(validate_file_against_schema(data[name], schema_root / schema_name, name))

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
    if state.get("target_grade") in GRADES and inp.get("target_grade") in GRADES and state.get("target_grade") != inp.get("target_grade"):
        errors.append("target grade drift between input and state")
    if state.get("primary_correctness_unit") not in CORRECTNESS_UNITS:
        errors.append("state invalid primary_correctness_unit")

    eids: set[str] = set()
    evidence_by_id: dict[str, dict[str, Any]] = {}
    observed_human = []
    real_grounding_ids: set[str] = set()
    validation_evidence_ids = set()
    grounding_evidence_ids = set()
    grounding_split_groups: set[tuple[str, str]] = set()
    validation_split_groups: set[tuple[str, str]] = set()
    for i, row in enumerate(evidence.get("entries", []) if isinstance(evidence, dict) else []):
        owner = f"evidence[{i}]"
        eid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(eid, str) or not EID.match(eid) or eid in eids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        eids.add(eid)
        evidence_by_id[eid] = row
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
            if not nonempty(row.get("source")):
                errors.append(f"{owner} OBSERVED_HUMAN requires source")
            if not nonempty(row.get("provenance")):
                errors.append(f"{owner} OBSERVED_HUMAN requires provenance")
            if use in {"GROUNDING","TRAINING"}:
                real_grounding_ids.add(eid)
        split_unit = row.get("split_unit")
        split_group = row.get("split_group")
        if use in {"GROUNDING","TRAINING"}:
            grounding_evidence_ids.add(eid)
            if nonempty(split_group):
                grounding_split_groups.add((str(split_unit or "OTHER"), split_group.strip()))
        if use in {"VALIDATION","CALIBRATION"} and row.get("held_out") is True:
            if not nonempty(split_group):
                errors.append(f"{owner} held-out human evidence requires split_group")
            else:
                validation_split_groups.add((str(split_unit or "OTHER"), split_group.strip()))
        if use == "VALIDATION" and row.get("held_out") is True:
            validation_evidence_ids.add(eid)

    overlap = grounding_evidence_ids & validation_evidence_ids
    if overlap:
        errors.append(f"holdout leakage: evidence used for grounding/training and held-out validation: {sorted(overlap)}")
    split_overlap = grounding_split_groups & validation_split_groups
    if split_overlap:
        errors.append(f"holdout leakage: split groups appear in both grounding/training and held-out validation: {sorted(split_overlap)}")

    rids: set[str] = set()
    for i, row in enumerate(runs.get("entries", []) if isinstance(runs, dict) else []):
        owner = f"runs[{i}]"
        rid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(rid, str) or not RID.match(rid) or rid in rids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        rids.add(rid)
        if row.get("mode") != state.get("mode"):
            errors.append(f"{owner} mode must match study mode")
        if not nonempty(row.get("model")) or not nonempty(row.get("model_version")):
            errors.append(f"{owner} requires model and model_version")
        for eid in row.get("evidence_ids", []):
            if eid not in eids:
                errors.append(f"{owner} references unknown evidence {eid}")
                continue
            source_row = evidence_by_id.get(eid, {})
            if source_row.get("held_out") is True or source_row.get("use") in {"VALIDATION","CALIBRATION"}:
                errors.append(f"{owner} cannot consume held-out validation/calibration evidence {eid}")

    vids: set[str] = set()
    held_validations = []
    for i, row in enumerate(vals.get("entries", []) if isinstance(vals, dict) else []):
        owner = f"validations[{i}]"
        vid = row.get("id") if isinstance(row, dict) else None
        if not isinstance(vid, str) or not VID.match(vid) or vid in vids:
            errors.append(f"{owner} invalid/duplicate id")
            continue
        vids.add(vid)
        run_id = row.get("run_id")
        if run_id not in rids:
            errors.append(f"{owner} references unknown run")
        observed_ids = row.get("observed_evidence_ids", [])
        if not isinstance(observed_ids, list):
            errors.append(f"{owner} observed_evidence_ids must be a list")
            observed_ids = []
        if row.get("held_out") is True and not observed_ids:
            errors.append(f"{owner} held-out validation requires observed_evidence_ids")
        for eid in observed_ids:
            source_row = evidence_by_id.get(eid)
            if source_row is None:
                errors.append(f"{owner} references unknown observed evidence {eid}")
                continue
            if source_row.get("evidence_type") != "OBSERVED_HUMAN":
                errors.append(f"{owner} observed evidence {eid} must be OBSERVED_HUMAN")
            if source_row.get("use") not in {"VALIDATION","CALIBRATION"} or source_row.get("held_out") is not True:
                errors.append(f"{owner} observed evidence {eid} must be held-out validation/calibration evidence")
            v_split_unit = row.get("split_unit")
            e_split_unit = source_row.get("split_unit")
            v_split_group = row.get("split_group")
            e_split_group = source_row.get("split_group")
            if nonempty(v_split_group) and nonempty(e_split_group) and v_split_group != e_split_group:
                errors.append(f"{owner} split_group must match linked observed evidence {eid}")
            if e_split_unit and v_split_unit and e_split_unit != v_split_unit:
                errors.append(f"{owner} split_unit must match linked observed evidence {eid}")
        if row.get("held_out") is True:
            held_validations.append(row)
        if row.get("correctness_unit") == "DISTRIBUTION" and run_id in rids:
            source_run = next((r for r in runs.get("entries", []) if r.get("id") == run_id), None)
            if source_run and isinstance(source_run.get("estimate"), dict) and isinstance(row.get("predicted"), dict):
                run_estimate = {k: float(v) for k, v in source_run["estimate"].items()}
                validation_prediction = {k: float(v) for k, v in row["predicted"].items()}
                if run_estimate != validation_prediction:
                    errors.append(f"{owner} predicted distribution must match referenced run estimate")
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
    target_grade = state.get("target_grade")
    target_gi = GRADE_INDEX.get(target_grade, -1)

    if gi > target_gi >= 0:
        errors.append(f"current_grade {grade} cannot exceed target_grade {target_grade}")

    if gi >= GRADE_INDEX["L1_PERSON_GROUNDED"] and not real_grounding_ids:
        errors.append(f"{grade} requires real OBSERVED_HUMAN grounding/training evidence")

    if gi >= GRADE_INDEX["L2_POPULATION_GROUNDED"]:
        population_design = state.get("population_design", {})
        if population_design.get("status") != "DEFINED":
            errors.append(f"{grade} requires a defined population design")
        if not nonempty(population_design.get("sampling_or_coverage")):
            errors.append(f"{grade} requires population sampling/coverage")
        sample_size = population_design.get("sample_size")
        if not isinstance(sample_size, int) or sample_size <= 0:
            errors.append(f"{grade} requires a positive population sample_size")

    if gi < GRADE_INDEX["L2_POPULATION_GROUNDED"] and state.get("mode") == "POPULATION_PREDICTION":
        if state.get("endpoint") in {"USE_WITH_CAUTION","DECISION_SUPPORT"}:
            errors.append("population prediction below L2 cannot be promoted beyond EXPLORE/TEST_REAL_WORLD")

    if gi >= GRADE_INDEX["L3_HELD_OUT_VALIDATED"]:
        if not held_validations:
            errors.append(f"{grade} requires held-out real-outcome validation")
        primary = state.get("primary_correctness_unit")
        primary_held = [v for v in held_validations if v.get("correctness_unit") == primary]
        if not primary_held:
            errors.append(f"{grade} requires held-out validation for primary correctness unit {primary}")
        validation_state = state.get("validation", {})
        if validation_state.get("status") != "COMPLETE":
            errors.append(f"{grade} requires validation status COMPLETE")
        if validation_state.get("held_out") is not True:
            errors.append(f"{grade} requires validation held_out = true")
        state_validation_ids = validation_state.get("validation_ids", [])
        if not state_validation_ids:
            errors.append(f"{grade} requires validation_ids in state")
        held_vids_now = {v.get("id") for v in held_validations}
        for vid in state_validation_ids:
            if vid not in held_vids_now:
                errors.append(f"{grade} state validation id {vid} must reference a held-out validation")
        if not validation_state.get("metric_predeclared"):
            errors.append(f"{grade} requires predeclared validation metric")
        declared_metric = validation_state.get("metric")
        if not nonempty(declared_metric):
            errors.append(f"{grade} requires the predeclared validation metric name")
        elif primary_held and not any(v.get("metric") == declared_metric for v in primary_held):
            errors.append(f"{grade} requires a primary held-out validation using predeclared metric {declared_metric}")
        if not state.get("model_config", {}).get("frozen_for_validation"):
            errors.append(f"{grade} requires model/config frozen for validation")

    if gi >= GRADE_INDEX["L4_DECISION_CALIBRATED"]:
        state_cal = state.get("calibration", {})
        if not state_cal.get("decision_threshold_predeclared"):
            errors.append("L4 requires a predeclared decision threshold in state")
        if not state_cal.get("predicted_error_evaluated_out_of_sample"):
            errors.append("L4 requires out-of-sample evaluation of predicted error")
        if not state.get("validation", {}).get("subgroup_checked"):
            errors.append("L4 requires subgroup validation checks")
        if state_cal.get("status") != "VALID" or state_cal.get("calibration_file_status") != "VALID":
            errors.append("L4 requires state calibration status and calibration_file_status VALID")
        if cal.get("status") != "VALID":
            errors.append("L4 requires calibration.json status VALID")
        if not nonempty(cal.get("model_scope")):
            errors.append("L4 requires calibration model_scope")
        if not nonempty(cal.get("split_method")):
            errors.append("L4 requires calibration split_method")
        if cal.get("decision_threshold") is None or not nonempty(cal.get("decision_metric")):
            errors.append("L4 requires decision metric and threshold")
        if not cal.get("validation_ids"):
            errors.append("L4 requires calibration validation_ids")
        held_vids = {v.get("id") for v in held_validations}
        for vid in cal.get("validation_ids", []):
            if vid not in vids:
                errors.append(f"calibration references unknown validation {vid}")
            elif vid not in held_vids:
                errors.append(f"calibration validation {vid} must be held out")
        metrics = cal.get("error_prediction_metrics", {})
        if not isinstance(metrics, dict) or not metrics:
            errors.append("L4 requires out-of-sample error-prediction metrics")
        if not cal.get("buckets"):
            errors.append("L4 requires empirically evaluated confidence/error buckets")
        freshness = cal.get("freshness", {})
        if not nonempty(freshness.get("last_validated_at")):
            errors.append("L4 requires calibration last_validated_at")
        if not freshness.get("revalidation_triggers"):
            errors.append("L4 requires revalidation triggers")
        if freshness.get("drift_status") not in {"OK","MONITOR","STALE"}:
            errors.append("L4 requires explicit drift_status")
        if freshness.get("drift_status") == "STALE":
            errors.append("L4 calibration is stale")

    if state.get("primary_correctness_unit") == "PLAUSIBILITY_ONLY" and gi >= GRADE_INDEX["L3_HELD_OUT_VALIDATED"]:
        errors.append("plausibility/believability alone cannot establish L3/L4 predictive validity")

    if rids and state.get("scenario_spec", {}).get("accepted") is not True:
        errors.append("recorded runs require an accepted scenario specification")
    if rids and state.get("model_config", {}).get("status") != "DEFINED":
        errors.append("recorded runs require defined model_config in state")

    if grade == "L0_ROLEPLAY" and state.get("endpoint") in {"USE_WITH_CAUTION","DECISION_SUPPORT"}:
        errors.append("L0_ROLEPLAY cannot be promoted beyond EXPLORE/TEST_REAL_WORLD/DO_NOT_USE")
    if state.get("endpoint") == "DECISION_SUPPORT" and grade != "L4_DECISION_CALIBRATED":
        errors.append("DECISION_SUPPORT endpoint requires L4_DECISION_CALIBRATED")

    if state.get("phase") == "COMPLETE" and state.get("status") != "COMPLETE":
        errors.append("COMPLETE phase requires status COMPLETE")
    if state.get("status") == "COMPLETE" and state.get("phase") != "COMPLETE":
        errors.append("status COMPLETE requires phase COMPLETE")
    if state.get("phase") == "COMPLETE" and state.get("endpoint") == "UNSET":
        errors.append("COMPLETE study requires a final endpoint")

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
