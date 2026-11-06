"""Record completion after scientific audits and real notebook execution; no model or estimator changes."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def main():
 def read(n):return json.loads((ROOT/'results'/n).read_text())
 audit=read('FINAL_VALIDATION.json');dense=read('DENSE_VALIDATION.json');nb=read('NOTEBOOK_EXECUTION.json');assert audit['status']==dense['status']==nb['status']=='pass'
 claims=read('NUMERIC_CLAIMS.json');sens=read('SENSITIVITY_RESULTS.json');split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');old=pd.read_csv(ROOT.parent/'xai_cross_institution/INSTITUTION_SPLIT.csv')
 newtargets=set(split.query("role=='target'").id);assert not newtargets&set(old.id);assert len(set(old.id)|set(split.id))==80
 completion=dict(status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),new_target_institutions=len(newtargets),new_targets_disjoint_from_all_original_institutions=True,total_unique_institutions_both_studies=80,source_anchors_reused=True,source_models_refitted=False,independent_network_replication=False,primary=claims['primary'],main_quality_records=claims['quality_records'],main_ig_cases=claims['ig_cases'],main_ig_failed=claims['ig_failed'],prediction_rows=audit['details']['prediction_rows'],main_xai_seconds=read('ATTRIBUTION_COMPLETE.json')['runtime_seconds'],forecast_seconds=read('FORECAST_EVALUATION.json')['runtime_seconds'],dense_xai_seconds=read('DENSE_COMPLETE.json')['runtime_seconds'],notebook=nb,scientific_audits_pass=True,scientific_amendments=[],post_hoc_descriptive_diagnostics=['All-cell forecast MASE scale/median diagnostic; no changes to metrics, floor, model or membership.'],frozen_input_files=len(read('PREEVALUATION_FREEZE.json')['files']))
 (ROOT/'results/REPLICATION_COMPLETION.json').write_text(json.dumps(completion,indent=2))
 p=ROOT/'README.md';s=p.read_text();header=f"""# Completed replication — 7 November 2026

32 new targets, 80 unique institutions across both studies. The main result uses {claims['primary']['pairs']} complete pairs: ΔQ {claims['primary']['mean']:.4f}, nominal 95% interval [{claims['primary']['ci_low']:.4f}, {claims['primary']['ci_high']:.4f}], {claims['primary']['bootstrap_valid']}/2,000 valid draws. It establishes neither systematic degradation nor equivalence. The original reference-specific zero-excluding secondary pattern does not recur here.

Start with [the executed notebook](XAI_Replication_32.ipynb), [results and every sensitivity](RESULTS_BRIEF.md), [research position](RESEARCH_POSITION.md), and [notebook guide](NOTEBOOK_GUIDE.md). The notebook has {nb['cells']} cells, {nb['code_cells']} code cells, {nb['embedded_pngs']} embedded plots and zero error outputs. All scientific/dense audits passed. The combined paper and editable presentation are in the sibling `xai_cross_institution` folder. Data attribution and the distinction between frozen analysis and later diagnostics are documented separately.

No new model fitting occurred. Main XAI: {completion['main_xai_seconds']/60:.1f} minutes; added dense XAI: {completion['dense_xai_seconds']/60:.1f} minutes on the local four-thread CPU. Runtime describes this workload, not scientific validity or independent sample size.

---

"""
 if not s.startswith('# Completed replication'):p.write_text(header+s)
 p=ROOT/'RESEARCH_POSITION.md';s=p.read_text().replace('The main replication evaluation is complete. The density and uncertainty sensitivities must still be read with their own final audit before drawing the combined conclusion.','The main evaluation, prespecified density/uncertainty sensitivities, independent audits and real-kernel notebook execution are complete. Read all fixed estimates and valid-draw counts in RESULTS_BRIEF.md and SENSITIVITY_RESULTS.json.');p.write_text(s)
 print(json.dumps(completion,indent=2))
if __name__=='__main__':main()
