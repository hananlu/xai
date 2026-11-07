# Paper visual revision — 7 November 2026

The main paper remains eight pages including references, six figures, three tables and 18 citations. This revision changes presentation only.

- Figure 1 uses an editable monochrome TikZ workflow, straight orthogonal connectors, aligned rectangular nodes and short left-aligned labels. Source fitting, validation, target matching, locked deployment, three evaluation questions and separate-cohort inference remain explicit. Additional checks are grouped in a dashed final block, with post-hoc checks identified. Result estimates stay in the Results section.
- All three tables use full-column booktabs layouts, grouped headers, consistent row spacing and notes below the table. Cohort counts and XAI budgets are separated by whitespace; forecast comparators and fitted models are grouped. The common-case panels retain distinct populations and their effective case counts.
- Ragged-bottom setting removes stretched gaps between paragraphs. IEEE font sizes and margins are unchanged. All figures precede the reference page.

Rounded forecast values were checked against the saved metrics; common-case means were checked against saved macro summaries and their rows/counts against the preceding manuscript. The 100 replication inputs and seven additional-check plan/source files retain their frozen hashes. No scientific estimator, notebook, checkpoint or primary result was changed. The optional supplement and editable presentation are unchanged by this paper-only design pass.

Validation: results/VISUAL_REVISION_VALIDATION.json and results/PAPER_PAGE_LIMIT_VALIDATION.json. Prior appearance is recoverable from Git commit 6548d8d903ae5220d720f38378c584fe4245f5c6.
