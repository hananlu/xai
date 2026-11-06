import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data_common import ROOT

def bootstrap(frame,B=2000):
 # frame: one matched source/target contrast per origin/operator after seed averaging.
 f=frame.copy();f['block']=(pd.to_datetime(f.origin,utc=True)-pd.to_datetime(f.year.astype(str)+'-04-08',utc=True)).dt.days//14
 cells=f.groupby(['pair','year','operator']).size();good=[p for p in f.pair.unique() if len(cells.loc[p])==4]
 f=f[f.pair.isin(good)];point=float(f.groupby(['pair','year','operator']).delta.mean().groupby('pair').mean().mean()) if len(f) else None
 if len(good)<4:return dict(mean=point,ci_low=None,ci_high=None,pairs=len(good),bootstrap_valid=0,reason='fewer_than_four_complete_pairs')
 arrays={}
 for p in good:
  arrays[p]={}
  for year in [2025,2026]:
   g=f[(f.pair==p)&(f.year==year)];blocks=sorted(g.block.unique());a=g.groupby(['block','operator']).delta.agg(['sum','count']).unstack('operator').reindex(blocks).fillna(0)
   arrays[p][year]=(a['sum'].reindex(columns=['interpolation','rotation']).to_numpy(),a['count'].reindex(columns=['interpolation','rotation']).to_numpy())
 rng=np.random.default_rng(20261105);vals=[]
 for _ in range(B):
  pair_stats=[];valid=True
  for p in rng.choice(good,len(good),replace=True):
   means=[]
   for year in [2025,2026]:
    sums,counts=arrays[p][year];ix=rng.integers(len(sums),size=len(sums));den=counts[ix].sum(0)
    if (den==0).any():valid=False;break
    means.extend((sums[ix].sum(0)/den).tolist())
   if not valid:break
   pair_stats.append(np.mean(means))
  if valid:vals.append(np.mean(pair_stats))
 return dict(mean=point,ci_low=float(np.quantile(vals,.025)) if len(vals)>=1000 else None,ci_high=float(np.quantile(vals,.975)) if len(vals)>=1000 else None,pairs=len(good),bootstrap_valid=len(vals),reason='nominal_paired_pair_and_14day_block_bootstrap')

def main():
 (ROOT/'figures').mkdir(exist_ok=True);m=pd.read_csv(ROOT/'results/forecast_metrics.csv');q=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'results').glob('quality_*.csv.gz'))],ignore_index=True)
 num=pd.concat([pd.read_csv(p).assign(model=p.stem.split('_')[2],seed=int(p.stem.split('_')[-1])) for p in sorted((ROOT/'results').glob('ig_numerics_*.csv'))],ignore_index=True)
 # Require a complete set of training seeds for the seed-averaged attribution endpoint.
 keys=['model','id','pair','cohort','year','arm','horizon','origin','reference','method','operator','ig_subset']
 a=q.groupby(keys,dropna=False).quality_q.agg(['mean','count']).reset_index();a['expected']=np.where(a.model=='ridge',1,3);a.loc[a['count']!=a.expected,'mean']=np.nan;a=a.rename(columns={'mean':'quality_q'})
 pk=['model','pair','year','arm','horizon','origin','reference','method','operator','ig_subset']
 paired=a.pivot_table(index=pk,columns='cohort',values='quality_q').reset_index();paired=paired.dropna(subset=['source','target']);paired['delta']=paired.target-paired.source;paired.to_csv(ROOT/'results/paired_quality.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 primary=paired[(paired.model=='gru')&(paired.arm=='frozen')&(paired.horizon==1)&(paired.reference=='source_calendar')&(paired.method=='shapley')];claim=bootstrap(primary)
 secondary=[]
 for key,g in paired[(paired.method=='shapley')&(paired.arm=='frozen')].groupby(['model','horizon','reference']):secondary.append(dict(model=key[0],horizon=int(key[1]),reference=key[2])|bootstrap(g))
 pd.DataFrame(secondary).to_csv(ROOT/'results/secondary_quality_contrasts.csv',index=False)
 # Macro scores: mean seeds -> institutions -> years, never treat seeds as independent institutions.
 qmacro=a.groupby(['model','id','cohort','year','arm','horizon','reference','method']).quality_q.mean().reset_index();qmacro.to_csv(ROOT/'results/quality_institution_macro.csv',index=False)
 mseed=m.groupby(['model','id','role','year','arm','horizon'])[['mae_gb','rmse_gb','mase','negative_fraction','zero_fraction']].mean().reset_index();mseed.to_csv(ROOT/'results/forecast_institution_macro.csv',index=False)
 mm=mseed.groupby(['model','role','arm','horizon'])[['mae_gb','rmse_gb','mase','negative_fraction','zero_fraction']].mean().reset_index();mm.to_csv(ROOT/'results/forecast_macro.csv',index=False)
 # Primary selection/exclusion audit retains denominator failures and all failed IG cases.
 exclusions=q.groupby(['model','cohort','year','arm','horizon','reference','method','operator']).agg(records=('quality_q','size'),defined=('quality_q','count'),discriminating=('discriminating','sum'),accepted=('accepted','sum')).reset_index();exclusions.to_csv(ROOT/'results/quality_exclusions.csv',index=False)
 nsummary=num.groupby(['model','reference','horizon']).agg(cases=('accepted','size'),accepted=('accepted','sum'),max_completeness_error_gb=('completeness_error_gb','max')).reset_index();nsummary.to_csv(ROOT/'results/ig_numerical_summary.csv',index=False)
 byop=primary.groupby(['pair','operator']).agg(source_q=('source','mean'),target_q=('target','mean'),delta=('delta','mean'),n=('origin','size')).reset_index();byop.to_csv(ROOT/'results/primary_pair_operator.csv',index=False)
 # Secondary calibration contrasts for Shapley Q, not a new primary endpoint.
 ck=['model','id','pair','cohort','year','horizon','origin','reference','method','operator','ig_subset']
 cal=a[a.method=='shapley'].pivot_table(index=ck,columns='arm',values='quality_q').reset_index();cal=cal.dropna(subset=['frozen','calibrated']);cal['delta']=cal.calibrated-cal.frozen;cal.to_csv(ROOT/'results/calibration_quality_changes.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 # Scientific figures.
 names=['persistence','daily','weekly','ridge','dlinear','gru'];colors=['#94a3b8','#64748b','#475569','#2563eb','#0d9488','#ea580c']
 fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for ax,h in zip(axs,[1,6]):
  f=mseed[(mseed.role=='target')&(mseed.arm=='frozen')&(mseed.horizon==h)].groupby(['model','id']).mase.mean()
  means=[f.loc[k].mean() for k in names];ax.bar(range(6),means,color=colors);ax.set_xticks(range(6),['Last','Daily','Weekly','Ridge','DLinear','GRU'],rotation=25);ax.set_ylabel('Mean institution MASE');ax.set_title(f'Unseen institutions: {h}h endpoint');ax.grid(axis='y',alpha=.2)
 fig.savefig(ROOT/'figures/target_forecast_mase.png',dpi=190);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
 ops=['interpolation','rotation'];markers=['o','s']
 for op,c,mark in zip(ops,['#2563eb','#ea580c'],markers):
  g=byop[byop.operator==op];ax.scatter(g.pair+(0 if op=='interpolation' else .12),g.delta,label=op,color=c,marker=mark,s=45)
 ax.axhline(0,color='black',lw=1);ax.set_xlabel('Matched institution pair');ax.set_ylabel('Target - source ranking score Q');ax.set_title('Primary GRU / 1h / source-calendar Shapley');ax.legend();ax.grid(axis='y',alpha=.2);fig.savefig(ROOT/'figures/primary_pair_contrasts.png',dpi=190);plt.close(fig)
 fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for ax,ref in zip(axs,['source_calendar','history_hour_median']):
  z=a[(a.method=='shapley')&(a.arm=='frozen')&(a.horizon==1)&(a.reference==ref)].groupby(['model','cohort','id']).quality_q.mean().reset_index()
  for j,kind in enumerate(['ridge','dlinear','gru']):
   for cohort,dx,c in [('source',-.16,'#2563eb'),('target',.16,'#ea580c')]:
    vals=z[(z.model==kind)&(z.cohort==cohort)].quality_q.to_numpy();ax.scatter(np.full(len(vals),j+dx),vals,color=c,s=24,alpha=.7,label=cohort if j==0 else None)
  ax.axhline(0,color='gray',lw=.6);ax.set_xticks(range(3),['Ridge','DLinear','GRU']);ax.set_ylabel('Mean Q per institution');ax.set_title(ref.replace('_',' '));ax.grid(axis='y',alpha=.2)
 axs[0].legend();fig.savefig(ROOT/'figures/reference_quality.png',dpi=190);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,4),layout='constrained');labels=[];rates=[]
 for r in nsummary.itertuples():labels.append(f'{r.model}\n{r.reference.split("_")[0]} {r.horizon}h');rates.append(r.accepted/r.cases)
 ax.bar(range(len(rates)),rates,color='#0d9488');ax.set_xticks(range(len(rates)),labels,rotation=35,ha='right',fontsize=8);ax.set_ylim(0,1.05);ax.set_ylabel('IG cases meeting numerical tolerances');ax.grid(axis='y',alpha=.2);fig.savefig(ROOT/'figures/ig_acceptance.png',dpi=190);plt.close(fig)
 claims=dict(primary=claim,primary_definition='GRU frozen, h1, source-calendar Shapley Q, target-minus-source, paired institution/time blocks',quality_records=len(q),seed_averaged_rows=len(a),paired_primary_records=len(primary),ig_cases=len(num),ig_failed=int((~num.accepted).sum()),forecast_metric_rows=len(m),target_institutions=8,matched_pairs=8,protocol='FULL_PROTOCOL.md',all_operators_controlled=True,causal_demand_claim=False)
 (ROOT/'results/NUMERIC_CLAIMS.json').write_text(json.dumps(claims,indent=2));print(json.dumps(claims,indent=2));print(mm[(mm.role=='target')&(mm.arm=='frozen')].to_string(index=False))
if __name__=='__main__':main()
