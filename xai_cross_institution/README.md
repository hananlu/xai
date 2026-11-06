# Conference manuscript: 7 pages including references

The requested maximum is 7-8 pages. The current main PDF is **7 pages**, with **6 figures, 2 tables and 18 references**, using standard IEEE fonts/margins. The optional **4-page supplementary PDF** is separate and retains six extended diagnostic figures and two tables. See [page-limit revision notes](PAPER_PAGE_LIMIT_NOTES.md). The prior 12-page version is archived; all scientific results, source models and freezes are unchanged.

---

# Combined paper and original training study

7 November 2026: the paper and editable slides now include the separately frozen [32-new-target replication](../xai_replication_32/README.md). Across both studies there are 80 unique institutions. The new primary is ΔQ -0.0075, nominal 95% interval [-0.0402,0.0241], 30 complete pairs. Dense 64-origin h1 is +0.0001, interval [-0.0229,0.0248]. Both remain inconclusive about degradation or equivalence. The stronger-looking original history-median secondary pattern does not recur as a zero-excluding interval in the new cohort. Source/model/ISP reuse and undefined-score exclusions remain explicit.

Use the original full training notebooks here together with the new `../xai_replication_32/XAI_Replication_32.ipynb` analysis companion. Its default reads audited batch outputs and recomputes local arithmetic and the primary bootstrap; opt-in full evaluation runs on an isolated copy. The added batch XAI evaluations took about 35 minutes on CPU with no retraining. See PAPER_REPLICATION_REVISION_NOTES.md for the combined manuscript, and the new cohort RESULTS_BRIEF.md for all fixed sensitivities. The original scientific study below remains unchanged.

---

# Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting

Status: full frozen study executed; manuscript and editable presentation prepared. The old development-only status is superseded by `results/STUDY_COMPLETE.json`. Historical protocol/hash manifests are preserved without rewriting their freeze-time status.

## Start here

- `XAI_Complete_Experiment.ipynb`: main notebook, 95 cells, full inline forecasting/XAI implementation, EDA, actual Ridge refit, local explanations, global analyses and reproduced primary bootstrap. See `NOTEBOOK_GUIDE.md`; use `requirements-notebook.txt`.
- `XAI_Results_and_Reproduction.ipynb`: earlier short results companion.

- `RESULTS_BRIEF_ID.md`: findings, honest publication assessment, remaining author/venue decisions.
- `paper/paper.pdf` and `paper/paper.tex`: English IEEE-style expanded anonymous draft, 7 pages including references, 6 figures and 18 cited references; editable overall TikZ pipeline and BibTeX source included. Adapt to the selected conference before submission.
- `presentation/XAI_Research_Results_v4.pptx`: 17 editable slides in Indonesian; opening, gap/goal, pipeline, results. Charts, tables, diagram and text remain native objects.
- `LITERATURE_AND_GAP.md`: closest work, bounded novelty and distinct future-paper directions.
- `FULL_PROTOCOL.md`, `ANALYSIS_CLARIFICATIONS.md`: frozen experimental and statistical decisions.
- `results/NUMERIC_CLAIMS.json`, `results/FINAL_VALIDATION.json`: authoritative headline estimates and final integrity/arithmetic audit.

Full training and batch evaluation were also executed locally on 6 November 2026 in `XAI_Full_Local_Run.ipynb` (58 code cells, no errors). See `FULL_LOCAL_RUN.md` and `results/LOCAL_REPRODUCTION_COMPARISON.json` for the fresh-run record and baseline comparisons.

See `PAPER_REVISION_NOTES.md` for the 6 November paper expansion, runtime explanation and remaining validity limitations.

## Main finding

The prespecified frozen GRU / 1h / source-calendar Shapley target-minus-source Q is -0.018876, nominal 95% paired block-bootstrap interval [-0.089139, 0.053345], seven complete institution pairs, 1,853 valid of 2,000 attempted draws. This does not establish systematic degradation, equivalence or non-inferiority. Reference-dependent secondary differences are exploratory and unadjusted for multiplicity. IG numerical rejection is 210/3360 = 6.25%; rejected cases are retained and never assigned an IG ranking score.

Forecast target macro MASE (1h / 6h): Ridge 0.681 / 0.813; DLinear 0.682 / 0.812; GRU 0.684 / 0.909. These are means over 15 available institution-year cells after averaging neural seeds, not significance tests or a balanced panel.

## Dataset and scope

CESNET-TimeSeries26 official institutional hourly byte volumes, 48 fixed institutions: 32 source, 8 validation, 8 target. Full training uses 227,478 source windows and no target gradient fitting. Evaluation considers eligible April–June 2025/2026 endpoints. One target institution lacks an eligible 2026 cell, reducing the complete paired panel to seven pairs. The 480 attribution origins per fitted model are timestamp-matched source/target cases selected without outcomes. Do not describe the many repeated method/operator/seed records as independent subjects.

See `DATA_ATTRIBUTION.md`. No Westermo/BigFlows/botnet/VPN/Tor captures are mixed into this benchmark. Old recovered experiments and their results are historical pilots, not results of this study.

## Reproduction

Python 3.11; CPU, four threads. `requirements-full.txt` records the executed core package versions. Use a copy of this folder for reruns: scripts write to their own parent project directory and overwrite the corresponding generated results. Preserve the delivered original for comparison.

From a copied study directory, create an environment and install requirements, then run:

```sh
python src/train_full.py
python src/evaluate_forecasts.py
python src/evaluate_attributions.py
python src/analyze_full.py
python src/validate_full_results.py
```

Training was approximately 318 seconds in the recorded run; hardware and software differences can change timing and numerical results. Seeds, hyperparameter selection, source-only normalization, selected epochs and checkpoint hashes are recorded. Exact byte-identical retraining is not promised across systems. To validate the delivered run without retraining, run only `src/validate_full_results.py`.

The 48 selected derived hourly files, models, predictions and detailed attribution results are included. Raw 1.7GB archive is not bundled. `src/prepare_full_data.py` and development scripts are historical extraction/development entry points and depend on sibling pilot artifacts; they are not required for the full benchmark rerun above. The raw archive's verified MD5 is cf06f8036df9b5b9652cbab7c148f2c5. Source member and derived hashes are in `data/MANIFEST.json`; the common native-time coverage fields are retained in every derived file.

Paper rebuild from the `paper` directory: `pdflatex paper.tex` twice (IEEEtran and TikZ needed). Presentation source is under `presentation/source/`; it uses the bundled OpenAI Artifact Tool runtime, not Python. The delivered PPTX is directly editable without that runtime. Native PowerPoint/Google Slides save-and-reopen behavior has not been tested; package, import, chart-workbook, typography, arithmetic and rendered layout checks were performed locally.

## Audit trail and interpretation

- `FULL_PREFIT_HASHES.json` and `FULL_PREEVALUATION_HASHES.json` record local freeze-time hashes. Their `target_outcomes_scored:false` describes the historical freeze and is intentionally unchanged. This is not a public preregistration.
- The post-evaluation audit script was added after outcomes, without modifying the frozen model, metrics or analysis. Its initial JSON serialization bug (NumPy bool) was corrected; no result computation or hypothesis changed.
- `primary_complete_pair_cells.csv` is a reporting derivative of frozen analysis output, equal-year weighted and limited to complete primary pairs. It avoids visually mixing incomplete pair 2 into the primary figure.
- Existing `primary_pair_contrasts.png` is an all-available descriptive plot, including incomplete pair 2; use `primary_complete_pairs.pdf/png` for the primary panel shown in the paper.
- Q is ranking alignment with controlled forecast-response operators. It is not a causal truth score, predictive-risk probability or universal explanation correctness measure.
- All institutions belong to one ISP. Missingness, model choice, seven day groups and finite numerical budget limit generalization.

No paper has been submitted or externally published. Author names, affiliations, target venue and its disclosure/format requirements still need to be finalized by the authors.
