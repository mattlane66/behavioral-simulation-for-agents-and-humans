---
name: behavioral-simulation
description: Explore or predict how defined people or populations may respond under changed conditions using explicit simulation modes, evidence grades, held-out validation, calibration, and hard separation between simulated estimates and observed human evidence.
license: MIT
---

# Behavioral Simulation

Use this skill when the decision depends on a counterfactual about human behavior:

- How might this population respond if the price, product, policy, message, interface, or market condition changed?
- Which behavioral mechanisms or edge cases should we investigate before fieldwork?
- Can an interview-grounded proxy reproduce a specific person's held-out responses?
- How might interactions among many agents produce emergent outcomes over time?
- Is a simulation validated well enough to carry decision weight?

Read [`PROTOCOL.md`](PROTOCOL.md) for the canonical method.

## Governing rule

> **Generated behavior is a model output. It is never observed human evidence.**

Calibration can justify more decision weight. It cannot change the source type.

## Two axes: mode and grade

### Simulation mode

Use exactly one primary mode:

- `PLAUSIBILITY_SPACE` — explore a breadth of possible behavior and mechanisms. No population prediction claim.
- `INDIVIDUAL_PROXY` — simulate a specific person using person-level grounding.
- `POPULATION_PREDICTION` — predict an aggregate response/action distribution for a defined population.
- `MULTI_AGENT_DYNAMICS` — simulate interaction, memory, diffusion, coordination, and emergent behavior over time.

A study may include secondary analyses in other modes, but each run has one mode.

### Evidence grade

Assign the highest grade whose requirements are actually met:

- `L0_ROLEPLAY` — model prior + prompt + assumptions only.
- `L1_PERSON_GROUNDED` — real person-level self-report or behavioral grounding; not population evidence.
- `L2_POPULATION_GROUNDED` — real population/experiment/behavioral data with defensible sampling or coverage.
- `L3_HELD_OUT_VALIDATED` — L1/L2 plus relevant held-out human outcomes and computed error.
- `L4_DECISION_CALIBRATED` — L3 plus predeclared decision metric/threshold, query-class calibration, subgroup checks, and freshness/drift controls.

`L4` is not "the model seems good." It requires evidence that the **error estimate itself** is useful on held-out queries.

## Core workflow

1. **FRAME** — define decision, population, baseline, intervention/scenario, outcome/action space, time/context, and harm if wrong.
2. **GROUND** — register observed human evidence, nonhuman context, assumptions, sampling/coverage, and model prior separately.
3. **SPECIFY** — choose mode, target grade, unit of analysis, model/config, run count, counterfactual distance, and success/error metrics before seeing results.
4. **RUN** — execute simulations while preserving run-level provenance and stochastic variation.
5. **VALIDATE** — compare with held-out real human/behavioral outcomes using a task-appropriate metric. Keep individual accuracy separate from population alignment.
6. **CALIBRATE** — if decision weight is requested, estimate likely error for new queries from held-out validation. Do not substitute entropy, verbal certainty, or self-reported confidence.
7. **STRESS_TEST** — examine subgroup error, model sensitivity, prompt/config sensitivity, temporal drift, counterfactual distance, and rival mechanisms.
8. **DELIVER** — report the simulation as `SIMULATED_ESTIMATE`, with grade, error, scope, and the highest-value real-world validation next.

The valid route is not always all eight phases. `L0_ROLEPLAY` can stop after RUN/STRESS_TEST/DELIVER. A claimed `L4` cannot skip held-out validation and calibration.

## Hard prohibitions

- Never call synthetic personas, simulated respondents, generated interactions, or model role-play "human evidence."
- Never estimate population percentages from `L0_ROLEPLAY` or `L1_PERSON_GROUNDED`. You may summarize the simulated sample, but label it as **simulation output only**.
- Never infer a population from one or a few hand-authored personas.
- Never use demographics-only prompting as if it were a high-fidelity individual model.
- Never use model verbal confidence, token probability, entropy, or a narrow-looking simulated distribution as calibrated confidence unless independently validated for that use.
- Never reuse the same human outcomes for grounding/training and call them held-out validation.
- Never hide evaluation leakage by splitting rows when the same question/experiment/sample appears across train and test. Split at the appropriate study/question/person unit.
- Never collapse **individual response accuracy** and **population distribution alignment** into one metric.
- Never use "believability" or human inability to distinguish synthetic text from real text as evidence of predictive validity.
- Never claim a counterfactual is calibrated when the validation set contains only in-distribution factual or historical questions.
- Never present `L4_DECISION_CALIBRATED` without a predeclared decision-quality metric/threshold and evidence that predicted error discriminates held-out good/bad simulations.
- Never let a simulation independently establish willingness to pay, adoption, retention, market size, or unit economics.
- Never let multi-agent narrative coherence substitute for empirical validation of system dynamics.
- Never omit model/version and configuration from a material run.
- Never allow a model upgrade to silently inherit the prior model's calibration.
- Never suppress subgroup performance gaps behind an overall average.
- Never use behavioral simulation as the sole basis for a consequential medical, legal, credit, employment, insurance, safety, or other high-stakes decision about real individuals.

## Mode-specific method

### `PLAUSIBILITY_SPACE`

Use the Social Simulacra principle: generate a **breadth** of plausible outcomes, including undesirable and surprising ones, then test whether changes in rules/design/interventions shift the space.

The output language is:

> "The simulation surfaced these plausible behaviors/mechanisms..."

not:

> "Users will do X."

Sample across prompts/seeds where practical. Deduplicate superficially different versions of the same mechanism. Preserve minority/edge behaviors.

### `INDIVIDUAL_PROXY`

Require person-specific grounding for `L1+`.

Prefer the person's own interviews, survey responses, behavioral traces, or artifacts over demographic stereotypes. Keep direct observations separate from model-generated reflections.

For evaluation, compare the agent with the person's held-out responses. When repeat human responses exist, benchmark against human test-retest consistency rather than assuming 100% self-consistency.

Expert/domain reflections may help extract latent implications, but they are **generated inferences**, not new observations. Preserve pointers to the grounding records that support each reflection.

### `POPULATION_PREDICTION`

Define the target population and coverage explicitly.

Predict the **distribution** over a closed action/outcome space when possible. Evaluate distributional alignment against held-out human data. For categorical responses, TVD is a useful default:

`TVD(P,Q) = 1/2 × Σ |P_i - Q_i|`.

Also report individual response accuracy if relevant, but do not assume optimizing one optimizes the other.

For treatment/intervention questions, validate effect direction and magnitude on held-out conditions, not merely overall response frequency.

### `MULTI_AGENT_DYNAMICS`

Use memory, retrieval, reflection, planning, reacting, environment state, and interaction rules when the outcome depends on temporal coherence.

A practical memory retrieval design can combine:

- recency;
- relevance to the current situation;
- importance.

Reflections must cite the underlying observations they synthesize.

Validate modules with ablations when architecture choices are material. Log retrieval failures, fabricated memory, norm/environment errors, over-cooperation, instruction-tuning artifacts, and cascading feedback.

## Validation and calibration

Pick the metric before looking at the answer.

Examples:

- categorical distribution → TVD;
- ordinal/continuous outcome → Wasserstein distance, MAE, or another justified metric;
- individual closed-form response → accuracy/correlation plus human test-retest benchmark when available;
- treatment effect → error in effect size, sign, and ranking;
- ranking/choice → appropriate ranking or probabilistic score;
- temporal/system dynamics → predeclared empirical event/rate/trajectory statistics.

`L3` requires actual held-out comparisons.

`L4` additionally requires a calibration mechanism. At minimum:

1. a set of held-out simulation questions/runs;
2. observed error for each;
3. features/representation available at inference time;
4. out-of-sample predicted error;
5. a predeclared decision-quality threshold;
6. discrimination/calibration metrics for predicted error;
7. subgroup and freshness analysis.

A high-confidence label must mean something empirical, for example:

> On held-out queries in this class, runs assigned this bucket met the decision-quality error threshold X% of the time.

If that sentence cannot be completed honestly, do not call the estimate calibrated.

## Foundation-model inheritance

Treat the base model as part of the instrument.

Record:

- provider/model/version;
- date;
- prompt/system configuration;
- decoding/sampling parameters when available;
- retrieval/reflection architecture;
- training/fine-tuning data description when known;
- safety/instruction-tuning behaviors that could distort human simulation.

Revalidate after material model or data changes.

## File-backed execution

Initialize with `scripts/init_study.py`, then use `scripts/next_simulation_move.py`, `scripts/calculate_metrics.py`, and `scripts/validate_study.py`.

The structured state outranks a polished narrative. If the report disagrees with persisted grade, validation, or evidence type, the report is invalid.

## Human-facing output

Use [`templates/simulation-report.md`](templates/simulation-report.md).

The report must make clear:

- what was simulated;
- why;
- simulation mode;
- evidence grade;
- observed grounding vs assumptions;
- simulated estimate;
- validation metric and held-out coverage;
- calibration status;
- subgroup/drift/model sensitivity;
- what the result supports;
- what it does **not** support;
- the highest-value real-world test.

## Cross-method handoffs

Use [Lead User Research](https://github.com/mattlane66/planning-skills-for-agents-and-humans/tree/main/lead-user-research) when the unknown is an emerging need, advanced user behavior, workaround, or unarticulated problem that should be discovered rather than simulated.

Use [Opportunity Underwriting](https://github.com/mattlane66/opportunity-underwriting-for-agents-and-humans) when the unknown is whether an evidenced need forms a sufficiently large, reachable, economically attractive market.

Use [Planning Skills](https://github.com/mattlane66/planning-skills-for-agents-and-humans) when the opportunity is accepted and the next question is what to make and how.
