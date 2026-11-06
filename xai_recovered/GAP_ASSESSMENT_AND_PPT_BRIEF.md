# Gap assessment and future presentation brief

5 November 2026. Assessment of the completed preliminary case study; no additional experiments are authorized or run by this note.

## Current evidence

The recovered aggregate has 40,298 observations and the common test set has 5,806 origins. Fifteen recurrent fits cover three seeds for five conditions. The 10-minute MAEs are 8.869 GB for Ridge, 8.883 GB for last-state LSTM, and 10.340 GB for learned Attention with 24-hour context. These are valid descriptive findings for the tested setup, not evidence that all attention architectures are inferior.

## Gaps and priorities

| Priority | Gap | What would address it |
|---|---|---|
| High | Aggregate construction and institution membership are not recovered. | Recover the aggregation procedure or obtain documented component series before making official-subset/network-wide claims. Current results remain a recovered-data case study. |
| High | Only one aggregate and one chronological holdout; three seeds repeat training, not independent datasets. | Rolling-origin robustness checks and independently sourced series with clear provenance; confirmatory claims need genuinely unseen data because current test results have already been inspected. |
| High | Pooling variants perform poorly under a fixed, limited configuration. | Validation-only tuning and controls for capacity/optimization. Broader architectures such as GRU, DLinear or PatchTST are candidate comparators, not currently executed results. |
| High | Residual persistence versus learned correction is not isolated by training ablations. | Train with/without the skip connection and compare prediction paths; retain the current secondary path diagnostic as exploratory. |
| High | IG is numerically provisional; attention-versus-random evidence is replacement dependent. | Independently cross-check IG, specify convergence criteria, and use direct perturbation controls with confidence intervals. Do not equate large shifts with causal explanation. |
| Medium | Fixed median replacements can create unrealistic temporal sequences; no ground-truth attribution exists. | Temporal replacement controls and synthetic signals with known influential lags, while distinguishing generator relevance from actual model reliance. |
| High | The literature expansion is targeted, mostly at metadata/abstract level, not a completed full-text novelty audit. | Read the closest network-XAI and temporal-interpretability papers in full and map their tested mechanisms, controls, metrics and datasets against the proposed contribution. |

These are research-development needs. They do not invalidate the completed artifact integrity checks or the saved descriptive forecasting results.

## Novelty assessment

Already established: LSTM/Attention forecasting; XAI applied to network traffic; comparing prediction and interpretation quality; temporal perturbation/IG methods; broad CESNET forecasting comparisons. Relevant direct precedents include [AIChronoLens](https://dspace.networks.imdea.org/handle/20.500.12761/1917), [DeExp](https://dspace.networks.imdea.org/handle/20.500.12761/1889), [CESNET model comparisons](https://arxiv.org/abs/2503.17410), [attention interpretability benchmarking](https://doi.org/10.3390/e23020143), and [TIMING](https://proceedings.mlr.press/v267/jang25a.html).

The present work has **candidate empirical value**, not a verified novel algorithm. Its defensible question is: under which conditions do temporal hidden-state attention rankings describe input influence in short-horizon network forecasting, especially when a persistence residual contributes outside the attention path?

A stronger contribution would jointly evaluate pooling/scoring choices, residual-path ablations, temporal replacements and attribution numerical reliability across documented series/horizons. It must demonstrate a specific, reproducible finding that the closest prior studies have not already covered. Naming this a new protocol is insufficient by itself; first/novel claims remain unconfirmed.

Current positioning: preliminary reproducible empirical case study with useful negative/inconclusive findings. Publication novelty and readiness are not established by reference count, model count or a finished PDF.

## Presentation requested for later

The user requested the deck later. No PPT is created now. Preserve the exact first-three-slide structure:

1. **Opening:** network capacity-management motivation and the question of trusting temporal attention.
2. **Research gap and goal:** narrowly scoped candidate gap, prior-work context, and goals to evaluate prediction accuracy and explanation reliability separately. Label unresolved novelty honestly.
3. **Pipeline diagram:** recovered data -> provenance/timestamp audit -> chronological split and common origins -> windowing/train-only scaling -> forecasting models -> parallel forecast evaluation and explanation audit -> bounded conclusions.
4. **Results: 10-minute forecast:** MAE/RMSE, baselines, three-seed variability and exact units.
5. **Results: 60-minute forecast:** same comparisons and targets.
6. **Results: pooling/context ablation:** 24/48-hour contexts and seed variation; no universal attention claim.
7. **Results: XAI interventions:** attention/occlusion/recency/random rankings under both replacements, including uncertainty.
8. **Results: numerical reliability:** IG completeness failures and residual-versus-correction interpretation scope.
9. **Findings, limitations and next experiments:** distinguish demonstrated results, unresolved explanations and proposed work.
10. **Selected references:** closest network forecasting/XAI and temporal-explanation studies; full bibliography in notes or appendix.

Do not present planned experiments as completed or the candidate gap as established novelty. The current results may support a progress/research-discussion presentation; strengthen the research before representing the deck as a final contribution.
