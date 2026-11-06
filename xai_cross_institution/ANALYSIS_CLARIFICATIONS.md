# Analysis implementation clarifications before final evaluation

These implement, rather than change, FULL_PROTOCOL.md. Written before new target outcomes are evaluated.

- A neural attribution case contributes to a seed-averaged endpoint only when all three seeds have a defined, accepted Q. Deterministic Ridge requires its one case. Keep incomplete cases and counts in exclusion files.
- A matched primary pair contributes to the four-cell aggregate only if paired valid source/target cases exist for both operators in both years. Average within year/operator, then equally across the four cells, then equally across retained pairs.
- Bootstrap draws resample pairs and observed 14-day blocks within each retained pair/year, carrying source/target and operator rows together. A draw lacking an operator cell is invalid and is counted. Report an interval only with at least 1,000 valid draws from the planned 2,000; otherwise give the point estimate and interval failure status. Fewer than four complete pairs precludes an inferential headline.
- Raw-GB forecast group averages describe institutions of different volume. MASE comparisons and same-institution model comparisons are emphasized. Any unmatched source/target forecast contrast is descriptive, not a causal effect or a matched-origin transfer penalty.
- Exact Shapley numerical checks and random/response-oracle arithmetic are checked separately from operator ranking alignment. The latter is not a universal attribution correctness score.
