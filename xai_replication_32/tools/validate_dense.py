"""Post-evaluation audit of frozen nested-budget outputs; does not alter the scientific estimator."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import numpy as np,pandas as pd
from data_common import windows
from benchmark_common import Predictor,games,templates,response_game,quality,order

def main():
 checks={};details={};freeze=json.loads((ROOT/'results/PREEVALUATION_FREEZE.json').read_text())
 checks['frozen_100_input_hashes']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items())
 mainplan=pd.read_csv(ROOT/'results/SELECTION_MAIN_FROZEN.csv');denseplan=pd.read_csv(ROOT/'results/SELECTION_DENSE_FROZEN.csv')
 keys=['id','origin'];checks['main_plan_nested']=set(map(tuple,mainplan[keys].values))<=set(map(tuple,denseplan[keys].values))
 checks['frozen_plan_equals_evaluated_main']=set(map(tuple,mainplan[keys].values))==set(map(tuple,pd.read_csv(ROOT/'results/explanation_selection.csv')[keys].values))
 q=pd.concat([pd.read_csv(ROOT/f'results/dense_quality_gru_{s}.csv.gz') for s in [42,123,2026]],ignore_index=True)
 checks['dense_record_count']=len(q)==len(denseplan)*3*2*3*2
 checks['dense_case_plan_exact']=set(map(tuple,q[keys].drop_duplicates().values))==set(map(tuple,denseplan[keys].values))
 base=pd.concat([pd.read_csv(ROOT/f'results/quality_gru_{s}.csv.gz') for s in [42,123,2026]],ignore_index=True).query("arm=='frozen' and reference=='source_calendar' and method in ['shapley','occlusion','recency']")
 ck=['id','origin','seed','horizon','operator','method'];joined=q[q.is_main].merge(base,on=ck,suffixes=('_dense','_main'),validate='one_to_one')
 d=abs(joined.quality_q_dense-joined.quality_q_main);details['main_roundtrip_max_abs_difference']=float(d.max())
 checks['reused_cases_preserved']=len(joined)==len(base) and np.allclose(joined.quality_q_dense,joined.quality_q_main,atol=1e-14,rtol=1e-14,equal_nan=True)
 profile=np.load(ROOT/'models/source_profile.npy');model=Predictor('gru',42);err=0.;nan_agree=True;sample_count=0
 for cohort in ['source','target']:
  for year in [2025,2026]:
   task=denseplan[(denseplan.cohort==cohort)&(denseplan.year==year)&~denseplan.is_main].sort_values(['pair','origin']).iloc[0]
   v=windows(ROOT/f'data/institution_{task.id}.csv.gz');o=int(v['t'].get_loc(pd.Timestamp(task.origin)));x=v['y'][o-167:o+1];t=v['t'][o-167:o+1];r=profile[t.day_of_week*24+t.hour];phi,_,_,_=games(model,x,r)
   for op,tmp in templates(x).items():
    vv,rand,oracle=response_game(model,x,tmp)
    for k,h in enumerate([1,6]):
     _,score,_=quality(vv,order(abs(phi[k]),f'{task.id}:{task.origin}:{h}'),rand,oracle)
     saved=q[(q.id==task.id)&(q.origin==task.origin)&(q.seed==42)&(q.method=='shapley')&(q.horizon==h)&(q.operator==op)].quality_q.iloc[0]
     nan_agree &= bool(np.isnan(score[k])==np.isnan(saved))
     if np.isfinite(saved):err=max(err,float(abs(saved-score[k])))
     sample_count+=1
 checks['added_case_nan_status']=nan_agree;checks['added_case_requeries']=err<1e-10;details.update(added_queries=sample_count,max_added_query_difference=err)
 # Independently reconstruct the primary point: require all three finite seed values before pairing.
 qq=q.query("method=='shapley' and horizon==1")
 a=qq.groupby(['id','cohort','pair','year','origin','operator']).quality_q.agg(['mean','count']).reset_index();a.loc[a['count']!=3,'mean']=np.nan
 p=a.pivot(index=['pair','year','origin','operator'],columns='cohort',values='mean').dropna();p['delta']=p.target-p.source
 cells=p.groupby(['pair','year','operator']).delta.mean().unstack(['year','operator']).dropna();point=float(cells.mean(axis=1).mean())
 results=json.loads((ROOT/'results/SENSITIVITY_RESULTS.json').read_text());stored=next(x for x in results['dense_budget_comparison'] if x['horizon']==1)['dense_original_pair_block']
 checks['dense_primary_point_independent']=abs(point-stored['mean'])<1e-12 and len(cells)==stored['pairs'];details.update(dense_h1_point_independent=point,dense_h1_complete_pairs=len(cells))
 # Preserve undefined denominators stratified by the original 2024 volume bin.
 split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');q=q.merge(split[['id','volume_stratum']],on='id',validate='many_to_one')
 out=q.groupby(['volume_stratum','cohort','seed','horizon','method','operator']).quality_q.agg(records='size',defined='count').reset_index();out['defined_fraction']=out.defined/out.records;out.to_csv(ROOT/'results/dense_denominators_by_stratum.csv',index=False)
 mainq=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'results').glob('quality_*.csv.gz'))],ignore_index=True).merge(split[['id','volume_stratum']],on='id',validate='many_to_one')
 out=mainq.groupby(['volume_stratum','model','cohort','arm','horizon','reference','method','operator']).quality_q.agg(records='size',defined='count').reset_index();out['defined_fraction']=out.defined/out.records;out.to_csv(ROOT/'results/main_denominators_by_stratum.csv',index=False)
 checks={k:bool(v) for k,v in checks.items()};report=dict(status='pass' if all(checks.values()) else 'FAIL',checks=checks,details=details,post_evaluation_audit=True)
 (ROOT/'results/DENSE_VALIDATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert all(checks.values())
if __name__=='__main__':main()
