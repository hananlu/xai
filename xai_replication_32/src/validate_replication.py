"""Post-evaluation independent arithmetic and integrity audit; never fits a model."""
import json,hashlib,itertools
import numpy as np,pandas as pd
from data_common import ROOT,windows,period
from benchmark_common import Predictor,games,templates,response_game,quality,order

def main():
 checks={};details={}
 for name in ['PREEVALUATION_FREEZE']:
  d=json.loads((ROOT/f'results/{name}.json').read_text());checks[name]=all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in d['files'].items())
 d=json.loads((ROOT/'data/MANIFEST.json').read_text());checks['64_data_hashes']=len(d['files'])==64 and all(hashlib.sha256((ROOT/'data'/r['file']).read_bytes()).hexdigest()==r['sha256'] for r in d['files'])
 d=json.loads((ROOT/'results/LOCKED_MODEL_REFERENCE.json').read_text());checks['model_hashes']=all(hashlib.sha256((ROOT/'models'/r['file']).read_bytes()).hexdigest()==r['sha256'] for r in d['models'])
 split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');checks['disjoint_membership']=split.id.is_unique and split.groupby('role').size().to_dict()=={'source':32,'target':32}
 metrics=pd.read_csv(ROOT/'results/forecast_metrics.csv');offsets=pd.read_csv(ROOT/'results/calibration_offsets.csv');cache={};max_metric=0.;max_pred=0.;prediction_rows=0
 for p in sorted((ROOT/'predictions').glob('*.csv.gz')):
  z=pd.read_csv(p);prediction_rows+=len(z);kind=z.model.iloc[0];seed=int(z.seed.iloc[0]);model=Predictor(kind,seed) if kind in ['ridge','gru','dlinear'] else None
  for key,g in z.groupby(['model','seed','id','role','year','arm','horizon']):
   sel=np.ones(len(metrics),bool)
   for col,val in zip(['model','seed','id','role','year','arm','horizon'],key):sel&=metrics[col]==val
   m=metrics.loc[sel].iloc[0];err=g.prediction_gb-g.target_gb
   max_metric=max(max_metric,abs(abs(err).mean()-m.mae_gb),abs(np.sqrt((err**2).mean())-m.rmse_gb),abs(abs(err).mean()/m.mase_denominator_gb-m.mase))
  # Re-query one origin per institution/year/arm/horizon (all fits, cohorts).
  for key,g in z.groupby(['id','year','arm','horizon']):
   ident,year,arm,h=key;r=g.iloc[len(g)//2]
   if ident not in cache:cache[ident]=windows(ROOT/f'data/institution_{ident}.csv.gz')
   v=cache[ident];o=int(v['t'].get_loc(pd.Timestamp(r.origin)));x=v['y'][o-167:o+1];k=[1,6].index(h)
   if model is not None:raw=model(x,rawlog=True)[k]
   else:raw=np.log1p(v['y'][o if kind=='persistence' else o+h-(24 if kind=='daily' else 168)])
   if arm=='calibrated':raw+=offsets[(offsets.model==kind)&(offsets.seed==seed)&(offsets.id==ident)&(offsets.year==year)&(offsets.horizon==h)].bias_log.iloc[0]
   max_pred=max(max_pred,abs(np.expm1(max(raw,0))-r.prediction_gb),abs(v['y'][o+h]-r.target_gb))
 checks['forecast_metric_recalculation']=max_metric<1e-10;checks['checkpoint_prediction_and_truth_requeries']=max_pred<1e-9
 details.update(prediction_rows=prediction_rows,max_metric_difference=max_metric,max_prediction_difference=max_pred)
 # Independently average marginal contributions over all 7! permutations.
 max_shapley=0.;max_quality=0.
 sel=pd.read_csv(ROOT/'results/explanation_selection.csv');profile=np.load(ROOT/'models/source_profile.npy')
 for kind,seed in [('ridge',0),('dlinear',42),('gru',42)]:
  model=Predictor(kind,seed);q=pd.read_csv(ROOT/f'results/quality_{kind}_{seed}.csv.gz')
  for cohort in ['source','target']:
   task=sel[sel.cohort==cohort].iloc[0];v=cache.setdefault(int(task.id),windows(ROOT/f'data/institution_{task.id}.csv.gz'));o=int(v['t'].get_loc(pd.Timestamp(task.origin)));x=v['y'][o-167:o+1];how=v['t'][o-167:o+1].day_of_week*24+v['t'][o-167:o+1].hour;r=profile[how];phi,_,game,_=games(model,x,r)
   accum=np.zeros_like(phi)
   for perm in itertools.permutations(range(7)):
    mask=0
    for j in perm:accum[:,j]+=game[mask+(1<<j)]-game[mask];mask+=1<<j
   max_shapley=max(max_shapley,float(abs(accum/5040-phi).max()))
   for op,t in templates(x).items():
    vv,rand,oracle=response_game(model,x,t)
    for k,h in enumerate([1,6]):
     rank=order(abs(phi[k]),f'{task.id}:{task.origin}:{h}');u,score,gap=quality(vv,rank,rand,oracle)
     saved=q[(q.id==task.id)&(q.origin==task.origin)&(q.arm=='frozen')&(q.reference=='source_calendar')&(q.method=='shapley')&(q.operator==op)&(q.horizon==h)].iloc[0]
     if np.isfinite(score[k]):max_quality=max(max_quality,abs(score[k]-saved.quality_q))
 checks['permutation_shapley_oracle']=max_shapley<1e-9;checks['ranking_quality_requeries']=max_quality<1e-9
 details.update(max_shapley_difference=max_shapley,max_quality_difference=max_quality)
 paired=pd.read_csv(ROOT/'results/paired_quality.csv.gz');p=paired[(paired.model=='gru')&(paired.arm=='frozen')&(paired.horizon==1)&(paired.reference=='source_calendar')&(paired.method=='shapley')];cells=p.groupby(['pair','year','operator']).delta.mean().unstack(['year','operator']).dropna();claim=json.loads((ROOT/'results/NUMERIC_CLAIMS.json').read_text());checks['primary_point_independent']=abs(cells.mean(axis=1).mean()-claim['primary']['mean'])<1e-12 and len(cells)==claim['primary']['pairs']
 allq=pd.concat([pd.read_csv(p,usecols=['method','accepted','quality_q']) for p in (ROOT/'results').glob('quality_*.csv.gz')]);checks['failed_ig_never_scored']=allq.loc[(allq.method=='ig')&~allq.accepted,'quality_q'].isna().all()
 details['selection_by_pair_year']=sel.groupby(['pair','year']).agg(selected=('origin','size'),common_eligible=('common_eligible_origins','first')).reset_index().to_dict('records')
 details['missing_pair_years']=pd.read_csv(ROOT/'results/AVAILABILITY.csv').query('common_eligible==0').to_dict('records')
 details['forecast_target_institution_years']=int(metrics[(metrics.model=='ridge')&(metrics.arm=='frozen')&(metrics.horizon==1)&(metrics.role=='target')].shape[0])
 checks={k:bool(v) for k,v in checks.items()}
 result=dict(status='pass' if all(checks.values()) else 'FAIL',checks=checks,details=details,target_outcomes_scored=True,post_evaluation_audit=True)
 (ROOT/'results/FINAL_VALIDATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2));assert all(checks.values())
if __name__=='__main__':main()
