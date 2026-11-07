# Focused conference checks

Two completed post-hoc additions strengthen the bounded empirical argument without changing either original primary endpoint: (A) common-case absolute explainer Q, (B) cascading learned-layer sensitivity of central daily Shapley. The new plan, case selection and five scripts were locally frozen before these summaries/randomized-model outcomes; original/new-cohort scores were already open. This is not a new holdout or external preregistration.

## Results to explain

- Main common-case target Q: Shapley 0.6902, occlusion 0.6869, recency 0.5335. The exact random-order mean is zero. Positive descriptive alignment does not establish physical/causal correctness or superiority. Shapley and occlusion have similar means.
- Accepted-IG common panel: target Shapley 0.7004, IG 0.7046, occlusion 0.7038, recency 0.4661. Its population differs from the full-budget panel. Do not compare IG's accepted subset with all-case Shapley as if the cases matched.
- Parameter control: 126 fixed histories, three trained seeds, three reset replicates and two cumulative learned-layer stages (2,268 records). Mean rank similarity to the trained allocation changes from 0.716/0.719 source/target after head reset to 0.119/0.162 after head+GRU reset, on the same conditional comparable panel. Signed-pattern distance is not monotonic; no pass threshold or confidence interval is claimed.
- Common nonflat comparisons are 337/567 source and 364/567 target per stage, with at least one comparison for every planned history. Flat/clipped cases remain counted. Source normalization and the architecture's fixed last-input residual route are retained.
- Identity-copy difference is zero. Audits check all original frozen inputs, independent common-case masks/macros, saved cumulative checkpoint structure, and fixed metadata-selected cases across four volume strata/cohorts. Five of sixteen audited randomized model/case games are nonflat, avoiding an exclusively zero-game arithmetic check.

Read PLAN.md and RESULTS.md plus every JSON/CSV denominator. `DENOMINATOR_CLARIFICATIONS.json` distinguishes 452 target IG-common cases before operator-cell aggregation from the 451 actually used. Frozen estimators are in src/. Later tools only clarify counts, improve the legend's placement and extend independent verification; they do not change estimands or saved numerical records.

## Reproduce on a copy

Use the parent project's Python 3.11 and requirements-full.txt. Keep original model/data/quality inputs alongside this subfolder, then run:

```sh
python conference_checks/src/explainer_comparison.py
python conference_checks/src/parameter_control.py
python conference_checks/src/summarize_controls.py
python conference_checks/src/validate_checks.py
python conference_checks/src/report_checks.py
python conference_checks/tools/report_denominators.py
python conference_checks/tools/render_parameter_figure.py
python conference_checks/tools/validate_informative_controls.py
```

The control itself took about 40 seconds on the local CPU with no training. Its historical FREEZE.json unscored field remains unchanged; COMPLETION.json records completion. The parent executed notebook includes both reconstructions/local tensor checks and an optional isolated control-only rerun flag. This reproduces already observed outcomes and does not provide new independent deployment institutions.
