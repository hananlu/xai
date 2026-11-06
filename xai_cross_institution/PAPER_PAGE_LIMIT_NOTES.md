# Conference page-limit revision

User limit: maximum 7-8 pages. The main IEEE conference manuscript is now **7 pages including all 18 cited references**, with six figures and two tables. Standard document fonts and margins are unchanged. The manuscript retains the gap/contribution, complete overall pipeline, both target cohorts, source-only training setup, attribution/response equations, primary estimates, density/uncertainty sensitivities, low-volume forecast failure, undefined-score exclusions and limitations.

Optional supplementary material is a **separate four-page PDF** with six additional figures and two tables: original coverage/training traces, forecast distribution/calibration, operator/leave-one-pair-out components, secondary reference forest, numerical breakdown and common accepted cases. It is not appended to the seven-page manuscript. Include it in a submission only when the selected venue permits supplementary files. The main manuscript is self-contained.

The full prior 12-page draft and its editable source are preserved under paper/archive_expanded_2026-11-07. The earlier PAPER_REPLICATION_REVISION_VALIDATION record identifies that expanded version; PAPER_PAGE_LIMIT_VALIDATION identifies the current seven-page main paper and four-page supplement.

No experiment, model, metric, primary endpoint or scientific freeze changes. The forecast table's rounded values were checked against saved outputs; all 100 new-cohort frozen input hashes remain unchanged. Every final PDF page was rendered and visually inspected, with no unresolved references or overfull boxes.

Build main from paper/: pdflatex paper; bibtex paper; pdflatex paper; pdflatex paper. Build supplementary: pdflatex supplementary twice. The supplementary source generator tools/build_supplementary.py reads the archived expanded source; tools/validate_paper_page_limit.py enforces the eight-page ceiling and verifies retained results.
