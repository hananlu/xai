# Paper source

- `paper.tex`: source matching the delivered five-page PDF. It currently uses an explicit `thebibliography` section so the submitted draft is directly reproducible with two pdflatex passes.
- `references.bib`: all 18 cited works as reusable BibTeX entries, with the same citation keys as paper.tex. Where final volume/pages were not verified, they are not invented.
- `paper.pdf`: anonymous draft; no submission has occurred.

To switch to BibTeX for a venue template, replace the thebibliography block with:

```tex
\bibliographystyle{IEEEtran}
\bibliography{references}
```

Then run pdflatex, bibtex, and pdflatex twice. Venue templates can change page counts. Figures are under `../figures/`. The technical content and primary study remain unchanged by providing this bibliography source.
