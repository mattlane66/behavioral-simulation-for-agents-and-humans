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


    def make_valid_l3_workspace(self) -> Path:
        root = self.make_workspace(mode="POPULATION_PREDICTION", target="L3_HELD_OUT_VALIDATED")
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        state["current_grade"] = "L3_HELD_OUT_VALIDATED"
        state["population_design"].update({
            "status": "DEFINED",
            "sampling_or_coverage": "Observed target-population study with a held-out question group",
            "sample_size": 200,
            "geography": "US",
            "time_period": "2026",
        })
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
            "metric": "TVD",
            "held_out": True,
            "split_unit": "QUESTION",
            "validation_ids": ["V001"],
        })
        self.write(root, "simulation-state.json", state)

        ev = self.read(root, "evidence-ledger.json")
        ev["entries"] = [
            {
                "id": "E001", "evidence_type": "OBSERVED_HUMAN",
                "claim": "Training responses", "source": "train.csv",
                "provenance": "study-1 training partition", "use": "TRAINING",
                "held_out": False, "population_scope": "target users",
                "time_scope": "2026", "notes": "", "split_unit": "QUESTION",
                "split_group": "train",
            },
            {
                "id": "E002", "evidence_type": "OBSERVED_HUMAN",
                "claim": "Held-out responses", "source": "holdout.csv",
                "provenance": "study-1 held-out partition", "use": "VALIDATION",
                "held_out": True, "population_scope": "target users",
                "time_scope": "2026", "notes": "", "split_unit": "QUESTION",
                "split_group": "q-holdout",
            },
        ]
        self.write(root, "evidence-ledger.json", ev)

        runs = self.read(root, "runs.json")
        runs["entries"] = [{
            "id": "R001", "ran_at": "2026-10-07",
            "mode": "POPULATION_PREDICTION", "model": "sim",
            "model_version": "1", "configuration": "fixed", "seed": 1,
            "sample_size": 100, "evidence_ids": ["E001"],
            "estimate": {"A": 0.7, "B": 0.3}, "notes": "",
        }]
        self.write(root, "runs.json", runs)

        vals = self.read(root, "validations.json")
        vals["entries"] = [{
            "id": "V001", "run_id": "R001", "correctness_unit": "DISTRIBUTION",
            "metric": "TVD", "predicted": {"A": 0.7, "B": 0.3},
            "observed": {"A": 0.6, "B": 0.4},
            "observed_evidence_ids": ["E002"], "computed_error": 0.1,
            "held_out": True, "split_unit": "QUESTION", "split_group": "q-holdout",
            "population_match": "MATCH", "time_match": "MATCH",
            "subgroup": None, "notes": "",
        }]
        self.write(root, "validations.json", vals)
        return root

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


    def test_valid_l3_population_study_passes(self):
        root = self.make_valid_l3_workspace()
        p = run("validate_study.py", str(root))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_l2_requires_human_grounding_not_context(self):
        root = self.make_workspace(target="L2_POPULATION_GROUNDED")
        state = self.read(root, "simulation-state.json")
        state["current_grade"] = "L2_POPULATION_GROUNDED"
        state["population_design"].update({
            "status": "DEFINED",
            "sampling_or_coverage": "Target-population sample",
            "sample_size": 100,
        })
        self.write(root, "simulation-state.json", state)
        ev = self.read(root, "evidence-ledger.json")
        ev["entries"].append({
            "id": "E001", "evidence_type": "OBSERVED_HUMAN",
            "claim": "Background fact", "source": "context.csv",
            "provenance": "context only", "use": "CONTEXT", "held_out": False,
            "population_scope": "target users", "time_scope": "2026", "notes": "",
        })
        self.write(root, "evidence-ledger.json", ev)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("grounding/training", p.stdout)

    def test_l3_requires_link_to_observed_holdout_evidence(self):
        root = self.make_valid_l3_workspace()
        vals = self.read(root, "validations.json")
        vals["entries"][0]["observed_evidence_ids"] = []
        self.write(root, "validations.json", vals)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("observed_evidence_ids", p.stdout)

    def test_l3_rejects_split_group_leakage_across_different_ids(self):
        root = self.make_valid_l3_workspace()
        ev = self.read(root, "evidence-ledger.json")
        ev["entries"][1]["split_group"] = "train"
        self.write(root, "evidence-ledger.json", ev)
        vals = self.read(root, "validations.json")
        vals["entries"][0]["split_group"] = "train"
        self.write(root, "validations.json", vals)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("split groups", p.stdout)

    def test_run_mode_must_match_study_mode(self):
        root = self.make_workspace(mode="PLAUSIBILITY_SPACE")
        state = self.read(root, "simulation-state.json")
        state["scenario_spec"]["accepted"] = True
        state["model_config"].update({
            "status": "DEFINED", "provider": "test", "model": "m",
            "version": "1", "configuration": "", "frozen_for_validation": False,
        })
        self.write(root, "simulation-state.json", state)
        runs = self.read(root, "runs.json")
        runs["entries"].append({
            "id": "R001", "ran_at": "2026-10-07",
            "mode": "POPULATION_PREDICTION", "model": "m", "model_version": "1",
            "configuration": "", "seed": 1, "sample_size": 10,
            "evidence_ids": [], "estimate": {}, "notes": "",
        })
        self.write(root, "runs.json", runs)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("mode must match", p.stdout)

    def test_current_grade_cannot_exceed_requested_target(self):
        root = self.make_workspace(mode="INDIVIDUAL_PROXY", target="L0_ROLEPLAY")
        state = self.read(root, "simulation-state.json")
        state["current_grade"] = "L1_PERSON_GROUNDED"
        self.write(root, "simulation-state.json", state)
        ev = self.read(root, "evidence-ledger.json")
        ev["entries"].append({
            "id": "E001", "evidence_type": "OBSERVED_HUMAN",
            "claim": "Interview", "source": "interview.txt",
            "provenance": "participant interview", "use": "GROUNDING",
            "held_out": False, "population_scope": "one participant",
            "time_scope": "2026", "notes": "", "split_unit": "PERSON",
            "split_group": "p1",
        })
        self.write(root, "evidence-ledger.json", ev)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("cannot exceed target_grade", p.stdout)

    def test_l3_requires_validation_of_primary_correctness_unit(self):
        root = self.make_valid_l3_workspace()
        vals = self.read(root, "validations.json")
        vals["entries"][0]["correctness_unit"] = "TREATMENT_EFFECT"
        self.write(root, "validations.json", vals)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("primary correctness unit", p.stdout)

    def test_l3_requires_named_predeclared_metric(self):
        root = self.make_valid_l3_workspace()
        state = self.read(root, "simulation-state.json")
        state["validation"]["metric"] = None
        self.write(root, "simulation-state.json", state)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("predeclared validation metric name", p.stdout)

    def test_l4_requires_out_of_sample_error_prediction(self):
        root = self.make_valid_l3_workspace()
        inp = self.read(root, "input.json")
        inp["target_grade"] = "L4_DECISION_CALIBRATED"
        self.write(root, "input.json", inp)
        state = self.read(root, "simulation-state.json")
        state["target_grade"] = "L4_DECISION_CALIBRATED"
        state["current_grade"] = "L4_DECISION_CALIBRATED"
        state["validation"]["subgroup_checked"] = True
        state["calibration"]["decision_threshold_predeclared"] = True
        state["calibration"]["predicted_error_evaluated_out_of_sample"] = False
        self.write(root, "simulation-state.json", state)
        cal = self.read(root, "calibration.json")
        cal.update({
            "status": "VALID", "model_scope": "test model v1",
            "decision_metric": "TVD", "decision_threshold": 0.16,
            "validation_ids": ["V001"], "split_method": "5-fold grouped CV",
            "error_prediction_metrics": {"rmse": 0.08},
            "buckets": [{"name": "high", "empirical_pass_rate": 0.95}],
        })
        cal["freshness"]["drift_status"] = "OK"
        self.write(root, "calibration.json", cal)
        p = run("validate_study.py", str(root))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("out-of-sample evaluation", p.stdout)



if __name__ == "__main__":
    unittest.main()
