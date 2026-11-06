# XAI network forecasting — research v2

Target: empirical conference paper, as clarified by the user on 5 November 2026. The completed recovered-data project under ../xai_recovered/ remains v1. This new study does not change its protocol, results or paper.

Read in order:

1. DECISION_AND_RESEARCH_GAP.md — worth/not-worth judgment and candidate contribution.
2. LITERATURE_MATRIX.md and SEARCH_SCOPE.md — actual overlap, reading scope and unresolved novelty checks.
3. DATASET_AND_PIPELINE.md and PROTOCOL_PILOT.md — dataset choice and frozen exploratory design.
4. PILOT_RESULTS_AND_VERDICT.md — generated after the pilot and validation finish.
5. OTHER_PAPER_IDEAS.md and CONFERENCE_STUDY_PLAN.md — distinct future questions and conference pathway.
6. INTERPRETATION_CONTRACT.md — limits of attribution and the prefit analytical control.

## Reproduce the selected-institution pilot

Python 3.11 was used. Install the versions in requirements-pilot.txt into a virtual environment. The pilot does not require PyTorch or a GPU. Run from this directory:

```
python src/pilot.py
python src/analyze_pilot.py
python src/validate_pilot.py
python src/report_pilot.py
```

The data/ directory contains the selected derived series required to reproduce fitting and evaluation. See DATA_ATTRIBUTION.md for source/licensing and modifications. The canonical audit is data/DATA_AUDIT.json. Outcomes in the reserved final period are present in the raw derived files but the pilot code does not score them.

## Reproduce source acquisition / institution selection

The original run acquired the official institutions.tar.gz plus metadata from Zenodo record 21945629. Publisher checksum verification is recorded in data/DATA_AUDIT.json. For selection from scratch, run `python src/fetch_official_data.py` from this project directory. It places the archive and verified metadata under `work/novelty_audit/data/` relative to that working directory. Then run `python src/prepare_data.py` from the same directory. It extracts hourly series and time mappings, checks the full 285-institution candidate pool, then exports the same selected files. This acquisition step needs about 1.73 GB download and several GB temporary disk; it is unnecessary for reproducing the supplied 12-institution pilot.

Core dependency locks, prefit hashes, manifests, selected alphas, per-institution metrics, stress records, checkpoint coefficients and numerical checks are retained. The numerical tolerances apply to float64 calculations and the stated unclipped Ridge functions.

## Scope

Exploratory pilot and research plan; no final conference submission or PPT is produced here. The prior PDF remains a preliminary recovered-data paper. A final v2 paper must use the completed expanded evidence and accurately label the pilot/confirmatory boundary.
