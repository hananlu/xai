"""Development-only nonnegative forecast function and attribution numerical feasibility."""
from pathlib import Path
import hashlib,json,time
import numpy as np,pandas as pd
from sklearn.linear_model import Ridge
from numpy.polynomial.legendre import leggauss
from math import factorial
ROOT=Path(__file__).resolve().parents[1];V2=ROOT.parent/'xai_research_v2';L=168
MASKS=((np.arange(128)[:,None]>>np.arange(7))&1).astype(float)

def predict(X,coef,intercept):return np.expm1(np.maximum(np.log1p(X)@coef.T+intercept,0))

def ig(X,R,coef,intercept):
 n=len(X);prev=None;accepted=np.zeros((n,2),bool);result=np.zeros((n,2,L));steps=np.zeros((n,2),int);errors=np.zeros((n,2));changes=np.zeros((n,2))
 contrast=predict(X,coef,intercept)-predict(R,coef,intercept)
 for nodes in [32,64,128,256,512,1024]:
  ab,w=leggauss(nodes);a=(ab+1)/2;w=w/2;p=R[:,None,:]+a[None,:,None]*(X-R)[:,None,:];z=np.log1p(p)@coef.T+intercept
  current=np.stack([(X-R)*np.sum(w[None,:,None]*((np.exp(np.maximum(z[:,:,k],0))*(z[:,:,k]>0))[:,:,None]*coef[k][None,None,:]/(1+p)),axis=1) for k in range(2)],axis=1)
  error=abs(current.sum(2)-contrast)
  if prev is not None:
   change=abs(current-prev).sum(2);ok=(error<=1e-8+1e-3*abs(contrast))&(change<=1e-8+1e-3*abs(current).sum(2));new=ok&~accepted
   result[new]=current[new];steps[new]=nodes;errors[new]=error[new];changes[new]=change[new];accepted|=ok
  prev=current
  if accepted.all():break
 un=~accepted;result[un]=current[un];steps[un]=nodes;errors[un]=error[un];changes[un]=change[un]
 return result,accepted,steps,errors,changes

def main():
 start=time.time();selection=pd.read_csv(V2/'data/selection_training_only.csv');dev=selection[selection.selected].copy();roles={}
 for _,group in dev.groupby('stratum'):
  ids=sorted(group.id.tolist(),key=lambda i:hashlib.sha256(f'ci-dev-2026-v1:{i}'.encode()).hexdigest())
  roles.update(dict(zip(ids,['source','validation','development_holdout'])))
 assert len(roles)==12;cache={};source_values=[];source_how=[];trainx=[];trainy=[]
 for ident,role in sorted(roles.items()):
  d=pd.read_csv(V2/f'data/institution_{ident}.csv.gz');t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));y=d.n_bytes.to_numpy(float)/1e9
  valid=d.complete_hour.to_numpy(bool)&~d.conservative_artifact_flag.to_numpy(bool)&np.isfinite(y)&(y>=0)
  o=np.arange(L-1,len(y)-6);ok=np.ones(len(o),bool)
  for j in range(L):ok&=valid[o-j]
  for h in [1,6]:ok&=valid[o+h]
  o=o[ok];X=np.stack([y[v-167:v+1] for v in o]);Y=np.stack([y[o+h] for h in [1,6]],1)
  target1=t[o+1];target6=t[o+6]
  tr=(target1>=pd.Timestamp('2024-01-01',tz='UTC'))&(target6<pd.Timestamp('2025-01-01',tz='UTC'))
  va=(target1>=pd.Timestamp('2025-01-01',tz='UTC'))&(target6<pd.Timestamp('2025-02-01',tz='UTC'))
  ev=(target1>=pd.Timestamp('2025-02-01',tz='UTC'))&(target6<pd.Timestamp('2025-04-01',tz='UTC'))&(t[o].hour%6==0)
  cache[ident]=dict(role=role,X=X,Y=Y,origins=o,time=t,y=y,tr=tr,va=va,ev=ev)
  if role=='source':
   trainx.append(np.log1p(X[tr]));trainy.append(np.log1p(Y[tr]));tt=(t>=pd.Timestamp('2024-01-01',tz='UTC'))&(t<pd.Timestamp('2025-01-01',tz='UTC'))&valid
   source_values.extend(y[tt]);source_how.extend((t.day_of_week.to_numpy()*24+t.hour.to_numpy())[tt])
 TX=np.concatenate(trainx);TY=np.concatenate(trainy);coef=[];intercept=[];choices=[]
 for k,h in enumerate([1,6]):
  candidates=[]
  for alpha in [.1,1,10,100]:
   m=Ridge(alpha=alpha,solver='cholesky').fit(TX,TY[:,k]);losses=[]
   for v in cache.values():
    if v['role']=='validation':losses.append(float(abs(m.predict(np.log1p(v['X'][v['va']]))-np.log1p(v['Y'][v['va'],k])).mean()))
   candidates.append((float(np.mean(losses)),alpha,m))
  loss,alpha,m=min(candidates,key=lambda z:(z[0],z[1]));coef.append(m.coef_);intercept.append(m.intercept_);choices.append(dict(horizon=h,alpha=alpha,validation_macro_log_mae=loss))
 coef=np.stack(coef);intercept=np.array(intercept);source_values=np.array(source_values);source_how=np.array(source_how)
 profile=np.array([np.median(source_values[source_how==k]) for k in range(168)])
 np.savez_compressed(ROOT/'results/development_ridge_log.npz',coef=coef,intercept=intercept,source_profile_gb=profile)
 metrics=[];attributes=[];gradient_errors=[];shapley_errors=[]
 for ident,v in cache.items():
  if v['role']=='validation':continue
  X=v['X'][v['ev']];Y=v['Y'][v['ev']];o=v['origins'][v['ev']];t=v['time'];y=v['y'];P=predict(X,coef,intercept)
  preds={'ridge_log_nonnegative':P,'persistence':np.repeat(X[:,-1,None],2,axis=1),'daily':np.stack([y[o+h-24] for h in [1,6]],1),'weekly':np.stack([y[o+h-168] for h in [1,6]],1)}
  for name,p in preds.items():
   for k,h in enumerate([1,6]):metrics.append(dict(id=ident,role=v['role'],model=name,horizon=h,n=len(o),mae_gb=float(abs(p[:,k]-Y[:,k]).mean()),rmse_gb=float(np.sqrt(np.mean((p[:,k]-Y[:,k])**2))),negative_fraction=float((p[:,k]<0).mean()),zero_fraction=float((p[:,k]==0).mean())))
  ix=np.unique(np.linspace(0,len(o)-1,12,dtype=int));xx=X[ix];oo=o[ix]
  local=np.tile(np.median(xx.reshape(len(xx),7,24),axis=1),(1,7));how=t.day_of_week.to_numpy()*24+t.hour.to_numpy();source=np.stack([profile[how[a-167:a+1]] for a in oo])
  # Independent finite difference gradient checks, avoiding clamp nondifferentiability.
  for x in xx[:2]:
   z=np.log1p(x)@coef.T+intercept
   for j in [0,83,167]:
    eps=1e-6*max(1.,x[j]);xp=x.copy();xm=x.copy();xp[j]+=eps;xm[j]=max(0.,xm[j]-eps)
    fd=(predict(xp,coef,intercept)-predict(xm,coef,intercept))/(xp[j]-xm[j]);analytic=np.exp(np.maximum(z,0))*(z>0)*coef[:,j]/(1+x[j])
    err=float(np.max(abs(fd-analytic)/(1+abs(analytic))));gradient_errors.append(err);assert err<1e-5
  for reference,R in [('source_calendar',source),('history_hour_median',local)]:
   coal=R[:,None,:]+np.repeat(MASKS,24,axis=1)[None,:,:]*(xx-R)[:,None,:]
   values=predict(coal.reshape(-1,L),coef,intercept).reshape(len(xx),128,2);base=predict(R,coef,intercept);delta=predict(xx,coef,intercept)-base
   phi=np.zeros((len(xx),2,7))
   for j in range(7):
    absent=np.where(MASKS[:,j]==0)[0];sizes=MASKS[absent].sum(1).astype(int);w=np.array([factorial(a)*factorial(6-a)/factorial(7) for a in sizes])
    phi[:,:,j]=np.sum((values[:,absent+(1<<j),:]-values[:,absent,:])*w[None,:,None],axis=1)
   se=abs(phi.sum(2)-delta);shapley_errors.extend(se.ravel().tolist());assert (se<=1e-8+1e-6*abs(delta)).all()
   attrib,ok,nodes,err,change=ig(xx,R,coef,intercept);g=attrib.reshape(len(xx),2,7,24).sum(3)
   agreement=abs(g-phi).sum(2)/np.maximum(abs(phi).sum(2),1e-9)
   for i in range(len(xx)):
    for k,h in enumerate([1,6]):
     attributes.append(dict(id=ident,role=v['role'],origin=str(t[oo[i]]),horizon=h,reference=reference,ig_accepted=bool(ok[i,k]),ig_nodes=int(nodes[i,k]),ig_completeness_error_gb=float(err[i,k]),ig_l1_last_change_gb=float(change[i,k]),shapley_completeness_error_gb=float(se[i,k]),allocation_difference_l1_normalized=float(agreement[i,k]),prediction_gb=float(predict(xx[i],coef,intercept)[k]),reference_prediction_gb=float(base[i,k])))
 pd.DataFrame(metrics).to_csv(ROOT/'results/development_forecast_metrics.csv',index=False);pd.DataFrame(attributes).to_csv(ROOT/'results/development_attribution_checks.csv',index=False)
 facts=dict(status='development_feasibility_complete',runtime_seconds=time.time()-start,roles={str(k):v for k,v in roles.items()},source_training_windows=len(TX),model_selection=choices,forecast_metric_rows=len(metrics),attribution_cases=len(attributes),ig_failed_cases=sum(not v['ig_accepted'] for v in attributes),ig_node_counts=pd.Series([v['ig_nodes'] for v in attributes]).value_counts().to_dict(),max_shapley_efficiency_error_gb=max(shapley_errors),max_gradient_check_scaled_error=max(gradient_errors),target_institutions_used=False,confirmatory=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),protocol_sha256=hashlib.sha256((ROOT/'DEVELOPMENT_PROTOCOL.md').read_bytes()).hexdigest())
 (ROOT/'results/DEVELOPMENT_FEASIBILITY.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
