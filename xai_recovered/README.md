# XAI network traffic forecasting: recovered project

This directory is the reconstructed project. The previous laptop is unavailable; source evidence comes exclusively from the user's Google Drive and supplied MHT. Recovered notebooks are preserved as evidence and are not executed by the new pipeline.

Start with **REFERENCE_UPDATED.md** and **PROTOCOL.md**. Results and paper status are recorded in **STATUS.md**. The source of each recovered item and its SHA-256 hash are in `recovery_manifest.json`.

## Layout

- `recovered/`: original downloaded notebooks/CSVs and user MHT, retained without edits.
- `src/experiment.py`: audit, chronological splits, baselines, matched recurrent experiments.
- `src/analyze.py`: metrics, paired moving-block bootstrap, explainability diagnostics, figures.
- `results/`: audits, training histories, checkpoints, all per-origin predictions, tables and XAI arrays.
- `figures/`: generated publication figures.
- `paper/`: English conference-style manuscript and editable source, generated after experiments.

## Reproduce

Tested on macOS arm64 with Python 3.11. Exact package versions are in `requirements-lock.txt`.

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python src/experiment.py --mode audit
.venv/bin/python src/experiment.py --mode all --device cpu
.venv/bin/python src/analyze.py
.venv/bin/python src/check_ig_convergence.py
.venv/bin/python src/explore_ridge.py
.venv/bin/python src/build_paper.py
.venv/bin/python src/validate_results.py
```

The paper build additionally needs a TeX distribution with IEEEtran and `pdflatex`. A single command, `.venv/bin/python src/run_all.py`, runs/resumes training, primary analysis, IG convergence follow-up, exploratory linear decomposition, paper generation and validation. It does not upload data or submit the paper.

Run paths are resolved relative to the source file, so the scripts also work when invoked outside this directory. `--mode all` runs four deterministic baselines and fifteen recurrent fits (three seeds for four pooling variants at 144 lags, plus learned Attention at 288 lags). Completed recurrent runs are skipped if their metric JSON exists. To deliberately rerun a fit, archive its metric, prediction, checkpoint and history files together first; do not mix old results with a changed protocol/source.

For one fit:

```bash
.venv/bin/python src/experiment.py --mode train --pooling attention --length 144 --seed 42 --device cpu
```

Training uses four CPU threads. A synthetic throughput benchmark on this host found CPU faster than Apple MPS for this small LSTM workload; no paid/cloud training was used. CPU/device timing is machine-specific.

The audit assertions verify one-to-one joins, finite nonnegative data, split boundaries, temporal continuity, lag/target alignment, output shapes, normalized Attention and the bounded-score ratio limit. These are substantive pipeline checks. Training must finish all fifteen metric files before running `analyze.py`.

## Interpretation

GB means decimal gigabytes per recovered interval, not Gbit/s. Forecasts are issued after observing the last input interval. Horizon 6 forecasts the sixth future interval's byte volume, not the sum of the next six intervals. All models use identical target timestamps, and historical inputs from an earlier split are allowed because they are available at the forecast origin.

The recurrent `last` and `uniform` implementations contain an unused scoring module for code simplicity. Its parameters receive no gradients; count active parameters separately when comparing model sizes. The `training_s` field includes final prediction/serialization overhead as well as fitting; epoch histories isolate elapsed fitting time.

The Attention models include a persistence skip connection. Their heatmaps describe weights over recurrent hidden states; they do not attribute the skip path. Integrated Gradients differentiates the full model including that path. A separately labeled secondary diagnostic subtracts the exact skip attribution and reports correction-only sensitivities. A full-model/path mismatch is not itself proof that attention fails to describe the correction branch.

**IG is provisional.** The planned completeness check exposed numerical nonconvergence on some cases. The manuscript reports a secondary 128/512/2,048-interval follow-up and does not treat IG rankings as a validated reference. Direct perturbation outputs, forecast metrics and the exact Ridge decomposition do not depend on IG quadrature. See `ig_convergence_followup.csv` and the execution notes.

No upstream aggregation script, multivariate CESNET file, old checkpoints, or separate Batch 4 JSON was recovered. The aggregate's institution membership is therefore unverified. Original flow CSVs are not substituted for throughput series. A single recovered aggregate supports a case study, not a multi-network benchmark or a claim of deployment readiness.

`results/historical_batch4_extracted.json` preserves the two result dictionaries extracted from embedded notebook outputs. It is a derived archival record, not the missing original JSON and not a newly executed reproduction. Its source hash is recorded, and it is excluded from new experimental metrics.
