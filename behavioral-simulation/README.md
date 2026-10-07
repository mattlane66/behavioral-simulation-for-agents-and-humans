# Behavioral Simulation

A research-backed method for using AI to explore how individuals or populations might respond under changed conditions—without treating generated behavior as observed human behavior.

## Use this when

Use Behavioral Simulation when the decision depends on a counterfactual:

- What might happen if we change a price, message, feature, policy, incentive, workflow, or environment?
- Which candidate scenario is most worth testing on real people?
- Which segment, edge case, or second-order effect deserves fieldwork?
- How might an interaction unfold over time?
- How sensitive is a decision to a behavioral assumption?

Do not use it merely to produce persuasive personas or realistic dialogue.

## Core rule

> **Simulation is a model estimate, not a human observation.**

The workflow must keep observed evidence, assumptions, simulation outputs, and calibration evidence separate.

## Simulation modes

### 1. Exploratory role-play

Base-model or prompted personas.

Use for:

- hypothesis generation;
- edge cases;
- adversarial scenarios;
- interview questions;
- search terms;
- mechanism brainstorming.

Do **not** report numeric population predictions or treat outputs as human evidence.

### 2. Individual-grounded simulation

An agent grounded in substantial evidence about a specific real person or well-defined individual case.

Use for:

- individualized scenario exploration;
- qualitative counterfactuals;
- estimating likely responses where the grounding evidence is relevant.

The preferred grounding sources are real interviews, surveys, behavioral traces, and artifacts. Demographics alone are a weak basis.

### 3. Population-grounded simulation

A model grounded or trained on real population response or behavioral data.

Use for:

- predicted response distributions;
- segment comparisons;
- condition comparisons;
- hypothesis screening.

Population-level claims require population-level validation. Accurate individual prediction does not by itself establish the joint or correlational structure of a population.

### 4. Dynamic / multi-agent simulation

Persistent agents interact over time in an environment.

Use for:

- journeys;
- social propagation;
- interaction effects;
- norm formation;
- repeated decisions;
- second-order effects.

Believability is not accuracy. Emergent behavior must be validated against appropriate real-world dynamics before it is used as decision evidence.

## Epistemic levels

Every run declares one level:

| Level | Basis | Legitimate use |
| --- | --- | --- |
| **L0 · ROLE_PLAY** | generic model + prompted persona/scenario | hypotheses and edge cases only |
| **L1 · EVIDENCE_GROUNDED** | real human/context evidence supplied to the model | bounded qualitative or individual estimates |
| **L2 · POPULATION_GROUNDED** | real response/behavioral data representing the target population or task | distributional estimates, still uncalibrated |
| **L3 · CALIBRATED** | L2 plus held-out real-human validation relevant to the task/population | weighted decision evidence with stated error |
| **L4 · DECISION_CALIBRATED** | repeated relevant validation, confidence/error model, freshness and drift controls | material decision support within the validated envelope |

A level is a ceiling, not a promise. Weak coverage, stale data, poor transfer, or out-of-distribution scenarios can lower the effective level for a particular claim.

## Workflow

```text
A. Frame the counterfactual
B. Define population / agents / environment
C. Register evidence and assumptions
D. Choose simulation mode and epistemic ceiling
E. Specify outcomes and action space
F. Run simulation
G. Stress-test and vary assumptions
H. Validate / calibrate where real outcomes exist
I. Interpret within the validated envelope
J. Route the next real-world action
```

See [SKILL.md](./SKILL.md) for the agent contract and [PROTOCOL.md](./PROTOCOL.md) for the full method.
