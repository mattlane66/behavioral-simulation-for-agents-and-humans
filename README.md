# Behavioral Simulation for Agents and Humans

Turn real human evidence and explicit assumptions into bounded behavioral simulations for exploring what people might do under changed conditions—without confusing model output with observed human behavior.

> **Simulation is a model estimate, not a human observation.**

## Status

Bootstrap repository. The research-backed simulation skill, protocol, schemas, validators, evaluation harness, and integrations will be added next.

## What this repository will own

This repository is the canonical home for methods that:

- define a population, context, intervention, and action or outcome space;
- construct individual or population models from explicit evidence;
- run behavioral counterfactuals and multi-agent simulations;
- compare predicted response distributions across scenarios;
- measure simulation error against held-out human or behavioral outcomes when available;
- calibrate confidence to the evidence, task, population, and validation regime;
- track freshness, drift, provenance, and known failure modes;
- route uncertain or decision-critical claims back to real-world research or experiments.

## What it will not own

Behavioral simulation does **not** turn generated responses into human evidence.

It does not independently establish:

- Lead User qualification or observed Lead User behavior;
- prevalence, propagation, or need importance in a real population;
- willingness to pay, adoption, retention, market size, or unit economics;
- product-planning truth or implementation authority.

Those claims require the appropriate evidence and decision method.

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

This is **not a mandatory pipeline**. Each method may invoke another when the unresolved uncertainty belongs there.

- [Lead User Research](https://github.com/mattlane66/planning-skills-for-agents-and-humans/tree/main/lead-user-research) owns future-facing need discovery and real Lead User evidence.
- [Opportunity Underwriting](https://github.com/mattlane66/opportunity-underwriting-for-agents-and-humans) owns business-level pursue / test / hold / reject decisions.
- [Planning Skills](https://github.com/mattlane66/planning-skills-for-agents-and-humans) owns accepted product intent through implementation.
- This repository will own behavioral simulation, validation, calibration, and simulation-specific evidence semantics.

## Research basis

The initial research set is documented in [`research/README.md`](./research/README.md). It includes work on populated social prototypes, generative-agent memory and planning, interview-grounded agents, population-level behavioral prediction, and foundation-model evaluation and risk.

Simile is a product reference for the capability class this repository is intended to study and reproduce methodologically where the public evidence supports it. It is not treated as an authority merely because it is a commercial implementation.

## Planned next step

Build the first canonical `behavioral-simulation` skill from the research corpus, including:

1. epistemic levels for role-play, evidence-grounded, population-grounded, calibrated, and decision-calibrated simulation;
2. a simulation brief and state contract;
3. scenario and population specification;
4. individual and multi-agent simulation modes;
5. validation, calibration, confidence, and drift rules;
6. deterministic checks that prevent synthetic output from being promoted to observed human evidence;
7. handoff contracts with Lead User Research and Opportunity Underwriting;
8. an assurance suite with failure cases and synthetic fixtures.

## License

MIT. See [`LICENSE`](./LICENSE).
