"""Post-hoc reporting assets from the frozen study; no target refit or primary-endpoint change."""
from pathlib import Path
import json,sys
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from data_common import ROOT,windows
from benchmark_common import Predictor,games,integrated_gradients

plt.rcParams.update({'font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
BLUE='#2365A0';ORANGE='#C16B24';TEAL='#0D8175';GRAY='#87949D'

def save(fig,name):
 fig.savefig(ROOT/f'figures/paper_{name}.pdf',bbox_inches='tight')
 fig.savefig(ROOT/f'figures/paper_{name}.png',dpi=190,bbox_inches='tight');plt.close(fig)

def main():
 split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv'); data=[]
 for row in split.itertuples():
  d=pd.read_csv(ROOT/f'data/institution_{row.id}.csv.gz');y=d.n_bytes.to_numpy(float)/1e9
  usable=np.isfinite(y)&(y>=0)&d.complete_hour.to_numpy(bool)&~d.conservative_artifact_flag.to_numpy(bool)
  data.append(dict(id=int(row.id),role=row.role,slots=len(d),observed=int(np.isfinite(y).sum()),usable=int(usable.sum())))
 m=pd.read_csv(ROOT/'results/forecast_institution_macro.csv');selection=pd.read_csv(ROOT/'results/explanation_selection.csv');hist=pd.read_csv(ROOT/'results/training_history.csv')
 counts=pd.read_csv(ROOT/'results/forecast_metrics.csv').query("model=='ridge' and arm=='frozen' and horizon==1")
 training=json.loads((ROOT/'results/TRAINING_COMPLETE.json').read_text());claim=json.loads((ROOT/'results/NUMERIC_CLAIMS.json').read_text())
 # One provenance-driven case: earliest shared eligible target origin, pair3/year2025.
 case=selection.query("pair==3 and year==2025 and cohort=='target'").sort_values('origin').iloc[0]
 v=windows(ROOT/f'data/institution_{int(case.id)}.csv.gz');o=int(v['t'].get_loc(pd.Timestamp(case.origin)));ix=int(np.flatnonzero(v['o']==o)[0]);x=v['X'][ix];y=v['Y'][ix]
 times=v['t'][o-167:o+1];how=times.day_of_week.to_numpy()*24+times.hour.to_numpy();profile=np.load(ROOT/'models/source_profile.npy')
 refs={'Source calendar':profile[how],'History hour median':np.tile(np.median(x.reshape(7,24),axis=0),7)}
 model=Predictor('gru',42);local={};numeric=[]
 for ref,r in refs.items():
  phi,occ,game,err=games(model,x,r);ig,accepted,nodes,igerr,change=integrated_gradients(model,x,r)
  local[ref]=(phi,ig,accepted)
  for k,h in enumerate([1,6]):numeric.append(dict(reference=ref,horizon=h,shapley_efficiency_error_gb=float(err[k]),ig_accepted=bool(accepted[k]),ig_nodes=int(nodes[k]),ig_completeness_error_gb=float(igerr[k])))
 # Dataset availability and learning curves.
 fig,axs=plt.subplots(1,3,figsize=(7.2,2.45),layout='constrained',gridspec_kw={'width_ratios':[1,1.1,1.1]})
 avail=counts.query("role=='target'").pivot(index='id',columns='year',values='n').reindex(columns=[2025,2026]);arr=avail.fillna(0).to_numpy()
 im=axs[0].imshow(arr,aspect='auto',vmin=0,vmax=320,cmap='Blues')
 axs[0].set_yticks(range(len(avail)),avail.index);axs[0].set_xticks([0,1],['2025','2026']);axs[0].set_ylabel('Target institution ID');axs[0].set_title('(a) Eligible forecast origins')
 for i in range(arr.shape[0]):
  for j in range(2):axs[0].text(j,i,str(int(arr[i,j])) if arr[i,j] else 'none',ha='center',va='center',fontsize=7,color='white' if arr[i,j]>200 else 'black')
 for ax,kind,label in zip(axs[1:],['dlinear','gru'],['(b) DLinear','(c) GRU']):
  for (seed,lr),g in hist.query('kind==@kind').groupby(['seed','lr']):ax.plot(g.epoch,g.validation_macro_log_mae,lw=.9,label=f'{seed}, {lr:g}')
  ax.set_title(label);ax.set_xlabel('Epoch');ax.set_ylabel('Validation log-MAE');ax.legend(fontsize=6,frameon=False)
 save(fig,'coverage_learning')
 # Equal available institution-year macro, unlike an unequal silent aggregation.
 names=['persistence','daily','weekly','ridge','dlinear','gru'];labels=['Last','Daily','Weekly','Ridge','DLinear','GRU'];colors=[GRAY]*3+[BLUE,TEAL,ORANGE]
 fig,axs=plt.subplots(1,2,figsize=(7.2,2.65),layout='constrained')
 for ax,h in zip(axs,[1,6]):
  g=m.query("role=='target' and arm=='frozen' and horizon==@h")
  mean=g.groupby('model').mase.mean().reindex(names)
  ax.bar(range(6),mean,color=colors,alpha=.65)
  for j,name in enumerate(names):
   a=g.query('model==@name').mase.to_numpy();ax.scatter(j+np.linspace(-.17,.17,len(a)),a,s=9,c='black',alpha=.6,zorder=4)
  ax.set_xticks(range(6),labels,rotation=25);ax.set_ylabel('MASE');ax.set_title(f'{h}h endpoint; dots = institution-year cells');ax.grid(axis='y',alpha=.15)
 save(fig,'forecast')
 # Real local-case history and accepted signed allocations, references explicit.
 fig=plt.figure(figsize=(7.2,3.5),layout='constrained');gs=fig.add_gridspec(2,2,height_ratios=[1,1.15]);ax=fig.add_subplot(gs[0,:])
 ax.plot(range(168),x,color='black',lw=.8,label='Observed history')
 for (name,r),c in zip(refs.items(),[BLUE,ORANGE]):ax.plot(range(168),r,lw=.8,label=name,color=c,alpha=.85)
 for boundary in range(24,168,24):ax.axvline(boundary,c='gray',alpha=.15)
 ax.set_xlabel('History hour (oldest to newest)');ax.set_ylabel('GB');ax.legend(loc='upper right',ncol=3,fontsize=6)
 for j,ref in enumerate(refs):
  ax=fig.add_subplot(gs[1,j]);phi,ig,accepted=local[ref];pos=np.arange(7)
  ax.bar(pos-.17,phi[0],.34,color=BLUE,label='Exact group Shapley')
  if accepted[0]:ax.bar(pos+.17,ig[0],.34,color=ORANGE,label='Accepted IG')
  else:ax.text(.02,.95,'IG numerically rejected',transform=ax.transAxes,va='top')
  ax.set_xticks(pos,[f'D{i+1}' for i in pos]);ax.set_ylabel('Signed h1 credit (GB)');ax.set_title(ref);ax.axhline(0,c='gray',lw=.6);ax.legend(fontsize=6)
 save(fig,'local_case')
 # Primary components, nominal interval and descriptive leave-one-pair-out (post-hoc).
 p=pd.read_csv(ROOT/'results/primary_complete_pair_cells.csv');by=p.groupby('pair').delta.mean();loo=(by.sum()-by)/(len(by)-1)
 fig,axs=plt.subplots(1,3,figsize=(7.2,2.5),layout='constrained',gridspec_kw={'width_ratios':[1.2,1,1]})
 for op,dx,c,marker in [('interpolation',-.08,BLUE,'o'),('rotation',.08,ORANGE,'s')]:
  z=p.query('operator==@op');axs[0].scatter(z['pair']+dx,z.delta,s=22,c=c,marker=marker,label=op)
 axs[0].axhline(0,c='gray',lw=.7);axs[0].set_xticks(by.index);axs[0].set_xlabel('Complete matched pair');axs[0].set_ylabel('Target - source Q');axs[0].legend(frameon=False,fontsize=6);axs[0].set_title('(a) Operator components')
 z=claim['primary'];axs[1].errorbar([z['mean']],[0],xerr=[[z['mean']-z['ci_low']],[z['ci_high']-z['mean']]],fmt='o',capsize=4,c=BLUE)
 axs[1].axvline(0,c='gray',ls='--',lw=.7);axs[1].set_yticks([0],['Primary']);axs[1].set_xlabel('Difference with nominal 95% CI');axs[1].set_title('(b) Frozen endpoint')
 axs[2].scatter(loo.values,range(len(loo)),c=GRAY,s=18);axs[2].axvline(z['mean'],c=BLUE,lw=.8,label='All seven pairs');axs[2].axvline(0,c='gray',ls='--',lw=.7)
 axs[2].set_yticks(range(len(loo)),[f'omit {k}' for k in loo.index]);axs[2].set_xlabel('Leave-one-pair-out point');axs[2].set_title('(c) Descriptive sensitivity')
 save(fig,'primary_sensitivity')
 # Twelve original exploratory contrasts as a forest plot.
 sec=pd.read_csv(ROOT/'results/secondary_quality_contrasts.csv');fig,axs=plt.subplots(1,2,figsize=(7.2,2.65),layout='constrained')
 for ax,ref,label in zip(axs,['source_calendar','history_hour_median'],['Source calendar','History hour median']):
  z=sec.query('reference==@ref').sort_values(['model','horizon']).reset_index(drop=True);pos=np.arange(len(z))
  ax.errorbar(z['mean'],pos,xerr=np.vstack([z['mean']-z.ci_low,z.ci_high-z['mean']]),fmt='o',capsize=3,c=BLUE,ms=3)
  ax.set_yticks(pos,[f'{a.model} {a.horizon}h' for a in z.itertuples()]);ax.axvline(0,c='gray',ls='--',lw=.7);ax.set_xlabel('Target - source Q');ax.set_title(label)
 save(fig,'secondary_forest')
 # Numerical audit with denominators, no percent-only denominator ambiguity.
 ig=pd.read_csv(ROOT/'results/ig_numerical_summary.csv');settings=[('source_calendar',1),('source_calendar',6),('history_hour_median',1),('history_hour_median',6)];kinds=['ridge','dlinear','gru'];rates=np.empty((3,4))
 fig,ax=plt.subplots(figsize=(3.45,2.35),layout='constrained')
 for i,kind in enumerate(kinds):
  for j,(ref,h) in enumerate(settings):
   row=ig[(ig.model==kind)&(ig.reference==ref)&(ig.horizon==h)].iloc[0];rates[i,j]=row.accepted/row.cases
 im=ax.imshow(rates,aspect='auto',vmin=0,vmax=1,cmap='Blues')
 for i,kind in enumerate(kinds):
  for j,(ref,h) in enumerate(settings):
   row=ig[(ig.model==kind)&(ig.reference==ref)&(ig.horizon==h)].iloc[0];ax.text(j,i,f'{int(row.accepted)}/{int(row.cases)}\n{100*rates[i,j]:.1f}%',ha='center',va='center',fontsize=6.5,color='white')
 ax.set_xticks(range(4),['calendar\n1h','calendar\n6h','history\n1h','history\n6h']);ax.set_yticks(range(3),['Ridge','DLinear','GRU']);ax.set_title('Accepted IG checks / all checks');save(fig,'ig_audit')
 # Matched common cases for IG and Shapley, three defined seeds per origin/operator.
 q=pd.concat([pd.read_csv(p) for p in sorted((ROOT/'results').glob('quality_*.csv.gz'))],ignore_index=True)
 z=q.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method in ['shapley','ig']")
 key=['id','seed','year','origin','cohort','operator'];common=z.pivot_table(index=key,columns='method',values='quality_q').dropna(subset=['shapley','ig']).reset_index();sk=['id','year','origin','cohort','operator'];common=common[common.groupby(sk).seed.transform('nunique')==3];cs=common.groupby(sk)[['shapley','ig']].mean().reset_index();cm=cs.groupby(['id','year','cohort'])[['shapley','ig']].mean().reset_index()
 fig,ax=plt.subplots(figsize=(3.45,2.65),layout='constrained')
 for cohort,c in [('source',BLUE),('target',ORANGE)]:
  z=cm.query('cohort==@cohort');ax.scatter(z.shapley,z.ig,c=c,s=18,label=cohort)
 lo=min(cm.shapley.min(),cm.ig.min());hi=max(cm.shapley.max(),cm.ig.max());ax.plot([lo,hi],[lo,hi],c='gray',ls='--',lw=.8);ax.set_xlabel('Shapley mean Q, common cases');ax.set_ylabel('IG mean Q, common cases');ax.legend(frameon=False);save(fig,'common_cases')
 # Summary includes exact sample units and workload, not inflated independent N.
 timing=json.loads((ROOT/'results/FULL_RUN_TIMINGS.json').read_text())
 times={name:item['runtime_seconds'] for name,item in timing.items()}
 total=json.loads((ROOT/'results/FULL_NOTEBOOK_RUN.json').read_text())['seconds'];times['diagnostics_analysis_and_overhead']=total-sum(times.values());times['total']=total
 facts=dict(reporting_only=True,new_analyses_posthoc=['leave-one-pair-out descriptive sensitivity','common-accepted-case visualization'],all_primary_decisions_unchanged=True,
  observed_hourly_values=sum(r['observed'] for r in data),hourly_grid_slots=sum(r['slots'] for r in data),usable_hourly_values=sum(r['usable'] for r in data),source_training_windows=training['source_windows'],source_windows_per_epoch=32*1024,neural_training_fits=len(hist.groupby(['kind','seed','lr'])),neural_epochs_all_fits=len(hist),neural_sample_exposures_all_fits=int(len(hist)*32*1024),forecast_origins_by_cohort=counts.groupby('role').n.sum().astype(int).to_dict(),target_institution_year_cells=len(counts.query("role=='target'")),explanation_origins_per_fit=len(selection),ig_history_origins_per_fit=int(selection.ig.sum()),complete_primary_pairs=claim['primary']['pairs'],parameter_counts={'ridge':338,'dlinear':676,'gru':3426},local_case=dict(id=int(case.id),pair=int(case.pair),year=int(case.year),origin=str(case.origin),observed_gb=y.tolist(),prediction_gb=model(x).tolist(),numerics=numeric),loo_points={str(k):float(v) for k,v in loo.items()},common_case_operator_seed_rows=len(common),common_case_origins_after_seed_average=len(cs),common_case_institution_year_cells=len(cm),runtime_seconds=times)
 (ROOT/'results/PAPER_REVISION_FACTS.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
