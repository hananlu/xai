# XAI network traffic projects — Farrel branch

Latest manuscript: **seven pages including all 18 references**, with a compact pipeline; six figures and three tables retained. See [revision notes](xai_cross_institution/SEVEN_PAGE_REVISION_NOTES.md).

Latest paper design: [monochrome workflow and regrouped tables](xai_cross_institution/VISUAL_REVISION_NOTES.md), with all results preserved and the eight-page limit retained.

## Current conference version

The main paper is **7 pages including references**, with six figures, three tables and all 18 cited sources. The reference page contains no figures. [Optional supplement](xai_cross_institution/paper/supplementary.pdf) is separate (six pages/seven figures/two tables). [Updated editable deck](xai_cross_institution/presentation/XAI_Research_Results_v5.pptx) has 19 slides, 11 native tables and three native charts with embedded workbooks.

Two focused post-hoc additions are complete and independently audited: [common-case absolute explainer alignment and cascading learned-layer sensitivity](xai_replication_32/conference_checks/README.md). Common-case target Q: Shapley 0.690, occlusion 0.687, recency 0.533. Conditional rank similarity is about 0.72 after head reset and 0.12-0.16 after head+GRU reset. Populations/flat outcomes and the fixed residual route remain explicit; no superiority, causal, equivalence or cross-ISP claim is added.

The latest [replication notebook](xai_replication_32/XAI_Replication_32.ipynb) has 62 cells, 37 executed code cells and eight plots, with zero errors. It includes inline computations and an optional isolated control-only rerun, without fitting. The original primary estimates, source models and scientific freezes remain unchanged. See [extension notes](xai_cross_institution/CONFERENCE_CHECKS_NOTES.md). Older revision/page counts below are historical.

---

## Conference page limit

The main manuscript is **7 pages including references**, within the requested 7-8-page limit. It retains six figures, two tables, all 18 references and the original/new-cohort outcomes. [Optional supplementary material](xai_cross_institution/paper/supplementary.pdf) is a separate four-page file with six additional diagnostic figures and two tables. The previous expanded draft is archived. Sources, figures, scientific results and model/protocol freezes remain available and unchanged.

This branch contains the recovered forecasting project, the executed cross-institution study, its notebooks, source code, selected datasets, checkpoints, per-origin predictions, attribution results, paper sources and editable presentation. The existing root `XAI_Network_Traffic.ipynb` remains the original classification notebook.

## Main forecasting study

**Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting**

Start with [the full experimental notebook](xai_cross_institution/XAI_Complete_Experiment.ipynb), [project README](xai_cross_institution/README.md), and [results brief](xai_cross_institution/RESULTS_BRIEF_ID.md).

| File / directory | Contents |
|---|---|
| [Full experiment notebook](xai_cross_institution/XAI_Complete_Experiment.ipynb) | 95 cells, 58 code cells, 22 plots; inline EDA, preprocessing, models, training loops, forecasting, Shapley/IG/occlusion, agreement, stability, latency and paired inference. Light default mode is executed. |
| [Full local run notebook](xai_cross_institution/XAI_Full_Local_Run.ipynb) | Local full-training and batch-evaluation run; execution record and fresh-run snapshot are in `runs/2026-11-06/`. |
| [Paper PDF](xai_cross_institution/paper/paper.pdf) | Expanded anonymous English working draft: 7 pages including references, 6 figures, overall TikZ pipeline and 18 references. |
| [LaTeX](xai_cross_institution/paper/paper.tex) / [BibTeX](xai_cross_institution/paper/references.bib) | Editable paper, complete TikZ pipeline, and all 18 cited bibliography entries; the manuscript builds directly from BibTeX. |
| [Editable slides](xai_cross_institution/presentation/XAI_Research_Results_v4.pptx) | Opening, gap/goal, pipeline, findings and limitations. |
| [Source](xai_cross_institution/src/) | Frozen core training/evaluation/analysis code and independent audits. |
| [Data](xai_cross_institution/data/) / [models](xai_cross_institution/models/) | 48 selected hourly institutional series, provenance hashes and trained checkpoints. |
| [Predictions](xai_cross_institution/predictions/) / [results](xai_cross_institution/results/) | Per-origin forecast output, detailed attribution records, numerical rejection records, statistics and freeze manifests. |

The original eight-target prespecified target-minus-source ranking contrast is approximately -0.019, with nominal 95% interval [-0.089, 0.053], seven complete pairs. This does not establish systematic degradation or equivalence. Additional notebook agreement/stability/latency analyses are exploratory. No paper has been submitted.

## Completed new-target replication, 7 November 2026

The additional cohort contains **32 previously unevaluated targets**, matched to the original 32 source anchors with the same locked models. Both studies together cover **80 unique institutions within one ISP**. [New results](xai_replication_32/RESULTS_BRIEF.md), [research position](xai_replication_32/RESEARCH_POSITION.md), [executed replication notebook](xai_replication_32/XAI_Replication_32.ipynb), [protocol](xai_replication_32/PROTOCOL_REPLICATION.md), and [reproduction guide](xai_replication_32/README.md).

The new primary contrast is **-0.0075**, nominal 95% interval **[-0.0402, 0.0241]**, 30 complete pairs. A prespecified nested 64-origin frozen-GRU sensitivity gives h1 **+0.0001**, interval **[-0.0229, 0.0248]**, on the same 30 pairs. Neither establishes degradation or equivalence. The original history-median zero-excluding secondary pattern does not recur in the new cohort. Sources, trained models and ISP are shared, so estimates remain separate.

All scientific/dense audits passed. The new analysis notebook has 52 cells, 31 executed code cells, seven embedded plots and zero errors. Its default reads the completed batch and reproduces local arithmetic/primary inference; optional full evaluation runs on a copy. The actual added main/dense XAI batches took about 35 minutes on the local CPU, without retraining. Low-volume forecast-scale failures and undefined ranking cases remain visible.

The combined paper now has **7 pages including references, 6 figures and 18 cited references**, with LaTeX/BibTeX/TikZ sources. The updated [editable PPT](xai_cross_institution/presentation/XAI_Research_Results_v4.pptx) has **17 slides**, ten native tables and two native charts with embedded workbooks. The previous 9-page paper is archived; original scientific freezes and the independent full local rerun remain unchanged. Conference page budget and authorship still need final selection; nothing has been submitted.

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

## Remaining submission work

The [readiness review](xai_cross_institution/SUBMISSION_READINESS_REVIEW.md) prioritizes an existing-output common-case comparison across explainers, a parameter-randomization control, and a sharper closest-work comparison. External-network evidence and realistic traffic replacements remain scope limits. The reference page now contains no figures; the main manuscript remains seven pages including references. No new experiment or stronger claim is asserted in this review.