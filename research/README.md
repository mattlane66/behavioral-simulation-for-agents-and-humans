# Research corpus

This repository's method is built from five unique papers supplied for the project, plus current public methodological material from Simile.

The same arXiv Foundation Models link was supplied three times; it is one unique source.

## 1. Social Simulacra: Creating Populated Prototypes for Social Computing Systems

Joon Sung Park, Lindsay Popowski, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein. UIST 2022.

- DOI: https://doi.org/10.1145/3526113.3545616
- arXiv: https://arxiv.org/abs/2208.04024
- Primary contribution: generate a breadth of plausible interactions from a social-space design and inspect how behavior changes under design interventions.
- Key boundary: the authors explicitly frame the method as early prototyping, not a claim to predict exactly what will happen.

## 2. Generative Agents: Interactive Simulacra of Human Behavior

Joon Sung Park, Joseph C. O'Brien, Carrie Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein. UIST 2023.

- DOI: https://doi.org/10.1145/3586183.3606763
- arXiv: https://arxiv.org/abs/2304.03442
- Primary contribution: memory stream, retrieval, reflection, planning, and reacting for persistent agents whose behavior unfolds over time.
- Key failures: memory-retrieval errors, fabricated embellishments, environmental-norm errors, instruction-tuning artifacts, inherited model bias, and unknown long-horizon robustness.

## 3. Generative Agent Simulations of 1,000 People / revised self-report-grounded work

Original 2024 preprint lineage by Joon Sung Park and collaborators; the arXiv record has since been revised under the title **LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals**.

- arXiv: https://arxiv.org/abs/2411.10109
- User-supplied archive: https://antephase.com/wp-content/uploads/2024/11/Generative-Agent-Simulations-of-1000-People-archive.pdf
- Primary contribution: ground agents in rich self-report data from real individuals and evaluate against those individuals' held-out responses.
- Important evaluation principle: individual simulation should be benchmarked against human test-retest reliability where available, because humans are not perfectly self-consistent.
- Important bias result: richer individual grounding generally reduces performance disparities relative to demographic-only prompting.

## 4. Finetuning LLMs for Human Behavior Prediction in Social Science Experiments

Akaash Kolluri, Shengguang Wu, Joon Sung Park, Michael S. Bernstein. EMNLP 2025.

- ACL Anthology: https://aclanthology.org/2025.emnlp-main.1530/
- DOI: https://doi.org/10.18653/v1/2025.emnlp-main.1530
- Primary contribution: SocSci210, 2.9M responses from more than 400k participants across 210 experiments; fine-tuning for generalization to unseen studies/conditions.
- Key methodological lesson: **individual response accuracy and population-distribution alignment are different objectives** and can move in different directions.
- Key boundary: useful for experimental hypothesis screening; human experiments remain the ground truth.

## 5. On the Opportunities and Risks of Foundation Models

Rishi Bommasani et al. 2021/2022.

- arXiv: https://arxiv.org/abs/2108.07258
- Stanford CRFM report: https://crfm.stanford.edu/report.html
- Primary contribution here: emergence, homogenization, inherited downstream defects, incomplete evaluation, bias, and sociotechnical risk.
- Method implication: never treat a base model as a neutral simulator of humans; model/version choice is part of the causal apparatus and must be logged and tested.

## Product reference: Simile

- Research/product site: https://www.simile.com/#research
- Public methodology on confidence: https://www.simile.com/blog/confidence
- Public methodology on behavioral simulation: https://www.simile.com/blog/what-if-machine

As publicly described in 2026, Simile combines observed behavioral data with interviews/surveys/experiments, validates simulations against real human outcomes, measures distributional error such as Total Variation Distance, trains a separate mechanism to predict likely simulation error, and monitors freshness/drift. These are useful design references. Proprietary mechanisms not publicly documented are **not** inferred.

## Extraction rule

For every source, distinguish:

- what the study actually validates;
- what is plausible but unvalidated;
- what is an implementation pattern rather than an empirical result;
- the unit of analysis: person, population, interaction, or system;
- the ground-truth source;
- the held-out split;
- the evaluation metric;
- subgroup/bias behavior;
- time horizon and out-of-distribution distance;
- limitations and failure modes.

See [`../behavioral-simulation/references/methodology-basis.md`](../behavioral-simulation/references/methodology-basis.md) for the operational synthesis.
