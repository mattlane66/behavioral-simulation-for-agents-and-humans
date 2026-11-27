import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"behavioral-simulation"/"scripts"))
from scarce_evidence import run

def request():
    design={k:True for k in ("same_target_distribution","independent_iid_samples","real_covariate_frame","real_human_labels","frozen_independent_predictor","weight_predeclared")}
    design.update(population="test fixture",estimand="scalar",model_version="fixture",provenance="synthetic test only")
    return dict(operation="rectify_mean",design=design,weight=1,
                unlabeled=[dict(unit_id="u1",prediction=4),dict(unit_id="u2",prediction=6)],
                labeled=[dict(unit_id="h1",prediction=3,human_outcome=1),dict(unit_id="h2",prediction=5,human_outcome=3)])

class ScarceEvidenceTests(unittest.TestCase):
    def test_correct(self):
        r=run(request())
        self.assertAlmostEqual(r["rectified_mean"],3)
        self.assertAlmostEqual(r["human_only_mean"],2)
        self.assertEqual(r["n_human"],2)
        self.assertFalse(r["grade_promotion"])
    def test_human_only(self):
        q=request();q["weight"]=0
        r=run(q)
        self.assertEqual(r["rectified_mean"],r["human_only_mean"])
        self.assertEqual(r["estimated_variance"],r["human_only_estimated_variance"])
    def test_overlap(self):
        q=request();q["unlabeled"][0]["unit_id"]="h1"
        with self.assertRaises(ValueError):run(q)
    def test_duplicate(self):
        q=request();q["unlabeled"][1]["unit_id"]="u1"
        with self.assertRaises(ValueError):run(q)
    def test_no_real_frame(self):
        q=request();q["design"]["real_covariate_frame"]=False
        with self.assertRaises(ValueError):run(q)
    def test_invalid_weight(self):
        q=request();q["weight"]=1.1
        with self.assertRaises(ValueError):run(q)
    def test_nonfinite(self):
        q=request();q["labeled"][0]["human_outcome"]=float("nan")
        with self.assertRaises(ValueError):run(q)
    def test_ssr(self):
        r=run(dict(operation="ssr",vector=[1,0],anchor_vectors=[[-1,0],[0,-1],[0,1],[1,1],[1,0]]))
        self.assertAlmostEqual(sum(r["rating_probabilities"]),1)
        self.assertEqual(r["evidence_type"],"SIMULATED_ESTIMATE")
    def test_variance_mismatch(self):
        r=run(dict(operation="fidelity",paired=[dict(unit_id="a",prediction=2,human_outcome=1),dict(unit_id="b",prediction=2,human_outcome=3)]))
        self.assertEqual(r["human_mean"],r["predicted_mean"])
        self.assertEqual(r["predicted_sample_variance"],0)
        self.assertIsNone(r["pearson"])
        self.assertFalse(r["grade_promotion"])
