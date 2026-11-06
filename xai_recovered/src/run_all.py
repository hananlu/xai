"""Run or resume the full experiment, analyze results, and compile the paper."""
import subprocess, sys
from pathlib import Path

src=Path(__file__).resolve().parent
for script,args in [('experiment.py',['--mode','all','--device','cpu']),('analyze.py',[]),('check_ig_convergence.py',[]),('explore_ridge.py',[]),('build_paper.py',[]),('validate_results.py',[])]:
    subprocess.run([sys.executable,str(src/script),*args],check=True)
