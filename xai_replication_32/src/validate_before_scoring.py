"""Calibrate arithmetic and old-cohort replay without querying any new-target history."""
import json,numpy as np,pandas as pd
from data_common import ROOT,windows
from benchmark_common import Predictor,games,templates,response_game,quality,order
from analyze_replication import bootstrap
from analyze_sensitivity import sensitivities

def main():
 base=ROOT.parent/'xai_cross_institution';sel=pd.read_csv(base/'results/explanation_selection.csv');case=sel.query("pair==3 and year==2025 and cohort=='target'").sort_values('origin').iloc[0];new=set(pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv').query("role=='target'").id);assert int(case.id) not in new
 v=windows(base/f'data/institution_{int(case.id)}.csv.gz');o=int(v['t'].get_loc(pd.Timestamp(case.origin)));x=v['y'][o-167:o+1];t=v['t'][o-167:o+1];r=np.load(ROOT/'models/source_profile.npy')[t.day_of_week.to_numpy()*24+t.hour.to_numpy()];maximum=0
 for kind,seed in [('ridge',0),('dlinear',42),('gru',42)]:
  m=Predictor(kind,seed);phi,occ,game,err=games(m,x,r);saved=pd.read_csv(base/f'results/quality_{kind}_{seed}.csv.gz')
  for op,tmp in templates(x).items():
   vv,rr,oo=response_game(m,x,tmp)
   for k,h in enumerate([1,6]):
    _,q,_=quality(vv,order(abs(phi[k]),f'{case.id}:{case.origin}:{h}'),rr,oo);a=saved[(saved.id==case.id)&(saved.origin==case.origin)&(saved.horizon==h)&(saved.method=='shapley')&(saved.operator==op)&(saved.arm=='frozen')&(saved.reference=='source_calendar')].iloc[0]
    if np.isfinite(q[k]):maximum=max(maximum,abs(q[k]-a.quality_q))
    else:assert pd.isna(a.quality_q)
 assert maximum<1e-9
 toy=[]
 for p in range(4):
  for y in [2025,2026]:
   for block in range(6):
    for op in ['interpolation','rotation']:toy.append(dict(pair=p,year=y,origin=str(pd.Timestamp(f'{y}-04-08',tz='UTC')+pd.Timedelta(days=14*block)),operator=op,delta=.01*p+.002*block))
 toy=pd.DataFrame(toy);a=bootstrap(toy);s=sensitivities(toy);point=float(toy.groupby(['pair','year','operator']).delta.mean().groupby('pair').mean().mean())
 assert abs(a['mean']-point)<1e-12 and a['bootstrap_valid']==2000
 assert abs(s['pair_only']['mean']-point)<1e-12 and s['pair_only']['bootstrap_valid']==2000
 assert abs(s['synchronized_blocks']['mean']-point)<1e-12 and s['synchronized_blocks']['bootstrap_valid']==2000
 facts=dict(status='passed',new_target_performance_used=False,old_cohort_max_q_difference=maximum,toy_primary_point=point,toy_original_bootstrap_valid=2000,toy_synchronized_valid=2000,pair_only_and_shared_block_definitions_checked=True)
 (ROOT/'results/PRESCORING_VALIDATION.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
