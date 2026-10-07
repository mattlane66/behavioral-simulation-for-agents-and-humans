"""Shared helpers for Behavioral Simulation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"

MODES = {
    "PLAUSIBILITY_SPACE",
    "INDIVIDUAL_PROXY",
    "POPULATION_PREDICTION",
    "MULTI_AGENT_DYNAMICS",
}

GRADES = [
    "L0_ROLEPLAY",
    "L1_PERSON_GROUNDED",
    "L2_POPULATION_GROUNDED",
    "L3_HELD_OUT_VALIDATED",
    "L4_DECISION_CALIBRATED",
]

GRADE_INDEX = {g: i for i, g in enumerate(GRADES)}

EVIDENCE_TYPES = {
    "OBSERVED_HUMAN",
    "NONHUMAN_CONTEXT",
    "ASSUMPTION",
    "SIMULATED_ESTIMATE",
    "CALIBRATION_EVIDENCE",
}

CORRECTNESS_UNITS = {
    "PLAUSIBILITY_ONLY",
    "INDIVIDUAL",
    "DISTRIBUTION",
    "TREATMENT_EFFECT",
    "SYSTEM_TRAJECTORY",
}

PHASES = [
    "FRAME",
    "GROUND",
    "SPECIFY",
    "RUN",
    "VALIDATE",
    "CALIBRATE",
    "STRESS_TEST",
    "DELIVER",
    "COMPLETE",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def make_state(mode: str, target_grade: str, *, population: str, baseline: str, scenario: str, outcome_space: str, time_context: str) -> dict[str, Any]:
    primary = {
        "PLAUSIBILITY_SPACE": "PLAUSIBILITY_ONLY",
        "INDIVIDUAL_PROXY": "INDIVIDUAL",
        "POPULATION_PREDICTION": "DISTRIBUTION",
        "MULTI_AGENT_DYNAMICS": "SYSTEM_TRAJECTORY",
    }[mode]

    return {
        "schema_version": SCHEMA_VERSION,
        "phase": "FRAME",
        "status": "ACTIVE",
        "mode": mode,
        "target_grade": target_grade,
        "current_grade": "L0_ROLEPLAY",
        "primary_correctness_unit": primary,
        "scenario_spec": {
            "population": population,
            "baseline": baseline,
            "scenario": scenario,
            "outcome_space": outcome_space,
            "time_context": time_context,
            "accepted": False,
        },
        "population_design": {
            "status": "UNASSESSED",
            "sampling_or_coverage": "",
            "sample_size": None,
            "geography": "",
            "time_period": "",
            "inclusions": [],
            "exclusions": [],
            "weighting": "",
            "limitations": [],
        },
        "model_config": {
            "status": "UNSET",
            "provider": "",
            "model": "",
            "version": "",
            "configuration": "",
            "frozen_for_validation": False,
        },
        "counterfactual_distance": "UNKNOWN",
        "validation": {
            "status": "NOT_ATTEMPTED",
            "metric_predeclared": False,
            "metric": None,
            "held_out": False,
            "split_unit": None,
            "validation_ids": [],
            "baseline": "",
            "subgroup_checked": False,
        },
        "calibration": {
            "status": "NOT_ATTEMPTED",
            "decision_threshold_predeclared": False,
            "predicted_error_evaluated_out_of_sample": False,
            "calibration_file_status": "NOT_ATTEMPTED",
        },
        "stress_tests": {
            "model_sensitivity": "NOT_RUN",
            "prompt_config_sensitivity": "NOT_RUN",
            "subgroup_error": "NOT_RUN",
            "drift_freshness": "NOT_RUN",
            "counterfactual_distance": "NOT_RUN",
            "multi_agent_failures": "NOT_APPLICABLE" if mode != "MULTI_AGENT_DYNAMICS" else "NOT_RUN",
        },
        "endpoint": "UNSET",
        "next_real_world_test": {
            "status": "UNSET",
            "test": "",
            "resolves": "",
            "decision_condition": "",
        },
        "notes": [],
    }


def empty_ledgers() -> dict[str, Any]:
    return {
        "evidence-ledger.json": {"schema_version": SCHEMA_VERSION, "entries": []},
        "runs.json": {"schema_version": SCHEMA_VERSION, "entries": []},
        "validations.json": {"schema_version": SCHEMA_VERSION, "entries": []},
        "calibration.json": {
            "schema_version": SCHEMA_VERSION,
            "status": "NOT_ATTEMPTED",
            "model_scope": "",
            "decision_metric": None,
            "decision_threshold": None,
            "validation_ids": [],
            "split_method": "",
            "error_prediction_metrics": {},
            "buckets": [],
            "freshness": {
                "data_period": "",
                "last_validated_at": "",
                "expires_at": "",
                "drift_status": "UNKNOWN",
                "revalidation_triggers": [],
            },
            "notes": [],
        },
    }
