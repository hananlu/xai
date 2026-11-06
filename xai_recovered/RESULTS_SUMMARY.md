# Results and pipeline decision

Recovery, reconstruction, experiments and the eight-page paper draft are complete.

The strongest tested short-term comparators are Ridge and last-state LSTM. Learned Attention did not improve their accuracy under the fixed budget. Keep Ridge as the transparent baseline and last-state LSTM as the neural comparator; treat Attention as an audited experimental variant. This is a result on one recovered aggregate, not a universal model ranking.

| Model | MAE, 10 min (GB) | MAE, 60 min (GB) |
|---|---:|---:|
| Persistence | 10.347 | 13.427 |
| Ridge | 8.869 | 11.075 |
| LSTM last-state, 24h | 8.883 | 11.147 |
| Learned Attention, 24h | 10.340 | 13.336 |
| Learned Attention, 48h | 10.348 | 13.443 |

All models share 5,806 held-out origins. Recurrent values average three seeds. GB means decimal gigabytes per interval. Complete metrics and seed variation are in results/forecast_summary.csv.

The practical explanation pipeline uses direct block replacements for recurrent models and exact fitted contributions for Ridge. IG32 results are provisional: the secondary 2,048-step check still finds completeness errors above 0.1 GB in three of six model/seed combinations on the fixed 16-origin subset. No conclusion relies on IG being a validated reference.

Artifact checks passed: 15 original hashes, 19 forecast files, 38 recomputed metric records and 15 checkpoint consistency checks. The maximum checkpoint discrepancy was 0.00001279 GB. All eight PDF pages were visually reviewed.

The paper is paper/paper.pdf; editable sources and numerical claim records are alongside it. See README.md to reproduce, PROTOCOL.md for the frozen primary design, and EXECUTION_NOTES.md for disclosed secondary analyses.

The expanded paper now cites 26 works; see LITERATURE_REVIEW.md for dataset clarification and the annotated literature additions.
