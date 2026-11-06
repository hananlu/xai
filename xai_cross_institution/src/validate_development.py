"""Recalculate saved development forecast metrics from data and coefficients."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];V2=ROOT.parent/'xai_research_v2'
def main():
 m=np.load(ROOT/'results/development_ridge_log.npz');meta=json.loads((ROOT/'results/DEVELOPMENT_FEASIBILITY.json').read_text());metrics=pd.read_csv(ROOT/'results/development_forecast_metrics.csv');maxdiff=0.;count=0
 frozen=json.loads((ROOT/'results/DEVELOPMENT_PREFIT_HASHES.json').read_text())
 for p,h in frozen['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 ids=set(map(int,meta['roles']));new=set(pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv').id.tolist());assert not ids&new
 for ident,role in meta['roles'].items():
  if role=='validation':continue
  ident=int(ident);d=pd.read_csv(V2/f'data/institution_{ident}.csv.gz');t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));y=d.n_bytes.to_numpy(float)/1e9
  valid=d.complete_hour.to_numpy(bool)&~d.conservative_artifact_flag.to_numpy(bool)&np.isfinite(y)&(y>=0)
  o=np.arange(167,len(y)-6);ok=np.ones(len(o),bool)
  for j in range(168):ok&=valid[o-j]
  for h in [1,6]:ok&=valid[o+h]
  o=o[ok];keep=(t[o+1]>=pd.Timestamp('2025-02-01',tz='UTC'))&(t[o+6]<pd.Timestamp('2025-04-01',tz='UTC'))&(t[o].hour%6==0);o=o[keep]
  X=np.stack([y[a-167:a+1] for a in o]);Y=np.stack([y[o+h] for h in [1,6]],1)
  P=np.expm1(np.maximum(np.log1p(X)@m['coef'].T+m['intercept'],0))
  models={'ridge_log_nonnegative':P,'persistence':np.repeat(X[:,-1,None],2,axis=1),'daily':np.stack([y[o+h-24] for h in [1,6]],1),'weekly':np.stack([y[o+h-168] for h in [1,6]],1)}
  for name,p in models.items():
   for k,h in enumerate([1,6]):
    row=metrics[(metrics.id==ident)&(metrics.model==name)&(metrics.horizon==h)].iloc[0];assert len(o)==row.n
    for val,expected in [(np.mean(abs(p[:,k]-Y[:,k])),row.mae_gb),(np.sqrt(np.mean((p[:,k]-Y[:,k])**2)),row.rmse_gb),(np.mean(p[:,k]<0),row.negative_fraction),(np.mean(p[:,k]==0),row.zero_fraction)]:
     err=abs(float(val)-float(expected));maxdiff=max(maxdiff,err);assert err<1e-9
    count+=1
 original=pd.read_csv(ROOT/'results/development_attribution_checks.csv');follow=pd.read_csv(ROOT/'results/ig_adaptive_followup.csv');assert len(follow)==int((~original.ig_accepted).sum())==12;assert follow.accepted.all();assert len(original)==384
 out=dict(status='passed',prefit_hashes_unchanged=True,development_ids_disjoint_from_new_48=True,forecast_metric_rows_recalculated=count,max_saved_metric_difference=maxdiff,original_ig_failures_retained=12,adaptive_followup_passes=12,target_institutions_used=False,scope='Artifact/numerical validation; no confirmatory transfer or novelty claim')
 (ROOT/'results/DEVELOPMENT_VALIDATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':main()
