# Development completed: metric calibration and functional prototype

5 November 2026. **This is exploratory development, not the 48-institution transfer study and not proof of publication novelty.** The eight new target institutions were not used. Previously inspected development data remain development data.

## 1. Calibration of explanation checks

The 12 old development institutions supplied 32 windows each, two horizons and seven day-sized history groups: 768 attribution cases per method. All 128 reference-replacement coalitions were explicitly queried.

| Attribution control | Maximum completeness error (GB) | Mean normalized coalition error |
|---|---:|---:|
| Exact linear | 4.88e-15 | 3.95e-16 |
| Uniform allocation preserving the total | 8.88e-16 | 0.2063 |
| Reversed allocation preserving the total | 4.66e-15 | 0.2649 |
| Permuted allocation preserving the total | 4.88e-15 | 0.2694 |
| Recency-only comparator preserving the total | 0 | 0.2314 |

The response check distinguishes the exact linear allocation from deliberately corrupted allocations that completeness cannot reject. Recency can be appropriate in other settings; it is not defined as wrong by construction.

An analytical nonlinear interaction example then shows the limit of this check: exact Shapley can have nonzero additive partial-coalition reconstruction error. Consequently, that residual is **not** adopted as a universal nonlinear fidelity metric. These controls are elementary validation devices, not novel theoretical contributions.

## 2. Nonnegative forecasting prototype

A fresh development-only log-Ridge predictor was fitted on four development source institutions, selected using four development validation institutions, then evaluated on the four source and four remaining development institutions. Roles were assigned within the existing volume strata before fitting.

- Source IDs: 28, 102, 104, 206.
- Validation IDs: 42, 128, 209, 254.
- Development-holdout IDs: 68, 107, 154, 155.
- Source fitting windows: 27,596; training target timestamps in 2024.
- Validation: January 2025; selected alpha 10 at horizon 1h and 100 at 6h.
- Evaluation: February–March 2025, 209 eligible six-hour-spaced origins per evaluated institution.
- Output function: expm1(max(0, linear(log1p(history)))). No negative predictions were produced.

Persistence, daily and weekly forecasts are saved on the same origins. Per-institution metrics are in results/development_forecast_metrics.csv. No inferential source-versus-target performance claim is made from raw-GB group averages. These development institutions were already inspected in earlier pilots.

## 3. Attribution numerical feasibility

Twelve origins per evaluated institution, two horizons, two reference definitions produced 384 attribution cases. Exact seven-group Shapley was computed from 128 coalitions; the largest efficiency error was 3.55e-15 GB. Analytic chain-rule gradients through the full forecast function were independently checked by finite differences; the maximum scaled discrepancy was 4.95e-10.

Initial Gauss–Legendre IG integration accepted 372/384 cases and rejected 12 under the prespecified completeness and vector-convergence tolerances, even at 1,024 nodes. Those records remain unchanged in development_attribution_checks.csv.

A separate, explicitly post-hoc development follow-up used adaptive vector quadrature with breakpoint hints around the clamp transition and two accuracy levels. All 12 originally failed cases passed the follow-up tolerances; maximum completeness error was 1.11e-16 GB. The root scan is not a formal certification of every possible crossing. This follow-up does not validate IG for GRU or other future models.

IG–Shapley allocation differences are recorded as descriptive agreement between different explanation definitions, never as a universal correctness ranking.

## Decision

**Proceed with source-trained neural feasibility and the full measurement protocol.** A correct linear control, a physically nonnegative functional prototype and an auditable numerical-integration route now exist. Their success does not settle whether attribution reliability transfers to new institutions, whether attribution improves operational decisions, or whether the eventual findings satisfy a conference's contribution standard.

The 32/8/8 institution split remains reserved for the new study. The complete statistical protocol is not yet frozen: neural numerical checks, input-intervention controls and the primary response endpoint must be finalized on development first. See MEASUREMENT_CONTRACT.md.
