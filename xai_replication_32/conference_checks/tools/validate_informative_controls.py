"""Additional post-computation audit across fixed volume strata, including nonflat controls."""
from pathlib import Path
import sys,json,itertools
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent;sys.path.insert(0,str(PROJECT/'src'))
from benchmark_common import Predictor,games
from data_common import windows

def main():
 checks={};details={};keys=['id','pair','cohort','year','origin','operator','ig_subset'];seeds=[42,123,2026]
 raw=pd.concat([pd.read_csv(PROJECT/f'results/quality_gru_{s}.csv.gz',usecols=keys+['seed','arm','horizon','reference','method','quality_q']) for s in seeds],ignore_index=True).query("arm=='frozen' and horizon==1 and reference=='source_calendar'")
 wide=raw.pivot(index=keys,columns=['method','seed'],values='quality_q')
 for panel,methods in [('A',['shapley','occlusion','recency']),('B',['shapley','ig','occlusion','recency'])]:
  cols=pd.MultiIndex.from_product([methods,seeds]);valid=np.isfinite(wide.reindex(columns=cols).to_numpy()).all(axis=1)
  if panel=='B':valid &= wide.index.get_level_values('ig_subset').to_numpy()
  expected=set(wide.index[valid].tolist());actual=pd.read_csv(ROOT/f'results/common_cases_{panel}.csv.gz');checks[f'independent_case_mask_{panel}']=expected==set(actual[keys].itertuples(index=False,name=None))
 plan=pd.read_csv(ROOT/'case_plan.csv').merge(pd.read_csv(PROJECT/'MATCHED_PAIRS.csv')[['pair','volume_stratum']],on='pair',validate='many_to_one');selected=plan.sort_values(['pair','year','origin']).groupby(['volume_stratum','cohort'],as_index=False).first();profile=np.load(PROJECT/'models/source_profile.npy');q=pd.read_csv(ROOT/'results/parameter_records.csv.gz');count=0;nonflat=0;permerr=0.;requery=0.;buffer_ok=True;head_ok=True;gru_ok=True
 # Check all saved cumulative checkpoints, independently of in-memory construction flags.
 for seed in seeds:
  trained=Predictor('gru',seed).net.state_dict()
  for rep in [701,1701,2701]:
   h=torch.load(ROOT/f'models/head_{seed}_{rep}.pt',weights_only=True,map_location='cpu')['state'];f=torch.load(ROOT/f'models/head_gru_{seed}_{rep}.pt',weights_only=True,map_location='cpu')['state']
   buffer_ok &= all(torch.equal(trained[k],h[k]) and torch.equal(trained[k],f[k]) for k in ['mean','std'])
   head_ok &= all(torch.equal(h[k],f[k]) for k in ['head.weight','head.bias']) and any(not torch.equal(h[k],trained[k]) for k in ['head.weight','head.bias'])
   gs=[k for k in trained if k.startswith('gru.')];gru_ok &= all(torch.equal(h[k],trained[k]) for k in gs) and any(not torch.equal(f[k],trained[k]) for k in gs)
 for task in selected.itertuples():
  v=windows(PROJECT/f'data/institution_{task.id}.csv.gz');o=int(v['t'].get_loc(pd.Timestamp(task.origin)));x=v['y'][o-167:o+1];t=v['t'][o-167:o+1];r=profile[t.day_of_week*24+t.hour]
  for stage in ['head','head_gru']:
   d=torch.load(ROOT/f'models/{stage}_42_701.pt',weights_only=True,map_location='cpu');model=Predictor('gru',42);model.net.load_state_dict(d['state']);phi,_,game,_=games(model,x,r);total=np.zeros(7)
   for perm in itertools.permutations(range(7)):
    m=0
    for j in perm:total[j]+=game[m+(1<<j),0]-game[m,0];m+=1<<j
   permerr=max(permerr,float(abs(total/5040-phi[0]).max()));count+=1;nonflat+=int(abs(phi[0]).sum()>1e-9)
   saved=q[(q.id==task.id)&(q.year==task.year)&(q.origin==task.origin)&(q.seed==42)&(q.replicate==701)&(q.stage==stage)].iloc[0];requery=max(requery,float(abs(phi[0]-saved[[f'score_{j}' for j in range(7)]].to_numpy(float)).max()),abs(float(model(x)[0])-saved.prediction_gb))
 checks.update(saved_buffers_preserved=bool(buffer_ok),saved_cumulative_heads_identical_and_changed=bool(head_ok),saved_gru_reset_stages_correct=bool(gru_ok),nonflat_permutation_audit_included=nonflat>0,stratified_permutation_checks=permerr<1e-9,stratified_checkpoint_requeries=requery<1e-10)
 details.update(volume_strata=4,cohorts=2,model_case_queries=count,nonflat_model_case_queries=nonflat,max_permutation_difference=permerr,max_requery_difference=requery)
 checks={k:bool(v) for k,v in checks.items()};result=dict(status='pass' if all(checks.values()) else 'FAIL',checks=checks,details=details,post_computation_audit=True,estimator_unchanged=True);(ROOT/'results/INFORMATIVE_VALIDATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert all(checks.values())
if __name__=='__main__':main()
