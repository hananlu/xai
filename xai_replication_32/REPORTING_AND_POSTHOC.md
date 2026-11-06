# Frozen analysis versus later reporting

`results/PREEVALUATION_FREEZE.json` hashes 100 files: membership, protocol, scientific evaluators/analyzers, selected data, models and timestamp plans. Those files remain immutable. `MEMBERSHIP_FREEZE.json` records the earlier cohort selection. Their historical unscored fields are not updated after execution. Completion and independent audit records are separate. No scientific amendment has been made.

The added `tools/validate_dense.py` independently audits the frozen dense evaluation; it does not change its estimator, membership, budget or acceptance threshold. `tools/build_report.py` renders completed results. `tools/build_notebook.py` authors the analysis companion and exposes the implemented algorithms. These tools were added after the pre-evaluation freeze and are not presented as frozen scientific estimators.

After observing extreme target MASE in the main evaluation, `tools/forecast_diagnostics.py` added an all-cell log-scale plot, mean/median/max summaries and an explicit institution-267 example. This is post-hoc descriptive reporting. No case was removed, model refitted, scale capped, floor changed, or original mean MASE replaced. Both the frozen means and diagnostic medians are retained.

Pair-only/synchronized-block intervals and the nested 64-origin GRU analysis were defined before new-target scoring in the protocol and frozen analyzers. Their designation is sensitivity, not replacement primary inference. Original and new-cohort estimates remain separate because sources, model bytes and ISP overlap. New secondary patterns are reported even when the stronger-looking original pattern does not recur.
