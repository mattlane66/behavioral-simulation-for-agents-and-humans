from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "behavioral-simulation" / "scripts"


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class ModeAwareGradeTests(unittest.TestCase):
    def make_workspace(self, target: str) -> Path:
        tmp = Path(tempfile.mkdtemp())
        root = tmp / "study"
        p = run(
            "init_study.py",
            "--workspace", str(root),
            "--decision", "Choose a concept",
            "--population", "Participant P1",
            "--baseline", "Current experience",
            "--scenario", "Concept A",
            "--outcome", "A/B choice",
            "--mode", "INDIVIDUAL_PROXY",
            "--target-grade", target,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        return root

    def read(self, root: Path, name: str):
        return json.loads((root / name).read_text())

    def write(self, root: Path, name: str, value):
        (root / name).write_text(json.dumps(value, indent=2) + "\n")

    def test_l3_individual_proxy_does_not_require_population_design(self):
        root = self.make_workspace("L3_HELD_OUT_VALIDATED")
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        state["current_grade"] = "L3_HELD_OUT_VALIDATED"
        state["model_config"].update({
            "status": "DEFINED",
            "provider": "test",
            "model": "sim",
            "version": "1",
            "configuration": "fixed",
            "frozen_for_validation": True,
        })
        state["validation"].update({
            "status": "COMPLETE",
            "metric_predeclared": True,
            "metric": "ACCURACY",
            "held_out": True,
            "split_unit": "QUESTION",
            "validation_ids": ["V001"],
        })
        state["endpoint"] = "USE_WITH_CAUTION"
        self.write(root, "simulation-state.json", state)

        evidence = self.read(root, "evidence-ledger.json")
        evidence["entries"] = [
            {
                "id": "E001",
                "evidence_type": "OBSERVED_HUMAN",
                "claim": "Interview grounding",
                "source": "interview.txt",
                "provenance": "P1 interview",
                "use": "GROUNDING",
                "held_out": False,
                "population_scope": "P1",
                "time_scope": "2026",
                "notes": "",
                "split_unit": "QUESTION",
                "split_group": "grounding",
            },
            {
                "id": "E002",
                "evidence_type": "OBSERVED_HUMAN",
                "claim": "Held-out responses",
                "source": "holdout.csv",
                "provenance": "P1 held-out response battery",
                "use": "VALIDATION",
                "held_out": True,
                "population_scope": "P1",
                "time_scope": "2026",
                "notes": "",
                "split_unit": "QUESTION",
                "split_group": "heldout",
            },
        ]
        self.write(root, "evidence-ledger.json", evidence)

        runs = self.read(root, "runs.json")
        runs["entries"] = [{
            "id": "R001",
            "ran_at": "2026-10-07",
            "mode": "INDIVIDUAL_PROXY",
            "model": "sim",
            "model_version": "1",
            "configuration": "fixed",
            "seed": 1,
            "sample_size": 1,
            "evidence_ids": ["E001"],
            "estimate": {"prediction": "A"},
            "notes": "",
        }]
        self.write(root, "runs.json", runs)

        validations = self.read(root, "validations.json")
        validations["entries"] = [{
            "id": "V001",
            "run_id": "R001",
            "correctness_unit": "INDIVIDUAL",
            "metric": "ACCURACY",
            "predicted": ["A", "B", "A"],
            "observed": ["A", "B", "B"],
            "observed_evidence_ids": ["E002"],
            "computed_error": 0.3333333333,
            "held_out": True,
            "split_unit": "QUESTION",
            "split_group": "heldout",
            "population_match": "MATCH",
            "time_match": "MATCH",
            "subgroup": None,
            "notes": "",
        }]
        self.write(root, "validations.json", validations)

        p = run("validate_study.py", str(root))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_router_skips_population_gate_for_l3_individual_proxy(self):
        root = self.make_workspace("L3_HELD_OUT_VALIDATED")
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        self.write(root, "simulation-state.json", state)
        evidence = self.read(root, "evidence-ledger.json")
        evidence["entries"] = [{
            "id": "E001",
            "evidence_type": "OBSERVED_HUMAN",
            "claim": "Interview grounding",
            "source": "interview.txt",
            "provenance": "P1 interview",
            "use": "GROUNDING",
            "held_out": False,
            "population_scope": "P1",
            "time_scope": "2026",
            "notes": "",
            "split_unit": "QUESTION",
            "split_group": "grounding",
        }]
        self.write(root, "evidence-ledger.json", evidence)
        p = run("next_simulation_move.py", str(root))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("SPECIFY:", p.stdout)


if __name__ == "__main__":
    unittest.main()
