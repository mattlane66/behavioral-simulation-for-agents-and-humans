# Calibration and confidence

## Three different uncertainties

Do not collapse:

1. **Monte Carlo uncertainty** — noise from a finite number of simulation samples.
2. **Model error** — distance between the simulator and real human outcomes.
3. **Error-prediction uncertainty** — uncertainty in the mechanism estimating model error for a new query.

More simulation samples can shrink (1) while leaving (2) unchanged.

## Distribution error

For closed categorical outcomes, use TVD when appropriate:

`TVD(P,Q) = 0.5 * Σ |P_i - Q_i|`

A binary percentage error is a special case, but keep the full distribution when there are more than two actions.

## Calibrated confidence

A confidence bucket is valid only if it has an empirical interpretation from held-out queries, such as:

> 93% of held-out runs assigned HIGH met the predeclared decision-quality threshold.

Do not define HIGH because the model "sounds sure."

## Split discipline

Keep semantically linked samples together. Depending on the claim, group by:

- question;
- experiment/study;
- participant;
- treatment condition;
- topic cluster;
- time period;
- geography.

Leakage makes confidence estimates look better than they are.

## Decision threshold

Predeclare:

- metric;
- allowed error;
- rationale;
- decision consequence;
- revalidation date/trigger.

A threshold from another product or study is a reference class, not a law.
