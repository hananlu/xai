# Updated project reference

5 November 2026. This reference supersedes the initial assumption that only a plan survived.

## Objective

Continue the original project on explainable network traffic **forecasting** and produce an evidence-based paper. The previous laptop and its Claude Code repository are unavailable. Recover only from Google Drive and the supplied files; reconstruct missing implementation locally. Do not combine classification results with forecasting results.

## Recovery inventory

Fifteen source artifacts are archived in `recovered/`, with byte sizes, origins and SHA-256 hashes in `recovery_manifest.json`:

- The user's MHT research timeline and paper outline.
- Four forecasting notebooks: Batch 4 CESNET LSTM+Attention; early Network Traffik Forecasting; CESNET Temporal Fusion Transformer exploration; PatchTST-named Westermo data exploration.
- One empty Network Forecast_Reduction notebook.
- Three XAI notebooks about Unicauca traffic **classification**, TreeSHAP, LIME and feature-importance evaluation.
- Six CSVs: two CESNET-derived aggregate/time files and four original candidate datasets (bottom, bigFlows, botnet, vpn_vnat_binary).

Recovered Google Drive locations:

- [farrel](https://drive.google.com/drive/u/2/folders/17TX-5nZ09364Utb5-pKqLjjaFHYeJZq_)
- [farrel/xai](https://drive.google.com/drive/u/2/folders/1xAq-HOmJpC9Kam58-QyZtMrIluwc8HvB)
- [Machine Learning](https://drive.google.com/drive/u/2/folders/1w89ZiTJFCFJM3d4FMpAl9N351gYtQjTj)
- [Batch 4 notebook](https://drive.google.com/file/d/1oD34tYFm0QwD6yNcfuzAb4560-AjJWMY/view)
- [Latest classification notebook](https://drive.google.com/file/d/1U37N9rUN0i07w2RYzrfw78RqAPjwOacF/view)

The complete Drive account was not exhaustively searched. Targeted XAI, forecasting, decision-log and Batch 4 searches plus the relevant folders were inspected. `DATASET_DECISION_LOG.md` and separate `results_batch4.json` were not located. The search hits for those terms were references inside the Batch 4 notebook. The farrel/colab_output listing contains classification/feature-reduction metrics; those files are not treated as forecasting evidence.

## What survived from the experiment

The Batch 4 notebook contains a custom AttentionContext layer, LSTM(96), bounded scalar tanh Attention scores, a one-step regression head, train-only MinMax scaling, chronological 70/15/15 splits, and completed seed-42 outputs. At 10-minute resolution, window 144 yielded RMSE 11.811 GB and MAE 8.877 GB; window 288 yielded RMSE 16.385 GB and MAE 13.408 GB. Multivariate training was skipped because its file was missing.

These are historical outputs, not new reproductions. The notebook resampled timestamps to wall-clock 10-minute bins, replaced zeros with missing values, forward-filled, and produced 40,308 bins from 40,298 original observations. Window lengths used different held-out target sets. Therefore the old result does not isolate the effect of context length. Attention scores were bounded to [-1,1], limiting max/min attention-weight ratio to exp(2). It also saved neither final model checkpoints nor an XAI faithfulness evaluation in the recovered artifact.

The TFT notebook uses CESNET-TimeSeries24 through TS-Zoo with different preprocessing/granularity; it is not a controlled comparator for Batch 4. The PatchTST-named notebook contains Westermo CSV exploration rather than a recovered trained PatchTST model. The earlier forecasting notebook uses dataset.csv and selects `flow_duration_sec` as its target, rather than volume. None of those metrics can be pooled with the new experiment.

## Dataset decisions

The CESNET-derived target has 40,298 positive finite byte-volume observations from 9 October 2023 to 14 July 2024 UTC. The timestamp table contains five departures from a 600-second step. The new pipeline preserves original observations and excludes windows crossing these boundaries. Exact aggregate construction and institution membership cannot be verified because the upstream aggregation script is missing.

The original names supplied by the user remain mapped as follows:

| File | Original reference | Decision for this paper |
|---|---|---|
| bottom.csv | [Westermo](https://github.com/westermo/network-traffic-dataset) | Recovered 25,232 flow rows, about 90 minutes. Whole-flow bytes cannot directly reconstruct bin-level throughput. Archive; exclude from primary forecasting. |
| bigFlows.csv | [Tcpreplay](https://tcpreplay.appneta.com/reference/sample-captures/) | Recovered 66,819 flow rows over about five minutes. Too short for the daily-context task. |
| botnet.csv | [CTU Botnet-54](https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-54/) | Recovered 67,039 flow rows over about 16.3 hours. Flow lifetime totals differ from interval throughput; archive. |
| vpn_vnat_binary.csv | [Zenodo 8035724](https://zenodo.org/records/8035724) | Recovered 43,400 rows of flow metadata/derived features and class labels. It is not the aggregate forecasting target. |
| Tor | [UNB ISCXTor2016](https://www.unb.ca/cic/datasets/tor.html) | Reference retained, but no project Tor file was recovered. |

The file/source mapping follows the user's provenance statement; a byte-for-byte match to original public distributions was not established.

## Chosen pipeline and why

The full frozen design is in `PROTOCOL.md`. The practical choice is a narrow, reproducible study: data audit -> chronological split -> common continuous origins -> simple baselines -> matched residual LSTMs -> XAI sensitivity audit -> bounded scientific claims.

Forecast horizons are 10 and 60 minutes. All models share 24,402 train, 6,039 validation and 5,806 test origins after continuity and weekly-history eligibility. The test targets end on 13 July because the final two gaps leave insufficient uninterrupted weekly history afterward. Standardization fits only the training portion. Forecast units are GB per interval.

Persistence, daily/weekly seasonal naive and validation-tuned Ridge establish whether recurrent complexity is useful. Four recurrent pooling variants distinguish last-state encoding, uniform pooling, bounded Attention and learned additive Attention. An additional 48-hour context condition tests context length. Every recurrent condition uses three seeds, common horizons, hidden width, residual path and optimization budget.

Explanations are evaluated rather than assumed: compare hidden-state Attention rankings against full-model Integrated Gradients, occlusion, recency and random order; perturb two-hour blocks under two replacements; measure ranking agreement, cross-seed stability, completeness error and uniform-weight sensitivity. No causal claims, human-trust claims or universal superiority follow from these diagnostics.

## Updated literature

- Koumar et al. (2025), [CESNET-TimeSeries24](https://doi.org/10.1038/s41597-025-04603-x), Scientific Data 12:338; [dataset record](https://zenodo.org/records/13382427). Supports CESNET context and attribution, not verification of the recovered aggregate.
- Oliveira Ferreira et al. (2023), [Forecasting Network Traffic: A Survey and Tutorial with Open-Source Comparative Evaluation](https://iris.polito.it/handle/11583/2974580), DOI 10.1109/ACCESS.2023.3236261. Positions statistical and neural baselines.
- Fiandrino et al. (2024), [AICHRONOLENS](https://dspace.networks.imdea.org/handle/20.500.12761/1788). Directly relevant prior work on explanations tied to temporal properties of mobile-network forecasting; the project must not claim to introduce XAI for network forecasting.
- Jain & Wallace (2019), [Attention is not Explanation](https://aclanthology.org/N19-1357/), and Wiegreffe & Pinter (2019), [Attention is not not Explanation](https://aclanthology.org/D19-1002/). NLP studies motivate explicit tests; they do not predetermine traffic-model outcomes.
- Sundararajan et al. (2017), [Axiomatic Attribution for Deep Networks](https://proceedings.mlr.press/v70/sundararajan17a.html). Source of Integrated Gradients.
- Crabbé & Van Der Schaar (2021), [Explaining Time Series Predictions with Dynamic Masks](https://proceedings.mlr.press/v139/crabbe21a.html). Motivates temporal awareness in perturbation-based explanation; Dynamask itself is not implemented here.
- Zeng et al., [Are Transformers Effective for Time Series Forecasting?](https://arxiv.org/abs/2205.13504). Motivates simple linear controls without asserting transfer of its long-horizon conclusions.

## Remaining scientific limits

This is one aggregate, one chronological holdout and a limited model family. Three seeds measure training variation, not cross-network replication. Timestamp discontinuities may have monitoring or clock causes that cannot be diagnosed from recovered files. Perturbations can leave the data distribution. Attention pools hidden states mixing multiple lags; the residual branch is outside those weights. A publication decision requires human review, confirmed data rights/provenance, author information and a target venue. These limits do not prevent completing a transparent empirical draft.

## Completed reconstructed experiment

All fifteen recurrent fits and four deterministic baseline conditions have now run locally. Every model uses the same 5,806 held-out origins. New mean MAEs in GB per interval:

| Model | 10-minute horizon | 60-minute horizon |
|---|---:|---:|
| Persistence | 10.347 | 13.427 |
| Ridge | 8.869 | 11.075 |
| LSTM last-state, 24h | 8.883 | 11.147 |
| Uniform pooling, 24h | 10.354 | 13.282 |
| Bounded Attention, 24h | 10.347 | 13.264 |
| Learned Attention, 24h | 10.340 | 13.336 |
| Learned Attention, 48h | 10.348 | 13.443 |

Ridge and last-state LSTM are the strongest tested short-term comparators. Learned Attention does not provide an accuracy advantage over them under the fixed training budget. This is a result of this model family and recovered aggregate, not a universal conclusion about Attention.

The primary XAI audit is complete for 96 fixed origins, two Attention variants and three seeds, including two replacement baselines, random controls and direct prediction recomputation. A disclosed secondary diagnostic separates the persistence residual from the learned correction. An exploratory exact Ridge decomposition reconstructs saved predictions within about 0.00002 GB without refitting.

**IG is numerically provisional.** The planned 32/64-step completeness checks exposed integration failures. A secondary 128/512/2,048-step check on the first 16 fixed origins per model/seed still finds errors above 0.1 GB in three of six combinations, with maximum about 2.70 GB at 2,048 steps. IG-based rankings are therefore not treated as a validated reference. The practical XAI pipeline is direct block intervention for recurrent models plus exact fitted contributions for Ridge, with explicit baseline and noncausal interpretation limits. IG remains a documented diagnostic pending a validated numerical method.

Full metrics, seed variation, temporal-third analyses, paired block-bootstrap contrasts, checkpoint files and per-origin predictions are in `results/`. The English manuscript and editable LaTeX source are in `paper/`. The frozen primary protocol remains unchanged; exploratory additions and the numerical follow-up are documented in `EXECUTION_NOTES.md`.

## Literature expansion

The paper now contains 26 cited references, including direct network-XAI precedents AIChronoLens (INFOCOM 2024 and IEEE TMC 2025), DeExp (2025), CESNET model comparisons (2025), and the November 2026 revision of Which Deep Learner. Time-series-specific references now include attention-interpretability benchmarking, temporal saliency rescaling, learned perturbations and TIMING. The targeted review, primary source links and limitations are in LITERATURE_REVIEW.md. The paper explicitly distinguishes literature comparators from models actually executed. The frozen primary training protocol, data and numerical results are unchanged.
