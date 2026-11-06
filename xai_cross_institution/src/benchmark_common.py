from pathlib import Path
import json,hashlib,itertools
from math import factorial
import numpy as np,torch
from torch import nn
from numpy.polynomial.legendre import leggauss
from data_common import ROOT
from neural_feasibility import Forecaster

torch.set_num_threads(4)
MASKS=((np.arange(128)[:,None]>>np.arange(7))&1).astype(float)
PERMUTATIONS=np.array(list(itertools.permutations(range(7))),dtype=int)
REMOVED=np.column_stack([np.zeros(5040,dtype=int),np.cumsum(1<<PERMUTATIONS,axis=1)])
SHAPLEY_WEIGHTS=[]
for j in range(7):
 ix=np.where(MASKS[:,j]==0)[0];s=MASKS[ix].sum(1).astype(int);w=np.array([factorial(k)*factorial(6-k)/factorial(7) for k in s]);SHAPLEY_WEIGHTS.append((ix,w))

class RidgeModule(nn.Module):
 def __init__(self,coef,intercept):
  super().__init__();self.register_buffer('coef',torch.tensor(coef,dtype=torch.float64));self.register_buffer('intercept',torch.tensor(intercept,dtype=torch.float64))
 def log_prediction(self,x):return x@self.coef.T+self.intercept
 def forward(self,x):return torch.expm1(torch.clamp_min(self.log_prediction(torch.log1p(x)),0))

class Predictor:
 def __init__(self,kind,seed):
  self.kind=kind;self.seed=seed
  if kind=='ridge':
   m=np.load(ROOT/'models/ridge_0.npz');self.net=RidgeModule(m['coef'],m['intercept'])
  else:
   d=torch.load(ROOT/f'models/{kind}_{seed}.pt',weights_only=True,map_location='cpu');self.net=Forecaster(kind,d['mean'],d['std']);self.net.load_state_dict(d['state']);self.net.double()
  self.net.eval()
 def __call__(self,x,bias=None,rawlog=False):
  x=np.asarray(x,dtype=float);flat=x.reshape(-1,168);chunks=[]
  with torch.no_grad():
   for a in range(0,len(flat),512):
    t=torch.tensor(flat[a:a+512],dtype=torch.float64);z=self.net.log_prediction(torch.log1p(t));
    if bias is not None:z=z+torch.tensor(bias,dtype=torch.float64)
    y=z if rawlog else torch.expm1(torch.clamp_min(z,0));chunks.append(y.numpy())
  return np.concatenate(chunks).reshape(x.shape[:-1]+(2,))

def games(model,x,r,bias=None):
 coal=r[None,:]+np.repeat(MASKS,24,axis=1)*(x-r)[None,:];v=model(coal,bias);phi=np.zeros((2,7))
 for j,(ix,w) in enumerate(SHAPLEY_WEIGHTS):phi[:,j]=np.sum((v[ix+(1<<j)]-v[ix])*w[:,None],axis=0)
 err=abs(phi.sum(1)-(v[-1]-v[0]));assert (err<=1e-8+1e-6*abs(v[-1]-v[0])).all()
 occ=abs(v[-1]-v[127-(1<<np.arange(7))]);return phi,occ.T,v,err

def templates(x):
 b=x.reshape(7,24)
 return {'interpolation':np.stack([np.linspace(a[0],a[-1],24) for a in b]).ravel(),'rotation':np.roll(b,1,axis=0).ravel()}

def response_game(model,x,r,bias=None):
 # V indexes replaced (rather than retained) groups.
 a=x[None,:]+np.repeat(MASKS,24,axis=1)*(r-x)[None,:];v=model(a,bias)
 response=abs(v[REMOVED[:,1:]]-v[REMOVED[:,:-1]]);cum=np.cumsum(response,axis=1);utilities=cum[:,[0,1,3],:].mean(1)
 return v,utilities.mean(0),utilities.max(0)

def order(scores,key):
 # Scores are nonnegative; shared deterministic tie keys.
 tie=np.array([int(hashlib.sha256(f'{key}:{j}'.encode()).hexdigest()[:12],16) for j in range(7)])
 return np.lexsort((tie,-np.asarray(scores)))

def quality(v,rank,random,oracle):
 masks=np.r_[0,np.cumsum(1<<rank)];cpd=np.cumsum(abs(v[masks[1:]]-v[masks[:-1]]),axis=0);u=cpd[[0,1,3]].mean(0);gap=oracle-random
 q=np.divide(u-random,gap,out=np.full(2,np.nan),where=gap>1e-9)
 assert np.all(q[np.isfinite(q)]<=1.00001),q
 return u,q,gap

NODES={n:leggauss(n) for n in [32,64,128,256,512]}
def integrated_gradients(model,x,r):
 delta=x-r;prev=None;accepted=np.zeros(2,bool);answer=np.zeros((2,168));steps=np.zeros(2,int);errors=np.zeros(2);lastchange=np.zeros(2)
 contrast=model(x)-model(r)
 for n,(ab,w) in NODES.items():
  alpha=(ab+1)/2;ww=w/2;current=np.zeros((2,168))
  for a in range(0,n,64):
   raw=r[None,:]+alpha[a:a+64,None]*delta[None,:];p=torch.tensor(raw,dtype=torch.float64,requires_grad=True);z=model.net(p)
   for k in range(2):
    grad=torch.autograd.grad(z[:,k].sum(),p,retain_graph=k==0)[0].detach().numpy();current[k]+=np.sum(ww[a:a+64,None]*grad,axis=0)*delta
  err=abs(current.sum(1)-contrast)
  if prev is not None:
   change=abs(current-prev).sum(1);ok=(err<=1e-8+1e-3*abs(contrast))&(change<=1e-8+1e-3*abs(current).sum(1));new=ok&~accepted
   answer[new]=current[new];steps[new]=n;errors[new]=err[new];lastchange[new]=change[new];accepted|=ok
  prev=current
  if accepted.all():break
 remaining=~accepted;answer[remaining]=current[remaining];steps[remaining]=n;errors[remaining]=err[remaining];lastchange[remaining]=change[remaining]
 return answer.reshape(2,7,24).sum(2),accepted,steps,errors,lastchange
