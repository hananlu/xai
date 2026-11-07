"""Render the fixed post-hoc conference checks; does not select a winning endpoint."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
 (ROOT/'figures').mkdir(exist_ok=True);c=json.loads((ROOT/'results/EXPLAINER_COMPARISON.json').read_text());s=json.loads((ROOT/'results/PATTERN_SUMMARY.json').read_text());run=json.loads((ROOT/'results/PARAMETER_CONTROL.json').read_text())
 q=pd.read_csv(ROOT/'results/control_institution_means.csv');fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained');plt.rcParams.update({'font.size':11})
 for ax,metric,title in zip(axes,['pattern_distance','rank_spearman'],['Signed normalized-pattern change','Absolute-importance rank similarity']):
  for cohort,offset,color in [('source',-.12,'#2365A0'),('target',.12,'#C16B24')]:
   for x,stage in enumerate(['head','head_gru']):
    vals=q[(q.metric==metric)&(q.cohort==cohort)&(q.stage==stage)].value
    ax.scatter(np.full(len(vals),x+offset),vals,color=color,s=14,alpha=.45,label=cohort if x==0 else None)
    if len(vals):ax.plot([x+offset-.07,x+offset+.07],[vals.mean(),vals.mean()],color=color,lw=3)
  ax.set(xticks=[0,1],xticklabels=['Head reset','Head + GRU reset'],title=title,ylabel='Half L1 distance' if metric=='pattern_distance' else 'Spearman correlation',ylim=(-.03,1.03) if metric=='pattern_distance' else (-1.03,1.03));ax.axhline(0,color='gray',lw=.6);ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
 axes[0].legend(loc='upper left',fontsize=9)
 for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/parameter_sensitivity.{ext}',dpi=190,bbox_inches='tight')
 plt.close(fig)
 macro=pd.DataFrame(c['macro']);table=macro.pivot(index='method',columns=['panel','cohort'],values='quality_q').reindex(['shapley','ig','occlusion','recency']);table.to_csv(ROOT/'results/method_table.csv')
 lines=['# Focused conference checks','', 'These additions are post-hoc. Original/new-cohort primary estimands and scientific freezes remain unchanged. No new dataset, model fitting, or new explanation method is claimed.','', '## Common-case absolute ranking alignment','', '| Method | A source | A target | B source | B target |','|---|---:|---:|---:|---:|']
 for method,row in table.iterrows():lines.append('| '+method+' | '+' | '.join('—' if pd.isna(row.get(k,np.nan)) else f'{row[k]:.4f}' for k in [('A','source'),('A','target'),('B','source'),('B','target')])+' |')
 lines+=['','Panel A: all main-budget cases common to Shapley/occlusion/recency. Panel B: original IG subset, all four methods common and IG accepted. Each method must have all three defined training seeds. Within-panel cases are identical; cross-panel populations differ. Q=0 is the exact random-order mean, not a universal explanation-ground-truth reference. Means are descriptive with equal institution weighting after operator/year aggregation.','', 'Counts:','', '```json',json.dumps(c['counts'],indent=2),'```','', '## Learned-layer parameter sensitivity','',f"{run['histories']} fixed histories, three trained seeds, three randomization replicates, two cumulative stages; {run['records']} comparison records. Copied-model max difference {run['identity_max_abs_difference']}. Source normalization and the fixed last-input residual route remain intact.",'', '```json',json.dumps(s,indent=2),'```','', 'Pattern/rank diagnostics are conditional on common comparable cases across both stages; all flat, clipped and undefined outcomes remain recorded. Dots in the plot are institution means, not independent seed/replicate tests. There is no prescribed pass threshold. Sensitivity does not prove causal demand correctness or universal usefulness; operator-normalized Q need not fall when the model and response game both change.']
 (ROOT/'RESULTS.md').write_text('\n'.join(lines)+'\n');(ROOT/'results/REPORT_FACTS.json').write_text(json.dumps(dict(explainer=c,control=s,run=run,post_hoc=True),indent=2));print('Rendered common-case table and conditional parameter-sensitivity plot.')
if __name__=='__main__':main()
