import json,time
from pathlib import Path
import numpy as np,pandas as pd
from data_common import ROOT,windows,period
from benchmark_common import Predictor
YEARS=[2025,2026]

def denominator(v):
 t,y,ok=v['t'],v['y'],v['valid'];ix=np.arange(168,len(y));q=(t[ix]>=pd.Timestamp('2024-01-01',tz='UTC'))&(t[ix]<pd.Timestamp('2025-01-01',tz='UTC'))&ok[ix]&ok[ix-168]
 d=float(np.mean(abs(y[ix[q]]-y[ix[q]-168])));return max(d,1e-9),bool(d<1e-9)

def naive(v,q,kind):
 o=v['o'][q];y=v['y']
 if kind=='persistence':return np.repeat(y[o,None],2,axis=1)
 lag=24 if kind=='daily' else 168
 return np.stack([y[o+h-lag] for h in [1,6]],axis=1)

def calibration(v,year,model=None,kind=None):
 q=period(v,f'{year}-04-01',f'{year}-04-08');n=int(q.sum())
 if n<24:return np.zeros(2),n
 predlog=model(v['X'][q],rawlog=True) if model is not None else np.log1p(naive(v,q,kind))
 return np.median(np.log1p(v['Y'][q])-predlog,axis=0),n

def main():
 start=time.time();(ROOT/'predictions').mkdir(exist_ok=True);split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');split=split[split.role!='validation'];cache={int(r.id):windows(ROOT/f'data/institution_{r.id}.csv.gz') for r in split.itertuples()};metrics=[];cal=[]
 specs=[(k,0) for k in ['persistence','daily','weekly','ridge']]+[(k,s) for k in ['dlinear','gru'] for s in [42,123,2026]]
 for kind,seed in specs:
  model=Predictor(kind,seed) if kind in ['ridge','dlinear','gru'] else None;frames=[]
  for row in split.itertuples():
   v=cache[row.id];den,floor=denominator(v)
   for year in YEARS:
    q=period(v,f'{year}-04-08',f'{year}-07-01',6);n=int(q.sum())
    if not n:continue
    bias,ncal=calibration(v,year,model,kind);base=model(v['X'][q],rawlog=True) if model is not None else np.log1p(naive(v,q,kind));truth=v['Y'][q];dates=v['t'][v['o'][q]].astype(str)
    for k,h in enumerate([1,6]):cal.append(dict(model=kind,seed=seed,id=row.id,year=year,horizon=h,n_calibration=ncal,bias_log=float(bias[k]),status='ok' if ncal>=24 else 'insufficient'))
    for arm,b in [('frozen',np.zeros(2)),('calibrated',bias)]:
     pred=np.expm1(np.maximum(base+b,0));assert np.isfinite(pred).all() and (pred>=0).all()
     for k,h in enumerate([1,6]):
      err=pred[:,k]-truth[:,k];metrics.append(dict(model=kind,seed=seed,id=row.id,role=row.role,year=year,arm=arm,horizon=h,n=n,mae_gb=float(abs(err).mean()),rmse_gb=float(np.sqrt(np.mean(err**2))),mase=float(abs(err).mean()/den),mase_denominator_gb=den,denominator_floored=floor,negative_fraction=float((pred[:,k]<0).mean()),zero_fraction=float((pred[:,k]==0).mean())))
      frames.append(pd.DataFrame(dict(model=kind,seed=seed,id=row.id,role=row.role,year=year,arm=arm,horizon=h,origin=dates,target_gb=truth[:,k],prediction_gb=pred[:,k])))
  pd.concat(frames,ignore_index=True).to_csv(ROOT/f'predictions/{kind}_{seed}.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  pd.DataFrame(metrics).to_csv(ROOT/'results/forecast_metrics.csv',index=False);pd.DataFrame(cal).to_csv(ROOT/'results/calibration_offsets.csv',index=False);print('Forecasts',kind,seed,'complete',flush=True)
 facts=dict(status='complete',runtime_seconds=time.time()-start,specs=specs,metric_rows=len(metrics),predictions_files=len(specs),target_outcomes_scored=True,evaluation_periods=YEARS)
 (ROOT/'results/FORECAST_EVALUATION.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
