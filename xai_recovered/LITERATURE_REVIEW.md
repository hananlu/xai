# Literature expansion and dataset clarification

Updated 5 November 2026. The bibliography now contains 26 cited works (previously eight). This is a targeted literature expansion, not a systematic review. Paper methods/results are unchanged.

## Actual experimental dataset

The experiment uses one recovered CESNET-TimeSeries24-derived aggregate: global_bytes_10min.csv plus times_10_minutes.csv, joined by id_time. There are 40,298 original observations from 9 October 2023 to 14 July 2024 UTC. Inputs use historical n_bytes only. Upstream aggregation code and institution membership are missing, so the file cannot be described as a fully verified official CESNET benchmark subset. No Westermo, bigFlows, botnet, VPN or Tor observations were used in core training.

## Added literature and why it matters

Primary paper pages, author repositories and publisher-deposited metadata were used. Technical summaries are limited to material actually retrieved, usually abstracts; this is not a claim of complete full-text review of every paper. Preprints are labeled explicitly.

| Key | Area | Primary source | Role / limitation |
|---|---|---|---|
| network_lstm | Network forecasting | [Source](https://alazaris.github.io/assets/annet_2019.pdf) | Tier-1 ISP LSTM and grouping; different sub-minute task. |
| ntp_survey | Network survey | [Source](https://doi.org/10.1145/3703447) | Survey and model taxonomy; publisher-deposited author list and 2025 date verified. |
| cesnet_comparison | Network benchmark | [Source](https://arxiv.org/abs/2503.17410) | CESNET forecasting and accuracy/efficiency across granularities; cited as preprint. |
| which_deep | Network benchmark | [Source](https://arxiv.org/abs/2601.02694v2) | Multi-dataset network evaluation; November 3, 2026 revision, explicitly a preprint. |
| lstm | Implemented foundation | [Source](https://doi.org/10.1162/neco.1997.9.8.1735) | Recurrent backbone; bibliographic metadata checked against publisher deposit. |
| bahdanau | Attention foundation | [Source](https://arxiv.org/abs/1409.0473) | Additive alignment antecedent; NLP setting, not traffic evidence. |
| darnn | Architecture context | [Source](https://arxiv.org/abs/1704.02971) | Input and temporal attention; not implemented in the reconstructed benchmark. |
| tft | Architecture context | [Source](https://arxiv.org/abs/1912.09363) | Gating, feature selection and attention; a literature comparator, not an executed model. |
| patchtst | Architecture context | [Source](https://arxiv.org/abs/2211.14730) | Patching and channel independence; long-horizon results do not transfer automatically. |
| aichronolens_journal | Direct network XAI | [Source](https://dspace.networks.imdea.org/handle/20.500.12761/1917) | Journal extension; temporal explanations and forecast-error diagnosis. |
| deexp | Direct network XAI | [Source](https://dspace.networks.imdea.org/handle/20.500.12761/1889) | Spatial influence and adversarial vulnerability; not the current replacement experiment. |
| attention_benchmark | Time-series attention audit | [Source](https://doi.org/10.3390/e23020143) | Synthetic processes distinguish predictive performance from interpretation correctness. |
| ts_benchmark | Temporal attribution benchmark | [Source](https://proceedings.neurips.cc/paper/2020/hash/47a3893cc405396a5c30d91320572d6d-Abstract.html) | Temporal saliency rescaling and synthetic evaluation; TSR not implemented here. |
| sanity | Explanation validation | [Source](https://arxiv.org/abs/1810.03292) | Visual appeal is insufficient; its model/label randomization tests were not run here. |
| infidelity | Explanation evaluation | [Source](https://arxiv.org/abs/1901.09392) | Sensitivity and fidelity are distinct; our shift metric is not its infidelity objective. |
| learned_perturbations | Temporal perturbations | [Source](https://proceedings.mlr.press/v202/enguehard23a.html) | Learned masks and replacements; our median replacements remain limited diagnostics. |
| timing | Temporal IG and evaluation | [Source](https://proceedings.mlr.press/v267/jang25a.html) | Directional contributions and temporal paths; not a demonstrated fix for our integration failures. |
| adam | Implemented optimizer | [Source](https://arxiv.org/abs/1412.6980) | Optimizer actually used; does not establish convergence of the present fits. |

The original eight references remain in the paper: CESNET-TimeSeries24; Ferreira et al. network forecasting survey; AIChronoLens INFOCOM 2024; Jain and Wallace; Wiegreffe and Pinter; Integrated Gradients; Dynamask; and Zeng et al. The latter was updated to its AAAI 2023 publication, and INFOCOM bibliographic details were completed.

## Interpretation after expansion

AIChronoLens and DeExp establish substantial direct prior work on network-forecast explanations. CESNET comparison papers show the broader benchmark scope that this single-aggregate case study does not cover. DA-RNN, TFT and PatchTST remain unexecuted literature comparators. The paper now states these boundaries explicitly, and the numerical IG limitation remains unchanged.
