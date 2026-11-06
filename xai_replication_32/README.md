# Completed replication — 7 November 2026

32 new targets, 80 unique institutions across both studies. The main result uses 30 complete pairs: ΔQ -0.0075, nominal 95% interval [-0.0402, 0.0241], 1885/2,000 valid draws. It establishes neither systematic degradation nor equivalence. The original reference-specific zero-excluding secondary pattern does not recur here.

Start with [the executed notebook](XAI_Replication_32.ipynb), [results and every sensitivity](RESULTS_BRIEF.md), [research position](RESEARCH_POSITION.md), and [notebook guide](NOTEBOOK_GUIDE.md). The notebook has 52 cells, 31 code cells, 7 embedded plots and zero error outputs. All scientific/dense audits passed. The combined paper and editable presentation are in the sibling `xai_cross_institution` folder. Data attribution and the distinction between frozen analysis and later diagnostics are documented separately.

No new model fitting occurred. Main XAI: 18.7 minutes; added dense XAI: 16.3 minutes on the local four-thread CPU. Runtime describes this workload, not scientific validity or independent sample size.

---

# New-target within-CESNET replication

This is the additional cohort study, separate from `xai_cross_institution` and its original eight targets. Membership was frozen before new-target performance scoring; the complete code/data/selection freeze is recorded in `results/PREEVALUATION_FREEZE.json`. The original outcome was already known when this replication was designed. There is no external preregistration or independent network.

## Fixed design

- 32 newly evaluated targets sampled deterministically from 217 eligible unused institutions, eight per reconstructed original 2024 volume stratum.
- 32 reused source anchors and their original locked Ridge/DLinear/GRU checkpoints; zero new gradient fitting or tuning.
- Main timestamp-matched XAI budget: up to 16 origins per pair/year, IG on four. Actual selection: 2,016 source/target histories per fit across 63 available pair-years.
- Prespecified dense frozen-GRU budget: up to 64 nested origins per pair/year, 8,064 histories; source-calendar reference, no dense IG or calibration.
- Primary endpoint and pair/block bootstrap match the original definition. Pair-only and synchronized-calendar bootstrap intervals and dense-budget comparisons are prespecified sensitivities, with interval failure reported when too few draws are valid.

Read `PROTOCOL_REPLICATION.md` before interpreting results. The freeze is a local audit trail; it does not turn shared source anchors, a shared trained model or a shared ISP into independent network replications. Different case/pair availability between budgets is reported, including the common complete-pair comparison. Q remains an operator-response alignment score, not causal demand truth.

## Provenance and sources

Official CESNET-TimeSeries26, Josef Koumar, Karel Hynek, Kamil Jeřábek, Pavel Šiška (2026), DOI https://doi.org/10.5281/zenodo.21945629, CC BY 4.0. New source-member hashes match the saved 2024 audit. Original complete-hour/native time-grid/artifact fields are retained. Missing values are not converted to zeros. `data/MANIFEST.json` records all 64 derived data files. The raw upstream archive is not bundled.

`src/benchmark_common.py`, `data_common.py`, `neural_feasibility.py`, forecast/attribution evaluators and arithmetic calibration are byte-preserved from the original study. `analyze_replication.py` changes only the study counts/protocol metadata of the original analysis; dense evaluation and sensitivities are separate prospectively frozen scripts. `tools/create_cohort.py` preserves the selection generator and refuses to overwrite a frozen cohort.

## Reproduction

Use Python3.11 and `requirements-full.txt`. Models and selected data are included; do not retrain or tune on new targets. To reproduce outputs, work on a copy of this project:

```sh
python src/evaluate_forecasts.py
python src/evaluate_attributions.py
python src/analyze_replication.py
python src/validate_replication.py
python src/evaluate_dense.py
python src/analyze_sensitivity.py
python tools/forecast_diagnostics.py
python tools/validate_dense.py
python tools/build_report.py
```

These scripts overwrite generated results in their own project folder; preserve the delivered snapshot. Preparation and one-time freezing scripts are provenance entry points, not steps to rerun on the frozen delivered directory. `PREEVALUATION_FREEZE.json` and `MEMBERSHIP_FREEZE.json` describe historical unscored states and remain unchanged after execution. Completion/audit results are recorded separately.

The frozen analysis and protocol do not guarantee significant degradation, equivalence, a narrow interval or conference acceptance. Original and new-cohort estimates must remain distinguished because source anchors/models overlap.
