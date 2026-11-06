from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
import numpy as np,pandas as pd
from scipy.optimize import linear_sum_assignment
r=Path(__file__).resolve().parents[1];base=r.parent/'xai_cross_institution';audit_path=r.parent/'xai_research_v2/data/selection_training_only.csv';
if (r/'results/MEMBERSHIP_FREEZE.json').exists():raise RuntimeError('Membership already frozen; do not overwrite it.')
a=pd.read_csv(audit_path);old=pd.read_csv(base/'INSTITUTION_SPLIT.csv');meta=json.loads((base/'SPLIT_MANIFEST.json').read_text());dev=set(meta['development_ids'])
elig=a[a.eligible&~a.id.isin(dev)].sort_values(['median_gb','id']).copy()
for s,ix in enumerate(np.array_split(np.arange(len(elig)),4)):elig.loc[elig.index[ix],'volume_stratum']=s
elig.volume_stratum=elig.volume_stratum.astype(int)
assert len(elig)==265 and old.merge(elig[['id','volume_stratum']],on='id',suffixes=('_old','_new')).eval('volume_stratum_old==volume_stratum_new').all()
unused=elig[~elig.id.isin(old.id)].copy();assert len(unused)==217
salt='xai-replication-32-20261106-v1'
unused['assignment_hash']=unused.id.map(lambda i:hashlib.sha256(f'{salt}:{i}'.encode()).hexdigest())
target=unused.sort_values(['volume_stratum','assignment_hash']).groupby('volume_stratum',sort=True).head(8).copy();assert len(target)==32
source=old.query("role=='source'")[['id','role','volume_stratum']].copy();source=source.merge(a[['id','median_gb','std_gb','coverage','sha256']],on='id')
target['role']='target';new=pd.concat([source,target[['id','role','volume_stratum','median_gb','std_gb','coverage','sha256']]],ignore_index=True)
new=new.merge(unused[['id','assignment_hash']],on='id',how='left');new['assignment_hash']=new.assignment_hash.fillna('locked_original_source')
assert len(new)==64 and new.id.is_unique and not (set(target.id)&set(old.id)) and not (set(target.id)&dev)
new.to_csv(r/'INSTITUTION_SPLIT.csv',index=False);unused.to_csv(r/'UNUSED_ELIGIBLE_POOL_2024.csv',index=False);a.to_csv(r/'data/selection_training_only.csv',index=False)
pair_rows=[]
for s in range(4):
 src=source[source.volume_stratum==s].sort_values('id');tar=target[target.volume_stratum==s].sort_values('assignment_hash')
 def desc(d):return np.column_stack([np.log1p(d.median_gb),np.log1p(d.std_gb/d.median_gb)])
 A=desc(src);B=desc(tar);scale=np.std(A,axis=0);scale=np.where(scale>1e-12,scale,1);dist=np.linalg.norm((B[:,None,:]-A[None,:,:])/scale,axis=2);rr,cc=linear_sum_assignment(dist)
 for j,k in zip(rr,cc):pair_rows.append(dict(pair=len(pair_rows),volume_stratum=s,source=int(src.id.iloc[k]),target=int(tar.id.iloc[j]),training_descriptor_distance=float(dist[j,k])))
pd.DataFrame(pair_rows).to_csv(r/'MATCHED_PAIRS.csv',index=False)
for p in (base/'models').iterdir():
 if p.is_file():shutil.copy2(p,r/'models'/p.name)
for name in ['data_common.py','neural_feasibility.py','benchmark_common.py','evaluate_forecasts.py','evaluate_attributions.py','validate_response_endpoint.py']:
 shutil.copy2(base/'src'/name,r/'src'/name)
# Reporting implementation copied with transparent metadata fixes, primary arithmetic preserved.
s=(base/'src/analyze_full.py').read_text().replace("target_institutions=8,matched_pairs=8,protocol='FULL_PROTOCOL.md'","target_institutions=32,matched_pairs=32,protocol='PROTOCOL_REPLICATION.md'")
(r/'src/analyze_replication.py').write_text(s)
shutil.copy2(base/'requirements-full.txt',r/'requirements-full.txt')
(r/'results/LOCKED_MODEL_REFERENCE.json').write_text((base/'results/TRAINING_COMPLETE.json').read_text())
facts=dict(frozen_utc=datetime.now(timezone.utc).isoformat(),phase='membership_frozen_before_new_target_scoring',new_target_outcomes_scored=False,external_preregistration=False,selected_target_count=32,source_anchor_count=32,eligible_unused_pool=217,selection_salt=salt,selection='first eight SHA256-ranked unused eligible institutions per original reconstructed 2024 volume stratum',matching='one-to-one Hungarian assignment within stratum using 2024 log1p median and log1p coefficient of variation; source descriptor SD scaling',used_ids_excluded=sorted(set(old.id)|dev),target_ids=sorted(int(i) for i in target.id),models_retrained=False,source_anchors_reused=True,original_outcomes_already_known=True,independent_network=False,training_audit_sha256=hashlib.sha256(audit_path.read_bytes()).hexdigest(),files={name:hashlib.sha256((r/name).read_bytes()).hexdigest() for name in ['INSTITUTION_SPLIT.csv','MATCHED_PAIRS.csv','UNUSED_ELIGIBLE_POOL_2024.csv']},model_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/'models').iterdir() if p.is_file()})
(r/'results/MEMBERSHIP_FREEZE.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
