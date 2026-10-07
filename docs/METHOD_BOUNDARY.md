# Method boundary

## Boundary decision

Behavioral Simulation is a distinct evidence-and-modeling method.

It may consume real human research, behavioral traces, experiments, market data, or explicitly hypothetical assumptions. It produces **model-derived estimates and simulated trajectories**, not observed human evidence.

```text
real evidence + assumptions + model + scenario
                    |
                    v
          behavioral simulation
                    |
                    v
     predictions + uncertainty + provenance
                    |
          explicit handoff only
                    v
research / underwriting / planning / experiment
```

## Evidence semantics

Use these types:

- `OBSERVED_HUMAN` — real statements, behavior, artifacts, transactions, experimental outcomes, or direct observation;
- `NONHUMAN_CONTEXT` — institutional, technical, environmental, economic, or other contextual evidence;
- `SIMULATED_ESTIMATE` — generated response, distribution, trajectory, or scenario result;
- `CALIBRATION_EVIDENCE` — comparison of simulation output with held-out real outcomes;
- `ASSUMPTION` — an input not established by evidence.

A generated response remains generated even if prediction error is low. Calibration changes the warranted **weight**, not the source type.

## Cross-method safeguards

### Lead User Research

Behavioral Simulation may generate hypotheses, edge cases, concept probes, rival explanations, or fieldwork priorities. It cannot establish LU1/LU2, observed behavior, prevalence, propagation, or need importance.

### Opportunity Underwriting

Behavioral Simulation may support scenario analysis, hypothesis ranking, sensitivity analysis, and value-of-information routing. It cannot independently establish willingness to pay, adoption, retention, market size, or unit economics.

### Planning

Behavioral Simulation may inform working requirements, candidate mechanisms, risk exploration, or concept probes. It does not create accepted requirements, select a product shape, set Appetite, or authorize implementation.

## Calibration principle

Use the strongest language the validation regime supports and no stronger.

A simulation without relevant held-out validation is exploratory or uncalibrated. A simulation with repeated task- and population-relevant validation may carry more decision weight, but its error metric, validation coverage, model version, data freshness, and known failure modes must remain visible.
