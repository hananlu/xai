"""Prospectively fixed computation for a post-hoc cascading learned-layer control."""
from pathlib import Path
import sys,json,copy,time,hashlib
import numpy as np,pandas as pd,torch
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent;sys.path.insert(0,str(PROJECT/'src'))
from data_common import windows
from benchmark_common import Predictor,games
EPS=1e-9

def pattern_metrics(a,b):
 la=float(abs(a).sum());lb=float(abs(b).sum());defined=la>EPS and lb>EPS
 distance=float(.5*abs(a/la-b/lb).sum()) if defined else np.nan
 rho=float(spearmanr(abs(a),abs(b)).statistic) if defined and np.ptp(abs(a))>0 and np.ptp(abs(b))>0 else np.nan
 return distance,rho,la,lb

def randomize(base,seed,replicate):
 hseed=seed*10000+replicate
 head=copy.deepcopy(base)
 with torch.random.fork_rng():torch.manual_seed(hseed);head.net.head.reset_parameters()
 full=copy.deepcopy(head)
 with torch.random.fork_rng():torch.manual_seed(hseed+100000000);full.net.gru.reset_parameters()
 return head,full

def main():
 start=time.perf_counter();plan=pd.read_csv(ROOT/'case_plan.csv');profile=np.load(PROJECT/'models/source_profile.npy');histories={}
 for ident,tasks in plan.groupby('id'):
  v=windows(PROJECT/f'data/institution_{ident}.csv.gz')
  for task in tasks.itertuples():
   o=int(v['t'].get_loc(pd.Timestamp(task.origin)));x=v['y'][o-167:o+1];t=v['t'][o-167:o+1];r=profile[t.day_of_week*24+t.hour];histories[(int(ident),task.origin)]=(x,r)
 rows=[];base_rows=[];identity_max=0.;head_equal=True;buffers_equal=True
 for seed in [42,123,2026]:
  base=Predictor('gru',seed);base_phi={}
  for task in plan.itertuples():
   key=(int(task.id),task.origin);x,r=histories[key];phi,_,_,eff=games(base,x,r);base_phi[key]=phi[0];clone=copy.deepcopy(base);cp,_,_,_=games(clone,x,r);identity_max=max(identity_max,float(abs(cp-phi).max()),float(abs(clone(x)-base(x)).max()))
   base_rows.append(dict(id=int(task.id),pair=int(task.pair),cohort=task.cohort,year=int(task.year),origin=task.origin,seed=seed,prediction_gb=float(base(x)[0]),rawlog=float(base(x,rawlog=True)[0]),l1_gb=float(abs(phi[0]).sum()),efficiency_error_gb=float(eff[0]),**{f'score_{j}':float(phi[0,j]) for j in range(7)}))
  for replicate in [701,1701,2701]:
   head,full=randomize(base,seed,replicate)
   head_equal &= all(torch.equal(a,b) for a,b in zip(head.net.head.state_dict().values(),full.net.head.state_dict().values()))
   for name in ['mean','std']:buffers_equal &= torch.equal(getattr(base.net,name),getattr(head.net,name)) and torch.equal(getattr(base.net,name),getattr(full.net,name))
   for stage,model in [('head',head),('head_gru',full)]:
    checkpoint=dict(kind='gru',state=model.net.state_dict(),mean=float(model.net.mean),std=float(model.net.std),trained_seed=seed,replicate=replicate,stage=stage,head_rng_seed=seed*10000+replicate,gru_rng_seed=seed*10000+replicate+100000000 if stage=='head_gru' else None,fixed_residual_route_retained=True)
    torch.save(checkpoint,ROOT/f'models/{stage}_{seed}_{replicate}.pt')
    for task in plan.itertuples():
     key=(int(task.id),task.origin);x,r=histories[key];phi,_,_,eff=games(model,x,r);p=model(x)[0];distance,rho,la,lb=pattern_metrics(base_phi[key],phi[0]);rows.append(dict(id=int(task.id),pair=int(task.pair),cohort=task.cohort,year=int(task.year),origin=task.origin,seed=seed,replicate=replicate,stage=stage,prediction_gb=float(p),prediction_change_gb=float(p-base(x)[0]),rawlog=float(model(x,rawlog=True)[0]),trained_l1_gb=la,randomized_l1_gb=lb,pattern_distance=distance,rank_spearman=rho,efficiency_error_gb=float(eff[0]),**{f'score_{j}':float(phi[0,j]) for j in range(7)}))
   print('Completed trained seed',seed,'replicate',replicate,'elapsed',round(time.perf_counter()-start,1),flush=True)
 pd.DataFrame(rows).to_csv(ROOT/'results/parameter_records.csv.gz',index=False,compression={'method':'gzip','mtime':0});pd.DataFrame(base_rows).to_csv(ROOT/'results/trained_allocations.csv.gz',index=False,compression={'method':'gzip','mtime':0})
 result=dict(status='complete',runtime_seconds=time.perf_counter()-start,histories=len(plan),trained_seeds=[42,123,2026],replicates=[701,1701,2701],stages=['head','head_gru'],records=len(rows),identity_max_abs_difference=identity_max,randomized_heads_identical_across_cumulative_stages=bool(head_equal),source_buffers_identical=bool(buffers_equal),fixed_residual_route_retained=True,positive_sensitivity_threshold_defined=False,post_hoc=True)
 assert identity_max==0 and head_equal and buffers_equal
 (ROOT/'results/PARAMETER_CONTROL.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
