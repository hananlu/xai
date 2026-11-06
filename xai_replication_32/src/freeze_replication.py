"""One-time pre-performance freeze; refuses to overwrite an existing freeze."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
import pandas as pd
from data_common import ROOT

def main():
 out=ROOT/'results/PREEVALUATION_FREEZE.json'
 if out.exists():raise RuntimeError('Freeze already exists; retain it. Log amendments separately if implementation bugs occur.')
 member=json.loads((ROOT/'results/MEMBERSHIP_FREEZE.json').read_text())
 for rel,h in member['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h
 for name,h in member['model_hashes'].items():assert hashlib.sha256((ROOT/'models'/name).read_bytes()).hexdigest()==h
 split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');assert len(split)==64 and split.id.is_unique
 assert not set(split.query("role=='target'").id)&set(member['used_ids_excluded'])
 assert json.loads((ROOT/'results/PRESCORING_VALIDATION.json').read_text())['status']=='passed'
 assert json.loads((ROOT/'results/RESPONSE_ENDPOINT_CALIBRATION.json').read_text())['status']=='passed'
 assert not list((ROOT/'results').glob('quality_*.csv.gz')) and not (ROOT/'results/FORECAST_EVALUATION.json').exists()
 files=list((ROOT/'src').glob('*.py'))+list((ROOT/'models').glob('*'))+list((ROOT/'data').glob('*'))
 files += [ROOT/x for x in ['PROTOCOL_REPLICATION.md','INSTITUTION_SPLIT.csv','MATCHED_PAIRS.csv','UNUSED_ELIGIBLE_POOL_2024.csv','requirements-full.txt','results/MEMBERSHIP_FREEZE.json','results/LOCKED_MODEL_REFERENCE.json','results/SELECTION_MAIN_FROZEN.csv','results/SELECTION_DENSE_FROZEN.csv','results/AVAILABILITY.csv','results/PREPARATION.json','results/PRESCORING_VALIDATION.json','results/RESPONSE_ENDPOINT_CALIBRATION.json']]
 hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}
 facts=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),new_target_outcomes_scored=False,original_target_outcomes_already_known=True,external_preregistration=False,models_retrained=False,source_anchors_reused=True,files=hashes)
 out.write_text(json.dumps(facts,indent=2));print('Frozen',len(hashes),'files before scoring newly selected target performance.',flush=True)
if __name__=='__main__':main()
