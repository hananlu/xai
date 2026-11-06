from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy.stats import spearmanr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def rho(x,y):
 if np.ptp(x)==0 or np.ptp(y)==0:return np.nan
 return float(spearmanr(x,y).statistic)

def main():
 clean=pd.read_csv(ROOT/'results/clean_metrics.csv');r=pd.read_csv(ROOT/'results/stress_records.csv.gz');checks=pd.read_csv(ROOT/'results/numerical_checks.csv')
 # Deterministic tail repeated at each seed is a single condition, not three replicates.
 r=r[~((r.pattern=='tail')&(r.seed!=42))].copy()
 r['corrupt_abs_error_gb']=abs(r.corrupt_prediction_gb-r.target_gb)
 assert np.allclose(r.corrupt_abs_error_gb,pd.read_csv(ROOT/'results/stress_records.csv.gz').loc[r.index,'corrupt_abs_error_gb'])
 group=['id','model','horizon','pattern','replacement']
 cond=r.groupby(group).agg(mae_gb=('corrupt_abs_error_gb','mean'),clean_mae_gb=('clean_abs_error_gb','mean'),incremental_error_sd=('incremental_error_sd','mean'),abs_shift_sd=('abs_shift_sd','mean'),attribution_mass_fraction=('attribution_mass_fraction','mean'),mass_imputed_gb=('mass_imputed_gb','mean'),mass_mask_gb=('mass_mask_gb','mean')).reset_index()
 cond.to_csv(ROOT/'results/stress_by_institution.csv',index=False)
 macro=clean.groupby(['model','horizon'])[['mae_gb','rmse_gb','mase','negative_fraction']].mean().reset_index();macro.to_csv(ROOT/'results/clean_macro.csv',index=False)
 stressmacro=cond.groupby(['model','horizon','pattern','replacement'])[['incremental_error_sd','abs_shift_sd','attribution_mass_fraction']].mean().reset_index();stressmacro.to_csv(ROOT/'results/stress_macro.csv',index=False)
 corr=[]
 for keys,f in r.groupby(group):
  corr.append(dict(zip(group,keys))|dict(n=len(f),rho_attribution_vs_incremental_error=rho(f.attribution_mass_fraction.to_numpy(),f.incremental_error_sd.to_numpy()),rho_recency_vs_incremental_error=rho(f.recency_score.to_numpy(),f.incremental_error_sd.to_numpy()),rho_displacement_vs_incremental_error=rho(f.value_displacement_sd.to_numpy(),f.incremental_error_sd.to_numpy())))
 cor=pd.DataFrame(corr);cor.to_csv(ROOT/'results/diagnostic_associations.csv',index=False)
 cor.groupby(['model','horizon','replacement'])[['rho_attribution_vs_incremental_error','rho_recency_vs_incremental_error','rho_displacement_vs_incremental_error']].agg(['median','count']).to_csv(ROOT/'results/association_summary.csv')
 # Paired week-block bootstrap of mask augmentation - clean Ridge corruption loss.
 # Same weeks sampled for every institution. Conditional on these 12 related institutions, not a population CI.
 r['week']=pd.to_datetime(r.origin,utc=True).dt.strftime('%G-%V')
 w=r.groupby(['id','week','model','horizon','pattern','replacement']).incremental_error_sd.mean().unstack('model')
 w['delta']=w.ridge_mask_aug-w.ridge_clean;w=w.reset_index();cis=[];rng=np.random.default_rng(20261105)
 for keys,f in w.groupby(['horizon','pattern','replacement']):
  a=f.pivot(index='week',columns='id',values='delta');assert a.notna().all().all()
  means=np.array([a.to_numpy()[rng.integers(len(a),size=len(a))].mean() for _ in range(1000)])
  cis.append(dict(horizon=keys[0],pattern=keys[1],replacement=keys[2],paired_delta_error_sd=float(a.to_numpy().mean()),ci_low=float(np.quantile(means,.025)),ci_high=float(np.quantile(means,.975)),weeks=len(a)))
 pd.DataFrame(cis).to_csv(ROOT/'results/paired_week_bootstrap.csv',index=False)
 # Small scientific plots: scale-normalized error prevents large institutions dominating.
 fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
 names=['persistence','daily','weekly','ridge_clean','ridge_mask_aug']
 for ax,h in zip(axs,[1,6]):
  f=clean[clean.horizon==h]
  for j,name in enumerate(names):
   vals=f[f.model==name].mase.to_numpy();ax.scatter(np.full(len(vals),j),vals,s=15,alpha=.5);ax.plot([j-.2,j+.2],[np.median(vals)]*2,color='black')
  ax.set_xticks(range(5),['Last','Daily','Weekly','Ridge','Mask+aug'],rotation=25);ax.set_title(f'{h}-hour endpoint');ax.set_ylabel('Weekly-seasonal MASE (lower better)');ax.grid(axis='y',alpha=.2)
 fig.suptitle('Exploratory clean forecasts: 12 CESNET institutions');fig.savefig(ROOT/'figures/clean_mase.png',dpi=180);plt.close(fig)
 fig,axs=plt.subplots(2,2,figsize=(11,7),layout='constrained')
 for row,model in enumerate(['ridge_clean','ridge_mask_aug']):
  for col,h in enumerate([1,6]):
   ax=axs[row,col];a=stressmacro[(stressmacro.model==model)&(stressmacro.horizon==h)]
   for j,repl in enumerate(['zero','ffill','profile']):
    b=a[a.replacement==repl].set_index('pattern').reindex(['scattered','block','tail']);ax.bar(np.arange(3)+(j-1)*.24,b.incremental_error_sd,width=.23,label=repl)
   ax.axhline(0,color='black',lw=.7);ax.set_xticks(range(3),['Scattered','Block','Latest 6h']);ax.set_ylabel('Incremental MAE / training SD');ax.set_title(f'{model}, horizon {h}h');ax.grid(axis='y',alpha=.2)
 axs[0,0].legend();fig.suptitle('Six missing history hours: paired telemetry-loss stress test');fig.savefig(ROOT/'figures/stress_error.png',dpi=180);plt.close(fig)
 # Example failure mode: profile imputation has zero value attribution by construction.
 z=r[(r.model=='ridge_clean')&(r.replacement=='profile')]
 facts=dict(institutions=int(clean.id.nunique()),stress_records_unique_conditions=len(r),max_reconstruction_error_gb=float(checks.reconstruction_max_gb.max()),max_shift_identity_error_gb=float(checks.shift_identity_max_gb.max()),profile_clean_ridge_max_imputed_mass_gb=float(z.mass_imputed_gb.max()),profile_clean_ridge_nonzero_shift_fraction=float((z.abs_shift_sd>1e-10).mean()),profile_clean_ridge_positive_incremental_error_fraction=float((z.incremental_error_sd>0).mean()),reserved_outcomes_scored=False,bootstrap_scope='weeks conditional on selected same-network institutions; descriptive, multiple comparisons unadjusted')
 (ROOT/'results/PILOT_FACTS.json').write_text(json.dumps(facts,indent=2));print(macro.to_string(index=False));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
