# Recovered XAI forecasting: protocol frozen before new training

Date: 5 November 2026. Status: design; results will be generated separately.

## Research question and scope

For the recovered CESNET aggregate, does learned temporal Attention improve short-term byte-volume forecasting over simple and matched recurrent baselines, and does its temporal ranking track sensitivity to input perturbations? This is an empirical evaluation, not a claim of a novel attention architecture or causal explanation.

Only Google Drive and user-provided files supply project data/code. Public primary literature is used to update methodological references, not to replace missing project artifacts. No external replacement dataset is added. The initial six-week plan is historical; no start date is inferred.

## Recovery findings

- Primary data: `global_bytes_10min.csv` and `times_10_minutes.csv` from Drive farrel/xai, joined one-to-one by id_time. 40,298 rows, 9 October 2023 to 14 July 2024 UTC. All recovered byte values are positive and finite. Exact upstream aggregation code and institution membership are missing, so call this a **recovered CESNET-derived aggregate**, not a verified network-wide total.
- Five consecutive timestamp differences differ from 600 seconds (4,200; 667; 956; 1,200; 1,800). Do not resample, interpolate, or fabricate observed targets. Form contiguous segments at each departure from 600 seconds and exclude windows/forecast intervals crossing any segment boundary. Report excluded counts.
- Batch 4 notebook contains completed single-seed LSTM+Attention runs at 144/288 lags, but differing evaluation targets and forward-filled resampling prevent direct comparison to the new experiment.
- Three similarly named XAI notebooks concern **Unicauca classification** with TreeSHAP/LIME. Archive as a separate branch; classification metrics cannot substantiate this forecasting paper.
- PatchTST notebook is data exploration of bottom.csv; TFT notebook contains exploratory CESNET usage/training on a different representation. They are historical context, not matched benchmark results. Network Forecast_Reduction is an empty notebook.
- Original bottom/bigFlows/botnet/VNAT CSVs are recovered. The first three aggregate entire flow lifetimes, so assigning Total Bytes to Start Time would not reconstruct interval throughput. bigFlows is only about five minutes, bottom about 90 minutes. VNAT contains flow classification features. Exclude these from the primary forecasting experiment. No Tor file has been recovered.
- DATASET_DECISION_LOG.md and a separate results_batch4.json were not found in targeted Drive searches (the Batch 4 notebook matches their text). Model checkpoints and multivariate CESNET features have not been recovered.

## Data and evaluation

Target: decimal gigabytes per observed 10-minute interval (`n_bytes / 1e9`). Forecast origin follows a fully observed interval. Direct horizons: 1 and 6 steps (approximately 10 and 60 minutes in continuous segments). Inputs contain past volume only; no forecast-time network statistics.

Chronological boundaries: first floor(0.70*N) observations for train, next floor(0.15*N) for validation, remainder test. No fitting or selection on test. Inputs may include earlier split history, which is available at forecast time; all requested labels must lie within the assigned split. Candidate 144/288 models and all baselines share the SAME origin lists, using maximum history 1,008 steps (seven days) and maximum horizon 6 within one continuous segment. This also makes daily/weekly seasonal comparators valid on identical timestamps.

Scale using train mean and standard deviation only. Preserve real zeros if later discovered; fail on nonfinite/negative values or join/ordering violations. No clipping of outliers or test predictions. Record SHA-256 hashes, split dates, window counts, gaps, and software versions.

Baseline models: persistence, daily seasonal naive (144-step lag), weekly seasonal naive (1,008-step lag); Ridge regression using 144 lags, with alpha selected from [0.1, 1, 10, 100] by mean validation MSE across horizons. These are finite comparators, not an exhaustive forecasting competition.

Recurrent models: one-layer LSTM, hidden size 32, identical direct two-horizon head and residual persistence connection. Pooling variants: last hidden state, uniform mean, learned additive Attention (`v^T tanh(W h + b)` with unbounded final score), and recovered-style bounded score (`tanh(w^T h + b)`). Main context: 144 lags. Additional context ablation: learned Attention with 288 lags. The bounded score variant diagnoses a recovered architectural choice; it is not a bit-for-bit TensorFlow reproduction. In the recovered design, score range [-1,1] restricts attention ratios to at most exp(2), which limits concentration.

Seeds: 42, 123, 2026. Optimizer Adam lr=0.001; batch=256; up to 40 epochs; patience=6 on mean standardized validation MSE; restore best checkpoint; gradient norm clipping at 1. All variants have the same training budget. No test-based reruns or parameter changes. Record training curves, best epoch, runtime, device, parameters, raw per-origin predictions and checkpoints. If a numerical/software failure requires changes, document it before rerunning.

Metrics: MAE, RMSE, WAPE and skill versus persistence on original GB scale, separately by horizon. Report mean and sample standard deviation across seeds; seed spread is not a confidence interval. Also report first/middle/final thirds of the held-out test period. Moving-block bootstrap (144 consecutive retained origins, 1,000 replicates) for paired MAE differences, accompanied by block-length sensitivity 72/288 and a warning that removed gaps change elapsed time represented by a block. No IID test on overlapping origins; no claim of generalization to multiple independent networks.

## Explainability audit

Use learned and bounded Attention models at 144 lags for all three seeds. Select 96 test origins evenly by order, before examining errors. Horizon 1 is the preregistered XAI focus. Group history into 12 contiguous blocks of 12 intervals (two hours each).

Compare block rankings from summed Attention, absolute Integrated Gradients (IG), single-block occlusion, recency, and 20 random permutations. IG uses a training-only local-time-of-day median profile and 32 trapezoidal integration intervals, with completeness residual reported. Perturbation replacement uses the same training profile. Report absolute prediction change and change in absolute forecast error after replacing top 1/3/6 blocks. These measure sensitivity to the chosen replacement, not causal importance or operator trust. Occlusion ranking is derived from the same perturbation family, so it is a diagnostic comparator, not independent evidence of explanation correctness.

Secondary replacement sensitivity: constant training median, with rankings held fixed. Report rank correlation between Attention and IG/occlusion, seed-to-seed ranking stability, Attention entropy, and output changes when learned weights are replaced by uniform weights while hidden states stay fixed. Temporal hidden states mix earlier inputs, so Attention over states is not automatically attribution to raw lags. Negative or inconclusive results must remain in the paper.

## Deliverables and limits

Deliver a hashed recovery inventory, updated reference, runnable source/configuration, completed experiment logs/checkpoints/tables/figures, and an English conference-style paper draft with reproducibility details. No publication/submission is authorized by this task. A single recovered aggregate supports a bounded case study; it does not establish cross-network superiority, validated multivariate benefits, or causal explanation. Author identities and venue are unspecified; keep draft anonymous and venue-neutral.

## Updated primary references

1. Koumar et al. (2025), CESNET-TimeSeries24, Scientific Data 12, 338. https://doi.org/10.1038/s41597-025-04603-x ; dataset https://zenodo.org/records/13382427 . Supports dataset context, not verification of the recovered aggregate construction.
2. Jain & Wallace (2019), Attention is not Explanation. https://aclanthology.org/N19-1357/ . Motivation for auditing faithfulness; original experiments are NLP, not direct evidence about this traffic model.
3. Wiegreffe & Pinter (2019), Attention is not not Explanation. https://aclanthology.org/D19-1002/ . Motivates uniform-weight and seed-variation diagnostics.
4. Sundararajan, Taly & Yan (2017), Axiomatic Attribution for Deep Networks. https://proceedings.mlr.press/v70/sundararajan17a.html . Integrated Gradients comparator.
5. Zeng et al., Are Transformers Effective for Time Series Forecasting? https://arxiv.org/abs/2205.13504 . Motivation to include simple linear comparators; no claim that its long-horizon findings directly transfer here.
