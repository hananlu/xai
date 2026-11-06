"""Select by training metadata only; never score reserved target outcomes."""
from pathlib import Path
import tarfile,json,hashlib
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1]
WORK=Path('work/novelty_audit/data')
def main():
 verified=json.loads((WORK/'archive_verified.json').read_text());assert verified['verified']
 dest=WORK/'hourly';dest.mkdir(exist_ok=True)
 with tarfile.open(WORK/'institutions.tar.gz','r|gz') as t:
  for m in t:
   if m.isfile() and ('/agg_1_hour/' in m.name or '/times/' in m.name or m.name.endswith('identifiers.csv')):
    p=dest/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
 base=dest/'institutions'
 ts=pd.read_csv(base/'times/times_1_hour.csv');ts['time']=pd.to_datetime(ts.time,utc=True)
 native=pd.read_csv(base/'times/times_10_minutes.csv');native['time']=pd.to_datetime(native.time,utc=True)
 assert ts.id_time.is_unique and ts.time.is_unique and native.id_time.is_unique and native.time.is_unique
 assert ts.time.diff().dropna().eq(pd.Timedelta(hours=1)).all()
 coverage=native.groupby(native.time.dt.floor('h')).size().reindex(ts.time,fill_value=0).to_numpy()
 clean=coverage==6
 time=ts.time
 artifact=((time>=pd.Timestamp('2024-05-21',tz='UTC'))&(time<pd.Timestamp('2024-06-05',tz='UTC'))).to_numpy()
 train=((time>=pd.Timestamp('2024-01-01',tz='UTC'))&(time<pd.Timestamp('2025-01-01',tz='UTC'))).to_numpy()
 stats=[];files=list((base/'agg_1_hour').glob('*.csv'));assert len(files)==285,len(files)
 for p in files:
  f=pd.read_csv(p,usecols=['id_time','n_bytes']);assert f.id_time.is_unique
  y=f.set_index('id_time').n_bytes.reindex(ts.id_time).to_numpy(dtype=float)/1e9
  eligible=train&clean&~artifact;v=y[eligible];valid=np.isfinite(v)&(v>=0)
  stats.append(dict(id=int(p.stem),coverage=float(valid.mean()),median_gb=float(np.nanmedian(v)),std_gb=float(np.nanstd(v)),eligible=bool(valid.mean()>=.9 and np.nanmedian(v)>0 and np.nanstd(v)>0),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 s=pd.DataFrame(stats).sort_values(['median_gb','id']);s['stratum']=-1;s['selected']=False
 eligible=s.index[s.eligible].to_numpy();assert len(eligible)>=12
 for k,ix in enumerate(np.array_split(eligible,4)):
  s.loc[ix,'stratum']=k
  chosen=sorted(ix,key=lambda i:hashlib.sha256(f'xai-v2-2026:{s.loc[i,"id"]}'.encode()).hexdigest())[:3]
  s.loc[chosen,'selected']=True
 s.to_csv(ROOT/'data/selection_training_only.csv',index=False)
 selected=s[s.selected].sort_values('id');manifest=[]
 for row in selected.itertuples():
  p=base/f'agg_1_hour/{row.id}.csv';f=pd.read_csv(p,usecols=['id_time','n_bytes'])
  out=f.merge(ts,on='id_time',how='right',validate='one_to_one');out['coverage_10min']=coverage;out['complete_hour']=clean;out['conservative_artifact_flag']=artifact
  q=ROOT/f'data/institution_{row.id}.csv.gz';out.to_csv(q,index=False,compression={'method':'gzip','mtime':0})
  manifest.append(dict(id=int(row.id),raw_member=f'institutions/agg_1_hour/{row.id}.csv',raw_sha256=row.sha256,selected_file=q.name,selected_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),train_median_gb=row.median_gb,stratum=int(row.stratum)))
 for key in ['outages.csv','europe_time_changes.csv']:(ROOT/'data'/key).write_bytes((WORK/key).read_bytes())
 audit=dict(source='https://zenodo.org/records/21945629',license='CC-BY-4.0',archive=verified,hourly_rows=len(ts),native_10min_rows=len(native),time_start=str(time.iloc[0]),time_end=str(time.iloc[-1]),coverage_counts={str(k):int(v) for k,v in pd.Series(coverage).value_counts().sort_index().items()},complete_hours=int(clean.sum()),partial_or_absent_hours=int((~clean).sum()),institutions_available=len(files),institutions_eligible=len(eligible),selected=manifest,reserved_outcomes_scored=False)
 (ROOT/'data/DATA_AUDIT.json').write_text(json.dumps(audit,indent=2));print(json.dumps({k:v for k,v in audit.items() if k not in ['selected']},indent=2));print('Selected IDs',selected.id.tolist())
if __name__=='__main__':main()
