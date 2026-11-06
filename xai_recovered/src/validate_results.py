"""Validate provenance, common targets, metrics and checkpoint/forecast consistency."""
import hashlib,json
import numpy as np
import pandas as pd
import torch
from experiment import ROOT,RESULTS,SEEDS,HORIZONS,prepare,arrays,Forecaster,infer,metric,save_json

def main():
    torch.set_num_threads(4);data=prepare();checks=[]
    manifest=json.loads((ROOT/'recovery_manifest.json').read_text())
    for item in manifest:
        assert hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest()==item['sha256']
    checks.append(f'All {len(manifest)} recovered source hashes match the recovery manifest.')
    hashes=json.loads((RESULTS/'protocol_source_hashes.json').read_text())
    assert hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()==hashes['PROTOCOL.md']
    assert hashlib.sha256((ROOT/'src/experiment.py').read_bytes()).hexdigest()==hashes['experiment.py']
    checks.append('Training protocol and experiment source match their frozen hashes.')
    metrics=[]
    for p in RESULTS.glob('metrics_*.json'):metrics.extend(json.loads(p.read_text()))
    assert len(metrics)==38
    expected_origins=data['idx']['test'];target=data['y'][expected_origins[:,None]+HORIZONS-1]
    negative=0
    prediction_files=sorted(RESULTS.glob('pred_*.csv'));assert len(prediction_files)==19
    for p in prediction_files:
        f=pd.read_csv(p);assert np.array_equal(f.origin_index,expected_origins)
        name=p.stem[5:];label,seed=name.rsplit('_s',1)
        for j,h in enumerate(HORIZONS):
            true=f[f'true_h{h}_GB'].to_numpy();pred=f[f'pred_h{h}_GB'].to_numpy()
            assert np.isfinite(pred).all() and np.allclose(true,target[:,j])
            negative+=int((pred<0).sum())
            expected=next(r for r in metrics if r['model']==label and r['seed']==int(seed) and r['horizon']==int(h))
            for key,value in metric(true,pred).items():assert np.isclose(value,expected[key],rtol=1e-8,atol=1e-8)
    checks.append('All 19 forecast files use identical 5,806 test origins and correct observed labels.')
    checks.append('All 38 MAE/RMSE/WAPE records recompute from saved per-origin forecasts.')
    maximum=0.
    checkpoints=list(RESULTS.glob('*_L*_s*.pt'));assert len(checkpoints)==15
    for p in checkpoints:
        ck=torch.load(p,map_location='cpu',weights_only=True);model=Forecaster(ck['pooling']);model.load_state_dict(ck['state_dict'])
        x,_=arrays(data,'test',ck['length']);ix=[0,len(x)//2,len(x)-1]
        pred=infer(model,x[ix])*data['std']+data['mean']
        saved=pd.read_csv(RESULTS/f'pred_{p.stem}.csv').iloc[ix]
        q=saved[['pred_h1_GB','pred_h6_GB']].to_numpy()
        error=float(np.abs(pred-q).max());maximum=max(maximum,error)
        assert error<.001
    checks.append(f'All 15 checkpoints reproduce three saved forecasts each within 0.001 GB (max {maximum:.8f} GB).')
    assert (RESULTS/'analysis_complete.json').exists()
    diag=pd.read_csv(RESULTS/'xai_diagnostics.csv');assert len(diag)==6 and np.isfinite(diag.select_dtypes('number')).all().all()
    xa=pd.read_csv(RESULTS/'xai_per_origin.csv');assert len(xa)==17280
    assert np.isfinite(xa[['prediction_shift_GB','error_delta_GB']]).all().all()
    checks.append('All six explanation runs and 17,280 per-origin perturbation records are present and finite.')
    pdf=ROOT/'paper/paper.pdf';assert pdf.exists() and pdf.stat().st_size>10000
    assert '@@' not in (ROOT/'paper/paper.tex').read_text()
    checks.append('Compiled PDF and fully populated editable manuscript are present.')
    checks.append(f'Negative raw test predictions across all model/horizon records: {negative}. Predictions were not clipped.')
    assert (RESULTS/'ig_convergence_followup.csv').exists()
    checks.append('Scientific limitation: IG numerical completeness fails in some cases; IG-based conclusions are explicitly provisional. Artifact integrity checks do not establish IG convergence.')
    report={'status':'artifact_checks_passed_with_ig_limitation','checks':checks,'max_checkpoint_discrepancy_GB':maximum,'negative_predictions':negative,'ig_status':'provisional_nonconverged'}
    save_json(RESULTS/'validation_report.json',report)
    (ROOT/'VALIDATION.md').write_text('# Validation\n\n'+ '\n'.join('- '+c for c in checks)+'\n\nVisual PDF review is recorded separately in STATUS.md.\n')
    print('\n'.join(checks))

if __name__=='__main__':main()
