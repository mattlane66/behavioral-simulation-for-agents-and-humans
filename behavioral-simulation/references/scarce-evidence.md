# Simulation-assisted discovery and scarce human evidence

Status: proposed operational extension; computation is not empirical validation. The governing protocol and its evidence grades remain authoritative.

## Route uncertainty, not every study through every model

Invoke simulation before, during or after empirical discovery when a decision-critical unknown has a useful counterfactual or hypothesis-generation formulation. It may precede a qualified lead user; that route is L0 unless independently eligible grounding exists. It must not supply a missing human observation.

| Uncertainty | Mode | Output and boundary |
|---|---|---|
| Unseen circumstances, needs, search terms, rivals, abandoned workarounds | PLAUSIBILITY_SPACE (Social Simulacra) | Candidate mechanisms and search directions; no population frequencies |
| How a real person might respond outside the observed episode | INDIVIDUAL_PROXY (self-report-grounded agents) | Person-specific hypotheses with source refs; no invented biographical facts |
| Distribution over a defined real population or measurable survey outcome | POPULATION_PREDICTION (SocSci210) | Only with defensible real population grounding; otherwise exploratory scenarios |
| Diffusion, learning, constraints and changing frontiers | MULTI_AGENT_DYNAMICS (Generative Agents) | Assumption-conditioned trajectories; validate system outcomes, not narrative realism |

Use the smallest eligible mode(s), one mode per run. Foundation-model inheritance applies to every run. Compare prompt/config/model sensitivity, retain disconfirming behavior and log all decisions. More draws from one model reduce Monte Carlo noise only, not model bias or empirical sample scarcity. Simile-style calibration requires independent held-out error prediction, not fluent confidence.

## Cycle and handoff

1. Record decision, specific unresolved variable, existing evidence refs, why additional real data are scarce, target scope and counterfactual distance. Keep unknowns open.
2. Select mode, grade ceiling, scenario, assumptions, model/config and test metric before generating. Person/ population grounding require actual data and permissions.
3. Produce a separate run (SIMULATED_ESTIMATE), including rival mechanisms, potential search routes or tests, and why each would change the decision.
4. Return only hypotheses, search queries, fieldwork priorities or scoped model estimates to the caller. A suggestion of a person or source must be independently located and inspected; don't invent identities or citations.
5. Collect real observations and attach new evidence through the caller's normal qualification/review process. Compare predicted and actual results; revise or reject the hypothesis. Never backfill LU1/LU2, interview evidence, coding, cluster membership, sufficiency, independent lineage or propagation from simulation. Keep generated cases separate from observed counts and freeze corpus.
6. Stop when further simulation has little information value, or route to targeted fieldwork; insufficient evidence remains valid.

## Optional measurement: SSR

Maier et al., [arXiv:2510.08338v3](https://arxiv.org/html/2510.08338v3), compare textual elicitation with direct numeric ratings. Predeclare a fixed ordinal attitude construct and verbal anchors, embed responses and anchors with one versioned embedding model, map cosine similarities to a distribution, and compare anchor sensitivity and real holdout performance. The existing [Scaled Interview implementation](https://github.com/mattlane66/scaled-interview-data-assistant/blob/38b85c697526123491ab01363b1a3f03313e15e2/simulation/ssr.py) remains the reference executable adapter (including provenance). Do not duplicate its schema/embedding pipeline or apply ordinal ratings to unobserved episodes. The shared primitive below is extracted from that implementation, not a new independent algorithm. No claim about actual buying or switching. The paper's correlation attainment is a ranking metric relative to human reliability, not individual accuracy.

## Optional statistical correction: fixed-weight PPI mean

Krsteski et al., [ACL 2026](https://aclanthology.org/2026.acl-long.498/) ([preprint equations 1–3](https://arxiv.org/html/2510.11408v2)), study synthesis plus rectification. For a scalar, question-specific target mean, use predictions on a disjoint real covariate sample U and real labeled sample H with paired predictions from the same frozen predictor. Under independent i.i.d. samples from the same target distribution and a predictor independent of inference samples, with fixed predeclared lambda in [0,1]:

    estimate = lambda * mean(predictions_U) + mean(y_H - lambda * predictions_H)
    estimated variance = lambda^2 * sample_var(predictions_U)/N + sample_var(y_H - lambda * predictions_H)/n

lambda=0 is the human-only baseline. Compare precision to that baseline; poor predictions can make full correction less efficient. The paper found power tuning useful in its studied surveys, not universal; subgroup bias can worsen. This first implementation supports fixed weight only; no optimized PPI++, complex survey weights, causal effects, confidence intervals, or automatic grade promotion. Do not select lambda on the inference outcomes. A separate tuning sample and valid inference procedure would be required. Do not use convenience lead-user interviews as a representative labeled sample, fictitious covariates, repeated synthetic draws as independent units, or use rectification to invent missing individual answers. The result is a model-assisted estimate, not observed human evidence.

## Fidelity stress tests

Bisbee et al., [Political Analysis 2024](https://doi.org/10.1017/pan.2024.5), show that matching means can mask compressed variance and distorted relationships; outputs shift with model and prompt. Compare mean, variance, distribution, subgroup errors and conditional relationships on relevant human holdouts; log prompt/model/time sensitivity. Averages alone cannot establish fidelity. The shared diagnostic computes means, sample variances and paired Pearson correlation only; other tests are explicit obligations, not implied by the function.

## Reproducible computational slice

`python behavioral-simulation/scripts/scarce_evidence.py input.json output.json` accepts a JSON request with operation `rectify_mean`, `ssr` or `fidelity`. See the tests for examples. The script refuses overlapping/duplicate person IDs and requires explicit design attestations for correction; those attestations are not independent verification. Keep it outside evidence banks. Run `python -m unittest discover -s tests -p test_scarce_evidence.py`. No provider calls, external data transfers or dependency installs.

## Integration acceptance

- Lead User Research: optional discovery/repair/interpretation lane, never qualifies generated cases.
- Scaled Interview Data Assistant: optional after actual reviewed checkpoint; preserve all original evidence/codes and human review/permission gates; use shared method without overwriting existing SSR results.
- Empirical benchmark needed: compare search-only and simulation-assisted discovery under equal budget on blind source corpora; independently score new real qualified episodes, refutations, diversity, precision and time. For population claims compare human-only, raw model and rectified estimators on held-out real data. No scientific effectiveness claim before evaluation.
