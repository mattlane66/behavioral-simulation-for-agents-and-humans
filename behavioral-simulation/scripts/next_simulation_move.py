#!/usr/bin/env python3
"""Recommend the smallest valid next move for a Behavioral Simulation study."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import GRADE_INDEX, read_json


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def recommendation(root: Path) -> str:
    state = read_json(root / "simulation-state.json")
    evidence = read_json(root / "evidence-ledger.json")
    runs = read_json(root / "runs.json")
    validations = read_json(root / "validations.json")
    calibration = read_json(root / "calibration.json")

    if not state.get("scenario_spec", {}).get("accepted"):
        return "FRAME: accept the population, baseline, scenario/intervention, outcome space, and time/context before running."

    target = state.get("target_grade", "L0_ROLEPLAY")
    target_i = GRADE_INDEX.get(target, 0)
    current = state.get("current_grade", "L0_ROLEPLAY")

    rows = [r for r in evidence.get("entries", []) if isinstance(r, dict)]
    real_grounding = [
        r for r in rows
        if r.get("evidence_type") == "OBSERVED_HUMAN"
        and r.get("use") in {"GROUNDING", "TRAINING"}
    ]

    if target_i >= GRADE_INDEX["L1_PERSON_GROUNDED"] and not real_grounding:
        return "GROUND: add real OBSERVED_HUMAN evidence used for GROUNDING or TRAINING; context-only human data does not establish L1+."

    population_mode = state.get("mode") in {"POPULATION_PREDICTION", "MULTI_AGENT_DYNAMICS"}
    if target_i >= GRADE_INDEX["L2_POPULATION_GROUNDED"] and population_mode:
        population = state.get("population_design", {})
        if population.get("status") != "DEFINED":
            return "GROUND: define the target-population design before making population or system estimates."
        if not nonempty(population.get("sampling_or_coverage")):
            return "GROUND: record how the target population is sampled or covered before claiming population-grounded evidence."
        if not isinstance(population.get("sample_size"), int) or population.get("sample_size") <= 0:
            return "GROUND: record a positive population sample_size before claiming population-grounded evidence."

    if state.get("model_config", {}).get("status") != "DEFINED":
        return "SPECIFY: freeze model/version/configuration, primary correctness unit, counterfactual distance, and validation metric."

    if not runs.get("entries"):
        return "RUN: execute and record at least one simulation run with provenance."

    if target_i >= GRADE_INDEX["L3_HELD_OUT_VALIDATED"]:
        primary = state.get("primary_correctness_unit")
        held = [
            v for v in validations.get("entries", [])
            if isinstance(v, dict)
            and v.get("held_out") is True
            and v.get("correctness_unit") == primary
            and isinstance(v.get("observed_evidence_ids"), list)
            and len(v.get("observed_evidence_ids")) > 0
        ]
        validation_state = state.get("validation", {})
        if not held:
            return "VALIDATE: compare the frozen simulation with linked held-out real human outcomes for the primary correctness unit."
        if validation_state.get("status") != "COMPLETE" or validation_state.get("held_out") is not True:
            return "VALIDATE: mark validation COMPLETE only after the held-out comparison is finished and recorded."
        if not validation_state.get("metric_predeclared") or not nonempty(validation_state.get("metric")):
            return "VALIDATE: record the predeclared validation metric before using the held-out result."
        if not validation_state.get("validation_ids"):
            return "VALIDATE: link the authoritative held-out validation IDs into simulation-state.json."

    if target_i >= GRADE_INDEX["L4_DECISION_CALIBRATED"]:
        state_cal = state.get("calibration", {})
        freshness = calibration.get("freshness", {})
        if (
            calibration.get("status") != "VALID"
            or state_cal.get("status") != "VALID"
            or state_cal.get("calibration_file_status") != "VALID"
            or not state_cal.get("decision_threshold_predeclared")
            or not state_cal.get("predicted_error_evaluated_out_of_sample")
            or (population_mode and not state.get("validation", {}).get("subgroup_checked"))
            or not nonempty(calibration.get("model_scope"))
            or not nonempty(calibration.get("split_method"))
            or calibration.get("decision_threshold") is None
            or not nonempty(calibration.get("decision_metric"))
            or not calibration.get("validation_ids")
            or not calibration.get("error_prediction_metrics")
            or not calibration.get("buckets")
            or not nonempty(freshness.get("last_validated_at"))
            or freshness.get("drift_status") not in {"OK", "MONITOR"}
            or not freshness.get("revalidation_triggers")
        ):
            return "CALIBRATE: complete out-of-sample error prediction, decision thresholding, subgroup checks, model scope, confidence buckets, and freshness/drift controls before claiming L4."

    if current != target:
        return f"GRADE: evidence appears ready for {target}; set current_grade to {target} and run validate_study.py. If validation fails, repair rather than promoting."

    stress = state.get("stress_tests", {})
    required = ["model_sensitivity", "prompt_config_sensitivity", "counterfactual_distance"]
    if population_mode and target_i >= GRADE_INDEX["L2_POPULATION_GROUNDED"]:
        required.extend(["subgroup_error", "drift_freshness"])
    elif target_i >= GRADE_INDEX["L4_DECISION_CALIBRATED"]:
        required.append("drift_freshness")
    if state.get("mode") == "MULTI_AGENT_DYNAMICS":
        required.append("multi_agent_failures")
    if any(stress.get(k) == "NOT_RUN" for k in required):
        return "STRESS_TEST: run the remaining decision-relevant model/config, subgroup, drift/freshness, counterfactual-distance, or multi-agent failure checks."

    if state.get("endpoint") == "UNSET":
        return "DELIVER: write the simulation report with supported/unsupported claims and the highest-value real-world validation next."

    return "COMPLETE: no structural next move detected; revisit only if the decision, model, data, scenario, or freshness status changes."


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workspace")
    args = p.parse_args()
    print(recommendation(Path(args.workspace)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
