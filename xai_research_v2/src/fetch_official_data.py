"""Optional official acquisition for selection-from-scratch. No authentication needed."""
from pathlib import Path
import urllib.request,hashlib,json,argparse

def digest(path,algorithm):
 h=hashlib.new(algorithm)
 with path.open('rb') as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,default=Path('work/novelty_audit/data'));args=ap.parse_args();args.cache.mkdir(parents=True,exist_ok=True)
 with urllib.request.urlopen('https://zenodo.org/api/records/21945629',timeout=60) as r:meta=json.load(r)
 for key in ['outages.csv','ids_relationship.csv','europe_time_changes.csv','institutions.tar.gz']:
  f=next(v for v in meta['files'] if v['key']==key);p=args.cache/key;offset=p.stat().st_size if p.exists() else 0
  if offset>f['size']:raise ValueError(f'Oversized local file: {p}')
  if offset<f['size']:
   req=urllib.request.Request(f['links']['self'],headers={'Range':f'bytes={offset}-'} if offset else {})
   with urllib.request.urlopen(req,timeout=120) as r:
    mode='ab' if offset and r.status==206 else 'wb'
    if mode=='ab':assert r.headers.get('Content-Range','').startswith(f'bytes {offset}-')
    with p.open(mode) as out:
     while b:=r.read(8*1024*1024):out.write(b)
  assert p.stat().st_size==f['size'];algorithm,wanted=f['checksum'].split(':');assert digest(p,algorithm)==wanted
  print('Verified',key,f['size'],f['checksum'],flush=True)
  if key=='institutions.tar.gz':(args.cache/'archive_verified.json').write_text(json.dumps(dict(record=21945629,filename=key,bytes=f['size'],checksum=f['checksum'],verified=True),indent=2))
 (args.cache/'zenodo_record_metadata.json').write_text(json.dumps(meta,indent=2))
if __name__=='__main__':main()
