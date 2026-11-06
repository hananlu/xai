# Measurement contract after development calibration

5 November 2026. Components established on development data; this is not yet a frozen full-study statistical protocol.

## Separate the claims

1. **Forecast accuracy** concerns the measured future target. Use MAE/MASE with an explicit denominator and matched origins. Raw GB error across source versus target institutions is confounded by institution scale; do not call that difference a transfer penalty without scale-aware, stratified or matched comparisons.
2. **Numerical/method-specific correctness** concerns the attribution definition. For linear models there is an exact contribution oracle. For grouped Shapley there is an exact 128-coalition game at seven groups. IG needs full-function gradients, integration convergence and completeness; completeness alone cannot certify allocation correctness.
3. **Intervention/ranking usefulness** concerns the response of a specified model to a specified input-change operator. It depends on the operator, group size, ranking budget and direction/cancellation. It is not ground-truth causal demand importance. Neither a large response nor a stable ranking is a universal correctness test.
4. **Reference sensitivity and method agreement** describe different explanation contrasts and allocation conventions. They do not, by themselves, demonstrate a defect. Different valid methods can allocate nonlinear interactions differently.

## What calibration established

On the 12 old development institutions, exact grouped linear contributions reconstruct explicitly queried coalition responses to numerical precision. Uniform, reversed and permuted allocations preserve the total forecast contrast, so they pass completeness, while failing this linear response check. Thus completeness alone is insufficient.

For the nonlinear control f(x1,x2)=x1*x2 at (2,3), baseline (0,0), exact Shapley is (3,3). Additive partial-coalition reconstruction predicts (0,3,3,6) while the true values are (0,0,0,6). The reconstruction residual includes interactions; it cannot be a universal test of Shapley correctness.

The development nonnegative log-Ridge prototype includes log1p, linear predictor, clamp and expm1 in the explained function. Initial IG quadrature failures are retained. A separate adaptive integration follow-up resolves the observed failed cases to the stated tolerances; this is numerical evidence for this prototype only.

## Rules for the full-study protocol

- Preserve a numerical-validation layer distinct from intervention response metrics.
- Freeze group definitions and reference construction before target evaluation. Same source-trained forecaster and same eligible origins across attribution methods.
- Include random and recency controls, method randomization where applicable, and exact linear/grouped-game checks. Recency is a comparator that can be legitimately good, not a necessarily wrong attribution.
- Evaluate rankings with at least two explicitly described input-change operators. An operator used to build a ranking cannot be its sole validation operator. Measure/report induced distribution changes; a training-profile replacement does not guarantee in-distribution inputs.
- Report cumulative responses across several block budgets and inspect opposing signed contributions, following the motivation of [TIMING](https://proceedings.mlr.press/v267/jang25a.html). Their use here is a regression adaptation and requires its own operator controls, not a newly invented metric.
- Attribute the final forecast function, including preprocessing and physical-output constraints. Conditional explanations may freeze context only if that context is disclosed and evaluated consistently.
- Preserve every numerical failure and report inclusion/exclusion rates by institution, reference, horizon and method. A failed integration case is not automatically a failure of model transfer.
- Source/target differences must be evaluated at comparable times with scale-aware institution summaries. Institutions in one ISP, seeds and overlapping windows are not independent networks.

Before the full benchmark is frozen, the response operators, numerical thresholds for neural models, primary endpoint, attribution sample size, random-control repetitions, adaptation schedule and clustered analysis must be specified and development-checked. Source-trained neural feasibility remains outstanding. The 48-institution assignment is frozen separately; no final-target results have been opened for these choices.
