# Full local reproduction — 6 November 2026

Full training, forecast evaluation, attribution evaluation, and statistical analysis were executed through the inline notebook on a separate local clone. All 58 notebook code cells completed, and a separate canonical audit of the fresh clone passed. This rerun reproduces already-opened target outcomes; it is not a new holdout experiment.

The executed notebook is `xai_cross_institution/XAI_Full_Local_Run.ipynb`. It first displays diagnostics from the delivered baseline and then executes the complete pipeline on its new clone. `results/LOCAL_REPRODUCTION_COMPARISON.json` records checkpoint and primary-result comparisons. Full-run numerical artifacts are in `runs/2026-11-06/full_local/` on the Git branch.

The baseline paper and protocol remain unchanged. Bibliography source is `paper/references.bib`; its 18 citation keys match the paper and it passes BibTeX compilation. The paper currently retains its explicit bibliography to preserve the delivered PDF layout.

This snapshot contains the notebook inputs as they existed when execution started. The executed output notebook is in the main project directory. The training/attribution source hash refers to the input notebook snapshot, not its later saved outputs. Baseline artifact/status manifests are retained under BASELINE names.
