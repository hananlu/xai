"""Recovered-data forecasting experiment. Run from any directory; see README.md."""
from pathlib import Path
import argparse, copy, hashlib, json, platform, random, time
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.linear_model import Ridge
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
HORIZONS = np.array([1, 6])
SEEDS = [42, 123, 2026]

def save_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, default=str))
    tmp.replace(path)

def prepare():
    a = pd.read_csv(ROOT/'recovered/global_bytes_10min.csv')
    t = pd.read_csv(ROOT/'recovered/times_10_minutes.csv')
    assert a.id_time.is_unique and t.id_time.is_unique
    d = t.merge(a, on='id_time', how='outer', validate='one_to_one', indicator=True)
    assert (d['_merge']=='both').all()
    d['timestamp'] = pd.to_datetime(d.time, utc=True)
    d = d.sort_values('timestamp').reset_index(drop=True)
    assert d.timestamp.is_unique and (np.diff(d.id_time)==1).all()
    y = d.n_bytes.to_numpy(dtype=np.float64)/1e9
    assert np.isfinite(y).all() and (y>=0).all()
    dt = d.timestamp.diff().dt.total_seconds().to_numpy()
    breaks = np.r_[False, dt[1:] != 600]
    segment = np.cumsum(breaks)
    n = len(d); ntrain=int(.7*n); nval=int(.15*n)
    # Origin o predicts y[o], y[o+5]; every interval from weekly lag to h6 continuous.
    origins = np.arange(1008, n-5)
    valid = segment[origins-1008] == segment[origins+5]
    origins=origins[valid]
    indices={
      'train':origins[origins+5<ntrain],
      'val':origins[(origins>=ntrain)&(origins+5<ntrain+nval)],
      'test':origins[origins>=ntrain+nval]}
    mean=float(y[:ntrain].mean()); std=float(y[:ntrain].std())
    assert std>0 and all(len(v)>0 for v in indices.values())
    z=(y-mean)/std
    local=d.timestamp.dt.tz_convert('Europe/Prague')
    slots=local.dt.hour.to_numpy()*6+local.dt.minute.to_numpy()//10
    # Time-of-day medians use training observations only.
    prof=np.array([np.median(y[:ntrain][slots[:ntrain]==s]) for s in range(144)])
    profile=(prof[slots]-mean)/std
    gaps=[{'after_index':int(i-1),'before':str(d.timestamp[i-1]),
           'after':str(d.timestamp[i]),'difference_seconds':float(dt[i])}
          for i in np.flatnonzero(breaks)]
    audit={'n':n,'first':str(d.timestamp.iloc[0]),'last':str(d.timestamp.iloc[-1]),
           'train_end_exclusive':ntrain,'val_end_exclusive':ntrain+nval,
           'gaps':gaps,'zero_values':int((y==0).sum()),'scale_mean_GB':mean,'scale_std_GB':std,
           'splits':{k:{'count':len(v),'first_target':str(d.timestamp.iloc[v[0]]),
                       'last_h6_target':str(d.timestamp.iloc[v[-1]+5])} for k,v in indices.items()},
           'excluded_noncontinuous_origins':int((~valid).sum()),
           'train_mean_GB':mean,'train_min_GB':float(y[:ntrain].min()),'max_GB':float(y.max())}
    RESULTS.mkdir(exist_ok=True)
    save_json(RESULTS/'data_audit.json',audit)
    d[['id_time','timestamp','n_bytes']].assign(segment=segment,split=np.where(
        np.arange(n)<ntrain,'train',np.where(np.arange(n)<ntrain+nval,'val','test'))).to_csv(
        RESULTS/'audited_series.csv',index=False)
    return dict(d=d,y=y,z=z,idx=indices,mean=mean,std=std,profile=profile,
                constant=(np.median(y[:ntrain])-mean)/std,audit=audit)

def arrays(data, split, length):
    o=data['idx'][split]
    x=data['z'][o[:,None]+np.arange(-length,0)[None,:]].astype('float32')[...,None]
    y=data['z'][o[:,None]+HORIZONS[None,:]-1].astype('float32')
    return x,y

class Forecaster(nn.Module):
    def __init__(self, pooling='attention', hidden=32):
        super().__init__();self.pooling=pooling
        self.lstm=nn.LSTM(1,hidden,batch_first=True)
        self.score=nn.Sequential(nn.Linear(hidden,hidden),nn.Tanh(),nn.Linear(hidden,1,bias=False)) if pooling=='attention' else nn.Linear(hidden,1)
        self.head=nn.Linear(hidden,2)
    def encode(self,x):return self.lstm(x)[0]
    def weights(self,h):
        if self.pooling=='last':
            w=torch.zeros_like(h[:,:,:1]);w[:,-1]=1;return w
        if self.pooling=='uniform':return torch.ones_like(h[:,:,:1])/h.shape[1]
        s=self.score(h)
        if self.pooling=='bounded':s=torch.tanh(s)
        return s.softmax(dim=1)
    def forward(self,x,uniform=False,return_weights=False):
        h=self.encode(x);w=torch.ones_like(h[:,:,:1])/h.shape[1] if uniform else self.weights(h)
        out=self.head((h*w).sum(dim=1))+x[:,-1,0:1]
        return (out,w.squeeze(-1)) if return_weights else out

def infer(model,x,device='cpu',uniform=False):
    model.eval();out=[]
    with torch.no_grad():
        for i in range(0,len(x),512):
            out.append(model(torch.as_tensor(x[i:i+512],device=device),uniform=uniform).cpu().numpy())
    return np.concatenate(out)

def metric(true,pred):
    e=pred-true
    return {'mae':float(np.abs(e).mean()),'rmse':float(np.sqrt(np.mean(e**2))),
            'wape_pct':float(100*np.abs(e).sum()/np.abs(true).sum())}

def record_predictions(data,label,seed,pred,val_mse=None,extras=None):
    o=data['idx']['test'];truth=data['y'][o[:,None]+HORIZONS[None,:]-1]
    rows=[]
    for j,h in enumerate(HORIZONS):
        m=metric(truth[:,j],pred[:,j]);m.update(model=label,seed=seed,horizon=int(h),
          n=len(o),validation_mse_standardized=val_mse)
        if extras:m.update(extras)
        rows.append(m)
    f=pd.DataFrame({'origin_index':o,'target_h1':data['d'].timestamp.iloc[o].astype(str).to_numpy(),
      'true_h1_GB':truth[:,0],'pred_h1_GB':pred[:,0],
      'true_h6_GB':truth[:,1],'pred_h6_GB':pred[:,1]})
    f.to_csv(RESULTS/f'pred_{label}_s{seed}.csv',index=False)
    save_json(RESULTS/f'metrics_{label}_s{seed}.json',rows)
    return rows

def baselines(data):
    o=data['idx']['test'];y=data['y']
    for label,lag in [('persistence',1),('seasonal_day',144),('seasonal_week',1008)]:
        pred=np.repeat(y[o-1,None],2,axis=1) if lag==1 else y[o[:,None]+HORIZONS-1-lag]
        record_predictions(data,label,0,pred)
    x,yt=arrays(data,'train',144);xv,yv=arrays(data,'val',144);xt,_=arrays(data,'test',144)
    selected=None;best=float('inf');search=[]
    with threadpool_limits(limits=4):
        for alpha in [.1,1,10,100]:
            model=Ridge(alpha=alpha).fit(x[:,:,0],yt)
            mse=float(np.mean((model.predict(xv[:,:,0])-yv)**2));search.append({'alpha':alpha,'val_mse':mse})
            if mse<best:best=mse;selected=model
        pred=selected.predict(xt[:,:,0])*data['std']+data['mean']
    np.savez(RESULTS/'ridge_parameters.npz',coef=selected.coef_,intercept=selected.intercept_,alpha=selected.alpha)
    save_json(RESULTS/'ridge_validation_search.json',search)
    record_predictions(data,'ridge',0,pred,best,{'alpha':selected.alpha})

def train(data,pooling,length,seed,device):
    label=f'{pooling}_L{length}';checkpoint=RESULTS/f'{label}_s{seed}.pt'
    if (RESULTS/f'metrics_{label}_s{seed}.json').exists():
        print('SKIP completed',label,seed,flush=True);return
    random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
    model=Forecaster(pooling).to(device)
    xt,yt=arrays(data,'train',length);xv,yv=arrays(data,'val',length)
    # Keep dataset on device to avoid repeated transfer/worker overhead.
    xt=torch.tensor(xt,device=device);yt=torch.tensor(yt,device=device)
    xv=torch.tensor(xv,device=device);yv=torch.tensor(yv,device=device)
    opt=torch.optim.Adam(model.parameters(),lr=.001)
    best=float('inf');best_state=None;best_epoch=0;stale=0;history=[];t0=time.time()
    gen=torch.Generator().manual_seed(seed)
    for epoch in range(1,41):
        model.train();total=0.;order=torch.randperm(len(xt),generator=gen).to(device)
        for batch in order.split(256):
            opt.zero_grad(set_to_none=True);pred=model(xt[batch]);loss=((pred-yt[batch])**2).mean()
            if not torch.isfinite(loss):raise FloatingPointError(f'Nonfinite {label} {seed}')
            loss.backward();nn.utils.clip_grad_norm_(model.parameters(),1.);opt.step()
            total+=loss.item()*len(batch)
        model.eval();vl=0.
        with torch.no_grad():
            for i in range(0,len(xv),512):
                vl+=((model(xv[i:i+512])-yv[i:i+512])**2).sum().item()
        vl/=yv.numel();tl=total/len(xt)
        history.append({'epoch':epoch,'train_mse':tl,'val_mse':vl,'elapsed_s':time.time()-t0})
        if vl<best:
            best=vl;best_state={k:v.detach().cpu().clone() for k,v in model.state_dict().items()};best_epoch=epoch;stale=0
        else:stale+=1
        print(f'{label} seed={seed} epoch={epoch} train={tl:.5f} val={vl:.5f} best={best_epoch} elapsed={time.time()-t0:.1f}s',flush=True)
        save_json(RESULTS/f'history_{label}_s{seed}.json',history)
        if stale>=6:break
    model.load_state_dict(best_state)
    torch.save({'state_dict':best_state,'pooling':pooling,'length':length,'seed':seed,
                'mean':data['mean'],'std':data['std'],'best_epoch':best_epoch},checkpoint)
    xte,_=arrays(data,'test',length)
    pred=infer(model,xte,device)*data['std']+data['mean']
    extras={'epochs':len(history),'best_epoch':best_epoch,'training_s':time.time()-t0,
            'device':device,'parameters':sum(p.numel() for p in model.parameters() if p.requires_grad)}
    record_predictions(data,label,seed,pred,best,extras)
    del model,xt,yt,xv,yv
    if device=='mps':torch.mps.empty_cache()

def verify(data):
    idx=data['idx'];d=data['d'];seg=np.cumsum(np.r_[False,d.timestamp.diff().dt.total_seconds().to_numpy()[1:]!=600])
    assert max(idx['train']+5)<data['audit']['train_end_exclusive']
    assert min(idx['val'])>=data['audit']['train_end_exclusive']
    assert max(idx['val']+5)<data['audit']['val_end_exclusive']
    assert min(idx['test'])>=data['audit']['val_end_exclusive']
    for split in idx:
        o=idx[split];assert (seg[o-1008]==seg[o+5]).all()
        for L in [144,288]:
            x,y=arrays(data,split,L)
            assert np.allclose(x[0,:,0],data['z'][o[0]-L:o[0]],rtol=1e-5,atol=1e-5)
            assert np.allclose(y[0],data['z'][o[0]+HORIZONS-1])
    # Attention normalizes over time and the recovered score is provably bounded.
    for pooling in ['last','uniform','attention','bounded']:
        m=Forecaster(pooling);x=torch.randn(3,144,1);out,w=m(x,return_weights=True)
        assert out.shape==(3,2) and torch.allclose(w.sum(1),torch.ones(3),atol=1e-6)
        if pooling=='bounded':assert (w.max(1).values/w.min(1).values<=np.exp(2)+1e-5).all()
    print('Verified split, segment, lag/target alignment, shapes and attention invariants.',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['audit','baselines','train','all'],default='all')
    p.add_argument('--device',default='cpu');p.add_argument('--pooling',default=None);p.add_argument('--seed',type=int);p.add_argument('--length',type=int,default=144)
    args=p.parse_args();torch.set_num_threads(4)
    data=prepare();verify(data)
    import sklearn,scipy,matplotlib
    save_json(RESULTS/'environment.json',dict(python=platform.python_version(),platform=platform.platform(),
      torch=torch.__version__,numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__,
      scipy=scipy.__version__,matplotlib=matplotlib.__version__,device=args.device))
    if args.mode in ['baselines','all']:baselines(data)
    if args.mode in ['train','all']:
        jobs=[(v,144,s) for v in ['last','uniform','attention','bounded'] for s in SEEDS]+[('attention',288,s) for s in SEEDS]
        if args.pooling:jobs=[(args.pooling,args.length,args.seed or 42)]
        for v,L,s in jobs:train(data,v,L,s,args.device)

if __name__=='__main__':main()
