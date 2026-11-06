"""Post-hoc reporting diagnostic of extreme MASE; preserves every model, case and frozen metric."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':12})
ROOT=Path(__file__).resolve().parents[1]
def main():
 f=pd.read_csv(ROOT/'results/forecast_metrics.csv').query("role=='target' and arm=='frozen'");m=f.groupby(['model','id','year','horizon'])[['mae_gb','rmse_gb','mase','mase_denominator_gb']].mean().reset_index()
 summary=m.groupby(['model','horizon']).agg(cells=('mase','size'),mean_mase=('mase','mean'),median_mase=('mase','median'),max_mase=('mase','max'),mean_mae_gb=('mae_gb','mean')).reset_index();summary.to_csv(ROOT/'results/forecast_distribution_diagnostic.csv',index=False)
 top=f.sort_values('mase',ascending=False).head(20);top.to_csv(ROOT/'results/forecast_extreme_cells.csv',index=False)
 # Keep all cells on a log axis: no clipping, winsorizing or case removal.
 fig,axes=plt.subplots(1,2,figsize=(11,4),sharey=True)
 for ax,h in zip(axes,[1,6]):
  for kind,color in [('ridge','C0'),('dlinear','C1'),('gru','C2')]:
   z=m[(m.horizon==h)&(m.model==kind)];ax.scatter(z.mase_denominator_gb,z.mase,s=25,alpha=.65,label=kind,color=color)
  ax.set(xscale='log',yscale='log',xlabel='2024 weekly MASE scale (GB)',ylabel='Institution-year MASE',title=f'New targets: h={h}');ax.axhline(1,color='gray',ls=':');ax.grid(alpha=.15)
 axes[1].legend();fig.tight_layout();(ROOT/'figures').mkdir(exist_ok=True)
 for ext in ['pdf','png']:fig.savefig(ROOT/f'figures/replication_forecast_scales.{ext}',dpi=190,bbox_inches='tight')
 plt.close(fig)
 d=float(f[f.id==267].mase_denominator_gb.iloc[0]);facts=dict(post_hoc_descriptive=True,trigger='Extreme new-cohort macro MASE observed after main analysis; inspect all institution-year values without modifying metric or membership.',institution_267_weekly_scale_gb=d,institution_267_weekly_scale_bytes=d*1e9,max_single_seed_mase=float(f.mase.max()),all_target_cells_retained=True,original_metric_floor_unchanged=True,summary=summary.to_dict('records'))
 (ROOT/'results/FORECAST_DIAGNOSTICS.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
