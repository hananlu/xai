"""Development-only metric calibration, with a nonlinear estimand counterexample."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1];V2=ROOT.parent/'xai_research_v2'
GROUPS=7;B=24;SEED=20261105
MASKS=((np.arange(2**GROUPS)[:,None]>>np.arange(GROUPS))&1).astype(float)

def evaluate(X,checkpoint):
 return ((X-float(checkpoint['mu']))/float(checkpoint['sigma']))@checkpoint['coef'].T*float(checkpoint['sigma'])+checkpoint['intercept']*float(checkpoint['sigma'])+float(checkpoint['mu'])

def main():
 manifest=json.loads((ROOT/'SPLIT_MANIFEST.json').read_text());rows=[];sources=[];rng=np.random.default_rng(SEED)
 for ident in manifest['development_ids']:
  p=V2/f'data/institution_{ident}.csv.gz';d=pd.read_csv(p);t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));y=d.n_bytes.to_numpy(float)/1e9
  path=V2/f'results/model_{ident}_ridge_clean.npz';m=np.load(path);orig=m['pilot_origins'];take=np.unique(np.linspace(0,len(orig)-1,32,dtype=int));orig=orig[take]
  X=np.stack([y[o-167:o+1] for o in orig]);hours=t.day_of_week.to_numpy()*24+t.hour.to_numpy();R=np.stack([m['profile'][hours[o-167:o+1]] for o in orig])
  # Query the saved function on all explicit input coalitions, rather than deriving responses from the tested contributions.
  all_x=R[:,None,:]+np.repeat(MASKS,B,axis=1)[None,:,:]*(X-R)[:,None,:]
  values=evaluate(all_x.reshape(-1,168),m).reshape(len(orig),128,2);baseline=evaluate(R,m);truth=values-baseline[:,None,:]
  pred=evaluate(X,m)
  for k,h in enumerate([1,6]):
   exact=((X-R)*m['coef'][k]).reshape(len(orig),GROUPS,B).sum(2)
   attribution={'exact_linear':exact,'uniform_complete':np.repeat((pred[:,k]-baseline[:,k])[:,None]/GROUPS,GROUPS,axis=1),'reversed_complete':exact[:,::-1],'permuted_complete':np.stack([rng.permutation(v) for v in exact]),'recency_complete':np.column_stack([np.zeros((len(orig),GROUPS-1)),pred[:,k]-baseline[:,k]])}
   for method,phi in attribution.items():
    error=phi@MASKS.T-truth[:,:,k];complete=abs(phi.sum(1)-(pred[:,k]-baseline[:,k]));denom=abs(exact).sum(1);valid=denom>1e-9
    for i in range(len(orig)):
     a=abs(phi[i]);b=abs(exact[i]);rho=float(spearmanr(a,b).statistic) if np.ptp(a)>0 and np.ptp(b)>0 else None
     rows.append(dict(id=ident,origin=str(t[orig[i]]),horizon=h,method=method,completeness_error_gb=float(complete[i]),coalition_max_error_gb=float(abs(error[i]).max()),coalition_nmae=float(abs(error[i]).mean()/denom[i]) if valid[i] else np.nan,rank_alignment=rho))
  sources.append(dict(id=ident,data_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checkpoint_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 f=pd.DataFrame(rows);f.to_csv(ROOT/'results/metric_calibration_cases.csv',index=False)
 summary=f.groupby('method').agg(cases=('id','size'),completeness_max_gb=('completeness_error_gb','max'),coalition_max_error_gb=('coalition_max_error_gb','max'),coalition_nmae_mean=('coalition_nmae','mean'),rank_alignment_median=('rank_alignment','median')).reset_index();summary.to_csv(ROOT/'results/metric_calibration_summary.csv',index=False)
 exact=summary[summary.method=='exact_linear'].iloc[0];assert exact.coalition_max_error_gb<1e-9
 for name in ['uniform_complete','reversed_complete','permuted_complete']:
  row=summary[summary.method==name].iloc[0];assert row.completeness_max_gb<1e-9 and row.coalition_nmae_mean>0.005
 # Correct Shapley values for f(x)=x1*x2, baseline zero and x=(2,3): interactions invalidate partial-coalition additive reconstruction as a general correctness test.
 toy_values=np.array([0.,0.,0.,6.]);toy_masks=np.array([[0,0],[1,0],[0,1],[1,1]])
 shapley=np.array([.5*((toy_values[1]-toy_values[0])+(toy_values[3]-toy_values[2])),.5*((toy_values[2]-toy_values[0])+(toy_values[3]-toy_values[1]))])
 toy_pred=toy_masks@shapley;assert np.allclose(shapley,[3,3]) and abs(shapley.sum()-6)<1e-12
 facts=dict(status='passed',development_institutions=len(sources),windows_per_institution=32,horizons=[1,6],groups=7,group_width_hours=24,coalitions=128,exact_linear_max_error_gb=float(exact.coalition_max_error_gb),wrong_controls_pass_completeness=True,wrong_controls_detected_by_linear_coalition_check=True,nonlinear_counterexample=dict(function='x1*x2',input=[2,3],baseline=[0,0],exact_shapley=shapley.tolist(),coalition_values=toy_values.tolist(),additive_surrogate_predictions=toy_pred.tolist(),additive_surrogate_mae=float(abs(toy_pred-toy_values).mean()),interpretation='Exact Shapley remains correct. Additive reconstruction residual includes interaction effects, so it is not a universal correctness criterion.'),target_institutions_used=False,new_forecasters_trained=False,source_hashes=sources,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'results/METRIC_CALIBRATION.json').write_text(json.dumps(facts,indent=2));print(summary.to_string(index=False));print(json.dumps({k:v for k,v in facts.items() if k!='source_hashes'},indent=2))
if __name__=='__main__':main()
