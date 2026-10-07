# Method boundary

## Boundary decision

Behavioral Simulation is a distinct evidence-and-modeling method.

It may consume real human research, behavioral traces, experiments, market data, or explicitly hypothetical assumptions. It produces **model-derived estimates and simulated trajectories**, not observed human evidence.

The core boundary is:

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

A generated response remains generated even when the model is highly accurate.

Calibration can increase how much decision weight a simulation deserves. It does not change its ontological status into an observation of a real person.

The future skill should therefore keep at least these categories separate:

- **OBSERVED_HUMAN** — statements, behavior, artifacts, transactions, experiments, or other direct human evidence;
- **NONHUMAN_CONTEXT** — environmental, institutional, technical, economic, or other contextual evidence;
- **SIMULATED_ESTIMATE** — model-generated response, distribution, trajectory, or scenario result;
- **CALIBRATION_EVIDENCE** — held-out comparison between model predictions and real outcomes;
- **ASSUMPTION** — an input not established by evidence.

## Cross-method safeguards

### Lead User Research

Simulation may generate hypotheses, edge cases, concept probes, rival explanations, or fieldwork priorities. It must not establish LU1/LU2, observed behavior, prevalence, propagation, or need importance.

### Opportunity Underwriting

Simulation may support scenario analysis, hypothesis ranking, sensitivity analysis, and value-of-information routing. It must not independently establish willingness to pay, adoption, market size, retention, or unit economics.

### Planning

Simulation may inform working requirements, candidate mechanisms, and risk exploration. It does not create accepted product requirements, select a shape, set scope, or authorize implementation.

## Calibration principle

Use the strongest language the validation regime supports and no stronger.

A simulation without relevant held-out validation should be treated as exploratory. A simulation with repeated task- and population-relevant validation may carry more decision weight, but its uncertainty, coverage, date, model version, and calibration basis must remain visible.
