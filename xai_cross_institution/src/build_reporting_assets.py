from pathlib import Path
import json,pandas as pd,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data_common import ROOT
r=ROOT;p=pd.read_csv(r/'results/paired_quality.csv.gz');p=p[(p.model=='gru')&(p.arm=='frozen')&(p.horizon==1)&(p.reference=='source_calendar')&(p.method=='shapley')]
c=p.groupby(['pair','year','operator'])[['source','target','delta']].mean();good=c.delta.unstack(['year','operator']).dropna().index;c=c.loc[good].groupby(['pair','operator']).mean();c.to_csv(r/'results/primary_complete_pair_cells.csv');overall=c.groupby('pair').mean();print('primary source target delta',overall.mean().to_dict());print(c.to_string())
fig,ax=plt.subplots(figsize=(6.7,3.2),layout='constrained')
for op,dx,color,marker in [('interpolation',-.08,'#2365A0','o'),('rotation',.08,'#C16B24','s')]:
 g=c.xs(op,level='operator');ax.scatter(g.index+dx,g.delta,color=color,marker=marker,label=op,s=32)
ax.axhline(0,c='gray',lw=.8);ax.set_xticks(good);ax.set_xlabel('Complete matched pair (equal-year mean)');ax.set_ylabel('Target − source Q');ax.legend(frameon=False);ax.grid(axis='y',alpha=.15);fig.savefig(r/'figures/primary_complete_pairs.pdf');fig.savefig(r/'figures/primary_complete_pairs.png',dpi=180)
f=pd.read_csv(r/'results/forecast_institution_macro.csv');f=f[f.role=='target'];f.groupby(['model','arm','horizon'])[['mae_gb','mase']].mean().to_csv(r/'results/target_forecast_table.csv')
q=pd.concat([pd.read_csv(p) for p in (r/'results').glob('quality_*.csv.gz')]);print('undefined',q.groupby(['method']).agg(records=('quality_q','size'),defined=('quality_q','count'),discriminating=('discriminating','sum')).to_string());print('numeric eff',pd.concat([pd.read_csv(p,usecols=['method','shapley_efficiency_error_gb']) for p in (r/'results').glob('allocations_*.csv.gz')]).shapley_efficiency_error_gb.max())
print('Forecast arms',f.groupby(['model','arm','horizon']).mase.mean().to_string());print('validation',json.loads((r/'results/FINAL_VALIDATION.json').read_text())['checks'])
s=pd.read_csv(r/'results/explanation_selection.csv');av=[]
for ident in pd.read_csv(r/'INSTITUTION_SPLIT.csv').query("role=='target'").id:
 d=pd.read_csv(r/f'data/institution_{ident}.csv.gz');t=pd.to_datetime(d.time,utc=True)
 for y in [2025,2026]:
  a=d[(t>=f'{y}-04-08')&(t<f'{y}-07-01')];av.append(dict(id=int(ident),year=y,total_hours=len(a),complete_hours=int(a.complete_hour.sum()),observed_values=int(a.n_bytes.notna().sum())))
pd.DataFrame(av).to_csv(r/'results/target_availability.csv',index=False)
