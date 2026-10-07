#!/usr/bin/env python3
"""Initialize a Behavioral Simulation study workspace."""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import GRADES, MODES, SCHEMA_VERSION, empty_ledgers, make_state, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", required=True)
    p.add_argument("--decision", required=True)
    p.add_argument("--population", required=True)
    p.add_argument("--baseline", default="")
    p.add_argument("--scenario", required=True)
    p.add_argument("--outcome", required=True)
    p.add_argument("--mode", choices=sorted(MODES), required=True)
    p.add_argument("--target-grade", choices=GRADES, default="L0_ROLEPLAY")
    p.add_argument("--time-context", default="")
    p.add_argument("--consequence-if-wrong", default="")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.workspace)
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"Refusing to initialize non-empty workspace: {root}")
    root.mkdir(parents=True, exist_ok=True)
    (root / "outputs").mkdir(exist_ok=True)

    input_data = {
        "schema_version": SCHEMA_VERSION,
        "decision": args.decision,
        "population": args.population,
        "baseline": args.baseline,
        "scenario": args.scenario,
        "outcome_space": args.outcome,
        "mode": args.mode,
        "target_grade": args.target_grade,
        "time_context": args.time_context,
        "consequence_if_wrong": args.consequence_if_wrong,
        "input_provenance": {
            "decision": "USER_SUPPLIED",
            "population": "USER_SUPPLIED",
            "baseline": "USER_SUPPLIED" if args.baseline else "EXPLICITLY_PROVISIONAL",
            "scenario": "USER_SUPPLIED",
            "outcome_space": "USER_SUPPLIED",
            "mode": "USER_SUPPLIED",
            "target_grade": "USER_SUPPLIED",
            "time_context": "USER_SUPPLIED" if args.time_context else "EXPLICITLY_PROVISIONAL",
            "consequence_if_wrong": "USER_SUPPLIED" if args.consequence_if_wrong else "EXPLICITLY_PROVISIONAL",
        },
    }
    write_json(root / "input.json", input_data)
    write_json(
        root / "simulation-state.json",
        make_state(
            args.mode,
            args.target_grade,
            population=args.population,
            baseline=args.baseline,
            scenario=args.scenario,
            outcome_space=args.outcome,
            time_context=args.time_context,
        ),
    )
    for name, value in empty_ledgers().items():
        write_json(root / name, value)
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
