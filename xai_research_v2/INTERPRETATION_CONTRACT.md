# What the explanation is allowed to mean

For a fixed fitted linear predictor and an explicit reference r, the value contribution is

`c_j = beta_j * (x_j - r_j)`.

These contributions explain the difference `f(x) - f(r)`. They do not directly quantify prediction error, missing-data uncertainty, or the demand that would have been recorded by a healthy monitoring system.

## Pre-experiment analytical control

Suppose a two-lag predictor is `f(x) = 0.2*x_previous + 0.8*x_latest`, with reference `(100,100)`. A complete input `(100,200)` yields 180. If the latest measurement is lost and replaced with 100, the input becomes `(100,100)` and the prediction becomes 100. The contribution of the imputed value relative to that reference is zero; the prediction has still shifted by 80. A measured future target of 180 would give clean absolute error 0 and corrupted error 80.

Completeness remains valid: the sum of contributions equals `f(corrupted)-f(reference)=0`. The unsupported inference would be “zero imputed-value attribution means this forecast is reliable”. This counterexample is an elementary consequence of reference-relative attribution, not a new theorem or an observed empirical result. The pilot asks whether its implications occur across the selected network series, and whether observation-mask dependence supplies useful additional diagnostics.

## Four distinct claims

| Claim | What can establish it in this project |
|---|---|
| Attribution arithmetic is correct | Exact linear reconstruction and finite perturbation identity. |
| A fitted model relies on particular input values/masks | An explicitly scoped contribution or a specified input intervention. Results depend on reference/perturbation semantics. |
| The explanation helps identify unreliable forecasts | Separate prediction-error evaluation, cheap comparator scores, held-out periods/institutions, and risk/coverage tests. Arithmetic alone is insufficient. |
| A traffic change has a real operational cause | Independent domain evidence or validated system interventions. Model attribution and native outage metadata alone cannot establish hidden demand. |

Known injected missing locations describe the observation intervention. They are not automatically ground-truth salient features: a good model may ignore a missing lag, infer substitutes, or rely on correlated observed values. Native outages lack the paired original measurements needed to score hidden-demand reconstruction. Synthetic repair using recorded values is an offline simulation with explicit assumptions about retrievability.
