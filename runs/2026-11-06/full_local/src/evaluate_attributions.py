import json,time,hashlib
import numpy as np,pandas as pd
from data_common import ROOT,windows,period
from benchmark_common import Predictor,games,templates,response_game,quality,order,integrated_gradients
from evaluate_forecasts import calibration

def main():
 start=time.time();pairs=pd.read_csv(ROOT/'MATCHED_PAIRS.csv');ids=set(pairs.source)|set(pairs.target);cache={int(i):windows(ROOT/f'data/institution_{i}.csv.gz') for i in ids};profile=np.load(ROOT/'models/source_profile.npy')
 tasks=[];selection=[]
 for pair in pairs.itertuples():
  for year in [2025,2026]:
   members={}
   for ident in [pair.source,pair.target]:
    v=cache[ident];q=period(v,f'{year}-04-08',f'{year}-07-01',6);ix=np.where(q)[0];members[ident]={int(v['o'][i]):int(i) for i in ix}
   common=sorted(set(members[pair.source])&set(members[pair.target]));take=np.unique(np.linspace(0,len(common)-1,min(16,len(common)),dtype=int)) if common else np.array([],int);chosen=[common[i] for i in take];ig_ix=set(np.unique(np.linspace(0,len(chosen)-1,min(4,len(chosen)),dtype=int))) if chosen else set()
   for j,o in enumerate(chosen):
    for ident,cohort in [(pair.source,'source'),(pair.target,'target')]:
     tasks.append(dict(pair=int(pair.pair),id=int(ident),cohort=cohort,year=year,o=int(o),window_ix=members[ident][o],ig=j in ig_ix));selection.append(dict(pair=int(pair.pair),id=int(ident),cohort=cohort,year=year,origin=str(cache[ident]['t'][o]),ig=j in ig_ix,common_eligible_origins=len(common)))
 pd.DataFrame(selection).to_csv(ROOT/'results/explanation_selection.csv',index=False)
 specs=[('ridge',0)]+[(k,s) for k in ['dlinear','gru'] for s in [42,123,2026]];all_summary=[]
 for kind,seed in specs:
  model=Predictor(kind,seed);rows=[];allocations=[];numeric=[];offsets={(i,y):calibration(cache[i],y,model)[0] for i in ids for y in [2025,2026]}
  for n,task in enumerate(tasks):
   ident=task['id'];v=cache[ident];o=task['o'];x=v['X'][task['window_ix']];origin=str(v['t'][o]);how=v['t'].day_of_week.to_numpy()*24+v['t'].hour.to_numpy();references={'source_calendar':profile[how[o-167:o+1]],'history_hour_median':np.tile(np.median(x.reshape(7,24),axis=0),7)};key=f'{ident}:{origin}'
   info={k:task[k] for k in ['pair','id','cohort','year']}|dict(model=kind,seed=seed,origin=origin,ig_subset=task['ig'])
   # IG is for the frozen full forecast function only.
   ig_results={name:integrated_gradients(model,x,r) for name,r in references.items()} if task['ig'] else {}
   for arm,bias in [('frozen',np.zeros(2)),('calibrated',offsets[(ident,task['year'])])]:
    responses={}
    for op,r in templates(x).items():
     vv,rr,oracle=response_game(model,x,r,bias);shift=float(np.sqrt(np.mean((np.log1p(r)-np.log1p(x))**2)));responses[op]=(vv,rr,oracle,shift)
    for reference,r in references.items():
     phi,occ,game,eff=games(model,x,r,bias);methods={'shapley':(phi,np.ones(2,bool)),'occlusion':(occ,np.ones(2,bool)),'recency':(np.repeat(np.arange(7)[None,:],2,axis=0),np.ones(2,bool))}
     if arm=='frozen' and task['ig']:
      val,ok,nodes,err,change=ig_results[reference];methods['ig']=(val,ok)
      for k,h in enumerate([1,6]):numeric.append(info|dict(reference=reference,horizon=h,accepted=bool(ok[k]),nodes=int(nodes[k]),completeness_error_gb=float(err[k]),l1_refinement_change_gb=float(change[k])))
     for method,(scores,accepted) in methods.items():
      for k,h in enumerate([1,6]):
       rank=np.arange(6,-1,-1) if method=='recency' else order(abs(scores[k]),f'{key}:{h}');base=info|dict(arm=arm,reference=reference,method=method,horizon=h,accepted=bool(accepted[k]));allocations.append(base|{f'score_{j}':float(scores[k,j]) for j in range(7)}|dict(shapley_efficiency_error_gb=float(eff[k]) if method=='shapley' else np.nan))
       for op,(vv,rr,oracle,shift) in responses.items():
        u,q,gap=quality(vv,rank,rr,oracle);rows.append(base|dict(operator=op,utility_gb=float(u[k]),random_utility_gb=float(rr[k]),oracle_utility_gb=float(oracle[k]),oracle_gap_gb=float(gap[k]),quality_q=float(q[k]) if accepted[k] else np.nan,discriminating=bool(gap[k]>1e-9),template_log_rms_shift=shift))
   if (n+1)%64==0:print(kind,seed,'cases',n+1,'/',len(tasks),'elapsed',round(time.time()-start,1),flush=True)
  stem=f'{kind}_{seed}';pd.DataFrame(rows).to_csv(ROOT/f'results/quality_{stem}.csv.gz',index=False,compression={'method':'gzip','mtime':0});pd.DataFrame(allocations).to_csv(ROOT/f'results/allocations_{stem}.csv.gz',index=False,compression={'method':'gzip','mtime':0});pd.DataFrame(numeric).to_csv(ROOT/f'results/ig_numerics_{stem}.csv',index=False)
  item=dict(model=kind,seed=seed,case_origins=len(tasks),quality_records=len(rows),ig_cases=len(numeric),ig_failed=sum(not r['accepted'] for r in numeric));all_summary.append(item);print('COMPLETED',item,flush=True)
  (ROOT/'results/ATTRIBUTION_PROGRESS.json').write_text(json.dumps(all_summary,indent=2))
 facts=dict(status='complete',runtime_seconds=time.time()-start,models=all_summary,target_outcomes_scored=True,source_sha256=hashlib.sha256(__import__('pathlib').Path(__file__).read_bytes()).hexdigest())
 (ROOT/'results/ATTRIBUTION_COMPLETE.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
