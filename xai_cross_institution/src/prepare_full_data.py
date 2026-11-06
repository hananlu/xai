from pathlib import Path
import json,csv,hashlib,tarfile,io
import pandas as pd,numpy as np
from scipy.optimize import linear_sum_assignment
from data_common import ROOT

def main():
 workspace=ROOT.parents[1];raw=workspace/'work/novelty_audit/data/institutions.tar.gz';audit=pd.read_csv(ROOT.parent/'xai_research_v2/data/selection_training_only.csv').set_index('id');split=pd.read_csv(ROOT/'INSTITUTION_SPLIT.csv');ids=set(split.id)
 assert raw.is_file();dest=ROOT/'data';dest.mkdir(exist_ok=True)
 common=pd.read_csv(ROOT.parent/'xai_research_v2/data/institution_28.csv.gz',usecols=['id_time','time','coverage_10min','complete_hour','conservative_artifact_flag'])
 records=[]
 with tarfile.open(raw,'r|gz') as archive:
  for m in archive:
   if not m.isfile() or '/agg_1_hour/' not in m.name:continue
   ident=int(Path(m.name).stem)
   if ident not in ids:continue
   b=archive.extractfile(m).read();sha=hashlib.sha256(b).hexdigest();assert sha==audit.loc[ident,'sha256']
   f=pd.read_csv(io.BytesIO(b),usecols=['id_time','n_bytes']);assert f.id_time.is_unique
   f=common.merge(f,on='id_time',how='left',validate='one_to_one');p=dest/f'institution_{ident}.csv.gz';f.to_csv(p,index=False,compression={'method':'gzip','mtime':0})
   records.append(dict(id=ident,role=split.set_index('id').loc[ident,'role'],source_member=m.name,raw_sha256=sha,file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
   if len(records)==48:break
 assert len(records)==48
 # Match source/target one-to-one within fixed training-volume strata. Matching uses only pre-existing 2024 metadata.
 pairs=[]
 for stratum,g in split.groupby('volume_stratum'):
  a=g[g.role=='source'].id.to_numpy();b=g[g.role=='target'].id.to_numpy()
  def descriptors(x):return np.array([[np.log1p(audit.loc[i,'median_gb']),np.log1p(audit.loc[i,'std_gb']/audit.loc[i,'median_gb'])] for i in x])
  A=descriptors(a);B=descriptors(b);scale=np.std(A,axis=0);scale=np.where(scale>1e-12,scale,1);distance=np.linalg.norm((B[:,None,:]-A[None,:,:])/scale,axis=2);rr,cc=linear_sum_assignment(distance)
  for j,k in zip(rr,cc):pairs.append(dict(pair=len(pairs),volume_stratum=int(stratum),source=int(a[k]),target=int(b[j]),training_descriptor_distance=float(distance[j,k])))
 pd.DataFrame(pairs).to_csv(ROOT/'MATCHED_PAIRS.csv',index=False)
 (dest/'MANIFEST.json').write_text(json.dumps(dict(dataset='CESNET-TimeSeries26',source='https://doi.org/10.5281/zenodo.21945629',license='CC BY 4.0',files=records,roles='frozen split',target_outcomes_scored=False,matching='2024 volume/CV metadata only; no outcome matching'),indent=2))
 print('Prepared 48 series and 8 matched pairs; target outcomes unscored',flush=True)
if __name__=='__main__':main()
