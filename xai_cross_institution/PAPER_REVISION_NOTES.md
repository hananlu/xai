# Paper revision and validity assessment — 6 November 2026

The earlier uploaded paper was the five-page draft, not an automatic expansion of the full notebook. It had one simplified pipeline and one quantitative plot. The full local rerun confirmed its numerical results; the rerun alone did not update the manuscript's presentation.

The revised paper adds an editable overall pipeline and seven result figures (eight figures total), a data/computation-unit table, a real metadata-selected forecast/explanation case, model-capacity and runtime accounting, exact full-rerun evidence, explicit sample-budget limitations, and a more precise statement of what can and cannot be concluded. It now builds its actual bibliography from references.bib. The earlier PDF/TeX are retained under paper/archive_2026-11-05/. This is an expanded working draft; venue page limits remain to be applied.

## Why approximately nine minutes is plausible

The measured full rerun took 529.5 seconds: training 324.3s, forecasting 9.7s, attribution 184.7s, plus 10.8s for notebook diagnostics, analysis and overhead. This is CPU execution on the local Apple M5, 16GB RAM, four threads. It is not a cloud benchmark.

- DLinear has 676 trainable parameters; GRU 3,426. These are compact models.
- The selected data contain 1,116,776 observed institution-hour values (1,147,296 grid slots). Training uses 227,478 eligible, overlapping 168-hour source windows.
- Each neural epoch samples 1,024 windows per source institution: 32,768 samples, not a full pass through every eligible window.
- Eight seed/learning-rate fits executed 201 total epochs, or 6,586,368 sampled window exposures including repeats. Exposures are not independent observations.
- Forecast evaluation covers 3,179 eligible target origins in 15 institution-year cells.
- The XAI audit samples 480 histories per fitted model, and IG uses 120. Seven day groups require 128 coalitions per game. All 5,040 orderings are calculated from cached game responses, not 5,040 separate forward passes.

See results/PAPER_REVISION_FACTS.json, results/FULL_RUN_TIMINGS.json and the full local reproduction snapshot on branch farrel. Runtime by itself does not establish validity or invalidity; the executed workload and sampling unit matter.

## What is supported

The fixed implementation is reproducible: all six neural parameter tensors matched, the primary estimate and interval matched exactly, and independent data/code/metric checks passed. Source/validation/target institution roles and target timestamps are separated as documented. Target outcomes do not select model hyperparameters. Predictions are evaluated against observed eligible labels. The primary analysis averages complete seeds and matched origins and uses institution pairs/time blocks instead of treating repeated queries as independent subjects.

These support a bounded empirical audit of controlled-operator ranking alignment on eligible observations. They do not prove external or causal validity, publication-level novelty, guaranteed bootstrap coverage, equivalence, or general degradation.

## What remains weak or missing

1. Only one ISP and seven complete matched institution pairs support the primary contrast. Raw rows, overlapping windows and seed/query repetitions cannot replace independent deployment units.
2. Attribution sampling is sparse: sixteen shared origins per available pair-year, four for IG. Budget, temporal grouping and block-length sensitivity need a prespecified extension; increasing the existing target sample is exploratory, not a fresh holdout.
3. Missingness and complete-history selection restrict which regimes are tested, especially in 2026. The results need not generalize to missing/interrupted periods.
4. Interpolation/rotation are controlled response tests, not validated conditional traffic replacements. High response can reward brittleness; Q is not a causal truth score.
5. Specialized temporal explanation baselines and an independent network replication are absent. Model/explainer coverage is limited; this is not a state-of-the-art superiority benchmark.
6. The primary interval includes zero; no equivalence margin was prespecified. Secondary intervals are unadjusted for multiplicity. Invalid bootstrap draws are excluded under the frozen rule, so coverage is uncertain in this small incomplete panel.

## Reporting-only additions

Leave-one-pair-out point estimates and the common-accepted Shapley/IG visualization are explicitly post-hoc/descriptive. They do not replace the frozen primary analysis. All primary code/protocol/checkpoint decisions and the headline estimate remain unchanged. The local example is selected by metadata (pair3, target, 2025, earliest sampled origin), not by its error or explanation appearance; its forecast overestimation makes the separation between explanation numerics and accuracy visible.

## Priority for stronger conference evidence

An additional separately specified cohort of previously unevaluated CESNET institutions can increase the number of deployment units while retaining the single-ISP limitation. The highest-value external extension is an independent network or genuinely newly reserved period, followed by a preregistered sampling/grouping budget sensitivity and better-validated replacement mechanisms, with relevant temporal-explainer baselines. More graphs make existing evidence easier to inspect; they do not supply those missing experiments. Conference worthiness depends on the venue and its empirical-study expectations, and is not guaranteed by this revision.
