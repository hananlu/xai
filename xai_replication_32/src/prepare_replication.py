"""Prepare frozen membership and timestamp-only case selections; no model performance queries."""
from pathlib import Path
import io,json,hashlib,tarfile,shutil,time
import numpy as np,pandas as pd
from data_common import ROOT,windows,period

def main():
 t0=time.perf_counter();base=ROOT.parent/'xai_cross_institution';raw=ROOT.parents[1]/'work/novelty_audit/data/institutions.tar.gz'
 if not raw.is_file():raise FileNotFoundError('Set up the official institutions.tar.gz archive under workspace/work/novelty_audit/data; see README provenance.')
 frozen=json.loads((ROOT/'results/MEMBERSHIP_FREEZE.json').read_text())
 for name,h in frozen['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
 split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');audit=pd.read_csv(ROOT/'data/selection_training_only.csv').set_index('id');oldmanifest={int(r['id']):r for r in json.loads((base/'data/MANIFEST.json').read_text())['files']};records=[]
 common=pd.read_csv(base/'data/institution_0.csv.gz',usecols=['id_time','time','coverage_10min','complete_hour','conservative_artifact_flag'])
 for row in split.query("role=='source'").itertuples():
  p=ROOT/f'data/institution_{row.id}.csv.gz';shutil.copy2(base/'data'/p.name,p);original=oldmanifest[int(row.id)]
  records.append(dict(id=int(row.id),role='source',source_member=original['source_member'],raw_sha256=original['raw_sha256'],file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 targets=set(split.query("role=='target'").id);remaining=set(targets)
 with tarfile.open(raw,'r|gz') as archive:
  for member in archive:
   if not member.isfile() or '/agg_1_hour/' not in member.name:continue
   ident=int(Path(member.name).stem)
   if ident not in remaining:continue
   b=archive.extractfile(member).read();rawhash=hashlib.sha256(b).hexdigest();assert rawhash==audit.loc[ident,'sha256']
   d=pd.read_csv(io.BytesIO(b),usecols=['id_time','n_bytes']);assert d.id_time.is_unique
   d=common.merge(d,on='id_time',how='left',validate='one_to_one');p=ROOT/f'data/institution_{ident}.csv.gz';d.to_csv(p,index=False,compression={'method':'gzip','mtime':0})
   records.append(dict(id=ident,role='target',source_member=member.name,raw_sha256=rawhash,file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));remaining.remove(ident)
   print('Prepared new target',ident,'remaining',len(remaining),flush=True)
   if not remaining:break
 assert not remaining and len(records)==64
 (ROOT/'data/MANIFEST.json').write_text(json.dumps(dict(dataset='CESNET-TimeSeries26',source='https://doi.org/10.5281/zenodo.21945629',license='CC BY 4.0',files=records,new_target_outcomes_scored=False,source_anchors_reused=True),indent=2))
 rows=[];dense=[];availability=[]
 for pair in pd.read_csv(ROOT/'MATCHED_PAIRS.csv').itertuples():
  cache={i:windows(ROOT/f'data/institution_{i}.csv.gz') for i in [pair.source,pair.target]}
  for year in [2025,2026]:
   members={}
   for ident in cache:
    v=cache[ident];q=period(v,f'{year}-04-08',f'{year}-07-01',6);ix=np.flatnonzero(q);members[ident]={int(v['o'][i]):int(i) for i in ix}
   common_origins=sorted(set(members[pair.source])&set(members[pair.target]));n=len(common_origins)
   base_positions=np.unique(np.linspace(0,n-1,min(16,n),dtype=int)) if n else np.array([],int);main_o=[common_origins[i] for i in base_positions];ig_positions=set(np.unique(np.linspace(0,len(main_o)-1,min(4,len(main_o)),dtype=int))) if main_o else set()
   remainder=sorted(set(common_origins)-set(main_o));extra=[remainder[j] for j in np.unique(np.linspace(0,len(remainder)-1,min(48,len(remainder)),dtype=int))] if remainder else [];dense_o=sorted(set(main_o)|set(extra))
   availability.append(dict(pair=int(pair.pair),year=year,source=int(pair.source),target=int(pair.target),source_eligible=len(members[pair.source]),target_eligible=len(members[pair.target]),common_eligible=n,main_origins=len(main_o),dense_origins=len(dense_o)))
   for ident,cohort in [(pair.source,'source'),(pair.target,'target')]:
    for j,o in enumerate(main_o):rows.append(dict(pair=int(pair.pair),id=int(ident),cohort=cohort,year=year,origin=str(cache[ident]['t'][o]),ig=j in ig_positions,common_eligible_origins=n))
    for o in dense_o:dense.append(dict(pair=int(pair.pair),id=int(ident),cohort=cohort,year=year,origin=str(cache[ident]['t'][o]),is_main=o in main_o,common_eligible_origins=n))
 pd.DataFrame(rows).to_csv(ROOT/'results/SELECTION_MAIN_FROZEN.csv',index=False);pd.DataFrame(dense).to_csv(ROOT/'results/SELECTION_DENSE_FROZEN.csv',index=False);pd.DataFrame(availability).to_csv(ROOT/'results/AVAILABILITY.csv',index=False)
 facts=dict(status='prepared',runtime_seconds=time.perf_counter()-t0,source_series=32,new_target_series=32,main_histories=len(rows),dense_histories=len(dense),new_target_performance_scored=False)
 (ROOT/'results/PREPARATION.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
if __name__=='__main__':main()
