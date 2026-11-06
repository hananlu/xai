from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def windows(path):
 d=pd.read_csv(path);t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));y=d.n_bytes.to_numpy(float)/1e9
 valid=d.complete_hour.to_numpy(bool)&~d.conservative_artifact_flag.to_numpy(bool)&np.isfinite(y)&(y>=0)
 o=np.arange(167,len(y)-6);ok=np.ones(len(o),bool)
 for j in range(168):ok&=valid[o-j]
 for h in [1,6]:ok&=valid[o+h]
 o=o[ok];X=np.stack([y[a-167:a+1] for a in o]);Y=np.stack([y[o+h] for h in [1,6]],1)
 return dict(X=X,Y=Y,o=o,t=t,y=y,valid=valid)

def period(v,start,end,stride=None):
 t,o=v['t'],v['o'];q=(t[o+1]>=pd.Timestamp(start,tz='UTC'))&(t[o+6]<pd.Timestamp(end,tz='UTC'))
 if stride:q&=(t[o].hour%stride==0)
 return q
