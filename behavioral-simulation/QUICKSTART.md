# Quickstart

## Initialize

```bash
python behavioral-simulation/scripts/init_study.py \
  --workspace research/my-simulation \
  --decision "Choose which onboarding concept to field-test first" \
  --population "US adults who opened a new brokerage account in the last 12 months" \
  --scenario "Compare concept A with concept B" \
  --outcome "Choice between A, B, neither" \
  --mode POPULATION_PREDICTION
```

The initializer creates:

```text
input.json
simulation-state.json
evidence-ledger.json
runs.json
validations.json
calibration.json
outputs/
```

## Determine the next valid move

```bash
python behavioral-simulation/scripts/next_simulation_move.py research/my-simulation
```

## Recompute validation metrics

When `validations.json` contains predicted and observed distributions:

```bash
python behavioral-simulation/scripts/calculate_metrics.py research/my-simulation
```

For categorical distributions, the default metric is Total Variation Distance:

```text
TVD(P,Q) = 1/2 × Σ |P_i - Q_i|
```

Do not use TVD mechanically for every outcome. Ordinal, continuous, time-to-event, treatment-effect, and trajectory tasks may need another predeclared metric.

## Validate the study state

```bash
python behavioral-simulation/scripts/validate_study.py research/my-simulation
```

Fix errors before promoting the evidence grade or publishing a final result.

## Output

Use [`templates/simulation-report.md`](templates/simulation-report.md).

Every result must expose:

- simulation mode;
- evidence grade;
- population and scenario;
- model/config/version;
- grounding and assumptions;
- whether estimates are individual or distributional;
- held-out validation coverage;
- observed error and/or calibrated predicted error;
- subgroup performance;
- freshness/drift status;
- what the simulation can and cannot support;
- highest-value real-world validation next.
