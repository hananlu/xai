# Dataset attribution

Derived selected series in data/ originate from:

Josef Koumar, Karel Hynek, Kamil Jeřábek and Pavel Šiška. **CESNET-TimeSeries26: A Multi-Year Network Traffic Time Series Dataset for Annual Seasonality, Concept Drift, and Long-Term Anomaly Detection.** Zenodo, record 21945629, published 15 August 2026. [Dataset DOI](https://doi.org/10.5281/zenodo.21945629). License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

Changes made for this pilot: select 12 institutions using training-only rules; retain n_bytes and explicit UTC time joins; add ten-minute coverage, completeness, and conservative measurement-artifact flags; compress exported CSVs. No claim is made that these derived files are an official dataset subset. Selection hashes and source member SHA-256 values are in data/DATA_AUDIT.json.

The full raw institutional archive is kept outside this deliverable under work/novelty_audit/data/. Source series remain pseudonymous. Exported data have not been mapped to named institutions.

Companion descriptor: Koumar et al., [arXiv:2610.14799](https://arxiv.org/abs/2610.14799), 10 October 2026, preprint. Literature PDFs are not bundled; retrieval manifests retain links and hashes.
