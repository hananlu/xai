from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 audit=json.loads((ROOT/'data/DATA_AUDIT.json').read_text());frozen=json.loads((ROOT/'results/prefit_hashes.json').read_text());metrics=pd.read_csv(ROOT/'results/clean_metrics.csv');checks=[];maxdiff=0
 for f,h in frozen['files'].items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h,f
 for item in audit['selected']:
  p=ROOT/'data'/item['selected_file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['selected_sha256']
  d=pd.read_csv(p);y=d.n_bytes.to_numpy(float)/1e9;t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));ident=item['id'];a=np.load(ROOT/f'results/model_{ident}_ridge_clean.npz');o=a['pilot_origins'];xx=np.stack([y[v-167:v+1] for v in o]);target=np.stack([y[o+h] for h in [1,6]],1)
  assert np.all(t[o+1]>=pd.Timestamp('2025-02-01',tz='UTC')) and np.all(t[o+6]<pd.Timestamp('2025-04-01',tz='UTC'))
  assert np.array_equal(target,a['targets'])
  for name in ['ridge_clean','ridge_mask_aug']:
   m=np.load(ROOT/f'results/model_{ident}_{name}.npz');assert np.array_equal(o,m['pilot_origins'])
   f=(xx-float(m['mu']))/float(m['sigma'])
   if name=='ridge_mask_aug':f=np.concatenate([f,np.zeros_like(f)],1)
   pred=(f@m['coef'].T+m['intercept'])*float(m['sigma'])+float(m['mu']);diff=np.max(abs(pred-m['clean_predictions']));maxdiff=max(maxdiff,float(diff));assert diff<1e-8
   for k,h in enumerate([1,6]):
    row=metrics[(metrics.id==ident)&(metrics.model==name)&(metrics.horizon==h)].iloc[0]
    assert abs(float(np.mean(abs(pred[:,k]-target[:,k])))-row.mae_gb)<1e-8
  for name,pred in [('persistence',np.repeat(xx[:,-1,None],2,1)),('daily',np.stack([y[o+h-24] for h in [1,6]],1)),('weekly',np.stack([y[o+h-168] for h in [1,6]],1))]:
   for k,h in enumerate([1,6]):
    row=metrics[(metrics.id==ident)&(metrics.model==name)&(metrics.horizon==h)].iloc[0];assert abs(np.mean(abs(pred[:,k]-target[:,k]))-row.mae_gb)<1e-8
 r=pd.read_csv(ROOT/'results/stress_records.csv.gz');assert np.allclose(abs(r.corrupt_prediction_gb-r.target_gb),r.corrupt_abs_error_gb,atol=1e-8)
 assert pd.to_datetime(r.origin,utc=True).max()<pd.Timestamp('2025-04-01',tz='UTC')
 n=pd.read_csv(ROOT/'results/numerical_checks.csv');assert n.reconstruction_max_gb.max()<1e-8 and n.shift_identity_max_gb.max()<1e-8
 report=dict(status='passed',institutions=len(audit['selected']),clean_metric_rows=len(metrics),stress_records=len(r),all_selected_hashes_verified=True,prefit_hashes_verified=True,all_clean_model_and_baseline_MAEs_recalculated=True,checkpoint_prediction_max_difference_gb=maxdiff,all_stress_absolute_errors_recalculated=True,reserved_outcomes_scored=False,scope='artifact and numerical checks; not validation of novelty, deployment utility, or external-network generalization')
 (ROOT/'results/VALIDATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
