"""Execute a selected notebook with a real Jupyter kernel, preserving errors in a separate file."""
from pathlib import Path
import argparse,json,time
import nbformat
from nbclient import NotebookClient

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('notebook',type=Path)
    parser.add_argument('--kernel',default='python3')
    parser.add_argument('--output',type=Path,required=True,help='New notebook output path; do not overwrite the input.')
    args=parser.parse_args();source=args.notebook.resolve();dest=args.output.resolve()
    if source==dest or dest.exists():raise ValueError('Choose a new output file to preserve the source and earlier run.')
    nb=nbformat.read(source,as_version=4);t=time.perf_counter()
    client=NotebookClient(nb,timeout=1800,kernel_name=args.kernel,resources={'metadata':{'path':str(source.parent)}})
    try:client.execute()
    except Exception:
        failure=dest.with_suffix('.failed.ipynb');nbformat.write(nb,failure);raise
    nbformat.validate(nb);nbformat.write(nb,dest)
    print(json.dumps({'status':'passed','seconds':time.perf_counter()-t,'code_cells':sum(c.cell_type=='code' for c in nb.cells),'output':str(dest)},indent=2))
if __name__=='__main__':main()
