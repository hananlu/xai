# Results: 32 new targets within CESNET

**This is a within-network replication using the original locked models and reused source anchors.** The old outcome was known before this protocol; new-target scoring followed the local membership/code/data freeze. No external preregistration, model refitting, target tuning or replacement of missing institutions occurred.

## Primary result

-0.0075; 95% interval [-0.0402, 0.0241]; 30 pairs; 1885/2,000 valid draws

Do not interpret a failed/zero-containing interval as equivalence or absence of a transfer effect. The primary remains the original pair/within-pair block procedure; the sensitivity intervals do not replace it.

## Prespecified uncertainty sensitivities

- Pair only: -0.0075; 95% interval [-0.0350, 0.0188]; 30 pairs; 2000/2,000 valid draws
- Synchronized calendar blocks: -0.0075; 95% interval [-0.0422, 0.0313]; 30 pairs; 1872/2,000 valid draws

## Nested explanation budget

### Horizon 1

- main_original_pair_block: -0.0075; 95% interval [-0.0402, 0.0241]; 30 pairs; 1885/2,000 valid draws
- dense_original_pair_block: 0.0001; 95% interval [-0.0229, 0.0248]; 30 pairs; 2000/2,000 valid draws
- common_pair_main: -0.0075; 95% interval [-0.0402, 0.0241]; 30 pairs; 1885/2,000 valid draws
- common_pair_dense: 0.0001; 95% interval [-0.0229, 0.0248]; 30 pairs; 2000/2,000 valid draws
- Dense pair-only: 0.0001; 95% interval [-0.0210, 0.0216]; 30 pairs; 2000/2,000 valid draws
- Dense synchronized blocks: 0.0001; 95% interval [-0.0258, 0.0276]; 30 pairs; 1995/2,000 valid draws

### Horizon 6

- main_original_pair_block: -0.0034; 95% interval [-0.0417, 0.0314]; 30 pairs; 1981/2,000 valid draws
- dense_original_pair_block: -0.0197; 95% interval [-0.0534, 0.0090]; 30 pairs; 1988/2,000 valid draws
- common_pair_main: -0.0034; 95% interval [-0.0417, 0.0314]; 30 pairs; 1981/2,000 valid draws
- common_pair_dense: -0.0197; 95% interval [-0.0534, 0.0090]; 30 pairs; 1988/2,000 valid draws
- Dense pair-only: -0.0197; 95% interval [-0.0536, 0.0098]; 30 pairs; 2000/2,000 valid draws
- Dense synchronized blocks: -0.0197; 95% interval [-0.0553, 0.0116]; 30 pairs; 1975/2,000 valid draws

## Accuracy and audit

Model | h1 MASE | h6 MASE
--- | ---: | ---:
persistence | 1.4083 | 2.4278
daily | 1.8642 | 1.8243
weekly | 1.6728 | 1.6740
ridge | 30.8226 | 57.3240
dlinear | 1.2082 | 1.3750
gru | 9.6824 | 64.1495

Main audit: 705,600 operator/seed/arm/reference/horizon records; 690 of 14,112 IG checks rejected. These are repeated computational records, not independent institutions.

Main: 2,016 histories per fit, 63 available pair-years. Dense: 8,064 histories per GRU seed. Pair 1 (source 260, target 8) has no common eligible origins in 2026 and is not replaced. Pair 4 (source 281, target 267) has no complete three-seed paired primary scores. Undefined response denominators are retained; the primary is conditional on the 30 informative complete pairs.

Original eight-target result: -0.0189, nominal interval [-0.0891, 0.0533], seven complete pairs. It is reported separately. Overall there are 80 unique institutions: 32 sources, eight validation institutions, eight old targets and 32 new targets.

## Scientific scope

The useful conference contribution is an audited empirical deployment comparison, numerical failure accounting, and an explicit sensitivity analysis of uncertainty and timestamp density. It is not a new Shapley/IG method. New targets improve within-CESNET coverage, while source/model reuse, one ISP, clipped low-volume predictions, missing periods, controlled replacement distributions and limited specialized baselines remain material limitations. Query count alone is not evidence of validity.

See the JSON/CSV outputs for every endpoint and failure count. Figure scripts only read results; scientific source and protocol hashes remain frozen.

## Post-hoc scale diagnostic

After inspecting extreme forecast MASE, we retained all target cells and the original scale/floor. Target 267 has 2024 weekly scale 750.7 bytes. Seed-specific MASE reaches 5921.0, despite absolute errors of only a few MB. Median MASE and the scale plot are descriptive diagnostics, not replacements for the frozen mean.
