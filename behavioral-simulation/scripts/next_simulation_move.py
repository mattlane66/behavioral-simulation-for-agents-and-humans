#!/usr/bin/env python3
"""Recommend the smallest valid next move for a Behavioral Simulation study."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import GRADE_INDEX, read_json


def recommendation(root: Path) -> str:
    state = read_json(root / "simulation-state.json")
    evidence = read_json(root / "evidence-ledger.json")
    runs = read_json(root / "runs.json")
    validations = read_json(root / "validations.json")
    calibration = read_json(root / "calibration.json")

    if not state.get("scenario_spec", {}).get("accepted"):
        return "FRAME: accept the population, baseline, scenario/intervention, outcome space, and time/context before running."

    target = state.get("target_grade", "L0_ROLEPLAY")
    types = {r.get("evidence_type") for r in evidence.get("entries", []) if isinstance(r, dict)}

    if GRADE_INDEX.get(target, 0) >= 1 and "OBSERVED_HUMAN" not in types:
        return "GROUND: add real person-level human evidence before claiming a person-grounded simulation."

    if GRADE_INDEX.get(target, 0) >= 2 and state.get("population_design", {}).get("status") != "DEFINED":
        return "GROUND: define the target-population sampling/coverage design before making population estimates."

    if state.get("model_config", {}).get("status") != "DEFINED":
        return "SPECIFY: freeze model/version/configuration, primary correctness unit, counterfactual distance, and validation metric."

    if not runs.get("entries"):
        return "RUN: execute and record at least one simulation run with provenance."

    if GRADE_INDEX.get(target, 0) >= 3:
        held = [v for v in validations.get("entries", []) if isinstance(v, dict) and v.get("held_out") is True]
        if not held:
            return "VALIDATE: compare the frozen simulation with relevant held-out real human outcomes."

    if GRADE_INDEX.get(target, 0) >= 4 and calibration.get("status") != "VALID":
        return "CALIBRATE: evaluate predicted error/confidence out of sample against a predeclared decision-quality threshold."

    stress = state.get("stress_tests", {})
    required = ["model_sensitivity", "prompt_config_sensitivity", "subgroup_error", "drift_freshness", "counterfactual_distance"]
    if any(stress.get(k) == "NOT_RUN" for k in required):
        return "STRESS_TEST: run the remaining model/config, subgroup, drift/freshness, and counterfactual-distance checks."

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
