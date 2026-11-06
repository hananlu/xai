"""Reporting only: retain extended diagnostics from the archived expanded manuscript."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'paper/archive_expanded_2026-11-07/paper.tex').read_text()
def part(a,b):return s[s.index(a):s.index(b)].strip()
blocks=[
('Original forecast distribution and calibration',part(r'\subsection{Target forecasting}',r'\subsection{A concrete forecast')),
('Original pair/operator components and leave-one-pair-out diagnostic',part(r'\subsection{Primary attribution transfer estimate}',r'\subsection{Secondary reference sensitivity}')),
('Original secondary reference contrasts',part(r'\subsection{Secondary reference sensitivity}',r'\subsection{Numerical audit')),
('Original numerical and denominator audit',part(r'\subsection{Numerical audit and score availability}',r'\subsection{Common accepted cases')),
('Original common accepted Shapley/IG cases',part(r'\subsection{Common accepted cases: an exploratory comparison}',r'\subsection{Computational scale')),
('Computational workload and independent rerun',part(r'\subsection{Computational scale and full rerun}',r'\input{replication_section.tex}')),
]
head=r'''\documentclass[conference]{IEEEtran}
\usepackage{amsmath,amssymb,booktabs,graphicx,url}
\usepackage[hidelinks]{hyperref}
\graphicspath{{../figures/}}
\renewcommand{\thefigure}{S\arabic{figure}}
\renewcommand{\thetable}{S\Roman{table}}
\title{Supplementary Material: Cross-Institution Reliability of Temporal Attributions in Network Traffic Forecasting}
\author{\IEEEauthorblockN{Anonymous research draft}}
\begin{document}\maketitle
\begin{abstract}
This optional technical companion retains coverage/training plots, original forecasting/calibration details, operator components, secondary contrasts, numerical audits, common accepted cases and reproduction workload omitted from the concise conference manuscript. It reports the same executed experiments. No endpoint, membership, tolerance, model or scientific freeze changes. The main paper is self-contained and includes both primary cohort outcomes, new-cohort sensitivities and limitations.
\end{abstract}
\section{Coverage, chronology and cohort provenance}
The original selected hourly files contain 1,147,296 institution-hour grid slots and 1,116,776 finite observed byte-volume values across all periods, not all training observations. Complete-history/period restrictions yield 227,478 overlapping source-training windows. The main paper's effective-unit table distinguishes these rows from institution-level inference. In 2026, original target cells contain 50 or 129 eligible origins, versus 206 or 307 in 2025; target 192 has none in 2026. Figure~\ref{fig:coverage} retains the complete original availability and validation traces.

\begin{figure*}[t]\centering\includegraphics[width=\textwidth]{paper_coverage_learning.pdf}
\caption{Original availability and every neural seed/learning-rate validation trace. An absent eligible cell is not zero traffic. Hyperparameter selection uses validation institutions; repeated and overlapping histories do not create independent institutional replications.}\label{fig:coverage}
\end{figure*}

The new cohort selects eight institutions per original 2024 volume stratum using SHA-256 of \texttt{xai-replication-32-20261106-v1:\{id\}}. Its 217-candidate unused pool excludes all original-study and earlier development institutions. Hungarian matching uses log1p median GB and log1p(std/median), scaled by source descriptor standard deviations within stratum (constant dimension scale one). Matching distances, unavailable cells and undefined scores are retained without replacements.

Main timestamp plans have 2,016 source/target histories per fit over 63 new pair-years; the nested dense plan has 8,064 histories per GRU seed. Dense evaluation adds 6,048 histories per seed and reuses 72,576 main operator/seed records across three seeds exactly. Independent added-case queries agree with stored quality scores. The original bootstrap uses random seed 20261105; new pair-only and synchronized-calendar sensitivities use 20261106, all with 2,000 attempted draws. Every endpoint, including both horizons' dense uncertainty families, is preserved in \texttt{SENSITIVITY\_RESULTS.json} in the new-cohort artifact.

The local freeze followed the original outcome but preceded new-target scoring. It is not external preregistration. Source models/anchors and ISP overlap; original and new contrasts must remain separate. Historical manifests retain their unscored-at-freeze fields; completion records describe execution. Dataset credit: Josef Koumar, Karel Hynek, Kamil Je\v{r}\'abek and Pavel \v{S}i\v{s}ka, CESNET-TimeSeries26 (2026), \url{https://doi.org/10.5281/zenodo.21945629}, CC BY 4.0. Official observed values remain unchanged; selected files add native-grid coverage/artifact fields and compression.
'''
# Replace subsection headings with supplement section headings; internal labels remain valid.
body=''
for title,text in blocks:
 text=text[text.index('\n')+1:]
 body+='\n\\section{'+title+'}\n'+text+'\n'
end=r'''
\end{document}
'''
(ROOT/'paper/supplementary.tex').write_text(head+body+end)
