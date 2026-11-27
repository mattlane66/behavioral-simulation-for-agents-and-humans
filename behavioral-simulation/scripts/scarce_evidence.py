"""Bounded deterministic measurement; outputs are not human observations.
Legacy SSR primitive from Scaled Interview Data Assistant 38b85c6 (MIT).
PPI mean: Krsteski et al. ACL 2026, Eqs. 1–3. Optional independent-pilot
weight uses the scalar variance objective in PPI++ §6. No automatic survey-
design verification, confidence interval or calibration.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics as st
from itertools import accumulate, groupby
from pathlib import Path

from calculate_metrics import tvd

def _vector(value: object) -> list[float]:
    if not isinstance(value, list) or not value:
        raise ValueError("Embedding vectors must be nonempty arrays")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) for x in value):
        raise ValueError("Embedding contains a nonnumeric element")
    vector = [float(x) for x in value]
    if not all(math.isfinite(x) for x in vector) or not any(x != 0 for x in vector):
        raise ValueError("Embedding is zero or nonfinite")
    return vector


def cosine(a: object, b: object) -> float:
    va, vb = _vector(a), _vector(b)
    if len(va) != len(vb):
        raise ValueError("Mismatched embedding dimensions")
    numerator = math.fsum(x * y for x, y in zip(va, vb, strict=True))
    den = math.sqrt(math.fsum(x * x for x in va) * math.fsum(y * y for y in vb))
    if den <= 0 or not math.isfinite(den):
        raise ValueError("Invalid embedding norm")
    return max(-1.0, min(1.0, numerator / den))


def distribution(vector: list[float], anchor_vectors: list[list[float]],
                 epsilon: float = 0.0, temperature: float = 1.0) -> list[float]:
    if len(anchor_vectors) != 5 or epsilon < 0 or temperature <= 0:
        raise ValueError("SSR needs five anchors, epsilon >= 0, and temperature > 0")
    if not math.isfinite(epsilon) or not math.isfinite(temperature):
        raise ValueError("SSR parameters must be finite")
    similarities = [cosine(vector, anchor) for anchor in anchor_vectors]
    minimum = min(similarities)
    weights = [max(0.0, s - minimum + epsilon) ** (1.0 / temperature)
               for s in similarities]
    total = math.fsum(weights)
    if total <= 0 or not math.isfinite(total):
        raise ValueError("Anchor set is degenerate; cannot create an SSR distribution")
    return [value / total for value in weights]



def _number(x):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError("Expected finite number")
    return float(x)

def _rows(rows, observed=False):
    if not isinstance(rows, list) or len(rows) < 2:
        raise ValueError("At least two independent real sampling units per sample")
    ids, predictions, outcomes = set(), [], []
    for row in rows:
        key = row["unit_id"]
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError("Missing or repeated unit ID")
        ids.add(key)
        predictions.append(_number(row["prediction"]))
        if observed:
            outcomes.append(_number(row["human_outcome"]))
    return ids, predictions, outcomes

def rectify_mean(request):
    design = request["design"]
    for field in ("same_target_distribution", "independent_iid_samples",
                  "real_covariate_frame", "real_human_labels",
                  "frozen_independent_predictor", "weight_predeclared"):
        if design.get(field) is not True:
            raise ValueError("Missing design attestation: " + field)
    for field in ("population", "estimand", "model_version", "provenance"):
        if not isinstance(design.get(field), str) or not design[field].strip():
            raise ValueError("Missing design metadata: " + field)
    ui, u, _ = _rows(request["unlabeled"])
    hi, p, y = _rows(request["labeled"], True)
    if ui & hi:
        raise ValueError("Labeled and unlabeled units overlap")
    if "tuning" in request:
        if "weight" in request:
            raise ValueError("Supply a fixed weight or independent tuning, whichever the design declares")
        if design.get("independent_tuning_sample_same_target") is not True:
            raise ValueError("Independent same-target tuning sample must be attested")
        if not isinstance(design.get("tuning_provenance"), str) or not design["tuning_provenance"].strip():
            raise ValueError("Missing tuning provenance")
        ti, tp, ty = _rows(request["tuning"], True)
        if ti & (ui | hi):
            raise ValueError("Tuning and inference units overlap")
        denominator = (1 + len(y) / len(u)) * st.variance(tp)
        weight = min(1.0, max(0.0, st.covariance(ty, tp) / denominator)) if denominator else 0.0
        weight_selection = "INDEPENDENT_PILOT"
    else:
        weight = _number(request["weight"])
        if not 0 <= weight <= 1:
            raise ValueError("Weight must be within [0,1]")
        weight_selection = "FIXED"
    residual = [a-weight*b for a,b in zip(y,p,strict=True)]
    variance = weight**2*st.variance(u)/len(u) + st.variance(residual)/len(y)
    baseline_var = st.variance(y)/len(y)
    return {"evidence_type":"SIMULATED_ESTIMATE",
            "estimate_basis":"MODEL_ASSISTED_STATISTICAL_ESTIMATE",
            "method":"FIXED_WEIGHT_PPI_MEAN","weight_selection":weight_selection,
            "weight":weight,"n_human":len(y),"n_real_covariate_units":len(u),
            "human_only_mean":st.mean(y),"raw_prediction_mean":st.mean(u),
            "rectified_mean":weight*st.mean(u)+st.mean(residual),
            "estimated_variance":variance,"human_only_estimated_variance":baseline_var,
            "estimated_precision_gain":(baseline_var/variance-1) if variance>0 else None,
            "design_attested_not_verified":True,"grade_promotion":False}

def fidelity(request):
    _, p, y = _rows(request["paired"], True)
    human_mean, predicted_mean = st.mean(y), st.mean(p)
    human_variance, predicted_variance = st.variance(y), st.variance(p)
    return {"comparison_type":"DESCRIPTIVE_DIAGNOSTIC","validation_status":"NOT_ASSESSED","n_pairs":len(y),
            "human_mean":human_mean,"predicted_mean":predicted_mean,
            "human_sample_variance":human_variance,"predicted_sample_variance":predicted_variance,
            "absolute_standardized_mean_gap":abs(predicted_mean - human_mean) / math.sqrt(human_variance)
            if human_variance else None,
            "spread_ratio":math.sqrt(predicted_variance / human_variance) if human_variance else None,
            "pearson":st.correlation(y,p) if human_variance and predicted_variance else None,
            "mae":st.mean(abs(a-b) for a,b in zip(y,p,strict=True)),
            "grade_promotion":False,"note":"Descriptive comparison only; verify holdout independence, subgroup and conditional effects separately."}


def ordinal_fidelity(request):
    """Compare two PMFs over an explicitly spaced and ordered rating scale."""
    scale = [_number(value) for value in request["scale"]]
    predicted = [_number(value) for value in request["predicted"]]
    observed = [_number(value) for value in request["observed"]]
    widths = [right - left for left, right in zip(scale, scale[1:])]
    if not widths or any(width <= 0 or not math.isfinite(width) for width in widths):
        raise ValueError("Scale must have at least two strictly increasing points")
    if not len(predicted) == len(observed) == len(scale):
        raise ValueError("Distributions must use the same declared scale")
    if any(value < 0 for value in predicted + observed):
        raise ValueError("Probabilities must be nonnegative")
    pred_sum, obs_sum = math.fsum(predicted), math.fsum(observed)
    if not all(math.isclose(total, 1.0, abs_tol=1e-6) for total in (pred_sum, obs_sum)):
        raise ValueError("Distributions must sum to one")
    predicted = [value / pred_sum for value in predicted]
    observed = [value / obs_sum for value in observed]
    gaps = [abs(p - y) for p, y in zip(accumulate(predicted), accumulate(observed), strict=True)]
    distance = math.fsum(gap * width for gap, width in zip(gaps[:-1], widths, strict=True))
    return {
        "comparison_type": "DESCRIPTIVE_DIAGNOSTIC",
        "validation_status": "NOT_ASSESSED",
        "wasserstein": distance,
        "normalized_wasserstein": distance / math.fsum(widths),
        "ks_similarity": 1 - max(gaps),
        "tvd": tvd(dict(zip(map(str, scale), predicted, strict=True)),
                   dict(zip(map(str, scale), observed, strict=True))),
        "grade_promotion": False,
    }


def error_fidelity(request):
    """Compare TVD estimates against observed TVD, one row per test question."""
    _, pred, actual = _rows(request["paired"], True)
    threshold = _number(request["decision_error_threshold"])
    acceptance = _number(request["accept_predicted_error_below"])
    if any(not 0 <= value <= 1 for value in (threshold, acceptance, *pred, *actual)):
        raise ValueError("TVD and thresholds must be in [0,1]")
    pairs = list(zip(pred, actual, strict=True))
    # A lower predicted error should rank a decision-quality case higher.
    # Count half a success when the positive and negative have the same score.
    worse_scored_bad = 0
    wins = 0.0
    good = sum(outcome < threshold for outcome in actual)
    bad = len(actual) - good
    for _, group in groupby(sorted(pairs, reverse=True), key=lambda pair: pair[0]):
        outcomes = [outcome for _, outcome in group]
        group_good = sum(outcome < threshold for outcome in outcomes)
        group_bad = len(outcomes) - group_good
        wins += group_good * (worse_scored_bad + 0.5 * group_bad)
        worse_scored_bad += group_bad
    accepted = [outcome for estimate, outcome in pairs if estimate < acceptance]
    return {
        "comparison_type": "DESCRIPTIVE_DIAGNOSTIC",
        "validation_status": "NOT_ASSESSED",
        "n_questions": len(actual),
        "rmse": math.sqrt(st.mean((estimate - outcome) ** 2 for estimate, outcome in pairs)),
        "pearson": st.correlation(pred, actual) if len(set(pred)) > 1 and len(set(actual)) > 1 else None,
        "decision_quality_auroc": wins / (good * bad) if good and bad else None,
        "accepted_fraction": len(accepted) / len(actual),
        "error_rate_among_accepted": (
            sum(outcome >= threshold for outcome in accepted) / len(accepted)
            if accepted else None
        ),
        "decision_error_threshold": threshold,
        "accept_predicted_error_below": acceptance,
        "grade_promotion": False,
    }


def run(request):
    op=request["operation"]
    if op=="rectify_mean": return rectify_mean(request)
    if op=="fidelity": return fidelity(request)
    if op=="ordinal_fidelity": return ordinal_fidelity(request)
    if op=="error_fidelity": return error_fidelity(request)
    if op=="ssr":
        pmf=distribution(request["vector"],request["anchor_vectors"],request.get("epsilon",0.0),request.get("temperature",1.0))
        return {"evidence_type":"SIMULATED_ESTIMATE","transform":"LEGACY_UNIFORM_EPSILON",
                "rating_probabilities":pmf,"grade_promotion":False}
    raise ValueError("Unsupported operation")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    result=run(json.loads(args.input.read_text(encoding="utf-8")))
    with args.output.open("x",encoding="utf-8") as out:
        json.dump(result,out,indent=2,allow_nan=False)
        out.write("\n")

if __name__=="__main__":
    main()
