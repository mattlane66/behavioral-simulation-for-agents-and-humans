# Behavioral Simulation for Agents and Humans

Turn human evidence, explicit assumptions, and model outputs into bounded behavioral simulations for exploring what people might do under changed conditions—without confusing simulation with observation.

> **Simulation is a model estimate, not a human observation.**

This repository contains a reusable `behavioral-simulation` skill for four related jobs:

- **plausibility-space exploration** — surface possible behaviors, edge cases, and emergent interactions without claiming prediction;
- **individual proxy simulation** — model how a specific person might respond when grounded in that person's own data;
- **population prediction** — estimate distributions of responses or actions for a defined population;
- **multi-agent dynamics** — explore how interactions, memory, rules, and interventions may produce system-level behavior over time.

The method makes **simulation mode** and **evidence grade** separate. A vivid multi-agent simulation can still be low-grade evidence. A simple population distribution can be much stronger if it has held-out human validation and calibration.

## Start here

Read [`behavioral-simulation/START_HERE.md`](./behavioral-simulation/START_HERE.md).

For an agent with file access, use:

- [`behavioral-simulation/SKILL.md`](./behavioral-simulation/SKILL.md) — operating contract;
- [`behavioral-simulation/PROTOCOL.md`](./behavioral-simulation/PROTOCOL.md) — canonical methodology;
- [`behavioral-simulation/QUICKSTART.md`](./behavioral-simulation/QUICKSTART.md) — file-backed execution;
- [`behavioral-simulation/PORTABLE_PROMPT.md`](./behavioral-simulation/PORTABLE_PROMPT.md) — compact prompt for environments without repo tooling.

## Governing distinction

```text
OBSERVED HUMAN EVIDENCE
what real people said or did
          │
          ├───────────────┐
          ▼               ▼
   model grounding   held-out validation
          │               │
          └──────┬────────┘
                 ▼
       BEHAVIORAL SIMULATION
    what the model predicts might happen
                 │
                 ▼
       SIMULATED ESTIMATE
      + uncertainty/calibration
```

A simulation can become **better validated**. It never becomes an observed human event.

## Evidence grades

| Grade | Minimum basis | What it can support |
| --- | --- | --- |
| `L0_ROLEPLAY` | model prior + explicit prompt/assumptions | hypotheses, edge cases, possible mechanisms; **no population prediction claim** |
| `L1_PERSON_GROUNDED` | real person-level interviews/surveys/traces used to ground agents | individual proxy exploration; still not population evidence |
| `L2_POPULATION_GROUNDED` | real population/experimental/behavioral data with defensible sampling or coverage | model-derived population estimates, clearly labeled uncalibrated |
| `L3_HELD_OUT_VALIDATED` | L1/L2 plus held-out real-human outcomes evaluated on the relevant task | validated estimates with observed error metrics |
| `L4_DECISION_CALIBRATED` | L3 plus predeclared decision metric/threshold, query-class calibration, subgroup checks, freshness/drift controls | decision-weighted simulation with explicit predicted error/confidence |

The grade is a ceiling, not a reward. Missing requirements lower the grade.

## Relationship to the other methods

```text
Lead User Research
What important future-facing needs are emerging?
          ↕
Behavioral Simulation
What might people do if X changed?
          ↕
Opportunity Underwriting
Is there enough real economic opportunity to act?
          ↕
Planning Skills
What should we make, and how?
```

This is **not a mandatory pipeline**.

- [Lead User Research](https://github.com/mattlane66/planning-skills-for-agents-and-humans/tree/main/lead-user-research) owns future-facing need discovery and real Lead User evidence.
- [Opportunity Underwriting](https://github.com/mattlane66/opportunity-underwriting-for-agents-and-humans) owns business-level pursue / test / hold / reject decisions.
- [Planning Skills](https://github.com/mattlane66/planning-skills-for-agents-and-humans) owns accepted product intent through implementation.
- This repository owns behavioral simulation, simulation-specific evidence semantics, validation, calibration, and confidence boundaries.

## Research basis

The methodology is derived from the research corpus documented in [`research/README.md`](./research/README.md) and [`behavioral-simulation/references/methodology-basis.md`](./behavioral-simulation/references/methodology-basis.md).

The core lineage is:

1. **Social Simulacra** — populate a proposed social system to expose a breadth of possible behavior rather than make a single point prediction.
2. **Generative Agents** — add memory, retrieval, reflection, planning, and reaction for behavior that unfolds over time.
3. **Generative Agent Simulations of 1,000 People / later revised self-report-grounded work** — ground individual agents in rich data from real people and evaluate against the same people's held-out responses and self-consistency.
4. **SOCRATES / SocSci210** — train on large-scale experimental response data and evaluate both individual accuracy and population-distribution alignment on held-out studies and conditions.
5. **Foundation Models** — treat inherited model defects, emergence, homogenization, evaluation gaps, and sociotechnical effects as first-class risks.
6. **Simile's public methodology** — combine behavioral and self-report data, validate against real outcomes, use distributional error such as TVD, predict likely error with a separate confidence mechanism, and monitor freshness/drift.

Simile is a product reference, not an authority over the method. Proprietary details are not inferred.

## Repository structure

```text
behavioral-simulation/
  SKILL.md
  PROTOCOL.md
  START_HERE.md
  QUICKSTART.md
  PORTABLE_PROMPT.md
  references/
  schemas/
  scripts/
  templates/
evals/
tests/
research/
docs/
```

## License

MIT. See [`LICENSE`](./LICENSE).
