"""Reporting-only counts before/after the already fixed complete-operator cell rule."""
from pathlib import Path
import json,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 facts=[]
 for panel in ['A','B']:
  d=pd.read_csv(ROOT/f'results/common_cases_{panel}.csv.gz');n=d.groupby(['id','cohort','year']).operator.nunique();good=n[n==2].reset_index()[['id','cohort','year']];used=d.merge(good,on=['id','cohort','year'],validate='many_to_one')
  for co in ['source','target']:
   v=used[used.cohort==co];facts.append(dict(panel=panel,cohort=co,common_cases_before_complete_operator_cell=int((d.cohort==co).sum()),used_history_operator_cases=len(v),histories_used=int(v[['id','year','origin']].drop_duplicates().shape[0]),institution_years_used=int((good.cohort==co).sum())))
 (ROOT/'results/DENOMINATOR_CLARIFICATIONS.json').write_text(json.dumps(dict(reporting_only=True,estimator_unchanged=True,counts=facts),indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
