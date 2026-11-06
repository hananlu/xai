"""Prespecified extra intervals and nested-budget comparison; never chooses a winning endpoint."""
import json
import numpy as np,pandas as pd
from data_common import ROOT
from analyze_replication import bootstrap

def paired_scores(q):
 keys=['model','id','pair','cohort','year','arm','horizon','origin','reference','method','operator','ig_subset']
 a=q.groupby(keys,dropna=False).quality_q.agg(['mean','count']).reset_index();a['expected']=np.where(a.model=='ridge',1,3);a.loc[a['count']!=a.expected,'mean']=np.nan
 pk=['model','pair','year','arm','horizon','origin','reference','method','operator','ig_subset'];p=a.pivot_table(index=pk,columns='cohort',values='mean').reset_index().dropna(subset=['source','target']);p['delta']=p.target-p.source;return p

def complete(frame):
 cells=frame.groupby(['pair','year','operator']).delta.mean().unstack(['year','operator']);good=cells.dropna().index.tolist();return frame[frame['pair'].isin(good)].copy(),cells.loc[good].mean(1)

def sensitivities(frame,B=2000):
 f,pairmeans=complete(frame);good=pairmeans.index.to_numpy();point=float(pairmeans.mean()) if len(good) else None
 if len(good)<4:return dict(pair_only=dict(mean=point,ci_low=None,ci_high=None,pairs=len(good),reason='fewer_than_four_pairs'),synchronized_blocks=dict(mean=point,ci_low=None,ci_high=None,pairs=len(good),bootstrap_valid=0,reason='fewer_than_four_pairs'))
 rng=np.random.default_rng(20261106);means=pairmeans.to_numpy();vals=means[rng.integers(len(means),size=(B,len(means)))].mean(1)
 paironly=dict(mean=point,ci_low=float(np.quantile(vals,.025)),ci_high=float(np.quantile(vals,.975)),pairs=len(good),bootstrap_valid=B,reason='pair_cluster_only_conditional_on_observed_periods')
 f['block']=(pd.to_datetime(f.origin,utc=True)-pd.to_datetime(f.year.astype(str)+'-04-08',utc=True)).dt.days//14;arrays={}
 for p in good:
  arrays[int(p)]={}
  for year in [2025,2026]:
   a=f[(f['pair']==p)&(f.year==year)].groupby(['block','operator']).delta.agg(['sum','count']).unstack('operator').reindex(range(6)).fillna(0)
   arrays[int(p)][year]=(a['sum'].reindex(columns=['interpolation','rotation']).fillna(0).to_numpy(),a['count'].reindex(columns=['interpolation','rotation']).fillna(0).to_numpy())
 rng=np.random.default_rng(20261106);values=[]
 for _ in range(B):
  chosen=rng.choice(good,len(good),replace=True);blocks={y:rng.integers(6,size=6) for y in [2025,2026]};stats=[];valid=True
  for p in chosen:
   v=[]
   for year in [2025,2026]:
    sums,counts=arrays[int(p)][year];ix=blocks[year];den=counts[ix].sum(0)
    if (den==0).any():valid=False;break
    v.extend((sums[ix].sum(0)/den).tolist())
   if not valid:break
   stats.append(np.mean(v))
  if valid:values.append(np.mean(stats))
 sync=dict(mean=point,ci_low=float(np.quantile(values,.025)) if len(values)>=1000 else None,ci_high=float(np.quantile(values,.975)) if len(values)>=1000 else None,pairs=len(good),bootstrap_valid=len(values),bootstrap_attempted=B,reason='synchronized_six_calendar_blocks_per_year')
 return dict(pair_only=paironly,synchronized_blocks=sync)

def main():
 p=pd.read_csv(ROOT/'results/paired_quality.csv.gz');main=p.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method=='shapley'")
 results=dict(main_original_pair_block=bootstrap(main),main_sensitivity=sensitivities(main));q=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'results').glob('dense_quality_gru_*.csv.gz'))],ignore_index=True);dense=paired_scores(q);dense.to_csv(ROOT/'results/dense_paired_quality.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 summaries=[]
 for h in [1,6]:
  d=dense[(dense.horizon==h)&(dense.method=='shapley')];m=p.query("model=='gru' and arm=='frozen' and horizon==@h and reference=='source_calendar' and method=='shapley'")
  dd,dm=complete(d);mm,mp=complete(m);intersection=sorted(set(dm.index)&set(mp.index));same_main=m[m['pair'].isin(intersection)];same_dense=d[d['pair'].isin(intersection)]
  item=dict(horizon=h,main_pairs=len(mp),dense_pairs=len(dm),common_pairs=len(intersection),main_original_pair_block=bootstrap(m),dense_original_pair_block=bootstrap(d),dense_sensitivity=sensitivities(d),common_pair_main=bootstrap(same_main),common_pair_dense=bootstrap(same_dense));summaries.append(item)
 results['dense_budget_comparison']=summaries
 # Identical origin cases must give identical results because main rows were reused.
 compare_keys=['id','seed','year','origin','horizon','operator','method'];base=pd.concat([pd.read_csv(ROOT/f'results/quality_gru_{s}.csv.gz') for s in [42,123,2026]],ignore_index=True).query("arm=='frozen' and reference=='source_calendar' and method in ['shapley','occlusion','recency']")
 reused=q[q.is_main].merge(base,on=compare_keys,suffixes=('_dense','_main'),validate='one_to_one');assert len(reused)==len(base) and np.allclose(reused.quality_q_dense,reused.quality_q_main,equal_nan=True,rtol=0,atol=0)
 results['dense_main_intersection_exact']=True;results['reused_operator_seed_records']=len(reused)
 # Transparent supplementary forecast weighting and annual breakdown.
 f=pd.read_csv(ROOT/'results/forecast_institution_macro.csv');metrics=['mae_gb','rmse_gb','mase'];equalid=f.groupby(['model','id','role','arm','horizon'])[metrics].mean().reset_index().groupby(['model','role','arm','horizon'])[metrics].mean().reset_index();equalid.to_csv(ROOT/'results/forecast_equal_institution_macro.csv',index=False)
 f.groupby(['model','role','year','arm','horizon'])[metrics].mean().reset_index().to_csv(ROOT/'results/forecast_per_year_macro.csv',index=False)
 (ROOT/'results/SENSITIVITY_RESULTS.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
if __name__=='__main__':main()
