"""Independent post-computation arithmetic and checkpoint audit for conference checks."""
from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent;sys.path.insert(0,str(PROJECT/'src'))
from benchmark_common import Predictor,games
from neural_feasibility import Forecaster
from data_common import windows

def main():
 checks={};detail={};f=json.loads((ROOT/'FREEZE.json').read_text())
 checks['extension_frozen_files']=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in f['files'].items())
 checks['upstream_frozen_files']=all(hashlib.sha256((PROJECT/p).read_bytes()).hexdigest()==h for p,h in f['upstream_files'].items())
 checks['original_quality_inputs']=all(hashlib.sha256((PROJECT/p).read_bytes()).hexdigest()==h for p,h in f['quality_inputs'].items())
 # Rebuild common means using an explicit institution/year/operator loop, independent of summarize().
 macros=pd.read_csv(ROOT/'results/explainer_macro.csv');maximum=0.
 for panel,methods in [('A',['shapley','occlusion','recency']),('B',['shapley','ig','occlusion','recency'])]:
  c=pd.read_csv(ROOT/f'results/common_cases_{panel}.csv.gz');checks[f'panel_{panel}_complete_values']=not c[methods].isna().any().any()
  per={}
  for (ident,cohort),g in c.groupby(['id','cohort']):
   values=[]
   for year,y in g.groupby('year'):
    if set(y.operator)!=set(['interpolation','rotation']):continue
    values.append(np.array([y[y.operator==op][methods].mean().to_numpy() for op in ['interpolation','rotation']]).mean(0))
   if values:per[(ident,cohort)]=np.mean(values,axis=0)
  for cohort in ['source','target']:
   means=np.mean([v for (i,co),v in per.items() if co==cohort],axis=0)
   for method,value in zip(methods,means):maximum=max(maximum,abs(value-macros.query('panel==@panel and cohort==@cohort and method==@method').quality_q.iloc[0]))
 checks['independent_explainer_macro']=maximum<1e-12;detail['max_explainer_macro_difference']=float(maximum)
 q=pd.read_csv(ROOT/'results/parameter_records.csv.gz');plan=pd.read_csv(ROOT/'case_plan.csv');checks['complete_control_grid']=len(q)==len(plan)*3*3*2 and not q.duplicated(['id','year','origin','seed','replicate','stage']).any()
 checks['finite_nonnegative_predictions']=bool(np.isfinite(q.prediction_gb).all() and (q.prediction_gb>=0).all());d=q.pattern_distance.dropna();checks['pattern_distance_bounds']=bool(((d>=-1e-12)&(d<=1+1e-12)).all())
 # Reconstruct normalized-pattern distance directly from saved group vectors.
 base=pd.read_csv(ROOT/'results/trained_allocations.csv.gz');keys=['id','year','origin','seed'];merged=q.merge(base,on=keys,suffixes=('_r','_t'),validate='many_to_one');a=merged[[f'score_{j}_t' for j in range(7)]].to_numpy();b=merged[[f'score_{j}_r' for j in range(7)]].to_numpy();aa=abs(a).sum(1);bb=abs(b).sum(1);mask=(aa>1e-9)&(bb>1e-9);ind=.5*abs(a[mask]/aa[mask,None]-b[mask]/bb[mask,None]).sum(1);detail['max_pattern_distance_difference']=float(abs(ind-merged.loc[mask,'pattern_distance']).max());checks['pattern_distance_recalculation']=detail['max_pattern_distance_difference']<1e-12 and merged.loc[~mask,'pattern_distance'].isna().all()
 # Exact case, three checkpoints: model roundtrip + full-permutation Shapley formula.
 task=plan.sort_values(['pair','year','cohort','origin']).iloc[0];v=windows(PROJECT/f'data/institution_{task.id}.csv.gz');o=int(v['t'].get_loc(pd.Timestamp(task.origin)));x=v['y'][o-167:o+1];t=v['t'][o-167:o+1];profile=np.load(PROJECT/'models/source_profile.npy');r=profile[t.day_of_week*24+t.hour];error=0.;requery=0.
 for stage in ['head','head_gru']:
  checkpoint=torch.load(ROOT/f'models/{stage}_42_701.pt',weights_only=True,map_location='cpu');model=Predictor('gru',42);model.net=Forecaster('gru',checkpoint['mean'],checkpoint['std']).double();model.net.load_state_dict(checkpoint['state']);model.net.eval();phi,_,game,_=games(model,x,r);total=np.zeros(7)
  for perm in itertools.permutations(range(7)):
   m=0
   for j in perm:total[j]+=game[m+(1<<j),0]-game[m,0];m+=1<<j
  error=max(error,float(abs(total/5040-phi[0]).max()));saved=q[(q.id==task.id)&(q.year==task.year)&(q.origin==task.origin)&(q.seed==42)&(q.replicate==701)&(q.stage==stage)].iloc[0];requery=max(requery,float(abs(phi[0]-saved[[f'score_{j}' for j in range(7)]].to_numpy(float)).max()),abs(float(model(x)[0])-saved.prediction_gb))
 checks['randomized_checkpoint_requeries']=requery<1e-10;checks['permutation_shapley_check']=error<1e-9;detail.update(max_checkpoint_requery_difference=requery,max_permutation_difference=error)
 status=json.loads((ROOT/'results/PARAMETER_CONTROL.json').read_text());checks['copied_model_identity']=status['identity_max_abs_difference']==0;checks['same_random_head_across_stages']=status['randomized_heads_identical_across_cumulative_stages'];checks['preserved_source_buffers']=status['source_buffers_identical'];checks['retained_fixed_residual_architecture']=status['fixed_residual_route_retained']
 checks={k:bool(v) for k,v in checks.items()};result=dict(status='pass' if all(checks.values()) else 'FAIL',checks=checks,details=detail,post_hoc=True);(ROOT/'results/VALIDATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert all(checks.values())
if __name__=='__main__':main()
