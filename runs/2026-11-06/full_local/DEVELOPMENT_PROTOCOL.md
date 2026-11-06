# Development feasibility protocol — 5 November 2026

This is an exploratory development stage, after metric calibration and before the 48-institution transfer study. Only the 12 previously inspected development institutions are used. No new target-institution data are fitted, scored or used as attribution references.

## Roles and data

Within each of the four saved 2024 volume strata, hash the three development IDs with salt `ci-dev-2026-v1:`. Assign the first to source fitting, second to validation, third to development holdout. Thus 4/4/4 institutions. This holdout is development data already used in earlier pilots, not a confirmatory test.

Hourly n_bytes / 1e9, 168 lag inputs, 1/6-hour endpoint targets. Reuse the existing complete-hour and conservative artifact flags. Keep complete histories and measured targets, do not remove observed zeros, and use the same eligible origins for every model/horizon within each institution.

Source fitting: 2024 target timestamps. Validation: January 2025, four validation institutions. Feasibility evaluation: February–March 2025 on the four source and four development-holdout institutions, at origin UTC hours divisible by six. No new final-period outcomes are scored.

## Forecast function

Source-trained Ridge in log1p(GB) coordinates. Alpha {0.1,1,10,100}, separately selected for each horizon by equal-institution validation MAE in log coordinates. Operational output is `expm1(max(0, linear(log1p(history))))`, so predicted volume is nonnegative. No target-institution scaling or fitting. This is an exploratory functional prototype, not a claim of a new model or a performance improvement over v2.

Compare persistence, daily and weekly seasonal-naive on the same origins. Save per-institution MAE, RMSE, negative-output fraction and zero-output fraction. No inferential claims from the eight related institutions.

## Attribution feasibility

Choose 12 origins by evenly spaced indices for each evaluated institution. Seven groups of 24 consecutive history hours (oldest to most recent).

Reference A: calendar median computed only from source 2024 observations, with phase matched to each history timestamp. Reference B: for each observed history window, the median across its seven days at each hour position, repeated across days. Reference B uses available inputs, is not an independent training reference, and answers a different contrast. Neither reference is declared universally correct or in-distribution.

Enumerate all 128 reference-replacement coalitions and compute exact grouped Shapley for that specified game. Check efficiency/completeness with tolerance 1e-8 GB + 1e-6 times absolute forecast contrast.

Compute IG along the raw-GB straight path through the **entire** log1p, linear, clamp and expm1 function. Analytic chain-rule derivatives are independently checked with finite differences on representative observed coordinates. Adaptive Gauss–Legendre nodes {32,64,128,256,512,1024}. Accept each case only if completeness error <=1e-8 GB +1e-3*abs(f(x)-f(reference)) and L1 change against the previous integration level <=1e-8 GB +1e-3*L1(attribution). Report failures and node counts rather than calling an unconverged result reliable.

Group IG by signed summation over each 24-hour block. Record IG–Shapley allocation difference as descriptive **agreement between different attribution definitions**, not correctness or causal faithfulness. Exact Shapley can be correct while disagreeing with path IG because nonlinear interactions distribute credit differently.

No sole primary fidelity score for nonlinear models is frozen at this stage. Calibration has already shown that completeness alone is insufficient, and partial-coalition additive reconstruction confounds interaction effects with explanation error. The full protocol must separate method-specific numerical checks from operator-specific intervention/ranking usefulness and model accuracy. Reference sensitivity alone is not proof of failure.
