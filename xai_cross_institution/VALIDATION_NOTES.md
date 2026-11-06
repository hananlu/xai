# Final validation notes

The frozen full experiment passed the independent post-evaluation audit in `results/FINAL_VALIDATION.json`:

- Both pre-fit and pre-evaluation protocol/code hash sets match.
- All 48 selected derived data hashes and every trained model/profile hash match.
- Institution membership is unique: 32 source / 8 validation / 8 target.
- All 3,160 saved forecast metric rows were recalculated from 684,640 stored prediction rows; maximum difference was zero at stored precision.
- Representative predictions and true labels were re-queried across all ten forecast fits, institutions, available years, arms and horizons; maximum difference was 1.43e-13 GB.
- Sampled exact Shapley games for all three model families agree with independent 7! permutation enumeration within 4.89e-15 GB.
- Sampled ranking Q re-queries match saved values; the primary equal-cell/equal-pair point estimate was independently recomputed.
- Failed IG cases never receive an IG Q score. Original missingness, non-discriminating denominators, complete-seed restrictions and missing pair-year cells remain in the outputs.

These are integrity/arithmetic checks, not proof of statistical assumptions, causal validity, exhaustive correctness or novelty.

The earlier five-page PDF (now archived) was compiled with resolved citations/references, checked for overfull boxes, rendered page by page and visually inspected. All twelve final PPTX slides were imported, rendered and inspected; diagram direction was corrected during QA. The PPTX passed package/import, declared canvas, font, native table, chart-workbook and explicit IG totals checks. It contains 2 native charts, 2 embedded data workbooks, 5 native tables and 12 speaker-note sections. Chart data are snapshots of the plotted numerical results; there is no claimed external formula/workbook lineage. The original failed intermediary builds remain private and are not delivered.

PowerPoint/Google Slides interactive editing and save/reopen tests were not available. File-level native editability and rendered previews do not establish identical behavior in every viewer. No submission or external publication occurred.

The paper was expanded on 6 November 2026 to nine pages with eight figures. Its bibliography now compiles from references.bib; the vector pipeline is editable TikZ. The revision adds explicit sample-unit/runtime accounting and labeled post-hoc descriptive diagnostics while preserving the primary results and frozen source hashes. See PAPER_REVISION_NOTES.md and results/PAPER_REVISION_VALIDATION.json for the revised-paper checks.
