# Full protocol v1: cross-institution temporal attribution reliability

Frozen before final target evaluation, 5 November 2026. No new target forecast outcomes have been scored at freeze. Development prototypes and all previous pilots are exploratory. The benchmark distinguishes numerical attribution correctness, operator-specific ranking usefulness and forecast accuracy; none implies real-world causal demand attribution.

## Dataset, split and eligibility

CESNET-TimeSeries26, official institutional hourly n_bytes, GB = bytes/1e9. Verify source member hashes against the previous 2024-only selection audit. Native time mapping determines hourly coverage; require six native ten-minute records, observed finite nonnegative values and no conservative probe-artifact flag. Exclude complete histories crossing unavailable hours; do not impute labels or treat absent values as traffic zeros. The conservative 2024-05-21–06-04 flag is a global screening choice, not a claim that every institution was affected.

History: 168 hours; direct endpoint targets at h={1,6}. Both target hours and all history must be eligible. All models share origins within each institution. No source-context or target values used for fitting extend past their stated split boundary.

The pre-existing 32-source/8-validation/8-target institution assignment is fixed in INSTITUTION_SPLIT.csv, outside 12 development institutions. Eight source–target pairs are fixed in MATCHED_PAIRS.csv using 2024 median volume and coefficient-of-variation descriptors, one-to-one within the four volume strata. Matching does not equalize all traffic properties or establish a causal transfer effect. All institutions belong to one ISP; no cross-operator generalization claim.

Source fitting: all eligible 2024 target times. Validation: January–March 2025 at the eight validation institutions, target endpoints strictly before 1 April. No target-institution scaling or hyperparameter fitting.

Final evaluation periods: [2025-04-08,2025-07-01) and [2026-04-08,2026-07-01), interpreted in UTC by target timestamps. Forecast metrics use origins with UTC hour divisible by six. Explanation sampling: for each fixed pair and period, intersect eligible source/target origins and select 16 evenly spaced indices; if fewer, retain all and report counts. Selection uses availability, never errors or attribution scores. IG uses four evenly spaced indices from the selected 16. Source and target explanation cases are timestamp-matched per pair.

## Forecast models and tuning

Predictors operate on log1p(GB) histories. Final GB output is expm1(max(0, predicted_log)), including adaptation offsets where applicable. Explain this complete function. No target-specific normalizer. DLinear/GRU use a scalar mean/std fitted only to pooled source training inputs; include the normalization in the model wrapper.

- Persistence, daily and weekly seasonal-naive at the correct endpoint lag.
- Ridge: alpha {0.1,1,10,100}, independently selected per horizon by equal-institution validation MAE in log units. Source samples pooled; no target data fitted.
- DLinear: moving-average kernel 25, replicated endpoint padding, separate trend/seasonal 168-to-2 linear maps, direct h=1/6 heads.
- GRU: one 32-unit recurrent layer, two-output correction added to the last observed log value; head initialized to zero.

Neural models: Adam, batch 256, learning rates {0.001,0.0003}; at most 30 epochs, early stopping after five epochs without improved equal-institution validation log-MAE. Each epoch samples 1,024 windows with replacement per source institution to balance institutions. MSE loss in log units, gradient norm clip 1.0. Select learning rate using seed 42; reuse its selected checkpoint and fit seeds 123 and 2026 with the selected setting. No expansion of the grid using final results. CPU four threads; record actual runtime.

Forecast metrics: per-institution/horizon MAE, RMSE, weekly seasonal MASE, negative and zero prediction fractions. MASE denominator uses eligible 2024 observed weekly pairs at that institution and a 1e-9 GB floor; this is evaluation scaling, not target model fitting. Report macro institution summaries and matched-pair comparisons. Different institution raw-GB error levels alone are not a transfer penalty.

## Secondary adaptation

Per model, institution, horizon and evaluation year, calibrate a single additive log-output bias using the median residual from eligible target timestamps in [April 1,April 8). Require >=24 calibration examples; otherwise use zero bias and mark insufficient calibration. This also applies to matched source institutions. No neural fine-tuning. Evaluate both frozen and calibrated functions on exactly the same later origins. Call the latter target-aware bias calibration, not zero-shot deployment. Calibration data precede evaluation and are excluded from its target set.

## Explanation definitions

Seven consecutive 24-hour groups, ordered oldest to latest. Source-calendar reference: median GB at each hour-of-week from source 2024 observations. History reference: median across the seven days at each aligned hour position of the current observed history, repeated across days. It uses available input and defines a different contrast; neither reference is guaranteed in-distribution or universally correct.

Exact grouped Shapley: query all 128 coalitions for the stated reference-replacement game; factorial weighting. Check efficiency within 1e-8 GB + 1e-6*absolute forecast contrast. Grouped occlusion: absolute prediction change on individually replacing a group by that same reference. Random order and newest-first are controls. Rank IG/Shapley by absolute **signed group sum**, not sum of absolute point attributions. Ties are broken deterministically by a hash of case/group identifiers and shared across methods.

IG on the four-origin subset, frozen forecasters only: raw-GB straight path through all preprocessing/output operations. Gauss–Legendre nodes {32,64,128,256,512}; accept only if completeness <=1e-8 GB +1e-3*absolute contrast AND L1 change from preceding level <=1e-8 GB +1e-3*L1 attribution. Keep and report every failure; no final-data tolerance relaxation. Comparisons involving IG use common accepted cases, alongside all-case Shapley results and acceptance rates. No claim that efficiency alone proves allocation correctness or that IG and Shapley must agree on nonlinear interactions.

Shapley/occlusion: both references, frozen and bias-calibrated models, all selected origins. IG: both references, frozen models, four-origin subset. Ridge is deterministic; neural scores are averaged over three seeds before institution inference.

## Controlled intervention endpoints

Assess ranking usefulness against two fixed replacement templates, independently of explanation references:

1. **Within-day interpolation:** replace each selected 24-hour block by a straight interpolation between that block's original first/last values. It preserves endpoint/level information and suppresses internal variation; it is not complete feature deletion.
2. **Day rotation:** shift the seven observed day blocks cyclically by one day and use the corresponding rotated block for each selected replacement. All values come from history already observed at forecast time. It perturbs temporal placement and is not a claim of a plausible naturally occurring event.

For each operator, query all 128 replaced-group subsets. For an ordering pi and k in {1,2,4}, CPD_k sums absolute successive forecast changes after replacing the first 1..k groups. U(pi) is the mean of CPD_1, CPD_2 and CPD_4. This is a regression response adaptation motivated by TIMING, not a new universal fidelity metric.

Enumerate all 5,040 day orderings from these responses: R is their exact mean U (random control), O their maximum U (operator-specific oracle upper bound, not a deployable policy). Ranking score Q=(U-R)/(O-R). If O-R <=1e-9 GB (one byte), mark the operator/model case non-discriminating; never divide by a tiny gap, fabricate zero or silently remove the failure. Negative Q is allowed; Q>1 beyond numerical tolerance is an implementation error. Report exclusions by cohort/method. Operator-specific oracle and random are obtained from identical model queries, without future target labels.

Q measures ranking alignment to the stated intervention game. It is not real-demand causal correctness, a universal Shapley/IG correctness test, or a calibrated forecast-risk probability. Different reference questions can yield different alignments legitimately. Record relative log-input RMS changes for each template; value support checks cannot certify temporal in-distribution perturbations.

## Primary and secondary analysis

Primary endpoint: for frozen GRU, h=1, source-calendar Shapley ordering, compare target-minus-source Q in the eight fixed pairs, averaging over operators, periods and seeds. Use pair-matched valid operator cases; preserve all original records/exclusions. This is a descriptive deployment contrast, not a causal effect of institution identity.

95% intervals: 2,000 paired bootstrap replicates, first resample institution pairs, then resample 14-day calendar blocks within pair; keep source/target, seeds, operators and methods together. Effective institution sample is eight related pairs; intervals do not justify cross-ISP inference. If fewer than four pairs have valid primary data, do not report an inferential headline; report the failure of the endpoint to support it.

Secondary endpoints: DLinear/Ridge, h=6, local-history reference, occlusion/recency, IG on its accepted subset, change under log-bias calibration, per-period and forecast-MASE contrasts. Label exploratory/multiplicity clearly; do not promote a winning secondary comparison to the primary claim. Inspect signed attribution cancellation and reference dependence without calling all changes failures.

A successful study can show preserved, degraded or operator-dependent alignment. No desired sign, method superiority, new architecture or guaranteed conference novelty is presupposed. Final paper must state the closest prior-work overlap, one-ISP scope, small number of pairs, controlled-operator limitations, and any negative/inconclusive result.

## Freeze and execution rules

Hash this protocol, institution/pair assignments and executable sources before opening final performance outcomes. Source/validation fitting may then proceed. Correct implementation failures with logged amendments and retained snapshots; do not change hypotheses, eligibility, metrics or thresholds based on final outcomes. All data hashes, checkpoints, predictions, selections and case-level explanations are retained. Paper/PPT statements must be generated from final saved results; v1/v2 and development results remain clearly separated.
