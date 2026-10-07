# Methodology basis

This document records what is operationally carried forward from the research corpus.

## Social Simulacra (Park et al., UIST 2022)

### What was tested

A social-space description—goal, rules, and seed personas—was expanded into synthetic members, posts, replies, and anti-social behavior. The system was used to explore design changes and interventions.

The technical evaluation regenerated 50 subreddits created after GPT-3's release from only community goals/rules and asked participants to distinguish real from generated threads. Participants misidentified an average of 41% of pairs, near chance. A separate study with 16 social-computing designers evaluated design usefulness.

### What the result supports

- synthetic interactions can be plausible enough for design prototyping;
- generating a **breadth** of outcomes can expose edge cases designers did not anticipate;
- intervention probes can help compare how the simulated behavior space changes.

### What it does not support

- exact future prediction;
- population prevalence;
- calibrated causal effects.

### Method carried forward

`PLAUSIBILITY_SPACE` mode:

`design/rules/personas → many possible behaviors → intervention variants → mechanism/edge-case synthesis`

Believability is kept separate from predictive validity.

## Generative Agents (Park et al., UIST 2023)

### Architecture

The paper adds temporal coherence through:

- memory stream;
- retrieval based on recency, relevance, and importance;
- reflection into higher-level inferences;
- planning and reacting;
- explicit environment state.

Controlled ablations showed memory, reflection, and planning matter to perceived believability. End-to-end simulation showed information diffusion, relationship formation, and coordination.

### Failure modes

The paper reports:

- failure to retrieve relevant memories;
- fabricated embellishments;
- environment/norm misunderstandings;
- overly formal or cooperative behavior associated with instruction tuning;
- unknown long-horizon robustness;
- prompt/memory hacking risk;
- inherited model bias;
- risk of over-replacing real human stakeholders.

### Method carried forward

`MULTI_AGENT_DYNAMICS` uses memory/retrieval/reflection/planning only when the question needs temporal/social dynamics. Reflections cite source memories. Architecture is stress-tested with ablations. Narrative coherence is not treated as predictive validation.

## Self-report-grounded agents / 1,000-person lineage (Park et al., 2024+)

The arXiv record supplied as "Generative Agent Simulations of 1,000 People" has been revised. The current version evaluates 1,052 U.S. participants and compares agents grounded in two-hour semi-structured interviews, structured surveys, or both.

### Operational findings

- rich self-report grounding outperforms demographic-only descriptions on many held-out individual tasks;
- a broad interview protocol independent of the downstream evaluation reduces obvious task leakage;
- expert reflections can surface latent implications but are model-generated inferences;
- participants repeated outcome batteries after roughly two weeks;
- model accuracy can be normalized relative to human test-retest consistency;
- richer grounding generally reduced some demographic performance gaps relative to demographics-only prompts.

### Method carried forward

`INDIVIDUAL_PROXY`:

`person's own data → traceable reflections → held-out person responses → error normalized/interpreted against self-consistency where available`

Demographic prompts are a weak baseline, not a substitute for person-specific grounding.

## SOCRATES / SocSci210 (Kolluri et al., EMNLP 2025)

### Study

SocSci210 contains roughly 2.9M individual responses from more than 400k participants across 210 open-source social-science experiments. Fine-tuned models are tested on held-out studies, conditions, outcomes, and participants.

### Operational findings

- training on real experimental response data improves response-distribution alignment on unseen studies;
- generalization to unseen conditions can be tested separately from unseen studies;
- the paper reports both individual accuracy and distribution distance;
- distributional alignment can improve while individual accuracy does not, so they cannot be collapsed;
- subgroup distributional performance and demographic parity differences are explicitly evaluated;
- authors position the technique for experimental hypothesis screening, not replacement of real experiments.

### Method carried forward

`POPULATION_PREDICTION` requires a declared unit of correctness and held-out split at the right level. Population-distribution accuracy is primary when the decision concerns prevalence/share. Individual accuracy remains a separate metric.

## Foundation Models (Bommasani et al.)

### Operational findings

Foundation models exhibit emergence and encourage homogenization because many downstream systems inherit the same base. Defects of the base model propagate downstream. Capabilities, failures, and societal effects are incompletely understood and are sociotechnical rather than purely technical.

### Method carried forward

- model/version/config is part of the measurement instrument;
- calibration is not automatically portable across model upgrades;
- many agents from one base model are not independent human samples;
- inherited bias/safety/instruction-tuning behavior must be stress-tested;
- evaluation must match the downstream use.

## Simile public methodology (2026)

Simile publicly describes a model taking population + situation + valid action space and returning a distribution over actions. It says training combines observed behavior (e.g., transactions/app behavior) with interviews/surveys/experiments.

Its public confidence methodology compares simulated vs observed distributions using Total Variation Distance, then trains a separate mechanism to predict expected error on new simulations. The published example evaluates the error predictor on held-out questions with cross-validation and reports metrics such as RMSE, AUROC, and correlation. Simile also publicly describes freshness/drift monitoring.

### Method carried forward

- observed error and predicted future error are separate;
- confidence must be empirically tied to held-out error;
- simple output confidence features are not assumed sufficient;
- decision-quality thresholds are explicit and calibrated;
- freshness/drift is a first-class dimension.

### What is not carried forward

No proprietary Simile architecture, data, confidence threshold, or internal model is assumed. Publicly reported thresholds are examples, not universal standards.

## Synthesis

The papers form a ladder:

```text
plausible behaviors
      ↓
temporally coherent agents
      ↓
person-grounded prediction
      ↓
population-grounded prediction
      ↓
held-out error
      ↓
predicted error / decision calibration
```

The repository deliberately keeps the earlier rungs useful rather than pretending every simulation must or can become predictive.
