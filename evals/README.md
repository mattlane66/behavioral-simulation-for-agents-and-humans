# Assurance evaluations

`assurance-cases.json` encodes methodological failures the skill must reject or downgrade.

The goal is not to benchmark model intelligence. It is to catch **epistemic promotion errors** such as:

- synthetic respondents relabeled as humans;
- population percentages from persona role-play;
- training/validation leakage;
- believability presented as predictive validity;
- individual accuracy conflated with distribution accuracy;
- model self-confidence presented as calibration;
- L4 claims without out-of-sample error prediction;
- stale calibration reused after model/data change.
