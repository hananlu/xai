"""Post-feasibility numerical follow-up; preserves all original failure records."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy.integrate import quad_vec
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1];V2=ROOT.parent/'xai_research_v2'
def main():
 f=pd.read_csv(ROOT/'results/development_attribution_checks.csv');failed=f[~f.ig_accepted];m=np.load(ROOT/'results/development_ridge_log.npz');rows=[]
 for row in failed.itertuples():
  d=pd.read_csv(V2/f'data/institution_{row.id}.csv.gz');t=pd.DatetimeIndex(pd.to_datetime(d.time,utc=True));o=int(np.where(t==pd.Timestamp(row.origin))[0][0]);x=d.n_bytes.to_numpy(float)[o-167:o+1]/1e9;k=[1,6].index(row.horizon)
  r=(m['source_profile_gb'][(t.day_of_week.to_numpy()*24+t.hour.to_numpy())[o-167:o+1]] if row.reference=='source_calendar' else np.tile(np.median(x.reshape(7,24),axis=0),7))
  b=m['coef'][k];c=float(m['intercept'][k]);delta=x-r
  def z(a):return np.log1p(r+a*delta)@b+c
  def integrand(a):
   p=r+a*delta;q=z(a)
   return np.exp(q)*b*delta/(1+p) if q>0 else np.zeros(168)
  grid=np.linspace(0,1,2049);v=np.array([z(a) for a in grid]);roots=[]
  for i in np.where(v[:-1]*v[1:]<0)[0]:roots.append(float(brentq(z,grid[i],grid[i+1],xtol=1e-14)))
  first,e1=quad_vec(integrand,0.,1.,epsabs=1e-11,epsrel=1e-7,points=roots,limit=10000)
  second,e2=quad_vec(integrand,0.,1.,epsabs=1e-13,epsrel=1e-9,points=roots,limit=10000)
  contrast=float(np.expm1(max(z(1),0))-np.expm1(max(z(0),0)));err=float(abs(second.sum()-contrast));change=float(abs(second-first).sum());ok=err<=1e-8+1e-3*abs(contrast) and change<=1e-8+1e-3*abs(second).sum()
  rows.append(dict(id=row.id,origin=row.origin,horizon=row.horizon,reference=row.reference,original_ig_failed=True,breakpoint_hints=len(roots),completeness_error_gb=err,l1_refinement_change_gb=change,quad_error_estimate=float(e2),accepted=bool(ok)))
 out=pd.DataFrame(rows);out.to_csv(ROOT/'results/ig_adaptive_followup.csv',index=False)
 facts=dict(scope='post-hoc development numerical follow-up; original results retained',original_failed_cases=len(failed),followup_passed=int(out.accepted.sum()),followup_failed=int((~out.accepted).sum()),max_completeness_error_gb=float(out.completeness_error_gb.max()),max_l1_refinement_change_gb=float(out.l1_refinement_change_gb.max()),breakpoint_hints='2049-point sign-change scan and Brent root refinement; not a certification of every possible zero crossing',target_institutions_used=False,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (ROOT/'results/IG_ADAPTIVE_FOLLOWUP.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
