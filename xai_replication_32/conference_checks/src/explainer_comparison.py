"""Post-hoc common-case absolute Q comparison, fixed by conference_checks/PLAN.md."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent
KEYS=['id','pair','cohort','year','origin','operator','ig_subset']
def summarize(case_scores,panel):
 long=case_scores.melt(id_vars=KEYS,var_name='method',value_name='quality_q')
 cells=long.groupby(['id','cohort','year','operator','method']).quality_q.mean().unstack('operator')
 cells=cells.reindex(columns=['interpolation','rotation']).dropna();year=cells.mean(axis=1).rename('quality_q').reset_index();inst=year.groupby(['id','cohort','method']).quality_q.mean().reset_index();inst['panel']=panel
 op=long.groupby(['id','cohort','year','operator','method']).quality_q.mean().reset_index().groupby(['id','cohort','operator','method']).quality_q.mean().reset_index().groupby(['cohort','operator','method']).quality_q.mean().reset_index();op['panel']=panel
 return inst,year,op

def main():
 use=KEYS+['model','seed','arm','horizon','reference','method','accepted','quality_q']
 q=pd.concat([pd.read_csv(PROJECT/f'results/quality_gru_{seed}.csv.gz',usecols=use) for seed in [42,123,2026]],ignore_index=True)
 q=q.query("arm=='frozen' and horizon==1 and reference=='source_calendar'").copy()
 assert not q.duplicated(KEYS+['method','seed']).any()
 a=q.groupby(KEYS+['method']).quality_q.agg(['mean','count']).reset_index();a.loc[a['count']!=3,'mean']=np.nan
 wide=a.pivot(index=KEYS,columns='method',values='mean');allinst=[];allyear=[];allop=[];facts=[]
 for panel,methods,subset in [('A',['shapley','occlusion','recency'],False),('B',['shapley','ig','occlusion','recency'],True)]:
  candidate=wide.reset_index();candidate=candidate[candidate.ig_subset] if subset else candidate
  valid=candidate.dropna(subset=methods)[KEYS+methods].copy();valid.to_csv(ROOT/f'results/common_cases_{panel}.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  inst,year,op=summarize(valid,panel);allinst.append(inst);allyear.append(year.assign(panel=panel));allop.append(op)
  for cohort in ['source','target']:
   cand=candidate[candidate.cohort==cohort];v=valid[valid.cohort==cohort];ii=inst[inst.cohort==cohort];yy=year[year.cohort==cohort]
   facts.append(dict(panel=panel,cohort=cohort,planned_history_operator_cases=len(cand),common_history_operator_cases=len(v),retained_institutions=int(ii.id.nunique()),retained_institution_years=int(yy[['id','year']].drop_duplicates().shape[0]),all_methods_three_seeds=True,all_required_operators_per_institution_year=True))
 inst=pd.concat(allinst,ignore_index=True);inst.to_csv(ROOT/'results/explainer_institution_means.csv',index=False);pd.concat(allyear,ignore_index=True).to_csv(ROOT/'results/explainer_institution_year_means.csv',index=False);pd.concat(allop,ignore_index=True).to_csv(ROOT/'results/explainer_operator_means.csv',index=False)
 macro=inst.groupby(['panel','cohort','method']).quality_q.mean().reset_index();macro.to_csv(ROOT/'results/explainer_macro.csv',index=False)
 result=dict(status='complete',post_hoc=True,methods=['shapley','ig','occlusion','recency'],scope='new cohort, main budget, frozen GRU h1/source-calendar',counts=facts,macro=macro.to_dict('records'),inference='descriptive; available-year-within-institution then equal institutions; no superiority test',random_order_q=0.0)
 (ROOT/'results/EXPLAINER_COMPARISON.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
