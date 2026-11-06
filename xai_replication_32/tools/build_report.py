"""Reporting only: render frozen-estimator outputs without choosing an endpoint."""
from pathlib import Path
import json,shutil
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':190})
def read(n):return json.loads((ROOT/'results'/n).read_text())
def save(fig,name):
 for ext in ['pdf','png']:fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight')
 plt.close(fig)
def num(x):return 'not available' if x is None else f'{x:.4f}'
def desc(d):
 return f"{num(d['mean'])}; 95% interval "+(f"[{num(d['ci_low'])}, {num(d['ci_high'])}]" if d.get('ci_low') is not None else 'not reported (fewer than 1,000 valid draws)')+f"; {d['pairs']} pairs; {d.get('bootstrap_valid',0)}/2,000 valid draws"
def texdesc(d):
 if d.get('ci_low') is None:return f"${d['mean']:.4f}$; no interval ({d.get('bootstrap_valid',0)}/2,000 valid draws)"
 return f"${d['mean']:.4f}$, nominal 95\\% interval $[{d['ci_low']:.4f},{d['ci_high']:.4f}]$ ({d.get('bootstrap_valid',0)}/2,000 valid draws)"
def main():
 s=read('SENSITIVITY_RESULTS.json');c=read('NUMERIC_CLAIMS.json');p=s['main_original_pair_block'];dense=s['dense_budget_comparison'];split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');pairs=pd.read_csv(ROOT/'MATCHED_PAIRS.csv')
 # Forest includes every fixed interval family; an unavailable interval is explicitly labeled.
 rows=[('Original 8 targets / original blocks',dict(mean=-.018876455601195535,ci_low=-.08913930523312447,ci_high=.05334453792169871,pairs=7,bootstrap_valid=1853)),('New targets / original blocks',p),('New targets / pair only',s['main_sensitivity']['pair_only']),('New targets / synchronized blocks',s['main_sensitivity']['synchronized_blocks'])]
 fig,ax=plt.subplots(figsize=(10,3.8))
 for y,(label,d) in enumerate(rows):
  ax.scatter(d['mean'],y,color='C0' if y else 'gray',zorder=3)
  if d.get('ci_low') is not None:ax.plot([d['ci_low'],d['ci_high']],[y,y],color='C0' if y else 'gray')
  else:ax.annotate('interval failed',(d['mean'],y),xytext=(8,6),textcoords='offset points',fontsize=9)
  ax.annotate(f"n={d['pairs']}; valid={d['bootstrap_valid']}/2000",(1,y),xycoords=('axes fraction','data'),xytext=(10,0),textcoords='offset points',va='center',fontsize=10)
 ax.set(yticks=range(len(rows)),yticklabels=[x[0] for x in rows],xlabel='Target minus source Q (h1, frozen GRU, calendar Shapley)');ax.axvline(0,color='black',lw=.7,ls=':');ax.invert_yaxis();save(fig,'replication_uncertainty')
 fig,axes=plt.subplots(1,2,figsize=(11,4),sharex=True)
 for ax,item in zip(axes,dense):
  specs=[('16 origins: own panel',item['main_original_pair_block']),('64 origins: own panel',item['dense_original_pair_block']),('16 origins: common pairs',item['common_pair_main']),('64 origins: common pairs',item['common_pair_dense'])]
  for y,(label,d) in enumerate(specs):
   ax.scatter(d['mean'],y,color='C0')
   if d.get('ci_low') is not None:ax.plot([d['ci_low'],d['ci_high']],[y,y],color='C0')
   else:ax.annotate('CI unavailable',(d['mean'],y),xytext=(5,5),textcoords='offset points',fontsize=9)
   ax.annotate(f"n={d['pairs']}",(1,y),xycoords=('axes fraction','data'),xytext=(4,0),textcoords='offset points',fontsize=10)
  ax.set(yticks=range(4),yticklabels=[x[0] for x in specs],title=f"h={item['horizon']}",xlabel='Target minus source Q');ax.axvline(0,color='gray',ls=':');ax.invert_yaxis()
 fig.tight_layout();save(fig,'replication_density')
 den=pd.read_csv(ROOT/'results/main_denominators_by_stratum.csv').query("arm=='frozen' and reference=='source_calendar' and method=='shapley' and horizon==1").groupby(['volume_stratum','model','cohort'])[['records','defined']].sum().reset_index();den['fraction']=den.defined/den.records
 fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
 for ax,cohort in zip(axes,['source','target']):
  for kind,g in den[den.cohort==cohort].groupby('model'):ax.plot(g.volume_stratum+1,g.fraction,'o-',label=kind)
  ax.set(ylim=(0,1.05),xticks=[1,2,3,4],xlabel='2024 volume stratum (low to high)',ylabel='Defined Q fraction',title=cohort.capitalize());ax.grid(alpha=.2)
 axes[1].legend();save(fig,'replication_denominators')
 paired=pd.read_csv(ROOT/'results/paired_quality.csv.gz').query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method=='shapley'");cells=paired.groupby(['pair','year','operator']).delta.mean().unstack(['year','operator']);means=cells.dropna().mean(1)
 fig,ax=plt.subplots(figsize=(10,3.5));ax.bar(means.index.astype(str),means,color='#2563eb');ax.axhline(0,color='black',lw=.7);ax.set(xlabel='Complete matched institution pair',ylabel='Target minus source Q',title='New targets: each pair weighted equally');save(fig,'replication_pair_means')
 f=pd.read_csv(ROOT/'results/forecast_macro.csv').query("role=='target' and arm=='frozen'")
 table=f.pivot(index='model',columns='horizon',values='mase').reindex(['persistence','daily','weekly','ridge','dlinear','gru'])
 # All fixed estimates and availability limits in a readable research note.
 lines=['# Results: 32 new targets within CESNET','', '**This is a within-network replication using the original locked models and reused source anchors.** The old outcome was known before this protocol; new-target scoring followed the local membership/code/data freeze. No external preregistration, model refitting, target tuning or replacement of missing institutions occurred.','', '## Primary result','',desc(p), '', 'Do not interpret a failed/zero-containing interval as equivalence or absence of a transfer effect. The primary remains the original pair/within-pair block procedure; the sensitivity intervals do not replace it.','', '## Prespecified uncertainty sensitivities','', '- Pair only: '+desc(s['main_sensitivity']['pair_only']),'- Synchronized calendar blocks: '+desc(s['main_sensitivity']['synchronized_blocks']),'', '## Nested explanation budget','']
 for item in dense:
  lines+= [f"### Horizon {item['horizon']}",'']
  for k in ['main_original_pair_block','dense_original_pair_block','common_pair_main','common_pair_dense']:lines+=['- '+k+': '+desc(item[k])]
  lines+=['- Dense pair-only: '+desc(item['dense_sensitivity']['pair_only']),'- Dense synchronized blocks: '+desc(item['dense_sensitivity']['synchronized_blocks']),'']
 lines+=['## Accuracy and audit','','Model | h1 MASE | h6 MASE\n--- | ---: | ---:\n'+'\n'.join(f'{kind} | {row[1]:.4f} | {row[6]:.4f}' for kind,row in table.iterrows()),'',f"Main audit: {c['quality_records']:,} operator/seed/arm/reference/horizon records; {c['ig_failed']:,} of {c['ig_cases']:,} IG checks rejected. These are repeated computational records, not independent institutions.",'','Main: 2,016 histories per fit, 63 available pair-years. Dense: 8,064 histories per GRU seed. Pair 1 (source 260, target 8) has no common eligible origins in 2026 and is not replaced. Pair 4 (source 281, target 267) has no complete three-seed paired primary scores. Undefined response denominators are retained; the primary is conditional on the 30 informative complete pairs.','', 'Original eight-target result: -0.0189, nominal interval [-0.0891, 0.0533], seven complete pairs. It is reported separately. Overall there are 80 unique institutions: 32 sources, eight validation institutions, eight old targets and 32 new targets.','', '## Scientific scope','', 'The useful conference contribution is an audited empirical deployment comparison, numerical failure accounting, and an explicit sensitivity analysis of uncertainty and timestamp density. It is not a new Shapley/IG method. New targets improve within-CESNET coverage, while source/model reuse, one ISP, clipped low-volume predictions, missing periods, controlled replacement distributions and limited specialized baselines remain material limitations. Query count alone is not evidence of validity.','', 'See the JSON/CSV outputs for every endpoint and failure count. Figure scripts only read results; scientific source and protocol hashes remain frozen.']
 (ROOT/'RESULTS_BRIEF.md').write_text('\n'.join(lines)+'\n')
 diagnostics=read('FORECAST_DIAGNOSTICS.json')
 lines+=['','## Post-hoc scale diagnostic','',f"After inspecting extreme forecast MASE, we retained all target cells and the original scale/floor. Target 267 has 2024 weekly scale {diagnostics['institution_267_weekly_scale_bytes']:.1f} bytes. Seed-specific MASE reaches {diagnostics['max_single_seed_mase']:.1f}, despite absolute errors of only a few MB. Median MASE and the scale plot are descriptive diagnostics, not replacements for the frozen mean."]
 (ROOT/'RESULTS_BRIEF.md').write_text('\n'.join(lines)+'\n')
 # Standalone section input copied into the main paper; old primary remains untouched.
 text=r'''\section{Prospective New-Target Within-Network Replication}\label{sec:replication}
\subsection{Design and scope}
After inspecting the original eight-target result, we specified an additional cohort before scoring its target outcomes. Of 217 eligible unused institutions, deterministic SHA-256 ordering selected eight per reconstructed 2024 volume stratum, for 32 new targets. One-to-one matching within strata reused all 32 original source anchors using log-transformed 2024 median volume and coefficient of variation. The original source normalization, reference profiles, model checkpoints, clipping and deployment arms were retained without gradient fitting or target tuning. Membership and then code/data/timestamp hashes were frozen locally; this was not external preregistration. Across both studies there are 80 unique institutions, but source anchors, trained models and ISP are shared. Estimates are not pooled as independent network replications.

The main explanation budget retained up to 16 shared origins per pair/year and four for IG, across all original model/reference/arm combinations. There were 63 available pair-years and 2,016 institution-origin histories per fit. Pair 1 (source 260, target 8) had no common eligible 2026 origins and was not replaced. The fixed primary estimand and 2,000-attempt pair/within-pair block procedure were retained. An interval required at least four complete pairs and 1,000 valid draws; we did not increase this attempt budget after inspecting the valid count.

Before scoring, we also specified pair-only cluster intervals conditional on observed periods, and synchronized six-calendar-block-per-year resampling shared across institutions. Both are uncertainty sensitivities, not replacements for primary inference. A nested dense budget retained all main origins and added up to 48 per pair/year, giving 8,064 histories per frozen GRU seed. Dense evaluation used source-calendar Shapley, occlusion and recency at both horizons, without IG or calibration. We compare both their own complete-pair panels and their intersection; changing availability can change the population summarized.

\subsection{New-cohort evidence}
'''
 text+=f"The new-cohort primary contrast was {texdesc(p)}, across {p['pairs']} complete pairs. The pair-only sensitivity gave {texdesc(s['main_sensitivity']['pair_only'])}; synchronized calendar blocks gave {texdesc(s['main_sensitivity']['synchronized_blocks'])}. These procedures condition on different aspects of the observed data; disagreement or interval failure is part of the result, not a basis for choosing the most favorable uncertainty statement.\n\n"
 text+=r'''\begin{figure*}[t]\centering\includegraphics[width=.96\textwidth]{replication_uncertainty.pdf}
\caption{Original and new-target h1 estimates shown separately. Every prespecified uncertainty family is retained; absent bars indicate a failed interval gate, not zero uncertainty. Pair-only intervals condition on observed periods. Shared sources/models/ISP prevent interpreting the two cohorts as independent network replications.}\label{fig:repuncertainty}\end{figure*}
'''
 text+=f"New-target frozen one-hour MASE was {table.loc['ridge',1]:.3f} for Ridge, {table.loc['dlinear',1]:.3f} for DLinear and {table.loc['gru',1]:.3f} for GRU; six-hour values were {table.loc['ridge',6]:.3f}, {table.loc['dlinear',6]:.3f} and {table.loc['gru',6]:.3f}. The main audit generated {c['quality_records']:,} ranking records and rejected {c['ig_failed']:,} of {c['ig_cases']:,} IG numerical cases. These repeated records do not increase the number of institutions. All twelve prespecified model/horizon/reference Shapley contrasts in the new cohort had nominal intervals containing zero; the original h1 history-median zero-excluding secondary pattern did not recur here. Pair 4 (source 281, target 267) has no complete three-seed paired primary scores. Thus the main complete-pair result omits an important low-volume regime and cannot certify its explanation reliability.\n\n"
 text+=r'''\paragraph{Post-hoc forecast-scale diagnostic.} After observing extreme macro MASE, we inspected every institution-year without modifying the metric, floor, membership or model. Target 267 has a 2024 weekly error scale of approximately 751 bytes. For example, frozen GRU seed 2026 at h6 has about 0.004445 GB MAE in 2025, giving MASE about 5,921. Small absolute errors can therefore dominate a mean of relative ratios. The descriptive median institution-year MASE at h1 is 0.761 for Ridge, 0.747 for DLinear and 0.824 for GRU; these medians do not replace the frozen mean MASE.\n\n'''.replace(r'\n','\n')
 text+=r'''\begin{figure*}[t]\centering\includegraphics[width=\textwidth]{replication_forecast_scales.pdf}
\caption{Post-hoc scale diagnostic retaining every target institution-year. Both axes use logarithmic scales. Near-constant low-volume targets can have large relative forecast errors; this plot supplements the original metric rather than capping it or removing difficult institutions.}\label{fig:repscale}\end{figure*}
'''
 for item in dense:
  text+=f"At h{item['horizon']}, the dense-panel contrast was {texdesc(item['dense_original_pair_block'])}. On {item['common_pairs']} common complete pairs, the 16-origin point was ${item['common_pair_main']['mean']:.4f}$ and the 64-origin point was ${item['common_pair_dense']['mean']:.4f}$. "
 text+=f"The main attribution evaluation took {read('ATTRIBUTION_COMPLETE.json')['runtime_seconds']/60:.1f} minutes and the added dense evaluation {read('DENSE_COMPLETE.json')['runtime_seconds']/60:.1f} minutes on the local four-thread CPU; no new training occurred. "
 text+='The comparison preserves the main cases exactly and audits added cases independently; density sensitivity is not a newly chosen primary test.\n\n'
 text+=r'''\begin{figure*}[t]\centering\includegraphics[width=\textwidth]{replication_density.pdf}
\caption{Prespecified nested explanation-budget sensitivity, with original pair/within-pair block intervals when the valid-draw gate passes. Own-panel and common-complete-pair views distinguish additional timestamps from changed institutional availability. Neither panel is selected to replace the main estimate.}\label{fig:repdensity}\end{figure*}
\begin{figure*}[t]\centering\includegraphics[width=.9\textwidth]{replication_denominators.pdf}
\caption{Defined h1 source-calendar Shapley Q fractions by original 2024 volume stratum, aggregating seeds and both operators. Low-volume clipped predictions can yield an uninformative response game. Undefined cases remain in the denominator audit; larger query budgets do not guarantee additional informative institutions.}\label{fig:repdenominators}\end{figure*}

This expansion provides additional deployment institutions and makes the consequences of response denominators, sampling density and block resampling visible. It still does not identify causal demand effects or cross-ISP reliability. In particular, complete-case intervals apply to institutions and observed regimes that support the required operator/year cells. The original result, new main endpoint and fixed sensitivities are reported together without promoting a more favorable analysis.
'''
 (ROOT/'replication_section.tex').write_text(text)
 facts=dict(primary=p,main_sensitivity=s['main_sensitivity'],dense_budget_comparison=dense,ig_cases=c['ig_cases'],ig_failed=c['ig_failed'],forecast_mase=table.reset_index().rename(columns={1:'h1',6:'h6'}).to_dict('records'),forecast_diagnostics=diagnostics,reporting_only=True)
 (ROOT/'results/REPORT_FACTS.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
