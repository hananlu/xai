# XAI network traffic projects — Farrel branch

This branch contains the recovered forecasting project, the executed cross-institution study, its notebooks, source code, selected datasets, checkpoints, per-origin predictions, attribution results, paper sources and editable presentation. The existing root `XAI_Network_Traffic.ipynb` remains the original classification notebook.

## Main forecasting study

**Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting**

Start with [the full experimental notebook](xai_cross_institution/XAI_Complete_Experiment.ipynb), [project README](xai_cross_institution/README.md), and [results brief](xai_cross_institution/RESULTS_BRIEF_ID.md).

| File / directory | Contents |
|---|---|
| [Full experiment notebook](xai_cross_institution/XAI_Complete_Experiment.ipynb) | 95 cells, 58 code cells, 22 plots; inline EDA, preprocessing, models, training loops, forecasting, Shapley/IG/occlusion, agreement, stability, latency and paired inference. Light default mode is executed. |
| [Full local run notebook](xai_cross_institution/XAI_Full_Local_Run.ipynb) | Local full-training and batch-evaluation run; execution record and fresh-run snapshot are in `runs/2026-11-06/`. |
| [Paper PDF](xai_cross_institution/paper/paper.pdf) | Anonymous English research draft. |
| [LaTeX](xai_cross_institution/paper/paper.tex) / [BibTeX](xai_cross_institution/paper/references.bib) | Editable paper and all 18 cited bibliography entries; see paper README for BibTeX conversion. |
| [Editable slides](xai_cross_institution/presentation/XAI_Research_Results_v2.pptx) | Opening, gap/goal, pipeline, findings and limitations. |
| [Source](xai_cross_institution/src/) | Frozen core training/evaluation/analysis code and independent audits. |
| [Data](xai_cross_institution/data/) / [models](xai_cross_institution/models/) | 48 selected hourly institutional series, provenance hashes and trained checkpoints. |
| [Predictions](xai_cross_institution/predictions/) / [results](xai_cross_institution/results/) | Per-origin forecast output, detailed attribution records, numerical rejection records, statistics and freeze manifests. |

The prespecified target-minus-source ranking contrast is approximately -0.019, with nominal 95% interval [-0.089, 0.053], seven complete pairs. This does not establish systematic degradation or equivalence. Additional notebook agreement/stability/latency analyses are exploratory. No paper has been submitted.

## Run locally

Extract or clone this branch, create a Python 3.11 environment, install `xai_cross_institution/requirements-notebook.txt`, and open the full notebook in an existing Jupyter/VS Code frontend. Install JupyterLab separately if needed. Set `PROJECT_DIR` to the `xai_cross_institution` folder when auto-discovery does not find it.

The light notebook default reconstructs fitting inputs, refits the locked Ridge model, re-queries checkpoints, computes local attributions and reproduces the primary bootstrap. Full neural training/evaluation can be enabled with explicit flags and writes to a new clone. The full local-run notebook has those flags enabled and can run longer.

For the canonical scripts, see [reproduction instructions](xai_cross_institution/README.md). No GPU is required by the current CPU implementation. Exact dependency versions, seeds, selected settings, institution membership and model/data hashes are included.

## Project history

- [Recovery / first aggregate pilot](xai_recovered/README.md): original recovered notebooks, input files, first experiment code/results and historical paper source.
- [Conference pilot v2](xai_research_v2/README.md): earlier institution pilot and literature/data audit.
- [Novelty direction decisions](xai_novelty_upgrade/): research positioning and chosen direction.
- [Chronological project reference](XAI_project_reference.md).

Historical pilot results are identified separately from the full 48-institution study. Duplicate convenience ZIPs are omitted because their unpacked source files are committed. Local virtual environments, caches, LaTeX build auxiliaries and the 1.7GB upstream raw archive are not versioned; selected derived data and provenance/checksums are included.

## Data attribution and research scope

Main data: **CESNET-TimeSeries26**, Josef Koumar, Karel Hynek, Kamil Jeřábek, Pavel Šiška (2026), [Zenodo DOI 10.5281/zenodo.21945629](https://doi.org/10.5281/zenodo.21945629), CC BY 4.0. See [data attribution and modifications](xai_cross_institution/DATA_ATTRIBUTION.md). Earlier recovered capture references have their own upstream provenance; a blanket license for those files is not asserted here.

All selected institutions belong to one ISP. Q measures controlled-operator ranking alignment, not causal demand truth. Missingness, finite numerical budgets, the small number of effective pairs and limited explainer/model families constrain the conclusions. Author information and venue formatting remain to be finalized.
