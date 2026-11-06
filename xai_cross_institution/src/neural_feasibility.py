from pathlib import Path
import json,copy,time,hashlib
import numpy as np,pandas as pd,torch
from torch import nn
from data_common import windows,period,ROOT

torch.set_num_threads(4)
class Forecaster(nn.Module):
 def __init__(self,kind,mean,std):
  super().__init__();self.kind=kind;self.register_buffer('mean',torch.tensor(float(mean)));self.register_buffer('std',torch.tensor(float(std)))
  if kind=='gru':self.gru=nn.GRU(1,32,batch_first=True);self.head=nn.Linear(32,2);nn.init.zeros_(self.head.weight);nn.init.zeros_(self.head.bias)
  else:
   self.trend=nn.Linear(168,2);self.season=nn.Linear(168,2)
   for m in [self.trend,self.season]:nn.init.constant_(m.weight,1/168);nn.init.zeros_(m.bias)
 def log_prediction(self,x):
  z=(x-self.mean)/self.std
  if self.kind=='gru':_,h=self.gru(z.unsqueeze(-1));return x[:,-1,None]+self.head(h[-1])*self.std
  trend=torch.nn.functional.avg_pool1d(torch.nn.functional.pad(z[:,None,:],(12,12),mode='replicate'),25,1)[:,0,:]
  return (self.trend(trend)+self.season(z-trend))*self.std+self.mean
 def forward(self,gb):return torch.expm1(torch.clamp_min(self.log_prediction(torch.log1p(gb)),0))

def main():
 start=time.time();roles=json.loads((ROOT/'results/DEVELOPMENT_FEASIBILITY.json').read_text())['roles'];cache={int(i):windows(ROOT.parent/f'xai_research_v2/data/institution_{i}.csv.gz') for i in roles}
 tx=[];ty=[];val=[]
 for i,v in cache.items():
  if roles[str(i)]=='source':
   q=period(v,'2024-01-01','2025-01-01');tx.append(np.log1p(v['X'][q]));ty.append(np.log1p(v['Y'][q]))
  elif roles[str(i)]=='validation':
   q=period(v,'2025-01-01','2025-02-01');val.append((torch.tensor(np.log1p(v['X'][q]),dtype=torch.float32),torch.tensor(np.log1p(v['Y'][q]),dtype=torch.float32)))
 X=np.concatenate(tx).astype('float32');Y=np.concatenate(ty).astype('float32');history=[];results=[]
 for kind in ['dlinear','gru']:
  torch.manual_seed(42);rng=np.random.default_rng(42);model=Forecaster(kind,X.mean(),X.std());opt=torch.optim.Adam(model.parameters(),lr=.001);best=np.inf;state=None
  for epoch in range(1,9):
   model.train();ix=rng.choice(len(X),4096,replace=True);losses=[]
   for chunk in np.array_split(ix,16):
    opt.zero_grad();p=model.log_prediction(torch.from_numpy(X[chunk]));loss=((p-torch.from_numpy(Y[chunk]))**2).mean();loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step();losses.append(float(loss.detach()))
   model.eval()
   with torch.no_grad():score=float(np.mean([float(((model.log_prediction(a)-b)**2).mean()) for a,b in val]))
   history.append(dict(kind=kind,epoch=epoch,training_mse=np.mean(losses),validation_macro_mse=score))
   if score<best:best=score;state=copy.deepcopy(model.state_dict())
   print(kind,epoch,score,flush=True)
  model.load_state_dict(state);model.double().eval();torch.save({'state':model.state_dict(),'kind':kind,'mean':float(model.mean),'std':float(model.std)},ROOT/f'results/development_{kind}.pt')
  for i,v in cache.items():
   if roles[str(i)]=='validation':continue
   q=period(v,'2025-02-01','2025-04-01',6);xx=v['X'][q];yy=v['Y'][q]
   with torch.no_grad():p=model(torch.tensor(xx,dtype=torch.float64)).numpy()
   assert np.isfinite(p).all() and (p>=0).all()
   for k,h in enumerate([1,6]):results.append(dict(kind=kind,id=i,role=roles[str(i)],horizon=h,n=len(p),mae_gb=float(abs(p[:,k]-yy[:,k]).mean()),negative_fraction=float((p[:,k]<0).mean())))
 pd.DataFrame(history).to_csv(ROOT/'results/neural_development_history.csv',index=False);pd.DataFrame(results).to_csv(ROOT/'results/neural_development_metrics.csv',index=False)
 facts=dict(status='passed',kind=['dlinear','gru'],epochs_max=8,seed=42,source_training_windows=len(X),development_only=True,target_institutions_used=False,runtime_seconds=time.time()-start,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'results/NEURAL_FEASIBILITY.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
