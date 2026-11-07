from pathlib import Path
import ast,nbformat as n
root=Path(__file__).resolve().parents[1]; cells=[]
def md(s):cells.append(n.v4.new_markdown_cell(s))
def code(s):cells.append(n.v4.new_code_cell(s))
def inline(file,names):
 s=(root/'src'/file).read_text(); tree=ast.parse(s)
 return '\n\n'.join(ast.get_source_segment(s,x) for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name in names)
md('''# XAI traffic forecasting: 32-new-target replication

A complete analysis companion to the original training notebook. **This study reuses locked forecasters; it does not retrain them.** The original study used 32 sources, eight validation institutions and eight targets. This replication adds 32 previously unevaluated targets matched to the same 32 source anchors. Across both studies there are 80 unique institutions, within one ISP.

Read `PROTOCOL_REPLICATION.md`. Membership, timestamps, models and scientific code were locally hashed before new-target scoring. The original outcome was already known. This is not external preregistration, an independent ISP replication, or evidence of causal demand effects.

Run from this folder or its parent. Data and checkpoints are included. Ordinary execution reads completed batch results and reproduces local arithmetic, plots and an independent primary point estimate. The final cell provides optional full evaluation on a **copy**. Original model fitting remains documented in `../xai_cross_institution/XAI_Complete_Experiment.ipynb`.''')
code('''from pathlib import Path
import sys, os, json, hashlib, platform, time
os.environ.setdefault('OPENBLAS_NUM_THREADS','4')
ROOT=Path.cwd()
if not (ROOT/'PROTOCOL_REPLICATION.md').exists():
    candidates=[ROOT/'xai_replication_32',ROOT/'outputs/xai_replication_32']
    ROOT=next(p for p in candidates if (p/'PROTOCOL_REPLICATION.md').exists())
sys.path.insert(0,str(ROOT/'src'))
import numpy as np, pandas as pd, matplotlib.pyplot as plt, torch
from IPython.display import display, Markdown
from math import factorial
from torch import nn
from numpy.polynomial.legendre import leggauss
from data_common import windows
from benchmark_common import Predictor, MASKS, REMOVED, PERMUTATIONS, SHAPLEY_WEIGHTS, NODES, order
from neural_feasibility import Forecaster
plt.rcParams.update({'figure.dpi':110,'axes.spines.top':False,'axes.spines.right':False})
torch.set_num_threads(4)
def readjson(name):return json.loads((ROOT/'results'/name).read_text())
print(platform.platform(), platform.python_version(), 'Torch',torch.__version__)
print('Project:',ROOT)''')
md('## 1. Provenance and frozen design\nThe freeze records the unscored historical state. Completion is recorded separately; do not rewrite frozen manifests after execution.')
code('''freeze=readjson('PREEVALUATION_FREEZE.json')
display(freeze if 'files' not in freeze else {k:v for k,v in freeze.items() if k!='files'})
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items())
print('Verified frozen file hashes:',len(freeze['files']))
display(readjson('PREPARATION.json'))''')
code('''split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv')
pairs=pd.read_csv(ROOT/'MATCHED_PAIRS.csv')
display(split.head()); display(pairs.head())
assert split.id.nunique()==64
print(split.groupby('role').size() if 'role' in split else split.groupby('cohort').size())''')
md('## 2. Membership and matching\nTargets were hash-ranked within four original 2024 volume strata. Matching uses 2024 descriptors, not final forecast/XAI outcomes. The old targets and 12 development institutions were excluded. Source anchors are reused, so old and new estimates are not pooled as independent replications.')
code('''display(pd.read_csv(ROOT/'UNUSED_ELIGIBLE_POOL_2024.csv').head())
print('Matching columns:',pairs.columns.tolist())
display(pairs.describe(include='all'))''')
code('''main_plan=pd.read_csv(ROOT/'results/SELECTION_MAIN_FROZEN.csv')
dense_plan=pd.read_csv(ROOT/'results/SELECTION_DENSE_FROZEN.csv')
availability=pd.read_csv(ROOT/'results/AVAILABILITY.csv')
assert set(zip(main_plan.id,main_plan.origin)) <= set(zip(dense_plan.id,dense_plan.origin))
print('Histories:',len(main_plan),'main;',len(dense_plan),'dense')
display(availability)
display(main_plan.groupby(['cohort','year']).size().rename('histories'))''')
code('''fig,ax=plt.subplots(figsize=(8,3));ax.hist(pairs.training_descriptor_distance,bins=12);ax.set(xlabel='2024 matching descriptor distance',ylabel='Matched pairs',title='Matching before target scoring');plt.show()''')
md('## 3. Inspect hourly data and eligible windows\nObserved zero traffic remains zero; missing values remain missing. Every input contains 168 usable hourly values. Both endpoint labels must be observed. The native coverage and artifact flags are part of the saved data, not inferred from XAI outputs.')
code('''case=main_plan.sort_values(['pair','year','cohort','origin']).iloc[0]
id0=int(case.id)
hourly=pd.read_csv(ROOT/f'data/institution_{id0}.csv.gz')
display(hourly.head());display(hourly.describe(include='all'))''')
code('''v=windows(ROOT/f'data/institution_{id0}.csv.gz')
print('Window fields:',list(v))
o=int(v['t'].get_loc(pd.Timestamp(case.origin)))
j=int(np.flatnonzero(v['o']==o)[0]);x=v['X'][j]
t=v['t'][o-167:o+1]
assert len(x)==168 and np.isfinite(x).all() and (x>=0).all()
fig,ax=plt.subplots(figsize=(11,3));ax.plot(t,x);ax.set(ylabel='Traffic (GB)',title=f'Frozen first planned case: institution {id0}');plt.show()''')
md('## 4. Locked forecasters and deployment semantics\nThe output includes log transformation, source normalization and nonnegative clipping. Attribution must explain this deployed function. Checkpoints are the original source-trained bytes. No target fitting occurs here.')
code('''display(readjson('LOCKED_MODEL_REFERENCE.json'))
models={kind:Predictor(kind,0 if kind=='ridge' else 42) for kind in ['ridge','dlinear','gru']}
display(pd.DataFrame({k:m(x) for k,m in models.items()},index=['h=1','h=6']).T)
for kind,m in models.items():
    print(kind,'torch parameters:',sum(p.numel() for p in m.net.parameters()),'buffer values:',sum(p.numel() for p in m.net.buffers()))''')
md('The following executable definitions expose the actual inference wrapper; the imported checkpoints remain fixed.')
code(inline('benchmark_common.py',{'RidgeModule','Predictor'}))
md('The neural architecture below is executable and identical to the locked implementation. No optimizer or fitting is run in this replication.')
code(inline('neural_feasibility.py',{'Forecaster'}))
md('## 5. Forecast performance: separate from explanation reliability\nMacro scores average seeds first. Different years have unequal availability. MASE compares absolute forecast error with the source-defined seasonal scale; values below one beat that scale, not every possible baseline.')
code('''forecast=pd.read_csv(ROOT/'results/forecast_macro.csv')
display(forecast)
plotdata=forecast.query("role=='target' and arm=='frozen'")
fig,ax=plt.subplots(figsize=(9,3.5))
names=['persistence','daily','weekly','ridge','dlinear','gru']; centers=np.arange(len(names))
for offset,(h,g) in zip([-.18,.18],plotdata.groupby('horizon')):ax.bar(centers+offset,g.set_index('model').loc[names].mase,.36,label=f'h={h}')
ax.set_yscale('log');ax.axhline(1,color='gray',ls=':');ax.set(xticks=centers,xticklabels=names,ylabel='Mean target MASE (log scale)',title='New targets: forecast endpoint accuracy');ax.legend();plt.xticks(rotation=30);plt.show()''')
code('''display(pd.read_csv(ROOT/'results/forecast_equal_institution_macro.csv'))
display(pd.read_csv(ROOT/'results/forecast_per_year_macro.csv'))''')
md('### Post-hoc MASE scale diagnostic\nAfter observing extreme macro MASE, this descriptive view retains all cases and the original 1e-9 GB floor. It does not replace the frozen mean MASE or change model selection. Institution 267 has a 2024 weekly scale of about 751 bytes; small absolute errors can therefore produce very large ratios.')
code('''distribution=pd.read_csv(ROOT/'results/forecast_distribution_diagnostic.csv')
display(distribution)
display(readjson('FORECAST_DIAGNOSTICS.json'))
from IPython.display import Image
display(Image(filename=str(ROOT/'figures/replication_forecast_scales.png')))''')
md('## 6. Exact seven-day Shapley allocations\nSeven groups represent the seven input days. Enumerating 128 coalitions gives exact Shapley values for the chosen replacement game. Efficiency is an arithmetic property, not evidence that the attribution is causal or operationally correct.')
code(inline('benchmark_common.py',{'games'}))
code('''profile=np.load(ROOT/'models/source_profile.npy')
how=t.day_of_week.to_numpy()*24+t.hour.to_numpy();r=profile[how]
model=Predictor('gru',42)
phi,occ,values,eff=games(model,x,r)
display(pd.DataFrame(phi.T,columns=['h=1 allocation GB','h=6 allocation GB'],index=[f'day {i+1}' for i in range(7)]))
print('Efficiency residual GB:',eff)
fig,ax=plt.subplots(figsize=(8,3));ax.bar(np.arange(7)-.17,phi[0],.34,label='h=1');ax.bar(np.arange(7)+.17,phi[1],.34,label='h=6');ax.axhline(0,color='gray',lw=.6);ax.set(xticks=range(7),xticklabels=range(1,8),xlabel='Input day, oldest to newest',ylabel='Shapley allocation (GB)');ax.legend();plt.show()''')
md('## 7. Independent replacement operators and ranking utility\nInterpolation and cyclic day rotation define controlled responses separately from the attribution reference. All 5,040 orders are enumerated to compute random-order and oracle utilities. Q=(U−R)/(O−R); it is undefined when the oracle gap is at most 1e−9 GB. Q can be negative and is not a probability.')
code(inline('benchmark_common.py',{'templates','response_game','quality'}))
code('''rows=[]
for op,tmp in templates(x).items():
    vv,random,oracle=response_game(model,x,tmp)
    for k,h in enumerate([1,6]):
        rank=order(abs(phi[k]),f'{id0}:{case.origin}:{h}')
        utility,q,gap=quality(vv,rank,random,oracle)
        rows.append(dict(operator=op,horizon=h,quality_q=q[k],utility_gb=utility[k],oracle_gap_gb=gap[k]))
display(pd.DataFrame(rows))''')
md('## 8. Integrated gradients: retain numerical failures\nQuadrature increases from 32 to 512 nodes. Acceptance requires both completeness and refinement tolerances. Rejected cases are retained in the numerical audit and excluded from accepted-IG ranking scores.')
code(inline('benchmark_common.py',{'integrated_gradients'}))
code('''ig,accepted,steps,error,change=integrated_gradients(model,x,r)
display(pd.DataFrame({'horizon':[1,6],'accepted':accepted,'nodes':steps,'completeness_error_gb':error,'L1_refinement_gb':change}))
display(pd.read_csv(ROOT/'results/ig_numerical_summary.csv'))''')
md('## 9. Effective denominators and missingness\nMore response queries do not create more independent institutions. Undefined Q and failed IG need explicit denominators. Outcome-dependent availability limits the population to which complete-case estimates apply.')
code('''exclusions=pd.read_csv(ROOT/'results/quality_exclusions.csv')
display(exclusions)
g=exclusions.query("arm=='frozen' and reference=='source_calendar' and method=='shapley'").groupby(['model','cohort'])[['records','defined']].sum()
g['defined_fraction']=g.defined/g.records;display(g)''')
md('## 10. Primary paired transfer contrast\nSeeds are averaged only with a complete seed set; source and target must share an origin. Equal weighting across two years and two operators precedes equal weighting across complete institution pairs. Independent inference units are institutions, not response queries.')
code('''paired=pd.read_csv(ROOT/'results/paired_quality.csv.gz')
primary=paired.query("model=='gru' and arm=='frozen' and horizon==1 and reference=='source_calendar' and method=='shapley'").copy()
cells=primary.groupby(['pair','year','operator']).delta.mean().unstack(['year','operator'])
complete_cells=cells.dropna()
independent_point=complete_cells.mean(axis=1).mean()
print('Complete pairs:',len(complete_cells),'independent point:',independent_point)
display(complete_cells)
fig,ax=plt.subplots(figsize=(9,3));ax.bar(complete_cells.index.astype(str),complete_cells.mean(axis=1));ax.axhline(0,color='black',lw=.7);ax.set(xlabel='Matched pair',ylabel='Target minus source Q',title='New-cohort complete pair means');plt.show()''')
md('## 11. Prespecified bootstrap and interval failure\nThe original pair/within-pair block bootstrap attempts exactly 2,000 draws. An interval requires at least four complete pairs and 1,000 valid draws. A missing interval is a failed inferential procedure; it is not evidence of no effect. No additional attempts are added after seeing the valid count.')
code(inline('analyze_replication.py',{'bootstrap'}))
code('''sensitivity=readjson('SENSITIVITY_RESULTS.json')
primary_report=sensitivity['main_original_pair_block']
assert np.isclose(independent_point,primary_report['mean'],rtol=0,atol=1e-12)
display(primary_report)
recomputed_primary=bootstrap(primary)
for k in ['mean','ci_low','ci_high']:assert np.isclose(recomputed_primary[k],primary_report[k],rtol=0,atol=1e-12)
assert recomputed_primary['bootstrap_valid']==primary_report['bootstrap_valid']
print('Recomputed all 2000 primary bootstrap attempts:',recomputed_primary)''')
md('## 12. Additional uncertainty analyses\nPair-only resampling conditions on the observed periods. Synchronized calendar-block resampling keeps common blocks across institutions. Both were specified before scoring, but remain sensitivity analyses and cannot replace a failed primary interval.')
code(inline('analyze_sensitivity.py',{'complete','sensitivities'}))
code('''display(sensitivity['main_sensitivity'])
print('Reused-case equality audit:',{k:v for k,v in sensitivity.items() if 'intersection' in k or 'reused_' in k})''')
md('## 13. Nested 16-to-64-origin comparison\nDense evaluation retains the original 16 origins, adds up to 48, and reuses their already computed rows. It uses frozen GRU checkpoints, source-calendar Shapley/occlusion/recency, no additional fitting and no dense IG. Compare both native and common-complete-pair panels; denominator changes can change the estimand.')
code('''budget=sensitivity['dense_budget_comparison']
display(pd.json_normalize(budget).T)
rows=[]
for item in budget:
    for key in ['main_original_pair_block','dense_original_pair_block','common_pair_main','common_pair_dense']:
        rows.append(dict(horizon=item['horizon'],analysis=key,**item[key]))
comparison=pd.DataFrame(rows);display(comparison)
fig,axes=plt.subplots(1,2,figsize=(11,3.5),sharey=True)
for ax,(h,g) in zip(axes,comparison.groupby('horizon')):
    ax.scatter(g['mean'],range(len(g)))
    for y,row in enumerate(g.itertuples()):
        if pd.notna(row.ci_low):ax.plot([row.ci_low,row.ci_high],[y,y],color='C0')
    ax.set(yticks=range(len(g)),yticklabels=g.analysis,title=f'h={h}',xlabel='Target minus source Q');ax.axvline(0,color='gray',ls=':')
plt.tight_layout();plt.show()''')
md('## 14. Secondary analyses\nReferences, horizons, models and calibration arms answer distinct questions. These contrasts are descriptive or secondary; no significant-looking contrast is promoted to primary.')
code('''display(pd.read_csv(ROOT/'results/secondary_quality_contrasts.csv'))
print('Available analysis tables:')
print('\\n'.join(p.name for p in sorted((ROOT/'results').glob('*.csv'))))''')
md('## 15. Validation and computational workload\nHashes protect the frozen inputs, model bytes and scientific code. Audit files separately test numerical arithmetic, saved outputs and independent calculations. A short training run can be valid for compact models; data and institution counts, coverage and effective sample size matter more than elapsed time alone.')
code('''display(readjson('FINAL_VALIDATION.json'))
display(readjson('DENSE_COMPLETE.json'))
for name in ['DENSE_VALIDATION.json','REPLICATION_COMPLETION.json']:
    if (ROOT/'results'/name).exists():display(readjson(name))''')
md('## 15b. Focused post-hoc conference checks\nThese analyses were specified after the original and new-cohort outcomes, then locally frozen before randomized-model outcomes. They preserve the two primary estimands. GRU h1/source-calendar is the limited scope. Read `conference_checks/PLAN.md` for the exact masks, seeds, metrics and conditional interpretation.')
code("""CHECKS=ROOT/'conference_checks'
comparison=json.loads((CHECKS/'results/EXPLAINER_COMPARISON.json').read_text())
display(pd.read_csv(CHECKS/'results/method_table.csv',header=[0,1],index_col=0))
display(pd.DataFrame(json.loads((CHECKS/'results/DENOMINATOR_CLARIFICATIONS.json').read_text())['counts']))
print('Exact random-order mean Q = 0 on informative response games. Cross-panel means use different populations.')""")
md('### Reconstruct the common-case absolute means\nAll required methods must have three defined seeds on identical cases. Panel A uses the main budget; panel B uses the original IG subset and accepted IG. Both operators are required within each retained institution-year. These available-period means are different from the complete-pair primary contrast.')
code("""saved=pd.read_csv(CHECKS/'results/explainer_macro.csv')
for panel,methods in [('A',['shapley','occlusion','recency']),('B',['shapley','ig','occlusion','recency'])]:
    common=pd.read_csv(CHECKS/f'results/common_cases_{panel}.csv.gz')
    cells=common.groupby(['id','cohort','year','operator'])[methods].mean().unstack('operator')
    cells=cells.dropna()
    years=pd.DataFrame({m:cells[m][['interpolation','rotation']].mean(axis=1) for m in methods}).reset_index()
    institutions=years.groupby(['id','cohort'])[methods].mean().reset_index()
    means=institutions.groupby('cohort')[methods].mean()
    for cohort in ['source','target']:
        for m in methods:
            expected=saved.query('panel==@panel and cohort==@cohort and method==@m').quality_q.iloc[0]
            assert np.isclose(means.loc[cohort,m],expected,atol=1e-12,rtol=0)
    display(means)
print('Both panels independently reconstructed.')""")
md('### Cascading learned-layer parameter sensitivity\nThe fixed control uses 126 timestamp-selected histories, three trained seeds and three reset replicates. Reset head, then GRU while keeping the same randomized head. The source buffers, reference, log/clipping/output and fixed last-input residual route remain. No threshold defines a pass. Comparisons condition on nonflat patterns common to both stages, with exclusions retained.')
code("""import copy
from scipy.stats import spearmanr
EPS=1e-9
"""+ '\n\n'.join(ast.get_source_segment((root/'conference_checks/src/parameter_control.py').read_text(),x) for x in ast.parse((root/'conference_checks/src/parameter_control.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name in {'pattern_metrics','randomize'}))
code("""# Actually regenerate one predeclared randomized model pair and verify saved tensors.
head_control,full_control=randomize(Predictor('gru',42),42,701)
for stage,net in [('head',head_control),('head_gru',full_control)]:
    checkpoint=torch.load(CHECKS/f'models/{stage}_42_701.pt',weights_only=True,map_location='cpu')
    assert all(torch.equal(net.net.state_dict()[k],v) for k,v in checkpoint['state'].items())
print('Head and cumulative GRU resets reproduce exactly; no fitting ran.')
task=pd.read_csv(CHECKS/'case_plan.csv').sort_values(['pair','year','cohort','origin']).iloc[0]
cv=windows(ROOT/f'data/institution_{int(task.id)}.csv.gz');co=int(cv['t'].get_loc(pd.Timestamp(task.origin)))
cx=cv['y'][co-167:co+1];ct=cv['t'][co-167:co+1];cr=profile[ct.day_of_week*24+ct.hour]
trained_phi,*_=games(Predictor('gru',42),cx,cr)
random_phi,*_=games(full_control,cx,cr)
distance,rho,_,_=pattern_metrics(trained_phi[0],random_phi[0])
records=pd.read_csv(CHECKS/'results/parameter_records.csv.gz')
record=records.query('id==@task.id and year==@task.year and origin==@task.origin and seed==42 and replicate==701 and stage=="head_gru"').iloc[0]
assert np.isclose(distance,record.pattern_distance,atol=1e-12,equal_nan=True)
assert np.isclose(rho,record.rank_spearman,atol=1e-12,equal_nan=True)
print({'fixed_first_case_pattern_distance':distance,'rank_similarity':rho,'flat_cases_stay_undefined':True})""")
code("""display(pd.read_csv(CHECKS/'results/control_macro.csv'))
display(Image(filename=str(CHECKS/'figures/parameter_sensitivity.png')))
for name in ['VALIDATION.json','INFORMATIVE_VALIDATION.json']:
    display(json.loads((CHECKS/'results'/name).read_text()))
freeze=json.loads((CHECKS/'FREEZE.json').read_text())
assert all(hashlib.sha256((CHECKS/p).read_bytes()).hexdigest()==h for p,h in freeze['files'].items())
print('Frozen extension computation files verified:',len(freeze['files']))""")
md('### Optional isolated rerun of conference checks only\nThis reruns the approximately 40-second control and existing-output comparison on a copy, without retraining or rerunning the entire primary benchmark. It reproduces already opened outcomes, not a new holdout. Delivered primary and control snapshots remain preserved.')
code("""RUN_CONFERENCE_CHECKS=False
if RUN_CONFERENCE_CHECKS:
    import shutil,subprocess
    target=ROOT.parent/'conference_check_reruns'/time.strftime('%Y%m%dT%H%M%S')
    shutil.copytree(ROOT,target)
    commands=['src/explainer_comparison.py','src/parameter_control.py','src/summarize_controls.py','src/validate_checks.py','src/report_checks.py','tools/report_denominators.py','tools/render_parameter_figure.py','tools/validate_informative_controls.py']
    for script in commands:
        subprocess.run([sys.executable,str(target/'conference_checks'/script)],cwd=target,check=True)
    print('Isolated post-hoc check reproduction:',target)
else:
    print('Using validated completed checks. No model refitting.')""")
md('## 16. Interpretation limits and original comparison\nThe original eight-target primary contrast was −0.0189 (nominal 95% interval −0.0891 to 0.0533; seven complete pairs). Keep that estimate separate. New target institutions improve within-network coverage, while the same ISP, source anchors and trained models remain shared. Do not claim causal truth, universal explainability, equivalence from a non-significant interval, or a new attribution method. Conference contribution is the controlled empirical audit and reproducible evidence.')
code('''summary=ROOT/'RESULTS_BRIEF.md'
if summary.exists():display(Markdown(summary.read_text()))''')
md('## 17. Optional complete evaluation on an isolated copy\nThis is opt-in because it recomputes many model queries. It never retrains. Preserve the delivered frozen snapshot. Historical freeze manifests remain unchanged; rerun outputs live in the copy. Exclude the copy from version control.')
code('''RUN_FULL_EVALUATION=False
if RUN_FULL_EVALUATION:
    import shutil, subprocess
    runroot=ROOT.parent/'replication_reruns'/time.strftime('%Y%m%dT%H%M%S')
    shutil.copytree(ROOT,runroot)
    for name in ['FINAL_VALIDATION.json','DENSE_VALIDATION.json','DENSE_COMPLETE.json','ATTRIBUTION_COMPLETE.json','SENSITIVITY_RESULTS.json','REPLICATION_COMPLETION.json','NOTEBOOK_EXECUTION.json']:
        (runroot/'results'/name).unlink(missing_ok=True)
    scripts=['src/evaluate_forecasts.py','src/evaluate_attributions.py','src/analyze_replication.py','src/validate_replication.py','src/evaluate_dense.py','src/analyze_sensitivity.py','tools/forecast_diagnostics.py','tools/validate_dense.py','tools/build_report.py']
    for script in scripts:
        subprocess.run([sys.executable,str(runroot/script)],cwd=runroot,check=True)
    print('Completed isolated run:',runroot)
else:
    print('Reading audited completed outputs; set the flag only to recompute on a copy.')''')
nb=n.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'XAI project (Python 3.11)','language':'python','name':'xai-project'},'language_info':{'name':'python','version':'3.11'}})
n.write(nb,root/'XAI_Replication_32.ipynb')
print(len(cells),'cells',sum(c.cell_type=='code' for c in cells),'code cells')
