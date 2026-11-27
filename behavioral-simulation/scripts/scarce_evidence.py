"""Bounded deterministic measurement; outputs are not human observations.
SSR primitive extracted from Scaled Interview Data Assistant 38b85c6 (MIT),
Maier et al. arXiv:2510.08338v3. Fixed-weight PPI mean: Krsteski et al.
ACL 2026, eqs 1–3. No automatic calibration or survey-design verification.
"""
from __future__ import annotations
import argparse
import json
import math
import statistics as st
from pathlib import Path

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
    weight = _number(request["weight"])
    if not 0 <= weight <= 1:
        raise ValueError("Weight must be within [0,1]")
    ui, u, _ = _rows(request["unlabeled"])
    hi, p, y = _rows(request["labeled"], True)
    if ui & hi:
        raise ValueError("Labeled and unlabeled units overlap")
    residual = [a-weight*b for a,b in zip(y,p,strict=True)]
    variance = weight**2*st.variance(u)/len(u) + st.variance(residual)/len(y)
    baseline_var = st.variance(y)/len(y)
    return {"evidence_type":"SIMULATED_ESTIMATE","method":"FIXED_WEIGHT_PPI_MEAN",
            "weight":weight,"n_human":len(y),"n_real_covariate_units":len(u),
            "human_only_mean":st.mean(y),"raw_prediction_mean":st.mean(u),
            "rectified_mean":weight*st.mean(u)+st.mean(residual),
            "estimated_variance":variance,"human_only_estimated_variance":baseline_var,
            "estimated_precision_gain":(baseline_var/variance-1) if variance>0 else None,
            "design_attested_not_verified":True,"grade_promotion":False}

def fidelity(request):
    _, p, y = _rows(request["paired"], True)
    return {"evidence_type":"CALIBRATION_EVIDENCE","n_pairs":len(y),
            "human_mean":st.mean(y),"predicted_mean":st.mean(p),
            "human_sample_variance":st.variance(y),"predicted_sample_variance":st.variance(p),
            "pearson":st.correlation(y,p) if st.variance(y)>0 and st.variance(p)>0 else None,
            "mae":st.mean(abs(a-b) for a,b in zip(y,p,strict=True)),
            "grade_promotion":False,"note":"Descriptive comparison only; verify holdout independence, subgroup and conditional effects separately."}

def run(request):
    op=request["operation"]
    if op=="rectify_mean": return rectify_mean(request)
    if op=="fidelity": return fidelity(request)
    if op=="ssr":
        pmf=distribution(request["vector"],request["anchor_vectors"],request.get("epsilon",0.0),request.get("temperature",1.0))
        return {"evidence_type":"SIMULATED_ESTIMATE","rating_probabilities":pmf,"grade_promotion":False}
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
