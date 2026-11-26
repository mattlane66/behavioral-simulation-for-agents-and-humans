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

The [November 16, 2026 revision (v4)](https://arxiv.org/abs/2411.10109v4) compares five grounding conditions across 1,052 U.S. adults. On held-out General Social Survey items, demographic, interview, survey and combined grounding scored 60.4%, 69.4%, 69.3% and 72.8%; two-week human test–retest agreement was 79.5%. The richer input did not improve incentivized economic choices. Across eight distortion measures, combined grounding reduced seven, with a median 53.5% gap closure; it did not reduce hyper-rationality. Across five replicated experiments, the median simulated-to-observed Cohen's d ratio was 4.9 even with combined grounding (Table 1). These are task-specific results, not adoption forecasts, a correction factor, or validation of this skill. Fine-tuning on other participants' answers to target questions is a different supervision regime. Start with a simple elicitation and grounding baseline; only introduce expert reflections, retrieval or elaborate prompts if ablations show benefit for the task. Treat those reflections as model-derived.

### Method carried forward

For predictive use, predeclare distortion checks relevant to the outcome and compare against held-out human data: mean bias; compressed variation/tail loss; distributional distance; excess inter-item correlation; dimensionality collapse; excessive association with group attributes; inflated intervention effects (direction and magnitude, including near-zero effects); and over-rationalized or over-cooperative behavior. Record metric, comparator, uncertainty, limitations and NOT_ASSESSED where data are absent. Do not equate low distortion on one task with calibration on another. In plausibility-only runs, use these as qualitative risk probes, not measured claims. When lead users or unusual behaviors matter, explicitly preserve rare mechanisms and counterexamples. Test incentivized or revealed behavior directly before assigning economic decision weight.

Use person-specific observations, a task-independent grounding design and a human reliability benchmark where available. Keep individual fidelity and aggregate fidelity distinct.

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
