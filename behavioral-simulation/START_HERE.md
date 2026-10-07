# Start Here

Use Behavioral Simulation when the question is:

> **What might people do if something changed, and how much confidence should we place in that simulation?**

Do not use it merely because synthetic users are cheap.

## Choose the smallest valid mode

- Need possible reactions, failure modes, or emergent behavior? Use `PLAUSIBILITY_SPACE`.
- Need a proxy for a specific person and you have that person's own data? Use `INDIVIDUAL_PROXY`.
- Need a distribution for a defined population? Use `POPULATION_PREDICTION`.
- Need behavior that unfolds across interacting agents and time? Use `MULTI_AGENT_DYNAMICS`.

Then assign the **evidence grade** based on what you actually have, not what you want to claim.

## Minimum input

```text
Decision:
What real decision will this simulation inform?

Population:
Who is being modeled?

Scenario / intervention:
What changes relative to the relevant baseline?

Outcome / action space:
What behavior or response is being simulated?

Time / context:
When and under what conditions?
```

If these fields are not stable, stay in framing. Do not run thousands of agents around an ambiguous counterfactual.

## Fast path

For exploration, a valid result may be:

> `L0_ROLEPLAY`: Here are plausible edge cases and mechanisms. These are hypotheses, not population evidence.

For predictive work, the method should force a higher burden:

> real grounding → explicit sampling/coverage → held-out outcomes → task-appropriate error → subgroup checks → calibration → freshness/drift

If you cannot satisfy that burden, lower the grade rather than invent confidence.
