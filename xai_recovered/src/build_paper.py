"""Fill manuscript only from completed machine-readable experiment outputs."""
import json, subprocess, re
from pathlib import Path
import numpy as np
import pandas as pd
from experiment import ROOT, RESULTS

def f(v,n=2):return f'{float(v):.{n}f}'
def main():
    assert (RESULTS/'analysis_complete.json').exists(),'Run all experiment and analysis steps first.'
    summary=pd.read_csv(RESULTS/'forecast_summary.csv')
    assert len(summary)==18 and summary.n_runs.sum()==38
    lookup=summary.set_index(['model','horizon'])
    def row(model,h=1):return lookup.loc[(model,h)]
    a=row('attention_L144');a6=row('attention_L144',6);ridge=row('ridge');ridge6=row('ridge',6)
    base=row('persistence');base6=row('persistence',6)
    bounded=row('bounded_L144');unif=row('uniform_L144');last=row('last_L144')
    xa=pd.read_csv(RESULTS/'xai_summary.csv')
    diag=pd.read_csv(RESULTS/'xai_diagnostics.csv')
    corr=pd.read_csv(RESULTS/'xai_rank_correlations.csv')
    stability=pd.read_csv(RESULTS/'attention_seed_stability.csv')
    convergence=pd.read_csv(RESULTS/'ig_convergence_followup.csv')
    contrasts=pd.read_csv(RESULTS/'matched_model_contrasts.csv')
    ci=pd.read_csv(RESULTS/'paired_block_bootstrap.csv')
    xci=pd.read_csv(RESULTS/'xai_paired_day_bootstrap.csv')
    def xx(method,replacement='time_of_day',k=3,model='attention'):
        return xa[(xa.model==model)&(xa.method==method)&(xa.replacement==replacement)&(xa.k_blocks==k)].iloc[0]
    def contrast(a,b,h):return contrasts[(contrasts.a==a)&(contrasts.b==b)&(contrasts.horizon==h)&(contrasts.block==144)].iloc[0]
    def interval(r):return '['+f(r.ci_low,3)+', '+f(r.ci_high,3)+']'
    names={'persistence':'Persistence','seasonal_day':'Daily seasonal','seasonal_week':'Weekly seasonal',
           'ridge':'Ridge','last_L144':'LSTM last, 144','uniform_L144':'Uniform, 144',
           'bounded_L144':'Bounded attn., 144','attention_L144':'Learned attn., 144','attention_L288':'Learned attn., 288'}
    lines=[]
    for name,label in names.items():
        r=row(name);q=row(name,6)
        def cell(v,key):
            sd=v[key+'_sd']
            return f(v[key+'_mean'],3)+(r' $\pm$ '+f(sd,3) if pd.notna(sd) else '')
        lines.append(label+' & '+cell(r,'mae')+' & '+cell(r,'rmse')+' & '+cell(q,'mae')+' & '+cell(q,'rmse')+r' \\')
    table=r'''\begin{table*}[t]
\caption{Forecast errors in GB per interval on 5,806 common test origins. Recurrent values are mean $\pm$ sample standard deviation across three seeds. Deterministic baselines have one fit.}
\label{tab:forecast}\centering\small
\begin{tabular}{lrrrr}\toprule
 & \multicolumn{2}{c}{10 minutes} & \multicolumn{2}{c}{60 minutes}\\
Model & MAE & RMSE & MAE & RMSE\\\midrule
'''+ '\n'.join(lines)+r'''
\bottomrule\end{tabular}\end{table*}'''
    ar=contrast('attention_L144','ridge',1);au=contrast('attention_L144','uniform_L144',1)
    al=contrast('attention_L144','last_L144',1);ab=contrast('attention_L144','bounded_L144',1)
    context=contrast('attention_L288','attention_L144',1)
    best1=summary[summary.horizon==1].sort_values('mae_mean').iloc[0]
    best6=summary[summary.horizon==6].sort_values('mae_mean').iloc[0]
    result=(table+'\n'+r'\subsection{Predictive Performance}'+'\n'+
      f"Table~\\ref{{tab:forecast}} reports every condition, including negative comparisons. At 10 minutes, learned attention has MAE {f(a.mae_mean)} GB and RMSE {f(a.rmse_mean)} GB, versus {f(base.mae_mean)} and {f(base.rmse_mean)} GB for persistence. Its MAE skill relative to persistence is {f(a.mae_skill_vs_persistence_pct)}\\%. Ridge achieves MAE {f(ridge.mae_mean)} GB and RMSE {f(ridge.rmse_mean)} GB. At 60 minutes, learned-attention MAE is {f(a6.mae_mean)} GB, persistence {f(base6.mae_mean)} GB and Ridge {f(ridge6.mae_mean)} GB. The lowest observed mean MAE among the evaluated conditions belongs to {names[best1.model]} at 10 minutes and {names[best6.model]} at 60 minutes; this is a descriptive ranking, not a test-selected retraining decision.\n\n"+
      f"For learned attention minus Ridge at 10 minutes, the paired MAE difference is {f(ar.delta_mae_GB)} GB, with primary moving-block interval {interval(ar)} GB. Against last-state pooling it is {f(al.delta_mae_GB)} GB {interval(al)}, against uniform pooling {f(au.delta_mae_GB)} GB {interval(au)}, and against bounded attention {f(ab.delta_mae_GB)} GB {interval(ab)}. Negative differences favor learned attention. These contrasts average per-origin losses across seeds, not predictions from a seed ensemble.\n\n"+
      r'\subsection{Context and Temporal Robustness}'+'\n'+
      f"Extending learned-attention context from 144 to 288 steps changes one-step MAE by {f(context.delta_mae_GB)} GB, with interval {interval(context)} GB. Because both contexts share target timestamps, this comparison isolates context more cleanly than the archived runs, although optimization difficulty and model capacity remain possible mechanisms. Full 72/144/288-origin bootstrap sensitivity and test-period-third metrics are included in the artifact. The point estimates above are not substituted into the historical notebook result. Figures~\\ref{{fig:mae}} and~\\ref{{fig:prediction}} summarize errors and a fixed initial test episode.")
    da=diag[diag.model=='attention'];db=diag[diag.model=='bounded']
    ac=corr[(corr.model=='attention')&(corr.pair=='attention-ig')].rho.mean()
    ao=corr[(corr.model=='attention')&(corr.pair=='attention-occlusion')].rho.mean()
    stab=stability[stability.model=='attention'].rho.mean()
    top=xx('attention');ig=xx('integrated_gradients');random=xx('random');rec=xx('recency');occ=xx('occlusion')
    consttop=xx('attention','constant');constig=xx('integrated_gradients','constant');constrand=xx('random','constant')
    xc=xci[(xci.model=='attention')&(xci.replacement=='time_of_day')&(xci.k_blocks==3)&(xci.method=='attention')&(xci.measure=='prediction_shift_GB')].iloc[0]
    xaitext=(r'\subsection{Attention Concentration and Intervention}'+'\n'+
      f"Learned attention has mean normalized entropy {f(da.attention_normalized_entropy_mean.mean(),3)}, versus {f(db.attention_normalized_entropy_mean.mean(),3)} for the bounded scorer (one indicates uniform weights). Mean maximum weight is {f(da.attention_max_weight_mean.mean(),4)} for learned attention and {f(db.attention_max_weight_mean.mean(),4)} for bounded attention. Replacing learned weights with uniform weights while holding hidden states fixed changes the one-step output by {f(da.uniform_weight_prediction_shift_GB.mean())} GB on average. This measures sensitivity of the pooling path; it does not remove the residual contribution.\n\n"+
      r'\subsection{Input Attribution and Perturbation}'+'\n'+
      'IG32-based comparisons below are provisional because numerical completeness fails in some cases, as detailed in the numerical-reliability diagnostic. '+
      f"Across fixed origins and seeds, mean block-rank Spearman correlation is {f(ac,3)} for attention versus absolute IG and {f(ao,3)} for attention versus occlusion. Mean cross-seed attention-rank correlation is {f(stab,3)}. The 32-interval IG mean absolute completeness residual is {f(da.ig_mean_abs_completeness_GB.mean(),4)} GB, with maximum {f(da.ig_max_abs_completeness_GB.max(),4)} GB. On the 16-origin numerical check, the 64-interval mean residual is {f(da.ig64_mean_abs_completeness_GB.mean(),4)} GB. These numerical diagnostics are reported rather than assuming exact integration.\n\n"+
      f"Replacing the top three two-hour blocks with the training time-of-day profile yields mean prediction shifts of {f(top.mean_shift_GB)} GB for attention ranking, {f(ig.mean_shift_GB)} GB for IG, {f(occ.mean_shift_GB)} GB for occlusion, {f(rec.mean_shift_GB)} GB for recency and {f(random.mean_shift_GB)} GB for random ranking. Attention minus random has mean difference {f(xc.delta_vs_random)} GB and paired day-bootstrap interval {interval(xc)} GB. The corresponding change in absolute forecast error is {f(top.mean_error_delta_GB)} GB for attention and {f(ig.mean_error_delta_GB)} GB for IG; an error reduction after perturbation is possible and is not censored.\n\n"+
      f"Under constant-median replacement with the same rankings, mean shifts are {f(consttop.mean_shift_GB)} GB for attention, {f(constig.mean_shift_GB)} GB for IG and {f(constrand.mean_shift_GB)} GB for random order. Figure~\\ref{{fig:perturbation}} shows the full 1/3/6-block curves. Sensitivity to replacement choice and the distinction between hidden-state weights and full-model input attribution limit a literal interpretation of the heatmaps in Fig.~\\ref{{fig:heatmaps}}.")
    rd=json.loads((RESULTS/'ridge_decomposition.json').read_text())
    high=convergence[convergence.steps==2048]
    xaitext+='\n\n'+r'\subsection{Numerical Reliability of IG}'+'\n'+f"The planned IG checks reveal substantial numerical nonconvergence on some model/origin combinations. A secondary follow-up repeats integration at 128, 512 and 2,048 intervals on the same first 16 fixed origins for every model/seed. At 2,048 intervals, the largest absolute completeness residual is still {f(high.max_abs_completeness_GB.max())} GB, and {int((high.n_residual_above_0_1GB>0).sum())} of the six model/seed combinations contain at least one residual above 0.1 GB. Accordingly, IG32 rankings and all comparisons involving them are provisional, including correction-only IG correlations. We do not infer that attention is inferior to a numerically validated IG explanation. Occlusion, recency, random interventions and exact Ridge decomposition use direct model evaluations and do not depend on IG quadrature. The artifact retains the original IG outputs and all convergence diagnostics rather than silently replacing the planned method."
    corr_branch=corr[(corr.model=='attention')&(corr.pair=='attention-ig_correction')].rho.mean()
    xaitext+='\n\n'+r'\subsection{Secondary Residual-Path Diagnostic}'+'\n'+f"As a secondary diagnostic added while primary training was in progress, after initial baseline outputs were available, we separate the pooled correction from the persistence path. Subtracting the exact linear residual attribution from full-model IG gives correction-only IG. Its mean block-rank correlation with attention is {f(corr_branch,3)}. Under three-block training-profile replacement, correction-only mean shifts are {f(top.mean_correction_shift_GB)} GB for attention ranking, {f(ig.mean_correction_shift_GB)} GB for the original full-model IG ranking and {f(random.mean_correction_shift_GB)} GB for random ranking. These retain the original rankings; the IG deletion comparator is not re-ranked using correction-only attribution. This path-aware diagnostic avoids interpreting a mismatch in computational scope as proof that attention fails to describe its own branch. It introduces no refitting and does not replace the planned full-model audit."
    xaitext+='\n\n'+r'\subsection{Exploratory Linear Decomposition}'+'\n'+f"After inspecting baseline results, we added a post-hoc Ridge decomposition without refitting or changing the primary protocol. Relative to the training-mean reference, its prediction equals a constant plus the sum of lag-wise fitted contributions. The most recent lag has coefficient {f(rd['last_lag_coefficient_h1'],3)} at 10 minutes and {f(rd['last_lag_coefficient_h6'],3)} at 60 minutes. Reconstructed predictions agree with saved forecasts to within {f(rd['max_reconstruction_discrepancy_GB'],5)} GB. Coefficients and all per-origin contributions are included in the artifact. Exact reconstruction explains the fitted linear computation; correlated lag coefficients are not causal effects."
    absresult=(f"At 10 minutes, learned attention achieves mean MAE {f(a.mae_mean)} GB, compared with {f(ridge.mae_mean)} GB for Ridge and {f(base.mae_mean)} GB for persistence.")
    absxai=(f"For three replaced two-hour blocks, attention ranking produces a mean prediction change of {f(top.mean_shift_GB)} GB versus {f(random.mean_shift_GB)} GB for random ranking under the training-profile replacement. Integrated Gradients fails numerical completeness checks on some cases and is treated as provisional.")
    conclusion=(f"On identical held-out targets, learned attention obtains MAE {f(a.mae_mean)} GB at 10 minutes and {f(a6.mae_mean)} GB at 60 minutes, compared with Ridge MAEs of {f(ridge.mae_mean)} and {f(ridge6.mae_mean)} GB. The matched controls and direct perturbation diagnostics support assessing forecasting accuracy separately from the interpretation of attention weights. Numerical IG nonconvergence prevents treating its rankings as a validated reference here. The recovered-data artifact makes preprocessing, target eligibility and model comparisons inspectable, while preserving negative results and provenance limits.")
    template=(ROOT/'paper/template.tex').read_text()
    replacements={'ABSTRACT_RESULTS':absresult,'ABSTRACT_XAI':absxai,'RIDGE_ALPHA':str(int(json.loads((RESULTS/'metrics_ridge_s0.json').read_text())[0]['alpha'])),
                  'RESULTS':result,'XAI_RESULTS':xaitext,'CONCLUSION':conclusion}
    for key,value in replacements.items():template=template.replace('@@'+key+'@@',value)
    assert '@@' not in template
    # IEEE numbering follows first citation, and every bibliography item must be used.
    start=template.index('\\begin{thebibliography}')
    end=template.index('\\end{thebibliography}')
    body=template[:start]
    bib=template[start:end]
    matches=list(re.finditer(r'\\bibitem\{([^}]+)\}',bib))
    entries={m.group(1):bib[m.start():matches[i+1].start() if i+1<len(matches) else len(bib)].strip()
             for i,m in enumerate(matches)}
    order=list(dict.fromkeys(k.strip() for group in re.findall(r'\\cite\{([^}]+)\}',body) for k in group.split(',')))
    assert set(order)==set(entries),f'Citation mismatch: {set(order)^set(entries)}'
    template=body+'\\begin{thebibliography}{99}\n'+'\n'.join(entries[k] for k in order)+'\n'+template[end:]
    (ROOT/'paper/citation_audit.json').write_text(json.dumps({'reference_count':len(order),
      'all_references_cited':True,'numbering':'first-citation order','keys_in_order':order},indent=2))
    tex=ROOT/'paper/paper.tex';tex.write_text(template)
    for _ in range(2):
        subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=tex.parent,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    numeric={'ig_status':'provisional_nonconverged','attention_h1_mae_GB':float(a.mae_mean),'ridge_h1_mae_GB':float(ridge.mae_mean),
             'attention_h6_mae_GB':float(a6.mae_mean),'ig_shift_GB':float(ig.mean_shift_GB),
             'attention_shift_GB':float(top.mean_shift_GB),'random_shift_GB':float(random.mean_shift_GB)}
    (ROOT/'paper/numeric_claims.json').write_text(json.dumps(numeric,indent=2))
    print('Generated',tex.parent/'paper.pdf')

if __name__=='__main__':main()
