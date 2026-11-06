# Complete experiment notebook

Open **XAI_Complete_Experiment.ipynb** as the main notebook. The earlier `XAI_Results_and_Reproduction.ipynb` remains a short results companion and is not the full experimental walkthrough.

The complete notebook has 95 cells, 58 code cells, 1,151 code lines, and 22 embedded Matplotlib figures. It was executed from a fresh real ipykernel through nbclient on the project Python 3.11 environment, with no error outputs. Figures were visually inspected. Counts describe the delivered version, not a measure of scientific novelty.

## What runs by default

- Verify frozen protocol/code hashes and all 48 selected data hashes.
- Read institution data, inspect schema, missingness, observed zeros and native-hour coverage.
- Visualize coverage, time series, source-only weekly profile and institution volume heterogeneity.
- Rebuild eligible 168-hour windows and source/validation fitting arrays; verify chronological and institution separation.
- Actually refit the fixed-alpha Ridge model on source data and compare coefficients with the delivered checkpoint.
- Reconstruct DLinear and GRU from native notebook class definitions and evaluate the selected case.
- Recompute a stored forecast-metric cell, forecast tables and error plots.
- Compute local exact Shapley, occlusion and adaptive IG directly from checkpoints with both references.
- Independently check sampled Shapley contributions by permutation enumeration; compute controlled-operator response games and match saved Q values.
- Analyze saved global allocations, method agreement, model-seed stability, numerical acceptance, and common-case Shapley/IG quality. Common-case neural comparisons require all three accepted/defined seeds.
- Recompute the complete-seed/timestamp-paired primary estimate and all 2,000 attempted bootstrap draws; confirm the original result.
- Run a small local latency benchmark; this and agreement/stability/local case analysis are exploratory notebook additions, not changes to the paper's primary endpoint.

## What is optional

Full source-only neural training and full batch forecast/attribution/analysis functions are **defined inline**, not hidden behind subprocess calls. Set RUN_FULL_TRAINING and/or RUN_FULL_EVALUATION in the configuration to run them on a new project clone. They were not re-executed in the default notebook validation. The original full study was previously trained/evaluated and its artifacts remain unchanged.

Rerun contexts record completed stages because the clone initially contains baseline artifacts. A fresh clone is reproduction of already-opened outcomes, not a new independent holdout. Original scientific results are not overwritten. Optional exploratory exports also go to a separate working folder.

## Environment and inputs

Extract the full research ZIP before opening the notebook. It needs the project data, models and result files. Use Python 3.11 and `requirements-notebook.txt` for a kernel environment. Open it in an existing Jupyter/VS Code notebook frontend, or install JupyterLab separately. Set PROJECT_DIR if auto-discovery cannot find the project. Colab setup is described but has not been validated on Colab.

## Reference and adaptation

Structural reference: https://github.com/hananlu/xai/blob/master/XAI_Network_Traffic.ipynb, accessed 6 November 2026. The original notebook addresses network traffic classification. Its staged presentation inspired a fuller EDA → preprocessing → modeling → global/local explanation → agreement/stability/latency → robustness walkthrough. No classification code, dataset, labels, random splitting or metric outputs were copied. The full forecasting core is mirrored from this study's frozen scripts, with notebook-specific paths and renamed batch entry points.

The new notebook does not add LIME, TreeSHAP or classification metrics to the forecasting paper. It exposes the implemented Shapley/IG/occlusion/recency methods and the actual forecasting protocol.
