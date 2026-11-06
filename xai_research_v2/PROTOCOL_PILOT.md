# Protocol v2: telemetry-loss explanation audit — exploratory pilot

Frozen before pilot outcomes, 5 November 2026. This protocol does not modify the completed v1 experiment or its registered source hashes. Public dataset acquisition is part of the user's request to choose a worthy dataset. No paid compute.

## Data and scope

Official CESNET-TimeSeries26, Zenodo record 21945629, CC BY 4.0. Acquire institutions archive plus reference metadata, check publisher MD5, retain SHA-256 for selected members. Raw archives stay under work/; portable selected data and manifest go under outputs/. This pilot is same-network, multiseries evidence, not external replication.

Use hourly n_bytes / 1e9 (GB per recorded hour), horizons 1 and 6 **endpoint hours**, not accumulated six-hour volume. Input has 168 hourly lags. IDs join explicit UTC time mappings. Native hourly values may include partial-hour aggregates; eligible clean windows require exactly six distinct ten-minute records in each corresponding UTC hour. Coverage is a measurement-availability proxy, not proof of successful capture at every probe. Never convert absent/partial targets to observed zeros.

Exclude 2024-05-21 through 2024-06-04 from clean train windows conservatively because the descriptor reports a partial probe-loss event, with entity scope not yet resolved. This is a conservative global screening choice, not a claim that every institution was affected. All zeros with full coverage remain valid observed values. Do not filter demand spikes by sigma rules. Do not impute evaluation targets.

Split by target timestamps: training 2024-01-01–2024-12-31; validation 2025-01-01–2025-01-31; exploratory pilot 2025-02-01–2025-03-31. Windows require all horizon targets in the same split. April 2025–June 2026 target outcomes remain unscored for future confirmation. Context may precede a target split, matching deployment. Fit all scaling/imputation profiles only on training.

Select 12 institutions using training data only: >=90% finite nonnegative hourly values on available complete hours, positive variance and positive median volume. Divide eligible institutions into four equal-count strata by training median volume; choose three per stratum by ascending SHA-256 of 'xai-v2-2026:' + numeric ID. If archive not yet complete, do not substitute first downloaded IDs. Publish exact selected IDs before fitting.

## Pilot models and controls

Persistence, daily seasonal persistence, weekly seasonal persistence, Ridge on 168 lags. Ridge alpha in {0.1,1,10,100}, chosen by validation MAE independently per institution and horizon; standardize input and target with training mean/std. No test tuning. Keep Ridge outputs unclipped to preserve exact linear decomposition; report negative-output rate. Explanations apply to this unclipped function. No claim of DLinear equivalence.

A second Ridge is trained with corruption augmentation and explicit 168 missingness indicators. Training uses clean and one augmented copy: uniform random choice of six missing hours versus a contiguous six-hour block, then training hour-of-week median imputation. Train masking is independent of targets. Both Ridge families use the same alpha grid. This intentionally changes both training distribution and mask access; it is a feasibility comparison, not an isolated mask ablation. Full study must add augmentation-only/no-mask and mask/augmentation factorial controls.

## Controlled telemetry loss

On complete pilot histories only, hold future targets unchanged. Three seeds {42,123,2026}; paired corruption locations shared across model families. Loss patterns: six isolated hours, contiguous six-hour block anywhere, and latest six hours. Three causal replacements: zero, last observed value scanning left-to-right (fallback training mean if needed), and training hour-of-week median. These are stress scenarios, not guaranteed in-distribution inputs. Native outages cannot reveal unobserved true traffic; evaluate those later as case studies without claiming reconstruction ground truth.

Pilot evaluation uses one origin every six hours (fixed UTC hour divisible by six) to reduce runtime and overlap; all models receive the same origins. Clean forecast metrics: MAE, RMSE, training weekly-seasonal MASE. Report per-institution results and equal-institution macro averages. Scale error shifts by training standard deviation for comparisons. No claim of independent origins or independent institutions.

## Explanation checks and falsifiable questions

For Ridge, contribution c_j = beta_j * (x_j - reference_j), in output GB. Reference is training hour-of-week median for value features and observed indicators (all zeros) for mask features. Intercept/reference prediction is disclosed. Verify sum(c) = f(x) - f(reference) within 1e-8 GB (float64). Separately verify corruption-induced forecast difference equals beta dot feature difference; this is a numerical calibration identity, not evidence of novel faithfulness or causal traffic influence.

Separate absolute attribution mass on observed values, imputed values, and mask indicators, with zero-total mass handled explicitly. Main exploratory diagnostic: fraction of absolute contribution assigned to imputed values plus missingness indicators. It describes model dependence relative to a chosen reference, not uncertainty probability. Record mass for each replacement; profile imputation can make value contributions exactly zero by construction, so zero mass does not certify safety.

RQ1: Does the augmented mask-aware pilot reduce corruption-induced forecast degradation relative to clean-trained Ridge, without unacceptable clean error? RQ2: Is attribution mass associated with incremental error beyond missing percentage / recency? Report Spearman association with abs(error_corrupt)-abs(error_clean) and the recency heuristic. Equal missing counts make missing-fraction discrimination undefined within this pilot; severity-varying controls are required in the full study. Do not label injected locations as universally 'true salient features'.

These exploratory associations are not a validated deployment detector. No test-based choice of a winning replacement, score, institution, or pattern. No p-values from hourly pseudo-replication. Any bootstrap is paired and grouped by calendar week; full study also clusters institution dependence and uses an external network.

## Next full study, contingent on the pilot

Expand severity {1,6,24,48 hours}, scattered/block/tail and sustained partial undercount. Compare Ridge, DLinear, GRU/LSTM, and one patch forecaster; include skip/no-skip only if needed to isolate scope. Neural methods use validation-only tuning and three seeds; five seeds if uncertainty warrants. Add exact linear control, block occlusion, IG only with per-example completeness and integration convergence, random/recency and trained-randomized sanity checks. Perturbation rankings must be evaluated with a different replacement or independent intervention from the one used to construct them. Neither large deletion shifts nor sparse attention alone establish faithfulness.

Freeze a final protocol before reading reserved outcomes, use rolling-origin forecasts on reserved periods and explicitly model/retrain around shifts. Native outage analysis uses coverage metadata, not hidden-demand labels. External-network dataset must be independently licensed and timestamp/provenance audited; older GEANT/Abilene may be useful for transfer but do not replace contemporary CESNET evidence. The paper and PPT follow evidence, not the reverse.
