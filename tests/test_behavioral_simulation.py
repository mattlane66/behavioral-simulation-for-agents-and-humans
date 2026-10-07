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


class BehavioralSimulationTests(unittest.TestCase):
    def make_workspace(self, mode="POPULATION_PREDICTION", target="L0_ROLEPLAY") -> Path:
        tmp = Path(tempfile.mkdtemp())
        p = run(
            "init_study.py",
            "--workspace", str(tmp / "study"),
            "--decision", "Choose which concept to test",
            "--population", "Target users",
            "--baseline", "Current experience",
            "--scenario", "Concept A",
            "--outcome", "Choose A/B/neither",
            "--mode", mode,
            "--target-grade", target,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        return tmp / "study"

    def read(self, root: Path, name: str):
        return json.loads((root / name).read_text())

    def write(self, root: Path, name: str, value):
        (root / name).write_text(json.dumps(value, indent=2) + "\n")

    def test_initializer_is_valid_at_l0(self):
        root = self.make_workspace(mode="PLAUSIBILITY_SPACE")
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        self.write(root, "simulation-state.json", state)
        p = run("validate_study.py", str(root))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_tvd_is_recomputed(self):
        root = self.make_workspace()
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        state["model_config"].update({"status":"DEFINED","provider":"x","model":"m","version":"1","configuration":"","frozen_for_validation":False})
        self.write(root, "simulation-state.json", state)
        runs = self.read(root, "runs.json")
        runs["entries"].append({
            "id":"R001","ran_at":"2026-10-07","mode":"POPULATION_PREDICTION",
            "model":"m","model_version":"1","configuration":"","seed":1,"sample_size":100,
            "evidence_ids":[],"estimate":{"A":0.7,"B":0.3},"notes":""
        })
        self.write(root, "runs.json", runs)
        vals = self.read(root, "validations.json")
        vals["entries"].append({
            "id":"V001","run_id":"R001","correctness_unit":"DISTRIBUTION","metric":"TVD",
            "predicted":{"A":0.7,"B":0.3},"observed":{"A":0.6,"B":0.4},
            "computed_error":None,"held_out":True,"split_unit":"QUESTION","split_group":"q1",
            "population_match":"MATCH","time_match":"MATCH","subgroup":None,"notes":""
        })
        self.write(root, "validations.json", vals)
        p = run("calculate_metrics.py", str(root))
        self.assertEqual(p.returncode, 0, p.stderr)
        vals = self.read(root, "validations.json")
        self.assertAlmostEqual(vals["entries"][0]["computed_error"], 0.1)

    def test_l3_requires_human_grounding_and_holdout(self):
        root = self.make_workspace(target="L3_HELD_OUT_VALIDATED")
        state = self.read(root, "simulation-state.json")
        state["current_grade"] = "L3_HELD_OUT_VALIDATED"
        state["population_design"]["status"] = "DEFINED"
        state["model_config"].update({"status":"DEFINED","provider":"x","model":"m","version":"1","configuration":"","frozen_for_validation":True})
        state["validation"]["metric_predeclared"] = True
        self.write(root, "simulation-state.json", state)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("OBSERVED_HUMAN", p.stdout)
        self.assertIn("held-out", p.stdout)

    def test_decision_support_requires_l4(self):
        root = self.make_workspace()
        state = self.read(root, "simulation-state.json")
        state["endpoint"] = "DECISION_SUPPORT"
        self.write(root, "simulation-state.json", state)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("DECISION_SUPPORT", p.stdout)

    def test_synthetic_cannot_be_human_grounding(self):
        root = self.make_workspace(mode="INDIVIDUAL_PROXY", target="L1_PERSON_GROUNDED")
        state = self.read(root, "simulation-state.json")
        state["current_grade"] = "L1_PERSON_GROUNDED"
        self.write(root, "simulation-state.json", state)
        ev = self.read(root, "evidence-ledger.json")
        ev["entries"].append({
            "id":"E001","evidence_type":"SIMULATED_ESTIMATE","claim":"Generated persona",
            "source":None,"provenance":"model","use":"GROUNDING","held_out":False,
            "population_scope":"one synthetic persona","time_scope":"","notes":""
        })
        self.write(root, "evidence-ledger.json", ev)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("synthetic output cannot substitute", p.stdout)


if __name__ == "__main__":
    unittest.main()
