import json,numpy as np,torch
from torch import nn
from benchmark_common import games,response_game,quality,order,templates,integrated_gradients,ROOT
class Mock(nn.Module):
 def __init__(self):
  super().__init__();b=np.repeat(np.arange(1,8),24)/168;self.register_buffer('b',torch.tensor(np.stack([b,b[::-1]]),dtype=torch.float64))
 def forward(self,x):return x@self.b.T
class Predictor:
 def __init__(self):self.net=Mock()
 def __call__(self,x,bias=None):
  with torch.no_grad():return self.net(torch.tensor(x,dtype=torch.float64)).numpy()
def main():
 m=Predictor();x=np.concatenate([np.full(24,j+1)+.2*(j+1)*np.sin(np.arange(24)*2*np.pi/24) for j in range(7)]);r=np.zeros(168)
 p,oc,v,e=games(m,x,r);exact=(x[None,:]*m.net.b.numpy()).reshape(2,7,24).sum(2);assert np.allclose(p,exact)
 checks=[]
 for name,replacement in templates(x).items():
  vv,random,oracle=response_game(m,x,replacement);effects=abs(((x-replacement)[None,:]*m.net.b.numpy()).reshape(2,7,24).sum(2));assert np.allclose(random,effects.sum(1)/3)
  for k in range(2):
   rank=order(effects[k],'mock');u,q,gap=quality(vv,rank,random,oracle);assert abs(q[k]-1)<1e-10
  checks.append(name)
 flat=np.ones(168);vv,rr,oo=response_game(m,flat,templates(flat)['interpolation']);_,q,g=quality(vv,np.arange(7),rr,oo);assert np.isnan(q).all()
 ig,accepted,nodes,err,change=integrated_gradients(m,x,r);assert accepted.all() and np.allclose(ig,exact)
 facts=dict(status='passed',linear_shapley_oracle=True,random_response_matches_closed_form=True,operator_oracle_quality_one=True,zero_response_marked_undefined=True,linear_ig_oracle=True,operators=checks,target_data_used=False,interpretation='Validates operator-specific ranking arithmetic, not real-world causal feature importance.')
 (ROOT/'results/RESPONSE_ENDPOINT_CALIBRATION.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
