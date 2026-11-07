"""Conditional paired-stage parameter-pattern diagnostics; no hypothesis tests."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
KEYS=['id','pair','cohort','year','origin','seed','replicate']
def main():
 q=pd.read_csv(ROOT/'results/parameter_records.csv.gz');b=pd.read_csv(ROOT/'results/trained_allocations.csv.gz');rows=[];insts=[];histories=[]
 for metric in ['pattern_distance','rank_spearman']:
  wide=q.pivot(index=KEYS,columns='stage',values=metric);common=wide.dropna(subset=['head','head_gru']).reset_index();common.to_csv(ROOT/f'results/common_control_{metric}.csv.gz',index=False,compression={'method':'gzip','mtime':0})
  long=common.melt(id_vars=KEYS,value_vars=['head','head_gru'],var_name='stage',value_name='value')
  hist=long.groupby(['id','cohort','year','origin','stage']).value.mean().reset_index();hist['metric']=metric;histories.append(hist)
  inst=hist.groupby(['id','cohort','stage']).value.mean().reset_index();inst['metric']=metric;insts.append(inst)
  for cohort in ['source','target']:
   for stage in ['head','head_gru']:
    raw=q[(q.cohort==cohort)&(q.stage==stage)];g=inst[(inst.cohort==cohort)&(inst.stage==stage)];cc=common[common.cohort==cohort]
    rows.append(dict(metric=metric,cohort=cohort,stage=stage,mean_equal_institutions=float(g.value.mean()) if len(g) else None,median_institution=float(g.value.median()) if len(g) else None,institutions=len(g),common_comparison_records=len(cc),common_histories=int(cc[['id','year','origin']].drop_duplicates().shape[0]),planned_comparison_records=len(raw),stage_metric_defined=int(raw[metric].notna().sum()),trained_nonflat=int((raw.trained_l1_gb>1e-9).sum()),randomized_nonflat=int((raw.randomized_l1_gb>1e-9).sum()),randomized_clipped=int((raw.rawlog<=0).sum())))
 pd.concat(insts).to_csv(ROOT/'results/control_institution_means.csv',index=False);pd.concat(histories).to_csv(ROOT/'results/control_history_means.csv',index=False);pd.DataFrame(rows).to_csv(ROOT/'results/control_macro.csv',index=False)
 result=dict(status='complete',post_hoc=True,scope='earliest frozen IG origin/pair/year/cohort; frozen GRU h1 source-calendar Shapley',trained_allocation_records=len(b),trained_nonflat_records=int((b.l1_gb>1e-9).sum()),trained_clipped_records=int((b.rawlog<=0).sum()),summaries=rows,common_stage_panels=True,aggregation='seed/replicate records within history, available years within institution, equal institutions',inference='descriptive conditional pattern sensitivity; no pass threshold/CI/superiority test; fixed residual retained')
 (ROOT/'results/PATTERN_SUMMARY.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
