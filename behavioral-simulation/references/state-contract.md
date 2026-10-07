# State contract

A file-backed study uses these authoritative files:

```text
input.json
simulation-state.json
evidence-ledger.json
runs.json
validations.json
calibration.json
outputs/
```

Narrative reports are derived views. They cannot silently upgrade the evidence grade or change evidence type.

`validate_study.py` enforces the JSON schemas in `schemas/` as well as cross-file epistemic rules. Unknown top-level fields, wrong types, broken IDs, leakage, and invalid grade promotion should fail validation rather than being tolerated as prose conventions.

## `input.json`

Human/project input:

- decision;
- population;
- baseline;
- scenario/intervention;
- outcome/action space;
- mode;
- time/context;
- consequence if wrong;
- requested target grade.

## `simulation-state.json`

The current methodological state:

- phase/status;
- mode;
- current evidence grade and target grade;
- primary correctness unit;
- scenario specification;
- population coverage;
- model configuration;
- counterfactual distance;
- validation/calibration status;
- subgroup/freshness/drift;
- endpoint and next real-world test.

## `evidence-ledger.json`

Each record has:

- stable ID;
- evidence type;
- claim/observation;
- source/provenance;
- person/population/time coverage;
- whether it is used for grounding, training, validation, or context;
- whether it is held out;
- split unit/group when the record participates in training/grounding or held-out validation;
- notes.

The same outcome cannot be both training/grounding evidence and held-out validation for the same claim. Different evidence IDs do not make the data independent: if grounding/training and validation share the same declared split group, validation fails.

## `runs.json`

Simulation-run provenance:

- run ID;
- mode;
- model/version;
- config/prompt hash or description;
- seed;
- sample/agent count;
- output summary;
- evidence IDs used;
- generated estimate;
- date.

## `validations.json`

Held-out comparison records:

- validation ID;
- run ID;
- primary correctness unit;
- predicted values;
- observed values;
- `observed_evidence_ids` linking the observed result to held-out `OBSERVED_HUMAN` evidence;
- metric;
- computed error;
- split unit/group;
- target population/time match;
- subgroup;
- notes.

`calculate_metrics.py` recomputes supported metrics and rejects stale prose math.

## `calibration.json`

Error-prediction/decision-quality evidence:

- status;
- decision metric and threshold;
- validation IDs used;
- split method;
- predicted vs observed error;
- RMSE/correlation/AUROC or other justified metrics;
- bucket success rates;
- subgroup/freshness scope;
- model/config scope.

A model change invalidates calibration unless compatibility is explicitly re-established.

## Evidence types

Allowed values:

- `OBSERVED_HUMAN`
- `NONHUMAN_CONTEXT`
- `ASSUMPTION`
- `SIMULATED_ESTIMATE`
- `CALIBRATION_EVIDENCE`

## Modes

- `PLAUSIBILITY_SPACE`
- `INDIVIDUAL_PROXY`
- `POPULATION_PREDICTION`
- `MULTI_AGENT_DYNAMICS`

## Evidence grades

- `L0_ROLEPLAY`
- `L1_PERSON_GROUNDED`
- `L2_POPULATION_GROUNDED`
- `L3_HELD_OUT_VALIDATED`
- `L4_DECISION_CALIBRATED`

## Primary correctness units

- `INDIVIDUAL`
- `DISTRIBUTION`
- `TREATMENT_EFFECT`
- `SYSTEM_TRAJECTORY`
- `PLAUSIBILITY_ONLY`

## State-before-story

If a report says "high confidence" while `calibration.status != VALID`, the report is invalid.

If a report describes a simulated output as observed behavior, the report is invalid.

If `current_grade` exceeds the structural evidence available in the ledgers, the study is invalid.
