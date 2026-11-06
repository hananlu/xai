# Paper source

- `paper.tex`: expanded empirical manuscript, revised 6 November 2026. It uses IEEEtran and the reusable BibTeX database below.
- `references.bib`: all 18 cited works, using the manuscript's citation keys. Unverified final volume/page details are not invented.
- `pipeline_overall.tex`: editable TikZ source for the complete pipeline, included by the manuscript.
- `paper.pdf`: rendered anonymous working draft; target conference, authors and final page limit remain to be set.
- `archive_2026-11-05/`: earlier five-page PDF/TeX retained for comparison. Its explicit bibliography matches that archived draft.

From this paper directory run:

```sh
pdflatex paper.tex
bibtex paper
pdflatex paper.tex
pdflatex paper.tex
```

Dependencies: IEEEtran, TikZ, placeins, and standard AMS/graphics/hyperref packages. Scientific vector figures are under `../figures/`; regenerate the revised assets with `python src/build_paper_revision.py` from the project root. Exact reporting numbers and source timings are in `results/PAPER_REVISION_FACTS.json` and `results/FULL_RUN_TIMINGS.json`.

The revision clarifies sampling, operator semantics, numerical exclusions and the measured full rerun. New leave-one-pair-out/common-case visualizations are descriptive and post-hoc; the frozen primary experiment is unchanged. See `../PAPER_REVISION_NOTES.md`. No submission has occurred.
