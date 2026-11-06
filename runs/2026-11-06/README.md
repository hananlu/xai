# Full local reproduction — 6 November 2026

Full training, forecast evaluation, attribution evaluation, and statistical analysis were executed through the inline notebook on a separate local clone. All 58 notebook code cells completed, and a separate canonical audit of the fresh clone passed. This rerun reproduces already-opened target outcomes; it is not a new holdout experiment.

The executed notebook is `xai_cross_institution/XAI_Full_Local_Run.ipynb`. It first displays diagnostics from the delivered baseline and then executes the complete pipeline on its new clone. `results/LOCAL_REPRODUCTION_COMPARISON.json` records checkpoint and primary-result comparisons. Full-run numerical artifacts are in `runs/2026-11-06/full_local/` on the Git branch.

The baseline paper and protocol remain unchanged. Bibliography source is `paper/references.bib`; its 18 citation keys match the paper and it passes BibTeX compilation. The paper currently retains its explicit bibliography to preserve the delivered PDF layout.

## Exact comparisons

```json
{
  "notebook_input_sha256": "3bff723d5f1576bdaeec9fc3f572c7449a387fa9a48802c415165b1250797031",
  "model_state_max_abs_differences": {
    "dlinear_42.pt": 0.0,
    "dlinear_123.pt": 0.0,
    "dlinear_2026.pt": 0.0,
    "gru_42.pt": 0.0,
    "gru_123.pt": 0.0,
    "gru_2026.pt": 0.0
  },
  "checkpoint_binary_note": "Checkpoint metadata includes measured training runtime, so file hashes can differ even when parameter tensors are identical.",
  "status": "completed",
  "local_date": "2026-11-06",
  "fresh_holdout": false,
  "primary_exact_matches": {
    "mean": true,
    "ci_low": true,
    "ci_high": true,
    "pairs": true,
    "bootstrap_valid": true
  },
  "checkpoint_exact_matches": {
    "dlinear_123.pt": false,
    "dlinear_2026.pt": false,
    "dlinear_42.pt": false,
    "gru_123.pt": false,
    "gru_2026.pt": false,
    "gru_42.pt": false,
    "ridge_0.npz": true,
    "source_profile.npy": true
  },
  "full_notebook": {
    "status": "passed",
    "cells": 95,
    "executed_code_cells": 58,
    "error_outputs": 0,
    "seconds": 529.4954149579862,
    "full_retraining": true,
    "full_batch_evaluation": true,
    "execution_engine": "nbclient real ipykernel Python 3.11, local CPU"
  },
  "independent_validation": "pass",
  "source_run_directory": "20261106T135234_008225Z"
}
```
