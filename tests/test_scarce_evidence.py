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
    def test_independent_pilot_weight_matches_scalar_derivation(self):
        q = request()
        del q["weight"]
        q["design"].update(independent_tuning_sample_same_target=True,
                           tuning_provenance="fixture only")
        q["tuning"] = [dict(unit_id="t1", prediction=1, human_outcome=3),
                       dict(unit_id="t2", prediction=3, human_outcome=5)]
        result = run(q)
        self.assertEqual(result["weight_selection"], "INDEPENDENT_PILOT")
        self.assertEqual(result["estimate_basis"], "MODEL_ASSISTED_STATISTICAL_ESTIMATE")
        self.assertAlmostEqual(result["weight"], 0.5)
        self.assertAlmostEqual(result["rectified_mean"], 2.5)
        self.assertAlmostEqual(result["estimated_variance"], 0.5)
        q["tuning"][0]["unit_id"] = "h1"
        with self.assertRaisesRegex(ValueError, "Tuning and inference"):
            run(q)
        q["tuning"][0]["unit_id"] = "t1"
        q["tuning"][0]["prediction"] = q["tuning"][1]["prediction"]
        self.assertEqual(run(q)["weight"], 0)
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
        self.assertEqual(r["transform"], "LEGACY_UNIFORM_EPSILON")
    def test_variance_mismatch(self):
        r=run(dict(operation="fidelity",paired=[dict(unit_id="a",prediction=2,human_outcome=1),dict(unit_id="b",prediction=2,human_outcome=3)]))
        self.assertEqual(r["human_mean"],r["predicted_mean"])
        self.assertEqual(r["predicted_sample_variance"],0)
        self.assertEqual(r["spread_ratio"], 0)
        self.assertEqual(r["absolute_standardized_mean_gap"], 0)
        self.assertIsNone(r["pearson"])
        self.assertEqual(r["validation_status"],"NOT_ASSESSED")
        self.assertNotIn("evidence_type",r)
        self.assertFalse(r["grade_promotion"])

    def test_ordinal_distances_respect_spacing(self):
        request = dict(operation="ordinal_fidelity", scale=[0, 2, 3],
                       predicted=[1, 0, 0], observed=[0, 0.5, 0.5])
        result = run(request)
        self.assertAlmostEqual(result["wasserstein"], 2.5)
        self.assertAlmostEqual(result["normalized_wasserstein"], 5 / 6)
        self.assertEqual(result["ks_similarity"], 0)
        self.assertEqual(result["tvd"], 1)
        self.assertFalse(result["grade_promotion"])
        request["scale"] = [0, 0, 2]
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            run(request)

    def test_error_diagnostics_include_auroc_ties_and_acceptance(self):
        request = dict(operation="error_fidelity", decision_error_threshold=0.5,
                       accept_predicted_error_below=0.5, paired=[
            dict(unit_id="q1", prediction=0.2, human_outcome=0.2),
            dict(unit_id="q2", prediction=0.4, human_outcome=0.3),
            dict(unit_id="q3", prediction=0.4, human_outcome=0.6),
            dict(unit_id="q4", prediction=0.7, human_outcome=0.8),
        ])
        result = run(request)
        self.assertAlmostEqual(result["rmse"], (0.06 / 4) ** 0.5)
        self.assertAlmostEqual(result["decision_quality_auroc"], 7 / 8)
        self.assertEqual(result["accepted_fraction"], 3 / 4)
        self.assertAlmostEqual(result["error_rate_among_accepted"], 1 / 3)
        self.assertEqual(result["validation_status"], "NOT_ASSESSED")
        request["accept_predicted_error_below"] = 0
        self.assertIsNone(run(request)["error_rate_among_accepted"])
        request["decision_error_threshold"] = 1
        self.assertIsNone(run(request)["decision_quality_auroc"])
