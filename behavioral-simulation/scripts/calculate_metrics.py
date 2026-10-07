#!/usr/bin/env python3
"""Recompute supported validation metrics from predicted and observed values."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from _common import read_json, write_json


def tvd(predicted: dict[str, Any], observed: dict[str, Any]) -> float:
    keys = set(predicted) | set(observed)
    if not keys:
        raise ValueError("TVD requires non-empty distributions")
    p = {k: float(predicted.get(k, 0.0)) for k in keys}
    q = {k: float(observed.get(k, 0.0)) for k in keys}
    if any(v < 0 for v in p.values()) or any(v < 0 for v in q.values()):
        raise ValueError("distribution probabilities cannot be negative")
    ps, qs = sum(p.values()), sum(q.values())
    if not math.isclose(ps, 1.0, abs_tol=1e-6) or not math.isclose(qs, 1.0, abs_tol=1e-6):
        raise ValueError(f"TVD distributions must sum to 1 (pred={ps}, obs={qs})")
    return 0.5 * sum(abs(p[k] - q[k]) for k in keys)


def compute(row: dict[str, Any]) -> float | None:
    metric = row.get("metric")
    if metric == "TVD":
        if not isinstance(row.get("predicted"), dict) or not isinstance(row.get("observed"), dict):
            raise ValueError("TVD requires object distributions")
        return tvd(row["predicted"], row["observed"])
    if metric == "ABSOLUTE_ERROR":
        return abs(float(row["predicted"]) - float(row["observed"]))
    if metric in {"ACCURACY", "CORRELATION", "OTHER"}:
        # These metrics can require raw paired observations or domain-specific code.
        # Keep an explicitly supplied result rather than pretending this generic script can reconstruct it.
        return row.get("computed_error")
    raise ValueError(f"unsupported metric: {metric}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workspace")
    args = p.parse_args()
    path = Path(args.workspace) / "validations.json"
    data = read_json(path)
    for row in data.get("entries", []):
        row["computed_error"] = compute(row)
    write_json(path, data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
