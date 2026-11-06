"""Analyze completed forecasts and audit temporal explanations without training."""
from pathlib import Path
import itertools, json, time
import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from experiment import ROOT, RESULTS, SEEDS, HORIZONS, Forecaster, prepare, arrays, infer, save_json, metric

FIG=ROOT/'figures'

def bootstrap_mean(values,block=144,n=1000,seed=2026):
    rng=np.random.default_rng(seed);values=np.asarray(values);N=len(values)
    # Moving blocks sample all valid non-wrapping start points, truncate final block.
    # Vectorized block sums avoid creating 1000 copies of the full origin list.
    full=N//block;rem=N%block;cs=np.r_[0,np.cumsum(values)]
    starts=rng.integers(0,N-block+1,size=(n,full))
    sums=(cs[starts+block]-cs[starts]).sum(1)
    if rem:
        tail=rng.integers(0,N-rem+1,size=n);sums+=cs[tail+rem]-cs[tail]
    means=sums/N
    return np.quantile(means,[.025,.975]).tolist()

def forecast_analysis(data):
    files=sorted(RESULTS.glob('metrics_*.json'));rows=[]
    for p in files:rows.extend(json.loads(p.read_text()))
    m=pd.DataFrame(rows);m.to_csv(RESULTS/'forecast_metrics.csv',index=False)
    table=m.groupby(['model','horizon']).agg(
      mae_mean=('mae','mean'),mae_sd=('mae','std'),rmse_mean=('rmse','mean'),
      rmse_sd=('rmse','std'),wape_mean=('wape_pct','mean'),n_runs=('seed','count')).reset_index()
    persistence=table[table.model=='persistence'].set_index('horizon').mae_mean
    table['mae_skill_vs_persistence_pct']=[100*(1-r.mae_mean/persistence.loc[r.horizon]) for r in table.itertuples()]
    table.to_csv(RESULTS/'forecast_summary.csv',index=False)
    base=pd.read_csv(RESULTS/'pred_persistence_s0.csv')
    intervals=[];thirds=[]
    for label in m.model.unique():
        paths=list(RESULTS.glob(f'pred_{label}_s*.csv'))
        forecasts=[pd.read_csv(p) for p in paths]
        assert all(np.array_equal(f.origin_index,base.origin_index) for f in forecasts)
        for h in [1,6]:
            truth=base[f'true_h{h}_GB'].to_numpy()
            # Average loss across independently trained seeds, NOT loss of an ensemble.
            losses=np.stack([np.abs(f[f'pred_h{h}_GB']-truth) for f in forecasts])
            delta=losses.mean(0)-np.abs(base[f'pred_h{h}_GB']-truth)
            for block in [72,144,288]:
                ci=bootstrap_mean(delta,block)
                intervals.append(dict(model=label,horizon=h,block=block,
                  delta_mae_GB=float(delta.mean()),ci_low=ci[0],ci_high=ci[1]))
            for k,idx in enumerate(np.array_split(np.arange(len(base)),3)):
                for i,f in enumerate(forecasts):
                    mm=metric(truth[idx],f[f'pred_h{h}_GB'].to_numpy()[idx]);mm.update(model=label,horizon=h,third=k+1,run=paths[i].stem)
                    thirds.append(mm)
    pd.DataFrame(intervals).to_csv(RESULTS/'paired_block_bootstrap.csv',index=False)
    pd.DataFrame(thirds).to_csv(RESULTS/'test_period_thirds.csv',index=False)
    print(table.to_string(index=False),flush=True)
    # Three matched recurrent comparisons, losses averaged across seeds.
    contrasts=[]
    for a,b in [('attention_L144','uniform_L144'),('attention_L144','last_L144'),
                ('attention_L144','bounded_L144'),('attention_L288','attention_L144'),
                ('attention_L144','ridge')]:
        for h in [1,6]:
            truth=base[f'true_h{h}_GB'].to_numpy()
            def loss(label):
                return np.mean([np.abs(pd.read_csv(p)[f'pred_h{h}_GB'].to_numpy()-truth)
                  for p in RESULTS.glob(f'pred_{label}_s*.csv')],axis=0)
            delta=loss(a)-loss(b)
            for block in [72,144,288]:
                ci=bootstrap_mean(delta,block);contrasts.append(dict(a=a,b=b,horizon=h,block=block,
                 delta_mae_GB=float(delta.mean()),ci_low=ci[0],ci_high=ci[1]))
    pd.DataFrame(contrasts).to_csv(RESULTS/'matched_model_contrasts.csv',index=False)
    return table

def get_weights(model,x):
    with torch.no_grad():
        pred,w=model(torch.tensor(x),return_weights=True)
    return pred.numpy(),w.numpy()

def integrated_gradients(model,x,b,steps=32):
    grad=np.zeros_like(x,dtype=np.float64)
    model.eval()
    for i,alpha in enumerate(np.linspace(0,1,steps+1)):
        inp=torch.tensor(b+alpha*(x-b),requires_grad=True,dtype=torch.float32)
        out=model(inp)[:,0].sum()
        g=torch.autograd.grad(out,inp)[0].detach().numpy()
        grad+=g*(.5 if i in [0,steps] else 1)
    attr=(x-b)*grad/steps
    diff=infer(model,x)[:,0]-infer(model,b)[:,0]
    residual=attr.sum((1,2))-diff
    return attr,residual

def perturb(model,x,b,orders,k,return_correction=False):
    xp=x.copy()
    for i,order in enumerate(orders):
        for block in order[:k]:xp[i,block*12:(block+1)*12]=b[i,block*12:(block+1)*12]
    pred=infer(model,xp)[:,0]
    return (pred,pred-xp[:,-1,0]) if return_correction else pred

def xai_analysis(data):
    allx,ally=arrays(data,'test',144)
    chosen=np.linspace(0,len(allx)-1,96,dtype=int)
    origins=data['idx']['test'][chosen]
    x=allx[chosen];truth=ally[chosen,0]
    profile=data['profile'][origins[:,None]+np.arange(-144,0)].astype('float32')[...,None]
    const=np.full_like(x,data['constant'])
    records=[];diag=[];agreements=[];weights={};raw=[]
    for variant in ['attention','bounded']:
        for seed in SEEDS:
            checkpoint=torch.load(RESULTS/f'{variant}_L144_s{seed}.pt',map_location='cpu',weights_only=True)
            model=Forecaster(variant);model.load_state_dict(checkpoint['state_dict']);model.eval()
            t0=time.time();pred,w=get_weights(model,x);p=pred[:,0]
            attr,residual=integrated_gradients(model,x,profile,32)
            # Exact subtraction of the linear persistence path from full-model IG.
            correction_attr=attr.copy()
            correction_attr[:,-1,0]-=x[:,-1,0]-profile[:,-1,0]
            attr64,res64=integrated_gradients(model,x[:16],profile[:16],64)
            wb=w.reshape(96,12,12).sum(2)
            ig=np.abs(attr[:,:,0]).reshape(96,12,12).sum(2)
            ig_correction=np.abs(correction_attr[:,:,0]).reshape(96,12,12).sum(2)
            weights[(variant,seed)]=wb
            occ=[]
            for block in range(12):
                xp=x.copy();xp[:,block*12:(block+1)*12]=profile[:,block*12:(block+1)*12]
                occ.append(np.abs(infer(model,xp)[:,0]-p))
            occ=np.stack(occ,axis=1)
            rankings={'attention':np.argsort(-wb,axis=1),
                      'integrated_gradients':np.argsort(-ig,axis=1),
                      'occlusion':np.argsort(-occ,axis=1),
                      'recency':np.tile(np.arange(11,-1,-1),(96,1))}
            rng=np.random.default_rng(2026)
            random_orders=[np.stack([rng.permutation(12) for _ in range(96)]) for j in range(20)]
            for i in range(96):
                for a,b in [('attention','ig'),('attention','occlusion'),('ig','occlusion'),('attention','ig_correction')]:
                    v={'attention':wb,'ig':ig,'occlusion':occ,'ig_correction':ig_correction}
                    rho=float(spearmanr(v[a][i],v[b][i]).statistic)
                    agreements.append(dict(model=variant,seed=seed,origin=int(origins[i]),pair=f'{a}-{b}',rho=rho))
            for replacement,b in [('time_of_day',profile),('constant',const)]:
                for method,order in list(rankings.items())+[('random',random_orders)]:
                    for k in [1,3,6]:
                        pairs=[perturb(model,x,b,order,k,True)] if method!='random' else [perturb(model,x,b,o,k,True) for o in random_orders]
                        outs=[q[0] for q in pairs]
                        correction_shifts=np.mean([np.abs(q[1]-(p-x[:,-1,0])) for q in pairs],axis=0)*data['std']
                        # Average the effects, not predictions, over random rankings.
                        shifts=np.mean([np.abs(q-p) for q in outs],axis=0)*data['std']
                        error_delta=np.mean([np.abs(q-truth)-np.abs(p-truth) for q in outs],axis=0)*data['std']
                        for i in range(96):
                            records.append(dict(model=variant,seed=seed,origin=int(origins[i]),method=method,
                              replacement=replacement,k_blocks=k,prediction_shift_GB=float(shifts[i]),
                              error_delta_GB=float(error_delta[i]),correction_shift_GB=float(correction_shifts[i])))
            unif=infer(model,x,uniform=True)[:,0]
            entropy=-(w*np.log(np.maximum(w,1e-30))).sum(1)/np.log(144)
            diag.append(dict(model=variant,seed=seed,ig_mean_abs_completeness_GB=float(np.abs(residual).mean()*data['std']),
              ig_max_abs_completeness_GB=float(np.abs(residual).max()*data['std']),
              ig64_mean_abs_completeness_GB=float(np.abs(res64).mean()*data['std']),
              ig32_64_mean_attribution_L1_GB=float(np.abs(attr[:16]-attr64).sum((1,2)).mean()*data['std']),
              attention_normalized_entropy_mean=float(entropy.mean()),
              attention_max_weight_mean=float(w.max(1).mean()),
              uniform_weight_prediction_shift_GB=float(np.abs(unif-p).mean()*data['std']),
              seconds=time.time()-t0))
            np.savez_compressed(RESULTS/f'xai_{variant}_s{seed}.npz',origins=origins,
              attention=w,ig=attr,ig_correction=correction_attr,occlusion=occ,inputs=x,baseline=profile,predictions=pred)
            print('XAI',variant,seed,'seconds',round(time.time()-t0,1),flush=True)
    pd.DataFrame(records).to_csv(RESULTS/'xai_per_origin.csv',index=False)
    xf=pd.DataFrame(records)
    xf.groupby(['model','method','replacement','k_blocks']).agg(
      mean_shift_GB=('prediction_shift_GB','mean'),mean_error_delta_GB=('error_delta_GB','mean'),mean_correction_shift_GB=('correction_shift_GB','mean')).reset_index().to_csv(RESULTS/'xai_summary.csv',index=False)
    pd.DataFrame(diag).to_csv(RESULTS/'xai_diagnostics.csv',index=False)
    pd.DataFrame(agreements).to_csv(RESULTS/'xai_rank_correlations.csv',index=False)
    stability=[]
    for variant in ['attention','bounded']:
        for a,b in itertools.combinations(SEEDS,2):
            for i,o in enumerate(origins):
                stability.append(dict(model=variant,seed_a=a,seed_b=b,origin=int(o),
                  rho=float(spearmanr(weights[(variant,a)][i],weights[(variant,b)][i]).statistic)))
    pd.DataFrame(stability).to_csv(RESULTS/'attention_seed_stability.csv',index=False)
    # Pair explanations against the random reference on exactly the same origins/seeds.
    # Aggregate repeats within origin, then bootstrap groups by UTC target day.
    xr=xf[xf.method=='random'];paired=[]
    for (variant,replacement,k),sub in xf[xf.method!='random'].groupby(['model','replacement','k_blocks']):
        ref=xr[(xr.model==variant)&(xr.replacement==replacement)&(xr.k_blocks==k)]
        for method,ss in sub.groupby('method'):
            joined=ss.merge(ref,on=['seed','origin'],suffixes=('_method','_random'))
            for measure in ['prediction_shift_GB','error_delta_GB','correction_shift_GB']:
                delta=joined[measure+'_method']-joined[measure+'_random']
                group=pd.DataFrame({'day':data['d'].timestamp.iloc[joined.origin].dt.floor('D').astype(str).to_numpy(),'delta':delta.to_numpy()})
                sums=group.groupby('day').delta.agg(['sum','count'])
                rng=np.random.default_rng(2026);sample=rng.integers(0,len(sums),size=(1000,len(sums)))
                boot=sums['sum'].to_numpy()[sample].sum(1)/sums['count'].to_numpy()[sample].sum(1)
                lo,hi=np.quantile(boot,[.025,.975]);paired.append(dict(model=variant,replacement=replacement,k_blocks=k,
                  method=method,measure=measure,delta_vs_random=float(delta.mean()),ci_low=float(lo),ci_high=float(hi),n_days=len(sums)))
    pd.DataFrame(paired).to_csv(RESULTS/'xai_paired_day_bootstrap.csv',index=False)

def figures(data,summary):
    FIG.mkdir(exist_ok=True);plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
    fig,ax=plt.subplots(figsize=(3.5,2.1));ax.plot(data['d'].timestamp,data['y'],lw=.35,color='#2563a6')
    for x in [data['audit']['train_end_exclusive'],data['audit']['val_end_exclusive']]:ax.axvline(data['d'].timestamp.iloc[x],ls='--',color='#c15b32')
    ax.set(ylabel='Volume (GB / interval)',xlabel='UTC date');ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'));fig.tight_layout();fig.savefig(FIG/'series.png');plt.close(fig)
    labels=['persistence','seasonal_day','seasonal_week','ridge','last_L144','uniform_L144','bounded_L144','attention_L144','attention_L288']
    pretty=['Persistence','Seasonal: day','Seasonal: week','Ridge','LSTM: last state','Uniform pooling','Bounded attn (24h)','Learned attn (24h)','Learned attn (48h)']
    fig,axes=plt.subplots(1,2,figsize=(7,3),sharey=True)
    for ax,h in zip(axes,[1,6]):
        sub=summary[summary.horizon==h].set_index('model').reindex(labels)
        ax.barh(np.arange(len(labels)),sub.mae_mean,color=['#8193a8']*4+['#3b82a0']*3+['#db7b39']*2)
        ax.errorbar(sub.mae_mean,np.arange(len(labels)),xerr=sub.mae_sd.fillna(0),fmt='none',ecolor='#17202a',capsize=2)
        ax.set_yticks(np.arange(len(labels)),pretty);ax.set(title=f'Horizon {h*10} min',xlabel='MAE (GB)')
    axes[0].invert_yaxis()
    fig.tight_layout();fig.savefig(FIG/'forecast_mae.png');plt.close(fig)
    pred=pd.read_csv(RESULTS/'pred_attention_L144_s42.csv');idx=np.arange(min(432,len(pred)))
    fig,ax=plt.subplots(figsize=(3.5,2.1));time=pd.to_datetime(pred.target_h1.iloc[idx],utc=True)
    ax.plot(time,pred.true_h1_GB.iloc[idx],label='Observed',color='#26364a',lw=1)
    ax.plot(time,pred.pred_h1_GB.iloc[idx],label='Attention, seed 42',color='#d47131',lw=.8)
    ax.set(ylabel='Volume (GB)',xlabel='First three test days (UTC)');ax.xaxis.set_major_locator(mdates.DayLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'));ax.legend(frameon=False,fontsize=7);fig.tight_layout();fig.savefig(FIG/'forecast_example.png');plt.close(fig)
    a=np.load(RESULTS/'xai_attention_s42.npz');b=np.load(RESULTS/'xai_bounded_s42.npz')
    fig,axes=plt.subplots(1,3,figsize=(7,2.5))
    for ax,w,title in zip(axes,[a['attention'],b['attention'],np.abs(a['ig'][:,:,0])],['Learned Attention','Bounded Attention','IG32 (provisional)']):
        w=w/(w.sum(1,keepdims=True)+1e-30);im=ax.imshow(w,aspect='auto',origin='lower',cmap='magma')
        ax.set(title=title,xlabel='History index (old to recent)');fig.colorbar(im,ax=ax,fraction=.04)
    axes[0].set_ylabel('96 fixed test origins');fig.tight_layout();fig.savefig(FIG/'attribution_heatmaps.png');plt.close(fig)
    sub=pd.read_csv(RESULTS/'xai_summary.csv');fig,axes=plt.subplots(1,2,figsize=(7,2.6))
    for ax,rep in zip(axes,['time_of_day','constant']):
        for method in ['attention','integrated_gradients','occlusion','recency','random']:
            ss=sub[(sub.model=='attention')&(sub.replacement==rep)&(sub.method==method)]
            label='IG32 (provisional)' if method=='integrated_gradients' else method.replace('_',' ')
            ax.plot(ss.k_blocks,ss.mean_shift_GB,marker='o',label=label,ms=3,ls='--' if method=='integrated_gradients' else '-')
        ax.set(title=rep.replace('_',' '),xlabel='Replaced 2-hour blocks',ylabel='Mean |prediction change| (GB)')
    axes[1].legend(fontsize=6,frameon=False);fig.tight_layout();fig.savefig(FIG/'perturbation.png');plt.close(fig)
    fig,axes=plt.subplots(2,3,figsize=(7,4.5))
    variants=['last_L144','uniform_L144','bounded_L144','attention_L144','attention_L288']
    for ax,variant in zip(axes.flat,variants):
        for seed in SEEDS:
            hist=pd.read_json(RESULTS/f'history_{variant}_s{seed}.json')
            ax.plot(hist.epoch,hist.train_mse,color='#2563a6',alpha=.6,lw=.8)
            ax.plot(hist.epoch,hist.val_mse,color='#cf6a32',alpha=.6,lw=.8)
        ax.set(title=variant.replace('_',' '),xlabel='Epoch',ylabel='Standardized MSE')
    axes.flat[-1].axis('off');axes.flat[-1].text(.05,.7,'Blue: training\nOrange: validation\nThree seeds per panel',fontsize=10)
    fig.tight_layout();fig.savefig(FIG/'training_curves.png');plt.close(fig)

if __name__=='__main__':
    torch.set_num_threads(4);data=prepare();summary=forecast_analysis(data);xai_analysis(data);figures(data,summary)
    save_json(RESULTS/'analysis_complete.json',{'status':'complete','forecast_rows':len(summary),'seeds':SEEDS,'xai_origins':96})
