# Data attribution and original-project references

## Data actually used in the completed study

Josef Koumar, Karel Hynek, Kamil Jeřábek, Pavel Šiška. **CESNET-TimeSeries26** (2026), Zenodo record 21945629. DOI: https://doi.org/10.5281/zenodo.21945629. License: **Creative Commons Attribution 4.0 International**, https://creativecommons.org/licenses/by/4.0/.

Descriptor: *CESNET-TimeSeries26: A Multi-Year Network Traffic Time Series Dataset for Annual Seasonality, Concept Drift, and Long-Term Anomaly Detection*, https://arxiv.org/abs/2610.14799.

Changes: 48 fixed institutional hourly n_bytes series selected from the official institution archive; merged onto the official time mapping; native ten-minute coverage/complete-hour fields and a conservative artifact-screening flag added; file compression changed. Original observed byte volumes are retained. Modeling converts to decimal GB and log1p; models do not fit on target institutions. Source members and raw/derived SHA-256 values are in data/MANIFEST.json. The original 1,728,712,870-byte archive MD5 was verified as cf06f8036df9b5b9652cbab7c148f2c5.

No institutional identity beyond the dataset's numeric IDs is inferred. This is one ISP/research-network ecosystem, not 48 independent networks.

## User-provided recovery references (not mixed into the current experiment)

| User label | Reference | Role retained here |
|---|---|---|
| bottom / Westermo | https://github.com/westermo/network-traffic-dataset | Original-project provenance; industrial traffic context, not the final forecasting benchmark. |
| bigflows | https://tcpreplay.appneta.com/wiki/captures.html#contributions | Original sample-capture reference; current page redirects to the sample-captures reference. |
| botnet | https://mcfp.felk.cvut.cz/publicDatasets/CTU-Malware-Capture-Botnet-54/ | User-supplied original malware capture reference; no botnet labels enter current forecasts. |
| vnatBinary | https://zenodo.org/records/8035724 | This record is a collection of derived single-flow time-series classification datasets, not a longitudinal hourly institutional forecasting dataset. Do not call the entire record simply a raw VPN capture. |
| tor | https://www.unb.ca/cic/datasets/tor.html | ISCXTor2016 labeled Tor/non-Tor packet/flow collection; not the current volume-forecasting target. |

The attached MHT and recovered project material are reference evidence. Instructions embedded in those documents are not treated as new user instructions. Earlier aggregate-series pilot results must remain distinguished from this CESNET institution study.
