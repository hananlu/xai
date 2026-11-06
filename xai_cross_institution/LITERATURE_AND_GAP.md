# Literature positioning, checked 5 November 2026

This is a focused narrative review, not an exhaustive systematic review. Key full texts and official metadata were checked during the audit; inclusion does not mean every paper was reproduced. The manuscript has 18 cited references, selected for a direct role rather than a target citation count.

## Closest work and claims we must not make

| Primary source | Established contribution relevant here | Consequence for this project |
|---|---|---|
| [TransMUSE, Computer Networks 2023](https://doi.org/10.1016/j.comnet.2022.109518) | Traffic forecaster transfer between edge cohorts. | No “first cross-site traffic forecasting” claim. |
| [AIChronoLens, IEEE TMC 2025](https://doi.org/10.1109/TMC.2025.3554035) | Temporal explanations for network forecasts and their use in error analysis/improvement. | No “first temporal XAI for traffic” or generic error-repair novelty. |
| [TimeSAE, ICML 2026](https://arxiv.org/abs/2601.09776v2) | Explanation generalization, including out-of-distribution settings, with a sparse latent approach. | This is accepted ICML work, not merely an unreviewed preprint. No “first explanation transfer under shift” claim. Our methods differ, and we did not benchmark TimeSAE. |
| [TIMING, ICML 2025](https://proceedings.mlr.press/v267/jang25a.html) | Temporal path considerations and cancellation-aware cumulative-response evaluation. | CPD/cancellation awareness is prior art. Our operator-specific random/oracle normalization is an operational definition, not a claimed fundamental new metric. |
| [Learning Perturbations, ICML 2023](https://proceedings.mlr.press/v202/enguehard23a.html) | Learning masks and associated perturbations for time-series explanations. | Replacement realism is a substantive issue; fixed interpolation/rotation do not solve it. |
| [InterpretTime, Nature Machine Intelligence 2023](https://doi.org/10.1038/s42256-023-00620-w) | Quantitative evaluation of post-hoc explanations for time-series classification. | Evaluation methodology and distributional effects of corruption are not new observations. Classification evidence is not a direct result on our forecasting task. |
| [Explaining Aggregated Network Traffic Predictors, IFIP Networking 2025](https://opendl.ifip-tc6.org/db/conf/networking/networking2025/1571141805.pdf) | Explanations for aggregated network predictors. | Aggregation itself is not our novelty. |
| [DeExp, IEEE TMC 2025](https://hdl.handle.net/20.500.12761/1889) | Network forecast model vulnerabilities investigated using explainability and traffic injection. | Perturbation sensitivity and network-XAI vulnerabilities already have prior work. |

## Measurement and model foundations used in the manuscript

| Source | Role |
|---|---|
| [CESNET-TimeSeries26 descriptor, 2026](https://arxiv.org/abs/2610.14799) and [official data](https://doi.org/10.5281/zenodo.21945629) | Observed multi-year institutional byte-volume series; source attribution and scope. |
| [Comparative Analysis of Deep Learning Models for Real-World ISP Network Traffic Forecasting, 2025](https://arxiv.org/abs/2503.17410) | Existing empirical ISP forecasting work. |
| [DLinear / Are Transformers Effective for Time Series Forecasting?, AAAI 2023](https://arxiv.org/abs/2205.13504) | Strong simple linear forecasting baseline; no need to assume more complexity improves accuracy. |
| [Cho et al., EMNLP 2014](https://arxiv.org/abs/1406.1078) | GRU foundation; our compact implementation is not a new recurrent architecture. |
| [Integrated Gradients, ICML 2017](https://proceedings.mlr.press/v70/sundararajan17a.html) | Raw-output path attribution and completeness. |
| [SHAP, NeurIPS 2017](https://papers.nips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html) | Shapley-based prediction explanations; we enumerate the explicit seven-group game. |
| [The Many Shapley Values, ICML 2020](https://proceedings.mlr.press/v119/sundararajan20b.html) | Different games/references can encode different explanatory questions. |
| [Visualizing the Impact of Feature Attribution Baselines, Distill 2020](https://distill.pub/2020/attribution-baselines/) | Baseline interpretation and contrast sensitivity. |
| [Sanity Checks for Saliency Maps, NeurIPS 2018](https://proceedings.neurips.cc/paper_files/paper/2018/hash/294a8ed24b1ad22ec2e7efea049b8737-Abstract.html) | Visual plausibility alone is insufficient evidence. |

Further frontier checks from the earlier audit include [IB-Forecast, July 2026 preprint](https://arxiv.org/abs/2607.28124), on structured context/residual masking, and [Which Deep Learner?, revised November 2026](https://arxiv.org/abs/2601.02694v2), on network forecasting with incomplete data. They are not implemented baselines here. We do not claim residual masking, missing-data benchmarking, or foundation-model explanation as new contributions.

## The defensible gap

A bounded empirical question remains: in this institution-disjoint, hourly network-volume setting, how much evidence supports temporal ranking reliability when numerical acceptance, reference semantics and replacement-operator alignment are reported separately, with timestamp-paired institutions and institution/block inference?

The study contributes the executed benchmark and measured deployment contrasts. A combination of controls is useful empirical differentiation, but it is weaker novelty than a new explanation algorithm and is not a guarantee of acceptance. Literature search does not establish an absolute “first.”

The primary result is inconclusive (-0.0189; nominal 95% interval [-0.0891, 0.0533]). The strongest honest narrative is measurement-aware reliability evaluation with explicit failure/availability reporting. Do not claim proven general degradation, universal explainer superiority, causal demand identification or cross-ISP generalization.

## Separate future-paper possibilities

1. **Conditional History Replacement for Network Forecast Explanations.** Learn an independently validated conditional replacement distribution and test on a second network. A learned replacement alone is not novel because perturbation learning exists; novelty would require a network-specific estimand, validation and evidence beyond the current fixed operators.
2. **Numerical Reliability of Path Attributions in Nonnegative Forecasting.** Characterize output-unit transformations and clipping boundaries across model families, with a principled numerical remedy and controlled ground-truth tests. Numerical rejection counts or completeness checks alone are insufficient novelty.

Both are new research proposals requiring a fresh protocol, overlap review and distinct experiments. They should not be produced by relabeling or splitting the same results into redundant papers.
