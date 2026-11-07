# Focused conference checks

These additions are post-hoc. Original/new-cohort primary estimands and scientific freezes remain unchanged. No new dataset, model fitting, or new explanation method is claimed.

## Common-case absolute ranking alignment

| Method | A source | A target | B source | B target |
|---|---:|---:|---:|---:|
| shapley | 0.6941 | 0.6902 | 0.6818 | 0.7004 |
| ig | — | — | 0.6815 | 0.7046 |
| occlusion | 0.6908 | 0.6869 | 0.6813 | 0.7038 |
| recency | 0.5415 | 0.5335 | 0.4540 | 0.4661 |

Panel A: all main-budget cases common to Shapley/occlusion/recency. Panel B: original IG subset, all four methods common and IG accepted. Each method must have all three defined training seeds. Within-panel cases are identical; cross-panel populations differ. Q=0 is the exact random-order mean, not a universal explanation-ground-truth reference. Means are descriptive with equal institution weighting after operator/year aggregation.

Counts:

```json
[
  {
    "panel": "A",
    "cohort": "source",
    "planned_history_operator_cases": 2016,
    "common_history_operator_cases": 1813,
    "retained_institutions": 31,
    "retained_institution_years": 61,
    "all_methods_three_seeds": true,
    "all_required_operators_per_institution_year": true
  },
  {
    "panel": "A",
    "cohort": "target",
    "planned_history_operator_cases": 2016,
    "common_history_operator_cases": 1824,
    "retained_institutions": 31,
    "retained_institution_years": 61,
    "all_methods_three_seeds": true,
    "all_required_operators_per_institution_year": true
  },
  {
    "panel": "B",
    "cohort": "source",
    "planned_history_operator_cases": 504,
    "common_history_operator_cases": 451,
    "retained_institutions": 31,
    "retained_institution_years": 61,
    "all_methods_three_seeds": true,
    "all_required_operators_per_institution_year": true
  },
  {
    "panel": "B",
    "cohort": "target",
    "planned_history_operator_cases": 504,
    "common_history_operator_cases": 452,
    "retained_institutions": 31,
    "retained_institution_years": 60,
    "all_methods_three_seeds": true,
    "all_required_operators_per_institution_year": true
  }
]
```

## Learned-layer parameter sensitivity

126 fixed histories, three trained seeds, three randomization replicates, two cumulative stages; 2268 comparison records. Copied-model max difference 0.0. Source normalization and the fixed last-input residual route remain intact.

```json
{
  "status": "complete",
  "post_hoc": true,
  "scope": "earliest frozen IG origin/pair/year/cohort; frozen GRU h1 source-calendar Shapley",
  "trained_allocation_records": 378,
  "trained_nonflat_records": 378,
  "trained_clipped_records": 17,
  "summaries": [
    {
      "metric": "pattern_distance",
      "cohort": "source",
      "stage": "head",
      "mean_equal_institutions": 0.6195955508550605,
      "median_institution": 0.6967922073034964,
      "institutions": 32,
      "common_comparison_records": 337,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 425,
      "trained_nonflat": 567,
      "randomized_nonflat": 425,
      "randomized_clipped": 203
    },
    {
      "metric": "pattern_distance",
      "cohort": "source",
      "stage": "head_gru",
      "mean_equal_institutions": 0.5700579909255958,
      "median_institution": 0.4545144175199938,
      "institutions": 32,
      "common_comparison_records": 337,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 342,
      "trained_nonflat": 567,
      "randomized_nonflat": 342,
      "randomized_clipped": 225
    },
    {
      "metric": "pattern_distance",
      "cohort": "target",
      "stage": "head",
      "mean_equal_institutions": 0.5648944512230974,
      "median_institution": 0.598493760815088,
      "institutions": 32,
      "common_comparison_records": 364,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 439,
      "trained_nonflat": 567,
      "randomized_nonflat": 439,
      "randomized_clipped": 167
    },
    {
      "metric": "pattern_distance",
      "cohort": "target",
      "stage": "head_gru",
      "mean_equal_institutions": 0.5311740628364279,
      "median_institution": 0.4546202884310233,
      "institutions": 32,
      "common_comparison_records": 364,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 367,
      "trained_nonflat": 567,
      "randomized_nonflat": 367,
      "randomized_clipped": 201
    },
    {
      "metric": "rank_spearman",
      "cohort": "source",
      "stage": "head",
      "mean_equal_institutions": 0.7162182451105443,
      "median_institution": 0.7333829365079367,
      "institutions": 32,
      "common_comparison_records": 337,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 425,
      "trained_nonflat": 567,
      "randomized_nonflat": 425,
      "randomized_clipped": 203
    },
    {
      "metric": "rank_spearman",
      "cohort": "source",
      "stage": "head_gru",
      "mean_equal_institutions": 0.11905375810625934,
      "median_institution": 0.05463699800100991,
      "institutions": 32,
      "common_comparison_records": 337,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 342,
      "trained_nonflat": 567,
      "randomized_nonflat": 342,
      "randomized_clipped": 225
    },
    {
      "metric": "rank_spearman",
      "cohort": "target",
      "stage": "head",
      "mean_equal_institutions": 0.7185323217828798,
      "median_institution": 0.7187500000000002,
      "institutions": 32,
      "common_comparison_records": 364,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 439,
      "trained_nonflat": 567,
      "randomized_nonflat": 439,
      "randomized_clipped": 167
    },
    {
      "metric": "rank_spearman",
      "cohort": "target",
      "stage": "head_gru",
      "mean_equal_institutions": 0.16174042249260281,
      "median_institution": 0.1450960193141511,
      "institutions": 32,
      "common_comparison_records": 364,
      "common_histories": 63,
      "planned_comparison_records": 567,
      "stage_metric_defined": 367,
      "trained_nonflat": 567,
      "randomized_nonflat": 367,
      "randomized_clipped": 201
    }
  ],
  "common_stage_panels": true,
  "aggregation": "seed/replicate records within history, available years within institution, equal institutions",
  "inference": "descriptive conditional pattern sensitivity; no pass threshold/CI/superiority test; fixed residual retained"
}
```

Pattern/rank diagnostics are conditional on common comparable cases across both stages; all flat, clipped and undefined outcomes remain recorded. Dots in the plot are institution means, not independent seed/replicate tests. There is no prescribed pass threshold. Sensitivity does not prove causal demand correctness or universal usefulness; operator-normalized Q need not fall when the model and response game both change.
