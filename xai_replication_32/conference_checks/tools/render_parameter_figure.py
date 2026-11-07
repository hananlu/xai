"""Reporting-only layout revision after frozen computation; no numerical estimator changes."""
from pathlib import Path
import pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main():
 q=pd.read_csv(ROOT/'results/control_institution_means.csv');plt.rcParams.update({'font.size':12});fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
 for ax,metric,title in zip(axes,['pattern_distance','rank_spearman'],['Signed normalized-pattern change','Absolute-importance rank similarity']):
  for cohort,offset,color in [('source',-.12,'#2365A0'),('target',.12,'#C16B24')]:
   for x,stage in enumerate(['head','head_gru']):
    vals=q[(q.metric==metric)&(q.cohort==cohort)&(q.stage==stage)].value
    ax.scatter(np.full(len(vals),x+offset),vals,color=color,s=14,alpha=.5,label=cohort if x==0 else None)
    if len(vals):ax.plot([x+offset-.07,x+offset+.07],[vals.mean(),vals.mean()],color=color,lw=3)
  ax.set(xticks=[0,1],xticklabels=['Head reset','Head + GRU reset'],title=title,ylabel='Half L1 distance' if metric=='pattern_distance' else 'Spearman correlation',ylim=(-.03,1.03) if metric=='pattern_distance' else (-1.03,1.03));ax.axhline(0,color='gray',lw=.6);ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
 handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,-.14),ncols=2,frameon=False,fontsize=10)
 for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/parameter_sensitivity.{ext}',dpi=190,bbox_inches='tight')
 plt.close(fig)
if __name__=='__main__':main()
