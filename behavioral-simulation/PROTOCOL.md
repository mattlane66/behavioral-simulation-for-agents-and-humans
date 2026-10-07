# Behavioral Simulation Protocol

## Status and scope

This is the canonical methodological specification for **Behavioral Simulation for Agents and Humans**.

It synthesizes methods from social-computing simulation, generative-agent architectures, person-grounded agent evaluation, population behavioral prediction, foundation-model evaluation, and current public simulation practice.

It is **not itself a scientifically validated instrument**. Its job is to make simulation claims harder to overstate and easier to audit.

The method answers:

> **Given a defined population or person, scenario, context, and outcome space, what model-derived behaviors are plausible or predicted—and what empirical validation supports placing decision weight on them?**

## 1. Start with the decision, not the synthetic population

Before generating agents, define:

- decision being informed;
- decision owner;
- consequence if wrong;
- target population/person;
- relevant baseline;
- changed condition/intervention;
- outcome/action space;
- time horizon/date/context;
- whether the decision needs plausibility exploration or predictive accuracy.

A simulation with a vague target is not rescued by more agents.

## 2. Simulation mode is separate from evidence grade

### Modes

#### `PLAUSIBILITY_SPACE`

Purpose: reveal possible behavior, edge cases, mechanisms, and emergent interactions.

This follows the strongest methodological contribution of Social Simulacra: use generated behavior to **expand the space of outcomes a designer considers**, not to make a single future prediction.

Believability can be useful for prototyping. It is not predictive validation.

#### `INDIVIDUAL_PROXY`

Purpose: model a specific person's likely response across tasks.

The relevant unit is the **individual**. Rich person-specific self-report or behavioral grounding is preferred over demographic descriptions. Evaluation compares the proxy's held-out responses to the same person's real responses.

#### `POPULATION_PREDICTION`

Purpose: estimate a response/action distribution for a defined population.

The relevant unit is the **population distribution**. A model can improve distributional alignment while degrading individual-level accuracy; therefore both must remain separate.

#### `MULTI_AGENT_DYNAMICS`

Purpose: model behavior that depends on interaction, temporal continuity, memory, diffusion, coordination, environment state, or feedback loops.

The relevant unit is an **emergent system trajectory**. Narrative coherence alone is insufficient; predictive claims require empirical system-level validation.

### Evidence grades

#### `L0_ROLEPLAY`

Requirements:

- explicit scenario;
- explicit assumptions;
- model/config recorded.

Permitted claims:

- possible behavior;
- hypothesis generation;
- edge cases;
- candidate mechanisms;
- design probes.

Forbidden claims:

- population prevalence;
- calibrated percentage;
- real-human evidence.

#### `L1_PERSON_GROUNDED`

Requirements:

- L0 requirements;
- real person-specific interviews, surveys, artifacts, or behavioral traces;
- provenance for each grounding source.

Permitted claims:

- person-grounded proxy exploration.

Still forbidden:

- generalizing from these persons to a population without a population design;
- calling generated reflections observed evidence.

#### `L2_POPULATION_GROUNDED`

Requirements:

- a defined target population;
- real population/experimental/behavioral data or a defensible sampling/coverage design;
- explicit mapping from source population to target population;
- temporal/geographic coverage;
- known selection limitations.

Permitted claims:

- **uncalibrated simulated population estimate**, clearly labeled.

Still forbidden:

- "decision-grade" or empirically calibrated confidence without held-out validation.

#### `L3_HELD_OUT_VALIDATED`

Requirements:

- L1 or L2 grounding as appropriate;
- real outcomes held out from grounding/training;
- no leakage at the relevant unit;
- task-appropriate metric;
- benchmark/baseline;
- model/config frozen for the evaluated run;
- subgroup error where relevant.

Permitted claims:

- validated simulation performance within the demonstrated scope.

#### `L4_DECISION_CALIBRATED`

Requirements:

- L3;
- a predeclared decision-quality metric and threshold;
- a held-out corpus of queries/runs representative enough of the intended use;
- an out-of-sample method for predicting likely error of a new run;
- calibration/discrimination evaluation for that error predictor;
- subgroup checks;
- freshness/drift policy;
- revalidation trigger after material model/data changes.

Permitted claims:

- decision-weighted simulated estimates with explicit predicted error/confidence **within the calibrated scope**.

## 3. Evidence ontology

Every material input/output is exactly one of:

### `OBSERVED_HUMAN`

Examples:

- interview statement;
- survey response;
- transaction;
- click/event log;
- experimental outcome;
- directly observed action.

### `NONHUMAN_CONTEXT`

Examples:

- price;
- interface state;
- policy;
- product rules;
- location/environment constraints;
- economic conditions.

### `ASSUMPTION`

A scenario input not established by evidence.

### `SIMULATED_ESTIMATE`

Anything generated by the behavioral model:

- synthetic person's response;
- predicted distribution;
- interaction;
- trajectory;
- model-generated reflection;
- predicted treatment effect.

### `CALIBRATION_EVIDENCE`

A comparison between a simulation and held-out real outcome.

No transformation inside the model converts `SIMULATED_ESTIMATE` into `OBSERVED_HUMAN`.

## 4. Grounding people without reducing them to stereotypes

The 1,000-person research lineage shows that rich self-report grounding can outperform demographic-only descriptions and reduce some group-level accuracy disparities.

Operational rules:

1. Prefer the person's own data over demographic stereotypes for individual proxies.
2. Preserve raw grounding evidence separately from model-generated reflections.
3. Reflections must retain pointers to the observations they synthesize.
4. If the model generates a latent inference, label it `SIMULATED_ESTIMATE` or model-derived reflection.
5. Do not treat demographic parity improvement in one study as proof that a new model/population is unbiased.
6. When repeated human responses are available, use human self-consistency/test-retest as a reference ceiling or reliability benchmark rather than assuming the target is perfectly deterministic.

Rich grounding can increase fidelity and also increase privacy risk. Minimize identifiable storage and default to aggregate output when individual disclosure is unnecessary.

## 5. Population prediction requires a population design

For any population estimate record:

- population definition;
- geography;
- date/time period;
- inclusion/exclusion;
- sampling/coverage source;
- weighting if used;
- sample size;
- action/outcome space;
- missing/unknown handling;
- whether the source is self-report, observed behavior, experiment, or mixed;
- mismatch between grounding population and decision population.

A model that produces 1,000 synthetic agents from ten seed personas has a simulation sample of 1,000. It does **not** thereby have a statistical sample of the real population.

## 6. Scenario and counterfactual specification

Record both a baseline and a change.

```text
Population P
Context C at time T
Baseline B
Intervention/change I
Outcome/action space Y
Time horizon H
```

The question is not merely "What do people think?" It is often:

> `P(Y | P, C, T, do(I))` relative to a relevant baseline.

Behavioral simulation is generally not sufficient to identify a causal effect unless the validation/training design supports the intervention relationship. Use causal language only when warranted by the underlying experiment or design.

### Counterfactual distance

Classify the scenario:

- `IN_DISTRIBUTION` — closely represented in grounding/validation data;
- `NEAR_OOD` — a modest change with related evidence;
- `FAR_OOD` — novel product/policy/context or mechanism with weak analog coverage;
- `UNKNOWN`.

Greater distance lowers warranted confidence unless directly validated.

## 7. Architecture for persistent or multi-agent behavior

When the outcome depends on history, a one-shot persona prompt is insufficient.

The Generative Agents architecture provides a useful pattern:

### Memory stream

Store experience as traceable records.

### Retrieval

Retrieve relevant memory using a combination such as:

- recency;
- relevance to the current situation;
- importance.

Do not let an uninspectable summary replace all underlying events.

### Reflection

Synthesize higher-level inferences from observations. Reflections should cite the records used to create them.

### Planning and reacting

Create longer-horizon plans, then revise them when environment state or new observations warrant it.

### Environment

Represent constraints the agents need to know. Many apparent "reasoning failures" are actually missing environment norms.

### Architecture stress tests

Run ablations when material:

- no memory;
- no reflection;
- no planning;
- alternate retrieval;
- alternate model/version;
- alternate prompt/system framing.

Log common failure modes:

- retrieval failure;
- fabricated memory/embellishment;
- stale memory;
- environment-norm violation;
- over-formality;
- over-cooperation;
- prompt/memory injection;
- feedback-loop amplification;
- stereotype/bias;
- mode collapse/homogenized agents.

## 8. Run design and stochasticity

A single simulation run is often a sample, not "the answer."

Before running, specify:

- model/version;
- system prompt/config;
- decoding parameters where available;
- number of agents;
- number of independent seeds/runs;
- persona/grounding construction method;
- retrieval/reflection settings;
- intervention assignment;
- stopping condition;
- outputs to aggregate.

For probabilistic population prediction, prefer a direct predicted distribution when the model supports it. If estimating from repeated generated samples, report Monte Carlo uncertainty separately from **model error**. A million samples can reduce sampling noise around a biased model without making the model correct.

## 9. Validation: choose the metric for the claim

### Categorical population distribution

Default candidate: Total Variation Distance.

`TVD(P,Q) = 1/2 × Σ_i |P_i - Q_i|`

Range: 0 (identical) to 1 (disjoint).

### Individual closed-form response

Possible metrics:

- accuracy;
- correlation;
- probabilistic log/Brier score where probabilities are available;
- normalized performance relative to human test-retest reliability.

### Ordinal/continuous outcomes

Possible metrics:

- Wasserstein distance;
- MAE/RMSE;
- correlation;
- calibration curves.

### Treatment effects

Compare:

- sign;
- effect-size error;
- rank/order across conditions;
- coverage of uncertainty intervals if modeled.

### Multi-agent/system dynamics

Predeclare empirical statistics such as:

- diffusion rate;
- event incidence;
- network change;
- coordination success;
- norm violation rate;
- time-to-event;
- trajectory distance.

Human ratings of believability can assess realism/usability, but **not predictive validity**.

## 10. Holdout integrity and leakage

A held-out validation set must be unavailable to the mechanism being evaluated.

Choose the split unit that matches the claim:

- person-level generalization → hold out people;
- question generalization → hold out questions;
- study generalization → hold out entire studies;
- condition generalization → hold out treatment conditions;
- temporal generalization → hold out future period;
- geographic generalization → hold out geography.

Do not split individual rows from one experiment across train/test if shared wording, participants, or context leaks the answer.

When questions are semantically clustered, stricter grouping may be needed.

## 11. Separate individual fidelity from distributional fidelity

The SOCRATES results make this distinction explicit: improving the match to the population response distribution can occur without improving individual response accuracy.

Therefore every predictive study declares a **primary unit of correctness**:

- `INDIVIDUAL`;
- `DISTRIBUTION`;
- `TREATMENT_EFFECT`;
- `SYSTEM_TRAJECTORY`.

Secondary metrics cannot silently replace the primary one.

## 12. Calibration and predicted error

Observed validation error answers:

> How wrong was the model on questions where we know the truth?

A confidence/error model answers:

> How wrong is this new simulation likely to be before we collect its ground truth?

These are different tasks.

A valid `L4` process needs:

1. held-out query/run corpus;
2. observed error per item;
3. features/representations available before knowing ground truth;
4. a model/rule predicting error;
5. out-of-sample evaluation of that error predictor;
6. a declared decision-quality threshold;
7. calibration of confidence buckets to actual success rates.

Useful evaluation metrics include:

- RMSE/MAE for predicted error;
- Pearson/Spearman correlation between predicted and observed error;
- AUROC or similar discrimination against the decision-quality threshold;
- calibration by bucket/decile;
- bootstrap confidence intervals where practical.

### What is not enough

- narrow predicted distribution;
- low entropy;
- model says "90% confident";
- repeated agreement across the same model family;
- chain-of-thought confidence;
- one benchmark average;
- a human evaluator saying the synthetic response "sounds real."

Simile's public 2026 work is especially instructive here: simple output/question features were weak predictors of actual error; held-out error prediction performed better when using richer learned representations and dedicated training. The generalizable principle is **empirical error prediction**, not any proprietary implementation.

## 13. Decision-quality thresholds are contextual

There is no universal TVD or accuracy threshold for "good enough."

Define the decision-quality threshold **before** using it:

- what error metric;
- what maximum error;
- why that error preserves the relevant decision;
- what false-positive/false-negative cost matters;
- who accepts it.

A threshold learned from internal raters for one product is not automatically transferable to another decision.

## 14. Subgroup performance and bias

Overall averages can conceal systematic failure.

For decision-relevant subgroups, report:

- sample size/coverage;
- error by group;
- worst-group error;
- gap between best and worst groups;
- whether the gap changed after grounding/fine-tuning;
- whether the subgroup was represented in training/validation.

Do not infer fairness from demographic parity alone. Choose bias metrics that match the task and harm.

## 15. Freshness and drift

Human behavior changes.

Record freshness at the data layer:

- data period;
- last validation date;
- context changes since validation;
- model/data refresh date;
- drift indicators.

Require revalidation when:

- base model materially changes;
- fine-tuning data changes;
- target population changes;
- product/policy/action space changes;
- environment changes;
- observed error exceeds the allowed threshold;
- validation becomes stale for a fast-changing domain.

## 16. Foundation-model inheritance and homogenization

A simulator inherits the base model's:

- training-data coverage and omissions;
- stereotypes and bias;
- instruction-tuning tendencies;
- safety refusals;
- cultural priors;
- hallucination behavior;
- model-family homogenization.

Using many personas on one model is not the same as obtaining many independent human perspectives.

For important decisions, vary model/config or compare against non-LLM baselines where feasible.

## 17. Ethics, privacy, and misuse

Person-grounded agents can infer sensitive information not directly stated. Treat their data as potentially more revealing than the original transcript.

Default safeguards:

- collect/use data with appropriate permission;
- minimize identifiable storage;
- aggregate outputs by default;
- separate public fixed tasks from restricted individual free-form access when appropriate;
- log material model inputs/config and outputs for audit;
- disclose that agents are computational;
- do not encourage parasocial deception;
- do not use the method to impersonate a real person deceptively;
- do not use simulated people as a substitute for stakeholder participation where real people bear the consequences.

## 18. Cross-method handoff rules

### From Lead User Research

Use simulation after real need discovery when the next uncertainty is:

- how a candidate intervention might change behavior;
- what edge cases a design could create;
- which concept probe deserves field testing;
- what real-world validation would be highest value.

Lead User evidence stays Lead User evidence. Simulation outputs use their own namespace and never backfill LU qualification.

### To Opportunity Underwriting

Underwriting may consume a simulation as **model-derived evidence** only.

An `L2` or `L3` result may help prioritize tests or sensitivity ranges. An `L4` result may carry more decision weight within its calibrated scope. None independently establishes actual WTP, adoption, retention, market size, or unit economics.

### To Planning

Simulation can inform working material and risk probes. Human acceptance/promotion gates remain unchanged.

## 19. Valid endpoints

A successful run can end with:

- `EXPLORE` — useful hypotheses/edge cases only;
- `TEST_REAL_WORLD` — simulation identified the highest-value empirical test;
- `USE_WITH_CAUTION` — validated but not decision-calibrated estimate;
- `DECISION_SUPPORT` — L4 estimate within calibrated scope;
- `DO_NOT_USE` — validation, drift, leakage, subgroup failure, or counterfactual distance makes the result unreliable.

The method never authorizes the underlying business/product decision. It states what decision weight the simulation deserves.
