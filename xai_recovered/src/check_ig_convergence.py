"""Secondary numerical follow-up after the planned IG completeness check failed."""
import time
import numpy as np
import pandas as pd
import torch
from experiment import RESULTS,SEEDS,Forecaster,save_json
from analyze import integrated_gradients

def main():
    torch.set_num_threads(4);rows=[]
    for variant in ['attention','bounded']:
        for seed in SEEDS:
            ck=torch.load(RESULTS/f'{variant}_L144_s{seed}.pt',weights_only=True,map_location='cpu')
            model=Forecaster(variant);model.load_state_dict(ck['state_dict'])
            a=np.load(RESULTS/f'xai_{variant}_s{seed}.npz');x=a['inputs'][:16];b=a['baseline'][:16]
            for steps in [128,512,2048]:
                start=time.time();attr,res=integrated_gradients(model,x,b,steps);resgb=np.abs(res)*ck['std']
                rows.append(dict(model=variant,seed=seed,steps=steps,origins=16,
                 mean_abs_completeness_GB=float(resgb.mean()),max_abs_completeness_GB=float(resgb.max()),
                 n_residual_above_0_1GB=int((resgb>.1).sum()),seconds=time.time()-start))
                print(variant,seed,'IG steps',steps,'mean abs residual',resgb.mean(),'max',resgb.max(),flush=True)
    frame=pd.DataFrame(rows);frame.to_csv(RESULTS/'ig_convergence_followup.csv',index=False)
    save_json(RESULTS/'ig_reliability.json',{'status':'provisional_nonconverged',
      'note':'Primary 32-interval IG fails numerical completeness in some cases; do not treat its rankings as validated attribution.',
      'followup_max_residual_GB_at_2048':float(frame[frame.steps==2048].max_abs_completeness_GB.max())})

if __name__=='__main__':main()
