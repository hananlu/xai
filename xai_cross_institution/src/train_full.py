from pathlib import Path
import json,hashlib,time,copy
import numpy as np,pandas as pd,torch
from sklearn.linear_model import Ridge
from torch import nn
from data_common import ROOT,windows,period
from neural_feasibility import Forecaster

torch.set_num_threads(4)
def save_model(kind,seed,model,meta):
 p=ROOT/f'models/{kind}_{seed}.pt';torch.save({'kind':kind,'state':model.state_dict(),'mean':float(model.mean),'std':float(model.std),'metadata':meta},p)
 return str(p.name)

def main():
 start=time.time();(ROOT/'models').mkdir(exist_ok=True);split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');source=[];validation=[];profile_y=[];profile_h=[];counts=[]
 for row in split.itertuples():
  if row.role=='target':continue
  v=windows(ROOT/f'data/institution_{row.id}.csv.gz');q=period(v,'2024-01-01','2025-01-01') if row.role=='source' else period(v,'2025-01-01','2025-04-01')
  x=np.log1p(v['X'][q]).astype('float32');y=np.log1p(v['Y'][q]).astype('float32');assert len(x)>0
  counts.append(dict(id=row.id,role=row.role,n=len(x)))
  if row.role=='source':
   source.append((row.id,x,y));t=v['t'];ok=(t>=pd.Timestamp('2024-01-01',tz='UTC'))&(t<pd.Timestamp('2025-01-01',tz='UTC'))&v['valid'];profile_y.extend(v['y'][ok]);profile_h.extend((t.day_of_week.to_numpy()*24+t.hour.to_numpy())[ok])
  else:validation.append((row.id,torch.from_numpy(x),torch.from_numpy(y)))
 X=np.concatenate([a[1] for a in source]);Y=np.concatenate([a[2] for a in source]);mean=float(X.mean());std=float(X.std());profile_y=np.array(profile_y);profile_h=np.array(profile_h);profile=np.array([np.median(profile_y[profile_h==j]) for j in range(168)])
 np.save(ROOT/'models/source_profile.npy',profile);pd.DataFrame(counts).to_csv(ROOT/'results/full_fit_counts.csv',index=False)
 choices=[];ridge_coef=[];ridge_intercept=[]
 for k,h in enumerate([1,6]):
  candidates=[]
  for alpha in [.1,1,10,100]:
   m=Ridge(alpha=alpha,solver='cholesky').fit(X.astype('float64'),Y[:,k].astype('float64'));loss=float(np.mean([np.mean(abs(m.predict(a.numpy())-b.numpy()[:,k])) for _,a,b in validation]));candidates.append((loss,alpha,m));choices.append(dict(kind='ridge_trial',seed=0,horizon=h,alpha=alpha,validation_log_mae=loss))
  loss,alpha,m=min(candidates,key=lambda z:(z[0],z[1]));ridge_coef.append(m.coef_);ridge_intercept.append(m.intercept_);choices.append(dict(kind='ridge_selected',seed=0,horizon=h,alpha=alpha,validation_log_mae=loss))
 np.savez_compressed(ROOT/'models/ridge_0.npz',coef=np.stack(ridge_coef),intercept=np.array(ridge_intercept))
 history=[]
 def fit(kind,seed,lr):
  torch.manual_seed(seed);rng=np.random.default_rng(seed);model=Forecaster(kind,mean,std);opt=torch.optim.Adam(model.parameters(),lr=lr);best=np.inf;state=None;stale=0;best_epoch=0;t0=time.time()
  for epoch in range(1,31):
   model.train();slices=[]
   for _,a,b in source:
    ix=rng.choice(len(a),1024,replace=True);slices.append((a[ix],b[ix]))
   ax=np.concatenate([a for a,b in slices]);by=np.concatenate([b for a,b in slices]);order=rng.permutation(len(ax));losses=[]
   for ix in np.array_split(order,128):
    opt.zero_grad();pred=model.log_prediction(torch.from_numpy(ax[ix]));loss=((pred-torch.from_numpy(by[ix]))**2).mean();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
   model.eval()
   with torch.no_grad():score=float(np.mean([float(abs(model.log_prediction(a)-b).mean()) for _,a,b in validation]))
   history.append(dict(kind=kind,seed=seed,lr=lr,epoch=epoch,train_mse=np.mean(losses),validation_macro_log_mae=score))
   if score<best-1e-12:best=score;state=copy.deepcopy(model.state_dict());stale=0;best_epoch=epoch
   else:stale+=1
   print(kind,seed,lr,'epoch',epoch,'val',round(score,6),'elapsed',round(time.time()-t0,1),flush=True)
   pd.DataFrame(history).to_csv(ROOT/'results/training_history.csv',index=False)
   if stale>=5:break
  model.load_state_dict(state);return model,dict(kind=kind,seed=seed,learning_rate=lr,best_epoch=best_epoch,validation_log_mae=best,runtime_seconds=time.time()-t0)
 for kind in ['dlinear','gru']:
  candidates=[]
  for lr in [.001,.0003]:
   model,meta=fit(kind,42,lr);candidates.append((meta['validation_log_mae'],lr,model,meta));choices.append(meta|{'phase':'lr_trial'})
  _,lr,model,meta=min(candidates,key=lambda v:(v[0],v[1]));save_model(kind,42,model,meta);choices.append(meta|{'phase':'selected'})
  for seed in [123,2026]:
   model,meta=fit(kind,seed,lr);save_model(kind,seed,model,meta);choices.append(meta|{'phase':'selected'})
 (ROOT/'results/MODEL_SELECTION.json').write_text(json.dumps(choices,indent=2));facts=dict(status='training_complete',runtime_seconds=time.time()-start,source_institutions=len(source),validation_institutions=len(validation),target_institutions_fitted=0,source_windows=len(X),normalization_mean=mean,normalization_std=std,models=[dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((ROOT/'models').glob('*'))],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'results/TRAINING_COMPLETE.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
