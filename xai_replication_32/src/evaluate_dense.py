"""Nested 64-origin frozen-GRU sensitivity. Main-budget rows reused, added origins only queried."""
import json,time
import numpy as np,pandas as pd
from data_common import ROOT,windows
from benchmark_common import Predictor,games,templates,response_game,quality,order

def main():
 start=time.perf_counter();plan=pd.read_csv(ROOT/'results/SELECTION_DENSE_FROZEN.csv');extra=plan[~plan.is_main];ids=sorted(plan.id.unique());cache={int(i):windows(ROOT/f'data/institution_{i}.csv.gz') for i in ids};profile=np.load(ROOT/'models/source_profile.npy');summaries=[]
 for seed in [42,123,2026]:
  model=Predictor('gru',seed);base=pd.read_csv(ROOT/f'results/quality_gru_{seed}.csv.gz');base=base[(base.arm=='frozen')&(base.reference=='source_calendar')&(base.method.isin(['shapley','occlusion','recency']))].copy();base['is_main']=True;rows=[]
  for n,task in enumerate(extra.itertuples()):
   v=cache[int(task.id)];o=int(v['t'].get_loc(pd.Timestamp(task.origin)));j=int(np.flatnonzero(v['o']==o)[0]);x=v['X'][j];t=v['t'][o-167:o+1];how=t.day_of_week.to_numpy()*24+t.hour.to_numpy();r=profile[how]
   phi,occ,game,eff=games(model,x,r);responses={op:response_game(model,x,tmp) for op,tmp in templates(x).items()}
   for k,h in enumerate([1,6]):
    for method,scores in [('shapley',phi[k]),('occlusion',occ[k]),('recency',np.arange(7))]:
     rank=np.arange(6,-1,-1) if method=='recency' else order(abs(scores),f'{task.id}:{task.origin}:{h}')
     for op,(vv,rr,oo) in responses.items():
      u,q,gap=quality(vv,rank,rr,oo);rows.append(dict(pair=int(task.pair),id=int(task.id),cohort=task.cohort,year=int(task.year),model='gru',seed=seed,origin=task.origin,ig_subset=False,arm='frozen',reference='source_calendar',method=method,horizon=h,accepted=True,operator=op,utility_gb=float(u[k]),random_utility_gb=float(rr[k]),oracle_utility_gb=float(oo[k]),oracle_gap_gb=float(gap[k]),quality_q=float(q[k]),discriminating=bool(gap[k]>1e-9),is_main=False))
   if (n+1)%256==0:print('Dense GRU',seed,n+1,'/',len(extra),'elapsed',round(time.perf_counter()-start,1),flush=True)
  added=pd.DataFrame(rows);out=pd.concat([base,added],ignore_index=True);out.to_csv(ROOT/f'results/dense_quality_gru_{seed}.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  summaries.append(dict(seed=seed,main_score_rows=len(base),added_score_rows=len(added),all_score_rows=len(out),added_histories=len(extra)));(ROOT/'results/DENSE_PROGRESS.json').write_text(json.dumps(summaries,indent=2));print('Dense complete',summaries[-1],flush=True)
 facts=dict(status='complete',runtime_seconds=time.perf_counter()-start,models=summaries,dense_planned_histories=len(plan),main_histories_reused=int(plan.is_main.sum()),new_target_outcomes_scored=True)
 (ROOT/'results/DENSE_COMPLETE.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
